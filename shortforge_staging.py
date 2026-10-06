"""Provider-neutral temporary media staging contracts."""
from abc import ABC, abstractmethod
from pathlib import Path
from urllib.parse import urlparse
import hashlib, shutil, time

STAGER_INFO={
 "filesystem":{"network":False,"implemented":True,"temporary_url":False},
}

def validate_staged_url(url):
    p=urlparse(url)
    if p.scheme!="https" or not p.netloc: raise ValueError("staged media URL must be absolute HTTPS")
    return url

class MediaStager(ABC):
    name="stager"
    @abstractmethod
    def stage(self,source,**kwargs): raise NotImplementedError

class FilesystemStager(MediaStager):
    """Deterministic qualification stager; does not pretend to provide a public URL."""
    name="filesystem"
    def stage(self,source,destination=None,**kwargs):
        src=Path(source)
        if not src.is_file(): raise ValueError("staging source not found")
        if destination is None: raise ValueError("filesystem stager requires destination")
        dst=Path(destination)
        if dst.exists(): raise ValueError("staging destination already exists")
        dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst)
        digest=hashlib.sha256(dst.read_bytes()).hexdigest()
        return {"kind":"ShortForgeStagedMedia","version":"0.1","provider":self.name,"source":str(src),"artifact":str(dst),"sha256":digest,"bytes":dst.stat().st_size,"url":None,"temporary":False}

class HTTPSURLStager(MediaStager):
    """Adapter for an external staging layer that has already produced a URL."""
    name="https-url"
    def stage(self,source,url=None,expires_at=None,**kwargs):
        src=Path(source)
        if not src.is_file(): raise ValueError("staging source not found")
        validate_staged_url(url)
        if expires_at is not None and float(expires_at)<=time.time(): raise ValueError("staged media URL is already expired")
        return {"kind":"ShortForgeStagedMedia","version":"0.1","provider":self.name,"source":str(src),"bytes":src.stat().st_size,"url":url,"expires_at":expires_at,"temporary":expires_at is not None}

def get_stager(name):
    if name=="filesystem": return FilesystemStager()
    if name=="https-url": return HTTPSURLStager()
    raise ValueError("unknown media stager: "+str(name))
