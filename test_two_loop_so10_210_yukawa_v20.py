#!/usr/bin/env python3
"""Tests for two-loop SO(10)+210 Yukawa next steps."""

from __future__ import annotations

import unittest

import numpy as np

import two_loop_so10_210_yukawa_v20 as two


class TwoLoopSO10210Tests(unittest.TestCase):
    def test_two_loop_betas_reduce_to_one_loop_at_vanishing_yukawa(self) -> None:
        z = np.zeros((3, 3), dtype=complex)
        b1h, b1f = two.so10_yukawa_betas_one_loop(z, z, g10=0.5)
        b2h, b2f = two.so10_yukawa_betas_two_loop(z, z, g10=0.5)
        self.assertLess(np.linalg.norm(b1h), 1e-30)
        self.assertLess(np.linalg.norm(b1f), 1e-30)
        # Pure gauge^4 × Y vanishes when Y=0 as well.
        self.assertLess(np.linalg.norm(b2h), 1e-30)
        self.assertLess(np.linalg.norm(b2f), 1e-30)

    def test_two_loop_differs_from_one_loop_for_nonzero_yukawa(self) -> None:
        h = np.diag([0.01, 0.1, 0.8]).astype(complex)
        f = np.diag([0.001, 0.02, 0.05]).astype(complex)
        b1h, _ = two.so10_yukawa_betas_one_loop(h, f, g10=0.55)
        b2h, _ = two.so10_yukawa_betas_two_loop(h, f, g10=0.55)
        self.assertGreater(np.linalg.norm(b2h - b1h), 0.0)

    def test_layer_sets_two_loop_without_fudge(self) -> None:
        layer = two.two_loop_so10_210_layer()
        self.assertTrue(layer["flag"]["two_loop_so10_complete"])
        self.assertTrue(layer["flag"]["explicit_two_loop_yukawa_betas"])
        self.assertFalse(layer["flag"]["uses_10pct_damping_fudge"])
        self.assertTrue(layer["flag"]["includes_210_gauge_threshold"])
        self.assertFalse(layer["yukawa_content"]["includes_210_as_yukawa"])

    def test_uv_fixing_remains_conditional(self) -> None:
        uv = two.uv_fixing_conditional_point()
        self.assertFalse(uv["flag"]["unconditional_unique_Cf"])
        self.assertIn("principle", uv)

    def test_fcnc_finite_absence_not_claimed(self) -> None:
        fcnc = two.fcnc_exact_limit_and_likelihood()
        self.assertTrue(
            fcnc["flag"]["exact_epsilon_limit_fcnc_absence_proved"]
        )
        self.assertFalse(
            fcnc["flag"]["actual_finite_model_fcnc_absence_proved"]
        )
        self.assertTrue(fcnc["flag"]["experimental_FCNC_bound_applied"])

    def test_aggregate_report(self) -> None:
        report = two.build_report()
        self.assertEqual(report["n_failed"], 0)
        self.assertTrue(report["flag"]["two_loop_so10_complete"])
        self.assertFalse(report["flag"]["unconditional_unique_Cf"])
        self.assertFalse(
            report["flag"]["actual_finite_model_fcnc_absence_proved"]
        )


if __name__ == "__main__":
    unittest.main()
