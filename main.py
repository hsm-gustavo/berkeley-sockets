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
    """
    drift = drift_inicial
    while True:
        msg = receber_objeto(conexao) # espera msg coord
        if not msg:
            break
        if msg['type'] == REQUISITAR_TEMPO: # se coord pedir tempo, responde com timestamp
            tempo_local = time.time() + drift
            enviar_objeto(conexao, {'type': ENVIAR_TEMPO, 'id': id_processo, 'time': tempo_local})
        elif msg['type'] == AJUSTAR_RELOGIO: # se coord enviar ajuste, atualizar o drift do relogio
            drift += msg['offset']
            print(f"Processo {id_processo}: Relógio ajustado em {msg['offset']:.4f} segundos. Novo drift = {drift:.4f}.")
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

    conexoes = [] # para guardar sockets dos clientes conectados
    print(f"Coordenador: Aguardando {NUMERO_DE_PROCESSOS} processos...")
    for _ in range(NUMERO_DE_PROCESSOS):
        conexao, endereco = servidor.accept()
        conexoes.append(conexao)
        print(f"Coordenador: Processo conectado de {endereco}.")

    # solicita tempo dos clientes
    for conn in conexoes:
        enviar_objeto(conn, {'type': REQUISITAR_TEMPO})

    tempos = [] # tuplas (socket, timestamp)
    for conn in conexoes:
        msg = receber_objeto(conn)
        if msg and msg['type'] == ENVIAR_TEMPO:
            print(f"Coordenador: Recebeu tempo {msg['time']:.4f} do processo {msg['id']}.")
            tempos.append((conn, msg['time']))

    # calcula média dos relogios
    tempo_coordenador = time.time()
    all_times = [t for (_, t) in tempos] + [tempo_coordenador] # timestamp de todos os clientes + timestamp do coord
    media = sum(all_times) / len(all_times)
    print(f"Coordenador: Tempo médio = {media:.4f}.")

    # envia ajustes
    for conn, t in tempos:
        offset = media - t # media calculada - timestamp do cliente
        enviar_objeto(conn, {'type': AJUSTAR_RELOGIO, 'offset': offset})

    ajuste_coord = media - tempo_coordenador # ajustando o do coord
    print(f"Coordenador: Ajustando próprio relógio em {ajuste_coord:.4f} segundos.")

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
        threading.Thread(target=executar_processo, args=(id_processo, d, conexao), daemon=True).start()

    # aguarda coord finalizar
    thread_coord.join()
