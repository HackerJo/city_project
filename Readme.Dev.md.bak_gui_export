# Entwicklerdokumentation

Dokumentationsstand: 16. November 2026 · Oberfläche: `0.3.0-dev`.

Diese Datei beschreibt die getestete Python-Fassung. Sie ist keine fertige
Build-Anleitung für ein eigenständiges EXE-Paket.

## 1. Zweck und Architektur

Ein Foto von ArUco-Gebäudekärtchen wird in eine Stadtdaten-Datei übersetzt und in
Godot dargestellt. Die Lehreroberfläche bündelt Auswahl, Erkennung, Kontrolle und
Viewerstart; Erkennung und Viewer laufen als getrennte Prozesse.

| Datei | Aufgabe |
|---|---|
| `teacher_app.py` | Tk-Oberfläche, Zustandswechsel, Vorschau, Prozesssteuerung |
| `teacher_backend.py` | Normale Sitzungen, Erkennungsaufruf, Ergebnis- und Viewerprüfung |
| `teacher_demo.py` | Demo-Manifest, Beispielsitzungen und Konsistenzprüfungen |
| `scripts/detect_city.py` | ArUco-Erkennung und Ausgabe von Stadtdaten/Kontrollbildern |
| `scripts/generate_prints.py` | Druckvorlagen und abgeleitete JSON-Dateien |
| `scripts/settings_loader.py` | Laden und Prüfen der CSV-Konfiguration |
| `scripts/i18n.py` | Übersetzungen der Skriptmeldungen |
| `scripts/paths.py` | Projektpfad-Hilfsfunktion |
| `cityviewer/scripts/main.gd` | Stadtdaten laden, Szene, Kamera und Bedienung |
| `cityviewer/scripts/building_builder.gd` | Modulare Gebäude aus Bauteilen zusammensetzen |
| `cityviewer/scripts/city_wall.gd` | Außenmauer und Tore |

Die UI-Widgets werden im Hauptthread verändert. Hintergrundarbeit meldet Ergebnisse
über eine Queue. Während Verarbeitung oder Viewerbetrieb sind relevante Auswahl-
und Startschaltflächen gesperrt.

Die angezeigte Oberflächenversion kommt im Demo-Stand aus
`teacher_demo.DEMO_VERSION`. `teacher_backend.VERSION` kann weiterhin `0.2.0-dev`
lauten, da das Backend bei der Demo-Erweiterung nicht ersetzt wurde. Dies ist vor
einem Release zu einer einheitlichen Versionsquelle zusammenzuführen.

## 2. Einrichtung eines frischen Arbeitsordners

Windows, Python mit Tk und die bisher getestete Godot-Engine verwenden. Getestete
Godot-Version laut Funktionstest: 4.7.2. Die Python-Abhängigkeiten sind derzeit keine
vollständig versionierte Lockdatei.

Optional eine virtuelle Umgebung einrichten:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Falls die Aktivierung durch lokale PowerShell-Regeln gesperrt ist, kann der
Interpreter direkt verwendet werden, etwa `.\.venv\Scripts\python.exe` statt `python`.
Keine pauschale Änderung der systemweiten Ausführungsrichtlinie voraussetzen.

```powershell
python -m pip install -r requirements-teacher.txt
```

### Godot-Erstimport: zwingender Einrichtungsschritt

PowerShell im Projektstamm, Pfad anpassen:

```powershell
$Godot = "C:\Pfad\zu\Godot_v4.7.2-stable_win64.exe"
& $Godot --headless --path ".\cityviewer" --import
if ($LASTEXITCODE -ne 0) {
    throw "Godot-Import fehlgeschlagen. Importausgabe prüfen."
}
```

Auf vollständigen Abschluss warten und die Ausgabe auf Fehler prüfen. Der
Exitcode allein ist kein Ersatz für den praktischen Darstellungstest.

Beim frischen Download fehlten erwartungsgemäß die erzeugten Ressourcen unter
`.godot/imported/`. Ein direkter Szenenstart führte zu Ladefehlern und Farbblöcken.
Nach Erstimport wurden laut Projektbetreiber Strukturen, Farben und Texturen korrekt
dargestellt. Die bisherige GUI führt diesen Erstimport nicht automatisch aus.

