import pandas as pd

from utils import ANO_FINAL, ANO_INICIAL, normalizar_estado, salvar_tratado, agregar_por_regiao_ano


def _extrair_ano(valor) -> int | None:
    if pd.isna(valor):
        return None
    texto = str(valor).strip().replace("*", "")
    if not texto:
        return None
    if texto.isdigit():
        return int(texto)
    return None


def _parse_numero(valor):
    if pd.isna(valor):
        return None
    if isinstance(valor, (int, float)):
        return float(valor)
    texto = str(valor).strip()
    if not texto or texto == "...":
        return None
    texto = texto.replace(".", "").replace(",", ".")
    return pd.to_numeric(texto, errors="coerce")


def processar_consumo_energia_industrial(
    caminho_arquivo: str = "bases/consumo-energia-eletrica-industrial-estado-2004-2025-epe.xlsx",
    agrupar_por_regiao: bool = False,
):
    """
    Processa a base estadual da EPE (planilha com anos e meses em linhas separadas)
    e devolve consumo anual por UF.

    Saida estadual:
        Estado | Ano | consumo_energia_industrial

    Saida regional (opcional):
        Regiao | Ano | consumo_energia_industrial
    """
    df = pd.read_excel(caminho_arquivo, sheet_name=0, header=None)

    anos_linha = df.iloc[4, 1:]
    anos = [_extrair_ano(a) for a in anos_linha.tolist()]
    if all(a is None for a in anos):
        raise ValueError("Nao foi possivel localizar a linha de anos na planilha.")

    dados = df.iloc[6:, 1:].copy()
    dados = dados.applymap(_parse_numero)
    dados.columns = anos

    # soma os meses por ano
    dados_ano = dados.groupby(level=0, axis=1).sum(min_count=1)

    estados = df.iloc[6:, 0].astype(str).str.strip()
    estados = estados[~estados.str.upper().str.contains("TOTAL", na=False)]
    estados = estados[~estados.str.upper().str.contains("NOTA", na=False)]
    estados_uf = estados.apply(normalizar_estado)

    dados_ano = dados_ano.loc[estados.index]
    dados_ano.insert(0, "Estado", estados_uf.values)
    dados_ano = dados_ano.dropna(subset=["Estado"])

    df_long = dados_ano.melt(
        id_vars=["Estado"],
        var_name="Ano",
        value_name="consumo_energia_industrial",
    )
    df_long["Ano"] = pd.to_numeric(df_long["Ano"], errors="coerce").astype("Int64")
    df_long = df_long.dropna(subset=["Ano"])
    df_long = df_long[(df_long["Ano"] >= ANO_INICIAL) & (df_long["Ano"] <= ANO_FINAL)]

    df_long["consumo_energia_industrial"] = pd.to_numeric(
        df_long["consumo_energia_industrial"], errors="coerce"
    )

    # Mantem chave unica por estado/ano
    df_long = (
        df_long.groupby(["Estado", "Ano"], as_index=False)["consumo_energia_industrial"]
        .sum(min_count=1)
    )

    if agrupar_por_regiao:
        df_long = agregar_por_regiao_ano(df_long)
        return salvar_tratado(df_long, "energia-industrial-regiao")

    return salvar_tratado(df_long, "energia-industrial-estado")
