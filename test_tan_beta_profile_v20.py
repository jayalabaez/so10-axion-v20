#!/usr/bin/env python3
"""Regression tests for the fixed-v_R tan(beta) profile."""

from __future__ import annotations

import json
import math
import unittest
from pathlib import Path

import numpy as np

import tan_beta_profile_v20 as profile


ROOT = Path(__file__).resolve().parent


class TanBetaProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads(
            ROOT.joinpath("TAN_BETA_PROFILE_V20_VERDICT.json").read_text(
                encoding="utf-8"
            )
        )

    def test_coordinate_round_trip(self):
        for tan_beta in (1.500001, 2.0, 10.0, 41.3, 49.0):
            x = profile.beta_coordinate(tan_beta)
            recovered = 1.5 + 48.5 / (1.0 + math.exp(-x))
            self.assertAlmostEqual(recovered, tan_beta, places=10)

    def test_profile_does_not_claim_unique_tan_beta(self):
        best = self.report["best_profile_point"]
        self.assertGreater(best["tan_beta"], 1.5)
        self.assertLess(best["tan_beta"], 50.0)
        self.assertFalse(self.report["unique_tan_beta_demonstrated"])
        self.assertIn("corrected_multistart_reference", self.report)

    def test_saved_best_point_recomputes(self):
        best = self.report["best_profile_point"]
        chi2 = profile.fixed_beta_chi2(
            np.asarray(best["nuisance"], dtype=float),
            best["tan_beta"],
            best["v_r_GeV"],
        )
        self.assertAlmostEqual(chi2, best["chi2"], places=8)

    def test_coefficients_materially_differ_across_profile(self):
        points = self.report["points"]
        ce = [row["fermion_coefficients"]["C_e"] for row in points]
        cp = [row["fermion_coefficients"]["C_p_central"] for row in points]
        cn = [row["fermion_coefficients"]["C_n_central"] for row in points]
        self.assertGreater(max(ce) - min(ce), 1e-2)
        self.assertGreater(max(cp) - min(cp), 1e-2)
        self.assertGreater(max(cn) - min(cn), 1e-2)


if __name__ == "__main__":
    unittest.main()
