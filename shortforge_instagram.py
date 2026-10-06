"""Instagram Reels publishing contract.

The package contains a local MP4, while Instagram's publishing flow consumes a
fetchable media URL. ShortForge therefore requires the caller/staging layer to
provide video_url explicitly; credentials and staging URLs are never persisted
into the qualified package.
"""
from pathlib import Path
from urllib.parse import urlparse
import json, os, time, urllib.request, urllib.parse
from shortforge_publishers import Publisher, validate_package

def resolve_access_token(explicit=None):
    return explicit or os.environ.get("SHORTFORGE_INSTAGRAM_ACCESS_TOKEN")

def validate_video_url(video_url):
    if not video_url: raise ValueError("Instagram publisher requires a fetchable video_url staging URL")
    p=urlparse(video_url)
    if p.scheme!="https" or not p.netloc: raise ValueError("Instagram video_url must be an absolute HTTPS URL")
    return video_url

GRAPH_VERSION=os.environ.get("SHORTFORGE_INSTAGRAM_GRAPH_VERSION","v25.0")
GRAPH_BASE="https://graph.facebook.com"

def _request_json(url,token,method="GET",data=None,transport=urllib.request.urlopen):
    headers={"Authorization":"Bearer "+token}
    if data is not None:
        data=urllib.parse.urlencode(data).encode(); headers["Content-Type"]="application/x-www-form-urlencoded"
    req=urllib.request.Request(url,data=data,method=method,headers=headers)
    with transport(req) as resp: result=json.loads(resp.read().decode())
    if "error" in result: raise ValueError("Instagram API error: "+str(result["error"].get("message",result["error"])))
    return result

def build_instagram_plan(package, video_url=None, caption=None, share_to_feed=True):
    root=Path(package); validate_package(root)
    validate_video_url(video_url)
    meta=json.loads((root/"metadata.json").read_text(encoding="utf-8"))
    return {"kind":"ShortForgeInstagramReelsPlan","version":"0.1",
            "local_video":str(root/"short.mp4"),"video_url":video_url,
            "media_type":"REELS","caption":caption if caption is not None else meta.get("title",""),
            "share_to_feed":bool(share_to_feed),
            "requires_remote_fetch":True}

def create_reel_container(plan,user_id,token,transport=urllib.request.urlopen,graph_version=GRAPH_VERSION):
    data={"media_type":"REELS","video_url":plan["video_url"],"caption":plan["caption"],"share_to_feed":str(plan["share_to_feed"]).lower()}
    result=_request_json(f"{GRAPH_BASE}/{graph_version}/{user_id}/media",token,"POST",data,transport)
    if not result.get("id"): raise ValueError("Instagram container response missing id")
    return result["id"]

def fetch_container_status(container_id,token,transport=urllib.request.urlopen,graph_version=GRAPH_VERSION):
    result=_request_json(f"{GRAPH_BASE}/{graph_version}/{container_id}?fields=status_code,status",token,transport=transport)
    code=result.get("status_code")
    if not code: raise ValueError("Instagram container response missing status_code")
    return {"status_code":code,"status":result.get("status"),"terminal":code in ("FINISHED","ERROR","EXPIRED","PUBLISHED")}

def wait_for_container(container_id,token,transport=urllib.request.urlopen,max_attempts=5,interval_seconds=2,sleep=time.sleep,graph_version=GRAPH_VERSION):
    history=[]
    for attempt in range(max_attempts):
        status=fetch_container_status(container_id,token,transport,graph_version); history.append(status)
        if status["status_code"]=="FINISHED": return status,history
        if status["status_code"] in ("ERROR","EXPIRED"): raise ValueError("Instagram container "+status["status_code"]+": "+str(status.get("status")))
        if attempt+1<max_attempts: sleep(interval_seconds)
    raise ValueError("Instagram container not ready within polling budget")

def publish_container(container_id,user_id,token,transport=urllib.request.urlopen,graph_version=GRAPH_VERSION):
    result=_request_json(f"{GRAPH_BASE}/{graph_version}/{user_id}/media_publish",token,"POST",{"creation_id":container_id},transport)
    if not result.get("id"): raise ValueError("Instagram publish response missing media id")
    return result["id"]

class InstagramPublisher(Publisher):
    name="instagram"
    def publish(self, package, access_token=None, video_url=None, instagram_user_id=None,
                caption=None, share_to_feed=True, dry_run=False, **kwargs):
        plan=build_instagram_plan(package,video_url,caption,share_to_feed)
        if dry_run:
            return {"kind":"ShortForgePublishResult","version":"0.2","publisher":self.name,
                    "status":"dry-run","remote":False,"plan":plan}
        token=resolve_access_token(access_token)
        if not token: raise ValueError("Instagram publisher requires OAuth access token or SHORTFORGE_INSTAGRAM_ACCESS_TOKEN")
        if not instagram_user_id: raise ValueError("Instagram publisher requires instagram_user_id")
        transport=kwargs.get("transport") or urllib.request.urlopen
        container_id=create_reel_container(plan,instagram_user_id,token,transport)
        ready,history=wait_for_container(container_id,token,transport,max_attempts=kwargs.get("max_attempts",5),interval_seconds=kwargs.get("interval_seconds",2),sleep=kwargs.get("sleep",time.sleep))
        media_id=publish_container(container_id,instagram_user_id,token,transport)
        return {"kind":"ShortForgePublishResult","version":"0.2","publisher":self.name,"status":"published","remote":True,"container_id":container_id,"media_id":media_id,"container_status":ready,"status_checks":len(history)}
