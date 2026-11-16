# Anleitung für Lehrkräfte – Entwicklungsfassung 0.2.0-dev

## Wichtig: noch kein fertiges EXE-Paket
Diese erste Oberfläche setzt das bereits funktionierende Projekt mit Python,
installierten Bibliotheken und der bisher verwendeten Godot-Programmdatei voraus.
Für die spätere Unterrichtsausgabe sollen diese Einrichtungsschritte entfallen.
Die 3D-Modelle müssen weiterhin vollständig im lokalen Projekt vorhanden sein.

## Einmal einrichten
1. Das Update über `install_update.py` wie in START_HIER.txt beschrieben installieren.
2. Im Projektordner eine PowerShell öffnen.
3. Ausführen:

```powershell
python -m pip install -r requirements-teacher.txt
```

Hierfür können Downloads erforderlich sein. Die spätere Verarbeitung selbst ist lokal.

## Starten
`Start_Lehreroberflaeche.bat` doppelklicken.
Alternativ im Projektordner: `python teacher_app.py`.

Beim ersten 3D-Start die bisher verwendete Godot-EXE über „Godot auswählen“ wählen.
Nicht `project.godot` und nicht eine beliebige andere EXE auswählen.
Der gewählte Programmpfad wird für die folgenden Starts gespeichert.

## Foto und Erkennung
1. Gedrucktes Rasterblatt mit den dazu passenden Gebäudekärtchen auslegen.
2. Alle vier Eckmarker sichtbar lassen. Blatt möglichst flach, scharf und ohne starke Schatten fotografieren.
3. „Bild auswählen“ drücken und das Foto auswählen.
4. „Stadt erkennen“ drücken und warten.
5. Kontrollbild prüfen: Sind Gebäude, Lage und Ausrichtung richtig?
6. Warnungen zu Überlappungen und außerhalb liegenden Kärtchen beachten.
7. „3D-Stadt öffnen“ drücken.

Das Auswahlfeld unten wechselt zwischen entzerrtem Kontrollbild, markiertem Original
und unverändertem Foto. Ein Doppelklick auf die Vorschau öffnet bei vorhandenem Ergebnis
das entzerrte Kontrollbild im externen Bildbetrachter.
Keine automatische Kontrolle kann garantieren, dass alle gelegten Kärtchen erkannt wurden.

## In der 3D-Stadt
- WASD oder Pfeiltasten: bewegen.
- Maus: umsehen.
- Umschalt: schneller bewegen.
- V: Rundgang / Vogelperspektive wechseln.
- Vogelperspektive: Mausrad zum Zoomen, Pos1 für die gesamte Stadt.
- F2: Gebäudenamen ein-/ausblenden.
- F3: Bildratenanzeige ein-/ausblenden.
- Esc: 3D-Ansicht schließen; Lehreroberfläche bleibt geöffnet.

## Falls etwas nicht funktioniert
- Fehlende Eckmarker: vollständiges Blatt neu fotografieren.
- Keine Gebäude: Fotoabstand, Schärfe und Sichtbarkeit der Marker prüfen.
- layout.json fehlt: die zum gedruckten Blatt gehörende Layoutdatei muss unter
  output/layout.json liegen. Nicht auf Verdacht neue Druckvorlagen erzeugen.
- Godot fehlt: richtige Godot-Programmdatei erneut auswählen.
- Blöcke statt Modellen: bestehende Modellinstallation bzw. Katalog prüfen lassen.
- Technische Fehler: „Protokoll“ und „Ergebnisordner“ öffnen. Dort liegen detect.log
  und nach einem Viewerstart viewer.log. Fehlermeldung mit Projektversion weitergeben.

## Datenschutz und Aufräumen
Es findet kein Foto-Upload durch diese Anwendung statt. Originalfotos werden nicht
verändert oder kopiert. Die Anwendung speichert jedoch Kontrollbilder, Stadtdaten
und Protokolle lokal; auch Kontrollbilder können personenbezogene Bildinhalte enthalten.
Unter Windows liegen sie unter `%LOCALAPPDATA%/CityProject/runs/`.
Mit „Ergebnisordner“ dorthin wechseln und nicht mehr benötigte Sitzungsordner löschen,
wenn keine Verarbeitung oder 3D-Ansicht läuft.

Für Beispieldateien möglichst nur das Stadtblatt ohne Personen oder Schülernamen verwenden.
