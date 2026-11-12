extends RefCounted
# Assembles buildings from glTF parts that are listed in res://data/parts.csv.
# The size of every part is measured from its meshes, so the origin of a model does not matter.
# Each part is placed by its bottom centre. "facing" (+z or -z) is the model side that looks outwards.
#
# Wall:  pieces of the "wall" template are repeated along each side; the last step can stretch or
#        compress them slightly so that the wall length is met exactly (FIT_WALL_LENGTH).
# Roof:  gable roof, ridge along the longer side (square: perpendicular to the door wall).
# Gable: triangular piece on the two walls at the ridge ends.

const PARTS_DIR := "res://models/parts/"
const OVERHANG_ACROSS := 0.5     # roof overhang at the eaves (metres)
const OVERHANG_ALONG := 0.7      # roof overhang at the gables (beams stick out there)
const FIT_WALL_LENGTH := true    # true: stretch/compress pieces to the exact wall length
const FLOOR_Y := 0.03            # height of the path tiles above the meadow

var parts := {}                  # role -> {"scene", "aabb", "facing", "ridge"}
var messages: Array = []


func is_ready() -> bool:
	return parts.has("wall") and parts.has("wall_door")


func load_parts(csv_path: String) -> void:
	parts.clear()
	messages.clear()
	var f := FileAccess.open(csv_path, FileAccess.READ)
	if f == null:
		messages.append("parts.csv not found: " + csv_path)
		return
	var header := f.get_csv_line(";")
	var i_role := header.find("role")
	var i_file := header.find("file")
	var i_facing := header.find("facing")
	var i_ridge := header.find("ridge_axis")
	if i_role < 0 or i_file < 0:
		messages.append("parts.csv needs the columns role and file")
		return
	while not f.eof_reached():
		var row := f.get_csv_line(";")
		if row.size() <= maxi(i_role, i_file):
			continue
		var role := row[i_role].strip_edges()
		if role == "" or role.begins_with("#"):
			continue
		var path := PARTS_DIR + row[i_file].strip_edges()
		if not ResourceLoader.exists(path):
			messages.append("Part '%s' missing or not imported yet: %s" % [role, path])
			continue
		var scene = load(path)
		if not (scene is PackedScene):
			messages.append("Part '%s' is not a scene: %s" % [role, path])
			continue
		var probe := (scene as PackedScene).instantiate() as Node3D
		if probe == null:
			continue
		var boxes: Array = []
		_collect(probe, Transform3D.IDENTITY, boxes)
		probe.free()
		parts[role] = {"scene": scene, "aabb": _merge(boxes),
			"facing": _cell(row, i_facing, "+z"), "ridge": _cell(row, i_ridge, "z")}


func _cell(row: PackedStringArray, index: int, fallback: String) -> String:
	if index < 0 or index >= row.size():
		return fallback
	var v := row[index].strip_edges()
	return v if v != "" else fallback


func _collect(node: Node, parent_xf: Transform3D, boxes: Array) -> void:
	var xf := parent_xf
	if node is Node3D:
		xf = parent_xf * (node as Node3D).transform
	if node is MeshInstance3D:
		var mesh := (node as MeshInstance3D).mesh
		if mesh != null:
			boxes.append(xf * mesh.get_aabb())
	for child in node.get_children():
		_collect(child, xf, boxes)


func _merge(boxes: Array) -> AABB:
	if boxes.is_empty():
		return AABB()
	var result: AABB = boxes[0]
	for i in range(1, boxes.size()):
		result = result.merge(boxes[i])
	return result


func _first_mesh(node: Node, parent_xf: Transform3D) -> Array:
	var xf := parent_xf
	if node is Node3D:
		xf = parent_xf * (node as Node3D).transform
	if node is MeshInstance3D and (node as MeshInstance3D).mesh != null:
		return [(node as MeshInstance3D).mesh, xf]
	for child in node.get_children():
		var found := _first_mesh(child, xf)
		if not found.is_empty():
			return found
	return []


