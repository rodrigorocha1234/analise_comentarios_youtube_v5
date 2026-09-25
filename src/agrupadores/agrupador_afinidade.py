from typing import List, Optional
import numpy as np
from sklearn.cluster import AffinityPropagation

from src.agrupadores.estrategia_agrupamento import EstrategiaAgrupamento


class AgrupadorAfinidade(EstrategiaAgrupamento):
    """Estratégia de agrupamento baseada em propagação de afinidade (exemplares)."""

    def __init__(self, damping: float = 0.8, random_state: int = 42) -> None:
        self.damping = damping
        self.random_state = random_state
        self.modelo = AffinityPropagation(damping=self.damping, random_state=self.random_state)
        self.rotulos: np.ndarray = np.array([], dtype=np.int32)

    def treinar_modelo(self, embeddings: np.ndarray, textos: Optional[List[str]] = None) -> np.ndarray:
        """Treina Affinity Propagation."""
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
        return "AffinityPropagation"
