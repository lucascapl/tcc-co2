# frame.py
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

from utils import salvar_tratado

REPROCESSAR_TUDO = False


def carregar_ou_processar(nome_base_tratada: str, funcao_processamento, *args, **kwargs) -> pd.DataFrame:
    caminho = f"bases/tratadas/{nome_base_tratada}-tratada.csv"

    if (not REPROCESSAR_TUDO) and os.path.exists(caminho):
        print(f"[cache] Carregando base tratada existente: {caminho}")
        return pd.read_csv(caminho)

    print(f"[processando] Gerando base: {nome_base_tratada}")
    return funcao_processamento(*args, **kwargs)

# Processar bases individualmente já agregadas por região
df_co2 = carregar_ou_processar("co2-regiao", processar_co2, agrupar_por_regiao=True)
df_frota = carregar_ou_processar("frota-regiao", processar_frota, agrupar_por_regiao=True)
df_rebanho = carregar_ou_processar("rebanho-regiao", processar_rebanho, agrupar_por_regiao=True)
df_doencas = carregar_ou_processar(
    "doencas-resp-regiao",
    processar_doencas_respiratorias,
    "bases/doencas_respiratorias",
    agrupar_por_regiao=True,
)
df_combustiveis = carregar_ou_processar("venda-combustiveis", processar_combustiveis, agrupar_por_regiao=True)
df_desmatamento_mapbiomas = carregar_ou_processar(
    "desmatamento-mapbiomas",
    processar_desmatamento_mapbiomas,
    agrupar_por_regiao=True,
)
df_inmet_temperatura = carregar_ou_processar(
    "inmet-temp-regiao",
    processar_inmet_temperatura,
    agrupar_por_regiao=True,
)
df_inmet_chuva = carregar_ou_processar(
    "inmet-chuva-regiao",
    processar_inmet_chuva,
    agrupar_por_regiao=True,
)
df_pib_percapita = carregar_ou_processar(
    "pib-percapita-regiao",
    processar_pib_per_capita,
    agrupar_por_regiao=True,
)

# criar dataframe principal a partir do CO2
df_principal = df_co2.copy()

# adicionar os demais dts
for df_secundario in [
    df_frota, 
    df_rebanho, 
    df_doencas,
    df_combustiveis,
    df_desmatamento_mapbiomas,
    df_inmet_temperatura,
    df_inmet_chuva,
    df_pib_percapita,
]:
    df_principal = df_principal.merge(df_secundario, on=["Regiao", "Ano"], how="left")

# salvar dataframe principal tratado
salvar_tratado(df_principal, "dataframe-principal")
