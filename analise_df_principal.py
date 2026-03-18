import pandas as pd
from visualizacoes import grafico_linha_co2_brasil, boxplot_co2_por_regiao
from analises import correlacao_pop_co2_por_ano, correlacao_pop_co2_por_uf

# carregar o dataFrame de um arquivo CSV
df_principal = pd.read_csv("bases/tratadas/dataframe_principal_tratado.csv")  # Carregar de CSV


print(df_principal.head())  # visualizar as primeiras linhas

# Realizar análises, por exemplo, verificando missing values
# missing_values = df_principal.isnull().sum()
# print(missing_values[missing_values > 0])

grafico_linha_co2_brasil(df_principal, salvar=True)

#distribuição completa de todos os valores observados ao longo dos anos para os estados daquela região
boxplot_co2_por_regiao(df_principal, salvar=True) 
