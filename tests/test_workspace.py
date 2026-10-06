import json, tempfile, unittest
from pathlib import Path
from shortforge_workspace import materialize_workspace
M={"kind":"ShortForgeAssetManifest","profile":"retro","format":"9:16","duration_seconds":20,"assets":[{"id":"beat-01-visual","type":"visual","required":True,"prompt":"opening"},{"id":"beat-01-caption","type":"caption","required":True,"text":"Hello"},{"id":"bed-music","type":"music","required":False,"prompt":"music"}]}
class TestWorkspace(unittest.TestCase):
    def test_materializes_files(self):
        with tempfile.TemporaryDirectory() as d:
            w=materialize_workspace(M,d); root=Path(d)
            self.assertEqual(w["kind"],"ShortForgeWorkspace")
            self.assertTrue((root/"workspace.json").is_file())
            self.assertTrue((root/"manifest.json").is_file())
            self.assertEqual((root/"captions/beat-01-caption.txt").read_text(),"Hello")
            p=json.loads((root/"assets/beat-01-visual.json").read_text())
            self.assertEqual(p["status"],"placeholder")
    def test_rejects_path_traversal_id(self):
        bad={**M,"assets":[{"id":"../oops","type":"visual"}]}
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError): materialize_workspace(bad,d)
if __name__=="__main__": unittest.main()
