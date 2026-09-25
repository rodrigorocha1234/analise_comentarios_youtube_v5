# Plataforma de Agrupamento de Comentários do YouTube & Trend Topics

Plataforma completa em Python para coleta diária, normalização, geração de embeddings spaCy, agrupamento não supervisionado (12 estratégias incluindo BERTopic), cálculo de Trend Topics temporais multiescopo, governança com MinIO/S3 e MLflow Serving, além de dashboard interativo Streamlit.

## Destaques da Arquitetura

- **Sem LLM**: Processamento semântico determinístico com spaCy e modelos clássicos/densos.
- **Embeddings spaCy**: Vetores semânticos densos gerados via spaCy (`pt_core_news_md`), alimentando diretamente o BERTopic e demais agrupadores.
- **Datalake 100% MinIO/S3**: Nenhuma persistência local para Bronze, Silver e Gold.
- **Padrões GoF**:
  - **Strategy**: 12 algoritmos intercambiáveis de agrupamento.
  - **Factory Method**: Criação padronizada de estratégias via `FabricaAgrupador`.
  - **Observer**: Pipeline desacoplado publicando eventos para `ObservadorMlflow`.
  - **Adapter**: Interface `ArmazenamentoObjeto` implementada por `AdaptadorS3`.
- **Regras Estritas**:
  - Exatamente uma palavra por tópico exibido.
  - Preservação integral de Unicode e caracteres acentuados em português.
  - Métodos controlados com exatamente duas palavras separadas por underscore.
  - Sem uso de `typing.Any`.

## Documentação

Consulte a pasta `docs/` para obter os detalhes completos:
- [Como Usar](docs/como_usar.md)
- [Arquitetura](docs/arquitetura.md)
- [Trade-offs](docs/tradeoffs.md)
- [Configuração](docs/configuracao.md)
- [Streamlit Dashboard](docs/streamlit.md)
