#!/usr/bin/env python3
"""Ultimate fail-closed gate for the authoritative SO(10) axion model.

The gate consumes the fresh contract-aware confirmation layer.  It does not
load the historical release verdict stack, so an old Option-C approval cannot
override the manuscript/executable U(1)_X mismatch.

Its tiers are the confirmation tiers (``ULTIMATE_THEORY_GATE_V20_SCOPE.md``).
Decision U3 removes the approval of tier 1, the internal candidate
(internal consistency, not phenomenology): ``internal_candidate_approved`` is
False on every path and ``--require-internal-approval`` always fails.  A
candidate that meets decision D3 may be released, never approved (tier
state RELEASED_NOT_APPROVED: certified tree-level vacuum, excluded by G8
flavour); decision D-E holds approval until G7 is CLOSED in any case.  The
overall state stays OPEN until every G1-G8 gate is CLOSED.
"""

from __future__ import annotations

import argparse
import json
import unittest
from pathlib import Path
from typing import Any

import theory_confirmation_verdict_v20 as confirmation

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "ULTIMATE_THEORY_GATE_V20_VERDICT.json"
OUT_MD = ROOT / "ULTIMATE_THEORY_GATE_V20.md"


VERDICT_INTERNAL_CANDIDATE_HELD_PENDING_G7 = (
    "WITHHOLD APPROVAL. The audit has no execution failure and the gauged-U(1)_X model contract is attested by bound "
    "external SARAH execution evidence; G1, G2, G3 (SM Pati-Salam benchmark family, scoped), G4 (at the G3 witness "
    "benchmark, tree level) and G5 are closed, which meets decision D3, but decision D-E holds the internal-candidate "
    "tier until G7 is CLOSED: for the declared benchmark (5 x (16 + 16bar) spectators at M_s ~ M_I, v_S = M_I) three "
    "independent two-loop RG codes find no perturbative gauge unification, a G7 no-go for that benchmark. The G6-G8 "
    "scientific gates remain open or blocked (sub-M_I coloured states, positivity beyond tree level and electroweak "
    "symmetry breaking, RG-anchor content and the Higgs quartic, Yukawas (flavour excluded on this witness branch at "
    "renormalizable tree level, Route C) and proton decay). No internal-candidate, conditional-benchmark, "
    "full-phenomenology, empirical-realization, or whole-model-exclusion claim is approved; the whole model is "
    "neither validated nor excluded."
)

# Decision U3: the candidate released, never approved.
VERDICT_INTERNAL_CANDIDATE_RELEASED_TEMPLATE = (
    "WITHHOLD APPROVAL. The audit has no execution failure and the gauged-U(1)_X model contract is attested by bound "
    "external SARAH execution evidence; G1, G2, G3 (SM Pati-Salam benchmark family, scoped), G4 (at the G3 witness "
    "benchmark, tree level) and G5 are closed, which meets decision D3, but decision D-E holds approval of the "
    "internal-candidate tier until G7 is CLOSED, and decision U3 never approves it. By decision U3 the internal "
    "candidate is released: {label} (CKM = 1, m_t = m_b, m_d = m_e; G8_SM_PATI_SALAM_FLAVOUR_NOGO_V20.json). The "
    "G6-G8 scientific gates remain open or blocked (sub-M_I coloured states, positivity beyond tree level and "
    "electroweak symmetry breaking, RG-anchor content and the Higgs quartic, Yukawas and proton decay). No "
    "internal-candidate, conditional-benchmark, full-phenomenology, empirical-realization, or whole-model-exclusion "
    "claim is approved; the whole model is neither validated nor excluded by a proof-grade certificate."
)