- `cityviewer/.godot/` bleibt regenerierbarer lokaler Cache.
- Quellmodelle, referenzierte Binärdaten und Texturen müssen vollständig vorliegen.
- Ressourcenbegleitende `.import`- und `.uid`-Dateien nicht pauschal entfernen.
- Bei Importfehlern die erste konkrete Ursache prüfen, nicht nur Folgefehler beim Laden.

## 3. Datenquellen und erzeugte Dateien

```text
settings/settings.csv + settings/buildings.csv
                  |
                  v
       scripts/generate_prints.py
                  |
                  +--> output/layout.json
                  +--> output/buildings.json
                  +--> output/print/grid_sheet.pdf
                  +--> output/print/cards.pdf
                  +--> cityviewer/data/buildings.json
```

Die CSV-Dateien sind bearbeitbare Quellen. JSON und PDFs sind abgeleitete Daten.
Der freigegebene, zu den verwendeten Ausdrucken passende Stand wird bewusst mit dem
Projekt aufbewahrt. Deshalb dürfen die fünf oben genannten Dateien nicht durch
Ignore-Regeln versehentlich aus dem vollständigen Download herausfallen.

Druckerzeugung nur bewusst aufrufen:

```powershell
python scripts/generate_prints.py
```

Nicht bei jedem GUI-Start neu erzeugen: Geänderte IDs, Grundflächen oder
Rasterparameter können alte Ausdrucke und Demos ungültig machen. CSV-Änderungen
werden nicht automatisch beim GUI-Start übernommen.

### Normale GUI-Erkennung

`prepare_run` verwendet:

- Layout: `output/layout.json`.
- Katalog: `cityviewer/data/buildings.json`, also den tatsächlich vom Viewer gelesenen Stand.

Diese Daten werden in die neue Sitzung nach `input/output/` geschrieben. Der
Detektor wird mit dem Sitzungs-Eingabestamm gestartet. `output/buildings.json`
bleibt zusätzlich der Katalog für einen direkten Standardaufruf des Detektors.
Abweichungen zwischen diesen beiden Katalogkopien deshalb nicht unbemerkt lassen.

### Erkennungs- und Vieweraufrufe

Sinngemäße Aufrufe; Platzhalter nicht wörtlich übernehmen:

```text
python scripts/detect_city.py --image <absolutes Foto> --root <Sitzung>/input --out <Sitzung>/result
<Godot-EXE> --path <absolutes Projekt>/cityviewer -- <Sitzung>/result/city.json
```

`main.gd` liest den ersten Benutzerparameter als Stadtdatenpfad. Ohne diesen wird
`res://data/city.json` verwendet. Eine mitversionierte Standardstadt ist für den
GUI-/Demo-Aufruf nicht erforderlich; ein argumentloser Direktstart benötigt sie.

Der direkte Detektoraufruf ohne eigenes `--out` schreibt standardmäßig nach
`scanresult/`. Die Oberfläche verwendet davon getrennte Sitzungsordner.

## 4. Beispiele und Demo-Modus

```text
examples/
├─ demos.json
├─ city02/
│  ├─ buildings.json
│  ├─ city.json
│  ├─ control.jpg
│  ├─ Example_City_02.JPEG
│  ├─ layout.json
│  ├─ rectified_raw.jpg
│  └─ rectified.jpg
├─ city03/                  # entsprechend mit Example_City_03.JPEG
├─ city04/                  # entsprechend mit Example_City_04.JPEG
├─ print/
├─ recognition/
└─ video/
```

`examples/demos.json` verwendet `schema_version: 1` und eine Liste `demos`.
Ein Eintrag enthält `id`, `title`, `folder`, `photo` und optional `description`.
Ordnerpfade sind relativ zu `examples/`, Fotopfade relativ zum Beispielordner.
Groß-/Kleinschreibung der tatsächlichen Dateinamen erhalten. Pfade außerhalb des
Beispielbereichs werden abgelehnt. Fehlende Dateien führen zu Demo-Hinweisen;
die betroffene Demo wird nicht angeboten.

### Zwei getrennte Aktionen

| Aktion | Eingaben und Ergebnis |
|---|---|
| Beispielfoto erkennen | Neue Erkennung mit Foto, Layout und Katalog des Beispiels |
| Demo direkt in 3D | Vorbereitete Stadt/Kontrollbilder in neue Sitzung kopieren; keine Erkennung |

