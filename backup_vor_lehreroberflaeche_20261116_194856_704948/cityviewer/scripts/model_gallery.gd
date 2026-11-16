extends Node3D
# Model gallery: loads every .glb/.gltf file in a folder (including sub folders) and places the
# models in a grid, at their real size, so that you can compare candidates and fly around.
#
# Run (editor):   open scenes/model_gallery.tscn and press F6. Default folder: res://models
# Run (console):  godot --path cityviewer res://scenes/model_gallery.tscn -- "C:\path\to\folder"
#
# Each model gets a label with file name, size in metres and triangle count.
# A light grey square shows the footprint: one grid field (meters_per_field), or the intended
# footprint if the file name matches the "model" column of buildings.json.
# Controls: WASD fly, Q/E down/up, Shift faster, mouse wheel = speed, click = capture mouse,
# Esc = release mouse (second Esc quits).

const DEFAULT_FOLDER := "res://models"
const BUILDINGS_PATH := "res://data/buildings.json"
const GAP := 4.0                 # free space between two models (metres)
const LABEL_FONT_SIZE := 48
const MOUSE_SENSITIVITY := 0.0025

var meters_per_field := 6.0
var by_model := {}               # model file name -> building entry from buildings.json
var cam: Camera3D
var hud: Label
var yaw := 0.0
var pitch := 0.0
var fly_speed := 10.0


func _ready() -> void:
	_build_environment()
	_build_hud()
	_load_catalog()
	var folder := DEFAULT_FOLDER
	var args := OS.get_cmdline_user_args()
	if args.size() > 0:
		folder = args[0]
	var files := _find_models(folder)
	if files.is_empty():
		hud.text = "No .glb/.gltf files found in: " + folder
		_build_camera(Vector3(0, 3, 10), 0.0, -0.2)
		return
	_build_gallery(files, folder)


func _load_json(path: String):
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return null
	return JSON.parse_string(f.get_as_text())


func _load_catalog() -> void:
	var data = _load_json(BUILDINGS_PATH)
	if data == null or not (data is Dictionary):
		return
	meters_per_field = float(data.get("world_meters_per_field", meters_per_field))
	for b in data.get("buildings", []):
		by_model[str(b.get("model", ""))] = b


func _find_models(folder: String) -> Array:
	var result := []
	var dir := DirAccess.open(folder)
	if dir == null:
		return result
	dir.list_dir_begin()
	var entry := dir.get_next()
	while entry != "":
		var full := folder.path_join(entry)
		if dir.current_is_dir():
			if not entry.begins_with("."):
				result.append_array(_find_models(full))
		else:
			var ext := entry.get_extension().to_lower()
			if ext == "glb" or ext == "gltf":
				result.append(full)
		entry = dir.get_next()
	dir.list_dir_end()
	result.sort()
	return result


func _load_model(path: String) -> Node3D:
	var doc := GLTFDocument.new()
	var state := GLTFState.new()
	var err := doc.append_from_file(path, state, 0, path.get_base_dir())
	if err != OK:
		push_warning("Cannot load model: " + path)
		return null
	return doc.generate_scene(state) as Node3D


func _mesh_instances(node: Node) -> Array:
	var found := []
	if node is MeshInstance3D:
		found.append(node)
	for child in node.get_children():
		found.append_array(_mesh_instances(child))
	return found


func _combined_aabb(root: Node3D) -> AABB:
	var result := AABB()
	var first := true
	for mi in _mesh_instances(root):
		var box: AABB = mi.global_transform * mi.get_aabb()
		if first:
			result = box
			first = false
		else:
			result = result.merge(box)
	return result


func _count_triangles(root: Node) -> int:
	var total := 0
	if root is MeshInstance3D:
		var mesh := (root as MeshInstance3D).mesh
		if mesh != null:
			total += int(mesh.get_faces().size() / 3)
	for child in root.get_children():
		total += _count_triangles(child)
	return total


func _footprint(file_name: String) -> Vector2:
	if by_model.has(file_name):
		var b: Dictionary = by_model[file_name]
		return Vector2(float(b.get("width", 1)), float(b.get("depth", 1))) * meters_per_field
	return Vector2(meters_per_field, meters_per_field)


func _build_gallery(files: Array, folder: String) -> void:
	var loaded := []
	var cell := 0.0
	for path in files:
		var model := _load_model(path)
		if model == null:
			continue
		add_child(model)
		var aabb := _combined_aabb(model)
		var fp := _footprint(String(path).get_file())
		cell = maxf(cell, maxf(maxf(aabb.size.x, aabb.size.z), maxf(fp.x, fp.y)))
		loaded.append({"path": path, "node": model, "aabb": aabb, "footprint": fp, "tris": _count_triangles(model)})

	var count := loaded.size()
	var columns := int(ceil(sqrt(float(count))))
	var rows := int(ceil(float(count) / float(columns)))
	var spacing := cell + GAP
	for i in count:
		var item: Dictionary = loaded[i]
		var col := i % columns
		var row := int(floor(float(i) / float(columns)))
		var centre := Vector3(col * spacing, 0.0, row * spacing)
		var node: Node3D = item["node"]
		var aabb: AABB = item["aabb"]
		node.position += centre - Vector3(aabb.get_center().x, aabb.position.y, aabb.get_center().z)
		_add_footprint(centre, item["footprint"])
		_add_label(centre, aabb, item, String(item["path"]).get_file())

	hud.text = str(count) + " models from " + folder + "   |   WASD fly, Q/E down/up, Shift faster, wheel: speed, Esc: release mouse / quit"
	fly_speed = clampf(spacing * 0.8, 5.0, 60.0)
	_build_camera(Vector3((columns - 1) * spacing / 2.0, maxf(6.0, cell * 0.6), (rows - 1) * spacing + spacing * 1.2), 0.0, -0.25)


