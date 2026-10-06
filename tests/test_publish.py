import json, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from shortforge_publish import build_publish_package
class TestPublish(unittest.TestCase):
 def test_requires_video(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(ValueError): build_publish_package(d)
 def test_package(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d); (r/"output").mkdir(); (r/"output/short.mp4").write_bytes(b"x")
   (r/"render-plan.json").write_text(json.dumps({"duration_seconds":2,"features":{"production_profile":"shorts"}}))
   (r/"manifest.json").write_text(json.dumps({"assets":[{"id":"c","type":"caption","text":"hi"}]}))
   with patch("shortforge_publish.qualify_video",return_value={"passed":True}), patch("shortforge_publish.shutil.which",return_value="/usr/bin/ffmpeg"), patch("shortforge_publish.subprocess.run") as run:
    def make_thumb(*a,**k): (r/"publish/thumbnail.png").write_bytes(b"png")
    run.side_effect=make_thumb; p=build_publish_package(r,title="Demo")
   self.assertTrue(p["qualified"]); self.assertTrue((r/"publish/package.json").is_file()); self.assertEqual(json.loads((r/"publish/metadata.json").read_text())["production_profile"],"shorts")
if __name__=="__main__": unittest.main()
