import pandas as pd

from utils import (
    ANO_FINAL,
    ANO_INICIAL,
    normalizar_estado,
    salvar_tratado,
    agregar_por_regiao_ano,
    ordenar_regioes,
)


def _ler_tabela_ibge_area(caminho_arquivo: str) -> pd.DataFrame:
    """Le a planilha/CSV do SIDRA/IBGE sem cabecalho."""
    extensao = str(caminho_arquivo).lower().split(".")[-1]

    if extensao in {"xlsx", "xls", "xlsm"}:
        return pd.read_excel(caminho_arquivo, sheet_name="Tabela", header=None)

    return pd.read_csv(caminho_arquivo, header=None)


def _normalizar_estado_seguro(valor):
    """Normaliza apenas valores textuais validos, evitando erro com NaN/float."""
    if pd.isna(valor):
        return None

    valor = str(valor).strip()
    if not valor or valor.lower() in {"nan", "none", "null"}:
        return None

    return normalizar_estado(valor)


def _processar_area_ibge(caminho_arquivo: str, coluna_valor: str) -> pd.DataFrame:
    """
    Converte tabela wide do IBGE para Estado | Ano | valor.

    Layout esperado:
    - linha 3: anos;
    - coluna 1: Unidade da Federacao;
    - linhas 5 em diante: UFs.
    """
    raw = _ler_tabela_ibge_area(caminho_arquivo)

    anos = pd.to_numeric(raw.iloc[3, :], errors="coerce")
    colunas_anos = [i for i, ano in anos.items() if pd.notna(ano)]

    if not colunas_anos:
        raise ValueError("Nao foram encontradas colunas de ano na linha esperada da tabela IBGE.")

    base = raw.iloc[5:, [1] + colunas_anos].copy()
    base.columns = ["Estado"] + [int(anos.loc[i]) for i in colunas_anos]

    # Remove linhas sem UF antes de chamar normalizar_estado, pois utils.normalizar_estado
    # nao trata NaN/float.
    base = base[base["Estado"].notna()].copy()
    base["Estado"] = base["Estado"].map(_normalizar_estado_seguro)
    base = base.dropna(subset=["Estado"])

    base_long = base.melt(
        id_vars=["Estado"],
        var_name="Ano",
        value_name=coluna_valor,
    )

    base_long["Ano"] = pd.to_numeric(base_long["Ano"], errors="coerce").astype("Int64")
    base_long = base_long[
        (base_long["Ano"] >= ANO_INICIAL) & (base_long["Ano"] <= ANO_FINAL)
    ].copy()

    # Trata separador decimal/strings do Excel/CSV sem quebrar valores numericos.
    base_long[coluna_valor] = pd.to_numeric(
        base_long[coluna_valor].replace({"...": pd.NA, "-": pd.NA}),
        errors="coerce",
    )

    return (
        base_long.groupby(["Estado", "Ano"], as_index=False)[coluna_valor]
        .sum(min_count=1)
        .sort_values(["Estado", "Ano"])
        .reset_index(drop=True)
    )


def processar_area_destinada_colheita(
    caminho_arquivo: str = "bases/area-destinada-colheita-1988-2024-ibge.xlsx",
    agrupar_por_regiao: bool = False,
):
    """
    Processa area plantada/destinada a colheita (IBGE) e retorna:
    - Estado | Ano | area_destinada_colheita, quando agrupar_por_regiao=False;
    - Regiao | Ano | area_destinada_colheita, quando agrupar_por_regiao=True.
    """
    df = _processar_area_ibge(caminho_arquivo, "area_destinada_colheita")

    if agrupar_por_regiao:
        df = agregar_por_regiao_ano(df)
        df = ordenar_regioes(df, coluna_regiao="Regiao", coluna_ano="Ano")
        return salvar_tratado(df, "area-destinada-colheita-regiao")

    return salvar_tratado(df, "area-destinada-colheita-estado")
