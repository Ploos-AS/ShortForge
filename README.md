# ShortForge

AI-assisted production pipeline for short-form vertical video.

ShortForge optimizes concepts for hooks, retention, payoff, comedy, looping, captions and platform-specific cuts rather than treating a short video as a miniature conventional film.

## Pipeline

```text
idea
 -> concept variants
 -> structural scoring
 -> candidate selection
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

## CLI

```sh
shortforge validate examples/retro-gag/project.yaml
shortforge score examples/retro-gag/project.yaml
shortforge variants examples/retro-gag/variants.yaml
shortforge select examples/retro-gag/variants.yaml
```

## Repository layout

```text
docs/
schema/
examples/
tests/
shortforge_cli.py
```

## Status

- M0 — foundation
- M1 — executable CLI
- M1.1 — ideation/variant foundation
- M1.2 — deterministic selection pipeline
- M1.3 — CI and qualification


## M2.11 YouTube publishing UX

YouTube publishing can resolve the normal upload bearer token from `SHORTFORGE_YOUTUBE_ACCESS_TOKEN` instead of placing it on the command line. Caption upload remains opt-in and deliberately requires a separate token, supplied with `--caption-access-token` or `SHORTFORGE_YOUTUBE_CAPTION_ACCESS_TOKEN`, because captions use the stronger `youtube.force-ssl` scope.

Example:

```sh
SHORTFORGE_YOUTUBE_ACCESS_TOKEN=... \\
SHORTFORGE_YOUTUBE_CAPTION_ACCESS_TOKEN=... \\
python shortforge_cli.py publish youtube publish/package \\
  --privacy private --upload-captions --caption-language no \\
  --result-file publish-result.json
```

The result file contains publication identifiers/status only; OAuth credentials are never persisted in ShortForge artifacts.
