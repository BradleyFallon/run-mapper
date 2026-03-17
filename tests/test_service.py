import unittest

from run_router.service import (
    RouteError,
    compute_elevation_stats,
    generate_candidate_starts,
    parse_coord_lines,
    parse_positive_float,
)


class ServiceTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
