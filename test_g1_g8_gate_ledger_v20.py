#!/usr/bin/env python3
"""Regression tests for the authoritative G1–G8 gate ledger."""
from __future__ import annotations

import unittest

import g1_g8_gate_ledger_v20 as mod


class G1G8GateLedgerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_source_contracts_and_integrity(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(
            self.report["status"],
            "G1_G8_LEDGER_VERIFIED__CLOSURE_PROGRAM_DEFINED__MODEL_BLOCKED",
        )
        self.assertEqual(self.report["overall_state"], "BLOCKED")

    def test_all_eight_gates_present(self):
        self.assertEqual(set(self.report["gates"]), {f"G{i}" for i in range(1, 9)})
        self.assertTrue(self.report["checks"]["dependency_graph_acyclic"])

    def test_fail_closed_statuses(self):
        expected = {
            "G1": mod.STATUS_OPEN,
            "G2": mod.STATUS_PARTIAL,
            "G3": mod.STATUS_PARTIAL,
            "G4": mod.STATUS_PARTIAL,
            "G5": mod.STATUS_PARTIAL,
            "G6": mod.STATUS_PARTIAL,
            "G7": mod.STATUS_OPEN,
            "G8": mod.STATUS_PARTIAL,
        }
        observed = {
            name: row["status"] for name, row in self.report["gates"].items()
        }
        self.assertEqual(observed, expected)
        self.assertEqual(self.report["summary"]["n_closed"], 0)

    def test_g1_count_correction(self):
        correction = self.report["gates"]["G1"]["corrections"]
        self.assertFalse(correction["claimed_44_coefficient_census_is_authoritative_closure"])
        self.assertEqual(correction["current_authoritative_signed_guaranteed_floor"], 34)
        self.assertFalse(correction["floor_is_complete_ring"])

    def test_g4_null_mode_correction(self):
        correction = self.report["gates"]["G4"]["corrections"]
        self.assertEqual(correction["exact_gauge_goldstones"], 33)
        self.assertEqual(correction["preprojection_phase_spectator_zeros"], 4)
        self.assertEqual(correction["bookkeeping_sum_33_plus_4"], 37)
        self.assertFalse(correction["thirty_seven_physical_null_modes"])

    def test_g6_rejects_legacy_scalar_thresholds(self):
        correction = self.report["gates"]["G6"]["corrections"]
        self.assertFalse(correction["legacy_aulakh_susy_matrices_are_nonsusy_scalar_masses"])
        self.assertFalse(correction["legacy_locked_triplet_threshold_chain_is_physical"])
        self.assertFalse(correction["signed_mt2_proxy_is_complete_physical_spectrum"])

    def test_dependency_critical_path(self):
        deps = self.report["dependencies"]
        self.assertEqual(deps["G2"], ["G1"])
        self.assertIn("G6", deps["G7"])
        self.assertEqual(deps["G8"], ["G3", "G6", "G7"])

    def test_feasibility_does_not_guarantee_survival(self):
        feasibility = self.report["feasibility"]
        self.assertTrue(feasibility["complete_closure_program_is_well_defined"])
        self.assertTrue(feasibility["all_missing_calculations_are_attemptable_in_principle"])
        self.assertFalse(feasibility["all_gates_closable_from_current_repo_evidence"])
        self.assertFalse(feasibility["current_hosted_runner_can_finish_all_without_new_derivations_or_tools"])
        self.assertFalse(feasibility["guarantee_model_passes_all_gates"])
        self.assertIn("THEORY_FAIL_AT_ONE_OR_MORE_GATES", feasibility["possible_terminal_outcomes"])


if __name__ == "__main__":
    unittest.main()
