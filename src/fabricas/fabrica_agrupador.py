from typing import Dict, List, Optional
from src.agrupadores.agrupador_afinidade import AgrupadorAfinidade
from src.agrupadores.agrupador_aglomerativo import AgrupadorAglomerativo
from src.agrupadores.agrupador_bertopic import AgrupadorBertopic
from src.agrupadores.agrupador_birch import AgrupadorBirch
from src.agrupadores.agrupador_dbscan import AgrupadorDbscan
from src.agrupadores.agrupador_espectral import AgrupadorEspectral
from src.agrupadores.agrupador_gaussiano import AgrupadorGaussiano
from src.agrupadores.agrupador_hdbscan import AgrupadorHdbscan
from src.agrupadores.agrupador_kmeans import AgrupadorKmeans
from src.agrupadores.agrupador_media import AgrupadorMedia
from src.agrupadores.agrupador_minibatch import AgrupadorMinibatch
from src.agrupadores.agrupador_optics import AgrupadorOptics
from src.agrupadores.estrategia_agrupamento import EstrategiaAgrupamento
from src.dominio.configuracao_projeto import ConfiguracaoProjeto
from src.processamento.tratador_stopword import TratadorStopword


class FabricaAgrupador:
    """Fábrica GoF Factory Method para instanciação padronizada de estratégias de agrupamento."""

    def __init__(self, configuracao: ConfiguracaoProjeto) -> None:
        self.configuracao = configuracao

    def listar_disponiveis(self) -> List[str]:
        """Lista os nomes de todos os algoritmos suportados pelo projeto."""
        return [
            "bertopic",
            "kmeans",
            "minibatch_kmeans",
            "dbscan",
            "hdbscan",
            "optics",
            "agglomerative",
            "gaussian_mixture",
            "spectral",
            "affinity_propagation",
            "mean_shift",
            "birch",
        ]

    def criar_modelo(self, nome_algoritmo: str) -> EstrategiaAgrupamento:
        """Cria e devolve a estratégia correspondente com base no nome e nas configurações."""
        nome = nome_algoritmo.lower().strip()
        if nome in ("bertopic",):
            tratador = TratadorStopword(self.configuracao.stopwords_adicionais)
            return AgrupadorBertopic(
                top_n_words=self.configuracao.top_n_palavras_bertopic,
                ngram_min=1,
                ngram_max=1,
                stopwords=list(tratador.obter_stopwords()),
            )
        if nome in ("kmeans",):
            return AgrupadorKmeans(n_clusters=10, random_state=42)
        if nome in ("minibatch_kmeans", "minibatch"):
            return AgrupadorMinibatch(n_clusters=10, batch_size=256, random_state=42)
        if nome in ("dbscan",):
            return AgrupadorDbscan(eps=0.5, min_samples=5, metric="cosine")
        if nome in ("hdbscan",):
            return AgrupadorHdbscan(min_cluster_size=15, min_samples=5, metric="euclidean")
        if nome in ("optics",):
            return AgrupadorOptics(min_samples=5, metric="cosine")
        if nome in ("agglomerative", "aglomerativo"):
            return AgrupadorAglomerativo(n_clusters=10, metric="cosine", linkage="average")
        if nome in ("gaussian_mixture", "gaussiano", "gmm"):
            return AgrupadorGaussiano(n_components=10, random_state=42)
        if nome in ("spectral", "espectral"):
            return AgrupadorEspectral(n_clusters=10, random_state=42)
        if nome in ("affinity_propagation", "afinidade"):
            return AgrupadorAfinidade(damping=0.8, random_state=42)
        if nome in ("mean_shift", "media"):
            return AgrupadorMedia(bandwidth=0.8)
        if nome in ("birch",):
            return AgrupadorBirch(n_clusters=10, threshold=0.5)

        raise ValueError(f"Algoritmo desconhecido: {nome_algoritmo}. Disponíveis: {self.listar_disponiveis()}")
