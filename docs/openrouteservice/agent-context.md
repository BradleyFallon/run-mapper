# ORS Agent Context

This file is a single-context handoff for an LLM agent that needs to assist with
openrouteservice development in this repo.

Assumption:
- "ORS" means openrouteservice
- The current product direction is a run-route suggestion tool that uses ORS as the routing engine
- The agent should optimize for practical implementation work, not generic API summaries

## Agent Role

You are assisting with openrouteservice-integrated product development.

Your main jobs are:
- help design ORS request/response flows
- implement or review code that calls ORS
- reason about route generation, loop generation, and route scoring
- translate natural-language route preferences into ORS-compatible parameters
- identify where ORS can handle a preference directly and where post-processing/scoring is required

You are not expected to:
- explain ORS from scratch every time
- invent unsupported ORS features
- assume archived docs are always accurate for the hosted API

## Source Priority

Use these sources in this order:

1. Current mirrored backend docs under:
   [giscience.github.io/openrouteservice/api-reference/index.html](./giscience.github.io/openrouteservice/api-reference/index.html)
2. Current live behavior already verified in this repo’s code and tests
3. Archived official markdown repo for easier reading:
   [openrouteservice-docs-repo/README.md](./openrouteservice-docs-repo/README.md)
4. Archived swagger specs:
   [openrouteservice-docs-repo/API V2/swagger.json](./openrouteservice-docs-repo/API%20V2/swagger.json)

If the archived markdown and live behavior disagree, prefer the current backend docs and observed
hosted API behavior.

## Repo-Relevant ORS Features

The most relevant ORS capabilities for this project are:
- directions routing
- round-trip / loop generation
- foot-profile weighting via `green` and `quiet`
- extra route metadata via `extra_info`
- geocoding for place-name entry
- possibly POI / isochrones later

The least relevant features right now are:
- HGV restrictions
- wheelchair-specific routing
- export endpoint
- self-host-only custom models

## Minimum Mental Model

For this project, ORS is doing two distinct jobs:

1. Generate candidate routes.
2. Return enough metadata to score those routes.

The best product flow is:

1. Convert user start input into coordinates.
2. Generate one or more ORS routes or round trips.
3. Request route metadata such as surface, way type, green, noise, and steepness.
4. Score and rank the results in app code.

Do not expect ORS to express every product preference directly in a single request.

## Directions Inputs That Matter Most

Important directions request fields:
- `profile`
- `coordinates`
- `preference`
- `options`
- `extra_info`
- `attributes`
- `geometry`
- `instructions`
- `elevation`

For this project, the typical useful profile is:
- `foot-walking`

Sometimes also:
- `foot-hiking`

## Loop Generation

ORS supports round-trip generation.

Conceptually, the relevant fields are:
- target `length`
- `points`
- optional `seed`

Important implementation note from live testing in this repo:
- the hosted ORS API accepted `round_trip` with an underscore
- the hosted ORS API rejected `round-trip` with a dash

Treat that as a live-hosted API quirk already observed locally.

## Direct Preference Controls ORS Can Handle

For foot profiles, ORS can directly bias:
- `green`
- `quiet`

It can also directly avoid:
- `ferries`
- `fords`
- `steps`
- other profile-appropriate `avoid_features`

It can avoid polygons with:
- `avoid_polygons`

It can create loops with:
- `round_trip`

## Preferences ORS Cannot Fully Solve Alone

These should usually be handled in post-scoring, not assumed to be fully controllable by ORS:
- strong pavement-quality preferences
- nuanced “good for running” judgments
- custom neighborhood desirability
- park-adjacency preferences beyond green/quiet proxies
- precise target climb profiles
- product-specific route aesthetics

For those, request `extra_info`, then score the route yourself.

## Most Useful `extra_info`

For run-route ranking, the most useful `extra_info` values are:
- `surface`
- `waytype`
- `green`
- `noise`
- `steepness`
- `suitability`

Sometimes also useful:
- `waycategory`
- `traildifficulty`
- `roadaccessrestrictions`
- `tollways`

## Interpreting Response Data

