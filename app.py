from __future__ import annotations

import os

from flask import Flask, jsonify, render_template, request

from run_router.env import load_env_file
from run_router.service import (
    LoopPreferenceProfile,
    RouteError,
    build_loop_candidates,
    fetch_route,
    maybe_apply_llm_preferences,
    meters_to_feet,
    miles_to_meters,
    parse_bias,
    parse_coord,
    parse_coord_lines,
    parse_positive_float,
)


load_env_file()


DEFAULT_CENTER = "-122.6765,45.5236"
DEFAULT_COORDS = """-122.66595,45.50495
-122.67020,45.50495
-122.67170,45.49620
-122.66840,45.52770
-122.66695,45.52765
-122.67020,45.50495
-122.67130,45.51328
-122.66695,45.51330
-122.66595,45.50495"""


app = Flask(__name__)


@app.get("/")
def index():
    return render_template(
        "index.html",
        default_center=DEFAULT_CENTER,
        default_coords=DEFAULT_COORDS,
        has_openai_key=bool(os.environ.get("OPENAI_API_KEY")),
    )


@app.post("/api/route")
def route():
    payload = request.get_json(silent=True) or {}
    profile = payload.get("profile", "foot-walking")
    coords_text = (payload.get("coords_text") or "").strip()
    noise_threshold_m = parse_positive_float(
        payload.get("noise_threshold_m", 2.0),
        name="Noise threshold",
        minimum=0.0,
    )

    api_key = os.environ.get("ORS_API_KEY")
    if not api_key:
        raise RouteError("Set ORS_API_KEY in your environment before requesting routes.")

    coords = parse_coord_lines(coords_text)
    result = fetch_route(
        api_key=api_key,
        profile=profile,
        coords=coords,
        noise_threshold_m=noise_threshold_m,
    )

    return jsonify(
        {
            "route": result.route_feature,
            "waypoints": coords,
            "summary": serialize_route_summary(result),
        }
    )


@app.post("/api/loop")
def loop():
    payload = request.get_json(silent=True) or {}
    profile = payload.get("profile", "foot-walking")
    center = parse_coord((payload.get("center_coord") or "").strip())
    target_distance_miles = parse_positive_float(
        payload.get("target_distance_miles"),
        name="Target distance",
        minimum=0.1,
    )
    start_radius_miles = parse_positive_float(
        payload.get("start_radius_miles"),
        name="Start radius",
        minimum=0.0,
    )

    base_preferences = LoopPreferenceProfile(
        pavement_preference=parse_bias(
            payload.get("pavement_preference", 0.75),
            name="Pavement preference",
        ),
        quiet_preference=parse_bias(
            payload.get("quiet_preference", 0.7),
            name="Quiet preference",
        ),
        green_preference=parse_bias(
            payload.get("green_preference", 0.65),
            name="Green preference",
        ),
        hill_preference=parse_bias(
            payload.get("hill_preference", 0.0),
            name="Hill preference",
            minimum=-1.0,
            maximum=1.0,
        ),
    )

    design_brief = (payload.get("design_brief") or "").strip()
    llm_hint = maybe_apply_llm_preferences(
        design_brief=design_brief,
        base_preferences=base_preferences,
    )
    effective_preferences = llm_hint.preferences if llm_hint else base_preferences

    api_key = os.environ.get("ORS_API_KEY")
    if not api_key:
        raise RouteError("Set ORS_API_KEY in your environment before generating loops.")

    candidates = build_loop_candidates(
        api_key=api_key,
        center=center,
        start_radius_m=miles_to_meters(start_radius_miles),
        target_distance_m=miles_to_meters(target_distance_miles),
        profile=profile,
        preferences=effective_preferences,
    )

    top_candidates = candidates[:3]
    return jsonify(
        {
            "center": center,
            "target_distance_miles": target_distance_miles,
            "llm_hint": (
                {
                    "summary": llm_hint.summary,
                    "preferences": serialize_preferences(llm_hint.preferences),
                }
                if llm_hint
                else None
            ),
            "effective_preferences": serialize_preferences(effective_preferences),
            "best_candidate_index": 0,
            "candidates": [serialize_candidate(candidate) for candidate in top_candidates],
        }
    )


@app.errorhandler(RouteError)
def handle_route_error(exc: RouteError):
    return jsonify({"error": str(exc)}), 400


def serialize_preferences(preferences: LoopPreferenceProfile) -> dict[str, float]:
    return {
        "pavement_preference": preferences.pavement_preference,
        "quiet_preference": preferences.quiet_preference,
        "green_preference": preferences.green_preference,
        "hill_preference": preferences.hill_preference,
    }


def serialize_route_summary(result) -> dict:
    return {
        "distance_m": result.distance_m,
        "distance_km": result.distance_km,
        "distance_mi": result.distance_mi,
        "duration_s": result.duration_s,
        "duration_min": result.duration_s / 60.0,
        "ascent_m": result.ascent_m,
        "ascent_ft": meters_to_feet(result.ascent_m),
        "descent_m": result.descent_m,
        "descent_ft": meters_to_feet(result.descent_m),
        "min_ele_m": result.min_ele_m,
        "max_ele_m": result.max_ele_m,
    }


def serialize_candidate(candidate) -> dict:
    return {
        "score": candidate.score,
        "score_breakdown": candidate.score_breakdown,
        "start_coord": candidate.start_coord,
        "start_offset_m": candidate.start_offset_m,
        "start_offset_miles": candidate.start_offset_m / 1609.344,
        "seed": candidate.seed,
        "route": candidate.route.route_feature,
        "summary": serialize_route_summary(candidate.route),
    }


if __name__ == "__main__":
    app.run(debug=True)
