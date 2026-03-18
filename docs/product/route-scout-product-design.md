# RouteScout Product Design

## Status

This document is an initial product design draft.

We have spent most of our time so far exploring what ORS and related services can do. We have not
yet committed to a final product scope or interaction model. The goal of this document is to move
from exploration into product planning.

## Product Framing

Primary launch surfaces:
- web app for planning
- iOS app for full product use

The product should support planning on web and full route use on iPhone. The iPhone remains the
primary execution and navigation device.

RouteScout helps runners discover a route they feel good about running before they head out.

The app is for runners who:
- are in an unfamiliar place
- want something new near home
- have a specific training objective
- want to explore without getting lost
- want a route that fits the moment, not just the mileage

At a high level, RouteScout is not only a route generator. It is a route scouting and route
selection tool that creates a custom route for the runner instead of mainly asking them to browse
what other people already uploaded.

## Core Value Proposition

RouteScout gives runners confidence before they run.

Its core product magic is:
- "I am here"
- "I have this much time"
- "I want this kind of run"
- "What should I do?"

RouteScout should answer that question as if an experienced runner had spent time studying the map,
weighing tradeoffs, and scouting the best option for that moment.

That confidence can come from:
- safety and predictability
- route quality
- route fit to training goals
- route fit to mood and environment
- confidence that the route will be worth the effort

## Product Promise

Before the user leaves the house or hotel, they should be able to answer:

- Is this route likely to feel safe enough?
- Will it match the kind of run I want to do today?
- Will it hit my distance and terrain targets?
- Will I enjoy what I see along the way?
- Can I trust it enough to just go run it?

Just as important, the user should feel:
- this route was made for me
- this is better than trying to figure it out myself on a map
- this is better than settling for a route somebody else happened to share

## What Makes RouteScout Different

RouteScout should be positioned as a custom running route planner, not primarily as a route
library.

That means:
- the main value is generating the right route for this runner, here, now
- shared routes can exist, but they are secondary
- the product should feel like it scouts the route for the user

The core contrast:
- generic maps help people get from A to B
- route-sharing products show what somebody else ran
- RouteScout decides what route this runner should do next

## Primary Use Cases

The product currently appears to have four strong use-case clusters:

1. unfamiliar-city confidence runs
2. exploration and sightseeing runs
3. training-target runs
4. guided trail discovery runs

These should shape both product design and technical design.

## User Story 1: Business Traveler, Early Morning, Safety First

A woman is on a business trip and wants to run in the morning before a conference.

Context:
- unfamiliar city
- still somewhat dark out
- limited time
- wants fresh air
- does not want to get lost
- wants a route she can trust without second-guessing

User intent:
- about a 3 mile loop
- tolerance around plus or minus 0.5 miles
- start within 0.2 miles of current location
- prefer flat
- prefer lit areas
- safety and reliability matter more than scenery
- nature is a bonus if it does not conflict with safety and lighting
- paved surfaces preferred
- traffic level does not matter much

Ideal product flow:
1. She opens RouteScout and sets her distance, start radius, and route type.
2. She selects flat terrain, lit paths, and paved preference.
3. The app shows notable landmarks or route highlights as cards.
4. She ranks or selects what she likes.
5. She taps “map my route.”
6. The system generates several candidate routes.
7. The app evaluates them against safety, lighting, flatness, and pavement.
8. It presents one recommended route with clear confidence metrics.

Key product need:
- remove uncertainty in an unfamiliar environment

## User Story 2: Vacation Runner, Exploration First

A man is on vacation and wants to explore the city through a run.

Context:
- unfamiliar city
- open to discovery
- route quality is partly about the places it passes
- landmarks and interesting areas matter more than technical training precision

User intent:
- use the app as a route discovery tool
- build a route around interesting landmarks
- prioritize memorable city exploration

Ideal product flow:
1. He opens a landmark explorer.
2. The app shows notable sights, neighborhoods, parks, riverfronts, plazas, and other highlights.
3. He picks or ranks the landmarks he wants to include.
4. The app proposes routes that connect those highlights cleanly.

Key product need:
- discovery should feel curated, not random

## User Story 3: Race Training, Technical Precision

A runner is training for a race and wants the route technicals to be right.

Context:
- training goal is primary
- wants consistent pavement
- wants a specific elevation pattern
- wants the right distance
- wants to minimize interruptions like crosswalk stops

User intent:
- use the app as a training route planner
- prioritize training fit over sightseeing or atmosphere

Ideal product flow:
1. He starts from a training-oriented plan.
2. He enters distance and desired hill profile.
3. He selects pavement consistency as important.
4. He indicates that minimizing stops matters.
5. The app proposes routes ranked for training quality.

Key product need:
- the route needs to be technically trustworthy

## User Story 4: Trail Discovery Without Chaos

A woman wants a new trail run, but does not want to get lost or end up on terrain that is too
muddy, steep, or hazardous.

Context:
- trail exploration
- wants adventure but not disorder
- needs confidence in navigation and terrain quality

User intent:
- find a route that feels wild enough to be interesting
- avoid overly steep, muddy, or hazardous segments
- avoid too many tripping hazards

Ideal product flow:
1. She selects trail-focused preferences.
2. She sets acceptable steepness and terrain quality.
3. The app proposes routes with enough trail character to feel adventurous.
4. The route still feels guided and legible.

Key product need:
- controlled adventure

## Product Pillars

Across all four stories, RouteScout seems to want four major pillars:

### 1. Confidence

The runner should feel they can trust the route before leaving.

Signals of confidence include:
- route clarity
- low chance of getting lost
- stable surfaces
- predictable distance and terrain
- clear route metrics

