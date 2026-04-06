from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ORS_URL_TEMPLATE = "https://api.openrouteservice.org/v2/directions/{profile}/geojson"
ORS_POIS_URL = "https://api.openrouteservice.org/pois"
EARTH_RADIUS_M = 6_371_000
MILES_TO_METERS = 1609.344

PAVED_SURFACE_IDS = {1, 3, 4, 14}
TRAIL_WAYTYPE_IDS = {4, 5, 7}
LANDMARK_POI_CATEGORY_IDS = {132, 134, 224, 227, 237, 240, 243, 246, 621, 622, 623, 627}
PARK_POI_CATEGORY_IDS = {272, 279, 280, 625}
WATER_POI_CATEGORY_IDS = {332, 338, 340, 623}
PRIORITY_OPTIONS = (
    "Distance accuracy",
    "Closer start",
    "Simple navigation",
    "Paved surface",
    "Elevation profile",
    "Landmarks",
    "Quiet surroundings",
    "Nature access",
    "Trail quality",
    "Low interruptions",
    "Lighting and confidence",
)
ROUTE_PATTERN_OPTIONS = ("loop", "out_and_back", "either")
REPEAT_PREFERENCE_OPTIONS = ("none", "as_needed", "preferred")
FOCUS_FEATURE_OPTIONS = ("climb",)
NON_NEGOTIABLE_OPTIONS = (
    "Distance accuracy",
    "Closer start",
    "Stay close to start",
    "No repeats",
    "Simple navigation",
    "Paved surface",
    "Elevation profile",
    "Landmarks",
    "Quiet surroundings",
    "Nature access",
    "Trail quality",
    "Low interruptions",
    "Lighting and confidence",
)


class RouteError(Exception):
    """Raised when the route request or input is invalid."""


class RouteFeasibilityError(RouteError):
    """Raised when routes exist, but none satisfy non-negotiable constraints."""

    def __init__(self, message: str, *, failure_analysis: dict):
        super().__init__(message)
        self.failure_analysis = failure_analysis


@dataclass
class RouteResult:
    route_feature: dict
    raw_geojson: dict
    distance_m: float
    duration_s: float
    ascent_m: float
    descent_m: float
    min_ele_m: float | None
    max_ele_m: float | None
    extras: dict
    poi_summary: dict | None = None

    @property
    def distance_km(self) -> float:
        return self.distance_m / 1000.0

    @property
    def distance_mi(self) -> float:
        return self.distance_m / MILES_TO_METERS


@dataclass
class LoopPreferenceProfile:
    pavement_preference: float
    quiet_preference: float
    green_preference: float
    hill_preference: float


@dataclass
class PlanningRequest:
    center: list[float]
    profile: str
    target_distance_miles: float
    distance_tolerance_miles: float
    start_radius_miles: float
    max_distance_from_start_miles: float
    max_candidates: int
    seed_count: int
    start_limit: int
    seed_offset: int
    route_pattern_preference: str
    repeat_preference: str
    focus_feature: str | None
    top_priority: str
    secondary_priority: str | None
    non_negotiables: list[str]
    preferences: LoopPreferenceProfile
    design_brief: str

    @property
    def target_distance_m(self) -> float:
        return miles_to_meters(self.target_distance_miles)

    @property
    def start_radius_m(self) -> float:
        return miles_to_meters(self.start_radius_miles)

    @property
    def max_distance_from_start_m(self) -> float:
        return miles_to_meters(self.max_distance_from_start_miles)


@dataclass
class LoopCandidate:
    start_coord: list[float]
    start_offset_m: float
    seed: int
    route: RouteResult
    score: float
    score_breakdown: dict[str, float]
    pattern_type: str = "loop"
    pattern_metadata: dict | None = None
    ranking_breakdown: dict[str, float] | None = None
    constraint_results: dict[str, dict] | None = None
    traits: "RouteTraits | None" = None
    badges: list["RouteBadge"] | None = None
    summary: "RouteSummary | None" = None


@dataclass
class LlmPreferenceHint:
    preferences: LoopPreferenceProfile
    summary: str


@dataclass
class RouteTraits:
    paved_ratio: float | None
    trail_ratio: float | None
    average_noise: float | None
    average_green: float | None
    ascent_ft_per_mi: float
    turn_count: int
    sharp_turn_count: int
    turns_per_mile: float
    turn_density_fit: float
    landmark_count: int
    park_count: int
    water_count: int
    landmark_signal: float
    max_distance_from_start_miles_actual: float
    repeat_count: int
    pattern_type: str
    repeat_fit: float
    outbound_distance_miles: float | None
    anchor_distance_miles: float | None
    repeat_segment_distance_miles: float | None
    repeat_segment_climb_feet: float | None
    repeat_segment_ft_per_mile: float | None
    distance_fit: float
    start_convenience: float
    surface_fit: float
    quiet_fit: float
    green_fit: float
    hill_fit: float
    route_simplicity: float
    discovery_fit: float
    training_fit: float
    trail_suitability: float
    is_loop: bool


@dataclass
class RouteBadge:
    code: str
    label: str
    strength: float


@dataclass
class RouteSummary:
    headline: str
    strengths: list[str]
    tradeoffs: list[str]
    top_reasons: list[str]


def parse_coord(text: str) -> list[float]:
    try:
        lon_s, lat_s = text.split(",", 1)
        lon = float(lon_s.strip())
        lat = float(lat_s.strip())
    except Exception as exc:
        raise RouteError(f"Bad coordinate '{text}'. Expected LON,LAT") from exc

    return validate_lon_lat(lon, lat, raw=text)


def validate_lon_lat(lon: float, lat: float, *, raw: str | None = None) -> list[float]:
    if not -180 <= lon <= 180:
        raise RouteError(f"Longitude out of range in '{raw or f'{lon},{lat}'}'")
    if not -90 <= lat <= 90:
        raise RouteError(f"Latitude out of range in '{raw or f'{lon},{lat}'}'")
    return [lon, lat]


