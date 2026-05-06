import matplotlib.pyplot as plt
import seaborn as sns
from utils import (
    base_regional_ano,
    obter_variaveis_numericas,
    preparar_pasta_graficos,
    construir_base_defasada,
)


def _finalizar_plot(salvar=False, nome_arquivo=None, mostrar=True):
    if salvar and nome_arquivo:
        plt.savefig(nome_arquivo, dpi=300, bbox_inches="tight")
    if mostrar:
        plt.show()
    else:
        plt.close()


def scatter_co2_vs_variavel(
    df_regional,
    variavel,
    coluna_co2="co2",
    coluna_ano="Ano",
    salvar=False,
    mostrar=True,
    pasta="graficos/scatterplots",
    defasagem_co2=0,
):
    coluna_co2_plot = coluna_co2
    if defasagem_co2 != 0:
        df_regional = construir_base_defasada(
            df_regional,
            coluna_alvo=coluna_co2,
            coluna_ano=coluna_ano,
            defasagem_alvo=defasagem_co2,
        )
        coluna_co2_plot = f"{coluna_co2}_t+{defasagem_co2}"

    base_plot = df_regional[[coluna_co2_plot, variavel, "Regiao", coluna_ano]].dropna().copy()

    g = sns.FacetGrid(
        base_plot,
        col="Regiao",
        col_wrap=3,
        sharex=False,
        sharey=False,
        height=4
    )

    g.map_dataframe(sns.scatterplot, x=coluna_co2_plot, y=variavel)
    g.map_dataframe(sns.regplot, x=coluna_co2_plot, y=variavel, scatter=False, truncate=False)

    for ax, (_, dados_regiao) in zip(g.axes.flat, base_plot.groupby("Regiao", observed=False)):
        for _, row in dados_regiao.iterrows():
            ax.annotate(
                str(int(row[coluna_ano])),
                (row[coluna_co2_plot], row[variavel]),
                fontsize=8,
                alpha=0.7
            )

    eixo_x = "CO2 bruto" if defasagem_co2 == 0 else f"CO2 bruto (t+{defasagem_co2})"
    g.set_axis_labels(eixo_x, variavel)
    g.set_titles("{col_name}")
    g.fig.suptitle(f"Scatter plot: {eixo_x} vs {variavel}", y=1.02)
    g.fig.tight_layout()

    nome_arquivo = None
    if salvar:
        preparar_pasta_graficos(pasta)
        nome_var = variavel.replace(' ', '_').replace('/', '_')
        sufixo = "" if defasagem_co2 == 0 else f"_lag{defasagem_co2}"
        nome_arquivo = f"{pasta}/scatter_co2_vs_{nome_var}{sufixo}.png"

    _finalizar_plot(salvar=salvar, nome_arquivo=nome_arquivo, mostrar=mostrar)


def scatter_co2_vs_variavel_limpo(
    df_regional,
    variavel,
    coluna_co2="co2",
    coluna_ano="Ano",
    salvar=False,
    mostrar=True,
    pasta="graficos/scatterplots",
    defasagem_co2=0,
):
    coluna_co2_plot = coluna_co2
    if defasagem_co2 != 0:
        df_regional = construir_base_defasada(
            df_regional,
            coluna_alvo=coluna_co2,
            coluna_ano=coluna_ano,
            defasagem_alvo=defasagem_co2,
        )
        coluna_co2_plot = f"{coluna_co2}_t+{defasagem_co2}"

    base_plot = df_regional[[coluna_co2_plot, variavel, "Regiao", coluna_ano]].dropna().copy()

    g = sns.FacetGrid(
        base_plot,
        col="Regiao",
        col_wrap=3,
        sharex=False,
        sharey=False,
        height=4
    )

    g.map_dataframe(sns.scatterplot, x=coluna_co2_plot, y=variavel)
    g.map_dataframe(sns.regplot, x=coluna_co2_plot, y=variavel, scatter=False, truncate=False)

    eixo_x = "CO2 bruto" if defasagem_co2 == 0 else f"CO2 bruto (t+{defasagem_co2})"
    g.set_axis_labels(eixo_x, variavel)
    g.set_titles("{col_name}")
    g.fig.suptitle(f"{eixo_x} vs {variavel}", y=1.02)
    g.fig.tight_layout()

    nome_arquivo = None
    if salvar:
        preparar_pasta_graficos(pasta)
        nome_var = variavel.replace(' ', '_').replace('/', '_')
        sufixo = "" if defasagem_co2 == 0 else f"_lag{defasagem_co2}"
        nome_arquivo = f"{pasta}/scatter_co2_vs_{nome_var}{sufixo}.png"

    _finalizar_plot(salvar=salvar, nome_arquivo=nome_arquivo, mostrar=mostrar)


def scatter_co2_vs_todas(
    df,
    ignorar_colunas=None,
    salvar=False,
    versao="limpo",
    mostrar=True,
    pasta="graficos/scatterplots",
    defasagem_co2=0,
):
    df_regional = base_regional_ano(df, ignorar_colunas=ignorar_colunas)
    variaveis = obter_variaveis_numericas(df_regional, ignorar_colunas=ignorar_colunas)

    variaveis = [v for v in variaveis if v != "co2"]

    for var in variaveis:
        if versao == "limpo":
            scatter_co2_vs_variavel_limpo(
                df_regional,
                var,
                salvar=salvar,
                mostrar=mostrar,
                pasta=pasta,
                defasagem_co2=defasagem_co2,
            )
        else:
            scatter_co2_vs_variavel(
                df_regional,
                var,
                salvar=salvar,
                mostrar=mostrar,
                pasta=pasta,
                defasagem_co2=defasagem_co2,
            )

    return df_regional
