import pandas as pd

from linha_boxplot import (
    grafico_linha_co2_brasil,
    grafico_linha_variavel_por_regiao,
    boxplots_todas_variaveis_por_regiao_ano,
)
from shapiro import shapiro_series_temporais_por_regiao
from scatter_plot import scatter_co2_vs_todas
from histogramas import histogramas_todas_variaveis_por_regiao
from missing_values import preparar_df_para_analise, relatorio_missing_values
from utils import agregar_por_regiao_ano
from pearson import correlacao_pearson_por_regiao
from spearman import correlacao_spearman_por_regiao

CAMINHO_DF = "bases/tratadas/dataframe_principal_tratado.csv"


def main():
    df_principal = pd.read_csv(CAMINHO_DF)

    print("=== Missing values antes do preenchimento ===")
    print(relatorio_missing_values(df_principal))

    df_principal = preparar_df_para_analise(
        df_principal,
        preencher_populacao=True,
        arredondar_populacao=True,
    )

    print("=== Missing values após o preenchimento ===")
    print(relatorio_missing_values(df_principal))

    grafico_linha_co2_brasil(df_principal, salvar=True, mostrar=False)
    grafico_linha_variavel_por_regiao(
        df_principal,
        variavel="CO2_bruto",
        ignorar_colunas=["IDHM"],
        salvar=True,
        mostrar=False,
    )

    df_regional = agregar_por_regiao_ano(df_principal, ignorar_colunas=["IDHM"])
    print(df_regional.head())

    resultado_shapiro = shapiro_series_temporais_por_regiao(df_principal, ignorar_colunas=["IDHM"])
    print(resultado_shapiro)
    resultado_shapiro.to_csv("bases/tratadas/shapiro_por_regiao.csv", index=False)

    resultado_pearson = correlacao_pearson_por_regiao(df_principal, ignorar_colunas=["IDHM"])
    print(resultado_pearson)
    resultado_pearson.to_csv("bases/tratadas/pearson_por_regiao.csv", index=False)

    resultado_spearman = correlacao_spearman_por_regiao(df_principal, ignorar_colunas=["IDHM"])
    print(resultado_spearman)
    resultado_spearman.to_csv("bases/tratadas/spearman_por_regiao.csv", index=False)

    scatter_co2_vs_todas(
        df_principal,
        ignorar_colunas=["IDHM"],
        salvar=True,
        versao="limpo",
        mostrar=False,
    )

    histogramas_todas_variaveis_por_regiao(
        df_principal,
        ignorar_colunas=["IDHM"],
        bins=8,
        kde=False,
        salvar=True,
        mostrar=False,
    )

    boxplots_todas_variaveis_por_regiao_ano(
        df_principal,
        ignorar_colunas=["IDHM"],
        salvar=True,
        showfliers=False,
        mostrar=False,
    )


if __name__ == "__main__":
    main()
