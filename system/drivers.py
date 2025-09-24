from __future__ import annotations
import logging, subprocess
from .os_utils import run_cmd

def scan_driver_updates() -> None:
    logging.info("Iniciando verificação de atualizações de drivers…")
    for arg in ('StartScan', 'StartInteractiveScan'):
        try:
            p = run_cmd(['UsoClient.exe', arg])
            if p.returncode == 0:
                logging.info("USOClient %s disparado.", arg)
                break
        except Exception:
            pass
    try:
        pnp = run_cmd(['pnputil', '/scan-devices'])
        if pnp.returncode == 0:
            logging.info("pnputil /scan-devices concluído.")
        else:
            logging.warning("pnputil retornou código %s", pnp.returncode)
    except Exception as e:
        logging.warning("Falha ao executar pnputil: %s", e)
    try:
        subprocess.Popen(['start', 'ms-settings:windowsupdate'], shell=True)
    except Exception:
        pass
    logging.info("Abra o Windows Update para acompanhar e instalar drivers disponíveis.")
