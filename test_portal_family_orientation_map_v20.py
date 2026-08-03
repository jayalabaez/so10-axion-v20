#!/usr/bin/env python3
import math
import unittest

import portal_family_orientation_map_v20 as orientation


class PortalFamilyOrientationMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = orientation.build_report()
        cls.scan = cls.report["scan"]

    def test_original_direction_is_reproduced(self):
        row = self.scan["reference_original_direction"]
        self.assertAlmostEqual(row["lam_Q_F"][0]["re"], 1.0, places=12)
        self.assertAlmostEqual(row["lam_Q_F"][1]["re"], 0.01, places=12)
        self.assertAlmostEqual(row["lam_Q_F"][1]["im"], 0.0, places=12)

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
        self.assertTrue(
            math.isclose(
                heavy["reference_lightest_heavy_over_vS"], 1.0, rel_tol=1e-8
            )
        )

    def test_grid_accounting(self):
        counts = self.scan["counts"]
        self.assertEqual(
            counts["n_NA62_excluded"] + counts["n_NA62_surviving"],
            counts["n_grid_points"],
        )
        self.assertEqual(
            counts["n_TWIST_excluded"] + counts["n_TWIST_surviving"],
            counts["n_grid_points"],
        )
        self.assertFalse(counts["grid_fraction_is_probability"])

    def test_extrema_are_finite_and_ordered(self):
        extrema = self.scan["extrema"]
        for channel in ("NA62", "TWIST"):
            low = extrema[f"min_{channel}_ratio"][f"{channel}_ratio"]
            high = extrema[f"max_{channel}_ratio"][f"{channel}_ratio"]
            self.assertTrue(math.isfinite(low) and low >= 0.0)
            self.assertTrue(math.isfinite(high) and high >= low)

    def test_invalid_orientation_fails_closed(self):
        for theta in (-0.1, math.pi, math.nan):
            with self.assertRaises(ValueError):
                orientation.family_vector(theta, 0.0)
        with self.assertRaises(ValueError):
            orientation.family_vector(0.2, 0.0, kappa=0.0)

    def test_scope_is_not_promoted(self):
        flags = self.report["flag"]
        self.assertTrue(flags["complex_F1_F2_orientation_plane_scanned"])
        self.assertFalse(flags["grid_fraction_is_probability"])
        self.assertFalse(flags["full_complex_three_family_orientation_scanned"])
        self.assertFalse(flags["all_portal_magnitudes_and_phases_scanned"])
        self.assertFalse(flags["portal_yukawa_posterior_derived"])
        self.assertFalse(flags["component_specific_uv_chiral_currents_derived"])
        self.assertFalse(flags["whole_v20_model_excluded"])
        self.assertEqual(self.report["n_failed"], 0)


if __name__ == "__main__":
    unittest.main()
