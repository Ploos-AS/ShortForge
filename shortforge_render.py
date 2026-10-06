"""Build and optionally execute a deterministic FFmpeg render plan."""
from pathlib import Path
import json, shutil, subprocess

def build_render_plan(root, output="output/short.mp4"):
    root=Path(root); wp=root/"workspace.json"
    if not wp.is_file(): raise ValueError("workspace.json not found")
    w=json.loads(wp.read_text(encoding="utf-8"))
    visuals=[a for a in w.get("assets",[]) if a.get("type")=="visual" and a.get("status")=="ready"]
    if not visuals: raise ValueError("no ready visual assets")
    duration=float(w["duration_seconds"]); out=root/output
    inputs=[]; filters=[]; concat=[]
    manifest=json.loads((root/"manifest.json").read_text(encoding="utf-8"))
    req={a["id"]:a for a in manifest.get("assets",[])}
    for i,a in enumerate(visuals):
        r=req[a["id"]]; d=float(r["end"])-float(r["start"])
        inputs += ["-loop","1","-t",str(d),"-i",str(root/a["path"])]
        filters.append(f"[{i}:v]scale=1080:1920,setsar=1,fps=30[v{i}]")
        concat.append(f"[v{i}]")
    fc=";".join(filters+[f"{''.join(concat)}concat=n={len(visuals)}:v=1:a=0[v]"])
    command=["ffmpeg","-y",*inputs,"-filter_complex",fc,"-map","[v]","-t",str(duration),"-c:v","libx264","-pix_fmt","yuv420p","-movflags","+faststart",str(out)]
    return {"version":"0.1","kind":"ShortForgeRenderPlan","output":str(out.relative_to(root)),"duration_seconds":duration,"command":command}

def render_workspace(root, output="output/short.mp4", execute=True):
    root=Path(root); plan=build_render_plan(root,output)
    (root/"render-plan.json").write_text(json.dumps(plan,indent=2)+"\n",encoding="utf-8")
    if not execute: return plan
    if not shutil.which("ffmpeg"): raise ValueError("ffmpeg not found")
    (root/output).parent.mkdir(parents=True,exist_ok=True)
    subprocess.run(plan["command"],check=True)
    return plan