def parse_coord_lines(text: str) -> list[list[float]]:
    coords: list[list[float]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            coords.append(parse_coord(stripped))
    return validate_coords(coords)


def validate_coords(coords: Iterable[Iterable[float]], *, minimum: int = 2) -> list[list[float]]:
    normalized = [[float(coord[0]), float(coord[1])] for coord in coords]
    if len(normalized) < minimum:
        raise RouteError(f"Pass at least {minimum} coordinate{'s' if minimum != 1 else ''}.")
    return normalized


def parse_positive_float(value: object, *, name: str, minimum: float = 0.0) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise RouteError(f"{name} must be a number.") from exc

    if parsed < minimum:
        comparator = "greater than zero" if minimum > 0 else f"at least {minimum}"
        raise RouteError(f"{name} must be {comparator}.")
    return parsed


def parse_bias(value: object, *, name: str, minimum: float = 0.0, maximum: float = 1.0) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise RouteError(f"{name} must be a number.") from exc
    if parsed < minimum or parsed > maximum:
        raise RouteError(f"{name} must be between {minimum} and {maximum}.")
    return parsed


def parse_priority(
    value: object,
    *,
    name: str,
    required: bool = True,
) -> str | None:
    text = str(value or "").strip()
    if not text:
        if required:
            raise RouteError(f"{name} is required.")
        return None
    if text not in PRIORITY_OPTIONS:
        raise RouteError(f"{name} must be one of: {', '.join(PRIORITY_OPTIONS)}.")
    return text


def parse_priority_list(value: object, *, name: str) -> list[str]:
    if value in (None, "", []):
        return []

    if isinstance(value, str):
        raw_items = [item.strip() for item in value.split(",") if item.strip()]
    elif isinstance(value, (list, tuple)):
        raw_items = [str(item).strip() for item in value if str(item).strip()]
    else:
        raise RouteError(f"{name} must be a list of priorities.")

    normalized: list[str] = []
    for item in raw_items:
        if item not in NON_NEGOTIABLE_OPTIONS:
            raise RouteError(
                f"{name} entries must be one of: {', '.join(NON_NEGOTIABLE_OPTIONS)}."
            )
        if item not in normalized:
            normalized.append(item)
    return normalized


def parse_choice(
    value: object,
    *,
    name: str,
    allowed: tuple[str, ...],
    required: bool = True,
) -> str | None:
    text = str(value or "").strip().lower()
    if not text:
        if required:
            raise RouteError(f"{name} is required.")
        return None
    if text not in allowed:
        raise RouteError(f"{name} must be one of: {', '.join(allowed)}.")
    return text


def first_value(data: dict, *names: str, default=None):
    for name in names:
        if name in data:
            return data[name]
    return default


def parse_preferences(
    data: dict,
    *,
    pavement_default: float = 0.8,
    quiet_default: float = 0.8,
    green_default: float = 0.7,
    hill_default: float = 0.0,
) -> LoopPreferenceProfile:
    return LoopPreferenceProfile(
        pavement_preference=parse_bias(
            first_value(data, "pavement_preference", "pavement", default=pavement_default),
            name="Pavement preference",
        ),
        quiet_preference=parse_bias(
            first_value(data, "quiet_preference", "quiet", default=quiet_default),
            name="Quiet preference",
        ),
        green_preference=parse_bias(
            first_value(data, "green_preference", "green", default=green_default),
            name="Green preference",
        ),
        hill_preference=parse_bias(
            first_value(data, "hill_preference", "hills", default=hill_default),
            name="Hill preference",
            minimum=-1.0,
            maximum=1.0,
        ),
    )


def default_max_distance_from_start_miles(
    *,
    route_pattern_preference: str,
    target_distance_miles: float,
    start_radius_miles: float,
) -> float:
    if route_pattern_preference == "loop":
        return max((1.25 * target_distance_miles / 3.0), start_radius_miles + 0.25, 0.75)
    return max(target_distance_miles / 2.0, start_radius_miles)


def default_focus_feature(
    *,
    top_priority: str,
    secondary_priority: str | None,
    preferences: LoopPreferenceProfile,
) -> str | None:
    if (
        top_priority == "Elevation profile"
        or secondary_priority == "Elevation profile"
        or preferences.hill_preference >= 0.65
    ):
        return "climb"
    return None


def parse_planning_request(
    data: dict,
    *,
    profile_default: str = "foot-walking",
    target_distance_default: float = 6.0,
    distance_tolerance_default: float = 0.5,
    start_radius_default: float = 1.5,
    max_distance_from_start_default: float | None = None,
    max_candidates_default: int = 3,
    seed_count_default: int = 1,
    start_limit_default: int = 3,
    seed_offset_default: int = 0,
    route_pattern_default: str = "loop",
    repeat_preference_default: str = "none",
    focus_feature_default: str | None = None,
    top_priority_default: str = "Distance accuracy",
    secondary_priority_default: str | None = "Closer start",
    pavement_default: float = 0.8,
    quiet_default: float = 0.8,
    green_default: float = 0.7,
    hill_default: float = 0.0,
) -> PlanningRequest:
    target_distance_miles = parse_positive_float(
        first_value(
            data,
            "target_distance_miles",
            "miles",
            default=target_distance_default,
        ),
        name="Target distance",
        minimum=0.1,
    )
    start_radius_miles = parse_positive_float(
        first_value(
            data,
            "start_radius_miles",
            "radius",
            default=start_radius_default,
        ),
        name="Start radius",
        minimum=0.0,
    )
    route_pattern_preference = parse_choice(
        first_value(
            data,
            "route_pattern_preference",
            "route_pattern",
            "route_shape",
            default=route_pattern_default,
        ),
        name="Route pattern",
        allowed=ROUTE_PATTERN_OPTIONS,
    )
    repeat_preference = parse_choice(
        first_value(
            data,
            "repeat_preference",
            "repeat_mode",
            default=repeat_preference_default,
        ),
        name="Repeat preference",
        allowed=REPEAT_PREFERENCE_OPTIONS,
    )
    preferences = parse_preferences(
        data,
        pavement_default=pavement_default,
        quiet_default=quiet_default,
        green_default=green_default,
        hill_default=hill_default,
    )
    top_priority = parse_priority(
        first_value(data, "top_priority", default=top_priority_default),
        name="Top priority",
        required=True,
    )
    secondary_priority = parse_priority(
        first_value(data, "secondary_priority", default=secondary_priority_default),
        name="Secondary priority",
        required=False,
    )
    max_distance_from_start_miles = parse_positive_float(
        first_value(
            data,
            "max_distance_from_start_miles",
            "max_distance_from_start",
            "max_drift_miles",
            default=(
                max_distance_from_start_default
                if max_distance_from_start_default is not None
                else default_max_distance_from_start_miles(
                    route_pattern_preference=route_pattern_preference,
                    target_distance_miles=target_distance_miles,
                    start_radius_miles=start_radius_miles,
                )
            ),
        ),
        name="Max distance from start",
        minimum=0.1,
    )
    focus_feature = parse_choice(
        first_value(
            data,
            "focus_feature",
            default=(
                focus_feature_default
                if focus_feature_default is not None
                else default_focus_feature(
                    top_priority=top_priority,
                    secondary_priority=secondary_priority,
                    preferences=preferences,
                )
            ),
        ),
        name="Focus feature",
        allowed=FOCUS_FEATURE_OPTIONS,
        required=False,
    )
    return PlanningRequest(
        center=parse_coord(first_value(data, "center_coord", "center", default="")),
        profile=str(first_value(data, "profile", default=profile_default)),
        target_distance_miles=target_distance_miles,
        distance_tolerance_miles=parse_positive_float(
            first_value(
                data,
                "distance_tolerance_miles",
                "distance_tolerance",
                "tolerance",
                default=distance_tolerance_default,
            ),
            name="Distance tolerance",
            minimum=0.0,
        ),
        start_radius_miles=start_radius_miles,
        max_distance_from_start_miles=max_distance_from_start_miles,
        max_candidates=int(
            parse_positive_float(
                first_value(data, "max_candidates", default=max_candidates_default),
                name="Max candidates",
                minimum=1.0,
            )
        ),
        seed_count=int(
            parse_positive_float(
                first_value(data, "seed_count", default=seed_count_default),
                name="Seed count",
                minimum=1.0,
            )
        ),
        start_limit=int(
            parse_positive_float(
                first_value(data, "start_limit", default=start_limit_default),
                name="Start limit",
                minimum=1.0,
            )
        ),
        seed_offset=int(
            parse_positive_float(
                first_value(data, "seed_offset", default=seed_offset_default),
                name="Seed offset",
                minimum=0.0,
            )
        ),
        route_pattern_preference=route_pattern_preference,
        repeat_preference=repeat_preference,
        focus_feature=focus_feature,
        top_priority=top_priority,
        secondary_priority=secondary_priority,
        non_negotiables=parse_priority_list(
            first_value(data, "non_negotiables", "must_have", default=[]),
            name="Non-negotiables",
        ),
        preferences=preferences,
        design_brief=str(first_value(data, "design_brief", "brief", default="")).strip(),
    )


def miles_to_meters(miles: float) -> float:
    return miles * MILES_TO_METERS


def meters_to_feet(meters: float) -> float:
    return meters * 3.28084


def compute_elevation_stats(
    coords: list[list[float]],
    noise_threshold_m: float = 2.0,
) -> tuple[float, float, float | None, float | None]:
    elevations = [pt[2] for pt in coords if len(pt) >= 3 and pt[2] is not None]
    if not elevations:
        return 0.0, 0.0, None, None

    ascent = 0.0
    descent = 0.0

    for idx in range(1, len(elevations)):
        delta = elevations[idx] - elevations[idx - 1]
        if delta >= noise_threshold_m:
            ascent += delta
        elif delta <= -noise_threshold_m:
            descent += abs(delta)

    return ascent, descent, min(elevations), max(elevations)


def geodesic_offset(origin: list[float], distance_m: float, bearing_deg: float) -> list[float]:
    lon_deg, lat_deg = origin
    bearing_rad = math.radians(bearing_deg)
    lat1 = math.radians(lat_deg)
    lon1 = math.radians(lon_deg)
    angular_distance = distance_m / EARTH_RADIUS_M

    lat2 = math.asin(
        math.sin(lat1) * math.cos(angular_distance)
        + math.cos(lat1) * math.sin(angular_distance) * math.cos(bearing_rad)
    )
    lon2 = lon1 + math.atan2(
        math.sin(bearing_rad) * math.sin(angular_distance) * math.cos(lat1),
        math.cos(angular_distance) - math.sin(lat1) * math.sin(lat2),
    )

    lon = ((math.degrees(lon2) + 540) % 360) - 180
    lat = math.degrees(lat2)
    return validate_lon_lat(lon, lat)


def haversine_distance_m(coord_a: list[float], coord_b: list[float]) -> float:
    lon1, lat1 = math.radians(coord_a[0]), math.radians(coord_a[1])
    lon2, lat2 = math.radians(coord_b[0]), math.radians(coord_b[1])
    delta_lon = lon2 - lon1
    delta_lat = lat2 - lat1
    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2
    )
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(a))


def bearing_degrees(coord_a: list[float], coord_b: list[float]) -> float | None:
    if haversine_distance_m(coord_a, coord_b) < 1.0:
        return None

    lon1 = math.radians(coord_a[0])
    lat1 = math.radians(coord_a[1])
    lon2 = math.radians(coord_b[0])
    lat2 = math.radians(coord_b[1])
    delta_lon = lon2 - lon1

    y = math.sin(delta_lon) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(delta_lon)
    angle = math.degrees(math.atan2(y, x))
    return (angle + 360.0) % 360.0


def angular_difference_degrees(a: float, b: float) -> float:
    delta = abs(a - b) % 360.0
    return min(delta, 360.0 - delta)


def turn_metrics_from_coords(
    coords: list[list[float]],
    *,
    min_segment_m: float = 35.0,
    turn_threshold_deg: float = 28.0,
    sharp_turn_threshold_deg: float = 60.0,
) -> tuple[int, int]:
    if len(coords) < 3:
        return 0, 0

    bearings: list[float] = []
    for index in range(len(coords) - 1):
        start = coords[index]
        end = coords[index + 1]
        if haversine_distance_m(start, end) < min_segment_m:
            continue
        bearing = bearing_degrees(start, end)
        if bearing is not None:
            bearings.append(bearing)

    if len(bearings) < 2:
        return 0, 0

    turn_count = 0
    sharp_turn_count = 0
    for index in range(len(bearings) - 1):
        change = angular_difference_degrees(bearings[index], bearings[index + 1])
        if change >= turn_threshold_deg:
            turn_count += 1
        if change >= sharp_turn_threshold_deg:
            sharp_turn_count += 1
    return turn_count, sharp_turn_count


def generate_candidate_starts(center: list[float], radius_m: float) -> list[tuple[list[float], float]]:
    starts: list[tuple[list[float], float]] = [(center, 0.0)]
    if radius_m <= 0:
        return starts

    for ring_distance in (radius_m * 0.45, radius_m * 0.9):
        for bearing in (0, 60, 120, 180, 240, 300):
            starts.append((geodesic_offset(center, ring_distance, bearing), ring_distance))
    return starts


def extract_response_text(data: dict) -> str:
    output_text = data.get("output_text")
    if isinstance(output_text, str) and output_text.strip():
        return output_text

    for item in data.get("output", []):
        for content in item.get("content", []):
            if content.get("type") == "output_text" and content.get("text"):
                return content["text"]
    raise RouteError("OpenAI response did not include text output.")


def maybe_apply_llm_preferences(
    *,
    design_brief: str,
    base_preferences: LoopPreferenceProfile,
) -> LlmPreferenceHint | None:
    if not design_brief.strip():
        return None

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None

    import requests

    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "summary": {"type": "string"},
            "pavement_preference": {"type": "number", "minimum": 0, "maximum": 1},
            "quiet_preference": {"type": "number", "minimum": 0, "maximum": 1},
            "green_preference": {"type": "number", "minimum": 0, "maximum": 1},
            "hill_preference": {"type": "number", "minimum": -1, "maximum": 1},
        },
        "required": [
            "summary",
            "pavement_preference",
            "quiet_preference",
            "green_preference",
            "hill_preference",
        ],
    }

    payload = {
        "model": model,
        "input": [
            {
                "role": "system",
                "content": (
                    "Convert a runner's natural language route brief into numeric routing "
                    "preferences. Return JSON only."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Current preferences: paved={base_preferences.pavement_preference:.2f}, "
                    f"quiet={base_preferences.quiet_preference:.2f}, "
                    f"green={base_preferences.green_preference:.2f}, "
                    f"hills={base_preferences.hill_preference:.2f}. "
                    f"Runner brief: {design_brief}"
                ),
            },
        ],
        "text": {
            "format": {
                "type": "json_schema",
                "name": "route_design_preferences",
                "strict": True,
                "schema": schema,
            }
        },
    }

    try:
        response = requests.post(
            "https://api.openai.com/v1/responses",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=45,
        )
        response.raise_for_status()
        data = response.json()
        parsed = json.loads(extract_response_text(data))
    except Exception as exc:
        raise RouteError(f"OpenAI design parsing failed: {exc}") from exc

    preferences = LoopPreferenceProfile(
        pavement_preference=parse_bias(
            parsed["pavement_preference"], name="pavement_preference"
        ),
        quiet_preference=parse_bias(parsed["quiet_preference"], name="quiet_preference"),
        green_preference=parse_bias(parsed["green_preference"], name="green_preference"),
        hill_preference=parse_bias(
            parsed["hill_preference"], name="hill_preference", minimum=-1.0, maximum=1.0
        ),
    )
    return LlmPreferenceHint(preferences=preferences, summary=parsed["summary"].strip())


