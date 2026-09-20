class Grafo:
    """Representa um grafo direcionado."""

    def __init__(self) -> None:
        self._adj_list = dict[str, list[str]]()

    def adicionar_vertice(self, v: str) -> None:
        """Adiciona um novo vértice `v` ao grafo."""
        self._adj_list[v] = []

    def adicionar_arco(self, v: str, u: str) -> None:
        """Adiciona um arco de `v` para `u`."""
        self._adj_list[v].append(u)

    def vertices(self) -> list[str]:
        """Retorna a lista dos vértices do grafo."""
        return list(self._adj_list.keys())

    def vizinhos(self, v: str) -> list[str]:
        """Retorna os vértices u tais que existe um arco (v -> u)."""
        return self._adj_list[v]

    def reverso(self) -> "Grafo":
        """Retorna um novo grafo com os mesmos vértices e todos os arcos invertidos."""
        g = Grafo()

        for v in self.vertices():
            g.adicionar_vertice(v)

        for v in self.vertices():
            for u in self.vizinhos(v):
                g.adicionar_arco(u,v)
        return g
