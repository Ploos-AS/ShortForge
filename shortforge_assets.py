"""Compile a ShortForgeStoryboard into a provider-neutral media asset manifest."""
ASSET_TYPES=("visual","voice","caption","sfx","music","overlay")

def compile_manifest(storyboard):
    if not isinstance(storyboard,dict) or storyboard.get("kind")!="ShortForgeStoryboard":
        raise ValueError("input must be a ShortForgeStoryboard")
    beats=storyboard.get("beats")
    if not isinstance(beats,list) or not beats: raise ValueError("storyboard has no beats")
    assets=[]
    for i,b in enumerate(beats,1):
        start,end=b.get("start"),b.get("end")
        if not isinstance(start,(int,float)) or not isinstance(end,(int,float)) or end<=start:
            raise ValueError(f"invalid timing in beat {i}")
        assets.extend([
          {"id":f"beat-{i:02d}-visual","type":"visual","required":True,"start":start,"end":end,"prompt":b.get("asset_prompt",""),"constraints":{"aspect_ratio":"9:16"}},
          {"id":f"beat-{i:02d}-voice","type":"voice","required":bool(b.get("voiceover")),"start":start,"end":end,"text":b.get("voiceover","")},
          {"id":f"beat-{i:02d}-caption","type":"caption","required":bool(b.get("caption")),"start":start,"end":end,"text":b.get("caption","")},
        ])
    assets.extend([
      {"id":"bed-music","type":"music","required":False,"start":0,"end":storyboard["duration_seconds"],"prompt":"Background music matching the selected profile and pacing."},
      {"id":"accent-sfx","type":"sfx","required":False,"start":0,"end":storyboard["duration_seconds"],"prompt":"Optional short accents supporting transitions and payoff."},
    ])
    return {"version":"0.1","kind":"ShortForgeAssetManifest","source_kind":"ShortForgeStoryboard","profile":storyboard.get("profile","default"),"format":storyboard.get("format","9:16"),"duration_seconds":storyboard["duration_seconds"],"assets":assets}

MEDIA_PROVIDER_CONTRACT={
 "visual":{"input":["prompt","constraints"],"output":["uri","mime_type"]},
 "voice":{"input":["text"],"output":["uri","mime_type","duration_seconds"]},
 "music":{"input":["prompt"],"output":["uri","mime_type","duration_seconds"]},
 "sfx":{"input":["prompt"],"output":["uri","mime_type","duration_seconds"]},
 "caption":{"input":["text","start","end"],"output":["text","start","end"]},
}
