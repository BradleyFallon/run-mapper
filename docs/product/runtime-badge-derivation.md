# RouteScout Runtime Badge Derivation For `service.py`

## Purpose

This document translates the Route Card badge system into runtime-oriented guidance for
`run_router/service.py`.

It answers:
- where badge derivation should live in the current runtime
- which helper functions should be added
- which route traits should be computed first
- how badges should be attached to loop candidates
- what can be implemented immediately versus later

This is the bridge between:
- [route-card-feature-badge-spec.md](./route-card-feature-badge-spec.md)
- [route-badge-trigger-matrix.md](./route-badge-trigger-matrix.md)
- the current Python runtime in [service.py](/Users/fallbro/code/run-mapper/run_router/service.py)

## Current Runtime Reality

The current runtime already computes:
- distance fit
- pavement fit
- quiet fit
- green fit
- hill fit
- start convenience

The current runtime does not yet compute:
- route simplicity
- discovery fit
- training fit
- trail suitability
- landmark confidence
- lighting confidence

That means the first implementation should not try to fully realize the complete product model in
one step.

## Recommended Runtime Shape

The runtime should grow in this order:

1. keep existing route generation and scoring intact
2. add a route-trait derivation layer
3. add badge-derivation helpers on top of route traits
4. attach badges to `LoopCandidate`
5. later, deepen the scoring model and reuse the same trait layer

The key idea is:
- scores are not enough by themselves
- raw ORS extras are too low-level by themselves
- RouteScout needs a small intermediate trait model

## Recommended New Runtime Types

The current `LoopCandidate` dataclass should eventually carry more than:
- `score`
- `score_breakdown`

Recommended additions:

```python
@dataclass
class RouteTraits:
    paved_ratio: float | None
    trail_ratio: float | None
    average_noise: float | None
    average_green: float | None
    ascent_ft_per_mi: float
    distance_fit: float
    start_convenience: float
    surface_fit: float
    quiet_fit: float
    green_fit: float
    hill_fit: float
    route_simplicity: float | None
    discovery_fit: float | None
    training_fit: float | None
    trail_suitability: float | None
    is_loop: bool
```

```python
@dataclass
class RouteBadge:
    code: str
    label: str
    strength: float
```

And then extend `LoopCandidate` to include:

```python
traits: RouteTraits | None = None
badges: list[RouteBadge] | None = None
```

This keeps the runtime structured and avoids hiding badge logic inside ad hoc dictionaries.

## Recommended Helper Functions

The first runtime pass should add these helpers:

### 1. `derive_route_traits(...)`

Purpose:
- compute reusable route traits from `RouteResult`, score breakdowns, and start metadata

Inputs:
- `route: RouteResult`
- `score_breakdown: dict[str, float]`
- `target_distance_m: float`
- `start_offset_m: float`
- `start_radius_m: float`

Outputs:
- `RouteTraits`

This helper should become the single place where badge logic gets its underlying truth.

### 2. `derive_route_badges(...)`

Purpose:
- turn `RouteTraits` into a ranked list of candidate badges

Inputs:
- `traits: RouteTraits`

Outputs:
- `list[RouteBadge]`

This helper should:
- evaluate badge eligibility
- apply thresholds
- apply conflict suppression
- sort by badge strength
- trim to the maximum display count

### 3. `select_display_badges(...)`

Purpose:
- enforce the final card badge rules

Inputs:
- `candidate_badges: list[RouteBadge]`

Outputs:
- `list[RouteBadge]`

This helper is where rules like:
- maximum of `4`
- no `FL` and `HL` together
- no `PV` and `TR` together unless explicitly allowed

should live.

## Where To Call Badge Logic

The best current insertion point is inside `build_loop_candidates(...)`, after
`score_loop_candidate(...)` returns.

Current flow:

1. fetch ORS route
2. compute `score` and `score_breakdown`
3. create `LoopCandidate`

Recommended flow:

1. fetch ORS route
2. compute `score` and `score_breakdown`
3. compute `traits = derive_route_traits(...)`
4. compute `badges = derive_route_badges(traits)`
5. create `LoopCandidate` with `traits` and `badges`

This keeps badge derivation attached to the same scoring pass rather than requiring a second route
analysis stage.

## First-Pass Trait Derivation

The first implementation should derive traits only from data already available in `service.py`.

### Available Immediately

These can be derived right away:
- `paved_ratio`
- `trail_ratio`
- `average_noise`
- `average_green`
- `ascent_ft_per_mi`
- `distance_fit`
- `start_convenience`
- `surface_fit`
- `quiet_fit`
- `green_fit`
- `hill_fit`

### First Approximation Traits

These should be approximated in the first pass:

#### `is_loop`

Suggested first rule:
- true when loop generation is used and the returned geometry looks like a round-trip result

Later:
- confirm by comparing first and last coordinates if ORS returns a closed shape or near-closed
  shape

