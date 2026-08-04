#!/usr/bin/env python3
import unittest

import mixed_rep_enlarged_floor_basis_v20 as mod


class EnlargedFloorBasisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_report_executes(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])

    def test_signed_guaranteed_floor_is_34(self):
        counts = self.report["counts"]
        self.assertEqual(counts["historical_ledger_claimed_total"], 25)
        self.assertEqual(counts["mechanical_locking_completion_total"], 26)
        self.assertEqual(
            counts["mechanical_augmented_total_before_signed_corrections"], 37
        )
        self.assertEqual(
            counts["signed_base_total_after_forbidden_and_unproven_removal"], 23
        )
        self.assertEqual(counts["new_norm_products"], 6)
        self.assertEqual(counts["new_independent_tensor_channels"], 5)
        self.assertEqual(counts["signed_guaranteed_floor_total"], 34)

    def test_signed_corrections(self):
        corrections = {row["name"]: row for row in self.report["signed_corrections"]}
        self.assertEqual(
            corrections["210_H 10_H^dag 10_H"]["signed_floor_multiplicity"],
            0,
        )
        self.assertEqual(corrections["210_H^3"]["signed_floor_multiplicity"], 1)
        self.assertEqual(
            corrections["210_H 126bar_H^dag 126bar_H"][
                "signed_floor_multiplicity"
            ],
            1,
        )

    def test_appended_entries_are_unique(self):
        appended = self.report["guaranteed_floor_basis"]["appended"]
        names = [row["name"] for row in appended]
        self.assertEqual(len(names), 11)
        self.assertEqual(len(names), len(set(names)))

    def test_exact_witnesses_are_nonzero(self):
        determinants = self.report["exact_witness_determinants"]
        self.assertEqual(len(determinants), 5)
        self.assertTrue(all(int(value) != 0 for value in determinants.values()))

    def test_scope_remains_fail_closed(self):
        flags = self.report["flag"]
        self.assertTrue(flags["mechanical_floor37_rejected"])
        self.assertTrue(flags["canonical_signed_floor_34_emitted"])
        self.assertTrue(flags["forbidden_210_10dag10_removed"])
        self.assertFalse(flags["full_unfiltered_molien_haar_series"])
        self.assertFalse(flags["full_tensor_normalizations"])
        self.assertFalse(flags["whole_model_excluded"])


if __name__ == "__main__":
    unittest.main()
