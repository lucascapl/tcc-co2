import pandas as pd
from utils import ANO_FINAL, ANO_INICIAL, normalizar_estado, salvar_tratado, agregar_por_regiao_ano


def processar_rebanho(agregar_total: bool = True, agrupar_por_regiao: bool = False):
    # lê sem cabeçalho para reconstruir
    raw = pd.read_excel("bases/rebanho-1974-2023-ibge.xlsx", sheet_name="Tabela", header=None)

    # linha 0 = anos (um por bloco); linha 1 = tipos de animal (um por coluna)
    years_row = raw.iloc[0, 1:].copy()
    types_row = raw.iloc[1, 1:].copy().astype(str)

    # propagar anos para a direita (cada bloco de categorias pertence ao mesmo ano)
    years_ffill = years_row.ffill()

    # montar colunas: primeira é Estado; restantes são pares (Ano, Animal)
    n_cols = 1 + len(years_ffill)
    tuples = [("Estado", "")] + list(zip(years_ffill.tolist(), types_row.tolist()))

    # Recortar dados (a partir da linha 2 começam os estados)
    df = raw.iloc[2:, :n_cols].copy()
    df.columns = pd.MultiIndex.from_tuples(tuples, names=["Ano", "Animal"])

    # Renomear coluna de Estado para nível simples e remover linhas vazias
    df = df.rename(columns={("Estado", ""): "Estado"})
    df = df[df["Estado"].notna()]

    # Empilhar (wide MultiIndex -> long)
    df_long = (
        df.set_index("Estado")
          .stack(level=[0, 1])
          .reset_index()
    )
    df_long.columns = ["Estado", "Ano", "Animal", "Quantidade"]

    # Tipos e recorte de anos
    df_long["Ano"] = pd.to_numeric(df_long["Ano"], errors="coerce").astype("Int64")
    df_long = df_long[(df_long["Ano"] >= ANO_INICIAL) & (df_long["Ano"] <= ANO_FINAL)]

    df_long["Animal"] = df_long["Animal"].astype(str).str.strip()
    df_long = df_long[df_long["Animal"].str.upper() == "BOVINO"]

    # Quantidades numéricas (trata "-", vazios etc.)
    df_long["Quantidade"] = pd.to_numeric(df_long["Quantidade"], errors="coerce").fillna(0)

    # Normalizar Estado -> UF e descartar linhas sem mapeamento
    df_long["Estado"] = df_long["Estado"].apply(normalizar_estado)
    df_long = df_long.dropna(subset=["Estado"])

    # Salva versão detalhada (útil para análises por tipo)
    #salvar_tratado(df_long[["Estado", "Ano", "Animal", "Quantidade"]], "rebanho_detalhado")

    if agregar_total:
        # Agrega tudo em rebanho
        df_total = (
            df_long.groupby(["Estado", "Ano"], as_index=False)["Quantidade"]
                   .sum()
                   .rename(columns={"Quantidade": "rebanho"})
        )
        if agrupar_por_regiao:
            df_total = agregar_por_regiao_ano(df_total)
            return salvar_tratado(df_total, "rebanho-regiao")
        return salvar_tratado(df_total, "rebanho-estado")

    # OU: gerar colunas por animal (pivot)
    wide = (
        df_long.pivot_table(
            index=["Estado", "Ano"],
            columns="Animal",
            values="Quantidade",
            aggfunc="sum",
            fill_value=0,
        )
        .reset_index()
    )

    if agrupar_por_regiao:
        wide = agregar_por_regiao_ano(wide)
        return salvar_tratado(wide, "rebanho-animal-regiao")

    # Observação: os nomes das colunas ficam como os animais (com acentos).
    return salvar_tratado(wide, "rebanho-animal-estado")
