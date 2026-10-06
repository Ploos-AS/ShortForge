"""Creative generation profiles shared by all ShortForge providers."""
PROFILES={
 "default":{"tone":"concise and engaging","audience":"general short-form viewers","duration_seconds":20,"requirements":["strong opening hook","clear angle","specific payoff"]},
 "comedy":{"tone":"deadpan, escalating, concise","audience":"short-form comedy viewers","duration_seconds":20,"requirements":["hook in first beat","escalation","surprising payoff","loop-friendly ending"]},
 "retro":{"tone":"authentic, playful, technically literate","audience":"retro-computing enthusiasts","duration_seconds":20,"requirements":["recognizable retro detail","avoid fake technical claims","strong hook","specific payoff"]},
 "educational":{"tone":"clear, curious, accessible","audience":"learners","duration_seconds":30,"requirements":["one learning objective","early curiosity gap","concrete explanation","memorable takeaway"]},
 "news-parody":{"tone":"straight-faced breaking news parody","audience":"general technology viewers","duration_seconds":20,"requirements":["news-style hook","credible setup","escalating absurdity","deadpan payoff"]},
 "product-demo":{"tone":"confident and concrete","audience":"potential users","duration_seconds":25,"requirements":["problem-first hook","show benefit","specific proof point","clear payoff"]},
}
def get_profile(name):
    if name not in PROFILES: raise ValueError(f"unknown profile: {name}")
    return {"name":name,**PROFILES[name]}
def profile_info(): return {k:v.copy() for k,v in PROFILES.items()}
