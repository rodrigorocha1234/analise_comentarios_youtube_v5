import collections
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Tuple
import pandas as pd

from src.armazenamento.armazenamento_objeto import ArmazenamentoObjeto
from src.dominio.agrupamento import Agrupamento
from src.dominio.configuracao_projeto import ConfiguracaoProjeto
from src.dominio.registro_tendencia import RegistroTendencia
from src.observadores.publicador_evento import PublicadorEvento
from src.processamento.tratador_stopword import TratadorStopword
from src.topicos.calculador_tendencia import CalculadorTendencia

logger = logging.getLogger(__name__)


class ServicoTendencia:
    """Orquestra o cálculo e persistência de Trend Topics temporais e nuvens de palavras."""

    def __init__(
        self,
        configuracao: ConfiguracaoProjeto,
        armazenamento: ArmazenamentoObjeto,
        publicador: PublicadorEvento,
    ) -> None:
        self.configuracao = configuracao
        self.armazenamento = armazenamento
        self.tratador_stopword = TratadorStopword(self.configuracao.stopwords_adicionais)
        self.calculador = CalculadorTendencia(
            self.configuracao.janelas_dias,
            tratador_stopword=self.tratador_stopword,
        )

    def persistir_tendencias(self, tendencias: List[RegistroTendencia], data_coleta: str) -> bool:
        """Separa e grava registros de tendência no MinIO de acordo com seus respectivos escopos."""
        df_todos = pd.DataFrame([t.para_dicionario() for t in tendencias])
        if df_todos.empty:
            return False

        # 1. Por vídeo
        df_vid = df_todos[df_todos["escopo"] == "video"]
        if not df_vid.empty:
            caminho_v = f"gold/tendencias_video/data_coleta={data_coleta}/tendencias.parquet"
            self.armazenamento.gravar_dataframe(caminho_v, df_vid)

        # 2. Por canal
        df_can = df_todos[df_todos["escopo"] == "canal"]
        if not df_can.empty:
            caminho_c = f"gold/tendencias_canal/data_coleta={data_coleta}/tendencias.parquet"
            self.armazenamento.gravar_dataframe(caminho_c, df_can)

        # 3. Por canal + vídeo
        df_cv = df_todos[df_todos["escopo"] == "canal_video"]
        if not df_cv.empty:
            caminho_cv = f"gold/tendencias_canal_video/data_coleta={data_coleta}/tendencias.parquet"
            self.armazenamento.gravar_dataframe(caminho_cv, df_cv)

        return True

    def gerar_nuvens(
        self, agrupamentos: List[Agrupamento], data_coleta: str
    ) -> Dict[str, Dict[str, int]]:
        """Extrai contagens de palavras para geração de nuvens semânticas em múltiplas granularidades."""
        stopwords = self.tratador_stopword.obter_stopwords()
        nuvem_global: collections.Counter = collections.Counter()
        nuvens_por_topico: Dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
        nuvens_por_canal: Dict[str, collections.Counter] = collections.defaultdict(collections.Counter)

        for agr in agrupamentos:
            palavras = agr.texto_original.lower().split()
            validas = [p.strip(".,!?\"':;()") for p in palavras if len(p) >= 3 and p not in stopwords]
            for v in validas:
                if v:
                    nuvem_global[v] += 1
                    nuvens_por_topico[agr.topico][v] += 1
                    nuvens_por_canal[agr.id_canal][v] += 1

        mapa_consolidado: Dict[str, Dict[str, int]] = {
            "global": dict(nuvem_global.most_common(100)),
        }
        for topico_nome, contador in nuvens_por_topico.items():
            mapa_consolidado[f"topico_{topico_nome}"] = dict(contador.most_common(50))
        for canal_id, contador in nuvens_por_canal.items():
            mapa_consolidado[f"canal_{canal_id}"] = dict(contador.most_common(50))

        caminho_nuvem = f"gold/nuvens_palavras/data_coleta={data_coleta}/frequencias.json"
        conteudo = json.dumps(mapa_consolidado, indent=2, ensure_ascii=False).encode("utf-8")
        self.armazenamento.gravar_objeto(caminho_nuvem, conteudo)

        return mapa_consolidado

    def executar_tendencias(self, agrupamentos: List[Agrupamento]) -> List[RegistroTendencia]:
        """Calcula todos os Trend Topics temporais e frequências para nuvens de palavras."""
        data_coleta = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        logger.info("Calculando Trend Topics temporais para a data %s.", data_coleta)

        tendencias = self.calculador.calcular_tendencias(agrupamentos, data_coleta)
        self.persistir_tendencias(tendencias, data_coleta)
        self.gerar_nuvens(agrupamentos, data_coleta)

        self.publicador.publicar_evento(
            "tendencias_calculadas", {"total_tendencias": str(len(tendencias))}
        )
        logger.info("Trend Topics calculados com sucesso: %d registros.", len(tendencias))

        return tendencias
