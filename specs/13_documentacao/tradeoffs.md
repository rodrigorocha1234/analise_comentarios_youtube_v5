# Trade-offs

- spaCy embeddings: arquitetura coerente e simples, mas pode ter menor qualidade semântica que modelos especializados; validar empiricamente o pipeline spaCy escolhido.
- Todos os agrupadores: amplia comparação, mas aumenta custo; executar suíte completa em experimentação e subconjunto aprovado em produção.
- Coleta completa: melhora consistência, mas aumenta quota/tempo; escrita incremental reduz duplicação, não o custo de descoberta.
- BERTopic versus clustering clássico: métricas geométricas não capturam toda a utilidade temática.
- Tópico de uma palavra: excelente para UI/trends, perde contexto; guardar internamente palavras auxiliares.
- Histórico de edição: aumenta armazenamento, mas permite auditoria e análise temporal.
