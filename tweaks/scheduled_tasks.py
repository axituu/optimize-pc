"""
Scheduled task disable/enable tweaks.
"""

from typing import Callable, Optional

from core.executor import run_ps, run_ps_query
from core.backup_manager import record_task, is_already_backed_up

TASKS = [
    {
        "id": "compat_appraiser",
        "label": "Disable Compatibility Appraiser (upgrade telemetry)",
        "description": "Scans your software for Windows upgrade compatibility. Telemetry-driven.",
        "folder": "\\Microsoft\\Windows\\Application Experience\\",
        "name": "Microsoft Compatibility Appraiser",
        "default": True,
    },
    {
        "id": "ceip_consolidator",
        "label": "Disable CEIP Consolidator (Customer Experience telemetry)",
        "description": "Collects usage patterns and sends them to Microsoft.",
        "folder": "\\Microsoft\\Windows\\Customer Experience Improvement Program\\",
        "name": "Consolidator",
        "default": True,
    },
    {
        "id": "ceip_usb",
        "label": "Disable CEIP USB telemetry",
        "description": "Tracks USB device usage for Microsoft's CEIP program.",
        "folder": "\\Microsoft\\Windows\\Customer Experience Improvement Program\\",
        "name": "UsbCeip",
        "default": True,
    },
    {
        "id": "disk_diag",
        "label": "Disable Disk Diagnostic Data Collector",
        "description": "Sends disk health data to Microsoft.",
        "folder": "\\Microsoft\\Windows\\Disk Diagnostic\\",
        "name": "Microsoft-Windows-DiskDiagnosticDataCollector",
        "default": True,
    },
    {
        "id": "winsat",
        "label": "Disable WinSAT Performance Benchmark",
        "description": "Runs CPU/GPU/disk benchmarks in the background. Useless on modern hardware.",
        "folder": "\\Microsoft\\Windows\\Maintenance\\",
        "name": "WinSAT",
        "default": True,
    },
    {
        "id": "maps_toast",
        "label": "Disable Maps Toast Task",
        "description": "Toast notifications for Windows Maps app.",
        "folder": "\\Microsoft\\Windows\\Maps\\",
        "name": "MapsToastTask",
        "default": True,
    },
    {
        "id": "maps_update",
        "label": "Disable Maps Update Task",
        "description": "Background map data updates for the Maps app.",
        "folder": "\\Microsoft\\Windows\\Maps\\",
        "name": "MapsUpdateTask",
        "default": True,
    },
    {
        "id": "defrag",
        "label": "Disable Scheduled Defragmentation (SSD)",
        "description": "Windows skips defrag on SSDs but still runs the task. Safe to disable.",
        "folder": "\\Microsoft\\Windows\\Defrag\\",
        "name": "ScheduledDefrag",
        "default": True,
    },
    {
        "id": "wu_auto_app",
        "label": "Disable Automatic App Update (Windows Update)",
        "description": "Stops automatic Store app updates via Windows Update.",
        "folder": "\\Microsoft\\Windows\\WindowsUpdate\\",
        "name": "Automatic App Update",
        "default": False,
    },
]


def _task_key(task: dict) -> str:
    return task["folder"].rstrip("\\") + "\\" + task["name"]


def apply_task_disable(
    task: dict,
    log_callback: Optional[Callable[[str], None]] = None,
):
    folder = task["folder"]
    name = task["name"]
    key = _task_key(task)

    # Backup current state
    if not is_already_backed_up("tasks", key):
        state = run_ps_query(
            f'(Get-ScheduledTask -TaskPath "{folder}" -TaskName "{name}" -ErrorAction SilentlyContinue).State'
        )
        was_enabled = state.strip().lower() == "ready"
        record_task(key, was_enabled)

    if log_callback:
        log_callback(f"[TASK] Disabling: {name}")

    run_ps(
        f'Disable-ScheduledTask -TaskPath "{folder}" -TaskName "{name}" -ErrorAction SilentlyContinue',
        log_callback,
    )
