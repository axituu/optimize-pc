# Gaming PC Optimizer ⚙️

A powerful, reusable GUI tool built in Python and `customtkinter` designed to optimize Windows 11 performance, privacy, and gaming frame rates—with an extra optional mode tailored for **Lenovo ThinkPads**.

---

## 🚀 Key Features

- **Gaming Performance**: Maximizes GPU and CPU availability for gaming workloads and stops unnecessary background processes that cause stuttering.
- **Bloatware Removal**: One-click removal of pre-installed Microsoft AppX packages (Xbox, News, Weather, etc.).
- **Privacy & Telemetry**: Disables invasive Windows tracking, background data collection, and advertising IDs.
- **System Optimization**: Tweaks background services, registry settings, and scheduled tasks for maximum speed.
- **Safe & Reversible**: Automatically backs up original settings before every change. The **Restore** tab allows you to undo registry, service, and task changes with one click.
- **Optional ThinkPad Protection**: Hard-coded protection for essential Lenovo software (Vantage, System Update, ImController) if you choose to use the tool on a ThinkPad.

---

## 🛠️ Performance Modes

The optimizer features two distinct operating modes:

1.  **Gaming PC Mode (Default)**: Lifts all restrictions. Allows for deeper bloatware removal and maximum performance settings for dedicated gaming machines.
2.  **ThinkPad Mode (Optional)**: Optimized for daily professional use. Power plans are left untouched, and Lenovo Vantage services are strictly protected.

---

## 📦 Installation & Usage

### Option 1: Run from Source (Recommended for Devs)
1. Clone the repository:
   ```bash
   git clone https://github.com/axituu/optimize-pc.git
   cd optimize-pc
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run as Administrator:
   ```bash
   python main.py
   ```

### Option 2: Standalone Executable
You can build a standalone `.exe` using the provided build script:
```powershell
./build.ps1
```
The output will be located in the `dist/` folder.

---

## ⚠️ Important Notes

- **Administrator Privileges**: This tool modifies system registry keys and services; it **must** be run as an Administrator.
- **AppX Removal**: Removing Windows Store apps (Bloatware) is **not reversible** via the Restore tab. Please review the selection before applying.
- **Power Plan Modification**: In ThinkPad Mode, the tool never touches Windows Power Plans, allowing Lenovo Vantage to manage thermal profiles safely. In Gaming PC mode, maximum performance is prioritized.

---

## 🏗️ Technology Stack

- **Language**: Python 3.12+
- **GUI Framework**: [customtkinter](https://github.com/TomSchimansky/CustomTkinter) (Modern Dark/Light UI)
- **Backend**: PowerShell interop for system-level modifications.

---

## 📜 License
This project is for personal and educational use. Use at your own risk.
