# RouteScout Route Card System

## Purpose

This document defines the active Route Card badge model for RouteScout.

It combines the earlier badge spec and badge trigger matrix into one reference covering:
- what badges exist
- what they mean
- how many can appear
- how they should be selected
- what route evidence should support them

## Product Principle

Route Card badges should be:
- route-truthful
- conservative
- easy to scan
- stable across similar routes

A route should earn a badge because it truly exhibits that trait, not just because the selected
plan wanted it.

## Badge System Goals

The badge system should:
1. make routes feel collectible and distinct
2. let users scan route strengths quickly
3. reinforce recommendation logic without exposing raw score math
4. stay compact enough that Route Cards remain clean

## Badge Count Rule

Recommended MVP rule:
- show a maximum of `4` badges on a Route Card

Recommended composition:
- `1` structural badge
- `1` terrain or surface badge
- `1` environment or discovery badge
- `1` optional standout badge if the route clearly deserves it

## Badge Families

### Structural

- `LP` loop
- `NX` nearby

### Surface And Terrain

- `PV` paved
- `TR` trail
- `FL` flat
- `HL` hills

### Environment And Discovery

- `PK` park
- `LM` landmark
- `QT` quiet
- `LT` lit

## Badge Set

### `LP` Loop

Meaning:
- clean loop route shape

Use when:
- the route is a loop
- the loop is legible rather than awkward or confusing

### `NX` Nearby

Meaning:
- starts comfortably close to the requested origin

Use when:
- the route begins inside the intended start zone
- start convenience is meaningfully strong

### `PV` Paved

Meaning:
- paved footing is the dominant route character

Use when:
- paved surfaces clearly dominate
- the route would feel consistently paved

### `TR` Trail

Meaning:
- trail character is a defining route trait

Use when:
- trail-heavy surfaces or way types are materially present
- trail suitability is strong

### `FL` Flat

Meaning:
- lower-climb route character

Use when:
- climb-per-mile is low
- the route would feel flatter than nearby alternatives

### `HL` Hills

Meaning:
- climbing is one of the route's defining traits

Use when:
- climb-per-mile is clearly elevated
- the route feels intentionally hill-focused

### `PK` Park

Meaning:
- meaningful park or green-corridor character

Use when:
- green or park-like character is a true part of the route identity

### `LM` Landmark

Meaning:
- includes a notable route anchor

Use when:
- RouteScout has explicit landmark support
- the landmark is strong enough to mention

### `QT` Quiet

Meaning:
- lower-noise route character than nearby alternatives

Use when:
- quiet / environmental fit is strong
- the route would reasonably feel calmer to run

### `LT` Lit

Meaning:
- confidence-friendly for darker hours

Use when:
- RouteScout has enough supported signal to make this claim conservatively

If that confidence does not exist, do not show it.

## Trigger Model

Each badge should be evaluated with three layers:

1. `Eligibility`
   Does the route exhibit the basic trait at all?
2. `Strength threshold`
   Is the trait strong enough to deserve visible card placement?
3. `Conflict check`
   Is there a stronger or more truthful badge that should suppress it?

Only then should the badge be considered for display.

## Shared Route Inputs

Badge decisions should rely on:
- route shape
- start convenience
- surface fit
- hill fit
- environmental fit
- route simplicity
- discovery fit
- training fit
- trail suitability
- available ORS `surface`, `waytype`, `green`, and `noise` support

For MVP, use relative thresholds and candidate-set comparisons where possible.

## Mutual Exclusion Rules

Do not show together by default:
- `FL` and `HL`
- `PV` and `TR` unless the route is intentionally hybrid and that is core to its identity

Can coexist:
- `LP` and `NX`
- `PK` and `LM`
- `QT` and `LT`

## Badge Ordering

Stable order:
1. structural
2. surface or terrain
3. environment or discovery
4. optional standout badge

Example:
- `LP`
- `PV`
- `QT`
- `NX`

## Selection Logic

When more than four badges qualify:
1. include the strongest truthful route trait
2. include a structure or usability badge if deserved
3. include a terrain or surface badge if deserved
4. include the most distinctive environment or discovery badge
5. stop at four

The row should tell a clean story rather than maximize coverage.

## MVP Confidence Levels

### Good Early Badge Candidates

These are realistic early badges because they map well to current route signals:
- `NX`
- `PV`
- `TR`
- `FL`
- `HL`
- `QT`

### Conditional Or Later Badges

These need better support or more conservative handling:
- `LP`
- `PK`
- `LM`
- `LT`

## Relationship To Scoring

Badges are downstream of scoring and route metadata.

They should be derived from:
- route traits
- route metadata
- score component wins

They should not expose raw numeric score details.

## Runtime Note

The runtime-oriented implementation note has been moved out of the product docs so this directory
stays product-focused.

See:
- [route-badge-runtime.md](/Users/fallbro/code/run-mapper/docs/implementation/route-badge-runtime.md)
