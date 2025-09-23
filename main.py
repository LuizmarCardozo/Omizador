#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Win Optimizer – GUI (Windows 10/11)
Visual com cores, abas grandes e botões alinhados. Sem aba de Logs.
"""
from __future__ import annotations

import os, sys, time, ctypes, logging, subprocess
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

# ----- dependências opcionais -----
try:
    from send2trash import send2trash  # type: ignore
    HAS_SEND2TRASH = True
except Exception:
    HAS_SEND2TRASH = False

try:
    import psutil  # type: ignore
    HAS_PSUTIL = True
except Exception:
    HAS_PSUTIL = False

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except Exception:
    HAS_PIL = False

# ----- ambiente -----
if os.name != 'nt':
    raise SystemExit("Este aplicativo é somente para Windows.")

APP_NAME = "Disdal Tech – Otimizador"
LOG_DIR = os.path.join(os.environ.get('TEMP', '.'), 'win_optimizer_logs')
os.makedirs(LOG_DIR, exist_ok=True)
LOG_PATH = os.path.join(LOG_DIR, f"optimizer_{int(time.time())}.log")

LOGO_FILENAME = "DTO.png"
LOGO_SMALL_HEIGHT = 120
LOGO_LARGE_HEIGHT = 320

# Paleta (inspirada na logo)
DARK_BG   = "#0f172a"  # header
LIGHT_BG  = "#f7f9fb"  # fundo
CARD_BG   = "#ffffff"  # cards
PRIMARY   = "#00a19a"  # teal
ACCENT    = "#f4c20d"  # amarelo
DANGER    = "#e53935"  # vermelho
TEXT_MUTE = "#6b7280"

# ========= helpers SO =========
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
        messagebox.showwarning(APP_NAME, f"Falha ao elevar privilégios: {e}")

def run_ps(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')

def human_size(num_bytes: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if num_bytes < 1024.0:
            return f"{num_bytes:3.1f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.1f} PB"

def resource_path(name: str) -> str:
    base = getattr(sys, "_MEIPASS", os.path.abspath(os.path.dirname(__file__)))
    return os.path.join(base, name)

# ========= operações =========
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
        logging.warning("Falha ao criar ponto de restauração: %s", p.stderr.strip())
        return False
    except Exception as e:
        logging.warning("Exceção ao criar ponto de restauração: %s", e)
        return False

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

def optimize_drives() -> bool:
    try:
        cmd = ['defrag', '/C', '/O', '/U', '/V']
        logging.info("Otimizando unidades… (pode demorar)")
        p = run_ps(cmd)
        out = (p.stdout or p.stderr or '').strip()
        if out: logging.info("Saída defrag:\n%s", out)
        ok = p.returncode == 0
        logging.info("Otimização %s.", "concluída" if ok else f"retornou código {p.returncode}")
        return ok
    except Exception as e:
        logging.error("Erro ao otimizar: %s", e)
        return False

def _known_cache_dirs() -> list[tuple[str, str]]:
    paths: list[tuple[str, str]] = []
    temp_user = os.environ.get('TEMP') or os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'Temp')
    system_root = os.environ.get('SystemRoot', r'C:\Windows')
    temp_win = os.path.join(system_root, 'Temp')
    localapp = os.environ.get('LOCALAPPDATA', '')
    if os.path.isdir(temp_user): paths.append(("Temp do Usuário (%TEMP%)", temp_user))
    if os.path.isdir(temp_win): paths.append(("Temp do Windows (C:/Windows/Temp)", temp_win))
    inetcache = os.path.join(localapp, 'Microsoft', 'Windows', 'INetCache') if localapp else ''
    if inetcache and os.path.isdir(inetcache): paths.append(("INetCache (cache navegador legado)", inetcache))
    return paths

def _delete_from_paths(paths: list[str], dry_run: bool, older_than_days: int) -> tuple[int, int]:
    now = time.time(); cutoff = now - max(0, older_than_days) * 86400
    total_bytes = 0; count = 0
    for base in paths:
        if not os.path.isdir(base): continue
        for root, _, files in os.walk(base):
            for fname in files:
                fpath = os.path.join(root, fname)
                try: st = os.stat(fpath)
                except Exception: continue
                if older_than_days > 0 and st.st_mtime >= cutoff: continue
                total_bytes += getattr(st, 'st_size', 0)
                if dry_run: count += 1; continue
                try:
                    if HAS_SEND2TRASH: send2trash(fpath)
                    else: os.remove(fpath)
                    count += 1
                except PermissionError:
                    try: os.chmod(fpath, 0o666); os.remove(fpath); count += 1
                    except Exception: logging.debug("Não foi possível excluir: %s", fpath)
                except Exception:
                    logging.debug("Não foi possível excluir: %s", fpath)
    return count, total_bytes

def clear_thumbnail_cache(dry_run: bool = False) -> tuple[int, int]:
    localapp = os.environ.get('LOCALAPPDATA')
    if not localapp:
        logging.warning("LOCALAPPDATA não definido."); return (0, 0)
    explorer = os.path.join(localapp, 'Microsoft', 'Windows', 'Explorer')
    if not os.path.isdir(explorer): return (0, 0)
    targets = [os.path.join(explorer, f) for f in os.listdir(explorer)
               if f.lower().startswith('thumbcache') and f.lower().endswith('.db')]
    total = sum((os.path.getsize(p) for p in targets if os.path.exists(p)), 0)
    if dry_run:
        logging.info("Miniaturas encontradas: %d (%s)", len(targets), human_size(total)); return (len(targets), total)
    deleted = 0
    for f in targets:
        try:
            if HAS_SEND2TRASH: send2trash(f)
            else: os.remove(f)
            deleted += 1
        except Exception:
            logging.debug("Não foi possível remover: %s (provavelmente em uso)", f)
    logging.info("Miniaturas removidas: %d (%s)", deleted, human_size(total))
    return (deleted, total)

# ========= Inicialização (Run) =========
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

# ========= Energia & Aparência =========
GUID_BALANCED = "381b4222-f694-41f0-9685-ff5bb260df2e"
GUID_HIGH     = "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"

def set_power_plan_high_performance() -> bool:
    try:
        p = run_ps(['powercfg', '/S', GUID_HIGH])
        ok = p.returncode == 0
        logging.info("Plano 'Alto desempenho' %s.", "ativado" if ok else f"falhou ({p.returncode})")
        if not ok: logging.debug((p.stdout or '') + "\n" + (p.stderr or ''))
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
        logging.info("Reversão concluída (Balanced + Melhor aparência).")
        return True
    logging.warning("Reversão concluída com avisos. Verifique o log.")
    return False

# ========= App =========
class WinOptimizerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry('1080x720')
        self.minsize(980, 640)

        self._init_styles()

        # Logo
        self.logo_small: tk.PhotoImage | None = None
        self.logo_large: tk.PhotoImage | None = None
        self._load_logo_images()
        if self.logo_small: self.iconphoto(True, self.logo_small)

        # Header colorido
        header = ttk.Frame(self, style="Header.TFrame"); header.pack(fill='x')
        if self.logo_small:
            ttk.Label(header, image=self.logo_small, style="Header.TLabel").pack(side='left', padx=(16, 12), pady=8)
        ttk.Label(header, text="DISDAL TECH – Otimizador", style="HeaderTitle.TLabel").pack(side='left', pady=8)
        self.admin_badge = ttk.Label(header, style="HeaderBadge.TLabel"); self._update_admin_badge()
        self.admin_badge.pack(side='left', padx=12)
        if not is_admin():
            ttk.Button(header, text="Executar como Administrador", command=relaunch_as_admin, style="Accent.TButton").pack(side='right', padx=16, pady=12)

        # Corpo
        body = ttk.Frame(self, style="App.TFrame"); body.pack(fill='both', expand=True)
        nb = ttk.Notebook(body, style="Big.TNotebook"); nb.pack(fill='both', expand=True, padx=16, pady=16)

        self.tab_main = ttk.Frame(nb, style="App.TFrame"); nb.add(self.tab_main, text='🧰  Geral')
        self.tab_cache = ttk.Frame(nb, style="App.TFrame"); nb.add(self.tab_cache, text='🧹  Caches')
        self.tab_start = ttk.Frame(nb, style="App.TFrame"); nb.add(self.tab_start, text='🔧  Inicialização')
        self.tab_power = ttk.Frame(nb, style="App.TFrame"); nb.add(self.tab_power, text='🚀  Energia & Aparência')

        self._build_tab_main()
        self._build_tab_cache()
        self._build_tab_start()
        self._build_tab_power()

        # Rodapé
        footer = ttk.Frame(self, style="Footer.TFrame"); footer.pack(fill='x')
        ttk.Label(footer, text=f"🧾 Log: {LOG_PATH}", style="Footer.TLabel").pack(side='left', padx=16, pady=8)

        self.show_system_info()

    # ----- estilos -----
    def _init_styles(self):
        style = ttk.Style(self)
        style.theme_use('clam')

        # Fundo da janela
        self.configure(bg=LIGHT_BG)
        style.configure("App.TFrame", background=LIGHT_BG)

        # Header
        style.configure("Header.TFrame", background=DARK_BG)
        style.configure("Header.TLabel", background=DARK_BG, foreground="white")
        style.configure("HeaderTitle.TLabel", background=DARK_BG, foreground="white",
                        font=("Segoe UI Semibold", 16))
        style.configure("HeaderBadge.TLabel", background=DARK_BG, foreground=ACCENT, font=("Segoe UI", 10))

        # Footer
        style.configure("Footer.TFrame", background=LIGHT_BG)
        style.configure("Footer.TLabel", background=LIGHT_BG, foreground=TEXT_MUTE)

        # Cards (LabelFrame)
        style.configure("Card.TLabelframe", background=CARD_BG, relief="flat", borderwidth=1)
        style.configure("Card.TLabelframe.Label", background=CARD_BG, foreground="#111", font=("Segoe UI Semibold", 11))
        style.map("Card.TLabelframe", background=[("active", CARD_BG)])

        # Notebook maior
        style.configure("Big.TNotebook", background=LIGHT_BG, borderwidth=0, tabmargins=(10, 8, 10, 0))
        style.configure("Big.TNotebook.Tab", font=("Segoe UI Semibold", 11), padding=(20, 12), background=LIGHT_BG)
        style.map("Big.TNotebook.Tab",
                  background=[("selected", CARD_BG)],
                  foreground=[("selected", "#111"), ("!selected", "#333")],
                  expand=[("selected", [1, 1, 1, 0])])

        # Botões
        style.configure("Primary.TButton", padding=(18, 12), font=("Segoe UI Semibold", 10),
                        background=PRIMARY, foreground="white", borderwidth=0)
        style.map("Primary.TButton",
                  background=[("active", "#019188"), ("pressed", "#017a73")],
                  foreground=[("disabled", "#ccc")])

        style.configure("Secondary.TButton", padding=(18, 12), font=("Segoe UI Semibold", 10),
                        background="#e5e7eb", foreground="#111", borderwidth=0)
        style.map("Secondary.TButton",
                  background=[("active", "#d5d7dc"), ("pressed", "#c9ccd2")])

        style.configure("Danger.TButton", padding=(18, 12), font=("Segoe UI Semibold", 10),
                        background=DANGER, foreground="white", borderwidth=0)
        style.map("Danger.TButton",
                  background=[("active", "#d32f2f"), ("pressed", "#b71c1c")])

        style.configure("Accent.TButton", padding=(14, 10), font=("Segoe UI Semibold", 10),
                        background=ACCENT, foreground="#111", borderwidth=0)
        style.map("Accent.TButton",
                  background=[("active", "#eabf0a"), ("pressed", "#d7ac06")])

    # ----- logo -----
    def _load_logo_images(self, small_h: int = LOGO_SMALL_HEIGHT, large_h: int = LOGO_LARGE_HEIGHT):
        path = resource_path(LOGO_FILENAME)
        if not os.path.exists(path): return
        if HAS_PIL:
            try:
                img = Image.open(path).convert("RGBA")
                alpha = img.split()[-1]; bbox = alpha.getbbox()
                if bbox: img = img.crop(bbox)
                def make(h):
                    w = int(round(img.width * (h / img.height)))
                    return ImageTk.PhotoImage(img.resize((w, h), Image.LANCZOS))
                self.logo_small = make(small_h); self.logo_large = make(large_h); return
            except Exception:
                pass
        try:
            raw = tk.PhotoImage(file=path)
            factor_small = max(1, int(round(raw.height() / max(1, small_h))))
            factor_large = max(1, int(round(raw.height() / max(1, large_h))))
            self.logo_small = raw.subsample(factor_small)
            self.logo_large = raw.subsample(factor_large)
        except Exception:
            self.logo_small = None; self.logo_large = None

    # ----- util UI -----
    def _update_admin_badge(self):
        if is_admin():
            self.admin_badge.configure(text="🟢 Administrador")
        else:
            self.admin_badge.configure(text="🟡 Permissões padrão")

    def _grid_two_cols(self, frame):
        frame.columnconfigure(0, weight=1, uniform="cols")
        frame.columnconfigure(1, weight=1, uniform="cols")

    def _btn(self, parent, text, cmd, style="Primary.TButton"):
        return ttk.Button(parent, text=text, command=cmd, style=style)

    # ----- abas -----
    def _build_tab_main(self):
        f = self.tab_main
        g = ttk.LabelFrame(f, text='Ações rápidas', style="Card.TLabelframe")
        g.pack(fill='x', padx=12, pady=12)
        self._grid_two_cols(g)

        self._btn(g, '🛡️  Criar ponto de restauração',
                  lambda: create_restore_point(f"WinOptimizer {datetime.now().strftime('%Y-%m-%d %H:%M')}")).grid(row=0, column=0, padx=8, pady=8, sticky="ew")
        self._btn(g, '🗑️  Esvaziar Lixeira', empty_recycle_bin).grid(row=0, column=1, padx=8, pady=8, sticky="ew")

        self._btn(g, '⚡  Otimizar unidades (defrag/TRIM)', optimize_drives).grid(row=1, column=0, padx=8, pady=8, sticky="ew")
        self._btn(g, '🖼️  Miniaturas (pré-visualizar)', lambda: clear_thumbnail_cache(True), style="Secondary.TButton").grid(row=1, column=1, padx=8, pady=8, sticky="ew")

        self._btn(g, '🧹  Miniaturas (executar)', lambda: clear_thumbnail_cache(False)).grid(row=2, column=0, padx=8, pady=8, sticky="ew")
        ttk.Label(g, text="", background=CARD_BG).grid(row=2, column=1, padx=8, pady=8, sticky="ew")

        d = ttk.LabelFrame(f, text='Desfazer', style="Card.TLabelframe")
        d.pack(fill='x', padx=12, pady=12)
        self._grid_two_cols(d)
        self._btn(d, '↩️  Balanceado + Melhor aparência', revert_performance_tweaks, style="Danger.TButton")\
            .grid(row=0, column=0, columnspan=2, padx=8, pady=8, sticky="ew")

    def _build_tab_cache(self):
        f = self.tab_cache
        box = ttk.LabelFrame(f, text='Limpar caches por pasta', style="Card.TLabelframe")
        box.pack(fill='x', padx=12, pady=12)

        self.cache_vars: list[tuple[tk.BooleanVar, str, str]] = []
        for label, path in _known_cache_dirs():
            var = tk.BooleanVar(value=False)
            row = ttk.Frame(box, style="App.TFrame"); row.pack(fill='x', padx=10, pady=4)
            ttk.Checkbutton(row, variable=var, text=label).pack(side='left')
            ttk.Label(row, text=path, foreground=TEXT_MUTE).pack(side='left', padx=8)
            self.cache_vars.append((var, label, path))

        extra = ttk.Frame(box, style="App.TFrame"); extra.pack(fill='x', padx=10, pady=(10, 6))
        ttk.Label(extra, text='Caminhos extras (separar por ;):').pack(side='left')
        self.extra_entry = ttk.Entry(extra, width=70); self.extra_entry.pack(side='left', padx=6)

        days = ttk.Frame(box, style="App.TFrame"); days.pack(fill='x', padx=10, pady=6)
        ttk.Label(days, text='Excluir arquivos mais antigos que (dias):').pack(side='left')
        self.days_spin = ttk.Spinbox(days, from_=0, to=365, width=6); self.days_spin.set('1'); self.days_spin.pack(side='left', padx=6)

        btns = ttk.Frame(box, style="App.TFrame"); btns.pack(fill='x', padx=8, pady=8)
        btns.columnconfigure(0, weight=1)
        self._btn(btns, '🔍  Pré-visualizar', lambda: self.cache_action(dry_run=True), style="Secondary.TButton").grid(row=0, column=1, padx=6, sticky="e")
        self._btn(btns, '🧽  Limpar', lambda: self.cache_action(dry_run=False)).grid(row=0, column=2, padx=6, sticky="e")

    def _build_tab_start(self):
        f = self.tab_start
        top = ttk.Frame(f, style="App.TFrame"); top.pack(fill='x', padx=12, pady=10)
        self._btn(top, '🔄 Atualizar lista', self.refresh_startup, style="Secondary.TButton").pack(side='left')
        self._btn(top, '🚫 Desabilitar selecionado', self.disable_selected, style="Danger.TButton").pack(side='left', padx=6)
        self._btn(top, '✅ Habilitar selecionado', self.enable_selected).pack(side='left', padx=6)

        cols = ('local', 'nome', 'comando')
        self.tree = ttk.Treeview(f, columns=cols, show='headings', height=12)
        self.tree.heading('local', text='Local'); self.tree.column('local', width=260, stretch=False)
        self.tree.heading('nome', text='Nome'); self.tree.column('nome', width=200, stretch=False)
        self.tree.heading('comando', text='Comando'); self.tree.column('comando', width=560, stretch=True)
        self.tree.pack(fill='both', expand=True, padx=12, pady=(0,12))

        vsb = ttk.Scrollbar(f, orient="vertical", command=self.tree.yview)
        vsb.place(in_=self.tree, relx=1.0, rely=0, relheight=1.0, x=-1)
        self.tree.configure(yscrollcommand=vsb.set)

    def _build_tab_power(self):
        f = self.tab_power
        g1 = ttk.LabelFrame(f, text='Plano de Energia', style="Card.TLabelframe")
        g1.pack(fill='x', padx=12, pady=12); self._grid_two_cols(g1)
        self._btn(g1, "💪  Ativar: Alto desempenho", set_power_plan_high_performance).grid(row=0, column=0, padx=8, pady=8, sticky="ew")
        self._btn(g1, "🧘  Ativar: Balanceado", set_power_plan_balanced, style="Secondary.TButton").grid(row=0, column=1, padx=8, pady=8, sticky="ew")

        g2 = ttk.LabelFrame(f, text='Aparência', style="Card.TLabelframe")
        g2.pack(fill='x', padx=12, pady=12); self._grid_two_cols(g2)
        self._btn(g2, "🚀  Melhor desempenho", lambda: set_visual_effects_best_performance(True)).grid(row=0, column=0, padx=8, pady=8, sticky="ew")
        self._btn(g2, "✨  Melhor aparência", lambda: set_visual_effects_best_performance(False), style="Secondary.TButton").grid(row=0, column=1, padx=8, pady=8, sticky="ew")

    # ----- ações -----
    def show_system_info(self):
        logging.info("==== Informações do Sistema ====")
        logging.info("Usuário: %s", os.environ.get('USERNAME'))
        logging.info("Computador: %s", os.environ.get('COMPUTERNAME'))
        if HAS_PSUTIL:
            try:
                vm = psutil.virtual_memory()
                logging.info("RAM: %s livre de %s", human_size(vm.available), human_size(vm.total))
                cpu_freq = psutil.cpu_freq()
                if cpu_freq:
                    logging.info("CPU: %d núcleos, %.0f MHz", psutil.cpu_count(logical=True), cpu_freq.current)
                for d in psutil.disk_partitions():
                    try:
                        usage = psutil.disk_usage(d.mountpoint)
                        logging.info("Disco %s: %s livres de %s", d.device, human_size(usage.free), human_size(usage.total))
                    except Exception:
                        pass
            except Exception:
                pass
        logging.info("Log em: %s", LOG_PATH)

    def cache_action(self, dry_run: bool):
        chosen: list[str] = []
        for var, _label, path in getattr(self, "cache_vars", []):
            if var.get(): chosen.append(path)
        extra = getattr(self, "extra_entry").get().strip()
        if extra:
            for part in extra.split(';'):
                p = part.strip().strip('"')
                if p and os.path.isdir(p): chosen.append(p)
        if not chosen:
            messagebox.showinfo(APP_NAME, "Nenhuma pasta selecionada."); return
        try: days = int(self.days_spin.get() or '1')
        except Exception: days = 1
        cnt, total = _delete_from_paths(chosen, dry_run=dry_run, older_than_days=days)
        if dry_run:
            messagebox.showinfo(APP_NAME, f"Pré-visualização:\nArquivos: {cnt}\nTamanho: {human_size(total)}")
        else:
            messagebox.showinfo(APP_NAME, f"Limpeza concluída:\nArquivos apagados: {cnt}\nTotal: {human_size(total)}")

    def refresh_startup(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        items = list_startup_entries()
        if not items:
            messagebox.showinfo(APP_NAME, "Nenhum item encontrado ou sem permissão."); return
        for (loc, name, cmd) in items:
            self.tree.insert('', tk.END, values=(loc, name, cmd))

    def _selected_startup_name(self) -> str | None:
        sel = self.tree.selection()
        if not sel: return None
        vals = (self.tree.item(sel[0]).get('values') or [])
        return vals[1] if len(vals) >= 2 else None

    def disable_selected(self):
        name = self._selected_startup_name()
        if not name: messagebox.showinfo(APP_NAME, "Selecione um item na lista."); return
        ok = disable_startup_entry(name)
        messagebox.showinfo(APP_NAME, "OK" if ok else "Falhou. Veja logs."); self.refresh_startup()

    def enable_selected(self):
        name = self._selected_startup_name()
        if not name: messagebox.showinfo(APP_NAME, "Selecione um item na lista."); return
        ok = enable_startup_entry(name)
        messagebox.showinfo(APP_NAME, "OK" if ok else "Falhou. Veja logs."); self.refresh_startup()

# ========= main =========
def main():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s [%(levelname)s] %(message)s',
                        handlers=[logging.FileHandler(LOG_PATH, encoding='utf-8'),
                                  logging.StreamHandler(sys.stdout)])
    app = WinOptimizerApp()
    app.mainloop()

if __name__ == '__main__':
    main()
