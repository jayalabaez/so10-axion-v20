#!/usr/bin/env python3
"""Canonical repository-level full-model gate for SO(10) axion v20.

The historical ``ultimate_theory_gate_v20`` checks an older artifact stack and
may approve an internal candidate.  That approval is not full-model validation.
This gate makes the corrected G1–G8 ledger and proton-decay falsification gate
the authoritative prerequisites for any whole-model claim.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import g1_g8_gate_ledger_v20 as gate_ledger
import proton_decay_falsification_gate_v20 as proton_gate

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "AUTHORITATIVE_FULL_MODEL_GATE_V20.json"
OUT_MD = ROOT / "AUTHORITATIVE_FULL_MODEL_GATE_V20.md"
LEGACY_ULTIMATE = ROOT / "ULTIMATE_THEORY_GATE_V20_VERDICT.json"


def _legacy_snapshot() -> dict[str, Any]:
    if not LEGACY_ULTIMATE.exists():
        return {"available": False, "authoritative_for_full_model": False}
    try:
        report = json.loads(LEGACY_ULTIMATE.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "available": True,
            "parse_error": str(exc),
            "authoritative_for_full_model": False,
        }
    return {
        "available": True,
        "status": report.get("status"),
        "decision": report.get("decision"),
        "internal_candidate_approved": report.get("internal_candidate_approved"),
        "full_phenomenology_approved": report.get("full_phenomenology_approved"),
        "empirical_realization_approved": report.get("empirical_realization_approved"),
        "authoritative_for_full_model": False,
        "reason": (
            "The historical gate does not consume the corrected G1–G8 dependency "
            "ledger, signed scalar-spectrum invalidation, or PR #105 proton gate."
        ),
    }


def build_report() -> dict[str, Any]:
    ledger = gate_ledger.build_report()
    proton = proton_gate.build_report()
    legacy = _legacy_snapshot()

    execution_failures: list[str] = []
    if ledger.get("n_failed", 1):
        execution_failures.extend(
            f"G1-G8 ledger: {item}" for item in ledger.get("failures", ["failed"])
        )
    if proton.get("n_failed", 1):
        execution_failures.extend(
            f"proton gate: {item}" for item in proton.get("failures", ["failed"])
        )

    gates_not_closed = [
        gate
        for gate, row in ledger.get("gates", {}).items()
        if row.get("status") != gate_ledger.STATUS_CLOSED
    ]
    readiness_open = [
        name
        for name, ready in proton.get("prediction_readiness", {}).items()
        if not ready
    ]
    exact_proton = bool(
        proton.get("classification", {}).get(
            "exact_unique_proton_lifetime_derived", False
        )
    )
    proton_observed = bool(
        proton.get("classification", {}).get("proton_decay_observed", False)
    )
    proton_excludes_model = bool(
        proton.get("classification", {}).get(
            "whole_model_excluded_by_proton_decay", False
        )
    )

    hard_theory_failures: list[str] = []
    # Conditional benchmark failures are deliberately not promoted here.
    all_gates_closed = not gates_not_closed
    full_model_validated = (
        not execution_failures
        and not hard_theory_failures
        and all_gates_closed
        and exact_proton
    )
    whole_model_excluded = bool(hard_theory_failures or proton_excludes_model)

    if execution_failures:
        overall_state = "EXECUTION_FAIL"
    elif whole_model_excluded:
        overall_state = "THEORY_FAIL"
    elif full_model_validated:
        overall_state = "PASS"
    else:
        overall_state = "BLOCKED"

    blockers = [f"{gate}_NOT_CLOSED" for gate in gates_not_closed]
    blockers.extend(f"PROTON_READINESS_{name}" for name in readiness_open)

    checks = {
        "ledger_executes": ledger.get("n_failed") == 0,
        "proton_gate_executes": proton.get("n_failed") == 0,
        "legacy_ultimate_not_authoritative": not legacy.get(
            "authoritative_for_full_model", True
        ),
        "internal_candidate_not_promoted_to_full_validation": not (
            legacy.get("internal_candidate_approved") and full_model_validated
        ),
        "conditional_proton_points_not_promoted_to_model_exclusion": not proton_excludes_model,
        "no_discovery_claim": not proton_observed,
    }
    failed_checks = [name for name, ok in checks.items() if not ok]
    if failed_checks and not execution_failures:
        execution_failures.extend(f"gate check: {name}" for name in failed_checks)
        overall_state = "EXECUTION_FAIL"
        full_model_validated = False

    return {
        "status": "AUTHORITATIVE_FULL_MODEL_GATE_EXECUTED",
        "overall_state": overall_state,
        "n_checks": len(checks),
        "n_failed": len(execution_failures),
        "failures": execution_failures,
        "checks": checks,
        "hard_theory_failures": hard_theory_failures,
        "blockers": sorted(set(blockers)),
        "g1_g8_summary": ledger.get("summary"),
        "g1_g8_status": ledger.get("status"),
        "proton_status": proton.get("status"),
        "proton_classification": proton.get("classification"),
        "legacy_ultimate_gate": legacy,
        "classification": {
            "all_g1_g8_closed": all_gates_closed,
            "exact_unique_proton_lifetime": exact_proton,
            "proton_decay_observed": proton_observed,
            "whole_model_validated": full_model_validated,
            "whole_model_excluded": whole_model_excluded,
            "empirical_discovery": full_model_validated and proton_observed,
        },
        "flag": {
            "authoritative_full_model_gate": True,
            "legacy_ultimate_gate_authoritative": False,
            "internal_candidate_approval_is_not_full_model_validation": True,
            "conditional_benchmarks_are_not_discovery": True,
            "whole_model_validated": full_model_validated,
            "whole_model_excluded": whole_model_excluded,
        },
        "verdict": (
            "The repository remains BLOCKED at full-model scope. The historical "
            "ultimate-gate internal-candidate approval is retained only as context; "
            "it cannot validate the model. Full approval requires every G1–G8 gate "
            "to close and the proton lifetime to be derived from the same physical "
            "vacuum and spectrum."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Authoritative full-model gate — v20",
        "",
        f"**Overall state:** `{report['overall_state']}`",
        "",
        report["verdict"],
        "",
        "## Classification",
        "",
    ]
    for key, value in report["classification"].items():
        lines.append(f"- `{key}`: {value}")
    lines.extend(["", "## Blockers", ""])
    lines.extend(f"- `{item}`" for item in report["blockers"] or ["None"])
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-pass", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(write_markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2))
    if report["n_failed"]:
        return 1
    if args.require_pass and report["overall_state"] != "PASS":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
