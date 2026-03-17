# Route Plans And Tuning

## Purpose

This document defines how RouteScout should serve both:
- users who want something fast and easy
- users who want detailed control over route generation

The product should not force every runner into the same level of complexity.

## Naming Decision

User-facing term:
- `plan`

Recommended usage:
- `starter plan` for a built-in default
- `saved plan` for a user-customized version

Why `plan`
- matches the idea of giving instructions to a virtual route planner
- feels intuitive to mainstream users
- works for both quick-start and advanced use
- naturally supports phrases like `choose a plan`, `edit plan`, and `save plan`
- fits the relationship between `category`, `plan`, and `route`

Terms to avoid for the main user-facing label:
- `profile`
  Too overloaded with account/profile meanings and training-profile meanings.
- `spec`
  Too technical for mainstream users.
- `configuration`
  Accurate, but too heavy and system-oriented.
- `setup`
  Understandable, but weaker than `plan` for something that acts like a planning brief.

## Product Principle

RouteScout should have two valid interaction styles:

1. fast path
   The user picks a starter plan, glances at the defaults, changes one or two things if needed,
   and generates a route.
2. tuning path
   The user opens advanced controls, adjusts many parameters deliberately, and saves a plan that
   reflects their exact preferences.

Both paths should feel first-class.

## User Types This Supports

### Low-friction user

This user wants help quickly. They do not want to think through every parameter.

Example:
- Vee, the business traveler

Her likely flow:
1. Open RouteScout.
2. Pick a starter plan like `Safe Early Morning`.
3. Review the defaults.
4. Change one thing if needed, such as distance or start radius.
5. Generate the route.

This path should feel calm, obvious, and reliable.

### Technical user

This user wants deep control because the route is serving a specific purpose.

Example:
- the serious race-training runner

Their likely flow:
1. Start from a training-oriented plan.
2. Open advanced controls.
3. Tune distance tolerance, elevation characteristics, pavement consistency, interruption
   avoidance, and other route-scoring inputs.
4. Save the result as a reusable plan.

This path should feel powerful without being messy.

## Core Product Model

The app should treat a plan as a reusable bundle of route-planning inputs and preferences.

A plan may include:
- route goal or intent
- route shape preference
- target distance
- distance tolerance
- start-radius preference
- elevation preference
- surface preference
- environmental preference
- confidence or safety preference
- discovery preference
- interruption avoidance preference
- trail tolerance

The plan is not the route itself.
It is the user's preferred planning recipe for generating routes.

## Starter Plans

Starter plans should give users good entry points without forcing them to start from a blank form.

Examples:
- `Safe Early Morning`
- `City Discovery Run`
- `Race Prep Hills`
- `Trail Adventure With Guardrails`
- `Easy Nearby Loop`

Each starter plan should:
- have a clear plain-language name
- have a category such as `Confidence`, `Explore`, `Training`, or `Trail`
- describe what kind of run it is good for
- expose a few key defaults upfront
- allow deeper editing if the user wants it

## Saved Plans

Users should be able to:
- duplicate a starter plan
- modify it
- save it under a custom name
- reuse it later

Examples:
- `Vee Hotel Morning`
- `Marathon Hill Session`
- `Vacation Landmark Loop`
- `Saturday Trail Confidence Run`

This gives the app memory and makes repeat use more valuable over time.

## Suggested UX Model

### Default experience

Lead with starter plans, not a blank advanced form.

The default route-creation screen should emphasize:
- a small set of starter plans
- the most important editable fields
- an `advanced` section for deeper tuning

### Editing model

Each plan should have:
- a compact summary
- a few primary controls
- an advanced panel

Primary controls are the most common adjustments:
- distance
- route shape
- start radius
- flat vs hilly
- paved vs trail
- confidence vs adventure

Advanced controls should hold the more technical tuning dimensions.

### Save behavior

If a user changes a starter plan, the app should treat it as:
- an unsaved customized plan until explicitly saved

Possible actions:
- `use once`
- `save as new plan`
- `update saved plan`

This keeps built-ins stable while still supporting customization.

## Vee Example

For the business-traveler story, Vee should not have to build a route plan from scratch.

Recommended flow:
1. She chooses `Safe Early Morning`.
2. The default plan already biases toward:
   - loops
   - close starts
   - flatter routes
   - paved surfaces
   - higher confidence and legibility
3. She changes only what matters today:
   - distance
   - maybe start radius
4. She generates a route.

That should be enough for her.

## Advanced Runner Example

For the serious training runner, the plan system should not feel simplistic.

Recommended flow:
1. They start from `Race Prep Hills`.
2. They expand advanced controls.
3. They tune the details.
4. They save a new plan with their own name.
5. They reuse it for future workouts.

The app should make this runner feel like RouteScout can be dialed in, not just sampled.

## Product Benefits

This model helps RouteScout in several ways:
- lowers the barrier to first use
- makes the app approachable for non-technical runners
- supports expert users without forcing complexity on everyone
- creates a reusable habit loop through saved plans
- gives the product a cleaner mental model than a long wall of settings

## Recommended Product Language

Good UI phrases:
- `Browse plans`
- `Filter by category`
- `Start with a plan`
- `Edit plan`
- `Advanced plan options`
- `Save plan`
- `Use this plan again`

Avoid:
- `profile`
- `configuration`
- `specification`
- `setup`

## Open Questions

These questions still need product decisions:

1. How many starter plans should exist at launch?
2. Should plan selection happen before location entry or after?
3. Should the app recommend a plan based on context, such as hotel area, trail area, or workout
   intent?
4. How many advanced parameters should be visible before the UI starts to feel crowded?
5. Should saved plans be shareable between users?
