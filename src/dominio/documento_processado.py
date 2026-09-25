from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class DocumentoProcessado:
    """Representa um documento textual processado e normalizado."""

    id_documento: str
    id_comentario: str
    id_video: str
    id_canal: str
    id_comentario_pai: str
    tipo: str
    texto_original: str
    texto_limpo: str
    tokens_lematizados: str
    data_publicacao: str
    data_processamento: str

    def para_dicionario(self) -> Dict[str, str]:
        """Converte a entidade para dicionário."""
        return {
            "id_documento": self.id_documento,
            "id_comentario": self.id_comentario,
            "id_video": self.id_video,
            "id_canal": self.id_canal,
            "id_comentario_pai": self.id_comentario_pai,
            "tipo": self.tipo,
            "texto_original": self.texto_original,
            "texto_limpo": self.texto_limpo,
            "tokens_lematizados": self.tokens_lematizados,
            "data_publicacao": self.data_publicacao,
            "data_processamento": self.data_processamento,
        }
