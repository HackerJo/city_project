# CityProject

Foto von ArUco-Gebäudekärtchen wird in eine Stadtdaten-Datei übersetzt und in Godot dargestellt.

## Schnellstart (Entwicklung)

1. Abhängigkeiten installieren:

```powershell
python -m pip install -r requirements-teacher.txt
```

2. Godot-Erstimport einmalig ausführen:

```powershell
$Godot = "C:\Pfad\zu\Godot_v4.7.2-stable_win64.exe"
& $Godot --headless --path ".\cityviewer" --import
```

3. Lehreroberfläche starten:

```powershell
python teacher_app.py
```

4. Druckvorlagen nur bei Bedarf neu erzeugen:

```powershell
python scripts/generate_prints.py
```

5. Direkter Detektoraufruf (optional):

```powershell
python scripts/detect_city.py --image photo.jpg
```

6. Viewer direkt starten (Entwicklung):

```powershell
& "C:\Pfad\zu\Godot_v4.7.2-stable_win64.exe" --path .\cityviewer -- C:\Pfad\zu\scanresult\city.json
```

## Lehrerausgabe (Windows, ohne Python/Godot)

Die Lehrerausgabe bündelt Oberfläche, Erkennung und den exportierten Godot-Viewer.

Build im Projektstamm:

```powershell
.\build_lehrerausgabe.ps1
```

Start:

```powershell
.\build\lehrerausgabe\Lehrer_Stadt.exe
```

Wichtig: Die exportierte Godot-`.pck` enthält die rohe `parts.csv` nicht zuverlässig.
Das Buildskript kopiert `cityviewer/data/parts.csv` und `cityviewer/data/city.json`
explizit nach `_internal\cityviewer\data\`. Fehlt die `parts.csv` dort, zeigt der
3D-Start Farbblöcke statt Gebäuden.

Der Godot-Viewer-Export erfolgt verbindlich über die Godot-GUI
(`Projekt` → `Export ...`, Preset `Windows Desktop 2`).

## Tests

```powershell
python test_teacher_backend.py
python test_teacher_demo.py
python check_demo_examples.py
```

## Dokumentation

- Entwicklerdokumentation: [Readme.Dev.md](Readme.Dev.md)
- Bedienung: [controls.md](controls.md)
- Lizenzstatus und Quellen: [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)
