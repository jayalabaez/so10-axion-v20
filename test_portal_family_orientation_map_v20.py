#!/usr/bin/env python3
import math
import unittest

import portal_family_orientation_map_v20 as orientation


class PortalFamilyOrientationMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = orientation.build_report()
        cls.scan = cls.report["scan"]

    def test_original_direction_is_reproduced_and_survives(self):
        row = self.scan["reference_original_direction"]
        self.assertAlmostEqual(row["lam_Q_F"][0]["re"], 1.0, places=12)
        self.assertAlmostEqual(row["lam_Q_F"][1]["re"], 0.01, places=12)
        self.assertAlmostEqual(row["lam_Q_F"][1]["im"], 0.0, places=12)
        self.assertAlmostEqual(row["NA62_ratio"], 0.32890249466584204, places=12)
        self.assertAlmostEqual(row["TWIST_ratio"], 0.0051281104101177305, places=12)
        self.assertFalse(row["NA62_excluded"])
        self.assertFalse(row["TWIST_excluded_strongest_published_case"])

    def test_phase_periodicity(self):
        y_q = self.scan["configuration"]["ordered_y_Q"]
        bases = orientation.physical.flavour_mass_bases()
        na62_limit, twist_limit = orientation.experimental_limits()
        theta = 0.37
        left = orientation.evaluate_orientation(
            theta, 0.0, y_q=y_q, bases=bases,
            na62_limit=na62_limit, twist_limit=twist_limit,
        )
        right = orientation.evaluate_orientation(
            theta, 2.0 * math.pi, y_q=y_q, bases=bases,
            na62_limit=na62_limit, twist_limit=twist_limit,
        )
        self.assertTrue(math.isclose(left["NA62_ratio"], right["NA62_ratio"], rel_tol=1e-12))
        self.assertTrue(math.isclose(left["TWIST_ratio"], right["TWIST_ratio"], rel_tol=1e-12))

    def test_heavy_spectrum_is_orientation_invariant(self):
        heavy = self.scan["heavy_spectrum"]
        self.assertTrue(heavy["orientation_invariant_at_fixed_norm"])
        self.assertLess(heavy["max_relative_drift_over_orientation_grid"], 1e-10)
        self.assertTrue(math.isclose(heavy["reference_lightest_heavy_over_vS"], 1.0, rel_tol=1e-8))

    def test_empirical_grid_classification_is_locked(self):
        counts = self.scan["counts"]
        self.assertEqual(counts["n_grid_points"], 5856)
        self.assertEqual(counts["n_NA62_excluded"], 5664)
        self.assertEqual(counts["n_NA62_surviving"], 192)
        self.assertAlmostEqual(counts["NA62_excluded_grid_fraction"], 0.9672131147540983, places=15)
        self.assertEqual(counts["n_TWIST_excluded"], 0)
        self.assertEqual(counts["n_TWIST_surviving"], 5856)
        self.assertFalse(counts["grid_fraction_is_probability"])

    def test_na62_extrema_show_orientation_sensitivity(self):
        extrema = self.scan["extrema"]
        low = extrema["min_NA62_ratio"]
        high = extrema["max_NA62_ratio"]
        self.assertLess(low["NA62_ratio"], 1e-20)
        self.assertTrue(math.isclose(low["theta_rad"], math.pi / 2.0, rel_tol=0.0, abs_tol=1e-15))
        self.assertGreater(high["NA62_ratio"], 800.0)
        self.assertTrue(math.isclose(high["theta_rad"], math.pi / 4.0, rel_tol=0.0, abs_tol=1e-15))
        self.assertTrue(math.isclose(high["phi_rad"], math.pi / 2.0, rel_tol=0.0, abs_tol=1e-15))
        self.assertGreater(high["NA62_ratio"] / max(low["NA62_ratio"], 1e-300), 1e30)

    def test_all_sampled_orientations_survive_twist(self):
        extrema = self.scan["extrema"]
        self.assertLess(extrema["max_TWIST_ratio"]["TWIST_ratio"], 0.01)
        self.assertFalse(self.report["flag"]["TWIST_has_excluded_grid_points"])
        self.assertTrue(self.report["flag"]["TWIST_has_surviving_grid_points"])

    def test_invalid_orientation_fails_closed(self):
        for theta in (-0.1, math.pi, math.nan):
            with self.assertRaises(ValueError):
                orientation.family_vector(theta, 0.0)
        with self.assertRaises(ValueError):
            orientation.family_vector(0.2, 0.0, kappa=0.0)

    def test_scope_is_not_promoted(self):
        flags = self.report["flag"]
        self.assertTrue(flags["complex_F1_F2_orientation_plane_scanned"])
        self.assertTrue(flags["NA62_has_excluded_grid_points"])
        self.assertTrue(flags["NA62_has_surviving_grid_points"])
        self.assertFalse(flags["grid_fraction_is_probability"])
        self.assertFalse(flags["full_complex_three_family_orientation_scanned"])
        self.assertFalse(flags["all_portal_magnitudes_and_phases_scanned"])
        self.assertFalse(flags["portal_yukawa_posterior_derived"])
        self.assertFalse(flags["component_specific_uv_chiral_currents_derived"])
        self.assertFalse(flags["whole_v20_model_excluded"])
        self.assertEqual(self.report["n_failed"], 0)


if __name__ == "__main__":
    unittest.main()
