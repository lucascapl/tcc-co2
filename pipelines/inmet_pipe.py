import glob
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
from typing import Optional

import pandas as pd

from utils import (
    ANO_FINAL,
    ANO_INICIAL,
    MAPA_REGIOES,
    normalizar_texto,
    ordenar_regioes,
    salvar_tratado,
)

CAPITAL_POR_UF = {
    "AC": "RIO BRANCO", "AL": "MACEIO", "AP": "MACAPA", "AM": "MANAUS",
    "BA": "SALVADOR", "CE": "FORTALEZA", "DF": "BRASILIA", "ES": "VITORIA",
    "GO": "GOIANIA", "MA": "SAO LUIS", "MT": "CUIABA", "MS": "CAMPO GRANDE",
    "MG": "BELO HORIZONTE", "PA": "BELEM", "PB": "JOAO PESSOA", "PR": "CURITIBA",
    "PE": "RECIFE", "PI": "TERESINA", "RJ": "RIO DE JANEIRO", "RN": "NATAL",
    "RS": "PORTO ALEGRE", "RO": "PORTO VELHO", "RR": "BOA VISTA", "SC": "FLORIANOPOLIS",
    "SP": "SAO PAULO", "SE": "ARACAJU", "TO": "PALMAS",
}

NA_VALUES_INMET = ["", "nan", "NaN", "None", "NULL", "-9999", "-9999.0", "-9999,0"]


def _listar_arquivos_inmet(pasta_inmet: str) -> list[str]:
    padroes = [
        os.path.join(pasta_inmet, "*", "*.CSV"),
        os.path.join(pasta_inmet, "*", "*.csv"),
    ]
    arquivos = []
    for padrao in padroes:
        arquivos.extend(glob.glob(padrao))
    return sorted(set(arquivos))


def _extrair_uf(nome_arquivo: str) -> Optional[str]:
    m = re.search(r"^INMET_[A-Z]+_([A-Z]{2})_", nome_arquivo, flags=re.IGNORECASE)
    return m.group(1).upper() if m else None


def _extrair_ano(caminho_arquivo: str) -> Optional[int]:
    pasta_pai = os.path.basename(os.path.dirname(caminho_arquivo))
    if re.fullmatch(r"\d{4}", pasta_pai):
        return int(pasta_pai)
    m = re.search(r"(19|20)\d{2}", os.path.basename(caminho_arquivo))
    return int(m.group(0)) if m else None


def _extrair_codigo_estacao(nome_arquivo: str) -> Optional[str]:
    m = re.search(r"_([A-Z]\d{3})_", nome_arquivo, flags=re.IGNORECASE)
    return m.group(1).upper() if m else None


def _extrair_nome_estacao(nome_arquivo: str) -> Optional[str]:
    m = re.search(
        r"^INMET_[A-Z]+_[A-Z]{2}_A\d+_(.+)_\d{2}-\d{2}-\d{4}_A_\d{2}-\d{2}-\d{4}\.[Cc][Ss][Vv]$",
        nome_arquivo,
        flags=re.IGNORECASE,
    )
    return m.group(1) if m else None


def _normalizar_nome_local(texto: str) -> str:
    texto_norm = normalizar_texto(texto).upper()
    return re.sub(r"[^A-Z0-9]", "", texto_norm)


def _eh_estacao_da_capital(uf: str, nome_arquivo: str) -> bool:
    capital = CAPITAL_POR_UF.get(uf)
    estacao = _extrair_nome_estacao(nome_arquivo)
    if not capital or not estacao:
        return False
    capital_norm = _normalizar_nome_local(capital)
    estacao_norm = _normalizar_nome_local(estacao)
    return (capital_norm in estacao_norm) or (estacao_norm in capital_norm)


def _detectar_linha_cabecalho(caminho_arquivo: str, max_linhas: int = 100) -> int:
    with open(caminho_arquivo, "r", encoding="latin1", errors="ignore") as f:
        for idx, linha in enumerate(f):
            if idx > max_linhas:
                break
            linha_norm = normalizar_texto(linha).lower()
            if "data" in linha_norm and "hora" in linha_norm and ";" in linha:
                if "precipitacao total" in linha_norm or "temperatura do ar" in linha_norm:
                    return idx
    raise ValueError(f"Cabecalho da serie horaria nao encontrado em: {caminho_arquivo}")


def _normalizar_colunas(colunas: list[str]) -> dict[str, str]:
    return {col: normalizar_texto(str(col)).strip().lower() for col in colunas}


