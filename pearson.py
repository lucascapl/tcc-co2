import pandas as pd
from scipy.stats import pearsonr
from utils import preparar_base_analitica, obter_variaveis_numericas, obter_coluna_grupo


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


def correlacao_pearson(df, nivel="regiao", coluna_alvo="CO2_bruto", coluna_ano="Ano", ignorar_colunas=None, alpha=0.05):
    if ignorar_colunas is None:
        ignorar_colunas = ["IDHM"]

    base = preparar_base_analitica(
        df,
        nivel=nivel,
        coluna_ano=coluna_ano,
        ignorar_colunas=ignorar_colunas,
    )
    coluna_grupo = obter_coluna_grupo(nivel)

    variaveis = obter_variaveis_numericas(base, coluna_ano=coluna_ano, ignorar_colunas=ignorar_colunas)
    variaveis = [v for v in variaveis if v != coluna_alvo]

    resultados = []
    for grupo in base[coluna_grupo].dropna().unique():
        base_grupo = base.loc[base[coluna_grupo] == grupo].copy()
        for var in variaveis:
            pares = base_grupo[[coluna_alvo, var]].dropna()
            if len(pares) < 3:
                resultados.append({
                    coluna_grupo: grupo,
                    "Variavel": var,
                    "Metodo": "Pearson",
                    "n": len(pares),
                    "Coeficiente": None,
                    "p_valor": None,
                    "Significativo_5pct": None,
                    "Direcao": None,
                    "Forca": None,
                    "Conclusao": "Amostra insuficiente",
                })
                continue
            coef, p = pearsonr(pares[coluna_alvo], pares[var])
            resultados.append({
                coluna_grupo: grupo,
                "Variavel": var,
                "Metodo": "Pearson",
                "n": len(pares),
                "Coeficiente": coef,
                "p_valor": p,
                "Significativo_5pct": "Sim" if p < alpha else "Não",
                "Direcao": "Positiva" if coef > 0 else "Negativa" if coef < 0 else "Nula",
                "Forca": classificar_forca_correlacao(abs(coef)),
                "Conclusao": "Correlação linear significativa" if p < alpha else "Sem evidência de correlação linear significativa",
            })
    return pd.DataFrame(resultados).sort_values([coluna_grupo, "Variavel"]).reset_index(drop=True)


def correlacao_pearson_por_regiao(df, coluna_alvo="CO2_bruto", coluna_ano="Ano", ignorar_colunas=None, alpha=0.05):
    return correlacao_pearson(df, nivel="regiao", coluna_alvo=coluna_alvo, coluna_ano=coluna_ano, ignorar_colunas=ignorar_colunas, alpha=alpha)


def correlacao_pearson_por_estado(df, coluna_alvo="CO2_bruto", coluna_ano="Ano", ignorar_colunas=None, alpha=0.05):
    return correlacao_pearson(df, nivel="estado", coluna_alvo=coluna_alvo, coluna_ano=coluna_ano, ignorar_colunas=ignorar_colunas, alpha=alpha)
