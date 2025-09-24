from __future__ import annotations

import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


import os, time, logging, tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from system.os_utils import is_admin, relaunch_as_admin, human_size, disable_maximize_button
from system.restore import create_restore_point
from system.recycle_bin import empty_recycle_bin
from system.defrag import optimize_drives
from system.caches import clear_thumbnail_cache, clear_all_browser_caches
from system.startup import list_startup_entries, disable_startup_entry, enable_startup_entry
from system.power import set_power_plan_high_performance, set_power_plan_balanced
from system.appearance import set_visual_effects_best_performance, revert_performance_tweaks
from system.memory import optimize_memory_ram
from system.drivers import scan_driver_updates

from ui.styles import init_styles, LIGHT_BG, CARD_BG, TEXT_MUTE
from ui.logo import load_logo_images

# psutil opcional (apenas informações)
try:
    import psutil  # type: ignore
    HAS_PSUTIL = True
except Exception:
    HAS_PSUTIL = False

class WinOptimizerApp(tk.Tk):
    def __init__(self, app_name: str, log_path: str):
        super().__init__()
        self.app_name = app_name
        self.log_path = log_path

        self.title(app_name)
        # Janela padrão, não maximizada
        try:
            self.state('normal')
        except Exception:
            pass
        self.geometry('1080x720')
        self.minsize(980, 640)

        # Estilos/cores
        init_styles(self)

        # Logo
        self.logo_small, self.logo_large = load_logo_images()
        if self.logo_small: self.iconphoto(True, self.logo_small)

        # Header
        header = ttk.Frame(self, style="Header.TFrame"); header.pack(fill='x')
        if self.logo_small:
            ttk.Label(header, image=self.logo_small, style="Header.TLabel").pack(side='left', padx=(16, 12), pady=8)
        ttk.Label(header, text="DISDAL TECH – Otimizador", style="HeaderTitle.TLabel").pack(side='left', pady=8)
        self.admin_badge = ttk.Label(header, style="HeaderBadge.TLabel"); self._update_admin_badge()
        self.admin_badge.pack(side='left', padx=12)
        if not is_admin():
            ttk.Button(header, text="Executar como Administrador", command=relaunch_as_admin, style="Accent.TButton").pack(side='right', padx=16, pady=12)

        # Body / Abas
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

        # Footer
        footer = ttk.Frame(self, style="Footer.TFrame"); footer.pack(fill='x')
        ttk.Label(footer, text=f"🧾 Log: {log_path}", style="Footer.TLabel").pack(side='left', padx=16, pady=8)

        # Info inicial
        self.show_system_info()

        # Bloquear maximizar
        self.after(0, lambda: disable_maximize_button(self))

    # ===== util ui =====
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

    # ===== abas =====
    def _build_tab_main(self):
        f = self.tab_main

        g = ttk.LabelFrame(f, text='Ações rápidas', style="Card.TLabelframe")
        g.pack(fill='x', padx=12, pady=12)
        self._grid_two_cols(g)

        self._btn(g, '🛡️  Criar ponto de restauração',
                  lambda: create_restore_point(f"WinOptimizer {datetime.now().strftime('%Y-%m-%d %H:%M')}")).grid(row=0, column=0, padx=8, pady=8, sticky="ew")
        self._btn(g, '🗑️  Esvaziar Lixeira', empty_recycle_bin).grid(row=0, column=1, padx=8, pady=8, sticky="ew")

        self._btn(g, '⚡  Otimizar unidades (defrag/TRIM)', self._action_optimize_drives).grid(row=1, column=0, padx=8, pady=8, sticky="ew")
        self._btn(g, '🧠  Otimizar memória RAM', self._action_optimize_ram, style="Secondary.TButton").grid(row=1, column=1, padx=8, pady=8, sticky="ew")

        self._btn(g, '🖼️  Miniaturas (pré-visualizar)', lambda: self._thumbs_action(True), style="Secondary.TButton").grid(row=2, column=0, padx=8, pady=8, sticky="ew")
        self._btn(g, '🧹  Miniaturas (executar)', lambda: self._thumbs_action(False)).grid(row=2, column=1, padx=8, pady=8, sticky="ew")

        h = ttk.LabelFrame(f, text='Atualizações de Driver', style="Card.TLabelframe")
        h.pack(fill='x', padx=12, pady=12); self._grid_two_cols(h)
        self._btn(h, '🔎  Buscar atualização de drivers (Windows Update)', scan_driver_updates)\
            .grid(row=0, column=0, padx=8, pady=8, sticky="ew")
        ttk.Label(h, text="Dica: para drivers OEM (placa-mãe, vídeo, etc.), use o app do fabricante.",
                  background=CARD_BG, foreground=TEXT_MUTE)\
            .grid(row=0, column=1, padx=8, pady=8, sticky="w")

        d = ttk.LabelFrame(f, text='Desfazer', style="Card.TLabelframe")
        d.pack(fill='x', padx=12, pady=12)
        self._grid_two_cols(d)
        self._btn(d, '↩️  Balanceado + Melhor aparência', revert_performance_tweaks, style="Danger.TButton")\
            .grid(row=0, column=0, columnspan=2, padx=8, pady=8, sticky="ew")

    def _build_tab_cache(self):
        f = self.tab_cache
        box = ttk.LabelFrame(f, text='Limpar cache de navegadores (Chrome, Edge, Opera/GX, Firefox)', style="Card.TLabelframe")
        box.pack(fill='x', padx=12, pady=12)

        desc = ("Esta ação limpa os caches dos navegadores suportados em todos os perfis detectados.\n"
                "Não há seleção manual: é limpeza geral de cache.")
        ttk.Label(box, text=desc, background=CARD_BG, foreground=TEXT_MUTE, justify='left').pack(anchor='w', padx=10, pady=(8, 12))

        btns = ttk.Frame(box, style="App.TFrame"); btns.pack(fill='x', padx=10, pady=(0,10))
        btns.columnconfigure(0, weight=1)
        ttk.Button(btns, text='🔍  Pré-visualizar (todos os navegadores)',
                   command=lambda: self._browser_cache_action(True),
                   style="Secondary.TButton").grid(row=0, column=1, padx=6, sticky="e")
        ttk.Button(btns, text='🧽  Limpar agora',
                   command=lambda: self._browser_cache_action(False),
                   style="Primary.TButton").grid(row=0, column=2, padx=6, sticky="e")

    def _build_tab_start(self):
        f = self.tab_start
        top = ttk.Frame(f, style="App.TFrame"); top.pack(fill='x', padx=12, pady=10)
        ttk.Button(top, text='🔄 Atualizar lista', command=self.refresh_startup, style="Secondary.TButton").pack(side='left')
        ttk.Button(top, text='🚫 Desabilitar selecionado', command=self.disable_selected, style="Danger.TButton").pack(side='left', padx=6)
        ttk.Button(top, text='✅ Habilitar selecionado', command=self.enable_selected, style="Primary.TButton").pack(side='left', padx=6)

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
        g1.pack(fill='x', padx=12, pady=12)
        self._grid_two_cols(g1)

        ttk.Button(
            g1,
            text="💪  Ativar: Alto desempenho",
            command=set_power_plan_high_performance,
            style="Primary.TButton"
        ).grid(row=0, column=0, padx=8, pady=8, sticky="ew")

        ttk.Button(
            g1,
            text="🧘  Ativar: Balanceado",
            command=set_power_plan_balanced,
            style="Secondary.TButton"
        ).grid(row=0, column=1, padx=8, pady=8, sticky="ew")

        g2 = ttk.LabelFrame(f, text='Aparência', style="Card.TLabelframe")
        g2.pack(fill='x', padx=12, pady=12)
        self._grid_two_cols(g2)

        ttk.Button(
            g2,
            text="🚀  Melhor desempenho",
            command=lambda: set_visual_effects_best_performance(True),
            style="Primary.TButton"
        ).grid(row=0, column=0, padx=8, pady=8, sticky="ew")

        ttk.Button(
            g2,
            text="✨  Melhor aparência",
            command=lambda: set_visual_effects_best_performance(False),
            style="Secondary.TButton"
        ).grid(row=0, column=1, padx=8, pady=8, sticky="ew")


    # ===== ações =====
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
        logging.info("Log em: %s", self.log_path)

    def _thumbs_action(self, dry_run: bool):
        cnt, total = clear_thumbnail_cache(dry_run=dry_run)
        if dry_run:
            messagebox.showinfo(self.app_name, f"Miniaturas (pré-visualização):\nArquivos: {cnt}\nTamanho: {human_size(total)}")
        else:
            messagebox.showinfo(self.app_name, f"Miniaturas removidas:\nArquivos: {cnt}\nTotal: {human_size(total)}")

    def _browser_cache_action(self, dry_run: bool):
        cnt, total = clear_all_browser_caches(dry_run=dry_run)
        if dry_run:
            messagebox.showinfo(self.app_name, f"Pré-visualização (todos os navegadores):\nArquivos: {cnt}\nTamanho: {human_size(total)}")
        else:
            messagebox.showinfo(self.app_name, f"Limpeza concluída:\nArquivos apagados: {cnt}\nTotal: {human_size(total)}")

    def refresh_startup(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        items = list_startup_entries()
        if not items:
            messagebox.showinfo(self.app_name, "Nenhum item encontrado ou sem permissão."); return
        for (loc, name, cmd) in items:
            self.tree.insert('', tk.END, values=(loc, name, cmd))

    def _selected_startup_name(self) -> str | None:
        sel = self.tree.selection()
        if not sel: return None
        vals = (self.tree.item(sel[0]).get('values') or [])
        return vals[1] if len(vals) >= 2 else None

    def disable_selected(self):
        name = self._selected_startup_name()
        if not name: messagebox.showinfo(self.app_name, "Selecione um item na lista."); return
        ok = disable_startup_entry(name)
        messagebox.showinfo(self.app_name, "OK" if ok else "Falhou. Veja logs."); self.refresh_startup()

    def enable_selected(self):
        name = self._selected_startup_name()
        if not name: messagebox.showinfo(self.app_name, "Selecione um item na lista."); return
        ok = enable_startup_entry(name)
        messagebox.showinfo(self.app_name, "OK" if ok else "Falhou. Veja logs."); self.refresh_startup()

    def _action_optimize_drives(self):
        import time as _t
        start = _t.time()
        ok = optimize_drives()
        elapsed = _t.time() - start
        mins = int(elapsed // 60); secs = int(elapsed % 60)
        if ok:
            messagebox.showinfo(self.app_name, f"Otimização concluída com sucesso!\n\nDuração: {mins} min {secs} s\nVeja o log para detalhes.")
        else:
            messagebox.showwarning(self.app_name, f"Otimização finalizada com avisos/erros.\n\nDuração: {mins} min {secs} s\nVeja o log para detalhes.")

    def _action_optimize_ram(self):
        import time as _t
        start = _t.time()
        ok_count, tries = optimize_memory_ram()
        elapsed = _t.time() - start
        mins = int(elapsed // 60); secs = int(elapsed % 60)
        messagebox.showinfo(self.app_name,
            f"Memória otimizada!\n\nProcessos ajustados: {ok_count} de {tries}\nDuração: {mins} min {secs} s")
