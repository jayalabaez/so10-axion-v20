#!/usr/bin/env python3
"""Fail-closed and sabotage tests for the ultimate v20 gate.

They also cover the confirmation layer it consumes.  G4 is CLOSED in the
ledger at the G3 witness benchmark (tree level) on the certified closure
evidence of ``g4_sm_closure_binding_v20``, which meets decision D3.  The
user's decision D-E (2026-09-26) holds the internal-candidate tier until G7
is CLOSED (strictly: G7 and its ledger dependency G6 CLOSED), so the tier
stays WITHHELD and the overall state OPEN.  A reopened G4, or a CLOSED
status without certified evidence, fails D3 as well; only D3 together with a
CLOSED G7 approves the tier (hypothetical ledgers below).
"""

from __future__ import annotations

import copy
import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import exact_x_symmetry_consistency_gate_v20 as x_gate
import g3_sm_target_track_v20 as sm_track
import g4_sm_closure_binding_v20 as g4_closure
import theory_confirmation_verdict_v20 as confirmation
import ultimate_theory_gate_v20 as gate

APPROVED_STATUS = (
    "ULTIMATE_GATE_AUDIT_COMPLETE__INTERNAL_CANDIDATE_APPROVED__FULL_APPROVAL_OPEN"
)
WITHHELD_STATUS = "ULTIMATE_GATE_AUDIT_COMPLETE__APPROVAL_OPEN"

TWO_LOOP_NO_GO = (
    "for the declared benchmark (5 x (16 + 16bar) spectators at M_s ~ M_I, "
    "v_S = M_I) three independent two-loop RG codes find no perturbative gauge "
    "unification"
)

ULTIMATE_HELD_VERDICT = (
    "WITHHOLD APPROVAL. The audit has no execution failure and the gauged-U(1)_X "
    "model contract is attested by bound external SARAH execution evidence; G1, "
    "G2, G3 (SM Pati-Salam benchmark family, scoped), G4 (at the G3 witness "
    "benchmark, tree level) and G5 are closed, which meets decision D3, but "
    "decision D-E holds the internal-candidate tier until G7 is CLOSED: "
    + TWO_LOOP_NO_GO
    + ", a G7 no-go for that benchmark. The G6-G8 scientific gates remain open "
    "or blocked (sub-M_I coloured states, positivity beyond tree level and "
    "electroweak symmetry breaking, RG-anchor content and the Higgs quartic, "
    "Yukawas (flavour excluded on this witness branch at renormalizable tree "
    "level, Route C) and proton decay). No internal-candidate, "
    "conditional-benchmark, full-phenomenology, empirical-realization, or "
    "whole-model-exclusion claim is approved; the whole model is neither "
    "validated nor excluded."
)

ULTIMATE_G3_CLOSED_WITHHELD_PREFIX = (
    "WITHHOLD APPROVAL. The audit has no execution failure and the "
    "gauged-U(1)_X model contract is attested by bound external "
    "SARAH execution evidence; G3 is closed on the SM Pati-Salam "
    "benchmark family (scoped), but the G4 and G6-G8 scientific "
    "gates remain open and the closing track's downstream caveats "
    "are unresolved. "
)

CONFIRMATION_HELD_INCORRECT_CLAIM = (
    "G3 or G4 is closed for a physically realistic or natural vacuum (the "
    "doublet-triplet splitting, O05 and M_I are tuned; G4 is certified at the "
    "r0 = 1/5, x0 = 1 benchmark at tree level only); the axion stays massless "
    "once the QCD anomaly or PQ-violating operators are included; the tuned "
    "eps = 0 point is the G3 witness; an internal candidate is approved "
    "(decision D-E holds it until G7 is CLOSED); G6, G7 or G8 is closed; the "
    "certified SU(5)+Delta point is a Standard-Model vacuum; the current "
    "repository validates the full theory; or the historical saddle excludes "
    "the gauged-U(1)_X model."
)

CONFIRMATION_HELD_VERDICT = (
    "WITHHOLD APPROVAL. The audit succeeds and the gauged-U(1)_X model contract "
    "is attested by bound external SARAH execution evidence. G1, G2, G3 (SM "
    "Pati-Salam benchmark family, scoped), G4 (at the G3 witness benchmark, tree "
    "level) and G5 are closed, which meets decision D3, but decision D-E holds "
    "the internal-candidate tier until G7 is CLOSED: "
    + TWO_LOOP_NO_GO
    + ". G6 is open and G7-G8 remain blocked (sub-M_I coloured states and "
    "positivity beyond tree level, electroweak symmetry breaking, RG-anchor "
    "content, the Higgs quartic, Yukawas (flavour excluded on this witness "
    "branch at renormalizable tree level, Route C) and proton decay), so no "
    "internal, conditional-benchmark, full-phenomenology, empirical, or "
    "exclusion claim is approved; the whole model is neither validated nor "
    "excluded."
)

HISTORY = (
    "Historical Option-C calculations are scoped subtheorems and neither "
    "validate nor exclude the gauged model."
)

TIER_DEFINITIONS = {
    "INTERNAL_CANDIDATE": (
        "internal consistency of the attested model contract: G1, G2 and G3 "
        "CLOSED, decision D3 satisfied (the closing G3 track's downstream "
        "caveats resolved, or G4 CLOSED) and, by decision D-E, G7 CLOSED; not "
        "phenomenology"
    ),
    "CONDITIONAL_BENCHMARK": (
        "a numerically safe benchmark region under extra portal assumptions on "
        "the current contract; withheld because the aligned benchmarks were "
        "computed under the superseded no-X contract"
    ),
    "FULL_PHENOMENOLOGY": (
        "every G1-G8 gate CLOSED and the authoritative full-model gate validated"
    ),
    "EMPIRICAL_REALIZATION": "full phenomenology plus a real empirical discovery",
    "WHOLE_MODEL_EXCLUSION": (
        "a proof-grade exclusion by the authoritative full-model gate"
    ),
}

