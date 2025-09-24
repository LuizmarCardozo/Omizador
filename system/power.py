from __future__ import annotations
import logging
from .os_utils import run_ps

GUID_BALANCED = "381b4222-f694-41f0-9685-ff5bb260df2e"
GUID_HIGH     = "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"

def set_power_plan_high_performance() -> bool:
    try:
        p = run_ps(['powercfg', '/S', GUID_HIGH])
        ok = p.returncode == 0
        logging.info("Plano 'Alto desempenho' %s.", "ativado" if ok else f"falhou ({p.returncode})")
        if not ok:
            logging.debug((p.stdout or '') + "\n" + (p.stderr or ''))
        return ok
    except Exception as e:
        logging.error("Erro ao ativar plano: %s", e)
        return False

def set_power_plan_balanced() -> bool:
    try:
        p = run_ps(['powercfg', '/S', GUID_BALANCED])
        ok = p.returncode == 0
        logging.info("Plano 'Balanceado' %s.", "ativado" if ok else f"falhou ({p.returncode})")
        return ok
    except Exception as e:
        logging.error("Erro ao ativar plano: %s", e)
        return False
