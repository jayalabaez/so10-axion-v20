#!/usr/bin/env python3
"""Fail-closed theory-confirmation verdict for SO(10) axion v20.

The authoritative manuscript gauges ``U(1)_X``.  This verdict is assembled
from fresh builders, rather than from the older release JSON stack, so stale
Option-C results cannot approve the manuscript model.  A scientifically
blocked report is still a successful audit: the default command exits zero,
while explicit approval requirements fail nonzero.

The internal-candidate tier (tier 1: internal consistency, not phenomenology)
follows decision D3: G1, G2 and G3 CLOSED, and either the closing G3 track's
downstream caveats resolved or G4 CLOSED.  G4 counts as CLOSED only when the
ledger row is CLOSED *and* carries the certified closure evidence of
``g4_sm_closure_binding_v20`` (``ledger_g4_closed``), so a forged status alone
cannot satisfy D3.  The user's decision D-E (2026-09-26) adds a further
condition: approval is held until G7 is CLOSED, because for the declared
benchmark (5 x (16 + 16bar) spectators at M_s ~ M_I, v_S = M_I) three
independent two-loop RG codes find no perturbative gauge unification
(research runs, reproduced by the committed spectator probe of
two_loop_thresholds_v20).  The user's decision U3 removes the approval
branch altogether: ``internal_candidate_approved`` is False on every path
(also with G6 and G7 CLOSED, or on a forged ledger) and
``--require-internal-approval`` always fails.  A candidate that meets D3,
with G5 CLOSED, G8 not CLOSED and the committed G8 flavour evidence (with
its minimum load-bearing pulls, read from the exact JSON fields) and the G8
structural obstruction recorded in the ledger, is released, never approved
(tier state RELEASED_NOT_APPROVED: "certified tree-level vacuum, excluded by
G8 flavour"); otherwise the tier is WITHHELD (the D-E hold while G7 is not
CLOSED; fail closed).  The ledger's separate program verdict (decision U1)
is copied for reference only while the ledger frontier is the recorded one
and never changes a status here.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import unittest
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import authoritative_full_model_gate_v20 as authoritative_gate
import exact_x_symmetry_consistency_gate_v20 as exact_x_gate
import g1_g8_gate_ledger_v20 as gate_ledger
import g3_sm_target_track_v20 as sm_track
import g4_sm_closure_binding_v20 as g4_closure
import gauged_u1x_scalar_contract_v20 as gauged_contract
import theory_validation_matrix_v20 as validation_matrix

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "THEORY_CONFIRMATION_VERDICT.json"
OUT_MD = ROOT / "THEORY_CONFIRMATION_VERDICT.md"

MODEL_CONTRACT_BLOCKED = (
    "MODEL_CONTRACT_INCONSISTENT__AUTHORITATIVE_GATES_REOPENED"
)
WITHHOLD_APPROVAL = "WITHHOLD_APPROVAL"

# Decision U3 (user, after the 2026-09-27 rescue study): the internal-candidate
# tier is never approved.  The former D3 + D-E approval branch is removed, so
# internal_candidate_approved is False on every path (also with G6 and G7
# CLOSED, or on any forged ledger) and --require-internal-approval always
# fails.  D3 and D-E are still evaluated and reported.
INTERNAL_CANDIDATE_APPROVAL_POSSIBLE = False

# Decision D-E (user, 2026-09-26): closing G4 does not approve the internal
# candidate; approval is held until G7 is CLOSED.
D_E_RULE = (
    "D-E (user decision, 2026-09-26): closing G4 does not approve the internal-candidate tier; approval is held "
    "until G7 resolves. The ledger has no FAILED status, so this gate implements the conservative reading: approval "
    "is held until G7 is CLOSED, in addition to decision D3 (G1-G3 CLOSED and the closing G3 track's downstream "
    "caveats resolved, or G4 CLOSED); decision U3 releases the candidate without approving it and keeps the tier "
    "unapproved on every path, also once G7 is CLOSED"
)
# The D-E evidence binds the ledger's G7 records (never the JSON files): the
# committed coupled-singlet spectator probe of two_loop_thresholds_v20 and the
# committed decoupled-singlet benchmark evidence.
_D_E_COUPLED_SINGLET = (
    "a G7 no-go for the declared coupled-singlet benchmark: with the anomaly-mandated 5 x (16 + 16bar) spectators at "
    "M_s ~ M_I and v_S = M_I, three independent two-loop RG codes find no perturbative two-loop gauge unification "
    "(research runs recorded with decision D-E)"
)
_D_E_PROBE_RECORDED = (
    ", reproduced by the committed gauge-only spectator probe of two_loop_thresholds_v20 (no perturbative root for "
    "M_I between 1e8 and 10^14.5 GeV; Yukawa terms and threshold matching omitted)"
)
_D_E_PROBE_UNAVAILABLE = (
    "; the committed spectator probe (two_loop_thresholds_v20.json) is unavailable or not recorded, so this rests on "
    "the research runs alone (not a committed repository certificate; fail closed)"
)
_D_E_G7_RECORDED = (
    "; for the decoupled-singlet benchmark BM-DA1 the committed evidence g7_decoupled_singlet_benchmark_evidence_v20 "
    "records a two-loop pass of the reduced-Planck Landau criterion on both two-code roots, a three-loop (gauge-only) "
    "outcome within the two-code root uncertainty and a conditional RG-improved axion-quality failure, so G7 stays "
    "BLOCKED"
)
_D_E_G7_UNAVAILABLE = (
    "; the committed decoupled-singlet evidence (G7_DECOUPLED_SINGLET_BENCHMARK_EVIDENCE_V20.json) is unavailable or "
    "not recorded (fail closed)"
)


def _d_e_evidence(g7_recorded: bool, probe_recorded: bool = True) -> str:
    """The decision-D-E evidence text for the ledger's G7 records (fail closed)."""
    return (
        _D_E_COUPLED_SINGLET
        + (_D_E_PROBE_RECORDED if probe_recorded else _D_E_PROBE_UNAVAILABLE)
        + (_D_E_G7_RECORDED if g7_recorded else _D_E_G7_UNAVAILABLE)
    )


D_E_EVIDENCE = _d_e_evidence(True, True)
D_E_EVIDENCE_G7_UNAVAILABLE = _d_e_evidence(False, True)
D_E_EVIDENCE_PROBE_UNAVAILABLE = _d_e_evidence(True, False)
U3_RELEASE_UNAVAILABLE = (
    "The decision-U3 release (certified tree-level vacuum, excluded by G8 flavour) is not available: the committed "
    "G8 flavour or structural evidence (with its minimum load-bearing pulls) is not recorded, G5 is not CLOSED, or G8 "
    "is recorded as CLOSED (fail closed)."
)
_HOLD_PREFIX = (
    "WITHHELD, held pending G7 (decision D-E): G4 is CLOSED at the G3 witness benchmark (tree level), which meets "
    "decision D3's G4 condition, but the internal-candidate tier is held until G7 is CLOSED because of "
)
# Hypothetical hold on the D3 caveats path (the closing track's downstream
# caveats recorded as resolved while G4 is not CLOSED): nothing claims G4.
_HOLD_PREFIX_CAVEATS_PATH = (
    "WITHHELD, held pending G7 (decision D-E): the closing G3 track's downstream caveats are recorded as resolved, "
    "which meets decision D3 while G4 is not CLOSED, but the internal-candidate tier is held until G7 is CLOSED "
    "because of "
)


