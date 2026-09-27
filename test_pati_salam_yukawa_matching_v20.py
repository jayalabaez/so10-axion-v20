#!/usr/bin/env python3
"""Tests for the one-loop Pati–Salam Yukawa matching layer."""

from __future__ import annotations

import unittest

import numpy as np

import pati_salam_yukawa_matching_v20 as ps


class PatiSalamYukawaMatchingTests(unittest.TestCase):
    def test_ps_betas_vanish_for_zero_yukawas(self) -> None:
        z = np.zeros((3, 3), dtype=complex)
        b10, b126, bR = ps.ps_yukawa_betas(z, z, z, g4=0.5, gL=0.6, gR=0.7)
        self.assertLess(np.linalg.norm(b10), 1e-30)
        self.assertLess(np.linalg.norm(b126), 1e-30)
        self.assertLess(np.linalg.norm(bR), 1e-30)

    def test_report_solves_ps_layer_without_two_loop_closure(self) -> None:
        report = ps.build_report()
        self.assertEqual(report["n_failed"], 0)
        self.assertTrue(report["flag"]["pati_salam_one_loop_yukawa_layer_solved"])
        self.assertTrue(report["flag"]["pati_salam_interval_matching"])
        self.assertFalse(report["flag"]["piecewise_component_threshold_matching_complete"])
        self.assertFalse(report["flag"]["two_loop_so10_complete"])
        self.assertFalse(report["flag"]["uses_so10_beta_across_PS_interval"])

    def test_genuine_two_loop_ps_couplings_unify_at_mgut(self) -> None:
        import two_loop_thresholds_v20 as thresholds

        gauge = thresholds.solve_unification(two_loop=True)
        couplings = ps.ps_gauge_couplings_at_mu(float(gauge["M_GUT_GeV"]), gauge)
        self.assertAlmostEqual(couplings["g4"], couplings["gL"], delta=1e-7)
        self.assertAlmostEqual(couplings["gL"], couplings["gR"], delta=1e-7)
        self.assertFalse(hasattr(ps, "two_loop_thresholds_uses_two_loop"))

    def test_consumers_fail_closed_when_two_loop_anchor_is_unavailable(self) -> None:
        import common_scale_so10_yukawa_v20 as common
        import next_phenomenology_lock_v20 as nxt
        import push_phenomenology_limits_v20 as push
        import two_loop_matrix_flavour_rg_ps_v20 as matrix
        import two_loop_thresholds_v20 as thresholds
        import yukawa_rge_2loop_v20 as yukawa

        original = thresholds._solve_two_loop_uncached

        def _boom():
            raise RuntimeError("injected failure")

        try:
            thresholds._solve_two_loop_uncached = _boom
            thresholds._two_loop_solution.cache_clear()
            self.assertIs(thresholds.solve_unification(two_loop=True)["available"], False)
            consumers = (("push", push), ("ps", ps), ("yukawa", yukawa), ("common", common),
                         ("next_phenomenology_lock", nxt), ("matrix_flavour", matrix))
            for name, module in consumers:
                with self.subTest(consumer=name):
                    report = module.build_report()  # must not raise
                    self.assertGreater(report["n_failed"], 0)
                    self.assertIn("FAILED", report["status"])
        finally:
            thresholds._solve_two_loop_uncached = original
            thresholds._two_loop_solution.cache_clear()
        self.assertIs(thresholds.solve_unification(two_loop=True)["available"], True)


if __name__ == "__main__":
    unittest.main()
