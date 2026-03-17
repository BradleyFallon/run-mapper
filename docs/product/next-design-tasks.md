# RouteScout Next Design Tasks

## Purpose

This document defines the next design tasks in order.

The goal is to keep the process focused and prevent the product work from turning into an
unstructured pile of ideas.

## Current State

We already have:
- product framing
- terminology
- personas and user stories
- MVP requirements
- platform strategy
- brand direction
- visual design system

That is enough foundation to move from concept documents into surface-specific design.

## Priority Rule

Design the planner web app first.
After that, design the iOS app.

Reason:
- the web planner is the best place to define the planning workflow clearly
- the iOS app should inherit the planning model rather than inventing a second one
- iOS navigation design will be easier once the planning outputs are defined

## Next Tasks In Order

### 1. Web Planner Information Architecture

Goal:
- define the structure of the web planning experience

Questions to answer:
- what are the top-level web sections?
- what is the main planner workspace layout?
- what are the major planner states?
- how do saved plans and saved routes fit into navigation?

Output:
- `web-planner-information-architecture.md`

### 2. Web Planner Low-Fidelity Wireframes

Goal:
- sketch the planner experience without visual polish

Screens or states to wireframe:
- planner empty state
- starter-plan browsing state
- plan editing state
- generating state
- candidate results state
- selected route detail state
- saved plans view
- saved routes view

Output:
- low-fidelity planner wireframes

### 3. Launch Plan Catalog

Goal:
- define the starter plans that ship in the MVP

Questions to answer:
- which starter plans exist at launch?
- what category does each belong to?
- what are the default values for each?
- which inputs are editable in the basic view versus advanced view?

Output:
- `launch-plan-catalog.md`

### 4. Route Scoring Model

Goal:
- define how candidate routes are compared and ranked

Questions to answer:
- what metrics matter most?
- how do different plan categories weight those metrics?
- what is deterministic versus LLM-assisted?
- how is the recommended route explained?

Output:
- `route-scoring-model.md`

### 5. iOS Information Architecture

Goal:
- define how the iPhone app organizes planning, saved items, and route use

Questions to answer:
- what are the main tabs or sections?
- how does web-to-phone handoff work?
- how does a user open a planned route on iPhone?
- how should saved plans and saved routes appear on mobile?

Output:
- `ios-information-architecture.md`

### 6. iOS Navigation Experience

Goal:
- define the in-run route experience

Questions to answer:
- what is shown before starting the run?
- what is shown during the run?
- how much guidance is needed?
- what belongs in MVP versus later?

Output:
- `ios-navigation-experience.md`

### 7. Sync And Account Model

Goal:
- define cross-surface continuity

Questions to answer:
- what needs to sync between web and iPhone?
- what account model is required?
- how do saved plans and selected routes travel across devices?

Output:
- `sync-and-account-model.md`

## What Not To Do Yet

Avoid these for now:
- high-fidelity mockups of every screen
- deep visual polish for iOS before the web planner flow exists
- detailed navigation edge cases before route-planning IA is settled
- excessive branching into secondary features

## Immediate Next Move

The immediate next artifact should be:
- `web-planner-information-architecture.md`

That doc should turn the current product thinking into a concrete planning workspace structure.
