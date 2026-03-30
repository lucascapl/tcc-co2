import pandas as pd

from linha_boxplot import grafico_linha_co2_brasil, boxplot_co2_por_regiao
from shapiro import shapiro_series_temporais_por_regiao
from scatter_plot import scatter_co2_vs_todas
from utils import agregar_por_regiao_ano

CAMINHO_DF = "bases/tratadas/dataframe_principal_tratado.csv"


def main():
    df_principal = pd.read_csv(CAMINHO_DF)

    print(df_principal.head())

    # gráfico geral
    grafico_linha_co2_brasil(df_principal, salvar=True)

    # boxplot regional
    # boxplot_co2_por_regiao(df_principal, salvar=True)

    # série regional agregada
    df_regional = agregar_por_regiao_ano(df_principal, ignorar_colunas=["IDHM"])
    print(df_regional.head())

    # shapiro
    resultado_shapiro = shapiro_series_temporais_por_regiao(
        df_principal,
        ignorar_colunas=["IDHM"]
    )
    print(resultado_shapiro)
    resultado_shapiro.to_csv("bases/tratadas/shapiro_por_regiao.csv", index=False)

    # scatter plots
    scatter_co2_vs_todas(
        df_principal,
        ignorar_colunas=["IDHM"],
        salvar=True,
        versao="limpo"
    )


if __name__ == "__main__":
    main()