#!/usr/bin/env python3
import unittest

import lambda_lock_cal_g_lift_v20 as mod


class LambdaLockCalGSourceCorrectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_withdrawn_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report)
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertEqual(
            self.report["status"],
            "LAMBDA_LOCK_CAL_G_LIFT_WITHDRAWN__NONSUSY_HESSIAN_OPEN",
        )

    def test_old_claims_are_false(self):
        flags = self.report["flag"]
        self.assertFalse(flags["selected_lambda_lock_raised_to_cal_G_lift"])
        self.assertFalse(flags["cal_G_soft_mode_cleared_at_raised_lock"])
        self.assertFalse(flags["selected_point_not_spoiled_by_lock_raise"])
        self.assertFalse(flags["old_lambda_lock_lift_claim_valid"])
        self.assertTrue(flags["cal_G_susy_gaugino_target_withdrawn"])

    def test_raised_helper_is_only_arithmetic(self):
        out = mod.raised_lambda_lock(0.955, 2.5889)
        self.assertGreater(abs(out["lambda_lock_raised"]), 2.5889)
        self.assertAlmostEqual(
            out["raise_factor"],
            abs(out["lambda_lock_raised"]) / 0.955,
        )
        self.assertFalse(out["physical_lift_proven"])

    def test_compatibility_evaluation_withdrawn(self):
        row = mod.evaluate_cal_g_at_lock(lambda_lock=2.0)
        self.assertTrue(row["withdrawn"])
        self.assertFalse(row["clears_null_tol"])
        self.assertFalse(
            row["with_lambda_lock_embed"][
                "physical_scalar_interpretation_allowed"
            ]
        )

    def test_no_model_overclaim(self):
        self.assertFalse(self.report["flag"]["whole_model_validated"])
        self.assertFalse(self.report["flag"]["whole_model_excluded"])
        self.assertFalse(self.report["flag"]["exact_unique_proton_lifetime"])


if __name__ == "__main__":
    unittest.main()
