---
name: routescout-product-docs
description: Use when updating RouteScout product docs, user stories, personas, MVP scope, platform strategy, or planning workflows in this repo. Best for work under docs/product and for keeping product terminology and document structure consistent.
---

# RouteScout Product Docs

Use this skill for product-definition work in `/Users/fallbro/code/run-mapper`.

## Start Here

Read these first:
- `docs/product/README.md`
- `docs/product/route-scout-terminology.md`
- `docs/product/mvp-feature-requirements.md`

Then read only the specific product docs needed for the task.

## Current Product Model

Use this vocabulary consistently:
- `category` = grouping/filtering property for plan templates
- `plan` = the reusable planning request
- `route` = generated output

Do not reintroduce `mode` as a first-class product object unless the user explicitly wants that
model back.

## Platform Model

Current platform split:
- web app for planning
- iOS app for full use, including navigation

The web planner is the current design priority.

## How To Work

- Keep docs small and question-focused.
- Prefer adding a new focused doc over bloating an existing one.
- Update `docs/product/README.md` when adding a new major product doc.
- Update `docs/product/next-design-tasks.md` when a planned artifact becomes completed or the next
  sequencing changes.

## Relevant Product Docs

- Product framing: `docs/product/route-scout-product-design.md`
- Plan model: `docs/product/route-plans-and-tuning.md`
- Platform split: `docs/product/platform-strategy.md`
- Brand: `docs/product/brand-positioning-and-identity.md`
- Visual system: `docs/product/visual-design-system.md`
- Web planner IA: `docs/product/web-planner-information-architecture.md`
- Web wireframes: `docs/product/web-planner-wireframe-spec.md`
- Launch plans: `docs/product/launch-plan-catalog.md`

## Avoid

- Reintroducing deleted Flask-prototype assumptions into product docs
- Mixing runtime implementation detail into product-definition docs
- Creating giant catch-all design documents