def _hold_text(g4_closed: bool, g7_recorded: bool, probe_recorded: bool = True) -> str:
    """The decision-D-E hold (shown only when the U3 release is unavailable)."""
    prefix = _HOLD_PREFIX if g4_closed else _HOLD_PREFIX_CAVEATS_PATH
    return prefix + _d_e_evidence(g7_recorded, probe_recorded) + ". " + U3_RELEASE_UNAVAILABLE


INTERNAL_CANDIDATE_HOLD = _hold_text(True, True)
INTERNAL_CANDIDATE_HOLD_CAVEATS_PATH = _hold_text(False, True)
# Hypothetical ledger with D3 met and G6, G7 CLOSED but no U3 release: the
# tier is withheld, never approved (decision U3).
INTERNAL_CANDIDATE_APPROVAL_DISABLED_HOLD = (
    "WITHHELD (decision U3): decision D3 is met and G6 and G7 are recorded as CLOSED, but decision U3 keeps "
    "internal_candidate_approved False on every path. " + U3_RELEASE_UNAVAILABLE
)

# Decision U3 (user, after the 2026-09-27 rescue study): the candidate is
# released, never approved.  The numbers come from the ledger's G8 flavour
# record, i.e. from the exact JSON fields of G8_SM_PATI_SALAM_FLAVOUR_NOGO_V20.
TIER_RELEASED_NOT_APPROVED = "RELEASED_NOT_APPROVED"
TIER_STATE_DEFINITIONS = {
    "APPROVED": (
        "the tier's conditions hold (never for tier 1: decision U3 keeps internal_candidate_approved False on every "
        "path)"
    ),
    "RELEASED_NOT_APPROVED": (
        "decision U3: a candidate that meets decision D3, with G5 CLOSED, G8 not CLOSED and its committed G8 flavour "
        "and structural evidence recorded, is released as a certified tree-level vacuum excluded by G8 flavour; it is "
        "never approved (internal_candidate_approved = False; --require-internal-approval fails)"
    ),
    "WITHHELD": "the tier's conditions do not hold",
    "NOT_ESTABLISHED": "no evidence establishes the tier",
}
U3_RULE = (
    "U3 (user decision after the 2026-09-27 rescue study): the internal candidate is released, not approved, as a "
    "certified tree-level vacuum excluded by G8 flavour; internal_candidate_approved stays False on every path (also "
    "with G6 and G7 CLOSED or on a forged ledger) and --require-internal-approval always fails; the release needs "
    "decision D3 met, G5 CLOSED, G8 not CLOSED and the committed G8 flavour evidence (with its minimum load-bearing "
    "pulls) and G8 structural evidence recorded in the ledger; otherwise the tier is WITHHELD (fail closed)"
)
U3_RELEASE_SOURCE = "ledger gates.G8.flavour_evidence (G8_SM_PATI_SALAM_FLAVOUR_NOGO_V20.json)"
U3_PULL_FIELDS = (
    "data.minimum_load_bearing_pull_raw_sigma",
    "data.minimum_load_bearing_pull_conservative_sigma",
)
U3_THRESHOLD_SIGMA = 5.0
U3_SCALE_BAND_GEV = [1e9, 2e16]
# The label's leading value is the conservative minimum pull rounded to
# 0.1 sigma and is never preceded by ">="; the parenthesis gives both minimum
# pulls to 0.01 sigma (all read from the exact JSON fields through the ledger).
INTERNAL_CANDIDATE_RELEASE_LABEL_TEMPLATE = (
    "certified tree-level vacuum, excluded by G8 flavour at {cons1} sigma (minimum load-bearing pull {cons2} sigma "
    "with a 10% theory term, {raw2} sigma on experimental errors alone; witness-branch renormalizable Yukawas, "
    "tan-beta-independent tests, 1e9-2e16 GeV), not approved"
)
U3_LABEL_ROUNDING = (
    "the label's leading value is the conservative minimum load-bearing pull rounded to 0.1 sigma and is never "
    "preceded by '>='; the parenthesis gives both minimum pulls to 0.01 sigma; the 5-sigma threshold is compared "
    "with the unrounded values"
)
INTERNAL_CANDIDATE_RELEASE_TEMPLATE = (
    "RELEASED (decision U3): {label}. The G3 witness vacuum is certified at tree level (G1-G5 CLOSED; G4 at the "
    "witness benchmark r0 = 1/5, x0 = 1, kappa = -r0/4); on this witness branch the renormalizable Yukawas give "
    "CKM = 1, m_t = m_b and m_d = m_e, and across 1e9-2e16 GeV the minimum load-bearing pulls of the "
    "tan-beta-independent tests are {raw2} sigma (experimental errors alone) and {cons2} sigma (with a 10% theory "
    "term) (G8_SM_PATI_SALAM_FLAVOUR_NOGO_V20.json, fields data.minimum_load_bearing_pull_raw_sigma and "
    "data.minimum_load_bearing_pull_conservative_sigma; the label's {cons1} sigma is the conservative pull rounded "
    "to 0.1 sigma). The structural obstruction (g8_sm_pati_salam_structural_obstruction_v20) extends the "
    "flavour-dead relations M_e = phase x M_d^T and CKM = 1 (tan beta = 1) to every vacuum of the "
    "degree-2-SOS-certified witness family at the dimension-4 level. The internal-candidate tier is not approved "
    "(decision U3 keeps internal_candidate_approved False on every path); the release is neither phenomenological "
    "validation nor a proof-grade exclusion of the SO(10) x U(1)_X contract."
)
# Hypothetical release on the D3 caveats path: nothing claims G4.
INTERNAL_CANDIDATE_RELEASE_CAVEATS_PATH_TEMPLATE = INTERNAL_CANDIDATE_RELEASE_TEMPLATE.replace(
    "(G1-G5 CLOSED; G4 at the witness benchmark r0 = 1/5, x0 = 1, kappa = -r0/4)",
    "(G1, G2, G3 and G5 CLOSED; the closing G3 track's downstream caveats are recorded as resolved while G4 is not "
    "CLOSED)",
)
TRUNCATION_SENTENCE = (
    "G1 and the model contract attest a truncation: 10 of the 26 renormalizable fermion bilinears "
    "allowed by SO(10) x U(1)_X x Z17 are declared (labels in the model file's field basis; no field redefinition "
    "removes the truncation), and the 16 omitted ones are not protected by any U(1) or multiplet-diagonal phase "
    "symmetry of the declared Lagrangian (g1_contract_truncation_scope_v20)."
)
PROGRAM_SENTENCE = (
    "Program verdict (decision U1, G1_G8_GATE_LEDGER_V20.json): " + gate_ledger.PROGRAM_VERDICT_HEADLINE
    + "; this is not a proof-grade exclusion of the SO(10) x U(1)_X contract."
)
# The G5-G8 frontier that every released/held text below states (mirrors
# G1_G8_GATE_LEDGER_V20: G5 CLOSED, G6 OPEN, G7-G8 BLOCKED); any other
# frontier gets the generic texts.
EXPECTED_G5_G8_FRONTIER = {
    name: gate_ledger.PROGRAM_VERDICT_EXPECTED_STATUSES[name] for name in ("G5", "G6", "G7", "G8")
}
EXPECTED_FRONTIER_TEXT = "G5 CLOSED, G6 OPEN and G7-G8 BLOCKED"

