#!/usr/bin/env python3
"""Tests for scalar-α non-uniqueness from flavour/Clebsches."""

from __future__ import annotations

import unittest

import scalar_alpha_flavour_nonuniqueness_v20 as mod


class ScalarAlphaFlavourNonuniquenessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_status_and_flags(self):
        self.assertEqual(
            self.report["status"],
            "SCALAR_ALPHA_PROVEN_NONUNIQUE_FROM_FLAVOUR__TAU_P_OPEN",
        )
        self.assertEqual(self.report["n_failed"], 0)
        flags = self.report["flag"]
        self.assertTrue(flags["scalar_alpha_proven_nonunique_from_flavour"])
        self.assertFalse(flags["alpha_identified_with_yukawa_fit"])
        self.assertTrue(flags["flavour_clebsch_benchmark_used"])
        self.assertTrue(flags["ps_alpha4_template_verified_at_closed_mt"])
        self.assertFalse(flags["live_sarah_or_pyrate_executable_run"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_flavour_and_grid(self):
        flav = self.report["flavour_benchmark"]
        self.assertTrue(flav["available"])
        self.assertGreater(flav["y10_max"], 0.0)
        self.assertGreater(flav["y126_max"], 0.0)
        grid = self.report["closed_mt_alpha_grid"]
        self.assertTrue(grid["template_alpha4_scaling_verified"])
        self.assertTrue(grid["distinct_lifetimes_on_grid"])
        self.assertGreaterEqual(grid["n_pass"], 1)
        self.assertEqual(len(grid["rows"]), len(mod.ALPHA_PROBE))

    def test_identification_rejected(self):
        ident = self.report["identification"]
        self.assertFalse(ident["alpha_identified_with_yukawa_fit"])
        self.assertGreaterEqual(ident["n_obstructions"], 3)
        self.assertTrue(
            self.report["certificate"]["residual_now_closed"][
                "scalar_alpha_not_unique_from_flavour"
            ]
        )


if __name__ == "__main__":
    unittest.main()
