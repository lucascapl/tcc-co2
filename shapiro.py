import pandas as pd
from scipy.stats import shapiro
from utils import base_grupo_ano, obter_variaveis_numericas, inferir_coluna_grupo


def shapiro_series_temporais_por_grupo(
    df,
    coluna_grupo="Estado",
    coluna_ano="Ano",
    ignorar_colunas=None,
    alpha=0.05,
    agregar_para_regiao=False,
):
    """
    Avalia a normalidade univariada de cada série temporal por grupo.
    Use coluna_grupo="Estado" para análise estadual ou "Regiao" para regional.
    """
    if ignorar_colunas is None:
        ignorar_colunas = ["IDHM"]

    base = base_grupo_ano(
        df,
        coluna_grupo=coluna_grupo,
        coluna_ano=coluna_ano,
        ignorar_colunas=ignorar_colunas,
        agregar_para_regiao=agregar_para_regiao,
    )
    coluna_grupo = inferir_coluna_grupo(base, "Regiao" if agregar_para_regiao else coluna_grupo)

    variaveis = obter_variaveis_numericas(
        base,
        coluna_ano=coluna_ano,
        ignorar_colunas=ignorar_colunas,
    )

    resultados = []
    for var in variaveis:
        for grupo in base[coluna_grupo].dropna().astype(str).unique():
            serie = base.loc[base[coluna_grupo].astype(str) == grupo, var].dropna()

            registro = {
                coluna_grupo: grupo,
                "Variavel": var,
                "n": len(serie),
                "W": None,
                "p_valor": None,
                "Normal_5pct": None,
                "Conclusao": None,
            }

            if len(serie) < 3:
                registro["Conclusao"] = "Amostra insuficiente"
            elif serie.nunique() < 2:
                registro["Conclusao"] = "Variável constante no grupo"
            else:
                stat, p = shapiro(serie)
                registro.update({
                    "W": stat,
                    "p_valor": p,
                    "Normal_5pct": "Sim" if p > alpha else "Não",
                    "Conclusao": "Não rejeita normalidade" if p > alpha else "Rejeita normalidade",
                })
            resultados.append(registro)

    return pd.DataFrame(resultados).sort_values([coluna_grupo, "Variavel"]).reset_index(drop=True)


def shapiro_series_temporais_por_estado(df, **kwargs):
    return shapiro_series_temporais_por_grupo(df, coluna_grupo="Estado", agregar_para_regiao=False, **kwargs)


def shapiro_series_temporais_por_regiao(df, **kwargs):
    # Wrapper antigo preservado: agrega Estado/Ano para Regiao/Ano se necessário.
    kwargs.pop("coluna_grupo", None)
    kwargs.pop("agregar_para_regiao", None)
    return shapiro_series_temporais_por_grupo(df, coluna_grupo="Regiao", agregar_para_regiao=True, **kwargs)