def _verdict(
    contract_ready: bool,
    g3_closed: bool = False,
    g4_closed: bool = False,
    held_pending_g7: bool = False,
    release_label: str | None = None,
    program_recorded: bool = False,
    frontier: dict[str, Any] | None = None,
) -> str:
    """Verdict text, branched on model-contract readiness, ledger G3/G4, D3, D-E and U3.

    ``g4_closed`` is the confirmation's strict G4 closure (status CLOSED with
    certified closure evidence), ``held_pending_g7`` its decision-D-E hold,
    ``release_label`` the decision-U3 release label (None when the release is
    not available), ``program_recorded`` whether the ledger's program verdict
    (decision U1) is recorded and ``frontier`` the ledger's G5-G8 statuses
    (None: the recorded G5 CLOSED, G6 OPEN, G7-G8 BLOCKED frontier).  There is no
    approval branch: decision U3 never approves the internal-candidate tier.
    """
    frontier_expected = frontier is None or dict(frontier) == confirmation.EXPECTED_G5_G8_FRONTIER
    if contract_ready and g3_closed and not frontier_expected:
        # Hypothetical or forged G5-G8 frontier (for example G6 and G7 CLOSED).
        return (
            "WITHHOLD APPROVAL. The audit has no execution failure and the gauged-U(1)_X model contract is attested "
            "by bound external SARAH execution evidence; G3 is closed on the SM Pati-Salam benchmark family (scoped), "
            "but the ledger records " + confirmation._frontier_text(frontier) + ", not the recorded "
            + confirmation.EXPECTED_FRONTIER_TEXT + " frontier. Decision U3 never approves the "
            "internal-candidate tier"
            + (": it is released as " + release_label if release_label else "")
            + ". No internal-candidate, conditional-benchmark, full-phenomenology, empirical-realization, or "
            "whole-model-exclusion claim is approved."
        )
    if contract_ready and g3_closed and g4_closed and release_label:
        # Decision U3: G1-G5 CLOSED, D-E holds approval, and the candidate is
        # released (never approved) on the ledger's bound G8 evidence.
        return VERDICT_INTERNAL_CANDIDATE_RELEASED_TEMPLATE.format(label=release_label) + (
            " Program verdict (decision U1): " + confirmation.gate_ledger.PROGRAM_VERDICT_HEADLINE + "."
            if program_recorded
            else ""
        )
    if contract_ready and g3_closed and g4_closed:
        # G1-G5 CLOSED in G1_G8_GATE_LEDGER_V20 (G4 at the G3 witness, tree
        # level); G4 meets decision D3, but decision D-E holds the tier.
        return VERDICT_INTERNAL_CANDIDATE_HELD_PENDING_G7
    if contract_ready and g3_closed and held_pending_g7:
        # Hypothetical decision-D-E hold on the D3 caveats path (the closing
        # track's caveats recorded as resolved while G4 is not CLOSED).
        return (
            "WITHHOLD APPROVAL. The audit has no execution failure and the gauged-U(1)_X model contract is attested "
            "by bound external SARAH execution evidence; G3 is closed on the SM Pati-Salam benchmark family (scoped) "
            "and the closing track's downstream caveats are recorded as resolved, which meets decision D3, but "
            "decision D-E holds the internal-candidate tier until G7 is CLOSED, and the G4 and G6-G8 scientific gates "
            "remain open. No internal-candidate, conditional-benchmark, full-phenomenology, empirical-realization, or "
            "whole-model-exclusion claim is approved."
            + (
                " By decision U3 the candidate is released: " + release_label + "."
                if release_label
                else ""
            )
        )
    if contract_ready and g3_closed:
        # G1, G2, G3 (SM Pati-Salam track, scoped) and G5 are CLOSED in
        # G1_G8_GATE_LEDGER_V20; decision D3 keeps the internal candidate
        # withheld while the closing track's downstream caveats are open.
        lead = (
            "WITHHOLD APPROVAL. The audit has no execution failure and the "
            "gauged-U(1)_X model contract is attested by bound external SARAH "
            "execution evidence; G3 is closed on the SM Pati-Salam benchmark "
            "family (scoped), but the G4 and G6-G8 scientific gates remain "
            "open and the closing track's downstream caveats are unresolved. "
        )
    elif contract_ready:
        # G5 is CLOSED in G1_G8_GATE_LEDGER_V20, so it is not listed as open.
        lead = (
            "WITHHOLD APPROVAL. The audit has no execution failure and the "
            "gauged-U(1)_X model contract is attested by bound external SARAH "
            "execution evidence, but the G3, G4 and G6-G8 scientific gates "
            "remain open. "
        )
    else:
        lead = (
            "WITHHOLD APPROVAL. The audit has no execution failure, but the "
            "statically consistent, tool-native gauged-U(1)_X model has no v2 "
            "manifest/log-bound external SARAH execution evidence. "
        )
    return lead + (
        "No internal-candidate, conditional-benchmark, full-phenomenology, "
        "empirical-realization, or whole-model-exclusion claim is approved."
    )


