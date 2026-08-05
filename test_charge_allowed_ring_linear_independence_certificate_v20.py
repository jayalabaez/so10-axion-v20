#!/usr/bin/env python3
"""Tests for charge-allowed ring linear independence."""

from __future__ import annotations

import unittest

import charge_allowed_ring_linear_independence_certificate_v20 as mod


class RingLinearIndependenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_executes_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertTrue(self.report["flags"]["ring_linear_independence_partial"])
        self.assertFalse(self.report["flags"]["full_invariant_ring_complete"])
        self.assertFalse(self.report["flags"]["whole_model_validated"])

    def test_subspaces_enumerated(self):
        ind = self.report["independence"]
        self.assertGreater(ind["n_charge_dim_subspaces"], 0)
        self.assertEqual(ind["status"], "PARTIAL_ON_CHARGE_SUBSPACES")
        self.assertFalse(ind["full_ring_independence"])


if __name__ == "__main__":
    unittest.main()
