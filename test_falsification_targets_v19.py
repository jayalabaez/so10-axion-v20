#!/usr/bin/env python3
"""Tests for branch-scoped falsification numbers."""

import unittest

import falsification_targets_v19 as targets


class FalsificationTargetTests(unittest.TestCase):
    def test_tensor_ceiling(self):
        self.assertAlmostEqual(targets.tensor_ratio_ceiling() / 1.339e-17, 1.0, places=3)

    def test_search_band_and_linewidth_are_not_conflated(self):
        result = targets.haloscope_target()
        self.assertEqual(result["theory_location_band_GHz"], [36.62, 37.60])
        self.assertTrue(33.0 < result["halo_linewidth_kHz"] < 34.0)

    def test_falsifiers_are_benchmark_scoped(self):
        report = targets.build_report()
        self.assertIn("not the discrete-anomaly theorem", report["scope"]["haloscope_null"])
        self.assertIn("post-inflationary", report["scope"]["b_mode_detection"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
