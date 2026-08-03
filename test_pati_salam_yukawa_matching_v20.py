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


if __name__ == "__main__":
    unittest.main()
