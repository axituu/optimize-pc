"""
Fast registry reads using the stdlib winreg module.
Used during backup phase to avoid PowerShell subprocess overhead.
"""

import winreg
from typing import Optional, Tuple, Any

HIVE_MAP = {
    "HKCU": winreg.HKEY_CURRENT_USER,
    "HKLM": winreg.HKEY_LOCAL_MACHINE,
}

REG_TYPE_NAMES = {
    winreg.REG_DWORD: "DWORD",
    winreg.REG_QWORD: "QWORD",
    winreg.REG_SZ: "STRING",
    winreg.REG_EXPAND_SZ: "EXPAND_SZ",
    winreg.REG_BINARY: "BINARY",
    winreg.REG_MULTI_SZ: "MULTI_SZ",
}


def query_reg_value(hive: str, path: str, name: str) -> Tuple[Any, Optional[str]]:
    """
    Read a registry value.

    Returns:
        (value, type_name) — or (None, None) if the key/value doesn't exist.
        type_name is a string like "DWORD", "STRING", "BINARY", etc.
    """
    root = HIVE_MAP.get(hive)
    if root is None:
        return None, None
    try:
        key = winreg.OpenKey(root, path, 0, winreg.KEY_READ)
        value, reg_type = winreg.QueryValueEx(key, name)
        winreg.CloseKey(key)
        type_name = REG_TYPE_NAMES.get(reg_type, f"UNKNOWN_{reg_type}")
        # Convert bytes to list for JSON serialisation
        if isinstance(value, bytes):
            value = list(value)
        return value, type_name
    except FileNotFoundError:
        return None, None
    except OSError:
        return None, None