The most useful route response fields for product logic are:
- summary distance
- summary duration
- ascent / descent
- geometry coordinates
- elevation in geometry
- extras for surface, way type, green, noise, steepness, suitability

Useful local references:
- [notes/route-response.md](./notes/route-response.md)
- [notes/routing.md](./notes/routing.md)

## Surface and Path-Type Heuristics

For running use cases, a useful heuristic is:

- treat paved surfaces as stronger candidates when the user prefers pavement
- use `surface` and `waytype` together, not either alone
- `surface` helps distinguish asphalt/concrete/gravel/etc.
- `waytype` helps distinguish street/path/track/footway

Examples:
- pavement-heavy route preference: favor `surface` values like paved, asphalt, concrete, paving stones
- trail-heavy route preference: favor `waytype` values like path, track, footway

Do not overfit a single ORS encoding table. Use weighted scoring.

## Noise and Greenery

ORS can return:
- `green`
- `noise`

These are useful proxies for:
- park-adjacent routes
- lower-traffic routes
- calmer routes

They should be treated as ranking signals, not guarantees.

## Elevation / Hill Handling

For climbing preferences:
- use route ascent and descent from the route geometry
- optionally use `steepness` extra info for segment-level analysis
- convert user hill preferences into a target climb-per-mile range

Recommended product pattern:
- ORS generates route
- app computes total ascent and climb-per-mile
- scorer compares result to target hill preference

## Geocoding

If the user provides place text instead of coordinates:
- geocode first
- then pass the resulting coordinate into directions

Useful local reference:
- [notes/geocoding.md](./notes/geocoding.md)

## What To Be Careful About

1. Archived docs may not match hosted API behavior exactly.
2. Public ORS can rate-limit aggressively.
3. Some ORS examples in older docs use older request shapes.
4. `custom_model` exists in docs but is not the right assumption for the hosted public API path.
5. A route that is “valid” is not necessarily “good for running.”

## Known Live Quirks Observed In This Repo

These are implementation observations from local testing, not official claims:

- `round_trip` was accepted by the hosted API
- `round-trip` was rejected by the hosted API
- hosted API accepted numeric `green` and `quiet` weighting values
- hosted API rejected the archived nested `{ "factor": ... }` object shape in our tested requests
- public ORS rate limiting can block repeated loop-generation attempts

When debugging request payloads, trust live results over older examples.

## Recommended Implementation Strategy

For an ORS-powered run-route assistant, use this pattern:

1. Accept user intent:
   - start location
   - distance
   - start radius
   - pavement bias
   - quiet bias
   - green bias
   - hill bias
   - optional natural-language brief

2. Convert the natural-language brief into numeric preferences outside ORS.

3. Generate a small set of ORS loop candidates.

4. Request route metadata with `extra_info`.

5. Score routes in your own code.

6. Return ranked suggestions with score breakdowns.

This is better than trying to encode every product preference directly into the ORS request.

## What The Agent Should Do In Practice

When asked to help with ORS development, prefer these actions:
- propose the smallest valid ORS request that can satisfy the requirement
- add post-scoring instead of chasing unsupported request parameters
- use `extra_info` aggressively when route quality matters
- reduce request counts when rate limits are likely
- document hosted-API quirks when discovered
- separate “officially documented” from “observed in live testing”

## Local Supporting Docs

Use these local markdown notes as supporting references:
- [notes/index.md](./notes/index.md)
- [notes/routing.md](./notes/routing.md)
- [notes/route-response.md](./notes/route-response.md)
- [notes/geocoding.md](./notes/geocoding.md)
- [notes/matrix.md](./notes/matrix.md)

## Suggested Prompt Prefix For Another Agent

Use the following framing when bootstrapping another agent:

> You are assisting with openrouteservice integration for a run-route suggestion tool. Prefer the
> current ORS backend docs and observed hosted API behavior over archived examples. Use ORS to
> generate candidate routes and use app-side scoring for product-specific preferences such as
> pavement quality, route feel, and hill profile. When uncertain, separate documented behavior from
> locally observed quirks.
