"""Provider-neutral concept generation for ShortForge."""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
import json, os
from urllib.request import Request, urlopen

@dataclass(frozen=True)
class GenerationRequest:
    idea: str
    count: int = 5
    source_project: str | None = None

class Provider(ABC):
    name = "provider"
    @abstractmethod
    def generate_variants(self, request: GenerationRequest) -> dict: ...

class DeterministicProvider(Provider):
    name = "deterministic"
    ANGLES=("deadpan announcement","modern influencer review","serious benchmark","reaction escalation","breaking-news report")
    PAYOFFS=("The smallest feature gets the biggest applause.","The revolutionary reveal is deliberately mundane.","The benchmark is won for an absurdly specific reason.","Everyone stays calm until the final technical detail.","The dramatic report ends on an intentionally tiny upgrade.")
    def generate_variants(self, request):
        idea=request.idea.strip()
        if not idea: raise ValueError("idea must not be empty")
        if request.count<1 or request.count>20: raise ValueError("count must be between 1 and 20")
        vs=[{"id":f"generated-{i+1:02d}","hook":f"{idea}: here's the part you didn't expect.","angle":self.ANGLES[i%5],"payoff":self.PAYOFFS[i%5]} for i in range(request.count)]
        return variant_set(request,self.name,vs)

def variant_set(request, provider, variants):
    return {"version":"0.1","kind":"ShortForgeVariantSet","id":"generated-variants","source_project":request.source_project,"provider":provider,"idea":request.idea.strip(),"variants":variants}

def _http_json(url, headers, payload):
    req=Request(url,data=json.dumps(payload).encode(),headers={**headers,"Content-Type":"application/json"},method="POST")
    with urlopen(req,timeout=60) as r: return json.load(r)

class OpenAICompatibleProvider(Provider):
    """Chat-completions compatible adapter; transport is injectable for offline tests."""
    name="openai-compatible"
    def __init__(self, base_url=None, api_key=None, model=None, transport=_http_json):
        self.base_url=(base_url or os.getenv("SHORTFORGE_OPENAI_BASE_URL","https://api.openai.com/v1")).rstrip("/")
        self.api_key=api_key if api_key is not None else os.getenv("SHORTFORGE_OPENAI_API_KEY",os.getenv("OPENAI_API_KEY",""))
        self.model=model or os.getenv("SHORTFORGE_OPENAI_MODEL","gpt-6-luna")
        self.transport=transport
    def generate_variants(self, request):
        if not request.idea.strip(): raise ValueError("idea must not be empty")
        if request.count<1 or request.count>20: raise ValueError("count must be between 1 and 20")
        prompt=f"""Generate exactly {request.count} short-form video concepts for: {request.idea}
Return JSON only as an object with key "variants". Each variant must contain string fields id, hook, angle, payoff."""
        payload={"model":self.model,"messages":[{"role":"system","content":"You generate concise ShortForge concept variants. Output valid JSON only."},{"role":"user","content":prompt}],"response_format":{"type":"json_object"}}
        headers={"Authorization":f"Bearer {self.api_key}"} if self.api_key else {}
        response=self.transport(f"{self.base_url}/chat/completions",headers,payload)
        try: content=response["choices"][0]["message"]["content"]; data=json.loads(content) if isinstance(content,str) else content
        except (KeyError,IndexError,TypeError,json.JSONDecodeError) as e: raise ValueError("provider returned invalid JSON response") from e
        vs=data.get("variants") if isinstance(data,dict) else None
        if not isinstance(vs,list) or len(vs)!=request.count: raise ValueError("provider returned wrong variant count")
        for i,v in enumerate(vs):
            if not isinstance(v,dict) or not all(isinstance(v.get(k),str) and v[k].strip() for k in ("hook","angle","payoff")): raise ValueError(f"provider returned invalid variant at index {i}")
            v.setdefault("id",f"generated-{i+1:02d}")
        return variant_set(request,self.name,vs)

def get_provider(name: str) -> Provider:
    if name=="deterministic": return DeterministicProvider()
    if name in ("openai-compatible","openai"): return OpenAICompatibleProvider()
    raise ValueError(f"unknown provider: {name}")
