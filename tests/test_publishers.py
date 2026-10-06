import json, tempfile, unittest
from pathlib import Path
from shortforge_publishers import PUBLISHER_INFO, validate_package, get_publisher
class TestPublishers(unittest.TestCase):
 def fixture(self,root):
  for f in ("short.mp4","thumbnail.png","captions.json","metadata.json","manifest.json","render-plan.json","qualification.json"): (root/f).write_bytes(b"{}")
  (root/"package.json").write_text(json.dumps({"kind":"ShortForgePublishingPackage","qualified":True}))
 def test_catalog(self):
  self.assertEqual(set(PUBLISHER_INFO),{"filesystem","youtube","tiktok","instagram"})
  self.assertTrue(PUBLISHER_INFO["youtube"]["requires_auth"]); self.assertFalse(PUBLISHER_INFO["filesystem"]["network"])
 def test_incomplete_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(ValueError): validate_package(d)
 def test_filesystem_publish(self):
  with tempfile.TemporaryDirectory() as d:
   src=Path(d)/"src"; src.mkdir(); self.fixture(src); dst=Path(d)/"out"
   r=get_publisher("filesystem").publish(src,destination=dst)
   self.assertEqual(r["status"],"published"); self.assertTrue((dst/"short.mp4").is_file())
 def test_youtube_is_implemented(self):
  self.assertEqual(get_publisher("youtube").name,"youtube")
 def test_remaining_network_publishers_are_unimplemented(self):
  for name in ("tiktok","instagram"):
   with self.assertRaisesRegex(ValueError,"not implemented"): get_publisher(name)
if __name__=="__main__": unittest.main()
