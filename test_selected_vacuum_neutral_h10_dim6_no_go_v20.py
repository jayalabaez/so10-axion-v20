#!/usr/bin/env python3
import unittest

import selected_vacuum_neutral_h10_dim6_no_go_v20 as mod


class SelectedVacuumNeutralH10Dim6NoGoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_executes_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report)
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertEqual(
            self.report["status"],
            "SELECTED_VACUUM_DIM6_PHASE_LIFTING_NO_GO__DIM7_OR_NEW_VACUUM_REQUIRED",
        )

    def test_exact_weak_dictionary(self):
        states = self.report["weak_state_dictionary"]
        expected = {
            "z67_plus": (0.5, 0.5, 1.0),
            "z67_minus": (-0.5, -0.5, -1.0),
            "z89_plus": (0.5, -0.5, 0.0),
            "z89_minus": (-0.5, 0.5, 0.0),
        }
        for name, values in expected.items():
            self.assertAlmostEqual(states[name]["T3L"], values[0], places=12)
            self.assertAlmostEqual(states[name]["T3R"], values[1], places=12)
            self.assertAlmostEqual(states[name]["Q"], values[2], places=12)
            self.assertLess(states[name]["T3L_eigen_residual"], mod.TOL)
            self.assertLess(states[name]["T3R_eigen_residual"], mod.TOL)
        self.assertLess(self.report["weak_state_gram_max_abs_residual"], mod.TOL)
        self.assertEqual(
            set(self.report["neutral_H10_basis"]["states"]),
            {"z89_plus", "z89_minus"},
        )

    def test_all_neutral_multilinear_coefficients_zero(self):
        audit = self.report["multilinear_metric_audit"]
        self.assertEqual(len(audit["representatives"]), 15)
        self.assertEqual(audit["total_graph_coefficient_evaluations"], 2662)
        self.assertLess(audit["maximum_abs_coefficient"], mod.TOL)
        self.assertTrue(audit["all_coefficients_zero"])
        for row in audit["representatives"]:
            self.assertTrue(row["all_neutral_H_coefficients_zero"], row)
            for assignment in row["assignments"]:
                self.assertTrue(assignment["all_coefficients_zero"], assignment)

    def test_epsilon_completion(self):
        epsilon = self.report["epsilon_completion"]
        self.assertTrue(epsilon["epsilon_sector_reduced_to_metric"])
        self.assertEqual(epsilon["total_one_epsilon_metric_topologies"], 18577)

    def test_scientific_boundary(self):
        flags = self.report["flags"]
        self.assertTrue(flags["exact_neutral_H10_cartesian_dictionary_derived"])
        self.assertTrue(flags["metric_zero_for_arbitrary_neutral_H10_VEV"])
        self.assertTrue(flags["epsilon_sector_reduced_to_metric"])
        self.assertTrue(
            flags["full_selected_vacuum_dimension6_phase_lifting_no_go_proven"]
        )
        self.assertFalse(flags["current_selected_vacuum_fully_phase_stabilized"])
        self.assertTrue(flags["dimension7_or_changed_vacuum_required"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])


if __name__ == "__main__":
    unittest.main()
