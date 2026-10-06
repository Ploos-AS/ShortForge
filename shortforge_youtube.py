"""YouTube publisher request planning and resumable upload transport."""
from pathlib import Path
import json, urllib.request, urllib.parse
from shortforge_publishers import Publisher, validate_package

UPLOAD_SCOPE="https://www.googleapis.com/auth/youtube.upload"
CAPTION_SCOPE="https://www.googleapis.com/auth/youtube.force-ssl"

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

class YouTubePublisher(Publisher):
    name="youtube"
    def __init__(self, transport=None): self.transport=transport or urllib.request.urlopen
    def publish(self, package, access_token=None, privacy="private", dry_run=False, upload_thumbnail_after=True, **kwargs):
        plan=build_youtube_plan(package,privacy)
        if dry_run: return {"kind":"ShortForgePublishResult","version":"0.1","publisher":"youtube","status":"dry-run","remote":False,"plan":plan}
        if not access_token: raise ValueError("YouTube publisher requires OAuth access token")
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
        return {"kind":"ShortForgePublishResult","version":"0.1","publisher":"youtube","status":"published","remote":True,"video_id":result["id"],"thumbnail_uploaded":thumb}
