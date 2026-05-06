import pandas as pd
from utils import ANO_FINAL, ANO_INICIAL, normalizar_estado, salvar_tratado, agregar_por_regiao_ano


def processar_co2(agrupar_por_regiao: bool = False):
    df = pd.read_csv("bases/emissao-co2-bruto-1990-2023-seeg.csv")

    df = df.melt(id_vars=["Categoria"], var_name="Ano", value_name="co2")
    df = df.rename(columns={"Categoria": "Estado"})

    df["Ano"] = pd.to_numeric(df["Ano"], errors="coerce").astype("Int64")
    df = df[(df["Ano"] >= ANO_INICIAL) & (df["Ano"] <= ANO_FINAL)]

    # remover a linha "Não alocado" (case-insensitive)
    df = df[df["Estado"].astype(str).str.strip().str.casefold() != "não alocado".casefold()]

    # normalizar Estado -> UF
    df["Estado"] = df["Estado"].apply(normalizar_estado)

    # descartar qualquer linha que não mapeou para UF
    df = df.dropna(subset=["Estado"])

    # garantir numérico
    df["co2"] = pd.to_numeric(df["co2"], errors="coerce")

    if agrupar_por_regiao:
        df = agregar_por_regiao_ano(df)
        return salvar_tratado(df, "co2-regiao")

    return salvar_tratado(df, "co2-estado")