def evaluate_reports(
    reports: dict[str, dict[str, Any]],
    *,
    current_test_count: int | None = None,
    preload_errors: list[str] | None = None,
) -> dict[str, Any]:
    """Evaluate injected fresh reports; useful for sabotage tests."""
    result = confirmation.evaluate_reports(
        reports,
        current_test_count=current_test_count,
        preload_errors=preload_errors,
    )

    if not result["integrity_pass"]:
        status = "ULTIMATE_GATE_EXECUTION_FAILED"
    elif result["overall_state"] == "BLOCKED":
        status = "ULTIMATE_GATE_AUDIT_COMPLETE__MODEL_CONTRACT_BLOCKED"
    elif result["whole_model_excluded"]:
        status = "ULTIMATE_GATE_COMPLETE__MODEL_EXCLUDED"
    elif result["full_phenomenology_approved"]:
        status = "ULTIMATE_GATE_COMPLETE__FULL_PHENOMENOLOGY_VALIDATED"
    else:
        status = "ULTIMATE_GATE_AUDIT_COMPLETE__APPROVAL_OPEN"

    return {
        "status": status,
        "overall_state": result["overall_state"],
        "classification": result["classification"],
        "decision": result["decision"],
        "integrity_pass": result["integrity_pass"],
        "n_failed": result["n_failed"],
        "errors": result["failures"],
        "failures": result["failures"],
        "current_tree_unit_tests": result["current_tree_unit_tests"],
        "model_contract_id": result["model_contract_id"],
        "model_contract_ready": result["model_contract_ready"],
        "internal_candidate_approved": result[
            "internal_candidate_approved"
        ],
        "internal_candidate_gate": result["internal_candidate_gate"],
        "internal_candidate_scope": result["internal_candidate_scope"],
        "internal_candidate_hold": result["internal_candidate_hold"],
        "internal_candidate_release": result["internal_candidate_release"],
        "internal_candidate_release_label": result["internal_candidate_release_label"],
        "internal_candidate_release_binding": result["internal_candidate_release_binding"],
        "tiers": result["tiers"],
        "tier_state_definitions": result["tier_state_definitions"],
        "program_verdict": result["program_verdict"],
        "model_contract_scope": result["model_contract_scope"],
        "conditional_benchmark_approved": result[
            "conditional_benchmark_approved"
        ],
        "full_phenomenology_approved": result[
            "full_phenomenology_approved"
        ],
        "full_theory_validated": result["full_theory_validated"],
        "empirical_realization_approved": result[
            "empirical_realization_approved"
        ],
        "whole_model_excluded": result["whole_model_excluded"],
        "approval": result["approval"],
        "scientific_blockers": result["scientific_blockers"],
        "full_approval_blockers": result["scientific_blockers"],
        "validation_matrix_contract_gate": result[
            "validation_matrix_contract_gate"
        ],
        "authoritative_gate_classification": result[
            "authoritative_gate_classification"
        ],
        "source_reports": result["source_reports"],
        "historical_option_c_subtheorems": result[
            "historical_option_c_subtheorems"
        ],
        "scope": result["scope"],
        "warnings": [
            "Historical Option-C results are preserved as non-authoritative "
            "subtheorems only."
        ],
        "verdict": _verdict(
            result["model_contract_ready"],
            g3_closed=result["internal_candidate_gate"]["G3_closed"],
            g4_closed=result["internal_candidate_gate"]["G4_closed"],
            held_pending_g7=result["internal_candidate_gate"]["approval_held_pending_G7"],
            release_label=result["internal_candidate_release_label"],
            program_recorded=result["program_verdict"]["recorded"],
            frontier=result["internal_candidate_gate"]["G5_G8_frontier"],
        ),
    }


