from typing import List, Optional
import numpy as np
from sklearn.mixture import GaussianMixture

from src.agrupadores.estrategia_agrupamento import EstrategiaAgrupamento


class AgrupadorGaussiano(EstrategiaAgrupamento):
    """Estratégia de agrupamento usando modelos de misturas gaussianas (GMM)."""

    def __init__(self, n_components: int = 10, random_state: int = 42) -> None:
        self.n_components = n_components
        self.random_state = random_state
        self.reg_covar = 1e-2
        self.modelo = GaussianMixture(
            n_components=self.n_components,
            random_state=self.random_state,
            reg_covar=self.reg_covar,
            covariance_type="diag",
        )
        self.rotulos: np.ndarray = np.array([], dtype=np.int32)
        self.probabilidades: np.ndarray = np.array([], dtype=np.float32)

    def treinar_modelo(self, embeddings: np.ndarray, textos: Optional[List[str]] = None) -> np.ndarray:
        """Ajusta o GMM nos embeddings com regularização de covariância e obtém probabilidades."""
        if len(embeddings) == 0:
            return np.array([], dtype=np.int32)
        n_amostras = len(embeddings)
        self.modelo.n_components = min(self.n_components, n_amostras)
        dados = embeddings.astype(np.float64)

        try:
            self.modelo.fit(dados)
            matriz_probs = self.modelo.predict_proba(dados)
        except Exception:
            self.modelo.covariance_type = "diag"
            self.modelo.reg_covar = 1e-1
            self.modelo.fit(dados)
            matriz_probs = self.modelo.predict_proba(dados)

        self.rotulos = np.argmax(matriz_probs, axis=1)
        self.probabilidades = np.max(matriz_probs, axis=1).astype(np.float32)
        return self.rotulos

    def obter_rotulos(self) -> np.ndarray:
        """Retorna os rótulos de cluster."""
        return self.rotulos

    def obter_probabilidades(self) -> np.ndarray:
        """Retorna a probabilidade máxima da componente gaussiana associada."""
        return self.probabilidades

    def obter_nome(self) -> str:
        """Identificador textual do algoritmo."""
        return "GaussianMixture"
