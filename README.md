# tcc-co2

Projeto de tratamento, integração e análise de bases estaduais e regionais relacionadas a emissões brutas de CO2 no Brasil.

O projeto consolida diferentes fontes públicas em um `dataframe-principal`, permitindo análises por **Estado/Ano** ou **Região/Ano**. O cenário atual recomendado é a análise **estadual**, usando a chave `Estado` + `Ano`.

---

## Objetivo

Construir uma base integrada para investigar relações entre emissões brutas de CO2 e variáveis ambientais, agropecuárias, econômicas, energéticas e de saúde.

A base principal pode incluir, entre outras variáveis:

- emissões brutas de CO2;
- frota veicular;
- rebanho bovino;
- internações por doenças respiratórias;
- venda de combustíveis;
- desmatamento MapBiomas;
- área colhida;
- área destinada à colheita;
- consumo de energia elétrica industrial;
- temperatura média anual do INMET;
- chuva média anual do INMET.

---

## Estrutura geral do projeto

```text
.
├── bases/
│   ├── inmet/
│   │   ├── 2003/
│   │   ├── 2004/
│   │   ├── ...
│   │   └── 2023/
│   ├── tratadas/
│   └── demais bases brutas
│
├── pipelines/
│   ├── co2_pipe.py
│   ├── frota_pipe.py
│   ├── rebanho_pipe.py
│   ├── doencas_respiratorias_pipe.py
│   ├── combustiveis_pipe.py
│   ├── desmatamento_mapbiomas_pipe.py
│   ├── area_colhida_pipe.py
│   ├── area_destinada_colheita_pipe.py
│   ├── energia_industrial_pipe.py
│   └── inmet_pipe.py
│
├── frames.py
├── analise_df_principal.py
├── utils.py
├── missing_values.py
├── pearson.py
├── spearman.py
├── shapiro.py
├── histogramas.py
├── linha_boxplot.py
├── scatter_plot.py
├── requirements.txt
└── README.md
```

---

## Requisitos

- Windows, Linux ou macOS;
- Python 3.11 recomendado;
- `pip` disponível;
- arquivos brutos dentro da pasta `bases/`;
- arquivo `requirements.txt` atualizado.

---

## Instalação no Windows usando CMD

### 1. Abrir a pasta do projeto

```bat
cd c:\Development\tcc-co2
```

Ajuste o caminho conforme a pasta real do projeto.

### 2. Confirmar Python 3.11

```bat
py -3.11 --version
```

Se o comando falhar, instale o Python 3.11 e marque a opção para adicionar o Python ao PATH.

### 3. Criar ambiente virtual

```bat
py -3.11 -m venv .env
```

### 4. Ativar ambiente virtual

```bat
.env\Scripts\activate.bat
```

Quando ativo, o terminal geralmente mostra o prefixo `(.env)`.

### 5. Atualizar pip e instalar dependências

```bat
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## Fluxo recomendado de execução

### 1. Gerar as bases tratadas e o dataframe principal

```bat
python frames.py
```

Esse script executa os pipelines em `pipelines/`, salva as bases tratadas individuais em `bases/tratadas/` e gera o dataframe principal.

No cenário estadual atual, o arquivo principal esperado é:

```text
bases/tratadas/dataframe-principal-estado-tratada.csv
```

### 2. Rodar a análise estatística e exploratória

```bat
python analise_df_principal.py
```

Esse script carrega o dataframe principal, avalia missing values, prepara a base e gera resultados como:

```text
bases/tratadas/shapiro_por_estado.csv
bases/tratadas/pearson_por_estado.csv
bases/tratadas/spearman_por_estado.csv
```

Se `GERAR_VISUALIZACOES = True`, também são gerados gráficos nas pastas dentro de `graficos/`.

---

## Configuração de granularidade

A granularidade é controlada no `frames.py`:

```python
AGRUPAR_POR_REGIAO = False
```

Use:

```python
AGRUPAR_POR_REGIAO = False
```

para gerar análise por:

```text
Estado | Ano
```

Use:

```python
AGRUPAR_POR_REGIAO = True
```

para gerar análise por:

```text
Regiao | Ano
```

O dataframe principal usa automaticamente as chaves corretas:

```python
CHAVES_MERGE = ["Regiao", "Ano"] if AGRUPAR_POR_REGIAO else ["Estado", "Ano"]
```

Isso evita misturar bases estaduais com merges regionais.

---

## Bases tratadas esperadas no cenário estadual

Após rodar `frames.py`, a pasta `bases/tratadas/` pode conter arquivos como:

```text
co2-estado-tratada.csv
frota-estado-tratada.csv
rebanho-estado-tratada.csv
doencas-resp-estado-tratada.csv
venda-combustiveis-estado-tratada.csv
desmatamento-mapbiomas-estado-tratada.csv
area-colhida-estado-tratada.csv
area-destinada-colheita-estado-tratada.csv
energia-industrial-estado-tratada.csv
inmet-clima-estado-tratada.csv
dataframe-principal-estado-tratada.csv
```

A base principal estadual deve ter chave única por:

```text
Estado + Ano
```

---

## INMET

A base do INMET deve estar organizada com uma pasta por ano:

```text
bases/inmet/
├── 2003/
│   ├── INMET_CO_GO_A012_LUZIANIA_01-01-2003_A_31-12-2003.CSV
│   └── ...
├── 2004/
│   └── ...
└── 2023/
    └── ...
