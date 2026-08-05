#!/usr/bin/env python3
import unittest

import selected_vacuum_lambda4_portal_null_audit_v20 as mod


class SelectedVacuumLambda4PortalNullTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_executes(self):
        self.assertEqual(self.report["n_failed"], 0, self.report)
        self.assertEqual(self.report["overall_state"], "BLOCKED")

    def test_delta_is_null_for_all_singlets(self):
        vacuum = self.report["vacuum_contraction"]
        for value in vacuum["basis_image_norms"].values():
            self.assertLess(value, 1e-12)
        self.assertLess(vacuum["selected_image_norm"], 1e-6)
        self.assertLess(vacuum["matrix_image_norm"], 1e-6)

    def test_full_map_remains_nonzero(self):
        fluctuation = self.report["fluctuation_map"]
        self.assertEqual(fluctuation["shape"], [10, 126])
        self.assertGreater(fluctuation["rank"], 0)
        self.assertGreater(fluctuation["largest_singular_value_GeV"], 0.0)
        self.assertTrue(fluctuation["nonzero"])

    def test_vacuum_claims_withdrawn(self):
        flags = self.report["flags"]
        self.assertTrue(flags["selected_DeltaR_is_portal_null_vector"])
        self.assertFalse(flags["selected_vacuum_lambda4_amplitude_nonzero"])
        self.assertTrue(flags["full_fluctuation_portal_map_nonzero"])
        self.assertFalse(flags["historical_reduced_lambda4_vacuum_term_physical"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])


if __name__ == "__main__":
    unittest.main()
