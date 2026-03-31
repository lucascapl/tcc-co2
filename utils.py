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
ORDEM_ESTADOS = sorted(MAPA_REGIOES.keys())


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
    if nome_estado_norm.upper() in MAPA_REGIOES:
        return nome_estado_norm.upper()
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


def garantir_uf(df, coluna_estado="Estado"):
    base = df.copy()
    base[coluna_estado] = base[coluna_estado].apply(normalizar_estado)
    return base


def obter_variaveis_numericas(df, coluna_ano="Ano", ignorar_colunas=None):
    if ignorar_colunas is None:
        ignorar_colunas = ["IDHM"]

    colunas_numericas = df.select_dtypes(include=["number"]).columns.tolist()
    variaveis = [c for c in colunas_numericas if c not in ignorar_colunas and c != coluna_ano]
    return variaveis


def construir_agregacoes(df, variaveis=None):
    if variaveis is None:
        variaveis = obter_variaveis_numericas(df)
    return {var: (lambda s: s.sum(min_count=1)) for var in variaveis}


def preparar_base_analitica(df, nivel="regiao", coluna_estado="Estado", coluna_ano="Ano", ignorar_colunas=None, agg_map=None):
    nivel = str(nivel).lower()
    base = garantir_uf(df, coluna_estado=coluna_estado)
    base = adicionar_regiao(base, coluna_estado=coluna_estado)

    if nivel == "estado":
        base = base.dropna(subset=[coluna_estado, coluna_ano]).copy()
        base[coluna_estado] = pd.Categorical(base[coluna_estado], categories=ORDEM_ESTADOS, ordered=True)
        return base.sort_values([coluna_estado, coluna_ano]).reset_index(drop=True)

    if nivel != "regiao":
        raise ValueError("nivel deve ser 'regiao' ou 'estado'.")

    base = base.dropna(subset=["Regiao", coluna_ano])
    variaveis = obter_variaveis_numericas(
        base,
        coluna_ano=coluna_ano,
        ignorar_colunas=ignorar_colunas,
    )

    if agg_map is None:
        agg_map = construir_agregacoes(base, variaveis)

    df_agregado = (
        base.groupby(["Regiao", coluna_ano], as_index=False)
        .agg(agg_map)
    )

    df_agregado["Regiao"] = pd.Categorical(
        df_agregado["Regiao"],
        categories=ORDEM_REGIOES,
        ordered=True,
    )

    return df_agregado.sort_values(["Regiao", coluna_ano]).reset_index(drop=True)


def agregar_por_regiao_ano(df, coluna_estado="Estado", coluna_ano="Ano", ignorar_colunas=None, agg_map=None):
    return preparar_base_analitica(
        df,
        nivel="regiao",
        coluna_estado=coluna_estado,
        coluna_ano=coluna_ano,
        ignorar_colunas=ignorar_colunas,
        agg_map=agg_map,
    )


def preparar_base_estado_ano(df, coluna_estado="Estado", coluna_ano="Ano"):
    return preparar_base_analitica(
        df,
        nivel="estado",
        coluna_estado=coluna_estado,
        coluna_ano=coluna_ano,
    )


def obter_coluna_grupo(nivel="regiao"):
    nivel = str(nivel).lower()
    if nivel == "regiao":
        return "Regiao"
    if nivel == "estado":
        return "Estado"
    raise ValueError("nivel deve ser 'regiao' ou 'estado'.")
