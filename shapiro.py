import pandas as pd
from scipy.stats import shapiro
from utils import base_regional_ano, obter_variaveis_numericas


def shapiro_series_temporais_por_regiao(
    df,
    coluna_ano="Ano",
    ignorar_colunas=None,
    alpha=0.05
):
    """
    Avalia a normalidade univariada de cada série temporal regional.
    Útil como diagnóstico exploratório, mas não valida sozinho o uso de Pearson.
    """
    if ignorar_colunas is None:
        ignorar_colunas = ["IDHM"]

    regional = base_regional_ano(
        df,
        coluna_ano=coluna_ano,
        ignorar_colunas=ignorar_colunas
    )

    variaveis = obter_variaveis_numericas(
        regional,
        coluna_ano=coluna_ano,
        ignorar_colunas=ignorar_colunas
    )

    resultados = []

    for var in variaveis:
        for regiao in regional["Regiao"].dropna().astype(str).unique():
            serie = regional.loc[regional["Regiao"].astype(str) == regiao, var].dropna()

            if len(serie) < 3:
                resultados.append({
                    "Regiao": regiao,
                    "Variavel": var,
                    "n": len(serie),
                    "W": None,
                    "p_valor": None,
                    "Normal_5pct": None,
                    "Conclusao": "Amostra insuficiente"
                })
                continue

            stat, p = shapiro(serie)

            resultados.append({
                "Regiao": regiao,
                "Variavel": var,
                "n": len(serie),
                "W": stat,
                "p_valor": p,
                "Normal_5pct": "Sim" if p > alpha else "Não",
                "Conclusao": "Não rejeita normalidade" if p > alpha else "Rejeita normalidade"
            })

    return pd.DataFrame(resultados).sort_values(["Regiao", "Variavel"]).reset_index(drop=True)
