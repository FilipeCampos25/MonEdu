import asyncio
import platform
from datetime import datetime, timedelta
import uuid

class BudgetManager:
    def __init__(self):
        self.planilhas = {}
        self.renda_total = 0
        self.despesa_fixa_total = 0
        self.despesa_variavel_total = 0
        self.investido = 0
        self.sobra_total = 0
        self.despesa_total = 0
        self.last_update = None
        self.update_delay = timedelta(days=3)

    # Funções por chamada
    def criar_planilha(self, nome_planilha):
        planilha_id = str(uuid.uuid4())
        self.planilhas[planilha_id] = {
            'nome': nome_planilha,
            'rendas': {},
            'despesas_fixas': {'investido': {'valor': 0}},
            'despesas_variaveis': {},
            'resumo': {}
        }
        self.gerar_planilha_inicial(planilha_id)
        return planilha_id

    def inserir_renda(self, planilha_id, nome, valor, tipo, tempo=1):
        if planilha_id not in self.planilhas:
            raise ValueError("Planilha não encontrada")
        if tipo not in ['continua', 'temporaria']:
            raise ValueError("Tipo deve ser 'continua' ou 'temporaria'")
        self.planilhas[planilha_id]['rendas'][nome] = {
            'valor': valor,
            'tipo': tipo,
            'tempo': tempo if tipo == 'temporaria' else None
        }
        self.renda_total += valor
        self.calcular_contas(planilha_id)

    def alterar_renda(self, planilha_id, nome, novo_nome, novo_valor, novo_tempo=1):
        if planilha_id not in self.planilhas or nome not in self.planilhas[planilha_id]['rendas']:
            raise ValueError("Renda ou planilha não encontrada")
        renda = self.planilhas[planilha_id]['rendas'][nome]
        self.renda_total -= renda['valor']
        renda['valor'] = novo_valor
        if renda['tipo'] == 'temporaria':
            renda['tempo'] = novo_tempo
        if nome != novo_nome:
            self.planilhas[planilha_id]['rendas'][novo_nome] = renda
            del self.planilhas[planilha_id]['rendas'][nome]
        self.renda_total += novo_valor
        self.calcular_contas(planilha_id)

    def remover_renda(self, planilha_id, nome):
        if planilha_id not in self.planilhas or nome not in self.planilhas[planilha_id]['rendas']:
            raise ValueError("Renda ou planilha não encontrada")
        renda = self.planilhas[planilha_id]['rendas'][nome]
        self.renda_total -= renda['valor']
        del self.planilhas[planilha_id]['rendas'][nome]
        self.calcular_contas(planilha_id)

    def alterar_investimentos(self, planilha_id, novo_valor):
        if planilha_id not in self.planilhas:
            raise ValueError("Planilha não encontrada")
        self.investido = novo_valor
        self.planilhas[planilha_id]['despesas_fixas']['investido']['valor'] = novo_valor
        self.calcular_contas(planilha_id)

    def inserir_despesa_fixa(self, planilha_id, nome, valor, tipo, tempo=1):
        if planilha_id not in self.planilhas:
            raise ValueError("Planilha não encontrada")
        if tipo not in ['continua', 'temporaria']:
            raise ValueError("Tipo deve ser 'continua' ou 'temporaria'")
        self.planilhas[planilha_id]['despesas_fixas'][nome] = {
            'valor': valor,
            'tipo': tipo,
            'tempo': tempo if tipo == 'temporaria' else None
        }
        self.despesa_fixa_total += valor
        self.calcular_contas(planilha_id)

    def alterar_despesa_fixa(self, planilha_id, nome, novo_nome, novo_valor, novo_tempo=1):
        if planilha_id not in self.planilhas or nome not in self.planilhas[planilha_id]['despesas_fixas']:
            raise ValueError("Despesa ou planilha não encontrada")
        despesa = self.planilhas[planilha_id]['despesas_fixas'][nome]
        self.despesa_fixa_total -= despesa['valor']
        despesa['valor'] = novo_valor
        if despesa['tipo'] == 'temporaria':
            despesa['tempo'] = novo_tempo
        if nome != novo_nome:
            self.planilhas[planilha_id]['despesas_fixas'][novo_nome] = despesa
            del self.planilhas[planilha_id]['despesas_fixas'][nome]
        self.despesa_fixa_total += novo_valor
        self.calcular_contas(planilha_id)

    def remover_despesa_fixa(self, planilha_id, nome):
        if planilha_id not in self.planilhas or nome not in self.planilhas[planilha_id]['despesas_fixas']:
            raise ValueError("Despesa ou planilha não encontrada")
        despesa = self.planilhas[planilha_id]['despesas_fixas'][nome]
        self.despesa_fixa_total -= despesa['valor']
        del self.planilhas[planilha_id]['despesas_fixas'][nome]
        self.calcular_contas(planilha_id)

    def inserir_despesa_variavel(self, planilha_id, nome, valor, tempo=1, juros=0):
        if planilha_id not in self.planilhas:
            raise ValueError("Planilha não encontrada")
        valor_com_juros = valor * (1 + juros / 100)
        self.planilhas[planilha_id]['despesas_variaveis'][nome] = {
            'valor': valor_com_juros,
            'tempo': tempo
        }
        self.despesa_variavel_total += valor_com_juros
        self.calcular_contas(planilha_id)

    def remover_despesa_variavel(self, planilha_id, nome):
        if planilha_id not in self.planilhas or nome not in self.planilhas[planilha_id]['despesas_variaveis']:
            raise ValueError("Despesa ou planilha não encontrada")
        despesa = self.planilhas[planilha_id]['despesas_variaveis'][nome]
        self.despesa_variavel_total -= despesa['valor']
        del self.planilhas[planilha_id]['despesas_variaveis'][nome]
        self.calcular_contas(planilha_id)

    def atualizar_manual(self, planilha_id):
        if planilha_id not in self.planilhas:
            raise ValueError("Planilha não encontrada")
        self.last_update = datetime.now()
        self.atualizacao_mensal(planilha_id)

    # Funções automáticas
    def gerar_planilha_inicial(self, planilha_id):
        if planilha_id not in self.planilhas:
            raise ValueError("Planilha não encontrada")
        planilha = self.planilhas[planilha_id]
        planilha['rendas'] = {}
        planilha['despesas_fixas'] = {'investido': {'valor': 0}}
        planilha['despesas_variaveis'] = {}
        planilha['resumo'] = {
            'renda_total': 0,
            'despesa_total': 0,
            'investido': 0,
            'sobra_total': 0
        }

    def atualizacao_mensal(self, planilha_id):
        if planilha_id not in self.planilhas:
            raise ValueError("Planilha não encontrada")
        planilha = self.planilhas[planilha_id]

        # Atualizar rendas temporárias
        rendas_remover = []
        for nome, renda in planilha['rendas'].items():
            if renda['tipo'] == 'temporaria':
                renda['tempo'] -= 1
                if renda['tempo'] <= 0:
                    rendas_remover.append(nome)
        for nome in rendas_remover:
            self.remover_renda(planilha_id, nome)

        # Atualizar despesas fixas temporárias
        despesas_fixas_remover = []
        for nome, despesa in planilha['despesas_fixas'].items():
            if nome != 'investido' and despesa['tipo'] == 'temporaria':
                despesa['tempo'] -= 1
                if despesa['tempo'] <= 0:
                    despesas_fixas_remover.append(nome)
        for nome in despesas_fixas_remover:
            self.remover_despesa_fixa(planilha_id, nome)

        # Atualizar despesas variáveis
        despesas_variaveis_remover = []
        for nome, despesa in planilha['despesas_variaveis'].items():
            despesa['tempo'] -= 1
            if despesa['tempo'] <= 0:
                despesas_variaveis_remover.append(nome)
        for nome in despesas_variaveis_remover:
            self.remover_despesa_variavel(planilha_id, nome)

        self.calcular_contas(planilha_id)

    def calcular_contas(self, planilha_id):
        if planilha_id not in self.planilhas:
            raise ValueError("Planilha não encontrada")
        self.despesa_total = self.despesa_fixa_total + self.despesa_variavel_total
        self.sobra_total = self.renda_total - (self.despesa_total + self.investido)
        planilha = self.planilhas[planilha_id]
        planilha['resumo'] = {
            'renda_total': self.renda_total,
            'despesa_total': self.despesa_total,
            'investido': self.investido,
            'sobra_total': self.sobra_total
        }

    def mostrar_resumo(self, planilha_id):
        if planilha_id not in self.planilhas:
            raise ValueError("Planilha não encontrada")
        resumo = self.planilhas[planilha_id]['resumo']
        return {
            'renda_total': resumo['renda_total'],
            'despesa_total': resumo['despesa_total'],
            'investido': resumo['investido'],
            'sobra_total': resumo['sobra_total']
        }

    def conselho_do_sistema(self, planilha_id):
        if planilha_id not in self.planilhas:
            raise ValueError("Planilha não encontrada")
        resumo = self.planilhas[planilha_id]['resumo']
        if resumo['renda_total'] == 0:
            return {"error": "Nenhuma renda registrada"}

        # Calcular percentuais
        perc_despesas = ((resumo['despesa_total'] + resumo['investido']) / resumo['renda_total']) * 100
        perc_lazer = (resumo['sobra_total'] / resumo['renda_total']) * 100
        perc_investido = (resumo['investido'] / resumo['renda_total']) * 100

        # Conselho 50/30/20
        conselho = {
            'recomendado': {
                'despesas': 50,
                'lazer': 30,
                'investimentos': 20
            },
            'atual': {
                'despesas': round(perc_despesas, 2),
                'lazer': round(perc_lazer, 2),
                'investimentos': round(perc_investido, 2)
            }
        }
        return conselho

    def grafico(self, planilha_id):
        conselho = self.conselho_do_sistema(planilha_id)
        if 'error' in conselho:
            return conselho
        return {
            'percentuais': conselho['atual']
        }

async def main():
    budget = BudgetManager()
    # Exemplo de uso
    planilha_id = budget.criar_planilha("Orçamento Pessoal")
    budget.inserir_renda(planilha_id, "Salário", 5000, "continua")
    budget.inserir_despesa_fixa(planilha_id, "Aluguel", 1500, "continua")
    budget.inserir_despesa_variavel(planilha_id, "Compras", 500, 1)
    budget.alterar_investimentos(planilha_id, 1000)
    print(budget.mostrar_resumo(planilha_id))
    print(budget.conselho_do_sistema(planilha_id))
    print(budget.grafico(planilha_id))

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())