from __future__ import annotations
import ctypes, logging

def empty_recycle_bin(show_confirm: bool = False, show_progress: bool = True, sound: bool = False) -> bool:
    SHERB_NOCONFIRMATION = 0x1
    SHERB_NOPROGRESSUI   = 0x2
    SHERB_NOSOUND        = 0x4
    flags = 0
    if not show_confirm: flags |= SHERB_NOCONFIRMATION
    if not show_progress: flags |= SHERB_NOPROGRESSUI
    if not sound: flags |= SHERB_NOSOUND
    try:
        logging.info("Esvaziando Lixeira…")
        ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, flags)
        logging.info("Lixeira esvaziada.")
        return True
    except Exception as e:
        logging.warning("Falha ao esvaziar Lixeira: %s", e)
        return False
