# RouteScout Route Scoring Model

## Purpose

This document defines how RouteScout should compare and rank route candidates.

The scoring model is the bridge between:
- a user's selected plan
- the route candidates returned by ORS
- the final recommendation shown in the product

This is a product-scoring document, not a strict code contract.
It defines the intended model for MVP and the path for improving it later.

## Scoring Goals

The scoring model should do four things well:

1. reward routes that match the selected plan
2. make tradeoffs visible instead of opaque
3. produce a clear recommendation plus alternatives
4. generate explanations that a runner can understand quickly

The model should not try to pretend that every routing preference can be controlled perfectly by
ORS alone.

## Product Principle

ORS generates plausible route candidates.
RouteScout scores them for product fit.

That means RouteScout should use a hybrid approach:
- request shaping in ORS when supported
- app-side scoring for product-specific judgment

## Scoring Pipeline

The recommended pipeline is:

1. interpret the selected plan into routing preferences
2. use ORS to generate a small candidate set
3. collect route metadata and extras
4. apply basic hard filters
5. calculate normalized component scores
6. weight those scores by plan and category
7. rank candidates
8. generate a short explanation for the recommended route

## Where ORS Helps Directly

ORS can help with:
- loop generation
- target route length
- route geometry
- distance and duration
- ascent / descent
- `green` weighting
- `quiet` weighting
- `extra_info` such as surface, way type, green, noise, suitability, and potentially steepness

ORS should be treated as the route generator and metadata provider, not the final judge of what is
best for the user.

## Hard Filters

Before scoring, RouteScout should reject or downrank obviously poor candidates.

Examples:
- route is far outside acceptable distance tolerance
- start point is too far from requested start radius
- surface mix clearly violates plan intent
- trail route exceeds acceptable steepness or hazard tolerance
- technical training route looks too interruption-prone

For MVP, these can begin as strong penalties instead of strict exclusions if needed.

## Normalized Score Components

Every candidate should be scored from `0.0` to `1.0` on a shared set of dimensions.

### 1. Distance Fit

Question:
- how close is the route to the target distance?

High score:
- route lands close to the requested mileage

Low score:
- route is meaningfully shorter or longer than requested

This should be one of the strongest components across all plans.

### 2. Start Convenience

Question:
- how close is the route start to the requested location or start radius?

High score:
- route begins very close to where the user wanted

Low score:
- route requires meaningful drift beyond the intended start zone

This matters especially for `Confidence` plans.

### 3. Surface Fit

Question:
- how well does the route surface match the plan?

Signals:
- ORS `surface`
- ORS `waytype`

Examples:
- paved-heavy plan should score asphalt, concrete, and similar surfaces highly
- trail-heavy plan should score path and track segments more favorably

### 4. Hill Fit

Question:
- how well does the route's elevation character match the plan?

Signals:
- ascent
- descent
- climb per mile
- later: `steepness` extras where useful

Examples:
- flatter plans should score low climb-per-mile better
- training hill plans should score higher climb-per-mile better

### 5. Environmental Fit

Question:
- how well does the route's feel match the desired environment?

Signals:
- ORS `green`
- ORS `noise`

Examples:
- quiet, park-adjacent routes should score better for calm plans
- some plans may care less about quietness

These are useful proxies, not guarantees.

### 6. Route Simplicity

Question:
- how easy does the route look to follow and trust?

Early MVP proxies:
- closer start
- cleaner loop shape
- fewer awkward deviations

Later signals:
- turn count
- self-intersection complexity
- route legibility heuristics

This matters heavily for `Confidence` plans.

### 7. Discovery Fit

Question:
- how worthwhile does the route feel for exploration?

Early MVP proxies:
- greener score
- category-specific route character heuristics

Later signals:
- landmark density
- POI quality
- scenic corridors

This matters most for `Explore` plans.

### 8. Training Fit

Question:
- how well does the route function as a workout tool?

Signals:
- distance fit
- hill fit
- pavement consistency
- interruption avoidance proxies

This matters most for `Training` plans.

### 9. Trail Suitability

Question:
- how well does the route match desired trail character without becoming reckless?

Signals:
- trail-heavy way types
- surface mix
- steepness tolerance
- hazard proxies later

This matters most for `Trail` plans.

## MVP Core Score Set

For MVP, RouteScout should start with this core score set:
- distance fit
- start convenience
- surface fit
- hill fit
- environmental fit
- route simplicity

Then add plan/category emphasis through weighting rather than trying to create fully separate
scoring systems for every plan.

## Category Weighting Model

The simplest MVP approach is:
- shared core dimensions for every route
- category-level weighting changes
- plan-level fine-tuning on top

## Recommended Category Weighting

