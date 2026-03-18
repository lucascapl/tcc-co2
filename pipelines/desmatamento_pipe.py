# pipelines/desmatamento_pipeline.py
import pandas as pd
from utils import normalizar_estado, salvar_tratado

ANOS_MIN = 2003
ANOS_MAX = 2018

def processar_desmatamento(municipio_file: str, desmatamento_file: str) -> pd.DataFrame:
    """
    Processa os dados de desmatamento por município, mapeia os municípios para estados,
    e retorna um DataFrame de desmatamento por Estado.
    """
    # carregar a ferramenta do INPE (municípios -> estado)
    df_municipios = pd.read_csv(municipio_file, sep=";", encoding="utf-8-sig")
    
    # verificar as primeiras linhas e corrigir os nomes das colunas pois estavam cheias de simbolos
    df_municipios.columns = df_municipios.columns.str.replace("ï»¿", "", regex=False)
    df_municipios.columns = df_municipios.columns.str.strip()
    
    # mapeamento: Código Município Completo -> Estado (UF)
    df_municipios = df_municipios[["Código Município Completo", "Nome_UF"]].drop_duplicates()
    
    # carregar os dados de desmatamento do INPE
    df_desmatamento = pd.read_csv(desmatamento_file, sep=",", encoding="latin1")
    
    # mapear o município para o Estado
    df_desmatamento = df_desmatamento.merge(
        df_municipios,
        left_on="id_municipio",
        right_on="Código Município Completo",
        how="left"
    )
    
    # normalizar o nome do Estado para a sigla
    df_desmatamento["Estado"] = df_desmatamento["Nome_UF"].apply(normalizar_estado)

    # filtrar os anos de interesse
    df_desmatamento = df_desmatamento[(df_desmatamento["ano"] >= ANOS_MIN) & (df_desmatamento["ano"] <= ANOS_MAX)]

    # agregar por Estado e Ano (somando a área desmatada por km2)
    df_aggregated = df_desmatamento.groupby(["Estado", "ano"], as_index=False)["desmatado"].sum()

    # renomear colunas para o padrao do df_principal
    df_aggregated = df_aggregated.rename(columns={"ano": "Ano", "desmatado": "Area_Desmatada km2"})

    # salvar o DataFrame tratado
    return salvar_tratado(df_aggregated, "desmatamento_por_estado")
