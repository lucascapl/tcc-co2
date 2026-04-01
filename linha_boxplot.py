import matplotlib.pyplot as plt
import seaborn as sns
from utils import ORDEM_REGIOES, base_regional_ano, obter_variaveis_numericas, preparar_pasta_graficos

sns.set_theme(style="whitegrid")


def _finalizar_plot(salvar=False, nome_arquivo=None, mostrar=True):
    if salvar and nome_arquivo:
        plt.savefig(nome_arquivo, dpi=300, bbox_inches="tight")
    if mostrar:
        plt.show()
    else:
        plt.close()


def grafico_linha_co2_brasil(df, salvar=False, caminho="graficos/co2_linha_anos.png", mostrar=True):
    base = base_regional_ano(df, ignorar_colunas=["IDHM"]).copy()
    base["Ano"] = base["Ano"].astype("Int64")
    base["CO2_bruto"] = base["CO2_bruto"].astype(float)

    co2_ano = (
        base.groupby("Ano", as_index=False)["CO2_bruto"]
        .sum(min_count=1)
        .sort_values("Ano")
    )

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


def grafico_linha_variavel_por_regiao(df, variavel="CO2_bruto", ignorar_colunas=None, salvar=False, pasta="graficos", mostrar=True):
    df_regional = base_regional_ano(df, ignorar_colunas=ignorar_colunas)
    base = df_regional[["Regiao", "Ano", variavel]].dropna().copy()

    plt.figure(figsize=(11, 6))
    sns.lineplot(data=base, x="Ano", y=variavel, hue="Regiao", hue_order=ORDEM_REGIOES, marker="o")
    plt.title(f"Série temporal de {variavel} por região")
    plt.xlabel("Ano")
    plt.ylabel(variavel)
    plt.xticks(sorted(base["Ano"].dropna().unique()), rotation=45)
    plt.legend(title="Região")
    plt.tight_layout()

    nome_arquivo = None
    if salvar:
        preparar_pasta_graficos(pasta)
        nome = variavel.replace(" ", "_").replace("/", "_")
        nome_arquivo = f"{pasta}/linha_{nome}_por_regiao.png"

    _finalizar_plot(salvar=salvar, nome_arquivo=nome_arquivo, mostrar=mostrar)


def boxplot_variavel_por_regiao_ano(df, variavel="CO2_bruto", ignorar_colunas=None, salvar=False, pasta="graficos", showfliers=False, mostrar=True):
    df_regional = base_regional_ano(df, ignorar_colunas=ignorar_colunas)
    base = df_regional[["Regiao", "Ano", variavel]].dropna().copy()

    plt.figure(figsize=(10, 6))
    sns.boxplot(data=base, x="Regiao", y=variavel, order=ORDEM_REGIOES, showfliers=showfliers)
    sns.stripplot(data=base, x="Regiao", y=variavel, order=ORDEM_REGIOES, color="black", size=4, alpha=0.55)

    plt.title(f"Distribuição temporal de {variavel} por região (base Região-Ano)")
    plt.xlabel("Região")
    plt.ylabel(variavel)
    plt.tight_layout()

    nome_arquivo = None
    if salvar:
        preparar_pasta_graficos(pasta)
        nome = variavel.replace(" ", "_").replace("/", "_")
        nome_arquivo = f"{pasta}/boxplot_{nome}_por_regiao.png"

    _finalizar_plot(salvar=salvar, nome_arquivo=nome_arquivo, mostrar=mostrar)


def boxplots_todas_variaveis_por_regiao_ano(df, ignorar_colunas=None, salvar=False, pasta="graficos", showfliers=False, mostrar=True):
    df_regional = base_regional_ano(df, ignorar_colunas=ignorar_colunas)
    variaveis = obter_variaveis_numericas(df_regional, coluna_ano="Ano", ignorar_colunas=ignorar_colunas)

    for var in variaveis:
        boxplot_variavel_por_regiao_ano(
            df_regional,
            variavel=var,
            ignorar_colunas=ignorar_colunas,
            salvar=salvar,
            pasta=pasta,
            showfliers=showfliers,
            mostrar=mostrar,
        )

    return df_regional


def boxplot_co2_por_regiao(df, salvar=False, caminho="graficos/co2_boxplot_regioes.png", mostrar=True):
    df_regional = base_regional_ano(df, ignorar_colunas=["IDHM"])
    base = df_regional[["Regiao", "Ano", "CO2_bruto"]].dropna().copy()

    plt.figure(figsize=(10, 6))
    sns.boxplot(data=base, x="Regiao", y="CO2_bruto", order=ORDEM_REGIOES, showfliers=False)
    sns.stripplot(data=base, x="Regiao", y="CO2_bruto", order=ORDEM_REGIOES, color="black", size=4, alpha=0.55)
    plt.title("Distribuição temporal das emissões de CO2 por região (base Região-Ano)")
    plt.xlabel("Região")
    plt.ylabel("CO2 bruto")
    plt.tight_layout()

    if salvar:
        preparar_pasta_graficos()

    _finalizar_plot(salvar=salvar, nome_arquivo=caminho, mostrar=mostrar)
