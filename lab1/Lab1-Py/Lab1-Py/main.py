from grafo import Grafo


def main() -> None:

    n = int(input())
    caes = Grafo(n)

    for i in range(n):
        linha = input().split()
        for j in range(n):
            if linha[j] == "I":
                caes.adicionar_aresta(i,j)

    if caes.tem_ciclos_impares():
        print("NAO\n")
    else:
        print("SIM\n")


if __name__ == "__main__":
    main()
