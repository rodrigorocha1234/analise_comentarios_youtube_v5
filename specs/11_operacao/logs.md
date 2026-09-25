# Logs e operação

Mensagens INFO devem indicar claramente a etapa: início da coleta, vídeos encontrados, sincronização de comentários/respostas, gravação Bronze, processamento spaCy, geração de embeddings, execução de cada algoritmo, cálculo de tendências, registro MLflow e atualização Gold.

Não registrar segredos nem texto integral quando isso não for necessário. Erros devem incluir contexto técnico suficiente para reprocessamento.
