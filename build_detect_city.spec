# -*- mode: python ; coding: utf-8 -*-
# PyInstaller-Spezifikation für die ArUco-Erkennung.
# Erzeugt: dist/Stadt_Erkennung/Stadt_Erkennung.exe
# Ausführen im Projektstamm:
#   pyinstaller --noconfirm --clean build_detect_city.spec

a = Analysis(
    ['scripts/detect_city.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Stadt_Erkennung',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name='Stadt_Erkennung',
)