### 2. Fit

The route should match the kind of run the user wants right now.

Fit dimensions include:
- distance
- elevation profile
- pavement vs trail
- scenic vs efficient
- quiet vs energetic
- safe vs adventurous

### 3. Discovery

The app should help users find routes they would not have planned on their own.

Discovery dimensions include:
- landmarks
- parks
- courtyards
- waterfronts
- city character
- trail character

### 4. Practicality

The route has to work in the real world.

Practicality dimensions include:
- start proximity
- time available
- navigation simplicity
- likely interruptions
- route reliability

## Proposed Top-Level Product Areas

The app likely wants at least these major feature areas:

### Route Scout

The main route generation workflow.

Inputs:
- start location
- start radius
- target distance
- tolerance
- loop vs other route shapes
- terrain preference
- surface preference
- environmental preference
- safety / confidence preference
- training preference

Outputs:
- ranked route options
- route metrics
- route explanation
- route confidence summary

### Landmark Explorer

A discovery-first workflow.

Inputs:
- city / area
- themes or landmark categories
- user ranking of places to include

Outputs:
- route plans centered around places worth seeing

### Training Planner

A performance-first workflow.

Inputs:
- distance target
- hill target
- surface consistency
- interruption avoidance

Outputs:
- routes ranked for workout quality

### Trail Scout

A terrain-first workflow.

Inputs:
- trail preference
- steepness tolerance
- terrain condition tolerance
- confidence / navigation tolerance

Outputs:
- trail routes ranked for adventure with guardrails

## Route Evaluation Dimensions

Regardless of workflow, candidate routes probably need to be evaluated across a common set of
dimensions.

These dimensions appear most important:
- distance accuracy
- elevation profile
- surface mix
- route simplicity
- start convenience
- environmental character
- likely safety / comfort
- landmark value
- training suitability
- interruption risk

Not every user cares equally about every dimension, but the app likely needs a shared scoring model.

## Candidate Route Workflow

The current product concept seems to imply a route generation pipeline like this:

1. Gather user constraints and preferences.
2. Gather environmental context around the area.
3. Identify candidate highlights, route anchors, or waypoint ideas.
4. Generate several route candidates.
5. Evaluate them on route metrics and experience metrics.
6. Use an LLM to compare tradeoffs and select or explain the best route.
7. Present the final route with a clear rationale.

This is more powerful than a single-shot route request because:
- the app can compare alternatives
- the app can mix deterministic metrics with fuzzy user intent
- the app can explain why a route was chosen

## Product Requirements Emerging From The Stories

The product likely needs:

### Required

- start location selection
- target distance with tolerance
- route shape selection, starting with loops
- elevation preference
- surface preference
- candidate route generation
- candidate ranking
- route explanation

### Strongly Suggested

- landmark discovery
- route highlights as cards
- route comparison
- save or bookmark routes
- confidence / safety framing
- starter setups with lightweight editing

### Eventually Needed

- saved custom setups
- stronger training templates
- better trail-specific terrain quality
- richer environmental signals such as lighting and crosswalk burden

## Key Experience Questions

These are still open and should drive future design work:

1. What does “safe enough” mean in the product, and what data can represent it?
2. How do we represent lighting, especially pre-dawn or nighttime confidence?
3. How do we measure likely stop frequency or crosswalk burden?
4. How do we source landmark photos and area descriptions?
5. How much control should the user have versus how much should the app infer?
6. Should the product lead with route generation or with place discovery?
7. How many route candidates should we show before choice becomes overwhelming?
8. Should the final recommendation be one route, or a ranked short list?

## Product Risks

The main product risks at this stage appear to be:

### False confidence

If the app claims safety or reliability too strongly without strong data, trust will break.

### Too much complexity

If every user has to tune too many settings, the app becomes work instead of help.

This suggests the product should lead with starter setups and hide deeper tuning behind an advanced
layer.

### Weak route differentiation

If route candidates feel interchangeable, the scouting concept loses value.

### Thin discovery layer

If landmarks and highlights are weak, the exploration use case becomes generic.

## Initial MVP Recommendation

A first meaningful MVP could focus on one narrow but strong promise:

“Find me a route I can trust for the kind of run I want today.”

Recommended MVP scope:
- loop route generation
- start radius
- target distance plus tolerance
- surface preference
- elevation preference
- quiet / green preference
- starter setups for common scenarios
- landmark-aware route enrichment
- route cards with metrics and explanation

Recommended MVP scenarios:
- unfamiliar-city confidence run
- local new-route discovery
- training-focused route

Trail-specific scouting may be better as a second-phase specialization unless trail data quality is
strong enough early on.

## Suggested Next Design Docs

From here, the most useful follow-on docs would be:

1. feature requirements by workflow
2. route scoring model
3. landmark explorer design
4. trust and safety signals design
5. route generation system design

Related scenario docs:
- [user-stories/README.md](./user-stories/README.md)

Related planning docs:
- [route-scout-terminology.md](./route-scout-terminology.md)
- [route-plans-and-tuning.md](./route-plans-and-tuning.md)
- [mvp-feature-requirements.md](./mvp-feature-requirements.md)
- [platform-strategy.md](./platform-strategy.md)
- [brand-positioning-and-identity.md](./brand-positioning-and-identity.md)
- [visual-design-system.md](./visual-design-system.md)

Related persona docs:
- [personas/README.md](./personas/README.md)

## Summary

RouteScout is shaping up to be a route scouting product, not just a route calculator.

The strongest emerging product themes are:
- confidence
- fit
- discovery
- practicality

If the app succeeds, the user will not just get “a route.”
They will get a route they feel good about running before they step outside.
