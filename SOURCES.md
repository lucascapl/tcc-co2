# Fontes de dados

Este documento registra as fontes efetivamente incorporadas ao dataframe final `bases/tratadas/dataframe-principal-estado-tratada.csv`. A referência principal para instituições, nomes e URLs é o arquivo de levantamento `bases_levantamento.csv`; detalhes de transformação foram conferidos nos pipelines.

## SEEG

- **Instituição/base:** Sistema de Estimativas de Emissões e Remoções de Gases de Efeito Estufa (SEEG), emissões brutas de CO2.
- **URL oficial:** https://plataforma.seeg.eco.br/?yearRange%5B0%5D=1990&yearRange%5B1%5D=2023&emissionType%5B0%5D=1&gas=8&groupBy=Sector&rankBy=State&filtersTab=highlights&statisticsTab=historical
- **Variável final:** `co2`.
- **Granularidade original:** Estado/ano na estrutura utilizada pelo arquivo; o código faz transformação wide para long.
- **Transformação:** filtro 2004–2023, remoção de `Não alocado`, normalização para UF e conversão numérica.
- **Período utilizado:** 2004–2023; a base registrada cobre 1990–2023.
- **Data de acesso:** A CONFIRMAR.
- **Licença/reutilização:** A CONFIRMAR; não há licença registrada no material disponível.

## SENATRAN

- **Instituição/base:** SENATRAN/DENATRAN, frota de veículos.
- **URL registrada:** https://basedosdados.org/dataset/61d592ca-5aec-4f66-b8eb-f7b894a29b66?table=3f0d609e-c85d-4daf-845f-08dd502665b2
- **Variável final:** `frota`.
- **Granularidade original:** mensal por UF e tipo de veículo.
- **Transformação:** seleção de tipos motorizados; soma por mês; escolha do último mês disponível de cada ano; renomeação para `Estado`, `Ano` e `frota`.
- **Período utilizado:** 2004–2023; a base registrada cobre 2003–2023.
- **Data de acesso:** A CONFIRMAR.
- **Licença/reutilização:** A CONFIRMAR; não há licença registrada no material disponível.

## IBGE/SIDRA

- **Instituição/base:** IBGE; produção pecuária municipal para `rebanho`, e tabelas IBGE/SIDRA para áreas agrícola destinada e colhida.
- **URLs registradas:** produção pecuária: https://www.ibge.gov.br/estatisticas/economicas/agricultura-e-pecuaria/9107-producao-da-pecuaria-municipal.html?=&t=series-historicas ; área destinada: https://sidra.ibge.gov.br/Tabela/5457 ; URL específica da área colhida: A CONFIRMAR.
- **Variáveis finais:** `rebanho`, `area_destinada_colheita`, `area_colhida`.
- **Granularidade original:** rebanho em tabela estruturada por UF, ano e tipo de animal; áreas em tabelas wide por UF e ano.
- **Transformação:** rebanho reconstruído a partir de cabeçalhos multinível, seleção de `BOVINO` e soma por UF/ano; áreas convertidas de wide para long, valores especiais tratados como ausentes e agregados por UF/ano.
- **Período utilizado:** 2004–2023; rebanho registrado como 1974–2023, área destinada como 1988–2024 e área colhida como 1974–2024.
- **Data de acesso:** A CONFIRMAR.
- **Licença/reutilização:** A CONFIRMAR; não há licença registrada no material disponível.

## ANP

- **Instituição/base:** A instituição responsável não é nomeada como ANP no `base_levantamento.csv`; o inventário registra `gov/min. transporte` e a origem `dados.gov.br`, para vendas de derivados de petróleo e biocombustíveis. A atribuição institucional específica fica A CONFIRMAR.
- **URL registrada:** https://dados.gov.br/dados/conjuntos-dados/vendas-de-derivados-de-petroleo-e-biocombustiveis
- **Variável final:** `venda_comb`.
- **Granularidade original:** mensal por UF e produto.
- **Transformação:** conversão de número no padrão brasileiro e soma de produtos e meses por UF/ano; filtro 2004–2023.
- **Período utilizado:** 2004–2023; a base registrada cobre 1990–2025.
- **Data de acesso:** A CONFIRMAR.
- **Licença/reutilização:** A CONFIRMAR; não há licença registrada no material disponível.

