#!/usr/bin/env python3
import unittest

import cal_g_portal_decision_v20 as mod


class CalGPortalSourceCorrectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_withdrawn_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report)
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertEqual(
            self.report["status"],
            "CAL_G_PORTAL_DECISION_WITHDRAWN__NONSUSY_SINGLET_HESSIAN_OPEN",
        )

    def test_decision_is_undetermined(self):
        dec = self.report["decision"]
        self.assertTrue(dec["withdrawn"])
        self.assertEqual(
            dec["label"],
            "undetermined_until_direct_nonsusy_singlet_hessian",
        )
        self.assertIsNone(dec["extra_new_portal_required"])
        self.assertFalse(dec["existing_lambda_lock_sufficient_in_principle"])
        self.assertIsNone(dec["mu_crit_GeV"])
        self.assertIsNone(dec["lambda_lock_crit_abs"])

    def test_old_lift_claim_is_false(self):
        flags = self.report["flag"]
        self.assertFalse(flags["cal_G_portal_decision_resolved"])
        self.assertFalse(flags["existing_lambda_lock_sufficient_in_principle"])
        self.assertFalse(flags["old_lambda_lock_lift_claim_valid"])
        self.assertTrue(flags["cal_G_susy_gaugino_target_withdrawn"])

    def test_dimensional_helpers_remain_consistent(self):
        m_i, m_gut = 1e12, 1e16
        mu = mod.lambda_lock_soft_mass_GeV(
            2.0, m_i=m_i, m_gut=m_gut
        )
        recovered = mod.lambda_lock_for_soft_mass(
            mu, m_i=m_i, m_gut=m_gut
        )
        self.assertAlmostEqual(recovered, 2.0, places=9)

    def test_no_model_overclaim(self):
        self.assertFalse(self.report["flag"]["whole_model_validated"])
        self.assertFalse(self.report["flag"]["whole_model_excluded"])
        self.assertFalse(self.report["flag"]["exact_unique_proton_lifetime"])


if __name__ == "__main__":
    unittest.main()
