"""Instagram Reels publishing contract.

The package contains a local MP4, while Instagram's publishing flow consumes a
fetchable media URL. ShortForge therefore requires the caller/staging layer to
provide video_url explicitly; credentials and staging URLs are never persisted
into the qualified package.
"""
from pathlib import Path
from urllib.parse import urlparse
import json, os
from shortforge_publishers import Publisher, validate_package

def resolve_access_token(explicit=None):
    return explicit or os.environ.get("SHORTFORGE_INSTAGRAM_ACCESS_TOKEN")

def validate_video_url(video_url):
    if not video_url: raise ValueError("Instagram publisher requires a fetchable video_url staging URL")
    p=urlparse(video_url)
    if p.scheme!="https" or not p.netloc: raise ValueError("Instagram video_url must be an absolute HTTPS URL")
    return video_url

def build_instagram_plan(package, video_url=None, caption=None, share_to_feed=True):
    root=Path(package); validate_package(root)
    validate_video_url(video_url)
    meta=json.loads((root/"metadata.json").read_text(encoding="utf-8"))
    return {"kind":"ShortForgeInstagramReelsPlan","version":"0.1",
            "local_video":str(root/"short.mp4"),"video_url":video_url,
            "media_type":"REELS","caption":caption if caption is not None else meta.get("title",""),
            "share_to_feed":bool(share_to_feed),
            "requires_remote_fetch":True}

class InstagramPublisher(Publisher):
    name="instagram"
    def publish(self, package, access_token=None, video_url=None, instagram_user_id=None,
                caption=None, share_to_feed=True, dry_run=False, **kwargs):
        plan=build_instagram_plan(package,video_url,caption,share_to_feed)
        if dry_run:
            return {"kind":"ShortForgePublishResult","version":"0.2","publisher":self.name,
                    "status":"dry-run","remote":False,"plan":plan}
        if not resolve_access_token(access_token):
            raise ValueError("Instagram publisher requires OAuth access token or SHORTFORGE_INSTAGRAM_ACCESS_TOKEN")
        if not instagram_user_id:
            raise ValueError("Instagram publisher requires instagram_user_id")
        raise NotImplementedError("Instagram live transport is intentionally gated until the Meta API contract is verified")
