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

    def test_executable_breakpoints_resolved(self):
        self.assertTrue(
            all(self.report["resolved_breakpoints"].values()),
            self.report["resolved_breakpoints"],
        )
        self.assertTrue(self.report["flags"]["executable_breakpoints_repaired"])

    def test_invariant_ledger_completeness_claim_is_falsified(self):
        numerical = self.report["numerical"]
        self.assertEqual(numerical["historical_invariant_total"], 25)
        self.assertGreaterEqual(numerical["corrected_guaranteed_invariant_floor"], 37)
        self.assertEqual(numerical["missing_norm_quartics"], 6)
        self.assertEqual(numerical["multiplicity_deficits"], 5)
        self.assertTrue(self.report["flags"]["historical_basis_claim_falsified"])
        self.assertTrue(
            self.report["remaining_blockers"]["complete_mixed_rep_invariant_enumeration"]
        )
        self.assertTrue(
            self.report["remaining_blockers"]["enlarged_potential_reminimization"]
        )

    def test_exact_goldstone_problem_resolved(self):
        numerical = self.report["numerical"]
        self.assertEqual(numerical["goldstone_count"], 33)
        self.assertEqual(numerical["unbroken_stabilizer_dimension"], 12)
        self.assertEqual(numerical["so6_stabilizer_dimension"], 8)
        self.assertEqual(numerical["so4_stabilizer_dimension"], 4)
        self.assertTrue(self.report["flags"]["goldstone_problem_resolved"])

    def test_full_theory_remains_fail_closed(self):
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertTrue(self.report["remaining_blockers"]["full_component_nonsusy_hessian"])
        self.assertTrue(self.report["remaining_blockers"]["full_tensor_two_loop_betas"])
        self.assertTrue(self.report["remaining_blockers"]["exact_unique_proton_lifetime"])
        self.assertFalse(self.report["flags"]["whole_model_validated"])


if __name__ == "__main__":
    unittest.main()