# Place a part so that the bottom centre of its bounding box lands on cb (relative to parent).
func _place(parent: Node3D, role: String, cb: Vector3, rot_deg: float, scale: Vector3) -> void:
	if not parts.has(role):
		return
	var part: Dictionary = parts[role]
	var box: AABB = part["aabb"]
	var inst := (part["scene"] as PackedScene).instantiate() as Node3D
	if inst == null:
		return
	var holder := Node3D.new()
	holder.add_child(inst)
	holder.basis = Basis(Vector3.UP, deg_to_rad(rot_deg)) * Basis.IDENTITY.scaled(scale)
	var native_cb := Vector3(box.get_center().x, box.position.y, box.get_center().z)
	holder.position = cb - holder.basis * native_cb
	parent.add_child(holder)


func _side_rotation(side: String, role: String) -> float:
	var base := 0.0
	match side:
		"N":
			base = 180.0
		"E":
			base = 90.0
		"W":
			base = -90.0
	if parts.has(role) and String(parts[role]["facing"]) == "-z":
		base += 180.0
	return base


func _wall_point(side: String, t: float, lx: float, lz: float, thick: float) -> Vector3:
	match side:
		"N":
			return Vector3(t, 0.0, -lz / 2.0 + thick / 2.0)
		"S":
			return Vector3(t, 0.0, lz / 2.0 - thick / 2.0)
		"E":
			return Vector3(lx / 2.0 - thick / 2.0, 0.0, t)
	return Vector3(-lx / 2.0 + thick / 2.0, 0.0, t)


# Door in the middle of the door wall (ground floor); windows on every second piece, mirrored,
# never at the corners and never next to the door. Ground floor: wide windows, upper floors: thin.
func _wall_role(is_door_wall: bool, i: int, n: int, floor_index: int) -> String:
	var middle := int(n / 2)
	var window := "wall_window_wide" if floor_index == 0 else "wall_window_thin"
	if not parts.has(window):
		window = "wall_window_thin" if parts.has("wall_window_thin") else "wall"
	if is_door_wall and i == middle:
		if floor_index == 0:
			return "wall_door"
		return window
	var mirrored := mini(i, n - 1 - i)
	if mirrored == 0:
		return "wall"
	if is_door_wall and abs(i - middle) <= 1:
		return "wall"
	if mirrored % 2 == 1:
		return window
	return "wall"


func _ridge_axis(lx: float, lz: float, door_side: String) -> String:
	if lx > lz + 0.01:
		return "x"
	if lz > lx + 0.01:
		return "z"
	return "z" if (door_side == "N" or door_side == "S") else "x"


