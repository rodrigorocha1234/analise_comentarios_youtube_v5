# MLflow

Aplicar Observer: o pipeline publica eventos de coleta, processamento, embeddings, treinamento, avaliação e publicação; `ObservadorMlflow` registra parâmetros, métricas, tags, artefatos e modelos.

Registrar: algoritmo, hiperparâmetros, quantidade de documentos, clusters, ruído, métricas aplicáveis, duração, versão do dataset, versão do schema e versão do código/configuração.

Versionar assinatura de entrada e saída no MLflow, com `input_example`. Modelo aprovado vai ao Model Registry e é servido pelo MLflow Serving. Nada deve depender de persistência local.
