import pytest
from src.dominio.configuracao_projeto import ConfiguracaoProjeto


def test_carregamento_configuracao_padrao():
    config = ConfiguracaoProjeto(caminho_yaml="config/configuracao.yaml").carregar_configuracao()
    assert config.idioma == "pt_BR"
    assert config.bucket_armazenamento == "youtube-comentarios"
    assert config.modelo_spacy == "pt_core_news_md"
    assert config.formato_armazenamento == "parquet"
    assert 1 in config.janelas_dias
    assert 30 in config.janelas_dias
    assert config.versao_schema_entrada == "1.0.0"
    assert config.versao_schema_saida == "1.0.0"


def test_obter_credencial_env():
    config = ConfiguracaoProjeto()
    valor = config.obter_credencial("VARIAVEL_INEXISTENTE_TESTE", "padrao")
    assert valor == "padrao"
