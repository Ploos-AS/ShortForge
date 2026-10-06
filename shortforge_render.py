"""Build and optionally execute a deterministic FFmpeg render plan."""
from pathlib import Path
import json, shutil, subprocess
from shortforge_production import get_production_profile

def _esc(text):
    return str(text).replace("\\","\\\\").replace("'","\\'").replace(":","\\:")

def build_render_plan(root, output="output/short.mp4", production_profile="generic-vertical"):
    profile=get_production_profile(production_profile)
    root=Path(root); wp=root/"workspace.json"
    if not wp.is_file(): raise ValueError("workspace.json not found")
    w=json.loads(wp.read_text(encoding="utf-8")); duration=float(w["duration_seconds"]); out=root/output
    if profile["max_duration"] is not None and duration>profile["max_duration"]: raise ValueError("duration exceeds production profile limit")
    manifest=json.loads((root/"manifest.json").read_text(encoding="utf-8")); req={a["id"]:a for a in manifest.get("assets",[])}
    ready=[a for a in w.get("assets",[]) if a.get("status")=="ready"]
    visuals=[a for a in ready if a.get("type")=="visual"]
    if not visuals: raise ValueError("no ready visual assets")
    inputs=[]; filters=[]; concat=[]; idx=0
    for a in visuals:
        r=req[a["id"]]; d=float(r["end"])-float(r["start"])
        inputs += ["-loop","1","-t",str(d),"-i",str(root/a["path"])]
        filters.append(f"[{idx}:v]scale={profile['width']}:{profile['height']},setsar=1,fps={profile['fps']}[v{idx}]"); concat.append(f"[v{idx}]"); idx+=1
    filters.append(f"{''.join(concat)}concat=n={len(visuals)}:v=1:a=0[vbase]")
    captions=[a for a in ready if a.get("type")=="caption"]
    vlabel="vbase"
    for n,a in enumerate(captions):
        r=req[a["id"]]; text=_esc(r.get("text","")); nxt=f"vc{n}"
        filters.append(f"[{vlabel}]drawtext=text='{text}':x=(w-text_w)/2:y=h*{profile['caption_y']}:fontsize=64:fontcolor=white:borderw=4:enable='between(t,{r['start']},{r['end']})'[{nxt}]"); vlabel=nxt
    audio=[]
    for a in [x for x in ready if x.get("type") in ("voice","music","sfx")]:
        r=req[a["id"]]; inputs += ["-i",str(root/a["path"])]
        delay=int(float(r.get("start",0))*1000); label=f"a{idx}"
        volume=0.22 if a["type"]=="music" else (0.55 if a["type"]=="sfx" else 1.0)
        filters.append(f"[{idx}:a]adelay={delay}|{delay},volume={volume}[{label}]"); audio.append(f"[{label}]"); idx+=1
    alabel=None
    if audio:
        filters.append(f"{''.join(audio)}amix=inputs={len(audio)}:normalize=0,alimiter=limit=0.95[aout]"); alabel="aout"
    command=["ffmpeg","-y",*inputs,"-filter_complex",";".join(filters),"-map",f"[{vlabel}]"]
    if alabel: command += ["-map",f"[{alabel}]","-c:a","aac","-b:a","192k"]
    command += ["-t",str(duration),"-c:v","libx264","-pix_fmt","yuv420p","-movflags","+faststart",str(out)]
    return {"version":"0.2","kind":"ShortForgeRenderPlan","output":str(out.relative_to(root)),"duration_seconds":duration,"features":{"captions":bool(captions),"audio_mix":bool(audio),"caption_safe_y":profile["caption_y"],"production_profile":production_profile,"safe_zone":profile["safe_zone"]},"command":command}

def render_workspace(root, output="output/short.mp4", execute=True, production_profile="generic-vertical"):
    root=Path(root); plan=build_render_plan(root,output,production_profile)
    (root/"render-plan.json").write_text(json.dumps(plan,indent=2)+"\n",encoding="utf-8")
    if not execute: return plan
    if not shutil.which("ffmpeg"): raise ValueError("ffmpeg not found")
    (root/output).parent.mkdir(parents=True,exist_ok=True)
    subprocess.run(plan["command"],check=True)
    return plan
