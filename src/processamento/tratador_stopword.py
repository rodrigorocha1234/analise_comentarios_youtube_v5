import logging
import re
from typing import List, Set
from spacy.lang.pt.stop_words import STOP_WORDS

logger = logging.getLogger(__name__)

STOPWORDS_EXTENDIDAS_PT: Set[str] = {
    # Contrações, preposições e pronomes informais
    "pra", "pras", "pro", "pros", "né", "ne", "vc", "vcs", "tb", "tbm", "tambem", "também",
    "q", "pq", "porque", "por que", "porquê", "por quê", "oq", "dq", "tipo", "ai", "aí",
    "la", "lá", "ta", "tá", "to", "tô", "ja", "já", "so", "só", "vou", "vai", "tao", "tão",
    "tem", "ter", "ser", "foi", "era", "eh", "é", "mano", "cara", "vei", "véi", "tmj",
    "vlw", "valeu", "obrigado", "obrigada", "show", "top", "mto", "mt", "muito", "muita",
    "muitos", "muitas", "pouco", "pouca", "poucos", "poucas", "mais", "menos",
    # Verbos auxiliares e formas comuns sem carga semântica
    "usando", "fazer", "fazendo", "fez", "faz", "ficou", "fica", "ficar", "ficando",
    "dar", "deu", "da", "dá", "dando", "acho", "acha", "achar", "achando", "ver", "viu",
    "vendo", "ve", "vê", "olha", "olhar", "deixar", "deixa", "deixou", "tinha",
    "pode", "podia", "poder", "consigo", "consegue", "conseguir", "quer", "queria", "querer",
    # Termos comuns de YouTube/redes sociais
    "video", "vídeo", "videos", "vídeos", "canal", "canais", "comentario", "comentário",
    "comentarios", "comentários", "inscrito", "inscritos", "inscrever", "like", "likes",
    "assistir", "assistindo", "assisti", "play", "postar", "postou",
    # Pronomes e advérbios adicionais
    "gente", "pessoal", "galera", "coisa", "coisas", "algo", "nada", "tudo", "todo", "toda",
    "todos", "todas", "outro", "outra", "outros", "outras", "mesmo", "mesma", "mesmos",
    "mesmas", "aqui", "ali", "agora", "depois", "sempre", "nunca", "ainda", "entao", "então",
    "assim", "bem", "mal", "melhor", "pior", "bom", "boa", "bons", "boas",
    # Interjeições, risos e cumprimentos
    "ola", "olá", "oi", "eae", "opa", "blz", "beleza", "belezinha", "haha", "hahaha",
    "hahahaha", "kkk", "kkkk", "kkkkk", "kkkkkk", "rs", "rsrs", "rsrsrs",
}


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
        """Une stopwords nativas do spaCy português com termos estendidos e configurados."""
        try:
            self.conjunto_stopwords = {p.lower() for p in STOP_WORDS}
        except Exception as erro:
            logger.warning("Falha ao obter stopwords padrão do spaCy: %s", erro)
            self.conjunto_stopwords = set()

        self.conjunto_stopwords.update(STOPWORDS_EXTENDIDAS_PT)

        for palavra in novas_palavras:
            if palavra and palavra.strip():
                self.conjunto_stopwords.add(palavra.strip().lower())
        return True

    def verificar_stopword(self, palavra: str) -> bool:
        """Verifica se um termo individual é stopword, numérico, risada ou inválido."""
        if not palavra:
            return True
        p_min = palavra.strip().lower()
        if len(p_min) < 3:
            return True
        if p_min.isdigit() or bool(re.match(r"^\d+$", p_min)):
            return True
        if bool(re.match(r"^(k{2,}|h[aeiou]{2,}|rs{2,})$", p_min)):
            return True
        if p_min in self.conjunto_stopwords:
            return True
        return False

    def filtrar_tokens(self, tokens: List[str]) -> List[str]:
        """Filtra uma lista de tokens removendo stopwords consolidadas e termos inválidos."""
        return [t for t in tokens if not self.verificar_stopword(t)]