def _encontrar_coluna_temperatura(colunas: list[str]) -> Optional[str]:
    colunas_norm = _normalizar_colunas(colunas)
    candidatos = [
        col for col, col_norm in colunas_norm.items()
        if "temperatura do ar - bulbo seco" in col_norm
    ]
    if not candidatos:
        candidatos = [
            col for col, col_norm in colunas_norm.items()
            if "temperatura do ar" in col_norm and "bulbo seco" in col_norm
        ]
    if not candidatos:
        return None
    for col in candidatos:
        if "horaria" in colunas_norm[col] or "horario" in colunas_norm[col]:
            return col
    return candidatos[0]


def _encontrar_coluna_precipitacao(colunas: list[str]) -> Optional[str]:
    colunas_norm = _normalizar_colunas(colunas)
    candidatos = [
        col for col, col_norm in colunas_norm.items()
        if "precipitacao total" in col_norm
    ]
    if not candidatos:
        return None
    for col in candidatos:
        if "horaria" in colunas_norm[col] or "horario" in colunas_norm[col]:
            return col
    return candidatos[0]


def _parse_numero_serie(serie: pd.Series) -> pd.Series:
    # Arquivos INMET normalmente usam virgula decimal. Mantemos robustez para texto.
    texto = (
        serie.astype(str)
        .str.strip()
        .str.replace("\ufeff", "", regex=False)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )
    texto = texto.replace({valor: None for valor in NA_VALUES_INMET})
    return pd.to_numeric(texto, errors="coerce")


def _ler_colunas_relevantes(caminho: str, cabecalho: int) -> tuple[pd.DataFrame, Optional[str], Optional[str]]:
    # Primeiro lê só o cabeçalho. Depois lê apenas temperatura e chuva.
    cab = pd.read_csv(
        caminho,
        sep=";",
        skiprows=cabecalho,
        encoding="latin1",
        nrows=0,
        engine="c",
    )
    colunas = [str(c).strip() for c in cab.columns]
    col_temp = _encontrar_coluna_temperatura(colunas)
    col_chuva = _encontrar_coluna_precipitacao(colunas)
    usecols = [c for c in [col_temp, col_chuva] if c is not None]

    if not usecols:
        return pd.DataFrame(), None, None

    df = pd.read_csv(
        caminho,
        sep=";",
        skiprows=cabecalho,
        encoding="latin1",
        usecols=usecols,
        dtype=str,
        na_values=NA_VALUES_INMET,
        engine="c",
    )
    df.columns = [str(c).strip() for c in df.columns]
    return df, col_temp, col_chuva


def _processar_um_arquivo(args) -> tuple[Optional[dict], Optional[dict]]:
    caminho, ano_min, ano_max, somente_capitais = args
    nome = os.path.basename(caminho)
    uf = _extrair_uf(nome)
    ano = _extrair_ano(caminho)
    codigo = _extrair_codigo_estacao(nome)

    if uf is None or ano is None:
        return None, None
    if ano < ano_min or ano > ano_max:
        return None, None
    if somente_capitais and (not _eh_estacao_da_capital(uf, nome)):
        return None, None

    try:
        cabecalho = _detectar_linha_cabecalho(caminho)
        df, col_temp, col_chuva = _ler_colunas_relevantes(caminho, cabecalho)

        temp_media_estacao = None
        n_obs_temp = 0
        if col_temp is not None and col_temp in df.columns:
            temp = _parse_numero_serie(df[col_temp])
            n_obs_temp = int(temp.notna().sum())
            if n_obs_temp > 0:
                temp_media_estacao = float(temp.mean())

        chuva_total_estacao = None
        n_obs_chuva = 0
        if col_chuva is not None and col_chuva in df.columns:
            chuva = _parse_numero_serie(df[col_chuva])
            n_obs_chuva = int(chuva.notna().sum())
            if n_obs_chuva > 0:
                chuva_total_estacao = float(chuva.sum(min_count=1))

        if temp_media_estacao is None and chuva_total_estacao is None:
            return None, None

        return {
            "Estado": uf,
            "Ano": int(ano),
            "Codigo_estacao": codigo,
            "Arquivo": nome,
            "Temp_media_estacao": temp_media_estacao,
            "N_obs_temp": n_obs_temp,
            "Chuva_total_estacao": chuva_total_estacao,
            "N_obs_chuva": n_obs_chuva,
        }, None
    except Exception as exc:
        return None, {"Arquivo": caminho, "Erro": str(exc)}


