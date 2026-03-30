import os
import pandas as pd
import unicodedata

MAPA_ESTADOS = {
    "Acre": "AC", "Alagoas": "AL", "Amapá": "AP", "Amazonas": "AM",
    "Bahia": "BA", "Ceará": "CE", "Distrito Federal": "DF", "Espírito Santo": "ES",
    "Goiás": "GO", "Maranhão": "MA", "Mato Grosso": "MT", "Mato Grosso do Sul": "MS",
    "Minas Gerais": "MG", "Pará": "PA", "Paraíba": "PB", "Paraná": "PR",
    "Pernambuco": "PE", "Piauí": "PI", "Rio de Janeiro": "RJ", "Rio Grande do Norte": "RN",
    "Rio Grande do Sul": "RS", "Rondônia": "RO", "Roraima": "RR",
    "Santa Catarina": "SC", "São Paulo": "SP", "Sergipe": "SE", "Tocantins": "TO"
}

MAPA_REGIOES = {
    "AC": "Norte", "AP": "Norte", "AM": "Norte", "PA": "Norte", "RO": "Norte", "RR": "Norte", "TO": "Norte",
    "AL": "Nordeste", "BA": "Nordeste", "CE": "Nordeste", "MA": "Nordeste", "PB": "Nordeste",
    "PE": "Nordeste", "PI": "Nordeste", "RN": "Nordeste", "SE": "Nordeste",
    "DF": "Centro-Oeste", "GO": "Centro-Oeste", "MT": "Centro-Oeste", "MS": "Centro-Oeste",
    "ES": "Sudeste", "MG": "Sudeste", "RJ": "Sudeste", "SP": "Sudeste",
    "PR": "Sul", "RS": "Sul", "SC": "Sul"
}

ORDEM_REGIOES = ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"]


def normalizar_texto(txt: str) -> str:
    if pd.isna(txt):
        return txt
    txt = str(txt).strip()
    txt = unicodedata.normalize("NFKD", txt).encode("ASCII", "ignore").decode("utf-8")
    return txt


def normalizar_estado(nome_estado: str) -> str:
    if not nome_estado:
        return None
    nome_estado_norm = normalizar_texto(nome_estado).title()
    for nome, uf in MAPA_ESTADOS.items():
        nome_norm = normalizar_texto(nome).title()
        if nome_estado_norm == nome_norm:
            return uf
    return None


def salvar_tratado(df, nome):
    os.makedirs("bases/tratadas", exist_ok=True)
    caminho = f"bases/tratadas/{nome}_tratado.csv"
    df.to_csv(caminho, index=False)
    print(f"✅ Base '{nome}' tratada salva em {caminho}")
    return df

def preparar_pasta_graficos(caminho="graficos"):
    os.makedirs(caminho, exist_ok=True)

def adicionar_regiao(df, coluna_estado="Estado"):
    base = df.copy()
    base["Regiao"] = base[coluna_estado].map(MAPA_REGIOES)
    return base


def obter_variaveis_numericas(df, coluna_ano="Ano", ignorar_colunas=None):
    if ignorar_colunas is None:
        ignorar_colunas = ["IDHM"]

    colunas_numericas = df.select_dtypes(include=["number"]).columns.tolist()
    variaveis = [c for c in colunas_numericas if c not in ignorar_colunas and c != coluna_ano]
    return variaveis


def agregar_por_regiao_ano(df, coluna_estado="Estado", coluna_ano="Ano", ignorar_colunas=None):
    base = adicionar_regiao(df, coluna_estado=coluna_estado)
    base = base.dropna(subset=["Regiao", coluna_ano])

    variaveis = obter_variaveis_numericas(
        base,
        coluna_ano=coluna_ano,
        ignorar_colunas=ignorar_colunas
    )

    df_regional = (
        base.groupby(["Regiao", coluna_ano], as_index=False)[variaveis]
        .sum()
    )

    df_regional["Regiao"] = pd.Categorical(
        df_regional["Regiao"],
        categories=ORDEM_REGIOES,
        ordered=True
    )

    df_regional = df_regional.sort_values(["Regiao", coluna_ano]).reset_index(drop=True)
    return df_regional