#!/usr/bin/env python3
"""Tests for common-scale flavour re-fit and one-loop SO(10) Yukawa layer."""

from __future__ import annotations

import unittest

import common_scale_so10_yukawa_v20 as common


class CommonScaleSO10Tests(unittest.TestCase):
    def test_scaled_targets_are_finite_and_clipped(self) -> None:
        scaled = common.rge_scaled_mass_targets()
        self.assertGreater(scaled["scale_GeV"], 1e10)
        for key, value in scaled["targets"].items():
            self.assertTrue(np_isfinite(value), msg=key)
            ratio = scaled["ratios_MI_over_low_clipped"][key]
            self.assertGreaterEqual(ratio, 0.05)
            self.assertLessEqual(ratio, 5.0)

    def test_so10_betas_vanish_for_zero_matrices(self) -> None:
        import numpy as np

        z = np.zeros((3, 3), dtype=complex)
        bh, bf = common.so10_yukawa_betas(z, z, g10=0.5)
        self.assertLess(np.linalg.norm(bh), 1e-30)
        self.assertLess(np.linalg.norm(bf), 1e-30)

    def test_threshold_layer_refuses_two_loop_claim(self) -> None:
        layer = common.so10_threshold_yukawa_layer()
        self.assertTrue(layer["flag"]["one_loop_so10_HF_layer_solved"])
        self.assertTrue(
            layer["flag"]["piecewise_threshold_yukawa_matching_complete"]
        )
        self.assertFalse(layer["flag"]["two_loop_so10_complete"])
        self.assertFalse(layer["flag"]["includes_210_yukawa_sector"])

    def test_common_scale_refit_runs(self) -> None:
        refit = common.optimize_common_scale(starts=4, seed=11)
        self.assertLess(refit["best_point"]["chi2"], 1e8)
        self.assertFalse(refit["flag"]["unconditional_unique_Cf"])
        self.assertFalse(refit["flag"]["unique_tan_beta"])

    def test_aggregate_report(self) -> None:
        report = common.build_report()
        self.assertEqual(report["n_failed"], 0)
        self.assertFalse(report["flag"]["two_loop_so10_complete"])
        self.assertFalse(report["flag"]["unconditional_unique_Cf"])
        self.assertTrue(
            report["flag"]["piecewise_threshold_yukawa_matching_complete"]
        )


def np_isfinite(value: float) -> bool:
    import math

    return math.isfinite(float(value))


if __name__ == "__main__":
    unittest.main()
