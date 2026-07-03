"""
Clusterizacao hierarquica dos estados a partir dos vetores de correlacao.

Este script segue a ideia descrita no artigo: cada estado e representado pelo
vetor de correlacoes entre CO2 e os potenciais direcionadores; em seguida, uma
clusterizacao hierarquica agrupa estados com perfis de emissao semelhantes.

Saidas:
    bases/tratadas/clusterizacao_estado_clusters.csv
    bases/tratadas/clusterizacao_estado_silhueta.csv
    bases/tratadas/clusterizacao_estado_perfil_medio.csv
    graficos/heatmaps/heatmap_clusterizacao_estado_correlacoes.png
"""

from __future__ import annotations

import os
from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
from scipy.cluster.hierarchy import dendrogram, fcluster, linkage
from scipy.spatial.distance import pdist, squareform

from heatmap_correlacao_estado import (
    ALPHA,
    BLOCO_POR_UF,
    CAMINHO_DF,
    COLUNA_ALVO,
    COLUNA_ANO,
    COLUNA_GRUPO,
    IGNORAR_COLUNAS,
    ROTULOS_VARIAVEIS,
    VARIAVEIS_CAUSAIS,
    calcular_correlacao_mista_por_estado,
)
from utils import preparar_pasta_graficos


PASTA_SAIDA_TABELAS = "bases/tratadas"
PASTA_SAIDA_GRAFICOS = "graficos/heatmaps"

CAMINHO_CLUSTERS = os.path.join(PASTA_SAIDA_TABELAS, "clusterizacao_estado_clusters.csv")
CAMINHO_SILHUETA = os.path.join(PASTA_SAIDA_TABELAS, "clusterizacao_estado_silhueta.csv")
CAMINHO_PERFIL_MEDIO = os.path.join(PASTA_SAIDA_TABELAS, "clusterizacao_estado_perfil_medio.csv")
CAMINHO_HEATMAP = os.path.join(PASTA_SAIDA_GRAFICOS, "heatmap_clusterizacao_estado_correlacoes.png")

# O artigo descreve a clusterizacao com base nos direcionadores, nao nas
# variaveis climaticas tratadas como consequencias.
VARIAVEIS_CLUSTER = [
    "desmat_area",
    "frp_anual_queimadas",
    "rebanho",
    "venda_comb",
    "frota",
    "consumo_energia_industrial",
    "area_colhida",
    "area_destinada_colheita",
]


def preparar_matriz_correlacoes(
    correlacoes: pd.DataFrame,
    variaveis_cluster: Iterable[str] = VARIAVEIS_CLUSTER,
) -> pd.DataFrame:
    base = correlacoes[correlacoes["Variavel"].isin(variaveis_cluster)].copy()
    matriz = base.pivot(index="Estado", columns="Variavel", values="Coeficiente")

    variaveis_presentes = [var for var in variaveis_cluster if var in matriz.columns]
    matriz = matriz[variaveis_presentes]

    # Correlacoes faltantes sao raras aqui; quando ocorrerem, usa-se a media da
    # variavel para preservar a dimensao do vetor sem criar extremos artificiais.
    matriz = matriz.apply(pd.to_numeric, errors="coerce")
    matriz = matriz.fillna(matriz.mean()).fillna(0)
    return matriz.sort_index()


def calcular_silhueta_manual(matriz: pd.DataFrame, labels: np.ndarray) -> float:
    labels = np.asarray(labels)
    grupos = np.unique(labels)
    if len(grupos) < 2 or len(grupos) >= len(labels):
        return float("nan")

    distancias = squareform(pdist(matriz.to_numpy(dtype=float), metric="euclidean"))
    valores = []

    for i, label in enumerate(labels):
        mesmo_grupo = np.where(labels == label)[0]
        mesmo_grupo = mesmo_grupo[mesmo_grupo != i]
        a_i = float(distancias[i, mesmo_grupo].mean()) if len(mesmo_grupo) else 0.0

        b_i = min(
            float(distancias[i, np.where(labels == outro)[0]].mean())
            for outro in grupos
            if outro != label
        )

        denominador = max(a_i, b_i)
        valores.append(0.0 if denominador == 0 else (b_i - a_i) / denominador)

    return float(np.mean(valores))


def avaliar_quantidade_clusters(
    matriz: pd.DataFrame,
    ligacao: np.ndarray,
    k_min: int = 2,
    k_max: int = 6,
) -> pd.DataFrame:
    limite_superior = min(k_max, len(matriz) - 1)
    resultados = []

    for k in range(k_min, limite_superior + 1):
        labels = fcluster(ligacao, t=k, criterion="maxclust")
        resultados.append({
            "k": k,
            "clusters_obtidos": int(len(np.unique(labels))),
            "silhueta": calcular_silhueta_manual(matriz, labels),
        })

    return pd.DataFrame(resultados)


