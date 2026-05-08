# frames.py
import os
import pandas as pd

from pipelines.co2_pipe import processar_co2
from pipelines.frota_pipe import processar_frota
from pipelines.rebanho_pipe import processar_rebanho
from pipelines.doencas_respiratorias_pipe import processar_doencas_respiratorias
from pipelines.combustiveis_pipe import processar_combustiveis
from pipelines.desmatamento_mapbiomas_pipe import processar_desmatamento_mapbiomas
from pipelines.inmet_pipe import processar_inmet_temperatura, processar_inmet_chuva
from pipelines.pib_pipe import processar_pib_per_capita
from pipelines.area_destinada_colheita_pipe import processar_area_destinada_colheita
from pipelines.area_colhida_pipe import processar_area_colhida
from pipelines.energia_industrial_pipe import processar_consumo_energia_industrial

from utils import salvar_tratado

REPROCESSAR_TUDO = True

# Escolha aqui a granularidade do dataframe principal:
# False => Estado/Ano
# True  => Regiao/Ano
AGRUPAR_POR_REGIAO = False
CHAVES_MERGE = ["Regiao", "Ano"] if AGRUPAR_POR_REGIAO else ["Estado", "Ano"]
SUFIXO_GRANULARIDADE = "regiao" if AGRUPAR_POR_REGIAO else "estado"


def carregar_ou_processar(nome_base_tratada: str, funcao_processamento, *args, **kwargs) -> pd.DataFrame:
    caminho = f"bases/tratadas/{nome_base_tratada}-tratada.csv"

    if (not REPROCESSAR_TUDO) and os.path.exists(caminho):
        print(f"[cache] Carregando base tratada existente: {caminho}")
        return pd.read_csv(caminho)

    print(f"[processando] Gerando base: {nome_base_tratada}")
    return funcao_processamento(*args, **kwargs)


def validar_chaves(df: pd.DataFrame, nome_base: str) -> None:
    chaves_faltantes = [col for col in CHAVES_MERGE if col not in df.columns]
    if chaves_faltantes:
        raise ValueError(
            f"A base '{nome_base}' nao esta na granularidade esperada "
            f"({', '.join(CHAVES_MERGE)}). Colunas ausentes: {chaves_faltantes}. "
            f"Confira se o pipeline recebeu agrupar_por_regiao={AGRUPAR_POR_REGIAO}."
        )


def preparar_base(nome_base_tratada: str, funcao_processamento, *args, **kwargs) -> pd.DataFrame:
    nome_cache = f"{nome_base_tratada}-{SUFIXO_GRANULARIDADE}"
    df = carregar_ou_processar(nome_cache, funcao_processamento, *args, **kwargs)
    validar_chaves(df, nome_base_tratada)
    return df


# Processar bases individualmente na mesma granularidade do dataframe principal.
df_co2 = preparar_base("co2", processar_co2, agrupar_por_regiao=AGRUPAR_POR_REGIAO)
df_frota = preparar_base("frota", processar_frota, agrupar_por_regiao=AGRUPAR_POR_REGIAO)
df_rebanho = preparar_base("rebanho", processar_rebanho, agrupar_por_regiao=AGRUPAR_POR_REGIAO)
df_doencas = preparar_base(
    "doencas-resp",
    processar_doencas_respiratorias,
    "bases/doencas_respiratorias",
    agrupar_por_regiao=AGRUPAR_POR_REGIAO,
)
df_combustiveis = preparar_base(
    "venda-combustiveis",
    processar_combustiveis,
    agrupar_por_regiao=AGRUPAR_POR_REGIAO,
)
df_desmatamento_mapbiomas = preparar_base(
    "desmatamento-mapbiomas",
    processar_desmatamento_mapbiomas,
    agrupar_por_regiao=AGRUPAR_POR_REGIAO,
)

"""
df_inmet_temperatura = preparar_base(
    "inmet-temp",
    processar_inmet_temperatura,
    agrupar_por_regiao=AGRUPAR_POR_REGIAO,
)
df_inmet_chuva = preparar_base(
    "inmet-chuva",
    processar_inmet_chuva,
    agrupar_por_regiao=AGRUPAR_POR_REGIAO,
)
df_pib_percapita = preparar_base(
    "pib-percapita",
    processar_pib_per_capita,
    agrupar_por_regiao=AGRUPAR_POR_REGIAO,
)
"""

df_area_destinada_colheita = preparar_base(
    "area-destinada-colheita",
    processar_area_destinada_colheita,
    agrupar_por_regiao=AGRUPAR_POR_REGIAO,
)
df_area_colhida = preparar_base(
    "area-colhida",
    processar_area_colhida,
    agrupar_por_regiao=AGRUPAR_POR_REGIAO,
)
df_energia_industrial = preparar_base(
    "energia-industrial",
    processar_consumo_energia_industrial,
    agrupar_por_regiao=AGRUPAR_POR_REGIAO,
)

# Criar dataframe principal a partir do CO2.
df_principal = df_co2.copy()

# Adicionar os demais dataframes usando a granularidade escolhida.
for nome_base, df_secundario in [
    ("frota", df_frota),
    ("rebanho", df_rebanho),
    ("doencas-resp", df_doencas),
    ("venda-combustiveis", df_combustiveis),
    ("desmatamento-mapbiomas", df_desmatamento_mapbiomas),
    # ("inmet-temp", df_inmet_temperatura),
    # ("inmet-chuva", df_inmet_chuva),
    # ("pib-percapita", df_pib_percapita),
    ("area-destinada-colheita", df_area_destinada_colheita),
    ("area-colhida", df_area_colhida),
    ("energia-industrial", df_energia_industrial),
]:
    validar_chaves(df_secundario, nome_base)
    df_principal = df_principal.merge(df_secundario, on=CHAVES_MERGE, how="left")

# Garantir ordenacao coerente do dataframe principal.
df_principal = df_principal.sort_values(CHAVES_MERGE).reset_index(drop=True)

# Salvar dataframe principal tratado.
salvar_tratado(df_principal, f"dataframe-principal-{SUFIXO_GRANULARIDADE}")
