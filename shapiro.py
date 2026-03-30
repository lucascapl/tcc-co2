import pandas as pd
from scipy.stats import shapiro

MAPA_REGIOES = {
    "AC": "Norte", "AP": "Norte", "AM": "Norte", "PA": "Norte", "RO": "Norte", "RR": "Norte", "TO": "Norte",
    "AL": "Nordeste", "BA": "Nordeste", "CE": "Nordeste", "MA": "Nordeste", "PB": "Nordeste",
    "PE": "Nordeste", "PI": "Nordeste", "RN": "Nordeste", "SE": "Nordeste",
    "DF": "Centro-Oeste", "GO": "Centro-Oeste", "MT": "Centro-Oeste", "MS": "Centro-Oeste",
    "ES": "Sudeste", "MG": "Sudeste", "RJ": "Sudeste", "SP": "Sudeste",
    "PR": "Sul", "RS": "Sul", "SC": "Sul"
}

def shapiro_series_temporais_por_regiao(
    df,
    coluna_estado="Estado",
    coluna_ano="Ano",
    ignorar_colunas=None,
    alpha=0.05,
    agregacao="sum"
):
    if ignorar_colunas is None:
        ignorar_colunas = ["IDHM"]

    base = df.copy()
    base["Regiao"] = base[coluna_estado].map(MAPA_REGIOES)
    base = base.dropna(subset=["Regiao", coluna_ano])

    colunas_numericas = base.select_dtypes(include=["number"]).columns.tolist()
    variaveis = [c for c in colunas_numericas if c not in ignorar_colunas and c != coluna_ano]

    resultados = []

    for var in variaveis:
        if agregacao == "sum":
            regional = base.groupby(["Regiao", coluna_ano], as_index=False)[var].sum()
        elif agregacao == "mean":
            regional = base.groupby(["Regiao", coluna_ano], as_index=False)[var].mean()
        else:
            raise ValueError("Use 'sum' ou 'mean'.")

        for regiao in sorted(regional["Regiao"].unique()):
            serie = regional.loc[regional["Regiao"] == regiao, var].dropna()

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
