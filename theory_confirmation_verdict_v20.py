#!/usr/bin/env python3
"""Fail-closed theory-confirmation verdict for SO(10) axion v20.

The authoritative manuscript gauges ``U(1)_X``.  This verdict is assembled
from fresh builders, rather than from the older release JSON stack, so stale
Option-C results cannot approve the manuscript model.  A scientifically
blocked report is still a successful audit: the default command exits zero,
while explicit approval requirements fail nonzero.
"""

from __future__ import annotations

import argparse
import json
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
import gauged_u1x_scalar_contract_v20 as gauged_contract
import theory_validation_matrix_v20 as validation_matrix

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "THEORY_CONFIRMATION_VERDICT.json"
OUT_MD = ROOT / "THEORY_CONFIRMATION_VERDICT.md"

MODEL_CONTRACT_BLOCKED = (
    "MODEL_CONTRACT_INCONSISTENT__AUTHORITATIVE_GATES_REOPENED"
)
WITHHOLD_APPROVAL = "WITHHOLD_APPROVAL"

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


def _claim_text(contract_ready: bool, g3_closed: bool = False) -> dict[str, str]:
    """Public-claim and verdict text, branched on model-contract readiness.

    ``g3_closed`` is the ledger's G3 status (CLOSED only through the final
    gate's SM Pati-Salam track); it changes the text only on a ready contract.
    """
    history = (
        "Historical Option-C calculations are scoped subtheorems and neither "
        "validate nor exclude the gauged model."
    )
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

    # Decision D3: G1-G3 CLOSED alone does not approve an internal candidate.
    # The closing G3 track's downstream caveats must also be resolved, or G4
    # (which classifies the witness's zero modes) must be CLOSED.
    g3_track = ledger.get("g3_sm_target_track", {}) if isinstance(ledger, dict) else {}
    g3_row = gates.get("G3") if isinstance(gates, dict) else None
    g4_row = gates.get("G4") if isinstance(gates, dict) else None
    g3_closed = isinstance(g3_row, dict) and g3_row.get("status") == gate_ledger.STATUS_CLOSED
    track_caveats_resolved = bool(
        isinstance(g3_track, dict)
        and g3_track.get("closed") is True
        and g3_track.get("downstream_caveats_resolved") is True
    )
    g4_closed = isinstance(g4_row, dict) and g4_row.get("status") == gate_ledger.STATUS_CLOSED
    caveats_cleared = bool(track_caveats_resolved or g4_closed)
    internal_candidate = bool(
        contract_ready and first_three_closed and caveats_cleared and not errors
    )
    internal_candidate_gate = {
        "G1_G2_G3_closed": first_three_closed,
        "G3_closed": g3_closed,
        "closing_track": g3_row.get("closing_track") if isinstance(g3_row, dict) else None,
        "closing_track_downstream_caveats_resolved": track_caveats_resolved,
        "G4_closed": g4_closed,
        "caveats_cleared": caveats_cleared,
        "rule": sm_track.D3_RULE,
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
    claims = _claim_text(contract_ready, g3_closed=g3_closed)
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
        },
        "tiers": {
            "INTERNAL_CANDIDATE": "APPROVED" if internal_candidate else "WITHHELD",
            "CONDITIONAL_BENCHMARK": "WITHHELD",
            "FULL_PHENOMENOLOGY": "WITHHELD",
            "EMPIRICAL_REALIZATION": "NOT_ESTABLISHED",
            "WHOLE_MODEL_EXCLUSION": "NOT_ESTABLISHED",
        },
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
        "- Internal-candidate gate (D3): caveats_cleared = "
        + str(verdict.get("internal_candidate_gate", {}).get("caveats_cleared")),
        f"- Conditional benchmark: **{approval['conditional_benchmark']}**",
        f"- Full phenomenology: **{approval['full_phenomenology']}**",
        f"- Empirical realization: **{approval['empirical_realization']}**",
        f"- Whole-model exclusion: **{approval['whole_model_excluded']}**",
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
