# frame.py
import pandas as pd
from pipelines.co2_pipe import processar_co2
from pipelines.populacao_pipe import processar_populacao
from pipelines.frota_pipe import processar_frota
from pipelines.rebanho_pipe import processar_rebanho
from pipelines.idhm_pipe import processar_idhm
from pipelines.doencas_respiratorias_pipe import processar_doencas_respiratorias
from pipelines.desmatamento_pipe import processar_desmatamento

from utils import salvar_tratado

# Processar bases individualmente
df_co2 = processar_co2()
df_pop = processar_populacao()
df_frota = processar_frota()
df_rebanho = processar_rebanho()
df_idhm = processar_idhm()
df_doencas = processar_doencas_respiratorias("bases/doencas_respiratorias")

municipio_file = "bases/ferramenta_municipio.csv"
desmatamento_file = "bases/desmatamento_inpe.csv"
df_desmatamento = processar_desmatamento(municipio_file, desmatamento_file)

# criar dataframe principal a partir do CO2
df_principal = df_co2.copy()

# adicionar os demais dts
df_principal = df_principal.merge(df_pop, on=["Estado", "Ano"], how="left")
df_principal = df_principal.merge(df_frota, on=["Estado", "Ano"], how="left")
df_principal = df_principal.merge(df_rebanho, on=["Estado","Ano"], how="left")
df_principal = df_principal.merge(df_idhm, on=["Estado", "Ano"], how="left")
df_principal = df_principal.merge(df_doencas, on=["Estado", "Ano"], how="left")
df_principal = df_principal.merge(df_desmatamento, on=["Estado", "Ano"], how="left")

# salvar dataframe principal tratado
salvar_tratado(df_principal, "dataframe_principal")

print(df_principal.head(10)) #printa o topo

print(df_principal.tail(10)) #printa o final


