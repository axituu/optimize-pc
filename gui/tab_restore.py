import tkinter.messagebox as mb
import customtkinter as ctk

from core.backup_manager import load_backup
from core.restore_engine import restore_all


class RestoreTab:
    def __init__(self, parent, log_callback=None):
        self._parent = parent
        self._log_callback = log_callback
        self._build(parent)

    def _build(self, parent):
        # Header
        hdr = ctk.CTkFrame(parent, fg_color=("#f8d7da", "#3d0a0a"), corner_radius=8)
        hdr.pack(fill="x", padx=8, pady=(8, 4))
        ctk.CTkLabel(
            hdr,
            text="Reset / Restore  —  Reverts all registry, service, and scheduled task changes to their original state.",
            text_color=("#721c24", "#ff8888"),
            font=ctk.CTkFont(size=12),
            wraplength=780,
            justify="left",
        ).pack(padx=10, pady=6, anchor="w")

        # Restore button
        btn_row = ctk.CTkFrame(parent, fg_color="transparent")
        btn_row.pack(fill="x", padx=8, pady=4)
        ctk.CTkButton(
            btn_row,
            text="Restore All Changes",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#c0392b",
            hover_color="#922b21",
            width=200,
            height=38,
            command=self._restore_all,
        ).pack(side="left", padx=(0, 10))
        ctk.CTkButton(
            btn_row,
            text="Refresh",
            width=80,
            height=38,
            fg_color=("gray75", "gray35"),
            hover_color=("gray65", "gray45"),
            text_color=("black", "white"),
            command=self.refresh,
        ).pack(side="left")

        # Backup summary scroll
        self._scroll = ctk.CTkScrollableFrame(
            parent, label_text="Backup State (changes that can be restored)"
        )
        self._scroll.pack(fill="both", expand=True, padx=8, pady=(0, 4))

        self.refresh()

    def refresh(self):
        for w in self._scroll.winfo_children():
            w.destroy()

        data = load_backup()
        if not data:
            ctk.CTkLabel(
                self._scroll,
                text="No backup recorded yet. Apply some tweaks first.",
                font=ctk.CTkFont(size=13),
                text_color=("gray50", "gray60"),
            ).pack(pady=20)
            return

        if "services" in data and data["services"]:
            self._section(
                "Services",
                [f"{svc}  →  was: {start}" for svc, start in data["services"].items()],
            )

        if "registry" in data and data["registry"]:
            self._section(
                "Registry Keys",
                [
                    f"{info['hive']}\\{info['path']}\\{info['name']}  =  "
                    f"{info['value'] if info['value'] is not None else '(did not exist)'}"
                    for info in data["registry"].values()
                ],
            )

        if "tasks" in data and data["tasks"]:
            self._section(
                "Scheduled Tasks",
                [
                    f"{path}  →  was: {'Enabled' if was_on else 'Disabled'}"
                    for path, was_on in data["tasks"].items()
                ],
            )

        if "appx_removed" in data and data["appx_removed"]:
            self._section(
                "Removed AppX Packages  (NOT auto-restorable — reinstall from Microsoft Store)",
                data["appx_removed"],
                color=("#721c24", "#ff8888"),
            )

    def _section(self, title: str, items: list, color=None):
        hdr = ctk.CTkFrame(
            self._scroll, fg_color=("gray85", "gray20"), corner_radius=6, height=28
        )
        hdr.pack(fill="x", padx=4, pady=(10, 2))
        hdr.pack_propagate(False)
        ctk.CTkLabel(
            hdr,
            text=title,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=color or ("black", "white"),
            anchor="w",
        ).pack(side="left", padx=8)
        for item in items:
            ctk.CTkLabel(
                self._scroll,
                text=f"  {item}",
                font=ctk.CTkFont(family="Consolas", size=11),
                text_color=color or ("gray30", "gray75"),
                anchor="w",
                justify="left",
            ).pack(anchor="w", padx=20, pady=1)

    def _restore_all(self):
        data = load_backup()
        if not data:
            mb.showinfo(
                "Nothing to Restore", "No backup data found. Nothing to restore."
            )
            return

        if not mb.askyesno(
            "Confirm Restore",
            "This will revert all registry and service changes to their backed-up state.\n\n"
            "• AppX packages that were removed CANNOT be automatically restored.\n"
            "• A restart is recommended after restoring.\n\n"
            "Proceed?",
        ):
            return

        import threading

        threading.Thread(target=self._do_restore, daemon=True).start()

    def _do_restore(self):
        restore_all(log_callback=self._log_callback, clear_after=True)
        self._scroll.after(0, self.refresh)
