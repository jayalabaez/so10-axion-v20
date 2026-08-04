#!/usr/bin/env python3
import unittest

import current_main_repair_closure_v20 as mod


class RepairClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_execution(self):
        self.assertEqual(self.report["execution_failures"], [])
        self.assertEqual(self.report["hard_theory_failures"], [])

    def test_reduced_breakpoints_resolved(self):
        self.assertTrue(
            all(self.report["resolved_breakpoints"].values()),
            self.report["resolved_breakpoints"],
        )
        self.assertTrue(self.report["flags"]["reduced_sector_repaired"])

    def test_full_theory_remains_fail_closed(self):
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertTrue(self.report["remaining_blockers"]["full_component_nonsusy_hessian"])
        self.assertTrue(self.report["remaining_blockers"]["full_tensor_two_loop_betas"])
        self.assertTrue(self.report["remaining_blockers"]["exact_unique_proton_lifetime"])
        self.assertFalse(self.report["flags"]["whole_model_validated"])


if __name__ == "__main__":
    unittest.main()
