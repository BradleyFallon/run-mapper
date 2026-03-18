# RouteScout Launch Plan Catalog

## Purpose

This document defines the starter plans that ship in the RouteScout MVP.

The goal is to make the product concrete:
- which plans exist at launch
- what category each belongs to
- what defaults each plan should carry
- what users can edit in the basic view
- what belongs in advanced options

This catalog is for MVP planning.
It should stay small and opinionated.

## Catalog Structure

Each launch plan should define:
- name
- category
- intended user need
- top priority
- secondary priority
- default route shape
- default planning biases
- editable basic controls
- editable advanced controls

## Launch Plan Set

The MVP should launch with five starter plans:

1. `Safe Early Morning`
2. `Easy Nearby Loop`
3. `City Landmark Run`
4. `Race Prep Hills`
5. `Trail Confidence Loop`

This is enough range to support the main personas without overwhelming the first-use experience.

## Summary Table

| Plan | Category | Primary user | Top priority | Secondary priority | Core promise |
|---|---|---|---|---|---|
| `Safe Early Morning` | `Confidence` | Vee | `Lighting and confidence` | `Simple navigation` | Reliable, close, flatter, easy-to-follow route |
| `Easy Nearby Loop` | `Confidence` | general | `Closer start` | `Distance accuracy` | Simple nearby default for low-friction route generation |
| `City Landmark Run` | `Explore` | Ace | `Landmarks` | `Nature access` | City discovery route built around memorable highlights |
| `Race Prep Hills` | `Training` | Flo | `Elevation profile` | `Distance accuracy` | Technically useful route with stronger hill and surface intent |
| `Trail Confidence Loop` | `Trail` | Sam | `Trail quality` | `Simple navigation` | Trail-forward route with guardrails on difficulty and confusion |

## Shared MVP Defaults

These defaults should apply unless a plan overrides them:
- route shape: `loop`
- route candidate count target: `3`
- distance tolerance: moderate by default
- selected route should be one recommended route plus alternatives

Shared basic controls:
- target distance
- distance tolerance
- start location
- start radius
- route shape
- terrain bias
- surface bias

Shared advanced controls:
- interruption avoidance
- stronger environmental bias
- stronger training bias
- more explicit trail tolerance

Shared priority rule:
- every starter plan must define one `top priority`
- every starter plan should define one `secondary priority`
- a `tertiary priority` may exist in advanced settings as a tie-breaker

## Plan 1: Safe Early Morning

### Category

`Confidence`

### Designed For

- business travelers
- unfamiliar-city runners
- users who want low cognitive load and strong route trust

### Core Promise

Find a route that feels easy to trust:
- close to start
- flatter
- paved leaning
- simple to follow

### Priority Ranking

- top priority: `Lighting and confidence`
- secondary priority: `Simple navigation`
- tertiary priority: `Paved surface`

### Default Biases

- route shape: `loop`
- start radius: small
- distance tolerance: moderate
- terrain: flatter
- surface: paved leaning
- confidence: high
- adventure: low
- route simplicity: high priority

### Basic Controls

- target distance
- distance tolerance
- start radius
- flatter vs hillier
- paved vs mixed surface

### Advanced Controls

- stronger route simplicity bias
- stronger quiet preference
- stronger greenery preference
- stronger paved-surface preference

### Notes

This should be the most approachable plan for first-time users.

## Plan 2: Easy Nearby Loop

### Category

`Confidence`

### Designed For

- users who just want a quick default run
- local runners who want something simple without thinking much

### Core Promise

Give me a solid nearby loop without a lot of setup.

### Priority Ranking

- top priority: `Closer start`
- secondary priority: `Distance accuracy`
- tertiary priority: `Simple navigation`

### Default Biases

- route shape: `loop`
- start radius: small-to-moderate
- distance tolerance: moderate
- terrain: neutral to slightly flatter
- surface: mixed but road-safe leaning
- confidence: medium-high
- adventure: low

### Basic Controls

- target distance
- start radius
- flatter vs hillier
- paved vs trail leaning

### Advanced Controls

- tighter tolerance
- stronger paved preference
- stronger quiet preference
- stronger simplicity bias

### Notes

This is the generic fallback starter plan when the user does not strongly identify with a more
specific use case.

## Plan 3: City Landmark Run

### Category

`Explore`

### Designed For

- vacation runners
- city explorers
- users who care more about memorable route character than strict training precision

### Core Promise

Build a runnable city route that feels worth doing because of what it passes through.

