class CarteiraVirtual:
    def __init__(self):
        self.saldo = 0  # Saldo em moedas, que também representa os pontos

    def receita(self, quantidade):
        if quantidade < 0:
            return 'A quantidade ganha deve ser positiva.'
        else:
            self.saldo += quantidade
            return f'Operação realizada com sucesso, foram depositados R$:{quantidade} ao seu saldo.'

    def despesa(self, quantidade):
        if quantidade < 0:
            return 'A quantidade gasta deve ser positiva.'
        elif quantidade > self.saldo:
            return 'Saldo insuficiente.'
        else:
            self.saldo -= quantidade
            return f'Operação realizada com sucesso, foram retirados R$:{quantidade} do seu saldo.'

    def consultar_saldo(self):
        return f'Saldo atual: R$:{self.saldo}.'

    @property
    def pontos(self):
        return self.saldo  # O saldo agora também é a pontuação


class Progresso:
    def __init__(self, id_progresso: int, id_usuario: int, id_licao: int, status_progresso: str = "iniciado", pontos_ganho: int = 0):
        self.id_progresso = id_progresso
        self.id_usuario = id_usuario
        self.id_licao = id_licao
        self.status_progresso = status_progresso
        self.pontos_ganho = pontos_ganho

    def atualizar_status(self, novo_status: str, carteira: CarteiraVirtual = None):
        self.status_progresso = novo_status
        if novo_status == "concluído" and carteira and self.pontos_ganho > 0:
            carteira.receita(self.pontos_ganho)

    def adicionar_pontos(self, pontos: int):
        if pontos < 0:
            raise ValueError("Pontos devem ser positivos")
        self.pontos_ganho += pontos

    def to_dict(self):
        return {
            "id_progresso": self.id_progresso,
            "id_usuario": self.id_usuario,
            "id_licao": self.id_licao,
            "status_progresso": self.status_progresso,
            "pontos_ganho": self.pontos_ganho
        }


class Usuario:
    def __init__(self, id: int, nome, email, senha, data_nascimento):
        self.__id = id
        self.__nome = self.inserir_nome(nome)
        self.__email = self.inserir_email(email)
        self.__senha = self.definir_senha(senha)
        self.__data_nascimento = self.validar_data_nascimento(data_nascimento)
        self.__carteira = CarteiraVirtual()
        self.__progressos = []

    def inserir_nome(self, nome):
        if not nome or nome.strip() == '':
            raise ValueError("Nome não pode estar vazio")
        return nome.strip()

    def inserir_email(self, email):
        valid_domains = ['@gmail.com', '@hotmail.com', '@outlook.com']
        if not email or email.strip() == '':
            raise ValueError("Email não pode estar vazio")
        if not any(domain in email for domain in valid_domains):
            raise ValueError("Email inválido! Use @gmail, @hotmail ou @outlook")
        return email.strip()

    def definir_senha(self, senha):
        if not senha or senha.strip() == '':
            raise ValueError("Senha não pode estar vazia")
        return senha.strip()

    def validar_data_nascimento(self, data_nasc):
        try:
            from datetime import datetime
            data = datetime.strptime(data_nasc, '%Y-%m-%d')
            return data.strftime('%d/%m/%Y')
        except ValueError:
            raise ValueError("Data de nascimento inválida. Use o formato YYYY-MM-DD")

    @property
    def id(self):
        return self.__id

    @property
    def nome(self):
        return self.__nome

    @property
    def email(self):
        return self.__email

    @property
    def senha(self):
        return self.__senha

    @property
    def data_nascimento(self):
        return self.__data_nascimento

    def to_dict(self):
        return {
            "id": self.__id,
            "nome": self.__nome,
            "email": self.__email,
            "senha": self.__senha,
            "data_nascimento": self.__data_nascimento,
            "progressos": [progresso.to_dict() for progresso in self.__progressos]
        }

    def mostrar_dados(self):
        print('\n')
        print(f"Nome: {self.__nome}")
        print(f"email: {self.__email}")
        print(f"Data de Nascimento: {self.__data_nascimento}")
        print(f"Saldo da Carteira: {self.__carteira.consultar_saldo()}")
        print(f"Pontuação Total: {self.__carteira.pontos}")
        print("Progressos:")
        for progresso in self.__progressos:
            print(f"  Lição {progresso.id_licao}: {progresso.status_progresso} - {progresso.pontos_ganho} pontos")
        print('\n')

    def adicionar_moedas(self, quantidade):
        return self.__carteira.receita(quantidade)

    def retirar_moedas(self, quantidade):
        return self.__carteira.despesa(quantidade)

    def ver_saldo(self):
        return self.__carteira.consultar_saldo()

    def adicionar_progresso(self, id_progresso: int, id_licao: int):
        progresso = Progresso(id_progresso, self.__id, id_licao)
        self.__progressos.append(progresso)
        return progresso

    def atualizar_progresso(self, id_progresso: int, novo_status: str, pontos: int = 0):
        for progresso in self.__progressos:
            if progresso.id_progresso == id_progresso:
                progresso.atualizar_status(novo_status, self.__carteira)
                if pontos > 0:
                    progresso.adicionar_pontos(pontos)
                return progresso
        raise ValueError("Progresso não encontrado")


