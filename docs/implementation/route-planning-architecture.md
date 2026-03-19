# RouteScout Route Planning Architecture

## Purpose

This document defines the active implementation model for RouteScout route planning.

It answers:
- what route-planning features RouteScout should support
- which system is responsible for each part
- how ORS, heuristics, and LLMs should work together
- what should ship first versus later

This is the bridge between product design and runtime implementation.

## Core Principle

RouteScout should use a hybrid planning system:
- `OpenRouteService` generates plausible route candidates and route metadata
- `heuristics` apply RouteScout-specific judgment and ranking
- `LLM` helps interpret intent, personalize, and explain decisions

The LLM should not be the primary route generator.
The route engine should stay deterministic enough to debug, tune, and trust.

## What Route Planning Needs To Do

At a high level, RouteScout needs to:
- understand what kind of run the user wants
- generate a small set of plausible routes
- compare them against the user's priorities
- pick a recommendation
- explain why it is a good fit

That breaks into several concrete feature areas.

## Route Planning Feature Set

### 1. Plan-Driven Route Requests

The system should accept:
- start location
- start radius
- target distance or time
- route shape
- selected plan
- top / secondary / tertiary priorities
- supporting preferences

This should produce a normalized planning brief that runtime code can use directly.

### 2. Candidate Loop Generation

For MVP, the main route type should be:
- loop routes

The system should support:
- start within a radius instead of one exact coordinate
- multiple candidate starts
- multiple seeds
- candidate rerolls

This is the current strongest ORS-compatible path.

### 3. Route Metadata Extraction

For every candidate route, RouteScout should extract:
- distance
- duration
- ascent / descent
- elevation range
- surface mix
- waytype mix
- green score
- noise score
- start offset

These become RouteScout traits and score inputs.

### 4. Heuristic Scoring

RouteScout should score candidates on:
- distance fit
- start convenience
- surface fit
- hill fit
- environmental fit
- route simplicity
- discovery fit
- training fit
- trail suitability

The scoring model should stay deterministic and tunable.

### 5. Explanation Generation

The app should explain:
- why the recommended route won
- what tradeoffs it made
- how it matches the selected plan

This can be generated from structured score reasons and optionally polished by an LLM.

### 6. Route Identity

Every route should be turned into a more productized object with:
- route summary
- score breakdown
- badges
- short explanation
- route card presentation data

### 7. Saved Planning Memory

Over time, RouteScout should support:
- saved plans
- saved routes
- plan variants
- trip route packs
- reuse of historical preferences

### 8. Personalization Later

Later planning layers should support:
- learned preference baselines
- learned pace / distance habits
- adaptive suggestions from simple prompts
- lightweight coaching-style route recommendations

This belongs after the base planning engine is stable.

## System Responsibilities

## OpenRouteService

ORS should be responsible for:
- generating route geometry
- generating loop candidates from seeds / round trips
- returning route distance and duration
- returning elevation data when available
- returning `extra_info` such as `surface`, `waytype`, `green`, and `noise`
- honoring supported biasing inputs such as `quiet` and `green`

ORS should not be treated as:
- the final product-ranking engine
- the source of user-facing explanation language
- the only source of route quality judgment

## Heuristics

Heuristics should be responsible for:
- candidate start generation
- candidate-set shaping
- hard filters
- trait extraction
- route scoring
- badge derivation
- tie-breaking
- stable recommendation ordering

Heuristics should be the main place where RouteScout becomes a product instead of a thin API
wrapper.

## LLM

The LLM should be responsible for:
- interpreting natural-language design briefs
- helping map loose user intent into structured preferences
- later, personalizing route suggestions from sparse prompts
- generating polished explanations from structured route reasons
- possibly ranking landmarks or POIs once those are available

The LLM should not be responsible for:
- directly drawing route geometry
- replacing scoring with opaque judgment
- making safety claims from weak evidence

## Recommended Planning Pipeline

### Step 1. Normalize The Planning Request

Inputs:
- plan
- location
- distance or time
- route shape
- explicit sliders / fields
- optional natural-language brief