Die vorbereitete Demo startet nach Prüfung den vorhandenen Viewerablauf. Warnungen
benötigen weiterhin eine Bestätigung. Die normale 3D-Schaltfläche kann das geladene
Ergebnis erneut öffnen. Beim Wechsel auf anderes Foto oder andere Demo wird das
vorige aktive Ergebnis verworfen.

Vorbereitete und neu erkannte Ergebnisse werden sichtbar unterschieden. Quellen
unter `examples/` bleiben unverändert. Eine neue Demo-Erkennung schreibt nicht in
den Beispielsatz zurück.

### Konsistenz und Katalogkonflikte

Geprüft werden unter anderem:

- Gültiges Layout und nichtleerer Katalog ohne doppelte IDs/Schlüssel.
- Rastergröße der Stadt im Verhältnis zum Demo-Layout.
- Gebäudeschlüssel, gegebenenfalls IDs und nach Türseite gedrehte Grundflächen.
- Lesbarkeit vorbereiteter Kontrollbilder.
- Kataloggleichheit vor dem 3D-Start.

Der vorbereitete Direktstart verlangt Gleichheit des gesamten JSON-Inhalts mit
`cityviewer/data/buildings.json`. Unterschiede in Einrückung und
Objektschlüsselreihenfolge sind egal; Listenreihenfolge und Werte sind relevant.
Auch redaktionelle Änderungen können daher einen Konflikt auslösen.

Ein abweichender Demo-Katalog darf für eine neue Demo-Erkennung verwendet werden;
der anschließende Viewerstart wird bei Katalogabweichung durch die Backendprüfung
gesperrt. Kein automatisches Überschreiben des globalen Katalogs implementiert.

Die Meldung des bisherigen Backends kann dabei „Katalog wurde seit der Erkennung
geändert“ lauten, obwohl der archivierte Demokatalog bereits vorher abwich. Gemeint
ist in beiden Fällen: Viewer- und Sitzungskatalog sind nicht identisch.

Technische Prüfungen beweisen nicht die inhaltliche Zuordnung von Foto und Scan.
Diese bei jeder Freigabe visuell prüfen.

## 5. Arbeitsdaten und Datenschutz

Unter Windows:

```text
%LOCALAPPDATA%/CityProject/
├─ teacher_settings.json
└─ runs/<Zeitstempel>_<Kennung>/
   ├─ session.json
   ├─ detect.log
   ├─ viewer.log                 # ab Viewerstart
   ├─ input/output/layout.json
   ├─ input/output/buildings.json
   └─ result/
      ├─ city.json
      ├─ control.jpg
      ├─ rectified.jpg
      └─ rectified_raw.jpg
```

Demoläufe enthalten `_demo_` im Sitzungsnamen. `session.json` dokumentiert den Modus
`prepared_demo` bzw. `demo_recognition`. Ohne LOCALAPPDATA verwendet die
Pfadhilfe `~/.local/share/CityProject/`.

Die Anwendung enthält keinen Foto-Upload. Originalfotos werden nicht kopiert oder
verändert. Erzeugte Kontrollbilder können dennoch den gesamten ursprünglichen
Bildinhalt enthalten. Protokolle/Metadaten enthalten möglicherweise lokale Pfade
und Benutzernamen. Keine automatische Löschfrist implementiert.

Sitzungen bei Bedarf löschen, wenn weder zugehörige Verarbeitung noch Viewer läuft.
Beispielfotos vor öffentlicher Veröffentlichung auf personenbezogene Inhalte prüfen.
Die gespeicherte Godot-Auswahl ist benutzerbezogen und kein portabler Projektpfad.

## 6. Tests und Abnahme

```powershell
python test_teacher_backend.py
python test_teacher_demo.py
python check_demo_examples.py
```

- Backendtests: Adapterfunktionen, isolierte Dateisätze und Prozessschnittstelle;
  ein künstlicher Testdetektor ist kein echter ArUco-Test.
- Demotests: künstliche Beispielsätze; Sitzungen, Pfade, Bild-/Datenprüfung und Konflikte.
- Beispielprüfung: echte lokale Beispielsätze, temporäre Kopien; keine Erkennung
  und kein Godot-Start. Quelldateien werden nicht verändert.

