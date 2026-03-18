# pipelines/idhm_pipeline.py
import pandas as pd
from utils import normalizar_estado, salvar_tratado

ANOS_MIN = 2003
ANOS_MAX = 2018

def processar_idhm():
    df = pd.read_excel("bases/IDHM_1991_2021.xlsx", sheet_name="Worksheet", header=0)

    # Renomear a primeira coluna
    df = df.rename(columns={df.columns[0]: "Estado"})

    # Remover Brasil
    df = df[df["Estado"] != "Brasil"]

    # Derreter colunas
    df_long = df.melt(id_vars=["Estado"], var_name="Coluna", value_name="IDHM")

    # Extrair ano (mantendo apenas dígitos)
    df_long["Ano"] = df_long["Coluna"].str.extract(r"(\d{4})")
    df_long.drop(columns=["Coluna"], inplace=True)

    # Converter tipos
    df_long["Ano"] = pd.to_numeric(df_long["Ano"], errors="coerce")
    df_long = df_long[(df_long["Ano"] >= ANOS_MIN) & (df_long["Ano"] <= ANOS_MAX)]
    df_long["IDHM"] = pd.to_numeric(df_long["IDHM"], errors="coerce")

    # Normalizar Estado -> UF
    df_long["Estado"] = df_long["Estado"].apply(normalizar_estado)

    # Organizar colunas
    df_long = df_long[["Estado", "Ano", "IDHM"]].sort_values(["Estado", "Ano"]).reset_index(drop=True)

    return salvar_tratado(df_long, "idhm")
