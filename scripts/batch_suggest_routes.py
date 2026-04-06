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

from run_router.env import load_env_file
from run_router.scenario_eval import discover_scenarios, evaluate_expectations
from run_router.service import (
    RouteFeasibilityError,
    RouteError,
    build_route_candidates,
    maybe_apply_llm_preferences,
    parse_planning_request,
)


load_env_file()

SCENARIO_ROOT = PROJECT_ROOT / "examples" / "scenarios"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a batch scenario corpus against the RouteScout route engine."
    )
    parser.add_argument("--scenario", help="Run a single scenario id.")
    parser.add_argument("--scenario-prefix", help="Run all scenario ids starting with this prefix.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text.")
    parser.add_argument("--output", help="Write the report to a file.")
    parser.add_argument("--no-llm", action="store_true", help="Disable LLM preference interpretation.")
    parser.add_argument(
        "--fail-on-expectation-miss",
        action="store_true",
        help="Exit nonzero when any scenario misses expectations.",
    )
    return parser


def load_api_key() -> str:
    api_key = os.environ.get("ORS_API_KEY")
    if not api_key:
        raise SystemExit("Missing ORS_API_KEY. Populate it in the environment or .env before running batch_suggest_routes.py.")
    return api_key


def scenario_manifests(selected_id: str | None, selected_prefix: str | None) -> list[dict]:
    manifests = discover_scenarios(SCENARIO_ROOT)
    if selected_id:
        filtered = [manifest for manifest in manifests if manifest["id"] == selected_id]
        if not filtered:
            raise SystemExit(f"Scenario id not found: {selected_id}")
        return filtered
    if selected_prefix:
        filtered = [manifest for manifest in manifests if manifest["id"].startswith(selected_prefix)]
        if not filtered:
            raise SystemExit(f"No scenario ids found with prefix: {selected_prefix}")
        return filtered
    return manifests


def selected_candidate_payload(candidate) -> dict:
    traits = candidate.traits
    summary = candidate.summary
    return {
        "selected_pattern": candidate.pattern_type,
        "selected_score": round(candidate.score, 4),
        "selected_distance_miles": round(candidate.route.distance_mi, 2),
        "selected_repeat_count": traits.repeat_count if traits else None,
        "selected_max_distance_from_start_miles_actual": (
            round(traits.max_distance_from_start_miles_actual, 2) if traits else None
        ),
        "selected_hill_fit": round(traits.hill_fit, 3) if traits else None,
        "top_reasons": summary.top_reasons if summary else [],
        "headline": summary.headline if summary else None,
    }


def run_scenario(manifest: dict, *, api_key: str, use_llm: bool) -> dict:
    request = parse_planning_request(manifest["request"])
    llm_hint = None
    if use_llm:
        llm_hint = maybe_apply_llm_preferences(
            design_brief=request.design_brief,
            base_preferences=request.preferences,
        )
        if llm_hint:
            request.preferences = llm_hint.preferences

    try:
        candidates = build_route_candidates(api_key=api_key, request=request)
        selected = selected_candidate_payload(candidates[0]) if candidates else None
        expectation_failures = evaluate_expectations(
            manifest["expectations"],
            status="success",
            request_target_distance_miles=request.target_distance_miles,
            selected=selected,
        )
        return {
            "id": manifest["id"],
            "label": manifest["label"],
            "status": "success",
            "expectation_passed": not expectation_failures,
            "selected_pattern": selected["selected_pattern"],
            "selected_score": selected["selected_score"],
            "selected_distance_miles": selected["selected_distance_miles"],
            "selected_repeat_count": selected["selected_repeat_count"],
            "selected_max_distance_from_start_miles_actual": selected["selected_max_distance_from_start_miles_actual"],
            "top_reasons": selected["top_reasons"],
            "failure_analysis": None,
            "expectation_failures": expectation_failures,
            "headline": selected["headline"],
            "llm_summary": llm_hint.summary if llm_hint else None,
        }
    except RouteFeasibilityError as exc:
        expectation_failures = evaluate_expectations(
            manifest["expectations"],
            status="feasibility_error",
            request_target_distance_miles=request.target_distance_miles,
            failure_analysis=exc.failure_analysis,
        )
        return {
            "id": manifest["id"],
            "label": manifest["label"],
            "status": "feasibility_error",
            "expectation_passed": not expectation_failures,
            "selected_pattern": None,
            "selected_score": None,
            "selected_distance_miles": None,
            "selected_repeat_count": None,
            "selected_max_distance_from_start_miles_actual": None,
            "top_reasons": [],
            "failure_analysis": exc.failure_analysis,
            "expectation_failures": expectation_failures,
            "headline": str(exc),
            "llm_summary": llm_hint.summary if llm_hint else None,
        }
    except RouteError as exc:
        return {
            "id": manifest["id"],
            "label": manifest["label"],
            "status": "error",
            "expectation_passed": False,
            "selected_pattern": None,
            "selected_score": None,
            "selected_distance_miles": None,
            "selected_repeat_count": None,
            "selected_max_distance_from_start_miles_actual": None,
            "top_reasons": [],
            "failure_analysis": None,
            "expectation_failures": [str(exc)],
            "headline": str(exc),
            "llm_summary": llm_hint.summary if llm_hint else None,
        }


def render_text_report(results: list[dict]) -> str:
    groups = {
        "success": [item for item in results if item["status"] == "success"],
        "feasibility_error": [item for item in results if item["status"] == "feasibility_error"],
        "error": [item for item in results if item["status"] == "error"],
    }
    lines: list[str] = []
    for status, heading in (
        ("success", "Success"),
        ("feasibility_error", "Feasibility Failures"),
        ("error", "Errors"),
    ):
        items = groups[status]
        if not items:
            continue
        lines.append(heading)
        lines.append("-" * len(heading))
        for item in items:
            marker = "PASS" if item["expectation_passed"] else "MISS"
            lines.append(f"[{marker}] {item['id']} · {item['label']}")
            if item["status"] == "success":
                lines.append(
                    f"  pattern={item['selected_pattern']} | distance={item['selected_distance_miles']} mi | score={item['selected_score']} | reasons={', '.join(item['top_reasons']) or 'n/a'}"
                )
            else:
                notes = ((item.get("failure_analysis") or {}).get("location_notes") or [])
                lines.append(
                    f"  status={item['status']} | notes={'; '.join(notes) or item['headline']}"
                )
            if item["expectation_failures"]:
                lines.append(f"  expectation failures: {'; '.join(item['expectation_failures'])}")
        lines.append("")
    passed = sum(1 for item in results if item["expectation_passed"])
    lines.append(f"Scenario expectation pass rate: {passed}/{len(results)}")
    return "\n".join(lines).strip() + "\n"


def maybe_write_output(path_text: str | None, content: str) -> None:
    if not path_text:
        return
    output_path = Path(path_text)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")


def main() -> int:
    args = build_parser().parse_args()
    api_key = load_api_key()
    manifests = scenario_manifests(args.scenario, args.scenario_prefix)
    results = [
        run_scenario(manifest, api_key=api_key, use_llm=not args.no_llm)
        for manifest in manifests
    ]

    if args.json:
        content = json.dumps(results, indent=2)
    else:
        content = render_text_report(results)

    print(content, end="" if content.endswith("\n") else "\n")
    maybe_write_output(args.output, content)

    if args.fail_on_expectation_miss and any(not item["expectation_passed"] for item in results):
        return 1
    if any(item["status"] == "error" for item in results):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
