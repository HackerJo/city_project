from pathlib import Path
from datetime import datetime
import shutil
import re

bundle = Path(__file__).resolve().parent
project = bundle.parent
bp = project / "cityviewer/scripts/building_builder.gd"
mp = project / "cityviewer/scripts/main.gd"
wp = project / "cityviewer/scripts/city_wall.gd"
if not bp.is_file() or not mp.is_file():
    raise SystemExit("Updateordner direkt in city_project ablegen. Nichts geaendert.")
b = bp.read_text(encoding="utf-8-sig")
m = mp.read_text(encoding="utf-8-sig")
BACKING = '\t\t\t# Window_Thin_Flat1 is an insert, not a complete closed wall.\n\t\t\tif role == "wall_window_thin":\n\t\t\t\t_place_wall(root, "wall", pos, side, step)\n\t\t\t\tmatch side:\n\t\t\t\t\t"N": pos.z -= 0.03\n\t\t\t\t\t"S": pos.z += 0.03\n\t\t\t\t\t"E": pos.x += 0.03\n\t\t\t\t\t"W": pos.x -= 0.03\n'
fn = re.search(r"^func _public_wall_run\(.*?(?=^func |\Z)", b, re.M | re.S)
if not fn:
    raise SystemExit("Die Version mit Kloster/Rathaus fehlt. Zuerst das vorherige Update installieren.")
section = fn.group(0)
marker = '\t\t\t_place_wall(root, role, pos, side, step)'
if '# Window_Thin_Flat1 is an insert' not in section:
    if section.count(marker) != 1:
        raise SystemExit("Wandfunktion nicht im erwarteten Format. Nichts geaendert.")
    section = section.replace(marker, BACKING + marker, 1)
    b = b[:fn.start()] + section + b[fn.end():]
if 'const CityWallScript :=' not in m:
    marker = 'const BuilderScript := preload("res://scripts/building_builder.gd")'
    if m.count(marker) != 1:
        raise SystemExit("main.gd: preload-Zeile nicht gefunden. Nichts geaendert.")
    m = m.replace(marker, marker + '\nconst CityWallScript := preload("res://scripts/city_wall.gd")', 1)
if 'CityWallScript.new().build(' not in m:
    marker = '\t_build_player(columns, rows, occupied)'
    if m.count(marker) != 1:
        raise SystemExit("main.gd: Stadtaufbau nicht erkannt. Nichts geaendert.")
    m = m.replace(marker, '\tCityWallScript.new().build(self, total_w, total_d)\n' + marker, 1)
source = bundle / "city_wall.gd"
if not source.is_file():
    raise SystemExit("city_wall.gd fehlt im Updatepaket. Nichts geaendert.")
backup = project / ("backup_mauer_tuerme_" + datetime.now().strftime("%Y%m%d_%H%M%S_%f"))
for path in (bp, mp, wp):
    if path.exists():
        dest = backup / path.relative_to(project)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dest)
bp.write_text(b, encoding="utf-8")
mp.write_text(m, encoding="utf-8")
shutil.copy2(source, wp)
print("Turmwand-Unterbau und automatische Stadtmauer installiert.")
print("Sicherung:", backup)
print("Viewer neu starten. CSV und JSON sind unveraendert.")
