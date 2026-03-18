# RouteScout Route Badge Trigger Matrix

## Purpose

This document maps Route Card badges to actual trigger logic.

It answers:
- which route data each badge depends on
- which score dimensions support each badge
- what kind of threshold logic should be used
- when a badge should be withheld even if it is plausible

This is an implementation-facing product document.
It sits between:
- the route scoring model
- the route badge spec
- the final runtime implementation

## Product Principle

Badges should be:
- route-truthful
- conservative
- understandable
- stable

Badges should not feel random, and they should not appear just because a plan wanted them.

## Trigger Model

Each badge should be evaluated using three layers:

1. `Eligibility`
   Does the route have the basic trait at all?

2. `Strength threshold`
   Is the trait strong enough to deserve visible card placement?

3. `Conflict check`
   Does the badge conflict with a stronger or more truthful badge?

Only then should the badge be considered for display.

## Threshold Style

For MVP, use relative thresholds instead of pretending we have perfect absolute truth.

Recommended threshold style:
- compare route trait strength against the candidate set
- use normalized component scores where possible
- apply conservative absolute guards where needed

This is especially important for badges like `LT` and `LM`.

## Shared Route Inputs

The first implementation of badge triggers should rely on:
- distance fit
- start convenience
- surface fit
- hill fit
- environmental fit
- route simplicity
- discovery fit
- training fit
- trail suitability

And where available:
- route shape
- ascent / descent
- climb per mile
- ORS `surface`
- ORS `waytype`
- ORS `green`
- ORS `noise`
- future landmark support

## Badge Trigger Matrix

### `LP` Loop

Primary meaning:
- clean loop shape

Primary inputs:
- route shape
- route simplicity

Eligibility:
- route shape is `loop`

Strength threshold:
- route simplicity is at least strong within the candidate set

Conflict check:
- suppress if loop geometry is overly awkward or confusing

MVP rule:
- award `LP` when the route is a loop and route simplicity is not weak

### `NX` Nearby

Primary meaning:
- closer-to-start convenience

Primary inputs:
- start convenience
- actual start offset from requested origin

Eligibility:
- route starts inside requested start radius

Strength threshold:
- start convenience is among the strongest route wins

Conflict check:
- suppress if another route is meaningfully closer and this one is only average

MVP rule:
- award `NX` when the route starts comfortably within the intended start zone and has a strong
  start-convenience score

### `PV` Paved

Primary meaning:
- paved surface dominance

Primary inputs:
- surface fit
- ORS `surface`
- ORS `waytype`

Eligibility:
- paved surfaces are clearly dominant

Strength threshold:
- surface fit is strong for a paved interpretation

Conflict check:
- suppress if the route is materially mixed or trail-forward
- suppress if `TR` is the more truthful terrain identity

MVP rule:
- award `PV` when paved surface is clearly dominant and the route would feel consistently paved

### `TR` Trail

Primary meaning:
- trail character is a defining route feature

Primary inputs:
- trail suitability
- surface fit
- ORS `waytype`
- ORS `surface`

Eligibility:
- trail-heavy surfaces or way types are materially present

Strength threshold:
- trail suitability is strong

Conflict check:
- suppress if the route only has brief trail segments
- suppress if `PV` is more truthful for the route overall

MVP rule:
- award `TR` when trail character is a defining route trait, not a minor accent

### `FL` Flat

Primary meaning:
- flatter route character

Primary inputs:
- hill fit
- climb per mile
- ascent

Eligibility:
- climb per mile is low for the route length

Strength threshold:
- route is flatter than the strongest nearby alternatives

Conflict check:
- suppress if `HL` is also plausible

MVP rule:
- award `FL` when climb-per-mile is low enough that the route would reasonably feel flat

### `HL` Hills

Primary meaning:
- climbing-focused route

Primary inputs:
- hill fit
- training fit
- climb per mile
- ascent

Eligibility:
- climb-per-mile is clearly elevated

Strength threshold:
- route is meaningfully hillier than typical alternatives

Conflict check:
- suppress if the route is only moderately rolling
- suppress if `FL` is more truthful

