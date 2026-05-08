import matplotlib.pyplot as plt
import seaborn as sns

from utils import base_grupo_ano, obter_variaveis_numericas, preparar_pasta_graficos, inferir_coluna_grupo

sns.set_theme(style="whitegrid")


def _finalizar_plot(salvar=False, nome_arquivo=None, mostrar=True):
    if salvar and nome_arquivo:
        plt.savefig(nome_arquivo, dpi=300, bbox_inches="tight")
    if mostrar:
        plt.show()
    else:
        plt.close()


def histograma_variavel_por_grupo(
    df_base,
    variavel,
    coluna_grupo="Estado",
    coluna_ano="Ano",
    bins=10,
    kde=True,
    salvar=False,
    pasta="graficos/histogramas",
    mostrar=True,
):
    coluna_grupo = inferir_coluna_grupo(df_base, coluna_grupo)
    base_plot = df_base[[coluna_grupo, coluna_ano, variavel]].dropna().copy()

    g = sns.FacetGrid(
        base_plot,
        col=coluna_grupo,
        col_wrap=3,
        sharex=False,
        sharey=False,
        height=4,
    )
    g.map_dataframe(sns.histplot, x=variavel, bins=bins, kde=kde)

    g.set_axis_labels(variavel, "Frequência")
    g.set_titles("{col_name}")
    g.fig.suptitle(f"Histograma de {variavel} por {coluna_grupo.lower()}", y=1.02)
    g.fig.tight_layout()

    nome_arquivo = None
    if salvar:
        preparar_pasta_graficos(pasta)
        nome = variavel.replace(" ", "_").replace("/", "_")
        nome_arquivo = f"{pasta}/histograma_{nome}_por_{coluna_grupo.lower()}.png"

    _finalizar_plot(salvar=salvar, nome_arquivo=nome_arquivo, mostrar=mostrar)


def histograma_variavel_geral(
    df_base,
    variavel,
    coluna_grupo="Estado",
    bins=10,
    kde=True,
    salvar=False,
    pasta="graficos/histogramas",
    mostrar=True,
):
    base_plot = df_base[[variavel]].dropna().copy()

    plt.figure(figsize=(8, 5))
    sns.histplot(base_plot[variavel], bins=bins, kde=kde)
    plt.title(f"Histograma geral de {variavel} ({coluna_grupo} + Ano)")
    plt.xlabel(variavel)
    plt.ylabel("Frequência")
    plt.tight_layout()

    nome_arquivo = None
    if salvar:
        preparar_pasta_graficos(pasta)
        nome = variavel.replace(" ", "_").replace("/", "_")
        nome_arquivo = f"{pasta}/histograma_geral_{nome}.png"

    _finalizar_plot(salvar=salvar, nome_arquivo=nome_arquivo, mostrar=mostrar)


def histogramas_todas_variaveis_por_grupo(
    df,
    coluna_grupo="Estado",
    ignorar_colunas=None,
    bins=10,
    kde=True,
    salvar=False,
    pasta="graficos/histogramas",
    mostrar=True,
    agregar_para_regiao=False,
):
    df_base = base_grupo_ano(
        df,
        coluna_grupo=coluna_grupo,
        ignorar_colunas=ignorar_colunas,
        agregar_para_regiao=agregar_para_regiao,
    )
    coluna_grupo = inferir_coluna_grupo(df_base, "Regiao" if agregar_para_regiao else coluna_grupo)
    variaveis = obter_variaveis_numericas(df_base, coluna_ano="Ano", ignorar_colunas=ignorar_colunas)

    for var in variaveis:
        histograma_variavel_por_grupo(
            df_base,
            variavel=var,
            coluna_grupo=coluna_grupo,
            bins=bins,
            kde=kde,
            salvar=salvar,
            pasta=pasta,
            mostrar=mostrar,
        )

    return df_base


def histogramas_co2_vs_todas(
    df,
    coluna_grupo="Estado",
    ignorar_colunas=None,
    bins=10,
    kde=True,
    salvar=False,
    pasta="graficos/histogramas",
    mostrar=True,
    agregar_para_regiao=False,
):
    df_base = base_grupo_ano(
        df,
        coluna_grupo=coluna_grupo,
        ignorar_colunas=ignorar_colunas,
        agregar_para_regiao=agregar_para_regiao,
    )
    coluna_grupo = inferir_coluna_grupo(df_base, "Regiao" if agregar_para_regiao else coluna_grupo)
    variaveis = obter_variaveis_numericas(df_base, coluna_ano="Ano", ignorar_colunas=ignorar_colunas)
    variaveis = [v for v in variaveis if v != "co2"]

    for var in variaveis:
        histograma_variavel_por_grupo(
            df_base,
            variavel=var,
            coluna_grupo=coluna_grupo,
            bins=bins,
            kde=kde,
            salvar=salvar,
            pasta=pasta,
            mostrar=mostrar,
        )

    return df_base


def histograma_variavel_por_regiao(df_regional, variavel, **kwargs):
    kwargs.pop("coluna_grupo", None)
    return histograma_variavel_por_grupo(df_regional, variavel, coluna_grupo="Regiao", **kwargs)


def histogramas_todas_variaveis_por_regiao(df, **kwargs):
    kwargs.pop("coluna_grupo", None)
    kwargs.pop("agregar_para_regiao", None)
    return histogramas_todas_variaveis_por_grupo(df, coluna_grupo="Regiao", agregar_para_regiao=True, **kwargs)
