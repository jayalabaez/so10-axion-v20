#!/usr/bin/env python3
"""Tests for PQ-axion quotient on the extended form-basis Hessian."""

from __future__ import annotations

import unittest

import extended_hessian_pq_axion_quotient_v20 as mod


class ExtendedHessianPqAxionQuotientTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_executes_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertEqual(
            self.report["status"],
            "EXTENDED_HESSIAN_PQ_AXION_QUOTIENT_READY__FULL_HESSIAN_OPEN",
        )
        flags = self.report["flags"]
        self.assertTrue(flags["pq_axion_quotient_on_extended_hessian"])
        self.assertTrue(flags["gauge_36_and_axion_1_removed"])
        self.assertTrue(flags["kappa_phase_block_injected"])
        self.assertFalse(flags["full_component_hessian_complete"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_projectors_and_spectrum(self):
        self.assertEqual(self.report["embedding"]["total"], 738)
        proj = self.report["projectors"]
        self.assertAlmostEqual(proj["trace_P_G"], 36.0, places=6)
        self.assertAlmostEqual(proj["trace_P_axion"], 1.0, places=6)
        self.assertAlmostEqual(proj["trace_P_phys"], 701.0, places=6)
        self.assertEqual(self.report["kappa_phase"]["axion_phi_integer"], [1, -2])
        ga = self.report["goldstone_axion_projection"]
        self.assertEqual(ga["n_removed"], 37)
        dyn = ga["dynamical_scaled_spectrum"]
        self.assertEqual(dyn["n_zero"], 37)
        self.assertEqual(dyn["n_positive"], 701)
        self.assertEqual(dyn["n_negative"], 0)


if __name__ == "__main__":
    unittest.main()
