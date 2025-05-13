import math

# Taxas iniciais (podem ser alteradas pelo usuário)
investimentos = {
    "CDB": 0.08,           # 8% ao ano
    "Tesouro Direto": 0.06, # 6% ao ano
    "FIIs": 0.07,          # 7% ao ano
    "Ações": 0.10          # 10% ao ano
}

def configurar_taxas():
    print("\n=== Configurar Taxas de Investimentos ===")
    print("Digite as novas taxas anuais (em %, ex.: 8 para 8%) ou pressione Enter para manter a taxa atual.")
    
    global investimentos
    for investimento in investimentos:
        taxa_atual = investimentos[investimento] * 100  # Converte para %
        nova_taxa = input(f"Taxa para {investimento} (atual: {taxa_atual}%): ")
        if nova_taxa.strip():  # Verifica se o usuário digitou algo
            try:
                investimentos[investimento] = float(nova_taxa) / 100  # Converte para decimal
            except ValueError:
                print(f"Taxa inválida para {investimento}. Mantendo {taxa_atual}%.")
        else:
            print(f"Taxa para {investimento} mantida em {taxa_atual}%.")

def simulador_rentabilidade():
    print("\n=== Simulador de Rentabilidade ===")
    print("Compare: CDB, Tesouro Direto, FIIs, Ações")
    
    valor_inicial = float(input("Digite o valor inicial investido (R$): "))
    aporte_mensal = float(input("Digite o aporte mensal (R$, ou 0 para nenhum): "))
    tempo_anos = int(input("Digite o tempo de investimento (anos): "))
    
    print("\nResultados (juros compostos com aportes):")
    for investimento, taxa in investimentos.items():
        # Cálculo com aporte inicial
        valor_final = valor_inicial * (1 + taxa) ** tempo_anos
        # Adiciona aportes mensais
        if aporte_mensal > 0:
            meses = tempo_anos * 12
            taxa_mensal = (1 + taxa) ** (1/12) - 1
            for _ in range(meses):
                valor_final = valor_final * (1 + taxa_mensal) + aporte_mensal
        
        print(f"{investimento}: R${valor_final:.2f} (Retorno: R${valor_final - valor_inicial - aporte_mensal * tempo_anos * 12:.2f})")

def calculadora_dividendos():
    print("\n=== Calculadora de Dividendos ===")
    valor_inicial = float(input("Digite o valor inicial investido (R$): "))
    aporte_mensal = float(input("Digite o aporte mensal (R$, ou 0 para nenhum): "))
    dy_anual = float(input("Digite o Dividend Yield anual (%): ")) / 100
    tempo_anos = int(input("Digite o tempo de investimento (anos): "))
    
    valor_final = valor_inicial
    total_dividendos = 0
    
    # Simulação com reinvestimento de dividendos e aportes
    meses = tempo_anos * 12
    for _ in range(meses):
        # Dividendos mensais (aproximado)
        dividendos = valor_final * (dy_anual / 12)
        total_dividendos += dividendos
        valor_final += dividendos + aporte_mensal
    
    print(f"Dividendos acumulados: R${total_dividendos:.2f}")
    print(f"Valor total após {tempo_anos} anos: R${valor_final:.2f}")

def independencia_financeira():
    print("\n=== Projeção de Independência Financeira ===")
    meta = float(input("Digite sua meta financeira (R$): "))
    aporte_mensal = float(input("Digite o aporte mensal (R$): "))
    rentabilidade_anual = float(input("Digite a rentabilidade anual esperada (%): ")) / 100
    
    # Fórmula de juros compostos com aportes mensais
    meses = 0
    saldo = 0
    taxa_mensal = (1 + rentabilidade_anual) ** (1/12) - 1
    
    while saldo < meta:
        saldo = saldo * (1 + taxa_mensal) + aporte_mensal
        meses += 1
    
    anos = meses / 12
    print(f"Você alcançará R${meta:.2f} em aproximadamente {anos:.1f} anos.")
    print(f"Saldo final: R${saldo:.2f}")

def main():
    while True:
        print("\n=== Calculadora de Investimentos ===")
        print("1. Simulador de Rentabilidade")
        print("2. Calculadora de Dividendos")
        print("3. Projeção de Independência Financeira")
        print("4. Configurar Taxas de Investimentos")
        print("5. Sair")
        
        opcao = input("Escolha uma opção (1-5): ")
        
        if opcao == "1":
            simulador_rentabilidade()
        elif opcao == "2":
            calculadora_dividendos()
        elif opcao == "3":
            independencia_financeira()
        elif opcao == "4":
            configurar_taxas()
        elif opcao == "5":
            print("Sair...")
            break
        else:
            print("Opção inválida! Tente novamente.")

if __name__ == "__main__":
    main()