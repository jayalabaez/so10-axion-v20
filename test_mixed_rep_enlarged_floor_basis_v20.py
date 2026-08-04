#!/usr/bin/env python3
import unittest

import mixed_rep_enlarged_floor_basis_v20 as mod


class EnlargedFloorBasisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_report_executes(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])

    def test_guaranteed_floor_is_37(self):
        counts = self.report["counts"]
        self.assertEqual(counts["historical_ledger_total"], 25)
        self.assertEqual(counts["locking_completion_total"], 26)
        self.assertEqual(counts["new_norm_products"], 6)
        self.assertEqual(counts["new_independent_tensor_channels"], 5)
        self.assertEqual(counts["guaranteed_floor_total"], 37)

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
        self.assertTrue(flags["canonical_floor_37_emitted"])
        self.assertFalse(flags["full_unfiltered_molien_haar_series"])
        self.assertFalse(flags["full_tensor_normalizations"])
        self.assertFalse(flags["whole_model_excluded"])


if __name__ == "__main__":
    unittest.main()
