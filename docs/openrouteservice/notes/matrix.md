# Matrix, Isochrones, and Nearby Services

This note is intentionally short. It points to the other ORS services that are most relevant when
the project grows beyond plain directions.

Primary local sources:
- [../openrouteservice-docs-repo/README.md](../openrouteservice-docs-repo/README.md)
- [../openrouteservice-docs-repo/API V2/swagger.json](../openrouteservice-docs-repo/API%20V2/swagger.json)

Current backend reference pages:
- [../giscience.github.io/openrouteservice/api-reference/endpoints/matrix/index.html](../giscience.github.io/openrouteservice/api-reference/endpoints/matrix/index.html)
- [../giscience.github.io/openrouteservice/api-reference/endpoints/isochrones/index.html](../giscience.github.io/openrouteservice/api-reference/endpoints/isochrones/index.html)
- [../giscience.github.io/openrouteservice/api-reference/endpoints/poi/index.html](../giscience.github.io/openrouteservice/api-reference/endpoints/poi/index.html)
- [../giscience.github.io/openrouteservice/api-reference/endpoints/elevation/index.html](../giscience.github.io/openrouteservice/api-reference/endpoints/elevation/index.html)

## Matrix

Archived markdown summary:
- the matrix response contains one matrix per requested metric
- rows correspond to `sources`
- columns correspond to `destinations`
- `null` is returned where a value cannot be determined

Why it matters:
- compare travel time from many candidate start points
- prefilter reachable candidate loops
- rank starts by access or logistics

## Isochrones

Why it matters:
- identify areas reachable within a target run time or distance
- seed candidate zones before requesting actual loops
- support “show me what 30 minutes from here looks like”

## POI

Why it matters:
- bias route scoring toward parks, water, bathrooms, transit, or landmarks
- enrich route suggestions with nearby amenities

## Elevation

Why it matters:
- sample or enrich elevation independently of the directions response
- support hill-focused route analysis outside the standard directions payload

## Practical Recommendation

For the current project, directions plus `extra_info` is enough for a first version.

The next most useful ORS service after directions is probably:
1. geocoding
2. POI
3. isochrones
4. matrix
