# Indicadores brasileiros VS emissão bruta CO2

Projeto de tratamento, integração e análise de bases estaduais e regionais relacionadas às emissões brutas de CO2 no Brasil.

O projeto consolida diferentes fontes públicas em um `dataframe-principal`, permitindo análises por **Estado/Ano** ou **Região/Ano**. O cenário atual recomendado é a análise **estadual**, usando a chave `Estado + Ano`.

---

## Objetivo

Construir uma base integrada para investigar relações entre emissões brutas de CO2 e variáveis ambientais, agropecuárias, energéticas, climáticas e socioeconômicas no Brasil.

A base principal é montada a partir das emissões brutas de CO2 e recebe, por merge, as demais variáveis tratadas pelos pipelines.

As variáveis atualmente consideradas no projeto incluem:

- emissões brutas de CO2;
- frota veicular;
- rebanho bovino;
- venda de combustíveis;
- desmatamento;
- área colhida;
- área destinada à colheita;
- consumo de energia elétrica industrial;
- FRP anual de queimadas;
- temperatura média anual;
- chuva média anual;



---

## Visão geral do fluxo

O fluxo recomendado do projeto é:

```text
1. Colocar as bases brutas em bases/
2. Ajustar as configurações centrais em config.py
3. Rodar frames.py para gerar bases tratadas e dataframe principal
4. Rodar analise_df_principal.py para gerar testes, tabelas e visualizações
```

Na prática:

```bat
python frames.py
python analise_df_principal.py
```

---

## Estrutura geral do projeto

```text
.
├── bases/
│   ├── inmet/
│   │   ├── 2004/
│   │   ├── 2005/
│   │   ├── ...
│   │   └── 2023/
│   ├── queimadas/
│   ├── tratadas/
│   └── demais bases brutas
│
├── pipelines/
│   ├── area_colhida_pipe.py
│   ├── area_destinada_colheita_pipe.py
│   ├── co2_pipe.py
│   ├── combustiveis_pipe.py
│   ├── desmatamento_mapbiomas_pipe.py
│   ├── doencas_respiratorias_pipe.py
│   ├── energia_industrial_pipe.py
│   ├── frota_pipe.py
│   ├── inmet_pipe.py
│   ├── pib_pipe.py
│   ├── queimadas_pipe.py
│   └── rebanho_pipe.py
│
├── config.py
├── utils.py
├── frames.py
├── analise_df_principal.py
├── heatmap_correlacao_estado.py
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

- Python 3.11 recomendado;
- `pip` disponível;
- bases brutas colocadas dentro da pasta `bases/`;
- dependências instaladas a partir de `requirements.txt`.

Instalação das dependências:

```bat
pip install -r requirements.txt
```

Dependências principais:

- `pandas`;
- `scipy`;
- `matplotlib`;
- `seaborn`;
- `openpyxl`.

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

### 3. Criar ambiente virtual

```bat
py -3.11 -m venv .env
```

### 4. Ativar ambiente virtual

```bat
.env\Scripts\activate.bat
```

Quando ativo, o terminal geralmente mostra o prefixo `(.env)`.

### 5. Atualizar `pip` e instalar dependências

```bat
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## Configuração central do projeto

As principais configurações ficam em `config.py`.



Exemplo de configurações principais:

```python
ANO_INICIAL = 2004
ANO_FINAL = 2023

AGRUPAR_POR_REGIAO = False
REPROCESSAR_TUDO = True

PASTA_BASES = "bases"
PASTA_TRATADAS = "bases/tratadas"
PASTA_GRAFICOS = "graficos"
PASTA_INMET = "bases/inmet"
PASTA_QUEIMADAS = "bases/queimadas"

INMET_SOMENTE_CAPITAIS = False
INMET_PARALELO = True
INMET_MAX_WORKERS = None

QUEIMADAS_PARALELO = True
QUEIMADAS_MAX_WORKERS = None

GERAR_VISUALIZACOES = False
GERAR_HEATMAPS = True
GERAR_HEATMAPS_POR_BLOCO = True

IGNORAR_COLUNAS = ("IDHM", "internacoes")
```

### Recorte temporal

O recorte temporal usado pelos pipelines é definido em:

```python
ANO_INICIAL = 2004
ANO_FINAL = 2023
```

Esses valores alimentam o restante do projeto. Assim, para alterar o período analisado, ajuste o recorte em `config.py`.

### Granularidade

A granularidade principal é controlada por:

