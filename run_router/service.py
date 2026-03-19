from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ORS_URL_TEMPLATE = "https://api.openrouteservice.org/v2/directions/{profile}/geojson"
EARTH_RADIUS_M = 6_371_000
MILES_TO_METERS = 1609.344

PAVED_SURFACE_IDS = {1, 3, 4, 14}
TRAIL_WAYTYPE_IDS = {4, 5, 7}


class RouteError(Exception):
    """Raised when the route request or input is invalid."""


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
    start_radius_miles: float
    max_candidates: int
    seed_count: int
    start_limit: int
    preferences: LoopPreferenceProfile
    design_brief: str

    @property
    def target_distance_m(self) -> float:
        return miles_to_meters(self.target_distance_miles)

    @property
    def start_radius_m(self) -> float:
        return miles_to_meters(self.start_radius_miles)


@dataclass
class LoopCandidate:
    start_coord: list[float]
    start_offset_m: float
    seed: int
    route: RouteResult
    score: float
    score_breakdown: dict[str, float]
    traits: "RouteTraits | None" = None
    badges: list["RouteBadge"] | None = None


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


def parse_planning_request(
    data: dict,
    *,
    profile_default: str = "foot-walking",
    target_distance_default: float = 6.0,
    start_radius_default: float = 1.5,
    max_candidates_default: int = 3,
    seed_count_default: int = 1,
    start_limit_default: int = 3,
    pavement_default: float = 0.8,
    quiet_default: float = 0.8,
    green_default: float = 0.7,
    hill_default: float = 0.0,
) -> PlanningRequest:
    return PlanningRequest(
        center=parse_coord(first_value(data, "center_coord", "center", default="")),
        profile=str(first_value(data, "profile", default=profile_default)),
        target_distance_miles=parse_positive_float(
            first_value(
                data,
                "target_distance_miles",
                "miles",
                default=target_distance_default,
            ),
            name="Target distance",
            minimum=0.1,
        ),
        start_radius_miles=parse_positive_float(
            first_value(
                data,
                "start_radius_miles",
                "radius",
                default=start_radius_default,
            ),
            name="Start radius",
            minimum=0.0,
        ),
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
        preferences=parse_preferences(
            data,
            pavement_default=pavement_default,
            quiet_default=quiet_default,
            green_default=green_default,
            hill_default=hill_default,
        ),
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
    start_offset_m: float,
    start_radius_m: float,
) -> RouteTraits:
    extras = route.extras
    paved_ratio = ratio_for_values(extras, "surface", PAVED_SURFACE_IDS)
    trail_ratio = ratio_for_values(extras, "waytype", TRAIL_WAYTYPE_IDS)
    average_noise = average_extra_score(extras, "noise")
    average_green = average_extra_score(extras, "green")

    ascent_ft_per_mi = 0.0
    if route.distance_mi > 0:
        ascent_ft_per_mi = meters_to_feet(route.ascent_m) / route.distance_mi

    surface_fit = score_breakdown.get("pavement", 0.5)
    quiet_fit = score_breakdown.get("quiet", 0.5)
    green_fit = score_breakdown.get("green", 0.5)
    hill_fit = score_breakdown.get("hills", 0.5)
    distance_fit = score_breakdown.get("distance", 0.5)
    start_convenience = score_breakdown.get("start", 0.5)

    route_simplicity = clamp((start_convenience * 0.55) + ((1 - trail_ratio) if trail_ratio is not None else 0.5) * 0.45)
    discovery_fit = clamp((green_fit * 0.65) + (quiet_fit * 0.35))
    training_fit = clamp((distance_fit * 0.4) + (hill_fit * 0.35) + (surface_fit * 0.25))
    trail_suitability = clamp((((trail_ratio or 0.0) * 0.55) + ((1 - surface_fit) * 0.25) + (hill_fit * 0.2)))

    coords = route.route_feature.get("geometry", {}).get("coordinates", [])
    is_loop = False
    if len(coords) >= 2:
        is_loop = haversine_distance_m(coords[0], coords[-1]) <= max(150.0, start_radius_m * 0.5)

    return RouteTraits(
        paved_ratio=paved_ratio,
        trail_ratio=trail_ratio,
        average_noise=average_noise,
        average_green=average_green,
        ascent_ft_per_mi=ascent_ft_per_mi,
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


def build_loop_candidates(
    *,
    api_key: str,
    center: list[float],
    start_radius_m: float,
    target_distance_m: float,
    profile: str,
    preferences: LoopPreferenceProfile,
    noise_threshold_m: float = 2.0,
    max_candidates: int = 12,
    seed_count: int = 4,
    start_limit: int | None = None,
) -> list[LoopCandidate]:
    if profile not in {"foot-walking", "foot-hiking"}:
        raise RouteError("Loop generation currently supports foot-walking and foot-hiking.")
    if seed_count < 1:
        raise RouteError("seed_count must be at least 1.")

    weightings = {
        "green": round(0.25 + preferences.green_preference * 0.75, 2),
        "quiet": round(0.25 + preferences.quiet_preference * 0.75, 2),
    }
    options = {
        "avoid_features": ["ferries", "fords"],
        "profile_params": {"weightings": weightings},
    }
    extra_info = ["surface", "waytype", "green", "noise", "suitability"]

    candidates: list[LoopCandidate] = []
    last_error: RouteError | None = None
    starts = generate_candidate_starts(center, start_radius_m)
    if start_limit is not None:
        starts = starts[:start_limit]

    for index, (start_coord, start_offset_m) in enumerate(starts):
        for seed in range(1, seed_count + 1):
            if len(candidates) >= max_candidates:
                break

            request_options = {
                **options,
                "round_trip": {
                    "length": int(target_distance_m),
                    "points": 4 if target_distance_m <= 12_000 else 5,
                    "seed": index * 10 + seed,
                },
            }
            try:
                route = fetch_directions_geojson(
                    api_key=api_key,
                    profile=profile,
                    coords=[start_coord],
                    preference="recommended",
                    options=request_options,
                    extra_info=extra_info,
                    noise_threshold_m=noise_threshold_m,
                )
            except RouteError as exc:
                last_error = exc
                continue

            score, score_breakdown = score_loop_candidate(
                route=route,
                target_distance_m=target_distance_m,
                start_offset_m=start_offset_m,
                max_start_offset_m=start_radius_m,
                preferences=preferences,
            )
            traits = derive_route_traits(
                route=route,
                score_breakdown=score_breakdown,
                start_offset_m=start_offset_m,
                start_radius_m=start_radius_m,
            )
            badges = derive_route_badges(traits)
            candidates.append(
                LoopCandidate(
                    start_coord=start_coord,
                    start_offset_m=start_offset_m,
                    seed=index * 10 + seed,
                    route=route,
                    score=score,
                    score_breakdown=score_breakdown,
                    traits=traits,
                    badges=badges,
                )
            )

    if not candidates:
        if last_error is not None:
            raise last_error
        raise RouteError("No viable loop routes were returned for that area and preference set.")

    candidates.sort(key=lambda candidate: candidate.score, reverse=True)
    return candidates


def write_geojson(route_geojson: dict, output_path: Path) -> None:
    output_path.write_text(json.dumps(route_geojson, indent=2), encoding="utf-8")
