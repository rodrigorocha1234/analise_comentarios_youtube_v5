import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
import yaml
from dotenv import load_dotenv


@dataclass
class ConfiguracaoProjeto:
    """Carrega e gerencia configurações do arquivo YAML e variáveis de ambiente."""

    caminho_yaml: str = "config/configuracao.yaml"
    nome_projeto: str = "agrupamento_youtube"
    idioma: str = "pt_BR"
    canais_alvo: List[str] = field(default_factory=list)
    videos_alvo: List[str] = field(default_factory=list)
    intervalo_horas: int = 24
    coletar_respostas: bool = True
    coletar_todos_comentarios: bool = True
    atualizar_comentarios: bool = True
    maximo_videos_canal: int = 20
    modelo_spacy: str = "pt_core_news_md"
    lote_spacy: int = 256
    lematizar_texto: bool = True
    remover_urls: bool = True
    stopwords_adicionais: List[str] = field(default_factory=list)
    top_n_palavras_bertopic: int = 10
    janelas_dias: List[int] = field(default_factory=lambda: [1, 3, 7, 14, 30])
    modo_execucao: str = "experimental"
    modelos_producao: List[str] = field(default_factory=lambda: ["bertopic", "kmeans", "hdbscan"])
    bucket_armazenamento: str = "youtube-comentarios"
    formato_armazenamento: str = "parquet"
    experimento_mlflow: str = "agrupamento_youtube"
    registrar_modelos: bool = True
    versionar_schema: bool = True
    versao_schema_entrada: str = "1.0.0"
    versao_schema_saida: str = "1.0.0"

    def carregar_configuracao(self) -> "ConfiguracaoProjeto":
        """Carrega configurações do arquivo YAML e atualiza os atributos."""
        load_dotenv()
        caminho = Path(self.caminho_yaml)
        if caminho.exists():
            with open(caminho, "r", encoding="utf-8") as arquivo:
                dados = yaml.safe_load(arquivo)
                if isinstance(dados, dict):
                    self._aplicar_dados(dados)
        return self

    def _aplicar_dados(self, dados: Dict[str, object]) -> None:
        """Aplica os dados lidos do YAML aos atributos correspondentes."""
        projeto = dados.get("projeto")
        if isinstance(projeto, dict):
            self.nome_projeto = str(projeto.get("nome", self.nome_projeto))
            self.idioma = str(projeto.get("idioma", self.idioma))

        coleta = dados.get("coleta")
        if isinstance(coleta, dict):
            canais = coleta.get("canais_alvo")
            if isinstance(canais, list):
                self.canais_alvo = [str(c) for c in canais]
            videos = coleta.get("videos_alvo")
            if isinstance(videos, list):
                self.videos_alvo = [str(v) for v in videos]
            self.intervalo_horas = int(coleta.get("intervalo_horas", self.intervalo_horas))
            self.coletar_respostas = bool(coleta.get("coletar_respostas", self.coletar_respostas))
            self.coletar_todos_comentarios = bool(coleta.get("coletar_todos_comentarios", self.coletar_todos_comentarios))
            self.atualizar_comentarios = bool(coleta.get("atualizar_comentarios", self.atualizar_comentarios))
            self.maximo_videos_canal = int(coleta.get("maximo_videos_canal", self.maximo_videos_canal))

        spacy_cfg = dados.get("spacy")
        if isinstance(spacy_cfg, dict):
            self.modelo_spacy = str(spacy_cfg.get("modelo", self.modelo_spacy))
            self.lote_spacy = int(spacy_cfg.get("lote", self.lote_spacy))

        texto_cfg = dados.get("texto")
        if isinstance(texto_cfg, dict):
            self.lematizar_texto = bool(texto_cfg.get("lematizar", self.lematizar_texto))
            self.remover_urls = bool(texto_cfg.get("remover_urls", self.remover_urls))
            stopwords = texto_cfg.get("stopwords_adicionais")
            if isinstance(stopwords, list):
                self.stopwords_adicionais = [str(s) for s in stopwords]

        bertopic_cfg = dados.get("bertopic")
        if isinstance(bertopic_cfg, dict):
            self.top_n_palavras_bertopic = int(bertopic_cfg.get("top_n_words", self.top_n_palavras_bertopic))

        tendencias_cfg = dados.get("tendencias")
        if isinstance(tendencias_cfg, dict):
            janelas = tendencias_cfg.get("janelas_dias")
            if isinstance(janelas, list):
                self.janelas_dias = [int(j) for j in janelas]

        execucao_cfg = dados.get("execucao")
        if isinstance(execucao_cfg, dict):
            self.modo_execucao = str(execucao_cfg.get("modo", self.modo_execucao))
            modelos_prod = execucao_cfg.get("modelos_producao")
            if isinstance(modelos_prod, list):
                self.modelos_producao = [str(m) for m in modelos_prod]

        armazenamento_cfg = dados.get("armazenamento")
        if isinstance(armazenamento_cfg, dict):
            self.bucket_armazenamento = str(armazenamento_cfg.get("bucket", self.bucket_armazenamento))
            self.formato_armazenamento = str(armazenamento_cfg.get("formato", self.formato_armazenamento))

        mlflow_cfg = dados.get("mlflow")
        if isinstance(mlflow_cfg, dict):
            self.experimento_mlflow = str(mlflow_cfg.get("experimento", self.experimento_mlflow))
            self.registrar_modelos = bool(mlflow_cfg.get("registrar_modelos", self.registrar_modelos))
            self.versionar_schema = bool(mlflow_cfg.get("versionar_schema", self.versionar_schema))
            self.versao_schema_entrada = str(mlflow_cfg.get("versao_schema_entrada", self.versao_schema_entrada))
            self.versao_schema_saida = str(mlflow_cfg.get("versao_schema_saida", self.versao_schema_saida))

    def obter_credencial(self, nome_variavel: str, padrao: str = "") -> str:
        """Obtém uma variável de ambiente de credencial."""
        return os.getenv(nome_variavel, padrao)
