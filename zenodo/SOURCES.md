# Fontes de dados

Este documento registra as fontes efetivamente incorporadas ao dataframe final `bases/tratadas/dataframe-principal-estado-tratada.csv`. A referência principal para instituições, nomes e URLs é o arquivo de levantamento `bases_levantamento.csv`; detalhes de transformação foram conferidos nos pipelines.

## SEEG

- **Instituição/base:** Sistema de Estimativas de Emissões e Remoções de Gases de Efeito Estufa (SEEG), emissões brutas de CO2.
- **URL oficial:** https://plataforma.seeg.eco.br/?yearRange%5B0%5D=1990&yearRange%5B1%5D=2023&emissionType%5B0%5D=1&gas=8&groupBy=Sector&rankBy=State&filtersTab=highlights&statisticsTab=historical
- **Variável final:** `co2`.
- **Granularidade original:** Estado/ano na estrutura utilizada pelo arquivo; o código faz transformação wide para long.
- **Transformação:** filtro 2004–2023, remoção de `Não alocado`, normalização para UF e conversão numérica.
- **Período utilizado:** 2004–2023; a base registrada cobre 1990–2023.
- **Data de acesso:** 24/06/2025.
- **Licença/reutilização:** Dados abertos e públicos sob licença Creative Commons Atribuição (CC BY). Permitido o uso, cruzamento e modificação com atribuição obrigatória da fonte (Observatório do Clima / SEEG).

## SENATRAN

- **Instituição/base:** SENATRAN/DENATRAN, frota de veículos (via portal Base dos Dados).
- **URL registrada:** https://basedosdados.org/dataset/61d592ca-5aec-4f66-b8eb-f7b894a29b66?table=3f0d609e-c85d-4daf-845f-08dd502665b2
- **Variável final:** `frota`.
- **Granularidade original:** mensal por UF e tipo de veículo.
- **Transformação:** seleção de tipos motorizados; soma por mês; escolha do último mês disponível de cada ano; renomeação para `Estado`, `Ano` e `frota`.
- **Período utilizado:** 2004–2023; a base registrada cobre 2003–2023.
- **Data de acesso:** 25/06/2025.
- **Licença/reutilização:** Domínio Público / Política de Dados Abertos do Governo Federal (Decreto nº 8.777/2016). A distribuição via portal Base dos Dados segue a licença Creative Commons CC BY 4.0. Livre reutilização mediante atribuição.

## IBGE/SIDRA

- **Instituição/base:** IBGE; produção pecuária municipal para `rebanho`, e tabelas IBGE/SIDRA para áreas agrícola destinada e colhida.
- **URLs registradas:** produção pecuária: https://www.ibge.gov.br/estatisticas/economicas/agricultura-e-pecuaria/9107-producao-da-pecuaria-municipal.html?=&t=series-historicas ; área destinada: https://sidra.ibge.gov.br/Tabela/5457 ;.
- **Variáveis finais:** `rebanho`, `area_destinada_colheita`, `area_colhida`.
- **Granularidade original:** rebanho em tabela estruturada por UF, ano e tipo de animal; áreas em tabelas wide por UF e ano.
- **Transformação:** rebanho reconstruído a partir de cabeçalhos multinível, seleção de `BOVINO` e soma por UF/ano; áreas convertidas de wide para long, valores especiais tratados como ausentes e agregados por UF/ano.
- **Período utilizado:** 2004–2023; rebanho registrado como 1974–2023, área destinada como 1988–2024 e área colhida como 1974–2024.
- **Data de acesso:** 21/09/2025.
- **Licença/reutilização:** Domínio público e acesso livre sob a Política de Acesso Aberto às Informações e Dados do IBGE (Resolução PR-1/2014). Reutilização livre mediante citação da fonte.

## ANP

- **Instituição/base:** Agência Nacional do Petróleo, Gás Natural e Biocombustíveis (ANP), disponibilizada via Portal Brasileiro de Dados Abertos (dados.gov.br).
- **URL registrada:** https://dados.gov.br/dados/conjuntos-dados/vendas-de-derivados-de-petroleo-e-biocombustiveis
- **Variável final:** `venda_comb`.
- **Granularidade original:** mensal por UF e produto.
- **Transformação:** conversão de número no padrão brasileiro e soma de produtos e meses por UF/ano; filtro 2004–2023.
- **Período utilizado:** 2004–2023; a base registrada cobre 1990–2025.
- **Data de acesso:**07/01/2026.
- **Licença/reutilização:** Dados abertos governamentais regidos pelo Decreto nº 8.777/2016 e pela Lei de Acesso à Informação (Lei nº 12.527/2011). Livre utilização, consumo e cruzamento sem restrições autorais, exigindo apenas o crédito à fonte.

