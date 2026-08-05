#!/usr/bin/env python3
import unittest

import selected_ps_singlet_symmetric45_diagnostic_v20 as diag


class PSSingletSymmetric45DiagnosticTests(unittest.TestCase):
    def test_pair_structure(self):
        report = diag.build_report()
        self.assertEqual(report["n_failed"], 0, report)
        self.assertLess(report["pair_norms"]["pxp"], 1e-10)
        self.assertLess(report["pair_norms"]["axa"], 1e-10)
        self.assertGreater(report["pair_norms"]["omegaxomega"], 1e-10)
        self.assertGreater(report["pair_norms"]["pxa"], 1e-10)
        self.assertGreater(report["pair_norms"]["axomega"], 1e-10)

    def test_full_singlet_span_is_nontrivial(self):
        report = diag.build_report()
        self.assertFalse(report["flags"]["full_p_a_omega_span_vanishes"])
        self.assertTrue(report["flags"]["generic_selected_singlet_vacuum_can_activate_45"])
        self.assertGreater(report["equal_combo_norm"], 1e-10)

    def test_fail_closed(self):
        report = diag.build_report()
        self.assertEqual(report["overall_state"], "BLOCKED")
        self.assertTrue(report["flags"]["actual_selected_coefficients_must_be_recomputed_in_source_convention"])
        self.assertTrue(report["flags"]["downstream_revalidation_required"])
        self.assertFalse(report["flags"]["whole_model_validated"])


if __name__ == "__main__":
    unittest.main()
