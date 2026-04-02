import glob
import os
import re

import pandas as pd

from utils import ANO_FINAL, ANO_INICIAL, MAPA_REGIOES, normalizar_texto, ordenar_regioes, salvar_tratado

CAPITAL_POR_UF = {
    "AC": "RIO BRANCO",
    "AL": "MACEIO",
    "AP": "MACAPA",
    "AM": "MANAUS",
    "BA": "SALVADOR",
    "CE": "FORTALEZA",
    "DF": "BRASILIA",
    "ES": "VITORIA",
    "GO": "GOIANIA",
    "MA": "SAO LUIS",
    "MT": "CUIABA",
    "MS": "CAMPO GRANDE",
    "MG": "BELO HORIZONTE",
    "PA": "BELEM",
    "PB": "JOAO PESSOA",
    "PR": "CURITIBA",
    "PE": "RECIFE",
    "PI": "TERESINA",
    "RJ": "RIO DE JANEIRO",
    "RN": "NATAL",
    "RS": "PORTO ALEGRE",
    "RO": "PORTO VELHO",
    "RR": "BOA VISTA",
    "SC": "FLORIANOPOLIS",
    "SP": "SAO PAULO",
    "SE": "ARACAJU",
    "TO": "PALMAS",
}


def _extrair_uf(nome_arquivo: str) -> str | None:
    """
    Extrai UF do padrao de nome de arquivo INMET:
    INMET_<REGIAO>_<UF>_Axxx_<ESTACAO>_<DATA_INI>_A_<DATA_FIM>.CSV
    """
    m = re.search(r"^INMET_[A-Z]+_([A-Z]{2})_", nome_arquivo, flags=re.IGNORECASE)
    if m:
        return m.group(1).upper()
    return None


def _extrair_ano(caminho_arquivo: str) -> int | None:
    """
    Prioriza o ano da pasta (bases/inmet/<ANO>/arquivo.csv).
    Se nao encontrar, tenta extrair do nome do arquivo.
    """
    pasta_pai = os.path.basename(os.path.dirname(caminho_arquivo))
    if re.fullmatch(r"\d{4}", pasta_pai):
        return int(pasta_pai)

    m = re.search(r"(\d{4})", os.path.basename(caminho_arquivo))
    if m:
        return int(m.group(1))
    return None


def _extrair_nome_estacao(nome_arquivo: str) -> str | None:
    """
    Extrai o nome da estacao a partir do nome do arquivo INMET.
    """
    m = re.search(
        r"^INMET_[A-Z]+_[A-Z]{2}_A\d+_(.+)_\d{2}-\d{2}-\d{4}_A_\d{2}-\d{2}-\d{4}\.CSV$",
        nome_arquivo,
        flags=re.IGNORECASE,
    )
    if not m:
        return None
    return m.group(1)


def _normalizar_nome_local(texto: str) -> str:
    texto_norm = normalizar_texto(texto).upper()
    return re.sub(r"[^A-Z0-9]", "", texto_norm)


def _eh_estacao_da_capital(uf: str, nome_arquivo: str) -> bool:
    capital = CAPITAL_POR_UF.get(uf)
    if not capital:
        return False

    estacao = _extrair_nome_estacao(nome_arquivo)
    if not estacao:
        return False

    capital_norm = _normalizar_nome_local(capital)
    estacao_norm = _normalizar_nome_local(estacao)

    # Aceita correspondencia por inclusao para cobrir sufixos/prefixos no nome da estacao.
    return (capital_norm in estacao_norm) or (estacao_norm in capital_norm)


def _detectar_linha_cabecalho(caminho_arquivo: str, max_linhas: int = 80) -> int:
    """
    Detecta a linha de cabecalho da serie horaria.
    Os arquivos INMET trazem metadados nas primeiras linhas.
    """
    with open(caminho_arquivo, "r", encoding="latin1", errors="ignore") as f:
        for idx, linha in enumerate(f):
            if idx > max_linhas:
                break

            linha_norm = normalizar_texto(linha).lower()
            if (
                "temperatura do ar - bulbo seco" in linha_norm
                and "data" in linha_norm
                and ";" in linha
            ):
                return idx

    raise ValueError(f"Cabecalho da serie horaria nao encontrado em: {caminho_arquivo}")