Output:
- `PlanningRequest`
- `EffectivePreferences`
- optional `LlmPreferenceHint`

LLM role here:
- translate natural-language intent into structured weights when useful

### Step 2. Generate Candidate Starts

Given:
- center point
- start radius

Generate:
- exact center start
- nearby distributed starts
- optionally prioritize more plausible starts later

Heuristic role:
- control exploration without exploding ORS costs

### Step 3. Generate ORS Candidate Routes

For each chosen start:
- request one or more round-trip routes
- vary seed
- request relevant `extra_info`

MVP focus:
- keep candidate count small and deliberate

### Step 4. Extract Route Traits

Convert ORS output into RouteScout traits like:
- paved ratio
- trail ratio
- average noise
- average green
- climb per mile
- distance fit
- start convenience
- route simplicity proxy
- discovery fit proxy
- training fit proxy

This trait layer is critical.
It prevents the scoring logic from becoming a pile of raw ORS conditionals.

### Step 5. Apply Hard Filters

Examples:
- distance too far outside tolerance
- start too far outside requested radius
- surface identity clearly violates the plan
- trail difficulty exceeds allowed ceiling

Hard filters should remove obviously wrong routes before ranking.

### Step 6. Score Candidates

Use:
- shared score components
- category baseline weights
- plan priority modifiers

This produces:
- total score
- structured score breakdown

### Step 7. Derive Route Badges And Route Summary

From traits and scores:
- derive badges
- derive route summary fields
- derive route card identity data

### Step 8. Recommend And Explain

Select:
- one recommended route
- a small number of alternates

Then explain:
- why the winner fits
- why alternates are different

LLM role here:
- optional language polish only

## Data Model Recommendation

The runtime should evolve toward these layers:

### Request Layer

- `PlanningRequest`
- `LoopPreferenceProfile`
- `LlmPreferenceHint`

### Route Layer

- `RouteResult`
- `RouteTraits`
- `RouteBadge`

### Candidate Layer

- `LoopCandidate`
- `score`
- `score_breakdown`
- `badges`
- `summary`

### Recommendation Layer

- `RecommendedRoute`
- `alternates`
- `explanation`

## LLM Use Cases By Priority

### High-Value Early Use Cases

1. natural-language brief parsing
2. explanation rewriting from structured reasons
3. later, preference-memory summarization

These are useful, bounded, and cheap enough to justify.

### Medium-Value Later Use Cases

1. POI / landmark prioritization
2. simple-prompt route planning like:
   - `easy 35-minute hotel run`
   - `tempo route from here`
3. route pack curation for a trip

### Low-Trust Use Cases To Avoid Early

1. letting the LLM decide the route winner without structured reasons
2. safety claims without supported data
3. hidden prompt-only behavior with no deterministic fallback

## Feature Phasing

### Phase 1: Strong MVP Planner

Implement:
- loop generation
- start radius support
- seeded candidate generation
- basic plan-driven scoring
- route badges
- structured explanation

### Phase 2: Better Candidate Quality

Add:
- route simplicity heuristics
- better trail suitability logic
- better training-fit logic
- better candidate pruning

### Phase 3: Landmark And Discovery Layer

Add:
- landmark support
- POI support
- stronger discovery fit
- better route card identity

### Phase 4: Personalization

Add:
- learned preferences
- learned pace and distance habits
- adaptive route suggestions
- coaching-style route planning

## Immediate Implementation Priorities

The next runtime priorities should be:

1. formalize a `PlanningRequest` layer instead of passing loosely related config values
2. deepen the trait layer in `run_router/service.py`
3. align scoring code more explicitly to plan priorities
4. add structured route summaries alongside badges
5. keep LLM use narrow and high-value

## Bottom Line

RouteScout should not be built as:
- ORS plus a prompt

It should be built as:
- a route-planning engine that uses ORS for geometry, heuristics for judgment, and LLMs for
  interpretation and explanation

That is what makes the product debuggable, differentiable, and ultimately trustworthy.