def calcular_perfil_medio(
    df_principal: pd.DataFrame,
    clusters: pd.DataFrame,
    variaveis: Iterable[str] = VARIAVEIS_CLUSTER,
) -> pd.DataFrame:
    variaveis_presentes = [var for var in variaveis if var in df_principal.columns]
    medias_estado = df_principal.groupby(COLUNA_GRUPO, as_index=True)[variaveis_presentes].mean()

    desvios = medias_estado.std(ddof=0).replace(0, np.nan)
    zscores = (medias_estado - medias_estado.mean()) / desvios
    zscores = zscores.fillna(0)

    base = zscores.merge(
        clusters[["Estado", "Cluster"]],
        left_index=True,
        right_on="Estado",
        how="inner",
    )
    perfil = base.groupby("Cluster", as_index=False)[variaveis_presentes].mean()
    return perfil


def gerar_heatmap_clusterizacao(
    matriz: pd.DataFrame,
    clusters: pd.DataFrame,
    caminho_saida: str = CAMINHO_HEATMAP,
) -> None:
    ordem = clusters.sort_values(["Ordem_dendrograma", "Estado"])["Estado"].tolist()
    matriz_plot = matriz.loc[ordem].rename(columns=ROTULOS_VARIAVEIS)

    cmap = LinearSegmentedColormap.from_list(
        "azul_branco_vermelho",
        ["#2166ac", "#ffffff", "#b2182b"],
        N=256,
    )

    altura = max(7, 0.48 * len(matriz_plot) + 3)
    largura = max(10, 1.2 * len(matriz_plot.columns) + 5)
    plt.figure(figsize=(largura, altura))
    ax = sns.heatmap(
        matriz_plot,
        cmap=cmap,
        vmin=-1,
        vmax=1,
        center=0,
        annot=True,
        fmt=".2f",
        linewidths=0.4,
        linecolor="#eeeeee",
        cbar_kws={"label": "Coeficiente de correlacao"},
    )

    clusters_ordenados = clusters.set_index("Estado").loc[ordem]["Cluster"].tolist()
    for i in range(1, len(clusters_ordenados)):
        if clusters_ordenados[i] != clusters_ordenados[i - 1]:
            ax.hlines(i, *ax.get_xlim(), colors="black", linewidth=1.5)

    ax.set_title("Correlacao com CO2 por estado, ordenada por cluster", fontsize=13, pad=16)
    ax.set_xlabel("Variavel")
    ax.set_ylabel("Estado")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0)

    plt.tight_layout()
    preparar_pasta_graficos(os.path.dirname(caminho_saida) or PASTA_SAIDA_GRAFICOS)
    plt.savefig(caminho_saida, dpi=300, bbox_inches="tight")
    plt.close()


def executar_clusterizacao_estado(
    caminho_df: str = CAMINHO_DF,
    n_clusters: int = 3,
    metodo_ligacao: str = "ward",
) -> dict[str, pd.DataFrame]:
    df_principal = pd.read_csv(caminho_df)

    correlacoes = calcular_correlacao_mista_por_estado(
        df_principal,
        coluna_estado=COLUNA_GRUPO,
        coluna_ano=COLUNA_ANO,
        coluna_alvo=COLUNA_ALVO,
        ignorar_colunas=IGNORAR_COLUNAS,
        alpha=ALPHA,
    )

    matriz = preparar_matriz_correlacoes(correlacoes)
    ligacao = linkage(matriz.to_numpy(dtype=float), method=metodo_ligacao, metric="euclidean")
    silhueta = avaliar_quantidade_clusters(matriz, ligacao)

    labels = fcluster(ligacao, t=n_clusters, criterion="maxclust")
    folhas = dendrogram(ligacao, no_plot=True)["leaves"]
    ordem_por_estado = {
        matriz.index[pos]: ordem
        for ordem, pos in enumerate(folhas, start=1)
    }

    clusters = pd.DataFrame({
        "Estado": matriz.index,
        "Cluster": labels,
    })
    clusters["Ordem_dendrograma"] = clusters["Estado"].map(ordem_por_estado)
    clusters["Perfil_artigo"] = clusters["Estado"].map(BLOCO_POR_UF)
    clusters = clusters.sort_values(["Cluster", "Estado"]).reset_index(drop=True)

    perfil_medio = calcular_perfil_medio(df_principal, clusters)

    os.makedirs(PASTA_SAIDA_TABELAS, exist_ok=True)
    clusters.to_csv(CAMINHO_CLUSTERS, index=False)
    silhueta.to_csv(CAMINHO_SILHUETA, index=False)
    perfil_medio.to_csv(CAMINHO_PERFIL_MEDIO, index=False)
    gerar_heatmap_clusterizacao(matriz, clusters)

    print(f"Clusters salvos em: {CAMINHO_CLUSTERS}")
    print(f"Silhueta salva em: {CAMINHO_SILHUETA}")
    print(f"Perfil medio salvo em: {CAMINHO_PERFIL_MEDIO}")
    print(f"Heatmap salvo em: {CAMINHO_HEATMAP}")

    return {
        "clusters": clusters,
        "silhueta": silhueta,
        "perfil_medio": perfil_medio,
        "matriz_correlacoes": matriz.reset_index(),
    }


if __name__ == "__main__":
    executar_clusterizacao_estado()
