from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class Video:
    """Representa um vídeo do YouTube monitorado."""

    id_video: str
    id_canal: str
    titulo: str
    descricao: str
    data_publicacao: str
    data_coleta: str
    total_visualizacoes: int = 0
    total_curtidas: int = 0
    total_comentarios: int = 0

    def para_dicionario(self) -> Dict[str, str]:
        """Converte a entidade para dicionário."""
        return {
            "id_video": self.id_video,
            "id_canal": self.id_canal,
            "titulo": self.titulo,
            "descricao": self.descricao,
            "data_publicacao": self.data_publicacao,
            "data_coleta": self.data_coleta,
            "total_visualizacoes": str(self.total_visualizacoes),
            "total_curtidas": str(self.total_curtidas),
            "total_comentarios": str(self.total_comentarios),
        }