@lru_cache(maxsize=8)
def _processar_inmet_estacao_ano_cache(
    pasta_inmet_abs: str,
    ano_min: int,
    ano_max: int,
    somente_capitais: bool,
    paralelo: bool,
    max_workers: Optional[int],
) -> pd.DataFrame:
    arquivos = _listar_arquivos_inmet(pasta_inmet_abs)
    if not arquivos:
        raise FileNotFoundError(f"Nenhum arquivo INMET encontrado em: {pasta_inmet_abs}")

    tarefas = [(arq, int(ano_min), int(ano_max), bool(somente_capitais)) for arq in arquivos]
    registros = []
    erros = []

    if paralelo:
        if max_workers is None:
            # Leitura de muitos arquivos pequenos/medios costuma ser I/O-bound.
            max_workers = min(32, max(4, (os.cpu_count() or 4) * 2))
        print(f"[inmet] Processando {len(tarefas)} arquivos com {max_workers} threads...")
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futuros = [executor.submit(_processar_um_arquivo, tarefa) for tarefa in tarefas]
            for i, futuro in enumerate(as_completed(futuros), start=1):
                registro, erro = futuro.result()
                if registro is not None:
                    registros.append(registro)
                if erro is not None:
                    erros.append(erro)
                if i % 500 == 0 or i == len(futuros):
                    print(f"[inmet] {i}/{len(futuros)} arquivos avaliados | válidos: {len(registros)} | erros: {len(erros)}")
    else:
        print(f"[inmet] Processando {len(tarefas)} arquivos em modo serial...")
        for i, tarefa in enumerate(tarefas, start=1):
            registro, erro = _processar_um_arquivo(tarefa)
            if registro is not None:
                registros.append(registro)
            if erro is not None:
                erros.append(erro)
            if i % 500 == 0 or i == len(tarefas):
                print(f"[inmet] {i}/{len(tarefas)} arquivos avaliados | válidos: {len(registros)} | erros: {len(erros)}")

    if not registros:
        detalhe = f" Exemplo de erro: {erros[0]['Erro']}" if erros else ""
        raise ValueError("Nenhuma observacao valida do INMET foi encontrada no recorte informado." + detalhe)

    if erros:
        os.makedirs("bases/tratadas", exist_ok=True)
        pd.DataFrame(erros).to_csv("bases/tratadas/inmet-erros-processamento.csv", index=False)
        print(f"[inmet] Aviso: {len(erros)} arquivos com erro foram registrados em bases/tratadas/inmet-erros-processamento.csv")

    return pd.DataFrame(registros)


def _processar_inmet_estacao_ano(
    pasta_inmet: str,
    ano_min: int,
    ano_max: int,
    somente_capitais: bool,
    paralelo: bool,
    max_workers: Optional[int],
) -> pd.DataFrame:
    pasta_abs = os.path.abspath(pasta_inmet)
    return _processar_inmet_estacao_ano_cache(
        pasta_abs,
        int(ano_min),
        int(ano_max),
        bool(somente_capitais),
        bool(paralelo),
        max_workers,
    ).copy()


def _agregar_estado_ano(estacoes: pd.DataFrame) -> pd.DataFrame:
    partes = []

    temp_base = estacoes.dropna(subset=["Temp_media_estacao"]).copy()
    if not temp_base.empty:
        temp_base["_soma_temp_ponderada"] = temp_base["Temp_media_estacao"] * temp_base["N_obs_temp"]
        temp_estado = (
            temp_base.groupby(["Estado", "Ano"], as_index=False)
            .agg({"_soma_temp_ponderada": "sum", "N_obs_temp": "sum"})
        )
        temp_estado["temp_media"] = temp_estado["_soma_temp_ponderada"] / temp_estado["N_obs_temp"]
        partes.append(temp_estado[["Estado", "Ano", "temp_media", "N_obs_temp"]])

    chuva_base = estacoes.dropna(subset=["Chuva_total_estacao"]).copy()
    if not chuva_base.empty:
        chuva_estado = (
            chuva_base.groupby(["Estado", "Ano"], as_index=False)
            .agg(
                chuva_media=("Chuva_total_estacao", "mean"),
                N_estacoes_chuva=("Chuva_total_estacao", "count"),
                N_obs_chuva=("N_obs_chuva", "sum"),
            )
        )
        partes.append(chuva_estado)

    if not partes:
        raise ValueError("Nao foi possivel agregar temperatura ou chuva do INMET.")

    estado_ano = partes[0]
    for parte in partes[1:]:
        estado_ano = estado_ano.merge(parte, on=["Estado", "Ano"], how="outer")

    colunas = ["Estado", "Ano"]
    if "temp_media" in estado_ano.columns:
        colunas.append("temp_media")
    if "chuva_media" in estado_ano.columns:
        colunas.append("chuva_media")

    return estado_ano[colunas].sort_values(["Estado", "Ano"]).reset_index(drop=True)


