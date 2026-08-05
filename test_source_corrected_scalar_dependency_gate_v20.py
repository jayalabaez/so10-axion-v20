#!/usr/bin/env python3
import unittest

import source_corrected_scalar_dependency_gate_v20 as gate


class SourceCorrectedDependencyGateTests(unittest.TestCase):
    def test_gate_executes_fail_closed(self):
        report = gate.build_report()
        self.assertEqual(report["n_failed"], 0, report)
        self.assertEqual(report["overall_state"], "BLOCKED")
        self.assertTrue(report["flags"]["pure_210_quartic_subsector_closed"])
        self.assertFalse(report["flags"]["merge_to_main_safe"])
        self.assertTrue(report["flags"]["pr98_must_remain_draft"])

    def test_valid_structural_results_and_pure210_are_retained(self):
        report = gate.build_report()
        self.assertTrue(all(report["retained_results"].values()))
        self.assertTrue(
            report["retained_results"]["source_normalized_pure_210_quartic_basis"]
        )
        self.assertTrue(
            report["retained_results"]["analytic_p_a_omega_pure_210_quartics"]
        )
        self.assertTrue(
            report["retained_results"]["selected_neutral_phase_gauge_quotient_for_positive_kappa"]
        )
        self.assertTrue(report["retained_results"]["cqit_haloscope_receiver_bridge"])

    def test_only_downstream_mixed_dependencies_are_reopened(self):
        report = gate.build_report()
        self.assertTrue(all(report["reopened_results"].values()))
        self.assertNotIn("complete_210_quartic_invariant_basis", report["reopened_results"])
        self.assertTrue(report["reopened_results"]["full_mixed_rep_invariant_ring_G1"])
        self.assertTrue(report["reopened_results"]["complete_component_hessian"])
        self.assertTrue(report["reopened_results"]["unique_proton_lifetime"])

    def test_pure210_closed_while_g1_to_g8_remain_open(self):
        report = gate.build_report()
        self.assertEqual(len(report["gate_states"]), 9)
        self.assertEqual(
            report["gate_states"]["PURE210_quartic_subsector"],
            "CLOSED_SOURCE_NORMALIZED",
        )
        scientific_states = [
            state
            for name, state in report["gate_states"].items()
            if name != "PURE210_quartic_subsector"
        ]
        self.assertTrue(all("CLOSED" not in state for state in scientific_states))
        self.assertFalse(report["flags"]["whole_model_validated"])
        self.assertFalse(report["flags"]["whole_model_excluded"])


if __name__ == "__main__":
    unittest.main()
