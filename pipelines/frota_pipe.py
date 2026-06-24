import re
import pandas as pd
from utils import ANO_FINAL, ANO_INICIAL, salvar_tratado, agregar_por_regiao_ano


TIPOS_MOTORIZADOS_EMITENTES = {
    "automovel",
    "caminhao",
    "caminhaotrator",
    "caminhonete",
    "camioneta",
    "ciclomotor",
    "microonibus",
    "motocicleta",
    "motoneta",
    "onibus",
    "quadriciclo",
    "triciclo",
    "utilitario",
}


def _normalizar_tipo_veiculo(valor: str) -> str:
    texto = str(valor).strip().lower()
    # Remove espacos, hifens e outros separadores para unificar grafias.
    return re.sub(r"[^a-z0-9]", "", texto)


def processar_frota(agrupar_por_regiao: bool = False):
    # Ler base (separador ; já confirmado)
    df = pd.read_csv("bases/frota-veiculos-2003-2023-denatran.csv", sep=";")

    # Garantir tipos corretos
    df["mes"] = pd.to_numeric(df["mes"], errors="coerce")
    df["ano"] = pd.to_numeric(df["ano"], errors="coerce").astype(int)
    df["quantidade"] = pd.to_numeric(df["quantidade"], errors="coerce").fillna(0)

    # Filtrar período de interesse
    df = df[(df["ano"] >= ANO_INICIAL) & (df["ano"] <= ANO_FINAL)]

    # Mantem somente categorias motorizadas com emissao direta na frota.
    df["tipo_norm"] = df["tipo_veiculo"].apply(_normalizar_tipo_veiculo)
    df = df[df["tipo_norm"].isin(TIPOS_MOTORIZADOS_EMITENTES)]

    # A base é mensal e cada mês traz linhas por tipo de veículo.
    # Primeiro somamos os tipos motorizados dentro de cada mês e, só depois,
    # usamos o último mês disponível no ano (normalmente dezembro) como
    # retrato do estoque anual.
    df = df.groupby(["sigla_uf", "ano", "mes"], as_index=False)["quantidade"].sum()
    df = df.dropna(subset=["mes"]).copy()
    df["mes"] = df["mes"].astype(int)
    df = df.sort_values(["sigla_uf", "ano", "mes"])
    df_agg = df.groupby(["sigla_uf", "ano"], as_index=False).tail(1)
    df_agg = df_agg[["sigla_uf", "ano", "quantidade"]]

    # Renomear colunas para padrão
    df_agg = df_agg.rename(columns={
        "sigla_uf": "Estado",
        "ano": "Ano",
        "quantidade": "frota"
    })

    if agrupar_por_regiao:
        df_agg = agregar_por_regiao_ano(df_agg)
        return salvar_tratado(df_agg, "frota-regiao")

    # Salvar tratado
    return salvar_tratado(df_agg, "frota-estado")
