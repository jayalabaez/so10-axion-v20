#!/usr/bin/env python3
"""Tests for OPEN_126_54_LOCKING Hermitian fluctuation census."""

from __future__ import annotations

import unittest

import open_126_54_locking_hermitian_fluctuation_census_v20 as mod


class Open12654LockingHermitianCensusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertTrue(
            self.report["flags"]["open_126_54_locking_hermitian_census_ready"]
        )
        self.assertFalse(
            self.report["flags"]["open_126_54_locking_positive_schur_seed"]
        )
        self.assertFalse(self.report["flags"]["cg_120_320_1050_4125_invented"])
        self.assertFalse(self.report["flags"]["whole_model_validated"])

    def test_indefinite_equal_spectrum(self):
        full = self.report["census"]["full_252"]["classification"]
        self.assertTrue(full["indefinite"])
        self.assertEqual(full["n_positive"], full["n_negative"])
        self.assertEqual(full["n_positive"], 252)
        delta = self.report["census"]["delta_r_eigenspace"]["classification"]
        self.assertEqual(delta["n_positive"], 126)
        self.assertEqual(delta["n_negative"], 126)


if __name__ == "__main__":
    unittest.main()