#### `route_simplicity`

Suggested first rule:
- derive from a weighted combination of:
  - start convenience
  - lower trail_ratio for confidence-oriented road routes
  - lower hill intensity for routes expected to be easy and legible

Later:
- use turn count
- self-intersection heuristics
- route legibility heuristics

#### `trail_suitability`

Suggested first rule:
- use a combination of:
  - `trail_ratio`
  - inverse paved dominance
  - acceptable hill profile

Later:
- include steepness classes and hazard-aware logic

#### `training_fit`

Suggested first rule:
- use a combination of:
  - distance fit
  - hill fit
  - surface fit

Later:
- add interruption avoidance and climb-pattern specifics

#### `discovery_fit`

Suggested first rule:
- use a combination of:
  - green fit
  - quiet fit

Later:
- add POIs
- add landmark support
- add scenic corridor heuristics

## First-Pass Badge Derivation

Given the current runtime, the first realistic badge pass should only auto-derive the badges that
have strong support today.

### Good First-Pass Auto Badges

- `NX`
- `PV`
- `TR`
- `FL`
- `HL`
- `QT`

### Conditional First-Pass Badge

- `LP`

Only if loop truth can be derived reliably enough from the returned route geometry or the loop
generation path.

### Badges That Should Wait

- `PK`
- `LM`
- `LT`

Reason:
- `PK` needs stronger park or green-corridor confidence than raw green score alone
- `LM` needs landmark-aware support
- `LT` needs real lighting or confidence support and should not be guessed from weak proxies

## Suggested MVP Threshold Helpers

The runtime should not hardcode badge logic inline.
Use small helper functions instead.

Recommended first helpers:

```python
def qualifies_nearby(traits: RouteTraits, *, threshold: float = 0.8) -> bool: ...
def qualifies_paved(traits: RouteTraits, *, paved_ratio_threshold: float = 0.65) -> bool: ...
def qualifies_trail(traits: RouteTraits, *, trail_ratio_threshold: float = 0.4) -> bool: ...
def qualifies_flat(traits: RouteTraits, *, climb_ft_per_mi_threshold: float = 90.0) -> bool: ...
def qualifies_hills(traits: RouteTraits, *, climb_ft_per_mi_threshold: float = 180.0) -> bool: ...
def qualifies_quiet(traits: RouteTraits, *, quiet_threshold: float = 0.72) -> bool: ...
```

These thresholds are starting points only.
They should be configurable constants near the top of the module.

## Conflict Resolution

Conflict logic should run after badge qualification, not before.

Recommended rules:

### `FL` vs `HL`

- if both qualify, keep the one with stronger normalized evidence
- usually compare flatness or hill strength margins against the threshold

### `PV` vs `TR`

- if both qualify, keep the more dominant terrain identity
- prefer `PV` when paved ratio clearly dominates
- prefer `TR` when trail ratio clearly dominates

### Badge Count Limit

- after conflict resolution, sort by badge strength
- trim to a maximum of `4`

## Suggested Sorting Logic

Each `RouteBadge` should have a `strength` value.

Suggested basis:
- how far above threshold the route is
- or the underlying normalized component score

Then sort by:
1. strongest standout trait
2. structure and usability
3. terrain and surface
4. environment and discovery

This matches the product badge spec.

## Example Runtime Flow

Recommended current structure:

```python
score, score_breakdown = score_loop_candidate(...)
traits = derive_route_traits(
    route=route,
    score_breakdown=score_breakdown,
    target_distance_m=target_distance_m,
    start_offset_m=start_offset_m,
    start_radius_m=start_radius_m,
)
badges = derive_route_badges(traits)
candidate = LoopCandidate(
    ...,
    score=score,
    score_breakdown=score_breakdown,
    traits=traits,
    badges=badges,
)
```

## Recommended Implementation Order

1. add `RouteTraits`
2. add `RouteBadge`
3. add `derive_route_traits(...)`
4. add first-pass badges: `NX`, `PV`, `TR`, `FL`, `HL`, `QT`
5. attach badges to `LoopCandidate`
6. expose badges in the standalone script output
7. later add `LP`, `PK`, `LM`, `LT` as better support exists

## Testing Guidance

The first badge tests should focus on deterministic helpers rather than live ORS calls.

Suggested tests:
- paved-heavy extras produce `PV`
- trail-heavy extras produce `TR`
- low climb-per-mile produces `FL`
- high climb-per-mile produces `HL`
- strong start convenience produces `NX`
- conflict resolution suppresses `FL` when `HL` is clearly stronger

## Recommended Next Move

After this note, the next step should be one of:

1. implement `RouteTraits` and first-pass badge derivation in [service.py](/Users/fallbro/code/run-mapper/run_router/service.py)
2. update [suggest_loop.py](/Users/fallbro/code/run-mapper/scripts/suggest_loop.py) to print candidate badges
3. add unit tests for the trait and badge helpers
