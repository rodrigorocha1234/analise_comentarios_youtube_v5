from typing import List, Optional
import numpy as np
from sklearn.cluster import SpectralClustering

from src.agrupadores.estrategia_agrupamento import EstrategiaAgrupamento


class AgrupadorEspectral(EstrategiaAgrupamento):
    """Estratégia de agrupamento espectral sobre grafo de similaridades."""

    def __init__(self, n_clusters: int = 10, random_state: int = 42) -> None:
        self.n_clusters = n_clusters
        self.random_state = random_state
        self.modelo = SpectralClustering(
            n_clusters=self.n_clusters,
            random_state=self.random_state,
            affinity="nearest_neighbors",
        )
        self.rotulos: np.ndarray = np.array([], dtype=np.int32)

    def treinar_modelo(self, embeddings: np.ndarray, textos: Optional[List[str]] = None) -> np.ndarray:
        """Treina Spectral Clustering nos embeddings."""
        if len(embeddings) == 0:
            return np.array([], dtype=np.int32)
        n_amostras = len(embeddings)
        self.modelo.n_clusters = min(self.n_clusters, n_amostras)
        try:
            self.rotulos = self.modelo.fit_predict(embeddings)
        except Exception:
            self.modelo.affinity = "rbf"
            try:
                self.rotulos = self.modelo.fit_predict(embeddings)
            except Exception:
                self.rotulos = np.zeros(len(embeddings), dtype=np.int32)
        return self.rotulos

    def obter_rotulos(self) -> np.ndarray:
        """Retorna os rótulos de cluster."""
        return self.rotulos

    def obter_probabilidades(self) -> np.ndarray:
        """Retorna probabilidades padrão unitárias."""
        if len(self.rotulos) == 0:
            return np.array([], dtype=np.float32)
        return np.ones(len(self.rotulos), dtype=np.float32)

    def obter_nome(self) -> str:
        """Identificador textual do algoritmo."""
        return "Spectral"
