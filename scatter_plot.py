import math
import matplotlib.pyplot as plt
import seaborn as sns
from utils import preparar_base_analitica, obter_variaveis_numericas, preparar_pasta_graficos, obter_coluna_grupo


def _finalizar_plot(salvar=False, nome_arquivo=None, mostrar=True):
    if salvar and nome_arquivo:
        plt.savefig(nome_arquivo, dpi=300, bbox_inches="tight")
    if mostrar:
        plt.show()
    else:
        plt.close()


def scatter_co2_vs_variavel(df, variavel, nivel="regiao", coluna_co2="CO2_bruto", coluna_ano="Ano", ignorar_colunas=None, salvar=False, mostrar=True, pasta="graficos", anotar_ano=False):
    base = preparar_base_analitica(df, nivel=nivel, ignorar_colunas=ignorar_colunas)
    coluna_grupo = obter_coluna_grupo(nivel)
    plot_df = base[[coluna_co2, variavel, coluna_grupo, coluna_ano]].dropna().copy()
    grupos = list(plot_df[coluna_grupo].dropna().unique())

    ncols = 3 if nivel == "regiao" else 4
    nrows = math.ceil(len(grupos) / ncols)
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(5 * ncols, 4 * nrows))
    axes = axes.flatten() if hasattr(axes, "flatten") else [axes]

    for ax, grupo in zip(axes, grupos):
        dados = plot_df.loc[plot_df[coluna_grupo] == grupo]
        sns.scatterplot(data=dados, x=coluna_co2, y=variavel, ax=ax)
        sns.regplot(data=dados, x=coluna_co2, y=variavel, scatter=False, truncate=False, ax=ax)
        if anotar_ano:
            for _, row in dados.iterrows():
                ax.annotate(str(int(row[coluna_ano])), (row[coluna_co2], row[variavel]), fontsize=7, alpha=0.65)
        ax.set_title(str(grupo))
        ax.set_xlabel("CO2 bruto")
        ax.set_ylabel(variavel)

    for ax in axes[len(grupos):]:
        ax.set_visible(False)

    fig.suptitle(f"CO2_bruto vs {variavel} por {coluna_grupo.lower()}", y=1.02)
    fig.tight_layout()

    nome_arquivo = None
    if salvar:
        preparar_pasta_graficos(pasta)
        nome = variavel.replace(" ", "_").replace("/", "_")
        nome_arquivo = f"{pasta}/scatter_co2_vs_{nome}_por_{coluna_grupo.lower()}.png"

    _finalizar_plot(salvar=salvar, nome_arquivo=nome_arquivo, mostrar=mostrar)


def scatter_co2_vs_todas(df, nivel="regiao", ignorar_colunas=None, salvar=False, mostrar=True, pasta="graficos", anotar_ano=False):
    base = preparar_base_analitica(df, nivel=nivel, ignorar_colunas=ignorar_colunas)
    variaveis = obter_variaveis_numericas(base, ignorar_colunas=ignorar_colunas)
    variaveis = [v for v in variaveis if v != "CO2_bruto"]
    for var in variaveis:
        scatter_co2_vs_variavel(df, variavel=var, nivel=nivel, ignorar_colunas=ignorar_colunas, salvar=salvar, mostrar=mostrar, pasta=pasta, anotar_ano=anotar_ano)
    return base
