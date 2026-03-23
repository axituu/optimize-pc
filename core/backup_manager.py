"""
Manages backup/backup.json — saves original state before any tweak is applied.
Uses an in-memory cache so repeated record_* calls during an apply run only
read the file once and write it once per change (no redundant re-reads).
"""

import json
import sys
from pathlib import Path
from typing import Any, Optional

# When frozen by PyInstaller (--onefile), __file__ points to a temp extraction
# directory that is deleted when the process exits — backup data would be lost.
# Store backup.json next to the actual exe instead.
if getattr(sys, "frozen", False):
    _APP_DIR = Path(sys.executable).parent
else:
    _APP_DIR = Path(__file__).parent.parent

BACKUP_PATH = _APP_DIR / "backup" / "backup.json"

_cache: Optional[dict] = None


def _load_from_disk() -> dict:
    if not BACKUP_PATH.exists():
        return {}
    try:
        with open(BACKUP_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def load_backup() -> dict:
    """Return the current backup data (from cache if available)."""
    global _cache
    if _cache is None:
        _cache = _load_from_disk()
    return _cache


def save_backup(data: dict):
    """Persist backup data to disk and keep the cache in sync."""
    global _cache
    _cache = data
    BACKUP_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(BACKUP_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def record_service(name: str, original_start_type: str):
    """Save the original StartType of a service before disabling it."""
    data = load_backup()
    data.setdefault("services", {})[name] = original_start_type
    save_backup(data)


def record_registry(
    hive: str,
    path: str,
    name: str,
    original_value: Any,
    original_type: Optional[str],
):
    """
    Save original registry value before modification.
    original_type=None means the key did not exist — restore will delete the value.
    """
    data = load_backup()
    key_id = f"{hive}\\{path}\\{name}"
    data.setdefault("registry", {})[key_id] = {
        "hive": hive,
        "path": path,
        "name": name,
        "value": original_value,
        "type": original_type,
    }
    save_backup(data)


def record_task(task_path: str, was_enabled: bool):
    """Save the original enabled/disabled state of a scheduled task."""
    data = load_backup()
    data.setdefault("tasks", {})[task_path] = was_enabled
    save_backup(data)


def record_restore_cmds(tweak_id: str, cmds: list):
    """Save restore_cmds for tweaks with no registry backup (e.g. wake_timers, hibernation)."""
    data = load_backup()
    data.setdefault("restore_cmds", {})[tweak_id] = cmds
    save_backup(data)


def record_appx(package_name: str):
    """Log an AppX removal (informational — not reversible by this tool)."""
    data = load_backup()
    removed = data.setdefault("appx_removed", [])
    if package_name not in removed:
        removed.append(package_name)
    save_backup(data)


def is_already_backed_up(section: str, key: str) -> bool:
    """Return True if this key was already recorded (avoid double-backup on re-run)."""
    return key in load_backup().get(section, {})


def clear_backup():
    """Wipe the backup file and cache (called after a successful full restore)."""
    global _cache
    _cache = None
    if BACKUP_PATH.exists():
        BACKUP_PATH.unlink()
