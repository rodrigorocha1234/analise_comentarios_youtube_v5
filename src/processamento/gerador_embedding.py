import logging
from typing import List
import numpy as np
import spacy
from spacy.language import Language

logger = logging.getLogger(__name__)


class GeradorEmbedding:
    """Gera matriz densa de embeddings semânticos exclusivamente a partir de modelos spaCy."""

    def __init__(self, modelo_spacy: str = "pt_core_news_md", lote_processamento: int = 256) -> None:
        self.modelo_spacy = modelo_spacy
        self.lote_processamento = lote_processamento
        try:
            self.nlp: Language = spacy.load(modelo_spacy)
        except Exception:
            logger.warning("Falha ao carregar %s. Usando pt_core_news_sm com fallback...", modelo_spacy)
            self.nlp = spacy.load("pt_core_news_sm")
        self.dimensao_vetor: int = self.obter_dimensao()
        self.validar_modelo()

    def obter_dimensao(self) -> int:
        """Determina a dimensão vetorial do modelo spaCy carregado."""
        exemplo = self.nlp("palavra")
        if exemplo.has_vector and exemplo.vector.shape[0] > 0:
            return int(exemplo.vector.shape[0])
        return 300

    def validar_modelo(self) -> bool:
        """Verifica se o pipeline spaCy possui vetores densos válidos."""
        doc_teste = self.nlp("teste semântico de agrupamento")
        if not doc_teste.has_vector:
            logger.warning(
                "O modelo spaCy %s não possui vetores densos nativos configurados. Embeddings podem conter zeros.",
                self.modelo_spacy,
            )
            return False
        logger.info("Modelo spaCy %s validado com dimensões: %d", self.modelo_spacy, self.dimensao_vetor)
        return True

    def gerar_embeddings(self, textos: List[str]) -> np.ndarray:
        """Gera matriz NumPy de embeddings densos processando textos em lote via nlp.pipe."""
        matriz_vetores: List[np.ndarray] = []
        vetor_minimo = np.full(self.dimensao_vetor, 1e-7, dtype=np.float32)

        for doc in self.nlp.pipe(textos, batch_size=self.lote_processamento):
            if doc.has_vector and float(np.linalg.norm(doc.vector)) > 1e-6:
                matriz_vetores.append(doc.vector.astype(np.float32))
            else:
                matriz_vetores.append(vetor_minimo)

        matriz_final = np.vstack(matriz_vetores)
        # Proteção extra garantindo que nenhuma linha tenha norma estritamente zero
        normas = np.linalg.norm(matriz_final, axis=1, keepdims=True)
        return np.where(normas == 0, 1e-7, matriz_final).astype(np.float32)

