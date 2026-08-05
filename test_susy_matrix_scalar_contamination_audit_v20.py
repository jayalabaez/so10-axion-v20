#!/usr/bin/env python3
import unittest

import susy_matrix_scalar_contamination_audit_v20 as audit


class SusyMatrixScalarContaminationAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_report()

    def test_audit_executes_cleanly(self):
        self.assertEqual(self.report["n_failed"], 0, self.report)
        self.assertEqual(
            self.report["status"],
            "SUSY_MATRIX_SCALAR_CONTAMINATION_AUDIT_CLEAN",
        )
        self.assertEqual(self.report["overall_state"], "BLOCKED")

    def test_every_known_path_is_withdrawn(self):
        self.assertGreaterEqual(self.report["counts"]["n_paths"], 7)
        self.assertEqual(self.report["counts"]["n_remaining"], 0)
        self.assertEqual(
            self.report["counts"]["n_withdrawn"],
            self.report["counts"]["n_paths"],
        )
        for name, row in self.report["paths"].items():
            self.assertTrue(row["withdrawn"], name)

    def test_direct_tensor_is_retained(self):
        retained = self.report["retained_physics"]
        self.assertEqual(retained["direct_tensor_map_shape"], [10, 126])
        self.assertLess(
            retained["published_TD_max_abs_residual"], 1e-12
        )
        self.assertTrue(self.report["flag"]["direct_tensor_problem_closed"])

    def test_scalar_theory_remains_open(self):
        flags = self.report["flag"]
        self.assertTrue(
            flags["all_known_susy_matrix_scalar_paths_withdrawn"]
        )
        self.assertFalse(flags["physical_scalar_CW_complete"])
        self.assertFalse(flags["full_component_hessian_complete"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])


if __name__ == "__main__":
    unittest.main()
