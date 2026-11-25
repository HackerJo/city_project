#!/usr/bin/env python3
"""Wendet die Patches für custom paper und Eckmarker auf cards.pdf an.

    python scripts/apply_patches.py

Erstellt Backups: settings_loader.py.bak, generate_prints.py.bak
"""
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parent.parent
LOADER = ROOT / "scripts" / "settings_loader.py"
PRINTS = ROOT / "scripts" / "generate_prints.py"


def patch_loader(text: str) -> str:
    # 1) DEFAULTS ergänzen
    old = '"language": "de", "paper": "A3", "field_size_mm": "30", "columns": "auto", "rows": "auto",'
    new = ('"language": "de", "paper": "A3", "paper_w_mm": "740", "paper_h_mm": "520", '
           '"field_size_mm": "30", "columns": "auto", "rows": "auto",')
    if old not in text:
        print("WARNUNG: DEFAULTS-Zeile nicht gefunden – evtl. bereits gepatcht.")
    else:
        text = text.replace(old, new)

    # 2) paper-Auswahl ersetzen
    old2 = ('    paper = _choice(values["paper"], "paper", list(PAPERS_MM), messages, "A3")\n'
            '    paper_w, paper_h = PAPERS_MM[paper]')
    new2 = ('    paper = _choice(values["paper"], "paper", list(PAPERS_MM) + ["custom"], messages, "A3")\n'
            '    if paper == "custom":\n'
            '        paper_w = _num(values["paper_w_mm"], "paper_w_mm", messages, 740.0)\n'
            '        paper_h = _num(values["paper_h_mm"], "paper_h_mm", messages, 520.0)\n'
            '    else:\n'
            '        paper_w, paper_h = PAPERS_MM[paper]')
    if old2 not in text:
        print("WARNUNG: paper-Auswahl nicht gefunden – evtl. bereits gepatcht.")
    else:
        text = text.replace(old2, new2)
    return text


def patch_prints(text: str) -> str:
    # Neue Funktion einfügen (vor def main)
    func = '''

def draw_corner_marker_cutouts(project: Project, c, page_h) -> None:
    """Draw the four corner markers as separate cut-outs on the last card page."""
    s = project.settings
    size = s.corner_marker_mm
    labels = {s.corner_ids[0]: "OL (oben links)", s.corner_ids[1]: "OR (oben rechts)",
              s.corner_ids[2]: "UR (unten rechts)", s.corner_ids[3]: "UL (unten links)"}
    x = CARD_SHEET_MARGIN_MM
    y = page_h - CARD_SHEET_MARGIN_MM - size - 6
    for marker_id in s.corner_ids:
        draw_marker(c, page_h, x, y, size, marker_cells(project, marker_id))
        c.setFillColorRGB(0.45, 0.45, 0.45)
        text_centered(c, page_h, x + size / 2, y + size + 2, labels[marker_id], 6)
        x += size + 8

'''
    if "draw_corner_marker_cutouts" in text:
        print("WARNUNG: draw_corner_marker_cutouts bereits vorhanden.")
    else:
        text = text.replace("def main() -> int:", func + "\ndef main() -> int:")

    # In make_cards: nach der letzten Seite die Eckmarker zeichnen
    old_loop = "    if current:\n        pages.append(current)\n\n    c = canvas.Canvas"
    new_loop = ("    if current:\n        pages.append(current)\n\n"
                "    c = canvas.Canvas")
    if old_loop in text:
        text = text.replace(old_loop, new_loop)
    # Eckmarker-Aufruf vor dem letzten showPage einfügen
    old_show = "        c.showPage()\n    c.save()"
    new_show = ("        if page is pages[-1]:\n"
                "            draw_corner_marker_cutouts(project, c, page_h)\n"
                "        c.showPage()\n    c.save()")
    if old_show in text:
        text = text.replace(old_show, new_show)
    else:
        print("WARNUNG: showPage-Stelle nicht gefunden – bitte manuell prüfen.")
    return text


def main() -> int:
    for path in (LOADER, PRINTS):
        if not path.exists():
            print(f"FEHLER: {path} nicht gefunden.")
            return 1
        backup = path.with_suffix(path.suffix + ".bak")
        shutil.copy2(path, backup)
        text = path.read_text(encoding="utf-8")
        if path == LOADER:
            text = patch_loader(text)
        else:
            text = patch_prints(text)
        path.write_text(text, encoding="utf-8")
        print(f"OK: {path.name} gepatcht (Backup: {backup.name})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
