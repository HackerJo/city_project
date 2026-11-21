# -*- mode: python ; coding: utf-8 -*-
# PyInstaller-Spezifikation für die Lehreroberfläche.
# Erzeugt: dist/Lehrer_Stadt/Lehrer_Stadt.exe
# Ausführen im Projektstamm:
#   pyinstaller --noconfirm --clean build_teacher_app.spec
#
# Wichtig: Die exportierte Godot-EXE benötigt zusätzlich die zugehörige
# .pck-Datei. Beide werden nach _internal/cityviewer kopiert.
# Zusätzlich wird die rohe parts.csv als lose Datei mitgegeben, weil die
# .pck sie nicht enthält und der Builder sie benötigt.

a = Analysis(
    ['teacher_app.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('examples', 'examples'),
        ('output/layout.json', 'output'),
        ('output/buildings.json', 'output'),
        ('output/print/cards.pdf', 'output/print'),
        ('output/print/grid_sheet.pdf', 'output/print'),
        ('cityviewer/data/buildings.json', 'cityviewer/data'),
        ('cityviewer/data/parts.csv', 'cityviewer/data'),
        ('cityviewer/data/city.json', 'cityviewer/data'),
        ('cityviewer/CityViewer.exe', 'cityviewer'),
        ('cityviewer/CityViewer.pck', 'cityviewer'),
    ],
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
    name='Lehrer_Stadt',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name='Lehrer_Stadt',
)
