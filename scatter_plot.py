import matplotlib.pyplot as plt
import seaborn as sns
from utils import (
    base_grupo_ano,
    obter_variaveis_numericas,
    preparar_pasta_graficos,
    construir_base_defasada,
    inferir_coluna_grupo,
)


def _finalizar_plot(salvar=False, nome_arquivo=None, mostrar=True):
    if salvar and nome_arquivo:
        plt.savefig(nome_arquivo, dpi=300, bbox_inches="tight")
    if mostrar:
        plt.show()
    else:
        plt.close()


def scatter_co2_vs_variavel(
    df_base,
    variavel,
    coluna_grupo="Estado",
    coluna_co2="co2",
    coluna_ano="Ano",
    salvar=False,
    mostrar=True,
    pasta="graficos/scatterplots",
    defasagem_co2=0,
    anotar_anos=True,
):
    coluna_grupo = inferir_coluna_grupo(df_base, coluna_grupo)
    coluna_co2_plot = coluna_co2
    if defasagem_co2 != 0:
        df_base = construir_base_defasada(
            df_base,
            coluna_alvo=coluna_co2,
            coluna_grupo=coluna_grupo,
            coluna_ano=coluna_ano,
            defasagem_alvo=defasagem_co2,
        )
        coluna_co2_plot = f"{coluna_co2}_t+{defasagem_co2}"

    base_plot = df_base[[coluna_co2_plot, variavel, coluna_grupo, coluna_ano]].dropna().copy()

    g = sns.FacetGrid(
        base_plot,
        col=coluna_grupo,
        col_wrap=3,
        sharex=False,
        sharey=False,
        height=4,
    )
    g.map_dataframe(sns.scatterplot, x=coluna_co2_plot, y=variavel)
    g.map_dataframe(sns.regplot, x=coluna_co2_plot, y=variavel, scatter=False, truncate=False)

    if anotar_anos:
        for ax, (_, dados_grupo) in zip(g.axes.flat, base_plot.groupby(coluna_grupo, observed=False)):
            for _, row in dados_grupo.iterrows():
                ax.annotate(
                    str(int(row[coluna_ano])),
                    (row[coluna_co2_plot], row[variavel]),
                    fontsize=8,
                    alpha=0.7,
                )

    eixo_x = "CO2 bruto" if defasagem_co2 == 0 else f"CO2 bruto (t+{defasagem_co2})"
    g.set_axis_labels(eixo_x, variavel)
    g.set_titles("{col_name}")
    g.fig.suptitle(f"Scatter plot: {eixo_x} vs {variavel} por {coluna_grupo.lower()}", y=1.02)
    g.fig.tight_layout()

    nome_arquivo = None
    if salvar:
        preparar_pasta_graficos(pasta)
        nome_var = variavel.replace(" ", "_").replace("/", "_")
        sufixo = "" if defasagem_co2 == 0 else f"_lag{defasagem_co2}"
        nome_arquivo = f"{pasta}/scatter_co2_vs_{nome_var}_por_{coluna_grupo.lower()}{sufixo}.png"

    _finalizar_plot(salvar=salvar, nome_arquivo=nome_arquivo, mostrar=mostrar)


def scatter_co2_vs_variavel_limpo(
    df_base,
    variavel,
    coluna_grupo="Estado",
    coluna_co2="co2",
    coluna_ano="Ano",
    salvar=False,
    mostrar=True,
    pasta="graficos/scatterplots",
    defasagem_co2=0,
):
    return scatter_co2_vs_variavel(
        df_base=df_base,
        variavel=variavel,
        coluna_grupo=coluna_grupo,
        coluna_co2=coluna_co2,
        coluna_ano=coluna_ano,
        salvar=salvar,
        mostrar=mostrar,
        pasta=pasta,
        defasagem_co2=defasagem_co2,
        anotar_anos=False,
    )


def scatter_co2_vs_todas(
    df,
    coluna_grupo="Estado",
    ignorar_colunas=None,
    salvar=False,
    versao="limpo",
    mostrar=True,
    pasta="graficos/scatterplots",
    defasagem_co2=0,
    agregar_para_regiao=False,
):
    df_base = base_grupo_ano(
        df,
        coluna_grupo=coluna_grupo,
        ignorar_colunas=ignorar_colunas,
        agregar_para_regiao=agregar_para_regiao,
    )
    coluna_grupo = inferir_coluna_grupo(df_base, "Regiao" if agregar_para_regiao else coluna_grupo)
    variaveis = obter_variaveis_numericas(df_base, ignorar_colunas=ignorar_colunas)
    variaveis = [v for v in variaveis if v != "co2"]

    for var in variaveis:
        if versao == "limpo":
            scatter_co2_vs_variavel_limpo(
                df_base,
                var,
                coluna_grupo=coluna_grupo,
                salvar=salvar,
                mostrar=mostrar,
                pasta=pasta,
                defasagem_co2=defasagem_co2,
            )
        else:
            scatter_co2_vs_variavel(
                df_base,
                var,
                coluna_grupo=coluna_grupo,
                salvar=salvar,
                mostrar=mostrar,
                pasta=pasta,
                defasagem_co2=defasagem_co2,
            )

    return df_base
