import os
import pandas as pd

from utils import ANO_FINAL, ANO_INICIAL, normalizar_texto, ordenar_regioes, salvar_tratado

ARQUIVOS_PADRAO = [
    "bases/PIB-Municipios-2002-2009-ibge.xlsx",
    "bases/PIB-Municipios-2010-2023-ibge.xlsx",
]

MAPA_NOME_REGIAO = {
    "norte": "Norte",
    "nordeste": "Nordeste",
    "centrooeste": "Centro-Oeste",
    "sudeste": "Sudeste",
    "sul": "Sul",
}


def _normalizar_coluna(coluna: str) -> str:
    return (
        normalizar_texto(str(coluna))
        .strip()
        .lower()
        .replace("\n", " ")
        .replace("(r$ 1.000)", "")
        .replace("(r$ 1,00)", "")
        .replace(" ", "")
        .replace(",", "")
        .replace(".", "")
        .replace("-", "")
        .replace("_", "")
    )


def _normalizar_nome_regiao(valor: str) -> str | None:
    if pd.isna(valor):
        return None

    chave = (
        normalizar_texto(str(valor))
        .strip()
        .lower()
        .replace("-", "")
        .replace(" ", "")
    )
    return MAPA_NOME_REGIAO.get(chave)


def _encontrar_coluna(
    df: pd.DataFrame,
    chaves: list[str],
    excluir_chaves: list[str] | None = None,
) -> str:
    if excluir_chaves is None:
        excluir_chaves = []

    normalizadas = {col: _normalizar_coluna(col) for col in df.columns}
    for col, col_norm in normalizadas.items():
        if all(chave in col_norm for chave in chaves) and all(exc not in col_norm for exc in excluir_chaves):
            return col
    raise ValueError(f"Nao foi possivel localizar coluna com chaves {chaves}")


def _carregar_planilha_pib(caminho_arquivo: str) -> pd.DataFrame:
    if not os.path.exists(caminho_arquivo):
        return pd.DataFrame()

    xls = pd.ExcelFile(caminho_arquivo)
    aba = next((s for s in xls.sheet_names if "pib" in s.lower()), xls.sheet_names[0])
    df = pd.read_excel(caminho_arquivo, sheet_name=aba)

    col_ano = _encontrar_coluna(df, ["ano"])
    col_regiao = _encontrar_coluna(df, ["nomedagranderegiao"])
    col_pib_total = _encontrar_coluna(
        df,
        ["produtointernobruto", "precoscorrentes"],
        excluir_chaves=["percapita"],
    )
    col_pib_pc = _encontrar_coluna(df, ["produtointernobrutopercapita"])

    base = df[[col_ano, col_regiao, col_pib_total, col_pib_pc]].copy()
    base.columns = ["Ano", "Regiao", "pib_total_mil", "pib_pc"]
    base["Regiao"] = base["Regiao"].apply(_normalizar_nome_regiao)

    base["Ano"] = pd.to_numeric(base["Ano"], errors="coerce").astype("Int64")
    base["pib_total_mil"] = pd.to_numeric(base["pib_total_mil"], errors="coerce")
    base["pib_pc"] = pd.to_numeric(base["pib_pc"], errors="coerce")

    base = base.dropna(subset=["Ano", "Regiao", "pib_total_mil", "pib_pc"])
    base = base[(base["Ano"] >= ANO_INICIAL) & (base["Ano"] <= ANO_FINAL)]
    base = base[base["pib_pc"] > 0]

    # Populacao implicita para ponderar corretamente o PIB per capita regional.
    base["pop_implicita"] = (base["pib_total_mil"] * 1000.0) / base["pib_pc"]
    base = base[base["pop_implicita"] > 0]

    return base


def processar_pib_per_capita(
    arquivos: list[str] | None = None,
    agrupar_por_regiao: bool = True,
) -> pd.DataFrame:
    if arquivos is None:
        arquivos = ARQUIVOS_PADRAO

    partes = []
    for caminho in arquivos:
        parte = _carregar_planilha_pib(caminho)
        if not parte.empty:
            partes.append(parte)

    if not partes:
        raise FileNotFoundError("Nenhuma base de PIB municipal encontrada para processamento.")

    base = pd.concat(partes, ignore_index=True)

    # PIB per capita regional ponderado por populacao implicita.
    regional = (
        base.groupby(["Regiao", "Ano"], as_index=False)
        .agg({"pib_total_mil": "sum", "pop_implicita": "sum"})
    )
    regional["pib_pc"] = (regional["pib_total_mil"] * 1000.0) / regional["pop_implicita"]
    regional = regional[["Regiao", "Ano", "pib_pc"]]
    regional = ordenar_regioes(regional, coluna_regiao="Regiao", coluna_ano="Ano")

    if agrupar_por_regiao:
        return salvar_tratado(regional, "pib-percapita-regiao")

    return salvar_tratado(regional, "pib-percapita")
