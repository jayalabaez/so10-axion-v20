#!/usr/bin/env python3
"""Tests for reduced-amplitude free-extrema solve."""

from __future__ import annotations

import unittest

import reduced_amplitude_free_extrema_v20 as mod


class ReducedAmplitudeFreeExtremaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_executes_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertTrue(self.report["flags"]["reduced_free_extrema_solved"])
        self.assertTrue(self.report["flags"]["selected_near_soft_matched_minimum"])
        self.assertFalse(self.report["flags"]["full_invariant_ring_extrema"])
        self.assertFalse(self.report["flags"]["whole_model_validated"])

    def test_soft_anchors_bare_may_drift(self):
        self.assertAlmostEqual(self.report["couplings"]["lam4"], 0.0, places=12)
        self.assertLess(self.report["max_relative_shift"]["with_soft"], 1.0e-2)
        self.assertGreater(self.report["max_relative_shift"]["no_soft"], 0.1)


if __name__ == "__main__":
    unittest.main()
