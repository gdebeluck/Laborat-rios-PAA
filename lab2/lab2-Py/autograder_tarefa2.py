import os
import re
import subprocess
import sys
import threading
import time
from pathlib import Path


PASTA_CASOS = Path("casos")
ARQUIVO_SOLUCAO = Path("main.py")
LIMITE_SEGUNDOS_POR_CASO = 15.0
LIMITE_MEMORIA = 2 * 1024 * 1024 * 1024
INTERVALO_MEMORIA = 0.005


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


def chave_natural(caminho: Path) -> list[object]:
    return [int(parte) if parte.isdigit() else parte.lower() for parte in re.split(r"(\d+)", caminho.name)]


def texto_curto(texto: str, limite: int = 500) -> str:
    texto = texto.strip()
    if len(texto) <= limite:
        return texto
    return texto[:limite] + "... [saída truncada]"


def memoria_linux(pid: int) -> int:
    try:
        with open(f"/proc/{pid}/status", "r", encoding="utf-8") as arquivo:
            for linha in arquivo:
                if linha.startswith("VmRSS:"):
                    return int(linha.split()[1]) * 1024
    except (FileNotFoundError, ProcessLookupError, PermissionError, ValueError):
        pass
    return 0


def monitorar_memoria_linux(processo: subprocess.Popen[bytes], resultado: list[int], excedeu: list[bool]) -> None:
    pico = 0
    while processo.poll() is None:
        memoria = memoria_linux(processo.pid)
        pico = max(pico, memoria)
        if memoria > LIMITE_MEMORIA:
            excedeu[0] = True
            processo.kill()
            break
        time.sleep(INTERVALO_MEMORIA)
    resultado[0] = pico


def monitorar_memoria_windows(processo: subprocess.Popen[bytes], resultado: list[int], excedeu: list[bool]) -> None:
    import ctypes
    from ctypes import wintypes

    class ProcessMemoryCounters(ctypes.Structure):
        _fields_ = [
            ("cb", wintypes.DWORD),
            ("PageFaultCount", wintypes.DWORD),
            ("PeakWorkingSetSize", ctypes.c_size_t),
            ("WorkingSetSize", ctypes.c_size_t),
            ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
            ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
            ("PagefileUsage", ctypes.c_size_t),
            ("PeakPagefileUsage", ctypes.c_size_t),
        ]

    kernel32 = ctypes.windll.kernel32
    psapi = ctypes.windll.psapi
    kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel32.OpenProcess.restype = wintypes.HANDLE
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL
    psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(ProcessMemoryCounters), wintypes.DWORD]
    psapi.GetProcessMemoryInfo.restype = wintypes.BOOL

    handle = kernel32.OpenProcess(0x0400 | 0x0010, False, processo.pid)
    if not handle:
        return

    pico = 0
    contadores = ProcessMemoryCounters()
    contadores.cb = ctypes.sizeof(contadores)

    try:
        while processo.poll() is None:
            if psapi.GetProcessMemoryInfo(handle, ctypes.byref(contadores), contadores.cb):
                memoria = int(contadores.WorkingSetSize)
                pico = max(pico, int(contadores.PeakWorkingSetSize), memoria)
                if memoria > LIMITE_MEMORIA:
                    excedeu[0] = True
                    processo.kill()
                    break
            time.sleep(INTERVALO_MEMORIA)
    finally:
        kernel32.CloseHandle(handle)

    resultado[0] = pico


def monitorar_memoria(processo: subprocess.Popen[bytes], resultado: list[int], excedeu: list[bool]) -> None:
    try:
        if os.name == "nt":
            monitorar_memoria_windows(processo, resultado, excedeu)
        elif sys.platform.startswith("linux"):
            monitorar_memoria_linux(processo, resultado, excedeu)
    except Exception:
        resultado[0] = 0


