# Route Response

This note collects the most implementation-relevant response encodings from the archived ORS
markdown plus pointers to the current backend reference.

Primary source:
- [../openrouteservice-docs-repo/README.md](../openrouteservice-docs-repo/README.md)

Current reference:
- [../giscience.github.io/openrouteservice/api-reference/endpoints/directions/extra-info/index.html](../giscience.github.io/openrouteservice/api-reference/endpoints/directions/extra-info/index.html)

## Steepness

Archived encoding:

| Value | Meaning |
| --- | --- |
| -5 | decline greater than 16% |
| -4 | decline 12-15% |
| -3 | decline 7-11% |
| -2 | decline 4-6% |
| -1 | decline 1-3% |
| 0 | flat |
| 1 | incline 1-3% |
| 2 | incline 4-6% |
| 3 | incline 7-11% |
| 4 | incline 12-15% |
| 5 | incline greater than 16% |

## Suitability

Archived interpretation:
- values range from `10` for best suitability to `1` for worst suitability

## Surface

Archived surface encodings:

| Value | Name |
| --- | --- |
| 0 | Unknown |
| 1 | Paved |
| 2 | Unpaved |
| 3 | Asphalt |
| 4 | Concrete |
| 5 | Cobblestone |
| 6 | Metal |
| 7 | Wood |
| 8 | Compacted Gravel |
| 9 | Fine Gravel |
| 10 | Gravel |
| 11 | Dirt |
| 12 | Ground |
| 13 | Ice |
| 14 | Paving Stones |
| 15 | Sand |
| 16 | Woodchips |
| 17 | Grass |
| 18 | Grass Paver |

Current local page:
- [../giscience.github.io/openrouteservice/api-reference/endpoints/directions/extra-info/surface.html](../giscience.github.io/openrouteservice/api-reference/endpoints/directions/extra-info/surface.html)

## WayCategory

Archived waycategory values are bit flags, so one segment can belong to multiple categories.

| Value | Meaning |
| --- | --- |
| 0 | No category |
| 1 | Highway |
| 2 | Steps |
| 4 | Unpaved road |
| 8 | Ferry |
| 16 | Track |
| 32 | Tunnel |
| 64 | Paved road |
| 128 | Ford |

## Waytype

Archived waytype encodings:

| Value | Name |
| --- | --- |
| 0 | Unknown |
| 1 | State Road |
| 2 | Road |
| 3 | Street |
| 4 | Path |
| 5 | Track |
| 6 | Cycleway |
| 7 | Footway |
| 8 | Steps |
| 9 | Ferry |
| 10 | Construction |

Current local page:
- [../giscience.github.io/openrouteservice/api-reference/endpoints/directions/extra-info/waytype.html](../giscience.github.io/openrouteservice/api-reference/endpoints/directions/extra-info/waytype.html)

## AvgSpeed

Archived interpretation:
- `AvgSpeed` is the average segment speed in km/h after grading and factor adjustments

## Instruction Types

Archived instruction encodings:

| Value | Meaning |
| --- | --- |
| 0 | Left |
| 1 | Right |
| 2 | Sharp left |
| 3 | Sharp right |
| 4 | Slight left |
| 5 | Slight right |
| 6 | Straight |
| 7 | Enter roundabout |
| 8 | Exit roundabout |
| 9 | U-turn |
| 10 | Goal |
| 11 | Depart |
| 12 | Keep left |
| 13 | Keep right |

## Tollways

Archived encoding:

| Value | Meaning |
| --- | --- |
| 0 | no tollway |
| 1 | is tollway |

## Trail Difficulty

Archived mapping:
- hiking uses `sac_scale`
- cycling uses `mtb:scale`

The archived table maps values `0-7` across those two schemes.

## Road Access Restrictions

Archived encodings:

| Value | Meaning |
| --- | --- |
| 0 | None |
| 1 | No |
| 2 | Customers |
| 4 | Destination |
| 8 | Delivery |
| 16 | Private |
| 32 | Permissive |

## Geometry Decoding

Archived note:
- ORS can return encoded polylines
- when elevation is included, standard 2D polyline decoders are not sufficient
- the decoder must know whether the geometry is `X,Y` or `X,Y,Z`

Current local page:
- [../giscience.github.io/openrouteservice/api-reference/endpoints/directions/geometry-decoding.html](../giscience.github.io/openrouteservice/api-reference/endpoints/directions/geometry-decoding.html)

## Most Useful Fields For Run Scoring

For run-route ranking, the most practically useful response data is:
- summary distance and duration
- ascent and descent
- geometry with elevation
- `surface`
- `waytype`
- `green`
- `noise`
- `steepness`
- `suitability`