## MapBiomas

- **Instituição/base:** MapBiomas, arquivo de desmatamento por bioma, estado e ano. O `base_levantamento.csv` usa a nomenclatura `MapBiomas(SEEG)`, mas a fonte identificada pelo arquivo local e pelo pipeline é MapBiomas.
- **URL registrada:** https://brasil.mapbiomas.org/estatisticas/
- **Variável final:** `desmat_area`.
- **Granularidade original:** estado/bioma/ano, com classes, transições e níveis de classe.
- **Transformação:** transformação wide para long e soma, por UF/ano, de biomas, classes e transições presentes na planilha; filtro 2004–2023.
- **Período utilizado:** 2004–2023; a base registrada cobre 1987–2024.
- **Data de acesso:** A CONFIRMAR.
- **Licença/reutilização:** A CONFIRMAR; não há licença registrada no material disponível.

## EPE

- **Instituição/base:** Empresa de Pesquisa Energética (EPE), consumo de energia elétrica industrial por estado.
- **URL registrada:** https://www.epe.gov.br/pt/publicacoes-dados-abertos/publicacoes/consumo-de-energia-eletrica
- **Variável final:** `consumo_energia_industrial`.
- **Granularidade original:** mensal por UF.
- **Transformação:** identificação dos anos na planilha, conversão numérica, soma dos meses por ano, exclusão de linhas `TOTAL`/`NOTA` e filtro 2004–2023.
- **Período utilizado:** 2004–2023; a base registrada cobre 2004–2025.
- **Data de acesso:** A CONFIRMAR.
- **Licença/reutilização:** A CONFIRMAR; não há licença registrada no material disponível.

## INPE / BDQueimadas

- **Instituição/base:** INPE / Terra Brasilis, Banco de Dados de Queimadas (BDQueimadas).
- **URL registrada:** https://terrabrasilis.dpi.inpe.br/queimadas/bdqueimadas/#exportar-dados
- **Variável final:** `frp_anual_queimadas`.
- **Granularidade original:** registro de foco de queimada, com data/hora, UF e FRP.
- **Transformação:** leitura em partes dos arquivos; seleção de registros do Brasil; uso do ano inicial indicado no nome do arquivo; normalização de UF; descarte de valores ausentes e códigos `-999`; soma anual de FRP por UF.
- **Período utilizado:** 2004–2023; os arquivos locais abrangem 2003–2023.
- **Data de acesso:** A CONFIRMAR.
- **Licença/reutilização:** A CONFIRMAR; não há licença registrada no material disponível.

## INMET

- **Instituição/base:** Instituto Nacional de Meteorologia (INMET), dados históricos de séries horárias de estações meteorológicas.
- **URL registrada:** https://portal.inmet.gov.br/dadoshistoricos
- **Variáveis finais:** `temp_media` e `chuva_media`.
- **Granularidade original:** observação horária por estação; a pasta presente no repositório contém arquivos de 2006 a 2019.
- **Transformação:** exclusão de sentinelas e valores inválidos; temperatura calculada por estação e ano e agregada por UF com ponderação pelo número de observações; chuva calculada como total anual por estação e média dos totais entre estações do estado; fusão por Estado/Ano.
- **Período utilizado:** efetivamente observado no repositório: 2006–2019. O recorte configurado do projeto é 2004–2023, mas não há arquivos INMET locais para os anos anteriores a 2006 ou posteriores a 2019.
- **Data de acesso:** A CONFIRMAR.
- **Licença/reutilização:** A CONFIRMAR; não há licença registrada no material disponível.

## Atribuição e reutilização

O dataset integrado é derivado de múltiplas fontes públicas. As atribuições, avisos, termos de uso e condições de reutilização aplicáveis às fontes originais permanecem vigentes e não são substituídos por este documento ou por uma futura licença do dataset integrado. O repositório não registra licenças específicas das fontes; por isso, essas informações permanecem A CONFIRMAR.
