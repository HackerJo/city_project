extends Node3D
# City viewer: reads city.json (from scripts/detect_city.py) and buildings.json
# (from scripts/generate_prints.py) and builds a walkable placeholder city.
# Two views: walk (first person) and bird (orthographic top-down view, north is up).
# Start:  godot --path cityviewer -- <absolute path to city.json>
# Without an argument, res://data/city.json is loaded.
# Coordinates: x = east, z = south (north = -z). Door "N" faces -z.

const BUILDINGS_PATH := "res://data/buildings.json"
const DEFAULT_CITY_PATH := "res://data/city.json"
const BUILDING_GAP := 0.6        # gap between buildings (metres)
const EYE_HEIGHT := 1.7
const WALK_SPEED := 5.0
const MOUSE_SENSITIVITY := 0.0025
const MEADOW_MARGIN := 60.0      # meadow outside the city (metres)
const DEFAULT_HEIGHT := 5.0
const DEFAULT_COLOR := Color(0.7, 0.7, 0.7)
const HELP_WALK := "WASD/arrows: walk   Mouse: look   Shift: faster   V: bird view   F2: names   F3: FPS   Esc: quit"
const HELP_BIRD := "WASD/arrows: move   Mouse wheel: zoom   Home: fit city   V: walk   F2: names   F3: FPS   Esc: quit"

# Name labels
const LABEL_FONT_SIZE := 64
const LABEL_MAX_PIXEL_SIZE := 0.02   # upper limit: text height = font size * pixel size (metres)
const LABEL_FILL := 0.85             # text may use this share of the available width
const LABEL_HEIGHT_FRACTION := 0.3   # text height may be this share of the available height
const LABEL_OUTLINE := 10
const LABEL_OFFSET := 0.08           # distance in front of a surface (metres)

# Bird view
const BIRD_HEIGHT := 150.0           # camera height (orthographic, so it only has to be above everything)
const BIRD_MARGIN := 1.08            # free space around the city when fitted
const BIRD_PAN_FRACTION := 0.8       # pan speed: share of the visible height per second
const BIRD_MIN_SIZE := 10.0          # closest zoom (visible height in metres)
const BIRD_MAX_ZOOM_OUT := 1.5       # farthest zoom as a multiple of the fitted size

var catalog := {}                # building key -> Dictionary from buildings.json
var meters_per_field := 6.0
var path_color := Color(0.72, 0.65, 0.54)
var meadow_color := Color(0.35, 0.6, 0.3)
var start_view := "walk"
var view_mode := "walk"          # "walk" or "bird"
var names_on := true
var city_size := Vector2.ZERO    # width (x) and depth (z) of the grid in metres
var player: CharacterBody3D
var camera: Camera3D
var bird_camera: Camera3D
var bird_size := 100.0
var bird_fit_size := 100.0
var player_marker: MeshInstance3D
var labels_root: Node3D          # names on the walls (walk view)
var top_labels_root: Node3D      # names on the roofs (bird view)
var pitch := 0.0
var hud: Label
var error_text := ""
var show_fps := true


func _ready() -> void:
	labels_root = Node3D.new()
	add_child(labels_root)
	top_labels_root = Node3D.new()
	add_child(top_labels_root)
	_build_environment()
	_build_hud()
	_load_catalog()
	var city_path := _city_path()
	var city = _load_json(city_path)
	if city == null or not (city is Dictionary) or not city.has("buildings"):
		error_text = "Cannot read city file: " + city_path \
			+ "\nArguments: " + str(OS.get_cmdline_user_args()) \
			+ "\nProject folder: " + ProjectSettings.globalize_path("res://")
		hud.text = error_text
		return
	_build_city(city)
	view_mode = start_view
	_apply_view()


func _city_path() -> String:
	var args := OS.get_cmdline_user_args()
	if args.size() > 0:
		return args[0]
	return DEFAULT_CITY_PATH


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
	path_color = Color.html(str(data.get("path_color", "#b8a58a")))
	meadow_color = Color.html(str(data.get("meadow_color", "#5a9a4d")))
	if str(data.get("start_view", "walk")) == "bird":
		start_view = "bird"
	for b in data.get("buildings", []):
		catalog[str(b["key"])] = b


