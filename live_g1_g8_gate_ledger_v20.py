#!/usr/bin/env python3
"""Superseding live G1-G8 ledger after the G2 component audit.

G1 remains closed under the exact live SO(10)+PQ+Z17 census and 64-direction
tensor ledger.  The merged PR #155 G2 closure is withdrawn: its numerical
assembler contained chiral/normalization defects and only differentiated an
eight-coordinate species probe, not the complete 486-real scalar field space.

The corrected G2 value layer compiles all 64 directions and 91 real
parameters, but the complete physical-field gradient and Hessian remain open.
Therefore G2 is PARTIAL and all downstream gates remain fail-closed.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

import g1_g8_gate_ledger_v20 as historical
import live_g1_tensor_closure_ledger_v20 as g1
import live_g2_component_potential_v20 as g2

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "LIVE_G1_G8_GATE_LEDGER_V20.json"
OUT_MD = ROOT / "LIVE_G1_G8_GATE_LEDGER_V20.md"


def build_report() -> dict[str, Any]:
    historical_report = historical.build_report()
    g1_report = g1.build_report()
    g2_report = g2.build_report()
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
            "historical_continuous_X_subcensus_is_live_ring": False,
            "live_independent_invariant_coefficients": 64,
            "live_real_potential_parameters": 91,
            "all_live_tensor_directions_explicit": True,
        },
        "closure_route_defined": True,
        "current_runner_can_close_without_new_tensor_derivation": True,
        "closure_source": "live_g1_tensor_closure_ledger_v20.py",
    }
    gates["G2"] = {
        "title": "Fully projected non-SUSY component potential",
        "status": historical.STATUS_PARTIAL,
        "closed_scope": [
            "all 48 Hermitian orbits compiled",
            "all 64 normalized invariant values callable on arbitrary fields",
            "91-real-parameter Hermitian coefficient assembly",
            "operator provenance and exact coefficient Jacobian",
            "physical -i 126bar chirality enforced",
            "homogeneous degree scaling checked for every direction",
        ],
        "open_scope": [
            "one canonical 486-real field-coordinate chart",
            "complete 486-entry field gradient for all 91 parameters",
            "complete symmetric 486x486 field Hessian with operator provenance",
            "independent covariance and finite-difference reconstruction on the physical chiral subspace",
        ],
        "corrections": {
            "PR155_eight_coordinate_probe_is_complete_gradient": False,
            "PR155_eight_coordinate_probe_is_complete_Hessian": False,
            "live_assembled_directions": 64,
            "live_real_couplings": 91,
            "complete_real_field_dimension": 486,
            "complete_symmetric_Hessian_entries": 486 * 487 // 2,
        },
        "closure_route_defined": True,
        "current_runner_can_close_without_G1": False,
        "closure_source": "live_g2_component_potential_v20.py",
    }

    statuses = {name: row["status"] for name, row in gates.items()}
    closed = [name for name, status in statuses.items() if status == historical.STATUS_CLOSED]
    partial = [name for name, status in statuses.items() if status == historical.STATUS_PARTIAL]
    open_gates = [name for name, status in statuses.items() if status == historical.STATUS_OPEN]
    blocked = [name for name, status in statuses.items() if status == historical.STATUS_BLOCKED]

    checks = {
        "historical_downstream_ledger_executes": historical_report.get("n_failed", 1) == 0,
        "live_G1_ledger_executes": g1_report.get("n_failed", 1) == 0,
        "corrected_G2_value_layer_executes": g2_report.get("n_failed", 1) == 0,
        "all_eight_gates_present": set(gates) == {f"G{i}" for i in range(1, 9)},
        "G1_is_closed": gates["G1"]["status"] == historical.STATUS_CLOSED,
        "G2_is_partial": gates["G2"]["status"] == historical.STATUS_PARTIAL,
        "G1_has_64_explicit_directions": gates["G1"]["corrections"][
            "live_independent_invariant_coefficients"
        ]
        == 64
        and gates["G1"]["corrections"]["all_live_tensor_directions_explicit"],
        "G2_requires_complete_486_real_differentiation": (
            gates["G2"]["corrections"]["complete_real_field_dimension"] == 486
            and len(gates["G2"]["open_scope"]) == 4
        ),
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
            "LIVE_G1_G8_LEDGER_CORRECTED__ONLY_G1_CLOSED__MODEL_BLOCKED"
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
                "status": "ACTIVE_PARTIAL",
                "deliverable": "Complete 486-real field gradient and Hessian for the assembled 64-direction potential.",
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
            "g2_value_layer_complete": not failures,
            "g2_closed": False,
            "all_g1_g8_closed": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
            "empirical_discovery": False,
        },
        "next_exact_target": (
            "G2: construct the canonical 486-real field vector and emit the "
            "complete gradient and Hessian of the corrected 91-parameter potential."
        ),
        "verdict": (
            "Only G1 is closed. The corrected G2 arbitrary-field value layer "
            "is complete, but G2 remains PARTIAL until the full 486-real "
            "gradient and Hessian are constructed inside the physical chiral "
            "field space. G3-G8 remain open or partial."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Corrected live G1-G8 gate ledger — v20",
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
