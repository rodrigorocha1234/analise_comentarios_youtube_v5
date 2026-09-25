from typing import List, Optional
import numpy as np
from sklearn.cluster import MiniBatchKMeans

from src.agrupadores.estrategia_agrupamento import EstrategiaAgrupamento


class AgrupadorMinibatch(EstrategiaAgrupamento):
    """Estratégia de agrupamento escalável usando MiniBatchKMeans."""

    def __init__(self, n_clusters: int = 10, batch_size: int = 256, random_state: int = 42) -> None:
        self.n_clusters = n_clusters
        self.batch_size = batch_size
        self.random_state = random_state
        self.modelo = MiniBatchKMeans(
            n_clusters=self.n_clusters,
            batch_size=self.batch_size,
            random_state=self.random_state,
            n_init="auto",
        )
        self.rotulos: np.ndarray = np.array([], dtype=np.int32)
        self.distancias: np.ndarray = np.array([], dtype=np.float32)

    def treinar_modelo(self, embeddings: np.ndarray, textos: Optional[List[str]] = None) -> np.ndarray:
        """Treina MiniBatchKMeans sobre a matriz de embeddings."""
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
        """Retorna os rótulos de cluster."""
        return self.rotulos

    def obter_probabilidades(self) -> np.ndarray:
        """Retorna probabilidades relativas aos centróides."""
        if len(self.distancias) == 0 or len(self.rotulos) == 0:
            return np.zeros(len(self.rotulos), dtype=np.float32)
        dists_escolhidas = self.distancias[np.arange(len(self.rotulos)), self.rotulos]
        probs = 1.0 / (1.0 + dists_escolhidas)
        return probs.astype(np.float32)

    def obter_nome(self) -> str:
        """Identificador textual do algoritmo."""
        return "MiniBatchKMeans"
