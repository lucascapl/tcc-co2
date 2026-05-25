"""
Gera as bases tratadas individuais e monta o dataframe principal do TCC.

Fluxo:
1. Processa ou carrega do cache cada base tratada.
2. Valida se todas estão na mesma granularidade: Estado/Ano ou Regiao/Ano.
3. Faz os merges a partir da base de CO2.
4. Salva o dataframe principal em bases/tratadas/.

Observação:
- As configurações centrais ficam em config.py.
- Este arquivo não deve fazer análises estatísticas; isso fica em analise_df_principal.py.
"""

from __future__ import annotations

import os
from collections.abc import Callable
from typing import Any

import pandas as pd

from pipelines.co2_pipe import processar_co2
from pipelines.frota_pipe import processar_frota
from pipelines.rebanho_pipe import processar_rebanho
from pipelines.combustiveis_pipe import processar_combustiveis
from pipelines.desmatamento_mapbiomas_pipe import processar_desmatamento_mapbiomas
from pipelines.inmet_pipe import processar_inmet_clima
from pipelines.area_destinada_colheita_pipe import processar_area_destinada_colheita
from pipelines.area_colhida_pipe import processar_area_colhida
from pipelines.energia_industrial_pipe import processar_consumo_energia_industrial
from pipelines.queimadas_pipe import processar_queimadas

from config import CONFIG
from utils import salvar_tratado


# ---------------------------------------------------------------------------
# Configuração centralizada
# ---------------------------------------------------------------------------

REPROCESSAR_TUDO = CONFIG.REPROCESSAR_TUDO
AGRUPAR_POR_REGIAO = CONFIG.AGRUPAR_POR_REGIAO
CHAVES_MERGE = CONFIG.chaves_merge
SUFIXO_GRANULARIDADE = CONFIG.sufixo_granularidade

PASTA_INMET = CONFIG.PASTA_INMET
INMET_SOMENTE_CAPITAIS = CONFIG.INMET_SOMENTE_CAPITAIS
INMET_PARALELO = CONFIG.INMET_PARALELO
INMET_MAX_WORKERS = CONFIG.INMET_MAX_WORKERS

PASTA_QUEIMADAS = CONFIG.PASTA_QUEIMADAS
QUEIMADAS_PARALELO = CONFIG.QUEIMADAS_PARALELO
QUEIMADAS_MAX_WORKERS = CONFIG.QUEIMADAS_MAX_WORKERS


# ---------------------------------------------------------------------------
# Funções auxiliares
# ---------------------------------------------------------------------------

def caminho_base_tratada(nome_base_tratada: str) -> str:
    """Retorna o caminho padrão de uma base tratada salva pelo projeto."""
    return CONFIG.caminho_base_tratada(nome_base_tratada)


def carregar_ou_processar(
    nome_base_tratada: str,
    funcao_processamento: Callable[..., pd.DataFrame],
    *args: Any,
    **kwargs: Any,
) -> pd.DataFrame:
    """
    Carrega uma base tratada existente ou executa o pipeline correspondente.

    Quando REPROCESSAR_TUDO=False, usa o CSV já salvo em bases/tratadas/
    se ele existir. Caso contrário, executa o pipeline.
    """
    caminho = caminho_base_tratada(nome_base_tratada)

    if (not REPROCESSAR_TUDO) and os.path.exists(caminho):
        print(f"[cache] Carregando base tratada existente: {caminho}")
        return pd.read_csv(caminho)

    print(f"[processando] Gerando base: {nome_base_tratada}")
    df = funcao_processamento(*args, **kwargs)

    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            f"O pipeline '{nome_base_tratada}' deveria retornar um DataFrame, "
            f"mas retornou {type(df).__name__}."
        )

    return df


def validar_chaves(df: pd.DataFrame, nome_base: str) -> None:
    """
    Garante que cada base esteja na granularidade esperada antes do merge.
    """
    chaves_faltantes = [col for col in CHAVES_MERGE if col not in df.columns]
    if chaves_faltantes:
        raise ValueError(
            f"A base '{nome_base}' nao esta na granularidade esperada "
            f"({', '.join(CHAVES_MERGE)}). Colunas ausentes: {chaves_faltantes}. "
            f"Confira se o pipeline recebeu agrupar_por_regiao={AGRUPAR_POR_REGIAO}."
        )

    duplicadas = int(df.duplicated(CHAVES_MERGE).sum())
    if duplicadas > 0:
        raise ValueError(
            f"A base '{nome_base}' possui {duplicadas} linhas duplicadas para as chaves "
            f"{CHAVES_MERGE}. Agregue a base antes do merge."
        )


