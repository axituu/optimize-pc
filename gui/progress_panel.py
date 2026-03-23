import customtkinter as ctk
from typing import Callable


class ProgressPanel(ctk.CTkFrame):
    """Bottom bar: Apply button + progress bar + status label."""

    def __init__(self, parent, apply_callback: Callable, **kwargs):
        super().__init__(parent, height=58, corner_radius=10, **kwargs)
        self._apply_callback = apply_callback
        self._applying = False
        self._build()

    def _build(self):
        self.pack_propagate(False)

        self._apply_btn = ctk.CTkButton(
            self,
            text="Apply Selected Tweaks",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#1a7a4a",
            hover_color="#145c38",
            width=200,
            height=38,
            command=self._on_click,
        )
        self._apply_btn.pack(side="left", padx=(12, 10), pady=8)

        self._progress = ctk.CTkProgressBar(self, width=320, height=14)
        self._progress.set(0)
        self._progress.pack(side="left", padx=8, pady=8)

        self._status = ctk.CTkLabel(
            self,
            text="Select tweaks above then click Apply.",
            anchor="w",
            font=ctk.CTkFont(size=12),
        )
        self._status.pack(side="left", padx=10, fill="x", expand=True)

    def _on_click(self):
        if self._applying:
            return
        self._applying = True
        self._apply_btn.configure(state="disabled", text="Applying…")
        self._apply_callback()

    def set_progress(self, value: float):
        """Thread-safe progress update (0.0 – 1.0)."""
        self.after(0, lambda v=value: self._do_progress(v))

    def _do_progress(self, value: float):
        self._progress.set(value)
        if value >= 1.0:
            self._applying = False
            self._apply_btn.configure(state="normal", text="Apply Selected Tweaks")

    def set_status(self, text: str):
        """Thread-safe status label update."""
        self.after(0, lambda t=text: self._status.configure(text=t))

    def reset(self):
        self.after(0, self._do_reset)

    def _do_reset(self):
        self._applying = False
        self._progress.set(0)
        self._apply_btn.configure(state="normal", text="Apply Selected Tweaks")
        self._status.configure(text="Ready.")
