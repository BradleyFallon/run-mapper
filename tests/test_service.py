import unittest

from run_router.service import (
    PRIORITY_OPTIONS,
    LoopCandidate,
    RouteError,
    RouteResult,
    aggregate_candidate_score,
    build_candidate_summary,
    build_feasibility_failure_analysis,
    choose_repeat_count,
    compose_out_and_back_route,
    compute_elevation_stats,
    default_max_distance_from_start_miles,
    derive_route_badges,
    derive_route_traits,
    evaluate_candidate_constraints,
    generate_candidate_starts,
    parse_coord_lines,
    parse_planning_request,
    parse_positive_float,
    turn_metrics_from_coords,
)


class ServiceTests(unittest.TestCase):
    center = [-122.0, 45.0]

    def make_route_result(self, *, extras=None, ascent_m=50.0, coords=None):
        return RouteResult(
            route_feature={
                "geometry": {
                    "coordinates": coords
                    or [
                        [-122.0, 45.0, 100.0],
                        [-122.001, 45.001, 110.0],
                        [-122.0002, 45.0002, 101.0],
                    ]
                }
            },
            raw_geojson={"type": "FeatureCollection", "features": []},
            distance_m=8046.72,
            duration_s=2400.0,
            ascent_m=ascent_m,
            descent_m=ascent_m * 0.8,
            min_ele_m=100.0,
            max_ele_m=120.0,
            extras=extras or {},
        )

    def make_request(self, **overrides):
        payload = {
            "center_coord": "-122.0,45.0",
            "target_distance_miles": 5.0,
            "distance_tolerance_miles": 0.5,
            "start_radius_miles": 0.25,
            "top_priority": "Distance accuracy",
            "secondary_priority": "Closer start",
        }
        payload.update(overrides)
        return parse_planning_request(payload)

    def make_candidate(
        self,
        *,
        route=None,
        score_breakdown=None,
        request=None,
        pattern_type="loop",
        pattern_metadata=None,
        start_offset_m=20.0,
        seed=1,
    ):
        route = route or self.make_route_result()
        request = request or self.make_request()
        score_breakdown = score_breakdown or {
            "distance": 0.88,
            "pavement": 0.91,
            "quiet": 0.87,
            "green": 0.35,
            "hills": 0.75,
            "start": 0.93,
        }
        candidate = LoopCandidate(
            start_coord=self.center,
            start_offset_m=start_offset_m,
            seed=seed,
            route=route,
            score=0.0,
            score_breakdown=score_breakdown,
            pattern_type=pattern_type,
            pattern_metadata=pattern_metadata or {"repeat_count": 1},
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
        candidate.score, candidate.ranking_breakdown = aggregate_candidate_score(
            candidate=candidate,
            request=request,
            traits=traits,
            score_breakdown=score_breakdown,
            top_priority=request.top_priority,
            secondary_priority=request.secondary_priority,
        )
        candidate.summary = build_candidate_summary(candidate)
        return candidate

    def test_parse_coord_lines_accepts_lon_lat_rows(self):
        coords = parse_coord_lines("-122.1,45.5\n-122.2,45.6\n")
        self.assertEqual(coords, [[-122.1, 45.5], [-122.2, 45.6]])

    def test_parse_coord_lines_requires_two_points(self):
        with self.assertRaises(RouteError):
            parse_coord_lines("-122.1,45.5")

    def test_compute_elevation_stats_ignores_small_noise(self):
        ascent_m, descent_m, min_ele_m, max_ele_m = compute_elevation_stats(
            [
                [-122.0, 45.0, 100.0],
                [-122.0, 45.0, 101.0],
                [-122.0, 45.0, 105.5],
                [-122.0, 45.0, 103.8],
                [-122.0, 45.0, 99.0],
            ],
            noise_threshold_m=2.0,
        )

        self.assertAlmostEqual(ascent_m, 4.5)
        self.assertAlmostEqual(descent_m, 4.8)
        self.assertEqual(min_ele_m, 99.0)
        self.assertEqual(max_ele_m, 105.5)

    def test_parse_positive_float_allows_zero_when_requested(self):
        self.assertEqual(parse_positive_float("0", name="Start radius", minimum=0.0), 0.0)

    def test_generate_candidate_starts_returns_center_for_zero_radius(self):
        starts = generate_candidate_starts([-122.6, 45.5], 0.0)
        self.assertEqual(starts, [([-122.6, 45.5], 0.0)])

    def test_parse_planning_request_supports_short_aliases_and_patterns(self):
        request = parse_planning_request(
            {
                "center": "-122.6765,45.5236",
                "miles": 4.5,
                "radius": 0.25,
                "seed_offset": 100,
                "route_pattern": "either",
                "repeat_preference": "as_needed",
                "max_drift_miles": 2.0,
                "focus_feature": "climb",
                "pavement": 0.9,
                "quiet": 0.6,
                "green": 0.4,
                "hills": -0.25,
                "brief": "Easy nearby loop.",
            },
            seed_count_default=2,
            start_limit_default=4,
        )

        self.assertEqual(request.center, [-122.6765, 45.5236])
        self.assertEqual(request.target_distance_miles, 4.5)
        self.assertEqual(request.start_radius_miles, 0.25)
        self.assertEqual(request.route_pattern_preference, "either")
        self.assertEqual(request.repeat_preference, "as_needed")
        self.assertEqual(request.max_distance_from_start_miles, 2.0)
        self.assertEqual(request.focus_feature, "climb")
        self.assertEqual(request.seed_count, 2)
        self.assertEqual(request.start_limit, 4)
        self.assertEqual(request.seed_offset, 100)
        self.assertEqual(request.top_priority, "Distance accuracy")
        self.assertEqual(request.secondary_priority, "Closer start")
        self.assertEqual(request.preferences.pavement_preference, 0.9)
        self.assertEqual(request.design_brief, "Easy nearby loop.")

    def test_parse_planning_request_uses_pattern_defaults(self):
        request = parse_planning_request(
            {
                "center_coord": "-122.6765,45.5236",
                "target_distance_miles": 6.0,
                "start_radius_miles": 0.2,
                "top_priority": "Elevation profile",
            },
            max_candidates_default=3,
            seed_count_default=3,
            start_limit_default=4,
        )

        self.assertEqual(request.profile, "foot-walking")
        self.assertEqual(request.route_pattern_preference, "loop")
        self.assertEqual(request.repeat_preference, "none")
        self.assertAlmostEqual(
            request.max_distance_from_start_miles,
            default_max_distance_from_start_miles(
                route_pattern_preference="loop",
                target_distance_miles=6.0,
                start_radius_miles=0.2,
            ),
        )
        self.assertEqual(request.focus_feature, "climb")

    def test_parse_planning_request_rejects_unknown_priority(self):
        with self.assertRaises(RouteError):
            parse_planning_request(
                {
                    "center_coord": "-122.6765,45.5236",
                    "top_priority": "Totally made up",
                }
            )

    def test_priority_options_include_expected_values(self):
        self.assertIn("Distance accuracy", PRIORITY_OPTIONS)
        self.assertIn("Simple navigation", PRIORITY_OPTIONS)

    def test_derive_route_traits_reports_surface_loop_and_pattern_fields(self):
        route = self.make_route_result(
            extras={
                "surface": {
                    "summary": [
                        {"value": 1, "distance": 6000.0},
                        {"value": 10, "distance": 2000.0},
                    ]
                },
                "noise": {"summary": [{"value": 2, "distance": 8000.0}]},
                "green": {"summary": [{"value": 6, "distance": 8000.0}]},
            },
            ascent_m=40.0,
        )
        request = self.make_request(max_distance_from_start_miles=1.0)
        traits = derive_route_traits(
            route=route,
            score_breakdown={
                "distance": 0.9,
                "pavement": 0.8,
                "quiet": 0.8,
                "green": 0.6,
                "hills": 0.7,
                "start": 0.9,
            },
            center=request.center,
            start_offset_m=50.0,
            start_radius_m=request.start_radius_m,
            pattern_type="out_and_back",
            pattern_metadata={"repeat_count": 1, "outbound_distance_miles": 2.1},
        )

        self.assertAlmostEqual(traits.paved_ratio or 0.0, 0.75, places=2)
        self.assertTrue(traits.is_loop)
        self.assertEqual(traits.pattern_type, "out_and_back")
        self.assertAlmostEqual(traits.outbound_distance_miles or 0.0, 2.1, places=2)
        self.assertGreater(traits.route_simplicity, 0.7)

    def test_derive_route_badges_returns_paved_nearby_and_quiet(self):
        route = self.make_route_result(
            extras={
                "surface": {"summary": [{"value": 1, "distance": 7600.0}]},
                "noise": {"summary": [{"value": 1, "distance": 7600.0}]},
            },
            ascent_m=35.0,
        )
        request = self.make_request()
        traits = derive_route_traits(
            route=route,
            score_breakdown={
                "distance": 0.86,
                "pavement": 0.9,
                "quiet": 0.9,
                "green": 0.4,
                "hills": 0.7,
                "start": 0.92,
            },
            center=request.center,
            start_offset_m=40.0,
            start_radius_m=request.start_radius_m,
        )
        badges = derive_route_badges(traits)
        codes = [badge.code for badge in badges]

        self.assertIn("NX", codes)
        self.assertIn("PV", codes)
        self.assertIn("QT", codes)

    def test_build_candidate_summary_is_pattern_aware(self):
        route = self.make_route_result(ascent_m=220.0)
        request = self.make_request(
            top_priority="Elevation profile",
            secondary_priority="Distance accuracy",
            repeat_preference="preferred",
            focus_feature="climb",
        )
        candidate = self.make_candidate(
            route=route,
            request=request,
            pattern_type="hill_repeat",
            pattern_metadata={
                "repeat_count": 3,
                "repeat_segment_distance_miles": 1.2,
                "repeat_segment_climb_feet": 180.0,
                "repeat_segment_ft_per_mile": 150.0,
            },
        )

        self.assertIn("Repeat-based", candidate.summary.headline)
        self.assertEqual(candidate.traits.repeat_count, 3)

    def test_aggregate_candidate_score_changes_with_priorities(self):
        route = self.make_route_result(
            extras={
                "surface": {"summary": [{"value": 1, "distance": 6000.0}]},
                "waytype": {"summary": [{"value": 3, "distance": 6000.0}]},
            },
            ascent_m=260.0,
        )
        score_breakdown = {
            "distance": 0.9,
            "pavement": 0.9,
            "quiet": 0.4,
            "green": 0.3,
            "hills": 0.92,
            "start": 0.6,
        }
        hill_request = self.make_request(
            top_priority="Elevation profile",
            secondary_priority="Distance accuracy",
        )
        start_request = self.make_request(
            top_priority="Closer start",
            secondary_priority="Distance accuracy",
        )
        hill_candidate = self.make_candidate(
            route=route,
            request=hill_request,
            score_breakdown=score_breakdown,
            start_offset_m=120.0,
        )
        start_candidate = self.make_candidate(
            route=route,
            request=start_request,
            score_breakdown=score_breakdown,
            start_offset_m=120.0,
        )

        self.assertGreater(
            hill_candidate.ranking_breakdown["hill_fit"],
            start_candidate.ranking_breakdown["hill_fit"],
        )
        self.assertGreater(
            start_candidate.ranking_breakdown["start_convenience"],
            hill_candidate.ranking_breakdown["start_convenience"],
        )
        self.assertNotEqual(hill_candidate.score, start_candidate.score)

    def test_repeat_preference_rewards_hill_repeats_when_preferred(self):
        route = self.make_route_result(ascent_m=220.0)
        preferred_request = self.make_request(
            top_priority="Elevation profile",
            secondary_priority="Distance accuracy",
            repeat_preference="preferred",
            focus_feature="climb",
        )
        none_request = self.make_request(
            top_priority="Elevation profile",
            secondary_priority="Distance accuracy",
            repeat_preference="none",
            focus_feature="climb",
        )
        preferred_candidate = self.make_candidate(
            route=route,
            request=preferred_request,
            pattern_type="hill_repeat",
            pattern_metadata={"repeat_count": 3},
        )
        none_candidate = self.make_candidate(
            route=route,
            request=none_request,
            pattern_type="hill_repeat",
            pattern_metadata={"repeat_count": 3},
        )

        self.assertGreater(preferred_candidate.score, none_candidate.score)

    def test_turn_metrics_from_coords_counts_bends(self):
        turn_count, sharp_turn_count = turn_metrics_from_coords(
            [
                [-122.0, 45.0],
                [-121.999, 45.0],
                [-121.999, 45.001],
                [-121.998, 45.001],
            ]
        )

        self.assertGreaterEqual(turn_count, 2)
        self.assertGreaterEqual(sharp_turn_count, 2)

    def test_landmark_priority_uses_poi_signal(self):
        route = self.make_route_result(
            extras={
                "surface": {"summary": [{"value": 1, "distance": 7600.0}]},
                "green": {"summary": [{"value": 4, "distance": 7600.0}]},
            },
            ascent_m=40.0,
        )
        route.poi_summary = {
            "total_count": 6,
            "landmark_count": 4,
            "park_count": 1,
            "water_count": 1,
        }
        score_breakdown = {
            "distance": 0.82,
            "pavement": 0.88,
            "quiet": 0.55,
            "green": 0.5,
            "hills": 0.7,
            "start": 0.8,
        }
        landmark_request = self.make_request(
            top_priority="Landmarks",
            secondary_priority="Distance accuracy",
        )
        distance_request = self.make_request(
            top_priority="Distance accuracy",
            secondary_priority="Closer start",
        )
        landmark_candidate = self.make_candidate(
            route=route,
            request=landmark_request,
            score_breakdown=score_breakdown,
        )
        distance_candidate = self.make_candidate(
            route=route,
            request=distance_request,
            score_breakdown=score_breakdown,
        )

        self.assertGreater(
            landmark_candidate.ranking_breakdown["landmark_fit"],
            distance_candidate.ranking_breakdown["landmark_fit"],
        )
        self.assertGreater(landmark_candidate.score, 0.0)

    def test_evaluate_non_negotiable_distance_accuracy_uses_tolerance(self):
        request = self.make_request(
            target_distance_miles=6.0,
            distance_tolerance_miles=0.25,
            non_negotiables=["Distance accuracy"],
        )
        candidate = self.make_candidate(route=self.make_route_result(), request=request)
        candidate.constraint_results = evaluate_candidate_constraints(candidate=candidate, request=request)

        self.assertFalse(candidate.constraint_results["Distance accuracy"]["passed"])

    def test_landmarks_can_be_non_negotiable(self):
        request = self.make_request(non_negotiables=["Landmarks"])
        route = self.make_route_result(extras={"green": {"summary": [{"value": 4, "distance": 7600.0}]}})
        route.poi_summary = {
            "total_count": 8,
            "landmark_count": 6,
            "park_count": 1,
            "water_count": 1,
        }
        candidate = self.make_candidate(route=route, request=request)
        candidate.constraint_results = evaluate_candidate_constraints(candidate=candidate, request=request)

        self.assertTrue(candidate.constraint_results["Landmarks"]["passed"])

    def test_stay_close_to_start_can_be_non_negotiable(self):
        request = self.make_request(
            max_distance_from_start_miles=0.1,
            non_negotiables=["Stay close to start"],
        )
        route = self.make_route_result(
            coords=[
                [-122.0, 45.0, 100.0],
                [-122.02, 45.02, 110.0],
                [-122.0, 45.0, 100.0],
            ]
        )
        candidate = self.make_candidate(route=route, request=request)
        candidate.constraint_results = evaluate_candidate_constraints(candidate=candidate, request=request)

        self.assertFalse(candidate.constraint_results["Stay close to start"]["passed"])

    def test_no_repeats_can_be_non_negotiable(self):
        request = self.make_request(non_negotiables=["No repeats"])
        candidate = self.make_candidate(
            request=request,
            pattern_type="hill_repeat",
            pattern_metadata={"repeat_count": 3},
        )
        candidate.constraint_results = evaluate_candidate_constraints(candidate=candidate, request=request)

        self.assertFalse(candidate.constraint_results["No repeats"]["passed"])

    def test_build_feasibility_failure_analysis_summarizes_requirements(self):
        request = self.make_request(non_negotiables=["Paved surface", "Quiet surroundings"])
        route = self.make_route_result()
        candidate = self.make_candidate(
            route=route,
            request=request,
            score_breakdown={
                "distance": 0.9,
                "pavement": 0.3,
                "quiet": 0.4,
                "green": 0.5,
                "hills": 0.7,
                "start": 1.0,
            },
        )
        candidate.constraint_results = evaluate_candidate_constraints(candidate=candidate, request=request)

        analysis = build_feasibility_failure_analysis(request=request, candidates=[candidate])

        self.assertEqual(len(analysis["requirements"]), 2)
        self.assertEqual(
            analysis["near_misses"][0]["failed_requirements"],
            ["Paved surface", "Quiet surroundings"],
        )

    def test_build_feasibility_failure_analysis_adds_area_notes(self):
        request = self.make_request(
            top_priority="Elevation profile",
            secondary_priority="Distance accuracy",
            focus_feature="climb",
            repeat_preference="none",
            hill_preference=0.8,
            non_negotiables=["Elevation profile", "No repeats"],
        )
        route = self.make_route_result(
            extras={"surface": {"summary": [{"value": 1, "distance": 7600.0}]}},
            ascent_m=25.0,
        )
        candidate = self.make_candidate(
            route=route,
            request=request,
            score_breakdown={
                "distance": 0.4,
                "pavement": 0.8,
                "quiet": 0.6,
                "green": 0.4,
                "hills": 0.2,
                "start": 1.0,
            },
            pattern_type="hill_repeat",
            pattern_metadata={"repeat_count": 3},
        )
        candidate.constraint_results = evaluate_candidate_constraints(candidate=candidate, request=request)

        analysis = build_feasibility_failure_analysis(request=request, candidates=[candidate])

        self.assertTrue(analysis["location_notes"])

    def test_choose_repeat_count_respects_tolerance(self):
        self.assertEqual(
            choose_repeat_count(
                target_distance_miles=6.0,
                tolerance_miles=0.5,
                repeat_segment_distance_miles=2.0,
                repeat_preference="as_needed",
            ),
            3,
        )
        self.assertIsNone(
            choose_repeat_count(
                target_distance_miles=6.0,
                tolerance_miles=0.2,
                repeat_segment_distance_miles=1.3,
                repeat_preference="as_needed",
            )
        )

    def test_compose_out_and_back_route_doubles_distance(self):
        base = self.make_route_result(
            coords=[
                [-122.0, 45.0, 100.0],
                [-122.001, 45.001, 110.0],
                [-122.002, 45.002, 120.0],
            ]
        )
        combined = compose_out_and_back_route(base)

        self.assertAlmostEqual(combined.distance_m, base.distance_m * 2)
        self.assertGreater(
            len(combined.route_feature["geometry"]["coordinates"]),
            len(base.route_feature["geometry"]["coordinates"]),
        )


if __name__ == "__main__":
    unittest.main()
