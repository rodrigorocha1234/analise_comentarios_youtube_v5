# Arquitetura do Sistema

## Visão Geral
A plataforma **Radar de Tópicos e Tendências do YouTube** foi concebida para fornecer análise semântica não supervisionada de comentários e respostas de múltiplos vídeos e canais do YouTube sem a utilização de Modelos de Linguagem de Grande Porte (LLMs).

## Fluxo de Dados de Ponta a Ponta
```text
YouTube Data API v3
  ├── Coleta Incremental Diária (Canais, Vídeos, Comentários, Respostas)
  ▼
MinIO / S3 (Camada Bronze - Parquet)
  ├── bronze/canais/data_coleta=YYYY-MM-DD/
  ├── bronze/videos/data_coleta=YYYY-MM-DD/
  ├── bronze/comentarios/data_coleta=YYYY-MM-DD/
  └── bronze/respostas/data_coleta=YYYY-MM-DD/
  ▼
Processamento spaCy PT-BR (Camada Silver - Parquet)
  ├── Normalização, Lematização, Stopwords Unificadas
  ├── Embeddings Densos spaCy (pt_core_news_md - dim 300)
  ├── silver/documentos/data=YYYY-MM-DD/
  └── silver/embeddings/data=YYYY-MM-DD/
  ▼
Suíte de Agrupamento & BERTopic (Camada Gold - Parquet)
  ├── 12 Estratégias GoF (KMeans, DBSCAN, HDBSCAN, BERTopic, etc.)
  ├── Nomeação de Tópicos (Exatamente 1 palavra, preservando Unicode/acentos)
  ├── Associação de Hierarquia (Comentários Pais -> Respostas)
  └── Avaliação de Métricas (Silhouette, Davies-Bouldin, Calinski-Harabasz)
  ▼
Trend Topics Temporais Multiescopo (Camada Gold - Parquet)
  ├── Escopos: Vídeo, Canal, Canal × Vídeo
  ├── Janelas Móveis: 1, 3, 7, 14, 30 dias
  └── Nuvens de Frequência de Palavras
  ▼
MLflow & Serving
  ├── Registro de Parâmetros, Métricas e Artefatos via Observer
  ├── Versionamento de Contratos de Schemas (Entrada e Saída 1.0.0)
  └── Model Registry e MLflow Models Serving
  ▼
Streamlit Dashboard
  └── 12 Abas de Visualização Interativa para Todos os Algoritmos
```

## Padrões de Projeto (GoF)

1. **GoF Strategy**:
   - `EstrategiaAgrupamento` define a interface comum para os algoritmos de clustering.
   - 12 estratégias concretas intercambiáveis: `AgrupadorKmeans`, `AgrupadorMinibatch`, `AgrupadorDbscan`, `AgrupadorHdbscan`, `AgrupadorOptics`, `AgrupadorAglomerativo`, `AgrupadorGaussiano`, `AgrupadorEspectral`, `AgrupadorAfinidade`, `AgrupadorMedia`, `AgrupadorBirch` e `AgrupadorBertopic`.

2. **GoF Factory Method**:
   - `FabricaAgrupador` centraliza a instanciação parametrizada das estratégias a partir do arquivo YAML, evitando blocos condicionais dispersos.

3. **GoF Observer**:
   - O pipeline emite eventos semânticos (`coleta_iniciada`, `embeddings_gerados`, `avaliacao_concluida`, etc.) através do `PublicadorEvento`.
   - `ObservadorMlflow` consome esses eventos e registra execuções, métricas e tags sem acoplar a lógica de domínio ao MLflow.

4. **Adapter**:
   - `ArmazenamentoObjeto` desacopla a aplicação do SDK de nuvem.
   - `AdaptadorS3` implementa a comunicação exclusiva com MinIO/S3 via `boto3`, garantindo a ausência de persistência em disco local para o datalake.
