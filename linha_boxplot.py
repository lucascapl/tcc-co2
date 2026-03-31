import matplotlib.pyplot as plt
import seaborn as sns
from utils import ORDEM_REGIOES, ORDEM_ESTADOS, preparar_base_analitica, obter_variaveis_numericas, preparar_pasta_graficos, obter_coluna_grupo

sns.set_theme(style="whitegrid")


def _finalizar_plot(salvar=False, nome_arquivo=None, mostrar=True):
    if salvar and nome_arquivo:
        plt.savefig(nome_arquivo, dpi=300, bbox_inches="tight")
    if mostrar:
        plt.show()
    else:
        plt.close()


def _ordem_e_rotacao(nivel):
    if nivel == "regiao":
        return ORDEM_REGIOES, 0
    return ORDEM_ESTADOS, 90


def grafico_linha_co2_brasil(df, salvar=False, caminho="graficos/co2_linha_anos.png", mostrar=True):
    base = df.copy()
    base["Ano"] = base["Ano"].astype("Int64")
    base["CO2_bruto"] = base["CO2_bruto"].astype(float)
    co2_ano = base.groupby("Ano", as_index=False)["CO2_bruto"].sum(min_count=1).sort_values("Ano")

    plt.figure(figsize=(10, 6))
    sns.lineplot(data=co2_ano, x="Ano", y="CO2_bruto", marker="o")
    plt.title("Emissões totais de CO2 no Brasil ao longo dos anos")
    plt.xlabel("Ano")
    plt.ylabel("CO2 bruto")
    plt.xticks(co2_ano["Ano"], rotation=45)
    plt.tight_layout()

    if salvar:
        preparar_pasta_graficos()
    _finalizar_plot(salvar=salvar, nome_arquivo=caminho, mostrar=mostrar)


def grafico_linha_variavel(df, variavel="CO2_bruto", nivel="regiao", ignorar_colunas=None, salvar=False, pasta="graficos", mostrar=True):
    base = preparar_base_analitica(df, nivel=nivel, ignorar_colunas=ignorar_colunas)
    coluna_grupo = obter_coluna_grupo(nivel)
    ordem, rotacao = _ordem_e_rotacao(nivel)
    plot_df = base[[coluna_grupo, "Ano", variavel]].dropna().copy()

    largura = 11 if nivel == "regiao" else 14
    plt.figure(figsize=(largura, 6))
    sns.lineplot(data=plot_df, x="Ano", y=variavel, hue=coluna_grupo, hue_order=ordem, marker="o")
    plt.title(f"Série temporal de {variavel} por {coluna_grupo.lower()}")
    plt.xlabel("Ano")
    plt.ylabel(variavel)
    plt.xticks(sorted(plot_df["Ano"].dropna().unique()), rotation=45)
    plt.legend(title=coluna_grupo, bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()

    nome_arquivo = None
    if salvar:
        preparar_pasta_graficos(pasta)
        nome = variavel.replace(" ", "_").replace("/", "_")
        nome_arquivo = f"{pasta}/linha_{nome}_por_{coluna_grupo.lower()}.png"

    _finalizar_plot(salvar=salvar, nome_arquivo=nome_arquivo, mostrar=mostrar)


def boxplot_variavel(df, variavel="CO2_bruto", nivel="regiao", ignorar_colunas=None, salvar=False, pasta="graficos", showfliers=False, mostrar=True):
    base = preparar_base_analitica(df, nivel=nivel, ignorar_colunas=ignorar_colunas)
    coluna_grupo = obter_coluna_grupo(nivel)
    ordem, rotacao = _ordem_e_rotacao(nivel)
    plot_df = base[[coluna_grupo, "Ano", variavel]].dropna().copy()

    largura = 10 if nivel == "regiao" else 16
    plt.figure(figsize=(largura, 6))
    sns.boxplot(data=plot_df, x=coluna_grupo, y=variavel, order=ordem, showfliers=showfliers)
    sns.stripplot(data=plot_df, x=coluna_grupo, y=variavel, order=ordem, color="black", size=3 if nivel == "estado" else 4, alpha=0.45)
    plt.title(f"Distribuição temporal de {variavel} por {coluna_grupo.lower()} (base {coluna_grupo}-Ano)")
    plt.xlabel(coluna_grupo)
    plt.ylabel(variavel)
    plt.xticks(rotation=rotacao)
    plt.tight_layout()

    nome_arquivo = None
    if salvar:
        preparar_pasta_graficos(pasta)
        nome = variavel.replace(" ", "_").replace("/", "_")
        nome_arquivo = f"{pasta}/boxplot_{nome}_por_{coluna_grupo.lower()}.png"

    _finalizar_plot(salvar=salvar, nome_arquivo=nome_arquivo, mostrar=mostrar)


def boxplots_todas_variaveis(df, nivel="regiao", ignorar_colunas=None, salvar=False, pasta="graficos", showfliers=False, mostrar=True):
    base = preparar_base_analitica(df, nivel=nivel, ignorar_colunas=ignorar_colunas)
    variaveis = obter_variaveis_numericas(base, coluna_ano="Ano", ignorar_colunas=ignorar_colunas)
    for var in variaveis:
        boxplot_variavel(df, variavel=var, nivel=nivel, ignorar_colunas=ignorar_colunas, salvar=salvar, pasta=pasta, showfliers=showfliers, mostrar=mostrar)
    return base


def grafico_linha_variavel_por_regiao(df, variavel="CO2_bruto", ignorar_colunas=None, salvar=False, pasta="graficos", mostrar=True):
    return grafico_linha_variavel(df, variavel=variavel, nivel="regiao", ignorar_colunas=ignorar_colunas, salvar=salvar, pasta=pasta, mostrar=mostrar)


def grafico_linha_variavel_por_estado(df, variavel="CO2_bruto", ignorar_colunas=None, salvar=False, pasta="graficos", mostrar=True):
    return grafico_linha_variavel(df, variavel=variavel, nivel="estado", ignorar_colunas=ignorar_colunas, salvar=salvar, pasta=pasta, mostrar=mostrar)


def boxplots_todas_variaveis_por_regiao_ano(df, ignorar_colunas=None, salvar=False, pasta="graficos", showfliers=False, mostrar=True):
    return boxplots_todas_variaveis(df, nivel="regiao", ignorar_colunas=ignorar_colunas, salvar=salvar, pasta=pasta, showfliers=showfliers, mostrar=mostrar)


def boxplots_todas_variaveis_por_estado_ano(df, ignorar_colunas=None, salvar=False, pasta="graficos", showfliers=False, mostrar=True):
    return boxplots_todas_variaveis(df, nivel="estado", ignorar_colunas=ignorar_colunas, salvar=salvar, pasta=pasta, showfliers=showfliers, mostrar=mostrar)
