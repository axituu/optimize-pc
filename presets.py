"""
Preset definitions: which tweak IDs are enabled for each preset level.

ThinkPad presets: Safe ⊆ Medium ⊆ Full
Gaming PC presets: GAMING_SAFE ⊆ GAMING_MEDIUM ⊆ GAMING_FULL
  (Gaming presets are supersets of their ThinkPad counterparts — they add
   gaming-specific tweaks and unlock previously restricted items.)
"""

# Safe — registry-only tweaks, no service disabling, no AppX removal.
# Zero risk of breaking anything. Completely reversible.
SAFE: frozenset = frozenset(
    [
        # Performance → registry
        "transparency",
        "tips_suggestions",
        "game_dvr",
        "delivery_opt",
        "bg_apps",
        "cortana_search",
        "advertising_id",
        # Battery
        "usb_selective_suspend",
        "wifi_scan",
        "wake_timers",
        "fast_startup",
        # Tasks
        "ceip_consolidator",
        "ceip_usb",
        "maps_toast",
        "maps_update",
        "defrag",
    ]
)

# Medium — Safe + service disabling + heavier registry tweaks.
# Noticeable performance gains. Easily restored via Restore tab.
MEDIUM: frozenset = SAFE | frozenset(
    [
        # Performance → registry
        "visual_effects",
        "telemetry",
        "defender_samples",
        # Performance → services
        "sysmain",
        "wsearch",
        "diagtrack",
        "wer_svc",
        "remote_registry",
        "fax",
        # Battery
        "bluetooth_manual",
        # Tasks
        "compat_appraiser",
        "disk_diag",
        "winsat",
    ]
)

# Full — Medium + AppX bloatware removal + remaining tasks.
# Maximum optimisation. AppX removal is NOT reversible by the Restore tab.
# Risky/optional tweaks (spooler, hibernation, ahci_lpm, nic_wol) are
# intentionally excluded — tick those manually if you want them.
FULL: frozenset = MEDIUM | frozenset(
    [
        # Bloatware (AppX)
        "xbox_app",
        "xbox_gamebar",
        "xbox_identity",
        "xbox_speech",
        "xbox_tcui",
        "bing_weather",
        "bing_news",
        "bing_finance",
        "maps",
        "3d_builder",
        "3d_viewer",
        "mixed_reality",
        "people",
        "solitaire",
        "tips",
        "office_hub",
        "cortana",
        # Battery
        "lock_screen_spotlight",
        # Tasks
        "wu_auto_app",
    ]
)

PRESETS = {
    "none": frozenset(),
    "safe": SAFE,
    "medium": MEDIUM,
    "full": FULL,
}

PRESET_META = {
    "none": {
        "label": "Clear All",
        "description": "Uncheck everything",
        "color": ("#555", "#444"),
        "hover": ("#666", "#555"),
        "text_color": ("white", "gray80"),
    },
    "safe": {
        "label": "Safe",
        "description": "Registry tweaks only — zero risk, fully reversible",
        "color": ("#1a7a4a", "#145c38"),
        "hover": ("#16633c", "#0f4a2d"),
        "text_color": ("white", "white"),
    },
    "medium": {
        "label": "Medium",
        "description": "Safe + services disabled + deeper registry — recommended",
        "color": ("#b8660a", "#8a4c08"),
        "hover": ("#9e5808", "#733f06"),
        "text_color": ("white", "white"),
    },
    "full": {
        "label": "Full Optimization",
        "description": "Medium + bloatware removal — AppX changes are NOT reversible",
        "color": ("#8b1a1a", "#6b1414"),
        "hover": ("#721515", "#581010"),
        "text_color": ("white", "white"),
    },
}

# ── Gaming PC presets ──────────────────────────────────────────────────────────
# Designed for a dedicated gaming desktop. No ThinkPad/Lenovo restrictions apply.
# Each gaming preset is a superset of its ThinkPad counterpart, adding
# gaming-specific tweaks and unlocking previously restricted items.

GAMING_SAFE: frozenset = SAFE | frozenset(
    [
        "game_mode",
        "fullscreen_opt",
        "mouse_accel",
        "priority_gpu",
    ]
)

GAMING_MEDIUM: frozenset = (
    GAMING_SAFE
    | MEDIUM
    | frozenset(
        [
            # MEDIUM explicitly unioned so services/registry from ThinkPad medium are included
            "power_throttling",
            "hags",
            "nagle_algorithm",
        ]
    )
)

GAMING_FULL: frozenset = (
    GAMING_MEDIUM
    | FULL
    | frozenset(
        [
            # FULL explicitly unioned so all AppX removals are included
            "hpet",
            "spooler",  # previously manual-only service tweak
            "hibernation",  # previously manual-only registry tweak
            "ahci_lpm",  # previously manual-only battery tweak
            "nic_wol",  # previously manual-only battery tweak
            "wu_auto_app",  # previously manual-only task
            "lock_screen_spotlight",  # previously manual-only battery tweak
        ]
    )
)

GAMING_PRESETS = {
    "none": frozenset(),
    "safe": GAMING_SAFE,
    "medium": GAMING_MEDIUM,
    "full": GAMING_FULL,
}

GAMING_PRESET_META = {
    "none": {
        "label": "Clear All",
        "description": "Uncheck everything",
        "color": ("#555", "#444"),
        "hover": ("#666", "#555"),
        "text_color": ("white", "gray80"),
    },
    "safe": {
        "label": "Gaming Safe",
        "description": "Core gaming optimizations + registry tweaks — fully reversible",
        "color": ("#1a5fa8", "#144080"),
        "hover": ("#165090", "#0f3268"),
        "text_color": ("white", "white"),
    },
    "medium": {
        "label": "Gaming Medium",
        "description": "Safe + CPU/GPU/network gaming tweaks + service disabling — recommended",
        "color": ("#b8660a", "#8a4c08"),
        "hover": ("#9e5808", "#733f06"),
        "text_color": ("white", "white"),
    },
    "full": {
        "label": "Maximum Performance",
        "description": "Everything — all gaming + system tweaks incl. risky ones. Restart required.",
        "color": ("#c0392b", "#8b1a1a"),
        "hover": ("#a93226", "#721515"),
        "text_color": ("white", "white"),
    },
}
