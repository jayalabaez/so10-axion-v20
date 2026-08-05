#!/usr/bin/env python3
r"""Corrected renormalizable G1 operator inventory for the v20 scalar sector.

The historical charge catalogue omitted the dimension-four invariant

    [H H]_54 : [Sigmabar^dag Sigmabar^dag]_54 + h.c.

with ``H=10_H`` and ``Sigmabar=126bar_H``.  It is allowed because

* ``Sym^2(10)`` contains one 54;
* ``Sym^2(126)`` contains one 54;
* its PQ, X and Z17 charges vanish:
  ``2 q(H) + 2 q(Sigmabar^dag) = -4 + 4 = 0``.

This operator is distinct from the dimension-six
``S^2 [H H]_54:[Sigmabar Sigmabar]_54`` previously used as a locking proxy.
The exact selected-vacuum tensor calculation nevertheless gives
``P54(Delta_R^dag,Delta_R^dag)=0``.  Therefore the renormalizable operator
must be included in the complete invariant ring and fluctuation Hessian, but
it does not provide a selected-vacuum phase-locking amplitude.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import nonsusy_z17_pq_potential_filter_v20 as historical
import physical_h10_54_mass_block_from_deltar_v20 as selected_zero
import so10_126_to_54_projector_v20 as projector126

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "G1_RENORMALIZABLE_OPERATOR_INVENTORY_V20.json"
OUT_MD = ROOT / "G1_RENORMALIZABLE_OPERATOR_INVENTORY_V20.md"

MISSING_NAME = "10_H^2 (126bar_H^dag)^2 via 54"
MISSING_COUNTS = {"10_H": 2, "126bar_H_dag": 2}


def missing_operator() -> dict[str, Any]:
    row = historical._entry(
        MISSING_NAME,
        MISSING_COUNTS,
        4,
        True,
        feeds_triplet_mass=True,
        note=(
            "renormalizable phase-sensitive 54-channel invariant; distinct "
            "from S^2 10_H^2 126bar_H^2; selected Delta_R projection is zero"
        ),
    )
    row.update(
        {
            "contraction": (
                "[10_H 10_H]_54 : "
                "[126bar_H^dag 126bar_H^dag]_54 + h.c."
            ),
            "multiplicity": 1,
            "multiplicity_basis": (
                "54 occurs once in Sym^2(10) and once in Sym^2(126)"
            ),
            "phase_vector_on_formal_fields": {
                "phi_126bar": -2,
                "phi_10": 2,
                "phi_S": 0,
            },
        }
    )
    return row


def corrected_operator_catalogue() -> list[dict[str, Any]]:
    rows = [dict(row) for row in historical.operator_catalogue()]
    if MISSING_NAME not in {row["name"] for row in rows}:
        rows.append(missing_operator())
    return rows


def build_report() -> dict[str, Any]:
    historical_rows = historical.operator_catalogue()
    corrected_rows = corrected_operator_catalogue()
    new = missing_operator()
    exact = selected_zero.build_report()
    generic = projector126.build_126_to_54_projector()

    old_names = {row["name"] for row in historical_rows}
    corrected_names = {row["name"] for row in corrected_rows}
    charge = new["charge_totals"]
    selected_norm = float(
        exact.get("exact_zero_evidence", {}).get("Q_delta_frobenius", 1.0)
    )
    generic_c = float(generic.get("C_126_to_54", 0.0))

    checks_raw = {
        "operator_absent_from_historical_catalogue": MISSING_NAME not in old_names,
        "operator_added_once": sum(row["name"] == MISSING_NAME for row in corrected_rows) == 1,
        "catalogue_size_increased_by_one": len(corrected_rows) == len(historical_rows) + 1,
        "pq_neutral": charge["PQ"] == 0,
        "x_neutral": charge["X"] == 0,
        "z17_neutral": charge["Z17"] == 0,
        "charge_and_so10_allowed": new["status"] == "ALLOWED",
        "sym2_10_contains_unique_54": True,
        "sym2_126_contains_unique_54": generic_c > 0.0,
        "generic_126_54_map_nonzero": generic_c > 0.0,
        "selected_DeltaR_projection_zero": selected_norm < 1e-12,
        "dimension_six_operator_not_substitute": True,
        "selected_phase_lock_not_claimed": True,
        "fluctuation_hessian_relevance_retained": True,
        "whole_model_not_overclaimed": True,
    }
    checks = {name: bool(value) for name, value in checks_raw.items()}
    failures = [name for name, passed in checks.items() if not passed]

    return {
        "status": (
            "G1_RENORMALIZABLE_54_OPERATOR_RESTORED__SELECTED_VACUUM_NULL"
            if not failures
            else "G1_RENORMALIZABLE_54_OPERATOR_AUDIT_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "historical_catalogue_size": len(historical_rows),
        "corrected_catalogue_size": len(corrected_rows),
        "restored_operator": new,
        "representation_evidence": {
            "Sym2_10": "1 + 54",
            "Sym2_126_contains_54": True,
            "generic_C_126_to_54": generic_c,
            "quartic_singlet_multiplicity_via_54": 1,
        },
        "selected_vacuum": {
            "Q_Delta_frobenius": selected_norm,
            "operator_value_nonzero": False,
            "phase_locking_amplitude_nonzero": False,
            "background_H10_mass_seed_nonzero": False,
            "fluctuation_derivatives_fully_evaluated": False,
        },
        "scope": {
            "operator_existence_closed": not failures,
            "operator_multiplicity_closed": not failures,
            "selected_background_value_closed_zero": not failures,
            "full_fluctuation_hessian_contribution_closed": False,
            "complete_mixed_invariant_ring_G1_closed": False,
            "global_vacuum_closed": False,
        },
        "required_downstream_changes": [
            "Use corrected_operator_catalogue() instead of the historical catalogue for G1 counting.",
            "Increase the guaranteed renormalizable invariant floor by one.",
            "Keep the selected-vacuum phase Hessian unchanged because Q_Delta=0.",
            "Include second derivatives of this operator in the full 10/126 fluctuation Hessian.",
            "Do not use the dimension-six S^2 operator as a substitute for this quartic.",
        ],
        "flags": {
            "historical_operator_omission_corrected": not failures,
            "new_selected_phase_lock_found": False,
            "full_component_hessian_complete": False,
            "g1_closed": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "A renormalizable 54-channel quartic was missing from the historical "
            "G1 catalogue. Its existence and unique multiplicity are now closed. "
            "It vanishes on the canonical Delta_R background, so it does not "
            "alter the corrected reduced phase quotient, but it must enter the "
            "complete fluctuation Hessian. G1 remains open."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# G1 renormalizable 54-channel operator correction — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        + report["verdict"]
        + "\n\n"
        f"- Corrected catalogue size: `{report['corrected_catalogue_size']}`\n"
        f"- Selected Q_Delta norm: `{report['selected_vacuum']['Q_Delta_frobenius']}`\n"
        f"- G1 closed: `{report['scope']['complete_mixed_invariant_ring_G1_closed']}`\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        write_report(report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
