import logging
from typing import List, Set
from spacy.lang.pt.stop_words import STOP_WORDS

logger = logging.getLogger(__name__)


class TratadorStopword:
    """Gerencia a união de stopwords nativas do spaCy com stopwords adicionais do projeto."""

    def __init__(self, stopwords_adicionais: List[str]) -> None:
        self.stopwords_adicionais: List[str] = stopwords_adicionais
        self.conjunto_stopwords: Set[str] = set()
        self.adicionar_palavras(stopwords_adicionais)

    def obter_stopwords(self) -> Set[str]:
        """Retorna o conjunto consolidado de stopwords em minúsculo preservando acentos."""
        return set(self.conjunto_stopwords)

    def adicionar_palavras(self, novas_palavras: List[str]) -> bool:
        """Une stopwords nativas do spaCy português com palavras configuradas."""
        try:
            self.conjunto_stopwords = {p.lower() for p in STOP_WORDS}
        except Exception as erro:
            logger.warning("Falha ao obter stopwords padrão do spaCy: %s", erro)
            self.conjunto_stopwords = set()

        for palavra in novas_palavras:
            if palavra and palavra.strip():
                self.conjunto_stopwords.add(palavra.strip().lower())
        return True

    def filtrar_tokens(self, tokens: List[str]) -> List[str]:
        """Filtra uma lista de tokens removendo stopwords consolidadas."""
        return [t for t in tokens if t.lower() not in self.conjunto_stopwords]
