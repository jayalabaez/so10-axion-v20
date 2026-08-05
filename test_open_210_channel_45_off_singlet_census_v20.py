#!/usr/bin/env python3
"""Tests for off-singlet mixed-45 operator census."""

from __future__ import annotations

import unittest

import open_210_channel_45_off_singlet_census_v20 as mod


class Open210Channel45OffSingletCensusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_executes_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertTrue(self.report["flags"]["off_singlet_45_census_ready"])
        self.assertFalse(self.report["flags"]["off_singlet_45_mode_cg"])
        self.assertFalse(self.report["flags"]["whole_model_validated"])

    def test_census_nontrivial(self):
        slot = self.report["inventory_slot"]
        self.assertEqual(slot["id"], "OPEN_210_CHANNEL_45_OFF_SINGLET")
        self.assertEqual(slot["status"], "PARTIAL_OFF_SINGLET_CENSUS_READY")
        self.assertEqual(
            self.report["census"]["n_nonzero_modes"],
            self.report["census"]["n_off_singlet_modes"],
        )
        self.assertGreater(
            self.report["diagnostic_seed"][
                "OPEN_210_CHANNEL_45_OFF_SINGLET_seed_GeV2"
            ],
            0.0,
        )


if __name__ == "__main__":
    unittest.main()
