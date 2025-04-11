from estrutura_usuario import Usuario

class Gamificacao:
    def __init__(self, id_gamificacao: int, id_usuario: int, tipo: str, valor: int):
        self.id_gamificacao = id_gamificacao
        self.id_usuario = id_usuario
        self.tipo = self.validar_tipo(tipo)  # Tipo de gamificação (ex.: "desafio", "missão", "conquista")
        self.valor = self.validar_valor(valor)  # Valor em pontos/moedas associado à gamificação

    def validar_tipo(self, tipo: str) -> str:
        """Valida se o tipo de gamificação é uma string não vazia."""
        if not isinstance(tipo, str) or tipo.strip() == "":
            raise ValueError("O tipo de gamificação deve ser uma string não vazia.")
        return tipo.strip().lower()

    def validar_valor(self, valor: int) -> int:
        """Valida se o valor é um inteiro positivo."""
        if not isinstance(valor, int) or valor < 0:
            raise ValueError("O valor deve ser um inteiro positivo.")
        return valor

    def aplicar_gamificacao(self, usuario: 'Usuario') -> str:
        """
        Aplica a gamificação ao usuário, adicionando o valor à carteira virtual.
        Retorna uma mensagem de sucesso ou erro.
        """
        if self.id_usuario != id(usuario):  # Supondo que o usuário tenha um método ou atributo id
            return "Erro: ID do usuário não corresponde ao ID da gamificação."
        
        resultado = usuario.adicionar_moedas(self.valor)
        return f"Gamificação '{self.tipo}' aplicada! {resultado}"

    def to_dict(self) -> dict:
        """Converte a gamificação em um dicionário para serialização."""
        return {
            "id_gamificacao": self.id_gamificacao,
            "id_usuario": self.id_usuario,
            "tipo": self.tipo,
            "valor": self.valor
        }
    