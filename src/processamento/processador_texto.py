import logging
import re
from datetime import datetime, timezone
from typing import List, Tuple
import spacy
from spacy.language import Language

from src.dominio.comentario import Comentario
from src.dominio.documento_processado import DocumentoProcessado
from src.dominio.resposta import Resposta
from src.processamento.tratador_stopword import TratadorStopword

logger = logging.getLogger(__name__)


class ProcessadorTexto:
    """Realiza limpeza, normalização e processamento linguístico em lote com spaCy."""

    def __init__(self, tratador_stopword: TratadorStopword, modelo_spacy: str = "pt_core_news_md") -> None:
        self.tratador_stopword = tratador_stopword
        self.modelo_spacy = modelo_spacy
        try:
            self.nlp: Language = spacy.load(modelo_spacy)
        except Exception:
            logger.warning("Modelo %s não carregado diretamente. Tentando carregar pt_core_news_sm...", modelo_spacy)
            self.nlp = spacy.load("pt_core_news_sm")

    def limpar_texto(self, texto_bruto: str) -> str:
        """Remove URLs, espaços redundantes e normaliza quebras preservando acentuação Unicode."""
        if not texto_bruto:
            return ""
        sem_url = re.sub(r"https?://\S+|www\.\S+", "", texto_bruto)
        sem_espacos = re.sub(r"\s+", " ", sem_url)
        return sem_espacos.strip()

    def extrair_lemas(self, doc_spacy: spacy.tokens.Doc) -> str:
        """Extrai lemas não-stopword preservando grafia original dos acentos."""
        stopwords = self.tratador_stopword.obter_stopwords()
        lemas: List[str] = []
        for token in doc_spacy:
            if token.is_punct or token.is_space:
                continue
            texto_token = token.text.strip()
            if not texto_token or len(texto_token) < 2:
                continue
            if texto_token.lower() in stopwords:
                continue
            lema = token.lemma_.strip()
            if lema and lema.lower() not in stopwords:
                lemas.append(lema)
            else:
                lemas.append(texto_token)
        return " ".join(lemas)

    def processar_lote(
        self,
        comentarios: List[Comentario],
        respostas: List[Resposta],
        tamanho_lote: int = 256,
    ) -> List[DocumentoProcessado]:
        """Processa comentários e respostas em lotes via nlp.pipe gerando documentos normalizados."""
        itens_entrada: List[Tuple[str, str, str, str, str, str, str, str]] = []
        data_proc = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        for c in comentarios:
            itens_entrada.append(
                (
                    f"doc_c_{c.id_comentario}_{c.versao}",
                    c.id_comentario,
                    c.id_video,
                    c.id_canal,
                    "",
                    "COMENTARIO",
                    c.texto,
                    c.data_publicacao,
                )
            )

        for r in respostas:
            itens_entrada.append(
                (
                    f"doc_r_{r.id_resposta}_{r.versao}",
                    r.id_resposta,
                    r.id_video,
                    r.id_canal,
                    r.id_comentario_pai,
                    "RESPOSTA",
                    r.texto,
                    r.data_publicacao,
                )
            )

        textos_limpos = [self.limpar_texto(item[6]) for item in itens_entrada]
        documentos: List[DocumentoProcessado] = []

        for info, doc in zip(itens_entrada, self.nlp.pipe(textos_limpos, batch_size=tamanho_lote)):
            id_doc, id_com, id_vid, id_can, id_pai, tipo, texto_orig, data_pub = info
            texto_limpo = doc.text
            tokens_lemas = self.extrair_lemas(doc)

            doc_proc = DocumentoProcessado(
                id_documento=id_doc,
                id_comentario=id_com,
                id_video=id_vid,
                id_canal=id_can,
                id_comentario_pai=id_pai,
                tipo=tipo,
                texto_original=texto_orig,
                texto_limpo=texto_limpo,
                tokens_lematizados=tokens_lemas,
                data_publicacao=data_pub,
                data_processamento=data_proc,
            )
            documentos.append(doc_proc)

        return documentos
