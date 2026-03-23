"""
ThinkPad PC Optimizer — entry point.
Must be run as Administrator. launcher.bat handles UAC elevation.
"""

import sys
import os

# Ensure the project root is on sys.path when launched from a different cwd.
# Not needed when frozen by PyInstaller (all modules are already bundled).
if not getattr(sys, "frozen", False):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.admin_check import is_admin, relaunch_as_admin


def main():
    if not is_admin():
        # Attempt auto-elevation via UAC
        relaunch_as_admin()
        sys.exit(0)

    # Import GUI only after confirming we have admin rights
    # (customtkinter must be installed — prompt user if not)
    try:
        from gui.app_window import AppWindow
    except ImportError as e:
        import tkinter as tk
        import tkinter.messagebox as mb

        root = tk.Tk()
        root.withdraw()
        mb.showerror(
            "Missing Dependency",
            f"Could not import GUI: {e}\n\n"
            "Please install dependencies first:\n"
            "    pip install customtkinter\n\n"
            "Or run:  pip install -r requirements.txt",
        )
        sys.exit(1)

    app = AppWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
