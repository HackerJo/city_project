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

## Demo-Erweiterung 0.3.0-dev

Die Oberfläche wird um eine Demo-Auswahl erweitert. `teacher_demo.py` enthält
Manifestprüfung, getrennte Demo-Sitzungen und zusätzliche Konsistenzprüfungen.
`teacher_backend.py` bleibt unverändert auf seinem bisherigen Stand; die angezeigte
Oberflächenversion kommt aus `teacher_demo.DEMO_VERSION`.

### Daten und Verhalten
`examples/demos.json` (schema_version 1) enthält die ausdrücklich freigegebenen Einträge.
Pfade sind relativ zu examples/. Jeder Beispielsatz enthält Foto, buildings.json,
layout.json, city.json, control.jpg, rectified_raw.jpg und rectified.jpg.
Fehlende Dateien deaktivieren nur das betroffene Beispiel; Hinweise erscheinen unten.
Dateinamen werden nicht umbenannt; Groß-/Kleinschreibung exakt wie im Manifest beachten.

Nach Auswahl eines Beispiels:
- Beispielfoto erkennen: echte Erkennung mit Layout und Katalog DES BEISPIELS.
- Demo direkt in 3D: vorbereitete Stadt und Kontrollbilder in eine neue Sitzung kopieren;
  keine neue Erkennung ausführen. Die Oberfläche kennzeichnet dies dauerhaft oben.
- Die vorhandene 3D-Schaltfläche öffnet anschließend das geladene/erkannte Ergebnis erneut.

Quellen werden niemals überschrieben. Neue Sitzungen landen im bestehenden lokalen
Arbeitsordner, Namen enthalten `_demo_`. Beispielkatalog und -layout werden nach
input/output kopiert. Die vorhandene Erkennungs-CLI bleibt unverändert.
Vorbereitete Kontrollbilder werden mit Pillow auf Lesbarkeit geprüft. Stadt und Layout
müssen dasselbe Raster haben; Gebäude müssen mit ID/Schlüssel/gedrehter Grundfläche zum
Demo-Katalog passen. Das beweist NICHT, dass Foto und Ergebnisse inhaltlich zusammengehören.
Diese Zuordnung muss bei der Abnahme visuell bestätigt werden.

### Katalogkonflikte
Beim direkten 3D-Start muss der gesamte Demo-Katalog als JSON-Inhalt dem aktuellen
cityviewer/data/buildings.json entsprechen. Einrückung und Schlüsselreihenfolge spielen
keine Rolle; Änderungen der Werte und der Gebäudelistenreihenfolge führen zum Konflikt.
Auch rein redaktionelle Abweichungen können daher blockieren. Das ist absichtlich streng.
Es gibt keinen automatischen Austausch des globalen Katalogs und keinen heimlichen
Fallback auf einen anderen Katalog. Die normale Viewerprüfung bleibt ebenfalls aktiv.

Die neue Erkennung eines Beispiels ist auch mit abweichendem Beispielkatalog möglich;
der 3D-Start wird dann durch die bestehende Viewerprüfung gesperrt. Die Erkennung allein
aktualisiert den Katalog nicht. Bei Konflikten Katalogstände vergleichen und den
Beispielsatz bewusst mit dem freigegebenen Projektstand neu herstellen. Nicht einfach
unterschiedliche JSON-Dateien durch Kopieren passend machen.

### Abnahme
1. Jede der drei Demos auswählen: Foto und Dateipfad stimmen.
2. Direkt in 3D starten: kein Erkennungslauf; sichtbare Kennzeichnung vorbereitet.
3. Mit Esc zurück; Beispielfoto neu erkennen; Kennzeichnung wechselt auf neu erkannt.
4. Kontrollbilder und Stadt mit dem Original vergleichen; Warnungen prüfen.
5. Zwischen Demos und eigenem Foto wechseln: altes Ergebnis sofort gesperrt.
6. Offline wiederholen. Beispiele unverändert; getrennte Ergebnisordner.
7. Fehlende Datei / beschädigtes JSON / abweichender Katalog: klare Meldung, kein alter Start.
8. Bisherige Tests mit eigenen Fotos erneut ausführen.

Automatische Tests: `python test_teacher_demo.py` und `python test_teacher_backend.py`.
Die Hilfsmodultests nutzen künstliche Beispielsätze, keine echte ArUco-Erkennung.
GUI/Windows/Godot und Ihre echten drei Beispielsätze sind noch praktisch abzunehmen.

### Git und spätere EXE
Versionieren: geänderte teacher_app.py, neues teacher_demo.py, test_teacher_demo.py,
examples/demos.json, freigegebene Beispielsätze und aktualisierte Anleitungen.
Updatepaket und backup_vor_demo_* nach dem Test extern archivieren.
Das Installations-Patchskript ist nur ein Hilfsmittel für dieses Update; ein frischer
Klon soll bereits die erweiterte teacher_app.py enthalten und keinen Patchlauf benötigen.
Die Demos müssen später im EXE-Paket enthalten sein. Worker-/Exportumbau ist weiterhin offen.
Videoeinbindung ist nicht Bestandteil dieser Erweiterung.
