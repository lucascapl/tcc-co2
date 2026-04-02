import pandas as pd

from utils import ANO_FINAL, ANO_INICIAL, normalizar_estado, agregar_por_regiao_ano, salvar_tratado


def processar_desmatamento_mapbiomas(
    caminho_arquivo="bases/desmatamento-bioma-estado-1987-2024-mapbiomas.xlsx",
    agrupar_por_regiao=True,
):
    """
    Processa a base de desmatamento do MapBiomas por estado/bioma/ano
    e devolve uma base no padrão do projeto.

    Saída regional:
        Regiao | Ano | desmat_area

    Saída estadual:
        Estado | Ano | desmat_area
    """

    df = pd.read_excel(caminho_arquivo, sheet_name="DEFORESTATION")

    colunas_anos = [c for c in df.columns if str(c).isdigit()]

    base = df.melt(
        id_vars=[
            "country",
            "biome",
            "state",
            "class",
            "transition_name",
            "class_level_0",
            "class_level_1",
            "class_level_2",
            "class_level_3",
            "class_level_4",
        ],
        value_vars=colunas_anos,
        var_name="Ano",
        value_name="desmat_area",
    )

    base["Ano"] = pd.to_numeric(base["Ano"], errors="coerce")
    base["desmat_area"] = pd.to_numeric(
        base["desmat_area"], errors="coerce"
    )

    base["state"] = base["state"].astype(str).str.strip()
    base["Estado"] = base["state"].apply(normalizar_estado)

    base = base.dropna(subset=["Estado", "Ano"])
    base["Ano"] = base["Ano"].astype(int)
    base = base[(base["Ano"] >= ANO_INICIAL) & (base["Ano"] <= ANO_FINAL)]

    # soma tudo por estado/ano:
    # - diferentes biomas dentro do mesmo estado
    # - supressão primária e secundária
    # - subclasses de cobertura
    df_estado = (
        base.groupby(["Estado", "Ano"], as_index=False)["desmat_area"]
        .sum(min_count=1)
    )

    #salvar_tratado(df_estado, "desmatamento_mapbiomas_estado")

    if not agrupar_por_regiao:
        return df_estado

    df_regional = agregar_por_regiao_ano(
        df_estado,
        coluna_estado="Estado",
        coluna_ano="Ano",
        ignorar_colunas=[],
    )

    salvar_tratado(df_regional, "desmatamento-mapbiomas")
    return df_regional