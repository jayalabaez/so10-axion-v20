#!/usr/bin/env python3
"""Tests for Hodge 126bar C-embedding and portal lift."""

from __future__ import annotations

import unittest

import numpy as np

import hodge_126bar_c_embedding_portal_lift_v20 as mod


class Hodge126barCEmbeddingPortalLiftTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_executes_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertEqual(
            self.report["status"],
            "HODGE_126BAR_C_EMBEDDING_PORTAL_LIFT_READY__IM_H_OPEN",
        )
        flags = self.report["flags"]
        self.assertTrue(flags["hodge_126bar_c_embedding_ready"])
        self.assertTrue(flags["portal_b_lifted_to_ambient_504"])
        self.assertFalse(flags["im_H_in_orbit_embedding"])
        self.assertFalse(flags["full_component_hessian_complete"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_frame_and_delta(self):
        frame = self.report["frame"]
        self.assertAlmostEqual(frame["trace_P_126bar"], 252.0, places=6)
        self.assertLess(frame["hodge_minus_i_residual"], 1e-8)
        self.assertLess(frame["projector_matrix_plus_i_residual"], 1e-8)
        self.assertTrue(self.report["delta_r_check"]["in_physical_subspace"])
        self.assertAlmostEqual(self.report["rayleigh_C0"]["abs_error"], 0.0, places=8)

    def test_assemble_api(self):
        a = np.ones(10)
        c = np.linspace(1.0, 2.0, 126)
        out = mod.assemble_h10_sigma_block(
            a_h10=a, c_diag=c, b_10x126=None, m2_210=3.0
        )
        self.assertEqual(out["shape"], [724, 724])
        self.assertFalse(out["portal"]["inserted"])
        eigs = np.linalg.eigvalsh(out["hessian_724"])
        self.assertGreater(float(eigs[0]), 0.0)


if __name__ == "__main__":
    unittest.main()
