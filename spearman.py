import pandas as pd
from scipy.stats import spearmanr
from utils import agregar_por_regiao_ano, obter_variaveis_numericas


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


def correlacao_spearman_por_regiao(
    df,
    coluna_alvo="CO2_bruto",
    coluna_ano="Ano",
    ignorar_colunas=None,
    alpha=0.05,
):
    if ignorar_colunas is None:
        ignorar_colunas = ["IDHM"]

    regional = agregar_por_regiao_ano(
        df,
        coluna_ano=coluna_ano,
        ignorar_colunas=ignorar_colunas,
    )

    variaveis = obter_variaveis_numericas(
        regional,
        coluna_ano=coluna_ano,
        ignorar_colunas=ignorar_colunas,
    )
    variaveis = [v for v in variaveis if v != coluna_alvo]

    resultados = []

    for regiao in sorted(regional["Regiao"].dropna().unique()):
        base_regiao = regional.loc[regional["Regiao"] == regiao].copy()

        for var in variaveis:
            pares = base_regiao[[coluna_alvo, var]].dropna()

            if len(pares) < 3:
                resultados.append({
                    "Regiao": regiao,
                    "Variavel": var,
                    "Metodo": "Spearman",
                    "n": len(pares),
                    "Coeficiente": None,
                    "p_valor": None,
                    "Significativo_5pct": None,
                    "Direcao": None,
                    "Forca": None,
                    "Conclusao": "Amostra insuficiente",
                })
                continue

            coef, p = spearmanr(pares[coluna_alvo], pares[var])
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
                "Metodo": "Spearman",
                "n": len(pares),
                "Coeficiente": coef,
                "p_valor": p,
                "Significativo_5pct": "Sim" if p < alpha else "Não",
                "Direcao": direcao,
                "Forca": classificar_forca_correlacao(coef_abs),
                "Conclusao": "Correlação monotônica significativa" if p < alpha else "Sem evidência de correlação monotônica significativa",
            })

    return pd.DataFrame(resultados).sort_values(["Regiao", "Variavel"]).reset_index(drop=True)