# centre: building centre (x, z) in world coordinates. Returns {"wall_top": float, "height": float}.
func build_house(parent: Node3D, centre: Vector2, lx: float, lz: float, floors: int, door_side: String) -> Dictionary:
	var wall_box: AABB = parts["wall"]["aabb"]
	var wall_len := wall_box.size.x
	var wall_h := wall_box.size.y
	var thick := wall_box.size.z
	var root := Node3D.new()
	root.position = Vector3(centre.x, 0.0, centre.y)
	parent.add_child(root)

	for side in ["N", "S", "E", "W"]:
		var length := lx if (side == "N" or side == "S") else lz
		var n := maxi(1, int(ceil(length / wall_len - 0.0001)))
		var piece_len := length / float(n) if FIT_WALL_LENGTH else wall_len
		for floor_index in floors:
			for i in n:
				var role := _wall_role(side == door_side, i, n, floor_index)
				var role_box: AABB = parts[role]["aabb"]
				var role_len := role_box.size.x
				var t := -length / 2.0 + (i + 0.5) * piece_len
				var pos := _wall_point(side, t, lx, lz, thick)
				pos.y = floor_index * wall_h
				_place(root, role, pos, _side_rotation(side, role), Vector3(piece_len / role_len, 1.0, 1.0))

	var wall_top := floors * wall_h
	var result := {"wall_top": wall_top, "height": wall_top}
	if not parts.has("roof"):
		return result

	var roof: Dictionary = parts["roof"]
	var rbox: AABB = roof["aabb"]
	var ridge_native := String(roof["ridge"])
	var ridge_world := _ridge_axis(lx, lz, door_side)
	var l_ridge := lx if ridge_world == "x" else lz
	var l_span := lz if ridge_world == "x" else lx
	var span_native := rbox.size.x if ridge_native == "z" else rbox.size.z
	var len_native := rbox.size.z if ridge_native == "z" else rbox.size.x
	var tan_pitch := rbox.size.y / (span_native / 2.0)
	var across := (l_span + 2.0 * OVERHANG_ACROSS) / span_native
	var along := (l_ridge + 2.0 * OVERHANG_ALONG) / len_native
	var roof_scale := Vector3(across, across, along) if ridge_native == "z" else Vector3(along, across, across)
	var roof_rot := 0.0 if ridge_native == ridge_world else 90.0
	_place(root, "roof", Vector3(0.0, wall_top - OVERHANG_ACROSS * tan_pitch, 0.0), roof_rot, roof_scale)
	result["height"] = wall_top + (l_span / 2.0) * tan_pitch

	var gable_role := "gable_large"
	if not parts.has("gable_large") or (l_span < 5.0 and parts.has("gable_small")):
		gable_role = "gable_small"
	if parts.has(gable_role):
		var gbox: AABB = parts[gable_role]["aabb"]
		var g_scale := Vector3(l_span / gbox.size.x, (l_span / 2.0 * tan_pitch) / gbox.size.y, 1.0)
		var end_sides := ["N", "S"] if ridge_world == "z" else ["E", "W"]
		for side in end_sides:
			var pos := _wall_point(side, 0.0, lx, lz, thick)
			pos.y = wall_top
			_place(root, gable_role, pos, _side_rotation(side, gable_role), g_scale)
	return result


# Path tiles on all free fields as one MultiMesh. Returns false if the floor part is not available.
func build_floor(parent: Node3D, columns: int, rows: int, cell: float, occupied: Dictionary) -> bool:
	if not parts.has("floor"):
		return false
	var part: Dictionary = parts["floor"]
	var box: AABB = part["aabb"]
	if box.size.x <= 0.01 or box.size.z <= 0.01:
		return false
	var probe := (part["scene"] as PackedScene).instantiate() as Node3D
	var found := _first_mesh(probe, Transform3D.IDENTITY)
	probe.free()
	if found.is_empty():
		return false
	var mesh: Mesh = found[0]
	var mesh_xf: Transform3D = found[1]

	var per_side := maxi(1, int(round(cell / box.size.x)))
	var tile := cell / float(per_side)
	var basis := Basis.IDENTITY.scaled(Vector3(tile / box.size.x, 1.0, tile / box.size.z))
	var native_top := Vector3(box.get_center().x, box.position.y + box.size.y, box.get_center().z)
	var transforms: Array = []
	for c in columns:
		for r in rows:
			if occupied.has(Vector2i(c, r)):
				continue
			for ix in per_side:
				for iz in per_side:
					var centre := Vector3(c * cell + (ix + 0.5) * tile, FLOOR_Y, r * cell + (iz + 0.5) * tile)
					transforms.append(Transform3D(basis, centre - basis * native_top) * mesh_xf)
	if transforms.is_empty():
		return true
	var mm := MultiMesh.new()
	mm.transform_format = MultiMesh.TRANSFORM_3D
	mm.mesh = mesh
	mm.instance_count = transforms.size()
	for i in transforms.size():
		mm.set_instance_transform(i, transforms[i])
	var mmi := MultiMeshInstance3D.new()
	mmi.multimesh = mm
	parent.add_child(mmi)
	return true
