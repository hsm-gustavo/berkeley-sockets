# Implementação do Algoritmo de Sincronização de Berkeley usando Python e Sockets

## Descrição do Projeto
Este projeto implementa o algoritmo de sincronização de relógios de Berkeley, um método para sincronizar relógios em um sistema distribuído. O algoritmo funciona elegendo um coordenador que coleta os tempos de todos os processos, calcula a média e distribui os ajustes necessários.

## Equipe

## Equipe

| Nome | Matrícula |
|---------------|---------------|
| **Caio Teixeira da Silva** | 22112243 |
| **Gustavo Henrique dos Santos Malaquias** | 22111978 |
| **Noemy Torres Pereira** | 22112110 |

---

## Informações Acadêmicas

- **Instituição**: Universidade Federal de Alagoas (UFAL) - Campus Arapiraca
- **Professor**: Tercio de Morais
- **Disciplina**: Sistemas Distribuídos

---
## Arquitetura do Sistema

O sistema é composto por dois tipos de processos:

- **Processo Coordenador**: Responsável por iniciar o algoritmo de sincronização, coletar os tempos dos clientes, calcular a média e distribuir os ajustes.
- **Processos Clientes**: Representam os nós da rede cujos relógios precisam ser sincronizados.

## Como o Algoritmo Funciona

### 1. Inicialização
- O coordenador inicia e aguarda conexões de processos clientes
- Cada processo cliente inicia com um drift de tempo aleatório (entre -10 e +10 segundos)

### 2. Coleta de Tempos
- O coordenador solicita o tempo atual de cada processo
- Cada processo responde com seu tempo local (afetado pelo drift)

### 3. Cálculo da Média
- O coordenador calcula a média de todos os tempos (incluindo o seu próprio)

### 4. Distribuição dos Ajustes
- O coordenador envia a cada processo um offset de ajuste (diferença entre a média e o tempo local)
- Cada processo aplica o offset recebido, ajustando seu relógio local

### 5. Resultado
- Todos os processos (incluindo o coordenador) ficam sincronizados com o tempo médio do sistema

## Como Executar

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/berkeley-sockets.git
cd berkeley-sockets

# Execute o programa
python main.py
```

## Configurações
As configurações do sistema podem ser ajustadas no arquivo `\helpers\constants.py`:

```python
# Número de processos clientes
NUMERO_DE_PROCESSOS = 4

# Configurações do coordenador
HOST_COORDENADOR = 'localhost'
PORTA_COORDENADOR = 10000

# Drift máximo em segundos (intervalo de +/- INTERVALO_DRIFT)
INTERVALO_DRIFT = 10.0
```

## Estrutura do Código

| Arquivo | Descrição |
|---------|-----------|
| `main.py` | Implementação principal do algoritmo com coordenador e clientes |
| `utils.py` | Funções auxiliares para enviar e receber objetos serializados |
| `constants.py` | Constantes e configurações do sistema |

## Detalhes de Implementação

### Comunicação
A comunicação entre processos é realizada através de sockets TCP, utilizando serialização de objetos Python com pickle. Para facilitar o envio e recebimento de objetos, foram criadas funções auxiliares:

```python
def enviar_objeto(conexao, objeto):
    dados = pickle.dumps(objeto)
    conexao.sendall(len(dados).to_bytes(4, 'big') + dados)

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
```

### Mensagens
O sistema utiliza três tipos de mensagens:

| Tipo | Descrição |
|------|-----------|
| `REQUISITAR_TEMPO` | Coordenador solicita o tempo atual de um processo |
| `ENVIAR_TEMPO` | Processo responde com seu tempo local |
| `AJUSTAR_RELOGIO` | Coordenador envia o offset de ajuste para um processo |

### Concorrência
A implementação utiliza threads para simular múltiplos processos executando concorrentemente:

- O coordenador executa em uma thread separada
- Cada processo cliente executa em sua própria thread
- A sincronização entre threads é gerenciada através de mensagens via sockets

## Licença
Este projeto está licenciado sob a licença MIT. Para mais detalhes, consulte o arquivo [LICENSE](https://github.com/hsm-gustavo/berkeley-sockets/blob/main/LICENSE) no repositório.