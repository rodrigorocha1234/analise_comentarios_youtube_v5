from abc import ABC, abstractmethod
from src.dominio.evento_pipeline import EventoPipeline


class Observador(ABC):
    """Interface GoF Observer para recebimento desacoplado de eventos do pipeline."""

    @abstractmethod
    def notificar_evento(self, evento: EventoPipeline) -> bool:
        """Processa a notificação de um evento ocorrido no pipeline."""
        pass
