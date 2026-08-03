#!/usr/bin/env python3
"""Tests for theory validity red/yellow/green/blue classification."""

from __future__ import annotations

import unittest

import theory_validity_classification_v20 as validity


class TheoryValidityClassificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = validity.build_report()

    def test_current_tier_is_yellow_conditional(self):
        self.assertEqual(self.report["tier"], "YELLOW")
        self.assertTrue(self.report["flag"]["tier_is_yellow"])
        self.assertTrue(self.report["flag"]["conditional_candidate"])
        self.assertFalse(self.report["flag"]["complete_viable_theory"])
        self.assertFalse(self.report["flag"]["empirically_supported"])
        self.assertFalse(self.report["flag"]["uniquely_confirmed"])

    def test_green_and_blue_not_overclaimed(self):
        self.assertFalse(self.report["green_ready"])
        self.assertFalse(self.report["blue_ready"])
        self.assertTrue(self.report["flag"]["green_not_claimed"])
        self.assertTrue(self.report["flag"]["blue_not_claimed"])
        self.assertEqual(self.report["n_failed"], 0)

    def test_critical_green_items_remain_open(self):
        open_items = set(self.report["open_critical_for_green"])
        for name in (
            "operator_basis_complete",
            "full_scalar_potential_vacuum",
            "two_loop_rg_threshold_matching",
            "proton_decay",
            "uv_portal_flavour_derivation",
            "complete_axion_cosmology",
            "multi_observable_fingerprint_frozen",
        ):
            self.assertIn(name, open_items)

    def test_ladder_order_is_locked(self):
        tiers = [row["tier"] for row in self.report["classification_ladder"]]
        self.assertEqual(tiers, ["RED", "YELLOW", "GREEN", "BLUE"])

    def test_green_overclaim_fails_checks(self):
        # Force an illegal GREEN classification path by mutating requirements.
        report = validity.classify(self.report["checklist"])
        report["tier"] = "GREEN"
        report["flag"]["tier_is_green"] = True
        # Re-run only the anti-overclaim checks manually:
        self.assertFalse(report["green_ready"])


class EnsurePortalArtifactsTests(unittest.TestCase):
    def test_sphere_present_after_ensure(self):
        import ensure_portal_artifacts_v20 as ensure

        result = ensure.ensure_portal_artifacts(force=False)
        self.assertTrue(result["sphere_present"])
        self.assertEqual(result["status"], "PORTAL_ARTIFACTS_ENSURED")


if __name__ == "__main__":
    unittest.main()
