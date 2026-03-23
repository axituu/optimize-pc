import customtkinter as ctk
from tweaks.battery import BATTERY_TWEAKS


class BatteryTab:
    def __init__(self, parent, count_callback=None):
        self._checkboxes: dict[str, tuple] = {}
        self._count_callback = count_callback
        self._build(parent)

    def _build(self, parent):
        # Info banner
        info = ctk.CTkFrame(parent, fg_color=("#cce5ff", "#0d1f3c"), corner_radius=8)
        info.pack(fill="x", padx=8, pady=(8, 4))
        ctk.CTkLabel(
            info,
            text="ℹ  Battery tweaks do not modify your ThinkPad power plans. "
            "Your 3 Lenovo Vantage presets remain completely untouched.",
            text_color=("#004085", "#66aaff"),
            font=ctk.CTkFont(size=12),
            wraplength=860,
            justify="left",
        ).pack(padx=10, pady=6, anchor="w")

        scroll = ctk.CTkScrollableFrame(parent, label_text="Battery Efficiency Tweaks")
        scroll.pack(fill="both", expand=True, padx=8, pady=(0, 4))

        btn_row = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_row.pack(fill="x", padx=4, pady=(4, 10))
        ctk.CTkButton(
            btn_row, text="Select All", width=100, height=28, command=self._select_all
        ).pack(side="left", padx=(0, 6))
        ctk.CTkButton(
            btn_row,
            text="Select None",
            width=100,
            height=28,
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40"),
            text_color=("black", "white"),
            command=self._select_none,
        ).pack(side="left")

        for tweak in BATTERY_TWEAKS:
            self._add_row(scroll, tweak)

    def _add_row(self, parent, tweak: dict):
        var = ctk.BooleanVar(value=tweak.get("default", True))
        var.trace_add("write", lambda *_: self._on_change())

        row = ctk.CTkFrame(parent, fg_color=("gray93", "gray17"), corner_radius=6)
        row.pack(fill="x", padx=4, pady=3)

        left = ctk.CTkFrame(row, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True, padx=(10, 6), pady=7)

        cb = ctk.CTkCheckBox(
            left,
            text=f"  {tweak['label']}",
            variable=var,
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        cb.pack(anchor="w")

        if tweak.get("description"):
            ctk.CTkLabel(
                left,
                text=tweak["description"],
                font=ctk.CTkFont(size=11),
                text_color=("gray45", "gray60"),
                anchor="w",
            ).pack(anchor="w", padx=30, pady=(1, 0))

        self._checkboxes[tweak["id"]] = (var, tweak)

    def _on_change(self):
        if self._count_callback:
            self._count_callback()

    # ── Public API ─────────────────────────────────────────────────────────

    def get_selected(self) -> list:
        return [tweak for var, tweak in self._checkboxes.values() if var.get()]

    def count_selected(self) -> int:
        return sum(1 for var, _ in self._checkboxes.values() if var.get())

    def set_preset(self, preset_ids: frozenset):
        for tid, (var, _) in self._checkboxes.items():
            var.set(tid in preset_ids)

    def _select_all(self):
        for var, _ in self._checkboxes.values():
            var.set(True)

    def _select_none(self):
        for var, _ in self._checkboxes.values():
            var.set(False)
