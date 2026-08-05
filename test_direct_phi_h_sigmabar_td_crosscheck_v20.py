#!/usr/bin/env python3
import unittest

import direct_phi_h_sigmabar_td_crosscheck_v20 as mod


class DirectTensorTDCrosscheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_executes_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report)
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertFalse(
            self.report["flags"]["whole_model_validated"]
        )
        self.assertFalse(
            self.report["flags"]["whole_model_excluded"]
        )

    def test_canonical_dictionary(self):
        self.assertEqual(
            self.report["canonical_dictionary"],
            {
                "P": "p",
                "A": "sqrt(3)*a",
                "W": "sqrt(6)*omega",
            },
        )

    def test_direct_svd_matches_published_td(self):
        self.assertLess(self.report["max_abs_residual"], 1e-12)
        self.assertEqual(
            len(self.report["direct_singular_values"]), 10
        )
        self.assertEqual(
            len(self.report["published_gamma_TD_singular_values"]),
            10,
        )
        self.assertTrue(
            self.report["flags"][
                "published_gamma_TD_magnitudes_matched"
            ]
        )

    def test_correct_target_not_efjx(self):
        self.assertTrue(self.report["checks"]["efjx_not_used"])
        self.assertIn(
            "wrong comparison target", self.report["verdict"]
        )


if __name__ == "__main__":
    unittest.main()
