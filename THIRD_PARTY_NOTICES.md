# Drittanbieter-Inhalte und Lizenzstatus

Dokumentationsstand: 21. November 2026.

Diese Übersicht dokumentiert die bestätigte Modellquelle, die Lizenzlage der
gebündelten Abhängigkeiten und die Lizenz des eigenen Codes.

## 1. 3D-Modelle: Medieval Village MegaKit

| Angabe | Inhalt |
|---|---|
| Urheber / Anbieter | Quaternius |
| Paket | Medieval Village MegaKit |
| Verwendete Ausgabe | Kostenlose Ausgabe, laut Angabe des Projektbetreibers |
| Offizielle Quelle | https://quaternius.com/packs/medievalvillagemegakit.html |
| Auf der Paketwebseite ausgewiesene Freigabe | CC0 |
| Vollständiger CC0-Text | https://creativecommons.org/publicdomain/zero/1.0/legalcode |
| Verwendung im Projekt | Modulare Bauteile für Gebäude und Stadtgestaltung |
| Ressourcenbereich | `cityviewer/models/parts/` |
| Lokale Lizenzdatei | `licenses/quaternius-medieval-village/License_Standard.txt` |

Die offizielle Paketwebseite wurde geprüft und weist CC0 aus.
CC0 erlaubt die urheberrechtlich erfasste Nutzung, Bearbeitung und Weitergabe
auch für kommerzielle Zwecke, ohne verpflichtende Namensnennung. Die Quellenangabe
hier ist bewusst aufgenommen, um die Herkunft nachvollziehbar zu halten.

## 2. Eigener Anwendungscode

Der eigene Projektcode ist unter der Custom-Lizenz in `LICENSE` verfügbar:

- Private Nutzung ist frei.
- Kommerzielle Nutzung erfordert vorherige schriftliche Zustimmung und eine
  angemessene Aufwandsentschädigung.
- Bei Weitergabe muss ein Hinweis auf dieses Projekt erhalten bleiben.
- Kontakt über GitHub: https://github.com/HackerJo/city_project

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

## 4. Softwarebestandteile: Lizenzen

Die Lizenzen der gebündelten Abhängigkeiten liegen im Ordner
`licenses/python-dependencies/`:

| Komponente | Lizenzdatei im Repo | Lizenz |
|---|---|---|
| Python | `python-3.15-64.LICENSE.txt` | PSF License |
| NumPy | `numpy.LICENSE.txt` | BSD-3-Clause |
| OpenCV | `opencv.LICENSE.txt` + `opencv.LICENSE-3RD-PARTY.txt` | Apache 2.0 + Drittanbieter-Hinweise |
| ReportLab | `reportlab.license.txt` | BSD |

Für die folgenden Komponenten ist die Lizenz online verfügbar (keine lokale
Datei im Repo, da nicht physisch vorhanden):

| Komponente | Lizenz | Online-Link |
|---|---|---|
| Tcl/Tk | Tcl/Tk License | http://www.tcl.tk/software/tcltk/license.html |
| Pillow | MIT-CMU (HPND) | https://github.com/python-pillow/Pillow/blob/main/LICENSE |
| PyInstaller | GPL mit Bootloader-Ausnahme | https://github.com/pyinstaller/pyinstaller/blob/develop/COPYING.txt |

Godot Engine: MIT-Lizenz, Hinweise sind in der exportierten EXE enthalten.

## 5. Status

- Bestätigt: offizielle Modellpaket-Webseite weist CC0 aus.
- Dokumentiert: Lizenzdateien für Python, NumPy, OpenCV, ReportLab im Repo.
- Dokumentiert: Online-Lizenzlinks für Tcl/Tk, Pillow, PyInstaller.
- Dokumentiert: Custom-Lizenz für den eigenen Code in `LICENSE`.
- Offen: abschließende Rechteprüfung der Beispielmedien.
- Offen: Prüfung, ob PyInstaller beim Build automatisch Lizenzdateien in
  `_internal` ablegt; falls ja, sind diese im Release-ZIP enthalten.
