# RouteScout Terminology

## Purpose

This document defines the core planning terms RouteScout should use consistently in product design,
UX copy, and technical discussions.

The goal is to avoid overloaded or ambiguous words and give the product a clean mental model.

## Core Terms

### Category

A `category` is a property of a plan used for browsing, filtering, and organizing plan templates.

Categories answer:
- what kind of run is this plan generally for?
- how should plans be grouped in the planner?

Examples:
- `Confidence`
- `Explore`
- `Training`
- `Trail`

A category is not a separate user workflow object.
It is metadata attached to a plan.

### Plan

A `plan` is the user's planning request or reusable planning specification.

Plans answer:
- how should the route be planned?
- what preferences and constraints should the planner follow?

A plan can include:
- target distance
- distance tolerance
- route shape
- start radius
- elevation preference
- surface preference
- confidence or adventure preference
- discovery preference
- interruption avoidance
- other route-scoring inputs

A plan is not the route itself.
It is the instruction set used to generate routes.

Examples:
- `Safe Early Morning`
- `City Landmark Run`
- `Race Prep Hills`
- `Trail Confidence Loop`

### Route

A `route` is the actual generated running route output.

Routes answer:
- what path should the runner actually follow?

A route includes things like:
- map geometry
- turn structure
- total distance
- elevation metrics
- surface mix
- route explanation
- confidence or suitability notes

The route is the result produced from a plan.

## Relationship Between The Terms

The model is:

1. `Category`
   A grouping and filtering property used for plan templates.
2. `Plan`
   The preferences and constraints given to the planner.
3. `Route`
   The generated result the runner can choose and follow.

Short version:
- category = grouping
- plan = request
- route = output

## Example

Business traveler example:
- Category: `Confidence`
- Plan: `Safe Early Morning`
- Route: a specific 3-mile paved loop near the hotel

Technical training example:
- Category: `Training`
- Plan: `Race Prep Hills`
- Route: a specific route matching the workout distance and elevation needs

## UI Guidance

These terms should be used consistently in product copy.

Good examples:
- `Browse plans`
- `Filter by category`
- `Start with a plan`
- `Edit plan`
- `Save plan`
- `Generate route`
- `Compare routes`

Avoid mixing these with less precise alternatives like:
- `profile`
- `configuration`
- `setup`
- `spec`

## Naming Guidance

Use `category` when referring to:
- plan-template groupings
- discovery and filtering labels

Use `plan` when referring to:
- reusable preference bundles
- built-in starter planning patterns
- user-saved custom planning instructions

Use `route` when referring to:
- generated candidate outputs
- recommended or selected paths on the map
