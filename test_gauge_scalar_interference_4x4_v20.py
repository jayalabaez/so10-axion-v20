#!/usr/bin/env python3
"""Tests for gauge–scalar interference with physical 4×4 mixings."""

from __future__ import annotations

import math
import unittest

import conditional_mt_interference_v20 as cmt
import gauge_scalar_interference_4x4_v20 as mod


class GaugeScalar4x4InterferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_status_and_flags(self):
        self.assertEqual(
            self.report["status"],
            "GAUGE_SCALAR_INTERFERENCE_WITH_PHYSICAL_4x4_MIXINGS",
        )
        self.assertEqual(self.report["n_failed"], 0)
        flags = self.report["flag"]
        self.assertTrue(flags["gauge_scalar_interference_with_4x4_mixings"])
        self.assertTrue(flags["physical_eigenvector_fractions_used"])
        self.assertTrue(flags["tprime_included_in_interference"])
        self.assertTrue(flags["relative_phase_is_envelope_not_derived"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_basis_four(self):
        self.assertEqual(
            self.report["basis"],
            ["T_10", "Tbar_10", "T_126", "Tprime_126"],
        )
        for row in self.report["scenarios"]:
            self.assertEqual(len(row["lightest_fractions"]), 4)
            self.assertIn("Tprime_126", row["lightest_fractions"])

    def test_some_excluded_some_survive(self):
        self.assertGreater(self.report["n_excluded_by_ps_mu_K0"], 0)
        self.assertLess(
            self.report["n_excluded_by_ps_mu_K0"], self.report["n_scenarios"]
        )
        self.assertGreater(
            self.report["n_excluded_by_constructive_SK_e_pi0_from_ps"], 0
        )
        self.assertLess(
            self.report["n_excluded_by_constructive_SK_e_pi0_from_ps"],
            self.report["n_scenarios"],
        )

    def test_interference_envelope_ordering(self):
        t_c = cmt.interference_lifetime_years(1.0e35, 1.0e35, 1.0)
        t_i = cmt.interference_lifetime_years(1.0e35, 1.0e35, 0.0)
        self.assertLess(t_c, t_i)

    def test_mixing_weighted_yeff(self):
        fracs = {"T_10": 0.5, "Tbar_10": 0.0, "T_126": 0.5, "Tprime_126": 0.0}
        y = mod.mixing_weighted_yeff(fracs, {"10_H": 0.1, "126bar_H": 0.1})
        self.assertAlmostEqual(y, 0.1, places=12)
        y2 = mod.mixing_weighted_yeff(fracs, {"10_H": 0.0, "126bar_H": 0.2})
        self.assertAlmostEqual(y2, 0.2 * math.sqrt(0.5), places=12)


if __name__ == "__main__":
    unittest.main()
