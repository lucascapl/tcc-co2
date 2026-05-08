import pandas as pd
from scipy.stats import pearsonr
from utils import base_grupo_ano, obter_variaveis_numericas, construir_base_defasada, inferir_coluna_grupo


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


def correlacao_pearson_por_grupo(
    df,
    coluna_grupo="Estado",
    coluna_alvo="co2",
    coluna_ano="Ano",
    ignorar_colunas=None,
    alpha=0.05,
    defasagem_alvo=0,
    agregar_para_regiao=False,
):
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

    coluna_alvo_analise = coluna_alvo
    if defasagem_alvo != 0:
        base = construir_base_defasada(
            base,
            coluna_alvo=coluna_alvo,
            coluna_grupo=coluna_grupo,
            coluna_ano=coluna_ano,
            defasagem_alvo=defasagem_alvo,
        )
        coluna_alvo_analise = f"{coluna_alvo}_t+{defasagem_alvo}"

    variaveis = obter_variaveis_numericas(
        base,
        coluna_ano=coluna_ano,
        ignorar_colunas=ignorar_colunas,
    )
    variaveis = [v for v in variaveis if v not in {coluna_alvo, coluna_alvo_analise}]

    resultados = []
    for grupo in base[coluna_grupo].dropna().astype(str).unique():
        base_grupo = base.loc[base[coluna_grupo].astype(str) == grupo].copy()

        for var in variaveis:
            pares = base_grupo[[coluna_alvo_analise, var, coluna_ano]].dropna()

            registro = {
                coluna_grupo: grupo,
                "Variavel": var,
                "Metodo": "Pearson",
                "Defasagem_CO2": defasagem_alvo,
                "n": len(pares),
                "Coeficiente": None,
                "p_valor": None,
                "Significativo_5pct": None,
                "Direcao": None,
                "Forca": None,
                "Conclusao": None,
            }

            if len(pares) < 3:
                registro["Conclusao"] = "Amostra insuficiente"
                resultados.append(registro)
                continue

            if pares[coluna_alvo_analise].nunique() < 2 or pares[var].nunique() < 2:
                registro["Conclusao"] = "Variável constante no grupo"
                resultados.append(registro)
                continue

            coef, p = pearsonr(pares[coluna_alvo_analise], pares[var])
            registro.update({
                "Ano_inicial_min": int(pares[coluna_ano].min()),
                "Ano_inicial_max": int(pares[coluna_ano].max()),
                "Coeficiente": coef,
                "p_valor": p,
                "Significativo_5pct": "Sim" if p < alpha else "Não",
                "Direcao": "Positiva" if coef > 0 else "Negativa" if coef < 0 else "Nula",
                "Forca": classificar_forca_correlacao(abs(coef)),
                "Conclusao": "Correlação linear significativa" if p < alpha else "Sem evidência de correlação linear significativa",
            })
            resultados.append(registro)

    return pd.DataFrame(resultados).sort_values([coluna_grupo, "Variavel"]).reset_index(drop=True)


def correlacao_pearson_por_estado(df, **kwargs):
    return correlacao_pearson_por_grupo(df, coluna_grupo="Estado", agregar_para_regiao=False, **kwargs)


def correlacao_pearson_por_regiao(df, **kwargs):
    kwargs.pop("coluna_grupo", None)
    kwargs.pop("agregar_para_regiao", None)
    return correlacao_pearson_por_grupo(df, coluna_grupo="Regiao", agregar_para_regiao=True, **kwargs)
