import pandas as pd


def relatorio_missing_values(df):
    return (
        pd.DataFrame({
            "coluna": df.columns,
            "missing": df.isna().sum().values,
            "percentual_missing": (df.isna().mean().values * 100).round(2),
        })
        .sort_values(["missing", "coluna"], ascending=[False, True])
        .reset_index(drop=True)
    )


def interpolar_coluna_por_grupo_tempo(
    df,
    coluna,
    grupo="Estado",
    tempo="Ano",
    metodo="linear",
    limitar_direcao="both",
    arredondar=False,
):
    if grupo not in df.columns:
        raise ValueError(f"Coluna de grupo '{grupo}' nao encontrada no dataframe.")
    if tempo not in df.columns:
        raise ValueError(f"Coluna de tempo '{tempo}' nao encontrada no dataframe.")
    if coluna not in df.columns:
        return df.copy()

    base = df.copy().sort_values([grupo, tempo]).reset_index(drop=True)
    base[coluna] = pd.to_numeric(base[coluna], errors="coerce")
    base[coluna] = (
        base.groupby(grupo, group_keys=False)[coluna]
        .apply(lambda s: s.interpolate(method=metodo, limit_direction=limitar_direcao))
    )
    if arredondar:
        base[coluna] = base[coluna].round()
    return base


def preencher_populacao_por_interpolacao(
    df,
    coluna_grupo="Estado",
    coluna_ano="Ano",
    coluna_populacao="Populacao",
    arredondar=True,
):
    return interpolar_coluna_por_grupo_tempo(
        df=df,
        coluna=coluna_populacao,
        grupo=coluna_grupo,
        tempo=coluna_ano,
        metodo="linear",
        limitar_direcao="both",
        arredondar=arredondar,
    )


def preparar_df_para_analise(
    df,
    preencher_populacao=True,
    arredondar_populacao=True,
    coluna_grupo=None,
    coluna_ano="Ano",
):
    base = df.copy()
    if coluna_grupo is None:
        coluna_grupo = "Estado" if "Estado" in base.columns else "Regiao"

    if preencher_populacao and "Populacao" in base.columns:
        base = preencher_populacao_por_interpolacao(
            base,
            coluna_grupo=coluna_grupo,
            coluna_ano=coluna_ano,
            coluna_populacao="Populacao",
            arredondar=arredondar_populacao,
        )
    return base
