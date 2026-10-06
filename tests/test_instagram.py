import json,tempfile,unittest
from pathlib import Path
from shortforge_instagram import build_instagram_plan,InstagramPublisher

class TestInstagram(unittest.TestCase):
 def fixture(self,r):
  for f in ("thumbnail.png","captions.json","manifest.json","render-plan.json","qualification.json"): (r/f).write_bytes(b"x")
  (r/"short.mp4").write_bytes(b"video")
  (r/"metadata.json").write_text(json.dumps({"title":"Demo Reel"}))
  (r/"package.json").write_text(json.dumps({"kind":"ShortForgePublishingPackage","qualified":True}))
 def test_requires_https_staging_url(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d); self.fixture(r)
   with self.assertRaises(ValueError): build_instagram_plan(r)
   with self.assertRaises(ValueError): build_instagram_plan(r,"http://example.test/a.mp4")
 def test_dry_run_plan(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d); self.fixture(r)
   x=InstagramPublisher().publish(r,video_url="https://cdn.example.test/a.mp4",dry_run=True)
   self.assertEqual(x["plan"]["media_type"],"REELS"); self.assertTrue(x["plan"]["requires_remote_fetch"])
 def test_live_transport_is_gated(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d); self.fixture(r)
   with self.assertRaises(NotImplementedError):
    InstagramPublisher().publish(r,video_url="https://cdn.example.test/a.mp4",access_token="token",instagram_user_id="123")
if __name__=="__main__": unittest.main()
