"""
Gaming PC performance tweaks.
Designed for a dedicated gaming desktop — no ThinkPad / power-plan restrictions.
"""

from typing import Callable, Optional

from core.executor import run_ps, run_ps_query
from core.reg_query import query_reg_value
from core.backup_manager import (
    record_service,
    record_registry,
    record_restore_cmds,
    is_already_backed_up,
)

GAMING_TWEAKS = [
    {
        "id": "game_mode",
        "label": "Enable Windows Game Mode",
        "description": "Tells Windows to prioritize the foreground game for CPU and GPU resources.",
        "default": True,
        "type": "registry",
        "backup_keys": [
            {
                "hive": "HKCU",
                "path": r"Software\Microsoft\GameBar",
                "name": "AutoGameModeEnabled",
            },
        ],
        "cmds": [
            r'New-Item -Path "HKCU:\Software\Microsoft\GameBar" -Force -ErrorAction SilentlyContinue | Out-Null',
            r'Set-ItemProperty -Path "HKCU:\Software\Microsoft\GameBar" -Name "AutoGameModeEnabled" -Value 1 -Type DWord -Force',
        ],
    },
    {
        "id": "fullscreen_opt",
        "label": "Disable Fullscreen Optimizations Globally",
        "description": "FSO can cause micro-stutters and input latency. Disabling reverts to exclusive fullscreen.",
        "default": True,
        "type": "registry",
        "backup_keys": [
            {
                "hive": "HKCU",
                "path": r"System\GameConfigStore",
                "name": "FSEBehaviorMode",
            },
        ],
        "cmds": [
            r'Set-ItemProperty -Path "HKCU:\System\GameConfigStore" -Name "FSEBehaviorMode" -Value 2 -Type DWord -Force',
        ],
    },
    {
        "id": "power_throttling",
        "label": "Disable CPU Power Throttling",
        "description": "Stops Windows throttling process clocks to save power. Requires restart.",
        "default": True,
        "type": "registry",
        "backup_keys": [
            {
                "hive": "HKLM",
                "path": r"SYSTEM\CurrentControlSet\Control\Power\PowerThrottling",
                "name": "PowerThrottlingOff",
            },
        ],
        "cmds": [
            r'New-Item -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Power\PowerThrottling" -Force -ErrorAction SilentlyContinue | Out-Null',
            r'Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Power\PowerThrottling" -Name "PowerThrottlingOff" -Value 1 -Type DWord -Force',
        ],
        "restore_cmds": [
            r'Remove-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Power\PowerThrottling" -Name "PowerThrottlingOff" -ErrorAction SilentlyContinue',
        ],
    },
    {
        "id": "hpet",
        "label": "Disable HPET (High Precision Event Timer)",
        "description": "On modern CPUs the TSC is more accurate. Disabling HPET can lower DPC latency. Requires restart.",
        "default": False,
        "type": "command",
        "backup_keys": [],
        "cmds": [
            "bcdedit /set useplatformclock false",
        ],
        "restore_cmds": [
            "bcdedit /deletevalue useplatformclock",
        ],
    },
    {
        "id": "hags",
        "label": "Enable Hardware-Accelerated GPU Scheduling (HAGS)",
        "description": "Moves GPU memory management to the GPU itself, reducing CPU overhead and frame latency. Requires restart.",
        "default": True,
        "type": "registry",
        "backup_keys": [
            {
                "hive": "HKLM",
                "path": r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers",
                "name": "HwSchMode",
            },
        ],
        "cmds": [
            r'Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\GraphicsDrivers" -Name "HwSchMode" -Value 2 -Type DWord -Force',
        ],
        "restore_cmds": [
            r'Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\GraphicsDrivers" -Name "HwSchMode" -Value 1 -Type DWord -Force',
        ],
    },
    {
        "id": "mouse_accel",
        "label": "Disable Mouse Acceleration (Enhanced Pointer Precision)",
        "description": "Removes the Windows mouse acceleration curve for 1:1 physical-to-cursor movement.",
        "default": True,
        "type": "registry",
        "backup_keys": [
            {"hive": "HKCU", "path": r"Control Panel\Mouse", "name": "MouseSpeed"},
            {"hive": "HKCU", "path": r"Control Panel\Mouse", "name": "MouseThreshold1"},
            {"hive": "HKCU", "path": r"Control Panel\Mouse", "name": "MouseThreshold2"},
        ],
        "cmds": [
            r'$p = "HKCU:\Control Panel\Mouse"; '
            r'Set-ItemProperty $p -Name "MouseSpeed" -Value "0" -Force; '
            r'Set-ItemProperty $p -Name "MouseThreshold1" -Value "0" -Force; '
            r'Set-ItemProperty $p -Name "MouseThreshold2" -Value "0" -Force',
        ],
    },
    {
        "id": "nagle_algorithm",
        "label": "Disable Nagle's Algorithm on All Network Adapters",
        "description": "Nagle buffers small TCP packets — disabling it lowers online game latency at the cost of slightly more packets.",
        "default": True,
        "type": "command",
        "backup_keys": [],
        "cmds": [
            r"""$base = "HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces"
Get-ChildItem $base | ForEach-Object {
    Set-ItemProperty -Path $_.PSPath -Name "TcpAckFrequency" -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue
    Set-ItemProperty -Path $_.PSPath -Name "TCPNoDelay"      -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue
}""",
        ],
        "restore_cmds": [
            r"""$base = "HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces"
Get-ChildItem $base | ForEach-Object {
    Remove-ItemProperty -Path $_.PSPath -Name "TcpAckFrequency" -ErrorAction SilentlyContinue
    Remove-ItemProperty -Path $_.PSPath -Name "TCPNoDelay"      -ErrorAction SilentlyContinue
}""",
        ],
    },
    {
        "id": "priority_gpu",
        "label": "Maximize GPU & Game Priority in Windows Scheduler",
        "description": "Sets GPU Priority=8, CPU Priority=6, and removes network throttling in the Windows Multimedia Scheduler.",
        "default": True,
        "type": "registry",
        "backup_keys": [
            {
                "hive": "HKLM",
                "path": r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games",
                "name": "GPU Priority",
            },
            {
                "hive": "HKLM",
                "path": r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games",
                "name": "Priority",
            },
            {
                "hive": "HKLM",
                "path": r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile",
                "name": "NetworkThrottlingIndex",
            },
        ],
        "cmds": [
            r'$p = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games"; '
            r"New-Item -Path $p -Force -ErrorAction SilentlyContinue | Out-Null; "
            r'Set-ItemProperty -Path $p -Name "GPU Priority" -Value 8 -Type DWord -Force; '
            r'Set-ItemProperty -Path $p -Name "Priority"     -Value 6 -Type DWord -Force',
            r'Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" -Name "NetworkThrottlingIndex" -Value 0xFFFFFFFF -Type DWord -Force',
        ],
    },
]


