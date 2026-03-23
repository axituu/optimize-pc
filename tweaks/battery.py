"""
Battery efficiency tweaks.
Power plans are never touched. Active plan settings (wake timers) are modified
via powercfg targeting SCHEME_CURRENT only.
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

BATTERY_TWEAKS = [
    {
        "id": "usb_selective_suspend",
        "label": "Enable USB Selective Suspend",
        "description": "Allows idle USB devices to be suspended to save power. Safe on ThinkPads.",
        "default": True,
        "type": "registry",
        "backup_keys": [
            {
                "hive": "HKLM",
                "path": r"SYSTEM\CurrentControlSet\Services\USB",
                "name": "DisableSelectiveSuspend",
            },
        ],
        "cmds": [
            r'Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\USB" -Name "DisableSelectiveSuspend" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue',
        ],
    },
    {
        "id": "wifi_scan",
        "label": "Reduce Background WiFi Scanning",
        "description": "Disables NLA active probing and reduces wlan autoconfig scan frequency.",
        "default": True,
        "type": "registry",
        "backup_keys": [
            {
                "hive": "HKLM",
                "path": r"SYSTEM\CurrentControlSet\Services\NlaSvc\Parameters\Internet",
                "name": "EnableActiveProbing",
            },
        ],
        "cmds": [
            r'Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\NlaSvc\Parameters\Internet" -Name "EnableActiveProbing" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue',
        ],
    },
    {
        "id": "bluetooth_manual",
        "label": "Set Bluetooth Service to Manual Start",
        "description": "Bluetooth won't auto-start on boot. Start it manually when needed.",
        "default": True,
        "type": "service",
        "service": "bthserv",
        "target": "Manual",
    },
    {
        "id": "wake_timers",
        "label": "Disable Wake Timers on Active Plan",
        "description": "Prevents background tasks from waking the laptop from sleep. Modifies the currently-active power plan's wake-timer setting only (not the plan itself).",
        "default": True,
        "type": "command",
        "backup_keys": [],
        "cmds": [
            "powercfg /setacvalueindex SCHEME_CURRENT SUB_SLEEP RTCWAKE 0",
            "powercfg /setdcvalueindex SCHEME_CURRENT SUB_SLEEP RTCWAKE 0",
            "powercfg /setactive SCHEME_CURRENT",
        ],
        "restore_cmds": [
            "powercfg /setacvalueindex SCHEME_CURRENT SUB_SLEEP RTCWAKE 1",
            "powercfg /setdcvalueindex SCHEME_CURRENT SUB_SLEEP RTCWAKE 1",
            "powercfg /setactive SCHEME_CURRENT",
        ],
    },
    {
        "id": "lock_screen_spotlight",
        "label": "Disable Lock Screen Spotlight & Ads",
        "description": "Stops Microsoft rotating ads/tips on your lock screen.",
        "default": False,
        "type": "registry",
        "backup_keys": [
            {
                "hive": "HKCU",
                "path": r"Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager",
                "name": "RotatingLockScreenEnabled",
            },
            {
                "hive": "HKCU",
                "path": r"Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager",
                "name": "RotatingLockScreenOverlayEnabled",
            },
        ],
        "cmds": [
            r'$p = "HKCU:\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager"; Set-ItemProperty $p -Name "RotatingLockScreenEnabled" -Value 0 -Type DWord -Force; Set-ItemProperty $p -Name "RotatingLockScreenOverlayEnabled" -Value 0 -Type DWord -Force',
        ],
    },
    {
        "id": "fast_startup",
        "label": "Enable Fast Startup (Hybrid Boot)",
        "description": "Speeds up boot by saving kernel state. Safe on ThinkPad.",
        "default": True,
        "type": "registry",
        "backup_keys": [
            {
                "hive": "HKLM",
                "path": r"SYSTEM\CurrentControlSet\Control\Session Manager\Power",
                "name": "HiberbootEnabled",
            },
        ],
        "cmds": [
            r'Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Power" -Name "HiberbootEnabled" -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue',
        ],
    },
    {
        "id": "ahci_lpm",
        "label": "Enable AHCI Link Power Management (HIPM+DIPM)",
        "description": "Allows the NVMe/SATA link to enter low-power states when idle. Can reduce battery draw by ~0.5W.",
        "default": False,
        "type": "registry",
        "backup_keys": [
            {
                "hive": "HKLM",
                "path": r"SYSTEM\CurrentControlSet\Services\storahci\Parameters\Device",
                "name": "LPMState",
            },
        ],
        "cmds": [
            r'New-Item -Path "HKLM:\SYSTEM\CurrentControlSet\Services\storahci\Parameters\Device" -Force -ErrorAction SilentlyContinue | Out-Null',
            r'Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\storahci\Parameters\Device" -Name "LPMState" -Value 3 -Type DWord -Force -ErrorAction SilentlyContinue',
        ],
    },
    {
        "id": "nic_wol",
        "label": "Disable NIC Wake-on-LAN & Power Management Override",
        "description": "Prevents the network adapter from waking the system and overriding OS power settings.",
        "default": False,
        "type": "command",
        "backup_keys": [],
        "cmds": [
            r"""
$adapters = Get-NetAdapter | Where-Object {$_.Status -eq "Up"}
foreach ($adapter in $adapters) {
    $ifDesc = $adapter.InterfaceDescription
    $regPath = Get-ChildItem "HKLM:\SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}" -ErrorAction SilentlyContinue |
        Where-Object { (Get-ItemProperty -Path $_.PSPath -ErrorAction SilentlyContinue).DriverDesc -eq $ifDesc }
    if ($regPath) {
        Set-ItemProperty -Path $regPath.PSPath -Name "PnPCapabilities" -Value 24 -Type DWord -Force -ErrorAction SilentlyContinue
    }
}
""".strip(),
        ],
    },
]


def apply_battery_tweak(
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
        log_callback(f"[BATTERY] Applying: {tweak['label']}")

    for cmd in tweak.get("cmds", []):
        run_ps(cmd, log_callback)
