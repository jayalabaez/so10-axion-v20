#!/usr/bin/env python3
"""Tests for Schur-C alternative channels certificate."""

from __future__ import annotations

import unittest

import schur_c_alternative_channels_certificate_v20 as mod


class SchurCAlternativeChannelsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_defensible_c_retires_locking(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertTrue(self.report["flags"]["schur_c_alternatives_ready"])
        self.assertTrue(
            self.report["flags"]["open_126_54_locking_retired_as_c_seed"]
        )
        self.assertGreater(self.report["composed"]["C_min_GeV2"], 0.0)
        self.assertIn(
            "OPEN_126_54_LOCKING", self.report["composed"]["retired_from_C"]
        )
        self.assertEqual(
            self.report["C_channels"]["OPEN_126_54_LOCKING"]["status"],
            "INDEFINITE_NOT_PD_SCHUR_C",
        )


if __name__ == "__main__":
    unittest.main()