def average_extra_score(extras: dict, key: str) -> float | None:
    node = extras.get(key) or extras.get(f"{key}s")
    if not node:
        return None

    summary = node.get("summary") or []
    total_distance = sum(item.get("distance", 0.0) for item in summary)
    if total_distance <= 0:
        return None

    weighted = sum(item.get("value", 0.0) * item.get("distance", 0.0) for item in summary)
    return weighted / total_distance


def ratio_for_values(extras: dict, key: str, accepted_values: set[int]) -> float | None:
    node = extras.get(key) or extras.get(f"{key}s")
    if not node:
        return None

    summary = node.get("summary") or []
    total_distance = sum(item.get("distance", 0.0) for item in summary)
    if total_distance <= 0:
        return None

    accepted_distance = sum(
        item.get("distance", 0.0)
        for item in summary
        if int(item.get("value", -1)) in accepted_values
    )
    return accepted_distance / total_distance


def landmark_sensitive_request(
    top_priority: str,
    secondary_priority: str | None,
    non_negotiables: list[str] | None = None,
) -> bool:
    interested = {top_priority, secondary_priority or ""}
    return (
        "Landmarks" in interested
        or "Nature access" in interested
        or "Landmarks" in (non_negotiables or [])
        or "Nature access" in (non_negotiables or [])
    )


def route_geometry_2d(route_feature: dict) -> dict:
    coords = route_feature.get("geometry", {}).get("coordinates", [])
    return {
        "type": "LineString",
        "coordinates": [[coord[0], coord[1]] for coord in coords if len(coord) >= 2],
    }


def extract_poi_category_ids(feature: dict) -> set[int]:
    props = feature.get("properties", {})
    raw_ids = (
        props.get("category_ids")
        or props.get("category_id")
        or props.get("category")
        or []
    )
    if isinstance(raw_ids, int):
        raw_items = [raw_ids]
    elif isinstance(raw_ids, str):
        raw_items = [part.strip() for part in raw_ids.split(",") if part.strip()]
    else:
        raw_items = list(raw_ids)

    category_ids: set[int] = set()
    for value in raw_items:
        try:
            category_ids.add(int(value))
        except (TypeError, ValueError):
            continue
    return category_ids


def summarize_route_pois(features: list[dict]) -> dict:
    landmark_count = 0
    park_count = 0
    water_count = 0

    for feature in features:
        category_ids = extract_poi_category_ids(feature)
        if category_ids & LANDMARK_POI_CATEGORY_IDS:
            landmark_count += 1
        if category_ids & PARK_POI_CATEGORY_IDS:
            park_count += 1
        if category_ids & WATER_POI_CATEGORY_IDS:
            water_count += 1

    return {
        "total_count": len(features),
        "landmark_count": landmark_count,
        "park_count": park_count,
        "water_count": water_count,
    }


def fetch_route_poi_summary(
    *,
    api_key: str,
    route_feature: dict,
    buffer_m: int = 120,
    timeout: int = 20,
) -> dict | None:
    import requests

    geometry = route_geometry_2d(route_feature)
    if len(geometry["coordinates"]) < 2:
        return None

    payload = {
        "request": "pois",
        "geometry": {
            "geojson": geometry,
            "buffer": buffer_m,
        },
        "filters": {
            "category_group_ids": [220, 260, 330, 620],
        },
        "limit": 200,
    }
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    try:
        response = requests.post(ORS_POIS_URL, headers=headers, json=payload, timeout=timeout)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException:
        return None

    features = data.get("features") or []
    return summarize_route_pois(features)


def clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def score_loop_candidate(
    *,
    route: RouteResult,
    target_distance_m: float,
    start_offset_m: float,
    max_start_offset_m: float,
    preferences: LoopPreferenceProfile,
) -> tuple[float, dict[str, float]]:
    extras = route.extras
    paved_ratio = ratio_for_values(extras, "surface", PAVED_SURFACE_IDS)
    trail_ratio = ratio_for_values(extras, "waytype", TRAIL_WAYTYPE_IDS)
    average_noise = average_extra_score(extras, "noise")
    average_green = average_extra_score(extras, "green")

    paved_target = 0.15 + (0.8 * preferences.pavement_preference)
    pavement_score = 0.5
    if paved_ratio is not None:
        pavement_score = 1 - min(1.0, abs(paved_ratio - paved_target))
    elif trail_ratio is not None:
        pavement_score = 1 - min(1.0, abs((1 - trail_ratio) - paved_target))

    quiet_score = 0.5 if average_noise is None else clamp(1 - (average_noise / 10.0))
    green_score = 0.5 if average_green is None else clamp(average_green / 10.0)

    ascent_ft_per_mi = 0.0
    if route.distance_mi > 0:
        ascent_ft_per_mi = meters_to_feet(route.ascent_m) / route.distance_mi

    hill_target_ft_per_mi = 50 + ((preferences.hill_preference + 1) / 2.0) * 350
    hill_score = 1 - min(1.0, abs(ascent_ft_per_mi - hill_target_ft_per_mi) / 350.0)

    distance_score = 1 - min(
        1.0,
        abs(route.distance_m - target_distance_m) / max(target_distance_m * 0.35, 1.0),
    )
    start_score = 1.0
    if max_start_offset_m > 0:
        start_score = 1 - min(1.0, start_offset_m / max_start_offset_m)

    score_breakdown = {
        "distance": distance_score,
        "pavement": pavement_score,
        "quiet": quiet_score,
        "green": green_score,
        "hills": hill_score,
        "start": start_score,
    }

    score = (
        distance_score * 0.34
        + pavement_score * 0.2
        + quiet_score * 0.14
        + green_score * 0.12
        + hill_score * 0.12
        + start_score * 0.08
    )
    return score, score_breakdown


def derive_route_traits(
    *,
    route: RouteResult,
    score_breakdown: dict[str, float],
    center: list[float],
    start_offset_m: float,
    start_radius_m: float,
    pattern_type: str = "loop",
    pattern_metadata: dict | None = None,
) -> RouteTraits:
    extras = route.extras
    paved_ratio = ratio_for_values(extras, "surface", PAVED_SURFACE_IDS)
    trail_ratio = ratio_for_values(extras, "waytype", TRAIL_WAYTYPE_IDS)
    average_noise = average_extra_score(extras, "noise")
    average_green = average_extra_score(extras, "green")

    ascent_ft_per_mi = 0.0
    if route.distance_mi > 0:
        ascent_ft_per_mi = meters_to_feet(route.ascent_m) / route.distance_mi

    coords = route.route_feature.get("geometry", {}).get("coordinates", [])
    turn_count, sharp_turn_count = turn_metrics_from_coords(coords)
    turns_per_mile = turn_count / max(route.distance_mi, 0.1)
    sharp_turn_ratio = sharp_turn_count / max(turn_count, 1)
    turn_density_fit = clamp(1 - min(1.0, turns_per_mile / 8.0) - (sharp_turn_ratio * 0.2))

    poi_summary = route.poi_summary or {}
    landmark_count = int(first_value(poi_summary, "landmark_count", default=0) or 0)
    park_count = int(first_value(poi_summary, "park_count", default=0) or 0)
    water_count = int(first_value(poi_summary, "water_count", default=0) or 0)
    landmark_density = landmark_count / max(route.distance_mi, 1.0)
    nature_density = (park_count + water_count) / max(route.distance_mi, 1.0)
    landmark_signal = clamp(
        (clamp(landmark_density / 1.5) * 0.7)
        + (clamp(nature_density / 1.5) * 0.15)
        + (score_breakdown.get("green", 0.5) * 0.15)
    )
    pattern_metadata = pattern_metadata or {}
    repeat_count = int(pattern_metadata.get("repeat_count", 1) or 1)
    actual_max_distance_from_start = max_distance_from_start_miles(
        coords=coords,
        center=center,
    )
    outbound_distance_miles = pattern_metadata.get("outbound_distance_miles")
    anchor_distance_miles = pattern_metadata.get("anchor_distance_miles")
    repeat_segment_distance_miles = pattern_metadata.get("repeat_segment_distance_miles")
    repeat_segment_climb_feet = pattern_metadata.get("repeat_segment_climb_feet")
    repeat_segment_ft_per_mile = pattern_metadata.get("repeat_segment_ft_per_mile")

    surface_fit = score_breakdown.get("pavement", 0.5)
    quiet_fit = score_breakdown.get("quiet", 0.5)
    green_fit = score_breakdown.get("green", 0.5)
    hill_fit = score_breakdown.get("hills", 0.5)
    distance_fit = score_breakdown.get("distance", 0.5)
    start_convenience = score_breakdown.get("start", 0.5)

    if route.poi_summary is None:
        landmark_signal = clamp((green_fit * 0.65) + (quiet_fit * 0.35))

    route_simplicity = clamp(
        (start_convenience * 0.3)
        + (turn_density_fit * 0.45)
        + (((1 - trail_ratio) if trail_ratio is not None else 0.5) * 0.1)
        + (surface_fit * 0.15)
    )
    discovery_fit = clamp(
        (green_fit * 0.4)
        + (quiet_fit * 0.15)
        + (landmark_signal * 0.25)
        + (clamp(nature_density / 2.0) * 0.2)
    )
    training_fit = clamp(
        (distance_fit * 0.35)
        + (hill_fit * 0.3)
        + (surface_fit * 0.2)
        + (turn_density_fit * 0.15)
    )
    trail_suitability = clamp(
        (((trail_ratio or 0.0) * 0.5) + ((1 - surface_fit) * 0.15) + (hill_fit * 0.15) + (green_fit * 0.2))
    )
    if pattern_type == "hill_repeat":
        if repeat_count <= 1:
            repeat_fit = 0.45
        else:
            repeat_fit = clamp(0.7 + min(0.25, (repeat_count - 1) * 0.05))
    elif repeat_count > 1:
        repeat_fit = clamp(0.4 + min(0.2, (repeat_count - 1) * 0.04))
    else:
        repeat_fit = 0.5

    is_loop = False
    if len(coords) >= 2:
        is_loop = haversine_distance_m(coords[0], coords[-1]) <= max(150.0, start_radius_m * 0.5)

    return RouteTraits(
        paved_ratio=paved_ratio,
        trail_ratio=trail_ratio,
        average_noise=average_noise,
        average_green=average_green,
        ascent_ft_per_mi=ascent_ft_per_mi,
        turn_count=turn_count,
        sharp_turn_count=sharp_turn_count,
        turns_per_mile=turns_per_mile,
        turn_density_fit=turn_density_fit,
        landmark_count=landmark_count,
        park_count=park_count,
        water_count=water_count,
        landmark_signal=landmark_signal,
        max_distance_from_start_miles_actual=actual_max_distance_from_start,
        repeat_count=repeat_count,
        pattern_type=pattern_type,
        repeat_fit=repeat_fit,
        outbound_distance_miles=float(outbound_distance_miles) if outbound_distance_miles is not None else None,
        anchor_distance_miles=float(anchor_distance_miles) if anchor_distance_miles is not None else None,
        repeat_segment_distance_miles=(
            float(repeat_segment_distance_miles) if repeat_segment_distance_miles is not None else None
        ),
        repeat_segment_climb_feet=(
            float(repeat_segment_climb_feet) if repeat_segment_climb_feet is not None else None
        ),
        repeat_segment_ft_per_mile=(
            float(repeat_segment_ft_per_mile) if repeat_segment_ft_per_mile is not None else None
        ),
        distance_fit=distance_fit,
        start_convenience=start_convenience,
        surface_fit=surface_fit,
        quiet_fit=quiet_fit,
        green_fit=green_fit,
        hill_fit=hill_fit,
        route_simplicity=route_simplicity,
        discovery_fit=discovery_fit,
        training_fit=training_fit,
        trail_suitability=trail_suitability,
        is_loop=is_loop,
    )