```

Cada arquivo representa uma estação meteorológica.

O pipeline otimizado do INMET lê os arquivos e calcula, em uma única passagem:

- `temp_media`: temperatura média anual;
- `chuva_media`: chuva média anual.

No `frames.py`, os principais parâmetros são:

```python
PASTA_INMET = "bases/inmet"
INMET_SOMENTE_CAPITAIS = False
INMET_PARALELO = True
INMET_MAX_WORKERS = None
```

### Usar todas as estações

```python
INMET_SOMENTE_CAPITAIS = False
```

Recomendado para representar melhor o estado como um todo.

### Usar apenas capitais

```python
INMET_SOMENTE_CAPITAIS = True
```

Útil se a análise quiser padronizar apenas estações próximas às capitais.

### Paralelismo

Para muitos arquivos do INMET, por exemplo cerca de 10 mil CSVs, recomenda-se:

```python
INMET_PARALELO = True
INMET_MAX_WORKERS = None
```

Com `None`, o pipeline escolhe automaticamente a quantidade de workers. Em SSD/NVMe, valores como `8`, `16` ou `32` podem ser testados manualmente:

```python
INMET_MAX_WORKERS = 8
```

---

## Análise estadual

O script `analise_df_principal.py` está configurado para análise estadual com:

```python
CAMINHO_DF = "bases/tratadas/dataframe-principal-estado-tratada.csv"
COLUNA_GRUPO = "Estado"
AGREGAR_PARA_REGIAO = False
SUFIXO_ANALISE = "estado"
```

As funções de análise foram generalizadas para aceitar uma coluna de agrupamento, como `Estado` ou `Regiao`.

Exemplos de funções genéricas:

```python
shapiro_series_temporais_por_grupo(..., coluna_grupo="Estado")
correlacao_pearson_por_grupo(..., coluna_grupo="Estado")
correlacao_spearman_por_grupo(..., coluna_grupo="Estado")
scatter_co2_vs_todas(..., coluna_grupo="Estado")
histogramas_todas_variaveis_por_grupo(..., coluna_grupo="Estado")
boxplots_todas_variaveis_por_grupo_ano(..., coluna_grupo="Estado")
```

---

## Missing values

O script de análise exibe um relatório antes e depois da preparação da base:

```text
=== Missing values antes do preenchimento ===
=== Missing values após o preenchimento ===
```

O preenchimento por interpolação é aplicado somente quando a coluna existe, por exemplo `Populacao`.

Alguns valores ausentes podem ser esperados por diferença de cobertura temporal das fontes. Exemplo: consumo de energia industrial pode começar em 2004, enquanto o dataframe principal começa em 2003.

---

## Cache e reprocessamento

No `frames.py`, a variável:

```python
REPROCESSAR_TUDO = True
```

força todos os pipelines a rodarem novamente.

Para reaproveitar arquivos já tratados em `bases/tratadas/`, use:

```python
REPROCESSAR_TUDO = False
```

Isso é especialmente útil após processar o INMET, que pode conter milhares de arquivos.

---

## Saídas principais

### Bases tratadas

```text
bases/tratadas/
```

### Gráficos

```text
graficos/
├── linhas/
├── boxplots/
├── histogramas/
└── scatterplots/
```

### Resultados estatísticos

```text
bases/tratadas/shapiro_por_estado.csv
bases/tratadas/pearson_por_estado.csv
bases/tratadas/spearman_por_estado.csv
```

---

## Observações para VS Code

Se o VS Code selecionar outro interpretador automaticamente, escolha manualmente o Python dentro da pasta `.env`.

Caminho típico no Windows:

```text
.env\Scripts\python.exe
```

---

## Comandos rápidos

```bat
cd c:\Development\tcc-co2
.env\Scripts\activate.bat
python frames.py
python analise_df_principal.py
deactivate
```

---

## Cuidados importantes

- Não misture bases estaduais com merge por região.
- Para análise estadual, use sempre `Estado + Ano` como chave.
- Para análise regional, gere novamente as bases com `AGRUPAR_POR_REGIAO = True`.
- Evite reprocessar o INMET sem necessidade; use cache quando possível.
- Confira se os nomes dos arquivos brutos batem com os caminhos esperados nos pipelines.
