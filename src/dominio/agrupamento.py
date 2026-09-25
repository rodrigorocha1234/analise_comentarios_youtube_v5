from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class Agrupamento:
    """Representa o resultado de associação de um documento a um cluster e tópico."""

    id_documento: str
    id_video: str
    id_canal: str
    id_comentario: str
    id_comentario_pai: str
    tipo: str
    numero_cluster: int
    topico: str
    probabilidade: float
    data_publicacao: str
    texto_original: str
    modelo: str
    versao_modelo: str

    def para_dicionario(self) -> Dict[str, str]:
        """Converte a entidade para dicionário."""
        return {
            "id_documento": self.id_documento,
            "id_video": self.id_video,
            "id_canal": self.id_canal,
            "id_comentario": self.id_comentario,
            "id_comentario_pai": self.id_comentario_pai,
            "tipo": self.tipo,
            "numero_cluster": str(self.numero_cluster),
            "topico": self.topico,
            "probabilidade": f"{self.probabilidade:.4f}",
            "data_publicacao": self.data_publicacao,
            "texto_original": self.texto_original,
            "modelo": self.modelo,
            "versao_modelo": self.versao_modelo,
        }
