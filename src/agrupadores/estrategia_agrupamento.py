from abc import ABC, abstractmethod
from typing import List, Optional
import numpy as np


class EstrategiaAgrupamento(ABC):
    """Interface abstrata GoF Strategy para algoritmos de agrupamento não supervisionado."""

    @abstractmethod
    def treinar_modelo(self, embeddings: np.ndarray, textos: Optional[List[str]] = None) -> np.ndarray:
        """Executa o treinamento do modelo e retorna o array de rótulos dos clusters."""
        pass

    @abstractmethod
    def obter_rotulos(self) -> np.ndarray:
        """Retorna os rótulos de cluster atribuídos aos documentos treinados."""
        pass

    @abstractmethod
    def obter_probabilidades(self) -> np.ndarray:
        """Retorna probabilidades de pertencimento quando suportadas pelo modelo ou array vazio."""
        pass

    @abstractmethod
    def obter_nome(self) -> str:
        """Retorna o identificador amigável da estratégia em português."""
        pass