TIER_DEFINITIONS = {
    "INTERNAL_CANDIDATE": "internal consistency of the attested model contract: G1, G2 and G3 CLOSED, decision D3 satisfied (the closing G3 track's downstream caveats resolved, or G4 CLOSED) and, by decision D-E, G7 CLOSED; not phenomenology; by decision U3 never approved (a candidate that meets D3 may be released, RELEASED_NOT_APPROVED)",
    "CONDITIONAL_BENCHMARK": "a numerically safe benchmark region under extra portal assumptions on the current contract; withheld because the aligned benchmarks were computed under the superseded no-X contract",
    "FULL_PHENOMENOLOGY": "every G1-G8 gate CLOSED and the authoritative full-model gate validated",
    "EMPIRICAL_REALIZATION": "full phenomenology plus a real empirical discovery",
    "WHOLE_MODEL_EXCLUSION": "a proof-grade exclusion by the authoritative full-model gate",
}

HISTORICAL_CI = {
    "commit_sha": "ba2c66364cd68d733a2dff51416f28d92100eff5",
    "workflow": "replicate-and-falsify",
    "run_id": 30790747879,
    "run_url": (
        "https://github.com/jayalabaez/so10-axion-v20/"
        "actions/runs/30790747879"
    ),
    "conclusion": "success",
    "unit_tests": "Ran 154 tests in 69.690s - OK",
}

REQUIRED_SOURCES = (
    "x_contract",
    "gauged_contract",
    "g1_g8",
    "authoritative",
)


def _historical_count() -> int | None:
    match = re.search(r"\bRan\s+(\d+)\s+tests\b", HISTORICAL_CI["unit_tests"])
    return int(match.group(1)) if match else None


def ci_attestation(current_tests: int) -> dict[str, Any]:
    """Scope software evidence without turning it into scientific approval."""
    if os.environ.get("GITHUB_ACTIONS") == "true":
        server = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
        repository = os.environ.get(
            "GITHUB_REPOSITORY", "jayalabaez/so10-axion-v20"
        )
        run_id = os.environ.get("GITHUB_RUN_ID", "")
        return {
            "scope": "CURRENT_CI_RUN",
            "commit_sha": os.environ.get("GITHUB_SHA", ""),
            "workflow": os.environ.get("GITHUB_WORKFLOW", ""),
            "run_id": int(run_id) if run_id.isdigit() else run_id,
            "run_url": (
                f"{server}/{repository}/actions/runs/{run_id}" if run_id else ""
            ),
            "unit_tests": f"{current_tests} tests discovered in the current tree",
            "current_tree_test_count": current_tests,
            "current_tree_covered": True,
            "scientific_approval_implied": False,
        }

    attestation = dict(HISTORICAL_CI)
    attestation.update(
        {
            "scope": "HISTORICAL_ONLY",
            "current_tree_test_count": current_tests,
            "current_tree_covered": False,
            "scientific_approval_implied": False,
            "note": (
                "This run covers only its named historical commit and cannot "
                "approve the current gauged-U(1)_X model."
            ),
        }
    )
    return attestation


def fresh_source_reports() -> dict[str, dict[str, Any]]:
    """Build every authoritative prerequisite without reading verdict JSON."""
    return {
        "x_contract": exact_x_gate.build_report(),
        "gauged_contract": gauged_contract.build_report(),
        "g1_g8": gate_ledger.build_report(),
        "authoritative": authoritative_gate.build_report(),
    }


def _source_snapshot(report: dict[str, Any]) -> dict[str, Any]:
    snapshot = {
        key: report.get(key)
        for key in (
            "status",
            "overall_state",
            "model_contract_id",
            "contract_consistent",
            "implementation_matches_manuscript",
            "n_checks",
            "n_failed",
        )
        if key in report
    }
    if "classification" in report:
        snapshot["classification"] = report["classification"]
    scaffold = report.get("executable_scaffold_contract")
    if isinstance(scaffold, dict):
        snapshot["model_syntax_class"] = scaffold.get("model_syntax_class")
        snapshot["tool_native_sarah_syntax"] = scaffold.get(
            "tool_native_sarah_syntax"
        )
    external = report.get("external_model_validation")
    if isinstance(external, dict):
        snapshot["external_validation_schema"] = external.get("schema")
        snapshot["external_validation_valid"] = external.get("valid")
    return snapshot


def _execution_errors(
    reports: dict[str, dict[str, Any]],
    preload_errors: list[str] | None,
) -> list[str]:
    errors = list(preload_errors or [])
    for name in REQUIRED_SOURCES:
        report = reports.get(name)
        if not isinstance(report, dict):
            errors.append(f"required fresh report missing: {name}")
            continue
        failed = report.get("n_failed")
        if failed != 0:
            details = report.get("failures") or report.get("audit_failures") or []
            errors.append(
                f"{name} audit did not pass (n_failed={failed!r}, "
                f"failures={details!r})"
            )
    return errors


