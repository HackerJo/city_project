from pathlib import Path
import re
import shutil

path = Path(__file__).resolve().parent / "cityviewer/scripts/building_builder.gd"
NEW = 'func build_well(parent: Node3D, centre: Vector2, lx: float, lz: float) -> Dictionary:\n\tvar box: AABB = parts["well_stairs"]["aabb"]\n\tvar yaw := float(parts["well_stairs"].get("yaw", 0.0))\n\t# The model\'s native opening is along Z, not X.\n\tvar correction := 90.0\n\tvar angle := deg_to_rad(correction + yaw)\n\tvar extent_x := absf(cos(angle)) * box.size.x + absf(sin(angle)) * box.size.z\n\tvar extent_z := absf(sin(angle)) * box.size.x + absf(cos(angle)) * box.size.z\n\tvar offset := extent_x / 2.0\n\tvar colliders: Array = []\n\tfor sign_x in [-1.0, 1.0]:\n\t\tvar turn := correction if sign_x > 0.0 else correction + 180.0\n\t\tvar pos := Vector3(centre.x + sign_x * offset, 0.0, centre.y)\n\t\t_place(parent, "well_stairs", pos, turn, Vector3.ONE)\n\t\tcolliders.append({"size": Vector3(extent_x, box.size.y, extent_z),\n\t\t\t"pos": pos + Vector3(0.0, box.size.y / 2.0, 0.0)})\n\tif WELL_WATER:\n\t\tvar water := MeshInstance3D.new()\n\t\tvar mesh := BoxMesh.new()\n\t\t# Water extends underneath the stone rim, hiding the exact seam.\n\t\tmesh.size = Vector3(2.0 * extent_x - 0.2, 0.06, extent_z - 0.2)\n\t\tvar mat := StandardMaterial3D.new()\n\t\tmat.albedo_color = WELL_WATER_COLOR\n\t\tmesh.material = mat\n\t\twater.mesh = mesh\n\t\twater.position = Vector3(centre.x, box.size.y * 0.45, centre.y)\n\t\tparent.add_child(water)\n\treturn {"wall_top": box.size.y, "height": box.size.y, "colliders": colliders,\n\t\t"wall_label_width": 2.0 * extent_x}\n\n\n'
if not path.is_file():
    raise SystemExit("building_builder.gd nicht gefunden. Skript in den Projektordner legen.")
text = path.read_text(encoding="utf-8-sig")
pattern = r"^func build_well\([^\n]*\n.*?(?=^func |\Z)"
match = re.search(pattern, text, re.M | re.S)
if match is None:
    raise SystemExit("build_well nicht gefunden. Nichts geaendert.")
backup = path.with_name("building_builder.gd.before_well_alignment.bak")
if not backup.exists():
    shutil.copy2(path, backup)
text = text[:match.start()] + NEW + text[match.end():]
path.write_text(text, encoding="utf-8")
print("Brunnenfunktion ersetzt. Sicherung:", backup)
