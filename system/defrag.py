from __future__ import annotations
import logging
from .os_utils import run_ps

def optimize_drives() -> bool:
    try:
        cmd = ['defrag', '/C', '/O', '/U', '/V']
        logging.info("Otimizando unidades… (pode demorar)")
        p = run_ps(cmd)
        out = (p.stdout or p.stderr or '').strip()
        if out:
            logging.info("Saída defrag:\n%s", out)
        ok = p.returncode == 0
        logging.info("Otimização %s.", "concluída" if ok else f"retornou código {p.returncode}")
        return ok
    except Exception as e:
        logging.error("Erro ao otimizar: %s", e)
        return False
