#!/usr/bin/env python3
"""Tests for the conditional portal–Yukawa sector posterior map."""

from __future__ import annotations

import unittest

import portal_yukawa_posterior_v20 as posterior


class PortalYukawaPosteriorTests(unittest.TestCase):
    def test_tiny_grid_runs_and_is_not_a_probability(self) -> None:
        scan = posterior.run_grid(n_theta=3, n_phi=4, n_y=3)
        self.assertEqual(scan["n_points"], 36)
        self.assertFalse(scan["survival_fraction_is_probability"])
        self.assertGreaterEqual(scan["n_surviving"], 0)

    def test_report_refuses_full_uv_posterior(self) -> None:
        report = posterior.build_report()
        self.assertEqual(report["n_failed"], 0)
        self.assertTrue(report["flag"]["portal_sector_posterior_derived"])
        self.assertFalse(report["flag"]["full_portal_yukawa_posterior_derived"])
        self.assertFalse(report["flag"]["survival_fraction_is_probability"])
        self.assertFalse(report["flag"]["unconditional_unique_Cf"])
        self.assertGreater(report["scan"]["n_points"], 100)


if __name__ == "__main__":
    unittest.main()