## MapBiomas

- **Instituição/base:** Projeto MapBiomas (Iniciativa do Observatório do Clima/SEEG e parceiros), estatísticas de desmatamento/cobertura vegetal.
- **URL registrada:** https://brasil.mapbiomas.org/estatisticas/
- **Variável final:** `desmat_area`.
- **Granularidade original:** estado/bioma/ano, com classes, transições e níveis de classe.
- **Transformação:** transformação wide para long e soma, por UF/ano, de biomas, classes e transições presentes na planilha; filtro 2004–2023.
- **Período utilizado:** 2004–2023; a base registrada cobre 1987–2024.
- **Data de acesso:** 03/09/2025.
- **Licença/reutilização:** Dados abertos e gratuitos sob licença Creative Commons Atribuição (CC BY / CC BY-SA). Livre adaptação e reprodução, exigindo citação formal do Projeto MapBiomas.

## EPE

- **Instituição/base:** Empresa de Pesquisa Energética (EPE), consumo de energia elétrica industrial por estado.
- **URL registrada:** https://www.epe.gov.br/pt/publicacoes-dados-abertos/publicacoes/consumo-de-energia-eletrica
- **Variável final:** `consumo_energia_industrial`.
- **Granularidade original:** mensal por UF.
- **Transformação:** identificação dos anos na planilha, conversão numérica, soma dos meses por ano, exclusão de linhas `TOTAL`/`NOTA` e filtro 2004–2023.
- **Período utilizado:** 2004–2023; a base registrada cobre 2004–2025.
- **Data de acesso:** 03/09/2025.
- **Licença/reutilização:** Dados abertos governamentais vinculados ao Ministério de Minas e Energia (MME), em consonância com a Política de Dados Abertos (Decreto nº 8.777/2016). Uso livre com atribuição de autoria à EPE.

## INPE / BDQueimadas

- **Instituição/base:** Instituto Nacional de Pesquisas Espaciais (INPE) / Terra Brasilis, Banco de Dados de Queimadas (BDQueimadas).
- **URL registrada:** https://terrabrasilis.dpi.inpe.br/queimadas/bdqueimadas/#exportar-dados
- **Variável final:** `frp_anual_queimadas`.
- **Granularidade original:** registro de foco de queimada, com data/hora, UF e FRP.
- **Transformação:** leitura em partes dos arquivos; seleção de registros do Brasil; uso do ano inicial indicado no nome do arquivo; normalização de UF; descarte de valores ausentes e códigos `-999`; soma anual de FRP por UF.
- **Período utilizado:** 2004–2023; os arquivos locais abrangem 2003–2023.
- **Data de acesso:** 13/05/2026.
- **Licença/reutilização:** Dados abertos públicos fornecidos por autarquia federal (MCTI/INPE), sob o Decreto nº 8.777/2016. Uso e distribuição livres mediante citação da fonte (INPE/BDQueimadas).

## INMET

- **Instituição/base:** Instituto Nacional de Meteorologia (INMET), dados históricos de séries horárias de estações meteorológicas.
- **URL registrada:** https://portal.inmet.gov.br/dadoshistoricos
- **Variáveis finais:** `temp_media` e `chuva_media`.
- **Granularidade original:** observação horária por estação; a pasta presente no repositório contém arquivos de 2006 a 2019.
- **Transformação:** exclusão de sentinelas e valores inválidos; temperatura calculada por estação e ano e agregada por UF com ponderação pelo número de observações; chuva calculada como total anual por estação e média dos totais entre estações do estado; fusão por Estado/Ano.
- **Período utilizado:** efetivamente observado no repositório: 2006–2019. O recorte configurado do projeto é 2004–2023, mas não há arquivos INMET locais para os anos anteriores a 2006 ou posteriores a 2019.
- **Data de acesso:** 01/04/2026.
- **Licença/reutilização:** Dados abertos governamentais vinculados ao Ministério da Agricultura e Pecuária (MAPA), sob a Política de Dados Abertos do Executivo Federal (Decreto nº 8.777/2016). Reutilização livre com indicação de crédito ao INMET.

## Atribuição e reutilização

O dataset integrado é derivado de múltiplas fontes públicas e abertas. Todas as fontes primárias operam sob licenças abertas (Creative Commons CC BY / CC BY-SA) ou sob o arcabouço da Política de Dados Abertos do Poder Executivo Federal (Decreto nº 8.777/2016 e Lei nº 12.527/2011). As atribuições, avisos de direitos autorais, termos de uso e condições de reutilização originais das instituições fornecedoras permanecem plenamente vigentes. O uso do dataframe final derivado é totalmente permitido para fins acadêmicos e analíticos, desde que mantidas as devidas citações e créditos a cada instituição geradora.