def dimension_scores_from_traits(
    score_breakdown: dict[str, float],
    traits: RouteTraits,
) -> dict[str, float]:
    environmental_fit = clamp((traits.quiet_fit * 0.45) + (traits.green_fit * 0.55))
    confidence_fit = clamp(
        (traits.route_simplicity * 0.35)
        + (traits.turn_density_fit * 0.2)
        + (traits.start_convenience * 0.2)
        + (traits.surface_fit * 0.15)
        + (traits.quiet_fit * 0.1)
    )
    landmark_fit = clamp((traits.landmark_signal * 0.75) + (traits.discovery_fit * 0.25))
    interruption_fit = clamp(
        (traits.turn_density_fit * 0.45)
        + (traits.training_fit * 0.35)
        + (traits.start_convenience * 0.1)
        + (traits.surface_fit * 0.1)
    )
    return {
        "distance_fit": score_breakdown.get("distance", 0.5),
        "start_convenience": score_breakdown.get("start", 0.5),
        "surface_fit": score_breakdown.get("pavement", 0.5),
        "hill_fit": score_breakdown.get("hills", 0.5),
        "environmental_fit": environmental_fit,
        "confidence_fit": confidence_fit,
        "landmark_fit": landmark_fit,
        "interruption_fit": interruption_fit,
        "route_simplicity": traits.route_simplicity,
        "discovery_fit": traits.discovery_fit,
        "training_fit": traits.training_fit,
        "trail_suitability": traits.trail_suitability,
        "repeat_fit": traits.repeat_fit,
    }


def priority_weight_map(priority: str) -> dict[str, float]:
    maps = {
        "Distance accuracy": {"distance_fit": 1.0},
        "Closer start": {"start_convenience": 1.0},
        "Simple navigation": {"route_simplicity": 0.75, "start_convenience": 0.25},
        "Paved surface": {"surface_fit": 1.0},
        "Elevation profile": {"hill_fit": 0.65, "training_fit": 0.35},
        "Landmarks": {"landmark_fit": 0.65, "discovery_fit": 0.35},
        "Quiet surroundings": {"environmental_fit": 0.7, "confidence_fit": 0.3},
        "Nature access": {"discovery_fit": 0.55, "environmental_fit": 0.45},
        "Trail quality": {"trail_suitability": 0.6, "surface_fit": 0.4},
        "Low interruptions": {"interruption_fit": 0.65, "training_fit": 0.35},
        "Lighting and confidence": {"confidence_fit": 0.7, "route_simplicity": 0.3},
    }
    return maps.get(priority, {"distance_fit": 1.0})


def aggregate_candidate_score(
    *,
    candidate: LoopCandidate,
    request: PlanningRequest,
    traits: RouteTraits,
    score_breakdown: dict[str, float],
    top_priority: str,
    secondary_priority: str | None,
) -> tuple[float, dict[str, float]]:
    dimension_scores = dimension_scores_from_traits(score_breakdown, traits)
    weights = {
        "distance_fit": 0.28,
        "surface_fit": 0.16,
        "environmental_fit": 0.14,
        "hill_fit": 0.12,
        "start_convenience": 0.10,
        "route_simplicity": 0.08,
        "discovery_fit": 0.06,
        "training_fit": 0.04,
        "trail_suitability": 0.02,
        "repeat_fit": 0.0,
        "confidence_fit": 0.0,
        "landmark_fit": 0.0,
        "interruption_fit": 0.0,
    }

    for dimension, amount in priority_weight_map(top_priority).items():
        weights[dimension] = weights.get(dimension, 0.0) + (0.12 * amount)

    if secondary_priority:
        for dimension, amount in priority_weight_map(secondary_priority).items():
            weights[dimension] = weights.get(dimension, 0.0) + (0.06 * amount)

    total_weight = sum(weights.values()) or 1.0
    normalized_weights = {
        dimension: weight / total_weight for dimension, weight in weights.items()
    }
    ranking_breakdown = {
        dimension: dimension_scores[dimension] * normalized_weights[dimension]
        for dimension in normalized_weights
    }
    score = sum(ranking_breakdown.values())

    if candidate.pattern_type == "loop" and request.route_pattern_preference == "loop":
        score += 0.02
        ranking_breakdown["pattern_alignment"] = 0.02
    elif candidate.pattern_type == "out_and_back":
        if request.route_pattern_preference == "out_and_back":
            score += 0.03
            ranking_breakdown["pattern_alignment"] = 0.03
        elif request.route_pattern_preference == "either":
            score -= 0.02
            ranking_breakdown["pattern_alignment"] = -0.02
    elif candidate.pattern_type == "hill_repeat":
        if request.repeat_preference == "preferred":
            bonus = 0.05 * traits.repeat_fit
            score += bonus
            ranking_breakdown["pattern_alignment"] = bonus
        else:
            penalty = route_repeat_penalty(
                pattern_type=candidate.pattern_type,
                repeat_preference=request.repeat_preference,
                repeat_count=traits.repeat_count,
            )
            score -= penalty
            ranking_breakdown["pattern_alignment"] = -penalty

    if request.repeat_preference == "preferred" and candidate.pattern_type != "hill_repeat" and traits.repeat_count <= 1:
        score -= 0.01
        ranking_breakdown["repeat_preference"] = -0.01
    elif request.repeat_preference == "none" and traits.repeat_count > 1:
        penalty = route_repeat_penalty(
            pattern_type=candidate.pattern_type,
            repeat_preference=request.repeat_preference,
            repeat_count=traits.repeat_count,
        )
        score -= penalty
        ranking_breakdown["repeat_preference"] = -penalty
    return score, ranking_breakdown


def evaluate_non_negotiable(
    *,
    name: str,
    candidate: LoopCandidate,
    request: PlanningRequest,
) -> dict:
    traits = candidate.traits
    if traits is None:
        raise RouteError("Cannot evaluate non-negotiables before deriving traits.")

    if name == "Distance accuracy":
        delta = abs(candidate.route.distance_mi - request.target_distance_miles)
        threshold = request.distance_tolerance_miles
        passed = delta <= threshold
        return {
            "name": name,
            "passed": passed,
            "score": max(0.0, 1 - (delta / max(threshold, 0.25))) if threshold > 0 else float(delta == 0),
            "threshold": threshold,
            "detail": f"Route is {delta:.2f} mi from target with {threshold:.2f} mi tolerance.",
        }

    if name == "Closer start":
        threshold = request.start_radius_miles
        delta = candidate.start_offset_m / MILES_TO_METERS
        passed = delta <= threshold
        return {
            "name": name,
            "passed": passed,
            "score": traits.start_convenience,
            "threshold": threshold,
            "detail": f"Start is {delta:.2f} mi away with {threshold:.2f} mi allowed radius.",
        }

    if name == "Stay close to start":
        threshold = request.max_distance_from_start_miles
        value = traits.max_distance_from_start_miles_actual
        return {
            "name": name,
            "passed": value <= threshold,
            "score": max(0.0, 1 - (value / max(threshold, 0.25))),
            "threshold": threshold,
            "detail": f"Route drifts {value:.2f} mi from the start at its farthest point with {threshold:.2f} mi allowed.",
        }

    if name == "No repeats":
        threshold = 1
        value = traits.repeat_count
        return {
            "name": name,
            "passed": value <= threshold,
            "score": 1.0 if value <= 1 else max(0.0, 1 - ((value - 1) / 4.0)),
            "threshold": threshold,
            "detail": f"Route uses {value} repeat block{'s' if value != 1 else ''}.",
        }

    if name == "Simple navigation":
        threshold = 0.68
        value = traits.route_simplicity
        return {
            "name": name,
            "passed": value >= threshold,
            "score": value,
            "threshold": threshold,
            "detail": f"Route simplicity scored {value:.2f} against a {threshold:.2f} requirement.",
        }

    if name == "Paved surface":
        threshold = 0.65
        value = traits.paved_ratio or 0.0
        return {
            "name": name,
            "passed": value >= threshold and traits.surface_fit >= 0.62,
            "score": value,
            "threshold": threshold,
            "detail": f"Paved share is {value:.2f}; RouteScout requires mostly paved footing.",
        }

    if name == "Elevation profile":
        threshold = 0.72
        value = traits.hill_fit
        return {
            "name": name,
            "passed": value >= threshold,
            "score": value,
            "threshold": threshold,
            "detail": f"Hill-fit scored {value:.2f} for the requested elevation profile.",
        }

    if name == "Landmarks":
        threshold = 0.56
        value = clamp((traits.landmark_signal * 0.75) + (traits.discovery_fit * 0.25))
        return {
            "name": name,
            "passed": value >= threshold,
            "score": value,
            "threshold": threshold,
            "detail": (
                f"Landmark-fit scored {value:.2f}; found {traits.landmark_count} landmark-type "
                f"POIs along the route."
            ),
        }

    if name == "Quiet surroundings":
        threshold = 0.68
        value = traits.quiet_fit
        return {
            "name": name,
            "passed": value >= threshold,
            "score": value,
            "threshold": threshold,
            "detail": f"Quiet-fit scored {value:.2f}; this area may be noisier than requested.",
        }

    if name == "Nature access":
        threshold = 0.62
        value = traits.discovery_fit
        return {
            "name": name,
            "passed": value >= threshold,
            "score": value,
            "threshold": threshold,
            "detail": f"Discovery-fit scored {value:.2f}; greener/scenic exposure may be limited.",
        }

    if name == "Trail quality":
        threshold = 0.62
        value = traits.trail_suitability
        return {
            "name": name,
            "passed": value >= threshold,
            "score": value,
            "threshold": threshold,
            "detail": f"Trail suitability scored {value:.2f}; trail character may be too weak here.",
        }

    if name == "Low interruptions":
        threshold = 0.62
        value = clamp(
            (traits.turn_density_fit * 0.45)
            + (traits.training_fit * 0.35)
            + (traits.route_simplicity * 0.2)
        )
        return {
            "name": name,
            "passed": value >= threshold,
            "score": value,
            "threshold": threshold,
            "detail": (
                f"Interruption proxy scored {value:.2f}; route has {traits.turn_count} meaningful turns "
                f"({traits.turns_per_mile:.1f} per mile)."
            ),
        }

    if name == "Lighting and confidence":
        threshold = 0.66
        value = clamp(
            (traits.route_simplicity * 0.35)
            + (traits.turn_density_fit * 0.2)
            + (traits.start_convenience * 0.2)
            + (traits.surface_fit * 0.15)
            + (traits.quiet_fit * 0.1)
        )
        return {
            "name": name,
            "passed": value >= threshold,
            "score": value,
            "threshold": threshold,
            "detail": f"Confidence proxy scored {value:.2f}; the area may not support the desired route confidence.",
        }

    raise RouteError(f"Unsupported non-negotiable: {name}")


