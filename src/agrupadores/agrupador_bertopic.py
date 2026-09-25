import logging
from typing import Dict, List, Optional, Tuple
from bertopic import BERTopic
import hdbscan
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
import umap

from src.agrupadores.estrategia_agrupamento import EstrategiaAgrupamento

logger = logging.getLogger(__name__)


class AgrupadorBertopic(EstrategiaAgrupamento):
    """Estratégia BERTopic PT-BR alimentada exclusivamente com embeddings spaCy."""

    def __init__(
        self,
        top_n_words: int = 10,
        n_neighbors: int = 15,
        n_components: int = 5,
        min_dist: float = 0.0,
        metric_umap: str = "cosine",
        random_state: int = 42,
        min_cluster_size: int = 15,
        min_samples: int = 5,
        ngram_min: int = 1,
        ngram_max: int = 2,
        min_df: int = 1,
        max_df: float = 0.90,
        stopwords: Optional[List[str]] = None,
    ) -> None:
        self.top_n_words = top_n_words
        self.n_neighbors = n_neighbors
        self.n_components = n_components
        self.min_dist = min_dist
        self.metric_umap = metric_umap
        self.random_state = random_state
        self.min_cluster_size = min_cluster_size
        self.min_samples = min_samples
        self.max_df = max_df

        self.modelo_umap = umap.UMAP(
            n_neighbors=self.n_neighbors,
            n_components=self.n_components,
            min_dist=self.min_dist,
            metric=self.metric_umap,
            random_state=self.random_state,
        )

        self.modelo_hdbscan = hdbscan.HDBSCAN(
            min_cluster_size=self.min_cluster_size,
            min_samples=self.min_samples,
            metric="euclidean",
            cluster_selection_method="eom",
            prediction_data=True,
        )

        # CountVectorizer com max_df=1.0 para compatibilidade com c-TF-IDF em poucos tópicos
        self.vetorizador = CountVectorizer(
            ngram_range=(ngram_min, ngram_max),
            min_df=min_df,
            max_df=1.0 if max_df < 1.0 else max_df,
            stop_words=stopwords,
        )

        # BERTopic inicializado SEM modelo de embedding interno para forçar spaCy
        self.modelo_bertopic = BERTopic(
            embedding_model=None,
            umap_model=self.modelo_umap,
            hdbscan_model=self.modelo_hdbscan,
            vectorizer_model=self.vetorizador,
            top_n_words=self.top_n_words,
            calculate_probabilities=True,
            verbose=False,
        )

        self.rotulos: np.ndarray = np.array([], dtype=np.int32)
        self.probabilidades: np.ndarray = np.array([], dtype=np.float32)

    def treinar_modelo(self, embeddings: np.ndarray, textos: Optional[List[str]] = None) -> np.ndarray:
        """Treina BERTopic recebendo textos e a matriz de embeddings gerada pelo spaCy."""
        if textos is None or len(textos) == 0:
            return np.array([], dtype=np.int32)

        n_amostras = len(textos)
        # Ajusta parâmetros dinamicamente para volumes pequenos em testes
        if n_amostras < self.min_cluster_size:
            tamanho_ajustado = max(2, n_amostras // 2)
            self.modelo_hdbscan.min_cluster_size = tamanho_ajustado
            self.modelo_hdbscan.min_samples = max(1, tamanho_ajustado // 2)

        if n_amostras <= self.n_neighbors:
            self.modelo_umap.n_neighbors = max(2, n_amostras - 1)
        if n_amostras <= self.n_components + 2:
            self.modelo_umap.n_components = max(2, min(self.n_components, n_amostras - 2)) if n_amostras > 3 else 2
            self.modelo_umap.init = "random"

        logger.info("Executando BERTopic fit_transform com %d documentos e embeddings spaCy.", len(textos))
        topicos, probs = self.modelo_bertopic.fit_transform(textos, embeddings=embeddings)

        self.rotulos = np.array(topicos, dtype=np.int32)
        if probs is not None:
            if isinstance(probs, np.ndarray) and probs.ndim == 2:
                self.probabilidades = np.max(probs, axis=1).astype(np.float32)
            elif isinstance(probs, np.ndarray):
                self.probabilidades = probs.astype(np.float32)
            elif isinstance(probs, list):
                self.probabilidades = np.array(probs, dtype=np.float32)
            else:
                self.probabilidades = np.ones(len(self.rotulos), dtype=np.float32)
        else:
            self.probabilidades = np.ones(len(self.rotulos), dtype=np.float32)

        return self.rotulos

    def obter_rotulos(self) -> np.ndarray:
        """Retorna os identificadores dos tópicos descobertos (-1 representa ruído)."""
        return self.rotulos

    def obter_probabilidades(self) -> np.ndarray:
        """Retorna probabilidades de pertencimento calculadas pelo BERTopic."""
        return self.probabilidades

    def obter_nome(self) -> str:
        """Identificador textual do algoritmo."""
        return "BERTopic"

    def obter_topicos(self) -> Dict[int, List[Tuple[str, float]]]:
        """Recupera dicionário de palavras e pesos de cada tópico."""
        try:
            todos = self.modelo_bertopic.get_topics()
            resultado: Dict[int, List[Tuple[str, float]]] = {}
            for top_id, palavras in todos.items():
                resultado[int(top_id)] = [(str(w), float(s)) for w, s in palavras]
            return resultado
        except Exception:
            return {}
