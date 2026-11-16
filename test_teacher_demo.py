"""Synthetic-file tests; no GUI, real marker recognition or Godot launch."""
from pathlib import Path
import hashlib
import json
import tempfile
import unittest
from PIL import Image
from teacher_demo import load_demos, prepare_demo_run, check_demo_result
from teacher_backend import read_json, viewer_command


class DemoTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "Projekt ä mit Leerzeichen"
        self.folder = self.root / "examples/city02"
        self.folder.mkdir(parents=True)
        (self.root / "cityviewer/data").mkdir(parents=True)
        (self.root / "cityviewer/project.godot").write_text("[application]\n")
        (self.root / "scripts").mkdir()
        (self.root / "scripts/detect_city.py").write_text("pass\n")
        self.layout = {"paper_mm":{"width":420,"height":297}, "field_mm":30, "columns":12,"rows":8,
            "grid_origin_mm":{"x":30,"y":28.5},"aruco_dict":"DICT_4X4_50","corner_markers_mm":{}}
        self.catalog = {"buildings":[{"id":2,"key":"house","width":2,"depth":1}]}
        self.city = {"grid":{"columns":12,"rows":8},"buildings":[{"id":2,"key":"house","name":"Haus",
            "col":1,"row":1,"width_fields":2,"depth_fields":1,"door":"N"}],"warnings":[]}
        for name, obj in (("layout.json",self.layout),("buildings.json",self.catalog),("city.json",self.city)):
            self.write(self.folder / name,obj)
        self.write(self.root / "cityviewer/data/buildings.json",self.catalog)
        for name in ("Example_City_02.JPEG","control.jpg","rectified.jpg","rectified_raw.jpg"):
            Image.new("RGB",(20,20),"white").save(self.folder / name)
        self.manifest={"schema_version":1,"demos":[{"id":"city02","title":"Beispiel 02","folder":"city02","photo":"Example_City_02.JPEG"}]}
        self.write(self.root / "examples/demos.json",self.manifest)
        self.work = self.root / "Arbeitsdaten"

    def write(self,path,obj):
        path.write_text(json.dumps(obj,ensure_ascii=False),encoding="utf-8")

    def demo(self):
        demos,errors=load_demos(self.root)
        self.assertEqual(errors,[])
        return demos[0]

    def snapshot(self):
        return {p.relative_to(self.folder).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                for p in self.folder.rglob("*") if p.is_file()}

    def test_manifest(self):
        self.assertEqual(self.demo()["photo"].name,"Example_City_02.JPEG")

    def test_missing_example_does_not_crash(self):
        (self.folder / "control.jpg").unlink()
        demos,errors=load_demos(self.root)
        self.assertEqual(demos,[])
        self.assertTrue(errors)

    def test_bad_json(self):
        (self.root / "examples/demos.json").write_text("not JSON")
        self.assertTrue(load_demos(self.root)[1])

    def test_path_escape(self):
        self.manifest["demos"][0]["folder"]="../../outside"
        self.write(self.root / "examples/demos.json",self.manifest)
        self.assertTrue(load_demos(self.root)[1])

    def test_duplicate_id(self):
        self.manifest["demos"].append(dict(self.manifest["demos"][0]))
        self.write(self.root / "examples/demos.json",self.manifest)
        demos,errors=load_demos(self.root)
        self.assertEqual(len(demos),1)
        self.assertTrue(errors)

    def test_prepared_copies_without_source_changes(self):
        before=self.snapshot()
        run=prepare_demo_run(self.root,self.demo(),True,self.work)
        self.assertEqual(self.snapshot(),before)
        self.assertEqual(len(check_demo_result(run)["buildings"]),1)
        self.assertEqual(read_json(run / "session.json")["mode"],"prepared_demo")
        self.assertIn("KEINE neue Erkennung",(run / "detect.log").read_text())

    def test_recognition_uses_example_inputs(self):
        run=prepare_demo_run(self.root,self.demo(),False,self.work)
        self.assertEqual(read_json(run / "input/output/layout.json"),self.layout)
        self.assertFalse((run / "result/city.json").exists())
        self.assertEqual(read_json(run / "session.json")["mode"],"demo_recognition")

    def test_unique_sessions(self):
        a=prepare_demo_run(self.root,self.demo(),False,self.work)
        b=prepare_demo_run(self.root,self.demo(),False,self.work)
        self.assertNotEqual(a,b)

    def test_catalog_conflict_blocks_prepared(self):
        self.write(self.root / "cityviewer/data/buildings.json",{"buildings":[]})
        with self.assertRaisesRegex(ValueError,"Demo-Katalog"):
            prepare_demo_run(self.root,self.demo(),True,self.work)

    def test_conflict_can_recognize_but_cannot_launch(self):
        self.write(self.root / "cityviewer/data/buildings.json",{"buildings":[]})
        run=prepare_demo_run(self.root,self.demo(),False,self.work)
        fake_exe=self.root / "Godot.exe"
        fake_exe.touch()
        with self.assertRaisesRegex(ValueError,"[Kk]atalog"):
            viewer_command(self.root,fake_exe,run)

    def test_bad_result_grid(self):
        self.city["grid"]["columns"]=13
        self.write(self.folder / "city.json",self.city)
        with self.assertRaisesRegex(ValueError,"Rastergroessen"):
            prepare_demo_run(self.root,self.demo(),True,self.work)

    def test_bad_building_id(self):
        self.city["buildings"][0]["id"]=99
        self.write(self.folder / "city.json",self.city)
        with self.assertRaisesRegex(ValueError,"Gebaeude-ID"):
            prepare_demo_run(self.root,self.demo(),True,self.work)

    def test_rotated_footprint(self):
        entry=self.city["buildings"][0]
        entry.update(door="E",width_fields=1,depth_fields=2)
        self.write(self.folder / "city.json",self.city)
        run=prepare_demo_run(self.root,self.demo(),True,self.work)
        self.assertEqual(check_demo_result(run)["buildings"][0]["door"],"E")

    def test_bad_footprint(self):
        self.city["buildings"][0]["width_fields"]=1
        self.write(self.folder / "city.json",self.city)
        with self.assertRaisesRegex(ValueError,"Grundflaeche|grundflaeche"):
            prepare_demo_run(self.root,self.demo(),True,self.work)

    def test_invalid_control_image(self):
        (self.folder / "control.jpg").write_text("not a JPEG")
        with self.assertRaises(OSError):
            prepare_demo_run(self.root,self.demo(),True,self.work)


if __name__=="__main__":
    unittest.main(verbosity=2)
