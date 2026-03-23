"""
Performance tweaks: services, registry, and command-based tweaks.
Power plans are never touched.
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

# ---------------------------------------------------------------------------
# Service tweaks
# ---------------------------------------------------------------------------

SERVICES = [
    {
        "id": "sysmain",
        "label": "Disable SysMain / Superfetch",
        "description": "Not needed on NVMe SSD. Causes disk thrashing on HDDs only.",
        "service": "SysMain",
        "target": "Disabled",
        "default": True,
    },
    {
        "id": "wsearch",
        "label": "Set Windows Search to Manual (reduce indexing overhead)",
        "description": "Manual start preserves Start menu search while stopping background indexing.",
        "service": "WSearch",
        "target": "Manual",
        "default": True,
    },
    {
        "id": "diagtrack",
        "label": "Disable Telemetry Service (DiagTrack)",
        "description": "Stops Windows sending diagnostic/usage data to Microsoft.",
        "service": "DiagTrack",
        "target": "Disabled",
        "default": True,
    },
    {
        "id": "wer_svc",
        "label": "Disable Windows Error Reporting Service",
        "description": "Stops crash reports being sent to Microsoft.",
        "service": "WerSvc",
        "target": "Disabled",
        "default": True,
    },
    {
        "id": "remote_registry",
        "label": "Disable Remote Registry",
        "description": "Prevents remote access to this machine's registry.",
        "service": "RemoteRegistry",
        "target": "Disabled",
        "default": True,
    },
    {
        "id": "fax",
        "label": "Disable Fax Service",
        "description": "Fax service — not needed on modern hardware.",
        "service": "Fax",
        "target": "Disabled",
        "default": True,
    },
    {
        "id": "spooler",
        "label": "Disable Print Spooler (only if no printer)",
        "description": "Disable ONLY if you have no printer. Some PDF apps depend on the spooler.",
        "service": "Spooler",
        "target": "Disabled",
        "default": False,
    },
]

# ---------------------------------------------------------------------------
# Registry tweaks — each entry may have multiple PS commands via "cmds" list
# ---------------------------------------------------------------------------

# Format: id, label, description, default, backup_keys (list of dicts), cmds (list of PS strings)
REGISTRY_TWEAKS = [
    {
        "id": "visual_effects",
        "label": "Disable Visual Effects (best performance)",
        "description": "Turns off animations, shadows, fades. Noticeably faster UI.",
        "default": True,
        "backup_keys": [
            {
                "hive": "HKCU",
                "path": r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects",
                "name": "VisualFXSetting",
            },
            {
                "hive": "HKCU",
                "path": r"Control Panel\Desktop\WindowMetrics",
                "name": "MinAnimate",
            },
            {
                "hive": "HKCU",
                "path": r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
                "name": "TaskbarAnimations",
            },
            {
                "hive": "HKCU",
                "path": r"Software\Microsoft\Windows\DWM",
                "name": "EnableAeroPeek",
            },
        ],
        "cmds": [
            r'New-Item -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects" -Force -ErrorAction SilentlyContinue | Out-Null',
            r'Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects" -Name "VisualFXSetting" -Value 2 -Type DWord -Force',
            r'Set-ItemProperty -Path "HKCU:\Control Panel\Desktop\WindowMetrics" -Name "MinAnimate" -Value "0" -Force',
            r'Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "TaskbarAnimations" -Value 0 -Type DWord -Force',
            r'Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\DWM" -Name "EnableAeroPeek" -Value 0 -Type DWord -Force',
        ],
    },
    {
        "id": "transparency",
        "label": "Disable Transparency Effects",
        "description": "Reduces GPU compositing overhead and saves a little battery.",
        "default": True,
        "backup_keys": [
            {
                "hive": "HKCU",
                "path": r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
                "name": "EnableTransparency",
            },
        ],
        "cmds": [
            r'Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize" -Name "EnableTransparency" -Value 0 -Type DWord -Force',
        ],
    },
    {
        "id": "tips_suggestions",
        "label": "Disable Windows Tips & Suggestions",
        "description": "Stops suggested apps, tips popups, and Start menu ads.",
        "default": True,
        "backup_keys": [
            {
                "hive": "HKCU",
                "path": r"Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager",
                "name": "SoftLandingEnabled",
            },
            {
                "hive": "HKCU",
                "path": r"Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager",
                "name": "SubscribedContent-338389Enabled",
            },
            {
                "hive": "HKCU",
                "path": r"Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager",
                "name": "SubscribedContent-338393Enabled",
            },
            {
                "hive": "HKCU",
                "path": r"Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager",
                "name": "SystemPaneSuggestionsEnabled",
            },
            {
                "hive": "HKCU",
                "path": r"Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager",
                "name": "SilentInstalledAppsEnabled",
            },
        ],
        "cmds": [
            r'$p = "HKCU:\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager"; Set-ItemProperty $p -Name "SoftLandingEnabled" -Value 0 -Type DWord -Force; Set-ItemProperty $p -Name "SubscribedContent-338389Enabled" -Value 0 -Type DWord -Force; Set-ItemProperty $p -Name "SubscribedContent-338393Enabled" -Value 0 -Type DWord -Force; Set-ItemProperty $p -Name "SystemPaneSuggestionsEnabled" -Value 0 -Type DWord -Force; Set-ItemProperty $p -Name "SilentInstalledAppsEnabled" -Value 0 -Type DWord -Force',
        ],
    },
    {
        "id": "telemetry",
        "label": "Set Telemetry to Minimal (Security level)",
        "description": "Restricts Windows data collection to minimum allowed on Pro/Home.",
        "default": True,
        "backup_keys": [
            {
                "hive": "HKLM",
                "path": r"SOFTWARE\Policies\Microsoft\Windows\DataCollection",
                "name": "AllowTelemetry",
            },
        ],
        "cmds": [
            r'New-Item -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\DataCollection" -Force -ErrorAction SilentlyContinue | Out-Null',
            r'Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\DataCollection" -Name "AllowTelemetry" -Value 1 -Type DWord -Force',
        ],
    },
    {
        "id": "game_dvr",
        "label": "Disable Xbox Game DVR / Game Bar Recording",
        "description": "Removes background recording hooks that consume CPU even outside games.",
        "default": True,
        "backup_keys": [
            {
                "hive": "HKCU",
                "path": r"System\GameConfigStore",
                "name": "GameDVR_Enabled",
            },
            {
                "hive": "HKLM",
                "path": r"SOFTWARE\Policies\Microsoft\Windows\GameDVR",
                "name": "AllowGameDVR",
            },
        ],
        "cmds": [
            r'Set-ItemProperty -Path "HKCU:\System\GameConfigStore" -Name "GameDVR_Enabled" -Value 0 -Type DWord -Force',
            r'New-Item -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\GameDVR" -Force -ErrorAction SilentlyContinue | Out-Null',
            r'Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\GameDVR" -Name "AllowGameDVR" -Value 0 -Type DWord -Force',
        ],
    },
    {
        "id": "delivery_opt",
        "label": "Disable Windows Update P2P Delivery Optimization",
        "description": "Stops Windows from uploading your downloaded updates to other PCs on the internet.",
        "default": True,
        "backup_keys": [
            {
                "hive": "HKLM",
                "path": r"SOFTWARE\Policies\Microsoft\Windows\DeliveryOptimization",
                "name": "DODownloadMode",
            },
        ],
        "cmds": [
            r'New-Item -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\DeliveryOptimization" -Force -ErrorAction SilentlyContinue | Out-Null',
            r'Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\DeliveryOptimization" -Name "DODownloadMode" -Value 0 -Type DWord -Force',
        ],
    },
    {
        "id": "defender_samples",
        "label": "Disable Defender Sample Submission (keep real-time protection)",
        "description": "Stops files being sent to Microsoft cloud for analysis. Real-time AV stays active.",
        "default": True,
        "backup_keys": [
            {
                "hive": "HKLM",
                "path": r"SOFTWARE\Policies\Microsoft\Windows Defender\Spynet",
                "name": "SubmitSamplesConsent",
            },
            {
                "hive": "HKLM",
                "path": r"SOFTWARE\Policies\Microsoft\Windows Defender\Spynet",
                "name": "SpynetReporting",
            },
        ],
        "cmds": [
            r'New-Item -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows Defender\Spynet" -Force -ErrorAction SilentlyContinue | Out-Null',
            r'Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows Defender\Spynet" -Name "SubmitSamplesConsent" -Value 2 -Type DWord -Force',
            r'Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows Defender\Spynet" -Name "SpynetReporting" -Value 0 -Type DWord -Force',
        ],
    },
    {
        "id": "bg_apps",
        "label": "Disable Background Apps Globally",
        "description": "Prevents UWP apps from running in the background when not in use.",
        "default": True,
        "backup_keys": [
            {
                "hive": "HKCU",
                "path": r"Software\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications",
                "name": "GlobalUserDisabled",
            },
            {
                "hive": "HKLM",
                "path": r"SOFTWARE\Policies\Microsoft\Windows\AppPrivacy",
                "name": "LetAppsRunInBackground",
            },
        ],
        "cmds": [
            r'Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications" -Name "GlobalUserDisabled" -Value 1 -Type DWord -Force',
            r'New-Item -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\AppPrivacy" -Force -ErrorAction SilentlyContinue | Out-Null',
            r'Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\AppPrivacy" -Name "LetAppsRunInBackground" -Value 2 -Type DWord -Force',
        ],
    },
    {
        "id": "cortana_search",
        "label": "Disable Cortana in Search",
        "description": "Disables Cortana integration in Windows Search via policy.",
        "default": True,
        "backup_keys": [
            {
                "hive": "HKLM",
                "path": r"SOFTWARE\Policies\Microsoft\Windows\Windows Search",
                "name": "AllowCortana",
            },
        ],
        "cmds": [
            r'New-Item -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\Windows Search" -Force -ErrorAction SilentlyContinue | Out-Null',
            r'Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\Windows Search" -Name "AllowCortana" -Value 0 -Type DWord -Force',
        ],
    },
    {
        "id": "advertising_id",
        "label": "Disable Advertising ID",
        "description": "Stops apps from using a unique ID to track you across different apps.",
        "default": True,
        "backup_keys": [
            {
                "hive": "HKCU",
                "path": r"Software\Microsoft\Windows\CurrentVersion\AdvertisingInfo",
                "name": "Enabled",
            },
        ],
        "cmds": [
            r'Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\AdvertisingInfo" -Name "Enabled" -Value 0 -Type DWord -Force',
        ],
    },
    {
        "id": "hibernation",
        "label": "Disable Hibernation (frees hiberfil.sys space)",
        "description": "Removes the hibernate file (~4-8 GB). Disable ONLY if you use Shutdown not Hibernate.",
        "default": False,
        "backup_keys": [],
        "cmds": [
            "powercfg /hibernate off",
        ],
        "restore_cmds": [
            "powercfg /hibernate on",
        ],
    },
]


def apply_service(
    svc: dict,
    log_callback: Optional[Callable[[str], None]] = None,
):
    svc_name = svc["service"]
    target = svc["target"]

    # Backup current state (only once)
    if not is_already_backed_up("services", svc_name):
        current = run_ps_query(
            f'(Get-Service -Name "{svc_name}" -ErrorAction SilentlyContinue).StartType'
        )
        record_service(svc_name, current or "Manual")

    if log_callback:
        log_callback(f"[SERVICE] {svc_name} → {target}")

    run_ps(
        f'Set-Service -Name "{svc_name}" -StartupType {target} -ErrorAction SilentlyContinue; '
        f'Stop-Service -Name "{svc_name}" -Force -ErrorAction SilentlyContinue',
        log_callback,
    )


def apply_registry_tweak(
    tweak: dict,
    log_callback: Optional[Callable[[str], None]] = None,
):
    # Backup each key before modifying
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
        log_callback(f"[REG] Applying: {tweak['label']}")

    for cmd in tweak.get("cmds", []):
        run_ps(cmd, log_callback)
