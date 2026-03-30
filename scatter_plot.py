import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

MAPA_REGIOES = {
    "AC": "Norte", "AP": "Norte", "AM": "Norte", "PA": "Norte", "RO": "Norte", "RR": "Norte", "TO": "Norte",
    "AL": "Nordeste", "BA": "Nordeste", "CE": "Nordeste", "MA": "Nordeste", "PB": "Nordeste",
    "PE": "Nordeste", "PI": "Nordeste", "RN": "Nordeste", "SE": "Nordeste",
    "DF": "Centro-Oeste", "GO": "Centro-Oeste", "MT": "Centro-Oeste", "MS": "Centro-Oeste",
    "ES": "Sudeste", "MG": "Sudeste", "RJ": "Sudeste", "SP": "Sudeste",
    "PR": "Sul", "RS": "Sul", "SC": "Sul"
}

ORDEM_REGIOES = ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"]


def agregar_por_regiao_ano(df, coluna_estado="Estado", coluna_ano="Ano", ignorar_colunas=None):
    """
    Agrega o dataframe original para o nível Regiao + Ano.
    """
    if ignorar_colunas is None:
        ignorar_colunas = ["IDHM"]

    base = df.copy()
    base["Regiao"] = base[coluna_estado].map(MAPA_REGIOES)
    base = base.dropna(subset=["Regiao", coluna_ano])

    colunas_numericas = base.select_dtypes(include=["number"]).columns.tolist()
    variaveis = [c for c in colunas_numericas if c not in ignorar_colunas and c != coluna_ano]

    df_regional = (
        base.groupby(["Regiao", coluna_ano], as_index=False)[variaveis]
        .sum()
    )

    df_regional["Regiao"] = pd.Categorical(df_regional["Regiao"], categories=ORDEM_REGIOES, ordered=True)
    df_regional = df_regional.sort_values(["Regiao", coluna_ano]).reset_index(drop=True)

    return df_regional


def scatter_co2_vs_variavel(df_regional, variavel, coluna_co2="CO2_bruto", coluna_ano="Ano", salvar=False):
    """
    Gera scatter plot entre CO2 e uma variável, com facetas por região.
    """
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
            ax.annotate(str(int(row[coluna_ano])), (row[coluna_co2], row[variavel]), fontsize=8, alpha=0.7)

    g.set_axis_labels("CO2 bruto", variavel)
    g.set_titles("{col_name}")
    g.fig.suptitle(f"Scatter plot: CO2_bruto vs {variavel}", y=1.02)
    g.fig.tight_layout()

    if salvar:
        nome_arquivo = f"scatter_co2_vs_{variavel.replace(' ', '_').replace('/', '_')}.png"
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
        nome_arquivo = f"scatter_co2_vs_{variavel.replace(' ', '_').replace('/', '_')}.png"
        plt.savefig(nome_arquivo, dpi=300, bbox_inches="tight")

    plt.show()