#!/usr/bin/env python3
"""Tests for 210 radial/cubic PS-singlet fill."""

from __future__ import annotations

import unittest

import diagonal_210_radial_cubic_ps_singlet_v20 as mod


class Diagonal210RadialCubicPsSingletTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_executes_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertTrue(self.report["flags"]["open_210_radial_ps_singlet_filled"])
        self.assertFalse(self.report["flags"]["off_singlet_210_channel_cg"])
        self.assertFalse(self.report["flags"]["whole_model_validated"])
        self.assertGreater(self.report["mass"]["mu2_P210_GeV2"], 0.0)
        self.assertIn("OPEN_210_CHANNEL_1050", self.report["still_open_slots"])
        self.assertIn("OPEN_210_CHANNEL_54", self.report["filled_slots"])
        self.assertIn("OPEN_210_CHANNEL_45", self.report["filled_slots"])
        self.assertIn("OPEN_210_CHANNEL_45_OFF_SINGLET", self.report["filled_slots"])
        self.assertIn("OPEN_210_CHANNEL_210", self.report["filled_slots"])
        self.assertNotIn("OPEN_210_CHANNEL_54", self.report["still_open_slots"])
        self.assertNotIn("OPEN_210_CHANNEL_210", self.report["still_open_slots"])
        self.assertNotIn(
            "OPEN_210_CHANNEL_45_OFF_SINGLET", self.report["still_open_slots"]
        )
        self.assertGreater(self.report["channel_54"]["seed_GeV2"], 0.0)
        self.assertGreater(self.report["channel_210"]["seed_GeV2"], 0.0)
        self.assertGreater(self.report["channel_45_off_singlet"]["seed_GeV2"], 0.0)
        self.assertTrue(self.report["flags"]["open_210_channel_54_ps_singlet_seed"])
        self.assertTrue(self.report["flags"]["open_210_channel_45_same_field_vanishes"])
        self.assertTrue(self.report["flags"]["open_210_channel_45_symmetric_source_reopened"])
        self.assertTrue(self.report["flags"]["open_210_channel_45_off_singlet_census"])
        self.assertTrue(self.report["flags"]["open_210_channel_45_off_singlet_sm_qn"])
        self.assertEqual(
            self.report["filled_slots"]["OPEN_210_CHANNEL_45"]["status"],
            "PARTIAL_ANTISYM_VANISHES__SYMMETRIC_SOURCE_REOPENED",
        )
        self.assertTrue(self.report["channel_45"]["symmetric_source_reopened"])
        self.assertTrue(self.report["remaining_blockers"]["symmetric_45_quartic_in_potential"])
        self.assertTrue(self.report["flags"]["open_210_channel_210_ps_singlet_seed"])
        self.assertIn("bucket_counts", self.report["channel_45_off_singlet"])


if __name__ == "__main__":
    unittest.main()
