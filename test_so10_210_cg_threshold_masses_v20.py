#!/usr/bin/env python3
"""Tests for 210 CG PS-singlet normalization + SM threshold masses."""

from __future__ import annotations

import unittest

import so10_210_cg_threshold_masses_v20 as mod


class So10210CgThresholdTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()
        cls.ledger = cls.report["invariant_cg_ledger"]

    def test_status_and_flags(self):
        self.assertEqual(
            self.report["status"],
            "210_CG_PS_SINGLETS_NORMALIZED__SM_THRESHOLD_MASSES_BUILT",
        )
        self.assertEqual(self.report["n_failed"], 0)
        flags = self.report["flag"]
        self.assertTrue(flags["ps_singlet_sector_normalized"])
        self.assertTrue(flags["published_cg_transcribed"])
        self.assertTrue(flags["sm_irrep_threshold_ledger_built"])
        self.assertFalse(flags["hilbert_series_certificate"])
        self.assertFalse(flags["complete_independent_invariant_basis"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_ledger_mix_of_normalized_and_open(self):
        self.assertGreaterEqual(self.ledger["n_normalized_or_transcribed"], 5)
        self.assertGreaterEqual(self.ledger["n_open_full_basis"], 1)
        statuses = {e["status"] for e in self.ledger["entries"]}
        self.assertIn("NORMALIZED_ON_PS_SINGLETS", statuses)
        self.assertIn("OPEN_FULL_COMPONENT_BASIS", statuses)

    def test_cg_weights_and_thresholds(self):
        w = self.report["cg_weighted_210"]
        self.assertGreater(w["eff_210_for_10_GeV"], 0.0)
        self.assertGreater(w["eff_210_for_126_GeV"], 0.0)
        thr = self.report["sm_irrep_thresholds"]
        self.assertGreaterEqual(thr["n_entries"], 8)
        self.assertTrue(
            any("triplet" in e["irrep"].lower() for e in thr["entries"])
        )

    def test_soft_stationarity(self):
        self.assertTrue(self.report["ps_singlet_potential"]["stationarity_with_soft_shifts"])


if __name__ == "__main__":
    unittest.main()
