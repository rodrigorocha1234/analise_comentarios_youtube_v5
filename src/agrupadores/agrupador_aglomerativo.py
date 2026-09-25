from typing import List, Optional
import numpy as np
from sklearn.cluster import AgglomerativeClustering

from src.agrupadores.estrategia_agrupamento import EstrategiaAgrupamento


class AgrupadorAglomerativo(EstrategiaAgrupamento):
    """Estratégia de agrupamento hierárquico aglomerativo."""

    def __init__(self, n_clusters: int = 10, metric: str = "cosine", linkage: str = "average") -> None:
        self.n_clusters = n_clusters
        self.metric = metric
        self.linkage = linkage
        self.modelo = AgglomerativeClustering(n_clusters=self.n_clusters, metric=self.metric, linkage=self.linkage)
        self.rotulos: np.ndarray = np.array([], dtype=np.int32)

    def treinar_modelo(self, embeddings: np.ndarray, textos: Optional[List[str]] = None) -> np.ndarray:
        """Ajusta o agrupamento aglomerativo."""
        if len(embeddings) == 0:
            return np.array([], dtype=np.int32)
        n_amostras = len(embeddings)
        self.modelo.n_clusters = min(self.n_clusters, n_amostras)
        matriz = embeddings
        if self.metric == "cosine":
            normas = np.linalg.norm(matriz, axis=1, keepdims=True)
            matriz = np.where(normas <= 1e-6, 1e-7, matriz)
        self.rotulos = self.modelo.fit_predict(matriz)
        return self.rotulos

    def obter_rotulos(self) -> np.ndarray:
        """Retorna os rótulos de cluster."""
        return self.rotulos

    def obter_probabilidades(self) -> np.ndarray:
        """Retorna probabilidades padrão unitárias por não possuir função de densidade."""
        if len(self.rotulos) == 0:
            return np.array([], dtype=np.float32)
        return np.ones(len(self.rotulos), dtype=np.float32)

    def obter_nome(self) -> str:
        """Identificador textual do algoritmo."""
        return "Agglomerative"
