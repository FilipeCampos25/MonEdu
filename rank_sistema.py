class Rank:
    def __init__(self, usuarios, usuario_atual):
        self.usuarios = usuarios  # Lista de objetos da classe Usuario
        self.usuario_atual = usuario_atual  # Objeto Usuario do usuário que está vendo
        self.ranking = []  # Lista para armazenar pares [pontuacao, usuario]

    def insertion_sort(self):
        # Copia os dados para ranking como pares [pontuacao, usuario]
        self.ranking = []
        for u in self.usuarios:
            pontos = u._Usuario__carteira.pontos if u._Usuario__carteira is not None else 0
            self.ranking.append([pontos, u])

        # Algoritmo Insertion Sort
        for i in range(1, len(self.ranking)):
            chave = self.ranking[i]
            j = i - 1
            while j >= 0 and self.ranking[j][0] < chave[0]:  # Ordem decrescente
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

        # Encontra a posição do usuário atual
        posicao_atual = -1
        for i, (_, usuario) in enumerate(self.ranking):
            if usuario == self.usuario_atual:
                posicao_atual = i + 1
                break

        # Se o usuário não está no top 10, mostra sua posição
        if posicao_atual > 10 and posicao_atual <= len(self.ranking):
            print("...")
            pontuacao, usuario = self.ranking[posicao_atual - 1]
            print(f"{posicao_atual}º - {usuario.nome}: {pontuacao} pontos")