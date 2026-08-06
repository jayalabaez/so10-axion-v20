#!/usr/bin/env python3
"""Tests for off-singlet Q-charged selection rule."""

from __future__ import annotations

import unittest

import off_singlet_qcharged_selection_rule_v20 as mod


class OffSingletQchargedSelectionRuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_all_channels_qcharged(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertTrue(self.report["flags"]["selection_rule_ready"])
        self.assertFalse(
            self.report["implications"][
                "em_neutral_light_singlet_seed_from_45_54_210_off_singlet"
            ]
        )
        for ch in self.report["channels"]:
            self.assertTrue(ch["all_Q_charged"], ch)
            self.assertEqual(ch["n_modes"], 207)


if __name__ == "__main__":
    unittest.main()