def evaluate_candidate_constraints(
    *,
    candidate: LoopCandidate,
    request: PlanningRequest,
) -> dict[str, dict]:
    return {
        name: evaluate_non_negotiable(name=name, candidate=candidate, request=request)
        for name in request.non_negotiables
    }


def build_feasibility_failure_analysis(
    *,
    request: PlanningRequest,
    candidates: list[LoopCandidate],
) -> dict:
    requirement_stats = []
    for name in request.non_negotiables:
        results = [candidate.constraint_results.get(name, {}) for candidate in candidates]
        passed_count = sum(1 for result in results if result.get("passed"))
        best_result = max(results, key=lambda item: item.get("score", 0.0), default={})
        requirement_stats.append(
            {
                "name": name,
                "passed_count": passed_count,
                "candidate_count": len(candidates),
                "best_score": best_result.get("score"),
                "threshold": best_result.get("threshold"),
                "detail": best_result.get("detail"),
            }
        )

    location_notes: list[str] = []
    if candidates:
        best_hill = max((candidate.traits.hill_fit for candidate in candidates if candidate.traits), default=0.0)
        max_ascent_ft_per_mi = max(
            (candidate.traits.ascent_ft_per_mi for candidate in candidates if candidate.traits),
            default=0.0,
        )
        max_trail_ratio = max(
            ((candidate.traits.trail_ratio or 0.0) for candidate in candidates if candidate.traits),
            default=0.0,
        )
        max_paved_ratio = max(
            ((candidate.traits.paved_ratio or 0.0) for candidate in candidates if candidate.traits),
            default=0.0,
        )
        max_landmarks = max(
            (candidate.traits.landmark_count for candidate in candidates if candidate.traits),
            default=0,
        )
        max_turns_per_mile = max(
            (candidate.traits.turns_per_mile for candidate in candidates if candidate.traits),
            default=0.0,
        )
        min_drift_cap_gap = min(
            (
                candidate.traits.max_distance_from_start_miles_actual
                for candidate in candidates
                if candidate.traits
            ),
            default=0.0,
        )
        repeat_capable_candidates = sum(
            1 for candidate in candidates if candidate.traits and candidate.traits.repeat_count > 1
        )
        best_distance_gap = min(
            (
                abs(candidate.route.distance_mi - request.target_distance_miles)
                for candidate in candidates
            ),
            default=0.0,
        )

        if "Elevation profile" in request.non_negotiables and best_hill < 0.62:
            if request.preferences.hill_preference >= 0.25 and max_ascent_ft_per_mi < 140:
                location_notes.append(
                    "This area appears relatively flat within the current start radius, so the requested climb profile may not exist nearby."
                )
            elif request.preferences.hill_preference <= -0.25 and max_ascent_ft_per_mi > 180:
                location_notes.append(
                    "This area appears hillier than the requested flat profile, so smoother routes may be limited nearby."
                )
        if "Trail quality" in request.non_negotiables and max_trail_ratio < 0.25:
            location_notes.append(
                "Trail coverage looks limited within the current start radius, so a trail-first route may require a different starting area."
            )
        if "Paved surface" in request.non_negotiables and max_paved_ratio < 0.55:
            location_notes.append(
                "Mostly paved footing appears limited here, so the nearby route network may skew more mixed-surface or trail-heavy."
            )
        if "Landmarks" in request.non_negotiables and max_landmarks < 2:
            location_notes.append(
                "There do not appear to be many landmark-type destinations along these nearby loops, so a landmark-forward route may be constrained here."
            )
        if "Low interruptions" in request.non_negotiables and max_turns_per_mile > 6.5:
            location_notes.append(
                "Nearby loops look fairly turn-heavy, which suggests this area may not support the uninterrupted flow you requested."
            )
        if "Stay close to start" in request.non_negotiables and min_drift_cap_gap > request.max_distance_from_start_miles:
            location_notes.append(
                "The current max-distance-from-start cap looks too tight for the requested mileage in this area."
            )
        if "No repeats" in request.non_negotiables and repeat_capable_candidates > 0 and request.preferences.hill_preference >= 0.5:
            location_notes.append(
                "The strongest climb-focused options nearby appear to require repeated segments rather than a single clean route."
            )
        if "Distance accuracy" in request.non_negotiables and best_distance_gap > request.distance_tolerance_miles:
            location_notes.append(
                "ORS could not form a loop within the requested distance tolerance here; a wider tolerance or larger start radius may be necessary."
            )

    near_misses = []
    sorted_candidates = sorted(
        candidates,
        key=lambda candidate: (
            sum(1 for item in (candidate.constraint_results or {}).values() if item.get("passed")),
            candidate.score,
        ),
        reverse=True,
    )
    for candidate in sorted_candidates[:3]:
        failed = [
            name
            for name, result in (candidate.constraint_results or {}).items()
            if not result.get("passed")
        ]
        near_misses.append(
            {
                "distance_miles": round(candidate.route.distance_mi, 2),
                "score": round(candidate.score, 3),
                "failed_requirements": failed,
                "headline": candidate.summary.headline if candidate.summary else "Route candidate",
            }
        )

    return {
        "message": "No routes satisfied every non-negotiable for this area.",
        "non_negotiables": request.non_negotiables,
        "requirements": requirement_stats,
        "location_notes": location_notes,
        "near_misses": near_misses,
    }


def qualifies_nearby(traits: RouteTraits, *, threshold: float = 0.8) -> bool:
    return traits.start_convenience >= threshold


def qualifies_paved(
    traits: RouteTraits,
    *,
    paved_ratio_threshold: float = 0.65,
    surface_fit_threshold: float = 0.62,
) -> bool:
    return (
        traits.paved_ratio is not None
        and traits.paved_ratio >= paved_ratio_threshold
        and traits.surface_fit >= surface_fit_threshold
    )


def qualifies_trail(
    traits: RouteTraits,
    *,
    trail_ratio_threshold: float = 0.4,
    trail_suitability_threshold: float = 0.56,
) -> bool:
    return (
        traits.trail_ratio is not None
        and traits.trail_ratio >= trail_ratio_threshold
        and traits.trail_suitability >= trail_suitability_threshold
    )


def qualifies_flat(
    traits: RouteTraits,
    *,
    climb_ft_per_mi_threshold: float = 90.0,
    hill_fit_floor: float = 0.45,
) -> bool:
    return traits.ascent_ft_per_mi <= climb_ft_per_mi_threshold and traits.hill_fit >= hill_fit_floor


def qualifies_hills(
    traits: RouteTraits,
    *,
    climb_ft_per_mi_threshold: float = 180.0,
    hill_fit_floor: float = 0.58,
) -> bool:
    return traits.ascent_ft_per_mi >= climb_ft_per_mi_threshold and traits.hill_fit >= hill_fit_floor


def qualifies_quiet(traits: RouteTraits, *, quiet_threshold: float = 0.72) -> bool:
    return traits.quiet_fit >= quiet_threshold


def qualifies_loop(traits: RouteTraits, *, simplicity_floor: float = 0.5) -> bool:
    return traits.is_loop and traits.route_simplicity >= simplicity_floor


def derive_route_badges(traits: RouteTraits) -> list[RouteBadge]:
    badges: list[RouteBadge] = []

    if qualifies_loop(traits):
        badges.append(RouteBadge(code="LP", label="Loop", strength=traits.route_simplicity))
    if qualifies_nearby(traits):
        badges.append(RouteBadge(code="NX", label="Nearby", strength=traits.start_convenience))
    if qualifies_paved(traits):
        badges.append(
            RouteBadge(
                code="PV",
                label="Paved",
                strength=((traits.paved_ratio or 0.0) * 0.65) + (traits.surface_fit * 0.35),
            )
        )
    if qualifies_trail(traits):
        badges.append(
            RouteBadge(
                code="TR",
                label="Trail",
                strength=((traits.trail_ratio or 0.0) * 0.65) + (traits.trail_suitability * 0.35),
            )
        )
    if qualifies_flat(traits):
        flat_strength = clamp(1 - (traits.ascent_ft_per_mi / 180.0))
        badges.append(RouteBadge(code="FL", label="Flat", strength=flat_strength))
    if qualifies_hills(traits):
        hill_strength = clamp((traits.ascent_ft_per_mi - 120.0) / 220.0)
        badges.append(RouteBadge(code="HL", label="Hills", strength=hill_strength))
    if qualifies_quiet(traits):
        badges.append(RouteBadge(code="QT", label="Quiet", strength=traits.quiet_fit))

    by_code = {badge.code: badge for badge in badges}
    if "FL" in by_code and "HL" in by_code:
        weaker = "FL" if by_code["FL"].strength < by_code["HL"].strength else "HL"
        badges = [badge for badge in badges if badge.code != weaker]
        by_code = {badge.code: badge for badge in badges}
    if "PV" in by_code and "TR" in by_code:
        weaker = "PV" if by_code["PV"].strength < by_code["TR"].strength else "TR"
        badges = [badge for badge in badges if badge.code != weaker]

    family_order = {
        "LP": 0,
        "NX": 0,
        "PV": 1,
        "TR": 1,
        "FL": 1,
        "HL": 1,
        "QT": 2,
    }
    badges.sort(key=lambda badge: (-badge.strength, family_order.get(badge.code, 9), badge.code))

    selected: list[RouteBadge] = []
    used_families: set[int] = set()
    for badge in badges:
        family = family_order.get(badge.code, 9)
        if len(selected) >= 4:
            break
        if family in used_families and len(selected) >= 3:
            continue
        selected.append(badge)
        used_families.add(family)

    selected.sort(key=lambda badge: (family_order.get(badge.code, 9), -badge.strength, badge.code))
    return selected[:4]


def score_reason_label(name: str, traits: RouteTraits) -> str:
    labels = {
        "distance": "distance fit",
        "start": "start proximity",
        "pavement": "surface consistency",
        "quiet": "quietness",
        "green": "green access",
        "hills": "elevation profile",
        "distance_fit": "distance fit",
        "start_convenience": "start proximity",
        "surface_fit": "surface consistency",
        "hill_fit": "elevation profile",
        "environmental_fit": "environmental fit",
        "route_simplicity": "simple navigation",
        "discovery_fit": "discovery fit",
        "training_fit": "training value",
        "trail_suitability": "trail quality",
        "confidence_fit": "route confidence",
        "landmark_fit": "landmark access",
        "interruption_fit": "low interruptions",
    }
    if name not in {"hills", "hill_fit"}:
        return labels.get(name, name)
    if traits.ascent_ft_per_mi >= 150:
        return "hill profile"
    if traits.ascent_ft_per_mi <= 90:
        return "flat profile"
    return labels["hills"]


