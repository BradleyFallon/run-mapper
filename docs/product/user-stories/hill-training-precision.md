# User Story: Hill Training Precision

Persona:
- [Flo](../personas/flo.md)

## Scenario

Flo is training for a race and wants a route that matches the technical needs of the workout.

This runner is less interested in scenery or novelty. The route needs to be the right training
tool.

## User Goal

They want a route with:
- the right distance
- the right elevation pattern
- consistent pavement
- minimal interruption

They want to avoid routes that look nice on paper but fail as workouts because of stops, uneven
surface changes, or the wrong climb profile.

## Constraints

- race-specific training intent
- high precision needed
- low tolerance for route mismatch
- wants to avoid crosswalk stops and interruptions

## Category, Plan, And Route

- plan category: `Training`
- starter plan: `Race Prep Hills`
- saved plan variants: user-created versions with different target distances, elevation profiles, or
  interruption tolerance
- route: a generated workout route chosen for technical fit rather than novelty

## Route Preferences

- exact or near-exact target distance
- specific hill profile
- strong pavement consistency
- low interruption / low stopping burden

## Experience 1: Initial Plan Creation

1. The runner opens RouteScout and filters plans by the `Training` category.
2. The app recommends the `Race Prep Hills` starter plan.
3. They open advanced plan options because they care about the technical details.
4. They set target distance and desired elevation profile.
5. They mark pavement consistency as important.
6. They indicate that avoiding stops matters.
7. The app generates several candidate routes from that plan.
8. The system ranks them by training suitability.
9. The app shows route metrics clearly enough that the runner trusts the result.
10. They save the tuned plan for later use.

## Experience 2: Saved Plan Variants

After the initial setup, the runner wants several related versions of the same training idea.

Examples:
- `Race Prep Hills 5 Mile`
- `Race Prep Hills 8 Mile`
- `Race Prep Hills Moderate Climb`
- `Race Prep Hills Long Climb`

Ideal follow-up flow:
1. They reopen the saved `Race Prep Hills` plan.
2. They duplicate it into a new variant.
3. They change only the variables that matter for that workout, such as distance or elevation
   profile.
4. They save the variant under a clear name.
5. They generate a route from that saved variant instead of starting from scratch.

This turns RouteScout into a repeat training tool rather than a one-off route finder.

## What Success Looks Like

The final route behaves like a training asset:
- right distance
- useful hills
- stable footing
- minimal interruptions

The runner feels that the route supports race preparation rather than getting in the way.

Over time, they build a small library of training plans that match different workouts.

## What The App Must Get Right

- strong training-oriented plans
- deep plan editing
- saved plan variants
- distance precision
- elevation profile quality
- pavement consistency
- interruption minimization
- clear route metrics

## Product Themes This Story Supports

- fit
- technical accuracy
- training trust
- performance-oriented planning
