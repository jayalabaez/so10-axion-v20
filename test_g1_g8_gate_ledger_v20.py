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
            "G1": mod.STATUS_CLOSED,
            "G2": mod.STATUS_CLOSED,
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
        self.assertEqual(set(self.report["summary"]["closed"]), {"G1", "G2"})
        self.assertEqual(self.report["summary"]["n_closed"], 2)

    def test_g1_live_ring_correction(self):
        correction = self.report["gates"]["G1"]["corrections"]
        self.assertFalse(correction["historical_signed_floor34_is_complete_ring"])
        self.assertFalse(correction["historical_44_coefficient_census_is_current_live_ring"])
        self.assertEqual(correction["live_hermitian_conjugacy_orbits"], 48)
        self.assertEqual(correction["live_independent_invariant_directions"], 64)
        self.assertEqual(correction["live_real_potential_parameters"], 91)
        self.assertEqual(correction["live_base_tensor_families"], 18)
        self.assertTrue(correction["live_ring_closed"])

    def test_g2_complete_derivative_assembly(self):
        correction = self.report["gates"]["G2"]["corrections"]
        self.assertEqual(correction["base_families"], 18)
        self.assertEqual(correction["invariant_directions"], 64)
        self.assertEqual(correction["real_parameters"], 91)
        self.assertEqual(correction["real_field_dimension"], 486)
        self.assertTrue(correction["G2_closed"])

    def test_g3_first_order_scope_is_honest(self):
        gate = self.report["gates"]["G3"]
        self.assertEqual(gate["status"], mod.STATUS_PARTIAL)
        self.assertIn(
            "find a tachyon-free stationary member; the current witness and bounded search remain nonpositive",
            gate["open_scope"],
        )
        self.assertFalse(
            gate["corrections"]["first_order_feasibility_is_global_vacuum_proof"]
        )
        self.assertEqual(
            gate["corrections"]["anchored_witness_physical_negative_modes"], 46
        )
        self.assertEqual(
            gate["corrections"]["massive_physical_quotient_dimension"], 449
        )
        self.assertFalse(gate["corrections"]["local_saddle_is_global_vacuum"])

    def test_g4_stage_resolved_null_mode_correction(self):
        correction = self.report["gates"]["G4"]["corrections"]
        self.assertEqual(correction["pre_EW_SO10_to_SM_goldstones"], 33)
        self.assertEqual(correction["physical_EW_SO10_to_U1em_goldstones"], 36)
        self.assertEqual(correction["preprojection_phase_spectator_zeros"], 4)
        self.assertEqual(correction["bookkeeping_sum_33_plus_4"], 37)
        self.assertFalse(correction["thirty_seven_physical_null_modes"])
        self.assertIn(
            "full 486x486 witness Hessian projected to the 449-dimensional massive quotient",
            self.report["gates"]["G4"]["closed_scope"],
        )

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
