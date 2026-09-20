from collections import deque

from grafo import Grafo


def toposort(g: Grafo) -> deque[str]:
    """Retorna uma ordenação topológica dos vértices, baseada em DFS."""
    pos: deque[str] = deque() # fila para ordenar os vértices
    visited: dict[str, bool] = {}
    for v in g.vertices():
        visited[v]=False

    def dfs_topo(g: Grafo, s: str) -> None:
        nonlocal pos, visited # essa linha significa que a função tem acesso às variáveis `pos` e `visited`
        visited[s] = True
        for v in g.vizinhos(s):
            if not visited[v]:
                dfs_topo(g,v)
        pos.appendleft(s)

    for s in g.vertices():
        if not visited[s]:
            dfs_topo(g,s) # inicia DFS
    return pos


def numero_minimo_bases(g: Grafo) -> int:
    """Retorna o menor número de bases necessário para atender todas as cidades."""

    grafo_reverso = g.reverso() #preparação para usar o Kosaraju
    ordem_topologica = toposort(grafo_reverso) #faz a ordem topológica

    visitados = {v: False for v in g.vertices()}
    quantidade_bases = 0

    def dfs_scc(vertice: str) -> None:
        visitados[vertice] = True
        for vizinho in g.vizinhos(vertice):
            if not visitados[vizinho]:
                dfs_scc(vizinho)

    for v in ordem_topologica:
        if not visitados[v]:
            quantidade_bases += 1 # Identificou um novo componente fortemente conexo (sumidouro disponível)
            dfs_scc(v)            # Explora e isola todos os vértices deste componente
            
    return quantidade_bases


def main() -> None:    
    primeira_linha = input().split()
    numero_cidades = int(primeira_linha[0])
    numero_estradas = int(primeira_linha[1])

    # Lê os rótulos das cidades e cria os vértices do grafo.
    grafo = Grafo()
    rotulos = input().split()
    for rotulo in rotulos:
        grafo.adicionar_vertice(rotulo)

    # Lê as estradas. O terceiro elemento de cada linha informa em quais
    # sentidos a estrada pode ser percorrida.
    for _ in range(numero_estradas):
        estrada = input().split()
        cidade1 = estrada[0]
        cidade2 = estrada[1]
        sentido = estrada[2]

        
        if sentido == "->":
            grafo.adicionar_arco(cidade1, cidade2)
            pass

        elif sentido == "<-":
            grafo.adicionar_arco(cidade2, cidade1)
            pass

        elif sentido == "<>":
            grafo.adicionar_arco(cidade1, cidade2)
            grafo.adicionar_arco(cidade2, cidade1)
            pass

    # As linhas abaixo calculam e imprimem a resposta do problema.
    resposta = numero_minimo_bases(grafo)
    print(resposta)


if __name__ == "__main__":
    main()
