import json, tempfile, unittest, wave
from pathlib import Path
from shortforge_workspace import materialize_workspace
from shortforge_media import resolve_workspace
M={"kind":"ShortForgeAssetManifest","profile":"retro","format":"9:16","duration_seconds":2,"assets":[{"id":"beat-01-visual","type":"visual","required":True,"start":0,"end":1,"prompt":"opening"},{"id":"beat-01-voice","type":"voice","required":True,"start":0,"end":1,"text":"hello"},{"id":"beat-01-caption","type":"caption","required":True,"start":0,"end":1,"text":"Hello"},{"id":"bed-music","type":"music","required":False,"start":0,"end":2,"prompt":"music"}]}
class TestMedia(unittest.TestCase):
    def test_resolves_binary_media(self):
        with tempfile.TemporaryDirectory() as d:
            materialize_workspace(M,d); w=resolve_workspace(d); root=Path(d)
            self.assertTrue((root/"assets/beat-01-visual.png").read_bytes().startswith(b"\x89PNG"))
            with wave.open(str(root/"assets/beat-01-voice.wav"),"rb") as f: self.assertEqual(f.getframerate(),16000)
            self.assertEqual((root/"captions/beat-01-caption.txt").read_text(),"Hello")
            ready=[x for x in w["assets"] if x["type"]=="visual"][0]
            self.assertEqual(ready["provider"],"deterministic")
            self.assertEqual(ready["mime_type"],"image/png")
    def test_missing_workspace(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError): resolve_workspace(d)
if __name__=="__main__": unittest.main()
