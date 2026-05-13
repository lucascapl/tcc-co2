import glob
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd

from utils import (
    ANO_FINAL,
    ANO_INICIAL,
    MAPA_REGIOES,
    normalizar_estado,
    normalizar_texto,
    ordenar_regioes,
    salvar_tratado,
)

# FRP = Fire Radiative Power / Potencia Radiativa do Fogo.
# A soma anual por UF representa o poder radiativo total detectado no ano.
COLUNAS_USADAS = ["DataHora", "Pais", "Estado", "FRP"]


def _normalizar_estado_seguro(valor):
    if pd.isna(valor):
        return None

    texto = str(valor).strip()
    if not texto or texto.lower() in {"nan", "none", "null"}:
        return None

    texto_sem_acento = normalizar_texto(texto).upper()
    if len(texto_sem_acento) == 2 and texto_sem_acento in MAPA_REGIOES:
        return texto_sem_acento

    return normalizar_estado(texto)


def _parse_numero_queimadas(serie: pd.Series) -> pd.Series:
    valores = (
        serie.astype(str)
        .str.strip()
        .str.replace(",", ".", regex=False)
        .replace({"": None, "nan": None, "None": None, "-999": None, "-999.0": None})
    )
    return pd.to_numeric(valores, errors="coerce")


def _extrair_ano_inicial_nome(caminho_arquivo: str) -> int | None:
    nome = os.path.basename(caminho_arquivo)
    m = re.search(r"bdqueimadas_(\d{4})-\d{2}-\d{2}_", nome, flags=re.IGNORECASE)
    if m:
        return int(m.group(1))
    return None


def _listar_arquivos(caminho_queimadas: str, padrao_arquivos: str) -> list[str]:
    if os.path.isfile(caminho_queimadas):
        return [caminho_queimadas]

    arquivos = sorted(glob.glob(os.path.join(caminho_queimadas, padrao_arquivos)))
    if not arquivos:
        arquivos = sorted(glob.glob(os.path.join(caminho_queimadas, "*.CSV")))

    if not arquivos:
        raise FileNotFoundError(
            f"Nenhum arquivo de queimadas encontrado em '{caminho_queimadas}' com padrao '{padrao_arquivos}'."
        )

    return arquivos


def _processar_arquivo_queimadas(
    caminho_arquivo: str,
    ano_min: int,
    ano_max: int,
    chunksize: int,
) -> pd.DataFrame:
    agregados = []

    leitor = pd.read_csv(
        caminho_arquivo,
        encoding="utf-8",
        usecols=lambda c: c in COLUNAS_USADAS,
        chunksize=chunksize,
        low_memory=False,
    )

    for chunk in leitor:
        colunas_faltantes = [c for c in ["DataHora", "Estado", "FRP"] if c not in chunk.columns]
        if colunas_faltantes:
            raise ValueError(
                f"Arquivo {os.path.basename(caminho_arquivo)} sem colunas obrigatorias: {colunas_faltantes}"
            )

        if "Pais" in chunk.columns:
            pais = chunk["Pais"].astype(str).str.strip().str.casefold()
            chunk = chunk[pais == "brasil"].copy()

        if chunk.empty:
            continue

        datas = pd.to_datetime(chunk["DataHora"], errors="coerce")
        ano_arquivo = _extrair_ano_inicial_nome(caminho_arquivo)

        if ano_arquivo is not None:
            # Arquivos como bdqueimadas_2003-01-01_2004-01-01.csv podem trazer
            # registros pontuais de 01/01 do ano seguinte. Mantemos apenas o ano inicial.
            chunk["Ano"] = ano_arquivo
            chunk = chunk[datas.dt.year == ano_arquivo].copy()
        else:
            chunk["Ano"] = datas.dt.year

        chunk = chunk[(chunk["Ano"] >= ano_min) & (chunk["Ano"] <= ano_max)].copy()
        if chunk.empty:
            continue

        chunk["Estado"] = chunk["Estado"].map(_normalizar_estado_seguro)
        chunk = chunk.dropna(subset=["Estado", "Ano"])
        if chunk.empty:
            continue

        chunk["Ano"] = chunk["Ano"].astype(int)
        chunk["FRP"] = _parse_numero_queimadas(chunk["FRP"])

        agregado_chunk = (
            chunk.groupby(["Estado", "Ano"], as_index=False)["FRP"]
            .sum(min_count=1)
            .rename(columns={"FRP": "frp_anual_queimadas"})
        )
        agregados.append(agregado_chunk)

    if not agregados:
        return pd.DataFrame(columns=["Estado", "Ano", "frp_anual_queimadas"])

    return pd.concat(agregados, ignore_index=True)


