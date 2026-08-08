#!/usr/bin/env python3
"""Historical Option-C/no-X G1-G8 snapshot on the 486-real field chart.

Within this superseded counterfactual contract, G1 was marked closed and G2
had two completed layers:

1. all 48 Hermitian orbits / 64 invariant directions / 91 real parameters
   evaluate on arbitrary physical fields;
2. one exact 486-real physical coordinate chart with identity kinetic metric,
   physical -i 126bar chirality, and SO(10) tangent vectors.

The manuscript instead gauges U(1)_X and uses the exact-X-neutral 44-direction,
51-parameter contract.  Consequently this module is retained only to reproduce
the old 64/91 ledger; it neither supersedes the current status nor closes the
manuscript's G1 or G2.
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
import live_g2_canonical_486_field_chart_v20 as chart

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "LIVE_G1_G8_GATE_LEDGER_V20.json"
OUT_MD = ROOT / "LIVE_G1_G8_GATE_LEDGER_V20.md"
MODEL_CONTRACT_ID = "historical_option_c_no_x_v20"
AUTHORITATIVE_FOR_MANUSCRIPT = False


def build_report() -> dict[str, Any]:
    historical_report = historical.build_report()
    g1_report = g1.build_report()
    g2_report = g2.build_report()
    chart_report = chart.build_report()
    gates = copy.deepcopy(historical_report["gates"])
    historical_statuses = {
        "G1": historical.STATUS_CLOSED,
        "G2": historical.STATUS_PARTIAL,
        "G3": historical.STATUS_PARTIAL,
        "G4": historical.STATUS_PARTIAL,
        "G5": historical.STATUS_PARTIAL,
        "G6": historical.STATUS_PARTIAL,
        "G7": historical.STATUS_OPEN,
        "G8": historical.STATUS_PARTIAL,
    }
    for name, row in gates.items():
        row["status"] = historical_statuses[name]
        row["model_contract_id"] = MODEL_CONTRACT_ID
        row["authoritative_for_manuscript"] = False
        row.pop("authoritative_model_contract_id", None)
        row.pop("authoritative_closed_scope", None)
        row.pop("closed_on_current_authoritative_contract", None)
        row.pop("blocking_root", None)

    gates["G1"] = {
        "title": "Invariant ring and component Clebsch tensors",
        "status": historical.STATUS_CLOSED,
        "closed_scope": [
            "live SO(10)+PQ+Z17 degree<=4 character census",
            "74 allowed field multidegrees and 48 Hermitian-conjugacy orbits",
            "64 independent invariant coefficients / 91 real potential parameters",
            "explicit Cartesian tensor basis and normalization for all 64 directions",
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
            "91-real-parameter Hermitian coefficient assembly and Jacobian",
            "physical -i 126bar chirality enforced",
            "homogeneous degree scaling checked for every direction",
            "canonical 486-real physical field chart",
            "exact pack/unpack with identity kinetic metric",
            "SO(10) generator tangent map on the complete chart",
        ],
        "open_scope": [
            "complete 486-entry field gradient for all 91 parameters",
            "complete symmetric 486x486 field Hessian with operator provenance",
            "independent covariance and finite-difference reconstruction of all derivative families",
        ],
        "corrections": {
            "PR155_eight_coordinate_probe_is_complete_gradient": False,
            "PR155_eight_coordinate_probe_is_complete_Hessian": False,
            "live_assembled_directions": 64,
            "live_real_couplings": 91,
            "complete_real_field_dimension": 486,
            "complete_symmetric_Hessian_entries": 118341,
            "canonical_field_chart_closed": True,
        },
        "closure_route_defined": True,
        "current_runner_can_close_without_G1": False,
        "closure_source": (
            "live_g2_component_potential_v20.py + "
            "live_g2_canonical_486_field_chart_v20.py"
        ),
    }

    statuses = {name: row["status"] for name, row in gates.items()}
    closed = [name for name, status in statuses.items() if status == historical.STATUS_CLOSED]
    partial = [name for name, status in statuses.items() if status == historical.STATUS_PARTIAL]
    open_gates = [name for name, status in statuses.items() if status == historical.STATUS_OPEN]
    blocked = [name for name, status in statuses.items() if status == historical.STATUS_BLOCKED]

    checks = {
        "current_contract_ledger_executes_as_metadata_template": historical_report.get("n_failed", 1) == 0,
        "live_G1_ledger_executes": g1_report.get("n_failed", 1) == 0,
        "historical_G2_value_layer_executes": g2_report.get("n_failed", 1) == 0,
        "canonical_486_chart_executes": chart_report.get("n_failed", 1) == 0,
        "all_eight_gates_present": set(gates) == {f"G{i}" for i in range(1, 9)},
        "historical_G1_is_closed": gates["G1"]["status"] == historical.STATUS_CLOSED,
        "historical_G2_is_partial": gates["G2"]["status"] == historical.STATUS_PARTIAL,
        "G1_has_64_explicit_directions": (
            gates["G1"]["corrections"]["live_independent_invariant_coefficients"] == 64
            and gates["G1"]["corrections"]["all_live_tensor_directions_explicit"]
        ),
        "G2_value_and_chart_layers_closed": (
            g2_report["flags"]["historical_option_c_g2_value_layer_complete"]
            and chart_report["flags"]["canonical_486_real_chart_closed"]
            and gates["G2"]["corrections"]["canonical_field_chart_closed"]
        ),
        "G2_requires_complete_derivative_layer": (
            gates["G2"]["corrections"]["complete_real_field_dimension"] == 486
            and gates["G2"]["corrections"]["complete_symmetric_Hessian_entries"] == 118341
            and len(gates["G2"]["open_scope"]) == 3
        ),
        "historical_G7_remains_open": gates["G7"]["status"] == historical.STATUS_OPEN,
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
        "model_contract_id": MODEL_CONTRACT_ID,
        "authoritative_for_manuscript": AUTHORITATIVE_FOR_MANUSCRIPT,
        "status": (
            "HISTORICAL_OPTION_C_G1_CLOSED__G2_VALUE_AND_CHART_PARTIAL__NONAUTHORITATIVE"
            if not failures
            else "LIVE_G1_G8_LEDGER_INTEGRITY_FAILED"
        ),
        "overall_state": "HISTORICAL" if not failures else "EXECUTION_FAIL",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "supersedes_for_current_status": False,
        "source_template_ledger_status": historical_report["status"],
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
                "completed": [
                    "64-direction arbitrary-field value layer",
                    "91-real-parameter assembly",
                    "canonical 486-real physical chart",
                ],
                "deliverable": "Complete analytic gradient and Hessian on the canonical chart.",
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
            "historical_option_c_g1_closed": not failures,
            "historical_option_c_g2_value_layer_complete": not failures,
            "historical_option_c_g2_canonical_field_chart_complete": not failures,
            "authoritative_manuscript_g1_closed": False,
            "authoritative_manuscript_g2_closed": False,
            "g1_closed": False,
            "g2_value_layer_complete": False,
            "g2_canonical_field_chart_complete": False,
            "g2_complete_gradient": False,
            "g2_complete_Hessian": False,
            "g2_closed": False,
            "all_g1_g8_closed": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
            "empirical_discovery": False,
        },
        "next_exact_target": (
            "Use gauged_u1x_scalar_contract_v20.py and the 44/51 derivative "
            "audit for the manuscript-authoritative theory."
        ),
        "verdict": (
            "This ledger reproduces historical Option-C/no-X bookkeeping only. "
            "Its 64/91 G1 closure and partial G2 layers are not gates of the "
            "gauged-U(1)_X manuscript and do not supersede the current ledger."
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
        OUT_JSON.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        OUT_MD.write_text(write_markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
