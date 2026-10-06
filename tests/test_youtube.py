import os
import json,tempfile,unittest,urllib.error
from pathlib import Path
from shortforge_youtube import build_youtube_plan,build_caption_upload_plan,build_caption_multipart,upload_caption,resumable_upload,resolve_access_token,YouTubePublisher,UPLOAD_SCOPE,CAPTION_SCOPE
class TestYouTube(unittest.TestCase):
 def fixture(self,r):
  for f in ("short.mp4","thumbnail.png","captions.json","manifest.json","render-plan.json","qualification.json"): (r/f).write_bytes(b"x")
  (r/"metadata.json").write_text(json.dumps({"title":"Demo"})); (r/"package.json").write_text(json.dumps({"kind":"ShortForgePublishingPackage","qualified":True})); (r/"captions.srt").write_text("1\\n00:00:00,000 --> 00:00:01,000\\nHei\\n",encoding="utf-8")
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
   if req.get_method()=="PUT": return Response(body=json.dumps({"id":"video-123"}).encode())
   return Response(body=json.dumps({"kind":"youtube#thumbnailSetResponse"}).encode())
  with tempfile.TemporaryDirectory() as d:
   r=Path(d); self.fixture(r); result=YouTubePublisher(transport).publish(r,access_token="token")
   self.assertEqual(result["video_id"],"video-123"); self.assertEqual([x.get_method() for x in calls],["POST","PUT","POST"])
   self.assertIn("uploadType=resumable",calls[0].full_url); self.assertEqual(calls[1].full_url,"https://upload.example/session"); self.assertIn("thumbnails/set?videoId=video-123",calls[2].full_url)
 def test_caption_plan_requires_stronger_scope(self):
  p=build_caption_upload_plan("v","captions.srt",language="no")
  self.assertEqual(p["scope"],CAPTION_SCOPE); self.assertEqual(p["language"],"no")
 def test_caption_multipart_upload(self):
  class R:
   headers={}
   def __enter__(self): return self
   def __exit__(self,*a): pass
   def read(self): return json.dumps({"id":"caption-123"}).encode()
  calls=[]
  def transport(req): calls.append(req); return R()
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"captions.srt"; p.write_text("1\\n00:00:00,000 --> 00:00:01,000\\nHei\\n",encoding="utf-8")
   result=upload_caption("video-123",p,"caption-token",language="no",transport=transport)
   self.assertEqual(result["caption_id"],"caption-123"); self.assertEqual(result["language"],"no")
   self.assertIn("uploadType=multipart",calls[0].full_url); self.assertIn("multipart/related",calls[0].headers["Content-type"])
   self.assertIn(b'"videoId":"video-123"',calls[0].data); self.assertIn(b"Hei",calls[0].data)
 def test_caption_requires_token(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"c.srt"; p.write_text("x")
   with self.assertRaisesRegex(ValueError,"youtube.force-ssl"): upload_caption("v",p,None)
 def test_integrated_caption_and_result_file(self):
  class Response:
   def __init__(self,headers=None,body=b""): self.headers=headers or {}; self.body=body
   def __enter__(self): return self
   def __exit__(self,*a): pass
   def read(self): return self.body
  calls=[]
  def transport(req):
   calls.append(req)
   if "videos?uploadType=resumable" in req.full_url: return Response({"Location":"https://upload.example/session"})
   if req.full_url=="https://upload.example/session": return Response(body=json.dumps({"id":"video-456"}).encode())
   if "captions?" in req.full_url: return Response(body=json.dumps({"id":"caption-456"}).encode())
   return Response(body=b"{}")
  with tempfile.TemporaryDirectory() as d:
   r=Path(d); self.fixture(r); out=r/"publish-result.json"
   result=YouTubePublisher(transport).publish(r,access_token="upload-token",caption_access_token="caption-token",upload_captions_after=True,caption_language="no",result_file=out)
   self.assertEqual(result["video_url"],"https://youtu.be/video-456"); self.assertEqual(result["caption"]["caption_id"],"caption-456")
   self.assertEqual(json.loads(out.read_text())["video_id"],"video-456")
   self.assertEqual(len(calls),4)
 def test_resolve_token_from_environment(self):
  from shortforge_youtube import resolve_access_token
  old=os.environ.get("SHORTFORGE_YOUTUBE_ACCESS_TOKEN"); os.environ["SHORTFORGE_YOUTUBE_ACCESS_TOKEN"]="env-token"
  try: self.assertEqual(resolve_access_token(),"env-token")
  finally:
   if old is None: os.environ.pop("SHORTFORGE_YOUTUBE_ACCESS_TOKEN",None)
   else: os.environ["SHORTFORGE_YOUTUBE_ACCESS_TOKEN"]=old
 def test_resume_after_retriable_failure(self):
  class Response:
   def __init__(self,body=b"",headers=None): self.body=body; self.headers=headers or {}
   def __enter__(self): return self
   def __exit__(self,*a): pass
   def read(self): return self.body
  calls=[]
  def transport(req):
   calls.append(req)
   if len(calls)==1: raise urllib.error.HTTPError(req.full_url,503,"busy",{},None)
   if len(calls)==2: raise urllib.error.HTTPError(req.full_url,308,"resume",{"Range":"bytes=0-3"},None)
   return Response(json.dumps({"id":"resumed-video"}).encode())
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"v.mp4"; p.write_bytes(b"abcdefgh")
   sleeps=[]; result=resumable_upload("https://upload.example/session",p,"token",transport,max_retries=2,sleep=sleeps.append)
   self.assertEqual(result["id"],"resumed-video"); self.assertEqual(sleeps,[1])
   self.assertEqual(calls[1].headers["Content-range"],"bytes */8")
   self.assertEqual(calls[2].headers["Content-range"],"bytes 4-7/8"); self.assertEqual(calls[2].data,b"efgh")
 def test_requires_token_for_network(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d); self.fixture(r)
   with self.assertRaises(ValueError): YouTubePublisher().publish(r)
if __name__=="__main__": unittest.main()