def _encontrar_coluna_temperatura(colunas: list[str]) -> str | None:
    """
    Identifica a coluna de temperatura horaria do ar (bulbo seco),
    tolerando variacoes de acentos e grafia.
    """
    candidatos = []
    for col in colunas:
        col_norm = normalizar_texto(col).lower()
        if "temperatura do ar - bulbo seco" in col_norm:
            candidatos.append(col)

    if not candidatos:
        return None

    for col in candidatos:
        col_norm = normalizar_texto(col).lower()
        if "horaria" in col_norm:
            return col

    return candidatos[0]


def _encontrar_coluna_precipitacao(colunas: list[str]) -> str | None:
    """
    Identifica a coluna de precipitacao total horaria.
    """
    candidatos = []
    for col in colunas:
        col_norm = normalizar_texto(col).lower()
        if "precipitacao total" in col_norm:
            candidatos.append(col)

    if not candidatos:
        return None

    for col in candidatos:
        col_norm = normalizar_texto(col).lower()
        if "horario" in col_norm or "horaria" in col_norm:
            return col

    return candidatos[0]


def processar_inmet_temperatura(
    pasta_inmet: str = "bases/inmet",
    ano_min: int = ANO_INICIAL,
    ano_max: int = ANO_FINAL,
    agrupar_por_regiao: bool = True,
    somente_capitais: bool = True,
) -> pd.DataFrame:
    """
    Processa todos os CSVs do INMET em subpastas por ano e calcula
    temperatura media anual.

    Retorno regional:
        Regiao | Ano | temp_media

    Retorno estadual:
        Estado | Ano | temp_media
    """
    arquivos = sorted(glob.glob(os.path.join(pasta_inmet, "*", "*.CSV")))
    if not arquivos:
        raise FileNotFoundError(f"Nenhum arquivo INMET encontrado em: {pasta_inmet}")

    registros_estacao = []

    for caminho in arquivos:
        nome = os.path.basename(caminho)
        uf = _extrair_uf(nome)
        ano = _extrair_ano(caminho)

        if uf is None or ano is None:
            continue
        if ano < ano_min or ano > ano_max:
            continue
        if somente_capitais and (not _eh_estacao_da_capital(uf, nome)):
            continue

        cabecalho = _detectar_linha_cabecalho(caminho)
        df = pd.read_csv(
            caminho,
            sep=";",
            skiprows=cabecalho,
            encoding="latin1",
            dtype=str,
        )

        col_temp = _encontrar_coluna_temperatura(list(df.columns))
        if col_temp is None:
            continue

        temp = (
            df[col_temp]
            .astype(str)
            .str.strip()
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
            .replace({"": None, "-9999": None, "-9999.0": None})
        )
        temp = pd.to_numeric(temp, errors="coerce")

        n_obs = int(temp.notna().sum())
        if n_obs == 0:
            continue

        registros_estacao.append(
            {
                "Estado": uf,
                "Ano": int(ano),
                "Temp_media_estacao": float(temp.mean()),
                "N_obs": n_obs,
            }
        )

    if not registros_estacao:
        raise ValueError("Nenhuma observacao valida de temperatura foi encontrada no recorte informado.")

    estacoes = pd.DataFrame(registros_estacao)
    estacoes["_soma_temp_ponderada"] = estacoes["Temp_media_estacao"] * estacoes["N_obs"]

    estado_ano = (
        estacoes.groupby(["Estado", "Ano"], as_index=False)
        .agg({"_soma_temp_ponderada": "sum", "N_obs": "sum"})
    )
    estado_ano["temp_media"] = estado_ano["_soma_temp_ponderada"] / estado_ano["N_obs"]
    estado_ano = estado_ano[["Estado", "Ano", "temp_media", "N_obs"]]
    estado_ano = estado_ano.sort_values(["Estado", "Ano"]).reset_index(drop=True)

    if not agrupar_por_regiao:
        saida_estado = estado_ano[["Estado", "Ano", "temp_media"]].copy()
        return salvar_tratado(saida_estado, "inmet-temp-estado")

    regional = estado_ano.copy()
    regional["Regiao"] = regional["Estado"].map(MAPA_REGIOES)
    regional = regional.dropna(subset=["Regiao"])
    regional["_soma_temp_ponderada"] = regional["temp_media"] * regional["N_obs"]

    regiao_ano = (
        regional.groupby(["Regiao", "Ano"], as_index=False)
        .agg({"_soma_temp_ponderada": "sum", "N_obs": "sum"})
    )
    regiao_ano["temp_media"] = regiao_ano["_soma_temp_ponderada"] / regiao_ano["N_obs"]
    regiao_ano = regiao_ano[["Regiao", "Ano", "temp_media"]]
    regiao_ano = ordenar_regioes(regiao_ano, coluna_regiao="Regiao", coluna_ano="Ano")

    return salvar_tratado(regiao_ano, "inmet-temp-regiao")


