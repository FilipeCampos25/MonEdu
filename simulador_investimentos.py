import random
import time
import threading
from estrutura_usuario import Usuario

class SimuladorInvestimentos:
    def __init__(self, usuario: Usuario):
        self.usuario = usuario
        self.valor_cota = 50.0
        self.qtd_cotas = 0  # Quantidade de cotas que o usuário possui
        self.volatilidade = 'padrao'
        
        # Inicia as threads para atualização automática
        threading.Thread(target=self.atualizar_valor_cota, daemon=True).start()
        threading.Thread(target=self.alterar_volatilidade, daemon=True).start()

    def atualizar_valor_cota(self):
        while True:
            time.sleep(30)  # Atualiza a cada 30 segundos
            chance = random.randint(1, 100)
            if self.volatilidade == 'padrao':
                if chance <= 50:
                    self.valor_cota *= 1.15  # Valoriza 15%
                else:
                    self.valor_cota *= 0.85  # Desvaloriza 15%
            elif self.volatilidade == 'pico_valorizacao':
                if chance <= 75:
                    self.valor_cota *= 1.15
                else:
                    self.valor_cota *= 0.85
            elif self.volatilidade == 'pico_desvalorizacao':
                if chance <= 25:
                    self.valor_cota *= 1.15
                else:
                    self.valor_cota *= 0.85

            self.valor_cota = round(self.valor_cota, 2)
            print(f'\nValor da cota atualizado: R$ {self.valor_cota}. Valor investido: R$ {self.qtd_cotas * self.valor_cota}')

    def alterar_volatilidade(self):
        while True:
            time.sleep(300)  # Altera a cada 5 minutos
            self.volatilidade = random.choice(['padrao', 'pico_valorizacao', 'pico_desvalorizacao'])
            if self.volatilidade == 'padrao':
                print('tudo permanece calmo na empresa')
            elif self.volatilidade == 'pico_valorizacao':
                print('parece que a empresa tomou boas decisões recentemente')
            elif self.volatilidade == 'pico_desvalorizacao':
                print('a empresa fez uma pessima escolha de negocios recentemente')
            print(f'Modo de volatilidade alterado para: {self.volatilidade}')

    def comprar_vender(self):
        print(f'Saldo atual: {self.usuario.ver_saldo()}\nValor atual da cota: R$ {self.valor_cota}')
        while True:
            opcao = input('Digite C para comprar, V para vender ou S para sair: ').upper()
            if opcao == 'C':
                max_cotas = int(self.usuario._Usuario__carteira.saldo // self.valor_cota)
                print(f'Você é capaz de comprar um total de {max_cotas} cota(s)')
                qtd_input = input('Quantas cotas deseja comprar? ')
                if qtd_input.lower() == 'max':
                    qtd = max_cotas
                else:
                    qtd = int(qtd_input)
                custo = qtd * self.valor_cota
                result = self.usuario.retirar_moedas(custo)
                if 'sucesso' in result:
                    self.qtd_cotas += qtd
                    print(f'Você comprou {qtd} cotas. {result} '
                          f'Valor em cotas: R$ {self.qtd_cotas * self.valor_cota}')
                else:
                    print(result)
            elif opcao == 'V':
                print(f'Você possui um total de {self.qtd_cotas} cotas.')
                qtd = int(input('Quantas cotas deseja vender? '))
                if qtd <= self.qtd_cotas:
                    ganho = qtd * self.valor_cota
                    self.usuario.adicionar_moedas(ganho)
                    self.qtd_cotas -= qtd
                    print(f'Você vendeu {qtd} cotas. Saldo atual: {self.usuario.ver_saldo()} '
                          f'Valor em cotas: R$ {self.qtd_cotas * self.valor_cota}')
                else:
                    print('Você não possui essa quantidade de cotas.')
            elif opcao == 'S':
                break
