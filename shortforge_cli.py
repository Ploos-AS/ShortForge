#!/usr/bin/env python3
"""ShortForge M1.2 CLI."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import yaml
REQUIRED=("version","kind","id","title","format","timeline")
def load(path):
    with Path(path).open(encoding="utf-8") as x: return yaml.safe_load(x)
def validate(p):
    e=[f"missing required field: {k}" for k in REQUIRED if k not in p]
    if p.get("kind")!="ShortForgeProject": e.append("kind must be ShortForgeProject")
    if float(p.get("format",{}).get("duration_target_seconds",0))<=0: e.append("duration_target_seconds must be > 0")
    last=0.0
    for i,b in enumerate(p.get("timeline",[])):
        start,end=float(b.get("start",-1)),float(b.get("end",-1))
        if start<last:e.append(f"timeline[{i}] overlaps previous beat")
        if start>last:e.append(f"timeline[{i}] leaves gap after {last:g}s")
        if end<=start:e.append(f"timeline[{i}] end must be after start")
        last=end
    return e
def score(p):
    tl=p.get("timeline",[]); funcs=[f for b in tl for f in b.get("functions",[])]
    first=min((float(b["start"]) for b in tl if "hook" in b.get("functions",[])),default=999); duration=float(p.get("format",{}).get("duration_target_seconds",0))
    coverage=(float(tl[-1]["end"]) if tl and duration else 0)/duration if duration else 0
    d={"hook":100 if first<=1 else 80 if first<=2 else 40 if first<999 else 0,"payoff":100 if "payoff" in funcs else 0,"loop":100 if "loop" in funcs else 40,"structure":min(100,round(coverage*100)),"caption_coverage":round(100*sum(bool(b.get("caption")) for b in tl)/len(tl)) if tl else 0}
    d["overall"]=round(sum(d.values())/len(d)); return {"project":p.get("id"),"scores":d,"advisory":"Structural heuristic only; not a prediction of platform performance."}
def variants(p):
    vs=p.get("variants",[]); return {"set":p.get("id"),"source_project":p.get("source_project"),"variant_count":len(vs),"variants":[{"id":v.get("id"),"hook":v.get("hook"),"angle":v.get("angle"),"payoff":v.get("payoff")} for v in vs]}
def _text_score(value, ideal_min, ideal_max):
    n=len((value or "").strip())
    if not n:return 0
    if ideal_min<=n<=ideal_max:return 100
    distance=ideal_min-n if n<ideal_min else n-ideal_max
    return max(20,100-distance*3)
def rank_variants(p):
    if p.get("kind")!="ShortForgeVariantSet": raise ValueError("kind must be ShortForgeVariantSet")
    ranked=[]
    for i,v in enumerate(p.get("variants",[])):
        scores={"hook":_text_score(v.get("hook"),12,72),"angle":_text_score(v.get("angle"),8,80),"payoff":_text_score(v.get("payoff"),12,100),"completeness":round(100*sum(bool(v.get(k)) for k in ("hook","angle","payoff"))/3)}
        scores["overall"]=round(sum(scores.values())/len(scores)); reasons=[]
        if scores["hook"]>=90: reasons.append("concise, explicit hook")
        if scores["payoff"]>=90: reasons.append("clear payoff")
        if scores["completeness"]==100: reasons.append("complete hook/angle/payoff structure")
        ranked.append({"id":v.get("id"),"source_index":i,"scores":scores,"reasons":reasons})
    ranked.sort(key=lambda x:(-x["scores"]["overall"],x["source_index"],str(x["id"])))
    for n,item in enumerate(ranked,1): item["rank"]=n
    return {"set":p.get("id"),"source_project":p.get("source_project"),"candidate_count":len(ranked),"selected":ranked[0]["id"] if ranked else None,"ranking":ranked,"advisory":"Deterministic structural heuristic only; ranking is not a prediction of virality or platform performance."}
def main():
    ap=argparse.ArgumentParser(prog="shortforge"); sp=ap.add_subparsers(dest="cmd",required=True)
    for cmd in ("validate","score","variants","select"):
        q=sp.add_parser(cmd); q.add_argument("project")
    a=ap.parse_args(); p=load(a.project)
    if a.cmd in ("variants","select"):
        if p.get("kind")!="ShortForgeVariantSet": raise SystemExit("ERROR: kind must be ShortForgeVariantSet")
        print(json.dumps(variants(p) if a.cmd=="variants" else rank_variants(p),indent=2)); return
    e=validate(p)
    if e: print("\n".join(f"ERROR: {x}" for x in e)); raise SystemExit(1)
    print("OK: valid ShortForge M1.2 project" if a.cmd=="validate" else json.dumps(score(p),indent=2))
if __name__=="__main__": main()
