"""
Executa a etapa de análise do dataframe principal.

Fluxo:
1. Carrega e valida o dataframe principal.
2. Mostra relatório de missing values antes e depois da preparação.
3. Salva os testes estatísticos: Shapiro-Wilk, Pearson e Spearman.
4. Opcionalmente gera visualizações exploratórias.
5. Opcionalmente gera os heatmaps estaduais de correlação.

Observação:
- Este arquivo parte do dataframe já gerado por frames.py.
- Não reprocessa bases brutas.
"""

from __future__ import annotations

import os

import pandas as pd

from config import CONFIG
from linha_boxplot import (
    boxplots_todas_variaveis_por_grupo_ano,
    grafico_linha_co2_brasil,
    grafico_linha_variavel_por_grupo,
)
from shapiro import shapiro_series_temporais_por_grupo
from scatter_plot import scatter_co2_vs_todas
from histogramas import histogramas_todas_variaveis_por_grupo
from missing_values import preparar_df_para_analise, relatorio_missing_values
from utils import base_grupo_ano
from pearson import correlacao_pearson_por_grupo
from spearman import correlacao_spearman_por_grupo
from heatmap_correlacao_estado import salvar_correlacao_e_heatmaps_estado
from clusterizacao_estado import executar_clusterizacao_estado


# ---------------------------------------------------------------------------
# Configuração centralizada
# ---------------------------------------------------------------------------

CAMINHO_DF = CONFIG.caminho_df_principal
PASTA_RESULTADOS = CONFIG.PASTA_TRATADAS

COLUNA_GRUPO = CONFIG.coluna_grupo
COLUNA_ANO = CONFIG.COLUNA_ANO
COLUNA_ALVO = CONFIG.COLUNA_ALVO
AGREGAR_PARA_REGIAO = CONFIG.AGRUPAR_POR_REGIAO
SUFIXO_ANALISE = CONFIG.sufixo_granularidade

# Internações/IDHM sairam da análise principal. Se ainda existir no CSV por histórico,
# fica ignorada nos testes e visualizações.
IGNORAR_COLUNAS = list(CONFIG.IGNORAR_COLUNAS)

GERAR_VISUALIZACOES = CONFIG.GERAR_VISUALIZACOES
GERAR_HEATMAPS = CONFIG.GERAR_HEATMAPS
GERAR_HEATMAPS_POR_BLOCO = CONFIG.GERAR_HEATMAPS_POR_BLOCO
GERAR_CLUSTERIZACAO = CONFIG.GERAR_CLUSTERIZACAO


# ---------------------------------------------------------------------------
# Funções auxiliares
# ---------------------------------------------------------------------------

def salvar_resultado(df: pd.DataFrame, nome_arquivo: str) -> str:
    os.makedirs(PASTA_RESULTADOS, exist_ok=True)
    caminho = os.path.join(PASTA_RESULTADOS, f"{nome_arquivo}.csv")
    df.to_csv(caminho, index=False)
    print(f"✅ Resultado salvo em {caminho}")
    return caminho


def validar_df_principal(df: pd.DataFrame) -> None:
    chaves = [COLUNA_GRUPO, COLUNA_ANO]
    faltantes = [col for col in chaves + [COLUNA_ALVO] if col not in df.columns]
    if faltantes:
        raise ValueError(f"Dataframe principal sem colunas obrigatorias: {faltantes}")

    duplicadas = int(df.duplicated(chaves).sum())
    if duplicadas > 0:
        raise ValueError(f"Foram encontradas {duplicadas} chaves duplicadas em {chaves}.")

    print("=== Estrutura do dataframe principal ===")
    print(f"Linhas: {len(df)}")
    print(f"Colunas: {len(df.columns)}")
    print(f"Grupos ({COLUNA_GRUPO}): {df[COLUNA_GRUPO].nunique()}")
    print(f"Anos: {int(df[COLUNA_ANO].min())} a {int(df[COLUNA_ANO].max())}")
    print(f"Duplicidades {COLUNA_GRUPO}/Ano: {duplicadas}")


def carregar_dataframe_principal() -> pd.DataFrame:
    if not os.path.exists(CAMINHO_DF):
        raise FileNotFoundError(
            f"Dataframe principal não encontrado em '{CAMINHO_DF}'. "
            "Execute primeiro: python frames.py"
        )

    df_principal = pd.read_csv(CAMINHO_DF)
    validar_df_principal(df_principal)
    return df_principal


def preparar_dataframe_para_analise(df_principal: pd.DataFrame) -> pd.DataFrame:
    print("=== Missing values antes do preenchimento ===")
    print(relatorio_missing_values(df_principal))

    df_preparado = preparar_df_para_analise(
        df_principal,
        preencher_populacao=True,
        arredondar_populacao=True,
        coluna_grupo=COLUNA_GRUPO,
        coluna_ano=COLUNA_ANO,
    )

    print("=== Missing values após o preenchimento ===")
    print(relatorio_missing_values(df_preparado))

    df_base_analise = base_grupo_ano(
        df_preparado,
        coluna_grupo=COLUNA_GRUPO,
        coluna_ano=COLUNA_ANO,
        ignorar_colunas=IGNORAR_COLUNAS,
        agregar_para_regiao=AGREGAR_PARA_REGIAO,
    )

    print("=== Prévia da base usada na análise ===")
    print(df_base_analise.head())

    return df_preparado


