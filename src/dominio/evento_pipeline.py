from dataclasses import dataclass, field
from typing import Dict


@dataclass(frozen=True)
class EventoPipeline:
    """Representa um evento disparado no ciclo de vida do pipeline para observadores."""

    nome_evento: str
    data_hora: str
    detalhes: Dict[str, str] = field(default_factory=dict)

    def obter_detalhe(self, chave: str, padrao: str = "") -> str:
        """Recupera um detalhe do evento por chave."""
        return self.detalhes.get(chave, padrao)