def build_strengths(traits: RouteTraits, score_breakdown: dict[str, float]) -> list[str]:
    strengths: list[str] = []
    if score_breakdown.get("distance", 0.0) >= 0.82:
        strengths.append("Hits the requested distance closely.")
    if score_breakdown.get("start", 0.0) >= 0.82:
        strengths.append("Starts close to the requested location.")
    if traits.paved_ratio is not None and traits.paved_ratio >= 0.7:
        strengths.append("Keeps footing mostly paved.")
    elif traits.trail_ratio is not None and traits.trail_ratio >= 0.45:
        strengths.append("Leans into trail-heavy segments.")
    if score_breakdown.get("quiet", 0.0) >= 0.72:
        strengths.append("Stays relatively quiet for the area.")
    if score_breakdown.get("green", 0.0) >= 0.7:
        strengths.append("Includes greener sections.")
    if traits.landmark_count >= 2:
        strengths.append("Passes multiple landmark-style destinations.")
    if traits.turn_density_fit >= 0.74:
        strengths.append("Keeps route flow relatively uninterrupted.")
    if traits.max_distance_from_start_miles_actual <= 0.6:
        strengths.append("Stays relatively close to the requested start area.")
    if traits.ascent_ft_per_mi >= 180 and score_breakdown.get("hills", 0.0) >= 0.58:
        strengths.append("Delivers a stronger climbing profile.")
    if traits.pattern_type == "out_and_back" and traits.outbound_distance_miles is not None:
        strengths.append(f"Uses a direct out-and-back shape with a {traits.outbound_distance_miles:.2f} mi outbound leg.")
    if traits.pattern_type == "hill_repeat" and traits.repeat_count > 1:
        strengths.append(f"Turns the strongest nearby hill into a {traits.repeat_count}x repeat workout.")
    elif traits.ascent_ft_per_mi <= 90 and score_breakdown.get("hills", 0.0) >= 0.45:
        strengths.append("Keeps the elevation profile relatively flat.")
    if traits.is_loop:
        strengths.append("Returns to the start cleanly as a loop.")
    return strengths


def build_tradeoffs(traits: RouteTraits, score_breakdown: dict[str, float]) -> list[str]:
    tradeoffs: list[str] = []
    if score_breakdown.get("distance", 1.0) < 0.72:
        tradeoffs.append("Distance fit is looser than the strongest candidates.")
    if score_breakdown.get("pavement", 1.0) < 0.5:
        tradeoffs.append("Surface mix may be less consistent than a pavement-first run.")
    if score_breakdown.get("quiet", 1.0) < 0.45:
        tradeoffs.append("May feel busier or noisier in places.")
    if score_breakdown.get("green", 1.0) < 0.45:
        tradeoffs.append("Has less green exposure than a more scenic option.")
    if traits.landmark_count == 0:
        tradeoffs.append("Does not pass many obvious landmark destinations.")
    if traits.turns_per_mile > 6.0:
        tradeoffs.append("May feel more stop-start or turn-heavy than ideal.")
    if traits.max_distance_from_start_miles_actual > 2.0:
        tradeoffs.append("Travels farther from the starting point than tighter nearby options.")
    if traits.pattern_type == "hill_repeat" and traits.repeat_count > 3:
        tradeoffs.append("Leans into repeated climbing rather than route variety.")
    if not traits.is_loop:
        tradeoffs.append("Loop closure is weaker than ideal.")
    return tradeoffs


def build_candidate_summary(candidate: LoopCandidate) -> RouteSummary:
    traits = candidate.traits
    if traits is None:
        raise RouteError("Cannot summarize a candidate before traits are derived.")

    ranking_source = candidate.ranking_breakdown or candidate.score_breakdown
    ranked_reasons = sorted(ranking_source.items(), key=lambda item: item[1], reverse=True)
    top_reasons = [
        score_reason_label(name, traits)
        for name, value in ranked_reasons
        if value >= 0.05
    ][:3]
    if not top_reasons:
        top_reasons = [score_reason_label(ranked_reasons[0][0], traits)]

    strengths = build_strengths(traits, candidate.score_breakdown)
    tradeoffs = build_tradeoffs(traits, candidate.score_breakdown)

    if traits.pattern_type == "hill_repeat":
        if "hill profile" in top_reasons:
            headline = "Repeat-based hill workout route with strong climb value."
        else:
            headline = "Repeat-based route built around the strongest nearby climbing segment."
    elif traits.pattern_type == "out_and_back":
        if "quietness" in top_reasons:
            headline = "Direct out-and-back route with calmer road and path choices."
        elif "green access" in top_reasons:
            headline = "Direct out-and-back route with greener exposure."
        else:
            headline = "Direct out-and-back route with a strong overall fit."
    elif "hill profile" in top_reasons:
        headline = "Climbing-focused loop with strong training value."
    elif "flat profile" in top_reasons:
        headline = "Flatter loop with a smoother elevation profile."
    elif "surface consistency" in top_reasons:
        headline = "Footing-forward loop with more consistent surface quality."
    elif "quietness" in top_reasons:
        headline = "Quieter loop that should feel calmer on the run."
    elif "green access" in top_reasons:
        headline = "Greener loop with more scenic exposure."
    else:
        headline = "Balanced loop with a strong overall fit."

    return RouteSummary(
        headline=headline,
        strengths=strengths[:4],
        tradeoffs=tradeoffs[:3],
        top_reasons=top_reasons,
    )


def fetch_directions_geojson(
    *,
    api_key: str,
    profile: str,
    coords: list[list[float]],
    preference: str = "recommended",
    options: dict | None = None,
    extra_info: list[str] | None = None,
    noise_threshold_m: float = 2.0,
    timeout: int = 60,
) -> RouteResult:
    import requests

    validate_coords(coords, minimum=1)
    if not api_key:
        raise RouteError("Missing ORS API key.")

    url = ORS_URL_TEMPLATE.format(profile=profile)
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json, application/geo+json",
    }
    payload: dict[str, object] = {
        "coordinates": coords,
        "elevation": True,
        "instructions": True,
        "preference": preference,
    }
    if options:
        payload["options"] = options
    if extra_info:
        payload["extra_info"] = extra_info

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=timeout)
        response.raise_for_status()
    except requests.HTTPError as exc:
        detail = ""
        try:
            body = exc.response.json()
            detail = body.get("error") or body.get("message") or json.dumps(body)
        except Exception:
            detail = exc.response.text if exc.response is not None else str(exc)
        raise RouteError(f"ORS request failed: {detail}") from exc
    except requests.RequestException as exc:
        raise RouteError(f"ORS request failed: {exc}") from exc

    data = response.json()
    features = data.get("features") or []
    if not features:
        raise RouteError("No route returned by ORS.")

    feature = features[0]
    route_coords = feature["geometry"]["coordinates"]
    props = feature.get("properties", {})
    summary = props.get("summary", {})
    distance_m = float(summary.get("distance", 0.0))
    duration_s = float(summary.get("duration", 0.0))
    ascent_m, descent_m, min_ele_m, max_ele_m = compute_elevation_stats(
        route_coords,
        noise_threshold_m=noise_threshold_m,
    )

    return RouteResult(
        route_feature=feature,
        raw_geojson=data,
        distance_m=distance_m,
        duration_s=duration_s,
        ascent_m=ascent_m,
        descent_m=descent_m,
        min_ele_m=min_ele_m,
        max_ele_m=max_ele_m,
        extras=props.get("extras", {}),
    )


def fetch_route(
    *,
    api_key: str,
    profile: str,
    coords: list[list[float]],
    noise_threshold_m: float = 2.0,
    timeout: int = 60,
) -> RouteResult:
    validate_coords(coords, minimum=2)
    return fetch_directions_geojson(
        api_key=api_key,
        profile=profile,
        coords=coords,
        noise_threshold_m=noise_threshold_m,
        timeout=timeout,
    )


def route_coordinates(route: RouteResult) -> list[list[float]]:
    return route.route_feature.get("geometry", {}).get("coordinates", [])


def reverse_route_coords(coords: list[list[float]]) -> list[list[float]]:
    return [list(coord) for coord in reversed(coords)]


def max_distance_from_start_miles(
    *,
    coords: list[list[float]],
    center: list[float],
) -> float:
    if not coords:
        return 0.0
    max_m = max(haversine_distance_m(center, coord) for coord in coords)
    return max_m / MILES_TO_METERS


def summarize_extra_node(summary_items: list[dict]) -> list[dict]:
    collapsed: dict[int, float] = {}
    for item in summary_items:
        value = int(item.get("value", -1))
        collapsed[value] = collapsed.get(value, 0.0) + float(item.get("distance", 0.0))
    return [
        {"value": value, "distance": distance}
        for value, distance in sorted(collapsed.items(), key=lambda item: item[0])
    ]


def merge_extras(*extras_list: dict) -> dict:
    merged: dict[str, dict] = {}
    for extras in extras_list:
        for key, node in (extras or {}).items():
            summary = (node or {}).get("summary") or []
            merged.setdefault(key, {"summary": []})
            merged[key]["summary"].extend(
                {"value": item.get("value"), "distance": float(item.get("distance", 0.0))}
                for item in summary
            )
    for key, node in merged.items():
        node["summary"] = summarize_extra_node(node["summary"])
    return merged


def combine_poi_summaries(*summaries: dict | None) -> dict | None:
    available = [summary for summary in summaries if summary]
    if not available:
        return None
    combined = {
        "total_count": 0,
        "landmark_count": 0,
        "park_count": 0,
        "water_count": 0,
    }
    for summary in available:
        for key in combined:
            combined[key] += int(summary.get(key, 0) or 0)
    return combined


def build_feature_collection_from_coords(coords: list[list[float]], *, extras: dict, distance_m: float, duration_s: float) -> tuple[dict, dict]:
    feature = {
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": coords,
        },
        "properties": {
            "summary": {
                "distance": distance_m,
                "duration": duration_s,
            },
            "extras": extras,
        },
    }
    geojson = {
        "type": "FeatureCollection",
        "features": [feature],
    }
    return feature, geojson


