#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import webbrowser
from dataclasses import asdict
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from run_router.env import load_env_file
from run_router.service import (
    NON_NEGOTIABLE_OPTIONS,
    PlanningRequest,
    PRIORITY_OPTIONS,
    RouteFeasibilityError,
    RouteError,
    build_loop_candidates,
    first_value,
    maybe_apply_llm_preferences,
    meters_to_feet,
    parse_planning_request,
)


load_env_file()


HTML_PATH = PROJECT_ROOT / "scripts" / "route_map_lab.html"
LOGO_PATH = PROJECT_ROOT / "logo.png"

PLAN_PRESETS = {
    "safe-early-morning": {
        "label": "Safe Early Morning",
        "category": "Confidence",
        "target_distance_miles": 3.0,
        "distance_tolerance_miles": 0.5,
        "start_radius_miles": 0.2,
        "top_priority": "Lighting and confidence",
        "secondary_priority": "Simple navigation",
        "supporting_trait": "Paved surface",
        "pavement_preference": 0.9,
        "quiet_preference": 0.75,
        "green_preference": 0.45,
        "hill_preference": -0.5,
        "design_brief": "Close, paved, confidence-friendly morning loop that feels easy to follow.",
    },
    "easy-nearby-loop": {
        "label": "Easy Nearby Loop",
        "category": "Confidence",
        "target_distance_miles": 4.0,
        "distance_tolerance_miles": 0.5,
        "start_radius_miles": 0.35,
        "top_priority": "Closer start",
        "secondary_priority": "Distance accuracy",
        "supporting_trait": "Low friction",
        "pavement_preference": 0.75,
        "quiet_preference": 0.55,
        "green_preference": 0.4,
        "hill_preference": -0.25,
        "design_brief": "Simple nearby loop with low friction and solid footing.",
    },
    "city-landmark-run": {
        "label": "City Landmark Run",
        "category": "Explore",
        "target_distance_miles": 5.0,
        "distance_tolerance_miles": 0.6,
        "start_radius_miles": 0.5,
        "top_priority": "Landmarks",
        "secondary_priority": "Nature access",
        "supporting_trait": "Memorable city loop",
        "pavement_preference": 0.65,
        "quiet_preference": 0.4,
        "green_preference": 0.75,
        "hill_preference": 0.0,
        "design_brief": "Memorable urban run with some green space and places worth seeing.",
    },
    "race-prep-hills": {
        "label": "Race Prep Hills",
        "category": "Training",
        "target_distance_miles": 6.0,
        "distance_tolerance_miles": 0.5,
        "start_radius_miles": 0.4,
        "top_priority": "Elevation profile",
        "secondary_priority": "Distance accuracy",
        "supporting_trait": "Paved surface",
        "pavement_preference": 0.9,
        "quiet_preference": 0.35,
        "green_preference": 0.35,
        "hill_preference": 0.8,
        "design_brief": "Training route with stronger climbing and consistent paved footing.",
    },
    "trail-confidence-loop": {
        "label": "Trail Confidence Loop",
        "category": "Trail",
        "target_distance_miles": 4.5,
        "distance_tolerance_miles": 0.6,
        "start_radius_miles": 0.5,
        "top_priority": "Trail quality",
        "secondary_priority": "Simple navigation",
        "supporting_trait": "Manageable terrain",
        "pavement_preference": 0.25,
        "quiet_preference": 0.7,
        "green_preference": 0.85,
        "hill_preference": 0.35,
        "design_brief": "Trail-forward loop with manageable terrain and good navigational confidence.",
    },
}


def compact_extra_summary(extras: dict) -> dict:
    summary: dict[str, list[dict[str, float | int]]] = {}
    for key, node in extras.items():
        items = (node or {}).get("summary") or []
        if not items:
            continue
        summary[key] = [
            {
                "value": int(item.get("value", 0)),
                "distance_miles": round(float(item.get("distance", 0.0)) / 1609.344, 2),
            }
            for item in items[:4]
        ]
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a local RouteScout map lab for loop generation testing."
    )
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind.")
    parser.add_argument("--port", type=int, default=8123, help="Port to bind.")
    parser.add_argument(
        "--open-browser",
        action="store_true",
        help="Open the map lab in the default browser after startup.",
    )
    return parser

def build_request(payload: dict) -> PlanningRequest:
    return parse_planning_request(
        payload,
        target_distance_default=3.0,
        start_radius_default=0.2,
        max_candidates_default=3,
        seed_count_default=3,
        start_limit_default=4,
        seed_offset_default=0,
    )


