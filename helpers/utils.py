import pickle

# envia objeto python por socket
def enviar_objeto(conexao, objeto):
    dados = pickle.dumps(objeto)
    conexao.sendall(len(dados).to_bytes(4, 'big') + dados)

# recebe o objeto python
def receber_objeto(conexao):
    bytes_tamanho = conexao.recv(4)
    if not bytes_tamanho:
        return None
    tamanho = int.from_bytes(bytes_tamanho, 'big')
    dados = b''
    while len(dados) < tamanho:
        pacote = conexao.recv(tamanho - len(dados))
        if not pacote:
            return None
        dados += pacote
    return pickle.loads(dados)
