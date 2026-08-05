#!/usr/bin/env python3
import unittest

import tau_p_hessian_residual_closure_v20 as mod


class TauPHessianSourceCorrectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_withdrawn_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report)
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertEqual(
            self.report["status"],
            "TAU_P_HESSIAN_CLOSURE_WITHDRAWN__DIRECT_NONSUSY_HESSIAN_OPEN",
        )

    def test_hessian_residuals_reopened(self):
        hess = self.report["certificate"]["hessian_residuals_closed"]
        self.assertTrue(hess)
        self.assertTrue(all(value is False for value in hess.values()))
        still = self.report["certificate"]["residual_still_open"]
        for name in mod.RESIDUAL_STILL_OPEN:
            self.assertTrue(still[name], name)

    def test_lifetime_is_conditional(self):
        life = self.report["lifetime"]
        self.assertTrue(life["conditional_only"])
        if life["selected_tau_e_years"] is not None:
            self.assertGreater(life["selected_tau_e_years"], 0.0)

    def test_old_uniqueness_flags_are_false(self):
        flags = self.report["flag"]
        self.assertFalse(flags["hessian_residuals_folded_into_tau_p"])
        self.assertFalse(flags["full_component_hessian_residual_closed"])
        self.assertFalse(flags["tau_p_unique_under_full_uv_stack"])
        self.assertFalse(flags["tau_p_unique_under_hessian_closed_stack"])
        self.assertTrue(flags["imported_susy_hessian_withdrawn"])

    def test_no_model_overclaim(self):
        self.assertFalse(self.report["flag"]["exact_unique_proton_lifetime"])
        self.assertFalse(self.report["flag"]["whole_model_validated"])
        self.assertFalse(self.report["flag"]["whole_model_excluded"])


if __name__ == "__main__":
    unittest.main()
