#!/usr/bin/env python3
"""Tests for authoritative physical-phase integration."""
from __future__ import annotations

import unittest

import selected_vacuum_physical_phase_integration_v20 as mod


class SelectedVacuumPhysicalPhaseIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report(1.0)

    def test_physical_phase_is_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report)
        self.assertEqual(
            self.report["status"],
            "PHYSICAL_NEUTRAL_PHASE_CLOSED__CORE_CONSUMERS_REVALIDATED",
        )
        closed = self.report["closed_subproblem"]
        self.assertEqual(closed["physical_rank"], 1)
        self.assertEqual(closed["physical_nullity"], 1)
        self.assertEqual(closed["physical_null"], "PQ axion")
        self.assertFalse(closed["extra_physical_nonaxion_flat_phase"])

    def test_core_consumers_revalidated(self):
        audit = self.report["legacy_consumer_audit"]
        self.assertGreaterEqual(audit["n_revalidated"], 3)
        for path in (
            "multi_operator_phase_hessian_v20.py",
            "gauge_fixing_goldstone_eating_v20.py",
            "phase_operator_independence_audit_v20.py",
        ):
            self.assertIn(path, audit["revalidated_paths"])
            self.assertNotIn(path, audit["stale_or_dependent_paths"])
        self.assertTrue(self.report["flags"]["core_prequotient_consumers_revalidated"])
        self.assertFalse(self.report["flags"]["legacy_phase_consumers_fully_revalidated"])

    def test_finite_search_is_corroboration(self):
        finite = self.report["finite_invariant_search_audit"]
        self.assertFalse(finite["missing_paths"])
        self.assertTrue(
            all(
                not row["required_for_physical_phase_closure"]
                for row in finite["modules"]
            )
        )
        self.assertFalse(
            self.report["flags"][
                "finite_dimension_search_workflows_scientifically_required"
            ]
        )

    def test_honest_whole_model_boundary(self):
        flags = self.report["flags"]
        self.assertTrue(flags["physical_neutral_phase_blocker_removed"])
        self.assertFalse(flags["full_component_scalar_hessian_complete"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])


if __name__ == "__main__":
    unittest.main()
