#!/usr/bin/env python3
import unittest

import deltar_54_locking_dependency_audit_v20 as mod


class DeltaR54LockingDependencyAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_audit_executes(self):
        self.assertEqual(self.report["n_failed"], 0, self.report)
        self.assertEqual(self.report["overall_state"], "BLOCKED")

    def test_partial_revalidation(self):
        counts = self.report["counts"]
        self.assertGreaterEqual(counts["n_known_consumers"], 10)
        self.assertGreaterEqual(counts["n_revalidated_on_exact_zero"], 5)
        self.assertGreater(counts["n_revalidation_required"], 0)
        self.assertEqual(
            counts["n_revalidated_on_exact_zero"] + counts["n_revalidation_required"],
            counts["n_known_consumers"],
        )
        self.assertEqual(counts["n_missing_files"], 0)
        self.assertEqual(counts["n_dependency_not_detected"], 0)
        flags = self.report["flags"]
        self.assertTrue(flags["all_known_consumers_identified"])
        self.assertFalse(flags["all_consumers_revalidated"])
        self.assertFalse(flags["selected_vacuum_lambda_lock_chain_valid"])
        self.assertFalse(flags["repository_ready_for_release"])

    def test_every_consumer_fail_closed(self):
        for row in self.report["consumers"]:
            self.assertTrue(row["file_exists"], row)
            self.assertTrue(row["dependency_detected"], row)
            self.assertIn(
                row["scientific_status"],
                {"REVALIDATION_REQUIRED", "REVALIDATED_ON_EXACT_ZERO"},
            )
            self.assertFalse(row["can_support_selected_vacuum_locking"])

    def test_whole_model_flags_false(self):
        flags = self.report["flags"]
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])


if __name__ == "__main__":
    unittest.main()
