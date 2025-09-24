from __future__ import annotations
import os
import tkinter as tk
try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except Exception:
    HAS_PIL = False

from system.os_utils import resource_path

LOGO_FILENAME = "assets/DTO.png"
LOGO_SMALL_HEIGHT = 120
LOGO_LARGE_HEIGHT = 320

def load_logo_images(small_h: int = LOGO_SMALL_HEIGHT, large_h: int = LOGO_LARGE_HEIGHT) -> tuple[tk.PhotoImage | None, tk.PhotoImage | None]:
    path = resource_path(LOGO_FILENAME)
    if not os.path.exists(path):
        return None, None
    if HAS_PIL:
        try:
            img = Image.open(path).convert("RGBA")
            alpha = img.split()[-1]; bbox = alpha.getbbox()
            if bbox: img = img.crop(bbox)
            def make(h):
                w = int(round(img.width * (h / img.height)))
                return ImageTk.PhotoImage(img.resize((w, h), Image.LANCZOS))
            return make(small_h), make(large_h)
        except Exception:
            pass
    try:
        raw = tk.PhotoImage(file=path)
        factor_small = max(1, int(round(raw.height() / max(1, small_h))))
        factor_large = max(1, int(round(raw.height() / max(1, large_h))))
        return raw.subsample(factor_small), raw.subsample(factor_large)
    except Exception:
        return None, None
