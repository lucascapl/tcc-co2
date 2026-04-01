import pandas as pd
from utils import normalizar_estado, salvar_tratado, agregar_por_regiao_ano

ANOS_MIN = 2003
ANOS_MAX = 2018


def processar_co2(agrupar_por_regiao: bool = False):
    df = pd.read_csv("bases/co2_bruto.csv")

    df = df.melt(id_vars=["Categoria"], var_name="Ano", value_name="CO2_bruto")
    df = df.rename(columns={"Categoria": "Estado"})

    df["Ano"] = pd.to_numeric(df["Ano"], errors="coerce").astype("Int64")
    df = df[(df["Ano"] >= ANOS_MIN) & (df["Ano"] <= ANOS_MAX)]

    # remover a linha "Não alocado" (case-insensitive)
    df = df[df["Estado"].astype(str).str.strip().str.casefold() != "não alocado".casefold()]

    # normalizar Estado -> UF
    df["Estado"] = df["Estado"].apply(normalizar_estado)

    # descartar qualquer linha que não mapeou para UF
    df = df.dropna(subset=["Estado"])

    # garantir numérico
    df["CO2_bruto"] = pd.to_numeric(df["CO2_bruto"], errors="coerce")

    if agrupar_por_regiao:
        df = agregar_por_regiao_ano(df)
        return salvar_tratado(df, "co2_regiao")

    return salvar_tratado(df, "co2")
