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
import canonical_g1_g8_gauged_u1x_v21 as canonical_gates

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


def _canonical_evidence_complete(
    report: dict[str, Any], root: Path | None = None
) -> bool:
    """Validate V21 from live artifacts, never from injected summary booleans."""
    validation_root = canonical_gates.ROOT if root is None else Path(root)
    if not isinstance(report, dict):
        return False
    body = dict(report)
    integrity = body.pop("integrity", None)
    if not isinstance(integrity, dict) or integrity.get("core_sha256") != canonical_gates._sha(body):
        return False
    expected = {gate["qualified_gate_id"]: gate for gate in canonical_gates.GATES}
    rows = report.get("gates")
    if not isinstance(rows, list) or len(rows) != len(expected):
        return False
    observed: dict[str, dict[str, Any]] = {}
    closed: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            return False
        gate_id = row.get("qualified_gate_id")
        if gate_id not in expected or gate_id in observed:
            return False
        specification = expected[gate_id]
        if (
            row.get("definition_sha256") != canonical_gates.DEFINITION_SHA256
            or row.get("dependencies") != specification["dependencies"]
            or row.get("required_artifact") != specification["required_artifact"]
            or row.get("acceptance") != specification["acceptance"]
            or row.get("required_evidence_schema") != canonical_gates.EVIDENCE_SCHEMA
        ):
            return False
        evidence = row.get("evidence_state")
        if not isinstance(evidence, dict):
            return False
        # Re-run the canonical gate validator against repository bytes.  This
        # independently executes the definition-pinned gate-specific verifier
        # whenever one exists and prevents a recomputed report hash from making
        # forged ``evidence_state.valid`` booleans authoritative.
        live_evidence = canonical_gates.validate_gate_artifact(
            specification, validation_root
        )
        if evidence != live_evidence:
            return False
        dependencies_closed = all(item in closed for item in specification["dependencies"])
        gate_closed = bool(evidence.get("valid") is True and dependencies_closed)
        if row.get("dependencies_closed") is not dependencies_closed or row.get("closed") is not gate_closed:
            return False
        if gate_closed:
            closed.add(gate_id)
        observed[gate_id] = row
    counts = report.get("closure_counts")
    checks = report.get("checks")
    all_closed = len(closed) == len(expected)
    return bool(
        report.get("schema") == canonical_gates.SCHEMA
        and report.get("contract_namespace") == canonical_gates.CONTRACT_NAMESPACE
        and report.get("model_contract_id") == canonical_gates.MODEL_CONTRACT_ID
        and report.get("definition_sha256") == canonical_gates.DEFINITION_SHA256
        and set(observed) == set(expected)
        and counts == {"closed": len(closed), "open": len(expected) - len(closed)}
        and isinstance(checks, dict)
        and checks
        and all(value is True for value in checks.values())
        and type(report.get("n_failed")) is int
        and report.get("n_failed") == 0
        and report.get("failures") == []
        and report.get("overall_state") == ("PASS" if all_closed else "BLOCKED")
        and report.get("classification", {}).get("all_canonical_gates_closed") is all_closed
        and report.get("classification", {}).get("whole_model_validated") is all_closed
    )


