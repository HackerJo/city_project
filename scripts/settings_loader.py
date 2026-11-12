"""Read and validate settings/settings.csv and settings/buildings.csv.

Both files may be saved by Excel (semicolon or comma, UTF-8 or Windows-1252).
Missing building IDs are assigned automatically and written back.
"""
from __future__ import annotations

import csv
import re
from dataclasses import dataclass, field
from pathlib import Path

from i18n import set_language, t
from paths import project_root

PAPERS_MM = {"A3": (420.0, 297.0), "A4": (297.0, 210.0)}  # landscape (width, height)
A4_PORTRAIT_MM = (210.0, 297.0)
CARD_SHEET_MARGIN_MM = 8.0
COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")
KEY_RE = re.compile(r"^[a-z0-9_]+$")

DEFAULTS = {
    "language": "de", "paper": "A3", "field_size_mm": "30", "columns": "auto", "rows": "auto",
    "world_meters_per_field": "6", "start_view": "walk", "path_color": "#b8a58a",
    "meadow_color": "#5a9a4d", "min_marker_mm": "15", "sheet_border_mm": "28",
    "corner_marker_mm": "20", "corner_offset_mm": "4", "corner_marker_ids": "46,47,48,49",
    "aruco_dict": "DICT_4X4_50", "card_margin_mm": "1.5", "card_arrow_mm": "3",
    "card_name_mm": "3", "card_quiet_zone_mm": "2.5",
}


@dataclass
class Message:
    level: str  # "error" | "warning" | "info"
    text: str


class SettingsError(Exception):
    def __init__(self, messages: list[Message]):
        self.messages = messages
        super().__init__("\n".join(m.text for m in messages))


@dataclass
class Settings:
    language: str
    paper: str
    paper_w_mm: float
    paper_h_mm: float
    field_mm: float
    columns: int
    rows: int
    world_meters_per_field: float
    start_view: str
    path_color: str
    meadow_color: str
    min_marker_mm: float
    sheet_border_mm: float
    corner_marker_mm: float
    corner_offset_mm: float
    corner_ids: tuple
    aruco_dict: str
    card_margin_mm: float
    card_arrow_mm: float
    card_name_mm: float
    quiet_zone_mm: float

    @property
    def dict_size(self) -> int:
        return int(self.aruco_dict.rsplit("_", 1)[1])

    @property
    def dict_bits(self) -> int:
        return int(re.match(r"DICT_(\d)X\d_", self.aruco_dict).group(1))


@dataclass
class Building:
    id: int
    key: str
    name_de: str
    name_en: str
    width: int
    depth: int
    model: str
    color: str
    height_m: float
    count: int
    active: bool
    floors: int = 1
    style: str = "block"

    def name(self, lang: str) -> str:
        primary, other = (self.name_de, self.name_en) if lang == "de" else (self.name_en, self.name_de)
        return primary or other or self.key


@dataclass
class Table:
    rows: list
    fieldnames: list
    delimiter: str


@dataclass
class Project:
    root: Path
    settings: Settings
    buildings: list
    messages: list = field(default_factory=list)


def read_table(path: Path) -> Table:
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw.decode("cp1252")
    lines = text.splitlines()
    first = lines[0] if lines else ""
    delimiter = max((";", ",", "\t"), key=first.count)
    reader = csv.DictReader(lines, delimiter=delimiter)
    rows = []
    for r in reader:
        clean = {(k or "").strip().lower(): (v or "").strip() for k, v in r.items()
                 if k is not None and not isinstance(v, list)}
        if any(clean.values()):
            rows.append(clean)
    return Table(rows, [f.strip() for f in (reader.fieldnames or [])], delimiter)


def write_table(path: Path, table: Table, rows: list) -> None:
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f, delimiter=table.delimiter)
        writer.writerow(table.fieldnames)
        for row in rows:
            writer.writerow([row.get(n.lower(), "") for n in table.fieldnames])


def _num(value: str, key: str, messages: list, default: float) -> float:
    try:
        return float(value.replace(",", "."))
    except ValueError:
        messages.append(Message("error", t("bad_number", key=key, value=value)))
        return default


def _choice(value: str, key: str, allowed: list, messages: list, default: str) -> str:
    v = value.strip()
    for a in allowed:
        if v.lower() == a.lower():
            return a
    messages.append(Message("error", t("bad_choice", key=key, value=value, allowed=", ".join(allowed))))
    return default


def _color(value: str, where: str, messages: list, default: str) -> str:
    if COLOR_RE.match(value):
        return value.lower()
    messages.append(Message("error", t("bad_color", where=where, value=value)))
    return default


