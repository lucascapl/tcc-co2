"""
Heatmaps de correlação por Estado entre CO2 e demais variáveis,
com os estados organizados em 3 blocos analíticos e variáveis separadas
entre possíveis CAUSAS e possíveis CONSEQUÊNCIAS.

Blocos:
1) Amazônia Legal
2) Agropecuária
3) Energia/industrial

Tipos de variável:
- Causas:
    area_colhida, area_destinada_colheita, consumo_energia_industrial,
    desmat_area, frota, frp_anual_queimadas, rebanho, venda_comb
- Consequências:
    chuva_media, temp_media

Regra metodológica:
- Para cada Estado e variável, aplica Shapiro-Wilk em CO2 e na variável analisada.
- Se ambas as séries não rejeitam normalidade (p > alpha), usa Pearson.
- Caso contrário, usa Spearman.
- Marca com asterisco (*) as correlações significativas (p < alpha).

Entradas esperadas:
    bases/tratadas/dataframe-principal-estado-tratada.csv

Saídas geradas:
    bases/tratadas/correlacao_estado_metodo_misto_blocos_causa_consequencia.csv
    bases/tratadas/correlacao_estado_heatmap_base_blocos_causa_consequencia.csv

    graficos/heatmaps/heatmap_correlacao_estado_blocos_causas.png
    graficos/heatmaps/heatmap_correlacao_estado_blocos_consequencias.png

    E, opcionalmente, heatmaps por bloco:
    graficos/heatmaps/heatmap_correlacao_estado_amazonia_legal_causas.png
    graficos/heatmaps/heatmap_correlacao_estado_amazonia_legal_consequencias.png
    graficos/heatmaps/heatmap_correlacao_estado_agropecuaria_causas.png
    graficos/heatmaps/heatmap_correlacao_estado_agropecuaria_consequencias.png
    graficos/heatmaps/heatmap_correlacao_estado_energia_industrial_causas.png
    graficos/heatmaps/heatmap_correlacao_estado_energia_industrial_consequencias.png

Observação:
    A coluna "internacoes" foi retirada da análise. Se ela ainda existir no
    dataframe principal por compatibilidade temporária, será ignorada.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
from scipy.stats import pearsonr, spearmanr, shapiro

try:
    from utils import preparar_pasta_graficos
except ImportError:
    def preparar_pasta_graficos(caminho="graficos"):
        os.makedirs(caminho, exist_ok=True)


CAMINHO_DF = "bases/tratadas/dataframe-principal-estado-tratada.csv"
PASTA_SAIDA_TABELAS = "bases/tratadas"
PASTA_SAIDA_GRAFICOS = "graficos/heatmaps"

COLUNA_GRUPO = "Estado"
COLUNA_ANO = "Ano"
COLUNA_ALVO = "co2"
ALPHA = 0.05
MIN_OBS = 3

# Internações saiu do trabalho. Mantemos aqui para evitar que entre caso exista
# em alguma versão antiga do dataframe principal.
IGNORAR_COLUNAS = ["IDHM", "internacoes"]

# ---------------------------------------------------------------------------
# Divisão analítica dos estados solicitada
# ---------------------------------------------------------------------------

BLOCOS_ESTADOS = {
    "Mudanca de Uso da Terra": [
        "AC", "AM", "AP", "MA", "MT", "PA", "RO", "RR", "TO",
    ],
    "Agropecuária": [
        "BA", "GO", "MS", "PI", "CE", "RN", "PB", "PE", "AL", "SE",
    ],
    "Energia/industrial": [
        "SP", "RJ", "MG", "ES", "PR", "SC", "RS", "DF",
    ],
}

ORDEM_BLOCOS = list(BLOCOS_ESTADOS.keys())

BLOCO_POR_UF = {
    uf: bloco
    for bloco, estados in BLOCOS_ESTADOS.items()
    for uf in estados
}

ORDEM_ESTADOS_POR_BLOCO = [
    uf
    for bloco in ORDEM_BLOCOS
    for uf in BLOCOS_ESTADOS[bloco]
]

SLUG_BLOCO = {
    "Mudanca de Uso da Terra": "mudanca_uso_da_terra",
    "Agropecuária": "agropecuaria",
    "Energia/industrial": "energia_industrial",
}

# ---------------------------------------------------------------------------
# Divisão causal/consequência solicitada
# ---------------------------------------------------------------------------

VARIAVEIS_CAUSAIS = [
    "area_colhida",
    "area_destinada_colheita",
    "consumo_energia_industrial",
    "desmat_area",
    "frota",
    "frp_anual_queimadas",
    "rebanho",
    "venda_comb",
]

VARIAVEIS_CONSEQUENCIAS = [
    "chuva_media",
    "temp_media",
]

TIPO_VARIAVEL = {
    **{var: "Causas" for var in VARIAVEIS_CAUSAIS},
    **{var: "Consequências" for var in VARIAVEIS_CONSEQUENCIAS},
}

ORDEM_TIPOS_VARIAVEL = ["Causas", "Consequências"]

SLUG_TIPO_VARIAVEL = {
    "Causas": "causas",
    "Consequências": "consequencias",
}

# Rótulos apenas para o gráfico. As tabelas CSV continuam com os nomes originais
# das colunas para facilitar o reuso em outras análises.
ROTULOS_VARIAVEIS = {
    "frp_anual_queimadas": "FRP anual queimadas",
    "desmat_area": "Desmatamento",
    "frota": "Frota",
    "rebanho": "Rebanho",
    "venda_comb": "Venda combustíveis",
    "temp_media": "Temperatura média",
    "chuva_media": "Chuva média",
    "area_destinada_colheita": "Área destinada",
    "area_colhida": "Área colhida",
    "consumo_energia_industrial": "Energia industrial",
}

ORDEM_VARIAVEIS_GRAFICO = VARIAVEIS_CAUSAIS + VARIAVEIS_CONSEQUENCIAS


@dataclass
class ResultadoNormalidade:
    n: int
    w: float | None
    p_valor: float | None
    normal: bool | None
    conclusao: str


def _shapiro_seguro(
    serie: pd.Series,
    alpha: float = ALPHA,
    min_obs: int = MIN_OBS,
) -> ResultadoNormalidade:
    serie = pd.to_numeric(serie, errors="coerce").dropna()
    n = int(len(serie))

    if n < min_obs:
        return ResultadoNormalidade(
            n=n,
            w=None,
            p_valor=None,
            normal=None,
            conclusao="Amostra insuficiente",
        )

    if serie.nunique() < 2:
        return ResultadoNormalidade(
            n=n,
            w=None,
            p_valor=None,
            normal=None,
            conclusao="Variável constante",
        )

    try:
        w, p = shapiro(serie)
    except Exception as exc:
        return ResultadoNormalidade(
            n=n,
            w=None,
            p_valor=None,
            normal=None,
            conclusao=f"Erro no Shapiro: {exc}",
        )

    return ResultadoNormalidade(
        n=n,
        w=float(w),
        p_valor=float(p),
        normal=bool(p > alpha),
        conclusao="Não rejeita normalidade" if p > alpha else "Rejeita normalidade",
    )


def _coeficiente_seguro(
    x: pd.Series,
    y: pd.Series,
    metodo: str,
) -> tuple[float | None, float | None, str]:
    pares = pd.DataFrame({"x": x, "y": y}).apply(pd.to_numeric, errors="coerce").dropna()

    if len(pares) < MIN_OBS:
        return None, None, "Amostra insuficiente"

    if pares["x"].nunique() < 2 or pares["y"].nunique() < 2:
        return None, None, "Variável constante"

    try:
        if metodo == "Pearson":
            coef, p = pearsonr(pares["x"], pares["y"])
        elif metodo == "Spearman":
            coef, p = spearmanr(pares["x"], pares["y"])
        else:
            raise ValueError(f"Método inválido: {metodo}")
    except Exception as exc:
        return None, None, f"Erro na correlação: {exc}"

    if pd.isna(coef) or pd.isna(p):
        return None, None, "Resultado indefinido"

    return float(coef), float(p), "OK"


def _ordenar_estados_por_bloco(df: pd.DataFrame, coluna_estado: str = COLUNA_GRUPO) -> list[str]:
    estados_presentes = df[coluna_estado].dropna().astype(str).str.upper().unique().tolist()
    estados_ordenados = [uf for uf in ORDEM_ESTADOS_POR_BLOCO if uf in estados_presentes]
    estados_restantes = sorted([uf for uf in estados_presentes if uf not in estados_ordenados])
    return estados_ordenados + estados_restantes


def _coagir_variaveis_potenciais_para_numerico(
    df: pd.DataFrame,
    colunas_chave: Iterable[str],
) -> pd.DataFrame:
    """
    Garante que colunas numéricas lidas como texto também entrem na análise.
    """
    base = df.copy()
    chaves = set(colunas_chave)

    for col in base.columns:
        if col in chaves:
            continue

        if base[col].dtype == "object":
            serie_texto = (
                base[col]
                .astype(str)
                .str.strip()
                .str.replace(".", "", regex=False)
                .str.replace(",", ".", regex=False)
                .replace({"": np.nan, "nan": np.nan, "None": np.nan, "null": np.nan})
            )
            convertida = pd.to_numeric(serie_texto, errors="coerce")

            if convertida.notna().sum() > 0:
                base[col] = convertida
        else:
            base[col] = pd.to_numeric(base[col], errors="coerce")

    return base


def _variaveis_disponiveis(base: pd.DataFrame) -> list[str]:
    """
    Retorna apenas as variáveis do desenho metodológico atual que existem no dataframe.
    """
    variaveis = [v for v in ORDEM_VARIAVEIS_GRAFICO if v in base.columns]

    ausentes = [v for v in ORDEM_VARIAVEIS_GRAFICO if v not in base.columns]
    if ausentes:
        print(f"[heatmap] Aviso: variáveis esperadas ausentes no dataframe: {ausentes}")

    return variaveis


def calcular_correlacao_mista_por_estado(
    df: pd.DataFrame,
    coluna_estado: str = COLUNA_GRUPO,
    coluna_ano: str = COLUNA_ANO,
    coluna_alvo: str = COLUNA_ALVO,
    ignorar_colunas: Iterable[str] | None = None,
    alpha: float = ALPHA,
) -> pd.DataFrame:
    """
    Gera uma tabela longa com uma linha por Estado x Variável.

    Colunas principais para o heatmap:
        Bloco | Estado | Tipo_variavel | Variavel | Coeficiente

    Colunas auxiliares:
        Metodo | p_valor | Significativo_5pct | normalidade de CO2 e da variável
    """
    if ignorar_colunas is None:
        ignorar_colunas = []

    base = df.copy()
    base[coluna_estado] = base[coluna_estado].astype(str).str.strip().str.upper()
    base[coluna_ano] = pd.to_numeric(base[coluna_ano], errors="coerce")
    base = base.dropna(subset=[coluna_estado, coluna_ano])

    if coluna_alvo not in base.columns:
        raise ValueError(f"Coluna alvo '{coluna_alvo}' não encontrada no dataframe.")

    base = _coagir_variaveis_potenciais_para_numerico(
        base,
        colunas_chave=[coluna_estado, "Regiao", "Bloco", coluna_ano],
    )

    ignorar = set(ignorar_colunas or [])
    variaveis = [v for v in _variaveis_disponiveis(base) if v not in ignorar and v != coluna_alvo]

    resultados = []
    estados_ordenados = _ordenar_estados_por_bloco(base, coluna_estado=coluna_estado)

    for estado in estados_ordenados:
        base_estado = base.loc[base[coluna_estado].astype(str) == estado].sort_values(coluna_ano).copy()
        normalidade_alvo = _shapiro_seguro(base_estado[coluna_alvo], alpha=alpha)

        for variavel in variaveis:
            normalidade_var = _shapiro_seguro(base_estado[variavel], alpha=alpha)

            usar_pearson = (
                normalidade_alvo.normal is True
                and normalidade_var.normal is True
            )
            metodo = "Pearson" if usar_pearson else "Spearman"

            pares = base_estado[[coluna_alvo, variavel, coluna_ano]].dropna()
            coef, p_corr, status_corr = _coeficiente_seguro(pares[coluna_alvo], pares[variavel], metodo)

            resultados.append({
                "Bloco": BLOCO_POR_UF.get(str(estado), "Outros"),
                "Estado": estado,
                "Tipo_variavel": TIPO_VARIAVEL.get(variavel, "Outras"),
                "Variavel": variavel,
                "Coeficiente": coef,
                "p_valor": p_corr,
                "Significativo_5pct": "Sim" if (p_corr is not None and p_corr < alpha) else "Não" if p_corr is not None else None,
                "Metodo": metodo,
                "n_pares": int(len(pares)),
                "Shapiro_CO2_n": normalidade_alvo.n,
                "Shapiro_CO2_W": normalidade_alvo.w,
                "Shapiro_CO2_p": normalidade_alvo.p_valor,
                "Shapiro_CO2_Normal_5pct": "Sim" if normalidade_alvo.normal is True else "Não" if normalidade_alvo.normal is False else None,
                "Shapiro_Var_n": normalidade_var.n,
                "Shapiro_Var_W": normalidade_var.w,
                "Shapiro_Var_p": normalidade_var.p_valor,
                "Shapiro_Var_Normal_5pct": "Sim" if normalidade_var.normal is True else "Não" if normalidade_var.normal is False else None,
                "Status": status_corr,
            })

    resultado = pd.DataFrame(resultados)
    resultado["Estado"] = pd.Categorical(resultado["Estado"], categories=estados_ordenados, ordered=True)
    resultado["Tipo_variavel"] = pd.Categorical(
        resultado["Tipo_variavel"],
        categories=ORDEM_TIPOS_VARIAVEL + ["Outras"],
        ordered=True,
    )
    resultado = resultado.sort_values(["Tipo_variavel", "Estado", "Variavel"]).reset_index(drop=True)
    resultado["Estado"] = resultado["Estado"].astype(str)
    resultado["Tipo_variavel"] = resultado["Tipo_variavel"].astype(str)
    return resultado


def preparar_base_heatmap(
    resultado: pd.DataFrame,
    tipo_variavel: str,
    bloco: str | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    base = resultado[resultado["Tipo_variavel"] == tipo_variavel].copy()

    if bloco is not None:
        base = base[base["Bloco"] == bloco].copy()

    if base.empty:
        return pd.DataFrame(), pd.DataFrame()

    matriz_coef = base.pivot(index="Estado", columns="Variavel", values="Coeficiente")
    matriz_sig = base.pivot(index="Estado", columns="Variavel", values="Significativo_5pct")

    if bloco is None:
        estados_base = ORDEM_ESTADOS_POR_BLOCO
    else:
        estados_base = BLOCOS_ESTADOS.get(bloco, [])

    estados_ordenados = [uf for uf in estados_base if uf in matriz_coef.index]
    estados_restantes = sorted([uf for uf in matriz_coef.index if uf not in estados_ordenados])
    estados_final = estados_ordenados + estados_restantes

    variaveis_base = VARIAVEIS_CAUSAIS if tipo_variavel == "Causas" else VARIAVEIS_CONSEQUENCIAS
    variaveis_final = [v for v in variaveis_base if v in matriz_coef.columns]
    variaveis_restantes = [v for v in matriz_coef.columns if v not in variaveis_final]
    variaveis_final = variaveis_final + variaveis_restantes

    matriz_coef = matriz_coef.loc[estados_final, variaveis_final]
    matriz_sig = matriz_sig.loc[estados_final, variaveis_final]
    return matriz_coef, matriz_sig


def _anotacoes_heatmap(matriz_coef: pd.DataFrame, matriz_sig: pd.DataFrame) -> pd.DataFrame:
    anotacoes = matriz_coef.copy().astype(object)
    for estado in matriz_coef.index:
        for variavel in matriz_coef.columns:
            valor = matriz_coef.loc[estado, variavel]
            significativo = matriz_sig.loc[estado, variavel] == "Sim"
            if pd.isna(valor):
                anotacoes.loc[estado, variavel] = ""
            else:
                anotacoes.loc[estado, variavel] = f"{valor:.2f}{'*' if significativo else ''}"
    return anotacoes


def gerar_heatmap_correlacao_estado(
    resultado: pd.DataFrame,
    tipo_variavel: str,
    caminho_saida: str,
    titulo: str,
    bloco: str | None = None,
    mostrar: bool = False,
) -> None:
    """
    Gera heatmap completo com os 3 blocos ou apenas um bloco específico,
    filtrando por tipo de variável: Causas ou Consequências.
    """
    matriz_coef, matriz_sig = preparar_base_heatmap(
        resultado,
        tipo_variavel=tipo_variavel,
        bloco=bloco,
    )

    if matriz_coef.empty:
        print(f"[heatmap] Nenhum dado disponível para tipo={tipo_variavel}, bloco={bloco}.")
        return

    anotacoes = _anotacoes_heatmap(matriz_coef, matriz_sig)

    matriz_coef_plot = matriz_coef.rename(columns=ROTULOS_VARIAVEIS)
    anotacoes_plot = anotacoes.rename(columns=ROTULOS_VARIAVEIS)

    # Roxo = negativo; branco = próximo de zero; laranja = positivo.
    cmap = LinearSegmentedColormap.from_list(
        "roxo_branco_laranja",
        ["#5e3c99", "#ffffff", "#e66101"],
        N=256,
    )

    n_estados, n_variaveis = matriz_coef_plot.shape
    largura = max(8, min(24, 1.25 * n_variaveis + 5))
    altura = max(6, 0.48 * n_estados + 3)

    plt.figure(figsize=(largura, altura))
    ax = sns.heatmap(
        matriz_coef_plot,
        cmap=cmap,
        vmin=-1,
        vmax=1,
        center=0,
        annot=anotacoes_plot,
        fmt="",
        linewidths=0.4,
        linecolor="#eeeeee",
        cbar_kws={"label": "Coeficiente de correlação"},
    )

    titulo_final = titulo
    if bloco is not None:
        titulo_final = f"{titulo_final} — {bloco}"

    ax.set_title(titulo_final, fontsize=13, pad=16)
    ax.set_xlabel("Variável")
    ax.set_ylabel("Estado")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0)

    if bloco is None:
        blocos_por_estado = [BLOCO_POR_UF.get(str(uf), "Outros") for uf in matriz_coef.index]

        # Linhas horizontais para separar os blocos.
        for i in range(1, len(blocos_por_estado)):
            if blocos_por_estado[i] != blocos_por_estado[i - 1]:
                ax.hlines(i, *ax.get_xlim(), colors="black", linewidth=1.5)

        # Rótulos dos blocos no lado esquerdo.
        grupos = []
        inicio = 0
        for i in range(1, len(blocos_por_estado) + 1):
            if i == len(blocos_por_estado) or blocos_por_estado[i] != blocos_por_estado[inicio]:
                grupos.append((blocos_por_estado[inicio], inicio, i - 1))
                inicio = i

        for nome_bloco, ini, fim in grupos:
            meio = (ini + fim + 1) / 2
            ax.text(
                -0.9,
                meio,
                nome_bloco,
                va="center",
                ha="right",
                fontsize=9,
                fontweight="bold",
                rotation=0,
                transform=ax.transData,
                clip_on=False,
            )

    plt.figtext(
        0.01,
        0.01,
        "* p < 0,05. Pearson usado quando CO2 e variável não rejeitam normalidade no Shapiro-Wilk; caso contrário, Spearman.",
        ha="left",
        fontsize=9,
    )
    plt.tight_layout(rect=[0.08 if bloco is None else 0.03, 0.04, 1, 1])

    preparar_pasta_graficos(os.path.dirname(caminho_saida) or PASTA_SAIDA_GRAFICOS)
    plt.savefig(caminho_saida, dpi=300, bbox_inches="tight")

    if mostrar:
        plt.show()
    else:
        plt.close()


def salvar_correlacao_e_heatmaps_estado(
    caminho_df: str = CAMINHO_DF,
    pasta_saida_tabelas: str = PASTA_SAIDA_TABELAS,
    pasta_saida_graficos: str = PASTA_SAIDA_GRAFICOS,
    coluna_estado: str = COLUNA_GRUPO,
    coluna_ano: str = COLUNA_ANO,
    coluna_alvo: str = COLUNA_ALVO,
    ignorar_colunas: Iterable[str] | None = None,
    alpha: float = ALPHA,
    mostrar: bool = False,
    gerar_heatmaps_por_bloco: bool = True,
) -> pd.DataFrame:
    if ignorar_colunas is None:
        ignorar_colunas = IGNORAR_COLUNAS

    df = pd.read_csv(caminho_df)

    estados_df = set(df[coluna_estado].dropna().astype(str).str.upper().unique())
    estados_mapeados = set(BLOCO_POR_UF.keys())
    estados_sem_bloco = sorted(estados_df - estados_mapeados)
    if estados_sem_bloco:
        print(f"[heatmap] Aviso: estados sem bloco definido: {estados_sem_bloco}. Eles entrarão como 'Outros'.")

    if "internacoes" in df.columns:
        print("[heatmap] Aviso: coluna 'internacoes' encontrada, mas será ignorada conforme a nova delimitação do trabalho.")

    resultado = calcular_correlacao_mista_por_estado(
        df,
        coluna_estado=coluna_estado,
        coluna_ano=coluna_ano,
        coluna_alvo=coluna_alvo,
        ignorar_colunas=ignorar_colunas,
        alpha=alpha,
    )

    os.makedirs(pasta_saida_tabelas, exist_ok=True)

    caminho_completo = os.path.join(
        pasta_saida_tabelas,
        "correlacao_estado_metodo_misto_blocos_causa_consequencia.csv",
    )
    resultado.to_csv(caminho_completo, index=False)

    base_heatmap = resultado[["Bloco", "Estado", "Tipo_variavel", "Variavel", "Coeficiente"]].copy()
    caminho_base_heatmap = os.path.join(
        pasta_saida_tabelas,
        "correlacao_estado_heatmap_base_blocos_causa_consequencia.csv",
    )
    base_heatmap.to_csv(caminho_base_heatmap, index=False)

    for tipo_variavel in ORDEM_TIPOS_VARIAVEL:
        slug_tipo = SLUG_TIPO_VARIAVEL[tipo_variavel]
        caminho_heatmap = os.path.join(
            pasta_saida_graficos,
            f"heatmap_correlacao_estado_blocos_{slug_tipo}.png",
        )
        gerar_heatmap_correlacao_estado(
            resultado,
            tipo_variavel=tipo_variavel,
            caminho_saida=caminho_heatmap,
            titulo=f"Correlação com CO2 por estado — variáveis {tipo_variavel.lower()}",
            bloco=None,
            mostrar=mostrar,
        )

    if gerar_heatmaps_por_bloco:
        for bloco in ORDEM_BLOCOS:
            slug_bloco = SLUG_BLOCO[bloco]
            for tipo_variavel in ORDEM_TIPOS_VARIAVEL:
                slug_tipo = SLUG_TIPO_VARIAVEL[tipo_variavel]
                caminho_bloco = os.path.join(
                    pasta_saida_graficos,
                    f"heatmap_correlacao_estado_{slug_bloco}_{slug_tipo}.png",
                )
                gerar_heatmap_correlacao_estado(
                    resultado,
                    tipo_variavel=tipo_variavel,
                    caminho_saida=caminho_bloco,
                    titulo=f"Correlação com CO2 por estado — variáveis {tipo_variavel.lower()}",
                    bloco=bloco,
                    mostrar=mostrar,
                )

    print(f"✅ Tabela completa salva em: {caminho_completo}")
    print(f"✅ Base longa do heatmap salva em: {caminho_base_heatmap}")
    print(f"✅ Heatmaps salvos em: {pasta_saida_graficos}")

    return resultado


# Compatibilidade com chamadas antigas do analise_df_principal.py.
def salvar_correlacao_e_heatmap_estado(*args, **kwargs) -> pd.DataFrame:
    return salvar_correlacao_e_heatmaps_estado(*args, **kwargs)


if __name__ == "__main__":
    salvar_correlacao_e_heatmaps_estado()
