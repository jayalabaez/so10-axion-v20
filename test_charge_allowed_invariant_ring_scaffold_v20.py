#!/usr/bin/env python3
"""Tests for charge-allowed invariant ring scaffold."""

from __future__ import annotations

import unittest
from pathlib import Path

import charge_allowed_invariant_ring_scaffold_v20 as mod


class ChargeAllowedInvariantRingScaffoldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_executes_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertTrue(self.report["flags"]["ring_scaffold_ready"])
        self.assertFalse(self.report["flags"]["full_invariant_ring_complete"])
        self.assertFalse(self.report["flags"]["whole_model_validated"])

    def test_ring_artifact_shape(self):
        ring = self.report["ring"]
        self.assertEqual(
            ring["status"],
            "FULL_MIXED_REP_INVARIANT_RING_SCAFFOLD_READY__CG_OPEN",
        )
        self.assertGreater(ring["summary"]["n_operators"], 10)
        self.assertEqual(ring["independence"]["status"], "OPEN")
        self.assertEqual(mod.RING_JSON.name, "FULL_MIXED_REP_INVARIANT_RING_V20.json")


if __name__ == "__main__":
    unittest.main()