def preparar_base(
    nome_base_tratada: str,
    funcao_processamento: Callable[..., pd.DataFrame],
    *args: Any,
    **kwargs: Any,
) -> pd.DataFrame:
    """
    Processa/carrega uma base já aplicando o sufixo da granularidade atual.
    """
    nome_cache = f"{nome_base_tratada}-{SUFIXO_GRANULARIDADE}"
    df = carregar_ou_processar(nome_cache, funcao_processamento, *args, **kwargs)
    validar_chaves(df, nome_base_tratada)
    return df


def processar_bases_individuais() -> dict[str, pd.DataFrame]:
    """
    Executa todos os pipelines que entram no dataframe principal.

    A ordem abaixo é mantida de propósito para preservar o mesmo resultado final
    dos merges já usados no projeto.
    """
    bases: dict[str, pd.DataFrame] = {}

    bases["co2"] = preparar_base(
        "co2",
        processar_co2,
        agrupar_por_regiao=AGRUPAR_POR_REGIAO,
    )

    bases["frota"] = preparar_base(
        "frota",
        processar_frota,
        agrupar_por_regiao=AGRUPAR_POR_REGIAO,
    )

    bases["rebanho"] = preparar_base(
        "rebanho",
        processar_rebanho,
        agrupar_por_regiao=AGRUPAR_POR_REGIAO,
    )

    bases["venda-combustiveis"] = preparar_base(
        "venda-combustiveis",
        processar_combustiveis,
        agrupar_por_regiao=AGRUPAR_POR_REGIAO,
    )

    bases["desmatamento-mapbiomas"] = preparar_base(
        "desmatamento-mapbiomas",
        processar_desmatamento_mapbiomas,
        agrupar_por_regiao=AGRUPAR_POR_REGIAO,
    )

    # INMET rápido: temperatura e chuva no mesmo processamento,
    # para não ler milhares de arquivos duas vezes.
    bases["inmet-clima"] = preparar_base(
        "inmet-clima",
        processar_inmet_clima,
        pasta_inmet=PASTA_INMET,
        agrupar_por_regiao=AGRUPAR_POR_REGIAO,
        somente_capitais=INMET_SOMENTE_CAPITAIS,
        paralelo=INMET_PARALELO,
        max_workers=INMET_MAX_WORKERS,
    )

    bases["area-destinada-colheita"] = preparar_base(
        "area-destinada-colheita",
        processar_area_destinada_colheita,
        agrupar_por_regiao=AGRUPAR_POR_REGIAO,
    )

    bases["area-colhida"] = preparar_base(
        "area-colhida",
        processar_area_colhida,
        agrupar_por_regiao=AGRUPAR_POR_REGIAO,
    )

    bases["energia-industrial"] = preparar_base(
        "energia-industrial",
        processar_consumo_energia_industrial,
        agrupar_por_regiao=AGRUPAR_POR_REGIAO,
    )

    bases["queimadas"] = preparar_base(
        "queimadas",
        processar_queimadas,
        caminho_queimadas=PASTA_QUEIMADAS,
        agrupar_por_regiao=AGRUPAR_POR_REGIAO,
        paralelo=QUEIMADAS_PARALELO,
        max_workers=QUEIMADAS_MAX_WORKERS,
    )

    return bases


def montar_dataframe_principal(bases: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Monta o dataframe principal a partir da base de CO2.

    As demais bases são adicionadas por left join, preservando a base CO2 como
    referência temporal e territorial.
    """
    if "co2" not in bases:
        raise ValueError("A base 'co2' é obrigatória para montar o dataframe principal.")

    df_principal = bases["co2"].copy()

    bases_para_merge = [
        "frota",
        "rebanho",
        "venda-combustiveis",
        "desmatamento-mapbiomas",
        "inmet-clima",
        # "pib-percapita",  # Mantido fora para não alterar o desenho atual do dataframe principal.
        "area-destinada-colheita",
        "area-colhida",
        "energia-industrial",
        "queimadas",
    ]

    for nome_base in bases_para_merge:
        df_secundario = bases[nome_base]
        validar_chaves(df_secundario, nome_base)
        df_principal = df_principal.merge(df_secundario, on=CHAVES_MERGE, how="left")

    return df_principal.sort_values(CHAVES_MERGE).reset_index(drop=True)


def main() -> pd.DataFrame:
    print("=== Geração do dataframe principal ===")
    print(f"Granularidade: {'Regiao/Ano' if AGRUPAR_POR_REGIAO else 'Estado/Ano'}")
    print(f"Chaves de merge: {CHAVES_MERGE}")
    print(f"Reprocessar tudo: {REPROCESSAR_TUDO}")

    bases = processar_bases_individuais()
    df_principal = montar_dataframe_principal(bases)

    salvar_tratado(df_principal, f"dataframe-principal-{SUFIXO_GRANULARIDADE}")
    print("=== Dataframe principal gerado com sucesso ===")
    print(f"Linhas: {len(df_principal)}")
    print(f"Colunas: {len(df_principal.columns)}")

    return df_principal


if __name__ == "__main__":
    main()
