# Schemas

## Comentário/resposta
Campos mínimos: id_comentario, id_video, id_canal, id_pai opcional, tipo, texto_original, autor quando disponível, data_publicacao, data_atualizacao_youtube, data_coleta, hash_conteudo, versao, ativo.

## Associação de cluster/tópico
id_documento, id_video, id_canal, id_comentario, id_comentario_pai, tipo, numero_cluster, topico, probabilidade, data_publicacao, texto_original, modelo, versao_modelo.

## Tendência
Escopos: vídeo; canal; canal+vídeo. Campos: janela, tópico, cluster, volume, crescimento, aceleração, novidade, volume_normalizado, score_tendencia.