def combine_route_results(
    *,
    routes: list[RouteResult],
    coords: list[list[float]] | None = None,
    poi_summary: dict | None = None,
) -> RouteResult:
    merged_coords: list[list[float]] = []
    if coords is not None:
        merged_coords = coords
    else:
        for route in routes:
            route_coords = route_coordinates(route)
            if not merged_coords:
                merged_coords.extend(route_coords)
            else:
                merged_coords.extend(route_coords[1:])

    distance_m = sum(route.distance_m for route in routes)
    duration_s = sum(route.duration_s for route in routes)
    ascent_m = sum(route.ascent_m for route in routes)
    descent_m = sum(route.descent_m for route in routes)
    min_ele_candidates = [route.min_ele_m for route in routes if route.min_ele_m is not None]
    max_ele_candidates = [route.max_ele_m for route in routes if route.max_ele_m is not None]
    extras = merge_extras(*(route.extras for route in routes))
    feature, geojson = build_feature_collection_from_coords(
        merged_coords,
        extras=extras,
        distance_m=distance_m,
        duration_s=duration_s,
    )
    return RouteResult(
        route_feature=feature,
        raw_geojson=geojson,
        distance_m=distance_m,
        duration_s=duration_s,
        ascent_m=ascent_m,
        descent_m=descent_m,
        min_ele_m=min(min_ele_candidates) if min_ele_candidates else None,
        max_ele_m=max(max_ele_candidates) if max_ele_candidates else None,
        extras=extras,
        poi_summary=poi_summary if poi_summary is not None else combine_poi_summaries(*(route.poi_summary for route in routes)),
    )


def enrich_route_pois_if_needed(
    *,
    api_key: str,
    route: RouteResult,
    enrich_pois: bool,
) -> None:
    if not enrich_pois:
        return
    route.poi_summary = fetch_route_poi_summary(
        api_key=api_key,
        route_feature=route.route_feature,
    )


def planning_request_from_runtime(
    *,
    center: list[float],
    profile: str,
    target_distance_m: float,
    distance_tolerance_miles: float,
    start_radius_m: float,
    max_distance_from_start_miles: float,
    max_candidates: int,
    seed_count: int,
    start_limit: int,
    seed_offset: int,
    route_pattern_preference: str,
    repeat_preference: str,
    focus_feature: str | None,
    top_priority: str,
    secondary_priority: str | None,
    non_negotiables: list[str],
    preferences: LoopPreferenceProfile,
) -> PlanningRequest:
    return PlanningRequest(
        center=center,
        profile=profile,
        target_distance_miles=target_distance_m / MILES_TO_METERS,
        distance_tolerance_miles=distance_tolerance_miles,
        start_radius_miles=start_radius_m / MILES_TO_METERS,
        max_distance_from_start_miles=max_distance_from_start_miles,
        max_candidates=max_candidates,
        seed_count=seed_count,
        start_limit=start_limit,
        seed_offset=seed_offset,
        route_pattern_preference=route_pattern_preference,
        repeat_preference=repeat_preference,
        focus_feature=focus_feature,
        top_priority=top_priority,
        secondary_priority=secondary_priority,
        non_negotiables=non_negotiables,
        preferences=preferences,
        design_brief="",
    )


def route_repeat_penalty(
    *,
    pattern_type: str,
    repeat_preference: str,
    repeat_count: int,
) -> float:
    if pattern_type != "hill_repeat":
        if repeat_preference == "none" and repeat_count > 1:
            return 0.04
        return 0.0
    if repeat_preference == "preferred":
        return 0.0
    if repeat_preference == "as_needed":
        return 0.03
    return 0.08


def route_weightings(preferences: LoopPreferenceProfile) -> dict[str, float]:
    return {
        "green": round(0.25 + preferences.green_preference * 0.75, 2),
        "quiet": round(0.25 + preferences.quiet_preference * 0.75, 2),
    }


def route_request_options(preferences: LoopPreferenceProfile) -> dict:
    return {
        "avoid_features": ["ferries", "fords"],
        "profile_params": {"weightings": route_weightings(preferences)},
    }


def route_extra_info() -> list[str]:
    return ["surface", "waytype", "green", "noise", "suitability"]


def should_enrich_pois(request: PlanningRequest) -> bool:
    return landmark_sensitive_request(
        top_priority=request.top_priority,
        secondary_priority=request.secondary_priority,
        non_negotiables=request.non_negotiables,
    )


def build_candidate(
    *,
    request: PlanningRequest,
    route: RouteResult,
    start_coord: list[float],
    start_offset_m: float,
    seed: int,
    pattern_type: str,
    pattern_metadata: dict | None = None,
) -> LoopCandidate:
    _, score_breakdown = score_loop_candidate(
        route=route,
        target_distance_m=request.target_distance_m,
        start_offset_m=start_offset_m,
        max_start_offset_m=request.start_radius_m,
        preferences=request.preferences,
    )
    candidate = LoopCandidate(
        start_coord=start_coord,
        start_offset_m=start_offset_m,
        seed=seed,
        route=route,
        score=0.0,
        score_breakdown=score_breakdown,
        pattern_type=pattern_type,
        pattern_metadata=pattern_metadata or {},
    )
    traits = derive_route_traits(
        route=route,
        score_breakdown=score_breakdown,
        center=request.center,
        start_offset_m=start_offset_m,
        start_radius_m=request.start_radius_m,
        pattern_type=pattern_type,
        pattern_metadata=candidate.pattern_metadata,
    )
    candidate.traits = traits
    candidate.badges = derive_route_badges(traits)
    score, ranking_breakdown = aggregate_candidate_score(
        candidate=candidate,
        request=request,
        traits=traits,
        score_breakdown=score_breakdown,
        top_priority=request.top_priority,
        secondary_priority=request.secondary_priority,
    )
    candidate.score = score
    candidate.ranking_breakdown = ranking_breakdown
    candidate.summary = build_candidate_summary(candidate)
    return candidate


def generate_loop_pattern_candidates(
    *,
    api_key: str,
    request: PlanningRequest,
    noise_threshold_m: float = 2.0,
) -> tuple[list[LoopCandidate], RouteError | None]:
    candidates: list[LoopCandidate] = []
    last_error: RouteError | None = None
    starts = generate_candidate_starts(request.center, request.start_radius_m)
    starts = starts[: request.start_limit]
    enrich_pois = should_enrich_pois(request)
    options = route_request_options(request.preferences)
    extra_info = route_extra_info()

    for index, (start_coord, start_offset_m) in enumerate(starts):
        for seed in range(1, request.seed_count + 1):
            if len(candidates) >= request.max_candidates:
                break
            request_options = {
                **options,
                "round_trip": {
                    "length": int(request.target_distance_m),
                    "points": 4 if request.target_distance_m <= 12_000 else 5,
                    "seed": request.seed_offset + index * 10 + seed,
                },
            }
            try:
                route = fetch_directions_geojson(
                    api_key=api_key,
                    profile=request.profile,
                    coords=[start_coord],
                    preference="recommended",
                    options=request_options,
                    extra_info=extra_info,
                    noise_threshold_m=noise_threshold_m,
                )
            except RouteError as exc:
                last_error = exc
                continue

            enrich_route_pois_if_needed(api_key=api_key, route=route, enrich_pois=enrich_pois)
            candidate = build_candidate(
                request=request,
                route=route,
                start_coord=start_coord,
                start_offset_m=start_offset_m,
                seed=request.seed_offset + index * 10 + seed,
                pattern_type="loop",
                pattern_metadata={
                    "repeat_count": 1,
                },
            )
            candidates.append(candidate)
    return candidates, last_error


def radial_anchor_coords(
    *,
    center: list[float],
    distances_m: list[float],
    bearings: tuple[int, ...] = (0, 45, 90, 135, 180, 225, 270, 315),
) -> list[list[float]]:
    anchors: list[list[float]] = []
    seen: set[tuple[float, float]] = set()
    for distance_m in distances_m:
        for bearing in bearings:
            coord = geodesic_offset(center, distance_m, bearing)
            key = (round(coord[0], 6), round(coord[1], 6))
            if key not in seen:
                anchors.append(coord)
                seen.add(key)
    return anchors


def compose_out_and_back_route(base_route: RouteResult) -> RouteResult:
    outbound_coords = route_coordinates(base_route)
    if len(outbound_coords) < 2:
        raise RouteError("Out-and-back composition requires at least two coordinates.")
    return_coords = reverse_route_coords(outbound_coords)[1:]
    combined_coords = outbound_coords + return_coords
    outbound_poi = base_route.poi_summary
    return combine_route_results(
        routes=[base_route, base_route],
        coords=combined_coords,
        poi_summary=outbound_poi,
    )


def generate_out_and_back_candidates(
    *,
    api_key: str,
    request: PlanningRequest,
    noise_threshold_m: float = 2.0,
) -> tuple[list[LoopCandidate], RouteError | None]:
    candidates: list[LoopCandidate] = []
    last_error: RouteError | None = None
    enrich_pois = should_enrich_pois(request)
    half_target_m = min(request.target_distance_m / 2.0, request.max_distance_from_start_m)
    base_distances = sorted(
        {
            max(min(half_target_m * 0.8, request.max_distance_from_start_m), 0.25 * MILES_TO_METERS),
            max(min(half_target_m, request.max_distance_from_start_m), 0.25 * MILES_TO_METERS),
            max(min(half_target_m * 1.1, request.max_distance_from_start_m), 0.25 * MILES_TO_METERS),
        }
    )
    anchors = radial_anchor_coords(center=request.center, distances_m=base_distances)
    extra_info = route_extra_info()

    for index, anchor in enumerate(anchors[: request.max_candidates * 2]):
        if len(candidates) >= request.max_candidates:
            break
        try:
            outbound = fetch_directions_geojson(
                api_key=api_key,
                profile=request.profile,
                coords=[request.center, anchor],
                preference="recommended",
                options=route_request_options(request.preferences),
                extra_info=extra_info,
                noise_threshold_m=noise_threshold_m,
            )
        except RouteError as exc:
            last_error = exc
            continue

        enrich_route_pois_if_needed(api_key=api_key, route=outbound, enrich_pois=enrich_pois)
        route = compose_out_and_back_route(outbound)
        candidate = build_candidate(
            request=request,
            route=route,
            start_coord=request.center,
            start_offset_m=0.0,
            seed=request.seed_offset + 1000 + index,
            pattern_type="out_and_back",
            pattern_metadata={
                "repeat_count": 1,
                "outbound_distance_miles": outbound.distance_mi,
                "anchor_distance_miles": max_distance_from_start_miles(
                    coords=route_coordinates(outbound),
                    center=request.center,
                ),
                "synthetic_composition": True,
            },
        )
        candidates.append(candidate)
    return candidates, last_error


def compose_hill_repeat_route(base_route: RouteResult, repeat_count: int) -> RouteResult:
    outbound_coords = route_coordinates(base_route)
    if len(outbound_coords) < 2:
        raise RouteError("Hill repeat composition requires at least two coordinates.")

    there_back_coords = outbound_coords + reverse_route_coords(outbound_coords)[1:]
    combined_coords: list[list[float]] = []
    for index in range(repeat_count):
        if index == 0:
            combined_coords.extend(there_back_coords)
        else:
            combined_coords.extend(there_back_coords[1:])

    lap_distance_m = base_route.distance_m * 2
    lap_duration_s = base_route.duration_s * 2
    lap_ascent_m = base_route.ascent_m + base_route.descent_m
    lap_descent_m = base_route.descent_m + base_route.ascent_m
    extras = merge_extras(base_route.extras, base_route.extras)
    feature, geojson = build_feature_collection_from_coords(
        combined_coords,
        extras=extras,
        distance_m=lap_distance_m * repeat_count,
        duration_s=lap_duration_s * repeat_count,
    )
    return RouteResult(
        route_feature=feature,
        raw_geojson=geojson,
        distance_m=lap_distance_m * repeat_count,
        duration_s=lap_duration_s * repeat_count,
        ascent_m=lap_ascent_m * repeat_count,
        descent_m=lap_descent_m * repeat_count,
        min_ele_m=base_route.min_ele_m,
        max_ele_m=base_route.max_ele_m,
        extras=extras,
        poi_summary=base_route.poi_summary,
    )


