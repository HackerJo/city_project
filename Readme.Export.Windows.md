# Windows-Export des CityViewers

Dokumentationsstand: 17. November 2026  
Godot-Version: **4.7.2 stable, offizieller Build, Commit `ed1daf0bf`**.

Diese Dateien bereiten den eigenständigen Windows-Export des 3D-Viewers vor.
Die Lehreroberfläche, die Erkennung und der getestete Python-Stand bleiben davon
unberührt. An GitHub wurde durch diese Dateien nichts geändert.

## 1. Dateien einsetzen

1. Das ZIP entpacken.
2. `cityviewer/export_presets.cfg` in den Ordner `cityviewer/` kopieren.
3. `build_viewer_windows.ps1` und `test_viewer_windows.ps1` in den Projektstamm kopieren.
4. `Readme.Export.Windows.md` bei Bedarf ebenfalls in den Projektstamm kopieren.

Falls bereits eine `export_presets.cfg` existiert, diese vorher sichern. Die
mitgelieferte Datei ist ein Startpunkt für den Windows-Export, keine fertige
Ersetzung ohne Sichtprüfung.

## 2. Export-Templates installieren

Godot benötigt für den Windows-Export die passenden Export-Templates:

1. Godot öffnen.
2. „Editor“ → „Export-Vorlagen verwalten …“ öffnen.
3. Die zu Godot **4.7.2 stable** passenden Windows-Export-Templates installieren.
4. Nach Abschluss Godot schließen.

Ohne passende Templates kann der Export nicht abgeschlossen werden. Die
Godot-Dokumentation beschreibt Export-Presets und die benötigten Templates für
den Export von Projekten. [web:397]

## 3. Windows-Export ausführen

PowerShell im Projektstamm öffnen und den Pfad zur Godot-EXE anpassen:

```powershell
.\build_viewer_windows.ps1 -Godot "C:\Pfad\zu\Godot_v4.7.2-stable_win64.exe"
```

Das Skript führt aus:

1. Godot-Erstimport für `cityviewer/`.
2. Windows-Export mit dem Profil `Windows Desktop`.
3. Prüfung der erwarteten Ausgabedatei und der Quellressourcen.

Das Ergebnis liegt standardmäßig unter:

```text
build/windows/CityViewer.exe
```

Der Export wird auf Windows erstellt. PyInstaller ist ebenfalls kein
plattformübergreifender Compiler; ein Windows-Build muss auf Windows erfolgen. [web:392]

## 4. Viewer testen

```powershell
.\test_viewer_windows.ps1 `
  -ViewerExe ".\build\windows\CityViewer.exe" `
  -Godot "C:\Pfad\zu\Godot_v4.7.2-stable_win64.exe"
```

Der Test startet standardmäßig die Demo-Stadt unter
`examples/city02/city.json`.

Prüfen Sie insbesondere:

- Die Stadt öffnet sich ohne Godot-Editor.
- Gebäude, Texturen und Farben werden korrekt dargestellt.
- Die Steuerung mit WASD/Pfeiltasten und Maus funktioniert.
- `V` wechselt zwischen Rundgang und Vogelperspektive.
- `Esc` schließt den Viewer.

Ein erfolgreicher Start beweist nicht automatisch, dass alle Modelle und
Texturen korrekt eingebunden sind. Die Sichtprüfung ist daher erforderlich.

## 5. Wenn etwas fehlt

| Problem | Wahrscheinliche Ursache | Vorgehen |
|---|---|---|
| Export-Templates fehlen | Templates nicht installiert | Templates für Godot 4.7.2 installieren. |
| Keine `CityViewer.exe` | Export fehlgeschlagen | Vollständige Godot-Ausgabe prüfen. |
| Nur Farbblöcke | Ressourcen oder Importcache unvollständig | Erstimport wiederholen und Importfehler prüfen. |
| JSON/CSV fehlen | Exportfilter unvollständig | `include_filter` in `export_presets.cfg` prüfen. |
| Viewer startet nicht | Pfad, Architektur oder fehlende Dateien | Fehlerausgabe und Zielordner prüfen. |

## 6. Nächster Schritt

Nach erfolgreicher Sichtprüfung wird die Lehreroberfläche angepasst:

- Automatischer Start der mitgelieferten `CityViewer.exe`.
- Keine Auswahl einer Godot-Editor-EXE im fertigen Lehrerpaket.
- Danach erst die Python-Anwendung für das Windows-Paket verpacken.

Die exportierte `CityViewer.exe` ist ein Zwischenschritt, nicht bereits das
fertige Unterrichtspaket.
