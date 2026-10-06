"""Caption sidecar generation for publishing targets."""
import json
from pathlib import Path

def _stamp(seconds):
    ms=round(float(seconds)*1000); h,ms=divmod(ms,3600000); m,ms=divmod(ms,60000); s,ms=divmod(ms,1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def captions_to_srt(manifest):
    assets=[a for a in manifest.get("assets",[]) if a.get("type")=="caption"]
    lines=[]
    for i,a in enumerate(assets,1):
        start=a.get("start",a.get("start_seconds")); end=a.get("end",a.get("end_seconds")); text=a.get("text",a.get("content",""))
        if start is None or end is None or not text: continue
        lines += [str(i),f"{_stamp(start)} --> {_stamp(end)}",str(text),""]
    return "\n".join(lines)

def write_srt(manifest_file,output):
    manifest=json.loads(Path(manifest_file).read_text(encoding="utf-8")); text=captions_to_srt(manifest)
    if not text: raise ValueError("no timed captions available")
    Path(output).write_text(text,encoding="utf-8"); return Path(output)
