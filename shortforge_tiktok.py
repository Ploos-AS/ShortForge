"""TikTok Content Posting API publisher."""
from pathlib import Path
import json, os, time, urllib.request
from shortforge_publishers import Publisher, validate_package

PUBLISH_SCOPE="video.publish"
INIT_URL="https://open.tiktokapis.com/v2/post/publish/video/init/"
CREATOR_INFO_URL="https://open.tiktokapis.com/v2/post/publish/creator_info/query/"
STATUS_URL="https://open.tiktokapis.com/v2/post/publish/status/fetch/"

def resolve_access_token(explicit=None):
    return explicit or os.environ.get("SHORTFORGE_TIKTOK_ACCESS_TOKEN")

def build_tiktok_plan(package, privacy_level="SELF_ONLY", title=None, is_aigc=False):
    root=Path(package); validate_package(root)
    video=root/"short.mp4"; meta=json.loads((root/"metadata.json").read_text(encoding="utf-8"))
    title=title if title is not None else meta.get("title","")
    if len(title.encode("utf-16-le"))//2 > 2200: raise ValueError("TikTok title exceeds 2200 UTF-16 code units")
    size=video.stat().st_size
    body={"post_info":{"title":title,"privacy_level":privacy_level,"disable_duet":False,"disable_comment":False,"disable_stitch":False,"is_aigc":bool(is_aigc)},
          "source_info":{"source":"FILE_UPLOAD","video_size":size,"chunk_size":size,"total_chunk_count":1}}
    return {"kind":"ShortForgeTikTokPublishPlan","version":"0.1","video":str(video),"scope":PUBLISH_SCOPE,"body":body}

def query_creator_info(access_token,transport=urllib.request.urlopen):
    req=urllib.request.Request(CREATOR_INFO_URL,data=b"",method="POST",headers={"Authorization":"Bearer "+access_token,"Content-Type":"application/json; charset=UTF-8"})
    with transport(req) as resp: result=json.loads(resp.read().decode())
    error=result.get("error",{})
    if error.get("code") not in (None,"ok"): raise ValueError("TikTok creator info failed: "+str(error.get("code")))
    data=result.get("data",{})
    if not data.get("privacy_level_options"): raise ValueError("TikTok creator info missing privacy options")
    return data

def fetch_publish_status(publish_id,access_token,transport=urllib.request.urlopen):
    if not publish_id: raise ValueError("TikTok publish_id is required")
    if not access_token: raise ValueError("TikTok status requires OAuth access token")
    payload=json.dumps({"publish_id":publish_id}).encode()
    req=urllib.request.Request(STATUS_URL,data=payload,method="POST",headers={"Authorization":"Bearer "+access_token,"Content-Type":"application/json; charset=UTF-8"})
    with transport(req) as resp: result=json.loads(resp.read().decode())
    error=result.get("error",{})
    if error.get("code") not in (None,"ok"): raise ValueError("TikTok status failed: "+str(error.get("code")))
    data=result.get("data",{})
    if not data.get("status"): raise ValueError("TikTok status response missing status")
    return {"kind":"ShortForgeTikTokStatus","version":"0.1","publish_id":publish_id,"status":data["status"],"terminal":data["status"] in ("PUBLISH_COMPLETE","FAILED"),"fail_reason":data.get("fail_reason"),"post_ids":data.get("publicaly_available_post_id",[]),"uploaded_bytes":data.get("uploaded_bytes")}

def poll_publish_status(publish_id,access_token,transport=urllib.request.urlopen,max_attempts=5,interval_seconds=2.0,sleep=time.sleep):
    if max_attempts<1: raise ValueError("max_attempts must be >= 1")
    if interval_seconds<2.0: raise ValueError("interval_seconds must be >= 2 to respect TikTok status rate limit")
    history=[]
    for attempt in range(max_attempts):
        status=fetch_publish_status(publish_id,access_token,transport); history.append(status)
        if status["terminal"]: return {"kind":"ShortForgeTikTokStatusPoll","version":"0.1","publish_id":publish_id,"terminal":True,"attempts":len(history),"result":status,"history":history}
        if attempt+1<max_attempts: sleep(interval_seconds)
    return {"kind":"ShortForgeTikTokStatusPoll","version":"0.1","publish_id":publish_id,"terminal":False,"attempts":len(history),"result":history[-1],"history":history}

class TikTokPublisher(Publisher):
    name="tiktok"
    def __init__(self, transport=None): self.transport=transport or urllib.request.urlopen
    def publish(self, package, access_token=None, privacy_level="SELF_ONLY", title=None, is_aigc=False, dry_run=False, result_file=None, **kwargs):
        plan=build_tiktok_plan(package,privacy_level,title,is_aigc)
        if dry_run: return {"kind":"ShortForgePublishResult","version":"0.2","publisher":"tiktok","status":"dry-run","remote":False,"plan":plan}
        token=resolve_access_token(access_token)
        if not token: raise ValueError("TikTok publisher requires OAuth access token or SHORTFORGE_TIKTOK_ACCESS_TOKEN")
        creator=query_creator_info(token,self.transport)
        if privacy_level not in creator["privacy_level_options"]: raise ValueError("TikTok privacy level is not available for this creator")
        meta=json.loads((Path(package)/"metadata.json").read_text(encoding="utf-8"))
        duration=float(meta.get("duration_seconds",0) or 0)
        max_duration=creator.get("max_video_post_duration_sec")
        if max_duration is not None and duration>float(max_duration): raise ValueError("video exceeds creator TikTok maximum duration")
        payload=json.dumps(plan["body"]).encode()
        req=urllib.request.Request(INIT_URL,data=payload,method="POST",headers={"Authorization":"Bearer "+token,"Content-Type":"application/json; charset=UTF-8"})
        with self.transport(req) as resp: init=json.loads(resp.read().decode())
        error=init.get("error",{})
        if error.get("code") not in (None,"ok"): raise ValueError("TikTok init failed: "+str(error.get("code")))
        data=init.get("data",{}); publish_id=data.get("publish_id"); upload_url=data.get("upload_url")
        if not publish_id or not upload_url: raise ValueError("TikTok init response missing publish_id or upload_url")
        video=Path(plan["video"]); media=video.read_bytes(); size=len(media)
        put=urllib.request.Request(upload_url,data=media,method="PUT",headers={"Content-Type":"video/mp4","Content-Length":str(size),"Content-Range":f"bytes 0-{size-1}/{size}"})
        with self.transport(put) as resp: resp.read()
        result={"kind":"ShortForgePublishResult","version":"0.2","publisher":"tiktok","status":"submitted","remote":True,"publish_id":publish_id,"processing":True,"creator_username":creator.get("creator_username")}
        if result_file: Path(result_file).write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
        return result
