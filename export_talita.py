import pandas as pd
df = pd.read_csv("bases/tratadas/dataframe_principal_tratado.csv")

df_15 = df.head(50)

df_15.to_csv("csv_lucas_leal_co2.csv", index=False)