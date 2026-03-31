import os
import pandas as pd

from linha_boxplot import (
    grafico_linha_co2_brasil,
    grafico_linha_variavel,
    boxplots_todas_variaveis,
)
from shapiro import shapiro_series_temporais
from scatter_plot import scatter_co2_vs_todas
from histogramas import histogramas_todas_variaveis
from missing_values import preparar_df_para_analise, relatorio_missing_values
from utils import preparar_base_analitica, preparar_pasta_graficos
from pearson import correlacao_pearson
from spearman import correlacao_spearman

CAMINHO_DF = "bases/tratadas/dataframe_principal_tratado.csv"


def rodar_analise_por_nivel(df_principal, nivel="regiao", ignorar_colunas=None, pasta_saida="bases/tratadas", pasta_graficos_base="graficos"):
    if ignorar_colunas is None:
        ignorar_colunas = ["IDHM"]

    preparar_pasta_graficos(pasta_graficos_base)
    os.makedirs(pasta_saida, exist_ok=True)
    pasta_graficos = f"{pasta_graficos_base}/{nivel}"

    base = preparar_base_analitica(df_principal, nivel=nivel, ignorar_colunas=ignorar_colunas)
    print(f"=== Base analítica {nivel}-ano ===")
    print(base.head())

    resultado_shapiro = shapiro_series_temporais(df_principal, nivel=nivel, ignorar_colunas=ignorar_colunas)
    print(resultado_shapiro)
    resultado_shapiro.to_csv(f"{pasta_saida}/shapiro_por_{nivel}.csv", index=False)

    resultado_pearson = correlacao_pearson(df_principal, nivel=nivel, ignorar_colunas=ignorar_colunas)
    print(resultado_pearson)
    resultado_pearson.to_csv(f"{pasta_saida}/pearson_por_{nivel}.csv", index=False)

    resultado_spearman = correlacao_spearman(df_principal, nivel=nivel, ignorar_colunas=ignorar_colunas)
    print(resultado_spearman)
    resultado_spearman.to_csv(f"{pasta_saida}/spearman_por_{nivel}.csv", index=False)

    grafico_linha_variavel(df_principal, variavel="CO2_bruto", nivel=nivel, ignorar_colunas=ignorar_colunas, salvar=True, pasta=pasta_graficos, mostrar=False)
    scatter_co2_vs_todas(df_principal, nivel=nivel, ignorar_colunas=ignorar_colunas, salvar=True, mostrar=False, pasta=pasta_graficos)
    histogramas_todas_variaveis(df_principal, nivel=nivel, ignorar_colunas=ignorar_colunas, bins=8, kde=False, salvar=True, mostrar=False, pasta=pasta_graficos)
    boxplots_todas_variaveis(df_principal, nivel=nivel, ignorar_colunas=ignorar_colunas, salvar=True, showfliers=False, mostrar=False, pasta=pasta_graficos)


def main(niveis=("regiao", "estado")):
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

    for nivel in niveis:
        rodar_analise_por_nivel(df_principal, nivel=nivel)


if __name__ == "__main__":
    main()
