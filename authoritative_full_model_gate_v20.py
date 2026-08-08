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
import exact_x_symmetry_consistency_gate_v20 as x_contract_gate
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
    contract = x_contract_gate.build_report()
    ledger = gate_ledger.build_report()
    proton = proton_gate.build_report()
    legacy = _legacy_snapshot()

    execution_failures: list[str] = []
    if contract.get("n_failed", 1):
        execution_failures.extend(
            f"X contract audit: {item}"
            for item in contract.get("failures", ["failed"])
        )
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
    declared_contract_consistent = bool(
        contract.get("contract_consistent", False)
    )
    contract_evidence_complete = gate_ledger._root_contract_evidence_complete(
        contract
    )
    contract_consistent = bool(
        declared_contract_consistent and contract_evidence_complete
    )

    hard_theory_failures: list[str] = []
    # Conditional benchmark failures are deliberately not promoted here.
    all_gates_closed = not gates_not_closed
    full_model_validated = (
        not execution_failures
        and not hard_theory_failures
        and contract_consistent
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
    if not contract_consistent:
        blockers.extend(
            contract.get(
                "scientific_blockers",
                [x_contract_gate.EXTERNAL_EXECUTION_BLOCKER],
            )
        )
    blockers.extend(f"PROTON_READINESS_{name}" for name in readiness_open)

    checks = {
        "x_contract_audit_executes": contract.get("n_failed") == 0,
        "consistent_contract_has_tool_native_bound_evidence": bool(
            not declared_contract_consistent or contract_evidence_complete
        ),
        "contract_state_respected_by_validation": contract_consistent
        or not full_model_validated,
        "contract_and_ledger_agree": (
            ledger.get("contract_consistent") is contract_consistent
        ),
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

    verdict = (
        "The repository remains BLOCKED at full-model scope. The repaired gauged "
        "U(1)_X contract promotes G1 and G2, but G3-G8 and the unique proton-lifetime "
        "derivation are not closed. Historical Option-C calculations remain context "
        "only and cannot validate or exclude the gauged model."
        if contract_consistent
        else "The repository remains BLOCKED at full-model scope. The manuscript's "
        "gauged U(1)_X contract is implemented by a statically consistent, "
        "tool-native SARAH input and hash-bound validation bundle, but it has no "
        "valid v2 manifest/log-bound external execution attestation, "
        "so no downstream Option-C calculation is authoritative. The historical "
        "ultimate-gate internal-candidate approval is retained only as context; "
        "it cannot validate the model. Full approval requires every G1-G8 gate "
        "to close and the proton lifetime to be derived from the same physical "
        "vacuum and spectrum."
    )

    return {
        "status": "AUTHORITATIVE_FULL_MODEL_GATE_EXECUTED",
        "overall_state": overall_state,
        "n_checks": len(checks),
        "n_failed": len(execution_failures),
        "failures": execution_failures,
        "checks": checks,
        "hard_theory_failures": hard_theory_failures,
        "blockers": sorted(set(blockers)),
        "model_contract_id": "gauged_u1x_phi17_v20",
        "model_contract": {
            "declared_consistent": declared_contract_consistent,
            "tool_native_bound_evidence_complete": contract_evidence_complete,
            "consistent": contract_consistent,
            "status": contract.get("status"),
            "overall_state": contract.get("overall_state"),
            "conflicts": contract.get("contract_conflicts", []),
        },
        "g1_g8_summary": ledger.get("summary"),
        "g1_g8_status": ledger.get("status"),
        "proton_status": proton.get("status"),
        "proton_classification": proton.get("classification"),
        "legacy_ultimate_gate": legacy,
        "classification": {
            "all_g1_g8_closed": all_gates_closed,
            "authoritative_model_contract_consistent": contract_consistent,
            "tool_native_bound_model_evidence_complete": (
                contract_evidence_complete
            ),
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
            "authoritative_model_contract_consistent": contract_consistent,
            "tool_native_bound_model_evidence_complete": (
                contract_evidence_complete
            ),
            "whole_model_validated": full_model_validated,
            "whole_model_excluded": whole_model_excluded,
        },
        "verdict": verdict,
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
