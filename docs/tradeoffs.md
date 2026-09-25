# Análise de Trade-offs Técnicos e Decisões de Arquitetura

O desenvolvimento da plataforma envolveu decisões estratégicas e ponderações técnicas explícitas:

## 1. spaCy Embeddings × SentenceTransformer
- **Decisão**: Utilização exclusiva de embeddings spaCy (`pt_core_news_md`, 300 dimensões) sem SentenceTransformer.
- **Vantagem**: Redução drástica do consumo de memória RAM e GPU, dependência de um único ecossistema NLP consolidado para português, e alta velocidade de processamento com `nlp.pipe`.
- **Limitação (Trade-off)**: SentenceTransformer (como modelos baseados em BERT/RoBERTa) captura nuances sintáticas mais profundas e relações de longa distância do que vetores estáticos ponderados. Para atenuar essa diferença, foi empregado o pipeline `md` do spaCy contendo vetores pré-treinados densos.

## 2. Qualidade Semântica × Padronização Tecnológica
- **Decisão**: Centralizar a extração linguística, tokenização, lematização e vetorização no spaCy.
- **Vantagem**: Contratos fortes e arquitetura uniforme sem fragmentação entre múltiplas bibliotecas neurais pesadas.
- **Limitação**: Menor flexibilidade para alternar dinamicamente arquiteturas de transformadores em tempo de execução.

## 3. Todos os Algoritmos × Custo Computacional
- **Decisão**: Implementação de 12 estratégias distintas de clustering (KMeans, MiniBatch, DBSCAN, HDBSCAN, OPTICS, Agglomerative, GMM, Spectral, Affinity, MeanShift, BIRCH, BERTopic).
- **Vantagem**: Capacidade analítica profunda para comparar famílias geométricas, de densidade e neurais no Streamlit.
- **Limitação**: Alto custo de treinamento na suíte completa à medida que o corpus cresce. Solução: divisão em Modo Experimental e Modo Produção no YAML.

## 4. Algoritmos Quadráticos × Grande Volume
- **Decisão**: Algoritmos com complexidade computacional $O(N^2)$ ou superior (AffinityPropagation, SpectralClustering) são mantidos para experimentação.
- **Limitação**: Inviáveis para centenas de milhares de comentários. Em produção, são priorizados algoritmos escaláveis como `MiniBatchKMeans`, `BIRCH` e `HDBSCAN`.

## 5. Coleta Completa × Quota da YouTube Data API
- **Decisão**: Coleta diária com paginação de todos os comentários e respostas disponíveis.
- **Vantagem**: Censo analítico completo dos canais monitorados.
- **Limitação**: Risco de exaustão da quota de 10.000 unidades diárias da API do YouTube. Para mitigar, os canais alvos e o número máximo de vídeos por canal são controlados via YAML, e vídeos já conhecidos não são duplicados.

## 6. Versionamento de Comentários × Custo de Armazenamento
- **Decisão**: Controle estrito por hash SHA-256 gerando novas versões para alterações e preservando o histórico completo.
- **Vantagem**: Auditoria total de edições e reconstrução temporal precisa.
- **Limitação**: Aumento no volume de dados persistidos no MinIO S3, compensado pelo uso do formato colunar Parquet compactado com Snappy.

## 7. BERTopic × Algoritmos Clássicos
- **Decisão**: BERTopic alimentado com embeddings spaCy e c-TF-IDF.
- **Vantagem**: Descoberta de tópicos semânticos expressivos superiores a centróides puramente euclidianos.
- **Limitação**: Métricas geométricas clássicas (como Silhouette) não capturam adequadamente a qualidade temática de modelos baseados em c-TF-IDF e UMAP não linear.

## 8. Exatamente Uma Palavra por Tópico × Perda de Contexto
- **Decisão**: Apresentação de uma única palavra representativa preservando acentos Unicode (ex: `produção`, `culinária`).
- **Vantagem**: Visualização limpa, objetiva e ideal para rankings de Trend Topics e nuvens de palavras.
- **Limitação**: Uma única palavra pode ser ambígua. Mitigação: o sistema persiste `palavras_auxiliares` (top 10 palavras do cluster) internamente para consulta detalhada no dashboard.

## 9. Reprocessamento Completo × Pipeline Incremental
- **Decisão**: Descoberta incremental na camada Bronze e reavaliação de tendências por janelas móveis temporais na camada Gold.
- **Vantagem**: Otimização do tempo de ingestão sem perda de consistência temporal.
- **Limitação**: O cálculo de tendências nas janelas maiores (14 e 30 dias) exige a leitura de fatias temporais consolidadas do Gold.

## 10. Modo Experimental × Modo Produção
- **Decisão**: Controle via chave `execucao.modo` no `config/configuracao.yaml`.
- **Modo Experimental**: Executa todos os 12 algoritmos para benchmark exaustivo.
- **Modo Produção**: Executa estritamente a lista `modelos_producao` configurada, reduzindo o tempo de processamento diário em até 80%.
