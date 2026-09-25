import logging
import os
from typing import Dict, List, Optional
import pandas as pd
import streamlit as st

from src.armazenamento.adaptador_s3 import AdaptadorS3

logger = logging.getLogger(__name__)


class PainelStreamlit:
    """Dashboard analítico Streamlit para visualização de agrupamentos, tópicos e tendências."""

    def __init__(self) -> None:
        self.armazenamento = AdaptadorS3()

    def carregar_dados(self, prefixo: str) -> pd.DataFrame:
        """Carrega e concatena DataFrames Parquet armazenados sob o prefixo no MinIO."""
        try:
            chaves = self.armazenamento.listar_objetos(prefixo)
            chaves_parquet = [c for c in chaves if c.endswith(".parquet")]
            if not chaves_parquet:
                return pd.DataFrame()
            dfs: List[pd.DataFrame] = []
            for ch in chaves_parquet:
                try:
                    df = self.armazenamento.ler_dataframe(ch)
                    dfs.append(df)
                except Exception as erro:
                    logger.warning("Falha ao ler chave %s: %s", ch, erro)
            if dfs:
                return pd.concat(dfs, ignore_index=True)
            return pd.DataFrame()
        except Exception as erro:
            logger.warning("Erro ao listar dados de %s: %s", prefixo, erro)
            return pd.DataFrame()

    def renderizar_cabecalho(self) -> None:
        """Renderiza o cabeçalho e descrição da plataforma."""
        st.title("🎯 Radar de Tópicos e Tendências do YouTube")
        st.markdown(
            "Plataforma não-supervisionada para descoberta de tópicos, Trend Topics temporais "
            "e comparação de algoritmos com embeddings spaCy e MinIO/S3."
        )

    def renderizar_filtros(self, df_agr: pd.DataFrame) -> Dict[str, str]:
        """Renderiza barra lateral com filtros dinâmicos."""
        st.sidebar.header("🔍 Filtros de Visualização")
        canais = ["Todos"] + sorted(list(df_agr["id_canal"].dropna().unique())) if not df_agr.empty else ["Todos"]
        canal_selecionado = st.sidebar.selectbox("Canal", canais)

        videos = ["Todos"] + sorted(list(df_agr["id_video"].dropna().unique())) if not df_agr.empty else ["Todos"]
        video_selecionado = st.sidebar.selectbox("Vídeo", videos)

        modelos = ["Todos"] + sorted(list(df_agr["modelo"].dropna().unique())) if not df_agr.empty else ["Todos"]
        modelo_selecionado = st.sidebar.selectbox("Algoritmo", modelos)

        return {
            "canal": canal_selecionado,
            "video": video_selecionado,
            "modelo": modelo_selecionado,
        }

    def renderizar_visao(self, df_agr: pd.DataFrame, df_ten: pd.DataFrame) -> None:
        """Aba 1: Visão Geral."""
        st.subheader("📊 Visão Geral do Ecossistema")
        col1, col2, col3, col4 = st.columns(4)
        total_docs = len(df_agr) if not df_agr.empty else 0
        total_topicos = df_agr["topico"].nunique() if not df_agr.empty else 0
        total_videos = df_agr["id_video"].nunique() if not df_agr.empty else 0
        total_canais = df_agr["id_canal"].nunique() if not df_agr.empty else 0

        col1.metric("Total Documentos", total_docs)
        col2.metric("Tópicos Distintos", total_topicos)
        col3.metric("Vídeos Analisados", total_videos)
        col4.metric("Canais Monitorados", total_canais)

        if not df_agr.empty:
            st.write("### Distribuição dos Tópicos Mais Populares")
            contagem = df_agr["topico"].value_counts().head(10)
            st.bar_chart(contagem)

    def renderizar_tendencias(self, df_ten: pd.DataFrame) -> None:
        """Aba 2: Tendências."""
        st.subheader("🔥 Trend Topics Temporais")
        if df_ten.empty:
            st.info("Nenhum registro de tendência calculado até o momento.")
            return

        janelas = sorted(list(df_ten["janela_dias"].unique())) if "janela_dias" in df_ten else []
        janela_sel = st.selectbox("Janela Temporal (Dias)", janelas) if janelas else None

        df_filtrado = df_ten[df_ten["janela_dias"] == janela_sel] if janela_sel is not None else df_ten
        st.dataframe(df_filtrado, use_container_width=True)

    def renderizar_videos(self, df_ten: pd.DataFrame) -> None:
        """Aba 3: Vídeos."""
        st.subheader("🎥 Tendências por Vídeo")
        if not df_ten.empty and "escopo" in df_ten.columns:
            df_v = df_ten[df_ten["escopo"] == "video"]
            st.dataframe(df_v, use_container_width=True)
        else:
            st.info("Sem dados de vídeo disponíveis.")

    def renderizar_canais(self, df_ten: pd.DataFrame) -> None:
        """Aba 4: Canais."""
        st.subheader("📺 Tendências por Canal")
        if not df_ten.empty and "escopo" in df_ten.columns:
            df_c = df_ten[df_ten["escopo"] == "canal"]
            st.dataframe(df_c, use_container_width=True)
        else:
            st.info("Sem dados de canal disponíveis.")

    def renderizar_cruzamento(self, df_ten: pd.DataFrame) -> None:
        """Aba 5: Canal × Vídeo."""
        st.subheader("🔗 Tendências por Canal × Vídeo")
        if not df_ten.empty and "escopo" in df_ten.columns:
            df_cv = df_ten[df_ten["escopo"] == "canal_video"]
            st.dataframe(df_cv, use_container_width=True)
        else:
            st.info("Sem dados de cruzamento canal × vídeo.")

    def renderizar_topicos(self, df_agr: pd.DataFrame) -> None:
        """Aba 6: Tópicos."""
        st.subheader("🏷️ Tópicos Identificados")
        if df_agr.empty:
            st.info("Nenhum tópico disponível.")
            return
        resumo = df_agr.groupby(["numero_cluster", "topico"]).size().reset_index(name="quantidade")
        st.dataframe(resumo, use_container_width=True)

    def renderizar_clusters(self, df_agr: pd.DataFrame) -> None:
        """Aba 7: Clusters."""
        st.subheader("🧩 Detalhes dos Clusters")
        if df_agr.empty:
            st.info("Nenhum agrupamento carregado.")
            return
        st.dataframe(
            df_agr[["id_documento", "numero_cluster", "topico", "probabilidade", "modelo"]],
            use_container_width=True,
        )

    def renderizar_comentarios(self, df_agr: pd.DataFrame) -> None:
        """Aba 8: Comentários e Respostas."""
        st.subheader("💬 Navegação de Comentários e Respostas")
        if df_agr.empty:
            st.info("Sem comentários para exibir.")
            return

        comentarios_pais = df_agr[df_agr["tipo"] == "COMENTARIO"]
        for _, com in comentarios_pais.head(20).iterrows():
            id_com = str(com.get("id_comentario", ""))
            with st.expander(f"Comentário: {com.get('texto_original', '')[:80]}... (Tópico: {com.get('topico')})"):
                st.write(f"**Autor:** {com.get('autor', 'Desconhecido')}")
                st.write(f"**Texto:** {com.get('texto_original', '')}")
                st.write(f"**Cluster:** {com.get('numero_cluster')} | **Score:** {com.get('probabilidade')}")

                respostas = df_agr[df_agr["id_comentario_pai"] == id_com]
                if not respostas.empty:
                    st.markdown("##### ↳ Respostas:")
                    for _, resp in respostas.iterrows():
                        st.markdown(f"> **{resp.get('autor', 'Anônimo')}:** {resp.get('texto_original')}")

    def renderizar_nuvens(self) -> None:
        """Aba 9: Nuvem de Palavras."""
        st.subheader("☁️ Nuvens de Frequência de Palavras")
        try:
            chaves = self.armazenamento.listar_objetos("gold/nuvens_palavras/")
            chaves_json = [c for c in chaves if c.endswith(".json")]
            if chaves_json:
                conteudo = self.armazenamento.ler_objeto(chaves_json[-1])
                import json
                dados = json.loads(conteudo.decode("utf-8"))
                for categoria, freq in dados.items():
                    with st.expander(f"Frequências - {categoria}"):
                        st.json(freq)
            else:
                st.info("Nenhuma frequência de palavras persistida ainda.")
        except Exception as erro:
            st.warning(f"Erro ao carregar nuvens de palavras: {erro}")

    def renderizar_comparacao(self) -> None:
        """Aba 10: Comparação de Modelos (OBRIGATÓRIA com todos os 12 algoritmos)."""
        st.subheader("⚖️ Comparação Detalhada de Modelos")
        modelos_disponiveis = [
            "BERTopic",
            "KMeans",
            "MiniBatchKMeans",
            "HDBSCAN",
            "DBSCAN",
            "OPTICS",
            "Agglomerative",
            "GaussianMixture",
            "Spectral",
            "AffinityPropagation",
            "MeanShift",
            "BIRCH",
        ]
        modelo_selecionado = st.selectbox("Selecione o Modelo para Análise Individual", modelos_disponiveis)
        df_modelo = self.carregar_dados(f"gold/agrupamentos/modelo={modelo_selecionado.lower()}/")
        df_metrica = self.carregar_dados(f"gold/metricas/modelo={modelo_selecionado.lower()}_")

        if not df_metrica.empty:
            st.markdown("#### Métricas de Desempenho")
            st.dataframe(df_metrica, use_container_width=True)

        if not df_modelo.empty:
            st.markdown(f"#### Tópicos e Distribuição ({modelo_selecionado})")
            dist = df_modelo["topico"].value_counts()
            st.bar_chart(dist)
            st.markdown("#### Documentos Associados")
            st.dataframe(df_modelo[["numero_cluster", "topico", "probabilidade", "texto_original"]], use_container_width=True)
        else:
            st.info(f"O modelo {modelo_selecionado} ainda não possui execuções gravadas no Gold.")

    def renderizar_execucoes(self) -> None:
        """Aba 11: Execuções MLflow."""
        st.subheader("📈 Rastreamento de Execuções e Servings no MLflow")
        uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
        st.markdown(f"Acesse a interface completa do MLflow em: [{uri}]({uri})")
        st.write("Modelos versionados com contratos de entrada e saída (Schemas 1.0.0).")

    def renderizar_qualidade(self) -> None:
        """Aba 12: Qualidade."""
        st.subheader("🛡️ Qualidade e Governança dos Dados")
        df_met_todas = self.carregar_dados("gold/metricas/")
        if not df_met_todas.empty:
            st.dataframe(df_met_todas, use_container_width=True)
        else:
            st.info("Métricas de qualidade consolidadas indisponíveis.")

    def executar_painel(self) -> None:
        """Coordena a montagem e exibição do dashboard Streamlit."""
        st.set_page_config(page_title="Radar de Tópicos YouTube", layout="wide", page_icon="🎯")
        self.renderizar_cabecalho()

        df_agr = self.carregar_dados("gold/agrupamentos/")
        df_ten = self.carregar_dados("gold/tendencias_")

        abas = st.tabs(
            [
                "Visão Geral",
                "Tendências",
                "Vídeos",
                "Canais",
                "Canal × Vídeo",
                "Tópicos",
                "Clusters",
                "Comentários",
                "Nuvem de Palavras",
                "Comparação de Modelos",
                "Execuções MLflow",
                "Qualidade",
            ]
        )

        with abas[0]:
            self.renderizar_visao(df_agr, df_ten)
        with abas[1]:
            self.renderizar_tendencias(df_ten)
        with abas[2]:
            self.renderizar_videos(df_ten)
        with abas[3]:
            self.renderizar_canais(df_ten)
        with abas[4]:
            self.renderizar_cruzamento(df_ten)
        with abas[5]:
            self.renderizar_topicos(df_agr)
        with abas[6]:
            self.renderizar_clusters(df_agr)
        with abas[7]:
            self.renderizar_comentarios(df_agr)
        with abas[8]:
            self.renderizar_nuvens()
        with abas[9]:
            self.renderizar_comparacao()
        with abas[10]:
            self.renderizar_execucoes()
        with abas[11]:
            self.renderizar_qualidade()


if __name__ == "__main__":
    painel = PainelStreamlit()
    painel.executar_painel()