def executar_caso(entrada: bytes) -> tuple[int | None, bytes, bytes, float, int, bool, bool]:
    ambiente = os.environ.copy()
    ambiente["PYTHONIOENCODING"] = "utf-8"
    ambiente["PYTHONUTF8"] = "1"

    inicio = time.perf_counter()
    processo = subprocess.Popen(
        [sys.executable, "-B", str(ARQUIVO_SOLUCAO)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=Path.cwd(),
        env=ambiente,
    )

    memoria = [0]
    excedeu_memoria = [False]
    monitor = threading.Thread(target=monitorar_memoria, args=(processo, memoria, excedeu_memoria), daemon=True)
    monitor.start()

    expirou = False
    try:
        stdout, stderr = processo.communicate(input=entrada, timeout=LIMITE_SEGUNDOS_POR_CASO)
    except subprocess.TimeoutExpired:
        expirou = True
        processo.kill()
        stdout, stderr = processo.communicate()

    monitor.join()
    tempo = time.perf_counter() - inicio
    return processo.returncode, stdout, stderr, tempo, memoria[0], expirou, excedeu_memoria[0]


def formatar_memoria(bytes_usados: int) -> str:
    if bytes_usados <= 0:
        return "indisponível"
    return f"{bytes_usados / (1024 * 1024):.2f} MiB"


def main() -> None:
    if not ARQUIVO_SOLUCAO.is_file():
        print(f"{VERMELHO}{NEGRITO}Arquivo {ARQUIVO_SOLUCAO} não encontrado.{RESET}")
        raise SystemExit(1)

    if not PASTA_CASOS.is_dir():
        print(f"{VERMELHO}{NEGRITO}Pasta {PASTA_CASOS} não encontrada.{RESET}")
        raise SystemExit(1)

    entradas = sorted(PASTA_CASOS.glob("*.in"), key=chave_natural)
    if not entradas:
        print(f"{VERMELHO}{NEGRITO}Nenhum arquivo .in foi encontrado em {PASTA_CASOS}.{RESET}")
        raise SystemExit(1)

    pares = list[tuple[Path, Path]]()
    for entrada in entradas:
        saida = entrada.with_suffix(".out")
        if not saida.is_file():
            print(f"{VERMELHO}{NEGRITO}Falta o arquivo esperado {saida}.{RESET}")
            raise SystemExit(1)
        pares.append((entrada, saida))

    print(f"Executando {len(pares)} casos...")

    numero_falhas = 0
    primeira_falha: str | None = None
    tempo_total = 0.0
    pico_memoria = 0

    for entrada_path, saida_path in pares:
        entrada = entrada_path.read_bytes()
        esperado = saida_path.read_text(encoding="utf-8").strip()

        try:
            codigo, stdout, stderr, tempo, memoria, expirou, excedeu_memoria = executar_caso(entrada)
        except Exception as erro:
            numero_falhas += 1
            if primeira_falha is None:
                primeira_falha = f"{entrada_path.name}: não foi possível executar a solução ({type(erro).__name__}: {erro})"
            continue

        tempo_total += tempo
        pico_memoria = max(pico_memoria, memoria)

        if excedeu_memoria:
            numero_falhas += 1
            if primeira_falha is None:
                primeira_falha = f"{entrada_path.name}: excedeu o limite de memória de {LIMITE_MEMORIA // (1024 * 1024)} MiB"
            continue

        if expirou:
            numero_falhas += 1
            if primeira_falha is None:
                primeira_falha = f"{entrada_path.name}: excedeu {LIMITE_SEGUNDOS_POR_CASO:.0f} s"
            continue

        stderr_texto = stderr.decode("utf-8", errors="replace")
        stdout_texto = stdout.decode("utf-8", errors="replace")

        if codigo != 0:
            numero_falhas += 1
            if primeira_falha is None:
                mensagem = f"{entrada_path.name}: terminou com código {codigo}"
                if stderr_texto.strip():
                    mensagem += f"\n    stderr: {texto_curto(stderr_texto)}"
                primeira_falha = mensagem
            continue

        obtido = stdout_texto.strip()
        if obtido != esperado:
            numero_falhas += 1
            if primeira_falha is None:
                mensagem = f"{entrada_path.name}: resposta incorreta\n    esperado: {esperado!r}\n    obtido:   {texto_curto(obtido)!r}"
                if stderr_texto.strip():
                    mensagem += f"\n    stderr: {texto_curto(stderr_texto)}"
                primeira_falha = mensagem

    if numero_falhas:
        print(f"\n{VERMELHO}{NEGRITO}{numero_falhas}/{len(pares)} caso(s) falharam.{RESET}")
        print(f"{AMARELO}O primeiro caso que falhou foi:{RESET}")
        print(f"\n{primeira_falha}")
        raise SystemExit(1)

    print(f"\n{VERDE}{NEGRITO}Todos os {len(pares)} casos passaram.{RESET}")
    print(f"Tempo total: {tempo_total:.3f} s")
    print(f"Pico de memória da solução: {formatar_memoria(pico_memoria)}")
    print(f"{VERDE}Parabéns!{RESET}")


if __name__ == "__main__":
    main()
