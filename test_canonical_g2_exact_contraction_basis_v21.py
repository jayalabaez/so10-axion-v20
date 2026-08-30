from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

import canonical_g2_exact_contraction_basis_v21 as basis


class CanonicalG2ExactContractionBasisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads(basis.OUT.read_text(encoding="utf-8"))

    def test_frozen_report_passes_all_exact_checks(self):
        checks = basis.validate(self.report)
        self.assertEqual(len(checks), 5)
        self.assertTrue(all(value is True for value in checks.values()))
        self.assertEqual(self.report["n_failed"], 0)
        self.assertEqual(self.report["canonical_invariant_direction_count"], 891)

    def test_all_modular_minors_are_nonzero_and_exactly_hashed(self):
        for row in self.report["sectors"]:
            with self.subTest(count_tuple=row["count_tuple"]):
                self.assertNotEqual(basis.determinant_mod(row["minor"]), 0)
                self.assertEqual(
                    basis.determinant_mod(row["minor"]),
                    row["minor_determinant_mod_prime"],
                )
                self.assertEqual(basis.sha(row["minor"]), row["minor_sha256"])

    def test_hardest_sector_is_exact_rank_95(self):
        row = next(
            value
            for value in self.report["sectors"]
            if value["count_tuple"] == [2, 0, 0, 2, 2]
        )
        self.assertEqual(row["target_multiplicity"], 95)
        self.assertEqual(len(row["basis_circuits"]), 95)
        self.assertEqual(row["minor_determinant_mod_prime"], 678)

    def test_parity_sector_contains_metric_and_epsilon_directions(self):
        row = next(
            value
            for value in self.report["sectors"]
            if value["count_tuple"] == [4, 1, 1, 0, 0]
        )
        kinds = [value["kind"] for value in row["basis_circuits"]]
        self.assertEqual(kinds.count("metric"), 10)
        self.assertEqual(kinds.count("epsilon"), 7)
        self.assertEqual(row["minor_determinant_mod_prime"], 85)

    def test_graph_mutation_is_rejected(self):
        forged = copy.deepcopy(self.report)
        forged["sectors"][0]["basis_circuits"][0]["kind"] = "forged"
        self.assertFalse(
            basis.validate(forged)[
                "all_basis_circuits_are_exact_allowed_delta_or_epsilon_graphs"
            ]
        )

    def test_singular_minor_is_rejected(self):
        forged = copy.deepcopy(self.report)
        row = next(value for value in forged["sectors"] if value["target_multiplicity"] > 1)
        row["minor"][0] = [0] * row["target_multiplicity"]
        row["minor_sha256"] = basis.sha(row["minor"])
        self.assertFalse(
            basis.validate(forged)[
                "all_105_modular_minors_have_nonzero_exact_determinant"
            ]
        )

    def test_missing_G1_row_mapping_is_rejected(self):
        forged = copy.deepcopy(self.report)
        forged["g1_row_projection_map"].pop()
        self.assertFalse(
            basis.validate(forged)[
                "all_168_G1_rows_map_to_their_exact_group_basis_and_singlet_dressing"
            ]
        )


if __name__ == "__main__":
    unittest.main()
