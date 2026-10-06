"""Production/output profiles for vertical short-form video."""
PRODUCTION_PROFILES={
 "generic-vertical":{"width":1080,"height":1920,"fps":30,"video_codec":"h264","audio_codec":"aac","max_duration":None,"caption_y":0.78,"safe_zone":{"top":0.10,"right":0.16,"bottom":0.18,"left":0.08},"basis":"ShortForge production default"},
 "tiktok":{"width":1080,"height":1920,"fps":30,"video_codec":"h264","audio_codec":"aac","max_duration":None,"caption_y":0.72,"safe_zone":{"top":0.12,"right":0.18,"bottom":0.22,"left":0.08},"basis":"ShortForge conservative 9:16 production preset; safe zone is advisory"},
 "reels":{"width":1080,"height":1920,"fps":30,"video_codec":"h264","audio_codec":"aac","max_duration":None,"caption_y":0.74,"safe_zone":{"top":0.12,"right":0.14,"bottom":0.20,"left":0.08},"basis":"ShortForge conservative 9:16 production preset"},
 "shorts":{"width":1080,"height":1920,"fps":30,"video_codec":"h264","audio_codec":"aac","max_duration":180,"caption_y":0.76,"safe_zone":{"top":0.10,"right":0.14,"bottom":0.18,"left":0.08},"basis":"YouTube Shorts: square/vertical up to 3 minutes; ShortForge renders 9:16"},
}
def get_production_profile(name):
    try: return PRODUCTION_PROFILES[name]
    except KeyError: raise ValueError(f"unknown production profile: {name}")
