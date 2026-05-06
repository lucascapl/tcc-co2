import csv

import pandas as pd

from utils import ANO_FINAL, ANO_INICIAL, ORDEM_REGIOES, ordenar_regioes, salvar_tratado


def _ler_linhas_csv(caminho_arquivo: str) -> list[list[str]]:
    for encoding in ["utf-8-sig", "latin1"]:
        try:
            with open(caminho_arquivo, "r", encoding=encoding, newline="") as f:
                return list(csv.reader(f))
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError("csv", b"", 0, 1, f"Nao foi possivel decodificar: {caminho_arquivo}")


def _parse_numero_brasileiro(valor):
    if pd.isna(valor):
        return None
    texto = str(valor).strip()
    if not texto or texto == "...":
        return None
    texto = texto.replace(".", "").replace(",", ".")
    return pd.to_numeric(texto, errors="coerce")


def processar_consumo_energia_industrial(
    caminho_arquivo: str = "bases/consumo-energia-eletrica-industrial-2004-2025-epe.csv",
    agrupar_por_regiao: bool = True,
):
    """
    Processa a base da EPE e extrai o consumo anual industrial (coluna ANO)
    por regiao geografica.

    Saida:
        Regiao | Ano | consumo_energia_industrial
    """
    if not agrupar_por_regiao:
        raise ValueError("Esta base ja e regional. Use agrupar_por_regiao=True.")

    linhas = _ler_linhas_csv(caminho_arquivo)
    registros = []

    i = 0
    while i < len(linhas):
        linha = linhas[i]
        primeira_col = linha[0].strip() if len(linha) > 0 else ""
        segunda_col = linha[1].strip() if len(linha) > 1 else ""

        if primeira_col == "" and segunda_col:
            ano_txt = segunda_col.replace("*", "").strip()
            if ano_txt.isdigit():
                ano = int(ano_txt)

                j = i + 1
                while j < len(linhas):
                    linha_j = linhas[j]
                    c0 = linha_j[0].strip() if len(linha_j) > 0 else ""
                    c1 = linha_j[1].strip() if len(linha_j) > 1 else ""

                    if c0 == "" and c1 and c1.replace("*", "").strip().isdigit():
                        break

                    if "REGIAO GEOGRAFICA" in c0.upper() or "REGIÃO GEOGRÁFICA" in c0.upper():
                        k = j + 1
                        while k < len(linhas):
                            linha_k = linhas[k]
                            nome_regiao = linha_k[0].strip() if len(linha_k) > 0 else ""

                            if "SUBSISTEMA" in nome_regiao.upper():
                                break

                            if nome_regiao in ORDEM_REGIOES:
                                valor_ano = linha_k[13] if len(linha_k) > 13 else None
                                registros.append(
                                    {
                                        "Regiao": nome_regiao,
                                        "Ano": ano,
                                        "consumo_energia_industrial": _parse_numero_brasileiro(valor_ano),
                                    }
                                )
                            k += 1
                        break
                    j += 1

                i = j
                continue

        i += 1

    if not registros:
        raise ValueError("Nenhum registro regional anual de energia foi encontrado na base.")

    df = pd.DataFrame(registros)
    df["Ano"] = pd.to_numeric(df["Ano"], errors="coerce").astype("Int64")
    df = df[(df["Ano"] >= ANO_INICIAL) & (df["Ano"] <= ANO_FINAL)].copy()

    df["consumo_energia_industrial"] = pd.to_numeric(df["consumo_energia_industrial"], errors="coerce")

    # Mantem chave unica por regiao/ano, somando se houver repeticao na origem.
    df = (
        df.groupby(["Regiao", "Ano"], as_index=False)["consumo_energia_industrial"]
        .sum(min_count=1)
    )

    df = ordenar_regioes(df, coluna_regiao="Regiao", coluna_ano="Ano")
    return salvar_tratado(df, "energia-industrial-regiao")