func _material(color: Color) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_color = color
	return m


func _box(size: Vector3, pos: Vector3, color: Color, collide := true) -> StaticBody3D:
	var body := StaticBody3D.new()
	body.position = pos
	var mi := MeshInstance3D.new()
	var mesh := BoxMesh.new()
	mesh.size = size
	mesh.material = _material(color)
	mi.mesh = mesh
	body.add_child(mi)
	if collide:
		var cs := CollisionShape3D.new()
		var shape := BoxShape3D.new()
		shape.size = size
		cs.shape = shape
		body.add_child(cs)
	add_child(body)
	return body


func _build_environment() -> void:
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(0.62, 0.78, 0.92)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.75, 0.75, 0.75)
	env.ambient_light_energy = 0.8
	var we := WorldEnvironment.new()
	we.environment = env
	add_child(we)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-50, -30, 0)
	sun.shadow_enabled = false
	add_child(sun)


func _build_hud() -> void:
	var layer := CanvasLayer.new()
	hud = Label.new()
	hud.position = Vector2(12, 8)
	hud.add_theme_color_override("font_color", Color.WHITE)
	hud.add_theme_color_override("font_shadow_color", Color.BLACK)
	hud.text = HELP_WALK
	layer.add_child(hud)
	add_child(layer)


func _build_city(city: Dictionary) -> void:
	var cell := meters_per_field
	var columns := int(city["grid"]["columns"])
	var rows := int(city["grid"]["rows"])
	var total_w := columns * cell
	var total_d := rows * cell
	city_size = Vector2(total_w, total_d)

	# meadow outside the grid, path on all fields inside (empty field = path)
	_box(Vector3(total_w + 2.0 * MEADOW_MARGIN, 0.2, total_d + 2.0 * MEADOW_MARGIN),
		Vector3(total_w / 2.0, -0.1, total_d / 2.0), meadow_color)
	_box(Vector3(total_w, 0.22, total_d), Vector3(total_w / 2.0, -0.09, total_d / 2.0), path_color, false)

	var occupied := {}
	for entry in city["buildings"]:
		var w := int(entry["width_fields"])
		var d := int(entry["depth_fields"])
		var col := int(entry["col"])
		var row := int(entry["row"])
		for dc in w:
			for dr in d:
				occupied[Vector2i(col + dc, row + dr)] = true
		var info: Dictionary = catalog.get(str(entry["key"]), {})
		var height: float = float(info.get("height_m", DEFAULT_HEIGHT))
		var color := DEFAULT_COLOR
		if info.has("color"):
			color = Color.html(str(info["color"]))
		var size := Vector3(w * cell - BUILDING_GAP, height, d * cell - BUILDING_GAP)
		var centre := Vector3((col + w / 2.0) * cell, height / 2.0, (row + d / 2.0) * cell)
		_box(size, centre, color, height >= 0.5)
		_door(centre, size, str(entry["door"]))
		_add_labels(centre, size, str(entry.get("name", entry["key"])))

	_build_player(columns, rows, occupied)
	_build_bird_view()


func _door(centre: Vector3, size: Vector3, side: String) -> void:
	if size.y < 0.5:
		return
	var door_w := 1.4
	var door_h: float = minf(2.2, size.y)
	var thick := 0.15
	var pos := Vector3(centre.x, door_h / 2.0, centre.z)
	var door_size := Vector3(door_w, door_h, thick)
	match side:
		"N":
			pos.z = centre.z - size.z / 2.0
		"S":
			pos.z = centre.z + size.z / 2.0
		"E":
			pos.x = centre.x + size.x / 2.0
			door_size = Vector3(thick, door_h, door_w)
		"W":
			pos.x = centre.x - size.x / 2.0
			door_size = Vector3(thick, door_h, door_w)
	_box(door_size, pos, Color(0.25, 0.15, 0.08), false)


