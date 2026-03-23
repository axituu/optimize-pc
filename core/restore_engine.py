"""
Reads backup.json and reverts every recorded change.
AppX removals are noted but cannot be automatically reversed.
"""

from typing import Callable, Optional

from core.backup_manager import load_backup, clear_backup
from core.executor import run_ps


def restore_all(
    log_callback: Optional[Callable[[str], None]] = None,
    clear_after: bool = True,
):
    data = load_backup()
    if not data:
        if log_callback:
            log_callback("[INFO] No backup data found — nothing to restore.")
        return

    errors = 0

    # --- Restore services ---
    for svc_name, start_type in data.get("services", {}).items():
        if log_callback:
            log_callback(f"[SERVICE] Restoring {svc_name} → {start_type}")
        # Map plain names to PowerShell StartupType enum values
        start_map = {
            "Automatic": "Automatic",
            "Automatic (Delayed Start)": "AutomaticDelayedStart",
            "AutomaticDelayedStart": "AutomaticDelayedStart",
            "Manual": "Manual",
            "Disabled": "Disabled",
        }
        ps_start = start_map.get(str(start_type), "Manual")
        r = run_ps(
            f'Set-Service -Name "{svc_name}" -StartupType {ps_start} -ErrorAction SilentlyContinue; '
            f'if ("{ps_start}" -ne "Disabled") {{ Start-Service -Name "{svc_name}" -ErrorAction SilentlyContinue }}',
            log_callback,
        )
        if not r["success"]:
            errors += 1

    # --- Restore registry values ---
    type_map = {
        "DWORD": "DWord",
        "QWORD": "QWord",
        "STRING": "String",
        "EXPAND_SZ": "ExpandString",
        "BINARY": "Binary",
        "MULTI_SZ": "MultiString",
    }
    hive_ps = {"HKCU": "HKCU:", "HKLM": "HKLM:"}

    for key_id, info in data.get("registry", {}).items():
        hive = info["hive"]
        path = info["path"]
        name = info["name"]
        value = info["value"]
        reg_type = info["type"]

        ps_path = f"{hive_ps[hive]}\\{path}"

        if reg_type is None:
            # Key didn't exist before — delete it
            if log_callback:
                log_callback(f"[REGISTRY] Removing {key_id} (was absent)")
            r = run_ps(
                f'Remove-ItemProperty -Path "{ps_path}" -Name "{name}" -ErrorAction SilentlyContinue',
                log_callback,
            )
        else:
            if log_callback:
                log_callback(f"[REGISTRY] Restoring {key_id} = {value} ({reg_type})")
            ps_type = type_map.get(reg_type, "String")
            # Handle binary (list of ints → byte array)
            if reg_type == "BINARY" and isinstance(value, list):
                byte_str = ",".join(str(b) for b in value)
                ps_value = f"([byte[]]@({byte_str}))"
            elif reg_type in ("STRING", "EXPAND_SZ", "MULTI_SZ"):
                ps_value = f'"{value}"'
            else:
                ps_value = str(value)
            r = run_ps(
                f'New-Item -Path "{ps_path}" -Force -ErrorAction SilentlyContinue | Out-Null; '
                f'Set-ItemProperty -Path "{ps_path}" -Name "{name}" -Value {ps_value} -Type {ps_type} -Force -ErrorAction SilentlyContinue',
                log_callback,
            )
        if not r["success"]:
            errors += 1

    # --- Restore scheduled tasks ---
    for task_path, was_enabled in data.get("tasks", {}).items():
        parts = task_path.rsplit("\\", 1)
        if len(parts) == 2:
            folder = parts[0] + "\\"
            task_name = parts[1]
        else:
            folder = "\\"
            task_name = task_path

        action = "Enable" if was_enabled else "Disable"
        if log_callback:
            log_callback(f"[TASK] {action}ing {task_name}")
        r = run_ps(
            f'{action}-ScheduledTask -TaskPath "{folder}" -TaskName "{task_name}" -ErrorAction SilentlyContinue',
            log_callback,
        )
        if not r["success"]:
            errors += 1

    # --- restore_cmds (e.g. wake_timers, hibernation) ---
    for tweak_id, cmds in data.get("restore_cmds", {}).items():
        if log_callback:
            log_callback(f"[CMD] Restoring via restore_cmds: {tweak_id}")
        for cmd in cmds:
            r = run_ps(cmd, log_callback)
            if not r["success"]:
                errors += 1

    # --- AppX (informational only) ---
    removed = data.get("appx_removed", [])
    if removed and log_callback:
        log_callback(
            f"[INFO] {len(removed)} AppX package(s) were removed and cannot be auto-restored:"
        )
        for pkg in removed:
            log_callback(f"       {pkg}")

    if log_callback:
        if errors:
            log_callback(
                f"[DONE] Restore complete with {errors} error(s). Check log above."
            )
        else:
            log_callback("[DONE] Restore complete. Restart recommended.")

    if clear_after and errors == 0:
        clear_backup()
