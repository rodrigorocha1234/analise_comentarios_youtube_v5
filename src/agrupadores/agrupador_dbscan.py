from typing import List, Optional
import numpy as np
from sklearn.cluster import DBSCAN

from src.agrupadores.estrategia_agrupamento import EstrategiaAgrupamento


class AgrupadorDbscan(EstrategiaAgrupamento):
    """Estratégia de agrupamento baseada em densidade DBSCAN."""

    def __init__(self, eps: float = 0.5, min_samples: int = 5, metric: str = "cosine") -> None:
        self.eps = eps
        self.min_samples = min_samples
        self.metric = metric
        self.modelo = DBSCAN(eps=self.eps, min_samples=self.min_samples, metric=self.metric)
        self.rotulos: np.ndarray = np.array([], dtype=np.int32)

    def treinar_modelo(self, embeddings: np.ndarray, textos: Optional[List[str]] = None) -> np.ndarray:
        """Ajusta o DBSCAN nos embeddings."""
        matriz = embeddings
        if self.metric == "cosine":
            normas = np.linalg.norm(matriz, axis=1, keepdims=True)
            matriz = np.where(normas <= 1e-6, 1e-7, matriz)
        self.rotulos = self.modelo.fit_predict(matriz)
        return self.rotulos

    def obter_rotulos(self) -> np.ndarray:
        """Retorna os rótulos de cluster identificados pelo DBSCAN (-1 indica ruído)."""
        return self.rotulos

    def obter_probabilidades(self) -> np.ndarray:
        """DBSCAN não fornece probabilidades contínuas; atribui 1.0 para núcleos e 0.0 para ruído."""
        if len(self.rotulos) == 0:
            return np.array([], dtype=np.float32)
        probs = np.where(self.rotulos >= 0, 1.0, 0.0)
        return probs.astype(np.float32)

    def obter_nome(self) -> str:
        """Identificador textual do algoritmo."""
        return "DBSCAN"