def build_report() -> dict[str, Any]:
    contract = x_contract_gate.build_report()
    ledger = gate_ledger.build_report()
    canonical = canonical_gates.build_report()
    proton = proton_gate.build_report()
    legacy = _legacy_snapshot()

    execution_failures: list[str] = []
    # The X audit, legacy ledger and historical proton gate remain diagnostic
    # evidence.  They cannot approve *or veto* qualified V21 closure; every
    # canonical gate's trusted verifier must bind the relevant facts directly.
    diagnostic_failures: list[str] = []
    if contract.get("n_failed", 1):
        diagnostic_failures.extend(
            f"X contract audit: {item}"
            for item in contract.get("failures", ["failed"])
        )
    if ledger.get("n_failed", 1):
        diagnostic_failures.extend(
            f"legacy G1-G8 ledger: {item}"
            for item in ledger.get("failures", ["failed"])
        )
    canonical_evidence_complete = _canonical_evidence_complete(canonical)
    if not canonical_evidence_complete:
        execution_failures.append("canonical G1-G8 V21 contract integrity failed")
    elif canonical.get("n_failed", 1):
        execution_failures.extend(
            f"canonical G1-G8 V21: {item}"
            for item in canonical.get("failures", ["failed"])
        )
    if proton.get("n_failed", 1):
        diagnostic_failures.extend(
            f"proton gate: {item}" for item in proton.get("failures", ["failed"])
        )

    gates_not_closed = [
        row.get("qualified_gate_id", "UNKNOWN_CANONICAL_GATE")
        for row in canonical.get("gates", [])
        if row.get("closed") is not True
    ]
    readiness_open = [
        name
        for name, ready in proton.get("prediction_readiness", {}).items()
        if not ready
    ]
    canonical_g8 = next(
        (
            row
            for row in canonical.get("gates", [])
            if row.get("qualified_gate_id") == canonical_gates.G8_ID
        ),
        {},
    )
    exact_proton = bool(
        canonical_evidence_complete and canonical_g8.get("closed") is True
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
    all_gates_closed = bool(
        canonical_evidence_complete
        and not gates_not_closed
        and canonical.get("overall_state") == "PASS"
        and canonical.get("closure_counts") == {"closed": 8, "open": 0}
    )
    full_model_validated = (
        not execution_failures
        and not hard_theory_failures
        and all_gates_closed
        and exact_proton
    )
    # Historical proton classifications are diagnostic.  Canonical G8's
    # verifier owns the versioned all-channel comparison and any authoritative
    # exclusion result.
    whole_model_excluded = bool(hard_theory_failures)

    if execution_failures:
        overall_state = "EXECUTION_FAIL"
    elif whole_model_excluded:
        overall_state = "THEORY_FAIL"
    elif full_model_validated:
        overall_state = "PASS"
    else:
        overall_state = "BLOCKED"

    blockers = [f"CANONICAL_GATE_NOT_CLOSED::{gate}" for gate in gates_not_closed]
    canonical_g1 = next(
        (
            row
            for row in canonical.get("gates", [])
            if row.get("qualified_gate_id") == canonical_gates.G1_ID
        ),
        {},
    )
    if canonical_g1.get("closed") is not True:
        blockers.extend(
            contract.get(
                "scientific_blockers",
                [x_contract_gate.EXTERNAL_EXECUTION_BLOCKER],
            )
        )
    if not exact_proton:
        blockers.extend(f"PROTON_READINESS_{name}" for name in readiness_open)

    checks = {
        "legacy_diagnostics_do_not_control_authoritative_closure": True,
        "canonical_V21_executes_and_has_valid_integrity": canonical_evidence_complete,
        "legacy_ledger_does_not_control_authoritative_closure": True,
        # Execution of the historical proton report is recorded below as
        # diagnostic evidence.  It cannot approve or veto the qualified V21
        # G8 verifier, so this authoritative invariant is about the boundary,
        # not the legacy report's current execution result.
        "legacy_proton_gate_does_not_control_authoritative_closure": True,
        "legacy_ultimate_not_authoritative": not legacy.get(
            "authoritative_for_full_model", True
        ),
        # A historical candidate flag can coexist with, but can never cause or
        # veto, qualified canonical closure.  Authority is established only by
        # the live V21 verifier replay above.
        "legacy_internal_candidate_does_not_control_authoritative_closure": True,
        "legacy_proton_result_is_diagnostic_only": True,
    }
    failed_checks = [name for name, ok in checks.items() if not ok]
    if failed_checks and not execution_failures:
        execution_failures.extend(f"gate check: {name}" for name in failed_checks)
        overall_state = "EXECUTION_FAIL"
        full_model_validated = False

    verdict = (
        "The repository satisfies the qualified canonical gauged-U(1)_X V21 "
        "contract: all eight evidence-bound gates, including the propagated "
        "proton-lifetime distribution, are closed."
        if full_model_validated
        else "The repository remains BLOCKED at full-model scope. The repaired gauged "
        "U(1)_X execution contract is valid, but one or more qualified canonical "
        "V21 phenomenology gates remain open. Historical scalar-ledger gate numbers "
        "are evidence only and cannot validate or exclude the gauged model."
        if contract_consistent
        else "The repository remains BLOCKED at full-model scope. The manuscript's "
        "gauged U(1)_X contract is implemented by a statically consistent, "
        "tool-native SARAH input and hash-bound validation bundle, but it has no "
        "valid v3 source-tree/runtime/log-bound external execution "
        "attestation, "
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
        "canonical_g1_g8": canonical,
        "canonical_g1_g8_summary": canonical.get("closure_counts"),
        "canonical_g1_g8_status": canonical.get("status"),
        "legacy_g1_g8_evidence": {
            "status": ledger.get("status"),
            "summary": ledger.get("summary"),
            "authoritative_for_closure": False,
            "diagnostic_failures": diagnostic_failures,
        },
        "proton_status": proton.get("status"),
        "proton_classification": proton.get("classification"),
        "legacy_ultimate_gate": legacy,
        "classification": {
            "all_g1_g8_closed": all_gates_closed,
            "authoritative_model_contract_consistent": bool(
                contract_consistent or canonical_g1.get("closed") is True
            ),
            "tool_native_bound_model_evidence_complete": bool(
                contract_evidence_complete or canonical_g1.get("closed") is True
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
            "legacy_ledger_controls_authoritative_closure": False,
            "internal_candidate_approval_is_not_full_model_validation": True,
            "conditional_benchmarks_are_not_discovery": True,
            "authoritative_model_contract_consistent": bool(
                contract_consistent or canonical_g1.get("closed") is True
            ),
            "tool_native_bound_model_evidence_complete": bool(
                contract_evidence_complete or canonical_g1.get("closed") is True
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
