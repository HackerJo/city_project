#!/usr/bin/env python3
"""Detect the building cards on a photo of the grid sheet and write scanresult/city.json.

    python scripts/detect_city.py --image photo.jpg

Needs output/layout.json and output/buildings.json (created by generate_prints.py).

Three passes: (1) original photo -> corner markers give the homography,
(2) rectified top-down image, (3) rectified image with contrast equalisation (CLAHE).
The same ID may appear several times (e.g. several houses); detections of the same ID that are
closer than DUPLICATE_MM are treated as one marker.

Writes to scanresult/: city.json, control.jpg (photo with detections),
rectified.jpg (annotated top view), rectified_raw.jpg (top view without annotations).
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import cv2
import numpy as np

from i18n import set_language, t
from paths import project_root

PX_PER_MM = 6        # resolution of the rectified image
DUPLICATE_MM = 8     # same ID closer than this = same marker


def read_image(path: Path):
    data = np.fromfile(str(path), dtype=np.uint8)  # works with umlauts in the path
    image = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if image is None:
        sys.exit(t("image_unreadable", path=path))
    return image


def detect_markers(image, dict_name: str):
    """Return (detections, rejected). detections: list of (id, 4x2 array in pixels)."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image
    dictionary = cv2.aruco.getPredefinedDictionary(getattr(cv2.aruco, dict_name))
    new_api = hasattr(cv2.aruco, "ArucoDetector")
    params = cv2.aruco.DetectorParameters() if new_api else cv2.aruco.DetectorParameters_create()
    params.adaptiveThreshWinSizeMin = 3
    params.adaptiveThreshWinSizeMax = 63
    params.adaptiveThreshWinSizeStep = 6
    params.minMarkerPerimeterRate = 0.01
    params.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX
    params.perspectiveRemovePixelPerCell = 8
    params.perspectiveRemoveIgnoredMarginPerCell = 0.2
    if new_api:
        corners, ids, rejected = cv2.aruco.ArucoDetector(dictionary, params).detectMarkers(gray)
    else:
        corners, ids, rejected = cv2.aruco.detectMarkers(gray, dictionary, parameters=params)
    found = [] if ids is None else [(int(i), c.reshape(4, 2)) for i, c in zip(ids.flatten(), corners)]
    return found, [r.reshape(4, 2) for r in rejected]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--image", required=True, type=Path)
    parser.add_argument("--root", type=Path, default=project_root())
    parser.add_argument("--out", type=Path, default=None, help="default: <root>/scanresult")
    args = parser.parse_args()
    root = args.root
    out_dir = args.out or root / "scanresult"
    out_dir.mkdir(parents=True, exist_ok=True)

    layout = json.loads((root / "output" / "layout.json").read_text(encoding="utf-8"))
    catalog_file = json.loads((root / "output" / "buildings.json").read_text(encoding="utf-8"))
    set_language(catalog_file.get("language", "de"))
    catalog = {b["id"]: b for b in catalog_file["buildings"]}

    field = layout["field_mm"]
    gx, gy = layout["grid_origin_mm"]["x"], layout["grid_origin_mm"]["y"]
    columns, rows = layout["columns"], layout["rows"]
    corner_target = {int(k): (v["x"], v["y"]) for k, v in layout["corner_markers_mm"].items()}
    warnings: list[str] = []

    image = read_image(args.image)

    found1, _ = detect_markers(image, layout["aruco_dict"])
    corners_px = {}
    for marker_id, c in found1:
        if marker_id in corner_target and marker_id not in corners_px:
            corners_px[marker_id] = c
    missing = [i for i in corner_target if i not in corners_px]
    if missing:
        sys.exit(t("corner_missing", ids=missing))
    src = np.array([corners_px[i].mean(axis=0) for i in corner_target], dtype=np.float32)
    dst = np.array([corner_target[i] for i in corner_target], dtype=np.float32)
    H, _ = cv2.findHomography(src, dst)
    H_inv = np.linalg.inv(H)

    def px_to_mm(points):
        p = np.array(points, dtype=np.float32).reshape(-1, 1, 2)
        return cv2.perspectiveTransform(p, H).reshape(-1, 2)

    def mm_to_px(points):
        p = np.array(points, dtype=np.float32).reshape(-1, 1, 2)
        return cv2.perspectiveTransform(p, H_inv).reshape(-1, 2)

    scale = np.diag([PX_PER_MM, PX_PER_MM, 1.0])
    size = (int(layout["paper_mm"]["width"] * PX_PER_MM), int(layout["paper_mm"]["height"] * PX_PER_MM))
    warped = cv2.warpPerspective(image, scale @ H, size, flags=cv2.INTER_CUBIC)

    found2, rejected2 = detect_markers(warped, layout["aruco_dict"])
    gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
    found3, _ = detect_markers(cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8)).apply(gray), layout["aruco_dict"])

    merged = []  # (id, corners_mm, pass_number); priority 2 > 3 > 1
    for number, found, to_mm in ((2, found2, lambda c: c / PX_PER_MM), (3, found3, lambda c: c / PX_PER_MM), (1, found1, px_to_mm)):
        for marker_id, c in found:
            mm_corners = to_mm(c)
            centre = mm_corners.mean(axis=0)
            if any(m == marker_id and np.linalg.norm(o.mean(axis=0) - centre) < DUPLICATE_MM for m, o, _ in merged):
                continue
            merged.append((marker_id, mm_corners, number))
    for number, found in ((1, found1), (2, found2), (3, found3)):
        count = sum(1 for i, _ in found if i not in corner_target)
        print(t("pass_summary", n=number, count=count))

    result, occupied = [], {}
    for marker_id, mm_corners, number in merged:
        if marker_id in corner_target:
            continue
        info = catalog.get(marker_id)
        if info is None:
            warnings.append(t("unknown_marker", id=marker_id))
            continue
        centre = mm_corners.mean(axis=0)
        top = mm_corners[1] - mm_corners[0]  # marker top edge = door side
        rotation = int(round(math.degrees(math.atan2(top[1], top[0])) / 90.0)) * 90 % 360
        door = {0: "N", 90: "E", 180: "S", 270: "W"}[rotation]
        width, depth = info["width"], info["depth"]
        if rotation in (90, 270):
            width, depth = depth, width
        col = int(math.floor((centre[0] - width * field / 2 - gx) / field + 0.5))
        row = int(math.floor((centre[1] - depth * field / 2 - gy) / field + 0.5))
        entry = {"id": marker_id, "key": info["key"], "name": info["name"], "col": col, "row": row,
                 "width_fields": width, "depth_fields": depth, "rotation": rotation, "door": door, "pass": number}
        if col < 0 or row < 0 or col + width > columns or row + depth > rows:
            warnings.append(t("outside_grid", name=info["name"], id=marker_id))
        for dc in range(width):
            for dr in range(depth):
                cell = (col + dc, row + dr)
                if cell in occupied:
                    label = f"{chr(65 + cell[0]) if 0 <= cell[0] < 26 else cell[0]}{cell[1] + 1}"
                    warnings.append(t("overlap", cell=label, a=info["name"], b=occupied[cell]))
                occupied[cell] = info["name"]
        result.append(entry)

    city = {"grid": {"columns": columns, "rows": rows, "field_mm": field},
            "buildings": sorted(result, key=lambda e: (e["row"], e["col"])),
            "warnings": warnings}
    (out_dir / "city.json").write_text(json.dumps(city, indent=2, ensure_ascii=False), encoding="utf-8")

    def label(marker_id):
        if marker_id in corner_target:
            return f"{marker_id} corner"
        return f"{marker_id} {catalog[marker_id]['key']}" if marker_id in catalog else f"{marker_id} ?"

    control, top_view = image.copy(), warped.copy()
    for r in rejected2:
        cv2.polylines(top_view, [r.astype(int)], True, (0, 140, 255), 2)
    for marker_id, mm_corners, _ in merged:
        px = mm_to_px(mm_corners).astype(int)
        pw = (mm_corners * PX_PER_MM).astype(int)
        cv2.polylines(control, [px], True, (0, 200, 0), 3)
        cv2.putText(control, label(marker_id), (int(px[0][0]), int(px[0][1])), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
        cv2.polylines(top_view, [pw], True, (0, 200, 0), 3)
        cv2.putText(top_view, label(marker_id), (int(pw[0][0]), int(pw[0][1]) - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
    cv2.imwrite(str(out_dir / "control.jpg"), control)
    cv2.imwrite(str(out_dir / "rectified.jpg"), top_view)
    cv2.imwrite(str(out_dir / "rectified_raw.jpg"), warped)

    print(t("detected_count", count=len(result)))
    for message in warnings:
        print("WARNING:", message)
    return 0


if __name__ == "__main__":
    sys.exit(main())
