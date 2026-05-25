import os
import pandas as pd
import unicodedata

from config import CONFIG

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
ORDEM_ESTADOS = list(MAPA_REGIOES.keys())

# Período único usado por todos os pipelines de tratamento.
ANO_INICIAL = CONFIG.ANO_INICIAL
ANO_FINAL = CONFIG.ANO_FINAL


def normalizar_texto(txt: str) -> str:
    if pd.isna(txt):
        return txt
    txt = str(txt).strip()
    txt = unicodedata.normalize("NFKD", txt).encode("ASCII", "ignore").decode("utf-8")
    return txt


def normalizar_estado(nome_estado: str) -> str | None:
    if pd.isna(nome_estado):
        return None
    texto = str(nome_estado).strip()
    if not texto or texto.upper() in MAPA_REGIOES:
        return texto.upper() if texto.upper() in MAPA_REGIOES else None

    nome_estado_norm = normalizar_texto(texto).title()
    for nome, uf in MAPA_ESTADOS.items():
        nome_norm = normalizar_texto(nome).title()
        if nome_estado_norm == nome_norm:
            return uf
    return None


def salvar_tratado(df, nome):
    os.makedirs(CONFIG.PASTA_TRATADAS, exist_ok=True)
    caminho = CONFIG.caminho_base_tratada(nome)
    df.to_csv(caminho, index=False)
    print(f"✅ Base '{nome}' tratada salva em {caminho}")
    return df


def preparar_pasta_graficos(caminho=None):
    if caminho is None:
        caminho = CONFIG.PASTA_GRAFICOS
    os.makedirs(caminho, exist_ok=True)


def adicionar_regiao(df, coluna_estado="Estado"):
    base = df.copy()
    if coluna_estado not in base.columns:
        raise ValueError(f"Coluna '{coluna_estado}' nao encontrada para adicionar Regiao.")
    base["Regiao"] = base[coluna_estado].map(MAPA_REGIOES)
    return base


def inferir_coluna_grupo(df, coluna_grupo=None):
    if coluna_grupo:
        if coluna_grupo not in df.columns:
            raise ValueError(f"Coluna de grupo '{coluna_grupo}' nao encontrada no dataframe.")
        return coluna_grupo
    if "Estado" in df.columns:
        return "Estado"
    if "Regiao" in df.columns:
        return "Regiao"
    raise ValueError("Nao encontrei coluna de agrupamento. Esperado 'Estado' ou 'Regiao'.")


def ordenar_grupos(df, coluna_grupo="Estado", coluna_ano="Ano"):
    base = df.copy()
    sort_cols = []

    if coluna_grupo in base.columns:
        if coluna_grupo == "Regiao":
            base[coluna_grupo] = pd.Categorical(
                base[coluna_grupo],
                categories=ORDEM_REGIOES,
                ordered=True,
            )
        elif coluna_grupo == "Estado":
            base[coluna_grupo] = pd.Categorical(
                base[coluna_grupo],
                categories=ORDEM_ESTADOS,
                ordered=True,
            )
        sort_cols.append(coluna_grupo)

    if coluna_ano in base.columns:
        sort_cols.append(coluna_ano)

    if sort_cols:
        base = base.sort_values(sort_cols).reset_index(drop=True)
    return base


def ordenar_regioes(df, coluna_regiao="Regiao", coluna_ano="Ano"):
    return ordenar_grupos(df, coluna_grupo=coluna_regiao, coluna_ano=coluna_ano)


def obter_variaveis_numericas(df, coluna_ano="Ano", ignorar_colunas=None):
    if ignorar_colunas is None:
        ignorar_colunas = ["IDHM"]
    ignorar = set(ignorar_colunas) | {coluna_ano}
    colunas_numericas = df.select_dtypes(include=["number"]).columns.tolist()
    return [c for c in colunas_numericas if c not in ignorar]


def construir_agregacoes(df, variaveis=None):
    if variaveis is None:
        variaveis = obter_variaveis_numericas(df)
    return {var: (lambda s: s.sum(min_count=1)) for var in variaveis}


