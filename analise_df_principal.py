import pandas as pd

# carregar o dataFrame de um arquivo CSV
df_principal = pd.read_csv("bases/tratadas/dataframe_principal_tratado.csv")  # Carregar de CSV


print(df_principal.head())  # visualizar as primeiras linhas

# Realizar análises, por exemplo, verificando missing values
missing_values = df_principal.isnull().sum()
print(missing_values[missing_values > 0])