def apply_gaming_tweak(
    tweak: dict,
    log_callback: Optional[Callable[[str], None]] = None,
):
    tweak_type = tweak.get("type", "registry")

    if tweak_type == "service":
        svc_name = tweak["service"]
        if not is_already_backed_up("services", svc_name):
            current = run_ps_query(
                f'(Get-Service -Name "{svc_name}" -ErrorAction SilentlyContinue).StartType'
            )
            record_service(svc_name, current or "Manual")
        if log_callback:
            log_callback(f"[SERVICE] {svc_name} → {tweak['target']}")
        run_ps(
            f'Set-Service -Name "{svc_name}" -StartupType {tweak["target"]} -ErrorAction SilentlyContinue',
            log_callback,
        )
        return

    # Backup registry keys
    for bk in tweak.get("backup_keys", []):
        key_id = f"{bk['hive']}\\{bk['path']}\\{bk['name']}"
        if not is_already_backed_up("registry", key_id):
            value, reg_type = query_reg_value(bk["hive"], bk["path"], bk["name"])
            record_registry(bk["hive"], bk["path"], bk["name"], value, reg_type)

    if tweak.get("restore_cmds") and not is_already_backed_up(
        "restore_cmds", tweak["id"]
    ):
        record_restore_cmds(tweak["id"], tweak["restore_cmds"])

    if log_callback:
        log_callback(f"[GAMING] Applying: {tweak['label']}")

    for cmd in tweak.get("cmds", []):
        run_ps(cmd, log_callback)
