import os
import pandas as pd

from linha_boxplot import (
    grafico_linha_co2_brasil,
    grafico_linha_variavel_por_grupo,
    boxplots_todas_variaveis_por_grupo_ano,
)
from shapiro import shapiro_series_temporais_por_grupo
from scatter_plot import scatter_co2_vs_todas
from histogramas import histogramas_todas_variaveis_por_grupo
from missing_values import preparar_df_para_analise, relatorio_missing_values
from utils import base_grupo_ano
from pearson import correlacao_pearson_por_grupo
from spearman import correlacao_spearman_por_grupo

CAMINHO_DF = "bases/tratadas/dataframe-principal-estado-tratada.csv"
GERAR_VISUALIZACOES = False

# Cenário atual: análise estadual.
COLUNA_GRUPO = "Estado"
AGREGAR_PARA_REGIAO = False
SUFIXO_ANALISE = "estado"
IGNORAR_COLUNAS = ["IDHM"]


def salvar_resultado(df, nome_arquivo):
    os.makedirs("bases/tratadas", exist_ok=True)
    caminho = f"bases/tratadas/{nome_arquivo}.csv"
    df.to_csv(caminho, index=False)
    print(f"✅ Resultado salvo em {caminho}")


def validar_df_principal(df):
    chaves = [COLUNA_GRUPO, "Ano"]
    faltantes = [col for col in chaves + ["co2"] if col not in df.columns]
    if faltantes:
        raise ValueError(f"Dataframe principal sem colunas obrigatorias: {faltantes}")

    duplicadas = df.duplicated(chaves).sum()
    if duplicadas > 0:
        raise ValueError(f"Foram encontradas {duplicadas} chaves duplicadas em {chaves}.")

    print("=== Estrutura do dataframe principal ===")
    print(f"Linhas: {len(df)}")
    print(f"Grupos ({COLUNA_GRUPO}): {df[COLUNA_GRUPO].nunique()}")
    print(f"Anos: {int(df['Ano'].min())} a {int(df['Ano'].max())}")
    print(f"Duplicidades {COLUNA_GRUPO}/Ano: {duplicadas}")


def main():
    df_principal = pd.read_csv(CAMINHO_DF)
    validar_df_principal(df_principal)

    print("=== Missing values antes do preenchimento ===")
    print(relatorio_missing_values(df_principal))

    df_principal = preparar_df_para_analise(
        df_principal,
        preencher_populacao=True,
        arredondar_populacao=True,
        coluna_grupo=COLUNA_GRUPO,
        coluna_ano="Ano",
    )

    print("=== Missing values após o preenchimento ===")
    print(relatorio_missing_values(df_principal))

    df_base_analise = base_grupo_ano(
        df_principal,
        coluna_grupo=COLUNA_GRUPO,
        ignorar_colunas=IGNORAR_COLUNAS,
        agregar_para_regiao=AGREGAR_PARA_REGIAO,
    )
    print("=== Prévia da base usada na análise ===")
    print(df_base_analise.head())

    if GERAR_VISUALIZACOES:
        grafico_linha_co2_brasil(
            df_principal,
            salvar=True,
            mostrar=False,
        )
        grafico_linha_variavel_por_grupo(
            df_principal,
            variavel="co2",
            coluna_grupo=COLUNA_GRUPO,
            ignorar_colunas=IGNORAR_COLUNAS,
            salvar=True,
            mostrar=False,
            agregar_para_regiao=AGREGAR_PARA_REGIAO,
        )

    resultado_shapiro = shapiro_series_temporais_por_grupo(
        df_principal,
        coluna_grupo=COLUNA_GRUPO,
        ignorar_colunas=IGNORAR_COLUNAS,
        agregar_para_regiao=AGREGAR_PARA_REGIAO,
    )
    print(resultado_shapiro)
    salvar_resultado(resultado_shapiro, f"shapiro_por_{SUFIXO_ANALISE}")

    resultado_pearson = correlacao_pearson_por_grupo(
        df_principal,
        coluna_grupo=COLUNA_GRUPO,
        ignorar_colunas=IGNORAR_COLUNAS,
        defasagem_alvo=0,
        agregar_para_regiao=AGREGAR_PARA_REGIAO,
    )
    print(resultado_pearson)
    salvar_resultado(resultado_pearson, f"pearson_por_{SUFIXO_ANALISE}")

    resultado_spearman = correlacao_spearman_por_grupo(
        df_principal,
        coluna_grupo=COLUNA_GRUPO,
        ignorar_colunas=IGNORAR_COLUNAS,
        defasagem_alvo=0,
        agregar_para_regiao=AGREGAR_PARA_REGIAO,
    )
    print(resultado_spearman)
    salvar_resultado(resultado_spearman, f"spearman_por_{SUFIXO_ANALISE}")

    if GERAR_VISUALIZACOES:
        scatter_co2_vs_todas(
            df_principal,
            coluna_grupo=COLUNA_GRUPO,
            ignorar_colunas=IGNORAR_COLUNAS,
            salvar=True,
            versao="limpo",
            mostrar=False,
            defasagem_co2=0,
            agregar_para_regiao=AGREGAR_PARA_REGIAO,
        )

        histogramas_todas_variaveis_por_grupo(
            df_principal,
            coluna_grupo=COLUNA_GRUPO,
            ignorar_colunas=IGNORAR_COLUNAS,
            bins=8,
            kde=False,
            salvar=True,
            mostrar=False,
            agregar_para_regiao=AGREGAR_PARA_REGIAO,
        )

        boxplots_todas_variaveis_por_grupo_ano(
            df_principal,
            coluna_grupo=COLUNA_GRUPO,
            ignorar_colunas=IGNORAR_COLUNAS,
            salvar=True,
            showfliers=False,
            mostrar=False,
            agregar_para_regiao=AGREGAR_PARA_REGIAO,
        )


if __name__ == "__main__":
    main()
