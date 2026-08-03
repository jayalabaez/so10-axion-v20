#!/usr/bin/env python3
"""Tests for next phenomenology lock."""

from __future__ import annotations

import unittest

import next_phenomenology_lock_v20 as nxt


class NextPhenomenologyLockTests(unittest.TestCase):
    def test_fcnc_absence_not_claimed(self):
        ledger = nxt.fcnc_ledger()
        self.assertFalse(ledger["tree_FCNC_absence_proved"])
        self.assertGreaterEqual(len(ledger["rows"]), 4)

    def test_hadronic_envelope_finite(self):
        env = nxt.hadronic_envelope(1.5)
        self.assertFalse(env["full_unique_Ce_Cp_Cn"])
        self.assertTrue(all(map(lambda x: x == x, env["C_p_range"])))

    def test_report_pass(self):
        report = nxt.build_report()
        self.assertEqual(report["n_failed"], 0)
        self.assertFalse(report["flag"]["full_unique_Ce_Cp_Cn"])
        self.assertFalse(report["flag"]["full_RG_global_fit"])


if __name__ == "__main__":
    unittest.main()
