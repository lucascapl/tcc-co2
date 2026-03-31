import pandas as pd
from scipy.stats import shapiro
from utils import preparar_base_analitica, obter_variaveis_numericas, obter_coluna_grupo


def shapiro_series_temporais(df, nivel="regiao", coluna_ano="Ano", ignorar_colunas=None, alpha=0.05):
    if ignorar_colunas is None:
        ignorar_colunas = ["IDHM"]

    base = preparar_base_analitica(
        df,
        nivel=nivel,
        coluna_ano=coluna_ano,
        ignorar_colunas=ignorar_colunas,
    )
    coluna_grupo = obter_coluna_grupo(nivel)

    variaveis = obter_variaveis_numericas(
        base,
        coluna_ano=coluna_ano,
        ignorar_colunas=ignorar_colunas,
    )

    resultados = []
    for var in variaveis:
        for grupo in base[coluna_grupo].dropna().unique():
            serie = base.loc[base[coluna_grupo] == grupo, var].dropna()
            if len(serie) < 3:
                resultados.append({
                    coluna_grupo: grupo,
                    "Variavel": var,
                    "n": len(serie),
                    "W": None,
                    "p_valor": None,
                    "Normal_5pct": None,
                    "Conclusao": "Amostra insuficiente",
                })
                continue
            stat, p = shapiro(serie)
            resultados.append({
                coluna_grupo: grupo,
                "Variavel": var,
                "n": len(serie),
                "W": stat,
                "p_valor": p,
                "Normal_5pct": "Sim" if p > alpha else "Não",
                "Conclusao": "Não rejeita normalidade" if p > alpha else "Rejeita normalidade",
            })

    return pd.DataFrame(resultados).sort_values([coluna_grupo, "Variavel"]).reset_index(drop=True)


def shapiro_series_temporais_por_regiao(df, coluna_ano="Ano", ignorar_colunas=None, alpha=0.05):
    return shapiro_series_temporais(df, nivel="regiao", coluna_ano=coluna_ano, ignorar_colunas=ignorar_colunas, alpha=alpha)


def shapiro_series_temporais_por_estado(df, coluna_ano="Ano", ignorar_colunas=None, alpha=0.05):
    return shapiro_series_temporais(df, nivel="estado", coluna_ano=coluna_ano, ignorar_colunas=ignorar_colunas, alpha=alpha)
