# Painel estadual de indicadores relacionados às emissões brutas de CO2 no Brasil

## Descrição

Este dataset contém um painel Estado-Ano com indicadores públicos relacionados às emissões brutas de CO2 nas 27 unidades federativas brasileiras, no período de 2004 a 2023. O arquivo final observado contém 540 registros, correspondentes a uma observação por UF e ano, e 13 variáveis.

O painel foi produzido pela fusão de bases heterogêneas de emissões, transporte, pecuária, combustíveis, uso da terra, clima, agricultura, energia e queimadas. O desenho é observacional e as análises do projeto são exploratórias/associativas; as correlações não devem ser interpretadas como efeitos causais.

## Objetivo

Disponibilizar uma base integrada para análises exploratórias de variação estadual e temporal de emissões brutas de CO2 e de indicadores ambientais, agropecuários, energéticos, climáticos e de transporte.

## Cobertura e estrutura

- **Período:** 2004–2023.
- **Cobertura espacial:** 27 unidades federativas brasileiras.
- **Estrutura:** Estado-Ano.
- **Registros:** 540.
- **Chave:** `Estado` + `Ano`, sem duplicidades no arquivo final observado.

## Variáveis

`Estado`, `Ano`, `co2`, `frota`, `rebanho`, `venda_comb`, `desmat_area`, `temp_media`, `chuva_media`, `area_destinada_colheita`, `area_colhida`, `consumo_energia_industrial` e `frp_anual_queimadas`.

As definições, fontes, unidades confirmadas e transformações estão em [DATA_DICTIONARY.csv](DATA_DICTIONARY.csv) e [SOURCES.md](SOURCES.md). A unidade de `co2` e `frp_anual_queimadas` não pode ser determinada sem ambiguidade a partir do material disponível e está marcada como A CONFIRMAR. `frota` e `rebanho` são contagens, mas a unidade formal da fonte não está registrada além de `unidade` no levantamento.

## Fontes

As fontes efetivamente presentes no dataframe final são SEEG, SENATRAN/DENATRAN, IBGE/SIDRA, dados.gov.br, MapBiomas, EPE, INPE/BDQueimadas e INMET. Consulte [SOURCES.md](SOURCES.md) para URLs, períodos, granularidades e limitações documentais.

## Processo de fusão

`frames.py` parte da base de CO2 e incorpora as demais bases por `left join` nas chaves `Estado` e `Ano`. Cada pipeline filtra o período comum, normaliza nomes de unidades federativas e retorna uma base anual estadual. O resultado é ordenado pelas chaves e salvo em `bases/tratadas/dataframe-principal-estado-tratada.csv`.

## Heterogeneidades

- **Temporal:** fontes mensais são agregadas para o ano; a frota usa o último mês disponível de cada ano; energia soma os meses; combustíveis somam produtos e meses; clima e queimadas são agregados anualmente.
- **Espacial:** nomes de estados são normalizados para siglas UF. O painel final usa a mesma chave estadual, embora as fontes originais possam ser por estação, produto, tipo de veículo, bioma ou foco.
- **Estrutural:** tabelas wide são convertidas para long; a planilha de rebanho é reconstruída a partir de cabeçalhos multinível; categorias e registros são selecionados conforme cada pipeline.

## Valores ausentes

No arquivo final observado, `temp_media` e `chuva_media` têm 203 valores ausentes cada; as demais colunas não apresentam ausências. Esses valores resultam do `left join` quando não há observação climática correspondente. O projeto não imputa as variáveis climáticas. Valores inválidos ou sentinelas são tratados nos pipelines, conforme detalhado no dicionário; a rotina de interpolação existente é condicional a uma coluna `Populacao`, que não existe no dataframe final.

## Arquivos disponibilizados

- `dataframe-principal-estado-tratada.csv`: painel integrado descrito neste documento.
- `DATA_DICTIONARY.csv`: dicionário das 13 colunas do painel.
- `SOURCES.md`: proveniência, transformações e informações de fontes.
- `LICENSE_DATASET_TEMPLATE.md`: modelo para registrar posteriormente a licença do dataset integrado.
- `CITATION.cff`: metadados de citação, com campos ainda pendentes de confirmação.
- `bases/tratadas/`: bases intermediárias e resultados derivados do projeto, quando incluídos no depósito.
- `bases/`: arquivos brutos utilizados pelo processamento, quando sua redistribuição for permitida pelas condições das fontes originais.

## Uso básico

Exemplo em Python:

```python
import pandas as pd

df = pd.read_csv("dataframe-principal-estado-tratada.csv")
df = df.sort_values(["Estado", "Ano"])
```

Para reproduzir o tratamento no repositório do projeto, consulte [README.md](README.md) e execute os pipelines conforme as configurações de [config.py](config.py). O código responsável pela montagem do painel é [frames.py](frames.py), e o código de análise é [analise_df_principal.py](analise_df_principal.py). URL pública do repositório: A CONFIRMAR.

## Citation

Use o arquivo `CITATION.cff` e a referência gerada pelo Zenodo após o depósito. DOI: A CONFIRMAR, pois ainda não foi criado.

## License and attribution

A licença do dataset integrado ainda não foi escolhida. Consulte [LICENSE_DATASET_TEMPLATE.md](LICENSE_DATASET_TEMPLATE.md). A licença ou os termos de reutilização do dataset integrado não substituem as condições aplicáveis às fontes originais; as atribuições correspondentes devem ser mantidas.

## Provenance

O dataset foi produzido neste projeto a partir dos arquivos locais e pipelines descritos em [SOURCES.md](SOURCES.md). Não estão registrados no material disponível a data de acesso às fontes, versões formais, hashes das bases brutas ou uma data de processamento reproduzível. O arquivo de desmatamento é processado durante a montagem e sua coluna `desmat_area` entra normalmente no painel final; o pipeline não salva, separadamente, uma base estadual intermediária desse indicador.
