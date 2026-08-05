#!/usr/bin/env python3
import unittest

import tau_p_ultimate_residual_checklist_v20 as mod


class TauPUltimateSourceCorrectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_corrected_fail_closed_status(self):
        self.assertEqual(self.report["n_failed"], 0, self.report)
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertEqual(
            self.report["status"],
            "TAU_P_CHECKLIST_CORRECTED__EFJX_CLOSURES_REOPENED",
        )

    def test_false_closures_are_reopened(self):
        flags = self.report["flag"]
        self.assertFalse(flags["ultimate_residual_checklist_folded"])
        self.assertFalse(flags["all_post_hessian_residuals_closed"])
        self.assertTrue(flags["EFJX_false_closures_reopened"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_only_source_corrections_are_closed(self):
        closed = self.report["certificate"]["residual_now_closed"]
        self.assertTrue(closed["scalar_alpha_not_unique_from_flavour"])
        self.assertTrue(closed["efjx_gauge_gamma_source_collision_identified"])
        self.assertTrue(closed["old_efjx_cgc_bound_withdrawn"])
        still = self.report["certificate"]["residual_still_open"]
        self.assertTrue(still)
        self.assertTrue(all(still.values()))
        self.assertIsNone(
            self.report["certificate"]["c_cgc_needed_abs_approx"]
        )

    def test_historical_lifetime_is_conditional(self):
        life = self.report["lifetime"]
        self.assertTrue(life["conditional_only"])
        if life["selected_tau_e_years"] is not None:
            self.assertGreater(life["selected_tau_e_years"], 0.0)


if __name__ == "__main__":
    unittest.main()
