import json,tempfile,unittest
from pathlib import Path
from shortforge_tiktok import build_tiktok_plan,fetch_publish_status,poll_publish_status,TikTokPublisher,PUBLISH_SCOPE

class TestTikTok(unittest.TestCase):
 def fixture(self,r):
  for f in ("thumbnail.png","captions.json","manifest.json","render-plan.json","qualification.json"): (r/f).write_bytes(b"x")
  (r/"short.mp4").write_bytes(b"video")
  (r/"metadata.json").write_text(json.dumps({"title":"Demo #short"}))
  (r/"package.json").write_text(json.dumps({"kind":"ShortForgePublishingPackage","qualified":True}))
 def test_plan_defaults_private(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d); self.fixture(r); p=build_tiktok_plan(r)
   self.assertEqual(p["scope"],PUBLISH_SCOPE); self.assertEqual(p["body"]["post_info"]["privacy_level"],"SELF_ONLY")
   self.assertEqual(p["body"]["source_info"]["source"],"FILE_UPLOAD")
 def test_dry_run(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d); self.fixture(r); x=TikTokPublisher().publish(r,dry_run=True)
   self.assertEqual(x["status"],"dry-run"); self.assertFalse(x["remote"])
 def test_mocked_direct_post(self):
  class R:
   def __init__(self,body=b""): self.body=body; self.headers={}
   def __enter__(self): return self
   def __exit__(self,*a): pass
   def read(self): return self.body
  calls=[]
  def transport(req):
   calls.append(req)
   if "creator_info/query" in req.full_url:
    return R(json.dumps({"data":{"creator_username":"tester","privacy_level_options":["SELF_ONLY"],"max_video_post_duration_sec":300},"error":{"code":"ok"}}).encode())
   if "video/init" in req.full_url:
    return R(json.dumps({"data":{"publish_id":"pub-123","upload_url":"https://upload.example/tiktok"},"error":{"code":"ok"}}).encode())
   return R()
  with tempfile.TemporaryDirectory() as d:
   r=Path(d); self.fixture(r); out=r/"result.json"
   x=TikTokPublisher(transport).publish(r,access_token="token",result_file=out,is_aigc=True)
   self.assertEqual(x["publish_id"],"pub-123"); self.assertEqual(x["status"],"submitted")
   self.assertEqual([q.get_method() for q in calls],["POST","POST","PUT"])
   self.assertEqual(calls[2].headers["Content-range"],"bytes 0-4/5")
   self.assertTrue(json.loads(calls[1].data)["post_info"]["is_aigc"])
   self.assertEqual(json.loads(out.read_text())["publish_id"],"pub-123"); self.assertEqual(x["creator_username"],"tester")
 def test_rejects_unavailable_privacy(self):
  class R:
   def __enter__(self): return self
   def __exit__(self,*a): pass
   def read(self): return json.dumps({"data":{"privacy_level_options":["SELF_ONLY"]},"error":{"code":"ok"}}).encode()
  with tempfile.TemporaryDirectory() as d:
   r=Path(d); self.fixture(r)
   with self.assertRaisesRegex(ValueError,"privacy level"): TikTokPublisher(lambda req:R()).publish(r,access_token="token",privacy_level="PUBLIC_TO_EVERYONE")
 def test_status_poll_completes(self):
  class R:
   def __init__(self,body): self.body=body
   def __enter__(self): return self
   def __exit__(self,*a): pass
   def read(self): return self.body
  states=iter(["PROCESSING_UPLOAD","PUBLISH_COMPLETE"]); calls=[]
  def transport(req):
   calls.append(req); status=next(states)
   return R(json.dumps({"data":{"status":status,"uploaded_bytes":5,"publicaly_available_post_id":[123] if status=="PUBLISH_COMPLETE" else []},"error":{"code":"ok"}}).encode())
  sleeps=[]; result=poll_publish_status("pub-1","token",transport,max_attempts=3,interval_seconds=2,sleep=sleeps.append)
  self.assertTrue(result["terminal"]); self.assertEqual(result["attempts"],2); self.assertEqual(result["result"]["status"],"PUBLISH_COMPLETE")
  self.assertEqual(result["result"]["post_ids"],[123]); self.assertEqual(sleeps,[2]); self.assertEqual(len(calls),2)
 def test_status_poll_failed_reason(self):
  class R:
   def __enter__(self): return self
   def __exit__(self,*a): pass
   def read(self): return json.dumps({"data":{"status":"FAILED","fail_reason":"duration_check_failed"},"error":{"code":"ok"}}).encode()
  result=fetch_publish_status("pub-2","token",lambda req:R())
  self.assertTrue(result["terminal"]); self.assertEqual(result["fail_reason"],"duration_check_failed")
 def test_status_poll_enforces_rate_floor(self):
  with self.assertRaisesRegex(ValueError,"rate limit"): poll_publish_status("p","t",max_attempts=1,interval_seconds=1)
 def test_requires_token(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d); self.fixture(r)
   with self.assertRaises(ValueError): TikTokPublisher().publish(r)
if __name__=="__main__": unittest.main()