def rodar_testes_estatisticos(df_principal: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """
    Roda os testes que geram tabelas de resultado.

    Mantém os mesmos métodos já utilizados:
    - Shapiro-Wilk para normalidade das séries temporais.
    - Pearson para correlação linear.
    - Spearman para correlação monotônica.
    """
    resultados: dict[str, pd.DataFrame] = {}

    resultados["shapiro"] = shapiro_series_temporais_por_grupo(
        df_principal,
        coluna_grupo=COLUNA_GRUPO,
        coluna_ano=COLUNA_ANO,
        ignorar_colunas=IGNORAR_COLUNAS,
        agregar_para_regiao=AGREGAR_PARA_REGIAO,
    )
    print(resultados["shapiro"])
    salvar_resultado(resultados["shapiro"], f"shapiro_por_{SUFIXO_ANALISE}")

    resultados["pearson"] = correlacao_pearson_por_grupo(
        df_principal,
        coluna_grupo=COLUNA_GRUPO,
        coluna_alvo=COLUNA_ALVO,
        coluna_ano=COLUNA_ANO,
        ignorar_colunas=IGNORAR_COLUNAS,
        defasagem_alvo=0,
        agregar_para_regiao=AGREGAR_PARA_REGIAO,
    )
    print(resultados["pearson"])
    salvar_resultado(resultados["pearson"], f"pearson_por_{SUFIXO_ANALISE}")

    resultados["spearman"] = correlacao_spearman_por_grupo(
        df_principal,
        coluna_grupo=COLUNA_GRUPO,
        coluna_alvo=COLUNA_ALVO,
        coluna_ano=COLUNA_ANO,
        ignorar_colunas=IGNORAR_COLUNAS,
        defasagem_alvo=0,
        agregar_para_regiao=AGREGAR_PARA_REGIAO,
    )
    print(resultados["spearman"])
    salvar_resultado(resultados["spearman"], f"spearman_por_{SUFIXO_ANALISE}")

    return resultados


def gerar_visualizacoes_exploratorias(df_principal: pd.DataFrame) -> None:
    """
    Gera gráficos exploratórios opcionais.

    Por padrão GERAR_VISUALIZACOES=False para evitar criar muitos arquivos em
    execuções rápidas. Altere a constante no topo do arquivo quando quiser gerar.
    """
    if not GERAR_VISUALIZACOES:
        return

    grafico_linha_co2_brasil(
        df_principal,
        salvar=True,
        mostrar=False,
    )

    grafico_linha_variavel_por_grupo(
        df_principal,
        variavel=COLUNA_ALVO,
        coluna_grupo=COLUNA_GRUPO,
        ignorar_colunas=IGNORAR_COLUNAS,
        salvar=True,
        mostrar=False,
        agregar_para_regiao=AGREGAR_PARA_REGIAO,
    )

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


def gerar_heatmaps(df_principal: pd.DataFrame) -> pd.DataFrame | None:
    """
    Gera os heatmaps estaduais como parte da análise principal.

    O heatmap atual é específico para Estado/Ano porque usa blocos de UFs.
    Por isso, ele só roda quando COLUNA_GRUPO="Estado" e AGREGAR_PARA_REGIAO=False.
    """
    if not GERAR_HEATMAPS:
        return None

    if COLUNA_GRUPO != "Estado" or AGREGAR_PARA_REGIAO:
        print("[heatmap] Etapa ignorada: o heatmap atual está definido para análise Estado/Ano.")
        return None

    return salvar_correlacao_e_heatmaps_estado(
        caminho_df=CAMINHO_DF,
        coluna_estado=COLUNA_GRUPO,
        coluna_ano=COLUNA_ANO,
        coluna_alvo=COLUNA_ALVO,
        ignorar_colunas=IGNORAR_COLUNAS,
        mostrar=False,
        gerar_heatmaps_por_bloco=GERAR_HEATMAPS_POR_BLOCO,
    )


def gerar_clusterizacao(df_principal: pd.DataFrame) -> dict[str, pd.DataFrame] | None:
    """
    Gera a clusterização estadual como parte da análise principal.

    Assim como os heatmaps por perfis, esta etapa é específica para Estado/Ano.
    """
    if not GERAR_CLUSTERIZACAO:
        return None

    if COLUNA_GRUPO != "Estado" or AGREGAR_PARA_REGIAO:
        print("[clusterizacao] Etapa ignorada: a clusterização atual está definida para análise Estado/Ano.")
        return None

    return executar_clusterizacao_estado(
        caminho_df=CAMINHO_DF,
        n_clusters=3,
    )


def main() -> dict[str, pd.DataFrame]:
    print("=== Análise do dataframe principal ===")
    print(f"Arquivo analisado: {CAMINHO_DF}")
    print(f"Grupo: {COLUNA_GRUPO}")
    print(f"Alvo: {COLUNA_ALVO}")

    df_principal = carregar_dataframe_principal()
    df_principal = preparar_dataframe_para_analise(df_principal)

    resultados = rodar_testes_estatisticos(df_principal)
    gerar_heatmaps(df_principal)
    resultados_clusterizacao = gerar_clusterizacao(df_principal)
    if resultados_clusterizacao is not None:
        resultados.update({
            f"clusterizacao_{nome}": valor
            for nome, valor in resultados_clusterizacao.items()
            if isinstance(valor, pd.DataFrame)
        })
    gerar_visualizacoes_exploratorias(df_principal)

    print("=== Análise concluída ===")
    return resultados


if __name__ == "__main__":
    main()
