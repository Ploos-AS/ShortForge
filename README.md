# ShortForge

AI-assisted production pipeline for short-form vertical video.

ShortForge optimizes concepts for hooks, retention, payoff, comedy, looping, captions and platform-specific cuts rather than treating a short video as a miniature conventional film.

## M0 goals

M0 defines a provider-neutral short-video project format and a repeatable path from an idea to multiple optimized edits.

```text
idea
 -> concept variants
 -> hook
 -> script
 -> comedy / payoff pass
 -> beat timeline
 -> shot plan
 -> media generation
 -> voice / music / SFX
 -> captions
 -> retention review
 -> platform cuts
```

## Initial targets

- vertical 9:16
- 15–30 second sweet spot
- TikTok
- YouTube Shorts
- Instagram Reels
- humorous content as a first-class mode

## Design principles

- Platform adapters, not platform lock-in.
- Generate several concepts/cuts cheaply before expensive rendering.
- Every second should have an intended function.
- Captions and audio are part of the edit, not post-processing afterthoughts.
- Hooks, escalation, payoff and loops are machine-readable.
- Reuse FilmForge/provider infrastructure where sensible without coupling the projects.

## Repository layout

```text
docs/
  architecture.md
  m0.md
schema/
  shortforge-project.schema.yaml
examples/
  retro-gag/
    project.yaml
```

## Status

M0 — foundation.
