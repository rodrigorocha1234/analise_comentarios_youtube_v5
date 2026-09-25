import collections
from datetime import datetime, timedelta, timezone
import logging
import re
from typing import Dict, List, Optional, Tuple
import numpy as np

from src.dominio.agrupamento import Agrupamento
from src.dominio.registro_tendencia import RegistroTendencia
from src.processamento.tratador_stopword import TratadorStopword

logger = logging.getLogger(__name__)


class CalculadorTendencia:
    """Calcula Trend Topics temporais com palavras únicas e sem stopwords em três escopos."""

    def __init__(
        self,
        janelas_dias: List[int],
        tratador_stopword: Optional[TratadorStopword] = None,
    ) -> None:
        self.janelas_dias = janelas_dias
        self.tratador_stopword = tratador_stopword or TratadorStopword([])

    def calcular_score(
        self,
        vol_atual: int,
        vol_ant: int,
        cresc_rel: float,
        aceleracao: float,
        novidade: float,
    ) -> float:
        """Calcula score composto de tendência priorizando tópicos emergentes sobre volume estático."""
        fator_volume = float(np.log1p(vol_atual))
        score = (cresc_rel * 0.4) + (aceleracao * 0.25) + (novidade * 0.2) + (fator_volume * 0.15)
        return float(max(0.0, score))

    def filtrar_periodo(
        self, registros: List[Agrupamento], data_inicio: datetime, data_fim: datetime
    ) -> List[Agrupamento]:
        """Filtra itens cuja data de publicação se situa no intervalo delimitado."""
        resultado: List[Agrupamento] = []
        for r in registros:
            try:
                data_limpa = r.data_publicacao[:19].replace("Z", "")
                dt = datetime.fromisoformat(data_limpa).replace(tzinfo=timezone.utc)
                if data_inicio <= dt <= data_fim:
                    resultado.append(r)
            except Exception:
                continue
        return resultado

    def calcular_tendencias(
        self, agrupamentos: List[Agrupamento], data_referencia: str = ""
    ) -> List[RegistroTendencia]:
        """Calcula métricas e scores de tendências garantindo palavras únicas e sem stopwords."""
        if not agrupamentos:
            return []

        if data_referencia:
            dt_ref = datetime.fromisoformat(data_referencia).replace(tzinfo=timezone.utc)
        else:
            dt_ref = datetime.now(timezone.utc)

        data_coleta_str = dt_ref.strftime("%Y-%m-%d")
        tendencias: List[RegistroTendencia] = []

        # Define agrupamentos por escopo
        escopos_definidos: List[Tuple[str, str, List[Agrupamento]]] = []

        # 1. Por vídeo
        mapa_video: Dict[str, List[Agrupamento]] = collections.defaultdict(list)
        # 2. Por canal
        mapa_canal: Dict[str, List[Agrupamento]] = collections.defaultdict(list)
        # 3. Por canal + vídeo
        mapa_canal_video: Dict[str, List[Agrupamento]] = collections.defaultdict(list)

        for agr in agrupamentos:
            # Ignora ruído e termos nulos/vazios para tendências
            if agr.numero_cluster < 0 or not agr.topico:
                continue

            # Garante rigorosamente uma palavra única e sem pontuação
            topico_limpo = re.sub(r"[^\wÀ-ÿ]", "", agr.topico).strip().split()[0] if agr.topico else ""
            if not topico_limpo or self.tratador_stopword.verificar_stopword(topico_limpo):
                continue

            import dataclasses

            # Registra com o tópico validado como palavra única
            agr_ajustado = dataclasses.replace(agr, topico=topico_limpo)
            mapa_video[agr.id_video].append(agr_ajustado)
            mapa_canal[agr.id_canal].append(agr_ajustado)
            chave_cv = f"{agr.id_canal}#{agr.id_video}"
            mapa_canal_video[chave_cv].append(agr_ajustado)

        for vid_id, lista in mapa_video.items():
            escopos_definidos.append(("video", vid_id, lista))
        for can_id, lista in mapa_canal.items():
            escopos_definidos.append(("canal", can_id, lista))
        for cv_id, lista in mapa_canal_video.items():
            escopos_definidos.append(("canal_video", cv_id, lista))

        for escopo_nome, id_escopo, lista_docs in escopos_definidos:
            for janela in self.janelas_dias:
                dt_inicio_atual = dt_ref - timedelta(days=janela)
                dt_fim_atual = dt_ref

                dt_inicio_ant = dt_inicio_atual - timedelta(days=janela)
                dt_fim_ant = dt_inicio_atual

                docs_atuais = self.filtrar_periodo(lista_docs, dt_inicio_atual, dt_fim_atual)
                docs_anteriores = self.filtrar_periodo(lista_docs, dt_inicio_ant, dt_fim_ant)

                contagem_atual = collections.Counter([(d.numero_cluster, d.topico) for d in docs_atuais])
                contagem_anterior = collections.Counter([(d.numero_cluster, d.topico) for d in docs_anteriores])

                todos_topicos = set(contagem_atual.keys()) | set(contagem_anterior.keys())
                registros_janela: List[RegistroTendencia] = []

                for num_cluster, nome_topico in todos_topicos:
                    # Assegura que o tópico da trend seja uma palavra única
                    topico_final = re.sub(r"[^\wÀ-ÿ]", "", nome_topico).strip().split()[0] if nome_topico else ""
                    if not topico_final or self.tratador_stopword.verificar_stopword(topico_final):
                        continue

                    vol_atual = contagem_atual.get((num_cluster, nome_topico), 0)
                    vol_ant = contagem_anterior.get((num_cluster, nome_topico), 0)

                    cresc_abs = vol_atual - vol_ant
                    cresc_rel = cresc_abs / max(vol_ant, 1)
                    aceleracao = cresc_abs / float(janela)
                    novidade = 1.0 if vol_ant == 0 and vol_atual > 0 else (vol_atual / max(vol_atual + vol_ant, 1))

                    score = self.calcular_score(vol_atual, vol_ant, cresc_rel, aceleracao, novidade)

                    reg = RegistroTendencia(
                        escopo=escopo_nome,
                        identificador_escopo=id_escopo,
                        janela_dias=janela,
                        data_coleta=data_coleta_str,
                        topico=topico_final,
                        numero_cluster=num_cluster,
                        volume_atual=vol_atual,
                        volume_anterior=vol_ant,
                        crescimento_absoluto=cresc_abs,
                        crescimento_relativo=cresc_rel,
                        aceleracao=aceleracao,
                        novidade=novidade,
                        score_tendencia=score,
                        posicao_ranking=0,
                    )
                    registros_janela.append(reg)

                # Ordena pelo score decrescente para definir ranking
                registros_janela.sort(key=lambda x: x.score_tendencia, reverse=True)
                for pos, item in enumerate(registros_janela, start=1):
                    item_com_posicao = RegistroTendencia(
                        escopo=item.escopo,
                        identificador_escopo=item.identificador_escopo,
                        janela_dias=item.janela_dias,
                        data_coleta=item.data_coleta,
                        topico=item.topico,
                        numero_cluster=item.numero_cluster,
                        volume_atual=item.volume_atual,
                        volume_anterior=item.volume_anterior,
                        crescimento_absoluto=item.crescimento_absoluto,
                        crescimento_relativo=item.crescimento_relativo,
                        aceleracao=item.aceleracao,
                        novidade=item.novidade,
                        score_tendencia=item.score_tendencia,
                        posicao_ranking=pos,
                    )
                    tendencias.append(item_com_posicao)

        return tendencias
