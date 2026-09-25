# BERTopic PT-BR

BERTopic deve receber embeddings gerados pelo spaCy, sem SentenceTransformer na inferência deste projeto. Pipeline: embeddings spaCy -> UMAP -> HDBSCAN -> BERTopic/c-TF-IDF.

Configuração inicial: UMAP n_neighbors=15, n_components=5, min_dist=0.0, metric=cosine, random_state=42; HDBSCAN min_cluster_size=15, min_samples=5, metric=euclidean, cluster_selection_method=eom, prediction_data=true; CountVectorizer com stopwords PT-BR, ngram_range 1-2, min_df 3, max_df 0.90, max_features 10000. Todos os valores devem ser externalizados no YAML.

Treinamento conceitual: `modelo.fit_transform(documentos, embeddings)`; a matriz `embeddings` vem do spaCy.
