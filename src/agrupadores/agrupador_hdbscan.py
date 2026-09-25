from typing import List, Optional
import hdbscan
import numpy as np

from src.agrupadores.estrategia_agrupamento import EstrategiaAgrupamento


class AgrupadorHdbscan(EstrategiaAgrupamento):
    """Estratégia de agrupamento hierárquico baseado em densidade HDBSCAN."""

    def __init__(
        self,
        min_cluster_size: int = 15,
        min_samples: int = 5,
        metric: str = "euclidean",
        cluster_selection_method: str = "eom",
        prediction_data: bool = True,
    ) -> None:
        self.min_cluster_size = min_cluster_size
        self.min_samples = min_samples
        self.metric = metric
        self.cluster_selection_method = cluster_selection_method
        self.prediction_data = prediction_data
        self.modelo = hdbscan.HDBSCAN(
            min_cluster_size=self.min_cluster_size,
            min_samples=self.min_samples,
            metric=self.metric,
            cluster_selection_method=self.cluster_selection_method,
            prediction_data=self.prediction_data,
        )
        self.rotulos: np.ndarray = np.array([], dtype=np.int32)
        self.probabilidades: np.ndarray = np.array([], dtype=np.float32)

    def treinar_modelo(self, embeddings: np.ndarray, textos: Optional[List[str]] = None) -> np.ndarray:
        """Treina HDBSCAN calculando clusters e probabilidades nativas."""
        if len(embeddings) == 0:
            return np.array([], dtype=np.int32)
        n_amostras = len(embeddings)
        tamanho_min = max(2, min(self.min_cluster_size, n_amostras // 2))
        self.modelo.min_cluster_size = tamanho_min
        self.modelo.min_samples = max(1, min(self.min_samples, tamanho_min))
        self.modelo.fit(embeddings)
        self.rotulos = self.modelo.labels_
        self.probabilidades = self.modelo.probabilities_.astype(np.float32)
        return self.rotulos

    def obter_rotulos(self) -> np.ndarray:
        """Retorna os rótulos de cluster atribuídos pelo HDBSCAN."""
        return self.rotulos

    def obter_probabilidades(self) -> np.ndarray:
        """Retorna as probabilidades nativas calculadas pelo HDBSCAN."""
        return self.probabilidades

    def obter_nome(self) -> str:
        """Identificador textual do algoritmo."""
        return "HDBSCAN"
