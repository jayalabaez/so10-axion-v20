#!/usr/bin/env python3
"""Tests for piecewise Yukawa RGE with Clebsch thresholds."""

from __future__ import annotations

import unittest

import numpy as np

import yukawa_rge_2loop_v20 as rge


class YukawaRGE2LoopTests(unittest.TestCase):
    def test_clebsch_minus_three_identity(self) -> None:
        h = np.diag([0.01, 0.1, 0.8]).astype(complex)
        f = np.diag([0.001, 0.02, 0.05]).astype(complex)
        match = rge.clebsch_match_from_hf(h, f, eta_i=1.0)
        self.assertTrue(match["clebsch_identity_check"]["Yd_equals_H_plus_F"])
        self.assertTrue(match["clebsch_identity_check"]["Ye_equals_H_minus_3F"])

    def test_zero_yukawas_give_zero_sm_betas(self) -> None:
        z = np.zeros((3, 3), dtype=complex)
        bu, bd, be = rge.sm_2hdm_yukawa_betas(z, z, z, g1=0.4, g2=0.6, g3=1.0)
        self.assertLess(np.linalg.norm(bu), 1e-30)
        self.assertLess(np.linalg.norm(bd), 1e-30)
        self.assertLess(np.linalg.norm(be), 1e-30)

    def test_report_advances_chain_without_two_loop_closure(self) -> None:
        report = rge.build_report()
        self.assertEqual(report["n_failed"], 0)
        self.assertTrue(report["flag"]["clebsch_threshold_matching_implemented"])
        self.assertTrue(report["flag"]["factor_minus_three_lepton_clebsch_applied"])
        self.assertTrue(report["flag"]["piecewise_yukawa_chain_integrated"])
        self.assertFalse(report["flag"]["two_loop_so10_complete"])
        self.assertFalse(report["flag"]["published_210_tensor_contractions"])
        self.assertFalse(
            report["flag"]["piecewise_component_threshold_matching_complete"]
        )


if __name__ == "__main__":
    unittest.main()
