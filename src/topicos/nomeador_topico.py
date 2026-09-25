import collections
import logging
import re
from typing import Dict, List, Optional, Set, Tuple
import numpy as np

from src.dominio.topico import Topico
from src.processamento.tratador_stopword import TratadorStopword

logger = logging.getLogger(__name__)


class NomeadorTopico:
    """Nomeia tópicos atribuindo exatamente UMA palavra representativa preservando acentos Unicode."""

    def __init__(self, tratador_stopword: TratadorStopword) -> None:
        self.tratador_stopword = tratador_stopword

    def extrair_candidatas(self, textos: List[str]) -> List[str]:
        """Extrai palavras candidatas de uma lista de textos removendo pontuação e stopwords."""
        stopwords = self.tratador_stopword.obter_stopwords()
        palavras_validas: List[str] = []
        for texto in textos:
            # Preserva caracteres acentuados latinos [a-zA-ZÀ-ÿ]
            tokens = re.findall(r"\b[a-zA-ZÀ-ÿ]{3,}\b", texto)
            for t in tokens:
                p_min = t.lower()
                if p_min not in stopwords:
                    palavras_validas.append(t)
        return palavras_validas

    def calcular_relevancia(
        self, palavras_cluster: List[str], palavras_fundo: collections.Counter
    ) -> List[Tuple[str, float]]:
        """Calcula relevância de palavras candidatas via contraste de frequência com o corpus."""
        contador_cluster = collections.Counter([p.lower() for p in palavras_cluster])
        total_cluster = sum(contador_cluster.values()) or 1
        total_fundo = sum(palavras_fundo.values()) or 1

        mapa_grafia: Dict[str, str] = {}
        for p in palavras_cluster:
            minusc = p.lower()
            if minusc not in mapa_grafia:
                mapa_grafia[minusc] = p

        scores: List[Tuple[str, float]] = []
        for p_min, freq_c in contador_cluster.items():
            freq_f = palavras_fundo.get(p_min, 1)
            # TF-IDF aproximado por contraste de proporção
            tf = freq_c / total_cluster
            idf = np.log((total_fundo + 1.0) / (freq_f + 1.0)) + 1.0
            relevancia = float(tf * idf)
            palavra_original = mapa_grafia.get(p_min, p_min)
            scores.append((palavra_original, relevancia))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores

    def nomear_topico(
        self,
        numero_cluster: int,
        textos_cluster: List[str],
        palavras_fundo: collections.Counter,
        palavras_bertopic: Optional[List[Tuple[str, float]]] = None,
    ) -> Topico:
        """Gera um Topico com exatamente UMA palavra representativa e palavras auxiliares."""
        if numero_cluster == -1:
            return Topico(
                numero_cluster=-1,
                palavra_representativa="Ruído",
                palavras_auxiliares=["outliers", "dispersos"],
                quantidade_documentos=len(textos_cluster),
                score_relevancia=0.0,
            )

        palavras_aux: List[str] = []
        palavra_escolhida = ""
        score_maximo = 0.0

        if palavras_bertopic and len(palavras_bertopic) > 0:
            stopwords = self.tratador_stopword.obter_stopwords()
            for cand, score in palavras_bertopic:
                cand_limpa = re.sub(r"[^\wÀ-ÿ]", "", cand).strip()
                if cand_limpa and " " not in cand_limpa and cand_limpa.lower() not in stopwords:
                    if not palavra_escolhida:
                        palavra_escolhida = cand_limpa
                        score_maximo = score
                    palavras_aux.append(cand_limpa)
                if len(palavras_aux) >= 10:
                    break

        if not palavra_escolhida:
            candidatas = self.extrair_candidatas(textos_cluster)
            ranking = self.calcular_relevancia(candidatas, palavras_fundo)
            if ranking:
                palavra_escolhida = ranking[0][0]
                score_maximo = ranking[0][1]
                palavras_aux = [r[0] for r in ranking[:10]]
            else:
                palavra_escolhida = f"Tópico_{numero_cluster}"
                score_maximo = 1.0
                palavras_aux = [palavra_escolhida]

        # Garante exatamente UMA palavra sem espaços e preservando acentos
        palavra_final = palavra_escolhida.split()[0].strip()

        return Topico(
            numero_cluster=numero_cluster,
            palavra_representativa=palavra_final,
            palavras_auxiliares=palavras_aux,
            quantidade_documentos=len(textos_cluster),
            score_relevancia=score_maximo,
        )
