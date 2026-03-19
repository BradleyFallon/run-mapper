# RouteScout Plan System

## Purpose

This document defines the active product model for RouteScout plans.

It combines the earlier plan-structure and parameter-model docs into one reference covering:
- what a plan is
- how starter plans and saved plans work
- how much tuning RouteScout should support
- how priorities and parameters should be structured

## Core Model

RouteScout should center planning around:
- `category`
- `plan`
- `route`

In this model:
- `category` organizes and filters plan templates
- `plan` is the reusable planning request
- `route` is the generated output

The user-facing term should remain:
- `plan`

Recommended UI language:
- `starter plan`
- `saved plan`
- `edit plan`
- `save plan`

Avoid for the main user-facing noun:
- `profile`
- `configuration`
- `setup`
- `spec`

## Product Principle

RouteScout should support two equally valid interaction styles:

1. fast path
   The user chooses a starter plan, changes one or two things, and scouts a route.
2. tuning path
   The user opens advanced controls, adjusts parameters deliberately, and saves a reusable plan.

The product should not force casual users into a control panel, and it should not make technical
users feel boxed in.

## Plan Types

### Starter Plans

Starter plans are built-in defaults that give users a clear place to start.

Examples:
- `Safe Early Morning`
- `Easy Nearby Loop`
- `City Landmark Run`
- `Race Prep Hills`
- `Trail Confidence Loop`

Each starter plan should:
- have a plain-language name
- belong to a category such as `Confidence`, `Explore`, `Training`, or `Trail`
- expose a few key defaults up front
- support deeper editing when needed

### Saved Plans

Users should be able to:
- duplicate a starter plan
- modify it
- name it
- reuse it later

This gives RouteScout memory and makes repeat planning more valuable over time.

## Plan Structure

Each plan should have three layers.

### 1. Hard Requirements

These define the planning envelope.

MVP requirements:
- target distance
- distance tolerance
- start location
- start radius
- route shape

These should always be visible in the main plan editor.

### 2. Ranked Priorities

These tell the planner what matters most when tradeoffs appear.

Each plan should require:
- one `top priority`

Each plan should usually support:
- one `secondary priority`

Each plan may support:
- one `tertiary priority`

For MVP, stop there.
Do not let users rank six or eight different priorities.

### 3. Supporting Parameters

These refine behavior without becoming the main identity of the plan.

Examples:
- stronger paved preference
- stronger quiet bias
- tighter start-radius preference
- interruption avoidance
- trail difficulty ceiling

These belong primarily in advanced editing.

## Priority Vocabulary

Priorities should stay plain-language and product-facing.

Recommended MVP set:
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

Do not expose ORS implementation language directly in the product model.

## Parameter Families

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

## Basic Vs Advanced

### Basic View

Show:
- target distance
- distance tolerance
- start radius
- route shape
- top priority
- secondary priority
- surface preference
- hill preference

This is the right surface for most users.

### Advanced View

Hold:
- tertiary priority
- quiet preference
- greenery preference
- interruption avoidance
- surface consistency
- trail difficulty ceiling
- stronger confidence bias
- stronger landmark bias
- stronger elevation-pattern bias

The advanced list can vary slightly by plan category.

## Parameter Count Guardrails

The MVP should support about:
- `10` to `12` editable parameters per plan overall

Recommended visibility split:
- `5` core fields always visible
- `2` to `3` ranked priorities visible in the main summary
- `4` to `6` advanced fields available on demand

This is enough flexibility without turning the product into a settings wall.

## Plan Card Rules

Scout Spec cards should emphasize:
- category
- plan name
- top priority
- secondary priority
- one supporting characteristic

They should not try to show every parameter.

## UX Recommendation

Default plan flow:
1. browse starter plans
2. filter by category if needed
3. choose a starter plan
4. edit a few primary fields
5. optionally open advanced tuning
6. scout routes
7. save the customized plan if it is worth reusing

## Relationship To Other Docs

Use this doc with:
- [launch-plan-catalog.md](./launch-plan-catalog.md)
- [route-scoring-model.md](./route-scoring-model.md)

The plan catalog defines the specific starter plans.
The scoring model defines how those priorities and parameters affect route ranking.
