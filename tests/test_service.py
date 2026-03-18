import unittest

from run_router.service import (
    RouteError,
    compute_elevation_stats,
    derive_route_badges,
    derive_route_traits,
    generate_candidate_starts,
    parse_coord_lines,
    parse_positive_float,
    RouteResult,
)


class ServiceTests(unittest.TestCase):
    def make_route_result(self, *, extras=None, ascent_m=50.0):
        return RouteResult(
            route_feature={
                "geometry": {
                    "coordinates": [
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

    def test_derive_route_traits_reports_surface_and_loop_shape(self):
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
            start_offset_m=50.0,
            start_radius_m=200.0,
        )

        self.assertAlmostEqual(traits.paved_ratio or 0.0, 0.75, places=2)
        self.assertTrue(traits.is_loop)
        self.assertGreater(traits.route_simplicity, 0.7)

    def test_derive_route_badges_returns_paved_nearby_and_quiet(self):
        route = self.make_route_result(
            extras={
                "surface": {"summary": [{"value": 1, "distance": 7600.0}]},
                "noise": {"summary": [{"value": 1, "distance": 7600.0}]},
            },
            ascent_m=35.0,
        )
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
            start_offset_m=40.0,
            start_radius_m=200.0,
        )
        badges = derive_route_badges(traits)
        codes = [badge.code for badge in badges]

        self.assertIn("NX", codes)
        self.assertIn("PV", codes)
        self.assertIn("QT", codes)

    def test_derive_route_badges_prefers_hills_over_flat_when_both_plausible(self):
        route = self.make_route_result(
            extras={
                "surface": {"summary": [{"value": 1, "distance": 7600.0}]},
            },
            ascent_m=420.0,
        )
        traits = derive_route_traits(
            route=route,
            score_breakdown={
                "distance": 0.82,
                "pavement": 0.85,
                "quiet": 0.5,
                "green": 0.5,
                "hills": 0.9,
                "start": 0.7,
            },
            start_offset_m=120.0,
            start_radius_m=300.0,
        )
        badges = derive_route_badges(traits)
        codes = [badge.code for badge in badges]

        self.assertIn("HL", codes)
        self.assertNotIn("FL", codes)


if __name__ == "__main__":
    unittest.main()
