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
    external["present"] = True
    external["valid"] = True
    external["fresh_for_exact_model_bytes"] = True
    # A repaired-contract fixture must model the complete v3 provenance
    # boundary.  Retaining the old eight-check v2 subset would test a forged
    # partial attestation, which production must (and does) reject.
    external["checks"] = {
        name: True
        for name in mod.gate_ledger.EXPECTED_EXACT_X_V3_EXTERNAL_CHECKS
    }


def forge_all_canonical_gate_booleans(report):
    """Adversarial report forgery; live verifier replay must reject it."""
    report = copy.deepcopy(report)
    for row in report["gates"]:
        row["evidence_state"].update(valid=True, closed=True, exists=True, errors=[])
        row["dependencies_closed"] = True
        row["closed"] = True
    report["closure_counts"] = {"closed": 8, "open": 0}
    report["overall_state"] = "PASS"
    report["classification"]["all_canonical_gates_closed"] = True
    report["classification"]["whole_model_validated"] = True
    body = dict(report)
    body.pop("integrity", None)
    report["integrity"] = {"core_sha256": mod.canonical_gates._sha(body)}
    return report


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

    def test_root_and_downstream_blockers_present(self):
        blockers = set(self.report["blockers"])
        self.assertNotIn(mod.x_contract_gate.EXTERNAL_EXECUTION_BLOCKER, blockers)
        for gate_id in (
            mod.canonical_gates.G4_ID,
            mod.canonical_gates.G7_ID,
            mod.canonical_gates.G8_ID,
        ):
            self.assertIn(f"CANONICAL_GATE_NOT_CLOSED::{gate_id}", blockers)
        self.assertTrue(any(item.startswith("PROTON_READINESS_") for item in blockers))

    def test_blocked_verdict_recognizes_repaired_contract_and_open_downstream(self):
        verdict = self.report["verdict"]
        self.assertIn("repaired gauged U(1)_X execution contract is valid", verdict)
        self.assertIn("canonical V21 phenomenology gates remain open", verdict)

    def test_repaired_execution_contract_does_not_alias_legacy_scalar_gates(self):
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
        self.assertEqual(repaired_ledger["gates"]["G1"]["status"], "CLOSED")
        self.assertEqual(repaired_ledger["gates"]["G2"]["status"], "CLOSED")
        self.assertEqual(repaired_ledger["gates"]["G5"]["status"], "CLOSED")
        self.assertNotIn(
            f"CANONICAL_GATE_NOT_CLOSED::{mod.canonical_gates.G1_ID}",
            report["blockers"],
        )
        self.assertNotIn(
            f"CANONICAL_GATE_NOT_CLOSED::{mod.canonical_gates.G2_ID}",
            report["blockers"],
        )
        self.assertIn(
            f"CANONICAL_GATE_NOT_CLOSED::{mod.canonical_gates.G8_ID}",
            report["blockers"],
        )
        self.assertFalse(
            report["flag"]["legacy_ledger_controls_authoritative_closure"]
        )
        self.assertFalse(report["classification"]["whole_model_validated"])

    def test_forged_complete_canonical_booleans_cannot_reach_pass(self):
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
        canonical = forge_all_canonical_gate_booleans(
            mod.canonical_gates.build_report()
        )
        with mock.patch.object(
            mod.x_contract_gate, "build_report", return_value=repaired_x
        ), mock.patch.object(
            mod.gate_ledger, "build_report", return_value=repaired_ledger
        ), mock.patch.object(
            mod.canonical_gates, "build_report", return_value=canonical
        ):
            report = mod.build_report()
        self.assertEqual(report["overall_state"], "EXECUTION_FAIL")
        self.assertIn(
            "canonical G1-G8 V21 contract integrity failed", report["failures"]
        )
        self.assertFalse(report["classification"]["all_g1_g8_closed"])
        self.assertFalse(report["classification"]["exact_unique_proton_lifetime"])
        self.assertFalse(report["classification"]["whole_model_validated"])

    def test_forged_canonical_summary_is_execution_failure(self):
        forged = copy.deepcopy(mod.canonical_gates.build_report())
        forged["overall_state"] = "PASS"
        forged["closure_counts"] = {"closed": 8, "open": 0}
        body = dict(forged)
        body.pop("integrity", None)
        forged["integrity"] = {"core_sha256": mod.canonical_gates._sha(body)}
        with mock.patch.object(
            mod.canonical_gates, "build_report", return_value=forged
        ):
            report = mod.build_report()
        self.assertEqual(report["overall_state"], "EXECUTION_FAIL")
        self.assertIn("canonical G1-G8 V21 contract integrity failed", report["failures"])

    def test_boolean_canonical_failure_count_is_rejected(self):
        forged = copy.deepcopy(mod.canonical_gates.build_report())
        forged["n_failed"] = False
        body = dict(forged)
        body.pop("integrity", None)
        forged["integrity"] = {"core_sha256": mod.canonical_gates._sha(body)}
        with mock.patch.object(
            mod.canonical_gates, "build_report", return_value=forged
        ):
            report = mod.build_report()
        self.assertEqual(report["overall_state"], "EXECUTION_FAIL")

    def test_unbound_legacy_consistency_boolean_cannot_approve_or_veto(self):
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
        self.assertEqual(report["overall_state"], "BLOCKED")
        self.assertFalse(report["classification"]["whole_model_validated"])
        self.assertFalse(report["flag"]["legacy_ledger_controls_authoritative_closure"])
        self.assertTrue(
            report["classification"][
                "tool_native_bound_model_evidence_complete"
            ]
        )
        self.assertEqual(report["failures"], [])

    def test_failed_legacy_proton_diagnostic_cannot_veto_canonical_state(self):
        proton = copy.deepcopy(mod.proton_gate.build_report())
        proton["n_failed"] = 1
        proton["failures"] = ["synthetic legacy diagnostic failure"]
        with mock.patch.object(mod.proton_gate, "build_report", return_value=proton):
            report = mod.build_report()

        self.assertEqual(report["overall_state"], "BLOCKED")
        self.assertEqual(report["failures"], [])
        self.assertFalse(report["classification"]["whole_model_validated"])
        self.assertIn(
            "proton gate: synthetic legacy diagnostic failure",
            report["legacy_g1_g8_evidence"]["diagnostic_failures"],
        )
        self.assertTrue(
            report["checks"][
                "legacy_proton_gate_does_not_control_authoritative_closure"
            ]
        )

    def test_legacy_internal_candidate_flag_cannot_veto_canonical_state(self):
        legacy = copy.deepcopy(mod._legacy_snapshot())
        legacy["internal_candidate_approved"] = True
        with mock.patch.object(mod, "_legacy_snapshot", return_value=legacy):
            report = mod.build_report()

        self.assertEqual(report["overall_state"], "BLOCKED")
        self.assertEqual(report["failures"], [])
        self.assertTrue(
            report["checks"][
                "legacy_internal_candidate_does_not_control_authoritative_closure"
            ]
        )


if __name__ == "__main__":
    unittest.main()
