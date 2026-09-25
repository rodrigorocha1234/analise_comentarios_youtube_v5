# Arquitetura

Fluxo: YouTube Data API -> coleta incremental -> MinIO Bronze -> normalização Silver -> spaCy -> embeddings -> estratégias de agrupamento -> avaliação -> Gold -> MLflow -> Model Registry/Serving -> Streamlit.

## GoF
- Strategy: algoritmos de agrupamento intercambiáveis.
- Observer: eventos do pipeline observados pelo ObservadorMlflow.
- Adapter: abstração de armazenamento de objetos para MinIO/S3.
- Factory Method: criação de agrupadores a partir da configuração.

## Separação de execução
Modo experimental executa a suíte de algoritmos; modo produção executa apenas modelos aprovados. Nenhum componente de domínio depende diretamente de boto3/MinIO ou de detalhes internos do MLflow.
