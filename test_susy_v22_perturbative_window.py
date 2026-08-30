from __future__ import annotations

import json
import unittest
from fractions import Fraction

import susy_v22_perturbative_window as window


class SusyV22PerturbativeWindowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = window.build_report()

    def test_exact_beta_and_window(self) -> None:
        self.assertEqual(self.report["SO10"]["b_one_loop"], 272)
        self.assertTrue(self.report["checks"]["coupling_is_finite_through_1p5_MGUT"])
        self.assertTrue(self.report["checks"]["one_loop_Landau_pole_occurs_before_2_MGUT"])

    def test_log_bounds_enclose_diagnostic_values(self) -> None:
        lo, hi = window.ln_bounds(Fraction(3, 2))
        self.assertLess(lo, hi)
        self.assertLess(hi - lo, Fraction(1, 10**30))
        self.assertLess(lo, Fraction(405466, 10**6))
        self.assertGreater(hi, Fraction(405465, 10**6))

    def test_does_not_overclaim(self) -> None:
        b = self.report["claim_boundary"]
        self.assertTrue(b["gauge_one_loop_window_closed"])
        self.assertFalse(b["all_dimensionless_couplings_perturbative"])
        self.assertFalse(b["canonical_G4_closed"])

    def test_outputs_fresh(self) -> None:
        self.assertEqual(json.loads(window.OUT_JSON.read_text(encoding="utf-8")), self.report)
        self.assertEqual(window.OUT_MD.read_text(encoding="utf-8"), window.markdown(self.report))


if __name__ == "__main__": unittest.main()
