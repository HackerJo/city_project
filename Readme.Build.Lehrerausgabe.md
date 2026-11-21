# Lehrerausgabe für Windows – Build und Test

Status: Vorbereitung. Es ist noch kein getesteter Build der Lehrerausgabe vorhanden.

## Voraussetzungen

- Windows mit Python und `pip`.
- PyInstaller installiert:

```powershell
python -m pip install pyinstaller
```

- Die getestete `cityviewer/CityViewer.exe` aus dem Godot-GUI-Export.
- Vollständige Projektdateien: `examples/`, `output/`, `cityviewer/data/`.
- Die Patches `apply_bundled_detector_patch.py` und `apply_exported_viewer_patch.py` angewendet.

## Build ausführen

```powershell
cd C:\Users\Joe\Documents\GitHub\city_project
.\build_lehrerausgabe.ps1
```

Das Skript erstellt:

```text
build/lehrerausgabe/
├─ Lehrer_Stadt.exe
├─ Stadt_Erkennung.exe
├─ cityviewer/CityViewer.exe
├─ cityviewer/data/buildings.json
├─ output/layout.json
├─ output/buildings.json
├─ output/print/
├─ examples/
├─ Readme.Teacher.md
└─ THIRD_PARTY_NOTICES.md
```

## Was das Skript tut

1. Baut `Lehrer_Stadt.exe` aus `teacher_app.py`.
2. Baut `Stadt_Erkennung.exe` aus `scripts/detect_city.py`.
3. Kopiert beide EXE-Dateien und alle benötigten Daten in `build/lehrerausgabe/`.
4. Prüft, ob alle kritischen Dateien vorhanden sind.

## Wichtiger Hinweis zu PyInstaller

PyInstaller kann Module und native Bibliotheken übersehen. Besonders zu prüfen
sind OpenCV/ArUco, Pillow und gegebenenfalls weitere dynamisch geladene
Komponenten. Falls beim Start einer EXE ein Importfehler erscheint, ist das
kein Grund zur Panik: Wir ergänzen dann gezielt `hiddenimports` oder
`datas` in der jeweiligen `.spec`-Datei.

## Test der Lehrerausgabe

Der Build gilt erst dann als fertig, wenn auf einem Rechner ohne installiertes
Python und ohne Godot-Editor geprüft wurde:

- Start per Doppelklick von `Lehrer_Stadt.exe`.
- Alle drei Demos, vorbereitet und neu erkannt.
- Eigenes Foto, Überlappungen und fehlender Eckmarker.
- Offlinebetrieb.
- Rückkehr zur Oberfläche nach Esc.
- Pfade mit Leerzeichen und Umlauten.
- Leistung auf dem Zielgerät Surface Go 3.

## Bekannte Grenzen

- Der PowerShell-Skript-Export des Godot-Viewers ist derzeit kein Ersatz für
  den GUI-Export, weil er die rohe `parts.csv` nicht zuverlässig einbindet.
  Maßgeblich ist daher der GUI-Export.
- Die PyInstaller-Buildkonfiguration ist ein Ausgangspunkt. Fehlende
  Abhängigkeiten werden erst beim praktischen Test sichtbar.
- Lizenztexte der tatsächlich gebündelten Komponenten müssen vor einer
  Veröffentlichung vervollständigt werden.
