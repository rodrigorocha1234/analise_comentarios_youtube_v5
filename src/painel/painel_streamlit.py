import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd
import streamlit as st

_raiz_projeto = str(Path(__file__).resolve().parents[2])
if _raiz_projeto not in sys.path:
    sys.path.insert(0, _raiz_projeto)

from src.armazenamento.adaptador_s3 import AdaptadorS3

logger = logging.getLogger(__name__)


class PainelStreamlit:
    """Dashboard analítico Streamlit para visualização de agrupamentos, tópicos e tendências."""

    def __init__(self) -> None:
        self.armazenamento = AdaptadorS3()
        self.mapa_canais: Dict[str, str] = {}
        self.mapa_videos: Dict[str, str] = {}

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

    def carregar_metadados(self) -> None:
        """Carrega mapeamentos de IDs de canais e vídeos para seus respectivos nomes e títulos."""
        try:
            df_canais = self.carregar_dados("bronze/canais/")
            if not df_canais.empty and "id_canal" in df_canais.columns and "titulo" in df_canais.columns:
                self.mapa_canais = dict(
                    zip(df_canais["id_canal"].astype(str), df_canais["titulo"].astype(str))
                )

            df_videos = self.carregar_dados("bronze/videos/")
            if not df_videos.empty and "id_video" in df_videos.columns and "titulo" in df_videos.columns:
                self.mapa_videos = dict(
                    zip(df_videos["id_video"].astype(str), df_videos["titulo"].astype(str))
                )
        except Exception as erro:
            logger.warning("Erro ao carregar metadados de canais e vídeos: %s", erro)

    def enriquecer_dados(
        self, df_agr: pd.DataFrame, df_ten: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Adiciona nomes legíveis de canais e vídeos aos DataFrames analíticos."""
        if not df_agr.empty:
            if "id_canal" in df_agr.columns:
                df_agr["nome_canal"] = df_agr["id_canal"].map(self.mapa_canais).fillna(df_agr["id_canal"])
            if "id_video" in df_agr.columns:
                df_agr["titulo_video"] = df_agr["id_video"].map(self.mapa_videos).fillna(df_agr["id_video"])

        if not df_ten.empty:
            df_ten["nome_canal"] = ""
            df_ten["titulo_video"] = ""
            df_ten["alvo_legivel"] = ""

            for idx, linha in df_ten.iterrows():
                escopo = str(linha.get("escopo", ""))
                identificador = str(linha.get("identificador_escopo", ""))

                if escopo == "canal":
                    nome_c = self.mapa_canais.get(identificador, identificador)
                    df_ten.at[idx, "nome_canal"] = nome_c
                    df_ten.at[idx, "alvo_legivel"] = f"📺 {nome_c}"
                elif escopo == "video":
                    titulo_v = self.mapa_videos.get(identificador, identificador)
                    df_ten.at[idx, "titulo_video"] = titulo_v
                    df_ten.at[idx, "alvo_legivel"] = f"🎥 {titulo_v}"
                elif escopo == "canal_video":
                    partes = identificador.split("__")
                    c_id = partes[0] if len(partes) > 0 else ""
                    v_id = partes[1] if len(partes) > 1 else ""
                    nome_c = self.mapa_canais.get(c_id, c_id)
                    titulo_v = self.mapa_videos.get(v_id, v_id)
                    df_ten.at[idx, "nome_canal"] = nome_c
                    df_ten.at[idx, "titulo_video"] = titulo_v
                    df_ten.at[idx, "alvo_legivel"] = f"📺 {nome_c} | 🎥 {titulo_v}"

        return df_agr, df_ten

    def renderizar_cabecalho(self) -> None:
        """Renderiza o cabeçalho e descrição da plataforma."""
        st.title("🎯 Radar de Tópicos e Tendências do YouTube")
        st.markdown(
            "Plataforma não-supervisionada para descoberta de tópicos, Trend Topics temporais "
            "e comparação de algoritmos com embeddings spaCy e MinIO/S3."
        )

    def renderizar_filtros(self, df_agr: pd.DataFrame) -> Dict[str, str]:
        """Renderiza barra lateral com filtros dinâmicos contendo nomes e títulos legíveis."""
        st.sidebar.header("🔍 Filtros de Visualização")

        mapa_canais_filtro: Dict[str, str] = {"Todos": "Todos"}
        if not df_agr.empty and "id_canal" in df_agr.columns:
            for c_id in sorted(df_agr["id_canal"].dropna().unique()):
                nome = self.mapa_canais.get(str(c_id), str(c_id))
                rotulo = f"📺 {nome} ({c_id})" if nome != c_id else f"📺 {c_id}"
                mapa_canais_filtro[rotulo] = str(c_id)

        escolha_canal = st.sidebar.selectbox("Canal", list(mapa_canais_filtro.keys()))
        canal_selecionado = mapa_canais_filtro[escolha_canal]

        mapa_videos_filtro: Dict[str, str] = {"Todos": "Todos"}
        if not df_agr.empty and "id_video" in df_agr.columns:
            df_base_videos = df_agr
            if canal_selecionado != "Todos":
                df_base_videos = df_agr[df_agr["id_canal"] == canal_selecionado]

            for v_id in sorted(df_base_videos["id_video"].dropna().unique()):
                titulo = self.mapa_videos.get(str(v_id), str(v_id))
                rotulo = f"🎥 {titulo[:45]}... ({v_id})" if len(titulo) > 45 else f"🎥 {titulo} ({v_id})"
                mapa_videos_filtro[rotulo] = str(v_id)

        escolha_video = st.sidebar.selectbox("Vídeo", list(mapa_videos_filtro.keys()))
        video_selecionado = mapa_videos_filtro[escolha_video]

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
        col_metricas, col_grafico = st.columns([1, 2])

        total_docs = len(df_agr) if not df_agr.empty else 0
        total_topicos = df_agr["topico"].nunique() if not df_agr.empty else 0
        total_videos = df_agr["id_video"].nunique() if not df_agr.empty else 0
        total_canais = df_agr["id_canal"].nunique() if not df_agr.empty else 0

        with col_metricas:
            st.markdown("#### 📌 Métricas Gerais")
            m1, m2 = st.columns(2)
            m1.metric("Documentos", total_docs)
            m2.metric("Tópicos", total_topicos)
            m1.metric("Vídeos", total_videos)
            m2.metric("Canais", total_canais)

            if self.mapa_canais:
                st.markdown("**📺 Canais Monitorados:**")
                for c_id, c_nome in self.mapa_canais.items():
                    st.write(f"- **{c_nome}** (`{c_id}`)")

        with col_grafico:
            st.markdown("#### 📊 Distribuição dos Tópicos Mais Populares")
            if not df_agr.empty:
                df_topicos = df_agr["topico"].value_counts().head(10).reset_index()
                df_topicos.columns = ["topico", "quantidade"]
                st.bar_chart(
                    df_topicos,
                    x="quantidade",
                    y="topico",
                    horizontal=True,
                    sort="-quantidade",
                )
            else:
                st.info("Nenhum agrupamento disponível para exibir o gráfico.")

    def renderizar_tendencias(self, df_ten: pd.DataFrame) -> None:
        """Aba 2: Tendências."""
        st.subheader("🔥 Trend Topics Temporais")
        if df_ten.empty:
            st.info("Nenhum registro de tendência calculado até o momento.")
            return

        janelas = sorted(list(df_ten["janela_dias"].unique())) if "janela_dias" in df_ten else []
        janela_sel = st.selectbox("Janela Temporal (Dias)", janelas) if janelas else None

        df_filtrado = df_ten[df_ten["janela_dias"] == janela_sel] if janela_sel is not None else df_ten
        colunas_exibir = [
            c
            for c in [
                "alvo_legivel",
                "escopo",
                "topico",
                "score_tendencia",
                "volume_atual",
                "crescimento_absoluto",
                "aceleracao",
                "janela_dias",
            ]
            if c in df_filtrado.columns
        ]
        st.dataframe(df_filtrado[colunas_exibir] if colunas_exibir else df_filtrado, use_container_width=True)

    def renderizar_videos(self, df_ten: pd.DataFrame) -> None:
        """Aba 3: Vídeos com títulos legíveis."""
        st.subheader("🎥 Tendências por Vídeo")
        if not df_ten.empty and "escopo" in df_ten.columns:
            df_v = df_ten[df_ten["escopo"] == "video"]
            colunas_exibir = [
                c
                for c in [
                    "titulo_video",
                    "topico",
                    "score_tendencia",
                    "volume_atual",
                    "crescimento_absoluto",
                    "aceleracao",
                    "janela_dias",
                    "posicao_ranking",
                ]
                if c in df_v.columns
            ]
            st.dataframe(df_v[colunas_exibir] if colunas_exibir else df_v, use_container_width=True)
        else:
            st.info("Sem dados de vídeo disponíveis.")

    def renderizar_canais(self, df_ten: pd.DataFrame) -> None:
        """Aba 4: Canais com nomes legíveis."""
        st.subheader("📺 Tendências por Canal")
        if not df_ten.empty and "escopo" in df_ten.columns:
            df_c = df_ten[df_ten["escopo"] == "canal"]
            colunas_exibir = [
                c
                for c in [
                    "nome_canal",
                    "topico",
                    "score_tendencia",
                    "volume_atual",
                    "crescimento_absoluto",
                    "aceleracao",
                    "janela_dias",
                    "posicao_ranking",
                ]
                if c in df_c.columns
            ]
            st.dataframe(df_c[colunas_exibir] if colunas_exibir else df_c, use_container_width=True)
        else:
            st.info("Sem dados de canal disponíveis.")

    def renderizar_cruzamento(self, df_ten: pd.DataFrame) -> None:
        """Aba 5: Canal × Vídeo com nomes legíveis."""
        st.subheader("🔗 Tendências por Canal × Vídeo")
        if not df_ten.empty and "escopo" in df_ten.columns:
            df_cv = df_ten[df_ten["escopo"] == "canal_video"]
            colunas_exibir = [
                c
                for c in [
                    "nome_canal",
                    "titulo_video",
                    "topico",
                    "score_tendencia",
                    "volume_atual",
                    "crescimento_absoluto",
                    "aceleracao",
                    "janela_dias",
                    "posicao_ranking",
                ]
                if c in df_cv.columns
            ]
            st.dataframe(df_cv[colunas_exibir] if colunas_exibir else df_cv, use_container_width=True)
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
        """Aba 7: Clusters com canal e título do vídeo."""
        st.subheader("🧩 Detalhes dos Clusters")
        if df_agr.empty:
            st.info("Nenhum agrupamento carregado.")
            return
        colunas_exibir = [
            c
            for c in [
                "nome_canal",
                "titulo_video",
                "numero_cluster",
                "topico",
                "probabilidade",
                "modelo",
                "texto_original",
            ]
            if c in df_agr.columns
        ]
        st.dataframe(
            df_agr[colunas_exibir] if colunas_exibir else df_agr,
            use_container_width=True,
        )

    def renderizar_comentarios(self, df_agr: pd.DataFrame) -> None:
        """Aba 8: Comentários e Respostas com nomes de canais e títulos dos vídeos."""
        st.subheader("💬 Navegação de Comentários e Respostas")
        if df_agr.empty:
            st.info("Sem comentários para exibir.")
            return

        comentarios_pais = df_agr[df_agr["tipo"] == "COMENTARIO"]
        for _, com in comentarios_pais.head(20).iterrows():
            id_com = str(com.get("id_comentario", ""))
            titulo_v = str(com.get("titulo_video", ""))
            nome_c = str(com.get("nome_canal", ""))
            rotulo = f"[{nome_c}] {titulo_v[:35]}... | {com.get('texto_original', '')[:50]}... (Tópico: {com.get('topico')})"

            with st.expander(rotulo):
                st.write(f"**Canal:** {nome_c}")
                st.write(f"**Vídeo:** {titulo_v}")
                st.write(f"**Autor:** {com.get('autor', 'Desconhecido')}")
                st.write(f"**Texto:** {com.get('texto_original', '')}")
                st.write(f"**Cluster:** {com.get('numero_cluster')} | **Score:** {com.get('probabilidade')}")

                respostas = df_agr[df_agr["id_comentario_pai"] == id_com]
                if not respostas.empty:
                    st.markdown("##### ↳ Respostas:")
                    for _, resp in respostas.iterrows():
                        st.markdown(f"> **{resp.get('autor', 'Anônimo')}:** {resp.get('texto_original')}")

    def gerar_nuvem(self, frequencias: Dict[str, int]) -> Optional[object]:
        """Gera uma figura Matplotlib contendo a nuvem de palavras estilizada."""
        if not frequencias:
            return None
        try:
            from wordcloud import WordCloud
            import matplotlib.pyplot as plt

            wc = WordCloud(
                width=1000,
                height=460,
                background_color="#0e1117",
                colormap="plasma",
                max_words=100,
                prefer_horizontal=0.85,
            ).generate_from_frequencies(frequencias)

            fig, ax = plt.subplots(figsize=(10, 4.6), facecolor="#0e1117")
            ax.imshow(wc, interpolation="bilinear")
            ax.axis("off")
            fig.tight_layout(pad=0)
            return fig
        except Exception as erro:
            logger.warning("Falha ao gerar nuvem de palavras: %s", erro)
            return None

    def renderizar_nuvens(self) -> None:
        """Aba 9: Nuvem de Palavras com visualização gráfica interativa."""
        st.subheader("☁️ Nuvem de Palavras e Frequências Lexicais")
        try:
            chaves = self.armazenamento.listar_objetos("gold/nuvens_palavras/")
            chaves_json = [c for c in chaves if c.endswith(".json")]
            if not chaves_json:
                st.info("Nenhuma frequência de palavras persistida ainda na camada Gold.")
                return

            conteudo = self.armazenamento.ler_objeto(chaves_json[-1])
            dados = json.loads(conteudo.decode("utf-8"))
            if not isinstance(dados, dict) or not dados:
                st.info("Arquivo de frequências vazio.")
                return

            # Formata opções amigáveis para seleção de categoria
            mapa_categorias: Dict[str, str] = {}
            for cat in dados.keys():
                if cat == "global":
                    rotulo = "🌐 Visão Global (Todos os Comentários)"
                elif cat.startswith("canal_"):
                    c_id = cat.replace("canal_", "")
                    nome_c = self.mapa_canais.get(c_id, c_id)
                    rotulo = f"📺 Canal: {nome_c}"
                elif cat.startswith("topico_"):
                    nome_t = cat.replace("topico_", "")
                    rotulo = f"🏷️ Tópico: {nome_t}"
                else:
                    rotulo = f"📁 {cat}"
                mapa_categorias[rotulo] = cat

            escolha = st.selectbox("Selecione o Escopo para Visualização da Nuvem", list(mapa_categorias.keys()))
            categoria_sel = mapa_categorias[escolha]
            freq_dados = dados.get(categoria_sel, {})

            if freq_dados and isinstance(freq_dados, dict):
                freq_int = {str(k): int(v) for k, v in freq_dados.items() if int(v) > 0}
                fig = self.gerar_nuvem(freq_int)
                if fig is not None:
                    st.pyplot(fig, use_container_width=True)
                else:
                    st.warning("Não foi possível gerar a imagem da nuvem de palavras.")

                st.markdown("#### 📊 Termos de Maior Destaque")
                df_termos = (
                    pd.Series(freq_int)
                    .sort_values(ascending=False)
                    .head(15)
                    .reset_index()
                )
                df_termos.columns = ["termo", "frequencia"]
                st.bar_chart(
                    df_termos,
                    x="frequencia",
                    y="termo",
                    horizontal=True,
                    sort="-frequencia",
                )

                with st.expander(f"Ver Frequências Brutas ({escolha})"):
                    st.json(freq_dados)
            else:
                st.info("Sem frequências disponíveis para a categoria selecionada.")
        except Exception as erro:
            logger.warning("Erro ao carregar nuvens de palavras: %s", erro)
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
            if "id_canal" in df_modelo.columns:
                df_modelo["nome_canal"] = df_modelo["id_canal"].map(self.mapa_canais).fillna(df_modelo["id_canal"])
            if "id_video" in df_modelo.columns:
                df_modelo["titulo_video"] = df_modelo["id_video"].map(self.mapa_videos).fillna(df_modelo["id_video"])

            st.markdown(f"#### Tópicos e Distribuição ({modelo_selecionado})")
            df_dist = df_modelo["topico"].value_counts().reset_index()
            df_dist.columns = ["topico", "quantidade"]
            st.bar_chart(
                df_dist,
                x="quantidade",
                y="topico",
                horizontal=True,
                sort="-quantidade",
            )
            st.markdown("#### Documentos Associados")
            colunas_doc = [
                c
                for c in [
                    "nome_canal",
                    "titulo_video",
                    "numero_cluster",
                    "topico",
                    "probabilidade",
                    "texto_original",
                ]
                if c in df_modelo.columns
            ]
            st.dataframe(df_modelo[colunas_doc] if colunas_doc else df_modelo, use_container_width=True)
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
        self.carregar_metadados()

        df_agr = self.carregar_dados("gold/agrupamentos/")
        df_ten = self.carregar_dados("gold/tendencias_")
        df_agr, df_ten = self.enriquecer_dados(df_agr, df_ten)

        filtros = self.renderizar_filtros(df_agr)
        if filtros["canal"] != "Todos" and not df_agr.empty and "id_canal" in df_agr.columns:
            df_agr = df_agr[df_agr["id_canal"] == filtros["canal"]]
        if filtros["video"] != "Todos" and not df_agr.empty and "id_video" in df_agr.columns:
            df_agr = df_agr[df_agr["id_video"] == filtros["video"]]
        if filtros["modelo"] != "Todos" and not df_agr.empty and "modelo" in df_agr.columns:
            df_agr = df_agr[df_agr["modelo"].str.lower() == filtros["modelo"].lower()]

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
