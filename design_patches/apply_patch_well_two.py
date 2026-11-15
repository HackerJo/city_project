#!/usr/bin/env python3
"""Well from two U pieces (normal + turned by 180 degrees). Run once, repeatable.

    python apply_patch_well_two.py

Replaces build_well in cityviewer/scripts/building_builder.gd.
"""
import re
import sys
from pathlib import Path

path = Path(__file__).resolve().parent / "cityviewer" / "scripts" / "building_builder.gd"
if not path.exists():
    sys.exit("not found: " + str(path))
NEW = r"""func build_well(parent: Node3D, centre: Vector2, lx: float, lz: float) -> Dictionary:
	# two U pieces face each other: the normal one on the east side, the one turned by 180 degrees on the west side
	var box: AABB = parts["well_stairs"]["aabb"]
	var offset := box.size.x / 2.0
	var pieces := [[1.0, 0.0], [-1.0, 180.0]]
	var colliders: Array = []
	for p in pieces:
		var dx: float = p[0] * offset
		var rot: float = p[1]
		_place(parent, "well_stairs", Vector3(centre.x + dx, 0.0, centre.y), rot, Vector3.ONE)
		colliders.append({"size": box.size, "pos": Vector3(centre.x + dx, box.size.y / 2.0, centre.y)})
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
	return {"wall_top": box.size.y, "height": box.size.y, "colliders": colliders, "wall_label_width": 2.0 * box.size.x}


"""
text = path.read_text(encoding="utf-8")
text, count = re.subn(r"func build_well\(.*?(?=# Path tiles on all free fields)", lambda m: NEW, text, count=1, flags=re.S)
if count != 1:
    sys.exit("build_well not found - run apply_patch_market_well.py first. Nothing changed.")
path.write_text(text, encoding="utf-8")
print("patched:", path.name)