def build_report(root: Path = ROOT) -> dict[str, Any]:
    current_tests = unittest.defaultTestLoader.discover(str(root)).countTestCases()
    return evaluate_reports(
        confirmation.fresh_source_reports(),
        current_test_count=current_tests,
    )


def write_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Ultimate theory gate - v20",
        "",
        f"**Status:** `{report['status']}`",
        f"**Overall state:** `{report['overall_state']}`",
        f"**Classification:** `{report['classification']}`",
        f"**Decision:** `{report['decision']}`",
        "",
        report["verdict"],
        "",
        "## Approval levels",
        "",
        f"- Internal candidate: **{report['internal_candidate_approved']}**",
    ]
    scope = report.get("internal_candidate_scope")
    if scope is not None:
        lines.append(f"- Internal-candidate scope: {scope}")
    hold = report.get("internal_candidate_hold")
    if hold is not None:
        lines.append(f"- Internal-candidate hold: {hold}")
    release = report.get("internal_candidate_release")
    if release is not None:
        lines.append(f"- Internal-candidate release: {release}")
    tiers = report.get("tiers") or {}
    lines.append(f"- Internal-candidate tier: **{tiers.get('INTERNAL_CANDIDATE')}**")
    program = report.get("program_verdict") or {}
    lines += [
        f"- Conditional benchmark: **{report['conditional_benchmark_approved']}**",
        f"- Full phenomenology: **{report['full_phenomenology_approved']}**",
        f"- Empirical realization: **{report['empirical_realization_approved']}**",
        f"- Whole-model exclusion: **{report['whole_model_excluded']}**",
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
    blockers = report.get("scientific_blockers") or []
    lines.extend(f"- `{item}`" for item in blockers)
    if not blockers:
        lines.append("- None")
    lines += ["", "## Integrity errors", ""]
    errors = report.get("errors") or []
    lines.extend(f"- {item}" for item in errors)
    if not errors:
        lines.append("- None")
    lines.append("")
    return "\n".join(lines)


def exit_code(
    report: dict[str, Any],
    *,
    require_internal_approval: bool = False,
    require_full_approval: bool = False,
    expect_blocked: bool = False,
    expect_full_block: bool = False,
    expect_open: bool = False,
) -> int:
    """Return zero for an honest BLOCKED/OPEN audit, nonzero for strict approval."""
    if report.get("n_failed", 1) != 0 or not report.get(
        "integrity_pass", False
    ):
        return 1
    if require_internal_approval and not report.get(
        "internal_candidate_approved", False
    ):
        return 2
    if require_full_approval and not report.get(
        "full_phenomenology_approved", False
    ):
        return 3
    if expect_blocked and report.get("overall_state") != "BLOCKED":
        return 4
    if expect_full_block and report.get("full_phenomenology_approved", False):
        return 5
    if expect_open and report.get("overall_state") != "OPEN":
        return 6
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-internal-approval", action="store_true")
    parser.add_argument("--require-full-approval", action="store_true")
    parser.add_argument("--expect-blocked", action="store_true")
    parser.add_argument(
        "--expect-full-block",
        action="store_true",
        help="compatibility mode: fail only if full approval is unexpectedly true",
    )
    parser.add_argument(
        "--expect-open",
        action="store_true",
        help="fail unless the honest state is OPEN (contract consistent, gates open)",
    )
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args(argv)

    report = build_report()
    if not args.no_write:
        OUT_JSON.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        OUT_MD.write_text(write_markdown(report), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": report["status"],
                "overall_state": report["overall_state"],
                "classification": report["classification"],
                "decision": report["decision"],
                "approval": report["approval"],
                "n_failed": report["n_failed"],
            },
            indent=2,
        )
    )
    return exit_code(
        report,
        require_internal_approval=args.require_internal_approval,
        require_full_approval=args.require_full_approval,
        expect_blocked=args.expect_blocked,
        expect_full_block=args.expect_full_block,
        expect_open=args.expect_open,
    )


if __name__ == "__main__":
    raise SystemExit(main())
