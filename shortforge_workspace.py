"""Materialize an asset manifest into a deterministic ShortForge production workspace."""
from pathlib import Path
import json, re

SAFE_ID=re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]*$")

def _safe_id(value):
    if not isinstance(value,str) or not SAFE_ID.fullmatch(value) or ".." in value:
        raise ValueError(f"unsafe asset id: {value!r}")
    return value

def materialize_workspace(manifest, output_dir):
    if not isinstance(manifest,dict) or manifest.get("kind")!="ShortForgeAssetManifest":
        raise ValueError("input must be a ShortForgeAssetManifest")
    root=Path(output_dir); assets=root/"assets"; captions=root/"captions"
    assets.mkdir(parents=True,exist_ok=True); captions.mkdir(parents=True,exist_ok=True)
    records=[]
    for asset in manifest.get("assets",[]):
        aid=_safe_id(asset.get("id"))
        typ=asset.get("type")
        if typ=="caption":
            path=captions/f"{aid}.txt"; path.write_text(asset.get("text",""),encoding="utf-8")
            status="ready"
        else:
            path=assets/f"{aid}.json"
            path.write_text(json.dumps({"id":aid,"type":typ,"status":"placeholder","request":asset},indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
            status="placeholder"
        records.append({"id":aid,"type":typ,"status":status,"path":str(path.relative_to(root))})
    workspace={"version":"0.1","kind":"ShortForgeWorkspace","profile":manifest.get("profile","default"),"format":manifest.get("format","9:16"),"duration_seconds":manifest.get("duration_seconds"),"assets":records}
    (root/"workspace.json").write_text(json.dumps(workspace,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    (root/"manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return workspace
