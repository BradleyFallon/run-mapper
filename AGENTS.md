# RouteScout Agents

This repo is for two things:
- the active Python route-suggestion core built on OpenRouteService and optional OpenAI preferences
- the product/design docs for the RouteScout web planner and iPhone app

## Current Repo Shape

Active runtime code:
- `run_router/service.py`
- `run_router/env.py`
- `scripts/suggest_loop.py`
- `tests/test_service.py`

Primary docs:
- `docs/product/README.md`
- `docs/openrouteservice/agent-context.md`
- `docs/openrouteservice/run-route-planner-endpoints.md`

Examples:
- `examples/suggest_loop.example.json`

## What Is Not Active

The old Flask prototype and legacy CLI were removed.
Do not reintroduce Flask app scaffolding or browser prototype code unless the user explicitly asks
for it.

## Core Product Model

Use this vocabulary consistently:
- `category` = a grouping/filtering property of a plan template
- `plan` = the reusable planning request the user selects or edits
- `route` = the generated output

Platform split:
- web app = planning-first surface
- iOS app = full product, including route use and navigation

## Working Rules

- Keep `.env` local and untouched unless the user explicitly asks to edit it.
- Prefer updating the active script/library path instead of building throwaway prototypes.
- Keep product docs focused and linked rather than growing one giant design document.
- When working on design/product tasks, start from `docs/product/README.md`.
- When working on ORS/runtime tasks, start from `docs/openrouteservice/agent-context.md`.

## Recommended Repo Skills

Use these repo-local skills when relevant:
- `routescout-product-docs`
- `routescout-routing-core`
- `routescout-surface-design`

## Validation

For runtime code changes:
- run `python3 -m unittest discover -s tests` when practical

For doc changes:
- keep links current in `docs/product/README.md` when adding new major product docs
