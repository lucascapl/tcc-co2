# frame.py
import pandas as pd
from pipelines.co2_pipe import processar_co2
from pipelines.frota_pipe import processar_frota
from pipelines.rebanho_pipe import processar_rebanho
from pipelines.doencas_respiratorias_pipe import processar_doencas_respiratorias
from pipelines.combustiveis_pipe import processar_combustiveis
from pipelines.desmatamento_mapbiomas_pipe import processar_desmatamento_mapbiomas

from utils import salvar_tratado

# Processar bases individualmente já agregadas por região
df_co2 = processar_co2(agrupar_por_regiao=True)
df_frota = processar_frota(agrupar_por_regiao=True)
df_rebanho = processar_rebanho(agrupar_por_regiao=True)
df_doencas = processar_doencas_respiratorias("bases/doencas_respiratorias", agrupar_por_regiao=True)
df_combustiveis = processar_combustiveis(agrupar_por_regiao=True)
df_desmatamento_mapbiomas = processar_desmatamento_mapbiomas(agrupar_por_regiao=True)

# criar dataframe principal a partir do CO2
df_principal = df_co2.copy()

# adicionar os demais dts
for df_secundario in [
    df_frota, 
    df_rebanho, 
    df_doencas,
    df_combustiveis,
    df_desmatamento_mapbiomas,
]:
    df_principal = df_principal.merge(df_secundario, on=["Regiao", "Ano"], how="left")

# salvar dataframe principal tratado
salvar_tratado(df_principal, "dataframe_principal")
