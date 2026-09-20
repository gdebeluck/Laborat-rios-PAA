import os
import random
import sys


RODADAS = 30
SEMENTE = 418_723


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


def verificar_vertices(grafo, vertices_esperados: set[str]) -> list[str]:
    vertices = chamar(grafo.vertices, "vertices()")
    exigir(isinstance(vertices, list), "vertices()", "uma lista de strings", type(vertices).__name__)
    exigir(all(isinstance(v, str) for v in vertices), "vertices()", "somente rótulos do tipo str", vertices)
    exigir(len(vertices) == len(set(vertices)), "vertices()", "rótulos sem repetição", vertices)
    exigir(set(vertices) == vertices_esperados, "vertices()", sorted(vertices_esperados), vertices)
    return vertices


def verificar_estado(grafo, vertices_esperados: set[str], arcos: set[tuple[str, str]]) -> None:
    vertices = verificar_vertices(grafo, vertices_esperados)
    vizinhanca = {v: set[str]() for v in vertices_esperados}

    for v, u in arcos:
        vizinhanca[v].add(u)

    for v in vertices:
        vizinhos = chamar(lambda v=v: grafo.vizinhos(v), f"vizinhos({v!r})")
        exigir(isinstance(vizinhos, list), f"vizinhos({v!r})", "uma lista", type(vizinhos).__name__)
        exigir(all(isinstance(u, str) for u in vizinhos), f"vizinhos({v!r})", "somente rótulos do tipo str", vizinhos)
        exigir(len(vizinhos) == len(set(vizinhos)), f"vizinhos({v!r})", f"sem repetições; vizinhos = {sorted(vizinhanca[v])}", vizinhos)
        exigir(set(vizinhos) == vizinhanca[v], f"vizinhos({v!r})", sorted(vizinhanca[v]), vizinhos)


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
            grafo = chamar(Grafo, "Grafo()")
            acoes.append("criar Grafo()")

            vertices = [f"cidade_{rodada}_{i}" for i in range(numero_vertices)]
            gerador.shuffle(vertices)

            for v in vertices:
                chamar(lambda v=v: grafo.adicionar_vertice(v), f"adicionar_vertice({v!r})")
                acoes.append(f"adicionar vértice {v!r}")

            vertices_esperados = set(vertices)
            arcos = set[tuple[str, str]]()

            candidatas = [(v, u) for v in vertices for u in vertices if v != u]
            quantidade_arcos = gerador.randint(0, min(len(candidatas), max(1, 2 * numero_vertices)))
            if quantidade_arcos:
                for v, u in gerador.sample(candidatas, quantidade_arcos):
                    chamar(lambda v=v, u=u: grafo.adicionar_arco(v, u), f"adicionar_arco({v!r}, {u!r})")
                    arcos.add((v, u))
                    acoes.append(f"adicionar arco ({v!r} -> {u!r})")

            verificar_estado(grafo, vertices_esperados, arcos)
            acoes.append("conferir o grafo original")

            reverso = chamar(grafo.reverso, "reverso()")
            acoes.append("obter reverso()")
            exigir(isinstance(reverso, Grafo), "reverso()", "um objeto da classe Grafo", type(reverso).__name__)

            arcos_reversos = {(u, v) for v, u in arcos}
            verificar_estado(reverso, vertices_esperados, arcos_reversos)
            acoes.append("conferir os vértices e arcos do grafo reverso")

            verificar_estado(grafo, vertices_esperados, arcos)
            acoes.append("conferir que o grafo original não foi modificado")

            duplo_reverso = chamar(reverso.reverso, "reverso().reverso()")
            acoes.append("obter reverso().reverso()")
            exigir(isinstance(duplo_reverso, Grafo), "reverso().reverso()", "um objeto da classe Grafo", type(duplo_reverso).__name__)
            verificar_estado(duplo_reverso, vertices_esperados, arcos)
            acoes.append("conferir o duplo reverso")

            novo_vertice = f"extra_{rodada}"
            chamar(lambda: reverso.adicionar_vertice(novo_vertice), f"adicionar_vertice({novo_vertice!r}) no reverso")
            acoes.append(f"adicionar vértice {novo_vertice!r} ao reverso")
            if vertices:
                destino = vertices[0]
                chamar(lambda: reverso.adicionar_arco(novo_vertice, destino), f"adicionar_arco({novo_vertice!r}, {destino!r}) no reverso")
                acoes.append(f"adicionar arco ({novo_vertice!r} -> {destino!r}) ao reverso")

            verificar_estado(grafo, vertices_esperados, arcos)
            acoes.append("conferir que alterações no reverso não afetam o original")

        except FalhaTeste as falha:
            imprimir_falha(rodada, acoes, falha)
            raise SystemExit(1)

    print(f"{VERDE}{NEGRITO}Todos os testes passaram: {RODADAS}/{RODADAS}.{RESET}")
    print(f"{VERDE}Parabéns!{RESET}")


if __name__ == "__main__":
    main()
