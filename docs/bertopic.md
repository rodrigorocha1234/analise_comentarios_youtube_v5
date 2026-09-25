# BERTopic PT-BR com Embeddings spaCy

## Arquitetura Específica do BERTopic
Diferente da configuração tradicional que utiliza SentenceTransformer por padrão, a implementação `AgrupadorBertopic` foi customizada para satisfazer os requisitos do projeto:
- **Modelo de Embedding**: `embedding_model=None`.
- Os embeddings são gerados previamente pelo pipeline spaCy (`pt_core_news_md`) e fornecidos explicitamente na chamada `modelo.fit_transform(textos, embeddings=embeddings)`.

## Componentes Internos
1. **Redução Dimensional (UMAP)**:
   - Métrica: Cosseno.
   - Componentes: 5.
   - Vizinhos: 15.
   - Ajuste dinâmico quando executado sobre datasets reduzidos ou de teste.
2. **Clustering de Densidade (HDBSCAN)**:
   - Métrica: Euclidiana sobre o espaço reduzido.
   - Método de seleção de cluster: `eom`.
   - `prediction_data=True` para inferência de novos documentos.
3. **Representação Temática (c-TF-IDF & CountVectorizer)**:
   - Unigramas e bigramas (`ngram_range=(1, 2)`).
   - Stopwords em português.
   - `top_n_words=10` para palavras explicativas internas.

## Nomeação com Exatamente UMA Palavra
Embora o BERTopic mantenha as N palavras mais relevantes de cada tópico internamente, a camada de apresentação (`NomeadorTopico`) extrai estritamente **uma única palavra representativa**, garantindo grafia e acentuação corretas. As palavras complementares são mantidas no atributo `palavras_auxiliares` para explicabilidade no dashboard.
