import os
import random
import sys


RODADAS = 30
SEMENTE = 731_927


def cores_ativas() -> bool:
    if not sys.stdout.isatty():
        return False
    if os.name != "nt":
        return True
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)
        modo = ctypes.c_uint()
        if not kernel32.GetConsoleMode(handle, ctypes.byref(modo)):
            return False
        return bool(kernel32.SetConsoleMode(handle, modo.value | 0x0004))
    except Exception:
        return False


USAR_CORES = cores_ativas()
VERDE = "\033[92m" if USAR_CORES else ""
VERMELHO = "\033[91m" if USAR_CORES else ""
AMARELO = "\033[93m" if USAR_CORES else ""
NEGRITO = "\033[1m" if USAR_CORES else ""
RESET = "\033[0m" if USAR_CORES else ""


class FalhaTeste(Exception):
    def __init__(self, ponto: str, esperado: object, obtido: object) -> None:
        super().__init__(ponto)
        self.ponto = ponto
        self.esperado = esperado
        self.obtido = obtido


def exigir(condicao: bool, ponto: str, esperado: object, obtido: object) -> None:
    if not condicao:
        raise FalhaTeste(ponto, esperado, obtido)


def chamar(funcao, ponto: str):
    try:
        return funcao()
    except Exception as erro:
        raise FalhaTeste(ponto, "nenhuma exceção", f"{type(erro).__name__}: {erro}") from erro


def verificar_vertices(grafo, vertices_esperados: set[int]) -> list[int]:
    vertices = chamar(grafo.vertices, "vertices()")
    exigir(isinstance(vertices, list), "vertices()", "uma lista de inteiros", type(vertices).__name__)
    exigir(all(isinstance(v, int) and not isinstance(v, bool) for v in vertices), "vertices()", "somente identificadores inteiros", vertices)
    exigir(len(vertices) == len(set(vertices)), "vertices()", "identificadores sem repetição", vertices)
    exigir(set(vertices) == vertices_esperados, "vertices()", sorted(vertices_esperados), vertices)
    return vertices


def verificar_estado(grafo, vertices_esperados: set[int], arestas: set[tuple[int, int]]) -> None:
    vertices = sorted(verificar_vertices(grafo, vertices_esperados))
    vizinhanca = {v: set[int]() for v in vertices}

    for u, v in arestas:
        vizinhanca[u].add(v)
        vizinhanca[v].add(u)

    for v in vertices:
        vizinhos = chamar(lambda v=v: grafo.vizinhos(v), f"vizinhos({v})")
        exigir(isinstance(vizinhos, list), f"vizinhos({v})", "uma lista", type(vizinhos).__name__)
        exigir(len(vizinhos) == len(set(vizinhos)), f"vizinhos({v})", f"sem repetições; vizinhos = {sorted(vizinhanca[v])}", vizinhos)
        exigir(set(vizinhos) == vizinhanca[v], f"vizinhos({v})", sorted(vizinhanca[v]), vizinhos)

        grau = chamar(lambda v=v: grafo.grau(v), f"grau({v})")
        exigir(grau == len(vizinhanca[v]), f"grau({v})", len(vizinhanca[v]), grau)

    for u in vertices:
        for v in vertices:
            esperado = v in vizinhanca[u]
            obtido = chamar(lambda u=u, v=v: grafo.sao_adjacentes(u, v), f"sao_adjacentes({u}, {v})")
            exigir(obtido == esperado, f"sao_adjacentes({u}, {v})", esperado, obtido)


def aresta_normalizada(u: int, v: int) -> tuple[int, int]:
    return (u, v) if u < v else (v, u)


def imprimir_falha(rodada: int, acoes: list[str], falha: FalhaTeste) -> None:
    print(f"\n{VERMELHO}{NEGRITO}FALHA na rodada {rodada}/{RODADAS}{RESET}")
    print("Ações executadas antes da falha:")
    for indice, acao in enumerate(acoes, start=1):
        print(f"  {indice:2d}. {acao}")
    print(f"\n{AMARELO}Ponto da falha:{RESET} {falha.ponto}")
    print(f"Esperado: {falha.esperado!r}")
    print(f"Obtido:   {falha.obtido!r}")


def main() -> None:
    try:
        from grafo import Grafo
    except Exception as erro:
        print(f"{VERMELHO}{NEGRITO}Não foi possível importar Grafo de grafo.py.{RESET}")
        print(f"{type(erro).__name__}: {erro}")
        raise SystemExit(1)

    gerador = random.Random(SEMENTE)

    for rodada in range(1, RODADAS + 1):
        acoes = list[str]()
        numero_vertices = gerador.choice([1, 2, 3, 4, 5, 6, 8, 10, 12])

        try:
            grafo = chamar(lambda: Grafo(numero_vertices), f"Grafo({numero_vertices})")
            acoes.append(f"criar Grafo({numero_vertices})")

            vertices = chamar(grafo.vertices, "vertices()")
            acoes.append("obter vertices()")
            exigir(isinstance(vertices, list), "vertices()", f"uma lista com {numero_vertices} inteiros distintos", type(vertices).__name__)
            exigir(len(vertices) == numero_vertices, "vertices()", f"{numero_vertices} vértices", vertices)
            exigir(all(isinstance(v, int) and not isinstance(v, bool) for v in vertices), "vertices()", "somente identificadores inteiros", vertices)
            exigir(len(vertices) == len(set(vertices)), "vertices()", "identificadores sem repetição", vertices)

            vertices_esperados = set(vertices)
            vertices_ordenados = sorted(vertices_esperados)
            arestas = set[tuple[int, int]]()

            verificar_estado(grafo, vertices_esperados, arestas)
            acoes.append("conferir o estado inicial vazio")

            candidatas = [(u, v) for indice, u in enumerate(vertices_ordenados) for v in vertices_ordenados[indice + 1:]]
            quantidade_adicoes = min(len(candidatas), gerador.randint(3, 7))

            if quantidade_adicoes:
                escolhidas = gerador.sample(candidatas, quantidade_adicoes)
                for u, v in escolhidas:
                    chamar(lambda u=u, v=v: grafo.adicionar_aresta(u, v), f"adicionar_aresta({u}, {v})")
                    arestas.add(aresta_normalizada(u, v))
                    acoes.append(f"adicionar aresta ({u}, {v})")
                    verificar_estado(grafo, vertices_esperados, arestas)

                quantidade_remocoes = min(len(arestas), gerador.randint(1, 2))
                removidas = gerador.sample(sorted(arestas), quantidade_remocoes)
                for u, v in removidas:
                    chamar(lambda u=u, v=v: grafo.remover_aresta(u, v), f"remover_aresta({u}, {v})")
                    arestas.remove((u, v))
                    acoes.append(f"remover aresta ({u}, {v})")
                    verificar_estado(grafo, vertices_esperados, arestas)

        except FalhaTeste as falha:
            imprimir_falha(rodada, acoes, falha)
            raise SystemExit(1)

    print(f"{VERDE}{NEGRITO}Todos os testes passaram: {RODADAS}/{RODADAS}.{RESET}")
    print(f"{VERDE}Parabéns!{RESET}")


if __name__ == "__main__":
    main()
