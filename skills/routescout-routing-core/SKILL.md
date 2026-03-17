---
name: routescout-routing-core
description: Use when working on RouteScout runtime code, OpenRouteService integration, loop suggestion logic, scoring helpers, or the standalone Python script in this repo. Best for run_router, scripts/suggest_loop.py, examples, and runtime tests.
---

# RouteScout Routing Core

Use this skill for runtime and API-integration work in `/Users/fallbro/code/run-mapper`.

## Start Here

Read these first:
- `docs/openrouteservice/agent-context.md`
- `run_router/service.py`
- `scripts/suggest_loop.py`

Read these when relevant:
- `docs/openrouteservice/run-route-planner-endpoints.md`
- `examples/suggest_loop.example.json`
- `tests/test_service.py`

## Current Active Runtime Path

Primary files:
- `run_router/service.py`
- `run_router/env.py`
- `scripts/suggest_loop.py`

The old Flask prototype was removed.
Do not rebuild web-server routes or Flask scaffolding unless explicitly asked.

## Runtime Principles

- Keep the repo script-first and library-first.
- Reuse `run_router/service.py` instead of duplicating ORS logic.
- Keep `.env` loading via `run_router/env.py`.
- Preserve the current ORS/OpenAI integration shape unless a deliberate redesign is requested.

## ORS Context

Hosted ORS behavior already verified in this repo:
- `round_trip` with underscore
- numeric `green` and `quiet` weightings

Before changing ORS payload semantics, check the current implementation and the ORS docs in
`docs/openrouteservice`.

## Validation

Run when practical:
- `python3 -m unittest discover -s tests`

For script behavior:
- use `python3 scripts/suggest_loop.py --config examples/suggest_loop.example.json`

## Avoid

- Reintroducing deleted prototype codepaths
- Adding runtime dependencies unless they materially improve the active script/library path
- Copy-pasting large chunks of ORS request logic into multiple files
