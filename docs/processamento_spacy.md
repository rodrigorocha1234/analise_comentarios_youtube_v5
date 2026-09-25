# Processamento de Texto e Embeddings com spaCy

## Princípios Linguísticos
O pipeline utiliza a biblioteca **spaCy** para todas as etapas de processamento em português brasileiro:
1. **Tokenização**: segmentação de sentenças e palavras.
2. **Normalização**: remoção controlada de URLs e espaços redundantes.
3. **Stopwords Híbridas**: união das stopwords nativas do spaCy (`spacy.lang.pt.stop_words.STOP_WORDS`) com as stopwords configuradas no YAML via `TratadorStopword`.
4. **Lematização**: extração de lemas para redução morfológica.
5. **Preservação de Unicode e Acentos**:
   - É estritamente proibido converter palavras apresentadas ao usuário em formas mutiladas sem acentuação (ex: `produção` -> `producao` ou `produo`). Caracteres latinos com diacríticos e cedilhas são integralmente preservados.

## Embeddings Densos com spaCy
Diferentemente de pipelines que usam SentenceTransformer ou modelos estáticos vazios, o projeto adota o modelo `pt_core_news_md`:
- Possui vetores densos reais de 300 dimensões treinados sobre grandes corpora em português.
- Processamento em lotes via `nlp.pipe(textos, batch_size=256)` para alta performance vetorial.
- O `GeradorEmbedding` valida a existência de vetores antes da execução e compõe uma matriz `np.ndarray` de shape `(N, 300)` que alimenta todos os algoritmos de clustering e o BERTopic.
