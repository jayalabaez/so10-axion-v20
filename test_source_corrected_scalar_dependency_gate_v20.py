#!/usr/bin/env python3
import unittest

import source_corrected_scalar_dependency_gate_v20 as gate


class SourceCorrectedDependencyGateTests(unittest.TestCase):
    def test_gate_executes_fail_closed(self):
        report = gate.build_report()
        self.assertEqual(report["n_failed"], 0, report)
        self.assertEqual(report["overall_state"], "BLOCKED")
        self.assertFalse(report["flags"]["merge_to_main_safe"])
        self.assertTrue(report["flags"]["pr98_must_remain_draft"])

    def test_valid_structural_results_are_retained(self):
        report = gate.build_report()
        self.assertTrue(all(report["retained_results"].values()))
        self.assertTrue(
            report["retained_results"]["selected_neutral_phase_gauge_quotient_for_positive_kappa"]
        )
        self.assertTrue(report["retained_results"]["cqit_haloscope_receiver_bridge"])

    def test_affected_dependencies_are_reopened(self):
        report = gate.build_report()
        self.assertTrue(all(report["reopened_results"].values()))
        self.assertTrue(report["reopened_results"]["complete_210_quartic_invariant_basis"])
        self.assertTrue(report["reopened_results"]["complete_component_hessian"])
        self.assertTrue(report["reopened_results"]["unique_proton_lifetime"])

    def test_no_g1_to_g8_gate_is_closed(self):
        report = gate.build_report()
        self.assertEqual(len(report["gate_states"]), 8)
        self.assertTrue(all("CLOSED" not in state for state in report["gate_states"].values()))
        self.assertFalse(report["flags"]["whole_model_validated"])
        self.assertFalse(report["flags"]["whole_model_excluded"])


if __name__ == "__main__":
    unittest.main()
