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
    RouteError,
    build_loop_candidates,
    parse_planning_request,
    first_value,
    maybe_apply_llm_preferences,
    meters_to_feet,
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

def format_candidate(index: int, candidate) -> str:
    route = candidate.route
    badges = ", ".join(badge.code for badge in (candidate.badges or [])) or "none"
    summary = candidate.summary
    summary_lines = []
    if summary:
        summary_lines.append(f"  Summary: {summary.headline}")
        if summary.top_reasons:
            summary_lines.append("  Why it won: " + ", ".join(summary.top_reasons))
        if summary.strengths:
            summary_lines.append("  Strengths: " + " | ".join(summary.strengths))
        if summary.tradeoffs:
            summary_lines.append("  Tradeoffs: " + " | ".join(summary.tradeoffs))
    return "\n".join(
        [
            f"Candidate {index + 1}",
            f"  Score: {candidate.score:.3f}",
            f"  Distance: {route.distance_mi:.2f} mi",
            f"  Duration: {route.duration_s / 60.0:.1f} min",
            f"  Climb: {meters_to_feet(route.ascent_m):.0f} ft",
            f"  Start offset: {candidate.start_offset_m / 1609.344:.2f} mi",
            f"  Badges: {badges}",
            *summary_lines,
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
    request = parse_planning_request(
        config,
        target_distance_default=6.0,
        start_radius_default=1.5,
        max_candidates_default=3,
        seed_count_default=1,
        start_limit_default=3,
    )

    try:
        llm_hint = maybe_apply_llm_preferences(
            design_brief=request.design_brief,
            base_preferences=request.preferences,
        )
        effective_preferences = llm_hint.preferences if llm_hint else request.preferences

        import os

        api_key = os.environ.get("ORS_API_KEY")
        if not api_key:
            raise RouteError("Missing ORS_API_KEY.")

        candidates = build_loop_candidates(
            api_key=api_key,
            center=request.center,
            start_radius_m=request.start_radius_m,
            target_distance_m=request.target_distance_m,
            profile=request.profile,
            preferences=effective_preferences,
            max_candidates=request.max_candidates,
            seed_count=request.seed_count,
            start_limit=request.start_limit,
        )
    except RouteError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.raw:
        payload = {
            "center": request.center,
            "profile": request.profile,
            "target_distance_miles": request.target_distance_miles,
            "effective_preferences": effective_preferences.__dict__,
            "llm_summary": llm_hint.summary if llm_hint else None,
            "candidates": [
                {
                    "score": candidate.score,
                    "score_breakdown": candidate.score_breakdown,
                    "badges": [
                        {"code": badge.code, "label": badge.label, "strength": badge.strength}
                        for badge in (candidate.badges or [])
                    ],
                    "summary_text": (
                        {
                            "headline": candidate.summary.headline,
                            "top_reasons": candidate.summary.top_reasons,
                            "strengths": candidate.summary.strengths,
                            "tradeoffs": candidate.summary.tradeoffs,
                        }
                        if candidate.summary
                        else None
                    ),
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
        print(f"Center: {request.center[0]:.5f},{request.center[1]:.5f}")
        print(f"Profile: {request.profile}")
        print(f"Target distance: {request.target_distance_miles:.2f} mi")
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
