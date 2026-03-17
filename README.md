# Run Router

Loop-oriented run route generator powered by OpenRouteService, with preference scoring and
optional LLM-assisted design briefs.

## What It Does

- Generates multiple loop candidates around a center coordinate
- Targets a desired run length in miles
- Lets the start point drift within a configurable radius from the requested location
- Scores routes for pavement bias, quietness, greenery, and elevation character
- Optionally uses an LLM design brief when `OPENAI_API_KEY` is set
- Keeps the original CLI exporter for explicit waypoint routes

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
cp .env.example .env
```

Then edit `.env`:

```bash
ORS_API_KEY="your_key_here"
OPENAI_API_KEY="your_key_here"  # optional, only for design-brief parsing
OPENAI_MODEL="gpt-4o-mini"      # optional
```

## Run The Web App

```bash
python3 -m flask --app app run --debug
```

Open `http://127.0.0.1:5000`.

The browser UI expects the center point in `LON,LAT` format for now.
The app, CLI, and test script automatically load keys from `.env`.

## Test Loop Suggestions From Python

```bash
python3 scripts/test_loop_generation.py \
  --center -122.6765,45.5236 \
  --miles 6 \
  --radius 1.5 \
  --pavement 0.8 \
  --quiet 0.8 \
  --green 0.7 \
  --hills 0.0 \
  --brief "Mostly paved, quiet six-mile loop with some park frontage and gentle rollers"
```

Add `--raw` if you want the full JSON response.

You can also put the request parameters in JSON:

```bash
python3 scripts/test_loop_generation.py --config examples/loop_request.example.json
```

The config file can use either the API field names:

```json
{
  "center_coord": "-122.6765,45.5236",
  "profile": "foot-walking",
  "target_distance_miles": 6.0,
  "start_radius_miles": 1.5,
  "pavement_preference": 0.8,
  "quiet_preference": 0.8,
  "green_preference": 0.7,
  "hill_preference": 0.0,
  "design_brief": "Mostly paved, quiet six-mile loop with some park frontage and gentle rollers"
}
```

or the shorter script aliases like `center`, `miles`, `radius`, `pavement`, `quiet`, `green`,
`hills`, and `brief`. CLI flags override values from the JSON file.

## Standalone Loop Suggestion Script

If you want to ignore the Flask app and just generate suggestions directly from Python:

```bash
.venv/bin/python scripts/suggest_loop.py --config examples/suggest_loop.example.json
```

This script:
- loads `.env`
- optionally applies the OpenAI design brief
- queries ORS for a small number of loop candidates
- prints ranked suggestions
- optionally saves the best route as GeoJSON if `output_geojson` is set in the config

## Run The CLI Exporter

```bash
python ors_route_with_elevation.py \
  --coords -122.66595,45.50495 -122.67020,45.50495 -122.67170,45.49620 \
           -122.66840,45.52770 -122.66695,45.52765 -122.67020,45.50495 \
           -122.67130,45.51328 -122.66695,45.51330 -122.66595,45.50495 \
  --out route_output
```
