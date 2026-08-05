#!/usr/bin/env python3
"""Tests for scoped BFB boundedness gate."""

from __future__ import annotations

import unittest

import scoped_bfb_boundedness_gate_v20 as mod


class ScopedBfbBoundednessGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_executes_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertTrue(self.report["flags"]["scoped_bfb_gate_ready"])
        self.assertTrue(self.report["flags"]["g5_partial"])
        self.assertFalse(self.report["flags"]["full_invariant_ring_bfb"])
        self.assertFalse(self.report["flags"]["whole_model_validated"])


if __name__ == "__main__":
    unittest.main()
