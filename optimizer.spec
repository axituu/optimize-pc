# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller spec for PC-Optimizer
# Run:  pyinstaller optimizer.spec --clean --noconfirm
# Or:   .\build.ps1
#
from PyInstaller.utils.hooks import collect_all

ctk_datas, ctk_binaries, ctk_hiddenimports = collect_all('customtkinter')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=ctk_binaries,
    datas=ctk_datas,
    hiddenimports=ctk_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    a.datas,
    a.binaries,
    a.zipfiles,
    name='PC-Optimizer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,      # no black terminal window
    uac_admin=True,     # embed UAC manifest — Windows prompts for elevation at launch
    icon=None,          # optional: set to 'assets/app.ico' if you add an icon
)
# No COLLECT() block → single-file output (--onefile behaviour)
