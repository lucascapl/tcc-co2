import pandas as pd

from utils import ANO_FINAL, ANO_INICIAL, ORDEM_REGIOES, ordenar_regioes, salvar_tratado


def processar_area_destinada_colheita(
    caminho_arquivo: str = "bases/area-destinada-colheita-1988-2024-ibge.csv",
    agrupar_por_regiao: bool = True,
):
    """
    Processa a base regional de area destinada a colheita (IBGE) e retorna:
    Regiao | Ano | area_destinada_colheita
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
        value_name="area_destinada_colheita",
    )

    base_long["Ano"] = pd.to_numeric(base_long["Ano"], errors="coerce").astype("Int64")
    base_long = base_long[
        (base_long["Ano"] >= ANO_INICIAL) & (base_long["Ano"] <= ANO_FINAL)
    ].copy()

    base_long["area_destinada_colheita"] = pd.to_numeric(
        base_long["area_destinada_colheita"], errors="coerce"
    )

    base_long = ordenar_regioes(base_long, coluna_regiao="Regiao", coluna_ano="Ano")
    return salvar_tratado(base_long, "area-destinada-colheita-regiao")
