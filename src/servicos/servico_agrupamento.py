import collections
import logging
import time
from datetime import datetime, timezone
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
from sklearn.metrics import calinski_harabasz_score, davies_bouldin_score, silhouette_score

from src.agrupadores.agrupador_bertopic import AgrupadorBertopic
from src.armazenamento.armazenamento_objeto import ArmazenamentoObjeto
from src.dominio.agrupamento import Agrupamento
from src.dominio.comentario import Comentario
from src.dominio.configuracao_projeto import ConfiguracaoProjeto
from src.dominio.documento_processado import DocumentoProcessado
from src.dominio.metrica_modelo import MetricaModelo
from src.dominio.resposta import Resposta
from src.dominio.topico import Topico
from src.fabricas.fabrica_agrupador import FabricaAgrupador
from src.observadores.publicador_evento import PublicadorEvento
from src.processamento.gerador_embedding import GeradorEmbedding
from src.processamento.processador_texto import ProcessadorTexto
from src.processamento.tratador_stopword import TratadorStopword
from src.topicos.associador_comentario import AssociadorComentario
from src.topicos.nomeador_topico import NomeadorTopico

logger = logging.getLogger(__name__)


class ServicoAgrupamento:
    """Orquestra pré-processamento spaCy, geração de embeddings densos, suíte de agrupamento e persistência Gold."""

    def __init__(
        self,
        configuracao: ConfiguracaoProjeto,
        armazenamento: ArmazenamentoObjeto,
        publicador: PublicadorEvento,
    ) -> None:
        self.configuracao = configuracao
        self.armazenamento = armazenamento
        self.publicador = publicador

        self.tratador_stopword = TratadorStopword(self.configuracao.stopwords_adicionais)
        self.processador_texto = ProcessadorTexto(self.tratador_stopword, self.configuracao.modelo_spacy)
        self.gerador_embedding = GeradorEmbedding(self.configuracao.modelo_spacy, self.configuracao.lote_spacy)
        self.fabrica = FabricaAgrupador(self.configuracao)
        self.nomeador = NomeadorTopico(self.tratador_stopword)
        self.associador = AssociadorComentario()

    def calcular_metricas(
        self,
        nome_algoritmo: str,
        embeddings: np.ndarray,
        rotulos: np.ndarray,
        tempo_treino: float,
        tempo_inferencia: float,
    ) -> MetricaModelo:
        """Calcula métricas de qualidade de clustering compatíveis matematicamente."""
        qtd_docs = len(rotulos)
        if qtd_docs == 0:
            return MetricaModelo(
                algoritmo=nome_algoritmo,
                quantidade_clusters=0,
                quantidade_documentos=0,
                percentual_ruido=0.0,
                silhouette_score=0.0,
                davies_bouldin_score=0.0,
                calinski_harabasz_score=0.0,
                tamanho_medio_cluster=0.0,
                maior_cluster=0,
                menor_cluster=0,
                tempo_treinamento=tempo_treino,
                tempo_inferencia=tempo_inferencia,
            )

        contagem = collections.Counter(rotulos)
        qtd_ruido = contagem.get(-1, 0)
        pct_ruido = float(qtd_ruido / qtd_docs)

        rotulos_validos = [r for r in rotulos if r >= 0]
        clusters_unicos = set(rotulos_validos)
        qtd_clusters = len(clusters_unicos)

        sil_score = 0.0
        db_score = 0.0
        ch_score = 0.0

        if qtd_clusters >= 2 and len(rotulos_validos) > qtd_clusters:
            indices_validos = np.where(rotulos >= 0)[0]
            emb_validos = embeddings[indices_validos]
            lbl_validos = rotulos[indices_validos]
            try:
                sil_score = float(silhouette_score(emb_validos, lbl_validos, metric="cosine"))
            except Exception:
                sil_score = 0.0
            try:
                db_score = float(davies_bouldin_score(emb_validos, lbl_validos))
            except Exception:
                db_score = 0.0
            try:
                ch_score = float(calinski_harabasz_score(emb_validos, lbl_validos))
            except Exception:
                ch_score = 0.0

        tamanhos = [contagem[c] for c in clusters_unicos] if clusters_unicos else [0]
        tam_medio = float(np.mean(tamanhos)) if tamanhos else 0.0
        maior_c = max(tamanhos) if tamanhos else 0
        menor_c = min(tamanhos) if tamanhos else 0

        return MetricaModelo(
            algoritmo=nome_algoritmo,
            quantidade_clusters=qtd_clusters,
            quantidade_documentos=qtd_docs,
            percentual_ruido=pct_ruido,
            silhouette_score=sil_score,
            davies_bouldin_score=db_score,
            calinski_harabasz_score=ch_score,
            tamanho_medio_cluster=tam_medio,
            maior_cluster=maior_c,
            menor_cluster=menor_c,
            tempo_treinamento=tempo_treino,
            tempo_inferencia=tempo_inferencia,
        )

    def persistir_gold(
        self,
        nome_algoritmo: str,
        agrupamentos: List[Agrupamento],
        topicos: List[Topico],
        metricas: MetricaModelo,
    ) -> bool:
        """Persiste tabelas analíticas no MinIO sob o prefixo gold/ sem persistência local."""
        caminho_agr = f"gold/agrupamentos/modelo={nome_algoritmo}/agrupamentos.parquet"
        caminho_top = f"gold/topicos/modelo={nome_algoritmo}_topicos.parquet"
        caminho_met = f"gold/metricas/modelo={nome_algoritmo}_metricas.parquet"

        df_agr = pd.DataFrame([a.para_dicionario() for a in agrupamentos])
        df_top = pd.DataFrame([t.para_dicionario() for t in topicos])
        df_met = pd.DataFrame([metricas.para_dicionario()])

        self.armazenamento.gravar_dataframe(caminho_agr, df_agr)
        self.armazenamento.gravar_dataframe(caminho_top, df_top)
        self.armazenamento.gravar_dataframe(caminho_met, df_met)
        return True

    def executar_agrupamento(
        self, comentarios: List[Comentario], respostas: List[Resposta]
    ) -> Dict[str, Tuple[List[Agrupamento], List[Topico], MetricaModelo]]:
        """Executa normalização Silver, geração de embeddings spaCy e agrupamentos solicitados."""
        data_exec = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        total_itens = len(comentarios) + len(respostas)
        logger.info("Iniciando processamento textual spaCy para %d itens.", total_itens)
        self.publicador.publicar_evento("processamento_iniciado", {"total_itens": str(total_itens)})

        # 1. Normalização Silver
        documentos = self.processador_texto.processar_lote(
            comentarios, respostas, tamanho_lote=self.configuracao.lote_spacy
        )
        caminho_docs = f"silver/documentos/data={data_exec}/documentos.parquet"
        df_docs = pd.DataFrame([d.para_dicionario() for d in documentos])
        self.armazenamento.gravar_dataframe(caminho_docs, df_docs)

        self.publicador.publicar_evento(
            "processamento_concluido", {"documentos_normalizados": str(len(documentos))}
        )

        # 2. Embeddings densos spaCy
        logger.info("Gerando embeddings spaCy (%s) em lote...", self.configuracao.modelo_spacy)
        textos_processados = [d.texto_limpo for d in documentos]
        embeddings = self.gerador_embedding.gerar_embeddings(textos_processados)

        caminho_emb = f"silver/embeddings/data={data_exec}/embeddings.parquet"
        df_emb = pd.DataFrame(embeddings)
        self.armazenamento.gravar_dataframe(caminho_emb, df_emb)
        self.publicador.publicar_evento(
            "embeddings_gerados", {"dimensao": str(self.gerador_embedding.dimensao_vetor)}
        )

        # Frequência global de palavras para c-TF-IDF / seleção de palavras
        todas_palavras: List[str] = []
        for t in textos_processados:
            todas_palavras.extend(self.nomeador.extrair_candidatas([t]))
        palavras_fundo = collections.Counter([p.lower() for p in todas_palavras])

        # 3. Seleção dos modelos
        if self.configuracao.modo_execucao == "producao":
            modelos_executar = self.configuracao.modelos_producao
        else:
            modelos_executar = self.fabrica.listar_disponiveis()

        logger.info("Executando modelos configurados: %s", modelos_executar)
        resultados: Dict[str, Tuple[List[Agrupamento], List[Topico], MetricaModelo]] = {}

        for nome_alg in modelos_executar:
            logger.info("Executando agrupamento com algoritmo: %s", nome_alg)
            self.publicador.publicar_evento("treinamento_iniciado", {"algoritmo": nome_alg})

            estrategia = self.fabrica.criar_modelo(nome_alg)
            t_inicio = time.time()
            rotulos = estrategia.treinar_modelo(embeddings, textos=textos_processados)
            t_treino = time.time() - t_inicio

            t_inferencia_ini = time.time()
            probabilidades = estrategia.obter_probabilidades()
            t_inferencia = time.time() - t_inferencia_ini

            # Nomeação de tópicos (UMA única palavra representativa)
            topicos_bertopic: Dict[int, List[Tuple[str, float]]] = {}
            if isinstance(estrategia, AgrupadorBertopic):
                topicos_bertopic = estrategia.obter_topicos()

            clusters_unicos = sorted(list(set(rotulos)))
            mapa_topicos: Dict[int, Topico] = {}
            lista_topicos: List[Topico] = []

            for c_id in clusters_unicos:
                indices_c = np.where(rotulos == c_id)[0]
                textos_c = [textos_processados[idx] for idx in indices_c]
                palavras_bt = topicos_bertopic.get(c_id)
                topico_obj = self.nomeador.nomear_topico(
                    numero_cluster=c_id,
                    textos_cluster=textos_c,
                    palavras_fundo=palavras_fundo,
                    palavras_bertopic=palavras_bt,
                )
                mapa_topicos[c_id] = topico_obj
                lista_topicos.append(topico_obj)

            # Associação de documentos
            agrupamentos = self.associador.associar_documentos(
                documentos=documentos,
                rotulos=rotulos,
                probabilidades=probabilidades,
                mapa_topicos=mapa_topicos,
                nome_modelo=estrategia.obter_nome(),
            )

            # Avaliação de métricas
            metricas = self.calcular_metricas(
                nome_algoritmo=estrategia.obter_nome(),
                embeddings=embeddings,
                rotulos=rotulos,
                tempo_treino=t_treino,
                tempo_inferencia=t_inferencia,
            )

            # Persistência na camada Gold
            self.persistir_gold(nome_alg, agrupamentos, lista_topicos, metricas)

            # Notificação GoF Observer
            detalhes_avaliacao = {
                "algoritmo": estrategia.obter_nome(),
                "clusters": str(metricas.quantidade_clusters),
                "silhouette": f"{metricas.silhouette_score:.4f}",
                "ruido": f"{metricas.percentual_ruido:.4f}",
            }
            self.publicador.publicar_evento("avaliacao_concluida", detalhes_avaliacao)

            resultados[nome_alg] = (agrupamentos, lista_topicos, metricas)

        return resultados