def build_loop_response(payload: dict) -> dict:
    request = build_request(payload)

    import os

    api_key = os.environ.get("ORS_API_KEY")
    if not api_key:
        raise RouteError("Missing ORS_API_KEY.")

    llm_hint = maybe_apply_llm_preferences(
        design_brief=request.design_brief,
        base_preferences=request.preferences,
    )
    effective_preferences = llm_hint.preferences if llm_hint else request.preferences

    candidates = build_loop_candidates(
        api_key=api_key,
        center=request.center,
        start_radius_m=request.start_radius_m,
        target_distance_m=request.target_distance_m,
        profile=request.profile,
        preferences=effective_preferences,
        top_priority=request.top_priority,
        secondary_priority=request.secondary_priority,
        distance_tolerance_miles=request.distance_tolerance_miles,
        non_negotiables=request.non_negotiables,
        max_candidates=request.max_candidates,
        seed_count=request.seed_count,
        start_limit=request.start_limit,
        seed_offset=request.seed_offset,
    )

    return {
        "request_debug": {
            "center_coord": f"{request.center[0]},{request.center[1]}",
            "profile": request.profile,
            "target_distance_miles": request.target_distance_miles,
            "distance_tolerance_miles": request.distance_tolerance_miles,
            "start_radius_miles": request.start_radius_miles,
            "max_candidates": request.max_candidates,
            "seed_count": request.seed_count,
            "start_limit": request.start_limit,
            "seed_offset": request.seed_offset,
            "top_priority": request.top_priority,
            "secondary_priority": request.secondary_priority,
            "non_negotiables": request.non_negotiables,
            "base_preferences": request.preferences.__dict__,
            "effective_preferences": effective_preferences.__dict__,
            "design_brief": request.design_brief,
        },
        "center": request.center,
        "profile": request.profile,
        "target_distance_miles": request.target_distance_miles,
        "distance_tolerance_miles": request.distance_tolerance_miles,
        "start_radius_miles": request.start_radius_miles,
        "top_priority": request.top_priority,
        "secondary_priority": request.secondary_priority,
        "non_negotiables": request.non_negotiables,
        "effective_preferences": effective_preferences.__dict__,
        "llm_summary": llm_hint.summary if llm_hint else None,
        "candidates": [
            {
                "score": candidate.score,
                "score_breakdown": candidate.score_breakdown,
                "ranking_breakdown": candidate.ranking_breakdown,
                "start_coord": candidate.start_coord,
                "start_offset_miles": candidate.start_offset_m / 1609.344,
                "seed": candidate.seed,
                "constraint_results": candidate.constraint_results,
                "badges": [
                    {"code": badge.code, "label": badge.label, "strength": badge.strength}
                    for badge in (candidate.badges or [])
                ],
                "traits": asdict(candidate.traits) if candidate.traits else None,
                "extra_summary": compact_extra_summary(candidate.route.extras),
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
                "summary": {
                    "distance_miles": candidate.route.distance_mi,
                    "duration_minutes": candidate.route.duration_s / 60.0,
                    "ascent_feet": meters_to_feet(candidate.route.ascent_m),
                    "descent_feet": meters_to_feet(candidate.route.descent_m),
                    "min_elevation_m": candidate.route.min_ele_m,
                    "max_elevation_m": candidate.route.max_ele_m,
                },
                "geojson": candidate.route.raw_geojson,
            }
            for candidate in candidates
        ],
    }


def build_request_debug_payload(payload: dict) -> dict:
    request = build_request(payload)
    return {
        "center_coord": f"{request.center[0]},{request.center[1]}",
        "profile": request.profile,
        "target_distance_miles": request.target_distance_miles,
        "distance_tolerance_miles": request.distance_tolerance_miles,
        "start_radius_miles": request.start_radius_miles,
        "max_candidates": request.max_candidates,
        "seed_count": request.seed_count,
        "start_limit": request.start_limit,
        "seed_offset": request.seed_offset,
        "top_priority": request.top_priority,
        "secondary_priority": request.secondary_priority,
        "non_negotiables": request.non_negotiables,
        "base_preferences": request.preferences.__dict__,
        "effective_preferences": request.preferences.__dict__,
        "design_brief": request.design_brief,
    }


class RouteMapLabHandler(BaseHTTPRequestHandler):
    server_version = "RouteScoutMapLab/0.1"

    def _send_bytes(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, status: int, payload: dict) -> None:
        self._send_bytes(status, json.dumps(payload, indent=2).encode("utf-8"), "application/json")

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        if self.path in {"/", "/index.html"}:
            self._send_bytes(200, HTML_PATH.read_bytes(), "text/html; charset=utf-8")
            return

        if self.path == "/logo.png" and LOGO_PATH.exists():
            self._send_bytes(200, LOGO_PATH.read_bytes(), "image/png")
            return

        if self.path == "/api/plans":
            self._send_json(
                200,
                {
                    "plans": PLAN_PRESETS,
                    "priorities": PRIORITY_OPTIONS,
                    "non_negotiables": NON_NEGOTIABLE_OPTIONS,
                },
            )
            return

        if self.path == "/health":
            self._send_json(200, {"ok": True})
            return

        self._send_json(404, {"error": "Not found"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/api/loop":
            self._send_json(404, {"error": "Not found"})
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        try:
            payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
        except json.JSONDecodeError:
            self._send_json(400, {"error": "Invalid JSON body."})
            return

        try:
            response = build_loop_response(payload)
        except RouteFeasibilityError as exc:
            self._send_json(
                422,
                {
                    "error": str(exc),
                    "failure_analysis": exc.failure_analysis,
                    "request_debug": build_request_debug_payload(payload),
                },
            )
            return
        except RouteError as exc:
            self._send_json(400, {"error": str(exc)})
            return
        except Exception as exc:  # pragma: no cover - defensive server path
            self._send_json(500, {"error": f"Unexpected server error: {exc}"})
            return

        self._send_json(200, response)

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return


def main() -> int:
    args = build_parser().parse_args()
    httpd = ThreadingHTTPServer((args.host, args.port), RouteMapLabHandler)
    url = f"http://{args.host}:{args.port}/"
    print(f"RouteScout map lab running at {url}")
    print("Use browser geolocation or click the map to set a start point.")

    if args.open_browser:
        webbrowser.open(url)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping map lab.")
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
