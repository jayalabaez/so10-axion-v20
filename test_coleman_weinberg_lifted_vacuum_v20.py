#!/usr/bin/env python3
"""Tests for Coleman–Weinberg corrections on the lifted vacuum."""

from __future__ import annotations

import unittest

import coleman_weinberg_lifted_vacuum_v20 as mod


class ColemanWeinbergLiftedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_status_and_flags(self):
        self.assertEqual(
            self.report["status"],
            "COLEMAN_WEINBERG_LIFTED_VACUUM_EVALUATED__STABILITY_CONDITIONAL",
        )
        self.assertEqual(self.report["n_failed"], 0)
        flags = self.report["flag"]
        self.assertTrue(flags["coleman_weinberg_evaluated"])
        self.assertTrue(flags["msbar_scheme"])
        self.assertTrue(flags["goldstones_excluded_unitary_gauge"])
        self.assertTrue(flags["phi17_uv_sector_split"])
        self.assertTrue(flags["one_loop_stability_conditional_on_counterterms"])
        self.assertFalse(flags["one_loop_stability_unconditional"])
        self.assertFalse(flags["full_sm_irrep_cw_spectrum"])
        self.assertFalse(flags["unique_vacuum_selected"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_cw_finite_and_gauge_map(self):
        cw = self.report["coleman_weinberg"]
        self.assertTrue(abs(cw["V1_gut_ps_GeV4"]) > 0.0)
        self.assertEqual(self.report["mass_ledger"]["n_goldstones_excluded"], 33)

    def test_tadpole_scan_recorded(self):
        scan = self.report["tadpole_curvature_scan"]
        self.assertEqual(scan["sector"], "gut_ps_mi_excluding_phi17")
        self.assertGreater(scan["tadpole_rel_GUT"], 0.0)


if __name__ == "__main__":
    unittest.main()
