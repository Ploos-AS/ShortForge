"""YouTube publisher request planning and resumable upload transport."""
from pathlib import Path
import json, os, urllib.request, urllib.parse
from shortforge_publishers import Publisher, validate_package

UPLOAD_SCOPE="https://www.googleapis.com/auth/youtube.upload"
CAPTION_SCOPE="https://www.googleapis.com/auth/youtube.force-ssl"

def resolve_access_token(explicit=None, env_name="SHORTFORGE_YOUTUBE_ACCESS_TOKEN"):
    """Resolve a bearer token without persisting it in ShortForge artifacts."""
    return explicit or os.environ.get(env_name)

def build_youtube_plan(package, privacy="private"):
    root=Path(package); validate_package(root)
    if privacy not in ("private","unlisted","public"): raise ValueError("invalid YouTube privacy")
    meta=json.loads((root/"metadata.json").read_text(encoding="utf-8"))
    body={"snippet":{"title":meta.get("title","ShortForge video"),"description":meta.get("description","")},"status":{"privacyStatus":privacy}}
    return {"kind":"ShortForgeYouTubePublishPlan","version":"0.1","video":str(root/"short.mp4"),"thumbnail":str(root/"thumbnail.png"),"body":body,"scope":UPLOAD_SCOPE,"caption_scope":CAPTION_SCOPE,"resumable":True}

def upload_thumbnail(video_id,thumbnail,access_token,transport=urllib.request.urlopen):
    path=Path(thumbnail); data=path.read_bytes()
    url="https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId="+urllib.parse.quote(video_id)
    req=urllib.request.Request(url,data=data,method="POST",headers={"Authorization":"Bearer "+access_token,"Content-Type":"image/png","Content-Length":str(len(data))})
    with transport(req) as resp: return json.loads(resp.read().decode() or "{}")

def build_caption_upload_plan(video_id,caption_file,language="en",name="ShortForge"):
    return {"video_id":video_id,"caption_file":str(caption_file),"language":language,"name":name,"scope":CAPTION_SCOPE,"endpoint":"https://www.googleapis.com/upload/youtube/v3/captions?part=snippet"}

def build_caption_multipart(video_id,caption_file,language="en",name="ShortForge",boundary="shortforge-caption-boundary"):
    path=Path(caption_file)
    if not path.is_file(): raise ValueError("caption file not found")
    if path.stat().st_size > 100*1024*1024: raise ValueError("caption file exceeds YouTube 100 MB limit")
    meta=json.dumps({"snippet":{"videoId":video_id,"language":language,"name":name}},separators=(",",":")).encode()
    media=path.read_bytes()
    crlf=b"\r\n"; b=boundary.encode()
    body=(b"--"+b+crlf+b"Content-Type: application/json; charset=UTF-8"+crlf+crlf+meta+crlf+
          b"--"+b+crlf+b"Content-Type: application/octet-stream"+crlf+crlf+media+crlf+b"--"+b+b"--"+crlf)
    return body,"multipart/related; boundary="+boundary

def upload_caption(video_id,caption_file,access_token,language="en",name="ShortForge",transport=urllib.request.urlopen):
    if not access_token: raise ValueError("YouTube caption upload requires OAuth access token with youtube.force-ssl")
    body,content_type=build_caption_multipart(video_id,caption_file,language,name)
    url="https://www.googleapis.com/upload/youtube/v3/captions?part=snippet&uploadType=multipart"
    req=urllib.request.Request(url,data=body,method="POST",headers={"Authorization":"Bearer "+access_token,"Content-Type":content_type,"Content-Length":str(len(body))})
    with transport(req) as resp: result=json.loads(resp.read().decode())
    if "id" not in result: raise ValueError("YouTube caption response missing caption id")
    return {"kind":"ShortForgeCaptionPublishResult","version":"0.1","status":"published","caption_id":result["id"],"video_id":video_id,"language":language}

class YouTubePublisher(Publisher):
    name="youtube"
    def __init__(self, transport=None): self.transport=transport or urllib.request.urlopen
    def publish(self, package, access_token=None, caption_access_token=None, privacy="private", dry_run=False, upload_thumbnail_after=True, upload_captions_after=False, caption_language="en", result_file=None, **kwargs):
        plan=build_youtube_plan(package,privacy)
        if dry_run: return {"kind":"ShortForgePublishResult","version":"0.2","publisher":"youtube","status":"dry-run","remote":False,"plan":plan}
        access_token=resolve_access_token(access_token)
        if not access_token: raise ValueError("YouTube publisher requires OAuth access token or SHORTFORGE_YOUTUBE_ACCESS_TOKEN")
        video=Path(plan["video"]); data=json.dumps(plan["body"]).encode()
        url="https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status"
        req=urllib.request.Request(url,data=data,method="POST",headers={"Authorization":"Bearer "+access_token,"Content-Type":"application/json; charset=UTF-8","X-Upload-Content-Length":str(video.stat().st_size),"X-Upload-Content-Type":"video/mp4"})
        with self.transport(req) as resp: location=resp.headers.get("Location")
        if not location: raise ValueError("YouTube resumable session missing Location")
        put=urllib.request.Request(location,data=video.read_bytes(),method="PUT",headers={"Authorization":"Bearer "+access_token,"Content-Type":"video/mp4","Content-Length":str(video.stat().st_size)})
        with self.transport(put) as resp: result=json.loads(resp.read().decode())
        if "id" not in result: raise ValueError("YouTube upload response missing video id")
        thumb=False
        if upload_thumbnail_after:
            upload_thumbnail(result["id"],plan["thumbnail"],access_token,self.transport); thumb=True
        caption_result=None
        if upload_captions_after:
            caption=Path(package)/"captions.srt"
            if not caption.is_file(): raise ValueError("publishing package has no captions.srt")
            caption_access_token=resolve_access_token(caption_access_token,"SHORTFORGE_YOUTUBE_CAPTION_ACCESS_TOKEN")
            if not caption_access_token: raise ValueError("YouTube caption upload requires separate OAuth token with youtube.force-ssl")
            caption_result=upload_caption(result["id"],caption,caption_access_token,caption_language,transport=self.transport)
        publish_result={"kind":"ShortForgePublishResult","version":"0.2","publisher":"youtube","status":"published","remote":True,"video_id":result["id"],"video_url":"https://youtu.be/"+result["id"],"thumbnail_uploaded":thumb,"caption":caption_result}
        if result_file:
            Path(result_file).write_text(json.dumps(publish_result,indent=2)+"\\n",encoding="utf-8")
        return publish_result
