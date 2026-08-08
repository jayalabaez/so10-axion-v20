#!/usr/bin/env python3
"""Ultimate fail-closed gate for the authoritative SO(10) axion model.

The gate consumes the fresh contract-aware confirmation layer.  It does not
load the historical release verdict stack, so an old Option-C approval cannot
override the manuscript/executable U(1)_X mismatch.
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
        "verdict": (
            "WITHHOLD APPROVAL. The audit has no execution failure, but the "
            "statically consistent, tool-native gauged-U(1)_X model has no v2 "
            "manifest/log-bound external SARAH execution evidence. "
            "No internal-candidate, conditional-benchmark, full-phenomenology, "
            "empirical-realization, or whole-model-exclusion claim is approved."
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
        f"- Conditional benchmark: **{report['conditional_benchmark_approved']}**",
        f"- Full phenomenology: **{report['full_phenomenology_approved']}**",
        f"- Empirical realization: **{report['empirical_realization_approved']}**",
        f"- Whole-model exclusion: **{report['whole_model_excluded']}**",
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
) -> int:
    """Return zero for an honest BLOCKED audit, nonzero for strict approval."""
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
    )


if __name__ == "__main__":
    raise SystemExit(main())