def _consolidar_agregados_estado(partes: list[pd.DataFrame]) -> pd.DataFrame:
    dados = pd.concat([p for p in partes if not p.empty], ignore_index=True)
    if dados.empty:
        raise ValueError("Nenhum registro valido de queimadas foi encontrado no recorte informado.")

    estado_ano = (
        dados.groupby(["Estado", "Ano"], as_index=False)["frp_anual_queimadas"]
        .sum(min_count=1)
        .sort_values(["Estado", "Ano"])
        .reset_index(drop=True)
    )

    return estado_ano


def _agregar_para_regiao(estado_ano: pd.DataFrame) -> pd.DataFrame:
    base = estado_ano.copy()
    base["Regiao"] = base["Estado"].map(MAPA_REGIOES)
    base = base.dropna(subset=["Regiao"])

    regiao_ano = (
        base.groupby(["Regiao", "Ano"], as_index=False)["frp_anual_queimadas"]
        .sum(min_count=1)
    )

    return ordenar_regioes(regiao_ano, coluna_regiao="Regiao", coluna_ano="Ano")


def processar_queimadas(
    caminho_queimadas: str = "bases/queimadas",
    padrao_arquivos: str = "bdqueimadas_*.csv",
    ano_min: int = ANO_INICIAL,
    ano_max: int = ANO_FINAL,
    agrupar_por_regiao: bool = False,
    chunksize: int = 250_000,
    paralelo: bool = True,
    max_workers: int | None = None,
) -> pd.DataFrame:
    """
    Processa arquivos CSV do Banco de Dados de Queimadas/INPE e calcula
    somente o FRP anual agregado por UF ou por regiao.

    Saida estadual:
        Estado | Ano | frp_anual_queimadas

    Saida regional:
        Regiao | Ano | frp_anual_queimadas

    Interpretacao:
    - frp_anual_queimadas = soma anual do FRP dos focos detectados;
    - representa o poder radiativo anual do fogo no territorio;
    - valores ausentes/codigos -999 sao ignorados.
    """
    arquivos = _listar_arquivos(caminho_queimadas, padrao_arquivos)
    print(f"[queimadas] Arquivos encontrados: {len(arquivos)}")

    partes = []
    if paralelo and len(arquivos) > 1:
        workers = max_workers or min(8, len(arquivos), (os.cpu_count() or 4))
        print(f"[queimadas] Processamento paralelo com {workers} workers")
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futuros = {
                executor.submit(_processar_arquivo_queimadas, arq, ano_min, ano_max, chunksize): arq
                for arq in arquivos
            }
            for futuro in as_completed(futuros):
                arq = futuros[futuro]
                try:
                    parte = futuro.result()
                    if not parte.empty:
                        partes.append(parte)
                    print(f"[queimadas] OK: {os.path.basename(arq)}")
                except Exception as exc:
                    raise RuntimeError(f"Erro processando {arq}: {exc}") from exc
    else:
        for arq in arquivos:
            parte = _processar_arquivo_queimadas(arq, ano_min, ano_max, chunksize)
            if not parte.empty:
                partes.append(parte)
            print(f"[queimadas] OK: {os.path.basename(arq)}")

    estado_ano = _consolidar_agregados_estado(partes)

    if agrupar_por_regiao:
        return salvar_tratado(_agregar_para_regiao(estado_ano), "queimadas-regiao")

    return salvar_tratado(estado_ano, "queimadas-estado")
