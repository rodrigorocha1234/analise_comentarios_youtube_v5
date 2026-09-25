# Tópicos

Cada cluster recebe `numero_cluster` e uma única `palavra_representativa`. O nome público do tópico deve conter exatamente uma palavra. Seleção pode combinar c-TF-IDF, frequência, centralidade e proximidade do centróide. Internamente podem ser preservadas as N melhores palavras para explicabilidade.

A palavra exibida deve preservar acentos e caracteres como ç. Ex.: `produção`, nunca `produo`; `música`, nunca `msica`. Cada tópico deve permitir recuperar os comentários e respostas associados.
