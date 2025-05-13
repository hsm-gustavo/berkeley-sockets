# config
NUMERO_DE_PROCESSOS = 4
HOST_COORDENADOR = 'localhost'
PORTA_COORDENADOR = 10000
INTERVALO_DRIFT = 10.0  # desvio máximo em segundos

# tipos de mensagem
REQUISITAR_TEMPO = 'REQUISITAR_TEMPO' # coord pede timestamp para cliente
ENVIAR_TEMPO = 'ENVIAR_TEMPO' # cliente envia timestamp pro coord
AJUSTAR_RELOGIO = 'AJUSTAR_RELOGIO' # coord envia ajuste pro cliente
