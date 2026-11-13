#!/usr/bin/env python3
"""Replace the church part of cityviewer/scripts/building_builder.gd (run once, repeatable).

    python apply_patch_church_block.py
"""
import re
import sys
from pathlib import Path

root = Path(__file__).resolve().parent
path = root / "cityviewer" / "scripts" / "building_builder.gd"
if not path.exists():
    sys.exit("not found: " + str(path))

NEW_SECTION = r'''# ---------------------------------------------------------------------------------------------
# Church: rectangular block (size x size). The door is in the middle of one side; on both sides
# of the door a tower rises out of the corner. Local layout with the door in the south (z+);
# the whole building is rotated to the real door side.
# Body: "floors" storeys (3 = ground floor + 2 upper floors).
# Towers: floors + TOWER_EXTRA_FLOORS storeys, CHURCH_TOWER_PIECES wall pieces wide.
# Each side has CHURCH_PIECES pieces: tower, centre part (door), tower.
# ---------------------------------------------------------------------------------------------
const TOWER_EXTRA_FLOORS := 3
const CHURCH_PIECES := 7
const CHURCH_TOWER_PIECES := 2
const CHURCH_GABLE_INSET := 0.6      # front gable is set back behind the tower faces (metres)


func _place_wall(root: Node3D, role: String, pos: Vector3, side: String, piece_len: float) -> void:
	var role_box: AABB = parts[role]["aabb"]
	_place(root, role, pos, _side_rotation(side, role), Vector3(piece_len / role_box.size.x, 1.0, 1.0))


func build_church(parent: Node3D, centre: Vector2, size: float, floors: int, door_side: String) -> Dictionary:
	var wall_box: AABB = parts["wall"]["aabb"]
	var wall_h := wall_box.size.y
	var thick := wall_box.size.z
	var body_floors := maxi(1, floors)
	var tower_floors := body_floors + TOWER_EXTRA_FLOORS
	var body_top := body_floors * wall_h
	var tower_top := tower_floors * wall_h
	var n := CHURCH_PIECES
	var piece_len := size / float(n)
	var tw := CHURCH_TOWER_PIECES * piece_len
	var half := size / 2.0

	var door_rot := 0.0
	match door_side:
		"N":
			door_rot = 180.0
		"E":
			door_rot = 90.0
		"W":
			door_rot = -90.0
	var root := Node3D.new()
	root.position = Vector3(centre.x, 0.0, centre.y)
	root.rotation_degrees = Vector3(0.0, door_rot, 0.0)
	parent.add_child(root)

	# outer walls: towers go up to tower_floors, the rest to body_floors
	for side in ["N", "S", "E", "W"]:
		for i in n:
			var in_tower := false
			if side == "S":
				in_tower = i < CHURCH_TOWER_PIECES or i >= n - CHURCH_TOWER_PIECES
			elif side == "E" or side == "W":
				in_tower = i >= n - CHURCH_TOWER_PIECES
			var storeys := tower_floors if in_tower else body_floors
			var t := -half + (i + 0.5) * piece_len
			for floor_index in storeys:
				var role := _wall_role(side == "S", i, n, floor_index)
				var pos := _wall_point(side, t, size, size, thick)
				pos.y = floor_index * wall_h
				_place_wall(root, role, pos, side, piece_len)

	# inner faces and back faces of the towers above the body
	for sx in [-1.0, 1.0]:
		var inner_side := "E" if sx < 0.0 else "W"
		for floor_index in range(body_floors, tower_floors):
			for k in CHURCH_TOWER_PIECES:
				var along := (k + 0.5) * piece_len
				var inner := Vector3(sx * (half - tw + thick / 2.0), floor_index * wall_h, half - tw + along)
				_place_wall(root, "wall", inner, inner_side, piece_len)
				var back := Vector3(sx * (half - along), floor_index * wall_h, half - tw + thick / 2.0)
				_place_wall(root, "wall", back, "N", piece_len)

	var height := tower_top
	if parts.has("roof"):
		var tan_pitch := _add_roof(root, Vector2(0.0, -OVERHANG_ALONG / 2.0), "z", size, size + OVERHANG_ALONG, body_top)
		_add_gable(root, "N", _wall_point("N", 0.0, size, size, thick), size, tan_pitch, body_top)
		var front := _wall_point("S", 0.0, size, size, thick)
		front.z -= CHURCH_GABLE_INSET
		_add_gable(root, "S", front, size, tan_pitch, body_top)
	if parts.has("roof_tower"):
		var tb: AABB = parts["roof_tower"]["aabb"]
		var sxs := (tw + 2.0 * OVERHANG_ACROSS) / tb.size.x
		var szs := (tw + 2.0 * OVERHANG_ACROSS) / tb.size.z
		var sys := (sxs + szs) / 2.0
		for side_x in [-1.0, 1.0]:
			var tower_centre := Vector3(side_x * (half - tw / 2.0), tower_top - TOWER_ROOF_SINK, half - tw / 2.0)
			_place(root, "roof_tower", tower_centre, 0.0, Vector3(sxs, sys, szs))
		height = tower_top - TOWER_ROOF_SINK + tb.size.y * sys

	var colliders: Array = [{"size": Vector3(size, tower_top, size),
		"pos": Vector3(centre.x, tower_top / 2.0, centre.y)}]
	return {"wall_top": body_top, "height": height, "colliders": colliders}


'''

text = path.read_text(encoding="utf-8")
pattern = re.compile(r"# -{20,}\n# Church:.*?(?=# Path tiles on all free fields)", re.S)
text, count = pattern.subn(lambda m: NEW_SECTION, text, count=1)
if count != 1:
    sys.exit("church section not found in building_builder.gd - nothing changed")
path.write_text(text, encoding="utf-8")
print("patched:", path.name)
