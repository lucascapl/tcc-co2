import os
import matplotlib.pyplot as plt
import seaborn as sns

from utils import (
    ORDEM_REGIOES,
    ORDEM_ESTADOS,
    base_grupo_ano,
    base_regional_ano,
    obter_variaveis_numericas,
    preparar_pasta_graficos,
    inferir_coluna_grupo,
)

sns.set_theme(style="whitegrid")


def _finalizar_plot(salvar=False, nome_arquivo=None, mostrar=True):
    if salvar and nome_arquivo:
        plt.savefig(nome_arquivo, dpi=300, bbox_inches="tight")
    if mostrar:
        plt.show()
    else:
        plt.close()


def _ordem_grupo(coluna_grupo):
    if coluna_grupo == "Regiao":
        return ORDEM_REGIOES
    if coluna_grupo == "Estado":
        return ORDEM_ESTADOS
    return None


def grafico_linha_co2_brasil(df, salvar=False, caminho="graficos/linhas/co2_linha_anos.png", mostrar=True):
    # Funciona tanto com base Estado/Ano quanto Regiao/Ano: soma CO2 por ano.
    base = df.copy()
    base["Ano"] = base["Ano"].astype("Int64")
    base["co2"] = base["co2"].astype(float)

    co2_ano = base.groupby("Ano", as_index=False)["co2"].sum(min_count=1).sort_values("Ano")

    plt.figure(figsize=(10, 6))
    sns.lineplot(data=co2_ano, x="Ano", y="co2", marker="o")
    plt.title("Emissões totais de CO2 no Brasil ao longo dos anos")
    plt.xlabel("Ano")
    plt.ylabel("CO2 bruto")
    plt.xticks(co2_ano["Ano"], rotation=45)
    plt.tight_layout()

    if salvar:
        preparar_pasta_graficos(os.path.dirname(caminho) or "graficos/linhas")

    _finalizar_plot(salvar=salvar, nome_arquivo=caminho, mostrar=mostrar)


def grafico_linha_variavel_por_grupo(
    df,
    variavel="co2",
    coluna_grupo="Estado",
    ignorar_colunas=None,
    salvar=False,
    pasta="graficos/linhas",
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
    base = df_base[[coluna_grupo, "Ano", variavel]].dropna().copy()

    plt.figure(figsize=(13 if coluna_grupo == "Estado" else 11, 7 if coluna_grupo == "Estado" else 6))
    sns.lineplot(
        data=base,
        x="Ano",
        y=variavel,
        hue=coluna_grupo,
        hue_order=_ordem_grupo(coluna_grupo),
        marker="o",
    )
    plt.title(f"Série temporal de {variavel} por {coluna_grupo.lower()}")
    plt.xlabel("Ano")
    plt.ylabel(variavel)
    plt.xticks(sorted(base["Ano"].dropna().unique()), rotation=45)
    plt.legend(title=coluna_grupo, bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()

    nome_arquivo = None
    if salvar:
        preparar_pasta_graficos(pasta)
        nome = variavel.replace(" ", "_").replace("/", "_")
        nome_arquivo = f"{pasta}/linha_{nome}_por_{coluna_grupo.lower()}.png"

    _finalizar_plot(salvar=salvar, nome_arquivo=nome_arquivo, mostrar=mostrar)


def boxplot_variavel_por_grupo_ano(
    df,
    variavel="co2",
    coluna_grupo="Estado",
    ignorar_colunas=None,
    salvar=False,
    pasta="graficos/boxplots",
    showfliers=False,
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
    base = df_base[[coluna_grupo, "Ano", variavel]].dropna().copy()

    plt.figure(figsize=(14 if coluna_grupo == "Estado" else 10, 7 if coluna_grupo == "Estado" else 6))
    sns.boxplot(data=base, x=coluna_grupo, y=variavel, order=_ordem_grupo(coluna_grupo), showfliers=showfliers)
    sns.stripplot(data=base, x=coluna_grupo, y=variavel, order=_ordem_grupo(coluna_grupo), color="black", size=3, alpha=0.45)

    plt.title(f"Distribuição temporal de {variavel} por {coluna_grupo.lower()} (base {coluna_grupo}-Ano)")
    plt.xlabel(coluna_grupo)
    plt.ylabel(variavel)
    plt.xticks(rotation=90 if coluna_grupo == "Estado" else 0)
    plt.tight_layout()

    nome_arquivo = None
    if salvar:
        preparar_pasta_graficos(pasta)
        nome = variavel.replace(" ", "_").replace("/", "_")
        nome_arquivo = f"{pasta}/boxplot_{nome}_por_{coluna_grupo.lower()}.png"

    _finalizar_plot(salvar=salvar, nome_arquivo=nome_arquivo, mostrar=mostrar)


def boxplots_todas_variaveis_por_grupo_ano(
    df,
    coluna_grupo="Estado",
    ignorar_colunas=None,
    salvar=False,
    pasta="graficos/boxplots",
    showfliers=False,
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
        boxplot_variavel_por_grupo_ano(
            df_base,
            variavel=var,
            coluna_grupo=coluna_grupo,
            ignorar_colunas=ignorar_colunas,
            salvar=salvar,
            pasta=pasta,
            showfliers=showfliers,
            mostrar=mostrar,
        )

    return df_base


def boxplot_co2_por_regiao(df, salvar=False, caminho="graficos/boxplots/co2_boxplot_regioes.png", mostrar=True):
    df_regional = base_regional_ano(df, ignorar_colunas=["IDHM"])
    base = df_regional[["Regiao", "Ano", "co2"]].dropna().copy()

    plt.figure(figsize=(10, 6))
    sns.boxplot(data=base, x="Regiao", y="co2", order=ORDEM_REGIOES, showfliers=False)
    sns.stripplot(data=base, x="Regiao", y="co2", order=ORDEM_REGIOES, color="black", size=4, alpha=0.55)
    plt.title("Distribuição temporal das emissões de CO2 por região (base Região-Ano)")
    plt.xlabel("Região")
    plt.ylabel("CO2 bruto")
    plt.tight_layout()

    if salvar:
        preparar_pasta_graficos(os.path.dirname(caminho) or "graficos/boxplots")

    _finalizar_plot(salvar=salvar, nome_arquivo=caminho, mostrar=mostrar)


# Wrappers antigos, para não quebrar chamadas existentes.
def grafico_linha_variavel_por_regiao(df, **kwargs):
    kwargs.pop("coluna_grupo", None)
    kwargs.pop("agregar_para_regiao", None)
    return grafico_linha_variavel_por_grupo(df, coluna_grupo="Regiao", agregar_para_regiao=True, **kwargs)


def boxplot_variavel_por_regiao_ano(df, **kwargs):
    kwargs.pop("coluna_grupo", None)
    kwargs.pop("agregar_para_regiao", None)
    return boxplot_variavel_por_grupo_ano(df, coluna_grupo="Regiao", agregar_para_regiao=True, **kwargs)


def boxplots_todas_variaveis_por_regiao_ano(df, **kwargs):
    kwargs.pop("coluna_grupo", None)
    kwargs.pop("agregar_para_regiao", None)
    return boxplots_todas_variaveis_por_grupo_ano(df, coluna_grupo="Regiao", agregar_para_regiao=True, **kwargs)
