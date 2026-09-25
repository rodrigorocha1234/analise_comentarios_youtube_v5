import logging
from datetime import datetime, timezone
from typing import Dict, List
from src.dominio.evento_pipeline import EventoPipeline
from src.observadores.observador import Observador

logger = logging.getLogger(__name__)


class PublicadorEvento:
    """Entidade observável GoF Observer responsável por gerenciar e notificar observadores."""

    def __init__(self) -> None:
        self.observadores: List[Observador] = []

    def registrar_observador(self, observador: Observador) -> bool:
        """Adiciona um observador à lista de inscritos."""
        if observador not in self.observadores:
            self.observadores.append(observador)
            return True
        return False

    def remover_observador(self, observador: Observador) -> bool:
        """Remove um observador previamente registrado."""
        if observador in self.observadores:
            self.observadores.remove(observador)
            return True
        return False

    def publicar_evento(self, nome_evento: str, detalhes: Dict[str, str]) -> None:
        """Cria e distribui o evento informado para todos os observadores cadastrados."""
        data_hora = datetime.now(timezone.utc).isoformat()
        evento = EventoPipeline(nome_evento=nome_evento, data_hora=data_hora, detalhes=detalhes)
        for obs in self.observadores:
            try:
                obs.notificar_evento(evento)
            except Exception as erro:
                logger.error("Erro ao notificar observador %s sobre evento %s: %s", type(obs).__name__, nome_evento, erro)
