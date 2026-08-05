#!/usr/bin/env python3
import unittest

import so10_210_symmetric_product_source_audit_v20 as audit


class SymmetricProductSourceAuditTests(unittest.TestCase):
    def test_exact_dimension_closure(self):
        report = audit.build_report()
        self.assertEqual(report["n_failed"], 0, report)
        self.assertEqual(report["symmetric_product"]["dimension"], 22155)
        self.assertEqual(report["symmetric_product"]["decomposition_dimension"], 22155)

    def test_missing_sectors_are_recovered(self):
        report = audit.build_report()
        names = {row["name"] for row in report["symmetric_product"]["irreps"]}
        self.assertTrue({"45", "1050bar", "8910", "5940"}.issubset(names))
        self.assertEqual(report["superseded_blocker"]["old_residual_dimension"], 5945)
        self.assertEqual(report["symmetric_product"]["true_residual_dimension"], 21845)

    def test_fail_closed_reclassification(self):
        report = audit.build_report()
        self.assertEqual(report["overall_state"], "BLOCKED")
        self.assertTrue(report["flags"]["source_decomposition_corrected"])
        self.assertTrue(report["flags"]["old_1050_blocker_superseded"])
        self.assertTrue(report["flags"]["downstream_revalidation_required"])
        self.assertFalse(report["flags"]["g1_closed"])
        self.assertFalse(report["flags"]["g2_closed"])
        self.assertFalse(report["flags"]["whole_model_validated"])

    def test_published_norm_identity_not_overclaimed(self):
        report = audit.build_report()
        identity = report["published_1050_norm_identity"]
        self.assertTrue(identity["can_close_210_only_quartic_invariant_after_normalization"])
        self.assertFalse(identity["normalization_reconciliation_complete"])
        self.assertFalse(identity["closes_full_1050_mode_cg"])


if __name__ == "__main__":
    unittest.main()
