# openrouteservice Endpoints for a Running Route Planner

This document explains the major openrouteservice endpoints and how each one could be used in a
route-planning app for running.

It is intentionally product-oriented rather than purely API-oriented. The goal is to answer:

- what does this endpoint do
- when would we use it
- how useful is it for a run planner
- what should we rely on it for versus handling ourselves in app logic

## Recommended Source Priority

When implementing against ORS, use these local references in order:

1. Current mirrored backend docs:
   [giscience.github.io/openrouteservice/api-reference/index.html](./giscience.github.io/openrouteservice/api-reference/index.html)
2. Current hosted API behavior observed in local testing
3. Archived official markdown source:
   [openrouteservice-docs-repo/README.md](./openrouteservice-docs-repo/README.md)
4. Archived swagger spec:
   [openrouteservice-docs-repo/API V2/swagger.json](./openrouteservice-docs-repo/API%20V2/swagger.json)

## High-Level View

The ORS ecosystem breaks down into three groups:

- core routing and network endpoints
- technical / self-hosting endpoints
- public convenience services like geocoding, POI, and optimization

For a running route planner, we care most about:
- `Directions`
- `Geocoder`
- `POI`
- `Elevation`
- `Isochrones`

We care much less about:
- `Export`
- `Optimization`
- `Health`
- `Status`

## 1. Directions

Docs:
- [Directions](./giscience.github.io/openrouteservice/api-reference/endpoints/directions/index.html)
- [Requests and Return Types](./giscience.github.io/openrouteservice/api-reference/endpoints/directions/requests-and-return-types.html)
- [Routing Options](./giscience.github.io/openrouteservice/api-reference/endpoints/directions/routing-options.html)
- [Extra Info](./giscience.github.io/openrouteservice/api-reference/endpoints/directions/extra-info/index.html)
- [Route Attributes](./giscience.github.io/openrouteservice/api-reference/endpoints/directions/route-attributes.html)

### What it does

`Directions` is the main routing endpoint. It calculates routes for a given profile and set of
coordinates and can return:
- route geometry
- turn instructions
- duration and distance
- ascent and descent
- profile-specific metadata
- route extra info like surface, steepness, noise, and greenery

### Why it matters for a running app

This is the core engine of the product.

We can use it to:
- generate routes between explicit waypoints
- generate loop routes / round trips
- render routes on a map
- compute distance and estimated duration
- score routes using metadata returned by `extra_info`

### Most important directions features for this app

#### Round trips / loops

ORS can generate loop routes automatically instead of requiring explicit waypoints.

That is the best built-in primitive for:
- “give me a 5-mile loop”
- “start near this location”
- “give me a few alternative loops”

#### `extra_info`

This is essential for route ranking.

Most useful extras for a run app:
- `surface`
- `waytype`
- `green`
- `noise`
- `steepness`
- `suitability`

We can use those to score:
- pavement preference
- trail vs road preference
- quietness
- greenery / park-likeness
- hilliness

#### `attributes`

Useful but secondary:
- `avgspeed`
- `detourfactor`
- `percentage`

These are more for analytics than for the main product behavior.

### What ORS can directly optimize here

For foot profiles, ORS can directly bias:
- `green`
- `quiet`

It can also:
- avoid ferries, fords, steps, and other avoidable features
- avoid polygons
- generate round trips

### What we still need to do ourselves

ORS does not fully solve product quality.

We still need app-side scoring for:
- how runnable a surface mix is
- how desirable a route feels
- exact climb profile preferences
- balancing many preferences at once

### Overall usefulness

Critical. This is the center of the app.

## 2. Geocoder

Docs:
- [Geocoder](./giscience.github.io/openrouteservice/api-reference/endpoints/geocoder/index.html)

### What it does

Geocoding converts text locations into coordinates and can also do reverse geocoding and
autocomplete.

### Why it matters for a running app

Users usually do not want to enter raw coordinates.

We can use it for:
- place-name search
- address lookup
- neighborhood or landmark search
- reverse geocoding start/end points for display

### Product use cases

- user types “Golden Gate Park” and we get a center point
- user types a home address and we route from nearby
- user clicks a map point and we show the nearest readable place label

### Overall usefulness

Very high. It is the natural front door to route generation.

## 3. POI

Docs:
- [POI](./giscience.github.io/openrouteservice/api-reference/endpoints/poi/index.html)

### What it does

Returns points of interest around a geometry or area.

### Why it matters for a running app

POIs are how the app can become more than “just distance plus roads.”

We can use POI data to:
- bias toward parks
- find drinking water
- find public toilets
- find transit access near route starts
- identify landmarks or amenities along a route

### Product use cases

- score routes higher if they pass parks
- annotate a route with water fountains or bathrooms
- suggest starts near parking or transit
- say “this route passes 2 parks and 1 restroom”

### Overall usefulness

High for route enrichment and better ranking. Not required for the first version, but very useful.

## 4. Elevation

Docs:
- [Elevation](./giscience.github.io/openrouteservice/api-reference/endpoints/elevation/index.html)

### What it does

Adds elevation to points or geometries.

### Why it matters for a running app

Running routes often depend heavily on climbing and descent.

We can use this endpoint to:
- build elevation profiles
- enrich custom lines or imported routes
- analyze hilliness independently from directions

### Product use cases

- show “flat”, “rolling”, or “hilly”
- graph elevation over distance
- compare routes by climb-per-mile

### Overall usefulness

