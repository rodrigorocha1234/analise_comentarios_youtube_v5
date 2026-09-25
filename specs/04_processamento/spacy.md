# Processamento spaCy

spaCy executa tokenização, lematização, stopwords, normalização textual e embeddings. Usar `nlp.pipe` em lotes. Stopwords = `nlp.Defaults.stop_words` unidas às stopwords configuradas no YAML.

O modelo configurado para embeddings deve fornecer vetores semanticamente úteis; validar `doc.vector`/vetores antes da produção. `pt_core_news_sm` pode ser usado para processamento linguístico, mas não deve ser presumido como fonte de vetores densos adequados sem validação.

Não remover acentos/cedilha da palavra apresentada ao usuário. Normalização auxiliar para comparação pode existir, mas a grafia exibida deve preservar Unicode.
