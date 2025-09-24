from __future__ import annotations
import os, logging, time
try:
    from send2trash import send2trash  # type: ignore
    HAS_SEND2TRASH = True
except Exception:
    HAS_SEND2TRASH = False

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
                    try:
                        os.chmod(fpath, 0o666); os.remove(fpath); count += 1
                    except Exception:
                        logging.debug("Não foi possível excluir: %s", fpath)
                except Exception:
                    logging.debug("Não foi possível excluir: %s", fpath)
    return count, total_bytes

def enumerate_browser_cache_paths() -> list[str]:
    """Chrome, Edge, Opera/GX, Firefox (todos perfis)."""
    paths: list[str] = []
    localapp = os.environ.get('LOCALAPPDATA', '')
    appdata  = os.environ.get('APPDATA', '')

    def add_if_exists(p: str):
        if p and os.path.isdir(p):
            paths.append(p)

    def add_chromium_profile_caches(root: str):
        if not os.path.isdir(root): return
        for prof in os.listdir(root):
            prof_path = os.path.join(root, prof)
            if not os.path.isdir(prof_path): continue
            for sub in [
                'Cache',
                os.path.join('Code Cache', 'js'),
                os.path.join('Code Cache', 'wasm'),
                'GPUCache',
                os.path.join('Service Worker', 'CacheStorage'),
                'Media Cache',
                'ShaderCache',
            ]:
                add_if_exists(os.path.join(prof_path, sub))

    # Chrome
    add_chromium_profile_caches(os.path.join(localapp, 'Google', 'Chrome', 'User Data'))
    # Edge
    add_chromium_profile_caches(os.path.join(localapp, 'Microsoft', 'Edge', 'User Data'))
    # Opera / GX (Roaming ou Local)
    for base in (appdata, localapp):
        opera_root = os.path.join(base, 'Opera Software')
        if os.path.isdir(opera_root):
            for ed in ('Opera Stable', 'Opera GX Stable'):
                add_chromium_profile_caches(os.path.join(opera_root, ed))

    # Firefox
    ff_profiles = os.path.join(appdata, 'Mozilla', 'Firefox', 'Profiles')
    if os.path.isdir(ff_profiles):
        for prof in os.listdir(ff_profiles):
            prof_path = os.path.join(ff_profiles, prof)
            if not os.path.isdir(prof_path): continue
            add_if_exists(os.path.join(prof_path, 'cache2'))
            add_if_exists(os.path.join(prof_path, 'startupCache'))
            add_if_exists(os.path.join(prof_path, 'jumpListCache'))
            add_if_exists(os.path.join(prof_path, 'storage', 'default'))

    return paths

def clear_all_browser_caches(dry_run: bool = False) -> tuple[int, int]:
    paths = enumerate_browser_cache_paths()
    if not paths:
        logging.info("Nenhuma pasta de cache de navegador encontrada.")
        return (0, 0)
    # 0 dias = apaga tudo
    return _delete_from_paths(paths, dry_run=dry_run, older_than_days=0)

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
        logging.info("Miniaturas encontradas: %d (%.1f KB)", len(targets), total/1024); return (len(targets), total)
    deleted = 0
    for f in targets:
        try:
            if HAS_SEND2TRASH: send2trash(f)
            else: os.remove(f)
            deleted += 1
        except Exception:
            logging.debug("Não foi possível remover: %s (provavelmente em uso)", f)
    logging.info("Miniaturas removidas: %d (%.1f KB)", deleted, total/1024)
    return (deleted, total)
