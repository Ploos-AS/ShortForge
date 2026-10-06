# Architecture

## Core

ShortForge Core stores platform-neutral intent:

- concept
- audience
- tone
- duration target
- beat timeline
- script
- shots
- captions
- audio cues
- variants
- review scores

## Beat functions

Each timed segment can be tagged with one or more functions:

- hook
- setup
- escalation
- reveal
- misdirection
- punchline
- payoff
- call-back
- loop

This makes timing explicit and lets automated reviewers detect dead space or delayed payoff.

## Comedy

Comedy is a first-class mode. A project can select one or more devices such as:

- absurd
- deadpan
- observational
- parody
- nerd/retro
- visual gag
- escalation
- anti-joke
- dialogue
- surreal
- wholesome

A comedy review pass should check setup/payoff relationships rather than merely asking an LLM whether something is funny.

## Platform adapters

Adapters translate a master short into platform-oriented cuts and metadata. The core must not assume TikTok-specific APIs or rules.

## Relationship to FilmForge

Share concepts such as provider adapters, media provenance and shot generation where useful. Keep short-form pacing/scoring independent from FilmForge's cinematic continuity model.
