"""Provider-neutral publishing contracts for ShortForge delivery packages."""
from pathlib import Path
from abc import ABC, abstractmethod
import json, shutil

PUBLISHER_INFO={
 "filesystem":{"network":False,"implemented":True,"requires_auth":False,"supports":["video","thumbnail","captions","metadata"]},
 "youtube":{"network":True,"implemented":False,"requires_auth":True,"supports":["video","thumbnail","metadata","captions"]},
 "tiktok":{"network":True,"implemented":False,"requires_auth":True,"supports":["video","metadata"]},
 "instagram":{"network":True,"implemented":False,"requires_auth":True,"supports":["video","thumbnail","metadata"]},
}
REQUIRED_PACKAGE_FILES={"package.json","short.mp4","thumbnail.png","captions.json","metadata.json","manifest.json","render-plan.json","qualification.json"}

def validate_package(path):
    root=Path(path)
    missing=sorted(x for x in REQUIRED_PACKAGE_FILES if not (root/x).is_file())
    if missing: raise ValueError("incomplete publishing package: "+", ".join(missing))
    package=json.loads((root/"package.json").read_text(encoding="utf-8"))
    if package.get("kind")!="ShortForgePublishingPackage" or not package.get("qualified"): raise ValueError("package is not qualified")
    return package

class Publisher(ABC):
    name="publisher"
    @abstractmethod
    def publish(self, package, **kwargs): raise NotImplementedError

class FilesystemPublisher(Publisher):
    name="filesystem"
    def publish(self, package, destination=None, **kwargs):
        src=Path(package); validate_package(src)
        if destination is None: raise ValueError("filesystem publisher requires destination")
        dst=Path(destination)
        if dst.exists(): raise ValueError("destination already exists")
        shutil.copytree(src,dst)
        return {"kind":"ShortForgePublishResult","version":"0.1","publisher":self.name,"status":"published","remote":False,"destination":str(dst)}

def get_publisher(name):
    if name=="filesystem": return FilesystemPublisher()
    if name in PUBLISHER_INFO: raise ValueError(f"publisher not implemented: {name}")
    raise ValueError(f"unknown publisher: {name}")
