#!/usr/bin/env python3
"""Fail-closed and sabotage tests for the ultimate v20 gate."""

from __future__ import annotations

import copy
import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

import exact_x_symmetry_consistency_gate_v20 as x_gate
import g3_sm_target_track_v20 as sm_track
import theory_confirmation_verdict_v20 as confirmation
import ultimate_theory_gate_v20 as gate


class UltimateGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fresh_reports = confirmation.fresh_source_reports()

    def evaluate(self, reports: dict | None = None) -> dict:
        return gate.evaluate_reports(
            copy.deepcopy(reports or self.fresh_reports),
            current_test_count=321,
        )

    def test_current_state_is_honestly_open(self) -> None:
        # The SARAH-attested contract is consistent; G3 is closed only on the
        # SM Pati-Salam benchmark family, G4 and G6-G8 are not closed, and
        # decision D3 keeps the internal candidate withheld.
        result = self.evaluate()
        self.assertTrue(result["integrity_pass"])
        self.assertEqual(result["n_failed"], 0)
        self.assertEqual(result["overall_state"], "OPEN")
        self.assertEqual(result["classification"], "AUTHORITATIVE_GATES_OPEN")
        self.assertEqual(result["decision"], "WITHHOLD_APPROVAL")
        self.assertEqual(
            result["validation_matrix_contract_gate"]["state"], "PASS"
        )
        self.assertFalse(result["internal_candidate_approved"])
        self.assertFalse(result["full_phenomenology_approved"])
        self.assertFalse(result["whole_model_excluded"])

    def test_unattested_contract_is_honestly_blocked(self) -> None:
        reports = copy.deepcopy(self.fresh_reports)
        reports["x_contract"] = x_gate.build_report(
            model_text=x_gate.MODEL.read_text(encoding="utf-8")
        )
        result = self.evaluate(reports)
        self.assertEqual(result["overall_state"], "BLOCKED")
        self.assertEqual(
            result["classification"],
            "MODEL_CONTRACT_INCONSISTENT__AUTHORITATIVE_GATES_REOPENED",
        )
        self.assertEqual(result["decision"], "WITHHOLD_APPROVAL")
        self.assertEqual(
            result["validation_matrix_contract_gate"]["state"], "BLOCKED"
        )
        self.assertEqual(result["verdict"], gate._verdict(False))

    def test_verdict_text_branches_on_contract_readiness(self) -> None:
        ready = gate._verdict(True, g3_closed=True)
        ready_g3_open = gate._verdict(True)
        blocked = gate._verdict(False)
        for text in (ready, ready_g3_open):
            self.assertNotIn("lacks", text)
            self.assertNotIn("no v2 manifest", text)
            self.assertIn("attested by bound external SARAH execution", text)
        self.assertTrue(
            ready.startswith(
                "WITHHOLD APPROVAL. The audit has no execution failure and the "
                "gauged-U(1)_X model contract is attested by bound external "
                "SARAH execution evidence; G3 is closed on the SM Pati-Salam "
                "benchmark family (scoped), but the G4 and G6-G8 scientific "
                "gates remain open and the closing track's downstream caveats "
                "are unresolved. "
            )
        )
        self.assertIn(
            "the G3, G4 and G6-G8 scientific gates remain open", ready_g3_open
        )
        self.assertIn(
            "has no v2 manifest/log-bound external SARAH execution evidence",
            blocked,
        )
        # A blocked contract ignores the G3 flag.
        self.assertEqual(gate._verdict(False, g3_closed=True), blocked)
        self.assertEqual(self.evaluate()["verdict"], ready)

    def test_confirmation_text_branches_on_contract_readiness(self) -> None:
        ready = confirmation._claim_text(True, g3_closed=True)
        ready_g3_open = confirmation._claim_text(True)
        blocked = confirmation._claim_text(False)
        for text in list(ready.values()) + list(ready_g3_open.values()):
            self.assertNotIn("lacks", text)
            self.assertNotIn("no v2 manifest", text)
        self.assertIn(
            "lacks a v2 manifest/log-bound external SARAH execution attestation",
            blocked["correct_public_claim"],
        )
        self.assertIn(
            "still lacks a real external SARAH execution", blocked["verdict"]
        )
        self.assertTrue(
            blocked["incorrect_claim_do_not_use"].startswith(
                "G1, G2, or G3 is closed"
            )
        )
        self.assertEqual(confirmation._claim_text(False, g3_closed=True), blocked)
        # The G3-closed text is scoped by the track's closure scope.
        self.assertIn(sm_track.CLOSURE_SCOPE, ready["correct_public_claim"])
        self.assertIn("G1, G2, G3 and G5 are closed.", ready["correct_public_claim"])
        self.assertIn("G1-G8 approval is withheld.", ready["correct_public_claim"])
        self.assertIn(
            "the tuned eps = 0 point is the G3 witness",
            ready["incorrect_claim_do_not_use"],
        )
        self.assertIn(
            "an internal candidate is approved", ready["incorrect_claim_do_not_use"]
        )
        self.assertIn(
            "the closing track's downstream caveats are unresolved",
            ready["verdict"],
        )
        self.assertIn("G3 remains open", ready_g3_open["correct_public_claim"])
        verdict = confirmation.evaluate_reports(
            copy.deepcopy(self.fresh_reports), current_test_count=321
        )
        for key, text in ready.items():
            self.assertEqual(verdict[key], text)
        # The ready text names G1, G2, G3 and G5 closed; keep it tied to the ledger.
        gates = self.fresh_reports["g1_g8"]["gates"]
        self.assertEqual(
            sorted(k for k, v in gates.items() if v["status"] == "CLOSED"),
            ["G1", "G2", "G3", "G5"],
        )
        self.assertEqual(gates["G3"]["closing_track"], "sm_pati_salam")

    # Decision D3: G1-G3 CLOSED does not approve an internal candidate unless
    # the closing track's downstream caveats are resolved or G4 is CLOSED.

    def test_d3_current_state_withholds_internal_candidate(self) -> None:
        result = self.evaluate()
        verdict = confirmation.evaluate_reports(
            copy.deepcopy(self.fresh_reports), current_test_count=321
        )
        for report in (result, verdict):
            self.assertFalse(report["internal_candidate_approved"])
            gate_d3 = report["internal_candidate_gate"]
            self.assertTrue(gate_d3["G1_G2_G3_closed"])
            self.assertTrue(gate_d3["G3_closed"])
            self.assertEqual(gate_d3["closing_track"], "sm_pati_salam")
            self.assertFalse(gate_d3["closing_track_downstream_caveats_resolved"])
            self.assertFalse(gate_d3["G4_closed"])
            self.assertFalse(gate_d3["caveats_cleared"])
            self.assertEqual(gate_d3["rule"], sm_track.D3_RULE)
        self.assertEqual(verdict["tiers"]["INTERNAL_CANDIDATE"], "WITHHELD")
        self.assertFalse(verdict["approval"]["internal_candidate"])
        track = self.fresh_reports["g1_g8"]["g3_sm_target_track"]
        self.assertIs(track["closed"], True)
        self.assertIs(track["downstream_caveats_resolved"], False)

    def test_d3_resolved_track_caveats_approve_internal_candidate(self) -> None:
        reports = copy.deepcopy(self.fresh_reports)
        reports["g1_g8"]["g3_sm_target_track"]["downstream_caveats_resolved"] = True
        result = self.evaluate(reports)
        verdict = confirmation.evaluate_reports(
            copy.deepcopy(reports), current_test_count=321
        )
        for report in (result, verdict):
            self.assertTrue(report["internal_candidate_approved"])
            self.assertTrue(
                report["internal_candidate_gate"][
                    "closing_track_downstream_caveats_resolved"
                ]
            )
            self.assertTrue(report["internal_candidate_gate"]["caveats_cleared"])
            self.assertFalse(report["full_phenomenology_approved"])
            self.assertEqual(report["overall_state"], "OPEN")
        self.assertEqual(verdict["tiers"]["INTERNAL_CANDIDATE"], "APPROVED")

    def test_d3_closed_g4_approves_internal_candidate(self) -> None:
        reports = copy.deepcopy(self.fresh_reports)
        reports["g1_g8"]["gates"]["G4"]["status"] = "CLOSED"
        result = self.evaluate(reports)
        verdict = confirmation.evaluate_reports(
            copy.deepcopy(reports), current_test_count=321
        )
        for report in (result, verdict):
            self.assertTrue(report["internal_candidate_approved"])
            self.assertTrue(report["internal_candidate_gate"]["G4_closed"])
            self.assertFalse(
                report["internal_candidate_gate"][
                    "closing_track_downstream_caveats_resolved"
                ]
            )
            self.assertTrue(report["internal_candidate_gate"]["caveats_cleared"])
        self.assertEqual(verdict["tiers"]["INTERNAL_CANDIDATE"], "APPROVED")

    def test_d3_open_g3_never_approves_even_with_resolved_caveats(self) -> None:
        reports = copy.deepcopy(self.fresh_reports)
        reports["g1_g8"]["gates"]["G3"]["status"] = "OPEN"
        reports["g1_g8"]["g3_sm_target_track"]["downstream_caveats_resolved"] = True
        result = self.evaluate(reports)
        verdict = confirmation.evaluate_reports(
            copy.deepcopy(reports), current_test_count=321
        )
        for report in (result, verdict):
            self.assertFalse(report["internal_candidate_approved"])
            self.assertFalse(report["internal_candidate_gate"]["G1_G2_G3_closed"])
            self.assertFalse(report["internal_candidate_gate"]["G3_closed"])
        self.assertEqual(verdict["tiers"]["INTERNAL_CANDIDATE"], "WITHHELD")
        # With ledger G3 OPEN the texts fall back to the G3-open branch.
        self.assertEqual(result["verdict"], gate._verdict(True))
        self.assertEqual(
            verdict["correct_public_claim"],
            confirmation._claim_text(True)["correct_public_claim"],
        )

    def test_d3_missing_or_unclosed_track_never_approves(self) -> None:
        removed = copy.deepcopy(self.fresh_reports)
        del removed["g1_g8"]["g3_sm_target_track"]
        not_closed = copy.deepcopy(self.fresh_reports)
        not_closed["g1_g8"]["g3_sm_target_track"]["closed"] = False
        not_closed["g1_g8"]["g3_sm_target_track"]["downstream_caveats_resolved"] = True
        forged_type = copy.deepcopy(self.fresh_reports)
        forged_type["g1_g8"]["g3_sm_target_track"]["downstream_caveats_resolved"] = "true"
        for label, reports in (
            ("removed", removed),
            ("not_closed", not_closed),
            ("forged_type", forged_type),
        ):
            with self.subTest(case=label):
                result = self.evaluate(reports)
                verdict = confirmation.evaluate_reports(
                    copy.deepcopy(reports), current_test_count=321
                )
                for report in (result, verdict):
                    self.assertFalse(report["internal_candidate_approved"])
                    self.assertFalse(
                        report["internal_candidate_gate"][
                            "closing_track_downstream_caveats_resolved"
                        ]
                    )
                    self.assertFalse(report["internal_candidate_gate"]["caveats_cleared"])
                self.assertEqual(verdict["tiers"]["INTERNAL_CANDIDATE"], "WITHHELD")

    def test_no_approval_or_exclusion_survives_contract_mismatch(self) -> None:
        reports = copy.deepcopy(self.fresh_reports)
        # Mismatch: the same model without its bound SARAH attestation.
        reports["x_contract"] = x_gate.build_report(
            model_text=x_gate.MODEL.read_text(encoding="utf-8")
        )
        reports["authoritative"]["classification"].update(
            {
                "whole_model_validated": True,
                "empirical_discovery": True,
                "whole_model_excluded": True,
            }
        )
        result = self.evaluate(reports)
        self.assertFalse(result["internal_candidate_approved"])
        self.assertFalse(result["conditional_benchmark_approved"])
        self.assertFalse(result["full_phenomenology_approved"])
        self.assertFalse(result["empirical_realization_approved"])
        self.assertFalse(result["whole_model_excluded"])

    def test_historical_option_c_results_are_scoped_context(self) -> None:
        result = self.evaluate()
        historical = result["historical_option_c_subtheorems"]
        self.assertFalse(historical["authoritative_for_gauged_model"])
        self.assertEqual(historical["G1"]["invariant_directions"], 64)
        self.assertEqual(historical["G1"]["real_potential_parameters"], 91)
        self.assertEqual(historical["G2"]["dense_Hessian_shape"], [486, 486])
        self.assertEqual(
            historical["G3"]["anchored_witness_negative_modes"], 46
        )
        self.assertFalse(historical["G3"]["strict_local_minimum_found"])
        self.assertFalse(historical["G3"]["whole_gauged_model_excluded"])

    def test_source_audit_failure_is_execution_failure(self) -> None:
        reports = copy.deepcopy(self.fresh_reports)
        reports["x_contract"]["n_failed"] = 1
        reports["x_contract"]["failures"] = ["sabotaged"]
        result = self.evaluate(reports)
        self.assertFalse(result["integrity_pass"])
        self.assertEqual(result["overall_state"], "EXECUTION_FAIL")
        self.assertEqual(
            result["classification"], "THEORY_CONFIRMATION_AUDIT_EXECUTION_FAILED"
        )
        self.assertEqual(result["decision"], "WITHHOLD_APPROVAL")
        self.assertFalse(result["whole_model_excluded"])

    def test_missing_source_fails_closed(self) -> None:
        reports = copy.deepcopy(self.fresh_reports)
        del reports["gauged_contract"]
        result = self.evaluate(reports)
        self.assertFalse(result["integrity_pass"])
        self.assertTrue(
            any("required fresh report missing" in item for item in result["errors"])
        )

    def test_build_report_uses_fresh_builders_not_release_json(self) -> None:
        with patch.object(
            confirmation,
            "fresh_source_reports",
            return_value=copy.deepcopy(self.fresh_reports),
        ) as fresh:
            report = gate.build_report()
        fresh.assert_called_once_with()
        self.assertEqual(report["overall_state"], "OPEN")
        self.assertEqual(report["decision"], "WITHHOLD_APPROVAL")

    def test_default_exit_accepts_honest_state_but_strict_modes_fail(self) -> None:
        report = self.evaluate()
        self.assertEqual(gate.exit_code(report), 0)
        self.assertEqual(gate.exit_code(report, expect_open=True), 0)
        self.assertNotEqual(gate.exit_code(report, expect_blocked=True), 0)
        self.assertEqual(gate.exit_code(report, expect_full_block=True), 0)
        self.assertNotEqual(
            gate.exit_code(report, require_internal_approval=True), 0
        )
        self.assertNotEqual(gate.exit_code(report, require_full_approval=True), 0)

    def test_cli_strict_approval_modes_are_nonzero(self) -> None:
        report = self.evaluate()
        with patch.object(gate, "build_report", return_value=report):
            with redirect_stdout(io.StringIO()):
                self.assertEqual(gate.main(["--no-write"]), 0)
                self.assertEqual(
                    gate.main(["--no-write", "--require-internal-approval"]), 2
                )
                self.assertEqual(
                    gate.main(["--no-write", "--require-full-approval"]), 3
                )

    def test_confirmation_cli_has_same_fail_closed_exit_policy(self) -> None:
        verdict = confirmation.evaluate_reports(
            copy.deepcopy(self.fresh_reports),
            current_test_count=321,
        )
        self.assertEqual(confirmation.exit_code(verdict), 0)
        self.assertEqual(
            confirmation.exit_code(verdict, require_internal_approval=True), 2
        )
        self.assertEqual(
            confirmation.exit_code(verdict, require_full_approval=True), 3
        )
        with patch.object(confirmation, "build_verdict", return_value=verdict):
            with redirect_stdout(io.StringIO()):
                self.assertEqual(confirmation.main(["--no-write"]), 0)
                self.assertEqual(
                    confirmation.main(
                        ["--no-write", "--require-internal-approval"]
                    ),
                    2,
                )
                self.assertEqual(
                    confirmation.main(["--no-write", "--require-full-approval"]),
                    3,
                )


if __name__ == "__main__":
    unittest.main()
