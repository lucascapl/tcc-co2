import pandas as pd
from utils import salvar_tratado, agregar_por_regiao_ano


def processar_frota(agrupar_por_regiao: bool = False):
    # Ler base (separador ; já confirmado)
    df = pd.read_csv("bases/Frota Veiculos 2003-2023.csv", sep=";")

    # Garantir tipos corretos
    df["ano"] = pd.to_numeric(df["ano"], errors="coerce").astype(int)
    df["quantidade"] = pd.to_numeric(df["quantidade"], errors="coerce").fillna(0)

    # Filtrar período de interesse
    df = df[(df["ano"] >= 2003) & (df["ano"] <= 2018)]

    # Agregar: Frota total por estado e ano
    df_agg = df.groupby(["sigla_uf", "ano"], as_index=False)["quantidade"].sum()

    # Renomear colunas para padrão
    df_agg = df_agg.rename(columns={
        "sigla_uf": "Estado",
        "ano": "Ano",
        "quantidade": "Frota_total"
    })

    if agrupar_por_regiao:
        df_agg = agregar_por_regiao_ano(df_agg)
        return salvar_tratado(df_agg, "frota_regiao")

    # Salvar tratado
    return salvar_tratado(df_agg, "frota")