```python
AGRUPAR_POR_REGIAO = False
```

Use:

```python
AGRUPAR_POR_REGIAO = False
```

para análise por:

```text
Estado | Ano
```

Use:

```python
AGRUPAR_POR_REGIAO = True
```

para análise por:

```text
Regiao | Ano
```

A partir disso, o próprio projeto define automaticamente:

```python
coluna_grupo
chaves_merge
sufixo_granularidade
caminho_df_principal
```

Ou seja, não é necessário alterar manualmente o caminho do dataframe principal em `frames.py` ou `analise_df_principal.py`.

### Cache e reprocessamento

A configuração:

```python
REPROCESSAR_TUDO = True
```

força todos os pipelines a serem executados novamente.

Para reaproveitar bases já tratadas em `bases/tratadas/`, use:

```python
REPROCESSAR_TUDO = False
```

Isso é especialmente útil depois de processar bases pesadas, como INMET e queimadas.

### Visualizações e heatmaps

As flags principais são:

```python
GERAR_VISUALIZACOES = False
GERAR_HEATMAPS = True
GERAR_HEATMAPS_POR_BLOCO = True
```

- `GERAR_VISUALIZACOES`: controla gráficos exploratórios como linhas, boxplots, histogramas e scatterplots.
- `GERAR_HEATMAPS`: controla a geração dos heatmaps de correlação.
- `GERAR_HEATMAPS_POR_BLOCO`: controla se também serão gerados heatmaps separados por bloco analítico de estados.

---

## Responsabilidade dos arquivos principais

| Arquivo | Função |
|---|---|
| `config.py` | Centraliza configurações do projeto, como anos, granularidade, caminhos, cache e flags de análise. |
| `utils.py` | Guarda funções utilitárias, normalização de estados, mapeamento de regiões, ordenação, agregação e salvamento de bases tratadas. |
| `frames.py` | Executa os pipelines, valida chaves, faz os merges e gera o dataframe principal. |
| `analise_df_principal.py` | Carrega o dataframe principal e executa missing values, Shapiro, Pearson, Spearman, heatmaps e visualizações opcionais. |
| `heatmap_correlacao_estado.py` | Gera a correlação mista por estado e os heatmaps por blocos e tipo de variável. |
| `missing_values.py` | Gera relatório de ausentes e prepara preenchimentos simples, como interpolação de população quando a coluna existe. |
| `pearson.py` | Calcula correlação de Pearson por grupo. |
| `spearman.py` | Calcula correlação de Spearman por grupo. |
| `shapiro.py` | Aplica Shapiro-Wilk nas séries temporais por grupo. |
| `linha_boxplot.py` | Gera gráficos de linha e boxplots. |
| `histogramas.py` | Gera histogramas por grupo. |
| `scatter_plot.py` | Gera gráficos de dispersão entre CO2 e demais variáveis. |

---

## Fontes e bases brutas

Preencha a coluna de link conforme as fontes utilizadas no trabalho.

| Tema | Fonte | Variável gerada | Pipeline | Arquivo/pasta bruta esperada | Link da fonte | Observações |
|---|---|---|---|---|---|---|
| Emissões de CO2 | SEEG | `co2` | `co2_pipe.py` | `bases/emissao-co2-bruto-1990-2023-seeg.csv` |  | Emissões brutas por UF/ano. |
| Frota veicular | DENATRAN/SENATRAN | `frota` | `frota_pipe.py` | `bases/frota-veiculos-2003-2023-denatran.csv` |  | Mantém categorias motorizadas com emissão direta. |
| Rebanho bovino | IBGE/SIDRA | `rebanho` | `rebanho_pipe.py` | `bases/rebanho-1974-2023-ibge.xlsx` |  | Considera apenas bovinos. |
| Venda de combustíveis | ANP / dados.gov.br | `venda_comb` | `combustiveis_pipe.py` | `bases/venda-combustiveis-m3-1990-2025-dados_gov.csv` |  | Soma anual por UF. |
| Desmatamento | MapBiomas | `desmat_area` | `desmatamento_mapbiomas_pipe.py` | `bases/desmatamento-bioma-estado-1987-2024-mapbiomas.xlsx` |  | Soma por estado/ano e opcionalmente região/ano. |
| Área colhida | IBGE/SIDRA | `area_colhida` | `area_colhida_pipe.py` | `bases/area-colhida-1974-2024-ibge.xlsx` |  | Tabela wide convertida para formato longo. |
| Área destinada à colheita | IBGE/SIDRA | `area_destinada_colheita` | `area_destinada_colheita_pipe.py` | `bases/area-destinada-colheita-1988-2024-ibge.xlsx` |  | Tabela wide convertida para formato longo. |
| Energia elétrica industrial | EPE | `consumo_energia_industrial` | `energia_industrial_pipe.py` | `bases/consumo-energia-eletrica-industrial-estado-2004-2025-epe.xlsx` |  | Soma mensal para total anual. |
| Queimadas | INPE | `frp_anual_queimadas` | `queimadas_pipe.py` | `bases/queimadas/` |  | Soma anual do FRP dos focos detectados. |
| Clima | INMET | `temp_media`, `chuva_media` | `inmet_pipe.py` | `bases/inmet/` |  | Processa temperatura e chuva em uma única passagem. |