def load_settings(path: Path, messages: list) -> Settings:
    values = dict(DEFAULTS)
    if path.exists():
        for row in read_table(path).rows:
            key = row.get("key", "").strip().lower()
            if not key or key.startswith("#"):
                continue
            if key in DEFAULTS:
                values[key] = row.get("value", "").strip()
            else:
                messages.append(Message("warning", t("unknown_setting", key=key)))
    else:
        messages.append(Message("error", t("file_missing", path=path)))

    lang = values["language"].lower()
    set_language(lang if lang in ("de", "en") else "de")
    language = _choice(values["language"], "language", ["de", "en"], messages, "de")
    set_language(language)

    paper = _choice(values["paper"], "paper", list(PAPERS_MM), messages, "A3")
    paper_w, paper_h = PAPERS_MM[paper]
    field_mm = _num(values["field_size_mm"], "field_size_mm", messages, 30.0)
    border = _num(values["sheet_border_mm"], "sheet_border_mm", messages, 28.0)

    max_cols = max(int((paper_w - 2 * border) // field_mm), 0) if field_mm > 0 else 0
    max_rows = max(int((paper_h - 2 * border) // field_mm), 0) if field_mm > 0 else 0

    def grid_value(name: str, maximum: int) -> int:
        raw = values[name].strip().lower()
        if raw in ("", "auto"):
            return maximum
        return int(_num(raw, name, messages, float(maximum)))

    columns, rows = grid_value("columns", max_cols), grid_value("rows", max_rows)
    if max_cols < 1 or max_rows < 1:
        messages.append(Message("error", t("grid_zero")))
    elif columns > max_cols or rows > max_rows or columns < 1 or rows < 1:
        messages.append(Message("error", t("grid_not_fit", columns=columns, rows=rows, field=f"{field_mm:g}",
                                           paper=paper, max_cols=max_cols, max_rows=max_rows)))

    try:
        ids = tuple(int(x) for x in values["corner_marker_ids"].replace(";", ",").split(","))
        if len(set(ids)) != 4:
            raise ValueError
    except ValueError:
        messages.append(Message("error", t("bad_ids")))
        ids = (46, 47, 48, 49)

    aruco = values["aruco_dict"].strip().upper()
    if not re.match(r"^DICT_\dX\d_\d+$", aruco):
        messages.append(Message("error", t("bad_dict", value=values["aruco_dict"])))
        aruco = "DICT_4X4_50"

    return Settings(
        language=language, paper=paper, paper_w_mm=paper_w, paper_h_mm=paper_h, field_mm=field_mm,
        columns=columns, rows=rows,
        world_meters_per_field=_num(values["world_meters_per_field"], "world_meters_per_field", messages, 6.0),
        start_view=_choice(values["start_view"], "start_view", ["walk", "bird"], messages, "walk"),
        path_color=_color(values["path_color"], "settings.csv path_color", messages, "#b8a58a"),
        meadow_color=_color(values["meadow_color"], "settings.csv meadow_color", messages, "#5a9a4d"),
        min_marker_mm=_num(values["min_marker_mm"], "min_marker_mm", messages, 15.0),
        sheet_border_mm=border,
        corner_marker_mm=_num(values["corner_marker_mm"], "corner_marker_mm", messages, 20.0),
        corner_offset_mm=_num(values["corner_offset_mm"], "corner_offset_mm", messages, 4.0),
        corner_ids=ids, aruco_dict=aruco,
        card_margin_mm=_num(values["card_margin_mm"], "card_margin_mm", messages, 1.5),
        card_arrow_mm=_num(values["card_arrow_mm"], "card_arrow_mm", messages, 3.0),
        card_name_mm=_num(values["card_name_mm"], "card_name_mm", messages, 3.0),
        quiet_zone_mm=_num(values["card_quiet_zone_mm"], "card_quiet_zone_mm", messages, 2.5),
    )


def _to_int(value: str, minimum: int):
    try:
        number = float(value.replace(",", "."))
    except ValueError:
        return None
    n = int(number)
    return n if n == number and n >= minimum else None


def load_buildings(path: Path, s: Settings, messages: list) -> list:
    if not path.exists():
        messages.append(Message("error", t("file_missing", path=path)))
        return []
    table = read_table(path)
    buildings, seen_ids, seen_keys, pending = [], set(), set(), []
    max_id = s.dict_size - 1

    def err(line, key, problem):
        messages.append(Message("error", t("row_error", line=line, key=key or "?", problem=problem)))

    for line, r in enumerate(table.rows, start=2):
        key = r.get("key", "")
        if not key:
            err(line, key, t("p_missing_key")); continue
        if not KEY_RE.match(key):
            err(line, key, t("p_bad_key")); continue
        if key in seen_keys:
            err(line, key, t("p_dup_key", key=key)); continue
        seen_keys.add(key)
        problems = []
        width, depth = _to_int(r.get("width", ""), 1), _to_int(r.get("depth", ""), 1)
        count = _to_int(r.get("count", "1") or "1", 0)
        if width is None: problems.append(t("p_bad_int", field="width", minimum=1))
        if depth is None: problems.append(t("p_bad_int", field="depth", minimum=1))
        if count is None: problems.append(t("p_bad_int", field="count", minimum=0))
        floors = _to_int(r.get("floors", "1") or "1", 1)
        if floors is None:
            problems.append(t("p_bad_int", field="floors", minimum=1))
            floors = 1
        style = (r.get("style", "block") or "block").lower()
        if style not in ("block", "modular"):
            style = "block"
        try:
            height = float((r.get("height_m", "5") or "5").replace(",", "."))
            if height < 0: raise ValueError
        except ValueError:
            height = 5.0
            problems.append(t("p_bad_float", field="height_m"))
        active_raw = (r.get("active", "yes") or "yes").lower()
        if active_raw in ("yes", "ja", "true", "1", "y", "j"): active = True
        elif active_raw in ("no", "nein", "false", "0", "n"): active = False
        else:
            active = True; problems.append(t("p_bad_active"))
        color = r.get("color", "") or "#b0b0b0"
        if not COLOR_RE.match(color):
            problems.append(t("bad_color", where="color", value=color)); color = "#b0b0b0"
        if not r.get("name_de") and not r.get("name_en"):
            problems.append(t("p_missing_name"))
        bid = None
        raw_id = r.get("id", "")
        if raw_id:
            bid = _to_int(raw_id, 1)
            if bid is None: problems.append(t("p_bad_int", field="id", minimum=1))
            elif bid > max_id: problems.append(t("p_id_range", id=bid, max_id=max_id)); bid = None
            elif bid in s.corner_ids: problems.append(t("p_id_corner", id=bid)); bid = None
            elif bid in seen_ids: problems.append(t("p_dup_id", id=bid)); bid = None
            else: seen_ids.add(bid)
        for p in problems:
            err(line, key, p)
        if problems:
            continue
        b = Building(bid if bid is not None else -1, key, r.get("name_de", ""), r.get("name_en", ""),
                     width, depth, r.get("model", ""), color.lower(), height, count, active, floors, style)
        buildings.append(b)
        if bid is None:
            pending.append((b, r))

    if pending:
        next_id = 1
        for b, row in pending:
            while next_id in seen_ids or next_id in s.corner_ids:
                next_id += 1
            if next_id > max_id:
                messages.append(Message("error", t("p_id_range", id=next_id, max_id=max_id)))
                break
            b.id = next_id; row["id"] = str(next_id); seen_ids.add(next_id)
        try:
            write_table(path, table, table.rows)
            messages.append(Message("info", t("ids_assigned", count=len(pending))))
        except PermissionError:
            messages.append(Message("warning", t("ids_not_saved")))
    return buildings


def marker_size_mm(s: Settings, width_fields: int, depth_fields: int) -> float:
    """Size of the marker on a card (same geometry as the PDF generator)."""
    w, h = width_fields * s.field_mm, depth_fields * s.field_mm
    free_h = h - 2 * s.card_margin_mm - s.card_arrow_mm - s.card_name_mm - 2 * s.quiet_zone_mm
    free_w = w - 2 * s.card_margin_mm - 2 * s.quiet_zone_mm
    return min(free_h, free_w)


def validate_layout(s: Settings, buildings: list, root: Path, messages: list) -> None:
    active = [b for b in buildings if b.active]
    if not active:
        messages.append(Message("error", t("no_buildings")))
    page_w, page_h = A4_PORTRAIT_MM
    missing_models = []
    for b in active:
        name = b.name(s.language)
        card_w, card_h = b.width * s.field_mm, b.depth * s.field_mm
        if card_w > page_w - 2 * CARD_SHEET_MARGIN_MM or card_h > page_h - 2 * CARD_SHEET_MARGIN_MM:
            messages.append(Message("error", t("card_too_big", name=name, w=card_w, h=card_h)))
        size = marker_size_mm(s, b.width, b.depth)
        if size < 5:
            messages.append(Message("error", t("marker_too_small", name=name)))
        elif size < s.min_marker_mm and b.count > 0:
            messages.append(Message("warning", t("marker_small", name=name, size=size, minimum=s.min_marker_mm)))
        if not b.model or not (root / "cityviewer" / "models" / b.model).exists():
            missing_models.append(b.key)
    if missing_models:
        messages.append(Message("info", t("models_missing", keys=", ".join(missing_models))))


def load_project(root: Path | None = None) -> Project:
    """Load and validate everything. Raises SettingsError if any error was found."""
    root = root or project_root()
    messages: list[Message] = []
    settings = load_settings(root / "settings" / "settings.csv", messages)
    buildings = load_buildings(root / "settings" / "buildings.csv", settings, messages)
    validate_layout(settings, buildings, root, messages)
    project = Project(root, settings, buildings, messages)
    if any(m.level == "error" for m in messages):
        raise SettingsError(messages)
    return project


def print_messages(messages: list) -> None:
    labels = {"error": "ERROR", "warning": "WARNING", "info": "INFO"}
    for m in messages:
        print(f"[{labels[m.level]}] {m.text}")
