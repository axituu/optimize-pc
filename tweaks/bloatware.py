"""
AppX bloatware removal definitions and apply logic.
Lenovo Vantage and related Lenovo system apps are protected and will never be removed.
"""

from typing import Callable, Optional

from core.executor import run_ps
from core.backup_manager import record_appx

# These package names (or substrings) must NEVER be removed.
PROTECTED_SUBSTRINGS = [
    "LenovoCompanion",
    "LenovoVantage",
    "ThinkVantage",
    "LenovoSystemUpdate",
    "LenovoID",
    "LenovoSettings",
    "ImControllerService",
]

# Each entry: id, label, pkg (exact or wildcard), default (bool), description
APPX_PACKAGES = [
    # Xbox ecosystem
    {
        "id": "xbox_app",
        "label": "Xbox App",
        "pkg": "Microsoft.XboxApp",
        "default": True,
        "description": "Xbox gaming client — not needed on a ThinkPad",
    },
    {
        "id": "xbox_gamebar",
        "label": "Xbox Game Bar (overlay)",
        "pkg": "Microsoft.XboxGamingOverlay",
        "default": True,
        "description": "In-game overlay. Causes background CPU overhead.",
    },
    {
        "id": "xbox_identity",
        "label": "Xbox Identity Provider",
        "pkg": "Microsoft.XboxIdentityProvider",
        "default": True,
        "description": "Xbox authentication service — not needed",
    },
    {
        "id": "xbox_speech",
        "label": "Xbox Speech To Text",
        "pkg": "Microsoft.XboxSpeechToTextOverlay",
        "default": True,
        "description": "Xbox voice overlay",
    },
    {
        "id": "xbox_tcui",
        "label": "Xbox TCUI (social overlay)",
        "pkg": "Microsoft.Xbox.TCUI",
        "default": True,
        "description": "Xbox social UI component",
    },
    # Bing
    {
        "id": "bing_weather",
        "label": "Bing Weather",
        "pkg": "Microsoft.BingWeather",
        "default": True,
        "description": "Bing weather app with background data sync",
    },
    {
        "id": "bing_news",
        "label": "Bing News",
        "pkg": "Microsoft.BingNews",
        "default": True,
        "description": "Bing news feed app",
    },
    {
        "id": "bing_finance",
        "label": "Bing Finance",
        "pkg": "Microsoft.BingFinance",
        "default": True,
        "description": "Bing finance app",
    },
    # Maps / 3D / Mixed Reality
    {
        "id": "maps",
        "label": "Microsoft Maps",
        "pkg": "Microsoft.WindowsMaps",
        "default": True,
        "description": "Windows Maps app",
    },
    {
        "id": "3d_builder",
        "label": "3D Builder",
        "pkg": "Microsoft.3DBuilder",
        "default": True,
        "description": "3D printing app — rarely used",
    },
    {
        "id": "3d_viewer",
        "label": "3D Viewer",
        "pkg": "Microsoft.Microsoft3DViewer",
        "default": True,
        "description": "3D model viewer",
    },
    {
        "id": "mixed_reality",
        "label": "Mixed Reality Portal",
        "pkg": "Microsoft.MixedReality.Portal",
        "default": True,
        "description": "HoloLens / VR portal — not relevant on a ThinkPad",
    },
    # Social / productivity fluff
    {
        "id": "people",
        "label": "Microsoft People",
        "pkg": "Microsoft.People",
        "default": True,
        "description": "Contacts app — duplicates Outlook contacts",
    },
    {
        "id": "solitaire",
        "label": "Microsoft Solitaire Collection",
        "pkg": "Microsoft.MicrosoftSolitaireCollection",
        "default": True,
        "description": "Built-in games suite with ads",
    },
    {
        "id": "tips",
        "label": "Tips / Get Started",
        "pkg": "Microsoft.Getstarted",
        "default": True,
        "description": "Windows onboarding tips app",
    },
    {
        "id": "office_hub",
        "label": "Office Hub (Get Office ad)",
        "pkg": "Microsoft.MicrosoftOfficeHub",
        "default": True,
        "description": "Advertisement to buy Microsoft 365",
    },
    # Cortana
    {
        "id": "cortana",
        "label": "Cortana",
        "pkg": "Microsoft.549981C3F5F10",
        "default": True,
        "description": "Cortana voice assistant — high idle CPU/memory usage",
    },
    # Optional (unchecked by default)
    {
        "id": "todo",
        "label": "Microsoft To-Do",
        "pkg": "Microsoft.Todos",
        "default": False,
        "description": "Microsoft task manager — uncheck to keep if you use it",
    },
    {
        "id": "skype",
        "label": "Skype",
        "pkg": "Microsoft.SkypeApp",
        "default": False,
        "description": "Skype messaging client",
    },
    {
        "id": "onenote",
        "label": "OneNote (Store version)",
        "pkg": "Microsoft.Office.OneNote",
        "default": False,
        "description": "Uncheck if you use the standalone OneNote desktop app",
    },
    {
        "id": "feedback_hub",
        "label": "Feedback Hub",
        "pkg": "Microsoft.WindowsFeedbackHub",
        "default": False,
        "description": "Windows feedback submission app",
    },
    {
        "id": "mcafee",
        "label": "McAfee (Lenovo trial antivirus)",
        "pkg": "*McAfee*",
        "default": False,
        "description": "Pre-installed McAfee trial — Windows Defender is sufficient",
    },
]


def _is_protected(pkg_name: str) -> bool:
    for sub in PROTECTED_SUBSTRINGS:
        if sub.lower() in pkg_name.lower():
            return True
    return False


def apply_appx_removal(
    pkg: dict,
    log_callback: Optional[Callable[[str], None]] = None,
    bypass_protection: bool = False,
):
    """Remove a single AppX package (user + provisioned).

    bypass_protection=True skips the Lenovo/ThinkPad protection check entirely
    (used in Gaming PC mode where there are no ThinkPad restrictions).
    """
    pkg_name = pkg["pkg"]

    if not bypass_protection and _is_protected(pkg_name):
        if log_callback:
            log_callback(f"[SKIP] {pkg_name} is protected — will not remove")
        return

    if log_callback:
        log_callback(f"[APPX] Removing {pkg['label']} ({pkg_name})")

    # Remove for current user
    run_ps(
        f'Get-AppxPackage -Name "{pkg_name}" | Remove-AppxPackage -ErrorAction SilentlyContinue',
        log_callback,
    )
    # Remove provisioned package (prevents reinstall for new users / Windows updates)
    run_ps(
        f'Get-AppxProvisionedPackage -Online | Where-Object {{$_.DisplayName -like "{pkg_name}"}} | '
        f"Remove-AppxProvisionedPackage -Online -ErrorAction SilentlyContinue",
        log_callback,
    )

    # Record for informational backup
    record_appx(pkg_name)
