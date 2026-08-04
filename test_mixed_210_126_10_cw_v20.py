#!/usr/bin/env python3
import unittest

import mixed_210_126_10_cw_v20 as mod


class CorrectedMixedBlockAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_source_correction_executes(self):
        self.assertEqual(self.report["n_failed"], 0, self.report)
        self.assertEqual(
            self.report["status"],
            "AULAKH_EFJX_SOURCE_CORRECTED__SCALAR_CW_WITHDRAWN",
        )

    def test_gauge_parameter_is_not_gamma(self):
        p = mod.reference_params(1e12, 1e16, 0.55)
        self.assertEqual(p["g_gauge"], 0.55)
        p["gamma"] = 99.0
        before = mod.aulakh_E(p)
        p["gamma"] = -27.0
        after = mod.aulakh_E(p)
        self.assertTrue((before == after).all())
        del p["g_gauge"]
        with self.assertRaises(KeyError):
            mod.aulakh_E(p)

    def test_no_false_scalar_cw(self):
        self.assertTrue(self.report["mixed_cw"]["withdrawn"])
        self.assertEqual(self.report["mixed_cw"]["n_entries"], 0)
        self.assertEqual(self.report["mixed_cw"]["V1_GeV4"], 0.0)
        self.assertFalse(self.report["flag"]["mixed_210_126_10_in_cw"])
        self.assertTrue(self.report["flag"]["E_F_J_X_gauge_gaugino_diagnostic_only"])

    def test_no_overclaim(self):
        self.assertFalse(self.report["flag"]["whole_model_validated"])
        self.assertFalse(self.report["flag"]["whole_model_excluded"])


if __name__ == "__main__":
    unittest.main()
