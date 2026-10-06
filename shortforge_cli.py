#!/usr/bin/env python3
"""ShortForge M1 CLI."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import yaml

REQUIRED=("version","kind","id","title","format","timeline")

def load(path):
    with Path(path).open(encoding="utf-8") as f: return yaml.safe_load(f)

def validate(p):
    errors=[]
    for k in REQUIRED:
        if k not in p: errors.append(f"missing required field: {k}")
    if p.get("kind")!="ShortForgeProject": errors.append("kind must be ShortForgeProject")
    fmt=p.get("format",{})
    if float(fmt.get("duration_target_seconds",0))<=0: errors.append("duration_target_seconds must be > 0")
    timeline=p.get("timeline",[])
    last=0.0
    for i,b in enumerate(timeline):
        start,end=float(b.get("start",-1)),float(b.get("end",-1))
        if start<last: errors.append(f"timeline[{i}] overlaps previous beat")
        if start>last: errors.append(f"timeline[{i}] leaves gap after {last:g}s")
        if end<=start: errors.append(f"timeline[{i}] end must be after start")
        last=end
    return errors

def score(p):
    tl=p.get("timeline",[])
    funcs=[f for b in tl for f in b.get("functions",[])]
    first_hook=min((float(b["start"]) for b in tl if "hook" in b.get("functions",[])),default=999)
    duration=float(p.get("format",{}).get("duration_target_seconds",0))
    coverage=(float(tl[-1]["end"]) if tl and duration else 0)/duration if duration else 0
    dims={
      "hook": 100 if first_hook<=1 else 80 if first_hook<=2 else 40 if first_hook<999 else 0,
      "payoff": 100 if "payoff" in funcs else 0,
      "loop": 100 if "loop" in funcs else 40,
      "structure": min(100,round(coverage*100)),
      "caption_coverage": round(100*sum(bool(b.get("caption")) for b in tl)/len(tl)) if tl else 0
    }
    dims["overall"]=round(sum(dims.values())/len(dims))
    return {"project":p.get("id"),"scores":dims,"advisory":"Structural heuristic only; not a prediction of platform performance."}

def main():
    ap=argparse.ArgumentParser(prog="shortforge")
    sp=ap.add_subparsers(dest="cmd",required=True)
    for cmd in ("validate","score"):
        q=sp.add_parser(cmd); q.add_argument("project")
    a=ap.parse_args(); p=load(a.project); errors=validate(p)
    if errors:
        print("\n".join(f"ERROR: {e}" for e in errors)); raise SystemExit(1)
    if a.cmd=="validate": print("OK: valid ShortForge M1 project")
    else: print(json.dumps(score(p),indent=2))

if __name__=="__main__": main()
