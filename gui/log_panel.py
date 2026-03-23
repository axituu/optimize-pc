import customtkinter as ctk


class LogPanel(ctk.CTkFrame):
    """Collapsible log output panel at the bottom of the window."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._expanded = False
        self._build()

    def _build(self):
        header = ctk.CTkFrame(self, fg_color="transparent", height=32)
        header.pack(fill="x", padx=5, pady=(2, 0))
        header.pack_propagate(False)

        self._toggle_btn = ctk.CTkButton(
            header,
            text="▶ Show Log",
            width=100,
            height=26,
            font=ctk.CTkFont(size=12),
            fg_color=("gray75", "gray30"),
            hover_color=("gray65", "gray40"),
            text_color=("black", "white"),
            command=self._toggle,
        )
        self._toggle_btn.pack(side="left", padx=(0, 8))

        self._summary = ctk.CTkLabel(
            header,
            text="No operations yet.",
            anchor="w",
            font=ctk.CTkFont(size=11),
            text_color=("gray40", "gray60"),
        )
        self._summary.pack(side="left", fill="x", expand=True)

        self._textbox = ctk.CTkTextbox(
            self,
            height=160,
            font=ctk.CTkFont(family="Consolas", size=11),
            state="disabled",
            wrap="none",
        )
        # Hidden by default

    def _toggle(self):
        self._expanded = not self._expanded
        if self._expanded:
            self._textbox.pack(fill="both", expand=True, padx=5, pady=(0, 5))
            self._toggle_btn.configure(text="▼ Hide Log")
        else:
            self._textbox.pack_forget()
            self._toggle_btn.configure(text="▶ Show Log")

    def append(self, message: str):
        """Thread-safe append — must be called from any thread."""
        self.after(0, lambda m=message: self._do_append(m))

    def _do_append(self, message: str):
        self._textbox.configure(state="normal")
        self._textbox.insert("end", message + "\n")
        self._textbox.see("end")
        self._textbox.configure(state="disabled")
        # Update summary with last line
        short = message[:90] + ("…" if len(message) > 90 else "")
        self._summary.configure(text=short)

    def clear(self):
        self.after(0, self._do_clear)

    def _do_clear(self):
        self._textbox.configure(state="normal")
        self._textbox.delete("1.0", "end")
        self._textbox.configure(state="disabled")
        self._summary.configure(text="Log cleared.")
