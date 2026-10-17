#!/usr/bin/env python3
"""Fail-closed and sabotage tests for the ultimate v20 gate.

They also cover the confirmation layer it consumes.  G4 is CLOSED in the
ledger at the G3 witness benchmark (tree level) on the certified closure
evidence of ``g4_sm_closure_binding_v20``, which meets decision D3.  The
user's decision D-E (2026-09-26) holds approval of the internal-candidate tier
until G7 is CLOSED (strictly: G7 and its ledger dependency G6 CLOSED).  The
user's decision U3 removes the approval altogether: ``internal_candidate_approved``
is False on every path, including hypothetical or forged ledgers with G6 and
G7 CLOSED, and ``--require-internal-approval`` always fails.  With decision D3
met, G5 CLOSED, G8 not CLOSED and the ledger's G8 flavour record (minimum
load-bearing pulls read from the exact JSON fields) and G8 structural record
recorded, the tier state is RELEASED_NOT_APPROVED; any malformed G8 record
gives WITHHELD (the D-E hold while G7 is not CLOSED).  A reopened G4, or a
CLOSED status without certified evidence, fails D3 as well.
"""

from __future__ import annotations

import copy
import io
import json
import re
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import exact_x_symmetry_consistency_gate_v20 as x_gate
import g1_g8_gate_ledger_v20 as gate_ledger
import g3_sm_target_track_v20 as sm_track
import g4_sm_closure_binding_v20 as g4_closure
import theory_confirmation_verdict_v20 as confirmation
import ultimate_theory_gate_v20 as gate

ROOT = Path(gate.__file__).resolve().parent

# The former approval status must never occur (decision U3).
APPROVED_STATUS = (
    "ULTIMATE_GATE_AUDIT_COMPLETE__INTERNAL_CANDIDATE_APPROVED__FULL_APPROVAL_OPEN"
)
WITHHELD_STATUS = "ULTIMATE_GATE_AUDIT_COMPLETE__APPROVAL_OPEN"

# The released numbers are bound to the committed G8 flavour JSON (exact
# fields) and also pinned literally.  The leading value is the conservative
# pull rounded to 0.1 sigma and is never preceded by ">=".
G8_DATA = json.loads(
    (ROOT / "G8_SM_PATI_SALAM_FLAVOUR_NOGO_V20.json").read_text(encoding="utf-8")
)["data"]
RAW1 = f"{G8_DATA['minimum_load_bearing_pull_raw_sigma']:.1f}"
CONS1 = f"{G8_DATA['minimum_load_bearing_pull_conservative_sigma']:.1f}"
RAW2 = f"{G8_DATA['minimum_load_bearing_pull_raw_sigma']:.2f}"
CONS2 = f"{G8_DATA['minimum_load_bearing_pull_conservative_sigma']:.2f}"
RELEASE_LABEL = (
    f"certified tree-level vacuum, excluded by G8 flavour at {CONS1} sigma (minimum load-bearing pull "
    f"{CONS2} sigma with a 10% theory term, {RAW2} sigma on experimental errors alone; witness-branch "
    "renormalizable Yukawas, tan-beta-independent tests, 1e9-2e16 GeV), not approved"
)
LITERAL_RELEASE_LABEL = (
    "certified tree-level vacuum, excluded by G8 flavour at 8.9 sigma (minimum load-bearing pull 8.86 sigma "
    "with a 10% theory term, 13.24 sigma on experimental errors alone; witness-branch renormalizable Yukawas, "
    "tan-beta-independent tests, 1e9-2e16 GeV), not approved"
)

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

