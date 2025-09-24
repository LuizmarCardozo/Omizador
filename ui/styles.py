from __future__ import annotations
from tkinter import ttk

# Paleta
DARK_BG   = "#0f172a"  # header
LIGHT_BG  = "#f7f9fb"  # fundo
CARD_BG   = "#ffffff"  # cards
PRIMARY   = "#00a19a"  # teal
ACCENT    = "#f4c20d"  # amarelo
DANGER    = "#e53935"  # vermelho
TEXT_MUTE = "#6b7280"

def init_styles(root):
    style = ttk.Style(root)
    style.theme_use('clam')

    root.configure(bg=LIGHT_BG)
    style.configure("App.TFrame", background=LIGHT_BG)

    style.configure("Header.TFrame", background=DARK_BG)
    style.configure("Header.TLabel", background=DARK_BG, foreground="white")
    style.configure("HeaderTitle.TLabel", background=DARK_BG, foreground="white",
                    font=("Segoe UI Semibold", 16))
    style.configure("HeaderBadge.TLabel", background=DARK_BG, foreground=ACCENT, font=("Segoe UI", 10))

    style.configure("Footer.TFrame", background=LIGHT_BG)
    style.configure("Footer.TLabel", background=LIGHT_BG, foreground=TEXT_MUTE)

    style.configure("Card.TLabelframe", background=CARD_BG, relief="flat", borderwidth=1)
    style.configure("Card.TLabelframe.Label", background=CARD_BG, foreground="#111", font=("Segoe UI Semibold", 11))
    style.map("Card.TLabelframe", background=[("active", CARD_BG)])

    style.configure("Big.TNotebook", background=LIGHT_BG, borderwidth=0, tabmargins=(10, 8, 10, 0))
    style.configure("Big.TNotebook.Tab", font=("Segoe UI Semibold", 11), padding=(20, 12), background=LIGHT_BG)
    style.map("Big.TNotebook.Tab",
              background=[("selected", CARD_BG)],
              foreground=[("selected", "#111"), ("!selected", "#333")],
              expand=[("selected", [1, 1, 1, 0])])

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

    return style
