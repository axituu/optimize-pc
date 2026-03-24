import os
import sys
import threading
import tkinter.messagebox as mb

import customtkinter as ctk

# ── Load custom theme before any widget is created ──────────────────────────
_BASE_PATH = getattr(sys, "_MEIPASS", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_THEME_PATH = os.path.join(_BASE_PATH, "assets", "theme.json")
if os.path.exists(_THEME_PATH):
    ctk.set_default_color_theme(_THEME_PATH)
else:
    ctk.set_default_color_theme("blue")
ctk.set_appearance_mode("dark")
# ────────────────────────────────────────────────────────────────────────────

from gui.log_panel import LogPanel
from gui.progress_panel import ProgressPanel
from gui.tab_bloatware import BloatwareTab
from gui.tab_performance import PerformanceTab
from gui.tab_battery import BatteryTab
from gui.tab_restore import RestoreTab
from gui.tab_gaming import GamingTab
from gui.tab_network import NetworkTab
from gui.tab_gpu import GpuTab
from gui.tab_cleaning import CleaningTab
from gui.tab_external import ExternalToolsTab

from tweaks.bloatware import apply_appx_removal
from tweaks.performance import apply_service, apply_registry_tweak
from tweaks.battery import apply_battery_tweak
from tweaks.scheduled_tasks import apply_task_disable
from tweaks.gaming import apply_gaming_tweak
from tweaks.network import apply_network_tweak
from tweaks.gpu import apply_gpu_tweak
from tweaks.cleaning import apply_clean_op

from presets import PRESETS, PRESET_META, GAMING_PRESETS, GAMING_PRESET_META

class AppWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Gaming PC Optimizer")
        self.geometry("1100x920")
        self.minsize(900, 720)
        self._set_icon()

        self._current_mode: str = "gaming"
        self._gaming_tab: GamingTab | None = None
        self._network_tab: NetworkTab | None = None
        self._gpu_tab: GpuTab | None = None
        self._cleaning_tab: CleaningTab | None = None
        self._preset_bar_frame = None  # stored so we can destroy it on mode switch

        self._build()
        self._apply_preset("medium")

    def _set_icon(self):
        ico = os.path.join(_BASE_PATH, "assets", "app.ico")
        if os.path.exists(ico):
            try:
                self.iconbitmap(ico)
            except Exception:
                pass

    def _load_logo(self, size: int) -> ctk.CTkImage:
        """Load app.ico and return a CTkImage at the requested size."""
        try:
            from PIL import Image
            ico_path = os.path.join(_BASE_PATH, "assets", "app.ico")
            img = Image.open(ico_path).convert("RGBA").resize((size, size), Image.Resampling.LANCZOS)
            return ctk.CTkImage(light_image=img, dark_image=img, size=(size, size))
        except Exception:
            # Fallback: blank transparent image
            try:
                from PIL import Image
                img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
                return ctk.CTkImage(light_image=img, dark_image=img, size=(size, size))
            except Exception:
                return None

    # ─────────────────────────────────────────────────────────────────────
    # Initial layout build
    # ─────────────────────────────────────────────────────────────────────

    def _build(self):
        self._build_titlebar()
        self._build_mode_bar()
        self._build_bottom_panels()  # pack bottom-up before tabview
        self._build_preset_bar()
        self._build_tabs()

    def _build_titlebar(self):
        bar = ctk.CTkFrame(
            self, height=68, corner_radius=0, fg_color=("#e8e8f0", "#0f0f18")
        )
        bar.pack(fill="x", side="top")
        bar.pack_propagate(False)

        # Logo image (lightning bolt icon)
        self._logo_image = self._load_logo(36)
        logo_label = ctk.CTkLabel(bar, image=self._logo_image, text="")
        logo_label.pack(side="left", padx=(14, 6))

        # Title + version stacked vertically
        title_stack = ctk.CTkFrame(bar, fg_color="transparent")
        title_stack.pack(side="left", pady=8)

        self._title_label = ctk.CTkLabel(
            title_stack,
            text="GAMING PC OPTIMIZER",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=("#1a1a2e", "#e8e8f4"),
        )
        self._title_label.pack(anchor="w")

        ctk.CTkLabel(
            title_stack,
            text="v1.2.0  ·  System Optimization Suite",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=("#555577", "#8888aa"),
        ).pack(anchor="w")

        # Right side: admin badge + subtitle
        ctk.CTkLabel(
            bar,
            text="● ADMIN",
            text_color=("#cc2222", "#ff5555"),
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
        ).pack(side="right", padx=(0, 16))

        self._subtitle_label = ctk.CTkLabel(
            bar,
            text="Maximum performance — no ThinkPad restrictions",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=("#c07010", "#ffaa33"),
        )
        self._subtitle_label.pack(side="right", padx=(0, 12))

        # 2px accent line below titlebar
        ctk.CTkFrame(
            self, height=2, corner_radius=0, fg_color=("#e84040", "#e84040")
        ).pack(fill="x", side="top")

    def _build_mode_bar(self):
        bar = ctk.CTkFrame(
            self, height=42, corner_radius=0, fg_color=("#e0e0ec", "#0d0d16")
        )
        bar.pack(fill="x", side="top")
        bar.pack_propagate(False)

        ctk.CTkLabel(
            bar,
            text="Mode:",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).pack(side="left", padx=(14, 6), pady=8)

        self._mode_seg = ctk.CTkSegmentedButton(
            bar,
            values=["Gaming PC", "ThinkPad"],
            command=self._on_mode_change,
            selected_color=("#c0392b", "#c0392b"),
            selected_hover_color=("#a93226", "#a93226"),
            unselected_color=("gray70", "gray28"),
            unselected_hover_color=("gray60", "gray38"),
            font=ctk.CTkFont(size=13, weight="bold"),
            width=230,
            height=30,
        )
        self._mode_seg.pack(side="left", padx=(0, 10), pady=6)
        self._mode_seg.set("Gaming PC")

        self._mode_desc_label = ctk.CTkLabel(
            bar,
            text="All restrictions lifted — Lenovo apps are removable",
            font=ctk.CTkFont(size=11),
            text_color=("gray45", "gray55"),
        )
        self._mode_desc_label.pack(side="right", padx=14)

    def _build_bottom_panels(self):
        self._log_panel = LogPanel(self)
        self._log_panel.pack(fill="x", side="bottom", padx=10, pady=(0, 4))

        self._progress_panel = ProgressPanel(self, apply_callback=self._on_apply)
        self._progress_panel.pack(fill="x", side="bottom", padx=10, pady=(0, 2))

    def _build_preset_bar(self):
        meta_map = GAMING_PRESET_META if self._current_mode == "gaming" else PRESET_META

        outer = ctk.CTkFrame(self, corner_radius=10, fg_color=("#e4e4ee", "#131320"))
        outer.pack(fill="x", padx=10, pady=(6, 4))
        self._preset_bar_frame = outer

        ctk.CTkLabel(
            outer,
            text="Preset:",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).pack(side="left", padx=(14, 8), pady=10)

        self._preset_btns: dict[str, ctk.CTkButton] = {}
        for key in ("none", "safe", "medium", "full"):
            meta = meta_map[key]
            btn = ctk.CTkButton(
                outer,
                text=meta["label"],
                font=ctk.CTkFont(size=13, weight="bold"),
                fg_color=meta["color"],
                hover_color=meta["hover"],
                text_color=meta["text_color"],
                width=148,
                height=36,
                corner_radius=8,
                command=lambda k=key: self._apply_preset(k),
            )
            btn.pack(side="left", padx=5, pady=8)
            self._preset_btns[key] = btn

        ctk.CTkFrame(outer, width=2, fg_color=("#c8c8dc", "#2a2a3e")).pack(
            side="left", fill="y", padx=12, pady=8
        )

        self._counter_label = ctk.CTkLabel(
            outer,
            text="0 tweaks selected",
            font=ctk.CTkFont(size=13),
            text_color=("gray40", "gray65"),
        )
        self._counter_label.pack(side="left", padx=4)

        self._preset_desc = ctk.CTkLabel(
            outer,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=("gray45", "gray55"),
        )
        self._preset_desc.pack(side="right", padx=14)

    def _build_tabs(self):
        self._tabs = ctk.CTkTabview(self, anchor="nw")
        self._tabs.pack(fill="both", expand=True, padx=10, pady=(0, 4))

        if self._current_mode == "gaming":
            tab_names = (
                "Bloatware",
                "Performance",
                "Battery",
                "Gaming",
                "Network",
                "GPU",
                "Cleaning",
                "External Tools",
                "Restore",
            )
        else:
            tab_names = (
                "Bloatware",
                "Performance",
                "Battery",
                "Network",
                "Cleaning",
                "Restore",
            )

        for name in tab_names:
            self._tabs.add(name)

        self._bloatware_tab = BloatwareTab(
            self._tabs.tab("Bloatware"),
            count_callback=self._update_counter,
            gaming_mode=(self._current_mode == "gaming"),
        )
        self._performance_tab = PerformanceTab(
            self._tabs.tab("Performance"),
            count_callback=self._update_counter,
        )
        self._battery_tab = BatteryTab(
            self._tabs.tab("Battery"),
            count_callback=self._update_counter,
            gaming_mode=(self._current_mode == "gaming"),
        )

        if self._current_mode == "gaming":
            self._gaming_tab = GamingTab(
                self._tabs.tab("Gaming"),
                count_callback=self._update_counter,
            )
            self._gpu_tab = GpuTab(
                self._tabs.tab("GPU"),
                count_callback=self._update_counter,
            )
            ExternalToolsTab(self._tabs.tab("External Tools"))
        else:
            self._gaming_tab = None
            self._gpu_tab = None

        self._network_tab = NetworkTab(
            self._tabs.tab("Network"),
            count_callback=self._update_counter,
        )
        self._cleaning_tab = CleaningTab(
            self._tabs.tab("Cleaning"),
            count_callback=self._update_counter,
        )

        self._restore_tab = RestoreTab(
            self._tabs.tab("Restore"),
            log_callback=self._log_panel.append,
        )

    # ─────────────────────────────────────────────────────────────────────
    # Mode switching
    # ─────────────────────────────────────────────────────────────────────

    def _on_mode_change(self, value: str):
        mode = "thinkpad" if value == "ThinkPad" else "gaming"
        if mode == self._current_mode:
            return
        self._switch_mode(mode)

    def _switch_mode(self, mode: str):
        self._current_mode = mode

        # 1. Tear down current tabs and preset bar (frees their pack slots)
        self._tabs.destroy()
        self._tabs = None
        self._bloatware_tab = None
        self._performance_tab = None
        self._battery_tab = None
        self._gaming_tab = None
        self._network_tab = None
        self._gpu_tab = None
        self._cleaning_tab = None
        self._restore_tab = None

        self._preset_bar_frame.destroy()
        self._preset_bar_frame = None
        self._preset_btns = {}

        # 2. Update title bar labels
        if mode == "gaming":
            self._title_label.configure(text="GAMING PC OPTIMIZER")
            self._subtitle_label.configure(
                text="Maximum performance — no ThinkPad restrictions",
                text_color=("#c07010", "#ffaa33"),
            )
            self._mode_seg.configure(
                selected_color=("#e84040", "#e84040"),
                selected_hover_color=("#c0392b", "#c0392b"),
            )
            self._mode_desc_label.configure(
                text="All restrictions lifted — Lenovo apps are removable"
            )
            self.title("Gaming PC Optimizer")
        else:
            self._title_label.configure(text="THINKPAD PC OPTIMIZER")
            self._subtitle_label.configure(
                text="ThinkPad mode: power plans protected  ·  Lenovo Vantage preserved",
                text_color=("#555577", "#8888aa"),
            )
            self._mode_seg.configure(
                selected_color=("#1a5fa8", "#1a5fa8"),
                selected_hover_color=("#165090", "#165090"),
            )
            self._mode_desc_label.configure(text="")
            self.title("ThinkPad PC Optimizer")

        # 3. Rebuild preset bar + tabs (in pack order: preset bar first, then tabs)
        self._build_preset_bar()
        self._build_tabs()

        # 4. Apply the default medium preset for this mode
        self._apply_preset("medium")

    # ─────────────────────────────────────────────────────────────────────
    # Preset logic
    # ─────────────────────────────────────────────────────────────────────

    def _apply_preset(self, key: str):
        self._active_preset = key
        preset_map = GAMING_PRESETS if self._current_mode == "gaming" else PRESETS
        meta_map = GAMING_PRESET_META if self._current_mode == "gaming" else PRESET_META
        ids = preset_map[key]

        self._bloatware_tab.set_preset(ids)
        self._performance_tab.set_preset(ids)
        self._battery_tab.set_preset(ids)
        if self._gaming_tab is not None:
            self._gaming_tab.set_preset(ids)
        if self._network_tab is not None:
            self._network_tab.set_preset(ids)
        if self._gpu_tab is not None:
            self._gpu_tab.set_preset(ids)
        # cleaning_tab.set_preset is a no-op (cleaning ops never auto-selected)
        if self._cleaning_tab is not None:
            self._cleaning_tab.set_preset(ids)

        self._update_counter()
        self._update_preset_buttons(key, meta_map)
        self._preset_desc.configure(text=meta_map[key]["description"])

    def _update_preset_buttons(self, active: str, meta_map: dict):
        for key, btn in self._preset_btns.items():
            if key == active:
                btn.configure(border_width=2, border_color="white")
            else:
                btn.configure(border_width=0)

    def _update_counter(self):
        n = (
            self._bloatware_tab.count_selected()
            + self._performance_tab.count_selected()
            + self._battery_tab.count_selected()
            + (self._gaming_tab.count_selected() if self._gaming_tab else 0)
            + (self._network_tab.count_selected() if self._network_tab else 0)
            + (self._gpu_tab.count_selected() if self._gpu_tab else 0)
            + (self._cleaning_tab.count_selected() if self._cleaning_tab else 0)
        )
        self._counter_label.configure(
            text=f"{n} tweak{'s' if n != 1 else ''} selected",
            text_color=("#1a7a4a", "#44cc80") if n > 0 else ("gray40", "gray55"),
        )

    # ─────────────────────────────────────────────────────────────────────
    # Apply logic
    # ─────────────────────────────────────────────────────────────────────

    def _on_apply(self):
        bypass = self._current_mode == "gaming"

        appx     = self._bloatware_tab.get_selected()
        services = self._performance_tab.get_selected_services()
        registry = self._performance_tab.get_selected_registry()
        tasks    = self._performance_tab.get_selected_tasks()
        battery  = self._battery_tab.get_selected()
        gaming   = self._gaming_tab.get_selected()   if self._gaming_tab   else []
        network  = self._network_tab.get_selected()  if self._network_tab  else []
        gpu      = self._gpu_tab.get_selected()      if self._gpu_tab      else []
        cleaning = self._cleaning_tab.get_selected() if self._cleaning_tab else []

        total = (
            len(appx) + len(services) + len(registry) + len(tasks)
            + len(battery) + len(gaming) + len(network) + len(gpu) + len(cleaning)
        )

        if total == 0:
            mb.showinfo(
                "Nothing Selected",
                "No tweaks are ticked. Pick a preset or select tweaks manually.",
            )
            self._progress_panel.reset()
            return

        if appx:
            pkg_note = (
                "No packages are protected in Gaming PC mode — "
                "even Lenovo apps will be removed if selected.\n\n"
                if bypass
                else "Lenovo Vantage and ThinkPad apps are protected and will not be removed.\n\n"
            )
            if not mb.askyesno(
                "Confirm AppX Removal",
                f"{len(appx)} AppX package(s) are selected for removal.\n\n"
                f"{pkg_note}"
                "AppX removal is NOT reversible by the Restore tab.\n\n"
                "Proceed?",
            ):
                self._progress_panel.reset()
                return

        if cleaning:
            if not mb.askyesno(
                "Confirm Cleaning Operations",
                f"{len(cleaning)} cleaning operation(s) are selected.\n\n"
                "These DELETE files and CANNOT be undone by the Restore tab.\n\n"
                "Proceed?",
            ):
                self._progress_panel.reset()
                return

        self._log_panel.clear()
        self._log_panel.append(
            f"[START] Applying {total} tweak(s) in {self._current_mode.upper()} mode..."
        )

        threading.Thread(
            target=self._apply_worker,
            args=(appx, services, registry, tasks, battery, gaming, network, gpu, cleaning, total, bypass),
            daemon=True,
        ).start()

    def _apply_worker(
        self, appx, services, registry, tasks, battery, gaming, network, gpu, cleaning, total, bypass
    ):
        log = self._log_panel.append
        done = 0

        def tick(label: str):
            nonlocal done
            done += 1
            self._progress_panel.set_progress(done / total)
            self._progress_panel.set_status(f"[{done}/{total}] {label[:65]}")

        try:
            for pkg in appx:
                tick(pkg["label"])
                apply_appx_removal(pkg, log, bypass_protection=bypass)

            for svc in services:
                tick(svc["label"])
                apply_service(svc, log)

            for tweak in registry:
                tick(tweak["label"])
                apply_registry_tweak(tweak, log)

            for task in tasks:
                tick(task["label"])
                apply_task_disable(task, log)

            for bt in battery:
                tick(bt["label"])
                apply_battery_tweak(bt, log)

            for gt in gaming:
                tick(gt["label"])
                apply_gaming_tweak(gt, log)

            for nt in network:
                tick(nt["label"])
                apply_network_tweak(nt, log)

            for gp in gpu:
                tick(gp["label"])
                apply_gpu_tweak(gp, log)

            for co in cleaning:
                tick(co["label"])
                apply_clean_op(co, log)

        except Exception as exc:
            log(f"[EXCEPTION] {exc}")

        self._progress_panel.set_progress(1.0)
        self._progress_panel.set_status(
            "Done!  Restart recommended to apply all changes."
        )
        log("[COMPLETE] All selected tweaks applied. Please restart your PC.")
        self.after(0, self._restore_tab.refresh)
