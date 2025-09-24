from __future__ import annotations
import os, logging, ctypes
import ctypes.wintypes as wintypes

try:
    import psutil  # type: ignore
    HAS_PSUTIL = True
except Exception:
    HAS_PSUTIL = False

def optimize_memory_ram() -> tuple[int, int]:
    """
    Enxuga RAM via EmptyWorkingSet em processos de usuário (ignora críticos).
    Retorna (processos_ajustados, tentativas).
    """
    logging.info("Otimizando memória RAM…")
    psapi = ctypes.WinDLL('psapi', use_last_error=True)
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

    EmptyWorkingSet = psapi.EmptyWorkingSet
    EmptyWorkingSet.argtypes = [wintypes.HANDLE]
    EmptyWorkingSet.restype  = wintypes.BOOL

    OpenProcess = kernel32.OpenProcess
    OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    OpenProcess.restype  = wintypes.HANDLE

    CloseHandle = kernel32.CloseHandle
    CloseHandle.argtypes = [wintypes.HANDLE]
    CloseHandle.restype  = wintypes.BOOL

    PROCESS_QUERY_INFORMATION = 0x0400
    PROCESS_SET_QUOTA         = 0x0100

    skipped = {"System", "Registry", "MemCompression", "Idle"}

    count_ok = 0
    count_try = 0

    if HAS_PSUTIL:
        for p in psutil.process_iter(['pid', 'name', 'username']):
            name = (p.info.get('name') or '').strip()
            pid  = p.info.get('pid')
            if not pid or name in skipped:
                continue
            if pid == os.getpid():
                continue
            user = (p.info.get('username') or '')
            if 'SYSTEM' in user or 'LOCAL SERVICE' in user or 'NETWORK SERVICE' in user:
                continue
            try:
                h = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_SET_QUOTA, False, pid)
                if h:
                    count_try += 1
                    if EmptyWorkingSet(h):
                        count_ok += 1
                    CloseHandle(h)
            except Exception:
                continue
    else:
        try:
            pid = os.getpid()
            h = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_SET_QUOTA, False, pid)
            if h:
                count_try = 1
                if EmptyWorkingSet(h):
                    count_ok = 1
                CloseHandle(h)
        except Exception:
            pass

    logging.info("RAM: processos ajustados: %d de %d.", count_ok, count_try)
    return count_ok, count_try
