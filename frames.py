# frames.py
import os
import pandas as pd

from pipelines.co2_pipe import processar_co2
from pipelines.frota_pipe import processar_frota
from pipelines.rebanho_pipe import processar_rebanho
from pipelines.combustiveis_pipe import processar_combustiveis
from pipelines.desmatamento_mapbiomas_pipe import processar_desmatamento_mapbiomas
from pipelines.inmet_pipe import processar_inmet_clima
from pipelines.area_destinada_colheita_pipe import processar_area_destinada_colheita
from pipelines.area_colhida_pipe import processar_area_colhida
from pipelines.energia_industrial_pipe import processar_consumo_energia_industrial
from pipelines.queimadas_pipe import processar_queimadas

from utils import salvar_tratado

REPROCESSAR_TUDO = True

# False => Estado/Ano
# True  => Regiao/Ano
AGRUPAR_POR_REGIAO = False
CHAVES_MERGE = ["Regiao", "Ano"] if AGRUPAR_POR_REGIAO else ["Estado", "Ano"]
SUFIXO_GRANULARIDADE = "regiao" if AGRUPAR_POR_REGIAO else "estado"

PASTA_INMET = "bases/inmet"
INMET_SOMENTE_CAPITAIS = False
INMET_PARALELO = True
# None escolhe automaticamente. Em HD mecânico, teste 4 ou 8. Em SSD/NVMe, 16 ou 32 costuma ir bem.
INMET_MAX_WORKERS = None

PASTA_QUEIMADAS = "bases/queimadas"
QUEIMADAS_PARALELO = True
QUEIMADAS_MAX_WORKERS = None  # use um inteiro, ex.: 8, se quiser controlar


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

    duplicadas = df.duplicated(CHAVES_MERGE).sum()
    if duplicadas > 0:
        raise ValueError(
            f"A base '{nome_base}' possui {duplicadas} linhas duplicadas para as chaves "
            f"{CHAVES_MERGE}. Agregue a base antes do merge."
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

# INMET rápido: temperatura e chuva no mesmo processamento, para não ler 10 mil arquivos duas vezes.
df_inmet_clima = preparar_base(
    "inmet-clima",
    processar_inmet_clima,
    pasta_inmet=PASTA_INMET,
    agrupar_por_regiao=AGRUPAR_POR_REGIAO,
    somente_capitais=INMET_SOMENTE_CAPITAIS,
    paralelo=INMET_PARALELO,
    max_workers=INMET_MAX_WORKERS,
)


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


df_queimadas = preparar_base(
    "queimadas",
    processar_queimadas,
    caminho_queimadas=PASTA_QUEIMADAS,
    agrupar_por_regiao=AGRUPAR_POR_REGIAO,
    paralelo=QUEIMADAS_PARALELO,
    max_workers=QUEIMADAS_MAX_WORKERS,
)

# Criar dataframe principal a partir do CO2.
df_principal = df_co2.copy()

# Adicionar os demais dataframes usando a granularidade escolhida.
for nome_base, df_secundario in [
    ("frota", df_frota),
    ("rebanho", df_rebanho),
    ("venda-combustiveis", df_combustiveis),
    ("desmatamento-mapbiomas", df_desmatamento_mapbiomas),
    ("inmet-clima", df_inmet_clima),
    # ("pib-percapita", df_pib_percapita),
    ("area-destinada-colheita", df_area_destinada_colheita),
    ("area-colhida", df_area_colhida),
    ("energia-industrial", df_energia_industrial),
    ("queimadas", df_queimadas),
]:
    validar_chaves(df_secundario, nome_base)
    df_principal = df_principal.merge(df_secundario, on=CHAVES_MERGE, how="left")

# Garantir ordenacao coerente do dataframe principal.
df_principal = df_principal.sort_values(CHAVES_MERGE).reset_index(drop=True)

# Salvar dataframe principal tratado.
salvar_tratado(df_principal, f"dataframe-principal-{SUFIXO_GRANULARIDADE}")
