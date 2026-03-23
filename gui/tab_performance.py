import customtkinter as ctk
from tweaks.performance import SERVICES, REGISTRY_TWEAKS
from tweaks.scheduled_tasks import TASKS


class PerformanceTab:
    def __init__(self, parent, count_callback=None):
        self._service_checkboxes: dict[str, tuple] = {}
        self._registry_checkboxes: dict[str, tuple] = {}
        self._task_checkboxes: dict[str, tuple] = {}
        self._count_callback = count_callback
        self._build(parent)

    def _build(self, parent):
        scroll = ctk.CTkScrollableFrame(parent, label_text="Performance Tweaks")
        scroll.pack(fill="both", expand=True, padx=8, pady=8)

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

        self._add_section(scroll, "Services", SERVICES, self._service_checkboxes)
        self._add_section(
            scroll,
            "Registry & System Settings",
            REGISTRY_TWEAKS,
            self._registry_checkboxes,
        )
        self._add_section(scroll, "Scheduled Tasks", TASKS, self._task_checkboxes)

    def _add_section(self, parent, title: str, items: list, store: dict):
        # Section header
        hdr = ctk.CTkFrame(
            parent, fg_color=("gray80", "gray22"), corner_radius=6, height=32
        )
        hdr.pack(fill="x", padx=4, pady=(12, 6))
        hdr.pack_propagate(False)
        ctk.CTkLabel(
            hdr,
            text=title,
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w",
        ).pack(side="left", padx=12)

        for item in items:
            self._add_row(parent, item, store)

    def _add_row(self, parent, item: dict, store: dict):
        var = ctk.BooleanVar(value=item.get("default", True))
        var.trace_add("write", lambda *_: self._on_change())

        row = ctk.CTkFrame(parent, fg_color=("gray93", "gray17"), corner_radius=6)
        row.pack(fill="x", padx=4, pady=3)

        # Left: checkbox + label
        left = ctk.CTkFrame(row, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True, padx=(10, 6), pady=7)

        cb = ctk.CTkCheckBox(
            left,
            text=f"  {item['label']}",
            variable=var,
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        cb.pack(anchor="w")

        if item.get("description"):
            ctk.CTkLabel(
                left,
                text=item["description"],
                font=ctk.CTkFont(size=11),
                text_color=("gray45", "gray60"),
                anchor="w",
            ).pack(anchor="w", padx=30, pady=(1, 0))

        store[item["id"]] = (var, item)

    def _on_change(self):
        if self._count_callback:
            self._count_callback()

    # ── Public API ─────────────────────────────────────────────────────────

    def get_selected_services(self) -> list:
        return [item for var, item in self._service_checkboxes.values() if var.get()]

    def get_selected_registry(self) -> list:
        return [item for var, item in self._registry_checkboxes.values() if var.get()]

    def get_selected_tasks(self) -> list:
        return [item for var, item in self._task_checkboxes.values() if var.get()]

    def count_selected(self) -> int:
        return sum(
            1
            for d in (
                self._service_checkboxes,
                self._registry_checkboxes,
                self._task_checkboxes,
            )
            for var, _ in d.values()
            if var.get()
        )

    def set_preset(self, preset_ids: frozenset):
        for store in (
            self._service_checkboxes,
            self._registry_checkboxes,
            self._task_checkboxes,
        ):
            for tid, (var, _) in store.items():
                var.set(tid in preset_ids)

    def _select_all(self):
        for d in (
            self._service_checkboxes,
            self._registry_checkboxes,
            self._task_checkboxes,
        ):
            for var, _ in d.values():
                var.set(True)

    def _select_none(self):
        for d in (
            self._service_checkboxes,
            self._registry_checkboxes,
            self._task_checkboxes,
        ):
            for var, _ in d.values():
                var.set(False)
