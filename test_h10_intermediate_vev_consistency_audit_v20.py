#!/usr/bin/env python3
import unittest

import h10_intermediate_vev_consistency_audit_v20 as mod


class H10IntermediateVevAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_audit_executes(self):
        self.assertEqual(self.report["n_failed"], 0, self.report)
        self.assertEqual(self.report["overall_state"], "BLOCKED")

    def test_no_singlet(self):
        branch = self.report["pati_salam_branching"]
        self.assertEqual(sum(branch["dimensions"]), 10)
        self.assertFalse(branch["contains_PS_singlet"])
        self.assertFalse(branch["contains_SM_singlet"])

    def test_proxy_withdrawal(self):
        flags = self.report["flags"]
        self.assertTrue(flags["H10_eff_MI_is_bookkeeping_proxy_only"])
        self.assertFalse(flags["legacy_A54_v10eff_MI_physical"])
        self.assertFalse(flags["legacy_isotropic_54_mass_seed_physical"])
        self.assertTrue(flags["exact_54_projectors_retained"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])


if __name__ == "__main__":
    unittest.main()