# Names: on all four walls (walk view) and lying on the roof (bird view, north is up).
# Label3D faces +Z by default; rotation about Y turns the front outwards:
# south 0 deg, north 180 deg, east +90 deg, west -90 deg.
func _add_labels(centre: Vector3, size: Vector3, text: String) -> void:
	if text == "":
		return
	var roof := Vector3(centre.x, size.y + LABEL_OFFSET, centre.z)
	_add_label(top_labels_root, text, roof, Vector3(-90, 0, 0), size.x, size.z)
	if size.y < 0.5:
		_add_label(labels_root, text, roof, Vector3(-90, 0, 0), minf(size.x, size.z), 0.0)
		return
	var y := clampf(size.y * 0.65, 0.6, 9.0)
	var half_x := size.x / 2.0 + LABEL_OFFSET
	var half_z := size.z / 2.0 + LABEL_OFFSET
	_add_label(labels_root, text, Vector3(centre.x, y, centre.z - half_z), Vector3(0, 180, 0), size.x, size.y)
	_add_label(labels_root, text, Vector3(centre.x, y, centre.z + half_z), Vector3(0, 0, 0), size.x, size.y)
	_add_label(labels_root, text, Vector3(centre.x + half_x, y, centre.z), Vector3(0, 90, 0), size.z, size.y)
	_add_label(labels_root, text, Vector3(centre.x - half_x, y, centre.z), Vector3(0, -90, 0), size.z, size.y)


func _add_label(parent: Node3D, text: String, pos: Vector3, rot_deg: Vector3, max_width: float, max_height: float) -> void:
	var label := Label3D.new()
	label.text = text
	label.font_size = LABEL_FONT_SIZE
	label.outline_size = LABEL_OUTLINE
	label.modulate = Color.WHITE
	label.outline_modulate = Color.BLACK
	label.shaded = false
	label.double_sided = false
	# scale the text so that it fits the available width (and height, if given)
	var font := ThemeDB.fallback_font
	var text_px := font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, LABEL_FONT_SIZE).x
	var px := LABEL_MAX_PIXEL_SIZE
	if text_px > 0.0:
		px = minf(px, LABEL_FILL * max_width / text_px)
	if max_height > 0.0:
		px = minf(px, LABEL_HEIGHT_FRACTION * max_height / LABEL_FONT_SIZE)
	label.pixel_size = px
	label.position = pos
	label.rotation_degrees = rot_deg
	parent.add_child(label)


func _build_player(columns: int, rows: int, occupied: Dictionary) -> void:
	# start on the free field closest to the grid centre
	var best := Vector2i(0, 0)
	var best_dist := INF
	var centre := Vector2(columns / 2.0 - 0.5, rows / 2.0 - 0.5)
	for c in columns:
		for r in rows:
			if not occupied.has(Vector2i(c, r)):
				var dist := Vector2(c, r).distance_to(centre)
				if dist < best_dist:
					best_dist = dist
					best = Vector2i(c, r)
	player = CharacterBody3D.new()
	player.position = Vector3((best.x + 0.5) * meters_per_field, 0.1, (best.y + 0.5) * meters_per_field)
	var cs := CollisionShape3D.new()
	var capsule := CapsuleShape3D.new()
	capsule.radius = 0.4
	capsule.height = 1.8
	cs.shape = capsule
	cs.position = Vector3(0, 0.9, 0)
	player.add_child(cs)
	camera = Camera3D.new()
	camera.position = Vector3(0, EYE_HEIGHT, 0)
	camera.far = 300.0
	player.add_child(camera)
	add_child(player)


# Orthographic camera looking straight down. North is up on the screen, east is right.
func _build_bird_view() -> void:
	bird_camera = Camera3D.new()
	bird_camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	bird_camera.rotation_degrees = Vector3(-90, 0, 0)
	bird_camera.near = 1.0
	bird_camera.far = BIRD_HEIGHT + 100.0
	add_child(bird_camera)
	# red ball above the walker's position
	player_marker = MeshInstance3D.new()
	var ball := SphereMesh.new()
	ball.radius = 1.2
	ball.height = 2.4
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(0.9, 0.1, 0.1)
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	ball.material = mat
	player_marker.mesh = ball
	add_child(player_marker)
	get_viewport().size_changed.connect(_fit_bird_view)
	_fit_bird_view()


