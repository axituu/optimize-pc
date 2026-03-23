import customtkinter as ctk
from tweaks.bloatware import APPX_PACKAGES


class BloatwareTab:
    def __init__(self, parent, count_callback=None, gaming_mode: bool = False):
        self._checkboxes: dict[str, tuple] = {}  # id → (BooleanVar, pkg_dict)
        self._count_callback = count_callback
        self._gaming_mode = gaming_mode
        self._build(parent)

    def _build(self, parent):
        # ── Banners ────────────────────────────────────────────────────────
        warn = ctk.CTkFrame(parent, fg_color=("#fff3cd", "#3d2e00"), corner_radius=8)
        warn.pack(fill="x", padx=8, pady=(8, 3))
        ctk.CTkLabel(
            warn,
            text="⚠  AppX removal is NOT reversible by this tool. "
            "Packages can be reinstalled from the Microsoft Store manually.",
            text_color=("#7d5a00", "#ffcc44"),
            font=ctk.CTkFont(size=12),
            wraplength=860,
            justify="left",
        ).pack(padx=10, pady=5, anchor="w")

        if not self._gaming_mode:
            info = ctk.CTkFrame(
                parent, fg_color=("#d4edda", "#0d2b1a"), corner_radius=8
            )
            info.pack(fill="x", padx=8, pady=(0, 6))
            ctk.CTkLabel(
                info,
                text="✔  Lenovo Vantage, ThinkPad Vantage and Lenovo System Update are protected — they will never be touched.",
                text_color=("#155724", "#55cc88"),
                font=ctk.CTkFont(size=12),
                wraplength=860,
                justify="left",
            ).pack(padx=10, pady=5, anchor="w")

        # ── Scrollable list ────────────────────────────────────────────────
        scroll = ctk.CTkScrollableFrame(parent, label_text="AppX Packages to Remove")
        scroll.pack(fill="both", expand=True, padx=8, pady=(0, 4))

        # Quick-select row
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

        # One checkbox per package
        for pkg in APPX_PACKAGES:
            self._add_row(scroll, pkg)

    def _add_row(self, parent, pkg: dict):
        var = ctk.BooleanVar(value=pkg.get("default", True))
        var.trace_add("write", lambda *_: self._on_change())

        row = ctk.CTkFrame(parent, fg_color=("gray93", "gray17"), corner_radius=6)
        row.pack(fill="x", padx=4, pady=3)

        cb = ctk.CTkCheckBox(
            row,
            text=f"  {pkg['label']}",
            variable=var,
            font=ctk.CTkFont(size=13, weight="bold"),
            width=26,
        )
        cb.pack(side="left", padx=(10, 6), pady=8)

        if pkg.get("description"):
            ctk.CTkLabel(
                row,
                text=pkg["description"],
                font=ctk.CTkFont(size=11),
                text_color=("gray45", "gray60"),
                anchor="w",
            ).pack(side="left", padx=4, fill="x", expand=True)

        self._checkboxes[pkg["id"]] = (var, pkg)

    def _on_change(self):
        if self._count_callback:
            self._count_callback()

    # ── Public API ─────────────────────────────────────────────────────────

    def get_selected(self) -> list:
        return [pkg for var, pkg in self._checkboxes.values() if var.get()]

    def count_selected(self) -> int:
        return sum(1 for var, _ in self._checkboxes.values() if var.get())

    def set_preset(self, preset_ids: frozenset):
        """Check only the tweaks whose IDs are in preset_ids; uncheck the rest."""
        for tid, (var, _) in self._checkboxes.items():
            var.set(tid in preset_ids)

    def _select_all(self):
        for var, _ in self._checkboxes.values():
            var.set(True)

    def _select_none(self):
        for var, _ in self._checkboxes.values():
            var.set(False)