def processar_inmet_chuva(
    pasta_inmet: str = "bases/inmet",
    ano_min: int = ANO_INICIAL,
    ano_max: int = ANO_FINAL,
    agrupar_por_regiao: bool = True,
    somente_capitais: bool = False,
) -> pd.DataFrame:
    """
    Processa todos os CSVs do INMET em subpastas por ano e calcula
    chuva anual por estacao, agregando para estado e regiao.

    Retorno regional:
        Regiao | Ano | chuva_media

    Retorno estadual:
        Estado | Ano | chuva_media
    """
    arquivos = sorted(glob.glob(os.path.join(pasta_inmet, "*", "*.CSV")))
    if not arquivos:
        raise FileNotFoundError(f"Nenhum arquivo INMET encontrado em: {pasta_inmet}")

    registros_estacao = []

    for caminho in arquivos:
        nome = os.path.basename(caminho)
        uf = _extrair_uf(nome)
        ano = _extrair_ano(caminho)

        if uf is None or ano is None:
            continue
        if ano < ano_min or ano > ano_max:
            continue
        if somente_capitais and (not _eh_estacao_da_capital(uf, nome)):
            continue

        cabecalho = _detectar_linha_cabecalho(caminho)
        df = pd.read_csv(
            caminho,
            sep=";",
            skiprows=cabecalho,
            encoding="latin1",
            dtype=str,
        )

        col_chuva = _encontrar_coluna_precipitacao(list(df.columns))
        if col_chuva is None:
            continue

        chuva = (
            df[col_chuva]
            .astype(str)
            .str.strip()
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
            .replace({"": None, "-9999": None, "-9999.0": None})
        )
        chuva = pd.to_numeric(chuva, errors="coerce")

        if chuva.notna().sum() == 0:
            continue

        registros_estacao.append(
            {
                "Estado": uf,
                "Ano": int(ano),
                "Chuva_total_estacao": float(chuva.sum(min_count=1)),
            }
        )

    if not registros_estacao:
        raise ValueError("Nenhuma observacao valida de chuva foi encontrada no recorte informado.")

    estacoes = pd.DataFrame(registros_estacao)

    estado_ano = (
        estacoes.groupby(["Estado", "Ano"], as_index=False)["Chuva_total_estacao"]
        .mean()
        .rename(columns={"Chuva_total_estacao": "chuva_media"})
    )
    estado_ano = estado_ano.sort_values(["Estado", "Ano"]).reset_index(drop=True)

    if not agrupar_por_regiao:
        return salvar_tratado(estado_ano, "inmet-chuva-estado")

    regional = estado_ano.copy()
    regional["Regiao"] = regional["Estado"].map(MAPA_REGIOES)
    regional = regional.dropna(subset=["Regiao"])

    regiao_ano = (
        regional.groupby(["Regiao", "Ano"], as_index=False)["chuva_media"]
        .mean()
    )
    regiao_ano = ordenar_regioes(regiao_ano, coluna_regiao="Regiao", coluna_ano="Ano")

    return salvar_tratado(regiao_ano, "inmet-chuva-regiao")
