# Suíte de Agrupamentos e Padrão Strategy

## Algoritmos Implementados
O projeto disponibiliza 12 algoritmos não supervisionados organizados no padrão GoF Strategy sob `src/agrupadores/`:

| Algoritmo | Classe | Família / Paradigma | Tratamento de Ruído | Probabilidades Nativas |
| :--- | :--- | :--- | :--- | :--- |
| **KMeans** | `AgrupadorKmeans` | Particionamento por centróides | Não | Derivadas do inverso da distância |
| **MiniBatchKMeans** | `AgrupadorMinibatch` | Particionamento estocástico por lotes | Não | Derivadas do inverso da distância |
| **DBSCAN** | `AgrupadorDbscan` | Baseado em densidade com eps | Sim (rótulo -1) | Binária (1.0 núcleo, 0.0 ruído) |
| **HDBSCAN** | `AgrupadorHdbscan` | Densidade hierárquica (HDBSCAN) | Sim (rótulo -1) | Sim (probabilities_) |
| **OPTICS** | `AgrupadorOptics` | Densidade por ordenação de pontos | Sim (rótulo -1) | Binária |
| **Agglomerative** | `AgrupadorAglomerativo` | Hierárquico aglomerativo | Não | Unitária |
| **GaussianMixture** | `AgrupadorGaussiano` | Misturas gaussianas probabilísticas | Não | Sim (predict_proba) |
| **Spectral** | `AgrupadorEspectral` | Grafo de afinidade espectral | Não | Unitária |
| **AffinityPropagation** | `AgrupadorAfinidade` | Propagação de mensagens entre exemplares | Não | Unitária |
| **MeanShift** | `AgrupadorMedia` | Deslocamento iterativo de média | Não | Unitária |
| **BIRCH** | `AgrupadorBirch` | Hierárquico baseado em árvores CF | Não | Unitária |
| **BERTopic** | `AgrupadorBertopic` | Tópicos neurais via UMAP + HDBSCAN + c-TF-IDF | Sim (rótulo -1) | Sim (calculate_probabilities) |

## Métricas de Avaliação
Calculadas pelo `ServicoAgrupamento`:
- **Silhouette Score**: Coesão e separação com distância cosseno.
- **Davies-Bouldin Score**: Similaridade média inter-cluster.
- **Calinski-Harabasz Score**: Razão de dispersão entre/intra-clusters.
- **Percentual de Ruído**: Proporção de documentos classificados como -1.
- **Distribuição de Tamanhos**: Maior, menor e média de documentos por cluster.
- **Tempos de Execução**: Tempo de treino e tempo de inferência.
