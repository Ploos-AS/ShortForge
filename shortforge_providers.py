"""Provider-neutral concept generation for ShortForge."""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass(frozen=True)
class GenerationRequest:
    idea: str
    count: int = 5
    source_project: str | None = None

class Provider(ABC):
    name = "provider"
    @abstractmethod
    def generate_variants(self, request: GenerationRequest) -> dict:
        """Return a ShortForgeVariantSet."""

class DeterministicProvider(Provider):
    """Offline provider used for development, tests and CI."""
    name = "deterministic"
    ANGLES = (
        "deadpan announcement",
        "modern influencer review",
        "serious benchmark",
        "reaction escalation",
        "breaking-news report",
    )
    PAYOFFS = (
        "The smallest feature gets the biggest applause.",
        "The revolutionary reveal is deliberately mundane.",
        "The benchmark is won for an absurdly specific reason.",
        "Everyone stays calm until the final technical detail.",
        "The dramatic report ends on an intentionally tiny upgrade.",
    )
    def generate_variants(self, request: GenerationRequest) -> dict:
        idea=request.idea.strip()
        if not idea: raise ValueError("idea must not be empty")
        if request.count < 1 or request.count > 20: raise ValueError("count must be between 1 and 20")
        vs=[]
        for i in range(request.count):
            angle=self.ANGLES[i % len(self.ANGLES)]
            payoff=self.PAYOFFS[i % len(self.PAYOFFS)]
            vs.append({"id":f"generated-{i+1:02d}","hook":f"{idea}: here's the part you didn't expect.","angle":angle,"payoff":payoff})
        return {"version":"0.1","kind":"ShortForgeVariantSet","id":"generated-variants","source_project":request.source_project,"provider":self.name,"idea":idea,"variants":vs}

def get_provider(name: str) -> Provider:
    if name == "deterministic": return DeterministicProvider()
    raise ValueError(f"unknown provider: {name}")