def base_grupo_ano(
    df,
    coluna_grupo=None,
    coluna_ano="Ano",
    ignorar_colunas=None,
    agregar_para_regiao=False,
    agg_map=None,
):
    """
    Retorna uma base coerente com a granularidade escolhida.

    - coluna_grupo="Estado" e agregar_para_regiao=False: mantém Estado/Ano.
    - coluna_grupo="Regiao" ou agregar_para_regiao=True: retorna Regiao/Ano.
    """
    base = df.copy()

    if agregar_para_regiao:
        return base_regional_ano(
            base,
            coluna_ano=coluna_ano,
            ignorar_colunas=ignorar_colunas,
            agg_map=agg_map,
        )

    coluna_grupo = inferir_coluna_grupo(base, coluna_grupo)
    base = base.dropna(subset=[coluna_grupo, coluna_ano]).copy()
    base[coluna_ano] = pd.to_numeric(base[coluna_ano], errors="coerce")
    base = base.dropna(subset=[coluna_ano]).copy()
    base[coluna_ano] = base[coluna_ano].astype(int)

    # Se houver duplicidade acidental na chave Grupo/Ano, consolida com soma para
    # manter uma linha por unidade temporal sem quebrar as análises.
    if base.duplicated([coluna_grupo, coluna_ano]).any():
        variaveis = obter_variaveis_numericas(base, coluna_ano=coluna_ano, ignorar_colunas=ignorar_colunas)
        agg_map = agg_map or construir_agregacoes(base, variaveis)
        base = base.groupby([coluna_grupo, coluna_ano], as_index=False).agg(agg_map)

    return ordenar_grupos(base, coluna_grupo=coluna_grupo, coluna_ano=coluna_ano)


def base_regional_ano(
    df,
    coluna_estado="Estado",
    coluna_regiao="Regiao",
    coluna_ano="Ano",
    ignorar_colunas=None,
    agg_map=None,
):
    base = df.copy()

    if coluna_regiao in base.columns and coluna_estado not in base.columns:
        base = base.dropna(subset=[coluna_regiao, coluna_ano]).copy()
        return ordenar_regioes(base, coluna_regiao=coluna_regiao, coluna_ano=coluna_ano)

    return agregar_por_regiao_ano(
        base,
        coluna_estado=coluna_estado,
        coluna_ano=coluna_ano,
        ignorar_colunas=ignorar_colunas,
        agg_map=agg_map,
    )


def agregar_por_regiao_ano(
    df,
    coluna_estado="Estado",
    coluna_ano="Ano",
    ignorar_colunas=None,
    agg_map=None,
):
    base = adicionar_regiao(df, coluna_estado=coluna_estado)
    base = base.dropna(subset=["Regiao", coluna_ano]).copy()

    variaveis = obter_variaveis_numericas(
        base,
        coluna_ano=coluna_ano,
        ignorar_colunas=ignorar_colunas,
    )

    if agg_map is None:
        agg_map = construir_agregacoes(base, variaveis)

    df_regional = base.groupby(["Regiao", coluna_ano], as_index=False).agg(agg_map)
    return ordenar_regioes(df_regional, coluna_regiao="Regiao", coluna_ano=coluna_ano)


def construir_base_defasada(
    df,
    coluna_alvo="co2",
    coluna_grupo=None,
    coluna_regiao=None,
    coluna_ano="Ano",
    defasagem_alvo=1,
):
    """
    Cria uma base em que a variável alvo é deslocada para frente no tempo.

    Exemplo com defasagem_alvo=1:
    X(2003) será comparado com CO2(2004).
    A coluna de ano preservada no resultado é a do preditor (X).

    Compatível com Estado/Ano ou Regiao/Ano.
    """
    base = df.copy()
    # coluna_regiao é mantida por compatibilidade com chamadas antigas.
    if coluna_grupo is None and coluna_regiao is not None:
        coluna_grupo = coluna_regiao
    coluna_grupo = inferir_coluna_grupo(base, coluna_grupo)

    base = base.dropna(subset=[coluna_grupo, coluna_ano]).copy()
    base[coluna_ano] = pd.to_numeric(base[coluna_ano], errors="coerce")
    base = base.dropna(subset=[coluna_ano]).copy()
    base[coluna_ano] = base[coluna_ano].astype(int)

    alvo = base[[coluna_grupo, coluna_ano, coluna_alvo]].copy()
    alvo = alvo.rename(columns={coluna_alvo: f"{coluna_alvo}_t+{defasagem_alvo}"})
    alvo[coluna_ano] = alvo[coluna_ano] - defasagem_alvo

    combinado = base.merge(alvo, on=[coluna_grupo, coluna_ano], how="left")
    return ordenar_grupos(combinado, coluna_grupo=coluna_grupo, coluna_ano=coluna_ano)
