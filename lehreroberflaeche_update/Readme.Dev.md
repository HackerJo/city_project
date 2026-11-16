# Entwicklerhinweise – Lehreroberfläche 0.2.0-dev

## Status
Dies ist eine zusätzliche Python-Lehreroberfläche für das vorhandene Projekt,
noch keine eigenständige Windows-EXE. Bestehende Erkennung und Godot-Dateien
werden nicht ersetzt. GUI-, Godot- und vollständiger ArUco-Test auf Windows stehen aus.

## Start
Im Projektordner:

```powershell
python -m pip install -r requirements-teacher.txt
python teacher_app.py
```

Python mit Tk-Unterstützung verwenden (bei der Windows-Python-Installation die
Tcl/Tk-Komponente mitinstallieren). Pillow ergänzt die bisherigen Anforderungen.
Diese Anforderungsdateien sind noch kein reproduzierbarer Versions-Lock.
Nach bestandenem Test in einer frischen Umgebung genaue Versionen dokumentieren.

## Architektur
- `teacher_app.py`: Tk-Oberfläche; nur der Hauptthread verändert Widgets.
- `teacher_backend.py`: Dateiprüfung, getrennte Sitzungen, CLI-Aufrufe, Ergebnisprüfung.
- `scripts/detect_city.py`: unveränderte bestehende Mehrpass-Erkennung.
- `cityviewer/`: unveränderter bestehender Godot-Viewer.

Erkennungsaufruf:

```text
python scripts/detect_city.py --image <absolutes Foto> --root <Sitzung>/input --out <Sitzung>/result
```

Der temporäre Eingabestamm enthält `output/layout.json` und `output/buildings.json`.
Dadurch schreibt die Erkennung nicht in bestehende scanresult-Ergebnisse.

Vieweraufruf:

```text
<Godot-Programm> --path <absoluter Projektpfad>/cityviewer -- <Sitzung>/result/city.json
```

`main.gd` liest das erste Benutzerargument als Stadtdatenpfad. Für diesen Aufruf
sind keine Änderungen an main.gd, building_builder.gd oder city_wall.gd erforderlich.
Der konfigurierte Programmpfad ist in dieser Fassung der Godot-Editor/Engine,
nicht eine bereits exportierte Viewer-EXE.

## Datenquellen und kein stilles Überschreiben
- `settings/settings.csv`, `settings/buildings.csv`: bearbeitbare Konfiguration.
- `scripts/generate_prints.py`: erzeugt Druckvorlagen und JSON-Dateien.
- `output/layout.json`: Geometrie des tatsächlich verwendeten Druckblatts.
- `cityviewer/data/buildings.json`: vom Viewer tatsächlich gelesener Katalog.
- `output/buildings.json`: bisheriger Scanner-Katalog aus der Druckerzeugung.

Die Oberfläche kopiert bewusst den VIEWER-Katalog in die neue Erkennungssitzung.
Damit verwenden Erkennung und Viewer denselben Katalogstand. Vor dem Viewerstart
wird geprüft, ob der Originalkatalog seit der Erkennung geändert wurde.
Es gibt KEINE automatische Druckerzeugung und KEINE automatische Übernahme von CSV-
Änderungen in JSON: neue IDs/Grundflächen/Rasterparameter müssen bewusst aktualisiert
und mit den gedruckten Kärtchen abgeglichen werden. Alte Drucklayouts nicht unbemerkt ersetzen.

## Arbeitsdaten
Windows: `%LOCALAPPDATA%/CityProject/`
Andere Systeme: `~/.local/share/CityProject/`

```text
teacher_settings.json       gespeicherter Godot-Pfad
runs/<Zeitstempel>_<ID>/
  session.json              Versions- und Quellpfade
  detect.log                Erkennung, stdout/stderr, Adapterfehler
  viewer.log                Godot-Ausgabe, sobald gestartet
  input/output/layout.json
  input/output/buildings.json
  result/city.json
  result/control.jpg
  result/rectified.jpg
  result/rectified_raw.jpg
```

Originalfotos werden nicht kopiert und nicht hochgeladen. Abgeleitete Kontrollbilder
enthalten aber ebenfalls das Foto bzw. den Blattinhalt. Protokolle/Sitzungsdaten können
lokale Dateinamen und Benutzernamen enthalten. Keine automatische Löschfrist implementiert.
Sitzungsordner nur löschen, wenn keine zugehörige Verarbeitung/3D-Ansicht läuft.

## UI-Zustände
Neues Foto -> altes Ergebnis verwerfen -> Erkennung im Hintergrund -> Ergebnis prüfen.
Keine Gebäude oder kaputte Ergebnisse -> kein 3D-Start. Warnungen (z.B. Überlappungen)
werden angezeigt; 3D-Start ist erst nach ausdrücklicher Bestätigung möglich.
Während Erkennung und Viewer sind Start- und Auswahlknöpfe gesperrt.
Beim Schließen fragt die Oberfläche bei laufendem Prozess nach und beendet diesen.
Keine automatische zeitliche Prozessbegrenzung, keine separate Abbrechen-Schaltfläche.

## Tests

```powershell
python test_teacher_backend.py
```

Acht Adaptertests: Eingabeprüfung, eindeutige Sitzungen, keine Originalfotokopie,
Ergebnisprüfung, leere Ergebnisse, Überlappungen, Katalogänderungen und CLI-Schnittstelle.
Der CLI-Test nutzt einen ausdrücklich künstlichen Testdetektor, keine echte ArUco-Erkennung.
Diese Tests ersetzen keinen Tk-, Godot- oder Windows-Integrationstest.

## Abnahme auf dem Surface Go 3
1. Bestehenden Programmstand ohne UI weiterhin starten können.
2. Beispielfoto auswählen und Kontrollbild vergleichen.
3. Vier Eckmarker, Anzahl, Grundflächen und Türseiten prüfen.
4. Testfoto mit fehlendem Eckmarker -> klare Meldung, kein altes Ergebnis verwenden.
5. Neues Foto wählen -> 3D-Schaltfläche sofort wieder gesperrt.
6. Godot wählen; Viewer öffnen, laufen, V wechseln, Esc -> Oberfläche bleibt offen.
7. Pfade mit Leerzeichen und Umlauten prüfen, insbesondere Kontrollbilder.
8. Überlappung -> Warnung und bewusste Bestätigung.
9. Zweite Erkennung -> eigener Ergebnisordner.
10. WLAN aus; derselbe komplette Ablauf.
11. Große Fotos, lange Erkennungsdauer und Speicherauslastung prüfen.

## Bekannte Grenzen / nächste Arbeiten
- Diese Version startet den Detektor mit dem aktuellen Python-Interpreter. Nicht
  unverändert mit PyInstaller einfrieren: sys.executable wäre dann die Launcher-EXE.
  Für den Build einen expliziten Worker-Modus oder eine gebündelte Erkennungs-EXE ergänzen.
- Bestehender Detektor schreibt Kontrollbilder mit cv2.imwrite; Schreibverhalten für
  Unicode-Pfade auf dem Zielsystem testen. Die Oberfläche meldet fehlende Kontrollbilder.
- JSON/CSV-Abgleich ist absichtlich noch nicht automatisiert.
- GUI-Stil, Touch-Bedienbarkeit und Größen auf dem Surface noch praktisch prüfen.
- Godot-Export, Exportfilter für JSON/CSV, Windows-Paket und Lizenzsammlung folgen.
- Ein fertiges EXE-Paket muss ohne Python-Installation und ohne Godot-Editor getestet werden.
- Keinen alten Gebäude-/Mauerpatch erneut auf den konsolidierten Viewer anwenden.
