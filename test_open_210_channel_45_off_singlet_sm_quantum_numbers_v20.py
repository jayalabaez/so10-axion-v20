#!/usr/bin/env python3
"""Tests for off-singlet mixed-45 SM Cartan quantum numbers."""

from __future__ import annotations

import unittest

import open_210_channel_45_off_singlet_sm_quantum_numbers_v20 as mod


class Open210Channel45OffSingletSmQnTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_executes_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertTrue(self.report["flags"]["off_singlet_45_sm_qn_ready"])
        self.assertFalse(self.report["flags"]["off_singlet_45_mode_cg"])
        self.assertFalse(self.report["flags"]["whole_model_validated"])

    def test_all_modes_labeled(self):
        qn = self.report["quantum_numbers"]
        self.assertEqual(qn["n_modes_labeled"], 207)
        self.assertEqual(
            qn["n_Q_neutral"] + qn["n_Q_charged"], qn["n_modes_labeled"]
        )
        self.assertEqual(
            self.report["inventory_slot"]["status"],
            "PARTIAL_SM_QUANTUM_NUMBERS_READY",
        )
        self.assertGreater(sum(qn["bucket_counts"].values()), 0)


if __name__ == "__main__":
    unittest.main()
