#!/usr/bin/env python3
import math
import unittest

import portal_boundary_heavy_spectrum_v20 as spectrum


class PortalBoundaryHeavySpectrumTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = spectrum.build_report()

    def test_full_heavy_spectrum_has_three_positive_values(self):
        row = self.report["na62_survival_boundary"]["heavy_spectrum"]
        values = row["heavy_singular_values_GeV_ascending"]
        self.assertEqual(row["matrix_rank"], 3)
        self.assertEqual(len(values), 3)
        self.assertTrue(all(value > 0.0 for value in values))
        self.assertEqual(values, sorted(values))

    def test_bare_D_is_not_mislabeled_as_eigenmass(self):
        row = self.report["na62_survival_boundary"]["heavy_spectrum"]
        self.assertFalse(
            math.isclose(
                row["bare_D_GeV"], row["lightest_heavy_singular_GeV"], rel_tol=1e-3
            )
        )
        self.assertTrue(self.report["flag"]["bare_D_is_not_a_physical_mass_eigenvalue"])
        self.assertFalse(
            self.report["flag"]["individual_Q_like_mass_eigenstate_uniquely_identified"]
        )

    def test_unique_ordering_boundary_rechecks(self):
        scan = self.report["lightest_heavy_equals_vS_scan"]
        self.assertTrue(scan["monotonic_nondecreasing"])
        self.assertEqual(scan["n_crossings"], 1)
        boundary = scan["unique_ordering_boundary"]
        self.assertIsNotNone(boundary)
        self.assertTrue(math.isclose(boundary["lightest_heavy_over_vS"], 1.0, rel_tol=1e-8))

    def test_dominant_two_entry_estimate_matches_full_ordering_boundary(self):
        boundary = self.report["lightest_heavy_equals_vS_scan"][
            "unique_ordering_boundary"
        ]
        estimate = spectrum.portals.VS / spectrum.portals.VPHI
        relative_difference = boundary["y_Q"] / estimate - 1.0
        self.assertLess(abs(relative_difference), 1.0e-3)
        self.assertAlmostEqual(relative_difference, -4.962255230045454e-5, delta=1e-8)

    def test_ordered_point_survives_both_channels(self):
        point = self.report["ordered_threshold_point_rate_result"]
        self.assertTrue(point["NA62_survives"])
        self.assertTrue(point["TWIST_survives_strongest_published_case"])
        self.assertLess(point["NA62_ratio"], 1.0)
        self.assertLess(point["TWIST_ratio"], 1.0)

    def test_piecewise_matching_stays_open(self):
        flags = self.report["flag"]
        self.assertTrue(flags["full_three_heavy_singular_values_computed"])
        self.assertTrue(flags["lightest_heavy_equals_vS_boundary_solved"])
        self.assertFalse(flags["piecewise_threshold_matching_complete"])
        self.assertFalse(flags["whole_v20_model_excluded"])
        self.assertEqual(self.report["n_failed"], 0)

    def test_invalid_yq_rejected_by_underlying_ray(self):
        with self.assertRaises(ValueError):
            spectrum.heavy_spectrum(0.0)


if __name__ == "__main__":
    unittest.main()
