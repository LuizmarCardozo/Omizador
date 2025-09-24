from __future__ import annotations
import logging
try:
    import winreg
except Exception:
    winreg = None  # type: ignore

RUN_PATHS = [
    (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
    (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
]
DISABLED_SUFFIX = " (Disabled by WinOptimizer)"

def _hive_name(hive) -> str:
    return 'HKCU' if hive == winreg.HKEY_CURRENT_USER else 'HKLM'

def _open_for_write(hive, path):
    return winreg.OpenKey(hive, path, 0, winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE)

def list_startup_entries() -> list[tuple[str, str, str]]:
    entries: list[tuple[str, str, str]] = []
    if not winreg:
        logging.warning("winreg indisponível."); return entries
    for hive, path in RUN_PATHS:
        try:
            with winreg.OpenKey(hive, path, 0, winreg.KEY_READ) as k:
                i = 0
                while True:
                    try:
                        name, value, _ = winreg.EnumValue(k, i)
                        entries.append((f"{_hive_name(hive)}\\{path}", name, str(value)))
                        i += 1
                    except OSError:
                        break
        except FileNotFoundError:
            continue
        except PermissionError:
            logging.warning("Sem permissão para ler: %s\\%s", _hive_name(hive), path)
    return entries

def disable_startup_entry(name: str) -> bool:
    if not winreg: return False
    changed = False
    for hive, path in RUN_PATHS:
        try:
            with _open_for_write(hive, path) as k:
                try: val, typ = winreg.QueryValueEx(k, name)
                except FileNotFoundError: continue
                winreg.SetValueEx(k, name + DISABLED_SUFFIX, 0, typ, val)
                winreg.DeleteValue(k, name)
                logging.info("Desabilitado em %s: %s", f"{_hive_name(hive)}\\{path}", name)
                changed = True
        except PermissionError:
            logging.warning("Sem permissão para alterar: %s\\%s", _hive_name(hive), path)
        except Exception as e:
            logging.error("Falha ao desabilitar %s: %s", name, e)
    return changed

def enable_startup_entry(name: str) -> bool:
    if not winreg: return False
    changed = False
    for hive, path in RUN_PATHS:
        try:
            with _open_for_write(hive, path) as k:
                try: val, typ = winreg.QueryValueEx(k, name + DISABLED_SUFFIX)
                except FileNotFoundError: continue
                winreg.SetValueEx(k, name, 0, typ, val)
                winreg.DeleteValue(k, name + DISABLED_SUFFIX)
                logging.info("Habilitado em %s: %s", f"{_hive_name(hive)}\\{path}", name)
                changed = True
        except PermissionError:
            logging.warning("Sem permissão para alterar: %s\\%s", _hive_name(hive), path)
        except Exception as e:
            logging.error("Falha ao habilitar %s: %s", name, e)
    return changed
