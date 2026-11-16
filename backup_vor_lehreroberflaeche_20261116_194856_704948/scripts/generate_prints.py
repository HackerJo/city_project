#!/usr/bin/env python3
"""Generate the print templates (PDF) and the data files for scanner and viewer.

    python scripts/generate_prints.py

Reads  settings/settings.csv and settings/buildings.csv
Writes output/print/grid_sheet.pdf, output/print/cards.pdf,
       output/layout.json, output/buildings.json
       and copies buildings.json to cityviewer/data/ (for the Godot viewer).

Dependencies: pip install opencv-contrib-python reportlab numpy
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
from pathlib import Path

from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas

from i18n import t
from paths import project_root
from settings_loader import (A4_PORTRAIT_MM, CARD_SHEET_MARGIN_MM, Project, SettingsError, load_project,
                             print_messages)

CARD_GAP_MM = 2.0
FONT = "Helvetica"


def marker_cells(project: Project, marker_id: int) -> list:
    """Return the marker as a square matrix of 0/1 (1 = black), including the black border."""
    s = project.settings
    side = s.dict_bits + 2
    try:
        import cv2
        dictionary = cv2.aruco.getPredefinedDictionary(getattr(cv2.aruco, s.aruco_dict))
        if hasattr(cv2.aruco, "generateImageMarker"):
            img = cv2.aruco.generateImageMarker(dictionary, marker_id, side)
        else:
            img = cv2.aruco.drawMarker(dictionary, marker_id, side)
        return [[1 if img[r][c] < 128 else 0 for c in range(side)] for r in range(side)]
    except ImportError:
        if os.environ.get("CITY_DUMMY_MARKERS") != "1":
            sys.exit(t("opencv_missing"))
        rng = random.Random(marker_id)
        inner = [[rng.randint(0, 1) for _ in range(side)] for _ in range(side)]
        return [[1 if r in (0, side - 1) or c in (0, side - 1) else inner[r][c] for c in range(side)]
                for r in range(side)]


def rect(c, page_h, x, y, w, h, fill=0, stroke=1):
    c.rect(x * mm, (page_h - y - h) * mm, w * mm, h * mm, stroke=stroke, fill=fill)


def line(c, page_h, x1, y1, x2, y2):
    c.line(x1 * mm, (page_h - y1) * mm, x2 * mm, (page_h - y2) * mm)


def triangle_up(c, page_h, cx, top, width, height):
    p = c.beginPath()
    p.moveTo(cx * mm, (page_h - top) * mm)
    p.lineTo((cx - width / 2) * mm, (page_h - top - height) * mm)
    p.lineTo((cx + width / 2) * mm, (page_h - top - height) * mm)
    p.close()
    c.drawPath(p, stroke=0, fill=1)


def text_centered(c, page_h, cx, baseline, text, size_pt, max_width_mm=None):
    while max_width_mm and stringWidth(text, FONT, size_pt) > max_width_mm * mm and size_pt > 4:
        size_pt -= 0.5
    c.setFont(FONT, size_pt)
    c.drawCentredString(cx * mm, (page_h - baseline) * mm, text)


def draw_marker(c, page_h, x, y, size, cells):
    n = len(cells)
    cell = size / n
    c.setFillColorRGB(0, 0, 0)
    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(0.1)
    for r in range(n):
        for col in range(n):
            if cells[r][col]:
                rect(c, page_h, x + col * cell, y + r * cell, cell, cell, fill=1, stroke=1)


def column_label(i: int) -> str:
    label = ""
    i += 1
    while i:
        i, rem = divmod(i - 1, 26)
        label = chr(65 + rem) + label
    return label


def grid_geometry(project: Project):
    s = project.settings
    grid_w, grid_h = s.columns * s.field_mm, s.rows * s.field_mm
    gx, gy = (s.paper_w_mm - grid_w) / 2, (s.paper_h_mm - grid_h) / 2
    o = s.corner_offset_mm + s.corner_marker_mm / 2
    corners = {
        s.corner_ids[0]: (o, o),
        s.corner_ids[1]: (s.paper_w_mm - o, o),
        s.corner_ids[2]: (s.paper_w_mm - o, s.paper_h_mm - o),
        s.corner_ids[3]: (o, s.paper_h_mm - o),
    }
    return gx, gy, grid_w, grid_h, corners


def make_grid_sheet(project: Project, path: Path) -> None:
    s = project.settings
    W, H = s.paper_w_mm, s.paper_h_mm
    gx, gy, gw, gh, corners = grid_geometry(project)
    c = canvas.Canvas(str(path), pagesize=(W * mm, H * mm))
    c.setTitle(t("sheet_title"))
    c.setStrokeColorRGB(0.6, 0.6, 0.6)
    c.setLineWidth(0.5)
    for i in range(s.columns + 1):
        line(c, H, gx + i * s.field_mm, gy, gx + i * s.field_mm, gy + gh)
    for j in range(s.rows + 1):
        line(c, H, gx, gy + j * s.field_mm, gx + gw, gy + j * s.field_mm)
    c.setFillColorRGB(0.45, 0.45, 0.45)
    for i in range(s.columns):
        text_centered(c, H, gx + (i + 0.5) * s.field_mm, gy - 2.5, column_label(i), 9)
    for j in range(s.rows):
        text_centered(c, H, gx - 4, gy + (j + 0.5) * s.field_mm + 1.2, str(j + 1), 9)
    for marker_id, (cx, cy) in corners.items():
        size = s.corner_marker_mm
        draw_marker(c, H, cx - size / 2, cy - size / 2, size, marker_cells(project, marker_id))
    c.setFillColorRGB(0.45, 0.45, 0.45)
    text_centered(c, H, W / 2, H - 6, t("print_hint"), 8)
    c.showPage()
    c.save()


def draw_card(project: Project, c, page_h, x, y, b) -> None:
    s = project.settings
    w, h = b.width * s.field_mm, b.depth * s.field_mm
    c.setStrokeColorRGB(0.5, 0.5, 0.5)
    c.setLineWidth(0.3)
    rect(c, page_h, x, y, w, h, fill=0, stroke=1)

    free_h = h - 2 * s.card_margin_mm - s.card_arrow_mm - s.card_name_mm - 2 * s.quiet_zone_mm
    free_w = w - 2 * s.card_margin_mm - 2 * s.quiet_zone_mm
    size = min(free_h, free_w)
    cx = x + w / 2
    c.setFillColorRGB(0, 0, 0)
    triangle_up(c, page_h, cx, y + s.card_margin_mm, s.card_arrow_mm + 0.8, s.card_arrow_mm)
    marker_top = y + s.card_margin_mm + s.card_arrow_mm + s.quiet_zone_mm + (free_h - size) / 2
    draw_marker(c, page_h, cx - size / 2, marker_top, size, marker_cells(project, b.id))
    text_centered(c, page_h, cx, y + h - s.card_margin_mm - 0.6, b.name(s.language),
                  s.card_name_mm * 2.83 * 0.85, max_width_mm=w - 2 * s.card_margin_mm)


def make_cards(project: Project, path: Path):
    s = project.settings
    page_w, page_h = A4_PORTRAIT_MM
    items = []
    for b in project.buildings:
        if b.active and b.count > 0:
            items += [b] * b.count
    items.sort(key=lambda b: -b.depth)
    pages, current, x, y, row_h = [], [], CARD_SHEET_MARGIN_MM, CARD_SHEET_MARGIN_MM, 0.0
    limit_x, limit_y = page_w - CARD_SHEET_MARGIN_MM, page_h - CARD_SHEET_MARGIN_MM - 4
    for b in items:
        cw, ch = b.width * s.field_mm, b.depth * s.field_mm
        if x + cw > limit_x:
            x, y, row_h = CARD_SHEET_MARGIN_MM, y + row_h + CARD_GAP_MM, 0.0
        if y + ch > limit_y:
            pages.append(current)
            current, x, y, row_h = [], CARD_SHEET_MARGIN_MM, CARD_SHEET_MARGIN_MM, 0.0
        current.append((b, x, y))
        x += cw + CARD_GAP_MM
        row_h = max(row_h, ch)
    if current:
        pages.append(current)

    c = canvas.Canvas(str(path), pagesize=(page_w * mm, page_h * mm))
    c.setTitle(t("cards_title"))
    for page in pages:
        for b, px, py in page:
            draw_card(project, c, page_h, px, py, b)
        c.setFillColorRGB(0.45, 0.45, 0.45)
        text_centered(c, page_h, page_w / 2, page_h - 4, t("print_hint"), 7)
        c.showPage()
    c.save()
    return len(items), len(pages)


def write_data_files(project: Project, out_dir: Path) -> None:
    s = project.settings
    gx, gy, gw, gh, corners = grid_geometry(project)
    layout = {
        "paper": s.paper,
        "paper_mm": {"width": s.paper_w_mm, "height": s.paper_h_mm},
        "field_mm": s.field_mm,
        "columns": s.columns,
        "rows": s.rows,
        "grid_origin_mm": {"x": gx, "y": gy},
        "aruco_dict": s.aruco_dict,
        "corner_markers_mm": {str(k): {"x": v[0], "y": v[1]} for k, v in corners.items()},
        "convention": "marker top edge = door side; empty field = path; outside grid = meadow",
    }
    (out_dir / "layout.json").write_text(json.dumps(layout, indent=2, ensure_ascii=False), encoding="utf-8")

    catalog = {
        "language": s.language,
        "world_meters_per_field": s.world_meters_per_field,
        "start_view": s.start_view,
        "path_color": s.path_color,
        "meadow_color": s.meadow_color,
        "buildings": [
            {"id": b.id, "key": b.key, "name": b.name(s.language), "name_de": b.name_de, "name_en": b.name_en,
             "width": b.width, "depth": b.depth, "model": b.model, "color": b.color, "height_m": b.height_m, "floors": b.floors, "style": b.style}
            for b in project.buildings if b.active
        ],
    }
    data = json.dumps(catalog, indent=2, ensure_ascii=False)
    (out_dir / "buildings.json").write_text(data, encoding="utf-8")
    viewer_data = project.root / "cityviewer" / "data"
    if viewer_data.exists():
        (viewer_data / "buildings.json").write_text(data, encoding="utf-8")


def generate(project: Project) -> Path:
    out_dir = project.root / "output"
    print_dir = out_dir / "print"
    print_dir.mkdir(parents=True, exist_ok=True)
    make_grid_sheet(project, print_dir / "grid_sheet.pdf")
    cards, pages = make_cards(project, print_dir / "cards.pdf")
    write_data_files(project, out_dir)
    print(t("cards_summary", cards=cards, pages=pages))
    return print_dir


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=project_root(), help="project folder")
    args = parser.parse_args()
    try:
        project = load_project(args.root)
    except SettingsError as e:
        print_messages(e.messages)
        return 1
    print_messages(project.messages)
    if os.environ.get("CITY_DUMMY_MARKERS") == "1":
        print(t("dummy_markers"))
    print(t("done_prints", path=generate(project)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
