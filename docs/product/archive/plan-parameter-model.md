# RouteScout Plan Parameter Model

## Purpose

This document defines the parameter model for RouteScout plans.

It answers:
- which parameters RouteScout should support
- how many parameters should be exposed in MVP
- how priority ranking should work
- which parameters should appear on plan cards

This is a product-model doc.
It is meant to keep the plan system powerful without letting it turn into an unstructured wall of
settings.

## Core Principle

Not every plan input should be treated the same way.

RouteScout should separate:
- hard requirements
- ranked priorities
- secondary tuning parameters

This makes the system easier to understand and easier to surface in the UI.

## Recommended MVP Structure

Each plan should contain three layers:

### 1. Hard Requirements

These are direct planning requirements, not preferences.

They should include:
- target distance
- distance tolerance
- start location
- start radius
- route shape

These define the basic planning envelope.
They should not be buried in advanced settings.

### 2. Ranked Priorities

These are the plan's main instructions to the planner.

They answer:
- what matters most if tradeoffs appear?

Each plan should require:
- one `top priority`

Each plan may also support:
- one `secondary priority`
- one `tertiary priority`

This gives the planner a clear instruction hierarchy without making the model too complicated.

### 3. Supporting Parameters

These are tuning parameters that refine behavior but do not need to be shown as the core identity
of the plan.

Examples:
- stronger paved preference
- tighter start-radius behavior
- stronger quiet bias
- higher adventure tolerance
- trail difficulty ceiling

These belong in advanced editing.

## Why A Priority System Is Useful

Yes, RouteScout should require a top priority.

That creates real value because route planning is full of tradeoffs.

Example:
- a route may match the distance perfectly but be hillier than desired
- another route may be flatter but start farther away
- another may be scenic but less direct

Without a clear priority structure, the recommendation logic becomes vague and the plan cards
become generic.

With a required top priority, RouteScout can say:
- this plan is distance-first
- this plan is confidence-first
- this plan is landmark-first
- this plan is elevation-pattern-first

That is much clearer for both users and scoring logic.

## Recommended MVP Parameter Families

The parameter model should be organized into families rather than one long flat list.

### Distance And Shape

- target distance
- distance tolerance
- route shape

### Start Constraints

- start location
- start radius

### Surface And Terrain

- surface preference
- hill preference
- trail preference
- terrain difficulty ceiling

### Environment And Feel

- quiet preference
- greenery / nature preference
- discovery / landmark preference
- simplicity / confidence preference

### Technical Training

- interruption avoidance
- surface consistency
- elevation pattern emphasis

### Safety And Navigation Confidence

- route simplicity
- closer-start preference
- lit-area preference
- unfamiliar-area caution bias

Some of these will overlap in implementation.
That is fine.
The important thing is that the user-facing model stays understandable.

## Recommended MVP Parameter Set

The MVP should support about `10` to `12` editable parameters per plan overall.

That does not mean all of them should be equally visible.

Recommended split:
- `5` core fields always visible
- `3` ranked priorities visible in the main plan summary
- `4` to `6` advanced tuning fields available on demand

This is enough flexibility without creating a control panel that feels heavy.

## Basic Vs Advanced

### Basic View

The basic plan editor should show:
- target distance
- distance tolerance
- start radius
- route shape
- top priority
- secondary priority
- surface preference
- hill preference

This is enough for most users.

### Advanced View

Advanced should hold:
- tertiary priority
- quiet preference
- greenery preference
- interruption avoidance
- surface consistency
- trail difficulty ceiling
- stronger confidence bias
- stronger landmark bias
- stronger elevation-pattern bias

The exact advanced list can vary by category and starter plan.

## Recommended Priority Vocabulary

The priorities should be plain-language and product-facing.

Good priority labels:
- `Distance accuracy`
- `Closer start`
- `Simple navigation`
- `Paved surface`
- `Elevation profile`
- `Landmarks`
- `Quiet surroundings`
- `Nature access`
- `Trail quality`
- `Low interruptions`
- `Lighting and confidence`

Avoid exposing low-level ORS language directly.

Bad user-facing labels:
- `waytype`
- `surface score`
- `green weighting`
- `noise weighting`
- `steepness class`

Those belong in implementation, not in the product model.

## Recommended Priority Rule

Each plan should always have:
- `top priority`

Each plan should usually have:
- `secondary priority`

Each plan may optionally have:
- `tertiary priority`

For MVP, I would stop there.

Do not let users rank six or eight priorities.
That looks powerful but usually collapses into noise.

Three is enough:
- one dominant instruction
- one supporting instruction
- one tie-breaker

## Top Priority Candidates

The top priority should come from a limited set.

Recommended MVP top-priority options:
- `Distance accuracy`
- `Closer start`
- `Simple navigation`
- `Paved surface`
- `Elevation profile`
- `Landmarks`
- `Quiet surroundings`
- `Nature access`
- `Trail quality`
- `Low interruptions`
- `Lighting and confidence`

This is a broad enough set to support the launch plans without overcomplicating the model.

## Parameter Count Guardrails

RouteScout should support more underlying scoring dimensions than it exposes directly.

Guardrails:
- do not show more than `8` editable items in the default plan editor
- do not show more than `12` total editable items in MVP advanced editing
- do not show more than `3` ranked priorities
- do not show more than `3` summary parameters on a plan card

That keeps the system legible.

## Plan Card Rules

Yes, the plan cards should show the top priority parameters.

That is the right place to express plan identity.

Each plan card should show:
- category
- plan name
- top priority
- secondary priority
- one supporting characteristic

Examples:

`Safe Early Morning`
- top priority: `Lighting and confidence`
- secondary priority: `Simple navigation`
- supporting characteristic: `Paved surface`

`Race Prep Hills`
- top priority: `Elevation profile`
- secondary priority: `Distance accuracy`
- supporting characteristic: `Paved surface`

`City Landmark Run`
- top priority: `Landmarks`
- secondary priority: `Nature access`
- supporting characteristic: `Simple navigation`

These should appear as:
- bottom stat rows
- compact badges
- or short labeled traits

They should not appear as a dense settings dump.

## Relationship To Scoring

The priority model should map directly into route scoring.

Recommended logic:
- top priority gets the strongest scoring weight
- secondary priority gets meaningful but smaller weight
- tertiary priority acts as a tie-breaker or modifier

This creates a clean line from:
- plan setup
- to route ranking
- to explanation copy

Example explanation:
- "Recommended because this plan prioritizes lighting and confidence first, and this route stays
  simpler and closer to your start than the alternatives."

## Relationship To Categories

Categories should guide defaults, but priorities should define the actual plan behavior.

That means:
- category helps users browse and filter plans
- priorities tell the planner what matters most

This is the cleaner model.

## Launch Recommendation

For MVP, use this model:

1. every plan has hard requirements
2. every plan has one required top priority
3. every plan has one default secondary priority
4. every plan may have one tertiary priority in advanced settings
5. plan cards show the top two priorities plus one supporting characteristic

That gives RouteScout:
- a stronger mental model
- better route explanations
- cleaner plan cards
- a controllable UI

## Suggested Next Step

The next product artifact should be:
- a pass on the launch plan catalog that assigns explicit top and secondary priorities to every
  starter plan

After that:
- the route scoring model should align its weighting inputs to the same priority vocabulary
