from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class Resposta:
    """Representa uma resposta a um comentário pai no YouTube."""

    id_resposta: str
    id_comentario_pai: str
    id_video: str
    id_canal: str
    texto: str
    autor: str
    data_publicacao: str
    data_atualizacao_youtube: str
    data_coleta: str
    hash_conteudo: str
    versao: int
    ativo: bool

    def para_dicionario(self) -> Dict[str, str]:
        """Converte a entidade para dicionário."""
        return {
            "id_resposta": self.id_resposta,
            "id_comentario_pai": self.id_comentario_pai,
            "id_video": self.id_video,
            "id_canal": self.id_canal,
            "texto": self.texto,
            "autor": self.autor,
            "data_publicacao": self.data_publicacao,
            "data_atualizacao_youtube": self.data_atualizacao_youtube,
            "data_coleta": self.data_coleta,
            "hash_conteudo": self.hash_conteudo,
            "versao": str(self.versao),
            "ativo": "true" if self.ativo else "false",
        }
