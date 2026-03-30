import pandas as pd
from visualizacoes import grafico_linha_co2_brasil, boxplot_co2_por_regiao
from shapiro import shapiro_series_temporais_por_regiao
from scatter_plot import scatter_co2_vs_variavel, agregar_por_regiao_ano

# carregar o dataFrame de um arquivo CSV
df_principal = pd.read_csv("bases/tratadas/dataframe_principal_tratado.csv")  # Carregar de CSV


print(df_principal.head())  # visualizar as primeiras linhas

# Realizar análises, por exemplo, verificando missing values
# missing_values = df_principal.isnull().sum()
# print(missing_values[missing_values > 0])

grafico_linha_co2_brasil(df_principal, salvar=True)

#distribuição completa de todos os valores observados ao longo dos anos para os estados daquela região
#boxplot_co2_por_regiao(df_principal, salvar=True) 

'''resultado_shapiro_normalidade = shapiro_series_temporais_por_regiao(
    df_principal,
    ignorar_colunas=["IDHM"],
    agregacao="sum"
)'''
df_regional = agregar_por_regiao_ano(df_principal, ignorar_colunas=["IDHM"])

scatter_co2_vs_variavel(df_regional, "Frota_total")
scatter_co2_vs_variavel(df_regional, "Populacao")
scatter_co2_vs_variavel(df_regional, "Rebanho_total")
scatter_co2_vs_variavel(df_regional, "Internacoes_Respiratorias")
scatter_co2_vs_variavel(df_regional, "Area_Desmatada km2")