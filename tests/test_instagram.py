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
 def test_mocked_reels_publish(self):
  class R:
   def __init__(self,body): self.body=body
   def __enter__(self): return self
   def __exit__(self,*a): pass
   def read(self): return self.body
  calls=[]; states=iter(["IN_PROGRESS","FINISHED"])
  def transport(req):
   calls.append(req)
   if req.full_url.endswith("/123/media"): return R(json.dumps({"id":"container-1"}).encode())
   if "container-1?fields=" in req.full_url: return R(json.dumps({"status_code":next(states),"status":"ok"}).encode())
   if req.full_url.endswith("/123/media_publish"): return R(json.dumps({"id":"media-1"}).encode())
   raise AssertionError(req.full_url)
  with tempfile.TemporaryDirectory() as d:
   r=Path(d); self.fixture(r); sleeps=[]
   x=InstagramPublisher().publish(r,video_url="https://cdn.example.test/a.mp4",access_token="token",instagram_user_id="123",transport=transport,sleep=sleeps.append)
   self.assertEqual(x["media_id"],"media-1"); self.assertEqual(x["container_id"],"container-1"); self.assertEqual(x["status_checks"],2); self.assertEqual(sleeps,[2])
   self.assertEqual([q.get_method() for q in calls],["POST","GET","GET","POST"])
if __name__=="__main__": unittest.main()
