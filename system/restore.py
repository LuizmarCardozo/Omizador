from __future__ import annotations
import logging
from .os_utils import run_ps

def create_restore_point(description: str = "WinOptimizer") -> bool:
    try:
        cmd = [
            'powershell', '-NoLogo', '-NoProfile', '-ExecutionPolicy', 'Bypass',
            'Checkpoint-Computer', '-Description', description,
            '-RestorePointType', 'MODIFY_SETTINGS'
        ]
        logging.info("Criando ponto de restauração…")
        p = run_ps(cmd)
        if p.returncode == 0:
            logging.info("Ponto de restauração criado com sucesso.")
            return True
        logging.warning("Falha ao criar ponto de restauração: %s", (p.stderr or '').strip())
        return False
    except Exception as e:
        logging.warning("Exceção ao criar ponto de restauração: %s", e)
        return False
