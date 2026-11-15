from pathlib import Path
import re
import shutil

path = Path(__file__).resolve().parent / "cityviewer/scripts/building_builder.gd"
ADDITION = '\t# Floating tower roof above the well; no support elements.\n\tvar well_total_height := box.size.y\n\tif parts.has("roof_tower"):\n\t\tvar roof_box: AABB = parts["roof_tower"]["aabb"]\n\t\tif roof_box.size.x > 0.01 and roof_box.size.y > 0.01 and roof_box.size.z > 0.01:\n\t\t\tvar roof_width := 2.0 * extent_x + 0.6\n\t\t\tvar roof_depth := extent_z + 0.6\n\t\t\tvar roof_sx := roof_width / roof_box.size.x\n\t\t\tvar roof_sz := roof_depth / roof_box.size.z\n\t\t\tvar roof_sy := minf(roof_sx, roof_sz)\n\t\t\tvar roof_bottom := maxf(2.6, box.size.y + 1.6)\n\t\t\t_place(parent, "roof_tower", Vector3(centre.x, roof_bottom, centre.y), 0.0,\n\t\t\t\tVector3(roof_sx, roof_sy, roof_sz))\n\t\t\twell_total_height = roof_bottom + roof_box.size.y * roof_sy\n\telse:\n\t\tpush_warning("Brunnendach fehlt: Rolle roof_tower konnte nicht geladen werden.")\n'
if not path.is_file():
    raise SystemExit("building_builder.gd fehlt. Skript im Projektordner ausfuehren.")
text = path.read_text(encoding="utf-8-sig")
m = re.search(r"^func build_well\([^\n]*\n.*?(?=^func |\Z)", text, re.M | re.S)
if not m:
    raise SystemExit("build_well nicht gefunden. Nichts geaendert.")
fn = m.group(0)
if "var well_total_height :=" in fn:
    raise SystemExit("Brunnendach bereits eingebaut. Nichts geaendert.")
if "var extent_x :=" not in fn or "var extent_z :=" not in fn:
    raise SystemExit("Bitte zuerst apply_patch_well_alignment.py ausfuehren. Nichts geaendert.")
marker = '\treturn {"wall_top": box.size.y, "height": box.size.y, "colliders": colliders,'
if fn.count(marker) != 1:
    raise SystemExit("Rueckgabe hat nicht die erwartete Form. Nichts geaendert.")
new_marker = '\treturn {"wall_top": box.size.y, "height": well_total_height, "colliders": colliders,'
fn = fn.replace(marker, ADDITION + new_marker, 1)
backup = path.with_name("building_builder.gd.before_well_roof.bak")
if not backup.exists():
    shutil.copy2(path, backup)
path.write_text(text[:m.start()] + fn + text[m.end():], encoding="utf-8")
print("Schwebendes Brunnendach eingebaut. Sicherung:", backup)