class Rank:
    def __init__(self, usuarios, usuario_atual):
        self.usuarios = usuarios
        self.usuario_atual = usuario_atual
        self.ranking = []

    def insertion_sort(self):
        self.ranking = []
        for u in self.usuarios:
            pontos = u._Usuario__carteira.pontos if u._Usuario__carteira is not None else 0
            self.ranking.append([pontos, u])

        for i in range(1, len(self.ranking)):
            chave = self.ranking[i]
            j = i - 1
            while j >= 0 and self.ranking[j][0] < chave[0]:
                self.ranking[j + 1] = self.ranking[j]
                j -= 1
            self.ranking[j + 1] = chave

    def exibir_top10(self):
        self.insertion_sort()
        print("Ranking - Top 10:")
        for i in range(min(10, len(self.ranking))):
            pontuacao, usuario = self.ranking[i]
            print(f"{i + 1}º - {usuario.nome}: {pontuacao} pontos")

    def exibir_rank_usuario(self):
        self.insertion_sort()
        posicao_atual = -1
        for i, (_, usuario) in enumerate(self.ranking):
            if usuario == self.usuario_atual:
                posicao_atual = i + 1
                break
        if posicao_atual > 10 and posicao_atual <= len(self.ranking):
            print("...")
            pontuacao, usuario = self.ranking[posicao_atual - 1]
            print(f"{posicao_atual}º - {usuario.nome}: {pontuacao} pontos")


class Gamificacao:
    def __init__(self, id_gamificacao: int, id_usuario: int, tipo: str, valor: int):
        self.id_gamificacao = id_gamificacao
        self.id_usuario = id_usuario
        self.tipo = self.validar_tipo(tipo)
        self.valor = self.validar_valor(valor)

    def validar_tipo(self, tipo: str) -> str:
        if not isinstance(tipo, str) or tipo.strip() == "":
            raise ValueError("O tipo de gamificação deve ser uma string não vazia.")
        return tipo.strip().lower()

    def validar_valor(self, valor: int) -> int:
        if not isinstance(valor, int) or valor < 0:
            raise ValueError("O valor deve ser um inteiro positivo.")
        return valor

    def aplicar_gamificacao(self, usuario: 'Usuario') -> str:
        if self.id_usuario != usuario.id:
            return "Erro: ID do usuário não corresponde ao ID da gamificação."
        resultado = usuario.adicionar_moedas(self.valor)
        return f"Gamificação '{self.tipo}' aplicada! {resultado}"

    def to_dict(self) -> dict:
        return {
            "id_gamificacao": self.id_gamificacao,
            "id_usuario": self.id_usuario,
            "tipo": self.tipo,
            "valor": self.valor
        }