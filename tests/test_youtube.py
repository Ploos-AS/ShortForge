import json,tempfile,unittest
from pathlib import Path
from shortforge_youtube import build_youtube_plan,YouTubePublisher,UPLOAD_SCOPE
class TestYouTube(unittest.TestCase):
 def fixture(self,r):
  for f in ("short.mp4","thumbnail.png","captions.json","manifest.json","render-plan.json","qualification.json"): (r/f).write_bytes(b"x")
  (r/"metadata.json").write_text(json.dumps({"title":"Demo"})); (r/"package.json").write_text(json.dumps({"kind":"ShortForgePublishingPackage","qualified":True}))
 def test_dry_run(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d); self.fixture(r); x=YouTubePublisher().publish(r,privacy="unlisted",dry_run=True)
   self.assertEqual(x["status"],"dry-run"); self.assertEqual(x["plan"]["body"]["status"]["privacyStatus"],"unlisted"); self.assertEqual(x["plan"]["scope"],UPLOAD_SCOPE)
 def test_requires_token_for_network(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d); self.fixture(r)
   with self.assertRaises(ValueError): YouTubePublisher().publish(r)
if __name__=="__main__": unittest.main()
