import os
import re
import glob
import pandas as pd
from utils import normalizar_estado, salvar_tratado, normalizar_texto, agregar_por_regiao_ano

ANOS_MIN = 2006
ANOS_MAX = 2019


def _detectar_ano(caminho_arquivo: str) -> int:
    """
    Extrai o ano do nome do arquivo CSV (ex.: "2003.csv").
    """
    m = re.search(r"(\d{4})", os.path.basename(caminho_arquivo))
    if m:
        return int(m.group(1))
    raise ValueError(f"Não foi possível identificar o ano para {caminho_arquivo}")


def _limpar_uf(valor: str) -> str:
    """
    Remove código IBGE à esquerda (ex.: '11 Rondônia' -> 'Rondônia')
    e tira aspas/resíduos.
    """
    if pd.isna(valor):
        return None
    s = str(valor).strip().strip('"').strip("'")
    # remove código no começo: dois dígitos (às vezes três) + espaço
    s = re.sub(r"^\d{1,3}\s+", "", s)
    return s


def processar_doencas_respiratorias(
    pasta: str = "bases/doencas_respiratorias",
    agrupar_por_regiao: bool = False,
) -> pd.DataFrame:
    """
    Lê todos os CSVs da pasta especificada, trata e retorna DataFrame unificado:
    colunas: Estado (UF), Ano, Internações_Respiratorias.
    """
    arquivos = sorted(glob.glob(os.path.join(pasta, "*.csv")))
    if not arquivos:
        raise FileNotFoundError(f"Nenhum CSV encontrado em: {pasta}")

    registros = []

    for arq in arquivos:
        # Detectar ano a partir do nome do arquivo
        ano = _detectar_ano(arq)

        # Ler a tabela, começando na linha 5 (ignorando as primeiras 4 linhas de metadados)
        df = pd.read_csv(
            arq,
            sep=";",
            header=4,
            encoding="latin1",
            quotechar='"'
        )

        # Normalizar nomes de colunas para evitar problemas com acentuação/maiúsculas
        df.columns = [normalizar_texto(col).lower() for col in df.columns]

        # Garantir que as colunas corretas estejam presentes
        col_uf = next((c for c in df.columns if "unidade" in c and "federacao" in c), None)
        col_int = next((c for c in df.columns if "internacoes" in c), None)

        if not col_uf or not col_int:
            raise ValueError(f"Não encontrei colunas de UF/Internações em {arq}. Colunas lidas: {list(df.columns)}")

        # Filtrar apenas as colunas relevantes
        df = df[[col_uf, col_int]].copy()

        # Remover linha "Total"
        df = df[~df[col_uf].astype(str).str.contains(r"Total", case=False, na=False)]

        # Limpar a coluna de Unidade da Federação
        df[col_uf] = df[col_uf].apply(_limpar_uf)

        # Normalizar Estado (UF)
        df["Estado"] = df[col_uf].apply(normalizar_estado)

        # Remover linhas sem mapeamento de UF
        df = df.dropna(subset=["Estado"])

        # Converter Internações para valores numéricos
        df["Internacoes_Respiratorias"] = pd.to_numeric(df[col_int], errors="coerce").fillna(0).astype("Int64")

        # Adicionar o ano extraído do nome do arquivo
        df["Ano"] = ano

        # Filtrar para o período do TCC (2003-2018)
        if not (ANOS_MIN <= ano <= ANOS_MAX):
            continue

        registros.append(df[["Estado", "Ano", "Internacoes_Respiratorias"]])

    if not registros:
        raise ValueError("Nenhum arquivo no período 2003–2018 foi processado.")

    # Unir todos os registros em um único DataFrame
    final = pd.concat(registros, ignore_index=True)

    # Checagem de duplicatas (Estado + Ano deve ser único)
    if final.duplicated(subset=["Estado", "Ano"]).any():
        # Se existir duplicata, agregamos somando as internações
        final = final.groupby(["Estado", "Ano"], as_index=False)["Internacoes_Respiratorias"].sum()

    # Organizar DataFrame final
    final = final.sort_values(["Estado", "Ano"]).reset_index(drop=True)

    if agrupar_por_regiao:
        final = agregar_por_regiao_ano(final)
        return salvar_tratado(final, "doencas_respiratorias_regiao")

    # Salvar o DataFrame tratado
    return salvar_tratado(final, "doencas_respiratorias")
