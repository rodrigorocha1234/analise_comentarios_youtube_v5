import collections
import logging
import re
from typing import Dict, List, Optional, Tuple
import numpy as np

from src.dominio.topico import Topico
from src.processamento.tratador_stopword import TratadorStopword

logger = logging.getLogger(__name__)


class NomeadorTopico:
    """Nomeia tópicos atribuindo rigorosamente UMA palavra representativa única sem stopwords."""

    def __init__(self, tratador_stopword: TratadorStopword) -> None:
        self.tratador_stopword = tratador_stopword

    def extrair_candidatas(self, textos: List[str]) -> List[str]:
        """Extrai palavras candidatas de uma lista de textos removendo pontuação, números e stopwords."""
        palavras_validas: List[str] = []
        for texto in textos:
            # Preserva caracteres acentuados latinos [a-zA-ZÀ-ÿ], rejeita números e símbolos
            tokens = re.findall(r"\b[a-zA-ZÀ-ÿ]{3,}\b", texto)
            for t in tokens:
                if not self.tratador_stopword.verificar_stopword(t):
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
            if self.tratador_stopword.verificar_stopword(p_min):
                continue
            freq_f = palavras_fundo.get(p_min, 1)
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
        """Gera um Topico com exatamente UMA palavra representativa única sem stopwords."""
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

        # 1. Avalia candidatos do BERTopic se disponíveis
        if palavras_bertopic and len(palavras_bertopic) > 0:
            for cand, score in palavras_bertopic:
                # Remove caracteres especiais e seleciona a primeira palavra
                cand_limpa = re.sub(r"[^\wÀ-ÿ]", "", cand).strip().split()[0] if cand else ""
                if cand_limpa and not self.tratador_stopword.verificar_stopword(cand_limpa):
                    if not palavra_escolhida:
                        palavra_escolhida = cand_limpa
                        score_maximo = float(score)
                    if cand_limpa not in palavras_aux:
                        palavras_aux.append(cand_limpa)
                if len(palavras_aux) >= 10:
                    break

        # 2. Se não houver do BERTopic ou todos forem stopwords, usa ranking c-TF-IDF local
        if not palavra_escolhida:
            candidatas = self.extrair_candidatas(textos_cluster)
            ranking = self.calcular_relevancia(candidatas, palavras_fundo)
            for r_palavra, r_score in ranking:
                r_limpa = re.sub(r"[^\wÀ-ÿ]", "", r_palavra).strip().split()[0] if r_palavra else ""
                if r_limpa and not self.tratador_stopword.verificar_stopword(r_limpa):
                    if not palavra_escolhida:
                        palavra_escolhida = r_limpa
                        score_maximo = r_score
                    if r_limpa not in palavras_aux:
                        palavras_aux.append(r_limpa)
                if len(palavras_aux) >= 10:
                    break

        # 3. Fallback de garantia sem stopwords
        if not palavra_escolhida:
            palavra_escolhida = f"Tema_{numero_cluster}"
            score_maximo = 1.0
            palavras_aux = [palavra_escolhida]

        # Garante estritamente UMA palavra única sem espaços
        palavra_final = re.sub(r"[^\wÀ-ÿ]", "", palavra_escolhida).strip().split()[0]

        return Topico(
            numero_cluster=numero_cluster,
            palavra_representativa=palavra_final,
            palavras_auxiliares=palavras_aux,
            quantidade_documentos=len(textos_cluster),
            score_relevancia=score_maximo,
        )
