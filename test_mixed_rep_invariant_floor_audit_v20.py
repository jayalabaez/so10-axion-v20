#!/usr/bin/env python3
import unittest

import mixed_rep_invariant_floor_audit_v20 as mod


class InvariantOmissionAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_report_executes(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])

    def test_norm_product_omissions(self):
        self.assertEqual(len(self.report["guaranteed_norm_quartics"]), 15)
        self.assertEqual(len(self.report["missing_norm_products"]), 6)

    def test_multiplicity_deficits(self):
        deficits = self.report["multiplicity_deficits"]
        self.assertEqual(len(deficits), 5)
        self.assertTrue(all(row["proven_lower_bound"] >= 2 for row in deficits))
        self.assertTrue(
            all(row["exact_integer_determinant"] != 0 for row in deficits)
        )

    def test_exact_tensor_contractions_have_rank_two(self):
        ranks = self.report["numerical_independence"]
        self.assertTrue(
            all(row["evaluation_rank"] == 2 for row in ranks.values()), ranks
        )

    def test_mechanical_augmentation_is_not_final_signed_floor(self):
        counts = self.report["counts"]
        flags = self.report["flag"]
        self.assertEqual(counts["historical_upstream_invariants_total"], 25)
        self.assertEqual(counts["after_locking_modulus_overlay"], 26)
        self.assertEqual(counts["additional_renormalizable_floor"], 11)
        self.assertEqual(
            counts["mechanical_augmented_total_before_signed_corrections"], 37
        )
        self.assertTrue(flags["mechanical_augmented_total_not_signed_floor"])
        self.assertFalse(flags["guaranteed_invariant_floor_constructed"])

    def test_scope(self):
        flags = self.report["flag"]
        self.assertFalse(flags["historical_filtered_basis_complete"])
        self.assertTrue(flags["historical_complete_filtered_basis_claim_falsified"])
        self.assertTrue(flags["omission_set_constructed"])
        self.assertFalse(flags["full_unfiltered_molien_haar_series"])
        self.assertFalse(flags["whole_model_excluded"])


if __name__ == "__main__":
    unittest.main()
