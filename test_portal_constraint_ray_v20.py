#!/usr/bin/env python3
import math
import unittest

import portal_constraint_ray_v20 as ray


class PortalConstraintRayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = ray.build_report()

    def test_reference_point_is_channel_dependent(self):
        reference = self.report["central_scan"]["reference_yQ_1e_minus_6"]
        self.assertGreater(reference["NA62_ratio"], 1.0)
        self.assertFalse(reference["NA62_survives"])
        self.assertLess(reference["TWIST_ratio"], 1.0)
        self.assertTrue(reference["TWIST_survives_strongest_published_case"])

    def test_all_reported_crossings_recheck(self):
        scan = self.report["central_scan"]
        self.assertGreaterEqual(scan["n_crossings"], 1)
        for crossing in scan["crossings"]:
            self.assertTrue(math.isclose(crossing["NA62_ratio"], 1.0, rel_tol=1e-8))

    def test_unique_monotonic_survival_boundary(self):
        scan = self.report["central_scan"]
        self.assertTrue(scan["na62_ratio_monotonic_nonincreasing"])
        self.assertEqual(scan["n_crossings"], 1)
        boundary = scan["unique_survival_boundary"]
        self.assertIsNotNone(boundary)
        self.assertGreater(boundary["y_Q"], 1.0e-6)
        self.assertLess(boundary["y_Q"], 1.0e-2)
        self.assertTrue(math.isclose(boundary["NA62_ratio"], 1.0, rel_tol=1e-8))

    def test_high_mass_side_survives(self):
        high = self.report["central_scan"]["high_endpoint"]
        self.assertTrue(high["NA62_survives"])
        self.assertLess(high["NA62_ratio"], 1.0)

    def test_form_factor_band_ordering(self):
        band = self.report["form_factor_boundary_band"]
        low = band["f0_minus_1sigma"]["y_Q"]
        central = band["f0_central"]["y_Q"]
        high = band["f0_plus_1sigma"]["y_Q"]
        self.assertLessEqual(low, central)
        self.assertLessEqual(central, high)

    def test_invalid_yq_fails_closed(self):
        for value in (0.0, -1.0, math.inf, math.nan):
            with self.assertRaises(ValueError):
                ray.portal_block(value)

    def test_scope_remains_conditional(self):
        flags = self.report["flag"]
        self.assertTrue(flags["one_dimensional_conditional_ray_scanned"])
        self.assertTrue(flags["central_NA62_survival_boundary_solved"])
        self.assertFalse(flags["full_portal_parameter_space_scanned"])
        self.assertFalse(flags["portal_yukawa_posterior_derived"])
        self.assertFalse(flags["component_specific_uv_chiral_currents_derived"])
        self.assertFalse(flags["whole_v20_model_excluded"])
        self.assertEqual(self.report["n_failed"], 0)


if __name__ == "__main__":
    unittest.main()