def _finite_number(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def _u3_release_binding(ledger: Any) -> dict[str, Any]:
    """Decision U3: bind the release to the ledger's G8 records (fail closed).

    Reads only the ledger report (gates.G8.flavour_evidence and
    gates.G8.structural_obstruction_evidence), never the JSON files, so no
    import or cycle is added.  Any malformed or missing value gives
    ``recorded = False`` and no numbers.  The threshold is compared with the
    unrounded pulls; the texts are rounded only for display.
    """
    gates = ledger.get("gates") if isinstance(ledger, dict) else None
    g8_row = gates.get("G8") if isinstance(gates, dict) else None
    flavour = g8_row.get("flavour_evidence") if isinstance(g8_row, dict) else None
    structural = (
        g8_row.get("structural_obstruction_evidence") if isinstance(g8_row, dict) else None
    )
    structural_recorded = isinstance(structural, dict) and structural.get("recorded") is True
    raw: Any = None
    conservative: Any = None
    try:
        raw = flavour["minimum_load_bearing_pull_raw_sigma"]
        conservative = flavour["minimum_load_bearing_pull_conservative_sigma"]
        recorded = bool(
            isinstance(flavour, dict)
            and flavour.get("recorded") is True
            and flavour.get("closes_gate") is False
            and _finite_number(raw)
            and _finite_number(conservative)
            and _finite_number(flavour.get("threshold_sigma"))
            and flavour.get("threshold_sigma") == U3_THRESHOLD_SIGMA
            and conservative >= U3_THRESHOLD_SIGMA
            and raw >= conservative
            and flavour.get("scale_band_GeV") == U3_SCALE_BAND_GEV
            and structural_recorded
        )
    except Exception:  # noqa: BLE001 - any malformed ledger record fails closed
        recorded = False
    return {
        "source": U3_RELEASE_SOURCE,
        "pull_fields": list(U3_PULL_FIELDS),
        "minimum_load_bearing_pull_raw_sigma": raw if recorded else None,
        "minimum_load_bearing_pull_conservative_sigma": conservative if recorded else None,
        "raw_sigma_text": f"{raw:.1f}" if recorded else None,
        "conservative_sigma_text": f"{conservative:.1f}" if recorded else None,
        "raw_sigma_text_2dp": f"{raw:.2f}" if recorded else None,
        "conservative_sigma_text_2dp": f"{conservative:.2f}" if recorded else None,
        "label_rounding": U3_LABEL_ROUNDING,
        "scale_band_GeV": list(U3_SCALE_BAND_GEV) if recorded else None,
        "structural_obstruction_recorded": structural_recorded,
        "recorded": recorded,
    }


def _release_record(binding: dict[str, Any], *, g4_closed: bool) -> dict[str, str] | None:
    """The formatted U3 release text and label, or None when not recorded."""
    if binding.get("recorded") is not True:
        return None
    numbers = {
        "cons1": binding["conservative_sigma_text"],
        "cons2": binding["conservative_sigma_text_2dp"],
        "raw2": binding["raw_sigma_text_2dp"],
    }
    label = INTERNAL_CANDIDATE_RELEASE_LABEL_TEMPLATE.format(**numbers)
    template = (
        INTERNAL_CANDIDATE_RELEASE_TEMPLATE
        if g4_closed
        else INTERNAL_CANDIDATE_RELEASE_CAVEATS_PATH_TEMPLATE
    )
    return {"text": template.format(label=label, **numbers), "label": label}


def _g5_g8_frontier(gates: Any) -> dict[str, Any]:
    """The ledger's G5-G8 statuses (None for a missing or malformed row)."""
    rows = gates if isinstance(gates, dict) else {}
    return {
        name: rows[name].get("status") if isinstance(rows.get(name), dict) else None
        for name in EXPECTED_G5_G8_FRONTIER
    }


def _frontier_text(frontier: Any) -> str:
    rows = frontier if isinstance(frontier, dict) else {}
    return (
        "G5 " + str(rows.get("G5")) + ", G6 " + str(rows.get("G6")) + ", G7 " + str(rows.get("G7"))
        + " and G8 " + str(rows.get("G8"))
    )


def _claim_text(
    contract_ready: bool,
    g3_closed: bool = False,
    g4_closed: bool = False,
    held_pending_g7: bool = False,
    release: dict[str, str] | None = None,
    program_recorded: bool = False,
    truncation_recorded: bool = False,
    g7_recorded: bool = True,
    probe_recorded: bool = True,
    frontier: dict[str, Any] | None = None,
) -> dict[str, str]:
    """Public-claim and verdict text, branched on model-contract readiness.

    ``g3_closed`` is the ledger's G3 status (CLOSED only through the final
    gate's SM Pati-Salam track), ``g4_closed`` the strict ledger G4 closure
    (``g4_sm_closure_binding_v20.ledger_g4_closed``) and ``held_pending_g7``
    the decision-D-E hold (D3 met, G7 not CLOSED); they change the text only
    on a ready contract.  There is no approval branch: decision U3 keeps the
    internal-candidate tier unapproved on every path.  ``release`` is the
    decision-U3 release record (``{"text", "label"}``, or None);
    ``program_recorded`` and ``truncation_recorded`` add the ledger's program
    verdict (decision U1) and the G1 truncation scope (decision U5) to the
    released texts; ``g7_recorded`` and ``probe_recorded`` select the D-E
    evidence variant of a hold text; ``frontier`` is the ledger's G5-G8
    statuses (None means the recorded G5 CLOSED, G6 OPEN, G7-G8 BLOCKED
    frontier, which the released and held texts state; any other frontier
    gets generic texts).
    """
    history = (
        "Historical Option-C calculations are scoped subtheorems and neither "
        "validate nor exclude the gauged model."
    )
    frontier_expected = frontier is None or dict(frontier) == EXPECTED_G5_G8_FRONTIER
    if contract_ready and g3_closed and not frontier_expected:
        # Hypothetical or forged G5-G8 frontier (for example G6 and G7
        # CLOSED): decision U3 never approves the internal-candidate tier.
        statuses = _frontier_text(frontier)
        candidate = (
            release["text"]
            if release is not None
            else "WITHHELD (decision U3 never approves it; the decision-U3 release is not available)."
        )
        released_clause = ": it is released as " + release["label"] if release is not None else ""
        return {
            "correct_public_claim": (
                "The authoritative gauged-U(1)_X model contract is attested by a manifest/log-bound external SARAH 4.15.3 "
                "execution, and G3 is closed. " + sm_track.CLOSURE_SCOPE + " The ledger records " + statuses
                + ", not the recorded " + EXPECTED_FRONTIER_TEXT + " frontier. The internal candidate is "
                + candidate
                + " G1-G8 approval is withheld. " + history
            ),
            "incorrect_claim_do_not_use": (
                "G3 or G4 is closed for a physically realistic or natural vacuum; the internal candidate is approved, "
                "viable or a prediction (decision U3 never approves it); the G8 exclusion is a proof-grade exclusion of "
                "the SO(10) x U(1)_X contract or of SO(10) axion models in general; the certified SU(5)+Delta point is a "
                "Standard-Model vacuum; the current repository validates the full theory; or the historical saddle "
                "excludes the gauged-U(1)_X model."
            ),
            "verdict": (
                "WITHHOLD APPROVAL. The audit succeeds and the gauged-U(1)_X model contract is attested by bound external "
                "SARAH execution evidence, and G3 is closed (SM Pati-Salam benchmark family, scoped), but the ledger "
                "records " + statuses + ", not the recorded " + EXPECTED_FRONTIER_TEXT + " frontier. Decision U3 "
                "never approves the internal-candidate tier" + released_clause + ". No internal, "
                "conditional-benchmark, "
                "full-phenomenology, empirical, or exclusion claim is approved."
            ),
        }
    if contract_ready and g3_closed and g4_closed and release is not None:
        # Decision U3: the candidate is released, never approved, bound to the
        # ledger's G8 flavour (minimum load-bearing pulls) and structural
        # records.  Gate lists mirror G1_G8_GATE_LEDGER_V20.
        return {
            "correct_public_claim": (
                "The authoritative gauged-U(1)_X model contract is attested by a manifest/log-bound external SARAH 4.15.3 "
                "execution, and G1, G2, G3, G4 and G5 are closed. "
                + (TRUNCATION_SENTENCE + " " if truncation_recorded else "")
                + sm_track.CLOSURE_SCOPE + " " + g4_closure.G4_CLOSED_SENTENCE
                + " The internal candidate is " + release["text"]
                + " G6 is open and G7-G8 remain blocked. G1-G8 approval is withheld. "
                + (PROGRAM_SENTENCE + " " if program_recorded else "")
                + history
            ),
            "incorrect_claim_do_not_use": (
                "G3 or G4 is closed for a physically realistic or natural vacuum (the doublet-triplet splitting, O05 and M_I "
                "are tuned; G4 is certified at the r0 = 1/5, x0 = 1 benchmark at tree level only); the axion stays massless "
                "once the QCD anomaly or PQ-violating operators are included; the tuned eps = 0 point is the G3 witness; the "
                "released internal candidate is approved, viable or a prediction (decision U3 releases it and never approves "
                "it); the G8 exclusion is a proof-grade exclusion of the SO(10) x U(1)_X contract or of SO(10) axion models "
                "in general; the attested contract contains every allowed renormalizable coupling; G6, G7 or G8 is closed; "
                "the certified SU(5)+Delta point is a Standard-Model vacuum; the current repository validates the full "
                "theory; or the historical saddle excludes the gauged-U(1)_X model."
            ),
            "verdict": (
                "WITHHOLD APPROVAL. The audit succeeds and the gauged-U(1)_X model contract is attested by bound external "
                "SARAH execution evidence. G1, G2, G3 (SM Pati-Salam benchmark family, scoped), G4 (at the G3 witness "
                "benchmark, tree level) and G5 are closed, which meets decision D3, but decision D-E holds approval of the "
                "internal-candidate tier until G7 is CLOSED, and decision U3 never approves it. By decision U3 the "
                "internal candidate is released: " + release["label"] + " (CKM = 1, m_t = m_b, m_d = m_e; "
                "G8_SM_PATI_SALAM_FLAVOUR_NOGO_V20.json). G6 is open and G7-G8 remain blocked (sub-M_I coloured states "
                "and positivity beyond tree level, electroweak symmetry breaking, RG-anchor content, the Higgs quartic, "
                "Yukawas and proton decay), so no internal, conditional-benchmark, full-phenomenology, empirical, or "
                "exclusion claim is approved; the whole model is neither validated nor excluded by a proof-grade "
                "certificate."
                + (
                    " Program verdict (decision U1): " + gate_ledger.PROGRAM_VERDICT_HEADLINE + "."
                    if program_recorded
                    else ""
                )
            ),
        }
    if contract_ready and g3_closed and g4_closed:
        # Gate lists mirror G1_G8_GATE_LEDGER_V20: G1-G5 CLOSED (G3 on the SM
        # Pati-Salam track, G4 at its witness benchmark, tree level); G6 OPEN;
        # G7-G8 BLOCKED.  G4 CLOSED meets decision D3, but decision D-E holds
        # the internal-candidate tier until G7 is CLOSED (U3 release unavailable).
        return {
            "correct_public_claim": (
                "The authoritative gauged-U(1)_X model contract is attested by a manifest/log-bound external SARAH 4.15.3 "
                "execution, and G1, G2, G3, G4 and G5 are closed. " + sm_track.CLOSURE_SCOPE + " "
                + g4_closure.G4_CLOSED_SENTENCE + " The internal candidate is "
                + _hold_text(True, g7_recorded, probe_recorded)
                + " G6 is open and G7-G8 remain blocked. G1-G8 approval is withheld. " + history
            ),
            "incorrect_claim_do_not_use": (
                "G3 or G4 is closed for a physically realistic or natural vacuum (the doublet-triplet splitting, O05 and M_I "
                "are tuned; G4 is certified at the r0 = 1/5, x0 = 1 benchmark at tree level only); the axion stays massless "
                "once the QCD anomaly or PQ-violating operators are included; the tuned eps = 0 point is the G3 witness; an "
                "internal candidate is approved (decision D-E holds it until G7 is CLOSED); G6, G7 or G8 is closed; the "
                "certified SU(5)+Delta point is a Standard-Model vacuum; the current repository validates the full theory; "
                "or the historical saddle excludes the gauged-U(1)_X model."
            ),
            "verdict": (
                "WITHHOLD APPROVAL. The audit succeeds and the gauged-U(1)_X model contract is attested by bound external "
                "SARAH execution evidence. G1, G2, G3 (SM Pati-Salam benchmark family, scoped), G4 (at the G3 witness "
                "benchmark, tree level) and G5 are closed, which meets decision D3, but decision D-E holds the "
                "internal-candidate tier until G7 is CLOSED: for the declared benchmark (5 x (16 + 16bar) spectators at "
                "M_s ~ M_I, v_S = M_I) three independent two-loop RG codes find no perturbative gauge unification. G6 is "
                "open and G7-G8 remain blocked (sub-M_I coloured states and positivity beyond tree level, electroweak "
                "symmetry breaking, RG-anchor content, the Higgs quartic, Yukawas (flavour excluded on this witness branch "
                "at renormalizable tree level, Route C) and proton decay), so no internal, conditional-benchmark, "
                "full-phenomenology, empirical, or exclusion claim is approved; the whole model is neither validated nor "
                "excluded."
            ),
        }
    if contract_ready and g3_closed and held_pending_g7:
        # Hypothetical decision-D-E hold on the D3 caveats path (the closing
        # track's downstream caveats recorded as resolved while G4 is not
        # CLOSED).  Nothing here claims G4.  With the decision-U3 release
        # recorded the candidate is released, not approved.
        caveats_status = (
            release["text"] if release is not None else _hold_text(False, g7_recorded, probe_recorded)
        )
        caveats_release = (
            " By decision U3 the candidate is released: " + release["label"] + "."
            if release is not None
            else ""
        )
        return {
            "correct_public_claim": (
                "The authoritative gauged-U(1)_X model contract is attested by a manifest/log-bound external SARAH 4.15.3 "
                "execution, and G1, G2, G3 and G5 are closed. " + sm_track.CLOSURE_SCOPE + " The internal candidate is "
                + caveats_status + " G1-G8 approval is withheld. " + history
            ),
            "incorrect_claim_do_not_use": (
                "G3 is closed for a physically realistic or natural vacuum (the doublet-triplet splitting, O05 and M_I are "
                "tuned); G4 is closed; the tuned eps = 0 point is the G3 witness; an internal candidate is approved "
                "(decision D-E holds it until G7 is CLOSED and decision U3 never approves it); the certified SU(5)+Delta "
                "point is a Standard-Model vacuum; the current repository validates the full theory; or the historical "
                "saddle excludes the gauged-U(1)_X model."
            ),
            "verdict": (
                "WITHHOLD APPROVAL. The audit succeeds and the gauged-U(1)_X model contract is attested by bound external "
                "SARAH execution evidence. G1, G2, G3 (SM Pati-Salam benchmark family, scoped) and G5 are closed and the "
                "closing track's downstream caveats are recorded as resolved, which meets decision D3, but decision D-E "
                "holds the internal-candidate tier until G7 is CLOSED. G4 and G6-G8 are not closed, so no internal, full, "
                "empirical, or exclusion claim is approved."
                + caveats_release
            ),
        }
    if contract_ready and g3_closed:
        # Gate lists mirror G1_G8_GATE_LEDGER_V20: G1, G2, G3 (SM Pati-Salam
        # track, scoped) and G5 CLOSED; G4 OPEN; G6-G8 BLOCKED.  Decision D3
        # keeps the internal-candidate tier withheld.
        return {
            "correct_public_claim": (
                "The authoritative gauged-U(1)_X model contract is attested by "
                "a manifest/log-bound external SARAH 4.15.3 execution, and G1, "
                "G2, G3 and G5 are closed. " + sm_track.CLOSURE_SCOPE
                + " G1-G8 approval is withheld. " + history
            ),
            "incorrect_claim_do_not_use": (
                "G3 is closed for a physically realistic or natural vacuum (the "
                "doublet-triplet splitting, O05 and M_I are tuned); the tuned "
                "eps = 0 point is the G3 witness; an internal candidate is "
                "approved; the certified SU(5)+Delta point is a Standard-Model "
                "vacuum; the current repository validates the full theory; or "
                "the historical saddle excludes the gauged-U(1)_X model."
            ),
            "verdict": (
                "WITHHOLD APPROVAL. The audit succeeds and the gauged-U(1)_X "
                "model contract is attested by bound external SARAH execution "
                "evidence. G1, G2, G3 (SM Pati-Salam benchmark family, scoped) "
                "and G5 are closed, but G4 and G6-G8 remain open or blocked and "
                "the closing track's downstream caveats are unresolved, so no "
                "internal, full, empirical, or exclusion claim is approved."
            ),
        }
    if contract_ready:
        # Gate lists mirror G1_G8_GATE_LEDGER_V20: G1, G2, G5 CLOSED.
        return {
            "correct_public_claim": (
                "The authoritative gauged-U(1)_X model contract is attested by "
                "a manifest/log-bound external SARAH 4.15.3 execution, and G1, "
                "G2 and G5 are closed. G3 remains open (the certified G3 point "
                "is not a Standard-Model vacuum; an SM-preserving candidate "
                "must pass the final gate), and G4 and G6-G8 remain open, so "
                "G1-G8 approval is withheld. " + history
            ),
            "incorrect_claim_do_not_use": (
                "G3 is closed for the manuscript model; the certified "
                "SU(5)+Delta point is a Standard-Model vacuum; the current "
                "repository validates the full theory; or the historical "
                "saddle excludes the gauged-U(1)_X model."
            ),
            "verdict": (
                "WITHHOLD APPROVAL. The audit succeeds and the gauged-U(1)_X "
                "model contract is attested by bound external SARAH execution "
                "evidence, but G3 (which needs an SM-preserving candidate), G4 "
                "and G6-G8 remain open, so no internal, full, empirical, or "
                "exclusion claim is approved."
            ),
        }
    return {
        "correct_public_claim": (
            "The repository has a statically consistent tool-native SARAH input "
            "for the authoritative gauged-U(1)_X scalar contract, but lacks a "
            "v2 manifest/log-bound external SARAH execution attestation. G1-G8 "
            "approval is withheld. " + history
        ),
        "incorrect_claim_do_not_use": (
            "G1, G2, or G3 is closed for the manuscript model; the current "
            "repository validates the full theory; or the historical saddle "
            "excludes the gauged-U(1)_X model."
        ),
        "verdict": (
            "WITHHOLD APPROVAL. The audit itself succeeds, but the manuscript's "
            "gauged U(1)_X model still lacks a real external SARAH execution. "
            "Bind an actual v2 external run and recertify "
            "G1-G3 on the 44-direction, 51-real-parameter potential before any "
            "internal, full, empirical, or exclusion claim."
        ),
    }


def evaluate_reports(
    reports: dict[str, dict[str, Any]],
    *,
    current_test_count: int | None = None,
    attestation: dict[str, Any] | None = None,
    preload_errors: list[str] | None = None,
) -> dict[str, Any]:
    """Evaluate fresh contract reports while separating BLOCKED from failure."""
    errors = _execution_errors(reports, preload_errors)
    x_report = reports.get("x_contract", {})
    gauged_report = reports.get("gauged_contract", {})
    ledger = reports.get("g1_g8", {})
    authoritative = reports.get("authoritative", {})

    matrix_contract_gate = validation_matrix._model_contract_gate(
        {
            "x_contract": x_report,
            "gauged_contract": gauged_report,
        }
    )
    contract_ready = bool(
        not errors
        and matrix_contract_gate.get("state") == "PASS"
        and x_report.get("contract_consistent") is True
        and gauged_report.get("implementation_matches_manuscript") is True
    )

    gates = ledger.get("gates", {}) if isinstance(ledger, dict) else {}
    first_three_closed = all(
        isinstance(gates.get(name), dict)
        and gates[name].get("status") == gate_ledger.STATUS_CLOSED
        for name in ("G1", "G2", "G3")
    )
    all_eight_closed = all(
        isinstance(gates.get(name), dict)
        and gates[name].get("status") == gate_ledger.STATUS_CLOSED
        for name in (f"G{index}" for index in range(1, 9))
    )

    authoritative_classification = authoritative.get("classification", {})
    if not isinstance(authoritative_classification, dict):
        errors.append("authoritative classification is not a JSON object")
        authoritative_classification = {}

    # Decision D3: G1-G3 CLOSED alone does not meet the internal-candidate
    # conditions.  The closing G3 track's downstream caveats must also be
    # resolved, or G4 (which classifies the witness's zero modes) must be
    # CLOSED; G4 counts as CLOSED only with the ledger's certified closure
    # evidence (strict).  Decision D-E holds approval until G7 is CLOSED
    # (strictly: G7 and its ledger dependency G6 both CLOSED).  Decision U3
    # removes the approval branch: the tier is never approved.
    g3_track = ledger.get("g3_sm_target_track", {}) if isinstance(ledger, dict) else {}
    gate_rows = gates if isinstance(gates, dict) else {}
    g3_row = gate_rows.get("G3")
    g4_row = gate_rows.get("G4")
    g3_closed = isinstance(g3_row, dict) and g3_row.get("status") == gate_ledger.STATUS_CLOSED
    g5_closed = (
        isinstance(gate_rows.get("G5"), dict)
        and gate_rows["G5"].get("status") == gate_ledger.STATUS_CLOSED
    )
    g8_closed = (
        isinstance(gate_rows.get("G8"), dict)
        and gate_rows["G8"].get("status") == gate_ledger.STATUS_CLOSED
    )
    track_caveats_resolved = bool(
        isinstance(g3_track, dict)
        and g3_track.get("closed") is True
        and g3_track.get("downstream_caveats_resolved") is True
    )
    g4_closed = g4_closure.ledger_g4_closed(ledger) is True
    g4_evidence = g4_row.get("closure_evidence") if isinstance(g4_row, dict) else None
    g4_evidence_certified = isinstance(g4_evidence, dict) and g4_evidence.get("certified") is True
    d3_satisfied = bool(track_caveats_resolved or g4_closed)
    g7_closed = all(
        isinstance(gate_rows.get(name), dict)
        and gate_rows[name].get("status") == gate_ledger.STATUS_CLOSED
        for name in ("G6", "G7")
    )
    caveats_cleared = bool(d3_satisfied and g7_closed)
    d3_met = bool(contract_ready and first_three_closed and d3_satisfied and not errors)
    # Decision U3: never approved, on every path (there is no approval branch).
    internal_candidate = False
    held_pending_g7 = bool(d3_met and not g7_closed)
    d3_met_with_g7_closed = bool(d3_met and g7_closed)
    frontier = _g5_g8_frontier(gate_rows)
    frontier_expected = frontier == EXPECTED_G5_G8_FRONTIER
    # The committed G7 records (decoupled-singlet benchmark evidence and the
    # coupled-singlet two-loop probe), read through the ledger row.
    g7_row = gate_rows.get("G7")
    g7_benchmark = g7_row.get("benchmark_evidence") if isinstance(g7_row, dict) else None
    g7_recorded = isinstance(g7_benchmark, dict) and g7_benchmark.get("recorded") is True
    g7_probe = g7_row.get("coupled_singlet_two_loop_probe") if isinstance(g7_row, dict) else None
    probe_recorded = isinstance(g7_probe, dict) and g7_probe.get("recorded") is True
    # Decision U3: a candidate that meets D3 is released (never approved) when
    # G5 is CLOSED, G8 is not CLOSED and the ledger records the G8 flavour
    # pulls and the G8 structural obstruction.
    release_binding = _u3_release_binding(ledger)
    released = bool(d3_met and g5_closed and not g8_closed and release_binding["recorded"])
    release = _release_record(release_binding, g4_closed=g4_closed) if released else None
    internal_candidate_gate = {
        "G1_G2_G3_closed": first_three_closed,
        "G3_closed": g3_closed,
        "closing_track": g3_row.get("closing_track") if isinstance(g3_row, dict) else None,
        "closing_track_downstream_caveats_resolved": track_caveats_resolved,
        "G4_closed": g4_closed,
        "G4_closure_evidence_certified": g4_evidence_certified,
        "G5_closed": g5_closed,
        "D3_satisfied": d3_satisfied,
        "G7_closed": g7_closed,
        "G8_closed": g8_closed,
        "G5_G8_frontier": frontier,
        "G5_G8_frontier_expected": frontier_expected,
        "caveats_cleared": caveats_cleared,
        "approval_held_pending_G7": held_pending_g7,
        "approval_disabled_by_U3": not INTERNAL_CANDIDATE_APPROVAL_POSSIBLE,
        "D3_met_with_G7_closed_not_approved": d3_met_with_g7_closed,
        "rule": sm_track.D3_RULE,
        "D_E_rule": D_E_RULE,
        "D_E_evidence": _d_e_evidence(g7_recorded, probe_recorded),
        "G4_closure_decision": g4_closure.G4_CLOSURE_DECISION,
        "released_not_approved": released,
        "U3_rule": U3_RULE,
        "G8_flavour_pulls_bound": release_binding["recorded"],
        "G7_benchmark_evidence_recorded": g7_recorded,
        "G7_coupled_singlet_probe_recorded": probe_recorded,
    }
    # No approval, so no approval scope (the key is kept for the schema).
    internal_candidate_scope = None
    if released:
        internal_candidate_hold = None
    elif held_pending_g7:
        internal_candidate_hold = _hold_text(g4_closed, g7_recorded, probe_recorded)
    elif d3_met_with_g7_closed:
        internal_candidate_hold = INTERNAL_CANDIDATE_APPROVAL_DISABLED_HOLD
    else:
        internal_candidate_hold = None
    internal_candidate_tier = TIER_RELEASED_NOT_APPROVED if released else "WITHHELD"
    # The ledger's separate program verdict (decision U1) and G1 truncation
    # scope (decision U5), copied for reference; never a status input here.
    # The program verdict is copied only while the ledger itself passed and
    # its gate frontier is the recorded one (G1-G5 CLOSED, G6 OPEN, G7-G8
    # BLOCKED); otherwise the unavailable variant is reported (fail closed).
    ledger_program = ledger.get("program_verdict") if isinstance(ledger, dict) else None
    ledger_statuses = {
        name: gate_rows[name].get("status") if isinstance(gate_rows.get(name), dict) else None
        for name in gate_ledger.PROGRAM_VERDICT_EXPECTED_STATUSES
    }
    ledger_n_failed = ledger.get("n_failed") if isinstance(ledger, dict) else None
    ledger_frontier_recorded = bool(
        ledger_statuses == gate_ledger.PROGRAM_VERDICT_EXPECTED_STATUSES
        and isinstance(ledger_n_failed, int)
        and not isinstance(ledger_n_failed, bool)
        and ledger_n_failed == 0
    )
    if isinstance(ledger_program, dict) and ledger_frontier_recorded:
        program_verdict = {
            "code": ledger_program.get("code"),
            "headline": ledger_program.get("headline"),
            "text": ledger_program.get("text"),
            "recorded": ledger_program.get("recorded") is True,
        }
    else:
        program_verdict = {
            "code": gate_ledger.PROGRAM_VERDICT_CODE_UNAVAILABLE,
            "headline": None,
            "text": None,
            "recorded": False,
        }
    ledger_scope = ledger.get("model_contract_scope") if isinstance(ledger, dict) else None
    model_contract_scope = {
        "recorded": isinstance(ledger_scope, dict) and ledger_scope.get("recorded") is True,
        "scope_text": ledger_scope.get("scope_text") if isinstance(ledger_scope, dict) else None,
    }
    # Old aligned benchmarks were calculated under the superseded no-X
    # contract.  They remain evidence, but not an approvable current benchmark.
    conditional_benchmark = False
    full_phenomenology = bool(
        contract_ready
        and all_eight_closed
        and authoritative_classification.get("whole_model_validated") is True
        and not errors
    )
    empirical_realization = bool(
        full_phenomenology
        and authoritative_classification.get("empirical_discovery") is True
    )
    whole_model_excluded = bool(
        contract_ready
        and authoritative_classification.get("whole_model_excluded") is True
        and not errors
    )

    if errors:
        overall_state = "EXECUTION_FAIL"
        classification = "THEORY_CONFIRMATION_AUDIT_EXECUTION_FAILED"
        decision = WITHHOLD_APPROVAL
        status = "THEORY_CONFIRMATION_AUDIT_EXECUTION_FAILED"
    elif not contract_ready:
        overall_state = "BLOCKED"
        classification = MODEL_CONTRACT_BLOCKED
        decision = WITHHOLD_APPROVAL
        status = "THEORY_CONFIRMATION_AUDIT_COMPLETE__MODEL_CONTRACT_BLOCKED"
    elif whole_model_excluded:
        overall_state = "FAIL"
        classification = "AUTHORITATIVE_MODEL_EXCLUDED"
        decision = "REJECT"
        status = "THEORY_CONFIRMATION_COMPLETE__MODEL_EXCLUDED"
    elif full_phenomenology:
        overall_state = "PASS"
        classification = "FULL_PHENOMENOLOGY_VALIDATED__NO_DISCOVERY_IMPLIED"
        decision = "VALIDATE_FULL_PHENOMENOLOGY"
        status = "THEORY_CONFIRMATION_COMPLETE__FULL_PHENOMENOLOGY_VALIDATED"
    else:
        overall_state = "OPEN"
        classification = "AUTHORITATIVE_GATES_OPEN"
        decision = WITHHOLD_APPROVAL
        status = "THEORY_CONFIRMATION_AUDIT_COMPLETE__GATES_OPEN"

    scientific_blockers: list[str] = []
    for source in (x_report, ledger, authoritative):
        for key in ("scientific_blockers", "blockers"):
            values = source.get(key, []) if isinstance(source, dict) else []
            if isinstance(values, list):
                scientific_blockers.extend(str(value) for value in values)
    mismatches = gauged_report.get("implementation_mismatches", [])
    if isinstance(mismatches, list):
        scientific_blockers.extend(str(value) for value in mismatches)
    scientific_blockers = sorted(set(scientific_blockers))

    current_tests = current_test_count if current_test_count is not None else 0
    historical = ledger.get("historical_option_c_subtheorems", {})
    claims = _claim_text(
        contract_ready,
        g3_closed=g3_closed,
        g4_closed=g4_closed,
        held_pending_g7=held_pending_g7,
        release=release,
        program_recorded=program_verdict["recorded"],
        truncation_recorded=model_contract_scope["recorded"],
        g7_recorded=g7_recorded,
        probe_recorded=probe_recorded,
        frontier=frontier,
    )
    return {
        "title": "SO(10) x Z17 axion candidate v20 - confirmation verdict",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "overall_state": overall_state,
        "classification": classification,
        "decision": decision,
        "verdict_code": classification,
        "integrity_pass": not errors,
        "n_failed": len(errors),
        "failures": errors,
        "audit_failures": errors,
        "model_contract_id": gauged_report.get(
            "model_contract_id", "gauged_u1x_phi17_v20"
        ),
        "model_contract_ready": contract_ready,
        "validation_matrix_contract_gate": matrix_contract_gate,
        "approval": {
            "internal_candidate": internal_candidate,
            "conditional_benchmark": conditional_benchmark,
            "full_phenomenology": full_phenomenology,
            "empirical_realization": empirical_realization,
            "whole_model_excluded": whole_model_excluded,
            "full_approval_blockers": scientific_blockers,
        },
        "internal_candidate_approved": internal_candidate,
        "internal_candidate_gate": internal_candidate_gate,
        "internal_candidate_scope": internal_candidate_scope,
        "internal_candidate_hold": internal_candidate_hold,
        "internal_candidate_release": release["text"] if release is not None else None,
        "internal_candidate_release_label": release["label"] if release is not None else None,
        "internal_candidate_release_binding": release_binding,
        "program_verdict": program_verdict,
        "model_contract_scope": model_contract_scope,
        "conditional_benchmark_approved": conditional_benchmark,
        "full_phenomenology_approved": full_phenomenology,
        "empirical_realization_approved": empirical_realization,
        "whole_model_excluded": whole_model_excluded,
        "full_theory_validated": full_phenomenology,
        "current_tree_unit_tests": current_tests,
        "ci_attestation": attestation or ci_attestation(current_tests),
        "source_reports": {
            name: _source_snapshot(report)
            for name, report in reports.items()
            if isinstance(report, dict)
        },
        "authoritative_gate_classification": authoritative_classification,
        "scientific_blockers": scientific_blockers,
        "historical_option_c_subtheorems": historical,
        "scope": {
            "authoritative_current_model": "gauged_u1x_phi17_v20",
            "historical_option_c_is_authoritative": False,
            "historical_results_may_close_current_gates": False,
            "software_pass_implies_scientific_approval": False,
            "release_is_approval": False,
            "program_verdict_changes_gate_statuses": False,
        },
        "tiers": {
            "INTERNAL_CANDIDATE": internal_candidate_tier,
            "CONDITIONAL_BENCHMARK": "WITHHELD",
            "FULL_PHENOMENOLOGY": "WITHHELD",
            "EMPIRICAL_REALIZATION": "NOT_ESTABLISHED",
            "WHOLE_MODEL_EXCLUSION": "NOT_ESTABLISHED",
        },
        "tier_definitions": dict(TIER_DEFINITIONS),
        "tier_state_definitions": dict(TIER_STATE_DEFINITIONS),
        "correct_public_claim": claims["correct_public_claim"],
        "incorrect_claim_do_not_use": claims["incorrect_claim_do_not_use"],
        "verdict": claims["verdict"],
    }


def build_verdict() -> dict[str, Any]:
    current_tests = unittest.defaultTestLoader.discover(str(ROOT)).countTestCases()
    return evaluate_reports(
        fresh_source_reports(),
        current_test_count=current_tests,
        attestation=ci_attestation(current_tests),
    )


def write_markdown(verdict: dict[str, Any]) -> str:
    approval = verdict["approval"]
    gate = verdict.get("internal_candidate_gate") or {}
    lines = [
        "# Theory confirmation verdict - v20",
        "",
        f"**Status:** `{verdict['status']}`",
        f"**Overall state:** `{verdict['overall_state']}`",
        f"**Classification:** `{verdict['classification']}`",
        f"**Decision:** `{verdict['decision']}`",
        "",
        verdict["verdict"],
        "",
        "## Approval levels",
        "",
        f"- Internal candidate: **{approval['internal_candidate']}**",
        "- Internal-candidate gate (D3 and D-E): caveats_cleared = "
        + str(gate.get("caveats_cleared"))
        + " (G4_closed = "
        + str(gate.get("G4_closed"))
        + "; closing-track downstream caveats resolved = "
        + str(gate.get("closing_track_downstream_caveats_resolved"))
        + "; G7_closed = "
        + str(gate.get("G7_closed"))
        + "; held pending G7 = "
        + str(gate.get("approval_held_pending_G7"))
        + "; approval disabled by decision U3 = "
        + str(gate.get("approval_disabled_by_U3"))
        + ")",
    ]
    scope = verdict.get("internal_candidate_scope")
    if scope is not None:
        lines.append(f"- Internal-candidate scope: {scope}")
    hold = verdict.get("internal_candidate_hold")
    if hold is not None:
        lines.append(f"- Internal-candidate hold: {hold}")
    release = verdict.get("internal_candidate_release")
    if release is not None:
        lines.append(f"- Internal-candidate release: {release}")
    tiers = verdict.get("tiers") or {}
    lines.append(f"- Internal-candidate tier: **{tiers.get('INTERNAL_CANDIDATE')}**")
    lines += [
        f"- Conditional benchmark: **{approval['conditional_benchmark']}**",
        f"- Full phenomenology: **{approval['full_phenomenology']}**",
        f"- Empirical realization: **{approval['empirical_realization']}**",
        f"- Whole-model exclusion: **{approval['whole_model_excluded']}**",
        "",
        "## Tiers",
        "",
    ]
    definitions = verdict.get("tier_definitions") or {}
    lines.extend(
        f"- {name}: **{state}** - {definitions.get(name, '')}"
        for name, state in tiers.items()
    )
    program = verdict.get("program_verdict") or {}
    lines += [
        "",
        "## Program verdict (decision U1)",
        "",
        f"**Code:** `{program.get('code')}`",
        "",
        str(program.get("text") if program.get("text") is not None else "Program verdict not recorded."),
        "",
        "## Scientific blockers",
        "",
    ]
    blockers = verdict.get("scientific_blockers") or []
    lines.extend(f"- `{item}`" for item in blockers)
    if not blockers:
        lines.append("- None")
    lines += [
        "",
        "## Historical scope",
        "",
        "The preserved Option-C G1-G3 calculations are non-authoritative",
        "subtheorems of the superseded no-X potential.",
        "",
        "## Correct public claim",
        "",
        f"> {verdict['correct_public_claim']}",
        "",
    ]
    return "\n".join(lines)


def exit_code(
    verdict: dict[str, Any],
    *,
    require_internal_approval: bool = False,
    require_full_approval: bool = False,
    expect_blocked: bool = False,
    expect_open: bool = False,
) -> int:
    if verdict.get("n_failed", 1) != 0:
        return 1
    if require_internal_approval and not verdict.get(
        "internal_candidate_approved", False
    ):
        return 2
    if require_full_approval and not verdict.get(
        "full_phenomenology_approved", False
    ):
        return 3
    if expect_blocked and verdict.get("overall_state") != "BLOCKED":
        return 4
    if expect_open and verdict.get("overall_state") != "OPEN":
        return 5
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-internal-approval", action="store_true")
    parser.add_argument("--require-full-approval", action="store_true")
    parser.add_argument("--expect-blocked", action="store_true")
    parser.add_argument(
        "--expect-open",
        action="store_true",
        help="fail unless the honest state is OPEN (contract consistent, gates open)",
    )
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args(argv)

    verdict = build_verdict()
    if not args.no_write:
        OUT_JSON.write_text(
            json.dumps(verdict, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        OUT_MD.write_text(write_markdown(verdict), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": verdict["status"],
                "overall_state": verdict["overall_state"],
                "classification": verdict["classification"],
                "decision": verdict["decision"],
                "approval": verdict["approval"],
                "n_failed": verdict["n_failed"],
            },
            indent=2,
        )
    )
    return exit_code(
        verdict,
        require_internal_approval=args.require_internal_approval,
        require_full_approval=args.require_full_approval,
        expect_blocked=args.expect_blocked,
        expect_open=args.expect_open,
    )


if __name__ == "__main__":
    raise SystemExit(main())
