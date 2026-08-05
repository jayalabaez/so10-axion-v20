#!/usr/bin/env python3
"""Tests for OPEN_MIXED_10 portal absorption."""

from __future__ import annotations

import unittest

import diagonal_mixed_10_portal_absorption_v20 as mod


class DiagonalMixed10PortalAbsorptionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_executes_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertEqual(
            self.report["status"],
            "OPEN_MIXED_10_ABSORBED_INTO_PORTAL_B__DIAGONAL_NOT_CLAIMED",
        )
        flags = self.report["flags"]
        self.assertTrue(flags["open_mixed_10_absorbed_into_portal"])
        self.assertTrue(flags["diagonal_A_C_not_filled_by_mixed_10"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_portal_identification(self):
        self.assertTrue(self.report["operator"]["charge_allowed"]["all"])
        portal = self.report["portal_identification"]
        self.assertLess(portal["portal_reconstruction_rel_err"], 1e-12)
        self.assertLess(portal["frobenius_match_rel_err"], 1e-12)


if __name__ == "__main__":
    unittest.main()