# Fit the whole grid into the window (also called when the window size changes).
func _fit_bird_view() -> void:
	if bird_camera == null:
		return
	var view := get_viewport().get_visible_rect().size
	var aspect := view.x / maxf(view.y, 1.0)
	bird_fit_size = maxf(city_size.y * BIRD_MARGIN, city_size.x * BIRD_MARGIN / aspect)
	bird_size = bird_fit_size
	bird_camera.size = bird_size
	bird_camera.position = Vector3(city_size.x / 2.0, BIRD_HEIGHT, city_size.y / 2.0)


func _zoom_bird(factor: float) -> void:
	bird_size = clampf(bird_size * factor, BIRD_MIN_SIZE, bird_fit_size * BIRD_MAX_ZOOM_OUT)
	bird_camera.size = bird_size


func _apply_view() -> void:
	if player == null or bird_camera == null:
		return
	var bird := view_mode == "bird"
	if bird:
		bird_camera.make_current()
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	else:
		camera.make_current()
		Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
	labels_root.visible = names_on and not bird
	top_labels_root.visible = names_on and bird
	player_marker.visible = bird


func _unhandled_input(ev: InputEvent) -> void:
	if ev is InputEventMouseMotion:
		var motion := ev as InputEventMouseMotion
		if player != null and view_mode == "walk" and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
			player.rotate_y(-motion.relative.x * MOUSE_SENSITIVITY)
			pitch = clampf(pitch - motion.relative.y * MOUSE_SENSITIVITY, -1.4, 1.4)
			camera.rotation.x = pitch
	elif ev is InputEventKey:
		var key := ev as InputEventKey
		if key.pressed and not key.echo:
			if key.keycode == KEY_ESCAPE:
				get_tree().quit()
			elif key.keycode == KEY_F3:
				show_fps = not show_fps
			elif key.keycode == KEY_F2:
				names_on = not names_on
				_apply_view()
			elif key.keycode == KEY_V:
				view_mode = "walk" if view_mode == "bird" else "bird"
				_apply_view()
			elif key.keycode == KEY_HOME and view_mode == "bird":
				_fit_bird_view()
	elif ev is InputEventMouseButton:
		var click := ev as InputEventMouseButton
		if click.pressed:
			if view_mode == "bird":
				if click.button_index == MOUSE_BUTTON_WHEEL_UP:
					_zoom_bird(0.9)
				elif click.button_index == MOUSE_BUTTON_WHEEL_DOWN:
					_zoom_bird(1.1)
			elif player != null:
				Input.mouse_mode = Input.MOUSE_MODE_CAPTURED


func _move_input() -> Vector2:
	var v := Vector2.ZERO
	if Input.is_physical_key_pressed(KEY_W) or Input.is_physical_key_pressed(KEY_UP):
		v.y -= 1.0
	if Input.is_physical_key_pressed(KEY_S) or Input.is_physical_key_pressed(KEY_DOWN):
		v.y += 1.0
	if Input.is_physical_key_pressed(KEY_A) or Input.is_physical_key_pressed(KEY_LEFT):
		v.x -= 1.0
	if Input.is_physical_key_pressed(KEY_D) or Input.is_physical_key_pressed(KEY_RIGHT):
		v.x += 1.0
	return v


func _process(delta: float) -> void:
	if error_text != "":
		return
	var text := HELP_BIRD if view_mode == "bird" else HELP_WALK
	if show_fps:
		text += "   |   FPS: " + str(Engine.get_frames_per_second())
	hud.text = text
	if player == null or bird_camera == null:
		return
	player_marker.position = Vector3(player.position.x, BIRD_HEIGHT - 20.0, player.position.z)
	if view_mode == "bird":
		var pan := _move_input()
		bird_camera.position.x += pan.x * bird_size * BIRD_PAN_FRACTION * delta
		bird_camera.position.z += pan.y * bird_size * BIRD_PAN_FRACTION * delta


func _physics_process(delta: float) -> void:
	if player == null or view_mode == "bird":
		return
	var input := _move_input()
	var speed := WALK_SPEED
	if Input.is_physical_key_pressed(KEY_SHIFT):
		speed *= 2.0
	var direction := (player.global_transform.basis * Vector3(input.x, 0.0, input.y)).normalized()
	player.velocity.x = direction.x * speed
	player.velocity.z = direction.z * speed
	if player.is_on_floor():
		player.velocity.y = 0.0
	else:
		player.velocity.y -= 20.0 * delta
	player.move_and_slide()
