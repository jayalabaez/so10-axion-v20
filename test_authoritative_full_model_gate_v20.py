#!/usr/bin/env python3
import copy
import unittest
from unittest import mock

import authoritative_full_model_gate_v20 as mod


def bind_tool_native_root_evidence(report):
    scaffold = report["executable_scaffold_contract"]
    scaffold.update(
        model_syntax_class="sarah_native",
        tool_native_sarah_syntax=True,
        statically_executable_model_contract=True,
    )
    scaffold["lagrangian"][
        "registered_in_GaugeES_LagrangianInput"
    ] = True
    external = report["external_model_validation"]
    external["schema"] = mod.x_contract_gate.EXTERNAL_VALIDATION_SCHEMA
    external["valid"] = True
    for name in (
        "tool_native_model_format_matches_path",
        "external_process_command_matches_tool",
        "input_manifest_schema_is_supported",
        "input_manifest_sha256_matches_entries",
        "primary_model_is_bound_in_input_manifest",
        "validation_driver_is_bound_to_command",
        "captured_process_log_is_hash_bound",
        "captured_process_log_has_all_required_pass_markers",
    ):
        external["checks"][name] = True


class AuthoritativeFullModelGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_executes_and_is_blocked(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertTrue(self.report["flag"]["authoritative_full_model_gate"])

    def test_legacy_ultimate_is_not_authoritative(self):
        self.assertFalse(
            self.report["legacy_ultimate_gate"]["authoritative_for_full_model"]
        )
        self.assertFalse(self.report["flag"]["legacy_ultimate_gate_authoritative"])
        self.assertTrue(
            self.report["flag"][
                "internal_candidate_approval_is_not_full_model_validation"
            ]
        )

    def test_no_full_model_claim(self):
        classification = self.report["classification"]
        self.assertFalse(
            classification["authoritative_model_contract_consistent"]
        )
        self.assertFalse(
            classification["tool_native_bound_model_evidence_complete"]
        )
        self.assertFalse(classification["all_g1_g8_closed"])
        self.assertFalse(classification["exact_unique_proton_lifetime"])
        self.assertFalse(classification["proton_decay_observed"])
        self.assertFalse(classification["whole_model_validated"])
        self.assertFalse(classification["whole_model_excluded"])
        self.assertFalse(classification["empirical_discovery"])

    def test_root_and_downstream_blockers_present(self):
        blockers = set(self.report["blockers"])
        self.assertIn(
            mod.x_contract_gate.EXTERNAL_EXECUTION_BLOCKER,
            blockers,
        )
        self.assertIn("G1_NOT_CLOSED", blockers)
        self.assertIn("G2_NOT_CLOSED", blockers)
        self.assertIn("G3_NOT_CLOSED", blockers)
        self.assertIn("G7_NOT_CLOSED", blockers)
        self.assertIn("G8_NOT_CLOSED", blockers)
        self.assertTrue(any(item.startswith("PROTON_READINESS_") for item in blockers))

    def test_repaired_contract_does_not_bypass_open_full_g1_scope(self):
        current_ledger = mod.gate_ledger.build_report()
        inputs = current_ledger["model_contract_reports"]
        repaired_x = copy.deepcopy(inputs["exact_X"])
        repaired_x.update(
            contract_consistent=True,
            blocker=None,
            scientific_blockers=[],
            contract_conflicts=[],
            overall_state="PASS",
        )
        repaired_x["flag"]["contract_consistent"] = True
        repaired_x["flag"]["x_selection_rule_consistently_declared"] = True
        bind_tool_native_root_evidence(repaired_x)
        repaired_ledger = mod.gate_ledger._build_report_from_inputs(
            x_report=repaired_x,
            g1_report=inputs["gauged_G1_character_census"],
            g2_report=inputs["gauged_G2_derivative_audit"],
            filter_report=inputs["gauged_scalar_filter"],
        )

        with mock.patch.object(
            mod.x_contract_gate, "build_report", return_value=repaired_x
        ), mock.patch.object(
            mod.gate_ledger, "build_report", return_value=repaired_ledger
        ):
            report = mod.build_report()

        self.assertEqual(report["n_failed"], 0, report["failures"])
        self.assertEqual(report["overall_state"], "BLOCKED")
        self.assertTrue(
            report["classification"]["authoritative_model_contract_consistent"]
        )
        self.assertEqual(repaired_ledger["gates"]["G1"]["status"], "OPEN")
        self.assertEqual(repaired_ledger["gates"]["G2"]["status"], "BLOCKED")
        self.assertIn("G1_NOT_CLOSED", report["blockers"])
        self.assertIn("G2_NOT_CLOSED", report["blockers"])
        self.assertIn("G3_NOT_CLOSED", report["blockers"])
        self.assertIn("G8_NOT_CLOSED", report["blockers"])
        self.assertFalse(report["classification"]["whole_model_validated"])

    def test_unbound_consistency_boolean_is_an_integrity_failure(self):
        contract = copy.deepcopy(mod.x_contract_gate.build_report())
        contract.update(
            contract_consistent=True,
            blocker=None,
            scientific_blockers=[],
            contract_conflicts=[],
            overall_state="PASS",
        )
        with mock.patch.object(
            mod.x_contract_gate, "build_report", return_value=contract
        ):
            report = mod.build_report()
        self.assertEqual(report["overall_state"], "EXECUTION_FAIL")
        self.assertFalse(
            report["classification"][
                "tool_native_bound_model_evidence_complete"
            ]
        )
        self.assertIn(
            "gate check: consistent_contract_has_tool_native_bound_evidence",
            report["failures"],
        )


if __name__ == "__main__":
    unittest.main()
