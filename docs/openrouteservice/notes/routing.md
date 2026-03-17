# Routing

## Core Capabilities

ORS directions can:
- route between explicit coordinates
- generate round trips / loops
- avoid features, borders, countries, or polygons
- apply profile-specific restrictions and weightings
- return extra route metadata such as surface, way type, green score, noise score, and steepness

Primary local sources:
- [../openrouteservice-docs-repo/README.md](../openrouteservice-docs-repo/README.md)
- [../openrouteservice-docs-repo/API V2/swagger.json](../openrouteservice-docs-repo/API%20V2/swagger.json)
- [../giscience.github.io/openrouteservice/api-reference/index.html](../giscience.github.io/openrouteservice/api-reference/index.html)

## Main Inputs

Important directions request inputs:
- `profile`
- `coordinates`
- `preference`
- `options`
- `extra_info`
- `attributes`
- `geometry`, `instructions`, `elevation` and output format controls

The newer backend docs cover request and return formats in detail:
- [../giscience.github.io/openrouteservice/api-reference/endpoints/directions/index.html](../giscience.github.io/openrouteservice/api-reference/endpoints/directions/index.html)
- [../giscience.github.io/openrouteservice/assets/api-reference_endpoints_directions_requests-and-return-types.md.CQbqfDPd.lean.js](../giscience.github.io/openrouteservice/assets/api-reference_endpoints_directions_requests-and-return-types.md.CQbqfDPd.lean.js)

## Advanced `options`

The archived markdown source groups the most important advanced routing parameters under `options`:
- `maximum_speed`
- `avoid_features`
- `avoid_borders`
- `avoid_countries`
- `vehicle_type`
- `profile_params`
- `avoid_polygons`

Avoidable features from the archived markdown:
- `highways`
- `tollways`
- `ferries`
- `tunnels`
- `tracks`
- `fords`
- `steps`
- `hills`

Profile-specific parameters from the archived markdown:
- cycling: `steepness_difficulty`, `gradient`
- foot: `green`, `quiet`
- HGV: `length`, `width`, `height`, `axleload`, `weight`, `hazmat`
- wheelchair: `surface_type`, `track_type`, `smoothness_type`, `maximum_sloped_kerb`, `maximum_incline`

Archived markdown source section:
- [../openrouteservice-docs-repo/README.md](../openrouteservice-docs-repo/README.md)

Current backend reference pages:
- [../giscience.github.io/openrouteservice/api-reference/endpoints/directions/routing-options.html](../giscience.github.io/openrouteservice/api-reference/endpoints/directions/routing-options.html)

## Round Trips / Loop Generation

The current backend docs expose round-trip generation as an options object with:
- target `length`
- `points`
- optional `seed`

This is the built-in ORS primitive for loop generation.

Current backend reference:
- [../giscience.github.io/openrouteservice/api-reference/endpoints/directions/routing-options.html](../giscience.github.io/openrouteservice/api-reference/endpoints/directions/routing-options.html)

Practical local note:
- In live testing against the hosted API, `round_trip` with an underscore was accepted.
- The archived docs and newer docs do not always match the hosted request shape exactly.

This last point is a local implementation note rather than an official doc claim.

## `extra_info`

For route scoring and analysis, the most useful ORS `extra_info` values are:
- `steepness`
- `suitability`
- `surface`
- `waycategory`
- `waytype`
- `tollways`
- `traildifficulty`
- `roadaccessrestrictions`
- `countryinfo`
- `green`
- `noise`

Current backend reference:
- [../giscience.github.io/openrouteservice/api-reference/endpoints/directions/extra-info/index.html](../giscience.github.io/openrouteservice/api-reference/endpoints/directions/extra-info/index.html)

Specific local reference pages:
- [../giscience.github.io/openrouteservice/api-reference/endpoints/directions/extra-info/surface.html](../giscience.github.io/openrouteservice/api-reference/endpoints/directions/extra-info/surface.html)
- [../giscience.github.io/openrouteservice/api-reference/endpoints/directions/extra-info/waytype.html](../giscience.github.io/openrouteservice/api-reference/endpoints/directions/extra-info/waytype.html)
- [../giscience.github.io/openrouteservice/api-reference/endpoints/directions/extra-info/steepness.html](../giscience.github.io/openrouteservice/api-reference/endpoints/directions/extra-info/steepness.html)

## Route Attributes

The current docs list extra route-level attributes such as:
- `avgspeed`
- `detourfactor`
- `percentage`

Current backend reference:
- [../giscience.github.io/openrouteservice/api-reference/endpoints/directions/route-attributes.html](../giscience.github.io/openrouteservice/api-reference/endpoints/directions/route-attributes.html)

## Best Fit For The Run-Route Project

For a run route suggester, the most useful ORS features are:
- round trips / loop generation
- `green` and `quiet` foot-profile weighting
- `surface`, `waytype`, `noise`, `green`, and `steepness` extra info
- `avoid_polygons` if you need to hard-exclude areas
- geocoding for place-name entry

This is the minimum ORS feature set needed to generate and score suggested runs.
