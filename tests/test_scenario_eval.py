import json
import tempfile
import unittest
from pathlib import Path

from run_router.scenario_eval import (
    discover_scenarios,
    evaluate_expectations,
    load_scenario_manifest,
)


class ScenarioEvalTests(unittest.TestCase):
    def test_load_scenario_manifest_requires_expected_keys(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "bad.json"
            path.write_text(json.dumps({"id": "only-id"}), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_scenario_manifest(path)

    def test_discover_scenarios_rejects_duplicate_ids(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            payload = {
                "id": "duplicate",
                "label": "Duplicate",
                "request": {"center_coord": "-122.0,45.0"},
                "expectations": {"expect_success": True},
            }
            (root / "a.json").write_text(json.dumps(payload), encoding="utf-8")
            (root / "b.json").write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(ValueError):
                discover_scenarios(root)

    def test_load_scenario_manifest_accepts_minimal_valid_shape(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "good.json"
            payload = {
                "id": "valid",
                "label": "Valid",
                "request": {"center_coord": "-122.0,45.0"},
                "expectations": {"expect_success": True},
            }
            path.write_text(json.dumps(payload), encoding="utf-8")
            manifest = load_scenario_manifest(path)
            self.assertEqual(manifest["id"], "valid")

    def test_evaluate_expectations_success_checks_patterns_and_reasons(self):
        failures = evaluate_expectations(
            {
                "expect_success": True,
                "allowed_patterns": ["loop", "out_and_back"],
                "preferred_pattern": "loop",
                "requires_top_reasons": ["start proximity"],
                "max_repeat_count": 1,
                "max_distance_from_start_miles_actual": 1.2,
                "min_hill_fit": 0.4,
                "max_distance_error_miles": 0.5,
            },
            status="success",
            request_target_distance_miles=4.5,
            selected={
                "selected_pattern": "loop",
                "top_reasons": ["start proximity", "distance fit"],
                "selected_repeat_count": 1,
                "selected_max_distance_from_start_miles_actual": 1.0,
                "selected_hill_fit": 0.5,
                "selected_distance_miles": 4.8,
            },
        )
        self.assertEqual(failures, [])

    def test_evaluate_expectations_failure_checks_notes_and_requirement_names(self):
        failures = evaluate_expectations(
            {
                "expect_success": False,
                "requires_failure_notes": ["flat"],
                "requires_non_negotiable_failures": ["Elevation profile"],
            },
            status="feasibility_error",
            request_target_distance_miles=5.0,
            failure_analysis={
                "location_notes": ["This area appears relatively flat nearby."],
                "requirements": [
                    {"name": "Elevation profile", "passed_count": 0},
                    {"name": "Stay close to start", "passed_count": 1},
                ],
                "near_misses": [],
            },
        )
        self.assertEqual(failures, [])

    def test_evaluate_expectations_reports_mismatches(self):
        failures = evaluate_expectations(
            {
                "expect_success": True,
                "preferred_pattern": "hill_repeat",
                "requires_top_reasons": ["landmark"],
                "max_distance_error_miles": 0.25,
            },
            status="success",
            request_target_distance_miles=4.0,
            selected={
                "selected_pattern": "loop",
                "top_reasons": ["distance fit"],
                "selected_distance_miles": 4.6,
            },
        )
        self.assertEqual(len(failures), 3)


if __name__ == "__main__":
    unittest.main()