---

## Variáveis do desenho atual

### Variável alvo

| Variável | Descrição |
|---|---|
| `co2` | Emissões brutas de CO2. |

### Possíveis causas / variáveis explicativas

| Variável | Descrição |
|---|---|
| `area_colhida` | Área colhida anual. |
| `area_destinada_colheita` | Área destinada à colheita anual. |
| `consumo_energia_industrial` | Consumo anual de energia elétrica industrial. |
| `desmat_area` | Área anual de desmatamento. |
| `frota` | Frota veicular motorizada. |
| `frp_anual_queimadas` | Soma anual do FRP das queimadas. |
| `rebanho` | Rebanho bovino anual. |
| `venda_comb` | Venda anual de combustíveis. |

### Possíveis consequências / variáveis climáticas

| Variável | Descrição |
|---|---|
| `chuva_media` | Média anual de chuva calculada a partir das estações do INMET. |
| `temp_media` | Temperatura média anual calculada a partir das estações do INMET. |

---

## Como rodar o projeto

### 1. Conferir o `config.py`

Antes de rodar, confira principalmente:

```python
ANO_INICIAL = 2004
ANO_FINAL = 2023
AGRUPAR_POR_REGIAO = False
REPROCESSAR_TUDO = True
```

### 2. Gerar bases tratadas e dataframe principal

```bat
python frames.py
```

Esse comando:

1. executa ou carrega do cache cada pipeline;
2. salva bases tratadas individuais em `bases/tratadas/`;
3. valida se cada base tem chave única por `Estado/Ano` ou `Regiao/Ano`;
4. faz os merges a partir da base de CO2;
5. salva o dataframe principal.

No cenário estadual, o arquivo final esperado é:

```text
bases/tratadas/dataframe-principal-estado-tratada.csv
```

No cenário regional, o arquivo final esperado é:

```text
bases/tratadas/dataframe-principal-regiao-tratada.csv
```

### 3. Rodar análise estatística e exploratória

```bat
python analise_df_principal.py
```

Esse comando:

1. carrega o dataframe principal definido automaticamente pelo `config.py`;
2. valida as chaves;
3. mostra missing values antes e depois da preparação;
4. roda Shapiro-Wilk;
5. roda Pearson;
6. roda Spearman;
7. gera heatmaps, se habilitado;
8. gera visualizações exploratórias, se habilitadas.

---

## Saídas geradas

### Bases tratadas individuais

```text
bases/tratadas/co2-estado-tratada.csv
bases/tratadas/frota-estado-tratada.csv
bases/tratadas/rebanho-estado-tratada.csv
bases/tratadas/venda-combustiveis-estado-tratada.csv
bases/tratadas/desmatamento-mapbiomas-estado-tratada.csv
bases/tratadas/inmet-clima-estado-tratada.csv
bases/tratadas/area-destinada-colheita-estado-tratada.csv
bases/tratadas/area-colhida-estado-tratada.csv
bases/tratadas/energia-industrial-estado-tratada.csv
bases/tratadas/queimadas-estado-tratada.csv
```

### Dataframe principal

```text
bases/tratadas/dataframe-principal-estado-tratada.csv
```

ou, se `AGRUPAR_POR_REGIAO = True`:

```text
bases/tratadas/dataframe-principal-regiao-tratada.csv
```

### Resultados estatísticos

```text
bases/tratadas/shapiro_por_estado.csv
bases/tratadas/pearson_por_estado.csv
bases/tratadas/spearman_por_estado.csv
```

ou, no cenário regional:

```text
bases/tratadas/shapiro_por_regiao.csv
bases/tratadas/pearson_por_regiao.csv
bases/tratadas/spearman_por_regiao.csv
```

