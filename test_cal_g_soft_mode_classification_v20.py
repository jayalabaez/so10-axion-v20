#!/usr/bin/env python3
import unittest

import cal_g_soft_mode_classification_v20 as mod


class CalGSourceCorrectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_withdrawn_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report)
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertEqual(
            self.report["status"],
            "CAL_G_SCALAR_CLASSIFICATION_WITHDRAWN__SUSY_GAUGINO_MATRIX",
        )

    def test_no_scalar_classification(self):
        flags = self.report["flag"]
        self.assertFalse(flags["cal_G_soft_mode_classified"])
        self.assertTrue(flags["cal_G_susy_gaugino_diagnostic_only"])
        self.assertFalse(flags["old_goldstone_classification_valid"])
        self.assertEqual(
            flags["primary_label"],
            "withdrawn_susy_fermion_gaugino_diagnostic",
        )

    def test_slices_are_withdrawn(self):
        for row in self.report["slices"].values():
            self.assertTrue(row["withdrawn"])
            self.assertFalse(
                row["classification"][
                    "physical_scalar_classification_allowed"
                ]
            )

    def test_helpers_preserve_software_compatibility(self):
        p = mod.hilbert_g_params(
            a=1.0,
            omega=1.0,
            p=1.0,
            m_i=1.0,
            m_gut=1.0,
            lam=0.1,
            eta=0.1,
            goldstone_compatible=True,
        )
        self.assertIn("diagnostic", p["physical_use"])
        self.assertTrue(p["goldstone_compatible_requested"])

    def test_no_model_overclaim(self):
        self.assertFalse(self.report["flag"]["whole_model_validated"])
        self.assertFalse(self.report["flag"]["whole_model_excluded"])
        self.assertFalse(self.report["flag"]["exact_unique_proton_lifetime"])


if __name__ == "__main__":
    unittest.main()
