# RouteScout Route Card Feature Badge Spec

## Purpose

This document defines the feature badge system for Route Cards.

It answers:
- which badges can appear on a Route Card
- what each badge means
- what qualifies a route to earn a badge
- how many badges can appear at once
- how badges should be ordered and prioritized

This is a product spec, not a final implementation formula.
The goal is to make Route Cards feel collectible, meaningful, and easy to scan.

## Product Principle

Feature badges should describe the route itself, not just the selected plan.

A route should earn a badge because the route truly exhibits that trait.

The selected plan still matters because it affects:
- which routes get generated
- which routes get recommended
- which badges are most likely to appear

But the badge row should remain route-truthful.

## Badge System Goals

The badge system should do four things:

1. make a route feel like a distinct collectible object
2. let users scan route strengths quickly
3. reinforce the recommendation logic without dumping score internals
4. stay small enough that the badge row does not become cluttered

## Badge Count Rule

Recommended MVP rule:
- show a maximum of `4` feature badges on a Route Card

Recommended composition:
- `1` structural badge
- `1` terrain or surface badge
- `1` environment or discovery badge
- `1` optional fourth badge if the route has a clearly standout trait

Do not show six or eight badges.
That turns the card into a sticker sheet instead of a collectible object.

## Badge Families

### Structural

These describe the shape or usability of the route.

- `LP` loop
- `NX` nearby

### Surface And Terrain

These describe footing and elevation character.

- `PV` paved
- `TR` trail
- `FL` flat
- `HL` hills

### Environment And Discovery

These describe what the route feels like or passes through.

- `PK` park
- `LM` landmark
- `QT` quiet
- `LT` lit

## Recommended MVP Badge Set

### `LP` Loop

Meaning:
- clean loop route shape

Use when:
- route is a loop
- route shape is legible and not awkwardly tangled

Do not use when:
- the route is technically a loop but looks confusing or heavily self-crossing

### `NX` Nearby

Meaning:
- starts very close to the requested origin

Use when:
- start convenience is high
- route begins comfortably within the user’s intended start zone

Do not use when:
- the route requires noticeable drift before the useful part begins

### `PV` Paved

Meaning:
- paved surface is dominant and route footing is consistent

Use when:
- paved share is clearly dominant
- route surface consistency is strong

Do not use when:
- route is mixed enough that `paved` would be misleading

### `TR` Trail

Meaning:
- trail character is a defining quality of the route

Use when:
- trail suitability is high
- trail-heavy way types and surfaces are meaningfully present

Do not use when:
- the route only touches trail briefly

### `FL` Flat

Meaning:
- lower-climb route character

Use when:
- climb-per-mile is low relative to route length
- the route would reasonably feel flatter than typical alternatives nearby

Do not use when:
- the route has enough rollers or climb to surprise the runner

### `HL` Hills

Meaning:
- climbing is a defining feature of the route

Use when:
- climb-per-mile is clearly elevated
- the route would feel intentionally hill-focused

Do not use when:
- the route only has one moderate hill and is otherwise neutral

### `PK` Park

Meaning:
- route has meaningful park or green-corridor character

Use when:
- greenery score is high
- park adjacency or green corridor presence is a real route trait

Do not use when:
- the route only brushes past one small green patch

### `LM` Landmark

Meaning:
- route includes a notable place or destination anchor

Use when:
- discovery fit is high
- the route passes a genuinely recognizable landmark or destination

Do not use when:
- the route is only generally urban or scenic without a meaningful highlight

### `QT` Quiet

Meaning:
- route has lower-noise character than nearby alternatives

Use when:
- quiet / environmental score is strong
- the route would reasonably feel calmer to run

Do not use when:
- the route only has a few short quiet sections

### `LT` Lit

Meaning:
- route is confidence-friendly for darker hours

Use when:
- RouteScout has enough confidence to claim stronger lighting / safer-feeling coverage
- the route stays in more predictable, confidence-friendly areas

Do not use when:
- this would be a guess rather than a supported signal

`LT` should be conservative.
It is better to omit it than overclaim.

## Mutual Exclusivity Rules

Some badges should not appear together by default.

Recommended MVP rules:
- do not show both `FL` and `HL`
- do not show both `PV` and `TR` unless the route is intentionally hybrid and that is core to its identity

Possible coexistence:
- `LP` and `NX`
- `PK` and `LM`
- `QT` and `LT`

## Badge Ordering

Badges should appear in a stable order.

Recommended order:
1. structural
2. surface or terrain
3. environment or discovery
4. optional standout badge

Example:
- `LP`
- `PV`
- `QT`
- `NX`

This keeps the row readable and consistent across cards.

## Badge Selection Logic

When more badges qualify than can be shown, use this order of decision:

1. include the strongest truthful route trait
2. include at least one structure or usability badge if deserved
3. include at least one terrain or surface badge if deserved
4. include the most distinctive environment or discovery badge
5. stop at four

The row should tell a clean story, not maximize coverage.

## Relationship To Scoring

Badges are downstream of scoring and route metadata.

They should be derived from:
- normalized route traits
- route metadata
- score component wins

They should not expose raw scoring numbers.

Example:
- `QT` can come from a strong quiet/environmental fit
- `PV` can come from dominant paved surface fit
- `NX` can come from strong start-convenience fit
- `LM` can come from strong discovery fit plus landmark support

## Relationship To Plans

Plans influence which routes are likely to earn certain badges.

Examples:
- `Safe Early Morning` is more likely to produce `LT`, `NX`, and `PV`
- `Race Prep Hills` is more likely to produce `HL` and `PV`
- `City Landmark Run` is more likely to produce `LM` and `PK`
- `Trail Confidence Loop` is more likely to produce `TR` and `PK`

But the route must still earn the badge honestly.

## Recommendation For MVP

Recommended launch badge set:
- `LP`
- `NX`
- `PV`
- `TR`
- `FL`
- `HL`
- `PK`
- `LM`
- `QT`
- `LT`

That is enough range to make Route Cards feel distinct without making the system too large.

## Example Route Cards

### Business Traveler Route

Possible badge row:
- `LP`
- `PV`
- `LT`
- `NX`

### City Explorer Route

Possible badge row:
- `LP`
- `LM`
- `PK`

### Hill Training Route

Possible badge row:
- `PV`
- `HL`
- `NX`

### Trail Confidence Route

Possible badge row:
- `TR`
- `PK`
- `LP`

## What To Avoid

Avoid:
- too many badges on one card
- badges that restate obvious stats
- badges that overclaim confidence or safety
- badges that require users to decode opaque abbreviations without help

## Suggested Next Step

The next implementation-facing artifact should be:
- a `route-badge-trigger-matrix` that maps each badge to actual scoring thresholds and route data

After that:
- the Route Card visual spec can define badge art, color roles, and hover / detail behavior
