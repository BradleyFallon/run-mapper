# RouteScout Product Docs

This directory contains the working product and design docs for RouteScout.

Use this file as the entry point.
The goal is to keep the work organized by question, not by chronology.

## Read First

Start here if you want the shortest path to the current product direction:

1. [route-scout-product-design.md](./route-scout-product-design.md)
2. [route-scout-terminology.md](./route-scout-terminology.md)
3. [mvp-feature-requirements.md](./mvp-feature-requirements.md)
4. [platform-strategy.md](./platform-strategy.md)

## Foundation

These docs define what the product is and how it is described.

- [route-scout-product-design.md](./route-scout-product-design.md)
  High-level product framing, value proposition, major use cases, and overall direction.
- [route-scout-terminology.md](./route-scout-terminology.md)
  Shared vocabulary for `category`, `plan`, and `route`.
- [platform-strategy.md](./platform-strategy.md)
  Platform split: web for planning, iOS for full use and navigation.
- [mvp-feature-requirements.md](./mvp-feature-requirements.md)
  What the MVP needs to do.

## Users

These docs define who the product is for and the situations it needs to support.

- [personas/README.md](./personas/README.md)
  Persona index.
- [user-stories/README.md](./user-stories/README.md)
  Scenario index.

## Product Decisions

These docs cover concrete product-model choices.

- [plan-system.md](./plan-system.md)
  Active plan model covering starter plans, saved plans, priority structure, parameter families,
  and tuning guardrails.

## Brand And Visuals

These docs define how the product should feel and look.

- [brand-positioning-and-identity.md](./brand-positioning-and-identity.md)
  Brand direction, market fit, premium positioning, and compatibility goals.
- [visual-design-system.md](./visual-design-system.md)
  Colors, typography, spacing, surfaces, and UI rules.
- [icon-vocabulary.md](./icon-vocabulary.md)
  Shared icon meanings, SF Symbols and Lucide counterparts, and RouteScout badge guidance.
- [route-card-system.md](./route-card-system.md)
  Active Route Card badge model covering badge meaning, trigger style, ordering, and MVP
  confidence levels.
- [style-guide/index.html](./style-guide/index.html)
  Browser-viewable HTML/CSS style guide for inspecting tokens, typography, components, and planner aesthetics.

## Current Product Model

Current core model:
- `category` organizes and filters plan templates
- `plan` is the reusable planning request the user selects or customizes
- `route` is the generated output

Current platform model:
- web app for planning
- iOS app for full use, including navigation

## What Is Already Decided

- planning should be centered on `plans`, not `modes`
- plan `category` is a property for browsing and filtering
- the web app is planning-first
- the iOS app is the full product surface
- the visual direction is dark, premium, high-contrast, and restrained

## What Is Not Yet Designed

These are the main open design areas:
- iOS information architecture
- iOS navigation experience
- sync and account model

## Recommended Working Order

If you are continuing product design work, use this order:

1. [next-design-tasks.md](./next-design-tasks.md)
2. [web-planner-information-architecture.md](./web-planner-information-architecture.md)
3. [web-planner-wireframe-spec.md](./web-planner-wireframe-spec.md)
4. [route-scoring-model.md](./route-scoring-model.md)
5. define `ios-information-architecture.md`
6. define `ios-navigation-experience.md`
7. define `sync-and-account-model.md`

## Surface Design

- [web-planner-information-architecture.md](./web-planner-information-architecture.md)
  Structure of the planning-first web app, including workspace layout and top-level sections.
- [web-planner-wireframe-spec.md](./web-planner-wireframe-spec.md)
  Low-fidelity wireframe spec for the web planner screens, panels, and key states.

## Plan Catalog

- [launch-plan-catalog.md](./launch-plan-catalog.md)
  Starter plans for MVP, including categories, defaults, and basic versus advanced controls.
- [plan-system.md](./plan-system.md)
  Shared plan structure, top-priority rules, parameter families, and plan card summary guidance.

## Scoring

- [route-scoring-model.md](./route-scoring-model.md)
  Shared scoring dimensions, category weighting, plan-level modifiers, and MVP recommendation logic.

## Archive And Implementation Notes

- [archive/README.md](./archive/README.md)
  Superseded product docs preserved for reference.
- [../implementation/README.md](../implementation/README.md)
  Implementation-facing notes that should not live in the product design set.

## Guidance

To avoid getting lost:
- keep each doc focused on one question
- prefer short linked docs over one giant document
- treat this README as the map of the product work
