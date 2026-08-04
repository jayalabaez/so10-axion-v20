#!/usr/bin/env python3
"""Tests for the signed SO(10) Kronecker M_T^2 audit."""
from __future__ import annotations

import unittest

import so10_kronecker_existence_mt_lock_v20 as mod


class KroneckerMT2AuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()
        cls.ops = {row["name"]: row for row in cls.report["resolved_operators"]}

    def test_status_and_flags(self):
        self.assertEqual(
            self.report["status"],
            "SO10_KRONECKER_SIGNED__FORBIDDEN_CUBICS_OFF__LAMBDA4_CG_OPEN",
        )
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        flags = self.report["flag"]
        self.assertTrue(flags["kronecker_resolved"])
        self.assertTrue(flags["ten2_S_so10_and_charge_allowed"])
        self.assertTrue(flags["forbidden_210_10dag10_removed"])
        self.assertTrue(flags["forbidden_10_126_S_removed"])
        self.assertTrue(flags["forbidden_cubic_contributions_locked_zero"])
        self.assertTrue(flags["lambda4_offdiag_allowed_but_CG_open"])
        self.assertTrue(flags["lambda4_offdiag_not_locked_zero"])
        self.assertFalse(flags["physical_component_CG_complete"])
        self.assertFalse(flags["physical_triplet_spectrum_complete"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_operator_verdicts(self):
        self.assertEqual(
            self.ops["10_H^2 S"]["status"], "ALLOWED_CHARGE_AND_SO10"
        )
        self.assertEqual(
            self.ops["210_H 10_H^dag 10_H"]["status"], "SO10_FORBIDDEN"
        )
        self.assertEqual(
            self.ops["10_H 126bar_H S"]["status"], "SO10_FORBIDDEN"
        )
        self.assertEqual(
            self.ops["210 · 10 · 126 · S"]["status"],
            "ALLOWED_CHARGE_AND_SO10",
        )

    def test_forbidden_cubics_zero_but_lambda4_preserved(self):
        audited = self.report["audited_mt2"]
        self.assertTrue(audited["forbidden_cubic_contributions_zero"])
        self.assertTrue(audited["lambda4_component_slot_preserved"])
        self.assertGreater(audited["n_nonzero_lambda4_scenarios"], 0)
        rows = audited["scenarios"]
        nonzero = [
            row
            for row in rows
            if abs(row["allowed_conditional_inputs"]["lam4_cg"]) > 0.0
        ]
        zero = [
            row
            for row in rows
            if abs(row["allowed_conditional_inputs"]["lam4_cg"]) == 0.0
        ]
        self.assertTrue(
            all(abs(row["mass_squared_matrix_GeV2"][0][1]) > 0.0 for row in nonzero)
        )
        self.assertTrue(
            all(abs(row["mass_squared_matrix_GeV2"][0][1]) == 0.0 for row in zero)
        )
        self.assertTrue(
            all(not row["flag"]["physical_triplet_spectrum_complete"] for row in rows)
        )

    def test_aulakh_without_s_is_pq_forbidden(self):
        self.assertTrue(
            self.report["key_verdicts"][
                "aulakh_210_10_126_pq_forbidden_without_S"
            ]
        )


if __name__ == "__main__":
    unittest.main()
