#!/usr/bin/env python3
import unittest

import selected_vacuum_lambda4_dependency_audit_v20 as mod


class SelectedVacuumLambda4DependencyAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_executes(self):
        self.assertEqual(self.report["n_failed"], 0, self.report)
        self.assertEqual(self.report["overall_state"], "BLOCKED")

    def test_partial_revalidation(self):
        counts = self.report["counts"]
        self.assertGreaterEqual(counts["n_revalidation_required"], 10)
        self.assertGreaterEqual(counts["n_retained_fluctuation_results"], 3)
        self.assertGreaterEqual(counts["n_revalidated"], 2)
        self.assertEqual(counts["n_missing_files"], 0)
        self.assertEqual(counts["n_undetected_dependencies"], 0)
        flags = self.report["flags"]
        self.assertTrue(flags["all_known_selected_vacuum_consumers_identified"])
        self.assertFalse(flags["all_selected_vacuum_consumers_revalidated"])
        self.assertTrue(flags["fluctuation_portal_results_retained"])
        self.assertFalse(flags["historical_lambda4_tachyon_valid"])
        self.assertFalse(flags["repository_ready_for_release"])

    def test_status_categories(self):
        for row in self.report["revalidation_required"]:
            self.assertTrue(row["file_exists"], row)
            self.assertTrue(row["dependency_detected"], row)
            self.assertEqual(row["scientific_status"], "REVALIDATION_REQUIRED")
        for row in self.report["revalidated"]:
            self.assertTrue(row["file_exists"], row)
            self.assertTrue(row["dependency_detected"], row)
            self.assertEqual(
                row["scientific_status"], "REVALIDATED_ON_SELECTED_VACUUM_NULL"
            )
        for row in self.report["retained_fluctuation_results"]:
            self.assertTrue(row["file_exists"], row)
            self.assertTrue(row["dependency_detected"], row)
            self.assertEqual(row["scientific_status"], "RETAINED_FLUCTUATION_RESULT")

    def test_whole_model_flags_false(self):
        self.assertFalse(self.report["flags"]["whole_model_validated"])
        self.assertFalse(self.report["flags"]["whole_model_excluded"])


if __name__ == "__main__":
    unittest.main()
