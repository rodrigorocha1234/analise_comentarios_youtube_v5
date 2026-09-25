import logging
import os
from typing import Dict
from urllib.parse import urlencode
import requests
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class ColetorYoutube:
    """Cliente base para chamadas HTTP seguras à YouTube Data API v3."""

    def __init__(self, chave_api: str = "") -> None:
        load_dotenv()
        self.chave_api: str = chave_api or self.obter_chave()
        self.url_base: str = "https://www.googleapis.com/youtube/v3"

    def obter_chave(self) -> str:
        """Obtém a chave da API do YouTube a partir do ambiente."""
        chave = os.getenv("YOUTUBE_API_KEY", "")
        if not chave:
            logger.warning("Variável YOUTUBE_API_KEY não encontrada no ambiente.")
        return chave

    def executar_requisicao(self, recurso: str, parametros: Dict[str, str]) -> Dict[str, object]:
        """Executa requisição GET autenticada na API do YouTube."""
        if not self.chave_api:
            raise ValueError("Chave de API do YouTube não configurada.")

        parametros_completos = dict(parametros)
        parametros_completos["key"] = self.chave_api
        url = f"{self.url_base}/{recurso}?{urlencode(parametros_completos)}"

        resposta = requests.get(url, timeout=30)
        if resposta.status_code != 200:
            logger.error("Erro na API do YouTube (%d): %s", resposta.status_code, resposta.text)
            raise RuntimeError(f"Erro na API do YouTube ({resposta.status_code}): {resposta.text}")

        dados = resposta.json()
        if isinstance(dados, dict):
            return dados
        return {}