def choose_repeat_count(
    *,
    target_distance_miles: float,
    tolerance_miles: float,
    repeat_segment_distance_miles: float,
    repeat_preference: str,
) -> int | None:
    minimum = 1
    maximum = 4 if repeat_preference == "as_needed" else 6
    best_count: int | None = None
    best_gap = float("inf")
    for count in range(minimum, maximum + 1):
        gap = abs((repeat_segment_distance_miles * count) - target_distance_miles)
        if gap < best_gap:
            best_gap = gap
            best_count = count
    if best_count is None:
        return None
    if best_gap > tolerance_miles:
        return None
    return best_count


def generate_hill_repeat_candidates(
    *,
    api_key: str,
    request: PlanningRequest,
    noise_threshold_m: float = 2.0,
) -> tuple[list[LoopCandidate], RouteError | None]:
    if request.repeat_preference == "none":
        return [], None

    candidates: list[LoopCandidate] = []
    last_error: RouteError | None = None
    enrich_pois = should_enrich_pois(request)
    probe_distances = sorted(
        {
            max(request.max_distance_from_start_m * 0.3, 0.2 * MILES_TO_METERS),
            max(request.max_distance_from_start_m * 0.5, 0.3 * MILES_TO_METERS),
            max(request.max_distance_from_start_m * 0.75, 0.4 * MILES_TO_METERS),
        }
    )
    anchors = radial_anchor_coords(center=request.center, distances_m=probe_distances)
    extra_info = route_extra_info()
    probes: list[tuple[float, RouteResult, dict]] = []

    for index, anchor in enumerate(anchors[:18]):
        try:
            probe = fetch_directions_geojson(
                api_key=api_key,
                profile=request.profile,
                coords=[request.center, anchor],
                preference="recommended",
                options=route_request_options(request.preferences),
                extra_info=extra_info,
                noise_threshold_m=noise_threshold_m,
            )
        except RouteError as exc:
            last_error = exc
            continue

        enrich_route_pois_if_needed(api_key=api_key, route=probe, enrich_pois=enrich_pois)
        ft_per_mile = meters_to_feet(probe.ascent_m) / max(probe.distance_mi, 0.1)
        anchor_distance_miles = max_distance_from_start_miles(
            coords=route_coordinates(probe),
            center=request.center,
        )
        climb_score = ft_per_mile * probe.distance_mi
        probes.append(
            (
                climb_score,
                probe,
                {
                    "anchor_distance_miles": anchor_distance_miles,
                    "repeat_segment_distance_miles": probe.distance_mi * 2,
                    "repeat_segment_climb_feet": meters_to_feet(probe.ascent_m),
                    "repeat_segment_ft_per_mile": ft_per_mile,
                    "probe_index": index,
                },
            )
        )

    probes.sort(key=lambda item: item[0], reverse=True)

    for offset, (_, probe, metadata) in enumerate(probes[: max(request.max_candidates, 3)]):
        repeat_count = choose_repeat_count(
            target_distance_miles=request.target_distance_miles,
            tolerance_miles=request.distance_tolerance_miles,
            repeat_segment_distance_miles=metadata["repeat_segment_distance_miles"],
            repeat_preference=request.repeat_preference,
        )
        if repeat_count is None:
            continue

        route = compose_hill_repeat_route(probe, repeat_count)
        candidate = build_candidate(
            request=request,
            route=route,
            start_coord=request.center,
            start_offset_m=0.0,
            seed=request.seed_offset + 2000 + offset,
            pattern_type="hill_repeat",
            pattern_metadata={
                **metadata,
                "repeat_count": repeat_count,
                "synthetic_composition": True,
            },
        )
        candidates.append(candidate)
        if len(candidates) >= request.max_candidates:
            break
    return candidates, last_error


def finalize_pattern_candidates(
    *,
    request: PlanningRequest,
    candidates: list[LoopCandidate],
    last_error: RouteError | None = None,
) -> list[LoopCandidate]:
    if not candidates:
        if last_error is not None:
            raise last_error
        raise RouteError("No viable routes were returned for that area and preference set.")

    drift_matching = [
        candidate
        for candidate in candidates
        if candidate.traits
        and candidate.traits.max_distance_from_start_miles_actual <= request.max_distance_from_start_miles
    ]
    if not drift_matching:
        drift_request = PlanningRequest(
            **{**request.__dict__, "non_negotiables": list(dict.fromkeys(request.non_negotiables + ["Stay close to start"]))}
        )
        for candidate in candidates:
            candidate.constraint_results = evaluate_candidate_constraints(
                candidate=candidate,
                request=drift_request,
            )
        analysis = build_feasibility_failure_analysis(request=drift_request, candidates=candidates)
        raise RouteFeasibilityError(
            "No routes satisfied the current max-distance-from-start limit.",
            failure_analysis=analysis,
        )

    candidates = drift_matching

    if request.repeat_preference == "as_needed":
        nonrepeat_candidates = [candidate for candidate in candidates if candidate.pattern_type != "hill_repeat"]
        hill_repeat_candidates = [candidate for candidate in candidates if candidate.pattern_type == "hill_repeat"]
        if nonrepeat_candidates and hill_repeat_candidates:
            best_nonrepeat_hill = max(candidate.traits.hill_fit for candidate in nonrepeat_candidates if candidate.traits)
            filtered: list[LoopCandidate] = []
            for candidate in candidates:
                if candidate.pattern_type != "hill_repeat":
                    filtered.append(candidate)
                    continue
                if candidate.traits and candidate.traits.hill_fit >= best_nonrepeat_hill + 0.05:
                    filtered.append(candidate)
            candidates = filtered or nonrepeat_candidates

    candidates.sort(key=lambda candidate: candidate.score, reverse=True)

    if request.non_negotiables:
        for candidate in candidates:
            candidate.constraint_results = evaluate_candidate_constraints(
                candidate=candidate,
                request=request,
            )
        matching_candidates = [
            candidate
            for candidate in candidates
            if all(result.get("passed") for result in (candidate.constraint_results or {}).values())
        ]
        if matching_candidates:
            return matching_candidates
        analysis = build_feasibility_failure_analysis(request=request, candidates=candidates)
        if (
            request.repeat_preference == "none"
            and request.focus_feature == "climb"
            and "Elevation profile" in {request.top_priority, request.secondary_priority}
        ):
            analysis.setdefault("location_notes", []).append(
                "The requested climb may require repeated segments or a different starting area because repeats are currently disallowed."
            )
        raise RouteFeasibilityError(
            "No routes satisfied every non-negotiable.",
            failure_analysis=analysis,
        )

    return candidates


def build_route_candidates(
    *,
    api_key: str,
    request: PlanningRequest,
    noise_threshold_m: float = 2.0,
) -> list[LoopCandidate]:
    if request.profile not in {"foot-walking", "foot-hiking"}:
        raise RouteError("Route generation currently supports foot-walking and foot-hiking.")
    if request.seed_count < 1:
        raise RouteError("seed_count must be at least 1.")

    all_candidates: list[LoopCandidate] = []
    last_error: RouteError | None = None

    if request.route_pattern_preference in {"loop", "either"}:
        loop_candidates, loop_error = generate_loop_pattern_candidates(
            api_key=api_key,
            request=request,
            noise_threshold_m=noise_threshold_m,
        )
        all_candidates.extend(loop_candidates)
        last_error = loop_error or last_error

    if request.route_pattern_preference in {"out_and_back", "either"}:
        out_back_candidates, out_back_error = generate_out_and_back_candidates(
            api_key=api_key,
            request=request,
            noise_threshold_m=noise_threshold_m,
        )
        all_candidates.extend(out_back_candidates)
        last_error = out_back_error or last_error

    if (
        request.repeat_preference in {"as_needed", "preferred"}
        and (
            request.focus_feature == "climb"
            or request.top_priority == "Elevation profile"
            or request.secondary_priority == "Elevation profile"
        )
    ):
        hill_repeat_candidates, hill_repeat_error = generate_hill_repeat_candidates(
            api_key=api_key,
            request=request,
            noise_threshold_m=noise_threshold_m,
        )
        all_candidates.extend(hill_repeat_candidates)
        last_error = hill_repeat_error or last_error

    return finalize_pattern_candidates(
        request=request,
        candidates=all_candidates[: max(request.max_candidates * 3, len(all_candidates))],
        last_error=last_error,
    )[: request.max_candidates]


def build_loop_candidates(
    *,
    api_key: str,
    center: list[float],
    start_radius_m: float,
    target_distance_m: float,
    profile: str,
    preferences: LoopPreferenceProfile,
    top_priority: str = "Distance accuracy",
    secondary_priority: str | None = "Closer start",
    distance_tolerance_miles: float = 0.5,
    non_negotiables: list[str] | None = None,
    noise_threshold_m: float = 2.0,
    max_candidates: int = 12,
    seed_count: int = 4,
    start_limit: int | None = None,
    seed_offset: int = 0,
    route_pattern_preference: str = "loop",
    repeat_preference: str = "none",
    max_distance_from_start_miles: float | None = None,
    focus_feature: str | None = None,
) -> list[LoopCandidate]:
    request = planning_request_from_runtime(
        center=center,
        profile=profile,
        target_distance_m=target_distance_m,
        distance_tolerance_miles=distance_tolerance_miles,
        start_radius_m=start_radius_m,
        max_distance_from_start_miles=(
            max_distance_from_start_miles
            if max_distance_from_start_miles is not None
            else default_max_distance_from_start_miles(
                route_pattern_preference=route_pattern_preference,
                target_distance_miles=target_distance_m / MILES_TO_METERS,
                start_radius_miles=start_radius_m / MILES_TO_METERS,
            )
        ),
        max_candidates=max_candidates,
        seed_count=seed_count,
        start_limit=start_limit or max_candidates,
        seed_offset=seed_offset,
        route_pattern_preference=route_pattern_preference,
        repeat_preference=repeat_preference,
        focus_feature=focus_feature,
        top_priority=top_priority,
        secondary_priority=secondary_priority,
        non_negotiables=non_negotiables or [],
        preferences=preferences,
    )
    return build_route_candidates(
        api_key=api_key,
        request=request,
        noise_threshold_m=noise_threshold_m,
    )


def write_geojson(route_geojson: dict, output_path: Path) -> None:
    output_path.write_text(json.dumps(route_geojson, indent=2), encoding="utf-8")
