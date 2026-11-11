"""Minimal translation helper. Code and file formats are English; messages can be de or en."""

MESSAGES = {
    "de": {
        "file_missing": "Datei nicht gefunden: {path}",
        "unknown_setting": "settings.csv: Unbekannte Einstellung '{key}' wird ignoriert.",
        "bad_number": "settings.csv: '{key}' = '{value}' ist keine gültige Zahl.",
        "bad_choice": "settings.csv: '{key}' = '{value}' ist nicht erlaubt. Erlaubt: {allowed}.",
        "bad_color": "{where}: '{value}' ist keine gültige Farbe (Format #rrggbb).",
        "bad_ids": "settings.csv: 'corner_marker_ids' muss genau 4 verschiedene Zahlen enthalten.",
        "bad_dict": "settings.csv: 'aruco_dict' = '{value}' ist kein gültiges Wörterbuch (z. B. DICT_4X4_50).",
        "grid_not_fit": "Das Raster ({columns}x{rows} Felder à {field} mm) passt nicht auf {paper}. Maximal möglich: {max_cols}x{max_rows}.",
        "grid_zero": "Mit dieser Feldgröße passt kein Raster auf das Papier. Feldgröße verkleinern oder A3 wählen.",
        "row_error": "buildings.csv, Zeile {line} ({key}): {problem}",
        "p_missing_key": "Spalte 'key' ist leer.",
        "p_bad_key": "'key' darf nur Kleinbuchstaben, Ziffern und _ enthalten.",
        "p_bad_int": "Spalte '{field}' braucht eine ganze Zahl ab {minimum}.",
        "p_bad_float": "Spalte '{field}' braucht eine Zahl ab 0.",
        "p_dup_id": "ID {id} kommt mehrfach vor.",
        "p_dup_key": "key '{key}' kommt mehrfach vor.",
        "p_id_range": "ID {id} liegt außerhalb des erlaubten Bereichs 1-{max_id} des Wörterbuchs.",
        "p_id_corner": "ID {id} ist für die Eckmarker reserviert.",
        "p_bad_active": "Spalte 'active' braucht yes/no (oder ja/nein).",
        "p_missing_name": "Mindestens 'name_de' oder 'name_en' muss ausgefüllt sein.",
        "no_buildings": "buildings.csv enthält keine aktiven Gebäude.",
        "ids_assigned": "{count} fehlende ID(s) wurden automatisch vergeben und in buildings.csv gespeichert.",
        "ids_not_saved": "Neue IDs konnten nicht in buildings.csv gespeichert werden (Datei in Excel geöffnet?). Bitte Datei schließen und erneut starten.",
        "marker_small": "{name}: Der Marker ist nur {size:.1f} mm groß (empfohlen: mind. {minimum:g} mm). Feldgröße erhöhen.",
        "marker_too_small": "{name}: Das Kärtchen ist zu klein für einen Marker. Feldgröße erhöhen.",
        "card_too_big": "{name}: Das Kärtchen ({w:g}x{h:g} mm) passt nicht auf eine A4-Seite.",
        "models_missing": "Noch kein 3D-Modell für: {keys}. Der Viewer zeigt dafür beschriftete Blöcke.",
        "print_hint": "Mit 100 % drucken (nicht 'An Seite anpassen').",
        "sheet_title": "Rasterblatt",
        "cards_title": "Kärtchen",
        "done_prints": "Druckvorlagen erstellt in: {path}",
        "cards_summary": "{cards} Kärtchen auf {pages} Seite(n).",
        "dummy_markers": "WARNUNG: Testmarker ohne OpenCV - nicht zum Drucken geeignet!",
        "opencv_missing": "OpenCV fehlt. Installation: pip install opencv-contrib-python",
        "image_unreadable": "Bild nicht lesbar: {path}",
        "corner_missing": "Eckmarker nicht gefunden: {ids}. Blatt komplett und scharf fotografieren.",
        "unknown_marker": "Unbekannter Marker mit ID {id}.",
        "outside_grid": "{name} (ID {id}) liegt außerhalb des Rasters.",
        "overlap": "Überlappung bei Feld {cell}: {a} und {b}.",
        "pass_summary": "Durchgang {n}: {count} Gebäude",
        "detected_count": "{count} Gebäude erkannt.",
    },
    "en": {
        "file_missing": "File not found: {path}",
        "unknown_setting": "settings.csv: unknown setting '{key}' is ignored.",
        "bad_number": "settings.csv: '{key}' = '{value}' is not a valid number.",
        "bad_choice": "settings.csv: '{key}' = '{value}' is not allowed. Allowed: {allowed}.",
        "bad_color": "{where}: '{value}' is not a valid colour (format #rrggbb).",
        "bad_ids": "settings.csv: 'corner_marker_ids' must contain exactly 4 different numbers.",
        "bad_dict": "settings.csv: 'aruco_dict' = '{value}' is not a valid dictionary (e.g. DICT_4X4_50).",
        "grid_not_fit": "The grid ({columns}x{rows} fields of {field} mm) does not fit on {paper}. Maximum: {max_cols}x{max_rows}.",
        "grid_zero": "No grid fits on the paper with this field size. Reduce the field size or choose A3.",
        "row_error": "buildings.csv, line {line} ({key}): {problem}",
        "p_missing_key": "Column 'key' is empty.",
        "p_bad_key": "'key' may only contain lowercase letters, digits and _.",
        "p_bad_int": "Column '{field}' needs a whole number >= {minimum}.",
        "p_bad_float": "Column '{field}' needs a number >= 0.",
        "p_dup_id": "ID {id} appears more than once.",
        "p_dup_key": "key '{key}' appears more than once.",
        "p_id_range": "ID {id} is outside the dictionary range 1-{max_id}.",
        "p_id_corner": "ID {id} is reserved for the corner markers.",
        "p_bad_active": "Column 'active' needs yes/no (or ja/nein).",
        "p_missing_name": "At least 'name_de' or 'name_en' must be filled in.",
        "no_buildings": "buildings.csv contains no active buildings.",
        "ids_assigned": "{count} missing ID(s) were assigned automatically and saved to buildings.csv.",
        "ids_not_saved": "New IDs could not be saved to buildings.csv (file open in Excel?). Close it and run again.",
        "marker_small": "{name}: the marker is only {size:.1f} mm (recommended: at least {minimum:g} mm). Increase the field size.",
        "marker_too_small": "{name}: the card is too small for a marker. Increase the field size.",
        "card_too_big": "{name}: the card ({w:g}x{h:g} mm) does not fit on an A4 page.",
        "models_missing": "No 3D model yet for: {keys}. The viewer shows labelled blocks instead.",
        "print_hint": "Print at 100 % (not 'fit to page').",
        "sheet_title": "Grid sheet",
        "cards_title": "Cards",
        "done_prints": "Print templates created in: {path}",
        "cards_summary": "{cards} cards on {pages} page(s).",
        "dummy_markers": "WARNING: test markers without OpenCV - not suitable for printing!",
        "opencv_missing": "OpenCV is missing. Install: pip install opencv-contrib-python",
        "image_unreadable": "Cannot read image: {path}",
        "corner_missing": "Corner markers not found: {ids}. Photograph the whole sheet in focus.",
        "unknown_marker": "Unknown marker with ID {id}.",
        "outside_grid": "{name} (ID {id}) is outside the grid.",
        "overlap": "Overlap at field {cell}: {a} and {b}.",
        "pass_summary": "Pass {n}: {count} buildings",
        "detected_count": "{count} buildings detected.",
    },
}

_language = "de"


def set_language(lang: str) -> None:
    global _language
    _language = lang if lang in MESSAGES else "de"


def get_language() -> str:
    return _language


def t(message_id: str, /, **kwargs) -> str:
    template = MESSAGES.get(_language, MESSAGES["de"]).get(message_id) or MESSAGES["en"].get(message_id) or message_id
    try:
        return template.format(**kwargs)
    except (KeyError, IndexError, ValueError):
        return template
