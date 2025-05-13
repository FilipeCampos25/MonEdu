from datetime import date, datetime


class CarteiraVirtual:
    def __init__(self):
        self.saldo: int = 0  # Saldo em moedas, que também representa os pontos

    def receita(self, quantidade):
        if quantidade < 0:
            return 'A quantidade ganha deve ser positiva.'
        else:
            self.saldo += quantidade
            return f'Operação realizada com sucesso, foram depositados {quantidade} moedas ao seu saldo.'

    def despesa(self, quantidade):
        if quantidade < 0:
            return 'A quantidade gasta deve ser positiva.'
        elif quantidade > self.saldo:
            return 'Saldo insuficiente.'
        else:
            self.saldo -= quantidade
            return f'Operação realizada com sucesso, foram retirados {quantidade} moedas do seu saldo.'

    def consultar_saldo(self):
        return f'Saldo atual: {self.saldo}.'

    @property
    def pontos(self):
        return self.saldo  # O saldo agora também é a pontuação


class Progresso:
    def __init__(self, id_progresso: int, id_usuario: int, id_licao: int, status_progresso: str = "iniciado", pontos_ganho: int = 0):
        self.id_progresso = id_progresso
        self.id_usuario = id_usuario  # Adicionado conforme a lista
        self.id_licao = id_licao
        self.status_progresso = status_progresso
        self.pontos_ganho = pontos_ganho

    def atualizar_status(self, novo_status: str, carteira: CarteiraVirtual = None):
        self.status_progresso = novo_status
        # Sincroniza pontos com a carteira ao concluir
        if novo_status == "concluído" and carteira and self.pontos_ganho > 0:
            carteira.receita(self.pontos_ganho)

    def adicionar_pontos(self, pontos: int):
        if pontos < 0:
            raise ValueError("Pontos devem ser positivos")
        self.pontos_ganho += pontos

    def to_dict(self):
        return {
            "id_progresso": self.id_progresso,
            "id_usuario": self.id_usuario,  # Incluído no dict
            "id_licao": self.id_licao,
            "status_progresso": self.status_progresso,
            "pontos_ganho": self.pontos_ganho
        }


class Usuario:
    def __init__(self, id: int, nome: str, email: str, senha: str, data_nascimento: date):
        self.__id: int = id
        self.__nome: str = nome
        self.__email: str = email
        self.__senha: str = senha
        self.__data_nascimento: date = data_nascimento
        self.__carteira = CarteiraVirtual()
        self.__progressos = {}

    @property
    def id(self) -> int:
        return self.__id

    @property
    def nome(self) -> str:
        return self.__nome

    @nome.setter
    def nome(self, nome: str) -> None:
        if not nome.strip(): # verificar se o nome está em branco
            raise ValueError('nome não pode estar vazio')
        self.__nome = nome

    @property
    def email(self) -> str:
        return self.__email
    
    @email.setter
    def email(self, email: str) -> None:
        valid_domains = ['@gmail.com', '@hotmail.com', '@outlook.com', '@yahoo.com']
        if not email.strip():
            raise ValueError("email não pode estar vazio")
        if not any(email.endswith(domain) for domain in valid_domains):
            raise ValueError("email inválido! Use um dominio, por exemplo: @gmail.com")
        self.__email = email

    @property
    def senha(self) -> str:
        return self.__senha
    
    @senha.setter
    def senha(self, senha: str) -> None:
        if not senha or senha.strip() == '':
            raise ValueError("senha não pode estar vazia")
        self.__senha = senha

    @property
    def data_nascimento(self):
        return self.__data_nascimento
    
    @data_nascimento.setter
    def data_nascimento(self, data_nasc: str) -> None:
        try:
            data = datetime.strptime(data_nasc, '%Y-%m-%d').date()
            self.__data_nascimento = data
        except ValueError:
            raise ValueError("Data de nascimento inválida. Use o formato AAAA-MM-DD")

    def to_dict(self):
        return {
            "id": self.__id,
            "nome": self.__nome,
            "email": self.__email,
            "senha": self.__senha,
            "data_nascimento": self.__data_nascimento.strftime('%Y-%m-%d'),  # Converte para string
            "progressos": [progresso.to_dict() for progresso in self.__progressos]
        }

    def mostrar_dados(self):
        print('\n')
        print(f"Nome: {self.__nome}")
        print(f"email: {self.__email}")
        print(f"Data de Nascimento: {self.__data_nascimento.strftime('%d/%m/%Y')}")
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

    # Método para adicionar um progresso
    def adicionar_progresso(self, id_progresso: int, id_licao: int):
        progresso = Progresso(id_progresso, self.__id, id_licao)
        self.__progressos[id_progresso] = progresso
        return progresso

    # Método para atualizar progresso e sincronizar pontos
    def atualizar_progresso(self, id_progresso: int, novo_status: str, pontos: int = 0):
        progresso = self.__progressos.get(id_progresso)
        if not progresso:
            raise ValueError("Progresso não encontrado")
        progresso.atualizar_status(novo_status, self.__carteira)
        if pontos > 0:
            progresso.adicionar_pontos(pontos)
        return progresso
