from pathlib import Path
import importlib.util
import json
import tempfile
import unittest
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import teacher_backend as backend


class BackendTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "Projekt mit Leerzeichen und Umlaut ä"
        for rel in ("scripts", "output", "cityviewer/data"):
            (self.root / rel).mkdir(parents=True, exist_ok=True)
        self.image = self.root / "Foto ä.jpg"
        self.image.write_bytes(b"fake-image-for-interface-test")
        self.layout = {"paper_mm":{"width":420,"height":297}, "field_mm":30, "columns":12, "rows":8,
                       "grid_origin_mm":{"x":30,"y":28.5}, "aruco_dict":"DICT_4X4_50", "corner_markers_mm":{}}
        self.catalog = {"buildings":[{"id":2,"key":"house"}]}
        self.write_json(self.root / "output/layout.json", self.layout)
        self.write_json(self.root / "cityviewer/data/buildings.json", self.catalog)
        (self.root / "cityviewer/project.godot").write_text("[application]\n")
        (self.root / "scripts/detect_city.py").write_text("pass\n")
        self.work = Path(self.tmp.name) / "Arbeitsdaten ä"

    def write_json(self, path, obj):
        path.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")

    def prepare(self):
        return backend.prepare_run(self.root, self.image, self.work)

    def example(self):
        return {"grid":{"columns":12,"rows":8}, "buildings":[
            {"key":"house","name":"Wohnhaus","col":1,"row":1,"width_fields":1,"depth_fields":1,"door":"N"}], "warnings":[]}

    def store_result(self, run, city):
        self.write_json(run / "result/city.json", city)
        (run / "result/rectified.jpg").write_bytes(b"placeholder")

    def test_snapshot_and_unique_results(self):
        first, second = self.prepare(), self.prepare()
        self.assertNotEqual(first, second)
        self.assertEqual(backend.read_json(first / "input/output/buildings.json"), self.catalog)
        self.assertFalse((second / "result/city.json").exists())

    def test_no_original_photo_copy(self):
        run = self.prepare()
        self.assertFalse(any(p.name == self.image.name for p in run.rglob("*")))

    def test_missing_layout(self):
        (self.root / "output/layout.json").unlink()
        with self.assertRaisesRegex(ValueError, "layout.json"):
            self.prepare()

    def test_result_validation(self):
        run = self.prepare()
        self.store_result(run, self.example())
        self.assertEqual(len(backend.validate_result(run)["buildings"]), 1)

    def test_empty_result_rejected(self):
        run = self.prepare()
        city = self.example()
        city["buildings"] = []
        self.store_result(run, city)
        with self.assertRaisesRegex(ValueError, "Keine Gebaeude"):
            backend.validate_result(run)

    def test_overlap_warning(self):
        run = self.prepare()
        city = self.example()
        city["buildings"].append(dict(city["buildings"][0]))
        self.store_result(run, city)
        self.assertTrue(backend.validate_result(run)["warnings"])

    def test_viewer_command_absolute_and_catalog_change(self):
        run = self.prepare()
        exe = self.root / "Godot.exe"
        exe.touch()
        cmd = backend.viewer_command(self.root, exe, run)
        self.assertEqual(cmd[-2], "--")
        self.assertTrue(Path(cmd[-1]).is_absolute())
        self.write_json(self.root / "cityviewer/data/buildings.json", {"buildings":[]})
        with self.assertRaisesRegex(ValueError, "geaendert"):
            backend.viewer_command(self.root, exe, run)

    def test_subprocess_interface_with_fake_detector(self):
        # Tests process invocation only, not ArUco recognition.
        script = """import argparse,json
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument('--image');p.add_argument('--root');p.add_argument('--out')
a=p.parse_args()
out=Path(a.out)
(out/'city.json').write_text(json.dumps({'grid':{'columns':12,'rows':8},'buildings':[{'key':'house','name':'Wohnhaus','col':1,'row':1,'width_fields':1,'depth_fields':1,'door':'N'}],'warnings':[]}),encoding='utf-8')
(out/'rectified.jpg').write_bytes(b'placeholder')
"""
        (self.root / "scripts/detect_city.py").write_text(script)
        run = self.prepare()
        result = subprocess.run(backend.detector_command(self.root, self.image, run), capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(backend.validate_result(run)["buildings"]), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
