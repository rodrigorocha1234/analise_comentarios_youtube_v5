from typing import List, Optional
import numpy as np
from sklearn.cluster import KMeans

from src.agrupadores.estrategia_agrupamento import EstrategiaAgrupamento


class AgrupadorKmeans(EstrategiaAgrupamento):
    """Estratégia de agrupamento usando KMeans sobre embeddings spaCy."""

    def __init__(self, n_clusters: int = 10, random_state: int = 42) -> None:
        self.n_clusters = n_clusters
        self.random_state = random_state
        self.modelo = KMeans(n_clusters=self.n_clusters, random_state=self.random_state, n_init="auto")
        self.rotulos: np.ndarray = np.array([], dtype=np.int32)
        self.distancias: np.ndarray = np.array([], dtype=np.float32)

    def treinar_modelo(self, embeddings: np.ndarray, textos: Optional[List[str]] = None) -> np.ndarray:
        """Ajusta o KMeans nos embeddings spaCy e calcula rótulos."""
        if len(embeddings) == 0:
            return np.array([], dtype=np.int32)
        n_amostras = len(embeddings)
        n_c = min(self.n_clusters, n_amostras)
        if n_c != self.modelo.n_clusters:
            self.modelo.n_clusters = n_c
        self.rotulos = self.modelo.fit_predict(embeddings)
        self.distancias = self.modelo.transform(embeddings)
        return self.rotulos

    def obter_rotulos(self) -> np.ndarray:
        """Retorna os rótulos de cluster atribuídos aos documentos."""
        return self.rotulos

    def obter_probabilidades(self) -> np.ndarray:
        """Calcula probabilidades normalizadas baseadas no inverso da distância ao centróide."""
        if len(self.distancias) == 0 or len(self.rotulos) == 0:
            return np.zeros(len(self.rotulos), dtype=np.float32)
        dists_escolhidas = self.distancias[np.arange(len(self.rotulos)), self.rotulos]
        probs = 1.0 / (1.0 + dists_escolhidas)
        return probs.astype(np.float32)

    def obter_nome(self) -> str:
        """Identificador textual do algoritmo."""
        return "KMeans"
