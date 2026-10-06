import json, tempfile, unittest
from pathlib import Path
from shortforge_workspace import materialize_workspace
from shortforge_media import resolve_workspace
from shortforge_render import build_render_plan, render_workspace
M={"kind":"ShortForgeAssetManifest","profile":"retro","format":"9:16","duration_seconds":2,"assets":[{"id":"beat-01-visual","type":"visual","required":True,"start":0,"end":1,"prompt":"a"},{"id":"beat-02-visual","type":"visual","required":True,"start":1,"end":2,"prompt":"b"}]}
class TestRender(unittest.TestCase):
    def test_plan(self):
        with tempfile.TemporaryDirectory() as d:
            materialize_workspace(M,d); resolve_workspace(d)
            p=build_render_plan(d)
            self.assertEqual(p["kind"],"ShortForgeRenderPlan")
            self.assertEqual(p["output"],"output/short.mp4")
            self.assertEqual(p["command"][0],"ffmpeg")
            self.assertIn("scale=1080:1920",p["command"][p["command"].index("-filter_complex")+1])
    def test_plan_only_writes_plan(self):
        with tempfile.TemporaryDirectory() as d:
            materialize_workspace(M,d); resolve_workspace(d); render_workspace(d,execute=False)
            self.assertTrue((Path(d)/"render-plan.json").is_file())
            self.assertFalse((Path(d)/"output/short.mp4").exists())
if __name__=="__main__": unittest.main()
