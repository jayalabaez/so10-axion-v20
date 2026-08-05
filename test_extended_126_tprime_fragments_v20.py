#!/usr/bin/env python3
"""Tests for extended 126 T' fragment 4×4 M_T."""

from __future__ import annotations

import unittest

import extended_126_tprime_fragments_v20 as mod


class Extended126TprimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()
        cls.ledger = cls.report["fragment_ledger"]

    def test_status_and_flags(self):
        self.assertEqual(
            self.report["status"],
            "EXTENDED_126_TPRIME_FRAGMENTS_LOCKED__4x4_MT",
        )
        self.assertEqual(self.report["n_failed"], 0)
        flags = self.report["flag"]
        self.assertTrue(flags["complete_126bar_fragment_multiplicity_locked"])
        self.assertTrue(flags["working_basis_4x4"])
        self.assertTrue(flags["tprime_included"])
        self.assertTrue(flags["t3_126_absent_without_126_H"])
        self.assertFalse(flags["invented_unpublished_cg_values"])
        self.assertFalse(flags["whole_model_excluded"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])

    def test_basis_four(self):
        self.assertEqual(
            self.ledger["working_basis"],
            ["T_10", "Tbar_10", "T_126", "Tprime_126"],
        )
        for row in self.report["scenarios"]:
            self.assertEqual(len(row["mass_matrix_GeV"]), 4)
            self.assertEqual(len(row["mass_matrix_GeV"][0]), 4)
            self.assertIn("Tprime_126", row["lightest_fractions"])

    def test_t3_t5_excluded(self):
        names = [e["aulakh_label"] for e in self.ledger["excluded_or_integrated_out"]]
        self.assertIn("t3", names)
        self.assertIn("t5", names)

    def test_phase_hessian(self):
        ph = self.report["locking_phase_hessian"]
        self.assertEqual(ph["n_positive"], 0)
        self.assertEqual(ph["n_zero"], 3)
        self.assertEqual(ph["A_54"], 0.0)

    def test_some_excluded_some_survive(self):
        self.assertGreater(self.report["n_excluded_by_ps_mu_K0"], 0)
        self.assertLess(
            self.report["n_excluded_by_ps_mu_K0"], self.report["n_scenarios"]
        )


if __name__ == "__main__":
    unittest.main()
