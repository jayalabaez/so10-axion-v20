#!/usr/bin/env python3
"""Tests for open-gap closure module."""

from __future__ import annotations

import unittest

import close_open_gaps_v20 as gaps


class OpenGapClosureTests(unittest.TestCase):
    def test_conditional_cf_and_not_unconditional(self):
        cf = gaps.conditional_unique_cf()
        self.assertTrue(cf["flag"]["conditional_unique_Cf"])
        self.assertFalse(cf["flag"]["unconditional_unique_Cf"])
        self.assertIn("C_e", cf["unique_point_under_principle"])

    def test_fcnc_theorem_aligned_vs_counterexample(self):
        th = gaps.fcnc_absence_theorem()
        self.assertTrue(th["flag"]["proved_under_alignment"])
        self.assertFalse(th["flag"]["proved_for_arbitrary_portals"])
        self.assertGreater(
            th["counterexample_generation_dependent"]["lepton_offdiag"], 1e-3
        )

    def test_detection_not_claimed(self):
        det = gaps.ghz_detection_package()
        self.assertFalse(det["discovery_claim"])
        self.assertTrue(det["injection_recovery"]["pass"])


if __name__ == "__main__":
    unittest.main()