APPROVED_TIERS = {
    "INTERNAL_CANDIDATE": "APPROVED",
    "CONDITIONAL_BENCHMARK": "WITHHELD",
    "FULL_PHENOMENOLOGY": "WITHHELD",
    "EMPIRICAL_REALIZATION": "NOT_ESTABLISHED",
    "WHOLE_MODEL_EXCLUSION": "NOT_ESTABLISHED",
}
WITHHELD_TIERS = dict(APPROVED_TIERS, INTERNAL_CANDIDATE="WITHHELD")


class UltimateGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fresh_reports = confirmation.fresh_source_reports()

    def evaluate(self, reports: dict | None = None) -> dict:
        return gate.evaluate_reports(
            copy.deepcopy(reports or self.fresh_reports),
            current_test_count=321,
        )

    def confirm(self, reports: dict | None = None) -> dict:
        return confirmation.evaluate_reports(
            copy.deepcopy(reports or self.fresh_reports),
            current_test_count=321,
        )

    def reports_with_g4(self, status: str) -> dict:
        reports = copy.deepcopy(self.fresh_reports)
        reports["g1_g8"]["gates"]["G4"]["status"] = status
        return reports

    @staticmethod
    def close_g7(reports: dict) -> dict:
        # Hypothetical: G7 CLOSED together with its ledger dependency G6.
        for name in ("G6", "G7"):
            reports["g1_g8"]["gates"][name]["status"] = "CLOSED"
        return reports

    def assert_withheld_g3_only(self, result: dict, verdict: dict) -> None:
        """D3 not met (G4 not strictly CLOSED, caveats unresolved): no hold, no approval."""
        for report in (result, verdict):
            self.assertFalse(report["internal_candidate_approved"])
            self.assertFalse(report["internal_candidate_gate"]["G4_closed"])
            self.assertFalse(report["internal_candidate_gate"]["D3_satisfied"])
            self.assertFalse(report["internal_candidate_gate"]["caveats_cleared"])
            self.assertFalse(report["internal_candidate_gate"]["approval_held_pending_G7"])
            self.assertEqual(report["classification"], "AUTHORITATIVE_GATES_OPEN")
            self.assertEqual(report["decision"], "WITHHOLD_APPROVAL")
            self.assertEqual(report["overall_state"], "OPEN")
            self.assertIsNone(report["internal_candidate_scope"])
            self.assertIsNone(report["internal_candidate_hold"])
            self.assertEqual(report["tiers"], WITHHELD_TIERS)
        self.assertEqual(result["status"], WITHHELD_STATUS)
        self.assertEqual(
            verdict["status"], "THEORY_CONFIRMATION_AUDIT_COMPLETE__GATES_OPEN"
        )
        self.assertFalse(verdict["approval"]["internal_candidate"])
        self.assertEqual(result["verdict"], gate._verdict(True, g3_closed=True))
        self.assertTrue(result["verdict"].startswith(ULTIMATE_G3_CLOSED_WITHHELD_PREFIX))
        for key, text in confirmation._claim_text(True, g3_closed=True).items():
            self.assertEqual(verdict[key], text)
        self.assertEqual(gate.exit_code(result, require_internal_approval=True), 2)
        self.assertEqual(
            confirmation.exit_code(verdict, require_internal_approval=True), 2
        )

    def assert_approved(self, result: dict, verdict: dict, *, g4_closed: bool) -> None:
        for report in (result, verdict):
            self.assertIs(report["internal_candidate_approved"], True)
            gate_d3 = report["internal_candidate_gate"]
            self.assertIs(gate_d3["D3_satisfied"], True)
            self.assertIs(gate_d3["G7_closed"], True)
            self.assertIs(gate_d3["caveats_cleared"], True)
            self.assertIs(gate_d3["approval_held_pending_G7"], False)
            self.assertIs(gate_d3["G4_closed"], g4_closed)
            self.assertEqual(report["overall_state"], "OPEN")
            self.assertEqual(report["decision"], confirmation.DECISION_INTERNAL_CANDIDATE)
            self.assertEqual(
                report["classification"], confirmation.CLASSIFICATION_INTERNAL_CANDIDATE
            )
            self.assertEqual(report["tiers"], APPROVED_TIERS)
            self.assertIsNone(report["internal_candidate_hold"])
            self.assertEqual(
                report["internal_candidate_scope"],
                confirmation.INTERNAL_CANDIDATE_SCOPE
                if g4_closed
                else confirmation.INTERNAL_CANDIDATE_SCOPE_CAVEATS_PATH,
            )
            self.assertFalse(report["full_phenomenology_approved"])
            self.assertFalse(report["conditional_benchmark_approved"])
        self.assertEqual(result["status"], APPROVED_STATUS)
        self.assertEqual(verdict["status"], confirmation.STATUS_INTERNAL_CANDIDATE)
        self.assertEqual(
            result["verdict"],
            gate._verdict(True, g3_closed=True, g4_closed=g4_closed, internal_candidate=True),
        )
        for key, text in confirmation._claim_text(
            True, g3_closed=True, g4_closed=g4_closed, internal_candidate=True
        ).items():
            self.assertEqual(verdict[key], text)
        self.assertEqual(gate.exit_code(result, require_internal_approval=True), 0)
        self.assertEqual(
            confirmation.exit_code(verdict, require_internal_approval=True), 0
        )

    # ------------------------------------------------------------------
    # The current state: G4 CLOSED meets D3; D-E holds the tier (G7 open).
    # ------------------------------------------------------------------

    def test_current_state_is_open_with_the_internal_candidate_held_pending_g7(self) -> None:
        # The SARAH-attested contract is consistent; G1-G5 are CLOSED (G3 on
        # the SM Pati-Salam benchmark family, G4 at its witness benchmark at
        # tree level); G6 is OPEN and G7-G8 BLOCKED.  Decision D-E holds the
        # internal-candidate tier until G7 is CLOSED.
        result = self.evaluate()
        self.assertTrue(result["integrity_pass"])
        self.assertEqual(result["n_failed"], 0)
        self.assertEqual(result["overall_state"], "OPEN")
        self.assertEqual(result["status"], WITHHELD_STATUS)
        self.assertEqual(result["classification"], "AUTHORITATIVE_GATES_OPEN")
        self.assertEqual(result["decision"], "WITHHOLD_APPROVAL")
        self.assertEqual(
            result["validation_matrix_contract_gate"]["state"], "PASS"
        )
        self.assertIs(result["internal_candidate_approved"], False)
        self.assertFalse(result["conditional_benchmark_approved"])
        self.assertFalse(result["full_phenomenology_approved"])
        self.assertFalse(result["full_theory_validated"])
        self.assertFalse(result["empirical_realization_approved"])
        self.assertFalse(result["whole_model_excluded"])
        self.assertEqual(result["tiers"], WITHHELD_TIERS)
        self.assertIsNone(result["internal_candidate_scope"])
        self.assertEqual(
            result["internal_candidate_hold"], confirmation.INTERNAL_CANDIDATE_HOLD
        )
        verdict = self.confirm()
        self.assertEqual(
            verdict["status"], "THEORY_CONFIRMATION_AUDIT_COMPLETE__GATES_OPEN"
        )
        self.assertEqual(verdict["classification"], "AUTHORITATIVE_GATES_OPEN")
        self.assertEqual(verdict["decision"], confirmation.WITHHOLD_APPROVAL)
        self.assertEqual(verdict["overall_state"], "OPEN")
        self.assertEqual(verdict["verdict_code"], verdict["classification"])
        self.assertIs(verdict["approval"]["internal_candidate"], False)
        self.assertFalse(verdict["approval"]["conditional_benchmark"])
        self.assertFalse(verdict["approval"]["full_phenomenology"])
        self.assertFalse(verdict["approval"]["empirical_realization"])
        self.assertFalse(verdict["approval"]["whole_model_excluded"])
        self.assertEqual(verdict["tiers"], WITHHELD_TIERS)
        self.assertEqual(verdict["tier_definitions"], TIER_DEFINITIONS)
        self.assertEqual(confirmation.TIER_DEFINITIONS, TIER_DEFINITIONS)
        self.assertEqual(
            verdict["internal_candidate_hold"], confirmation.INTERNAL_CANDIDATE_HOLD
        )

    def test_internal_candidate_gate_records_d3_met_and_the_d_e_hold(self) -> None:
        result = self.evaluate()
        verdict = self.confirm()
        for report in (result, verdict):
            gate_d3 = report["internal_candidate_gate"]
            self.assertTrue(gate_d3["G1_G2_G3_closed"])
            self.assertTrue(gate_d3["G3_closed"])
            self.assertEqual(gate_d3["closing_track"], "sm_pati_salam")
            self.assertIs(gate_d3["closing_track_downstream_caveats_resolved"], False)
            self.assertIs(gate_d3["G4_closed"], True)
            self.assertIs(gate_d3["G4_closure_evidence_certified"], True)
            self.assertIs(gate_d3["D3_satisfied"], True)
            self.assertIs(gate_d3["G7_closed"], False)
            self.assertIs(gate_d3["caveats_cleared"], False)
            self.assertIs(gate_d3["approval_held_pending_G7"], True)
            self.assertEqual(gate_d3["rule"], sm_track.D3_RULE)
            self.assertEqual(gate_d3["D_E_rule"], confirmation.D_E_RULE)
            self.assertEqual(gate_d3["D_E_evidence"], confirmation.D_E_EVIDENCE)
            self.assertEqual(gate_d3["G4_closure_decision"], g4_closure.G4_CLOSURE_DECISION)
            self.assertNotIn("D3_cascade", gate_d3)
        ledger = self.fresh_reports["g1_g8"]
        self.assertIs(g4_closure.ledger_g4_closed(ledger), True)
        evidence = ledger["gates"]["G4"]["closure_evidence"]
        self.assertIs(evidence["certified"], True)
        self.assertEqual(evidence["status"], g4_closure.REQUIRED_STATUS)
        track = ledger["g3_sm_target_track"]
        self.assertIs(track["closed"], True)
        self.assertIs(track["downstream_caveats_resolved"], False)
        # The hold is tied to the live ledger: G6 OPEN, G7 and G8 BLOCKED.
        gates = ledger["gates"]
        self.assertEqual(
            sorted(k for k, v in gates.items() if v["status"] == "CLOSED"),
            ["G1", "G2", "G3", "G4", "G5"],
        )
        self.assertEqual(gates["G6"]["status"], "OPEN")
        self.assertEqual(gates["G7"]["status"], "BLOCKED")
        self.assertEqual(gates["G8"]["status"], "BLOCKED")
        self.assertEqual(gates["G3"]["closing_track"], "sm_pati_salam")

    def test_hold_text_cites_decision_d_e_and_the_two_loop_no_go(self) -> None:
        hold = confirmation.INTERNAL_CANDIDATE_HOLD
        for fragment in (
            "WITHHELD, held pending G7 (decision D-E)",
            "G4 is CLOSED at the G3 witness benchmark (tree level)",
            "meets decision D3's G4 condition",
            "held until G7 is CLOSED",
            "5 x (16 + 16bar) spectators at M_s ~ M_I",
            "v_S = M_I",
            "three independent two-loop RG codes",
            "no perturbative two-loop gauge unification",
            "not a committed repository certificate",
            "decoupling v_S from v_R",
        ):
            self.assertIn(fragment, hold)
        self.assertIn(confirmation.D_E_EVIDENCE, hold)
        self.assertIn("held until G7 is CLOSED", confirmation.D_E_RULE)
        caveats_hold = confirmation.INTERNAL_CANDIDATE_HOLD_CAVEATS_PATH
        self.assertNotIn("G4 is CLOSED", caveats_hold)
        self.assertIn("while G4 is not CLOSED", caveats_hold)
        self.assertIn(confirmation.D_E_EVIDENCE, caveats_hold)
        self.assertIn(TWO_LOOP_NO_GO, gate.VERDICT_INTERNAL_CANDIDATE_HELD_PENDING_G7)

    def test_internal_candidate_scope_texts_require_g7_closed(self) -> None:
        # Only used on an approval, which D-E makes unreachable until G7 closes.
        scope = confirmation.INTERNAL_CANDIDATE_SCOPE
        for fragment in (
            "tier 1: internal consistency, not phenomenology",
            "decision D3 satisfied by G4 CLOSED",
            "tree level",
            "G7 CLOSED (decision D-E)",
            "massless only for the renormalizable PQ-neutral benchmark potential",
            "CKM = 1 and m_t = m_b, which data exclude (G8 Route C)",
            "Not phenomenologically validated; whole model neither validated nor excluded.",
        ):
            self.assertIn(fragment, scope)
        caveats_scope = confirmation.INTERNAL_CANDIDATE_SCOPE_CAVEATS_PATH
        self.assertNotIn("satisfied by G4 CLOSED", caveats_scope)
        self.assertIn("while G4 is not CLOSED", caveats_scope)
        self.assertIn("G7 CLOSED (decision D-E)", caveats_scope)
        self.assertIn(
            "Not phenomenologically validated; whole model neither validated nor excluded.",
            caveats_scope,
        )

    def test_scope_document_matches_the_tiers(self) -> None:
        text = (Path(gate.__file__).resolve().parent / "ULTIMATE_THEORY_GATE_V20_SCOPE.md").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("levels 1 and 2", text)
        self.assertNotIn("tier 1 APPROVED", text)
        for fragment in (
            "reports five tiers",
            "1. **Internal candidate**",
            "2. **Conditional benchmark**",
            "3. **Full phenomenology**",
            "4. **Empirical realization**",
            "5. **Whole-model exclusion**",
            "and, by decision D-E, G7 CLOSED",
            "Current result: tier 1 WITHHELD, held pending G7 (decision D-E)",
            "tiers 2 and 3 WITHHELD; tiers 4 and 5 NOT_ESTABLISHED",
            "G4 at its witness benchmark at tree level",
            "three independent two-loop RG codes find no perturbative gauge unification",
            "not a committed certificate",
            "The whole model is neither validated nor excluded.",
        ):
            self.assertIn(fragment, text)

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
        self.assertFalse(result["internal_candidate_approved"])
        self.assertIsNone(result["internal_candidate_scope"])
        self.assertIsNone(result["internal_candidate_hold"])
        self.assertFalse(result["internal_candidate_gate"]["approval_held_pending_G7"])
        self.assertEqual(result["verdict"], gate._verdict(False))

    # ------------------------------------------------------------------
    # Verdict and claim texts.
    # ------------------------------------------------------------------

    def test_verdict_text_branches_on_contract_readiness(self) -> None:
        held = gate._verdict(True, g3_closed=True, g4_closed=True, held_pending_g7=True)
        approved = gate._verdict(True, g3_closed=True, g4_closed=True, internal_candidate=True)
        approved_caveats = gate._verdict(True, g3_closed=True, internal_candidate=True)
        held_caveats = gate._verdict(True, g3_closed=True, held_pending_g7=True)
        withheld = gate._verdict(True, g3_closed=True)
        ready_g3_open = gate._verdict(True)
        blocked = gate._verdict(False)
        self.assertEqual(held, ULTIMATE_HELD_VERDICT)
        self.assertEqual(held, gate.VERDICT_INTERNAL_CANDIDATE_HELD_PENDING_G7)
        # A strict G4 closure without an approval is always the D-E hold text.
        self.assertEqual(gate._verdict(True, g3_closed=True, g4_closed=True), held)
        for text in (held, approved, approved_caveats, held_caveats, withheld, ready_g3_open):
            self.assertNotIn("lacks", text)
            self.assertNotIn("no v2 manifest", text)
            self.assertIn("attested by bound external SARAH execution", text)
        for text in (held, held_caveats, withheld, ready_g3_open, blocked):
            self.assertTrue(text.startswith("WITHHOLD APPROVAL."))
            self.assertNotIn("APPROVE INTERNAL CANDIDATE", text)
        # Hypothetical approvals need G7 CLOSED (decision D-E).
        for text in (approved, approved_caveats):
            self.assertTrue(text.startswith("APPROVE INTERNAL CANDIDATE ONLY."))
            self.assertIn("G7 is CLOSED (decision D-E)", text)
            self.assertIn("not phenomenologically validated", text)
        self.assertIn("G4 is CLOSED at the G3 witness benchmark, tree level", approved)
        self.assertNotIn("G4 is CLOSED at", approved_caveats)
        self.assertIn("while G4 is not CLOSED", approved_caveats)
        self.assertIn("decision D-E holds the internal-candidate tier", held_caveats)
        self.assertIn("the G4 and G6-G8 scientific gates remain open", held_caveats)
        self.assertNotIn("G4 (at the G3 witness", held_caveats)
        # The G3-closed withheld text (G4 not CLOSED, D3 not met) is unchanged.
        self.assertTrue(withheld.startswith(ULTIMATE_G3_CLOSED_WITHHELD_PREFIX))
        self.assertTrue(
            withheld.endswith(
                "No internal-candidate, conditional-benchmark, full-phenomenology, "
                "empirical-realization, or whole-model-exclusion claim is approved."
            )
        )
        self.assertIn(
            "the G3, G4 and G6-G8 scientific gates remain open", ready_g3_open
        )
        self.assertIn(
            "has no v2 manifest/log-bound external SARAH execution evidence",
            blocked,
        )
        # A blocked contract ignores the G3/G4/D3/D-E flags.
        self.assertEqual(gate._verdict(False, g3_closed=True), blocked)
        self.assertEqual(
            gate._verdict(
                False, g3_closed=True, g4_closed=True, internal_candidate=True, held_pending_g7=True
            ),
            blocked,
        )
        self.assertEqual(self.evaluate()["verdict"], held)

    def test_confirmation_text_branches_on_contract_readiness(self) -> None:
        held = confirmation._claim_text(
            True, g3_closed=True, g4_closed=True, held_pending_g7=True
        )
        approved = confirmation._claim_text(
            True, g3_closed=True, g4_closed=True, internal_candidate=True
        )
        approved_caveats = confirmation._claim_text(True, g3_closed=True, internal_candidate=True)
        held_caveats = confirmation._claim_text(True, g3_closed=True, held_pending_g7=True)
        withheld = confirmation._claim_text(True, g3_closed=True)
        ready_g3_open = confirmation._claim_text(True)
        blocked = confirmation._claim_text(False)
        for text in (
            list(held.values())
            + list(approved.values())
            + list(approved_caveats.values())
            + list(held_caveats.values())
            + list(withheld.values())
            + list(ready_g3_open.values())
        ):
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
        self.assertEqual(
            confirmation._claim_text(
                False, g3_closed=True, g4_closed=True, internal_candidate=True, held_pending_g7=True
            ),
            blocked,
        )
        # The current branch: G4 CLOSED meets D3; D-E holds the tier.
        self.assertEqual(
            held["correct_public_claim"],
            "The authoritative gauged-U(1)_X model contract is attested by a "
            "manifest/log-bound external SARAH 4.15.3 execution, and G1, G2, G3, "
            "G4 and G5 are closed. " + sm_track.CLOSURE_SCOPE + " "
            + g4_closure.G4_CLOSED_SENTENCE + " The internal candidate is "
            + confirmation.INTERNAL_CANDIDATE_HOLD
            + " G6 is open and G7-G8 remain blocked. G1-G8 approval is withheld. "
            + HISTORY,
        )
        self.assertEqual(held["incorrect_claim_do_not_use"], CONFIRMATION_HELD_INCORRECT_CLAIM)
        self.assertEqual(held["verdict"], CONFIRMATION_HELD_VERDICT)
        self.assertEqual(
            confirmation._claim_text(True, g3_closed=True, g4_closed=True), held
        )
        self.assertIn(
            "massless only for the renormalizable PQ-neutral benchmark potential",
            held["correct_public_claim"],
        )
        for text in held.values():
            self.assertNotIn("APPROVE INTERNAL CANDIDATE", text)
            self.assertNotIn("the internal-candidate tier is approved", text)
        # Hypothetical approval with G4 CLOSED and G7 CLOSED.
        self.assertTrue(approved["verdict"].startswith("APPROVE INTERNAL CANDIDATE ONLY."))
        self.assertIn("G7 is CLOSED (decision D-E)", approved["verdict"])
        self.assertIn(g4_closure.G4_CLOSED_SENTENCE, approved["correct_public_claim"])
        self.assertIn(confirmation.INTERNAL_CANDIDATE_SCOPE, approved["correct_public_claim"])
        self.assertIn("every G1-G8 gate is closed", approved["incorrect_claim_do_not_use"])
        # Hypothetical approval on the caveats path: never claims G4.
        self.assertTrue(approved_caveats["verdict"].startswith("APPROVE INTERNAL CANDIDATE ONLY."))
        for text in approved_caveats.values():
            self.assertNotIn("G4 (at the G3 witness", text)
            self.assertNotIn(g4_closure.G4_CLOSED_SENTENCE, text)
        self.assertIn(
            confirmation.INTERNAL_CANDIDATE_SCOPE_CAVEATS_PATH,
            approved_caveats["correct_public_claim"],
        )
        # Hypothetical D-E hold on the caveats path: never claims G4.
        self.assertTrue(held_caveats["verdict"].startswith("WITHHOLD APPROVAL."))
        self.assertIn(
            confirmation.INTERNAL_CANDIDATE_HOLD_CAVEATS_PATH,
            held_caveats["correct_public_claim"],
        )
        self.assertIn("G4 and G6-G8 are not closed", held_caveats["verdict"])
        for text in held_caveats.values():
            self.assertNotIn(g4_closure.G4_CLOSED_SENTENCE, text)
        # The G3-closed withheld text (D3 not met) is unchanged.
        self.assertIn(sm_track.CLOSURE_SCOPE, withheld["correct_public_claim"])
        self.assertIn("G1, G2, G3 and G5 are closed.", withheld["correct_public_claim"])
        self.assertIn("G1-G8 approval is withheld.", withheld["correct_public_claim"])
        self.assertIn(
            "the tuned eps = 0 point is the G3 witness",
            withheld["incorrect_claim_do_not_use"],
        )
        self.assertIn(
            "an internal candidate is approved", withheld["incorrect_claim_do_not_use"]
        )
        self.assertIn(
            "the closing track's downstream caveats are unresolved",
            withheld["verdict"],
        )
        self.assertTrue(withheld["verdict"].startswith("WITHHOLD APPROVAL."))
        self.assertIn("G3 remains open", ready_g3_open["correct_public_claim"])
        verdict = self.confirm()
        for key, text in held.items():
            self.assertEqual(verdict[key], text)

    # ------------------------------------------------------------------
    # Decision D3 (G4 CLOSED or caveats resolved) and decision D-E (G7).
    # ------------------------------------------------------------------

    def test_d_e_closed_g7_with_closed_g4_approves_the_internal_candidate(self) -> None:
        reports = self.close_g7(copy.deepcopy(self.fresh_reports))
        self.assert_approved(self.evaluate(reports), self.confirm(reports), g4_closed=True)

    def test_d_e_g7_not_strictly_closed_stays_held(self) -> None:
        # G7 counts as CLOSED only as the exact status with G6 also CLOSED.
        g7_without_g6 = copy.deepcopy(self.fresh_reports)
        g7_without_g6["g1_g8"]["gates"]["G7"]["status"] = "CLOSED"
        g7_lowercase = self.close_g7(copy.deepcopy(self.fresh_reports))
        g7_lowercase["g1_g8"]["gates"]["G7"]["status"] = "closed"
        g7_removed = self.close_g7(copy.deepcopy(self.fresh_reports))
        del g7_removed["g1_g8"]["gates"]["G7"]
        g6_bool = self.close_g7(copy.deepcopy(self.fresh_reports))
        g6_bool["g1_g8"]["gates"]["G6"]["status"] = True
        for label, reports in (
            ("g7_without_g6", g7_without_g6),
            ("g7_lowercase", g7_lowercase),
            ("g7_removed", g7_removed),
            ("g6_bool", g6_bool),
        ):
            with self.subTest(case=label):
                result = self.evaluate(reports)
                verdict = self.confirm(reports)
                for report in (result, verdict):
                    self.assertFalse(report["internal_candidate_approved"])
                    self.assertFalse(report["internal_candidate_gate"]["G7_closed"])
                    self.assertFalse(report["internal_candidate_gate"]["caveats_cleared"])
                    self.assertTrue(report["internal_candidate_gate"]["approval_held_pending_G7"])
                    self.assertEqual(
                        report["internal_candidate_hold"], confirmation.INTERNAL_CANDIDATE_HOLD
                    )
                    self.assertEqual(report["tiers"], WITHHELD_TIERS)
                self.assertEqual(result["verdict"], ULTIMATE_HELD_VERDICT)
                self.assertEqual(gate.exit_code(result, require_internal_approval=True), 2)

    def test_d3_reopened_g4_withholds_internal_candidate(self) -> None:
        for label, reports in (
            ("g7_open", self.reports_with_g4("OPEN")),
            ("g7_closed", self.close_g7(self.reports_with_g4("OPEN"))),
        ):
            with self.subTest(case=label):
                result = self.evaluate(reports)
                verdict = self.confirm(reports)
                self.assert_withheld_g3_only(result, verdict)
                for report in (result, verdict):
                    # The evidence is still certified; only the ledger status reopened.
                    self.assertIs(
                        report["internal_candidate_gate"]["G4_closure_evidence_certified"], True
                    )

    def test_d3_forged_g4_closure_without_certified_evidence_withholds(self) -> None:
        certified_false = self.reports_with_g4("CLOSED")
        certified_false["g1_g8"]["gates"]["G4"]["closure_evidence"]["certified"] = False
        certified_str = self.reports_with_g4("CLOSED")
        certified_str["g1_g8"]["gates"]["G4"]["closure_evidence"]["certified"] = "true"
        removed = self.reports_with_g4("CLOSED")
        removed["g1_g8"]["gates"]["G4"].pop("closure_evidence", None)
        old_status = self.reports_with_g4("CLOSED")
        old_status["g1_g8"]["gates"]["G4"]["closure_evidence"]["status"] = (
            "G4_SM_PATI_SALAM_PHYSICAL_QUOTIENT_CERTIFIED__G4_NOT_WIRED"
        )
        for label, reports, evidence_certified in (
            ("certified_false", certified_false, False),
            ("certified_str", certified_str, False),
            ("removed", removed, False),
            ("old_status", old_status, True),
        ):
            # Even a CLOSED G7 cannot approve on a forged G4 closure.
            for g7_label, candidate in (("g7_open", reports), ("g7_closed", self.close_g7(copy.deepcopy(reports)))):
                with self.subTest(case=label, g7=g7_label):
                    result = self.evaluate(candidate)
                    verdict = self.confirm(candidate)
                    self.assertEqual(
                        candidate["g1_g8"]["gates"]["G4"]["status"], "CLOSED"
                    )
                    self.assert_withheld_g3_only(result, verdict)
                    for report in (result, verdict):
                        self.assertIs(
                            report["internal_candidate_gate"]["G4_closure_evidence_certified"],
                            evidence_certified,
                        )

    def test_d3_resolved_track_caveats_are_held_pending_g7(self) -> None:
        # G4 reopened, so D3 is met through the caveats path alone.
        reports = self.reports_with_g4("OPEN")
        reports["g1_g8"]["g3_sm_target_track"]["downstream_caveats_resolved"] = True
        result = self.evaluate(reports)
        verdict = self.confirm(reports)
        for report in (result, verdict):
            self.assertFalse(report["internal_candidate_approved"])
            gate_d3 = report["internal_candidate_gate"]
            self.assertTrue(gate_d3["closing_track_downstream_caveats_resolved"])
            self.assertFalse(gate_d3["G4_closed"])
            self.assertTrue(gate_d3["D3_satisfied"])
            self.assertFalse(gate_d3["G7_closed"])
            self.assertFalse(gate_d3["caveats_cleared"])
            self.assertTrue(gate_d3["approval_held_pending_G7"])
            self.assertEqual(report["decision"], "WITHHOLD_APPROVAL")
            self.assertIsNone(report["internal_candidate_scope"])
            self.assertEqual(
                report["internal_candidate_hold"],
                confirmation.INTERNAL_CANDIDATE_HOLD_CAVEATS_PATH,
            )
            self.assertEqual(report["tiers"], WITHHELD_TIERS)
        self.assertEqual(result["status"], WITHHELD_STATUS)
        self.assertEqual(
            result["verdict"], gate._verdict(True, g3_closed=True, held_pending_g7=True)
        )
        for key, text in confirmation._claim_text(
            True, g3_closed=True, held_pending_g7=True
        ).items():
            self.assertEqual(verdict[key], text)

    def test_d3_resolved_track_caveats_with_g7_closed_approve_internal_candidate(self) -> None:
        reports = self.close_g7(self.reports_with_g4("OPEN"))
        reports["g1_g8"]["g3_sm_target_track"]["downstream_caveats_resolved"] = True
        self.assert_approved(self.evaluate(reports), self.confirm(reports), g4_closed=False)

    def test_d3_open_g3_never_approves_even_with_resolved_caveats_and_g7(self) -> None:
        reports = self.close_g7(copy.deepcopy(self.fresh_reports))
        reports["g1_g8"]["gates"]["G3"]["status"] = "OPEN"
        reports["g1_g8"]["g3_sm_target_track"]["downstream_caveats_resolved"] = True
        result = self.evaluate(reports)
        verdict = self.confirm(reports)
        for report in (result, verdict):
            self.assertFalse(report["internal_candidate_approved"])
            self.assertFalse(report["internal_candidate_gate"]["G1_G2_G3_closed"])
            self.assertFalse(report["internal_candidate_gate"]["G3_closed"])
            self.assertFalse(report["internal_candidate_gate"]["approval_held_pending_G7"])
            self.assertIsNone(report["internal_candidate_hold"])
        self.assertEqual(verdict["tiers"]["INTERNAL_CANDIDATE"], "WITHHELD")
        # With ledger G3 OPEN the texts fall back to the G3-open branch.
        self.assertEqual(result["verdict"], gate._verdict(True))
        self.assertEqual(
            verdict["correct_public_claim"],
            confirmation._claim_text(True)["correct_public_claim"],
        )

    def test_d3_missing_or_unclosed_track_never_approves(self) -> None:
        # G4 is reopened in every case: with the fresh ledger's certified G4
        # closure D3 would be met through G4 instead.
        removed = self.reports_with_g4("OPEN")
        del removed["g1_g8"]["g3_sm_target_track"]
        not_closed = self.reports_with_g4("OPEN")
        not_closed["g1_g8"]["g3_sm_target_track"]["closed"] = False
        not_closed["g1_g8"]["g3_sm_target_track"]["downstream_caveats_resolved"] = True
        forged_type = self.reports_with_g4("OPEN")
        forged_type["g1_g8"]["g3_sm_target_track"]["downstream_caveats_resolved"] = "true"
        for label, reports in (
            ("removed", removed),
            ("not_closed", not_closed),
            ("forged_type", forged_type),
        ):
            with self.subTest(case=label):
                reports = self.close_g7(reports)
                result = self.evaluate(reports)
                verdict = self.confirm(reports)
                for report in (result, verdict):
                    self.assertFalse(report["internal_candidate_approved"])
                    self.assertFalse(
                        report["internal_candidate_gate"][
                            "closing_track_downstream_caveats_resolved"
                        ]
                    )
                    self.assertFalse(report["internal_candidate_gate"]["G4_closed"])
                    self.assertFalse(report["internal_candidate_gate"]["D3_satisfied"])
                    self.assertFalse(report["internal_candidate_gate"]["caveats_cleared"])
                    self.assertFalse(report["internal_candidate_gate"]["approval_held_pending_G7"])
                self.assertEqual(verdict["tiers"]["INTERNAL_CANDIDATE"], "WITHHELD")

    def test_no_approval_or_exclusion_survives_contract_mismatch(self) -> None:
        reports = self.close_g7(copy.deepcopy(self.fresh_reports))
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
        self.assertFalse(result["internal_candidate_gate"]["approval_held_pending_G7"])
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
        reports = self.close_g7(copy.deepcopy(self.fresh_reports))
        reports["x_contract"]["n_failed"] = 1
        reports["x_contract"]["failures"] = ["sabotaged"]
        result = self.evaluate(reports)
        self.assertFalse(result["integrity_pass"])
        self.assertEqual(result["overall_state"], "EXECUTION_FAIL")
        self.assertEqual(
            result["classification"], "THEORY_CONFIRMATION_AUDIT_EXECUTION_FAILED"
        )
        self.assertEqual(result["decision"], "WITHHOLD_APPROVAL")
        self.assertFalse(result["internal_candidate_approved"])
        self.assertFalse(result["internal_candidate_gate"]["approval_held_pending_G7"])
        self.assertFalse(result["whole_model_excluded"])

    def test_missing_source_fails_closed(self) -> None:
        reports = copy.deepcopy(self.fresh_reports)
        del reports["gauged_contract"]
        result = self.evaluate(reports)
        self.assertFalse(result["integrity_pass"])
        self.assertFalse(result["internal_candidate_approved"])
        self.assertIsNone(result["internal_candidate_hold"])
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
        self.assertIs(report["internal_candidate_approved"], False)

    def test_markdown_states_the_hold_and_not_an_approval(self) -> None:
        result = self.evaluate()
        verdict = self.confirm()
        hold_line = "- Internal-candidate hold: " + confirmation.INTERNAL_CANDIDATE_HOLD
        ultimate_md = gate.write_markdown(result)
        confirmation_md = confirmation.write_markdown(verdict)
        for text in (ultimate_md, confirmation_md):
            self.assertIn(hold_line, text)
            self.assertNotIn("Internal-candidate scope", text)
            self.assertIn("- Internal candidate: **False**", text)
        self.assertIn(
            "- INTERNAL_CANDIDATE: **WITHHELD** - " + TIER_DEFINITIONS["INTERNAL_CANDIDATE"],
            confirmation_md,
        )
        # caveats_cleared is qualified: D3 is met through G4, but G7 is open.
        self.assertIn(
            "- Internal-candidate gate (D3 and D-E): caveats_cleared = False (G4_closed = True; "
            "closing-track downstream caveats resolved = False; G7_closed = False; "
            "held pending G7 = True)",
            confirmation_md,
        )
        # A hypothetical approval (G7 CLOSED) states its scope, not a hold.
        approved = self.evaluate(self.close_g7(copy.deepcopy(self.fresh_reports)))
        approved_md = gate.write_markdown(approved)
        self.assertIn(
            "- Internal-candidate scope: " + confirmation.INTERNAL_CANDIDATE_SCOPE, approved_md
        )
        self.assertNotIn("Internal-candidate hold", approved_md)
        withheld = self.evaluate(self.reports_with_g4("OPEN"))
        self.assertNotIn("Internal-candidate hold", gate.write_markdown(withheld))
        self.assertNotIn("Internal-candidate scope", gate.write_markdown(withheld))

    # ------------------------------------------------------------------
    # Exit codes and CLIs.
    # ------------------------------------------------------------------

    def test_default_exit_accepts_honest_state_and_refuses_internal_approval(self) -> None:
        report = self.evaluate()
        self.assertEqual(gate.exit_code(report), 0)
        self.assertEqual(gate.exit_code(report, expect_open=True), 0)
        self.assertNotEqual(gate.exit_code(report, expect_blocked=True), 0)
        self.assertEqual(gate.exit_code(report, expect_full_block=True), 0)
        # Decision D-E holds the tier, so the internal-approval requirement fails.
        self.assertEqual(gate.exit_code(report, require_internal_approval=True), 2)
        self.assertEqual(
            gate.exit_code(report, expect_open=True, require_internal_approval=True), 2
        )
        self.assertEqual(gate.exit_code(report, require_full_approval=True), 3)
        approved = self.evaluate(self.close_g7(copy.deepcopy(self.fresh_reports)))
        self.assertEqual(
            gate.exit_code(approved, expect_open=True, require_internal_approval=True), 0
        )

    def test_cli_strict_approval_modes(self) -> None:
        report = self.evaluate()
        with patch.object(gate, "build_report", return_value=report):
            with redirect_stdout(io.StringIO()):
                self.assertEqual(gate.main(["--no-write"]), 0)
                self.assertEqual(gate.main(["--expect-open", "--no-write"]), 0)
                self.assertEqual(
                    gate.main(["--no-write", "--require-internal-approval"]), 2
                )
                self.assertEqual(
                    gate.main(
                        ["--expect-open", "--no-write", "--require-internal-approval"]
                    ),
                    2,
                )
                self.assertEqual(
                    gate.main(["--no-write", "--require-full-approval"]), 3
                )
                self.assertNotEqual(gate.main(["--no-write", "--expect-blocked"]), 0)

    def test_confirmation_cli_has_same_fail_closed_exit_policy(self) -> None:
        verdict = self.confirm()
        self.assertEqual(confirmation.exit_code(verdict), 0)
        self.assertEqual(confirmation.exit_code(verdict, expect_open=True), 0)
        self.assertEqual(
            confirmation.exit_code(verdict, require_internal_approval=True), 2
        )
        self.assertEqual(
            confirmation.exit_code(verdict, require_full_approval=True), 3
        )
        self.assertNotEqual(confirmation.exit_code(verdict, expect_blocked=True), 0)
        with patch.object(confirmation, "build_verdict", return_value=verdict):
            with redirect_stdout(io.StringIO()):
                self.assertEqual(confirmation.main(["--no-write"]), 0)
                self.assertEqual(
                    confirmation.main(["--expect-open", "--no-write"]), 0
                )
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
