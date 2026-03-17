#!/usr/bin/env python3
"""
Route a walking/running loop with elevation using openrouteservice.

What it does
------------
- Calls openrouteservice Directions API with profile=foot-walking
- Requests GeoJSON route geometry with elevation included
- Calculates:
  - exact routed distance (meters / km / miles)
  - ascent / descent (meters / feet)
  - min / max elevation
- Writes:
  - route.geojson
  - route_map.html

Setup
-----
pip install requests folium

Set your API key:
export ORS_API_KEY="your_key_here"

Example
-------
python ors_route_with_elevation.py \
  --coords -122.66595,45.50495 -122.67020,45.50495 -122.67170,45.49620 -122.66840,45.52770 \
           -122.66695,45.52765 -122.67020,45.50495 -122.67130,45.51328 -122.66695,45.51330 \
           -122.66595,45.50495 \
  --out route_output

Coordinate format is LON,LAT because that is what ORS expects.
You can pass as many waypoint coordinates as you want.
"""

import argparse
import os
from pathlib import Path

import folium

from run_router.env import load_env_file
from run_router.service import RouteError, fetch_route, meters_to_feet, write_geojson


load_env_file()


def parse_coord(text: str):
    from run_router.service import parse_coord as shared_parse_coord

    try:
        return shared_parse_coord(text)
    except RouteError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def centroid_lonlat(coords):
    lons = [c[0] for c in coords]
    lats = [c[1] for c in coords]
    return [sum(lats) / len(lats), sum(lons) / len(lons)]


def build_map(route_coords, waypoint_coords, output_html: Path, summary_html: str):
    center = centroid_lonlat(route_coords)
    m = folium.Map(location=center, zoom_start=14)

    latlon_route = [[c[1], c[0]] for c in route_coords]
    folium.PolyLine(latlon_route, weight=5, opacity=0.9).add_to(m)

    # Start marker
    start = waypoint_coords[0]
    finish = waypoint_coords[-1]
    folium.Marker(
        [start[1], start[0]],
        tooltip="Start",
        popup="Start",
    ).add_to(m)

    if finish != start:
        folium.Marker(
            [finish[1], finish[0]],
            tooltip="Finish",
            popup="Finish",
        ).add_to(m)

    # Intermediate waypoints
    for idx, coord in enumerate(waypoint_coords[1:-1], start=1):
        folium.CircleMarker(
            [coord[1], coord[0]],
            radius=5,
            tooltip=f"Waypoint {idx}",
        ).add_to(m)

    # Summary panel
    panel = folium.Element(f"""
    <div style="
        position: fixed;
        top: 12px;
        left: 12px;
        z-index: 9999;
        background: rgba(255,255,255,0.95);
        border-radius: 12px;
        padding: 12px 14px;
        box-shadow: 0 4px 18px rgba(0,0,0,0.18);
        max-width: 360px;
        font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
        font-size: 14px;
        line-height: 1.35;
    ">
        {summary_html}
    </div>
    """)
    m.get_root().html.add_child(panel)

    m.fit_bounds(latlon_route)
    m.save(str(output_html))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--profile",
        default="foot-walking",
        help="ORS routing profile. Default: foot-walking",
    )
    parser.add_argument(
        "--coords",
        nargs="+",
        required=True,
        type=parse_coord,
        help="Waypoint coordinates in LON,LAT format. Pass 2 or more.",
    )
    parser.add_argument(
        "--out",
        default="route_output",
        help="Output folder. Default: route_output",
    )
    parser.add_argument(
        "--noise-threshold-m",
        type=float,
        default=2.0,
        help="Ignore elevation wiggles smaller than this when summing ascent/descent.",
    )
    args = parser.parse_args()

    api_key = os.environ.get("ORS_API_KEY")
    if not api_key:
        raise SystemExit("Missing ORS_API_KEY environment variable.")

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    geojson_path = out_dir / "route.geojson"
    try:
        result = fetch_route(
            api_key=api_key,
            profile=args.profile,
            coords=args.coords,
            noise_threshold_m=args.noise_threshold_m,
        )
    except RouteError as exc:
        raise SystemExit(str(exc)) from exc

    write_geojson(result.raw_geojson, geojson_path)

    summary_text = [
        "<h3 style='margin:0 0 8px 0;'>Route summary</h3>",
        f"<div><strong>Distance:</strong> {result.distance_m:,.0f} m / {result.distance_km:.2f} km / {result.distance_mi:.2f} mi</div>",
        f"<div><strong>Duration:</strong> {result.duration_s/60.0:.1f} min (API estimate)</div>",
        f"<div><strong>Ascent:</strong> {result.ascent_m:.0f} m / {meters_to_feet(result.ascent_m):.0f} ft</div>",
        f"<div><strong>Descent:</strong> {result.descent_m:.0f} m / {meters_to_feet(result.descent_m):.0f} ft</div>",
    ]
    if result.min_ele_m is not None:
        summary_text.append(
            f"<div><strong>Elevation range:</strong> {result.min_ele_m:.0f}–{result.max_ele_m:.0f} m</div>"
        )
    summary_html = "\n".join(summary_text)

    html_map_path = out_dir / "route_map.html"
    build_map(
        result.route_feature["geometry"]["coordinates"],
        args.coords,
        html_map_path,
        summary_html,
    )

    print("Done.")
    print(f"GeoJSON: {geojson_path}")
    print(f"Map:     {html_map_path}")
    print()
    print(f"Distance: {result.distance_m:,.0f} m / {result.distance_km:.2f} km / {result.distance_mi:.2f} mi")
    print(f"Duration: {result.duration_s/60.0:.1f} min")
    print(f"Ascent:   {result.ascent_m:.0f} m / {meters_to_feet(result.ascent_m):.0f} ft")
    print(f"Descent:  {result.descent_m:.0f} m / {meters_to_feet(result.descent_m):.0f} ft")
    if result.min_ele_m is not None:
        print(f"Elevation range: {result.min_ele_m:.0f}–{result.max_ele_m:.0f} m")


if __name__ == "__main__":
    main()
