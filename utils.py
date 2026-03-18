import os
import pandas as pd
import unicodedata

# Dicionário Nome -> UF
MAPA_ESTADOS = {
    "Acre": "AC", "Alagoas": "AL", "Amapá": "AP", "Amazonas": "AM",
    "Bahia": "BA", "Ceará": "CE", "Distrito Federal": "DF", "Espírito Santo": "ES",
    "Goiás": "GO", "Maranhão": "MA", "Mato Grosso": "MT", "Mato Grosso do Sul": "MS",
    "Minas Gerais": "MG", "Pará": "PA", "Paraíba": "PB", "Paraná": "PR",
    "Pernambuco": "PE", "Piauí": "PI", "Rio de Janeiro": "RJ", "Rio Grande do Norte": "RN",
    "Rio Grande do Sul": "RS", "Rondônia": "RO", "Roraima": "RR",
    "Santa Catarina": "SC", "São Paulo": "SP", "Sergipe": "SE", "Tocantins": "TO"
}

def normalizar_texto(txt: str) -> str:
    if pd.isna(txt): return txt
    txt = str(txt).strip()
    txt = unicodedata.normalize("NFKD", txt).encode("ASCII", "ignore").decode("utf-8")
    return txt

def normalizar_estado(nome_estado: str) -> str:
    if not nome_estado:
        return None
    nome_estado_norm = normalizar_texto(nome_estado).title()
    for nome, uf in MAPA_ESTADOS.items():
        nome_norm = normalizar_texto(nome).title()
        if nome_estado_norm == nome_norm:
            return uf
    return None

def salvar_tratado(df, nome):
    """Salva dataframe em bases/tratadas com nome_tratado.csv e retorna o df"""
    os.makedirs("bases/tratadas", exist_ok=True)
    caminho = f"bases/tratadas/{nome}_tratado.csv"
    df.to_csv(caminho, index=False)
    print(f"✅ Base '{nome}' tratada salva em {caminho}")
    return df   # <<< precisa retornar o df!

