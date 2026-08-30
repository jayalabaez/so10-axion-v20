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
        self.assertEqual(report["status"], rge.STATUS)
        self.assertEqual(report["artifact_class"], "diagnostic_only")
        self.assertEqual(report["n_failed"], 0)
        self.assertTrue(report["flag"]["clebsch_threshold_matching_implemented"])
        self.assertTrue(report["flag"]["factor_minus_three_lepton_clebsch_applied"])
        self.assertTrue(report["flag"]["piecewise_yukawa_chain_integrated"])
        self.assertFalse(report["flag"]["two_loop_so10_complete"])
        self.assertFalse(report["flag"]["published_210_tensor_contractions"])
        self.assertFalse(report["flag"]["explicit_two_loop_yukawa_betas"])
        self.assertFalse(
            report["flag"]["source_bound_exact_two_loop_gauge_anchor_used"]
        )
        self.assertTrue(report["flag"]["heuristic_two_loop_gauge_thresholds_used"])
        self.assertTrue(report["flag"]["diagnostic_only_for_physical_G7"])
        self.assertFalse(report["flag"]["physical_G7_closed"])
        self.assertFalse(report["flag"]["mathematical_G7_closed"])
        self.assertFalse(report["flag"]["release_G7_verified"])
        self.assertFalse(report["flag"]["authoritative_renormalizable_G7_closed"])
        self.assertFalse(
            report["flag"]["piecewise_component_threshold_matching_complete"]
        )
        self.assertEqual(
            report["chain"]["gauge_anchor"]["scheme"],
            "heuristic-two-loop-shift-diagnostic",
        )
        self.assertIn("No explicit two-loop Yukawa beta", report["verdict"])


if __name__ == "__main__":
    unittest.main()
