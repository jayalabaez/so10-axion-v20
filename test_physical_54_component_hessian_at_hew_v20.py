#!/usr/bin/env python3
"""Tests for physical 54-component Hessian at hEW=174 GeV."""

from __future__ import annotations

import math
import unittest

import numpy as np

import physical_54_component_hessian_at_hew_v20 as mod


class Physical54ComponentHessianAtHEWTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_executes_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertEqual(
            self.report["status"],
            "PHYSICAL_54_COMPONENT_HESSIAN_AT_HEW_EXECUTED__FULL_HESSIAN_OPEN",
        )
        flags = self.report["flags"]
        self.assertTrue(flags["physical_54_component_hessian_at_hEW"])
        self.assertTrue(flags["Q_H_nonzero"])
        self.assertTrue(flags["selected_vacuum_locking_amplitude_zero"])
        self.assertTrue(flags["OPEN_H10_54_exact_zero"])
        self.assertTrue(flags["OPEN_126_54_LOCKING_holomorphic_kernel_nonzero"])
        self.assertFalse(flags["OPEN_126_54_LOCKING_positive_schur_seed"])
        self.assertFalse(flags["H10_MI_proxy_used"])
        self.assertFalse(flags["full_component_hessian_complete"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_q_h_geometry(self):
        tensors = self.report["tensors"]
        self.assertGreater(tensors["Q_H_frobenius"], 0.0)
        self.assertAlmostEqual(
            tensors["Q_H_unit_frobenius"],
            tensors["Q_H_unit_frobenius_expected_sqrt_9_10"],
            places=12,
        )
        self.assertLess(tensors["Q_Delta_frobenius"], 1e-12)
        self.assertLess(abs(tensors["vacuum_amplitude_QH_dot_QDelta"]), 1e-8)
        self.assertLess(tensors["H10_DHH_frobenius_GeV2"], 1e-6)

    def test_holomorphic_kernel_not_pd_schur(self):
        block = self.report["blocks"]["OPEN_126_54_LOCKING"]
        self.assertEqual(
            block["status"],
            "PHYSICAL_HOLOMORPHIC_KERNEL_FROM_HEW__NOT_PD_SCHUR_SEED",
        )
        self.assertEqual(block["n_nonzero_singular"], 126)
        self.assertFalse(block["positive_hermitian_schur_seed"])
        self.assertGreater(block["s_max_GeV2"], 0.0)
        self.assertLess(
            block["suppression_vs_MI_proxy"],
            1.0e-10,
        )
        self.assertTrue(math.isfinite(block["frobenius_GeV2"]))

    def test_helpers(self):
        ehat = mod.hew_unit_vector()
        self.assertAlmostEqual(float(np.linalg.norm(ehat)), 1.0, places=12)
        q = mod.q54_from_10_vector(ehat)
        self.assertAlmostEqual(mod.frobenius(q), 0.9, places=12)


if __name__ == "__main__":
    unittest.main()
