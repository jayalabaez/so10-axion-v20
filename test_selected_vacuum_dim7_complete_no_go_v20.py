#!/usr/bin/env python3
"""Tests for the consolidated dimension-seven selected-vacuum verdict."""
from __future__ import annotations

import unittest

import selected_vacuum_dim7_complete_no_go_v20 as mod


class SelectedVacuumDim7CompleteNoGoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_complete_zero_verdict(self):
        self.assertEqual(self.report["n_failed"], 0, self.report)
        self.assertEqual(
            self.report["status"],
            "SELECTED_VACUUM_DIM7_PHASE_LIFTING_NO_GO_PROVEN",
        )
        summary = self.report["dimension7_summary"]
        self.assertEqual(summary["charge_allowed_even_H_conjugacy_representatives"], 13)
        self.assertEqual(summary["exact_graph_coefficient_evaluations"], 62948)
        self.assertEqual(summary["maximum_abs_coefficient"], 0.0)
        self.assertEqual(summary["nonzero_representatives"], 0)

    def test_evidence_partition(self):
        stages = [row["stage"] for row in self.report["evidence"]]
        self.assertIn("dimension6_prerequisite", stages)
        self.assertEqual(len([s for s in stages if s.startswith("dimension7_")]), 5)
        self.assertTrue(
            all(row["artifact_digest"].startswith("sha256:") for row in self.report["evidence"])
        )

    def test_honest_boundary(self):
        flags = self.report["flags"]
        self.assertTrue(flags["full_selected_vacuum_dimension7_phase_lifting_no_go_proven"])
        self.assertTrue(flags["dimension8_search_required"])
        self.assertFalse(flags["selected_vacuum_fully_stabilized"])
        self.assertFalse(flags["stationarity_rebuilt"])
        self.assertFalse(flags["full_scalar_hessian_rebuilt"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])


if __name__ == "__main__":
    unittest.main()
