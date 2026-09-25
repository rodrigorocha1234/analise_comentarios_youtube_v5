from dataclasses import dataclass, asdict
from typing import Dict


@dataclass(frozen=True)
class Canal:
    """Representa um canal do YouTube monitorado."""

    id_canal: str
    titulo: str
    descricao: str
    data_coleta: str
    total_inscritos: int = 0
    total_videos: int = 0

    def para_dicionario(self) -> Dict[str, str]:
        """Converte a entidade para dicionário."""
        return {
            "id_canal": self.id_canal,
            "titulo": self.titulo,
            "descricao": self.descricao,
            "data_coleta": self.data_coleta,
            "total_inscritos": str(self.total_inscritos),
            "total_videos": str(self.total_videos),
        }
