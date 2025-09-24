#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Disdal Tech – Otimizador (GUI) • Windows 10/11
App modularizado.
"""
from __future__ import annotations
import os, sys, time, logging
from datetime import datetime

# === garantir que pastas system/ e ui/ estejam no path ===
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ui.app import WinOptimizerApp
from system.os_utils import ensure_windows

APP_NAME = "Disdal Tech – Otimizador"
LOG_DIR = os.path.join(os.environ.get('TEMP', '.'), 'win_optimizer_logs')
os.makedirs(LOG_DIR, exist_ok=True)
LOG_PATH = os.path.join(LOG_DIR, f"optimizer_{int(time.time())}.log")

def main():
    ensure_windows()
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[logging.FileHandler(LOG_PATH, encoding='utf-8'),
                  logging.StreamHandler(sys.stdout)]
    )
    app = WinOptimizerApp(app_name=APP_NAME, log_path=LOG_PATH)
    app.mainloop()

if __name__ == '__main__':
    main()
