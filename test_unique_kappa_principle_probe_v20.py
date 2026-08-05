#!/usr/bin/env python3
"""Tests for unique-κ principle probe."""

from __future__ import annotations

import unittest

import unique_kappa_principle_probe_v20 as mod


class UniqueKappaPrincipleProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_executes_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertTrue(self.report["flags"]["unique_kappa_probes_executed"])
        self.assertFalse(self.report["flags"]["uv_kappa_uniquely_determined"])
        self.assertFalse(self.report["flags"]["whole_model_validated"])

    def test_probes_disagree(self):
        self.assertFalse(self.report["flags"]["probes_numerically_agree"])
        self.assertGreater(self.report["comparison"]["relative_spread"], 0.05)
        self.assertIn("NOT_UNIQUE", self.report["status"])


if __name__ == "__main__":
    unittest.main()
