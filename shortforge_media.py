"""Resolve ShortForge workspace placeholders into deterministic local media."""
from pathlib import Path
import json, struct, wave, zlib

def _png(path,width=360,height=640):
    # Valid RGB PNG, generated with stdlib only.
    raw=b"".join(b"\x00"+bytes([32,32,32])*width for _ in range(height))
    def chunk(t,d): return struct.pack(">I",len(d))+t+d+struct.pack(">I",zlib.crc32(t+d)&0xffffffff)
    data=b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",struct.pack(">IIBBBBB",width,height,8,2,0,0,0))+chunk(b"IDAT",zlib.compress(raw,9))+chunk(b"IEND",b"")
    path.write_bytes(data)

def _silence(path,duration,rate=16000):
    frames=max(1,int(float(duration)*rate))
    with wave.open(str(path),"wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes(b"\x00\x00"*frames)

def resolve_workspace(root):
    root=Path(root); wp=root/"workspace.json"
    if not wp.is_file(): raise ValueError("workspace.json not found")
    workspace=json.loads(wp.read_text(encoding="utf-8"))
    if workspace.get("kind")!="ShortForgeWorkspace": raise ValueError("invalid workspace")
    for record in workspace.get("assets",[]):
        if record.get("status")!="placeholder": continue
        req_path=root/record["path"]; req=json.loads(req_path.read_text(encoding="utf-8"))["request"]
        aid=record["id"]; typ=record["type"]
        if typ=="visual":
            out=root/"assets"/f"{aid}.png"; _png(out); mime="image/png"
        elif typ in ("voice","music","sfx"):
            out=root/"assets"/f"{aid}.wav"; _silence(out,max(0.1,float(req.get("end",1))-float(req.get("start",0)))); mime="audio/wav"
        else:
            continue
        record.update({"status":"ready","path":str(out.relative_to(root)),"mime_type":mime,"provider":"deterministic"})
    wp.write_text(json.dumps(workspace,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return workspace
