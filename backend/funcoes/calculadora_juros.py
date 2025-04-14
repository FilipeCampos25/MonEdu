def calcular_juros():
    try:
        # Solicita os valores ao usuário via input
        principal = float(input("Digite o valor principal (R$): "))
        taxa = float(input("Digite a taxa de juros (% ao período): ")) / 100
        tempo = float(input("Digite o tempo (períodos): "))

        # Pergunta sobre o tipo de juros
        tipo = int(input("Escolha o tipo de juros (1 para Simples, 2 para Compostos): "))

        if tipo == 1:  # Juros Simples
            juros = principal * taxa * tempo
            total = principal + juros
            print(f"\nJuros Simples: R${juros:.2f}")
            print(f"Total: R${total:.2f}")
        elif tipo == 2:  # Juros Compostos
            total = principal * (1 + taxa) ** tempo
            juros = total - principal
            print(f"\nJuros Compostos: R${juros:.2f}")
            print(f"Total: R${total:.2f}")
        else:
            print("Tipo de juros inválido! Use 1 para Simples ou 2 para Compostos.")

    except ValueError:
        print("Erro: Por favor, insira valores numéricos válidos")


def main():
    while True:
        print("\n=== Calculadora de Juros ===")
        calcular_juros()

        # Pergunta se o usuário quer continuar
        continuar = input("\nDeseja fazer outro cálculo? (s/n): ").lower()
        if continuar != 's':
            print("Encerrando a calculadora...")
            break


if __name__ == "__main__":
    main()