import socket
import threading
import time
import random

from helpers.utils import enviar_objeto, receber_objeto
from helpers.constants import AJUSTAR_RELOGIO,REQUISITAR_TEMPO,ENVIAR_TEMPO,PORTA_COORDENADOR,HOST_COORDENADOR,NUMERO_DE_PROCESSOS,INTERVALO_DRIFT

# cliente
def executar_processo(id_processo, drift_inicial, conexao):
    """
    Cada processo simula um relógio local com um drift (atrasado ou adiantado).
    Ele aguarda solicitações de tempo (REQUISITAR_TEMPO) e response (ENVIAR_TEMPO), depois aplica ajuste (AJUSTAR_RELOGIO).
    Usa contador de segundos e sleep para avançar o tempo
    """
    drift = drift_inicial
    segundos = 0

    while True:
        time.sleep(1)
        segundos += 1

        msg = receber_objeto(conexao) # espera msg coord
        if not msg:
            break
        if msg['type'] == REQUISITAR_TEMPO: # se coord pedir tempo, responde com timestamp
            tempo_local = segundos + drift
            print(f"Processo {id_processo}: Tempo atual (antes do ajuste) = {tempo_local:.4f} segundos.")
            enviar_objeto(conexao, {'type': ENVIAR_TEMPO, 'id': id_processo, 'time': tempo_local})
        elif msg['type'] == AJUSTAR_RELOGIO: # se coord enviar ajuste, atualizar o drift do relogio
            tempo_antes = segundos + drift # tempo antes do ajuste para log
            offset = msg['offset'] # ajuste
            drift += offset
            tempo_depois = segundos + drift # tempo depois do ajuste
            print(f"Processo {id_processo}: Tempo antes = {tempo_antes:.4f} segundos, após ajuste = {tempo_depois:.4f} segundos. Offset aplicado = {offset:.4f} segundos.")
            break
    conexao.close()

# coord
def executar_coordenador():
    """
    Função principal do coordenador: aceita conexões, solicita tempo aos clientes, calcula média e envia o ajuste.
    """
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind((HOST_COORDENADOR, PORTA_COORDENADOR))
    servidor.listen(NUMERO_DE_PROCESSOS)

    drift_coord = 0 # sem desvio inicial
    segundos_coord = 0 # contador de segundos

    conexoes = [] # para guardar sockets dos clientes conectados
    print(f"Coordenador: Aguardando {NUMERO_DE_PROCESSOS} processos...")
    for _ in range(NUMERO_DE_PROCESSOS):
        conexao, endereco = servidor.accept()
        conexoes.append(conexao)
        print(f"Coordenador: Processo conectado de {endereco}.")

    time.sleep(1)
    segundos_coord += 1

    # solicita tempo dos clientes
    for conn in conexoes:
        enviar_objeto(conn, {'type': REQUISITAR_TEMPO})

    tempos = [] # tuplas (socket, timestamp)
    for conn in conexoes:
        msg = receber_objeto(conn)
        if msg and msg['type'] == ENVIAR_TEMPO:
            print(f"Coordenador: Recebeu tempo {msg['time']:.4f} segundos do processo {msg['id']}.")
            tempos.append((conn, msg['time']))

    # calcula média dos relogios
    tempo_coordenador = segundos_coord + drift_coord
    all_times = [t for (_, t) in tempos] + [tempo_coordenador] # timestamp de todos os clientes + timestamp do coord
    media = sum(all_times) / len(all_times)
    print(f"Coordenador: Tempo próprio = {tempo_coordenador:.4f} segundos.")
    print(f"Coordenador: Tempo médio = {media:.4f} segundos.")

    # envia ajustes
    for conn, t in tempos:
        offset = media - t # media calculada - timestamp do cliente
        enviar_objeto(conn, {'type': AJUSTAR_RELOGIO, 'offset': offset})

    ajuste_coord = media - tempo_coordenador # ajustando o do coord
    tempo_antes = tempo_coordenador
    tempo_depois = tempo_coordenador + ajuste_coord
    print(f"Coordenador: Tempo antes = {tempo_antes:.4f} segundos, após ajuste = {tempo_depois:.4f} segundos. Offset aplicado = {ajuste_coord:.4f} segundos.")

    # fechando conexoes
    for conn, _ in tempos:
        conn.close()
    servidor.close()

if __name__ == '__main__':
    # inicia o coordenador em thread para aceitar conexoes antes dos clientes
    thread_coord = threading.Thread(target=executar_coordenador, daemon=True)
    thread_coord.start()

    time.sleep(0.5)  # tempo de espera pra garantir que o coord esteja pronto para aceitar conexoes

    # drifts aleatorios e iniciando clientes
    drifts = [random.uniform(-INTERVALO_DRIFT, INTERVALO_DRIFT) for _ in range(NUMERO_DE_PROCESSOS)]
    for id_processo, d in enumerate(drifts, start=1):
        print(f"Processo {id_processo}: drift inicial = {d:.4f} segundos.")
        conexao = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conexao.connect((HOST_COORDENADOR, PORTA_COORDENADOR))
        threading.Thread(target=executar_processo, args=(id_processo, d, conexao), daemon=False).start()

    # aguarda coord finalizar
    thread_coord.join()
