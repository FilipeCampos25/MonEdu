import random
import time
import threading

# Valores iniciais
saldo_usuario = 1000
valor_cota = 50
qtd_cotas = 0
volatilidade = 'padrao'

print(f'saldo atual: {saldo_usuario}\nvalor atual da cota: {valor_cota}')


# Funções para volatilidade
def atualizar_valor_cota():
    global valor_cota, volatilidade
    while True:
        time.sleep(30)  # Atualiza a cada 30 segundos
        chance = random.randint(1, 100)
        if volatilidade == 'padrao':
            if chance <= 50:
                valor_cota *= 1.15  # Valoriza 15%
            else:
                valor_cota *= 0.85  # Desvaloriza 15%
        elif volatilidade == 'pico_valorizacao':
            if chance <= 75:
                valor_cota *= 1.15
            else:
                valor_cota *= 0.85
        elif volatilidade == 'pico_desvalorizacao':
            if chance <= 25:
                valor_cota *= 1.15
            else:
                valor_cota *= 0.85

        valor_cota = round(valor_cota, 2)
        print(f'\nValor da cota atualizado: R$ {valor_cota}. Valor investido: R$ {qtd_cotas * valor_cota}')


# Função para alterar volatilidade
def alterar_volatilidade():
    global volatilidade
    while True:
        time.sleep(300)  # Altera a cada 5 minuto
        volatilidade = random.choice(['padrao', 'pico_valorizacao', 'pico_desvalorizacao'])
        if volatilidade == 'padrao':
            print('tudo permanece calmo na empresa')
        elif volatilidade == 'pico_valorizacao':
            print('parece que a empresa tomou boas decisões recentemente')
        elif volatilidade == 'pico_desvalorizacao':
            print('a empresa fez uma pessima escolha de negocios recentemente')
        print(f'Modo de volatilidade alterado para: {volatilidade}')


# Função para compra e venda
def comprar_vender():
    global saldo_usuario, qtd_cotas, valor_cota
    while True:
        opcao = input('Digite C para comprar, V para vender ou S para sair: ').upper()
        if opcao == 'C':
            print(f'Você é capaz de comprar um total de {saldo_usuario // valor_cota} cotas(s)')
            qtd_input = input('Quantas cotas deseja comprar? ')
            if qtd_input.lower() == 'max':
                qtd = saldo_usuario // valor_cota
            else:
                qtd = int(qtd_input)
            custo = qtd * valor_cota
            if custo <= saldo_usuario:
                saldo_usuario -= custo
                qtd_cotas += qtd
                print(f'Você comprou {qtd} cotas. Saldo atual: R$ {saldo_usuario}. '
                      f'Valor em cotas: R$ {qtd_cotas * valor_cota}')
            else:
                print('Saldo insuficiente.')
        elif opcao == 'V':
            print(f'Você possui um total de {qtd_cotas} cotas.')
            qtd = int(input('Quantas cotas deseja vender? '))
            if qtd <= qtd_cotas:
                saldo_usuario += qtd * valor_cota
                qtd_cotas -= qtd
                print(f'Você vendeu {qtd} cotas. Saldo atual: R$ {saldo_usuario}. '
                      f'Valor em cotas: R$ {qtd_cotas * valor_cota}')
            else:
                print('Você não possui essa quantidade de cotas.')
        elif opcao == 'S':
            break


# Threads para atualizações automáticas
threading.Thread(target=atualizar_valor_cota, daemon=True).start()
threading.Thread(target=alterar_volatilidade, daemon=True).start()

# Inicia a interação com o usuário
comprar_vender()