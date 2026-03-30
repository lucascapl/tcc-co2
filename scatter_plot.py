import matplotlib.pyplot as plt
import seaborn as sns
from utils import agregar_por_regiao_ano, obter_variaveis_numericas


def scatter_co2_vs_variavel(df_regional, variavel, coluna_co2="CO2_bruto", coluna_ano="Ano", salvar=False):
    base_plot = df_regional[[coluna_co2, variavel, "Regiao", coluna_ano]].dropna().copy()

    g = sns.FacetGrid(
        base_plot,
        col="Regiao",
        col_wrap=3,
        sharex=False,
        sharey=False,
        height=4
    )

    g.map_dataframe(sns.scatterplot, x=coluna_co2, y=variavel)
    g.map_dataframe(sns.regplot, x=coluna_co2, y=variavel, scatter=False, truncate=False)

    for ax, (_, dados_regiao) in zip(g.axes.flat, base_plot.groupby("Regiao", observed=False)):
        for _, row in dados_regiao.iterrows():
            ax.annotate(
                str(int(row[coluna_ano])),
                (row[coluna_co2], row[variavel]),
                fontsize=8,
                alpha=0.7
            )

    g.set_axis_labels("CO2 bruto", variavel)
    g.set_titles("{col_name}")
    g.fig.suptitle(f"Scatter plot: CO2_bruto vs {variavel}", y=1.02)
    g.fig.tight_layout()

    if salvar:
        nome_arquivo = f"graficos/scatter_co2_vs_{variavel.replace(' ', '_').replace('/', '_')}.png"
        plt.savefig(nome_arquivo, dpi=300, bbox_inches="tight")

    plt.show()


def scatter_co2_vs_variavel_limpo(df_regional, variavel, coluna_co2="CO2_bruto", salvar=False):
    base_plot = df_regional[[coluna_co2, variavel, "Regiao"]].dropna().copy()

    g = sns.FacetGrid(
        base_plot,
        col="Regiao",
        col_wrap=3,
        sharex=False,
        sharey=False,
        height=4
    )

    g.map_dataframe(sns.scatterplot, x=coluna_co2, y=variavel)
    g.map_dataframe(sns.regplot, x=coluna_co2, y=variavel, scatter=False, truncate=False)

    g.set_axis_labels("CO2 bruto", variavel)
    g.set_titles("{col_name}")
    g.fig.suptitle(f"CO2_bruto vs {variavel}", y=1.02)
    g.fig.tight_layout()

    if salvar:
        nome_arquivo = f"graficos/scatter_co2_vs_{variavel.replace(' ', '_').replace('/', '_')}.png"
        plt.savefig(nome_arquivo, dpi=300, bbox_inches="tight")

    plt.show()


def scatter_co2_vs_todas(df, ignorar_colunas=None, salvar=False, versao="limpo"):
    df_regional = agregar_por_regiao_ano(df, ignorar_colunas=ignorar_colunas)
    variaveis = obter_variaveis_numericas(df_regional, ignorar_colunas=ignorar_colunas)

    variaveis = [v for v in variaveis if v != "CO2_bruto"]

    for var in variaveis:
        if versao == "limpo":
            scatter_co2_vs_variavel_limpo(df_regional, var, salvar=salvar)
        else:
            scatter_co2_vs_variavel(df_regional, var, salvar=salvar)

    return df_regional