### Heatmaps

Quando `GERAR_HEATMAPS = True`, são gerados:

```text
bases/tratadas/correlacao_estado_metodo_misto_blocos_causa_consequencia.csv
bases/tratadas/correlacao_estado_heatmap_base_blocos_causa_consequencia.csv
graficos/heatmaps/
```

O heatmap atual é específico para análise estadual, pois organiza os estados em blocos analíticos.

---

## INMET

A base do INMET deve estar organizada com uma pasta por ano:

```text
bases/inmet/
├── 2004/
│   ├── INMET_CO_GO_A012_LUZIANIA_01-01-2004_A_31-12-2004.CSV
│   └── ...
├── 2005/
│   └── ...
└── 2023/
    └── ...
```

Cada arquivo representa uma estação meteorológica.

O pipeline do INMET calcula, em uma única passagem:

- `temp_media`: temperatura média anual;
- `chuva_media`: chuva média anual.

Configurações principais:

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

```python
INMET_PARALELO = True
INMET_MAX_WORKERS = None
```

Com `None`, o pipeline escolhe automaticamente a quantidade de workers.

Em SSD/NVMe, valores como `8`, `16` ou `32` podem ser testados manualmente:

```python
INMET_MAX_WORKERS = 8
```

---

## Queimadas

A base de queimadas deve estar em:

```text
bases/queimadas/
```

Configurações principais:

```python
PASTA_QUEIMADAS = "bases/queimadas"
QUEIMADAS_PARALELO = True
QUEIMADAS_MAX_WORKERS = None
```

O pipeline calcula:

```text
frp_anual_queimadas
```

Essa variável representa a soma anual do FRP detectado nos focos de queimadas.

---

## Missing values

O script de análise exibe:

```text
=== Missing values antes do preenchimento ===
=== Missing values após o preenchimento ===
```

A preparação atual aplica interpolação apenas quando a coluna existe, por exemplo `Populacao`.

Valores ausentes podem ser esperados por diferença de cobertura temporal entre as fontes. Por exemplo, algumas bases começam depois de 2004 ou possuem cobertura incompleta em determinados estados.

---

## Metodologia estatística implementada

### Shapiro-Wilk

Avalia a normalidade das séries temporais de cada variável por grupo.

Saída:

```text
bases/tratadas/shapiro_por_estado.csv
```

### Pearson

Calcula correlação linear entre `co2` e as demais variáveis por grupo.

Saída:

```text
bases/tratadas/pearson_por_estado.csv
```

### Spearman

Calcula correlação monotônica entre `co2` e as demais variáveis por grupo.

Saída:

```text
bases/tratadas/spearman_por_estado.csv
```

### Heatmap de correlação mista

O heatmap estadual usa a seguinte lógica:

1. aplica Shapiro-Wilk em `co2` e na variável analisada;
2. se ambas as séries não rejeitam normalidade, usa Pearson;
3. caso contrário, usa Spearman;
4. marca com `*` as correlações significativas a 5%.

Os estados são organizados em três blocos analíticos:

| Bloco | Estados |
|---|---|
| Amazônia Legal | AC, AM, AP, MA, MT, PA, RO, RR, TO |
| Agropecuária | BA, GO, MS, PI, CE, RN, PB, PE, AL, SE |
| Energia/industrial | SP, RJ, MG, ES, PR, SC, RS, DF |

As variáveis são separadas em:

- causas;
- consequências.

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

## Observações para VS Code

Se o VS Code selecionar outro interpretador automaticamente, escolha manualmente o Python dentro da pasta `.env`.

Caminho típico no Windows:

```text
.env\Scripts\python.exe
```

---

## Cuidados importantes

- Ajuste configurações metodológicas em `config.py`, não diretamente em `frames.py` ou `analise_df_principal.py`.
- Não misture bases estaduais com merge regional.
- Para análise estadual, use `AGRUPAR_POR_REGIAO = False`.
- Para análise regional, use `AGRUPAR_POR_REGIAO = True` e gere novamente as bases.
- O heatmap atual foi desenhado para análise estadual.
- Evite reprocessar o INMET sem necessidade; use `REPROCESSAR_TUDO = False` quando quiser reaproveitar bases tratadas.
- Confira se os nomes dos arquivos brutos batem com os caminhos esperados nos pipelines.
- Ao mudar o recorte temporal em `config.py`, rode novamente `frames.py`.
