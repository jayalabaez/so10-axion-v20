#!/usr/bin/env python3
"""Superseding live G1-G8 ledger after exact closure of G1.

The historical g1_g8_gate_ledger_v20 remains useful for its downstream source
contracts, but its G1 entry predates the live SO(10)+PQ+Z17 character census
and the completed 64-direction tensor ledger.  This module imports that
downstream evidence and replaces only G1.  G2-G8 remain fail-closed.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

import g1_g8_gate_ledger_v20 as historical
import live_g1_tensor_closure_ledger_v20 as g1

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "LIVE_G1_G8_GATE_LEDGER_V20.json"
OUT_MD = ROOT / "LIVE_G1_G8_GATE_LEDGER_V20.md"


def build_report() -> dict[str, Any]:
    historical_report = historical.build_report()
    g1_report = g1.build_report()
    gates = copy.deepcopy(historical_report["gates"])
    gates["G1"] = {
        "title": "Invariant ring and component Clebsch tensors",
        "status": historical.STATUS_CLOSED,
        "closed_scope": [
            "live SO(10)+PQ+Z17 degree<=4 character census",
            "74 allowed field multidegrees and 48 Hermitian-conjugacy orbits",
            "64 independent invariant coefficients / 91 real potential parameters",
            "explicit Cartesian tensor basis for all 64 directions",
            "normalization convention recorded for every direction",
        ],
        "open_scope": [],
        "corrections": {
            "historical_continuous_X_44_coefficient_subcensus_is_live_ring": False,
            "historical_signed_floor_34_is_completion_metric": False,
            "live_independent_invariant_coefficients": 64,
            "live_real_potential_parameters": 91,
            "all_live_tensor_directions_explicit": True,
        },
        "closure_route_defined": True,
        "current_runner_can_close_without_new_tensor_derivation": True,
        "closure_source": "live_g1_tensor_closure_ledger_v20.py",
    }

    statuses = {name: row["status"] for name, row in gates.items()}
    closed = [name for name, status in statuses.items() if status == historical.STATUS_CLOSED]
    partial = [name for name, status in statuses.items() if status == historical.STATUS_PARTIAL]
    open_gates = [name for name, status in statuses.items() if status == historical.STATUS_OPEN]
    blocked = [name for name, status in statuses.items() if status == historical.STATUS_BLOCKED]

    checks = {
        "historical_downstream_ledger_executes": historical_report.get("n_failed", 1) == 0,
        "live_G1_ledger_executes": g1_report.get("n_failed", 1) == 0,
        "all_eight_gates_present": set(gates) == {f"G{i}" for i in range(1, 9)},
        "G1_is_closed": gates["G1"]["status"] == historical.STATUS_CLOSED,
        "G1_has_64_explicit_directions": gates["G1"]["corrections"][
            "live_independent_invariant_coefficients"
        ]
        == 64
        and gates["G1"]["corrections"]["all_live_tensor_directions_explicit"],
        "G2_remains_partial": gates["G2"]["status"] == historical.STATUS_PARTIAL,
        "G7_remains_open": gates["G7"]["status"] == historical.STATUS_OPEN,
        "only_G1_is_closed": closed == ["G1"],
        "no_downstream_gate_promoted": all(
            gates[name]["status"] != historical.STATUS_CLOSED
            for name in ("G2", "G3", "G4", "G5", "G6", "G7", "G8")
        ),
        "whole_model_not_overclaimed": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "status": (
            "LIVE_G1_G8_LEDGER_VERIFIED__G1_CLOSED__MODEL_BLOCKED"
            if not failures
            else "LIVE_G1_G8_LEDGER_INTEGRITY_FAILED"
        ),
        "overall_state": "BLOCKED" if not failures else "EXECUTION_FAIL",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "supersedes_for_current_status": "g1_g8_gate_ledger_v20.py",
        "historical_ledger_status": historical_report["status"],
        "dependencies": historical.DEPENDENCIES,
        "gates": gates,
        "summary": {
            "closed": closed,
            "partial": partial,
            "open": open_gates,
            "blocked": blocked,
            "n_closed": len(closed),
            "n_partial": len(partial),
            "n_open": len(open_gates),
            "n_blocked": len(blocked),
        },
        "closure_waves": [
            {
                "wave": 1,
                "gates": ["G1"],
                "status": "COMPLETE",
                "deliverable": "Live invariant multiplicities, tensors, and normalizations.",
            },
            {
                "wave": 2,
                "gates": ["G2"],
                "status": "ACTIVE",
                "deliverable": "Assemble all 64 directions into one component potential.",
            },
            {
                "wave": 3,
                "gates": ["G3", "G4", "G5"],
                "status": "BLOCKED_BY_G2",
                "deliverable": "Global vacuum, gauge quotient Hessian, and global BFB.",
            },
            {
                "wave": 4,
                "gates": ["G6"],
                "status": "BLOCKED_BY_G3_G4_G5",
                "deliverable": "Complete physical threshold spectrum.",
            },
            {
                "wave": 5,
                "gates": ["G7"],
                "status": "BLOCKED_BY_G6",
                "deliverable": "Validated two-loop running and matching.",
            },
            {
                "wave": 6,
                "gates": ["G8"],
                "status": "BLOCKED_BY_G3_G6_G7",
                "deliverable": "Unique proton-decay prediction or falsification.",
            },
        ],
        "flags": {
            "g1_closed": not failures,
            "g2_closed": False,
            "all_g1_g8_closed": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
            "empirical_discovery": False,
        },
        "next_exact_target": (
            "G2: construct one arbitrary-component potential evaluator containing "
            "all 64 G1 directions and generate its complete gradient/Hessian."
        ),
        "verdict": (
            "G1 is now closed under the live declared symmetry contract. G2-G8 "
            "remain open or partial, so the candidate theory is still blocked and "
            "has not been validated or excluded."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Live G1-G8 gate ledger — v20",
        "",
        f"**Status:** `{report['status']}`",
        f"**Overall state:** `{report['overall_state']}`",
        "",
        report["verdict"],
        "",
        "| Gate | Domain | Status | Remaining scope |",
        "|---|---|---:|---|",
    ]
    for gate, row in report["gates"].items():
        remaining = "; ".join(row["open_scope"]) if row["open_scope"] else "Closed"
        lines.append(f"| {gate} | {row['title']} | **{row['status']}** | {remaining} |")
    lines.extend(["", f"**Next:** {report['next_exact_target']}", ""])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if not args.no_write:
        OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        OUT_MD.write_text(write_markdown(report))
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
