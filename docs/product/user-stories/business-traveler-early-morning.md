# User Story: Business Traveler, Early Morning

Persona:
- [Vee](../personas/vee.md)

## Scenario

Vee is on a business trip and wants to go for a run in the morning before a conference.

She wants to get outside for some fresh air, but it is still somewhat dark out. She does not know
the city, does not know what areas are safe, and does not want to spend mental energy wandering or
recovering from wrong turns.

She has a hard time limit before she needs to get ready for the conference.

## User Goal

She wants a route she can trust immediately:
- safe enough to feel comfortable in an unfamiliar place
- easy to follow
- close to where she is staying
- relatively flat
- paved
- approximately 3 miles

Nature would be a bonus, but safety and lighting matter more.

## Constraints

- unfamiliar city
- early morning / partially dark conditions
- limited time
- low tolerance for getting lost
- wants a loop
- wants start proximity

## Category, Plan, And Route

- plan category: `Confidence`
- starter plan: `Safe Early Morning`
- route: a generated 3-mile paved loop near her hotel with strong legibility and higher-confidence
  environmental characteristics

## Route Preferences

- distance: 3 miles
- distance tolerance: plus or minus 0.5 miles
- route type: loop
- start radius: within 0.2 miles of current location
- elevation: prefer flat
- feature preference: lit paths
- surface preference: paved preferred
- traffic preference: no strong preference

## Ideal Product Flow

1. She opens RouteScout.
2. The app shows starter plans and lets her filter by the `Confidence` category.
3. The app recommends the `Safe Early Morning` starter plan.
4. She reviews the plan defaults and changes only what matters today, such as distance or start
   radius.
5. She keeps the route type as a loop.
6. She confirms flat terrain, lit paths, and paved surfaces.
7. The app shows some route highlights or landmark cards.
8. She ranks or selects what feels most appealing.
9. She taps `Generate route`.
10. The app generates multiple candidate routes from the selected plan.
11. The system compares them on safety, lighting, flatness, route clarity, and pavement quality.
12. The app proposes one recommended route plus supporting metrics.

## What Success Looks Like

She feels comfortable leaving her hotel and starting the run without worrying about:
- getting lost
- ending up in a poorly lit area
- finding herself on awkward terrain
- overrunning her schedule

The route feels practical, reliable, and easy to trust.

## What The App Must Get Right

- a good starter plan for this situation
- route clarity
- close start point
- strong confidence framing
- lighting / safety cues
- flatness
- paved paths
- time predictability

## Product Themes This Story Supports

- confidence
- safety
- practicality
- low-cognitive-load route planning
