#!/usr/bin/env python3
"""Tests for the SO(10) Goldstone nullspace projector."""

from __future__ import annotations

import unittest

import numpy as np

import so10_goldstone_nullspace_projector_v20 as mod


class GoldstoneNullspaceProjectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_executes_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertEqual(
            self.report["status"],
            "SO10_GOLDSTONE_NULLSPACE_PROJECTOR_READY__FULL_HESSIAN_OPEN",
        )
        flags = self.report["flags"]
        self.assertTrue(flags["goldstone_nullspace_projector_ready"])
        self.assertTrue(flags["exact_33_goldstone_rank"])
        self.assertFalse(flags["full_component_field_space"])
        self.assertFalse(flags["full_component_hessian_complete"])
        self.assertFalse(
            flags["root_by_root_33_goldstone_projection_on_dynamical_hessian"]
        )
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_orbit_and_projectors(self):
        orb = self.report["orbit"]
        self.assertEqual(orb["goldstone_rank"], 33)
        self.assertEqual(orb["physical_complement_dimension"], 681)
        self.assertEqual(self.report["embedding"]["total"], 714)
        proj = self.report["projectors"]
        self.assertAlmostEqual(proj["trace_P_G"], 33.0, places=6)
        self.assertAlmostEqual(proj["trace_P_phys"], 681.0, places=6)
        self.assertLess(proj["P_G_idempotence_residual"], 1e-8)
        synth = self.report["synthetic_validation"]
        self.assertEqual(synth["n_zero_after_reproject"], 33)
        self.assertEqual(synth["n_positive_after_reproject"], 681)
        self.assertEqual(synth["n_negative_after_reproject"], 0)

    def test_api_project_hessian(self):
        info = mod.combined_tangent_matrix()
        frame = mod.goldstone_frame_from_tangent(info["matrix"])["frame"]
        projs = mod.projectors(frame, info["n_field_components"])
        rng = np.random.default_rng(1)
        h = rng.normal(size=(714, 714))
        h = 0.5 * (h + h.T)
        hp = mod.project_hessian(h, projs["P_phys"])
        # Goldstone directions are exact nulls of the projected Hessian.
        null_block = frame.T @ hp @ frame
        self.assertLess(float(np.linalg.norm(null_block)), 1e-8)


if __name__ == "__main__":
    unittest.main()
