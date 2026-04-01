import pandas as pd
from utils import normalizar_estado, salvar_tratado, agregar_por_regiao_ano


def processar_populacao(agrupar_por_regiao: bool = False):
    # Ler sem cabeçalho para reconstruir colunas manualmente
    raw = pd.read_excel("bases/populacao.xlsx", sheet_name="Tabela", header=None)

    # Linha 3 (index 3) traz os anos nas colunas 2..N (2003, 2004, ..., 2025)
    anos = raw.iloc[3, 2:].tolist()
    anos = [int(a) if pd.notna(a) else a for a in anos]

    colunas = ["Tipo", "Estado"] + anos

    # Dados começam na linha 4 (index 4). Colunas até o tamanho do cabeçalho montado
    df = raw.iloc[4:, :len(colunas)].copy()
    df.columns = colunas

    # Ficar apenas com linhas de UFs (exclui Brasil/BR e quaisquer outras linhas)
    df = df[df["Tipo"] == "UF"].drop(columns=["Tipo"])

    # Derreter para longo
    df_long = df.melt(id_vars=["Estado"], var_name="Ano", value_name="Populacao")

    # Limpar/forçar tipos
    df_long = df_long[pd.to_numeric(df_long["Ano"], errors="coerce").notnull()]
    df_long["Ano"] = df_long["Ano"].astype(int)

    # Período do TCC
    df_long = df_long[(df_long["Ano"] >= 2003) & (df_long["Ano"] <= 2018)]

    # Normalizar Estado -> UF
    df_long["Estado"] = df_long["Estado"].apply(normalizar_estado)

    # População numérica (nullable int)
    df_long["Populacao"] = pd.to_numeric(df_long["Populacao"], errors="coerce").astype("Int64")

    # Ordenar/organizar
    df_long = df_long[["Estado", "Ano", "Populacao"]].sort_values(["Estado", "Ano"]).reset_index(drop=True)

    if agrupar_por_regiao:
        df_long = agregar_por_regiao_ano(df_long)
        return salvar_tratado(df_long, "populacao_regiao")

    return salvar_tratado(df_long, "populacao")
