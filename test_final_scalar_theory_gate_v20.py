#!/usr/bin/env python3
import unittest

import final_scalar_theory_gate_v20 as mod


class FinalScalarTheoryGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_execution(self):
        self.assertEqual(self.report["execution_failures"], [])
        self.assertEqual(self.report["hard_theory_failures"], [])

    def test_all_executable_breakpoints_are_resolved(self):
        self.assertTrue(
            all(self.report["resolved_breakpoints"].values()),
            self.report["resolved_breakpoints"],
        )

    def test_historical_point_is_excluded_and_not_perturbatively_rescued(self):
        flags = self.report["flags"]
        numerical = self.report["numerical"]
        self.assertTrue(flags["historical_lambda4_benchmark_excluded"])
        self.assertTrue(
            flags[
                "historical_lambda4_benchmark_not_rescuable_with_floor37_perturbative_even_H_terms"
            ]
        )
        self.assertLess(
            numerical["historical_direct_HH_curvature_GeV2"], -1.0e30
        )
        self.assertGreater(
            numerical["required_over_floor37_perturbative_allowance"], 1.0e20
        )
        self.assertLess(
            numerical["best_case_floor37_rescued_HH_curvature_GeV2"], 0.0
        )

    def test_latest_main_valid_results_are_retained(self):
        flags = self.report["flags"]
        self.assertTrue(flags["live_pyrate_artifacts_validated"])
        self.assertTrue(flags["scalar_alpha_nonuniqueness_proven"])
        self.assertTrue(flags["latest_main_proxy_selected_point_closures_invalidated"])
        self.assertNotIn(
            "live_sarah_or_pyrate_run", self.report["remaining_blockers"]
        )
        self.assertTrue(
            self.report["remaining_blockers"][
                "cal_G_lift_revalidation_on_physical_EW_survival_point"
            ]
        )
        self.assertTrue(
            self.report["remaining_blockers"]["lambda4_CGC_live_encoding"]
        )
        self.assertTrue(
            self.report["remaining_blockers"]["dim6_lambda_lock_live_encoding"]
        )

    def test_survival_region_exists_but_model_remains_blocked(self):
        flags = self.report["flags"]
        self.assertTrue(flags["reduced_survival_region_exists"])
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertTrue(
            self.report["remaining_blockers"][
                "new_odd_H_tensor_channel_or_hierarchy_mechanism"
            ]
        )
        self.assertTrue(
            self.report["remaining_blockers"]["full_component_nonsusy_hessian"]
        )
        self.assertTrue(
            self.report["remaining_blockers"]["exact_unique_proton_lifetime"]
        )
        self.assertFalse(flags["whole_model_excluded"])
        self.assertFalse(flags["whole_model_validated"])


if __name__ == "__main__":
    unittest.main()