The weights below are product targets, not exact implementation requirements.
Each category should sum to `1.00`.

### Confidence

Use when reliability and trust matter most.

| Dimension | Weight |
|---|---:|
| Distance fit | 0.24 |
| Start convenience | 0.16 |
| Surface fit | 0.18 |
| Hill fit | 0.12 |
| Environmental fit | 0.12 |
| Route simplicity | 0.18 |

### Explore

Use when discovery matters more than technical precision.

| Dimension | Weight |
|---|---:|
| Distance fit | 0.20 |
| Start convenience | 0.10 |
| Surface fit | 0.12 |
| Hill fit | 0.08 |
| Environmental fit | 0.16 |
| Route simplicity | 0.10 |
| Discovery fit | 0.24 |

### Training

Use when route technicals matter most.

| Dimension | Weight |
|---|---:|
| Distance fit | 0.24 |
| Start convenience | 0.08 |
| Surface fit | 0.18 |
| Hill fit | 0.20 |
| Environmental fit | 0.06 |
| Route simplicity | 0.08 |
| Training fit | 0.16 |

### Trail

Use when adventure matters, but with guardrails.

| Dimension | Weight |
|---|---:|
| Distance fit | 0.20 |
| Start convenience | 0.08 |
| Surface fit | 0.16 |
| Hill fit | 0.14 |
| Environmental fit | 0.10 |
| Route simplicity | 0.08 |
| Trail suitability | 0.24 |

## Plan-Level Modifiers

Within a category, the selected plan should shift the scoring emphasis.

Examples:

### Safe Early Morning

Should increase emphasis on:
- route simplicity
- start convenience
- flatter hill fit
- paved surface fit

### Easy Nearby Loop

Should increase emphasis on:
- start convenience
- simplicity
- reasonable all-around fit

### City Landmark Run

Should increase emphasis on:
- discovery fit
- environmental fit
- route cohesion

### Race Prep Hills

Should increase emphasis on:
- distance fit
- hill fit
- training fit
- paved consistency

### Trail Confidence Loop

Should increase emphasis on:
- trail suitability
- hill tolerance fit
- route clarity

## Deterministic Versus LLM-Assisted Logic

### Deterministic

The ranking model itself should remain deterministic.

Deterministic responsibilities:
- component score calculation
- weighting
- total score calculation
- final ranking

### LLM-Assisted

LLM assistance should be used for:
- interpreting natural-language design briefs into preferences
- helping explain the final recommendation in clearer language
- optionally summarizing tradeoffs between candidates

The LLM should not be the primary scoring authority.

## Recommendation Output

The product should return:
- one recommended route
- a small number of alternatives
- a visible score breakdown or reason breakdown

The explanation should map back to the score components.

Good recommendation language:
- "Closest to your target distance"
- "Flatter and easier to follow"
- "More paved than the alternatives"
- "Stronger hill match for your workout"

## MVP Explanation Model

For MVP, explanations can be generated from the top 2 to 3 strongest component wins.

Example:
- best distance match
- flatter than alternatives
- more paved and simpler to follow

This is enough to make the recommendation feel defensible.

## Current Runtime Alignment

The current Python runtime already implements a simplified version of this model in
`run_router/service.py`.

Current implemented score components:
- distance
- pavement
- quiet
- green
- hills
- start

Current implemented weights:
- distance `0.34`
- pavement `0.20`
- quiet `0.14`
- green `0.12`
- hills `0.12`
- start `0.08`

That is a reasonable initial baseline, but it is still flatter than the full product model.

Most notable gaps between runtime and product target:
- no explicit discovery-fit dimension yet
- no explicit route-simplicity dimension yet
- no explicit training-fit dimension yet
- no explicit trail-suitability dimension yet
- no category-specific weighting in the current implementation

## Recommended MVP Implementation Strategy

Implementation order:

1. keep the current shared deterministic baseline
2. add category-level weighting
3. add route-simplicity heuristics
4. add lightweight discovery/training/trail secondary dimensions
5. improve explanation generation from score breakdowns

This keeps the model simple enough to ship while aligning it more closely with the product design.

## Open Questions

These should be resolved in future implementation work:

1. Should distance fit remain the heaviest global factor, or should category-specific weighting
   dominate more strongly?
2. What is the best early MVP proxy for route simplicity?
3. How should interruption avoidance be estimated before richer map semantics are available?
4. How much landmark-aware scoring is required before `City Landmark Run` truly feels distinct?
5. Should trail suitability remain a soft ranking signal or become a stronger filter for bad
   terrain matches?

## Recommended Next Doc

After this scoring model, the next design doc should be:
- `ios-information-architecture.md`

The web planning structure, starter plans, and scoring model are now defined well enough to begin
mapping the iPhone app.
