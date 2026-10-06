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
 def test_mocked_resumable_upload(self):
  class Response:
   def __init__(self,headers=None,body=b""): self.headers=headers or {}; self.body=body
   def __enter__(self): return self
   def __exit__(self,*a): pass
   def read(self): return self.body
  calls=[]
  def transport(req):
   calls.append(req)
   if req.get_method()=="POST": return Response({"Location":"https://upload.example/session"})
   return Response(body=json.dumps({"id":"video-123"}).encode())
  with tempfile.TemporaryDirectory() as d:
   r=Path(d); self.fixture(r); result=YouTubePublisher(transport).publish(r,access_token="token")
   self.assertEqual(result["video_id"],"video-123"); self.assertEqual([x.get_method() for x in calls],["POST","PUT"])
   self.assertIn("uploadType=resumable",calls[0].full_url); self.assertEqual(calls[1].full_url,"https://upload.example/session")
 def test_requires_token_for_network(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d); self.fixture(r)
   with self.assertRaises(ValueError): YouTubePublisher().publish(r)
if __name__=="__main__": unittest.main()
