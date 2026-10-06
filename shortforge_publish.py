"""Build a self-contained ShortForge publishing package."""
from pathlib import Path
import json, shutil, subprocess
from shortforge_qualify import qualify_video

def build_publish_package(root, destination="publish", title=None):
    root=Path(root); dest=root/destination
    video=root/"output/short.mp4"; plan_file=root/"render-plan.json"; manifest_file=root/"manifest.json"
    if not video.is_file(): raise ValueError("rendered video not found")
    if not plan_file.is_file() or not manifest_file.is_file(): raise ValueError("render plan or manifest not found")
    plan=json.loads(plan_file.read_text(encoding="utf-8")); manifest=json.loads(manifest_file.read_text(encoding="utf-8"))
    report=qualify_video(video,plan.get("duration_seconds"))
    if not report["passed"]: raise ValueError("render qualification failed")
    dest.mkdir(parents=True,exist_ok=True)
    shutil.copy2(video,dest/"short.mp4"); shutil.copy2(plan_file,dest/"render-plan.json"); shutil.copy2(manifest_file,dest/"manifest.json")
    captions=[a for a in manifest.get("assets",[]) if a.get("type")=="caption"]
    (dest/"captions.json").write_text(json.dumps(captions,indent=2)+"\n",encoding="utf-8")
    metadata={"kind":"ShortForgePublishingMetadata","version":"0.1","title":title or manifest.get("title") or "ShortForge video","production_profile":plan.get("features",{}).get("production_profile","generic-vertical"),"duration_seconds":plan.get("duration_seconds"),"format":"9:16"}
    (dest/"metadata.json").write_text(json.dumps(metadata,indent=2)+"\n",encoding="utf-8")
    (dest/"qualification.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    thumb=dest/"thumbnail.png"
    if not shutil.which("ffmpeg"): raise ValueError("ffmpeg not found")
    subprocess.run(["ffmpeg","-y","-ss","0.5","-i",str(video),"-frames:v","1",str(thumb)],check=True,capture_output=True)
    package={"kind":"ShortForgePublishingPackage","version":"0.1","files":["short.mp4","thumbnail.png","captions.json","metadata.json","manifest.json","render-plan.json","qualification.json"],"qualified":True}
    (dest/"package.json").write_text(json.dumps(package,indent=2)+"\n",encoding="utf-8")
    return package
