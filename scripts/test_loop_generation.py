#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import app
from run_router.env import load_env_file


load_env_file()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Test loop route suggestions through the Flask /api/loop endpoint."
    )
    parser.add_argument(
        "--config",
        help="Path to a JSON file with loop request parameters.",
    )
    parser.add_argument(
        "--center",
        help="Center coordinate in LON,LAT format.",
    )
    parser.add_argument(
        "--profile",
        choices=["foot-walking", "foot-hiking"],
        help="Routing profile.",
    )
    parser.add_argument(
        "--miles",
        type=float,
        help="Target route distance in miles.",
    )
    parser.add_argument(
        "--radius",
        type=float,
        help="Maximum start offset from center in miles.",
    )
    parser.add_argument(
        "--pavement",
        type=float,
        help="Pavement preference from 0 to 1.",
    )
    parser.add_argument(
        "--quiet",
        type=float,
        help="Quiet preference from 0 to 1.",
    )
    parser.add_argument(
        "--green",
        type=float,
        help="Green preference from 0 to 1.",
    )
    parser.add_argument(
        "--hills",
        type=float,
        help="Hill preference from -1 to 1.",
    )
    parser.add_argument(
        "--brief",
        help="Optional natural-language route brief. Requires OPENAI_API_KEY.",
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Print the raw JSON response.",
    )
    return parser


def load_config(path: str | None) -> dict:
    if not path:
        return {}

    config_path = Path(path)
    try:
        return json.loads(config_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"Config file not found: {config_path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in config file {config_path}: {exc}") from exc


def first_value(*values):
    for value in values:
        if value is not None:
            return value
    return None


def build_payload(args: argparse.Namespace, config: dict) -> dict:
    payload = {
        "center_coord": first_value(
            args.center,
            config.get("center_coord"),
            config.get("center"),
            "-122.6765,45.5236",
        ),
        "profile": first_value(
            args.profile,
            config.get("profile"),
            "foot-walking",
        ),
        "target_distance_miles": first_value(
            args.miles,
            config.get("target_distance_miles"),
            config.get("miles"),
            6.0,
        ),
        "start_radius_miles": first_value(
            args.radius,
            config.get("start_radius_miles"),
            config.get("radius"),
            1.5,
        ),
        "pavement_preference": first_value(
            args.pavement,
            config.get("pavement_preference"),
            config.get("pavement"),
            0.8,
        ),
        "quiet_preference": first_value(
            args.quiet,
            config.get("quiet_preference"),
            config.get("quiet"),
            0.8,
        ),
        "green_preference": first_value(
            args.green,
            config.get("green_preference"),
            config.get("green"),
            0.7,
        ),
        "hill_preference": first_value(
            args.hills,
            config.get("hill_preference"),
            config.get("hills"),
            0.0,
        ),
        "design_brief": first_value(
            args.brief,
            config.get("design_brief"),
            config.get("brief"),
            "",
        ),
    }
    return payload


def format_candidate(index: int, candidate: dict) -> str:
    summary = candidate["summary"]
    return "\n".join(
        [
            f"Candidate {index + 1}",
            f"  Score: {candidate['score']:.3f}",
            f"  Distance: {summary['distance_mi']:.2f} mi",
            f"  Duration: {summary['duration_min']:.1f} min",
            f"  Climb: {summary['ascent_ft']:.0f} ft",
            f"  Start offset: {candidate['start_offset_miles']:.2f} mi",
            (
                "  Breakdown: "
                + ", ".join(
                    f"{name}={value:.2f}"
                    for name, value in candidate["score_breakdown"].items()
                )
            ),
        ]
    )


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    config = load_config(args.config)

    if not os.environ.get("ORS_API_KEY"):
        print("Missing ORS_API_KEY.", file=sys.stderr)
        return 2

    payload = build_payload(args, config)

    with app.test_client() as client:
        response = client.post("/api/loop", json=payload)

    data = response.get_json()
    if response.status_code != 200:
        print(json.dumps(data, indent=2), file=sys.stderr)
        return 1

    if args.raw:
        print(json.dumps(data, indent=2))
        return 0

    if data.get("llm_hint"):
        print(f"LLM hint: {data['llm_hint']['summary']}")
        print()

    print(f"Center: {data['center'][0]:.5f},{data['center'][1]:.5f}")
    print(f"Target distance: {data['target_distance_miles']:.2f} mi")
    print()

    for index, candidate in enumerate(data.get("candidates", [])):
        print(format_candidate(index, candidate))
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