MVP rule:
- award `HL` when climbing is one of the route's defining traits

### `PK` Park

Primary meaning:
- meaningful park or green-corridor character

Primary inputs:
- environmental fit
- discovery fit
- ORS `green`

Eligibility:
- greener score is meaningfully present

Strength threshold:
- the route has a strong green/scenic signal relative to the candidate set

Conflict check:
- suppress if greenery is only incidental

MVP rule:
- award `PK` when green or park-adjacent character is a true route identity trait

### `LM` Landmark

Primary meaning:
- includes a notable route anchor

Primary inputs:
- discovery fit
- future landmark detection support
- future POI / landmark matching

Eligibility:
- landmark support exists and identifies a meaningful anchor

Strength threshold:
- discovery fit is strong and the landmark is notable enough to mention

Conflict check:
- suppress if the route is only generally scenic
- suppress if there is no supported landmark signal

MVP rule:
- award `LM` only when RouteScout has explicit landmark support

Until landmark support exists, this badge should be held back or manually curated in demos.

### `QT` Quiet

Primary meaning:
- lower-noise route character

Primary inputs:
- environmental fit
- ORS `noise`

Eligibility:
- quiet-related signals are meaningfully favorable

Strength threshold:
- route is calmer than the nearby alternatives

Conflict check:
- suppress if quietness is mixed or inconsistent

MVP rule:
- award `QT` when environmental fit is strong and noise signals are clearly favorable

### `LT` Lit

Primary meaning:
- confidence-friendly for darker hours

Primary inputs:
- route simplicity
- start convenience
- future lighting confidence support
- future area-confidence heuristics

Eligibility:
- route stays in confidence-friendly areas and RouteScout has a meaningful basis for the claim

Strength threshold:
- confidence-related signals are strong and supported

Conflict check:
- suppress if this would rely on guesswork

MVP rule:
- do not auto-award `LT` from weak proxies alone
- require a conservative confidence-specific signal or curated support

`LT` should be one of the strictest badges in the system.

## Mutual Exclusion Matrix

Recommended MVP exclusions:

| Badge | Do not pair with | Reason |
|---|---|---|
| `FL` | `HL` | opposite terrain story |
| `PV` | `TR` | opposite dominant surface story in most cases |

Allowed coexisting pairs:
- `LP` + `NX`
- `PK` + `LM`
- `QT` + `LT`

## Selection Priority

When more than four badges qualify, use this order:

1. strongest truthful standout trait
2. strongest structure or usability trait
3. strongest terrain or surface trait
4. strongest environment or discovery trait

If a fifth badge still seems desirable, drop the weakest one.

## Recommended MVP Badge Confidence Levels

The badges do not all have the same implementation readiness.

### Ready earliest

- `LP`
- `NX`
- `PV`
- `TR`
- `FL`
- `HL`
- `QT`

These can be driven from current scoring and ORS metadata with reasonable confidence.

### Later or conditional

- `PK`
- `LM`
- `LT`

These need better environmental, landmark, or confidence support to avoid overclaiming.

## Implementation Guidance

Recommended implementation order:

1. implement `LP`, `NX`, `PV`, `FL`, `HL`
2. add `TR` and `QT`
3. add `PK` when green/park signals are strong enough
4. add `LM` once landmark support exists
5. add `LT` only when confidence-specific support is trustworthy

## Example Trigger Outcomes

### Confidence Route

Strong signals:
- high route simplicity
- high start convenience
- paved dominance

Likely badges:
- `LP`
- `NX`
- `PV`

Possible fourth:
- `QT`

`LT` only if confidence-specific support exists.

### Training Hill Route

Strong signals:
- high hill fit
- high training fit
- paved consistency

Likely badges:
- `HL`
- `PV`
- `NX`

### Trail Confidence Route

Strong signals:
- trail suitability
- moderate route simplicity
- green corridor character

Likely badges:
- `TR`
- `LP`
- `PK`

## Recommended Next Step

After this matrix, the next useful artifact is:
- a runtime-oriented badge derivation note for `run_router/service.py`

That would map these product rules into concrete score inputs and threshold helpers.
