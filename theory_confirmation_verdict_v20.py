#!/usr/bin/env python3
"""Fail-closed theory-confirmation verdict for SO(10) axion v20.

The authoritative manuscript gauges ``U(1)_X``.  This verdict is assembled
from fresh builders.  Qualified canonical V21 evidence is the sole G1--G8
closure authority; stale Option-C and scalar-ledger rows remain diagnostic
evidence and cannot approve or veto the model.
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
import gauged_u1x_scalar_contract_v20 as gauged_contract
import theory_validation_matrix_v20 as validation_matrix
import canonical_g1_g8_gauged_u1x_v21 as canonical_gates

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "THEORY_CONFIRMATION_VERDICT.json"
OUT_MD = ROOT / "THEORY_CONFIRMATION_VERDICT.md"

CANONICAL_GATES_OPEN = "CANONICAL_G1_G8_GATES_OPEN"
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
    "canonical",
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
        "canonical": canonical_gates.build_report(),
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


def evaluate_reports(
    reports: dict[str, dict[str, Any]],
    *,
    current_test_count: int | None = None,
    attestation: dict[str, Any] | None = None,
    preload_errors: list[str] | None = None,
) -> dict[str, Any]:
    """Evaluate fresh reports against the qualified canonical V21 state."""
    errors = _execution_errors(reports, preload_errors)
    x_report = reports.get("x_contract", {})
    gauged_report = reports.get("gauged_contract", {})
    ledger = reports.get("g1_g8", {})
    canonical = reports.get("canonical", {})
    authoritative = reports.get("authoritative", {})

    matrix_contract_gate = validation_matrix._model_contract_gate(
        {
            "x_contract": x_report,
            "gauged_contract": gauged_report,
        }
    )
    canonical_integrity = authoritative_gate._canonical_evidence_complete(
        canonical
    )
    if not canonical_integrity:
        errors.append("canonical G1-G8 V21 contract integrity failed")
    canonical_rows = (
        canonical.get("gates", []) if isinstance(canonical, dict) else []
    )
    gates_by_number = {
        row.get("gate_number"): row
        for row in canonical_rows
        if isinstance(row, dict)
    }
    first_three_closed = all(
        gates_by_number.get(number, {}).get("closed") is True
        for number in (1, 2, 3)
    )
    canonical_root_closed = gates_by_number.get(1, {}).get("closed") is True
    all_eight_closed = bool(
        canonical_integrity
        and canonical.get("closure_counts") == {"closed": 8, "open": 0}
        and canonical.get("overall_state") == "PASS"
        and all(
            gates_by_number.get(number, {}).get("closed") is True
            for number in range(1, 9)
        )
    )

    authoritative_classification = authoritative.get("classification", {})
    if not isinstance(authoritative_classification, dict):
        errors.append("authoritative classification is not a JSON object")
        authoritative_classification = {}

    authoritative_consistent = bool(
        authoritative.get("canonical_g1_g8") == canonical
        and authoritative.get("canonical_g1_g8_summary")
        == canonical.get("closure_counts")
        and authoritative_classification.get("all_g1_g8_closed")
        is all_eight_closed
        and authoritative_classification.get("whole_model_validated")
        is all_eight_closed
        and authoritative.get("flag", {}).get(
            "legacy_ledger_controls_authoritative_closure"
        )
        is False
        and authoritative.get("legacy_g1_g8_evidence", {}).get(
            "authoritative_for_closure"
        )
        is False
    )
    if canonical_integrity and not authoritative_consistent:
        errors.append(
            "authoritative full-model report disagrees with canonical V21 state"
        )
    contract_ready = bool(
        canonical_integrity
        and authoritative_consistent
        and canonical_root_closed
    )
    internal_candidate = bool(first_three_closed and contract_ready and not errors)
    # Historical aligned benchmarks remain evidence, not closure authority.
    conditional_benchmark = False
    full_phenomenology = bool(
        contract_ready
        and all_eight_closed
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
        overall_state = "BLOCKED"
        classification = CANONICAL_GATES_OPEN
        decision = WITHHOLD_APPROVAL
        status = "THEORY_CONFIRMATION_AUDIT_COMPLETE__CANONICAL_GATES_OPEN"

    scientific_blockers: list[str] = [
        f"CANONICAL_GATE_NOT_CLOSED::{row.get('qualified_gate_id')}"
        for row in canonical_rows
        if row.get("closed") is not True
    ]
    for source in (x_report, authoritative):
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
        "canonical_G1_G8_V21": canonical,
        "canonical_authoritative_consistency": {
            "canonical_integrity_valid": canonical_integrity,
            "authoritative_report_matches_canonical_state": (
                authoritative_consistent
            ),
            "legacy_ledger_controls_authoritative_closure": False,
        },
        "scientific_blockers": scientific_blockers,
        "historical_option_c_subtheorems": historical,
        "scope": {
            "authoritative_current_model": "gauged_u1x_phi17_v20",
            "historical_option_c_is_authoritative": False,
            "historical_results_may_close_current_gates": False,
            "historical_results_may_veto_current_gates": False,
            "canonical_V21_controls_full_authoritative_closure": True,
            "software_pass_implies_scientific_approval": False,
        },
        "tiers": {
            "INTERNAL_CANDIDATE": "APPROVED" if internal_candidate else "WITHHELD",
            "CONDITIONAL_BENCHMARK": "WITHHELD",
            "FULL_PHENOMENOLOGY": "APPROVED" if full_phenomenology else "WITHHELD",
            "EMPIRICAL_REALIZATION": "ESTABLISHED" if empirical_realization else "NOT_ESTABLISHED",
            "WHOLE_MODEL_EXCLUSION": "ESTABLISHED" if whole_model_excluded else "NOT_ESTABLISHED",
        },
        "correct_public_claim": (
            "All eight qualified canonical gauged-U(1)_X V21 gates are closed "
            "with evidence-bound artifacts; full phenomenology is validated "
            "without implying empirical discovery."
            if full_phenomenology
            else "Qualified canonical gauged-U(1)_X V21 evidence remains open; "
            "full approval is withheld. Historical Option-C and scalar-ledger "
            "gate numbers are scoped evidence and neither promote nor veto the "
            "canonical state."
        ),
        "incorrect_claim_do_not_use": (
            "Bare legacy G1-G8 status labels determine closure for the qualified "
            "canonical gauged-U(1)_X V21 model."
        ),
        "verdict": (
            "VALIDATE FULL PHENOMENOLOGY. Every qualified canonical V21 gate is "
            "closed and the authoritative report agrees exactly."
            if full_phenomenology
            else "WITHHOLD APPROVAL. One or more qualified canonical V21 gates "
            "remain open, or the authoritative summary is not yet consistent."
        ),
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
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-internal-approval", action="store_true")
    parser.add_argument("--require-full-approval", action="store_true")
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
    )


if __name__ == "__main__":
    raise SystemExit(main())