Medium to high. Directions with `elevation` already gets us far, but this becomes more valuable for
analytics and imported routes.

## 5. Isochrones

Docs:
- [Isochrones](./giscience.github.io/openrouteservice/api-reference/endpoints/isochrones/index.html)

### What it does

Builds reachable polygons by time or distance from one or more starting points.

### Why it matters for a running app

Isochrones are useful for exploration and prefiltering.

They can answer:
- where can I get in 30 minutes
- what area is reachable in 5 miles
- what neighborhoods are inside a target run time

### Product use cases

- “show me a 20-minute running reach bubble”
- pre-select candidate start or route areas
- constrain route generation to reachable zones

### Overall usefulness

Medium. Useful for exploration and UX, not essential for the first route generator.

## 6. Matrix

Docs:
- [Matrix](./giscience.github.io/openrouteservice/api-reference/endpoints/matrix/index.html)

### What it does

Computes travel time and/or distance matrices between many sources and destinations.

### Why it matters for a running app

Matrix is more of an optimization support tool than a direct route generator.

We can use it to:
- compare many candidate start points
- evaluate logistics
- rank accessibility to route starts from parking or transit

### Product use cases

- evaluate the closest parking lot to each route start
- compare how far different candidate starts are from the user’s desired location
- pre-rank areas before requesting full route geometry

### Overall usefulness

Medium-low for initial product work. Useful later when ranking many candidates efficiently.

## 7. Snapping

Docs:
- [Snapping](./giscience.github.io/openrouteservice/api-reference/endpoints/snapping/index.html)

### What it does

Snaps raw coordinates to the nearest routable network edge.

### Why it matters for a running app

User clicks and imported points are often not exactly on the road/path network.

We can use snapping to:
- normalize clicked points
- ensure route starts are valid
- clean rough map inputs before routing

### Product use cases

- user taps map to start a run and we snap to a valid path
- imported favorite points are normalized before route generation

### Overall usefulness

Medium. Very helpful when map interaction becomes more important.

## 8. Matching

Docs:
- [Matching](./giscience.github.io/openrouteservice/api-reference/endpoints/matching/index.html)

### What it does

Matches track-like geometries or features to the routing network.

### Why it matters for a running app

This is mainly useful for post-run analysis, not initial route generation.

### Product use cases

- import a GPX run and clean it up
- reconstruct a runner’s route onto the network
- analyze recurring paths or route similarity

### Overall usefulness

Low for the first route planner. More useful later for import and analysis features.

## 9. Optimization

Docs:
- [Optimization](./giscience.github.io/openrouteservice/api-reference/endpoints/optimization/index.html)

### What it does

Vehicle routing optimization through VROOM.

### Why it matters for a running app

Usually it does not.

This endpoint is for multi-stop vehicle logistics, not human running loops.

### Product use cases

Probably none for the core app.

### Overall usefulness

Very low.

## 10. Export

Docs:
- [Export](./giscience.github.io/openrouteservice/api-reference/endpoints/export/index.html)

### What it does

Exports the routing graph for an area in JSON or TopoJSON.

### Why it matters for a running app

Mostly useful for self-hosting, offline analysis, or advanced debugging.

### Product use cases

- inspect the graph structure in a custom tool
- debug weird network behavior if self-hosting

### Overall usefulness

Very low for the hosted-app product path.

## 11. Health and Status

Docs:
- [Endpoints Overview](./giscience.github.io/openrouteservice/api-reference/endpoints/index.html)

### What they do

Operational service checks for health and status.

### Why they matter

Only if we self-host ORS or build monitoring around our own instance.

### Overall usefulness

Very low unless we self-host.

## Key Directions Subfeatures We Should Build Around

For this run planner, the most important ORS capabilities are:

1. `Directions` with round-trip generation
2. `extra_info` for route scoring
3. `Geocoder` for location input
4. `POI` for route enrichment
5. `Elevation` for hill analysis

## Product Architecture Recommendation

The cleanest route-planner architecture using ORS is:

1. User enters a place or address.
2. `Geocoder` turns that into a center coordinate.
3. `Directions` generates several round-trip candidates.
4. Request route metadata with `extra_info`.
5. Score routes in our own code for:
   - distance accuracy
   - pavement preference
   - trail vs road preference
   - quietness
   - greenery
   - hill profile
   - start distance from requested center
6. Optionally call `POI` to annotate or re-rank routes by amenities.
7. Optionally call `Elevation` for deeper route analysis or charts.

This keeps ORS focused on routing and network-derived metadata, while the app handles product-level
quality and ranking.

## What ORS Is Good At vs What We Must Handle Ourselves

ORS is good at:
- finding valid routes
- generating loops
- avoiding network features
- returning route metadata
- giving proxies for quietness and greenery

Our app must still handle:
- subjective route quality
- product-specific ranking
- balancing conflicting preferences
- runner-specific heuristics
- public API rate-limit handling

## Best Endpoints by Priority

For implementation order:

1. `Directions`
2. `Geocoder`
3. `POI`
4. `Elevation`
5. `Isochrones`
6. `Matrix`
7. `Snapping`
8. `Matching`
9. `Optimization`
10. `Export`
11. `Health` / `Status`

## Related Local Notes

- [notes/routing.md](./notes/routing.md)
- [notes/route-response.md](./notes/route-response.md)
- [notes/geocoding.md](./notes/geocoding.md)
- [notes/matrix.md](./notes/matrix.md)
- [agent-context.md](./agent-context.md)
