from __future__ import annotations

import json
from pathlib import Path


REQUIRED_SCENARIO_KEYS = ("id", "label", "request", "expectations")


def load_scenario_manifest(path: Path) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"Scenario file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in scenario file {path}: {exc}") from exc

    missing = [key for key in REQUIRED_SCENARIO_KEYS if key not in payload]
    if missing:
        raise ValueError(f"Scenario file {path} is missing keys: {', '.join(missing)}")

    if not isinstance(payload["request"], dict):
        raise ValueError(f"Scenario file {path} must have an object-valued 'request'.")
    if not isinstance(payload["expectations"], dict):
        raise ValueError(f"Scenario file {path} must have an object-valued 'expectations'.")

    payload["source_path"] = str(path)
    return payload


def discover_scenarios(root: Path) -> list[dict]:
    manifests = [load_scenario_manifest(path) for path in sorted(root.glob("*.json"))]
    ids = [manifest["id"] for manifest in manifests]
    duplicates = {scenario_id for scenario_id in ids if ids.count(scenario_id) > 1}
    if duplicates:
        raise ValueError(f"Duplicate scenario ids found: {', '.join(sorted(duplicates))}")
    return manifests


def _contains_substring(haystack_items: list[str], needle: str) -> bool:
    wanted = needle.strip().lower()
    return any(wanted in item.lower() for item in haystack_items)


def evaluate_expectations(
    expectations: dict,
    *,
    status: str,
    request_target_distance_miles: float | None = None,
    selected: dict | None = None,
    failure_analysis: dict | None = None,
) -> list[str]:
    failures: list[str] = []
    expect_success = expectations.get("expect_success", True)
    normalized_status = status.lower()
    is_success = normalized_status == "success"
    is_feasibility_failure = normalized_status == "feasibility_error"

    if expect_success and not is_success:
        failures.append(f"Expected success but got {status}.")
        return failures
    if not expect_success and not is_feasibility_failure:
        failures.append(f"Expected feasibility_error but got {status}.")
        return failures

    if is_success and selected is not None:
        allowed_patterns = expectations.get("allowed_patterns") or []
        if allowed_patterns and selected.get("selected_pattern") not in allowed_patterns:
            failures.append(
                f"Selected pattern {selected.get('selected_pattern')} not in allowed set {allowed_patterns}."
            )

        preferred_pattern = expectations.get("preferred_pattern")
        if preferred_pattern and selected.get("selected_pattern") != preferred_pattern:
            failures.append(
                f"Selected pattern {selected.get('selected_pattern')} did not match preferred pattern {preferred_pattern}."
            )

        requires_top_reasons = expectations.get("requires_top_reasons") or []
        top_reasons = selected.get("top_reasons") or []
        for reason in requires_top_reasons:
            if not _contains_substring(top_reasons, reason):
                failures.append(f"Missing expected top reason containing '{reason}'.")

        max_repeat_count = expectations.get("max_repeat_count")
        if max_repeat_count is not None:
            repeat_count = selected.get("selected_repeat_count")
            if repeat_count is None or repeat_count > max_repeat_count:
                failures.append(
                    f"Repeat count {repeat_count} exceeded max_repeat_count {max_repeat_count}."
                )

        max_distance = expectations.get("max_distance_from_start_miles_actual")
        if max_distance is not None:
            actual = selected.get("selected_max_distance_from_start_miles_actual")
            if actual is None or actual > max_distance:
                failures.append(
                    f"Actual max distance from start {actual} exceeded {max_distance}."
                )

        min_hill_fit = expectations.get("min_hill_fit")
        if min_hill_fit is not None:
            hill_fit = selected.get("selected_hill_fit")
            if hill_fit is None or hill_fit < min_hill_fit:
                failures.append(f"Hill fit {hill_fit} was below required minimum {min_hill_fit}.")

        max_distance_error_miles = expectations.get("max_distance_error_miles")
        if max_distance_error_miles is not None and request_target_distance_miles is not None:
            selected_distance = selected.get("selected_distance_miles")
            if selected_distance is None or abs(selected_distance - request_target_distance_miles) > max_distance_error_miles:
                failures.append(
                    f"Distance error {None if selected_distance is None else round(abs(selected_distance - request_target_distance_miles), 2)} exceeded max_distance_error_miles {max_distance_error_miles}."
                )

    if is_feasibility_failure and failure_analysis is not None:
        requires_failure_notes = expectations.get("requires_failure_notes") or []
        location_notes = failure_analysis.get("location_notes") or []
        for note in requires_failure_notes:
            if not _contains_substring(location_notes, note):
                failures.append(f"Missing expected failure note containing '{note}'.")

        required_failures = expectations.get("requires_non_negotiable_failures") or []
        failed_requirements = set()
        for requirement in failure_analysis.get("requirements") or []:
            if requirement.get("passed_count") == 0:
                failed_requirements.add(requirement.get("name"))
        for near_miss in failure_analysis.get("near_misses") or []:
            failed_requirements.update(near_miss.get("failed_requirements") or [])
        for requirement_name in required_failures:
            if requirement_name not in failed_requirements:
                failures.append(
                    f"Missing expected non-negotiable failure '{requirement_name}'."
                )

    return failures
