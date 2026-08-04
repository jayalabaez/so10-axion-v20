#!/usr/bin/env python3
"""Tests for mixed-rep charge+SO(10) filtered Hilbert series."""

from __future__ import annotations

import unittest

import mixed_rep_hilbert_series_v20 as mod


class MixedRepHilbertSeriesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_status_and_flags(self):
        self.assertEqual(
            self.report["status"],
            "MIXED_REP_FILTERED_HILBERT_SERIES_CLOSED__UNFILTERED_MOLIEN_OPEN",
        )
        self.assertEqual(self.report["n_failed"], 0)
        flags = self.report["flag"]
        self.assertTrue(
            flags["mixed_rep_charge_so10_filtered_renorm_hilbert_closed"]
        )
        self.assertTrue(flags["mixed_rep_full_hilbert_series"])
        self.assertFalse(flags["mixed_rep_unfiltered_molien_haar_series"])
        self.assertTrue(flags["kronecker_forbidden_channels_excluded"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_basis_and_generating_function(self):
        b = self.report["filtered_basis"]
        self.assertTrue(b["complete_filtered_renorm_basis"])
        self.assertGreaterEqual(b["n_invariants_total"], 20)
        self.assertIn("t^2", b["generating_function_filtered"])
        self.assertIn("t^3", b["generating_function_filtered"])
        self.assertIn("t^4", b["generating_function_filtered"])
        grades = b["multiplicity_by_grade"]
        self.assertEqual(grades["t2"], 5)  # 210+10+126+S+Phi17 masses
        self.assertGreaterEqual(grades["t3"], 2 + 1 + 2 + 1)  # 210^3 + portals
        self.assertGreaterEqual(grades["t4"], 4)

    def test_forbidden_excluded(self):
        included_names = {
            e["name"] for e in self.report["filtered_basis"]["included"]
        }
        for bad in ("10_H 126bar_H S", "126bar_H^2 S", "bare_10_H^2"):
            self.assertNotIn(bad, included_names)
        self.assertIn(
            "210 · 10 · 126 · S",
            included_names,
        )


if __name__ == "__main__":
    unittest.main()
