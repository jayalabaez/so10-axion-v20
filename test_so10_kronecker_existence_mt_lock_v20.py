#!/usr/bin/env python3
"""Tests for SO(10) Kronecker existence + locked M_T."""

from __future__ import annotations

import unittest

import so10_kronecker_existence_mt_lock_v20 as mod


class KroneckerMTLockTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()
        cls.ops = {o["name"]: o for o in cls.report["resolved_operators"]}

    def test_status_and_flags(self):
        self.assertEqual(
            self.report["status"],
            "SO10_KRONECKER_RESOLVED__MT_MIX_LOCKED_OFF__CG_NORMS_OPEN",
        )
        self.assertEqual(self.report["n_failed"], 0)
        flags = self.report["flag"]
        self.assertTrue(flags["kronecker_resolved"])
        self.assertTrue(flags["ten2_S_so10_and_charge_allowed"])
        self.assertTrue(flags["ten_126_S_so10_forbidden"])
        self.assertTrue(flags["mt_offdiag_locked_zero"])
        self.assertTrue(flags["aulakh_offdiag_not_imported_pq"])
        self.assertFalse(flags["invented_unpublished_cg_normalizations"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_operator_verdicts(self):
        self.assertEqual(self.ops["10_H^2 S"]["status"], "ALLOWED_CHARGE_AND_SO10")
        self.assertEqual(self.ops["10_H 126bar_H S"]["status"], "SO10_FORBIDDEN")
        self.assertEqual(self.ops["126bar_H^2 S"]["status"], "SO10_FORBIDDEN")

    def test_all_m12_zero(self):
        self.assertTrue(self.report["locked_mt"]["all_M12_zero"])
        for row in self.report["locked_mt"]["scenarios"]:
            self.assertEqual(row["mass_matrix_GeV"][0][1], 0.0)

    def test_aulakh_pq(self):
        self.assertTrue(
            self.report["key_verdicts"]["aulakh_210_10_126_pq_forbidden_in_v20"]
        )


if __name__ == "__main__":
    unittest.main()