ULTIMATE_RELEASED_VERDICT = (
    "WITHHOLD APPROVAL. The audit has no execution failure and the gauged-U(1)_X "
    "model contract is attested by bound external SARAH execution evidence; G1, "
    "G2, G3 (SM Pati-Salam benchmark family, scoped), G4 (at the G3 witness "
    "benchmark, tree level) and G5 are closed, which meets decision D3, but "
    "decision D-E holds approval of the internal-candidate tier until G7 is "
    "CLOSED, and decision U3 never approves it. By decision U3 the internal "
    "candidate is released: " + LITERAL_RELEASE_LABEL + " (CKM = 1, m_t = m_b, "
    "m_d = m_e; G8_SM_PATI_SALAM_FLAVOUR_NOGO_V20.json). The G6-G8 scientific "
    "gates remain open or blocked (sub-M_I coloured states, positivity beyond tree "
    "level and electroweak symmetry breaking, RG-anchor content and the Higgs "
    "quartic, Yukawas and proton decay). No internal-candidate, "
    "conditional-benchmark, full-phenomenology, empirical-realization, or "
    "whole-model-exclusion claim is approved; the whole model is neither "
    "validated nor excluded by a proof-grade certificate. Program verdict "
    "(decision U1): NOT VIABLE as a complete description of nature under the "
    "declared standards; the no-go is method-limited at G3 x G8."
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

CONFIRMATION_RELEASED_VERDICT = (
    "WITHHOLD APPROVAL. The audit succeeds and the gauged-U(1)_X model contract "
    "is attested by bound external SARAH execution evidence. G1, G2, G3 (SM "
    "Pati-Salam benchmark family, scoped), G4 (at the G3 witness benchmark, tree "
    "level) and G5 are closed, which meets decision D3, but decision D-E holds "
    "approval of the internal-candidate tier until G7 is CLOSED, and decision U3 "
    "never approves it. By decision U3 the internal candidate is released: "
    + LITERAL_RELEASE_LABEL + " (CKM = 1, m_t = m_b, m_d = m_e; "
    "G8_SM_PATI_SALAM_FLAVOUR_NOGO_V20.json). G6 is open and G7-G8 remain blocked "
    "(sub-M_I coloured states and positivity beyond tree level, electroweak "
    "symmetry breaking, RG-anchor content, the Higgs quartic, Yukawas and proton "
    "decay), so no internal, conditional-benchmark, full-phenomenology, empirical, "
    "or exclusion claim is approved; the whole model is neither validated nor "
    "excluded by a proof-grade certificate. Program verdict (decision U1): NOT "
    "VIABLE as a complete description of nature under the declared standards; the "
    "no-go is method-limited at G3 x G8."
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
        "phenomenology; by decision U3 never approved (a candidate that meets D3 "
        "may be released, RELEASED_NOT_APPROVED)"
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

WITHHELD_TIERS = {
    "INTERNAL_CANDIDATE": "WITHHELD",
    "CONDITIONAL_BENCHMARK": "WITHHELD",
    "FULL_PHENOMENOLOGY": "WITHHELD",
    "EMPIRICAL_REALIZATION": "NOT_ESTABLISHED",
    "WHOLE_MODEL_EXCLUSION": "NOT_ESTABLISHED",
}
RELEASED_TIERS = dict(WITHHELD_TIERS, INTERNAL_CANDIDATE="RELEASED_NOT_APPROVED")

STALE_FRAGMENTS = (
    "being researched",
    "not yet a committed",
    "need a decision",
    "need a user decision",
    "not yet part of this release",
    ">= 8.9 sigma",
    "at least 13.2 sigma",
    "APPROVE INTERNAL CANDIDATE",
)


def _normalised(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


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

    @staticmethod
    def release_record(*, g4_closed: bool = True) -> dict:
        template = (
            confirmation.INTERNAL_CANDIDATE_RELEASE_TEMPLATE
            if g4_closed
            else confirmation.INTERNAL_CANDIDATE_RELEASE_CAVEATS_PATH_TEMPLATE
        )
        return {
            "text": template.format(label=RELEASE_LABEL, cons1=CONS1, cons2=CONS2, raw2=RAW2),
            "label": RELEASE_LABEL,
        }

    def assert_withheld_g3_only(self, result: dict, verdict: dict) -> None:
        """D3 not met (G4 not strictly CLOSED, caveats unresolved): no hold, no release, no approval."""
        frontier = verdict["internal_candidate_gate"]["G5_G8_frontier"]
        for report in (result, verdict):
            self.assertFalse(report["internal_candidate_approved"])
            self.assertFalse(report["internal_candidate_gate"]["G4_closed"])
            self.assertFalse(report["internal_candidate_gate"]["D3_satisfied"])
            self.assertFalse(report["internal_candidate_gate"]["caveats_cleared"])
            self.assertFalse(report["internal_candidate_gate"]["approval_held_pending_G7"])
            self.assertFalse(report["internal_candidate_gate"]["released_not_approved"])
            self.assertIs(report["internal_candidate_gate"]["approval_disabled_by_U3"], True)
            self.assertEqual(report["classification"], "AUTHORITATIVE_GATES_OPEN")
            self.assertEqual(report["decision"], "WITHHOLD_APPROVAL")
            self.assertEqual(report["overall_state"], "OPEN")
            self.assertIsNone(report["internal_candidate_scope"])
            self.assertIsNone(report["internal_candidate_hold"])
            self.assertIsNone(report["internal_candidate_release"])
            self.assertIsNone(report["internal_candidate_release_label"])
            self.assertEqual(report["tiers"], WITHHELD_TIERS)
        self.assertEqual(result["status"], WITHHELD_STATUS)
        self.assertEqual(
            verdict["status"], "THEORY_CONFIRMATION_AUDIT_COMPLETE__GATES_OPEN"
        )
        self.assertFalse(verdict["approval"]["internal_candidate"])
        self.assertEqual(result["verdict"], gate._verdict(True, g3_closed=True, frontier=frontier))
        if frontier == confirmation.EXPECTED_G5_G8_FRONTIER:
            self.assertTrue(result["verdict"].startswith(ULTIMATE_G3_CLOSED_WITHHELD_PREFIX))
        for key, text in confirmation._claim_text(True, g3_closed=True, frontier=frontier).items():
            self.assertEqual(verdict[key], text)
        self.assertEqual(gate.exit_code(result, require_internal_approval=True), 2)
        self.assertEqual(
            confirmation.exit_code(verdict, require_internal_approval=True), 2
        )

    def assert_never_approved_with_g7_closed(
        self, result: dict, verdict: dict, *, g4_closed: bool, released: bool = True
    ) -> None:
        """Decision U3: D3 met with G6 and G7 CLOSED (hypothetical) is never an approval."""
        frontier = verdict["internal_candidate_gate"]["G5_G8_frontier"]
        self.assertNotEqual(frontier, confirmation.EXPECTED_G5_G8_FRONTIER)
        release = self.release_record(g4_closed=g4_closed) if released else None
        for report in (result, verdict):
            self.assertIs(report["internal_candidate_approved"], False)
            self.assertIs(report["approval"]["internal_candidate"], False)
            gate_d3 = report["internal_candidate_gate"]
            self.assertIs(gate_d3["D3_satisfied"], True)
            self.assertIs(gate_d3["G7_closed"], True)
            self.assertIs(gate_d3["caveats_cleared"], True)
            self.assertIs(gate_d3["approval_held_pending_G7"], False)
            self.assertIs(gate_d3["approval_disabled_by_U3"], True)
            self.assertIs(gate_d3["D3_met_with_G7_closed_not_approved"], True)
            self.assertIs(gate_d3["released_not_approved"], released)
            self.assertIs(gate_d3["G4_closed"], g4_closed)
            self.assertIs(gate_d3["G5_G8_frontier_expected"], False)
            self.assertEqual(report["overall_state"], "OPEN")
            self.assertEqual(report["decision"], "WITHHOLD_APPROVAL")
            self.assertEqual(report["classification"], "AUTHORITATIVE_GATES_OPEN")
            self.assertEqual(report["tiers"], RELEASED_TIERS if released else WITHHELD_TIERS)
            self.assertIsNone(report["internal_candidate_scope"])
            if released:
                self.assertIsNone(report["internal_candidate_hold"])
                self.assertEqual(report["internal_candidate_release"], release["text"])
                self.assertEqual(report["internal_candidate_release_label"], RELEASE_LABEL)
            else:
                self.assertEqual(
                    report["internal_candidate_hold"],
                    confirmation.INTERNAL_CANDIDATE_APPROVAL_DISABLED_HOLD,
                )
                self.assertIsNone(report["internal_candidate_release"])
            # The ledger frontier differs from the recorded one, so the program
            # verdict is not copied (fail closed).
            self.assertIs(report["program_verdict"]["recorded"], False)
            self.assertFalse(report["full_phenomenology_approved"])
            self.assertFalse(report["conditional_benchmark_approved"])
        self.assertEqual(result["status"], WITHHELD_STATUS)
        self.assertNotEqual(result["status"], APPROVED_STATUS)
        self.assertEqual(verdict["status"], "THEORY_CONFIRMATION_AUDIT_COMPLETE__GATES_OPEN")
        self.assertEqual(
            result["verdict"],
            gate._verdict(
                True, g3_closed=True, g4_closed=g4_closed, held_pending_g7=False,
                release_label=RELEASE_LABEL if released else None, frontier=frontier,
            ),
        )
        self.assertIn("Decision U3 never approves the internal-candidate tier", result["verdict"])
        for key, text in confirmation._claim_text(
            True, g3_closed=True, g4_closed=g4_closed, release=release, frontier=frontier,
        ).items():
            self.assertEqual(verdict[key], text)
        for text in (result["verdict"], verdict["verdict"]):
            self.assertTrue(text.startswith("WITHHOLD APPROVAL."))
            self.assertNotIn("APPROVE INTERNAL CANDIDATE", text)
        self.assertEqual(gate.exit_code(result, require_internal_approval=True), 2)
        self.assertEqual(confirmation.exit_code(verdict, require_internal_approval=True), 2)

    def assert_held_fallback(self, result: dict, verdict: dict, label: str) -> None:
        """D3 met, G7 not CLOSED, U3 release unavailable: the D-E hold (WITHHELD)."""
        for report in (result, verdict):
            self.assertIs(report["internal_candidate_approved"], False, label)
            gate_d3 = report["internal_candidate_gate"]
            self.assertIs(gate_d3["approval_held_pending_G7"], True, label)
            self.assertIs(gate_d3["released_not_approved"], False, label)
            self.assertIs(gate_d3["G8_flavour_pulls_bound"], False, label)
            self.assertEqual(report["tiers"], WITHHELD_TIERS, label)
            self.assertIsNone(report["internal_candidate_release"], label)
            self.assertIsNone(report["internal_candidate_release_label"], label)
            self.assertEqual(
                report["internal_candidate_hold"], confirmation.INTERNAL_CANDIDATE_HOLD, label
            )
            self.assertIn(confirmation.U3_RELEASE_UNAVAILABLE, report["internal_candidate_hold"])
            self.assertIs(report["internal_candidate_release_binding"]["recorded"], False, label)
            self.assertIsNone(
                report["internal_candidate_release_binding"]["conservative_sigma_text"], label
            )
            self.assertEqual(report["overall_state"], "OPEN", label)
            self.assertEqual(report["decision"], "WITHHOLD_APPROVAL", label)
        self.assertEqual(result["status"], WITHHELD_STATUS, label)
        self.assertEqual(result["verdict"], ULTIMATE_HELD_VERDICT, label)
        for key, text in confirmation._claim_text(
            True, g3_closed=True, g4_closed=True, held_pending_g7=True
        ).items():
            self.assertEqual(verdict[key], text, label)
        self.assertEqual(verdict["verdict"], CONFIRMATION_HELD_VERDICT, label)
        self.assertEqual(gate.exit_code(result, require_internal_approval=True), 2, label)
        self.assertEqual(confirmation.exit_code(verdict, require_internal_approval=True), 2, label)

    # ------------------------------------------------------------------
    # The current state: G4 CLOSED meets D3; D-E holds approval (G7 open);
    # U3 releases the candidate without approving it.
    # ------------------------------------------------------------------

    def test_current_state_is_open_with_the_internal_candidate_released_not_approved(self) -> None:
        # The SARAH-attested contract is consistent; G1-G5 are CLOSED (G3 on
        # the SM Pati-Salam benchmark family, G4 at its witness benchmark at
        # tree level); G6 is OPEN and G7-G8 BLOCKED.  Decision D-E holds
        # approval until G7 is CLOSED; decision U3 releases the candidate and
        # never approves it.
        self.assertEqual((RAW1, CONS1, RAW2, CONS2), ("13.2", "8.9", "13.24", "8.86"))
        self.assertEqual(RELEASE_LABEL, LITERAL_RELEASE_LABEL)
        self.assertNotIn(">=", RELEASE_LABEL)
        self.assertNotIn("at least", RELEASE_LABEL)
        expected_release = self.release_record()["text"]
        self.assertTrue(expected_release.startswith("RELEASED (decision U3): " + LITERAL_RELEASE_LABEL + ". "))
        result = self.evaluate()
        verdict = self.confirm()
        self.assertTrue(result["integrity_pass"])
        self.assertEqual(result["n_failed"], 0)
        self.assertEqual(result["status"], WITHHELD_STATUS)
        self.assertEqual(
            result["validation_matrix_contract_gate"]["state"], "PASS"
        )
        self.assertEqual(
            verdict["status"], "THEORY_CONFIRMATION_AUDIT_COMPLETE__GATES_OPEN"
        )
        self.assertEqual(verdict["verdict_code"], verdict["classification"])
        for report in (result, verdict):
            self.assertEqual(report["overall_state"], "OPEN")
            self.assertEqual(report["classification"], "AUTHORITATIVE_GATES_OPEN")
            self.assertEqual(report["decision"], "WITHHOLD_APPROVAL")
            self.assertIs(report["internal_candidate_approved"], False)
            self.assertIs(report["approval"]["internal_candidate"], False)
            self.assertFalse(report["conditional_benchmark_approved"])
            self.assertFalse(report["full_phenomenology_approved"])
            self.assertFalse(report["full_theory_validated"])
            self.assertFalse(report["empirical_realization_approved"])
            self.assertFalse(report["whole_model_excluded"])
            self.assertEqual(report["tiers"], RELEASED_TIERS)
            self.assertIsNone(report["internal_candidate_scope"])
            self.assertIsNone(report["internal_candidate_hold"])
            self.assertEqual(report["internal_candidate_release"], expected_release)
            self.assertEqual(report["internal_candidate_release_label"], RELEASE_LABEL)
            self.assertEqual(
                report["tier_state_definitions"], confirmation.TIER_STATE_DEFINITIONS
            )
            gate_d3 = report["internal_candidate_gate"]
            self.assertIs(gate_d3["approval_held_pending_G7"], True)
            self.assertIs(gate_d3["released_not_approved"], True)
            self.assertIs(gate_d3["G8_flavour_pulls_bound"], True)
            binding = report["internal_candidate_release_binding"]
            self.assertEqual(
                binding,
                {
                    "source": "ledger gates.G8.flavour_evidence (G8_SM_PATI_SALAM_FLAVOUR_NOGO_V20.json)",
                    "pull_fields": [
                        "data.minimum_load_bearing_pull_raw_sigma",
                        "data.minimum_load_bearing_pull_conservative_sigma",
                    ],
                    "minimum_load_bearing_pull_raw_sigma": G8_DATA["minimum_load_bearing_pull_raw_sigma"],
                    "minimum_load_bearing_pull_conservative_sigma": G8_DATA[
                        "minimum_load_bearing_pull_conservative_sigma"
                    ],
                    "raw_sigma_text": "13.2",
                    "conservative_sigma_text": "8.9",
                    "raw_sigma_text_2dp": "13.24",
                    "conservative_sigma_text_2dp": "8.86",
                    "label_rounding": confirmation.U3_LABEL_ROUNDING,
                    "scale_band_GeV": [1e9, 2e16],
                    "structural_obstruction_recorded": True,
                    "recorded": True,
                },
            )
            self.assertIs(report["scope"]["release_is_approval"], False)
            self.assertIs(report["scope"]["program_verdict_changes_gate_statuses"], False)
            self.assertEqual(gate.exit_code(report, require_internal_approval=True), 2)
            self.assertEqual(confirmation.exit_code(report, require_internal_approval=True), 2)
        for text in ("13.24 sigma (experimental errors alone)", "8.86 sigma (with a 10% theory term)",
                     "the label's 8.9 sigma is the conservative pull rounded to 0.1 sigma",
                     "data.minimum_load_bearing_pull_raw_sigma",
                     "data.minimum_load_bearing_pull_conservative_sigma",
                     "degree-2-SOS-certified witness family at the dimension-4 level",
                     "not approved", "neither phenomenological validation nor a proof-grade exclusion",
                     "decision U3 keeps internal_candidate_approved False on every path"):
            self.assertIn(text, expected_release)
        for stale in (">=", "at least"):
            self.assertNotIn(stale, expected_release)
        self.assertIn("never preceded by '>='", confirmation.U3_LABEL_ROUNDING)
        self.assertEqual(verdict["tier_definitions"], TIER_DEFINITIONS)
        self.assertEqual(confirmation.TIER_DEFINITIONS, TIER_DEFINITIONS)
        self.assertEqual(
            result["verdict"],
            gate._verdict(
                True, g3_closed=True, g4_closed=True, release_label=RELEASE_LABEL, program_recorded=True
            ),
        )
        self.assertEqual(result["verdict"], ULTIMATE_RELEASED_VERDICT)
        self.assertEqual(verdict["verdict"], CONFIRMATION_RELEASED_VERDICT)
        # The program verdict is copied from the ledger, never recomputed here.
        ledger_program = self.fresh_reports["g1_g8"]["program_verdict"]
        expected_program = {
            "code": ledger_program["code"],
            "headline": ledger_program["headline"],
            "text": ledger_program["text"],
            "recorded": True,
        }
        self.assertEqual(ledger_program["recorded"], True)
        self.assertEqual(verdict["program_verdict"], expected_program)
        self.assertEqual(result["program_verdict"], expected_program)
        self.assertEqual(expected_program["code"], gate_ledger.PROGRAM_VERDICT_CODE)
        self.assertEqual(
            verdict["model_contract_scope"],
            {"recorded": True, "scope_text": gate_ledger.G1_TRUNCATION_SCOPE_TEXT},
        )
        self.assertEqual(result["model_contract_scope"], verdict["model_contract_scope"])

    def test_internal_candidate_gate_records_d3_met_the_d_e_hold_and_the_u3_release(self) -> None:
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
            self.assertIs(gate_d3["released_not_approved"], True)
            self.assertIs(gate_d3["G8_flavour_pulls_bound"], True)
            self.assertIs(gate_d3["G7_benchmark_evidence_recorded"], True)
            self.assertIs(gate_d3["G7_coupled_singlet_probe_recorded"], True)
            self.assertIs(gate_d3["G5_closed"], True)
            self.assertIs(gate_d3["G8_closed"], False)
            self.assertEqual(
                gate_d3["G5_G8_frontier"],
                {"G5": "CLOSED", "G6": "OPEN", "G7": "BLOCKED", "G8": "BLOCKED"},
            )
            self.assertEqual(gate_d3["G5_G8_frontier"], confirmation.EXPECTED_G5_G8_FRONTIER)
            self.assertIs(gate_d3["G5_G8_frontier_expected"], True)
            self.assertIs(gate_d3["approval_disabled_by_U3"], True)
            self.assertIs(gate_d3["D3_met_with_G7_closed_not_approved"], False)
            self.assertEqual(gate_d3["rule"], sm_track.D3_RULE)
            self.assertEqual(gate_d3["D_E_rule"], confirmation.D_E_RULE)
            self.assertEqual(gate_d3["D_E_evidence"], confirmation.D_E_EVIDENCE)
            self.assertEqual(gate_d3["U3_rule"], confirmation.U3_RULE)
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
        # The hold and release are tied to the live ledger: G6 OPEN, G7 and G8 BLOCKED.
        gates = ledger["gates"]
        self.assertEqual(
            sorted(k for k, v in gates.items() if v["status"] == "CLOSED"),
            ["G1", "G2", "G3", "G4", "G5"],
        )
        self.assertEqual(gates["G6"]["status"], "OPEN")
        self.assertEqual(gates["G7"]["status"], "BLOCKED")
        self.assertEqual(gates["G8"]["status"], "BLOCKED")
        self.assertEqual(gates["G3"]["closing_track"], "sm_pati_salam")
        self.assertIs(gates["G7"]["benchmark_evidence"]["recorded"], True)
        self.assertIs(gates["G7"]["coupled_singlet_two_loop_probe"]["recorded"], True)
        self.assertIs(gates["G8"]["flavour_evidence"]["recorded"], True)
        self.assertIs(gates["G8"]["structural_obstruction_evidence"]["recorded"], True)

    def test_hold_and_d_e_texts_cite_the_committed_g7_evidence(self) -> None:
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
            "(research runs recorded with decision D-E)",
            "reproduced by the committed gauge-only spectator probe of two_loop_thresholds_v20",
            "decoupled-singlet benchmark BM-DA1",
            "g7_decoupled_singlet_benchmark_evidence_v20",
            "so G7 stays BLOCKED",
        ):
            self.assertIn(fragment, hold)
        self.assertIn(confirmation.D_E_EVIDENCE, hold)
        self.assertIn(confirmation.U3_RELEASE_UNAVAILABLE, hold)
        self.assertEqual(hold, confirmation._hold_text(True, True))
        self.assertEqual(hold, confirmation._hold_text(True, True, True))
        self.assertIn("held until G7 is CLOSED", confirmation.D_E_RULE)
        self.assertIn(
            "decision U3 releases the candidate without approving it and keeps the tier unapproved on every path",
            confirmation.D_E_RULE,
        )
        caveats_hold = confirmation.INTERNAL_CANDIDATE_HOLD_CAVEATS_PATH
        self.assertNotIn("G4 is CLOSED", caveats_hold)
        self.assertIn("while G4 is not CLOSED", caveats_hold)
        self.assertIn(confirmation.D_E_EVIDENCE, caveats_hold)
        self.assertIn(confirmation.U3_RELEASE_UNAVAILABLE, caveats_hold)
        self.assertIn(TWO_LOOP_NO_GO, gate.VERDICT_INTERNAL_CANDIDATE_HELD_PENDING_G7)
        unavailable = confirmation._hold_text(True, False)
        self.assertIn(confirmation.D_E_EVIDENCE_G7_UNAVAILABLE, unavailable)
        self.assertIn("unavailable or not recorded (fail closed)", unavailable)
        # Without the committed spectator probe the coupled-singlet result rests
        # on the research runs alone and says so.
        probe_unavailable = confirmation._hold_text(True, True, False)
        self.assertIn(confirmation.D_E_EVIDENCE_PROBE_UNAVAILABLE, probe_unavailable)
        self.assertIn("not a committed repository certificate", confirmation.D_E_EVIDENCE_PROBE_UNAVAILABLE)
        self.assertNotIn("reproduced by", confirmation.D_E_EVIDENCE_PROBE_UNAVAILABLE)
        self.assertNotIn("not a committed repository certificate", confirmation.D_E_EVIDENCE)
        for text in (
            confirmation.D_E_RULE,
            confirmation.D_E_EVIDENCE,
            confirmation.D_E_EVIDENCE_G7_UNAVAILABLE,
            confirmation.D_E_EVIDENCE_PROBE_UNAVAILABLE,
            confirmation.INTERNAL_CANDIDATE_HOLD,
            confirmation.INTERNAL_CANDIDATE_HOLD_CAVEATS_PATH,
            confirmation.INTERNAL_CANDIDATE_APPROVAL_DISABLED_HOLD,
            confirmation.U3_RULE,
            confirmation.U3_RELEASE_UNAVAILABLE,
            confirmation.INTERNAL_CANDIDATE_RELEASE_TEMPLATE,
            confirmation.INTERNAL_CANDIDATE_RELEASE_CAVEATS_PATH_TEMPLATE,
            confirmation.INTERNAL_CANDIDATE_RELEASE_LABEL_TEMPLATE,
            gate.VERDICT_INTERNAL_CANDIDATE_HELD_PENDING_G7,
            gate.VERDICT_INTERNAL_CANDIDATE_RELEASED_TEMPLATE,
        ):
            for stale in STALE_FRAGMENTS:
                self.assertNotIn(stale, text)
        self.assertNotIn("decoupling v_S from v_R", confirmation.D_E_EVIDENCE)
        self.assertEqual(confirmation.TIER_DEFINITIONS, TIER_DEFINITIONS)
        self.assertEqual(
            set(confirmation.TIER_STATE_DEFINITIONS),
            {"APPROVED", "RELEASED_NOT_APPROVED", "WITHHELD", "NOT_ESTABLISHED"},
        )
        self.assertIn(
            "it is never approved (internal_candidate_approved = False; --require-internal-approval fails)",
            confirmation.TIER_STATE_DEFINITIONS["RELEASED_NOT_APPROVED"],
        )
        self.assertIn("G5 CLOSED, G8 not CLOSED", confirmation.TIER_STATE_DEFINITIONS["RELEASED_NOT_APPROVED"])
        self.assertIn("never for tier 1", confirmation.TIER_STATE_DEFINITIONS["APPROVED"])
        for fragment in (
            "internal_candidate_approved stays False on every path",
            "also with G6 and G7 CLOSED or on a forged ledger",
            "--require-internal-approval always fails",
            "decision D3 met, G5 CLOSED, G8 not CLOSED",
        ):
            self.assertIn(fragment, confirmation.U3_RULE)
        self.assertEqual(confirmation.TIER_RELEASED_NOT_APPROVED, "RELEASED_NOT_APPROVED")
        caveats_release = confirmation.INTERNAL_CANDIDATE_RELEASE_CAVEATS_PATH_TEMPLATE
        self.assertNotIn("G4 at the witness benchmark", caveats_release)
        self.assertIn("while G4 is not CLOSED", caveats_release)
        self.assertIn("G6 and G7 are recorded as CLOSED", confirmation.INTERNAL_CANDIDATE_APPROVAL_DISABLED_HOLD)
        self.assertIn(confirmation.U3_RELEASE_UNAVAILABLE, confirmation.INTERNAL_CANDIDATE_APPROVAL_DISABLED_HOLD)

    def test_the_approval_branch_is_removed_structurally(self) -> None:
        # Decision U3: no approval constant, scope, status or text survives, and
        # the evaluator sets internal_candidate to a literal False.
        self.assertIs(confirmation.INTERNAL_CANDIDATE_APPROVAL_POSSIBLE, False)
        for name in (
            "STATUS_INTERNAL_CANDIDATE",
            "CLASSIFICATION_INTERNAL_CANDIDATE",
            "DECISION_INTERNAL_CANDIDATE",
            "INTERNAL_CANDIDATE_SCOPE",
            "INTERNAL_CANDIDATE_SCOPE_CAVEATS_PATH",
        ):
            self.assertFalse(hasattr(confirmation, name), name)
        confirmation_source = Path(confirmation.__file__).read_text(encoding="utf-8")
        ultimate_source = Path(gate.__file__).read_text(encoding="utf-8")
        self.assertIn("    internal_candidate = False\n", confirmation_source.replace("\r\n", "\n"))
        for source in (confirmation_source, ultimate_source):
            self.assertNotIn("APPROVE INTERNAL CANDIDATE", source)
            self.assertNotIn("APPROVE_INTERNAL_CANDIDATE_ONLY", source)
            self.assertNotIn("INTERNAL_CANDIDATE_APPROVED", source)
            self.assertNotIn("internal_candidate=", source)

    def test_scope_document_matches_the_tiers(self) -> None:
        text = (ROOT / "ULTIMATE_THEORY_GATE_V20_SCOPE.md").read_text(encoding="utf-8")
        self.assertNotIn("levels 1 and 2", text)
        self.assertNotIn("tier 1 APPROVED", text)
        self.assertNotIn("tier 1 WITHHELD", text)
        for stale in STALE_FRAGMENTS + ("not a committed certificate", "rounded to 0.1 sigma"):
            self.assertNotIn(stale, text)
        for fragment in (
            "reports five tiers",
            "1. **Internal candidate**",
            "2. **Conditional benchmark**",
            "3. **Full phenomenology**",
            "4. **Empirical realization**",
            "5. **Whole-model exclusion**",
            "and, by decision D-E, G7 CLOSED",
            "Decision U3 removes the approval of this tier: internal_candidate_approved is False on every path",
            "may be released, never approved (tier state RELEASED_NOT_APPROVED)",
            "Current result: tier 1 RELEASED_NOT_APPROVED (decision U3: " + LITERAL_RELEASE_LABEL,
            "internal_candidate_approved stays False on every path",
            "tiers 2 and 3 WITHHELD; tiers 4 and 5 NOT_ESTABLISHED",
            "G4 at its witness benchmark at tree level",
            "three independent two-loop RG codes find no perturbative gauge unification",
            "research runs, reproduced by the committed gauge-only spectator probe of `two_loop_thresholds_v20`",
            "g7_decoupled_singlet_benchmark_evidence_v20",
            "minimum load-bearing pulls of 13.24 sigma (experimental errors alone) and 8.86 sigma",
            "NOT VIABLE as a complete description of nature under the declared standards (exact G3 vacuum "
            "certification and the G1-G8 gate criteria)",
            "The whole model is neither validated nor excluded by a proof-grade certificate.",
        ):
            self.assertIn(fragment, text)

    def test_static_documents_are_bound_to_the_g8_json(self) -> None:
        # README, the scope document and the manuscript print the released
        # numbers; they must equal the committed G8 JSON fields.
        readme = _normalised(ROOT / "README.md")
        scope = _normalised(ROOT / "ULTIMATE_THEORY_GATE_V20_SCOPE.md")
        tex = _normalised(ROOT / "axion_so10_theory_v20.tex")
        headline = (
            "**NOT VIABLE as a complete description of nature under the declared standards; "
            "the no-go is method-limited at G3 x G8.**"
        )
        self.assertIn(headline, readme)
        self.assertIn(gate_ledger.PROGRAM_VERDICT_HEADLINE, headline)
        self.assertIn("## Program verdict (decision U1)", readme)
        for text in (readme, scope):
            self.assertIn(RELEASE_LABEL, text)
            self.assertIn(
                f"minimum load-bearing pulls of {RAW2} sigma (experimental errors alone) and {CONS2} sigma "
                "(with a 10% theory term)",
                text,
            )
        for label in gate_ledger.G1_TRUNCATION_UNDECLARED:
            self.assertIn(label, readme)
        for fragment in (
            "Gate statuses are unchanged: G1-G5 CLOSED, G6 OPEN, G7 BLOCKED, G8 BLOCKED.",
            "The declared standards are exact G3 vacuum certification and the G1-G8 gate criteria of "
            "`G1_G8_GATE_LEDGER_V20`.",
            "Decision U5: G1 and the SARAH-attested contract attest a truncation.",
            "16 are not (in the model file's field basis:",
            "no field basis removes the truncation (EXACT: the omitted couplings span 48 real "
            "generation-expanded dimensions, more than the 25 of U(5) on the five X = 1 sixteens)",
            "radiative generation is argued, not computed",
            "The couplings are not added.",
            "Decisions adopted (D1-D6, D-E, U1, U3, U5):",
            "Neither route is pursued (decision U1).",
            "realistic flavour would need leaving the certified orientation (route A) or extending the "
            "contract (route B;",
            "excluded only numerically, research)",
            "no certification method has been demonstrated for the flavour-capable vacuum orientations",
            "G6 is not closable on the SOS-certified witness family at one loop with tree-level matching",
            "fail the reduced-Planck Landau criterion already at two loops",
            "as does the contract content itself on that root",
            "the omitted Yukawa terms are not conservative for a fail statement",
            "reproduced by the committed gauge-only spectator probe of `two_loop_thresholds_v20.py`",
            "This is not a proof-grade exclusion of the SO(10) x U(1)_X contract",
            "under the declared standards it is not viable as a complete description of nature",
            "tier state RELEASED_NOT_APPROVED",
            "`internal_candidate_approved` is False on every path",
        ):
            self.assertIn(fragment, readme)
        for stale in (
            "no other exact certification method",
            "every analysed flavour-capable SO(10)-phase addition fails",
            "which is not pursued (decision U1)",
            "(research runs, not a committed certificate)",
            "a G7 no-go for that benchmark, not a committed certificate",
        ):
            self.assertNotIn(stale, readme)
        # The manuscript prints the U3 label (scale band and tests included).
        tex_label = (
            f"excluded by G8 flavour at ${CONS1}\\sigma$ (minimum load-bearing pull ${CONS2}\\sigma$ with "
            f"a 10\\% theory term, ${RAW2}\\sigma$ on experimental errors alone; witness-branch "
            "renormalizable Yukawas, $\\tan\\beta$-independent tests, $10^9$--$2\\times10^{16}\\GeV$), "
            "not approved (CKM $=1$, $m_t=m_b$, $m_d=m_e$)."
        )
        self.assertIn(tex_label, tex)
        for fragment in (
            "not viable as a complete description of nature",
            "the no-go is method-limited, not a proof-grade exclusion of the model",
            "flavour-capable orientations lack a demonstrated certification (research runs)",
            "degree-2-SOS-certified witness vacua are flavour-dead at dimension four",
            "G6 is open and G7--G8 are blocked.",
            "unification (three independent research codes; reproduced by the release's spectator probe)",
            "perturbatively (three research codes and our spectator probe)",
            "replaced. Open tasks would be an independent",
        ):
            self.assertIn(fragment, tex)
        self.assertNotIn("The remaining scientific tasks are", tex)
        self.assertNotIn("$\\geq", tex)
        # Any sigma value printed in the manuscript's status sentence is one of
        # the JSON-derived numbers (no stale or hand-typed pulls).
        status = tex[tex.index("The witness is released as a certified tree-level vacuum"):]
        status = status[: status.index("of the model.") + len("of the model.")]
        values = re.findall(r"(\d+\.\d+)\\sigma", status)
        self.assertEqual(sorted(values), sorted([CONS1, CONS2, RAW2]))
        for text in (readme, scope, tex):
            for stale in STALE_FRAGMENTS:
                self.assertNotIn(stale, text)

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
        self.assertIsNone(result["internal_candidate_release"])
        self.assertEqual(result["tiers"], WITHHELD_TIERS)
        self.assertFalse(result["internal_candidate_gate"]["approval_held_pending_G7"])
        self.assertFalse(result["internal_candidate_gate"]["released_not_approved"])
        self.assertEqual(result["verdict"], gate._verdict(False))

    # ------------------------------------------------------------------
    # Decision U3: fail-closed release bound to the ledger's G8 records.
    # ------------------------------------------------------------------

    def test_u3_release_falls_back_to_the_d_e_hold_on_any_malformed_g8_record(self) -> None:
        def mutate(label, func):
            reports = copy.deepcopy(self.fresh_reports)
            func(reports["g1_g8"]["gates"]["G8"])
            return label, reports

        pull = "minimum_load_bearing_pull_conservative_sigma"
        cases = [
            mutate("flavour recorded False", lambda g8: g8["flavour_evidence"].update(recorded=False)),
            mutate("flavour closes gate", lambda g8: g8["flavour_evidence"].update(closes_gate=True)),
            mutate("pull 4.0", lambda g8: g8["flavour_evidence"].update({pull: 4.0})),
            mutate("pull True", lambda g8: g8["flavour_evidence"].update({pull: True})),
            mutate("pull NaN", lambda g8: g8["flavour_evidence"].update({pull: float("nan")})),
            mutate("pull string", lambda g8: g8["flavour_evidence"].update({pull: "8.9"})),
            mutate("pull deleted", lambda g8: g8["flavour_evidence"].pop(pull)),
            mutate("raw below conservative", lambda g8: g8["flavour_evidence"].update(
                minimum_load_bearing_pull_raw_sigma=8.0)),
            mutate("threshold 3", lambda g8: g8["flavour_evidence"].update(threshold_sigma=3.0)),
            mutate("scale band changed", lambda g8: g8["flavour_evidence"].update(
                scale_band_GeV=[1e9, 1e16])),
            mutate("flavour record removed", lambda g8: g8.pop("flavour_evidence")),
            mutate("structural recorded False",
                   lambda g8: g8["structural_obstruction_evidence"].update(recorded=False)),
            mutate("structural record removed", lambda g8: g8.pop("structural_obstruction_evidence")),
        ]
        for label, reports in cases:
            with self.subTest(case=label):
                self.assert_held_fallback(self.evaluate(reports), self.confirm(reports), label)

    def test_u3_release_needs_g5_closed_and_g8_not_closed(self) -> None:
        # Both release templates state G5 CLOSED and "excluded by G8 flavour"
        # with G8 BLOCKED; a forged G5 or G8 status never keeps the release.
        for label, name, status in (("G5 OPEN", "G5", "OPEN"), ("G8 CLOSED", "G8", "CLOSED")):
            with self.subTest(case=label):
                reports = copy.deepcopy(self.fresh_reports)
                reports["g1_g8"]["gates"][name]["status"] = status
                result = self.evaluate(reports)
                verdict = self.confirm(reports)
                frontier = verdict["internal_candidate_gate"]["G5_G8_frontier"]
                self.assertNotEqual(frontier, confirmation.EXPECTED_G5_G8_FRONTIER)
                for report in (result, verdict):
                    gate_d3 = report["internal_candidate_gate"]
                    self.assertIs(report["internal_candidate_approved"], False)
                    self.assertIs(gate_d3["released_not_approved"], False)
                    self.assertIs(gate_d3["G8_flavour_pulls_bound"], True)
                    self.assertIs(gate_d3["approval_held_pending_G7"], True)
                    self.assertEqual(report["tiers"], WITHHELD_TIERS)
                    self.assertIsNone(report["internal_candidate_release"])
                    self.assertEqual(report["internal_candidate_hold"], confirmation.INTERNAL_CANDIDATE_HOLD)
                    # The ledger frontier is not the recorded one: no program verdict.
                    self.assertIs(report["program_verdict"]["recorded"], False)
                self.assertEqual(
                    result["verdict"],
                    gate._verdict(True, g3_closed=True, g4_closed=True, held_pending_g7=True, frontier=frontier),
                )
                for key, text in confirmation._claim_text(
                    True, g3_closed=True, g4_closed=True, held_pending_g7=True, frontier=frontier
                ).items():
                    self.assertEqual(verdict[key], text)
                self.assertIn("not the recorded G5 CLOSED, G6 OPEN and G7-G8 BLOCKED frontier", result["verdict"])
                self.assertNotIn("G1, G2, G3, G4 and G5 are closed", verdict["correct_public_claim"])
                self.assertEqual(gate.exit_code(result, require_internal_approval=True), 2)
                self.assertEqual(confirmation.exit_code(verdict, require_internal_approval=True), 2)

    def test_missing_g7_evidence_changes_only_the_d_e_evidence_text(self) -> None:
        reports = copy.deepcopy(self.fresh_reports)
        reports["g1_g8"]["gates"]["G7"]["benchmark_evidence"]["recorded"] = False
        result = self.evaluate(reports)
        verdict = self.confirm(reports)
        fresh = self.confirm()
        for report in (result, verdict):
            gate_d3 = report["internal_candidate_gate"]
            self.assertEqual(gate_d3["D_E_evidence"], confirmation.D_E_EVIDENCE_G7_UNAVAILABLE)
            self.assertIs(gate_d3["G7_benchmark_evidence_recorded"], False)
            self.assertIs(gate_d3["released_not_approved"], True)
            self.assertEqual(report["tiers"], RELEASED_TIERS)
            self.assertEqual(report["internal_candidate_release"], fresh["internal_candidate_release"])
            self.assertEqual(report["internal_candidate_release_label"], RELEASE_LABEL)
            self.assertIs(report["internal_candidate_approved"], False)
        self.assertEqual(result["verdict"], ULTIMATE_RELEASED_VERDICT)
        # Without the release as well, the hold cites the unavailable G7 evidence.
        reports["g1_g8"]["gates"]["G8"]["flavour_evidence"]["recorded"] = False
        held = self.confirm(reports)
        self.assertEqual(held["internal_candidate_hold"], confirmation._hold_text(True, False))
        self.assertIn(confirmation.D_E_EVIDENCE_G7_UNAVAILABLE, held["correct_public_claim"])
        self.assertEqual(held["tiers"], WITHHELD_TIERS)
        # A missing committed spectator probe changes only the coupled-singlet clause.
        no_probe = copy.deepcopy(self.fresh_reports)
        no_probe["g1_g8"]["gates"]["G7"]["coupled_singlet_two_loop_probe"]["recorded"] = False
        no_probe_verdict = self.confirm(no_probe)
        self.assertEqual(
            no_probe_verdict["internal_candidate_gate"]["D_E_evidence"],
            confirmation.D_E_EVIDENCE_PROBE_UNAVAILABLE,
        )
        self.assertIs(no_probe_verdict["internal_candidate_gate"]["G7_coupled_singlet_probe_recorded"], False)
        self.assertEqual(no_probe_verdict["tiers"], RELEASED_TIERS)
        no_probe["g1_g8"]["gates"]["G8"]["flavour_evidence"]["recorded"] = False
        no_probe_held = self.confirm(no_probe)
        self.assertEqual(no_probe_held["internal_candidate_hold"], confirmation._hold_text(True, True, False))
        self.assertIn("not a committed repository certificate", no_probe_held["internal_candidate_hold"])

    def test_program_verdict_and_truncation_scope_are_copied_fail_closed(self) -> None:
        reports = copy.deepcopy(self.fresh_reports)
        del reports["g1_g8"]["program_verdict"]
        del reports["g1_g8"]["model_contract_scope"]
        result = self.evaluate(reports)
        verdict = self.confirm(reports)
        unavailable = {
            "code": gate_ledger.PROGRAM_VERDICT_CODE_UNAVAILABLE,
            "headline": None,
            "text": None,
            "recorded": False,
        }
        for report in (result, verdict):
            self.assertEqual(report["program_verdict"], unavailable)
            self.assertEqual(report["model_contract_scope"], {"recorded": False, "scope_text": None})
            # The release does not depend on the program verdict.
            self.assertEqual(report["tiers"], RELEASED_TIERS)
            self.assertEqual(report["status"] if report is verdict else verdict["status"],
                             "THEORY_CONFIRMATION_AUDIT_COMPLETE__GATES_OPEN")
        self.assertEqual(
            result["verdict"],
            gate.VERDICT_INTERNAL_CANDIDATE_RELEASED_TEMPLATE.format(label=RELEASE_LABEL),
        )
        self.assertNotIn("Program verdict", result["verdict"])
        self.assertNotIn(confirmation.PROGRAM_SENTENCE, verdict["correct_public_claim"])
        self.assertNotIn(confirmation.TRUNCATION_SENTENCE, verdict["correct_public_claim"])
        self.assertNotIn("Program verdict", verdict["verdict"])
        # A ledger whose program verdict is not recorded is copied as such.
        reports = copy.deepcopy(self.fresh_reports)
        reports["g1_g8"]["program_verdict"]["recorded"] = "true"
        self.assertIs(self.confirm(reports)["program_verdict"]["recorded"], False)
        self.assertNotIn("Program verdict", self.evaluate(reports)["verdict"])
        # A recorded program verdict is not copied from a ledger whose own gate
        # frontier or audit disagrees with it (forged inputs; fail closed).
        forged_cases = []
        for name, status in (("G4", "OPEN"), ("G5", "OPEN"), ("G6", "CLOSED"), ("G8", "CLOSED")):
            forged = copy.deepcopy(self.fresh_reports)
            forged["g1_g8"]["gates"][name]["status"] = status
            forged_cases.append((f"{name} {status}", forged))
        for value in (False, "0", None, 1):
            forged = copy.deepcopy(self.fresh_reports)
            forged["g1_g8"]["n_failed"] = value
            forged_cases.append((f"ledger n_failed {value!r}", forged))
        for label, forged in forged_cases:
            with self.subTest(case=label):
                self.assertIs(forged["g1_g8"]["program_verdict"]["recorded"], True)
                copied = self.confirm(forged)["program_verdict"]
                self.assertEqual(copied, unavailable)
                self.assertNotIn("Program verdict", self.evaluate(forged)["verdict"])

    # ------------------------------------------------------------------
    # Verdict and claim texts.
    # ------------------------------------------------------------------

    def test_verdict_text_branches_on_contract_readiness(self) -> None:
        held = gate._verdict(True, g3_closed=True, g4_closed=True, held_pending_g7=True)
        released = gate._verdict(
            True, g3_closed=True, g4_closed=True, held_pending_g7=True,
            release_label=RELEASE_LABEL, program_recorded=True,
        )
        released_no_program = gate._verdict(
            True, g3_closed=True, g4_closed=True, release_label=RELEASE_LABEL
        )
        g7_closed_frontier = {"G5": "CLOSED", "G6": "CLOSED", "G7": "CLOSED", "G8": "BLOCKED"}
        g7_closed_released = gate._verdict(
            True, g3_closed=True, g4_closed=True, release_label=RELEASE_LABEL,
            program_recorded=True, frontier=g7_closed_frontier,
        )
        g7_closed_withheld = gate._verdict(True, g3_closed=True, g4_closed=True, frontier=g7_closed_frontier)
        held_caveats = gate._verdict(True, g3_closed=True, held_pending_g7=True)
        released_caveats = gate._verdict(
            True, g3_closed=True, held_pending_g7=True, release_label=RELEASE_LABEL
        )
        withheld = gate._verdict(True, g3_closed=True)
        ready_g3_open = gate._verdict(True)
        blocked = gate._verdict(False)
        self.assertEqual(held, ULTIMATE_HELD_VERDICT)
        self.assertEqual(held, gate.VERDICT_INTERNAL_CANDIDATE_HELD_PENDING_G7)
        self.assertEqual(released, ULTIMATE_RELEASED_VERDICT)
        self.assertEqual(
            released_no_program,
            gate.VERDICT_INTERNAL_CANDIDATE_RELEASED_TEMPLATE.format(label=RELEASE_LABEL),
        )
        # The expected frontier is the default.
        self.assertEqual(
            gate._verdict(
                True, g3_closed=True, g4_closed=True, release_label=RELEASE_LABEL, program_recorded=True,
                frontier=dict(confirmation.EXPECTED_G5_G8_FRONTIER),
            ),
            released,
        )
        # A strict G4 closure without a release is the D-E hold text.
        self.assertEqual(gate._verdict(True, g3_closed=True, g4_closed=True), held)
        all_ready = (
            held, released, g7_closed_released, g7_closed_withheld, held_caveats, released_caveats,
            withheld, ready_g3_open,
        )
        for text in all_ready:
            self.assertNotIn("lacks", text)
            self.assertNotIn("no v2 manifest", text)
            self.assertIn("attested by bound external SARAH execution", text)
        for text in all_ready + (blocked,):
            self.assertTrue(text.startswith("WITHHOLD APPROVAL."))
            for stale in STALE_FRAGMENTS:
                self.assertNotIn(stale, text)
        for text in (released, released_caveats):
            self.assertIn("released: " + RELEASE_LABEL, text)
        # Hypothetical G6 and G7 CLOSED: generic texts, never an approval, no
        # program verdict, and the ledger frontier is named.
        for text in (g7_closed_released, g7_closed_withheld):
            self.assertIn("Decision U3 never approves the internal-candidate tier", text)
            self.assertIn(
                "the ledger records G5 CLOSED, G6 CLOSED, G7 CLOSED and G8 BLOCKED, not the recorded "
                "G5 CLOSED, G6 OPEN and G7-G8 BLOCKED frontier",
                text,
            )
            self.assertNotIn("Program verdict", text)
            self.assertNotIn("G6-G8 scientific gates remain open", text)
        self.assertIn("it is released as " + RELEASE_LABEL, g7_closed_released)
        self.assertNotIn("released", g7_closed_withheld)
        self.assertIn("decision D-E holds the internal-candidate tier", held_caveats)
        self.assertIn("the G4 and G6-G8 scientific gates remain open", held_caveats)
        self.assertNotIn("G4 (at the G3 witness", held_caveats)
        self.assertNotIn("G4 (at the G3 witness", released_caveats)
        self.assertTrue(released_caveats.startswith(held_caveats))
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
        # A blocked contract ignores the G3/G4/D3/D-E/U3 flags and the frontier.
        self.assertEqual(gate._verdict(False, g3_closed=True), blocked)
        self.assertEqual(
            gate._verdict(
                False, g3_closed=True, g4_closed=True, held_pending_g7=True,
                release_label=RELEASE_LABEL, program_recorded=True, frontier=g7_closed_frontier,
            ),
            blocked,
        )
        self.assertEqual(self.evaluate()["verdict"], released)

    def test_confirmation_text_branches_on_contract_readiness(self) -> None:
        held = confirmation._claim_text(
            True, g3_closed=True, g4_closed=True, held_pending_g7=True
        )
        released = confirmation._claim_text(
            True, g3_closed=True, g4_closed=True, held_pending_g7=True,
            release=self.release_record(), program_recorded=True, truncation_recorded=True,
        )
        g7_closed_frontier = {"G5": "CLOSED", "G6": "CLOSED", "G7": "CLOSED", "G8": "BLOCKED"}
        g7_closed_released = confirmation._claim_text(
            True, g3_closed=True, g4_closed=True, release=self.release_record(),
            program_recorded=True, truncation_recorded=True, frontier=g7_closed_frontier,
        )
        g7_closed_withheld = confirmation._claim_text(
            True, g3_closed=True, g4_closed=True, frontier=g7_closed_frontier
        )
        held_caveats = confirmation._claim_text(True, g3_closed=True, held_pending_g7=True)
        released_caveats = confirmation._claim_text(
            True, g3_closed=True, held_pending_g7=True, release=self.release_record(g4_closed=False)
        )
        withheld = confirmation._claim_text(True, g3_closed=True)
        ready_g3_open = confirmation._claim_text(True)
        blocked = confirmation._claim_text(False)
        for text in (
            list(held.values())
            + list(released.values())
            + list(g7_closed_released.values())
            + list(g7_closed_withheld.values())
            + list(held_caveats.values())
            + list(released_caveats.values())
            + list(withheld.values())
            + list(ready_g3_open.values())
        ):
            self.assertNotIn("lacks", text)
            self.assertNotIn("no v2 manifest", text)
            for stale in STALE_FRAGMENTS:
                self.assertNotIn(stale, text)
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
                False, g3_closed=True, g4_closed=True, held_pending_g7=True,
                release=self.release_record(), program_recorded=True, truncation_recorded=True,
                frontier=g7_closed_frontier,
            ),
            blocked,
        )
        # The current branch: D-E holds approval, U3 releases the candidate.
        self.assertEqual(
            released["correct_public_claim"],
            "The authoritative gauged-U(1)_X model contract is attested by a "
            "manifest/log-bound external SARAH 4.15.3 execution, and G1, G2, G3, "
            "G4 and G5 are closed. " + confirmation.TRUNCATION_SENTENCE + " "
            + sm_track.CLOSURE_SCOPE + " "
            + g4_closure.G4_CLOSED_SENTENCE + " The internal candidate is "
            + self.release_record()["text"]
            + " G6 is open and G7-G8 remain blocked. G1-G8 approval is withheld. "
            + confirmation.PROGRAM_SENTENCE + " " + HISTORY,
        )
        self.assertEqual(released["verdict"], CONFIRMATION_RELEASED_VERDICT)
        for fragment in (
            "the released internal candidate is approved, viable or a prediction",
            "decision U3 releases it and never approves it",
            "the G8 exclusion is a proof-grade exclusion of the SO(10) x U(1)_X contract",
            "the attested contract contains every allowed renormalizable coupling",
            "G6, G7 or G8 is closed",
        ):
            self.assertIn(fragment, released["incorrect_claim_do_not_use"])
        self.assertIn(
            "Program verdict (decision U1, G1_G8_GATE_LEDGER_V20.json): "
            "NOT VIABLE as a complete description of nature under the declared standards; "
            "the no-go is method-limited at G3 x G8; this is not a proof-grade exclusion of "
            "the SO(10) x U(1)_X contract.",
            released["correct_public_claim"],
        )
        self.assertIn(
            "G1 and the model contract attest a truncation: 10 of the 26 renormalizable fermion "
            "bilinears allowed by SO(10) x U(1)_X x Z17 are declared",
            released["correct_public_claim"],
        )
        # The plain D-E hold (release unavailable) keeps its texts.
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
        for text in list(held.values()) + list(released.values()):
            self.assertNotIn("APPROVE INTERNAL CANDIDATE", text)
            self.assertNotIn("the internal-candidate tier is approved", text)
        # Hypothetical G6 and G7 CLOSED (decision U3): generic texts, never an
        # approval; the release (when recorded) is stated, the program verdict
        # and the G1-G5 list are not.
        for texts in (g7_closed_released, g7_closed_withheld):
            self.assertTrue(texts["verdict"].startswith("WITHHOLD APPROVAL."))
            self.assertIn("Decision U3 never approves the internal-candidate tier", texts["verdict"])
            self.assertIn(
                "The ledger records G5 CLOSED, G6 CLOSED, G7 CLOSED and G8 BLOCKED, not the recorded "
                "G5 CLOSED, G6 OPEN and G7-G8 BLOCKED frontier.",
                texts["correct_public_claim"],
            )
            self.assertIn("decision U3 never approves it", texts["incorrect_claim_do_not_use"])
            for text in texts.values():
                self.assertNotIn("Program verdict", text)
                self.assertNotIn(g4_closure.G4_CLOSED_SENTENCE, text)
        self.assertIn(
            "The internal candidate is " + self.release_record()["text"],
            g7_closed_released["correct_public_claim"],
        )
        self.assertIn(": it is released as " + RELEASE_LABEL + ".", g7_closed_released["verdict"])
        self.assertIn(
            "The internal candidate is WITHHELD (decision U3 never approves it",
            g7_closed_withheld["correct_public_claim"],
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
        # Hypothetical U3 release on the caveats path: never claims G4.
        self.assertIn(
            self.release_record(g4_closed=False)["text"],
            released_caveats["correct_public_claim"],
        )
        self.assertEqual(
            released_caveats["verdict"],
            held_caveats["verdict"]
            + " By decision U3 the candidate is released: " + RELEASE_LABEL + ".",
        )
        for text in released_caveats.values():
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
        for key, text in released.items():
            self.assertEqual(verdict[key], text)

    # ------------------------------------------------------------------
    # Decision D3 (G4 CLOSED or caveats resolved) and decision D-E (G7).
    # ------------------------------------------------------------------

    def test_closed_g7_never_approves_the_internal_candidate(self) -> None:
        # Decision U3: even a ledger with G6 and G7 CLOSED (and D3 met through
        # G4) never approves the tier; the U3 release still applies.
        reports = self.close_g7(copy.deepcopy(self.fresh_reports))
        self.assert_never_approved_with_g7_closed(
            self.evaluate(reports), self.confirm(reports), g4_closed=True, released=True
        )
        # Without the U3 release the tier is WITHHELD with the approval-disabled hold.
        reports["g1_g8"]["gates"]["G8"]["flavour_evidence"]["recorded"] = False
        self.assert_never_approved_with_g7_closed(
            self.evaluate(reports), self.confirm(reports), g4_closed=True, released=False
        )
        # Every gate CLOSED (forged) still gives no internal-candidate approval.
        every = copy.deepcopy(self.fresh_reports)
        for name in every["g1_g8"]["gates"]:
            every["g1_g8"]["gates"][name]["status"] = "CLOSED"
        for report in (self.evaluate(every), self.confirm(every)):
            self.assertIs(report["internal_candidate_approved"], False)
            self.assertNotEqual(report["tiers"]["INTERNAL_CANDIDATE"], "APPROVED")
            self.assertEqual(gate.exit_code(report, require_internal_approval=True), 2)

    def test_d_e_g7_not_strictly_closed_stays_released_not_approved(self) -> None:
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
                    self.assertTrue(report["internal_candidate_gate"]["released_not_approved"])
                    self.assertIsNone(report["internal_candidate_hold"])
                    self.assertEqual(report["internal_candidate_release_label"], RELEASE_LABEL)
                    self.assertEqual(report["tiers"], RELEASED_TIERS)
                    self.assertIs(report["internal_candidate_gate"]["G5_G8_frontier_expected"], False)
                    self.assertIs(report["program_verdict"]["recorded"], False)
                frontier = verdict["internal_candidate_gate"]["G5_G8_frontier"]
                self.assertEqual(
                    result["verdict"],
                    gate._verdict(
                        True, g3_closed=True, g4_closed=True, held_pending_g7=True,
                        release_label=RELEASE_LABEL, frontier=frontier,
                    ),
                )
                self.assertIn(": it is released as " + RELEASE_LABEL, result["verdict"])
                self.assertEqual(gate.exit_code(result, require_internal_approval=True), 2)
                self.assertEqual(confirmation.exit_code(verdict, require_internal_approval=True), 2)

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

    def test_d3_resolved_track_caveats_are_released_not_approved_pending_g7(self) -> None:
        # G4 reopened, so D3 is met through the caveats path alone; U3 releases
        # the held candidate without claiming G4.
        reports = self.reports_with_g4("OPEN")
        reports["g1_g8"]["g3_sm_target_track"]["downstream_caveats_resolved"] = True
        result = self.evaluate(reports)
        verdict = self.confirm(reports)
        release = self.release_record(g4_closed=False)
        for report in (result, verdict):
            self.assertFalse(report["internal_candidate_approved"])
            gate_d3 = report["internal_candidate_gate"]
            self.assertTrue(gate_d3["closing_track_downstream_caveats_resolved"])
            self.assertFalse(gate_d3["G4_closed"])
            self.assertTrue(gate_d3["D3_satisfied"])
            self.assertFalse(gate_d3["G7_closed"])
            self.assertFalse(gate_d3["caveats_cleared"])
            self.assertTrue(gate_d3["approval_held_pending_G7"])
            self.assertTrue(gate_d3["released_not_approved"])
            self.assertEqual(report["decision"], "WITHHOLD_APPROVAL")
            self.assertIsNone(report["internal_candidate_scope"])
            self.assertIsNone(report["internal_candidate_hold"])
            self.assertEqual(report["internal_candidate_release"], release["text"])
            self.assertEqual(report["tiers"], RELEASED_TIERS)
        self.assertEqual(result["status"], WITHHELD_STATUS)
        self.assertEqual(
            result["verdict"],
            gate._verdict(
                True, g3_closed=True, held_pending_g7=True, release_label=RELEASE_LABEL,
            ),
        )
        self.assertIs(verdict["program_verdict"]["recorded"], False)
        for key, text in confirmation._claim_text(
            True, g3_closed=True, held_pending_g7=True, release=release,
            truncation_recorded=True,
        ).items():
            self.assertEqual(verdict[key], text)
        # Without the release the caveats-path hold applies.
        reports["g1_g8"]["gates"]["G8"]["structural_obstruction_evidence"]["recorded"] = False
        held = self.confirm(reports)
        self.assertEqual(
            held["internal_candidate_hold"], confirmation.INTERNAL_CANDIDATE_HOLD_CAVEATS_PATH
        )
        self.assertEqual(held["tiers"], WITHHELD_TIERS)
        for key, text in confirmation._claim_text(True, g3_closed=True, held_pending_g7=True).items():
            self.assertEqual(held[key], text)

    def test_d3_resolved_track_caveats_with_g7_closed_never_approve(self) -> None:
        reports = self.close_g7(self.reports_with_g4("OPEN"))
        reports["g1_g8"]["g3_sm_target_track"]["downstream_caveats_resolved"] = True
        self.assert_never_approved_with_g7_closed(
            self.evaluate(reports), self.confirm(reports), g4_closed=False, released=True
        )

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
            self.assertFalse(report["internal_candidate_gate"]["released_not_approved"])
            self.assertIsNone(report["internal_candidate_hold"])
            self.assertIsNone(report["internal_candidate_release"])
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
                    self.assertFalse(report["internal_candidate_gate"]["released_not_approved"])
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
        self.assertFalse(result["internal_candidate_gate"]["released_not_approved"])
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
        self.assertFalse(result["internal_candidate_gate"]["released_not_approved"])
        self.assertFalse(result["whole_model_excluded"])

    def test_missing_source_fails_closed(self) -> None:
        reports = copy.deepcopy(self.fresh_reports)
        del reports["gauged_contract"]
        result = self.evaluate(reports)
        self.assertFalse(result["integrity_pass"])
        self.assertFalse(result["internal_candidate_approved"])
        self.assertIsNone(result["internal_candidate_hold"])
        self.assertIsNone(result["internal_candidate_release"])
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
        self.assertEqual(report["tiers"]["INTERNAL_CANDIDATE"], "RELEASED_NOT_APPROVED")

    def test_markdown_states_the_release_and_not_an_approval(self) -> None:
        result = self.evaluate()
        verdict = self.confirm()
        release_line = "- Internal-candidate release: " + self.release_record()["text"]
        ultimate_md = gate.write_markdown(result)
        confirmation_md = confirmation.write_markdown(verdict)
        for text in (ultimate_md, confirmation_md):
            self.assertIn(release_line, text)
            self.assertIn("- Internal-candidate tier: **RELEASED_NOT_APPROVED**", text)
            self.assertNotIn("Internal-candidate hold", text)
            self.assertNotIn("Internal-candidate scope", text)
            self.assertIn("- Internal candidate: **False**", text)
            self.assertIn("## Program verdict (decision U1)", text)
            self.assertIn(f"**Code:** `{gate_ledger.PROGRAM_VERDICT_CODE}`", text)
            self.assertIn(gate_ledger.PROGRAM_VERDICT_TEXT, text)
        self.assertIn(
            "- INTERNAL_CANDIDATE: **RELEASED_NOT_APPROVED** - " + TIER_DEFINITIONS["INTERNAL_CANDIDATE"],
            confirmation_md,
        )
        # caveats_cleared is qualified: D3 is met through G4, but G7 is open.
        self.assertIn(
            "- Internal-candidate gate (D3 and D-E): caveats_cleared = False (G4_closed = True; "
            "closing-track downstream caveats resolved = False; G7_closed = False; "
            "held pending G7 = True; approval disabled by decision U3 = True)",
            confirmation_md,
        )
        # The D-E hold (release unavailable) is stated as a hold.
        held_reports = copy.deepcopy(self.fresh_reports)
        held_reports["g1_g8"]["gates"]["G8"]["flavour_evidence"]["recorded"] = False
        held_md = gate.write_markdown(self.evaluate(held_reports))
        self.assertIn("- Internal-candidate hold: " + confirmation.INTERNAL_CANDIDATE_HOLD, held_md)
        self.assertIn("- Internal-candidate tier: **WITHHELD**", held_md)
        self.assertNotIn("Internal-candidate release", held_md)
        # A hypothetical G7 CLOSED ledger is never an approval (decision U3).
        g7_closed = self.evaluate(self.close_g7(copy.deepcopy(self.fresh_reports)))
        g7_closed_md = gate.write_markdown(g7_closed)
        self.assertNotIn("Internal-candidate scope", g7_closed_md)
        self.assertIn("- Internal candidate: **False**", g7_closed_md)
        self.assertIn("- Internal-candidate tier: **RELEASED_NOT_APPROVED**", g7_closed_md)
        self.assertNotIn("**APPROVED**", g7_closed_md)
        withheld = self.evaluate(self.reports_with_g4("OPEN"))
        self.assertNotIn("Internal-candidate hold", gate.write_markdown(withheld))
        self.assertNotIn("Internal-candidate scope", gate.write_markdown(withheld))
        self.assertNotIn("Internal-candidate release", gate.write_markdown(withheld))

    # ------------------------------------------------------------------
    # Exit codes and CLIs.
    # ------------------------------------------------------------------

    def test_default_exit_accepts_honest_state_and_refuses_internal_approval(self) -> None:
        report = self.evaluate()
        self.assertEqual(gate.exit_code(report), 0)
        self.assertEqual(gate.exit_code(report, expect_open=True), 0)
        self.assertNotEqual(gate.exit_code(report, expect_blocked=True), 0)
        self.assertEqual(gate.exit_code(report, expect_full_block=True), 0)
        # The U3 release is not an approval: the internal-approval requirement fails.
        self.assertEqual(gate.exit_code(report, require_internal_approval=True), 2)
        self.assertEqual(
            gate.exit_code(report, expect_open=True, require_internal_approval=True), 2
        )
        self.assertEqual(gate.exit_code(report, require_full_approval=True), 3)
        # Decision U3: no ledger state makes the internal-approval requirement pass.
        g7_closed = self.evaluate(self.close_g7(copy.deepcopy(self.fresh_reports)))
        self.assertEqual(
            gate.exit_code(g7_closed, expect_open=True, require_internal_approval=True), 2
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
