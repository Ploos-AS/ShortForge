"""Qualify a rendered ShortForge MP4 using ffprobe."""
from pathlib import Path
import json, shutil, subprocess

def probe_video(path):
    path=Path(path)
    if not path.is_file(): raise ValueError("rendered video not found")
    if not shutil.which("ffprobe"): raise ValueError("ffprobe not found")
    p=subprocess.run(["ffprobe","-v","error","-show_streams","-show_format","-of","json",str(path)],check=True,capture_output=True,text=True)
    return json.loads(p.stdout)

def qualify_video(path, expected_duration=None):
    data=probe_video(path); streams=data.get("streams",[])
    video=next((s for s in streams if s.get("codec_type")=="video"),None)
    audio=next((s for s in streams if s.get("codec_type")=="audio"),None)
    errors=[]
    if not video: errors.append("missing video stream")
    else:
        if video.get("codec_name")!="h264": errors.append("video codec is not h264")
        if (video.get("width"),video.get("height"))!=(1080,1920): errors.append("video is not 1080x1920")
        rate=video.get("avg_frame_rate","0/1").split("/")
        fps=float(rate[0])/float(rate[1]) if len(rate)==2 and float(rate[1]) else 0
        if abs(fps-30)>0.01: errors.append("video is not 30 fps")
    if not audio: errors.append("missing audio stream")
    elif audio.get("codec_name")!="aac": errors.append("audio codec is not aac")
    duration=float(data.get("format",{}).get("duration",0))
    if expected_duration is not None and abs(duration-float(expected_duration))>0.25: errors.append("duration outside tolerance")
    return {"kind":"ShortForgeRenderQualification","passed":not errors,"errors":errors,"duration_seconds":duration,"video":video,"audio":audio}
