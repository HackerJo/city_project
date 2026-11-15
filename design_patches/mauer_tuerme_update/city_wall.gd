extends RefCounted
# Always-present perimeter, outside the grid. All dimensions in metres.
const HEIGHT := 3.1
const THICKNESS := 0.6
const OFFSET := 0.8
const GATE_WIDTH := 3.0
const SPRING_HEIGHT := 1.3
const ARCH_STEPS := 24

func build(parent: Node3D, width: float, depth: float) -> void:
	var root := Node3D.new()
	root.name = "AutomaticCityWall"
	parent.add_child(root)
	var material := ShaderMaterial.new()
	var shader := Shader.new()
	shader.code = """shader_type spatial;
render_mode cull_disabled;
void fragment() {
    vec2 p = UV / vec2(0.6, 0.3);
    float row = floor(p.y);
    p.x += mod(row, 2.0) * 0.5;
    vec2 f = fract(p);
    float mortar = max(1.0 - step(0.035, f.x), 1.0 - step(0.065, f.y));
    float variation = fract(sin(dot(vec2(floor(p.x), row), vec2(12.9898,78.233))) * 43758.5453);
    vec3 stone = vec3(0.43, 0.41, 0.36) * (0.87 + 0.24 * variation);
    ALBEDO = mix(stone, vec3(0.25, 0.24, 0.21), mortar);
    ROUGHNESS = 0.95;
}
"""
	material.shader = shader
	_side(root, Vector3(width / 2.0, 0.0, -OFFSET), 0.0, width + 2.0 * OFFSET + THICKNESS, material)
	_side(root, Vector3(width / 2.0, 0.0, depth + OFFSET), 0.0, width + 2.0 * OFFSET + THICKNESS, material)
	_side(root, Vector3(-OFFSET, 0.0, depth / 2.0), 90.0, depth + 2.0 * OFFSET + THICKNESS, material)
	_side(root, Vector3(width + OFFSET, 0.0, depth / 2.0), 90.0, depth + 2.0 * OFFSET + THICKNESS, material)

func _side(parent: Node3D, pos: Vector3, yaw: float, length: float, material: Material) -> void:
	var root := Node3D.new()
	root.position = pos
	root.rotation_degrees.y = yaw
	parent.add_child(root)
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var radius := minf(GATE_WIDTH / 2.0, length / 4.0)
	_prism(st, root, -length / 2.0, -radius, 0.0, 0.0)
	_prism(st, root, radius, length / 2.0, 0.0, 0.0)
	# The underside follows the semicircle. The space below stays empty.
	for i in range(ARCH_STEPS):
		var a := PI - PI * float(i) / float(ARCH_STEPS)
		var b := PI - PI * float(i + 1) / float(ARCH_STEPS)
		_prism(st, root, radius * cos(a), radius * cos(b),
			SPRING_HEIGHT + radius * sin(a), SPRING_HEIGHT + radius * sin(b))
	var mi := MeshInstance3D.new()
	mi.mesh = st.commit()
	mi.material_override = material
	root.add_child(mi)

func _prism(st: SurfaceTool, root: Node3D, x0: float, x1: float, y0: float, y1: float) -> void:
	var z := THICKNESS / 2.0
	var v := PackedVector3Array([
		Vector3(x0,y0,-z), Vector3(x1,y1,-z), Vector3(x1,HEIGHT,-z), Vector3(x0,HEIGHT,-z),
		Vector3(x0,y0,z), Vector3(x1,y1,z), Vector3(x1,HEIGHT,z), Vector3(x0,HEIGHT,z)])
	var faces := [[0,1,2,3], [5,4,7,6], [4,0,3,7], [1,5,6,2], [3,2,6,7], [4,5,1,0]]
	for face in faces:
		for tri in [[face[0],face[1],face[2]], [face[0],face[2],face[3]]]:
			var normal := (v[tri[2]] - v[tri[0]]).cross(v[tri[1]] - v[tri[0]]).normalized()
			for index in tri:
				st.set_normal(normal)
				st.set_uv(Vector2(v[index].x, v[index].y))
				st.add_vertex(v[index])
	# Individual convex pieces keep the opening free, unlike one bounding box.
	var body := StaticBody3D.new()
	var collision := CollisionShape3D.new()
	var shape := ConvexPolygonShape3D.new()
	shape.points = v
	collision.shape = shape
	body.add_child(collision)
	root.add_child(body)
