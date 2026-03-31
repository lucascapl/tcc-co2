import math
import matplotlib.pyplot as plt
import seaborn as sns
from utils import preparar_base_analitica, obter_variaveis_numericas, preparar_pasta_graficos, obter_coluna_grupo

sns.set_theme(style="whitegrid")


def _finalizar_plot(salvar=False, nome_arquivo=None, mostrar=True):
    if salvar and nome_arquivo:
        plt.savefig(nome_arquivo, dpi=300, bbox_inches="tight")
    if mostrar:
        plt.show()
    else:
        plt.close()


def histograma_variavel(df, variavel, nivel="regiao", ignorar_colunas=None, bins=10, kde=True, salvar=False, pasta="graficos", mostrar=True):
    base = preparar_base_analitica(df, nivel=nivel, ignorar_colunas=ignorar_colunas)
    coluna_grupo = obter_coluna_grupo(nivel)
    plot_df = base[[coluna_grupo, "Ano", variavel]].dropna().copy()
    grupos = list(plot_df[coluna_grupo].dropna().unique())

    ncols = 3 if nivel == "regiao" else 4
    nrows = math.ceil(len(grupos) / ncols)
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(5 * ncols, 3.8 * nrows))
    axes = axes.flatten() if hasattr(axes, "flatten") else [axes]

    for ax, grupo in zip(axes, grupos):
        dados = plot_df.loc[plot_df[coluna_grupo] == grupo, variavel].dropna()
        sns.histplot(dados, bins=bins, kde=kde, ax=ax)
        ax.set_title(str(grupo))
        ax.set_xlabel(variavel)
        ax.set_ylabel("Frequência")

    for ax in axes[len(grupos):]:
        ax.set_visible(False)

    fig.suptitle(f"Histograma de {variavel} por {coluna_grupo.lower()}", y=1.02)
    fig.tight_layout()

    nome_arquivo = None
    if salvar:
        preparar_pasta_graficos(pasta)
        nome = variavel.replace(" ", "_").replace("/", "_")
        nome_arquivo = f"{pasta}/histograma_{nome}_por_{coluna_grupo.lower()}.png"

    _finalizar_plot(salvar=salvar, nome_arquivo=nome_arquivo, mostrar=mostrar)


def histogramas_todas_variaveis(df, nivel="regiao", ignorar_colunas=None, bins=10, kde=True, salvar=False, pasta="graficos", mostrar=True):
    base = preparar_base_analitica(df, nivel=nivel, ignorar_colunas=ignorar_colunas)
    variaveis = obter_variaveis_numericas(base, coluna_ano="Ano", ignorar_colunas=ignorar_colunas)
    for var in variaveis:
        histograma_variavel(df, variavel=var, nivel=nivel, ignorar_colunas=ignorar_colunas, bins=bins, kde=kde, salvar=salvar, pasta=pasta, mostrar=mostrar)
    return base


def histogramas_todas_variaveis_por_regiao(df, ignorar_colunas=None, bins=10, kde=True, salvar=False, pasta="graficos", mostrar=True):
    return histogramas_todas_variaveis(df, nivel="regiao", ignorar_colunas=ignorar_colunas, bins=bins, kde=kde, salvar=salvar, pasta=pasta, mostrar=mostrar)


def histogramas_todas_variaveis_por_estado(df, ignorar_colunas=None, bins=10, kde=True, salvar=False, pasta="graficos", mostrar=True):
    return histogramas_todas_variaveis(df, nivel="estado", ignorar_colunas=ignorar_colunas, bins=bins, kde=kde, salvar=salvar, pasta=pasta, mostrar=mostrar)
