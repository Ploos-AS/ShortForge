import tempfile, unittest
from shortforge_workspace import materialize_workspace
from shortforge_media import resolve_workspace
from shortforge_render import build_render_plan
M={"kind":"ShortForgeAssetManifest","profile":"retro","format":"9:16","duration_seconds":2,"assets":[{"id":"beat-01-visual","type":"visual","required":True,"start":0,"end":2,"prompt":"a"},{"id":"beat-01-voice","type":"voice","required":True,"start":0,"end":1,"text":"hello"},{"id":"beat-01-caption","type":"caption","required":True,"start":0,"end":1,"text":"Hello: world"},{"id":"bed-music","type":"music","required":False,"start":0,"end":2,"prompt":"music"},{"id":"accent-sfx","type":"sfx","required":False,"start":1,"end":2,"prompt":"hit"}]}
class TestAudioCaptions(unittest.TestCase):
    def test_plan_has_caption_and_mix(self):
        with tempfile.TemporaryDirectory() as d:
            materialize_workspace(M,d); resolve_workspace(d); p=build_render_plan(d)
            fc=p["command"][p["command"].index("-filter_complex")+1]
            self.assertIn("drawtext=",fc); self.assertIn("y=h*0.78",fc)
            self.assertIn("adelay=1000|1000",fc); self.assertIn("volume=0.22",fc)
            self.assertIn("amix=inputs=3",fc); self.assertIn("alimiter=limit=0.95",fc)
            self.assertTrue(p["features"]["captions"]); self.assertTrue(p["features"]["audio_mix"])
            self.assertIn("aac",p["command"])
if __name__=="__main__": unittest.main()
