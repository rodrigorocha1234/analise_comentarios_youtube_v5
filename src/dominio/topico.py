from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(frozen=True)
class Topico:
    """Representa um tópico descoberto pelo agrupamento com uma palavra representativa."""

    numero_cluster: int
    palavra_representativa: str
    palavras_auxiliares: List[str] = field(default_factory=list)
    quantidade_documentos: int = 0
    score_relevancia: float = 0.0

    def para_dicionario(self) -> Dict[str, str]:
        """Converte a entidade para dicionário."""
        return {
            "numero_cluster": str(self.numero_cluster),
            "palavra_representativa": self.palavra_representativa,
            "palavras_auxiliares": ",".join(self.palavras_auxiliares),
            "quantidade_documentos": str(self.quantidade_documentos),
            "score_relevancia": f"{self.score_relevancia:.4f}",
        }
