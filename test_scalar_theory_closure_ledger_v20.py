#!/usr/bin/env python3
"""Tests for scalar theory closure ledger."""

from __future__ import annotations

import unittest

import scalar_theory_closure_ledger_v20 as mod


class ScalarTheoryClosureLedgerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_executes_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertFalse(self.report["flags"]["theory_complete"])
        self.assertFalse(self.report["flags"]["whole_model_validated"])
        self.assertFalse(self.report["flags"]["whole_model_excluded"])
        self.assertEqual(self.report["gate_summary"]["n_closed"], 0)
        self.assertEqual(self.report["gate_summary"]["n_partial"], 4)
        self.assertEqual(self.report["gate_summary"]["n_open"], 4)
        self.assertEqual(len(self.report["gates"]), 8)


if __name__ == "__main__":
    unittest.main()
