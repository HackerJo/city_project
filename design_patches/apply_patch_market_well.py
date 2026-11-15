#!/usr/bin/env python3
"""Add market square and well (corner pieces / U stairs) to the viewer (run once, repeatable).

    python apply_patch_market_well.py

Patches cityviewer/scripts/building_builder.gd and cityviewer/scripts/main.gd.
"""
import re
import sys
from pathlib import Path

root = Path(__file__).resolve().parent
SECTION = r"""# ---------------------------------------------------------------------------------------------
# Market square and well
# Market: one corner piece in each corner of the building area (the rest stays open path).
#   The corner model is a corner with arms to the east and south (seen from above, north up);
#   it is turned by 0 / -90 / 180 / 90 degrees for NW / NE / SE / SW.
# Well: four U-shaped stair pieces (open to the west in the model) on the four sides of the
#   centre, each turned so that its opening faces the centre; optional water disc in the middle.
# If a model is rotated wrongly, correct it with the column yaw_deg in parts.csv.
# ---------------------------------------------------------------------------------------------
const WELL_WATER := true
const WELL_WATER_RADIUS := 0.8
const WELL_WATER_COLOR := Color(0.25, 0.5, 0.8)


func has_role(role: String) -> bool:
	return parts.has(role)


func can_build(key: String) -> bool:
	if key == "market":
		return parts.has("market_corner")
	if key == "well":
		return parts.has("well_stairs")
	return is_ready()


# Market and well stand on path tiles (the fields are not blocked for the floor).
func leaves_floor_open(key: String) -> bool:
	return (key == "market" and parts.has("market_corner")) or (key == "well" and parts.has("well_stairs"))


func build_building(key: String, parent: Node3D, centre: Vector2, lx: float, lz: float, floors: int, door_side: String) -> Dictionary:
	if key == "church":
		return build_church(parent, centre, lx, floors, door_side)
	if key == "market":
		return build_market(parent, centre, lx, lz)
	if key == "well":
		return build_well(parent, centre, lx, lz)
	return build_house(parent, centre, lx, lz, floors, door_side)


func build_market(parent: Node3D, centre: Vector2, lx: float, lz: float) -> Dictionary:
	var box: AABB = parts["market_corner"]["aabb"]
	var corners := [[-1.0, -1.0, 0.0], [1.0, -1.0, -90.0], [1.0, 1.0, 180.0], [-1.0, 1.0, 90.0]]
	var colliders: Array = []
	for c in corners:
		var dx: float = c[0] * (lx / 2.0 - box.size.x / 2.0)
		var dz: float = c[1] * (lz / 2.0 - box.size.z / 2.0)
		var rot: float = c[2]
		_place(parent, "market_corner", Vector3(centre.x + dx, 0.0, centre.y + dz), rot, Vector3.ONE)
		colliders.append({"size": box.size, "pos": Vector3(centre.x + dx, box.size.y / 2.0, centre.y + dz)})
	return {"wall_top": 0.0, "height": 0.0, "colliders": colliders}


func build_well(parent: Node3D, centre: Vector2, lx: float, lz: float) -> Dictionary:
	var box: AABB = parts["well_stairs"]["aabb"]
	var offset := minf(lx, lz) / 2.0 - box.size.x / 2.0
	var pieces := [[1.0, 0.0, 0.0], [0.0, -1.0, 90.0], [-1.0, 0.0, 180.0], [0.0, 1.0, -90.0]]
	var colliders: Array = []
	for p in pieces:
		var dx: float = p[0] * offset
		var dz: float = p[1] * offset
		var rot: float = p[2]
		_place(parent, "well_stairs", Vector3(centre.x + dx, 0.0, centre.y + dz), rot, Vector3.ONE)
		colliders.append({"size": box.size, "pos": Vector3(centre.x + dx, box.size.y / 2.0, centre.y + dz)})
	if WELL_WATER:
		var water := MeshInstance3D.new()
		var cylinder := CylinderMesh.new()
		cylinder.top_radius = WELL_WATER_RADIUS
		cylinder.bottom_radius = WELL_WATER_RADIUS
		cylinder.height = 0.1
		var mat := StandardMaterial3D.new()
		mat.albedo_color = WELL_WATER_COLOR
		cylinder.material = mat
		water.mesh = cylinder
		water.position = Vector3(centre.x, 0.25, centre.y)
		parent.add_child(water)
	return {"wall_top": box.size.y, "height": box.size.y, "colliders": colliders, "wall_label_width": box.size.x}


"""


