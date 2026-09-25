from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class RegistroTendencia:
    """Representa a evolução temporal e score de tendência de um tópico."""

    escopo: str
    identificador_escopo: str
    janela_dias: int
    data_coleta: str
    topico: str
    numero_cluster: int
    volume_atual: int
    volume_anterior: int
    crescimento_absoluto: int
    crescimento_relativo: float
    aceleracao: float
    novidade: float
    score_tendencia: float
    posicao_ranking: int

    def para_dicionario(self) -> Dict[str, str]:
        """Converte o registro para dicionário."""
        return {
            "escopo": self.escopo,
            "identificador_escopo": self.identificador_escopo,
            "janela_dias": str(self.janela_dias),
            "data_coleta": self.data_coleta,
            "topico": self.topico,
            "numero_cluster": str(self.numero_cluster),
            "volume_atual": str(self.volume_atual),
            "volume_anterior": str(self.volume_anterior),
            "crescimento_absoluto": str(self.crescimento_absoluto),
            "crescimento_relativo": f"{self.crescimento_relativo:.4f}",
            "aceleracao": f"{self.aceleracao:.4f}",
            "novidade": f"{self.novidade:.4f}",
            "score_tendencia": f"{self.score_tendencia:.4f}",
            "posicao_ranking": str(self.posicao_ranking),
        }
