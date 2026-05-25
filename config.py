from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    # Recorte temporal do TCC
    ANO_INICIAL: int = 2004
    ANO_FINAL: int = 2023

    # Granularidade principal
    AGRUPAR_POR_REGIAO: bool = False
    COLUNA_ANO: str = "Ano"
    COLUNA_ALVO: str = "co2"

    # Reprocessamento/cache
    REPROCESSAR_TUDO: bool = True

    # Caminhos
    PASTA_BASES: str = "bases"
    PASTA_TRATADAS: str = "bases/tratadas"
    PASTA_GRAFICOS: str = "graficos"
    PASTA_INMET: str = "bases/inmet"
    PASTA_QUEIMADAS: str = "bases/queimadas"

    # INMET
    INMET_SOMENTE_CAPITAIS: bool = False
    INMET_PARALELO: bool = True
    INMET_MAX_WORKERS: int | None = None

    # Queimadas
    QUEIMADAS_PARALELO: bool = True
    QUEIMADAS_MAX_WORKERS: int | None = None

    # Análises
    GERAR_VISUALIZACOES: bool = True
    GERAR_HEATMAPS: bool = True
    GERAR_HEATMAPS_POR_BLOCO: bool = True
    IGNORAR_COLUNAS: tuple[str, ...] = ("IDHM", "internacoes")

    @property
    def coluna_grupo(self) -> str:
        return "Regiao" if self.AGRUPAR_POR_REGIAO else "Estado"

    @property
    def chaves_merge(self) -> list[str]:
        return [self.coluna_grupo, self.COLUNA_ANO]

    @property
    def sufixo_granularidade(self) -> str:
        return "regiao" if self.AGRUPAR_POR_REGIAO else "estado"

    @property
    def caminho_df_principal(self) -> str:
        return f"{self.PASTA_TRATADAS}/dataframe-principal-{self.sufixo_granularidade}-tratada.csv"

    def caminho_base_tratada(self, nome_base_tratada: str) -> str:
        return f"{self.PASTA_TRATADAS}/{nome_base_tratada}-tratada.csv"


CONFIG = Config()