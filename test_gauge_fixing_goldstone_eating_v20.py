#!/usr/bin/env python3
"""Tests for unitary gauge / Goldstone eating."""

from __future__ import annotations

import unittest

import gauge_fixing_goldstone_eating_v20 as mod


class GaugeFixingGoldstoneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()
        cls.by_name = {p["name"]: p for p in cls.report["points"]}

    def test_status_and_flags(self):
        self.assertEqual(
            self.report["status"],
            "UNITARY_GAUGE_GOLDSTONE_EATING_COMPLETE__FLAVOUR_ROTATIONS_OPEN",
        )
        self.assertEqual(self.report["n_failed"], 0)
        flags = self.report["flag"]
        self.assertTrue(flags["unitary_gauge_goldstone_eating_complete"])
        self.assertTrue(flags["generator_counts_exact"])
        self.assertTrue(flags["physical_phase_hessian_projected"])
        self.assertFalse(flags["root_by_root_oscillator_basis"])
        self.assertFalse(flags["unique_flavour_rotations_for_XY"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_generator_and_eating_counts(self):
        self.assertEqual(
            self.report["breaking_chain"]["broken"]["SO10_to_SM_total"], 33
        )
        self.assertTrue(self.report["massive_gauge_map"]["matches_broken_generators"])
        self.assertEqual(self.report["massive_gauge_map"]["n_goldstones_eaten"], 33)
        self.assertEqual(self.report["phase_classification"]["n_physical_active"], 3)
        self.assertEqual(self.report["phase_classification"]["n_gauge_fixed_or_eaten"], 4)

    def test_physical_phase_patterns(self):
        lo = self.by_name["locking_only"]["physical_phase"]
        self.assertEqual(lo["n_positive"], 1)
        self.assertEqual(lo["n_zero"], 2)
        self.assertEqual(lo["spectator_zeros_removed"], 4)
        fk = self.by_name["finite_kappa_benchmark"]["physical_phase"]
        self.assertEqual(fk["n_positive"], 2)
        self.assertEqual(fk["n_zero"], 1)

    def test_ew_goldstones(self):
        ew = self.report["phase_classification"]["sm_ew_goldstones"]
        self.assertEqual(ew["n_real"], 3)
        self.assertEqual(ew["class"], "eaten_by_SM")


if __name__ == "__main__":
    unittest.main()