def load(rel: str) -> tuple:
    path = root / rel
    if not path.exists():
        sys.exit("not found: " + str(path))
    return path, path.read_text(encoding="utf-8")


def apply(text: str, edits: list, name: str) -> str:
    for pattern, repl, label in edits:
        text, count = re.subn(pattern, repl, text, count=1, flags=re.S)
        if count != 1:
            sys.exit(f"{name}: edit '{label}' not applicable - nothing was written")
    return text


# ---- building_builder.gd ----
bpath, btext = load("cityviewer/scripts/building_builder.gd")
if "func build_market" in btext:
    print("already patched:", bpath.name)
else:
    btext = apply(btext, [
        (r'([ \t]+var i_ridge := header\.find\("ridge_axis"\)\n)',
         lambda m: m.group(1) + m.group(1).split("var")[0] + 'var i_yaw := header.find("yaw_deg")\n', "yaw column"),
        (r'"ridge": _cell\(row, i_ridge, "z"\)\}',
         lambda m: '"ridge": _cell(row, i_ridge, "z"), "yaw": float(_cell(row, i_yaw, "0"))}', "yaw value"),
        (r'deg_to_rad\(rot_deg\)\) \* Basis\.IDENTITY\.scaled\(scale\)',
         lambda m: 'deg_to_rad(rot_deg + float(part.get("yaw", 0.0)))) * Basis.IDENTITY.scaled(scale)', "yaw in _place"),
        (r'(# Path tiles on all free fields)',
         lambda m: SECTION + m.group(1), "new section"),
    ], bpath.name)
    bpath.write_text(btext, encoding="utf-8")
    print("patched:", bpath.name)

# ---- main.gd ----
mpath, mtext = load("cityviewer/scripts/main.gd")
if "build_building" in mtext:
    print("already patched:", mpath.name)
else:
    mtext = apply(mtext, [
        (r'== "modular" and builder\.is_ready\(\):',
         lambda m: '== "modular" and builder.can_build(str(entry["key"])):', "can_build"),
        (r'(?P<i>[ \t]+)if str\(entry\["key"\]\) == "church":\n[ \t]+built = builder\.build_church\([^\n]*\)\n[ \t]+else:\n[ \t]+built = builder\.build_house\([^\n]*\)\n',
         lambda m: m.group("i") + 'built = builder.build_building(str(entry["key"]), self, Vector2(cx, cz), lx, lz, floors, str(entry["door"]))\n',
         "build_building"),
        (r'(?P<i>[ \t]+)builder\.build_floor\(self, columns, rows, cell, occupied\)\n',
         lambda m: (m.group("i") + 'var floor_blocked := occupied.duplicate()\n'
                    + m.group("i") + 'for entry in city["buildings"]:\n'
                    + m.group("i") + '\tif builder.leaves_floor_open(str(entry["key"])):\n'
                    + m.group("i") + '\t\tfor dc in int(entry["width_fields"]):\n'
                    + m.group("i") + '\t\t\tfor dr in int(entry["depth_fields"]):\n'
                    + m.group("i") + '\t\t\t\tfloor_blocked.erase(Vector2i(int(entry["col"]) + dc, int(entry["row"]) + dr))\n'
                    + m.group("i") + 'builder.build_floor(self, columns, rows, cell, floor_blocked)\n'),
         "floor without market and well"),
    ], mpath.name)
    mpath.write_text(mtext, encoding="utf-8")
    print("patched:", mpath.name)
