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
        # The SARAH-attested model contract is consistent; the model is not.
        self.assertTrue(
            classification["authoritative_model_contract_consistent"]
        )
        self.assertTrue(
            classification["tool_native_bound_model_evidence_complete"]
        )
        self.assertFalse(classification["all_g1_g8_closed"])
        self.assertFalse(classification["exact_unique_proton_lifetime"])
        self.assertFalse(classification["proton_decay_observed"])
        self.assertFalse(classification["whole_model_validated"])
        self.assertFalse(classification["whole_model_excluded"])
        self.assertFalse(classification["empirical_discovery"])

    def test_root_resolved_and_downstream_blockers_present(self):
        blockers = set(self.report["blockers"])
        self.assertNotIn(
            mod.x_contract_gate.EXTERNAL_EXECUTION_BLOCKER,
            blockers,
        )
        self.assertNotIn("G1_NOT_CLOSED", blockers)
        self.assertNotIn("G2_NOT_CLOSED", blockers)
        # G3 closes on the SM Pati-Salam track and G5 on the same coupling vector.
        self.assertNotIn("G3_NOT_CLOSED", blockers)
        self.assertNotIn("G5_NOT_CLOSED", blockers)
        for gate in ("G4", "G6", "G7", "G8"):
            self.assertIn(f"{gate}_NOT_CLOSED", blockers)
        self.assertTrue(any(item.startswith("PROTON_READINESS_") for item in blockers))

    def test_verdict_scopes_the_g3_closure(self):
        verdict = self.report["verdict"]
        self.assertTrue(
            verdict.startswith(
                "The repository remains BLOCKED at full-model scope. On the "
                "attested gauged U(1)_X contract the ledger closes G1, G2, G3, G5 "
            ),
            verdict,
        )
        self.assertIn("G3 on the SM Pati-Salam benchmark family only", verdict)
        self.assertIn(
            ", but G4, G6, G7, G8 and the unique proton-lifetime derivation "
            "are not closed.",
            verdict,
        )
        self.assertEqual(
            self.report["classification"]["g3_closing_track"], "sm_pati_salam"
        )
        self.assertEqual(self.report["overall_state"], "BLOCKED")

    def test_repaired_contract_promotes_g1_g2_without_full_model_approval(self):
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
        self.assertNotIn("G1_NOT_CLOSED", report["blockers"])
        self.assertNotIn("G2_NOT_CLOSED", report["blockers"])
        self.assertNotIn("G3_NOT_CLOSED", report["blockers"])
        self.assertIn("G4_NOT_CLOSED", report["blockers"])
        self.assertIn("G8_NOT_CLOSED", report["blockers"])
        self.assertIn("G3 on the SM Pati-Salam benchmark family only", report["verdict"])
        self.assertFalse(report["classification"]["whole_model_validated"])

    def test_unbound_consistency_boolean_is_an_integrity_failure(self):
        # Audit the shipped model without its attestation, then forge the flag.
        contract = copy.deepcopy(
            mod.x_contract_gate.build_report(
                model_text=mod.x_contract_gate.MODEL.read_text(encoding="utf-8")
            )
        )
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
