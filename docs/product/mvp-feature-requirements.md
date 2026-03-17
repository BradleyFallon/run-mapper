# RouteScout MVP Feature Requirements

## Purpose

This document defines the initial product requirements for the first meaningful RouteScout MVP.

The goal of the MVP is not to solve every route-planning problem. The goal is to deliver a useful,
trustworthy product experience that helps runners generate a route they feel good about before they
head out.

## Platform

Launch surfaces:
- web app for planning
- iOS app for full use, including navigation

Platform strategy:
- web is planning-first
- iOS is the primary full-featured product

Why this split:
- many users will want to plan ahead from a laptop
- larger screens are better for route comparison and deliberate editing
- iPhone remains the natural device for pre-run review and in-run use

The MVP should be designed as a coordinated multi-surface product, with iOS as the primary
execution surface.

## MVP Product Goal

A user should be able to:
1. open the web app or iPhone app
2. browse or filter plans
3. start from a plan
4. adjust a few key preferences
5. generate several route candidates
6. compare them quickly
7. choose one route they trust

## Core MVP Promise

RouteScout helps a runner find a route that fits the kind of run they want right now, without
forcing them to manually inspect maps or guess what the route will feel like.

## Primary Launch Personas

The MVP should primarily support:
- [Vee](./personas/vee.md)
- [Ace](./personas/ace.md)
- [Flo](./personas/flo.md)

The trail-running experience for [Sam](./personas/sam.md) is still important, but may need tighter
scoping depending on terrain-data quality.

## Plan Categories

The MVP should include these plan categories:
- `Confidence`
- `Explore`
- `Training`
- `Trail`

Each category should:
- communicate a clear intent
- organize starter plans coherently
- help users discover and filter plans quickly

## Launch Starter Plans

Recommended starter plans for MVP:
- `Safe Early Morning`
- `City Landmark Run`
- `Race Prep Hills`
- `Trail Confidence Loop`
- `Easy Nearby Loop`

The user should not start from a blank screen by default.

## Required User Flows

The MVP should support both:
- a planning flow on web
- a full planning and route-use flow on iOS

### 1. Start A Route Search

The app must allow the user to:
- open the route-planning flow
- browse or filter plans by category
- choose a starter plan
- optionally start from current location or a searched location

### 2. Edit A Plan

The app must allow lightweight editing of the selected plan before route generation.

Primary editable fields:
- target distance
- distance tolerance
- route shape, starting with loop
- start radius
- flatter vs hillier
- paved vs trail leaning
- confidence vs adventure leaning

Advanced editing may exist in the MVP, but the default experience should emphasize the primary
controls first.

### 3. Generate Candidate Routes

The app must:
- generate multiple route candidates from the selected plan
- evaluate them against the selected preferences
- return a short ranked list

The candidate list should be small enough to scan quickly.
Recommended MVP target:
- 2 to 4 candidate routes

### 4. Compare Candidate Routes

The app must present route candidates in a format that supports fast comparison.

Each candidate should show:
- total distance
- estimated duration
- elevation gain
- route shape summary
- surface or terrain summary
- a short explanation of why it matches the plan

The app should make one recommendation, while still allowing the user to inspect alternatives.

### 5. View A Route In Detail

The product must allow the user to open a selected route and see:
- map preview
- major route metrics
- route summary
- reasons the route was recommended

### 6. Save A Plan

The app must allow the user to:
- use a starter plan as-is
- modify a starter plan
- save a customized plan under a user-defined name
- reuse saved plans later

This is especially important for training-oriented users like Flo.

### 7. Open A Planned Route On iPhone

The MVP should allow a user who planned on web to access that route on iPhone later.

At minimum, the product should support:
- saved plan availability across surfaces
- selected route availability on iPhone

Full sync details can be specified in later docs, but cross-surface continuity is part of the
product direction.

## Functional Requirements

### Location Input

The MVP must support:
- current location
- place search
- manually selected area or place input

The user must be able to choose the general area where the route should begin.

### Route Shape

The MVP must support:
- loop routes

Optional but not required for MVP:
- out-and-back
- point-to-point

Loop routes should be the default and primary route shape at launch.

### Distance Control

The MVP must support:
- target distance input
- a tolerance or acceptable range around the target distance

This matters for all launch personas.

### Plan Controls

The MVP must support enough plan controls to meaningfully differentiate the starter plans.

Required plan control categories:
- distance and tolerance
- start radius
- terrain or hill preference
- surface preference
- environmental preference
- confidence or adventure preference

Training-oriented advanced controls should include:
- interruption avoidance
- stronger elevation intent
- stronger surface consistency preference

### Candidate Evaluation

The MVP must evaluate routes using a shared scoring model that can be weighted differently by plan
and plan category.

At minimum, route comparison should consider:
- distance fit
- elevation fit
- surface fit
- start convenience
- route simplicity
- environmental character
- training suitability

### Route Explanation

The MVP must provide human-readable explanations for why a route was recommended.

These explanations should help users answer:
- why this route fits my plan
- what tradeoffs were made
- why it is being shown ahead of the alternatives

### Plan Persistence

The MVP must support saved plans.

The user should be able to:
- save a plan
- rename a plan
- reuse a saved plan

Nice to have, but not required for MVP:
- duplicate a plan
- delete a plan
- edit an existing saved plan

## UX Requirements

### Web Planning Experience

The web app should feel designed for deliberate planning on a larger screen.

This means:
- strong map and panel layouts
- comfortable route comparison
- more space for advanced plan editing
- clear scanability for route metrics

### iPhone-First Route Use

The iOS app should feel designed for iPhone, not squeezed down from desktop.

This means:
- thumb-friendly controls
- clear one-handed interaction patterns
- short, scannable route cards
- map and cards working together cleanly
- minimal typing where possible

### Low-Friction Default Path

The app should support a fast path where a user like Vee can:
- choose a starter plan
- accept a recommended starter plan
- make one small edit
- generate a route quickly

### Advanced Tuning Path

The app should also support a deeper path where a user like Flo can:
- open advanced plan controls
- tune more detailed route parameters
- save multiple plan variants over time

### Recommendation Clarity

The app should not feel like an opaque black box.

It should clearly communicate:
- what plan is active
- why a route was recommended
- which tradeoffs are likely in each candidate

## Out Of Scope For MVP

These should not be treated as required for the initial launch:
- social sharing
- collaborative planning
- Android app
- Apple Watch app
- deep post-run analytics
- shareable plan libraries
- highly detailed safety claims without strong supporting data

Possible partial deferral depending on scope:
- fully mature turn-by-turn navigation polish

But iOS should still be navigation-oriented from the start.

## Technical Product Requirements

The MVP should be built around a route-candidate workflow:
1. collect plan, category, and location inputs
2. generate several route candidates
3. score them
4. explain them
5. present a recommended route and alternatives

The product should avoid a single-route black-box experience.

## Success Criteria

The MVP succeeds if:
- a new user can generate a route quickly without confusion
- the route options feel meaningfully different
- the recommended route feels defensible
- users can save and reuse plans
- the app feels native to iPhone usage patterns

## Suggested Next Docs

After this document, the next useful product docs are:
1. launch modes and starter plans
2. route scoring model
3. web information architecture and screen flow
4. iOS information architecture and screen flow
5. trust and safety signals
