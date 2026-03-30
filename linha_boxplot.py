import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from utils import MAPA_REGIOES, ORDEM_REGIOES, preparar_pasta_graficos

sns.set_theme(style="whitegrid")


def grafico_linha_co2_brasil(df, salvar=False, caminho="graficos/co2_linha_anos.png"):
    base = df.copy()
    base["Ano"] = pd.to_numeric(base["Ano"], errors="coerce")
    base["CO2_bruto"] = pd.to_numeric(base["CO2_bruto"], errors="coerce")

    co2_ano = (
        base.groupby("Ano", as_index=False)["CO2_bruto"]
        .sum()
        .sort_values("Ano")
    )

    plt.figure(figsize=(10, 6))
    sns.lineplot(data=co2_ano, x="Ano", y="CO2_bruto", marker="o")
    plt.title("Emissões totais de CO2 no Brasil ao longo dos anos")
    plt.xlabel("Ano")
    plt.ylabel("CO2 bruto")
    plt.xticks(co2_ano["Ano"], rotation=45)
    plt.tight_layout()

    if salvar:
        preparar_pasta_graficos()
        plt.savefig(caminho, dpi=300, bbox_inches="tight")

    plt.show()


def boxplot_co2_por_regiao(df, salvar=False, caminho="graficos/co2_boxplot_regioes.png"):
    base = df.copy()
    base["CO2_bruto"] = pd.to_numeric(base["CO2_bruto"], errors="coerce")
    base["Regiao"] = base["Estado"].map(MAPA_REGIOES)
    base = base.dropna(subset=["Regiao", "CO2_bruto"])

    plt.figure(figsize=(10, 6))
    sns.boxplot(data=base, x="Regiao", y="CO2_bruto", order=ORDEM_REGIOES, showfliers=False)
    plt.title("Distribuição das emissões de CO2 por região do Brasil")
    plt.xlabel("Região")
    plt.ylabel("CO2 bruto")
    plt.tight_layout()

    if salvar:
        preparar_pasta_graficos()
        plt.savefig(caminho, dpi=300, bbox_inches="tight")

    plt.show()