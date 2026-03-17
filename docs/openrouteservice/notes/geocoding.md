# Geocoding

Primary local source:
- [../openrouteservice-docs-repo/README.md](../openrouteservice-docs-repo/README.md)

Current backend reference:
- [../giscience.github.io/openrouteservice/api-reference/endpoints/geocoder/index.html](../giscience.github.io/openrouteservice/api-reference/endpoints/geocoder/index.html)

## Structured Query Fields

The archived markdown documents these structured geocoding inputs:
- `address`
- `neighbourhood`
- `borough`
- `locality`
- `county`
- `region`
- `postalcode`
- `country`

Archived example:

```json
{
  "address": "Berliner Straße 45",
  "locality": "Heidelberg",
  "country": "Germany",
  "postalcode": "69120"
}
```

The archived markdown also notes that this JSON may need URL encoding if supplied through a query
string.

## Place Types In Responses

Archived place-type meanings:

| Value | Meaning |
| --- | --- |
| `venue` | POI or business |
| `address` | place with street address |
| `street` | road or street |
| `neighbourhood` | neighborhood-scale place |
| `borough` | borough-level place |
| `localadmin` | local administrative boundary |
| `locality` | town, hamlet, or city |
| `county` | county-level administrative area |
| `macrocounty` | grouped counties |
| `region` | state or province |
| `macroregion` | grouped regions |
| `country` | nation-state |

## Why It Matters For This Project

For a run-route suggester, geocoding is the cleanest way to support:
- city or neighborhood input instead of raw coordinates
- address-to-start conversion
- place-name search before route generation

The simplest future upgrade path is:
1. geocode the user’s text input to a center coordinate
2. pass that coordinate into ORS directions with round-trip options
3. rank the returned loops with route metadata
