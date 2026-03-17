#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from run_router.env import load_env_file
from run_router.service import (
    LoopPreferenceProfile,
    RouteError,
    build_loop_candidates,
    maybe_apply_llm_preferences,
    meters_to_feet,
    miles_to_meters,
    parse_bias,
    parse_coord,
    parse_positive_float,
    write_geojson,
)


load_env_file()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate loop route suggestions directly from a JSON config."
    )
    parser.add_argument(
        "--config",
        default="examples/suggest_loop.example.json",
        help="Path to a JSON config file.",
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Print the raw candidate JSON instead of the formatted summary.",
    )
    return parser


def load_config(path: str) -> dict:
    config_path = Path(path)
    try:
        return json.loads(config_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"Config file not found: {config_path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in config file {config_path}: {exc}") from exc


def first_value(config: dict, *names: str, default=None):
    for name in names:
        if name in config:
            return config[name]
    return default


def build_preferences(config: dict) -> LoopPreferenceProfile:
    return LoopPreferenceProfile(
        pavement_preference=parse_bias(
            first_value(config, "pavement_preference", "pavement", default=0.8),
            name="Pavement preference",
        ),
        quiet_preference=parse_bias(
            first_value(config, "quiet_preference", "quiet", default=0.8),
            name="Quiet preference",
        ),
        green_preference=parse_bias(
            first_value(config, "green_preference", "green", default=0.7),
            name="Green preference",
        ),
        hill_preference=parse_bias(
            first_value(config, "hill_preference", "hills", default=0.0),
            name="Hill preference",
            minimum=-1.0,
            maximum=1.0,
        ),
    )


def format_candidate(index: int, candidate) -> str:
    route = candidate.route
    return "\n".join(
        [
            f"Candidate {index + 1}",
            f"  Score: {candidate.score:.3f}",
            f"  Distance: {route.distance_mi:.2f} mi",
            f"  Duration: {route.duration_s / 60.0:.1f} min",
            f"  Climb: {meters_to_feet(route.ascent_m):.0f} ft",
            f"  Start offset: {candidate.start_offset_m / 1609.344:.2f} mi",
            "  Breakdown: "
            + ", ".join(
                f"{name}={value:.2f}" for name, value in candidate.score_breakdown.items()
            ),
        ]
    )


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    config = load_config(args.config)

    center = parse_coord(first_value(config, "center_coord", "center", default=""))
    profile = first_value(config, "profile", default="foot-walking")
    target_distance_miles = parse_positive_float(
        first_value(config, "target_distance_miles", "miles", default=6.0),
        name="Target distance",
        minimum=0.1,
    )
    start_radius_miles = parse_positive_float(
        first_value(config, "start_radius_miles", "radius", default=1.5),
        name="Start radius",
        minimum=0.0,
    )
    max_candidates = int(
        parse_positive_float(
            first_value(config, "max_candidates", default=3),
            name="Max candidates",
            minimum=1.0,
        )
    )
    seed_count = int(
        parse_positive_float(
            first_value(config, "seed_count", default=1),
            name="Seed count",
            minimum=1.0,
        )
    )
    start_limit = int(
        parse_positive_float(
            first_value(config, "start_limit", default=3),
            name="Start limit",
            minimum=1.0,
        )
    )

    base_preferences = build_preferences(config)
    design_brief = first_value(config, "design_brief", "brief", default="")

    try:
        llm_hint = maybe_apply_llm_preferences(
            design_brief=design_brief,
            base_preferences=base_preferences,
        )
        effective_preferences = llm_hint.preferences if llm_hint else base_preferences

        import os

        api_key = os.environ.get("ORS_API_KEY")
        if not api_key:
            raise RouteError("Missing ORS_API_KEY.")

        candidates = build_loop_candidates(
            api_key=api_key,
            center=center,
            start_radius_m=miles_to_meters(start_radius_miles),
            target_distance_m=miles_to_meters(target_distance_miles),
            profile=profile,
            preferences=effective_preferences,
            max_candidates=max_candidates,
            seed_count=seed_count,
            start_limit=start_limit,
        )
    except RouteError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.raw:
        payload = {
            "center": center,
            "profile": profile,
            "target_distance_miles": target_distance_miles,
            "effective_preferences": effective_preferences.__dict__,
            "llm_summary": llm_hint.summary if llm_hint else None,
            "candidates": [
                {
                    "score": candidate.score,
                    "score_breakdown": candidate.score_breakdown,
                    "start_coord": candidate.start_coord,
                    "start_offset_miles": candidate.start_offset_m / 1609.344,
                    "summary": {
                        "distance_mi": candidate.route.distance_mi,
                        "duration_min": candidate.route.duration_s / 60.0,
                        "ascent_ft": meters_to_feet(candidate.route.ascent_m),
                        "descent_ft": meters_to_feet(candidate.route.descent_m),
                    },
                }
                for candidate in candidates
            ],
        }
        print(json.dumps(payload, indent=2))
    else:
        print(f"Center: {center[0]:.5f},{center[1]:.5f}")
        print(f"Profile: {profile}")
        print(f"Target distance: {target_distance_miles:.2f} mi")
        print(
            "Preferences: "
            f"pavement={effective_preferences.pavement_preference:.2f}, "
            f"quiet={effective_preferences.quiet_preference:.2f}, "
            f"green={effective_preferences.green_preference:.2f}, "
            f"hills={effective_preferences.hill_preference:.2f}"
        )
        if llm_hint:
            print(f"LLM brief: {llm_hint.summary}")
        print()

        for index, candidate in enumerate(candidates):
            print(format_candidate(index, candidate))
            print()

    output_geojson = first_value(config, "output_geojson")
    if output_geojson:
        output_path = Path(output_geojson)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        write_geojson(candidates[0].route.raw_geojson, output_path)
        print(f"Saved best route GeoJSON to {output_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
