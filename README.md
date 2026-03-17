# Run Router

This repo is now centered on two things:
- a Python route-suggestion core built on OpenRouteService
- product/design docs for the RouteScout planning and navigation app

## Current Focus

Runtime code lives in:
- [`run_router`](./run_router)
- [`scripts/suggest_loop.py`](./scripts/suggest_loop.py)

Product/design docs live in:
- [`docs/product/README.md`](./docs/product/README.md)

## What The Suggestion Script Does

- generates multiple loop candidates around a center coordinate
- targets a desired run length in miles
- lets the start point drift within a configurable radius
- scores routes for pavement bias, quietness, greenery, and elevation character
- optionally uses an LLM design brief when `OPENAI_API_KEY` is set

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
cp .env.example .env
```

Then edit `.env`:

```bash
ORS_API_KEY="your_key_here"
OPENAI_API_KEY="your_key_here"   # optional
OPENAI_MODEL="gpt-5.4-mini"      # optional
```

## Generate Suggestions

Run the standalone script with the example config:

```bash
python3 scripts/suggest_loop.py --config examples/suggest_loop.example.json
```

Print raw JSON instead of the formatted summary:

```bash
python3 scripts/suggest_loop.py \
  --config examples/suggest_loop.example.json \
  --raw
```

The config controls things like:
- center coordinate
- target distance
- start radius
- pavement / quiet / green / hill preferences
- optional natural-language design brief
- candidate generation limits

## Tests

```bash
python3 -m unittest discover -s tests
```

## Notes

- `.env` is intentionally local and ignored by git.
- generated output under `output/` is ignored by git.
- the mirrored ORS docs and curated notes live under [`docs/openrouteservice`](./docs/openrouteservice).
