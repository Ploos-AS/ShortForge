"""Provider-neutral expansion from a selected variant to a production storyboard."""
from dataclasses import dataclass
from shortforge_profiles import get_profile

@dataclass(frozen=True)
class ExpansionRequest:
    idea: str
    variant: dict
    profile: str = "default"

def validate_variant(v):
    if not isinstance(v,dict) or not all(isinstance(v.get(k),str) and v[k].strip() for k in ("hook","angle","payoff")):
        raise ValueError("selected variant must contain hook, angle and payoff")

def deterministic_expand(request):
    validate_variant(request.variant)
    p=get_profile(request.profile); duration=p["duration_seconds"]; cut=max(2,duration//3)
    beats=[
      {"start":0,"end":cut,"purpose":"hook","voiceover":request.variant["hook"],"caption":request.variant["hook"],"shot":"Immediate visual establishing the premise","asset_prompt":f'Create a vertical visual for: {request.idea}. Opening hook.'},
      {"start":cut,"end":cut*2,"purpose":"develop","voiceover":request.variant["angle"],"caption":request.variant["angle"],"shot":"Escalate the central angle with one clear visual change","asset_prompt":f'Create a vertical visual illustrating: {request.variant["angle"]}.'},
      {"start":cut*2,"end":duration,"purpose":"payoff","voiceover":request.variant["payoff"],"caption":request.variant["payoff"],"shot":"Land the payoff and compose the final frame so it can loop to the opening","asset_prompt":f'Create a vertical payoff visual for: {request.variant["payoff"]}.'},
    ]
    return {"version":"0.1","kind":"ShortForgeStoryboard","idea":request.idea,"profile":request.profile,"duration_seconds":duration,"format":"9:16","variant":request.variant,"beats":beats,"loop":{"enabled":True,"instruction":"Final frame should transition naturally back to the opening."}}

def expand_variant(request, provider="deterministic"):
    if provider!="deterministic": raise ValueError(f"unknown expansion provider: {provider}")
    return deterministic_expand(request)
