# API via MLflow Serving

O serving principal deve ser feito pelo MLflow. A entrada segue a assinatura registrada. A resposta fornece cluster/tópico e demais campos suportados pelo modelo. Endpoints analíticos de tendências e consulta tópico->comentários podem ser atendidos por uma camada de leitura sobre Gold, sem duplicar inferência.

Não usar LLM em nenhuma etapa.
