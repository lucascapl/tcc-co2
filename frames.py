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

# Processar bases individualmente já agregadas por região
df_co2 = processar_co2(agrupar_por_regiao=True)
df_pop = processar_populacao(agrupar_por_regiao=True)
df_frota = processar_frota(agrupar_por_regiao=True)
df_rebanho = processar_rebanho(agrupar_por_regiao=True)
df_idhm = processar_idhm(agrupar_por_regiao=True)
df_doencas = processar_doencas_respiratorias("bases/doencas_respiratorias", agrupar_por_regiao=True)

municipio_file = "bases/ferramenta_municipio.csv"
desmatamento_file = "bases/desmatamento_inpe.csv"
df_desmatamento = processar_desmatamento(
    municipio_file,
    desmatamento_file,
    agrupar_por_regiao=True,
)

# criar dataframe principal a partir do CO2
df_principal = df_co2.copy()

# adicionar os demais dts
for df_secundario in [df_pop, df_frota, df_rebanho, df_idhm, df_doencas, df_desmatamento]:
    df_principal = df_principal.merge(df_secundario, on=["Regiao", "Ano"], how="left")

# salvar dataframe principal tratado
salvar_tratado(df_principal, "dataframe_principal_regiao")

print(df_principal.head(10))  # printa o topo
print(df_principal.tail(10))  # printa o final