def _agregar_regiao_ano(estado_ano: pd.DataFrame) -> pd.DataFrame:
    regional = estado_ano.copy()
    regional["Regiao"] = regional["Estado"].map(MAPA_REGIOES)
    regional = regional.dropna(subset=["Regiao", "Ano"])

    agg = {}
    if "temp_media" in regional.columns:
        # Média simples entre estados da região. Evita regiões com mais estações dominarem o resultado.
        agg["temp_media"] = lambda s: s.mean(skipna=True)
    if "chuva_media" in regional.columns:
        agg["chuva_media"] = lambda s: s.mean(skipna=True)

    regiao_ano = regional.groupby(["Regiao", "Ano"], as_index=False).agg(agg)
    return ordenar_regioes(regiao_ano, coluna_regiao="Regiao", coluna_ano="Ano")


def processar_inmet_clima(
    pasta_inmet: str = "bases/inmet",
    ano_min: int = ANO_INICIAL,
    ano_max: int = ANO_FINAL,
    agrupar_por_regiao: bool = False,
    somente_capitais: bool = False,
    paralelo: bool = True,
    max_workers: Optional[int] = None,
) -> pd.DataFrame:
    """
    Processa todos os CSVs do INMET uma única vez e gera temperatura e chuva.

    Saída estadual:
        Estado | Ano | temp_media | chuva_media

    Saída regional:
        Regiao | Ano | temp_media | chuva_media

    Observação:
    - temp_media é média ponderada pelo número de observações horárias válidas.
    - chuva_media é a média dos totais anuais das estações do estado/região.
    """
    estacoes = _processar_inmet_estacao_ano(
        pasta_inmet=pasta_inmet,
        ano_min=ano_min,
        ano_max=ano_max,
        somente_capitais=somente_capitais,
        paralelo=paralelo,
        max_workers=max_workers,
    )
    estado_ano = _agregar_estado_ano(estacoes)

    if agrupar_por_regiao:
        regiao_ano = _agregar_regiao_ano(estado_ano)
        return salvar_tratado(regiao_ano, "inmet-clima-regiao")

    return salvar_tratado(estado_ano, "inmet-clima-estado")


def processar_inmet_temperatura(
    pasta_inmet: str = "bases/inmet",
    ano_min: int = ANO_INICIAL,
    ano_max: int = ANO_FINAL,
    agrupar_por_regiao: bool = False,
    somente_capitais: bool = False,
    paralelo: bool = True,
    max_workers: Optional[int] = None,
) -> pd.DataFrame:
    clima = processar_inmet_clima(
        pasta_inmet=pasta_inmet,
        ano_min=ano_min,
        ano_max=ano_max,
        agrupar_por_regiao=agrupar_por_regiao,
        somente_capitais=somente_capitais,
        paralelo=paralelo,
        max_workers=max_workers,
    )
    chave = "Regiao" if agrupar_por_regiao else "Estado"
    saida = clima[[chave, "Ano", "temp_media"]].copy()
    nome = "inmet-temp-regiao" if agrupar_por_regiao else "inmet-temp-estado"
    return salvar_tratado(saida, nome)


def processar_inmet_chuva(
    pasta_inmet: str = "bases/inmet",
    ano_min: int = ANO_INICIAL,
    ano_max: int = ANO_FINAL,
    agrupar_por_regiao: bool = False,
    somente_capitais: bool = False,
    paralelo: bool = True,
    max_workers: Optional[int] = None,
) -> pd.DataFrame:
    clima = processar_inmet_clima(
        pasta_inmet=pasta_inmet,
        ano_min=ano_min,
        ano_max=ano_max,
        agrupar_por_regiao=agrupar_por_regiao,
        somente_capitais=somente_capitais,
        paralelo=paralelo,
        max_workers=max_workers,
    )
    chave = "Regiao" if agrupar_por_regiao else "Estado"
    saida = clima[[chave, "Ano", "chuva_media"]].copy()
    nome = "inmet-chuva-regiao" if agrupar_por_regiao else "inmet-chuva-estado"
    return salvar_tratado(saida, nome)
