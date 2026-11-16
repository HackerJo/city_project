# Drittanbieter-Inhalte und Lizenzstatus

Dokumentationsstand: 16. November 2026.

Diese Übersicht dokumentiert die bestätigte Modellquelle und den noch offenen
Lizenzumfang des späteren Windows-Pakets. Sie ist noch keine vollständige Sammlung
aller für die binäre Weitergabe erforderlichen Lizenztexte.

## 1. 3D-Modelle: Medieval Village MegaKit

| Angabe | Inhalt |
|---|---|
| Urheber / Anbieter | Quaternius |
| Paket | Medieval Village MegaKit |
| Verwendete Ausgabe | Kostenlose Ausgabe, laut Angabe des Projektbetreibers |
| Offizielle Quelle | https://quaternius.com/packs/medievalvillagemegakit.html |
| Auf der Paketwebseite ausgewiesene Freigabe | CC0 |
| Erläuterung CC0 1.0 Universal | https://creativecommons.org/publicdomain/zero/1.0/deed.de |
| Vollständiger CC0-Text | https://creativecommons.org/publicdomain/zero/1.0/legalcode |
| Verwendung im Projekt | Modulare Bauteile für Gebäude und Stadtgestaltung |
| Ressourcenbereich | `cityviewer/models/parts/` |

Die offizielle Paketwebseite wurde am 16. November 2026 geprüft und weist CC0 aus.
Die konkrete Herkunft der verwendeten Ausgabe beruht auf der Angabe des
Projektbetreibers; ein vollständiger Einzeldateiabgleich mit dem Originalarchiv
wurde im Rahmen dieser Dokumentation nicht vorgenommen.

Die Modelle werden in der Anwendung zu Gebäuden und Stadtanordnungen zusammengesetzt.
Quaternius ist der Anbieter dieser Modellressourcen, nicht der Entwickler der
Lehreroberfläche, Erkennung oder projektspezifischen Gebäude-Baulogik.

### Bedeutung der CC0-Freigabe

CC0 erlaubt die urheberrechtlich erfasste Nutzung, Bearbeitung und Weitergabe auch
für kommerzielle Zwecke, ohne verpflichtende Namensnennung. Die Quellenangabe hier
ist bewusst aufgenommen, um die Herkunft nachvollziehbar zu halten.

CC0 enthält keine Garantie und beseitigt nicht automatisch etwaige eigenständige
Marken-, Patent- oder Persönlichkeitsrechte. Eine Unterstützung oder Empfehlung
dieser Anwendung durch Quaternius wird nicht behauptet.

### Originalhinweise erhalten

Falls das verwendete Downloadarchiv eine Lizenz-, Quellen- oder Readme-Datei
enthält, diese unverändert zusätzlich aufbewahren, beispielsweise unter
`licenses/quaternius-medieval-village/`. Dieser Pfad ist eine Empfehlung; die
Existenz solcher Dateien wird mit dieser Übersicht nicht behauptet.

Die CC0-Angabe gilt für die tatsächlich vom Paket erfassten Inhalte. Separat
hinzugefügte Modelle oder Texturen benötigen eine eigene Herkunfts- und Lizenzprüfung.

## 2. Eigener Anwendungscode

Diese Dokumentation legt keine Lizenz für den eigenen Projektcode fest. Die
Modellfreigabe überträgt sich nicht automatisch auf Python-/GDScript-Code,
Dokumentation oder sämtliche übrigen Inhalte.

Vor einer ausdrücklich lizenzierten Veröffentlichung ist die Lizenzentscheidung
des Rechteinhabers in einer separaten `LICENSE`-Datei zu dokumentieren. Falls bereits
eine Lizenzdatei existiert, ist diese zu prüfen; diese Übersicht ersetzt sie nicht.
Aus der bloßen Erreichbarkeit des Repositorys folgt keine hier erteilte allgemeine
Nutzungserlaubnis für alle Inhalte.

## 3. Beispiele, Bilder und Video

Die Beispielsätze unter `examples/city02/`, `examples/city03/` und `examples/city04/`
umfassen Foto, Katalog, Layout, Stadtdaten und Kontrollbilder. Ergänzende Medien
liegen unter `examples/recognition/`, `examples/print/` und `examples/video/`.

Für diese Dateien ist vor Weitergabe sicherzustellen:

- Die erforderlichen Rechte an Fotos, Video und gegebenenfalls Ton liegen vor.
- Enthaltene Fremdinhalte werden von einer passenden Erlaubnis erfasst.
- Es werden keine personenbezogenen Inhalte unbeabsichtigt veröffentlicht.
- Historische Demonstrationen sind als solche gekennzeichnet.

Für Fotos oder Video wird mit dieser Datei keine eigenständige CC0-Freigabe behauptet.

## 4. Softwarebestandteile: Prüfung vor dem EXE-Paket

Die derzeitige Entwicklungsfassung verwendet bzw. benennt folgende Komponenten.
Die Tabelle ist eine Prüfliste, keine vollständige Lizenzbilanz:

| Komponente | Verwendung | Vor binärer Weitergabe festzuhalten |
|---|---|---|
| Godot Engine | 3D-Viewer und späterer Engine-Export | Version, Lizenztext, erforderliche Drittanbieter-Hinweise des Exports |
| Python | Interpreter der Entwicklungsfassung, eventuell im Paket gebündelt | Tatsächlich gebündelte Version und Lizenzhinweise |
| Tcl/Tk | Tk-Oberfläche | Tatsächlich mitgelieferte Laufzeit und Lizenzhinweise |
| Pillow | Bildvorschau und Bildprüfungen | Version, Lizenz und mitgelieferte native Komponenten |
| opencv-contrib-python / OpenCV | ArUco-Erkennung und Bildverarbeitung | Wheel-/OpenCV-Version und enthaltene Drittanbieter-Hinweise |
| NumPy | Verarbeitung von Bild- und Koordinatendaten | Version und Hinweise zu enthaltenen Bibliotheken |
| ReportLab | Erzeugung der Druck-PDFs | Version; klären, ob im Lehrerausgabepaket tatsächlich enthalten |
| PyInstaller | Geplantes Buildwerkzeug | Bei Verwendung Version und Bedingungen des Bootloaders berücksichtigen |

Nicht jede Entwicklungsabhängigkeit muss zwingend Bestandteil der Lehrerausgabe
sein. Maßgeblich ist, was der konkrete Build tatsächlich enthält. Transitive und
native Abhängigkeiten ebenfalls erfassen; die obige Liste ist nicht abschließend.

### Abschlusskriterien für die Lizenzsammlung

1. Den getesteten Build samt exakten Abhängigkeitsversionen festhalten.
2. Lizenz- und Notice-Dateien aus den tatsächlich verwendeten Distributionen sammeln.
3. Geforderte Hinweise ohne Verkürzung übernehmen und gut auffindbar beilegen.
4. Originalhinweise nicht durch diese zusammenfassende Markdown-Datei ersetzen.
5. Einbeziehung in das endgültige Windows-Paket prüfen.

## 5. Status

- Bestätigt: offizielle Modellpaket-Webseite weist CC0 aus.
- Dokumentiert: Nutzung der kostenlosen Ausgabe laut Projektbetreiber.
- Offen: ausdrückliche Lizenzentscheidung für den eigenen Code.
- Offen: abschließende Rechteprüfung der Beispielmedien.
- Offen: vollständige versionsbezogene Lizenz-/Notice-Sammlung des Windows-Pakets.

Die erfolgreiche technische Abnahme der Python-Fassung bedeutet nicht, dass diese
noch offenen Veröffentlichungspunkte bereits erledigt sind.
