# Lehrerausgabe für Windows – Plan

Status: Planung. Es ist noch kein getesteter Build der Lehrerausgabe vorhanden.

## Ziel

Ein entpackbarer Ordner, den Lehrkräfte per Doppelklick starten können. Die
Lehrerausgabe soll ohne installiertes Python und ohne Godot-Editor funktionieren.

## Vorgeschlagene Paketstruktur

```text
Stadtprojekt/
├─ Lehrer_Stadt.exe
├─ Stadt_Erkennung.exe
├─ cityviewer/
│  ├─ CityViewer.exe
│  └─ data/buildings.json
├─ output/
│  ├─ layout.json
│  ├─ buildings.json
│  └─ print/
│     ├─ cards.pdf
│     └─ grid_sheet.pdf
├─ examples/
├─ licenses/
└─ Readme.Teacher.md
```

Die bestehenden Ordner- und Dateinamen bleiben erhalten, damit die aktuelle
Logik möglichst wenig angepasst werden muss:

- `PROJECT` ist künftig der Ordner der `Lehrer_Stadt.exe`.
- `cityviewer/data/buildings.json` bleibt der Viewer-Katalog.
- `output/layout.json` bleibt das Layout für Erkennung und Demos.
- `cityviewer/CityViewer.exe` bleibt der automatische Viewer-Pfad.
- `examples/` bleibt der Speicherort der Demos.
- `output/print/` bleibt der Speicherort der Druckvorlagen.

## Zwei getrennte EXE-Dateien

| Datei | Aufgabe | Grundlage |
|---|---|---|
| `Lehrer_Stadt.exe` | Lehreroberfläche, Sitzungen, Viewerstart | `teacher_app.py` |
| `Stadt_Erkennung.exe` | ArUco-Erkennung als eigener Prozess | `scripts/detect_city.py` |

Diese Trennung ist wichtig: In einer mit PyInstaller erstellten Anwendung
bezeichnet `sys.executable` die Anwendungs-EXE, nicht mehr Python. Die
bisherige Logik ruft den Detektor über `sys.executable` auf und würde daher in
einer einzelnen EXE nicht funktionieren.

Mit zwei EXE-Dateien ruft die Oberfläche die Erkennungs-EXE direkt auf. Der
vorbereitete Patch in `apply_bundled_detector_patch.py` unterstützt das:

- Wenn `Stadt_Erkennung.exe` im Projektstamm liegt, wird sie verwendet.
- Wenn sie fehlt, verwendet die Entwicklungsfassung weiterhin Python und
  `scripts/detect_city.py`.
- Die `prepare_run`-Prüfung akzeptiert den gebündelten Detektor ebenfalls.

## Godot-Viewer

Die getestete `CityViewer.exe` wird aus dem Godot-GUI-Export übernommen und
unter `cityviewer/CityViewer.exe` im Paket abgelegt. Sie wird von der
Lehreroberfläche automatisch gefunden und mit `-- <city.json>` gestartet.

Der PowerShell-Skript-Export ist derzeit kein Ersatz für den GUI-Export, weil
er die rohe `parts.csv` nicht zuverlässig in das Paket aufnimmt. Maßgeblich
ist daher der GUI-Export.

## PyInstaller-Build: noch nicht getestet

Die folgenden Befehle sind ein Ausgangspunkt, keine fertige Anleitung:

```powershell
pyinstaller --noconfirm --clean --onedir --name Lehrer_Stadt teacher_app.py
pyinstaller --noconfirm --clean --onedir --name Stadt_Erkennung scripts/detect_city.py
```

Nach dem Build müssen die erzeugten Ordner geprüft und die benötigten
Ressourcen manuell bzw. über eine Build-Konfiguration ergänzt werden:

- `examples/`
- `output/layout.json`
- `output/buildings.json`
- `output/print/`
- `cityviewer/data/buildings.json`
- `cityviewer/CityViewer.exe`
- Lizenz- und Hinweistexte

PyInstaller kann Module und native Bibliotheken übersehen. Besonders zu
prüfen sind OpenCV/ArUco, Pillow und gegebenenfalls weitere dynamisch
geladene Komponenten.

## Abnahme der Lehrerausgabe

Der Build gilt erst dann als fertig, wenn auf einem Rechner ohne installiertes
Python und ohne Godot-Editor geprüft wurde:

- Start per Doppelklick.
- Alle drei Demos, vorbereitet und neu erkannt.
- Eigenes Foto, Überlappungen und fehlender Eckmarker.
- Offlinebetrieb.
- Rückkehr zur Oberfläche nach Esc.
- Pfade mit Leerzeichen und Umlauten.
- Leistung auf dem Zielgerät Surface Go 3.
- Lizenz- und Hinweistexte vollständig enthalten.

## Offene Punkte

- Tatsächliche PyInstaller-Buildkonfiguration erstellen und testen.
- Fehlende versteckte Imports und native Abhängigkeiten ermitteln.
- Lizenztexte der tatsächlich gebündelten Komponenten sammeln.
- Reproduzierbaren Build oder zumindest dokumentierten GUI-Export festhalten.
- Abschließende Abnahme auf dem Zielgerät.
