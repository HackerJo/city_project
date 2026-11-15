from pathlib import Path
import csv
import io
import re
import shutil

root = Path(__file__).resolve().parent
path = root / "cityviewer/scripts/building_builder.gd"
csv_path = root / "cityviewer/data/parts.csv"
INSERT = '\t\t\t# Four slender posts, grounded at the outer corners of the well.\n\t\t\tif parts.has("well_support"):\n\t\t\t\tvar post_box: AABB = parts["well_support"]["aabb"]\n\t\t\t\tif post_box.size.y > 0.01:\n\t\t\t\t\tvar post_scale := Vector3(1.0, roof_bottom / post_box.size.y, 1.0)\n\t\t\t\t\tvar post_x := maxf(0.0, extent_x - post_box.size.x / 2.0)\n\t\t\t\t\tvar post_z := maxf(0.0, extent_z / 2.0 - post_box.size.z / 2.0)\n\t\t\t\t\tvar post_corners := [[-1.0, -1.0, 0.0], [1.0, -1.0, -90.0],\n\t\t\t\t\t\t[1.0, 1.0, 180.0], [-1.0, 1.0, 90.0]]\n\t\t\t\t\tfor corner in post_corners:\n\t\t\t\t\t\tvar post_pos := Vector3(centre.x + float(corner[0]) * post_x,\n\t\t\t\t\t\t\t0.0, centre.y + float(corner[1]) * post_z)\n\t\t\t\t\t\t_place(parent, "well_support", post_pos, float(corner[2]), post_scale)\n\t\t\telse:\n\t\t\t\tpush_warning("Brunnenstuetzen fehlen: Rolle well_support nicht geladen.")\n'
if not path.is_file() or not csv_path.is_file():
    raise SystemExit("Projektdateien fehlen. Skript in city_project ablegen.")
text = path.read_text(encoding="utf-8-sig")
m = re.search(r"^func build_well\([^\n]*\n.*?(?=^func |\Z)", text, re.M | re.S)
if not m:
    raise SystemExit("build_well fehlt. Nichts geaendert.")
fn = m.group(0)
if 'parts.has("well_support")' not in fn:
    pattern = r"^(\t+)var roof_bottom := [^\n]+$"
    matches = list(re.finditer(pattern, fn, re.M))
    if len(matches) != 1 or 'var extent_x :=' not in fn or 'var extent_z :=' not in fn:
        raise SystemExit("Erwartete Brunnenfunktion mit Dach fehlt. Nichts geaendert.")
    fn = re.sub(pattern, lambda x: x.group(1) + 'var roof_bottom := maxf(3.0, box.size.y + 1.6)\n' + INSERT.rstrip('\n'), fn, count=1, flags=re.M)
reader = csv.DictReader(io.StringIO(csv_path.read_text(encoding="utf-8-sig")), delimiter=";")
fields = reader.fieldnames
if not fields or "role" not in fields or "file" not in fields:
    raise SystemExit("parts.csv hat nicht die erwarteten Spalten. Nichts geaendert.")
rows = list(reader)
role = {"role":"well_support", "file":"Corner_Interior_Small.gltf", "facing":"+z", "ridge_axis":"z", "yaw_deg":"0", "expected_size_whd":"0.2 x 3 x 0.2", "note":"Four well roof supports"}
found = False
for row in rows:
    if row.get("role") == "well_support":
        row.update({k:v for k,v in role.items() if k in fields})
        found = True
if not found:
    rows.append({k:role.get(k, "") for k in fields})
buf = io.StringIO(newline="")
w = csv.DictWriter(buf, fieldnames=fields, delimiter=";", lineterminator="\n")
w.writeheader()
w.writerows(rows)
for p in (path, csv_path):
    backup = p.with_name(p.name + ".before_well_supports.bak")
    if not backup.exists():
        shutil.copy2(p, backup)
path.write_text(text[:m.start()] + fn + text[m.end():], encoding="utf-8")
csv_path.write_text(buf.getvalue(), encoding="utf-8")
print("Vier Brunnenstuetzen ergaenzt; parts.csv aktualisiert. Vorhandene Brunnendrehung beibehalten.")