### Vom Projektbetreiber bestätigte Funktionstests

- Eigene Bilder und drei Demo-Fotos erfolgreich erkannt.
- Vorbereitete Demos geöffnet; Kennzeichnung und Bedienung wie vorgesehen.
- Überlappungen angezeigt, fehlender Eckmarker verständlich behandelt.
- Keine alten Stadtdaten nach Eingabewechsel oder fehlgeschlagener Erkennung startbar.
- Rückkehr mit Esc zur weiterhin geöffneten Oberfläche.
- Offlinebetrieb bestätigt.
- Frischer GitHub-ZIP-Download: Prüfskripte erfolgreich, GUI startbar.
- Nach Godot-Erstimport: Gebäudestrukturen, Texturen und Farben korrekt.

Aus der Rückmeldung zum frischen Download folgt keine Prüfung auf einem Rechner
ohne Entwicklungswerkzeuge. Die gemeldete Grafik-Hardware dieses Downloadtests
war Intel Arc 140V; eine vollständige Performanceabnahme des Zielgeräts Surface Go 3
ist daraus nicht abzuleiten.

### Wiederholung vor einer Freigabe

1. Frischen Repository-Download in eigenem Ordner verwenden.
2. Abhängigkeiten und Godot-Erstimport einrichten.
3. Tests und Demo-Prüfung ausführen.
4. Demos und eigenes Foto praktisch prüfen, inklusive Warnung/Fehlerfall.
5. Gebäude, Texturen und Farben prüfen.
6. Offline testen; vollständige Zielgeräte-/Performanceprüfung separat festhalten.
7. Keine fehlenden Ressourcen aus dem alten Arbeitsordner hineinkopieren.

## 7. Repository-Hygiene

Behalten: Quellcode, Tests, Szenen, benötigte Modelle/Texturen, `.uid`- und
ressourcenbegleitende `.import`-Dateien, Einstellungen, freigegebene Demos,
Layout/Katalog/Druckvorlagen, Dokumentation und Lizenznachweise.

Nicht als erforderlichen Quellstand behandeln: `.godot/`, `__pycache__/`, virtuelle
Umgebungen, Build-Ausgaben, lokale Logs, Editor-EXEs, alte Updatepakete oder Sicherungen.
Persönliche Notizen unter `docs_development/` sind keine Build-Voraussetzung.
Quellen-/Lizenzinformationen nicht versehentlich als private Notizen aussortieren.

Ignore-Ausnahmen müssen unter den allgemeinen Regeln stehen, wenn diese Daten
bewusst versioniert werden:

```gitignore
!/output/layout.json
!/output/buildings.json
!/output/print/cards.pdf
!/output/print/grid_sheet.pdf
!/cityviewer/data/buildings.json
```

Ein frischer Klon enthält bereits den integrierten Code und benötigt keine
historischen `apply_patch_*.py`- oder Update-Installer.

## 8. Windows-Paket: noch offen

Die früher skizzierten PyInstaller-Aufrufe sind keine fertig geprüfte Buildlösung.
Noch umzusetzen und separat zu testen:

- Definierter Worker-Modus oder eigene Erkennungs-EXE.
- Korrekte Einbindung von `scripts/` und dessen Imports.
- Trennung von gebündelten Ressourcen, Projektdateien und beschreibbaren Benutzerdaten.
- Automatischer Aufruf eines exportierten Godot-Viewers statt Editor-Auswahl.
- Godot-Import und -Export im Build; JSON-/CSV-Filter und dynamisch geladene Modelle prüfen.
- Demos, Texturen und abhängige Modelldateien vollständig paketieren.
- Abhängigkeitsversionen und Drittanbieter-Hinweise festhalten.
- Abnahme auf Windows ohne separate Python-/Godot-Editor-Installation und offline.

Nicht einfach `sys.executable scripts/detect_city.py` unverändert einfrieren:
`sys.executable` bezeichnet in einer eingefrorenen Anwendung die Anwendungs-EXE.
Der aktuelle Vieweraufruf verwendet Editorparameter (`--path`); der Exportaufruf
muss passend zur späteren Paketstruktur implementiert werden.

Lizenzstatus und Quellen: [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
