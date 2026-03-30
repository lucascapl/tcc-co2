import os
import matplotlib.pyplot as plt
import seaborn as sns

from utils import agregar_por_regiao_ano, obter_variaveis_numericas, preparar_pasta_graficos

sns.set_theme(style="whitegrid")


def histograma_variavel_por_regiao(
    df_regional,
    variavel,
    bins=10,
    kde=True,
    salvar=False,
    pasta="graficos"
):

    base_plot = df_regional[["Regiao", "Ano", variavel]].dropna().copy()

    g = sns.FacetGrid(
        base_plot,
        col="Regiao",
        col_wrap=3,
        sharex=False,
        sharey=False,
        height=4
    )

    g.map_dataframe(
        sns.histplot,
        x=variavel,
        bins=bins,
        kde=kde
    )

    g.set_axis_labels(variavel, "Frequência")
    g.set_titles("{col_name}")
    g.fig.suptitle(f"Histograma de {variavel} por região", y=1.02)
    g.fig.tight_layout()

    if salvar:
        preparar_pasta_graficos(pasta)
        nome_arquivo = f"{pasta}/histograma_{variavel.replace(' ', '_').replace('/', '_')}.png"
        plt.savefig(nome_arquivo, dpi=300, bbox_inches="tight")

    plt.show()


def histograma_variavel_geral(
    df_regional,
    variavel,
    bins=10,
    kde=True,
    salvar=False,
    pasta="graficos"
):
    
    ##Gera um histograma geral da variável já agregada por Regiao + Ano.

    base_plot = df_regional[[variavel]].dropna().copy()

    plt.figure(figsize=(8, 5))
    sns.histplot(base_plot[variavel], bins=bins, kde=kde)

    plt.title(f"Histograma geral de {variavel} (Região + Ano)")
    plt.xlabel(variavel)
    plt.ylabel("Frequência")
    plt.tight_layout()

    if salvar:
        preparar_pasta_graficos(pasta)
        nome_arquivo = f"{pasta}/histograma_geral_{variavel.replace(' ', '_').replace('/', '_')}.png"
        plt.savefig(nome_arquivo, dpi=300, bbox_inches="tight")

    plt.show()


def histogramas_todas_variaveis_por_regiao(
    df,
    ignorar_colunas=None,
    bins=10,
    kde=True,
    salvar=False,
    pasta="graficos"
):
    """
    Agrega por Regiao + Ano e gera histogramas por região
    para todas as variáveis numéricas, exceto CO2 se você quiser filtrar depois.
    """
    df_regional = agregar_por_regiao_ano(df, ignorar_colunas=ignorar_colunas)
    variaveis = obter_variaveis_numericas(
        df_regional,
        coluna_ano="Ano",
        ignorar_colunas=ignorar_colunas
    )

    for var in variaveis:
        histograma_variavel_por_regiao(
            df_regional,
            variavel=var,
            bins=bins,
            kde=kde,
            salvar=salvar,
            pasta=pasta
        )

    return df_regional


def histogramas_co2_vs_todas(
    df,
    ignorar_colunas=None,
    bins=10,
    kde=True,
    salvar=False,
    pasta="graficos"
):
    """
    Gera histogramas de todas as variáveis exceto Ano e IDHM,
    já com agregação Regiao + Ano.
    """
    df_regional = agregar_por_regiao_ano(df, ignorar_colunas=ignorar_colunas)
    variaveis = obter_variaveis_numericas(
        df_regional,
        coluna_ano="Ano",
        ignorar_colunas=ignorar_colunas
    )

    for var in variaveis:
        histograma_variavel_por_regiao(
            df_regional,
            variavel=var,
            bins=bins,
            kde=kde,
            salvar=salvar,
            pasta=pasta
        )

    return df_regional