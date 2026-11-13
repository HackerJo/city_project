#!/usr/bin/env python3
"""Patch cityviewer/scripts/main.gd so that the church is built by build_church (run once).

    python apply_patch_church.py
"""
import re
import sys
from pathlib import Path

root = Path(__file__).resolve().parent
path = root / "cityviewer" / "scripts" / "main.gd"
if not path.exists():
    sys.exit("not found: " + str(path))
text = path.read_text(encoding="utf-8")
if "build_church" in text:
    print("already patched:", path.name)
    sys.exit(0)

call = re.compile(
    r'(?P<i>[ \t]+)var built: Dictionary = builder\.build_house\(self, Vector2\(cx, cz\), lx, lz, floors, str\(entry\["door"\]\)\)\n'
    r'(?P<keep>[ \t]+var wall_top: float = built\["wall_top"\]\n[ \t]+var total_h: float = built\["height"\]\n)'
    r'[ \t]+_collider\(Vector3\(lx, wall_top, lz\), Vector3\(cx, wall_top / 2\.0, cz\)\)\n')


def new_call(m):
    i = m.group("i")
    return (
        f'{i}var built: Dictionary\n'
        f'{i}if str(entry["key"]) == "church":\n'
        f'{i}\tbuilt = builder.build_church(self, Vector2(cx, cz), lx, floors, str(entry["door"]))\n'
        f'{i}else:\n'
        f'{i}\tbuilt = builder.build_house(self, Vector2(cx, cz), lx, lz, floors, str(entry["door"]))\n'
        + m.group("keep") +
        f'{i}if built.has("colliders"):\n'
        f'{i}\tfor c in built["colliders"]:\n'
        f'{i}\t\t_collider(c["size"], c["pos"])\n'
        f'{i}else:\n'
        f'{i}\t_collider(Vector3(lx, wall_top, lz), Vector3(cx, wall_top / 2.0, cz))\n')


text, n1 = call.subn(new_call, text, count=1)

text, n2 = re.subn(r'(_add_labels\(Vector3\(cx, 0\.0, cz\), Vector3\(lx, total_h, lz\), label_text, wall_top)\)',
                   r'\1, float(built.get("wall_label_width", -1.0)))', text, count=1)

text, n3 = re.subn(r'func _add_labels\(centre: Vector3, size: Vector3, text: String, wall_height := -1\.0\) -> void:',
                   'func _add_labels(centre: Vector3, size: Vector3, text: String, wall_height := -1.0, wall_label_width := -1.0) -> void:',
                   text, count=1)

text, n4 = re.subn(r'([ \t]+)(var wall_h := size\.y if wall_height < 0\.0 else wall_height\n)',
                   lambda m: m.group(1) + m.group(2) + m.group(1) + 'var label_w := size.x if wall_label_width < 0.0 else wall_label_width\n',
                   text, count=1)

n5 = 0
for old, new in [("Vector3(0, 180, 0), size.x, wall_h)", "Vector3(0, 180, 0), label_w, wall_h)"),
                 ("Vector3(0, 0, 0), size.x, wall_h)", "Vector3(0, 0, 0), label_w, wall_h)"),
                 ("Vector3(0, 90, 0), size.z, wall_h)", "Vector3(0, 90, 0), label_w if wall_label_width >= 0.0 else size.z, wall_h)"),
                 ("Vector3(0, -90, 0), size.z, wall_h)", "Vector3(0, -90, 0), label_w if wall_label_width >= 0.0 else size.z, wall_h)")]:
    if old in text:
        text = text.replace(old, new, 1)
        n5 += 1

if (n1, n2, n3, n4, n5) != (1, 1, 1, 1, 4):
    sys.exit(f"main.gd does not have the expected form (matches: {(n1, n2, n3, n4, n5)}). Nothing changed.")
path.write_text(text, encoding="utf-8")
print("patched:", path.name)