### Priority Ranking

- top priority: `Landmarks`
- secondary priority: `Nature access`
- tertiary priority: `Simple navigation`

### Default Biases

- route shape: `loop`
- start radius: moderate
- distance tolerance: moderate
- terrain: neutral
- surface: mixed urban runnable surface
- discovery: high
- confidence: medium
- adventure: medium

### Basic Controls

- target distance
- start radius
- landmark / discovery intensity
- paved vs mixed surface
- confidence vs adventure

### Advanced Controls

- stronger landmark density
- stronger route cohesion bias
- stronger scenic bias
- stronger route simplicity bias if desired

### Notes

This plan should bias for places worth seeing without becoming chaotic or overly touristy.

## Plan 4: Race Prep Hills

### Category

`Training`

### Designed For

- serious runners
- race-prep sessions
- users who care about technical route fit

### Core Promise

Build a route that works as a training tool, not just a pretty suggestion.

### Priority Ranking

- top priority: `Elevation profile`
- secondary priority: `Distance accuracy`
- tertiary priority: `Paved surface`

### Default Biases

- route shape: `loop`
- start radius: small-to-moderate
- distance tolerance: tighter
- terrain: hillier
- surface: strong paved consistency
- interruption avoidance: higher
- training fit: high priority

### Basic Controls

- target distance
- distance tolerance
- hill intent
- paved consistency
- start radius

### Advanced Controls

- interruption avoidance
- stronger elevation intent
- stronger surface consistency
- flatter vs steeper climb distribution
- regenerate around a tighter start constraint

### Notes

This plan should be the clearest example of why saved plan variants matter.

Recommended likely saved variants:
- `Race Prep Hills 5 Mile`
- `Race Prep Hills 8 Mile`
- `Race Prep Hills Moderate Climb`
- `Race Prep Hills Long Climb`

## Plan 5: Trail Confidence Loop

### Category

`Trail`

### Designed For

- trail-curious runners
- runners who want adventure with guardrails
- users who want trail character without getting in over their head

### Core Promise

Find a trail-forward route that feels interesting but still manageable and navigable.

### Priority Ranking

- top priority: `Trail quality`
- secondary priority: `Simple navigation`
- tertiary priority: `Nature access`

### Default Biases

- route shape: `loop`
- start radius: moderate
- distance tolerance: moderate
- terrain: moderate trail challenge
- surface: trail leaning
- confidence: medium-high
- adventure: medium
- hazard tolerance: lower

### Basic Controls

- target distance
- trail vs paved leaning
- steepness tolerance
- confidence vs adventure
- start radius

### Advanced Controls

- stronger trail preference
- hazard-aware ranking
- stronger steepness ceiling
- terrain-condition tolerance
- route simplicity bias

### Notes

This plan should make trail discovery feel inviting, not reckless.

## Category-Level Behavior

The category should influence how plans are displayed and filtered, but the plan itself remains the
main unit the user selects.

Plan cards should surface:
- top priority
- secondary priority
- one supporting characteristic from the plan defaults

### Confidence

Display emphasis:
- reliable
- simple
- lower-friction

### Explore

Display emphasis:
- discovery
- landmarks
- memorable areas

### Training

Display emphasis:
- precision
- technical fit
- repeatability

### Trail

Display emphasis:
- nature
- adventure
- terrain guardrails

## MVP Editing Model

The planner should present each starter plan with:
- a short summary
- a few high-leverage basic controls
- an expandable advanced section

The MVP should avoid exposing every possible tuning knob immediately.

Recommended rule:
- basic view: 4 to 6 controls
- advanced view: deeper tuning specific to the plan

## Recommendation Rules

For MVP:
- the product should recommend a starter plan based on browsing context or category filter
- but the user should still be able to switch plans easily

Examples:
- users browsing `Confidence` should likely see `Safe Early Morning` first
- users browsing `Training` should likely see `Race Prep Hills` first

## Open Questions

These questions remain open:

1. Should `Easy Nearby Loop` be the default first plan, or should the app bias toward a more
   contextual recommendation?
2. How much landmark selection should be embedded directly inside `City Landmark Run` in MVP?
3. Should `Trail Confidence Loop` ship at launch if trail-data confidence is weaker than city/road
   data?
4. Should tighter training controls be visible immediately in `Race Prep Hills`, or still live
   behind advanced options?

## Recommended Next Doc

After this catalog, the next most useful doc is:
- `route-scoring-model.md`

That is the document that will define how these plan defaults actually affect route ranking.
