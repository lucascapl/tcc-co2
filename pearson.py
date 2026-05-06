import pandas as pd
from scipy.stats import pearsonr
from utils import base_regional_ano, obter_variaveis_numericas, construir_base_defasada


def classificar_forca_correlacao(valor_abs):
    if pd.isna(valor_abs):
        return None
    if valor_abs < 0.20:
        return "Muito fraca"
    if valor_abs < 0.40:
        return "Fraca"
    if valor_abs < 0.60:
        return "Moderada"
    if valor_abs < 0.80:
        return "Forte"
    return "Muito forte"


def correlacao_pearson_por_regiao(
    df,
    coluna_alvo="co2",
    coluna_ano="Ano",
    ignorar_colunas=None,
    alpha=0.05,
    defasagem_alvo=0,
):
    if ignorar_colunas is None:
        ignorar_colunas = ["IDHM"]

    regional = base_regional_ano(
        df,
        coluna_ano=coluna_ano,
        ignorar_colunas=ignorar_colunas,
    )

    coluna_alvo_analise = coluna_alvo
    if defasagem_alvo != 0:
        regional = construir_base_defasada(
            regional,
            coluna_alvo=coluna_alvo,
            coluna_ano=coluna_ano,
            defasagem_alvo=defasagem_alvo,
        )
        coluna_alvo_analise = f"{coluna_alvo}_t+{defasagem_alvo}"

    variaveis = obter_variaveis_numericas(
        regional,
        coluna_ano=coluna_ano,
        ignorar_colunas=ignorar_colunas,
    )
    variaveis = [v for v in variaveis if v not in {coluna_alvo, coluna_alvo_analise}]

    resultados = []

    for regiao in regional["Regiao"].dropna().astype(str).unique():
        base_regiao = regional.loc[regional["Regiao"].astype(str) == regiao].copy()

        for var in variaveis:
            pares = base_regiao[[coluna_alvo_analise, var, coluna_ano]].dropna()

            if len(pares) < 3:
                resultados.append({
                    "Regiao": regiao,
                    "Variavel": var,
                    "Metodo": "Pearson",
                    "Defasagem_CO2": defasagem_alvo,
                    "n": len(pares),
                    "Coeficiente": None,
                    "p_valor": None,
                    "Significativo_5pct": None,
                    "Direcao": None,
                    "Forca": None,
                    "Conclusao": "Amostra insuficiente",
                })
                continue

            if pares[coluna_alvo_analise].nunique() < 2 or pares[var].nunique() < 2:
                resultados.append({
                    "Regiao": regiao,
                    "Variavel": var,
                    "Metodo": "Pearson",
                    "Defasagem_CO2": defasagem_alvo,
                    "n": len(pares),
                    "Coeficiente": None,
                    "p_valor": None,
                    "Significativo_5pct": None,
                    "Direcao": None,
                    "Forca": None,
                    "Conclusao": "Variável constante na região",
                })
                continue

            coef, p = pearsonr(pares[coluna_alvo_analise], pares[var])
            coef_abs = abs(coef)

            if coef > 0:
                direcao = "Positiva"
            elif coef < 0:
                direcao = "Negativa"
            else:
                direcao = "Nula"

            resultados.append({
                "Regiao": regiao,
                "Variavel": var,
                "Metodo": "Pearson",
                "Defasagem_CO2": defasagem_alvo,
                "n": len(pares),
                "Ano_inicial_min": int(pares[coluna_ano].min()),
                "Ano_inicial_max": int(pares[coluna_ano].max()),
                "Coeficiente": coef,
                "p_valor": p,
                "Significativo_5pct": "Sim" if p < alpha else "Não",
                "Direcao": direcao,
                "Forca": classificar_forca_correlacao(coef_abs),
                "Conclusao": "Correlação linear significativa" if p < alpha else "Sem evidência de correlação linear significativa",
            })

    return pd.DataFrame(resultados).sort_values(["Regiao", "Variavel"]).reset_index(drop=True)
