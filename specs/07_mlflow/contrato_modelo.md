# Contrato do modelo

## Entrada lógica
- texto: string
- id_video: string
- id_canal: string

## Saída lógica
- numero_cluster: inteiro
- topico: string de uma palavra
- probabilidade: float opcional conforme algoritmo

Versionar `schema_entrada`, `schema_saida` e versão do modelo. Para modelos sem probabilidade nativa, definir contrato explícito sem inventar probabilidade.
