#!/usr/bin/env python3
"""Re-layout a demo city.json to the new 37x26 grid with new building sizes."""
import json, sys, csv
from pathlib import Path

COLS, ROWS = 37, 26

def load_sizes(csv_path):
    sizes = {}
    with open(csv_path, encoding='utf-8') as f:
        for row in csv.DictReader(f, delimiter=';'):
            sizes[row['key']] = (int(row['width']), int(row['depth']))
    return sizes

def relayout(old_city, sizes):
    items = sorted(old_city['buildings'],
                   key=lambda e: -(sizes.get(e['key'], (2,2))[0] * sizes.get(e['key'], (2,2))[1]))
    occupied, result = set(), []
    for e in items:
        w, d = sizes.get(e['key'], (2, 2))
        for r in range(ROWS - d + 1):
            for c in range(COLS - w + 1):
                cells = {(c+dc, r+dr) for dc in range(w) for dr in range(d)}
                if not (cells & occupied):
                    occupied |= cells
                    result.append({**e, 'col': c, 'row': r, 'width_fields': w, 'depth_fields': d})
                    break
            else:
                continue
            break
    return {'grid': {'columns': COLS, 'rows': ROWS, 'field_mm': 20.0},
            'buildings': sorted(result, key=lambda e: (e['row'], e['col'])),
            'warnings': []}

if __name__ == '__main__':
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    sizes = load_sizes(Path(sys.argv[3]) if len(sys.argv) > 3 else Path('settings/buildings.csv'))
    old = json.loads(src.read_text(encoding='utf-8'))
    new = relayout(old, sizes)
    dst.write_text(json.dumps(new, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"Relayout: {src} -> {dst} ({len(new['buildings'])} Gebäude)")
