from __future__ import annotations
import os, sys, ctypes, subprocess
import tkinter as tk
from tkinter import messagebox

def ensure_windows():
    if os.name != 'nt':
        raise SystemExit("Este aplicativo é somente para Windows.")

def is_admin() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False

def relaunch_as_admin():
    try:
        params = " ".join(f'"{a}"' for a in sys.argv)
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
    except Exception as e:
        messagebox.showwarning("Permissão", f"Falha ao elevar privilégios: {e}")

def run_ps(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')

def run_cmd(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore', shell=False)

def human_size(num_bytes: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if num_bytes < 1024.0:
            return f"{num_bytes:3.1f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.1f} PB"

def resource_path(name: str) -> str:
    base = getattr(sys, "_MEIPASS", os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
    return os.path.join(base, name)

def disable_maximize_button(root: tk.Tk) -> None:
    try:
        GWL_STYLE      = -16
        WS_MAXIMIZEBOX = 0x00010000
        hwnd = root.winfo_id()
        user32 = ctypes.windll.user32
        style = user32.GetWindowLongW(hwnd, GWL_STYLE)
        style &= ~WS_MAXIMIZEBOX
        user32.SetWindowLongW(hwnd, GWL_STYLE, style)
        SWP_NOSIZE=0x1; SWP_NOMOVE=0x2; SWP_NOZORDER=0x4; SWP_FRAMECHANGED=0x20
        user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0, SWP_NOSIZE|SWP_NOMOVE|SWP_NOZORDER|SWP_FRAMECHANGED)
    except Exception:
        pass