func _add_footprint(centre: Vector3, fp: Vector2) -> void:
	var mi := MeshInstance3D.new()
	var mesh := BoxMesh.new()
	mesh.size = Vector3(fp.x, 0.04, fp.y)
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(0.85, 0.85, 0.85)
	mesh.material = mat
	mi.mesh = mesh
	mi.position = Vector3(centre.x, -0.02, centre.z)
	add_child(mi)


func _add_label(centre: Vector3, aabb: AABB, item: Dictionary, file_name: String) -> void:
	var text := file_name + "\n%.1f x %.1f x %.1f m (w x h x d)\n%d triangles" % [aabb.size.x, aabb.size.y, aabb.size.z, item["tris"]]
	if by_model.has(file_name):
		var b: Dictionary = by_model[file_name]
		text += "\nfor: %s (%dx%d fields)" % [str(b.get("name", "")), int(b.get("width", 1)), int(b.get("depth", 1))]
	var label := Label3D.new()
	label.text = text
	label.font_size = LABEL_FONT_SIZE
	label.outline_size = 8
	label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	label.no_depth_test = true
	label.shaded = false
	label.pixel_size = clampf(maxf(aabb.size.y, 4.0) / 250.0, 0.008, 0.1)
	label.position = Vector3(centre.x, aabb.size.y + 1.5 + 4.0 * label.pixel_size * LABEL_FONT_SIZE / 2.0, centre.z)
	add_child(label)


func _build_environment() -> void:
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(0.62, 0.78, 0.92)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.8, 0.8, 0.8)
	env.ambient_light_energy = 0.8
	var we := WorldEnvironment.new()
	we.environment = env
	add_child(we)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-50, -30, 0)
	sun.shadow_enabled = false
	add_child(sun)
	var ground := MeshInstance3D.new()
	var mesh := BoxMesh.new()
	mesh.size = Vector3(4000, 0.2, 4000)
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(0.42, 0.6, 0.38)
	mesh.material = mat
	ground.mesh = mesh
	ground.position = Vector3(0, -0.14, 0)
	add_child(ground)


func _build_hud() -> void:
	var layer := CanvasLayer.new()
	hud = Label.new()
	hud.position = Vector2(12, 8)
	hud.add_theme_color_override("font_color", Color.WHITE)
	hud.add_theme_color_override("font_shadow_color", Color.BLACK)
	layer.add_child(hud)
	add_child(layer)


func _build_camera(pos: Vector3, start_yaw: float, start_pitch: float) -> void:
	cam = Camera3D.new()
	cam.far = 2000.0
	cam.position = pos
	add_child(cam)
	cam.make_current()
	yaw = start_yaw
	pitch = start_pitch
	cam.rotation = Vector3(pitch, yaw, 0.0)


func _unhandled_input(ev: InputEvent) -> void:
	if ev is InputEventMouseMotion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED and cam != null:
		var motion := ev as InputEventMouseMotion
		yaw -= motion.relative.x * MOUSE_SENSITIVITY
		pitch = clampf(pitch - motion.relative.y * MOUSE_SENSITIVITY, -1.5, 1.5)
		cam.rotation = Vector3(pitch, yaw, 0.0)
	elif ev is InputEventMouseButton:
		var click := ev as InputEventMouseButton
		if click.pressed:
			if click.button_index == MOUSE_BUTTON_WHEEL_UP:
				fly_speed = minf(fly_speed * 1.2, 500.0)
			elif click.button_index == MOUSE_BUTTON_WHEEL_DOWN:
				fly_speed = maxf(fly_speed / 1.2, 1.0)
			else:
				Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
	elif ev is InputEventKey:
		var key := ev as InputEventKey
		if key.pressed and not key.echo and key.keycode == KEY_ESCAPE:
			if Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
				Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
			else:
				get_tree().quit()


func _process(delta: float) -> void:
	if cam == null:
		return
	var move := Vector3.ZERO
	var basis := cam.global_transform.basis
	if Input.is_physical_key_pressed(KEY_W) or Input.is_physical_key_pressed(KEY_UP):
		move -= basis.z
	if Input.is_physical_key_pressed(KEY_S) or Input.is_physical_key_pressed(KEY_DOWN):
		move += basis.z
	if Input.is_physical_key_pressed(KEY_A) or Input.is_physical_key_pressed(KEY_LEFT):
		move -= basis.x
	if Input.is_physical_key_pressed(KEY_D) or Input.is_physical_key_pressed(KEY_RIGHT):
		move += basis.x
	if Input.is_physical_key_pressed(KEY_E):
		move += Vector3.UP
	if Input.is_physical_key_pressed(KEY_Q):
		move -= Vector3.UP
	var speed := fly_speed
	if Input.is_physical_key_pressed(KEY_SHIFT):
		speed *= 3.0
	if move.length() > 0.0:
		cam.position += move.normalized() * speed * delta
