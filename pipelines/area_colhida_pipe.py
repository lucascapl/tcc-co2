import pandas as pd

from utils import ANO_FINAL, ANO_INICIAL, ORDEM_REGIOES, ordenar_regioes, salvar_tratado


def processar_area_colhida(
    caminho_arquivo: str = "bases/area-colhida-regiao-1974-2024-ibge.csv.csv",
    agrupar_por_regiao: bool = True,
):
    """
    Processa a base regional de area colhida (IBGE) e retorna:
    Regiao | Ano | area_colhida
    """
    if not agrupar_por_regiao:
        raise ValueError("Esta base ja e regional. Use agrupar_por_regiao=True.")

    raw = pd.read_csv(caminho_arquivo, header=None)

    anos = pd.to_numeric(raw.iloc[3, 1:], errors="coerce")
    colunas_validas = [i for i, ano in enumerate(anos.tolist(), start=1) if pd.notna(ano)]

    base = raw.iloc[5:, [0] + colunas_validas].copy()
    base.columns = ["Regiao"] + [int(raw.iloc[3, i]) for i in colunas_validas]

    base["Regiao"] = base["Regiao"].astype(str).str.strip()
    base = base[base["Regiao"].isin(ORDEM_REGIOES)].copy()

    base_long = base.melt(
        id_vars=["Regiao"],
        var_name="Ano",
        value_name="area_colhida",
    )

    base_long["Ano"] = pd.to_numeric(base_long["Ano"], errors="coerce").astype("Int64")
    base_long = base_long[
        (base_long["Ano"] >= ANO_INICIAL) & (base_long["Ano"] <= ANO_FINAL)
    ].copy()

    base_long["area_colhida"] = pd.to_numeric(base_long["area_colhida"], errors="coerce")

    base_long = ordenar_regioes(base_long, coluna_regiao="Regiao", coluna_ano="Ano")
    return salvar_tratado(base_long, "area-colhida-regiao")
