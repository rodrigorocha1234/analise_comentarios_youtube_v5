from typing import List, Optional
import numpy as np
from sklearn.cluster import MeanShift

from src.agrupadores.estrategia_agrupamento import EstrategiaAgrupamento


class AgrupadorMedia(EstrategiaAgrupamento):
    """Estratégia de agrupamento por deslocamento de média (Mean Shift)."""

    def __init__(self, bandwidth: Optional[float] = 0.8) -> None:
        self.bandwidth = bandwidth
        self.modelo = MeanShift(bandwidth=self.bandwidth)
        self.rotulos: np.ndarray = np.array([], dtype=np.int32)

    def treinar_modelo(self, embeddings: np.ndarray, textos: Optional[List[str]] = None) -> np.ndarray:
        """Treina Mean Shift nos embeddings."""
        if len(embeddings) == 0:
            return np.array([], dtype=np.int32)
        try:
            self.rotulos = self.modelo.fit_predict(embeddings)
        except Exception:
            self.rotulos = np.zeros(len(embeddings), dtype=np.int32)
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
        return "MeanShift"
