from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class MetricaModelo:
    """Métricas de avaliação e desempenho de um modelo de agrupamento."""

    algoritmo: str
    quantidade_clusters: int
    quantidade_documentos: int
    percentual_ruido: float
    silhouette_score: float
    davies_bouldin_score: float
    calinski_harabasz_score: float
    tamanho_medio_cluster: float
    maior_cluster: int
    menor_cluster: int
    tempo_treinamento: float
    tempo_inferencia: float

    def para_dicionario(self) -> Dict[str, str]:
        """Converte as métricas para dicionário."""
        return {
            "algoritmo": self.algoritmo,
            "quantidade_clusters": str(self.quantidade_clusters),
            "quantidade_documentos": str(self.quantidade_documentos),
            "percentual_ruido": f"{self.percentual_ruido:.4f}",
            "silhouette_score": f"{self.silhouette_score:.4f}",
            "davies_bouldin_score": f"{self.davies_bouldin_score:.4f}",
            "calinski_harabasz_score": f"{self.calinski_harabasz_score:.4f}",
            "tamanho_medio_cluster": f"{self.tamanho_medio_cluster:.2f}",
            "maior_cluster": str(self.maior_cluster),
            "menor_cluster": str(self.menor_cluster),
            "tempo_treinamento": f"{self.tempo_treinamento:.4f}",
            "tempo_inferencia": f"{self.tempo_inferencia:.4f}",
        }
