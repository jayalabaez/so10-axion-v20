#!/usr/bin/env python3
"""Tests for reduced quartic co-positivity / Schur BFB."""

from __future__ import annotations

import unittest

import reduced_quartic_copositivity_bfb_v20 as mod


class ReducedQuarticCopositivityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_executes_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertTrue(self.report["flags"]["reduced_quartic_copositive"])
        self.assertTrue(self.report["flags"]["reduced_quartic_spectral_pd"])
        self.assertTrue(self.report["flags"]["schur_portal_pd"])
        self.assertFalse(self.report["flags"]["full_invariant_ring_bfb"])
        self.assertFalse(self.report["flags"]["whole_model_validated"])

    def test_spectral_and_mc(self):
        self.assertGreater(self.report["spectral"]["min_eig"], 0.0)
        self.assertGreaterEqual(
            self.report["monte_carlo_copositivity"]["min_xTLx"], -1e-8
        )
        self.assertGreater(self.report["schur_portal"]["schur_margin"], 0.0)


if __name__ == "__main__":
    unittest.main()
