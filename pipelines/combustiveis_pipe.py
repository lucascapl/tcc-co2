import pandas as pd
from utils import ANO_FINAL, ANO_INICIAL, normalizar_estado, salvar_tratado, agregar_por_regiao_ano


def processar_combustiveis(
    arquivo: str = "bases/venda-combustiveis-m3-1990-2025-dados_gov.csv",
    produtos=None,
    agrupar_por_regiao: bool = False,
):
    """
    Processa a base de vendas de combustíveis.

    Regras:
    - mantém apenas anos de 2003 a 2018
    - agrega os meses em total anual
    - por padrão soma todos os produtos em uma única métrica anual
    - opcionalmente filtra apenas alguns produtos
    - opcionalmente agrega de Estado para Região
    """
    df = pd.read_csv(arquivo, sep=";")

    # padronizar colunas
    df.columns = [str(c).strip() for c in df.columns]

    # tipos
    df["ANO"] = pd.to_numeric(df["ANO"], errors="coerce").astype("Int64")
    df = df[(df["ANO"] >= ANO_INICIAL) & (df["ANO"] <= ANO_FINAL)]

    # filtro opcional por produto
    if produtos is not None:
        if isinstance(produtos, str):
            produtos = [produtos]
        produtos_norm = {str(p).strip().upper() for p in produtos}
        df["PRODUTO"] = df["PRODUTO"].astype(str).str.strip()
        df = df[df["PRODUTO"].str.upper().isin(produtos_norm)]

    # vendas em formato pt-BR decimal
    df["VENDAS"] = (
        df["VENDAS"]
        .astype(str)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )
    df["VENDAS"] = pd.to_numeric(df["VENDAS"], errors="coerce")

    # normalizar estado -> UF
    df["Estado"] = df["UNIDADE DA FEDERAÇÃO"].apply(normalizar_estado)
    df = df.dropna(subset=["Estado"])

    # agregar por estado e ano
    df_total = (
        df.groupby(["Estado", "ANO"], as_index=False)["VENDAS"]
          .sum(min_count=1)
                    .rename(columns={"ANO": "Ano", "VENDAS": "venda_comb"})
    )

    if agrupar_por_regiao:
        df_total = agregar_por_regiao_ano(df_total)
        return salvar_tratado(df_total, "venda-combustiveis")

    return salvar_tratado(df_total, "venda-combustiveis-estado")
