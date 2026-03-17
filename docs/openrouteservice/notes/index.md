# openrouteservice Notes

This directory is a markdown-first working set derived from the official ORS sources already
downloaded into this repo.

Primary local sources:
- [../openrouteservice-docs-repo/README.md](../openrouteservice-docs-repo/README.md)
- [../openrouteservice-docs-repo/API V2/swagger.json](../openrouteservice-docs-repo/API%20V2/swagger.json)
- [../giscience.github.io/openrouteservice/api-reference/index.html](../giscience.github.io/openrouteservice/api-reference/index.html)

Recommended reading order:
- [routing.md](./routing.md)
- [route-response.md](./route-response.md)
- [geocoding.md](./geocoding.md)
- [matrix.md](./matrix.md)

Notes:
- The archived `openrouteservice-docs-repo` source is easier to read, but it is deprecated.
- The mirrored backend reference is newer and should be treated as the source of truth when the two
  disagree.
- Practical local testing against the hosted API showed that some request shapes differ from the
  archived markdown examples. Treat the markdown notes here as a guide, then confirm against the
  current backend reference or live API behavior when implementing.
