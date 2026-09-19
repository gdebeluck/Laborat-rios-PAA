from collections import deque


class Grafo:

    #Método "construtor" do grafo, utilizando lista de adjacência. Grafo não dirigido sempre.
    def __init__(self, numero_vertices: int) -> None:
        self.numero_vertices = numero_vertices
        #Dicionário com todos vértices sendo listas de seus vizinhos.
        self.dic: dict[int, list] = {}
        #inicializa cada vértice como uma lista vazia de vizinhos.
        for i in range(self.numero_vertices):
             self.dic[i] = []
        

    def vertices(self) -> list[int]:
        lista = []
        for i in range(self.numero_vertices):
            lista.append(i) 
        return lista
        #retorna a lista de vertices

    def adicionar_aresta(self, u: int, v: int) -> None:
         
        if v not in self.dic[u]:       # busca linear na lista
            self.dic[u].append(v)
            self.dic[v].append(u)

    def remover_aresta(self, u: int, v: int) -> None:
        #teste se u está na como vizinho de v e o oposto.
        if u in self.dic[v] and v in self.dic[u]:
            #percorre a lista linearmente e remove um do outro.
            self.dic[u].remove(v)
            self.dic[v].remove(u)

    def sao_adjacentes(self, u: int, v: int) -> bool:
        return u in self.dic[v] and v in self.dic[u]

    def grau(self, v: int) -> int:
        return sum(1 for u in self.dic if v in self.dic[u])
    
    def vizinhos(self, v: int) -> list[int]:
        return self.dic[v]
    def tem_ciclos_impares(self) -> bool:
        valores = dict[int, int]()
        for inicio in self.vertices():
            if inicio in valores:
                continue
            valores[inicio] = 0
            fila = deque([inicio])
            while fila:
                u = fila.popleft()
                for v in self.vizinhos(u):
                    if v not in valores:
                        valores[v] = 1 - valores[u]
                        fila.append(v)
                    elif valores[v] == valores[u]:
                        return True
        return False
