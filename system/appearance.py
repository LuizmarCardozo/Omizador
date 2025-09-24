from __future__ import annotations
import logging, subprocess
from .os_utils import run_ps
from .power import set_power_plan_balanced  # usado na reversão

def set_visual_effects_best_performance(best_performance: bool = True) -> bool:
    try:
        val = 2 if best_performance else 1
        cmd = [
            'reg', 'add',
            r'HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects',
            '/v', 'VisualFXSetting', '/t', 'REG_DWORD', '/d', str(val), '/f'
        ]
        p = run_ps(cmd)
        ok = p.returncode == 0
        logging.info("Efeitos visuais: %s", "Melhor desempenho" if best_performance else "Melhor aparência")
        if ok:
            try:
                subprocess.run(['taskkill', '/F', '/IM', 'explorer.exe'], capture_output=True)
                subprocess.run(['start', 'explorer'], shell=True)
            except Exception:
                pass
        else:
            logging.warning("Falha (código %s)", p.returncode)
        return ok
    except Exception as e:
        logging.error("Erro ao ajustar efeitos: %s", e)
        return False

def revert_performance_tweaks() -> bool:
    ok1 = set_power_plan_balanced()
    ok2 = set_visual_effects_best_performance(False)
    if ok1 and ok2:
        logging.info("Reversão concluída (Balanceado + Melhor aparência).")
        return True
    logging.warning("Reversão concluída com avisos. Verifique o log.")
    return False
