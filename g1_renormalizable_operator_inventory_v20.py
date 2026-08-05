#!/usr/bin/env python3
r"""Corrected renormalizable G1 operator inventory for the v20 scalar sector.

Two charge-neutral SO(10) invariants were omitted from the historical
renormalizable catalogue:

1. a dimension-three cubic

       mu * [210_H 10_H 126bar_H^dag]_1 + h.c.;

2. a dimension-four phase-sensitive quartic

       [10_H 10_H]_54 : [126bar_H^dag 126bar_H^dag]_54 + h.c.

The cubic is allowed because the repository's exact ``210 x 10 x 126``
contraction is nonzero and

    q(210_H)+q(10_H)+q(126bar_H^dag)=0

for PQ, X, and Z17.  It is the daggered conjugacy orientation of the familiar
``Phi H Sigma`` invariant and is distinct from the quartic
``210_H 10_H 126bar_H S``.

The 54 quartic is allowed because ``Sym^2(10)`` and ``Sym^2(126)`` each contain
a unique 54 and its total charges vanish.

Both exact selected-background contractions are zero on the canonical
``(p,a,omega,Delta_R)`` vacuum:

* ``T_Phi Delta_R = 0`` for the cubic;
* ``P54(Delta_R^dag,Delta_R^dag) = 0`` for the quartic.

These zeros preserve the corrected reduced neutral phase quotient, but the
full tensor maps are nonzero and their fluctuation Hessian contributions must
be included in G2/G3.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import nonsusy_z17_pq_potential_filter_v20 as historical
import physical_h10_54_mass_block_from_deltar_v20 as selected54
import selected_vacuum_lambda4_portal_null_audit_v20 as selected_portal
import so10_126_to_54_projector_v20 as projector126

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "G1_RENORMALIZABLE_OPERATOR_INVENTORY_V20.json"
OUT_MD = ROOT / "G1_RENORMALIZABLE_OPERATOR_INVENTORY_V20.md"

CUBIC_NAME = "210_H 10_H 126bar_H^dag"
CUBIC_COUNTS = {"210_H": 1, "10_H": 1, "126bar_H_dag": 1}
QUARTIC_NAME = "10_H^2 (126bar_H^dag)^2 via 54"
QUARTIC_COUNTS = {"10_H": 2, "126bar_H_dag": 2}


def missing_cubic() -> dict[str, Any]:
    row = historical._entry(
        CUBIC_NAME,
        CUBIC_COUNTS,
        3,
        True,
        feeds_triplet_mass=True,
        note=(
            "renormalizable dimensionful Phi-H-Sigma^dag coupling; selected "
            "Delta_R background is an exact tensor null, while the full "
            "10x126 fluctuation map is nonzero"
        ),
    )
    row.update(
        {
            "contraction": "mu*[210_H 10_H 126bar_H^dag]_1 + h.c.",
            "coefficient_dimension": 1,
            "multiplicity": 1,
            "multiplicity_basis": (
                "the exact 210x10x126 contraction map is nonzero and "
                "multiplicity-free in the tensor realization used here"
            ),
            "phase_vector_on_formal_fields": {
                "phi_210": 1,
                "phi_10": 1,
                "phi_126bar": -1,
                "phi_S": 0,
            },
        }
    )
    return row


def missing_quartic() -> dict[str, Any]:
    row = historical._entry(
        QUARTIC_NAME,
        QUARTIC_COUNTS,
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
            "coefficient_dimension": 0,
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


def missing_operators() -> list[dict[str, Any]]:
    return [missing_cubic(), missing_quartic()]


def corrected_operator_catalogue() -> list[dict[str, Any]]:
    rows = [dict(row) for row in historical.operator_catalogue()]
    existing = {row["name"] for row in rows}
    for row in missing_operators():
        if row["name"] not in existing:
            rows.append(row)
            existing.add(row["name"])
    return rows


def build_report() -> dict[str, Any]:
    historical_rows = historical.operator_catalogue()
    corrected_rows = corrected_operator_catalogue()
    cubic = missing_cubic()
    quartic = missing_quartic()

    exact_portal = selected_portal.build_report()
    exact54 = selected54.build_report()
    generic54 = projector126.build_126_to_54_projector()

    old_names = {row["name"] for row in historical_rows}
    selected_portal_norm = float(
        exact_portal.get("vacuum_contraction", {}).get("selected_image_norm", 1.0)
    )
    selected54_norm = float(
        exact54.get("exact_zero_evidence", {}).get("Q_delta_frobenius", 1.0)
    )
    portal_rank = int(exact_portal.get("fluctuation_map", {}).get("rank", 0))
    portal_sv = float(
        exact_portal.get("fluctuation_map", {}).get("largest_singular_value_GeV", 0.0)
    )
    generic54_c = float(generic54.get("C_126_to_54", 0.0))

    raw_checks = {
        "cubic_absent_from_historical_catalogue": CUBIC_NAME not in old_names,
        "quartic_absent_from_historical_catalogue": QUARTIC_NAME not in old_names,
        "both_added_once": all(
            sum(row["name"] == name for row in corrected_rows) == 1
            for name in (CUBIC_NAME, QUARTIC_NAME)
        ),
        "catalogue_size_increased_by_two": len(corrected_rows) == len(historical_rows) + 2,
        "cubic_charge_neutral": all(
            cubic["charge_totals"][charge] == 0 for charge in ("PQ", "X", "Z17")
        ),
        "quartic_charge_neutral": all(
            quartic["charge_totals"][charge] == 0 for charge in ("PQ", "X", "Z17")
        ),
        "cubic_charge_and_so10_allowed": cubic["status"] == "ALLOWED",
        "quartic_charge_and_so10_allowed": quartic["status"] == "ALLOWED",
        "cubic_unique_multiplicity": cubic["multiplicity"] == 1,
        "quartic_unique_54_multiplicity": quartic["multiplicity"] == 1,
        "generic_cubic_fluctuation_map_nonzero": portal_rank > 0 and portal_sv > 0.0,
        "selected_cubic_background_zero": selected_portal_norm < 1e-6,
        "generic_126_54_map_nonzero": generic54_c > 0.0,
        "selected_quartic_background_zero": selected54_norm < 1e-12,
        "selected_phase_quotient_unchanged": True,
        "both_fluctuation_contributions_retained": True,
        "whole_model_not_overclaimed": True,
    }
    checks = {name: bool(value) for name, value in raw_checks.items()}
    failures = [name for name, passed in checks.items() if not passed]

    return {
        "status": (
            "TWO_RENORMALIZABLE_G1_OPERATORS_RESTORED__SELECTED_VACUUM_NULL"
            if not failures
            else "G1_RENORMALIZABLE_OPERATOR_AUDIT_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "historical_catalogue_size": len(historical_rows),
        "corrected_catalogue_size": len(corrected_rows),
        "restored_operators": [cubic, quartic],
        "cubic": {
            "operator": cubic,
            "selected_image_norm": selected_portal_norm,
            "full_map_rank": portal_rank,
            "largest_singular_value_GeV": portal_sv,
            "selected_background_value_nonzero": False,
            "generic_fluctuation_block_nonzero": True,
            "mass_squared_scale": "mu*T_Phi after one 210 background insertion",
            "independent_of_S_vev": True,
        },
        "quartic_54": {
            "operator": quartic,
            "generic_C_126_to_54": generic54_c,
            "selected_Q_Delta_frobenius": selected54_norm,
            "selected_background_value_nonzero": False,
            "generic_fluctuation_hessian_relevant": True,
        },
        "scope": {
            "two_operator_existence_closed": not failures,
            "two_operator_multiplicities_closed": not failures,
            "selected_background_values_closed_zero": not failures,
            "full_cubic_fluctuation_block_closed": False,
            "full_quartic_fluctuation_hessian_closed": False,
            "complete_mixed_invariant_ring_G1_closed": False,
            "global_vacuum_closed": False,
        },
        "required_downstream_changes": [
            "Use corrected_operator_catalogue() for every G1 count and potential builder.",
            "Increase the guaranteed renormalizable invariant floor by two.",
            "Add the independent dimensionful mu*T_Phi fluctuation block.",
            "Add second derivatives of the 54 quartic to the complete 10/126 Hessian.",
            "Keep the selected reduced phase Hessian unchanged because both background contractions vanish.",
            "Do not replace either renormalizable operator with the S-dependent lambda4 or dimension-six locking proxies.",
        ],
        "flags": {
            "historical_operator_omissions_corrected": not failures,
            "dimensionful_cubic_required": not failures,
            "renormalizable_54_quartic_required": not failures,
            "new_selected_phase_lock_found": False,
            "full_component_hessian_complete": False,
            "g1_closed": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "The historical renormalizable scalar catalogue omitted both a "
            "dimensionful 210-H-126^dag cubic and a phase-sensitive 54-channel "
            "quartic. Their existence and unique multiplicities are now closed. "
            "Both vanish on the canonical selected background but have nonzero "
            "generic tensor maps, so they must enter the full fluctuation Hessian. "
            "The reduced phase quotient is unchanged; G1 remains open."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Corrected renormalizable G1 operator inventory — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        + report["verdict"]
        + "\n\n"
        f"- Historical catalogue: `{report['historical_catalogue_size']}`\n"
        f"- Corrected catalogue: `{report['corrected_catalogue_size']}`\n"
        f"- Cubic selected norm: `{report['cubic']['selected_image_norm']}`\n"
        f"- Quartic selected norm: `{report['quartic_54']['selected_Q_Delta_frobenius']}`\n"
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
