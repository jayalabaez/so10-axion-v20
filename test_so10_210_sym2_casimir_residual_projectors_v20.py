#!/usr/bin/env python3
"""Tests for Sym²(210) Casimir residual ledger."""

from __future__ import annotations

import unittest

import so10_210_sym2_casimir_residual_projectors_v20 as mod


class Sym2CasimirResidualTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_c2_calibrated_and_degenerate_block(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertAlmostEqual(self.report["c2_on_210"]["target"], 96.0)
        self.assertLess(self.report["c2_on_210"]["max_abs_error"], 1e-6)
        self.assertTrue(self.report["flags"]["770_1050_1050bar_casimir_degenerate"])
        self.assertFalse(self.report["flags"]["closes_full_1050_mode_cg"])
        self.assertFalse(self.report["flags"]["whole_model_validated"])
        self.assertAlmostEqual(
            self.report["casimir_table"]["residual_by_irrep"]["4125"]["C2"], 192.0
        )


if __name__ == "__main__":
    unittest.main()
