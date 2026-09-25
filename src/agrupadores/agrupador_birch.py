from typing import List, Optional
import numpy as np
from sklearn.cluster import Birch

from src.agrupadores.estrategia_agrupamento import EstrategiaAgrupamento


class AgrupadorBirch(EstrategiaAgrupamento):
    """Estratégia de agrupamento hierárquico por árvore balanceada BIRCH."""

    def __init__(self, n_clusters: int = 10, threshold: float = 0.5) -> None:
        self.n_clusters = n_clusters
        self.threshold = threshold
        self.modelo = Birch(n_clusters=self.n_clusters, threshold=self.threshold)
        self.rotulos: np.ndarray = np.array([], dtype=np.int32)

    def treinar_modelo(self, embeddings: np.ndarray, textos: Optional[List[str]] = None) -> np.ndarray:
        """Treina BIRCH na matriz vetorial."""
        if len(embeddings) == 0:
            return np.array([], dtype=np.int32)
        n_amostras = len(embeddings)
        self.modelo.n_clusters = min(self.n_clusters, n_amostras)
        self.rotulos = self.modelo.fit_predict(embeddings)
        return self.rotulos

    def obter_rotulos(self) -> np.ndarray:
        """Retorna os rótulos de cluster."""
        return self.rotulos

    def obter_probabilidades(self) -> np.ndarray:
        """Retorna probabilidades padrão."""
        if len(self.rotulos) == 0:
            return np.array([], dtype=np.float32)
        return np.ones(len(self.rotulos), dtype=np.float32)

    def obter_nome(self) -> str:
        """Identificador textual do algoritmo."""
        return "BIRCH"
