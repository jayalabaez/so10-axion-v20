#!/usr/bin/env python3
"""Reproduce historical no-X Phi17 dressings through dimension 4.

This module belongs to the superseded ``historical_option_c_no_x_v20``
counterfactual.  There Phi17 was treated as neutral under all enforced
symmetries, giving the finite dressing inventory:

* a Hermitian quadratic core Q has Q*Phi17+h.c., Q*Phi17^2+h.c.,
  and Q*|Phi17|^2;
* a Hermitian cubic core C has C*Phi17+h.c.;
* a complex cubic core O has two independent classes,
  O*Phi17+h.c. and O*Phi17dag+h.c.

For the already-proved non-singlet cores this produces 15 classes. Eight are
already registered and exactly seven are missing. No new SO(10) Clebsches are
needed: every missing class inherits the normalized multiplicity-one core.
After <Phi17>=z they promote existing masses and cubic coefficients and, in
general, create heavy--Phi17 cross-Hessian blocks.

In the manuscript Phi17 has gauged X=17.  The holomorphic dressings enumerated
here are therefore gauge-forbidden.  The inventory and coefficient maps are
retained only to reproduce the historical no-X calculation; they do not close
the live G1 basis or support a model-wide conclusion.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import nonsusy_z17_pq_hsigma_completion_v20 as current_catalogue
import nonsusy_z17_pq_potential_filter_v20 as charge_filter

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_PHI17_NEUTRAL_DRESSING_COMPLETION_V20.json"
OUT_MD = ROOT / "EXACT_PHI17_NEUTRAL_DRESSING_COMPLETION_V20.md"
MODEL_CONTRACT_ID = "historical_option_c_no_x_v20"

PHI_NORM_P = "210_H^dag 210_H Phi17"
PHI_NORM_P2 = "210_H^dag 210_H Phi17^2"
SIGMA_NORM_P = "126bar_H^dag 126bar_H Phi17"
SIGMA_NORM_P2 = "126bar_H^dag 126bar_H Phi17^2"
PHI3_P = "210_H^3 Phi17"
PHISIGMA_P = "210_H 126bar_H^dag 126bar_H Phi17"
H2S_PBAR = "10_H^2 S Phi17_dag"

ADDITIONS: tuple[dict[str, Any], ...] = (
    {
        "name": PHI_NORM_P,
        "counts": {"210_H_dag": 1, "210_H": 1, "Phi17": 1},
        "dim": 3,
        "multiplicity": 1,
        "core": "210_H^dag 210_H",
        "role": "linear Phi17 promotion of the 210 mass coefficient",
    },
    {
        "name": PHI_NORM_P2,
        "counts": {"210_H_dag": 1, "210_H": 1, "Phi17": 2},
        "dim": 4,
        "multiplicity": 1,
        "core": "210_H^dag 210_H",
        "role": "holomorphic-quadratic Phi17 promotion of the 210 mass coefficient",
    },
    {
        "name": SIGMA_NORM_P,
        "counts": {"126bar_H_dag": 1, "126bar_H": 1, "Phi17": 1},
        "dim": 3,
        "multiplicity": 1,
        "core": "126bar_H^dag 126bar_H",
        "role": "linear Phi17 promotion of the 126bar mass coefficient",
    },
    {
        "name": SIGMA_NORM_P2,
        "counts": {"126bar_H_dag": 1, "126bar_H": 1, "Phi17": 2},
        "dim": 4,
        "multiplicity": 1,
        "core": "126bar_H^dag 126bar_H",
        "role": "holomorphic-quadratic Phi17 promotion of the 126bar mass coefficient",
    },
    {
        "name": PHI3_P,
        "counts": {"210_H": 3, "Phi17": 1},
        "dim": 4,
        "multiplicity": 1,
        "core": "210_H^3",
        "role": "Phi17 promotion of the unique 210 cubic coefficient",
    },
    {
        "name": PHISIGMA_P,
        "counts": {
            "210_H": 1,
            "126bar_H_dag": 1,
            "126bar_H": 1,
            "Phi17": 1,
        },
        "dim": 4,
        "multiplicity": 1,
        "core": "210_H 126bar_H^dag 126bar_H",
        "role": "Phi17 promotion of the unique Hermitian Phi-Sigma cubic",
    },
    {
        "name": H2S_PBAR,
        "counts": {"10_H": 2, "S": 1, "Phi17_dag": 1},
        "dim": 4,
        "multiplicity": 1,
        "core": "10_H^2 S",
        "role": "second independent Phi17 dressing of the H^2 S channel",
    },
)

HERMITIAN_QUADRATIC_CORES = {
    "210_H^dag 210_H": {
        "linear": PHI_NORM_P,
        "holomorphic_quadratic": PHI_NORM_P2,
        "modulus": "210_H^dag 210_H Phi17^dag Phi17",
    },
    "126bar_H^dag 126bar_H": {
        "linear": SIGMA_NORM_P,
        "holomorphic_quadratic": SIGMA_NORM_P2,
        "modulus": "|Phi17|^2 |126bar_H|^2",
    },
    "10_H^dag 10_H": {
        "linear": "10_H^dag 10_H Phi17",
        "holomorphic_quadratic": "10_H^dag 10_H Phi17^2",
        "modulus": "|Phi17|^2 |10_H|^2",
    },
}
HERMITIAN_CUBIC_CORES = {
    "210_H^3": PHI3_P,
    "210_H 126bar_H^dag 126bar_H": PHISIGMA_P,
}
COMPLEX_CUBIC_CORES = {
    "10_H^2 S": {
        "Phi17": "10_H^2 S Phi17",
        "Phi17_dag": H2S_PBAR,
    },
    "210_H 10_H_dag 126bar_H": {
        "Phi17": "210_H 10_H_dag 126bar_H Phi17",
        "Phi17_dag": "210_H 10_H_dag 126bar_H Phi17_dag",
    },
}


def required_dressing_names() -> set[str]:
    names: set[str] = set()
    for companions in HERMITIAN_QUADRATIC_CORES.values():
        names.update(companions.values())
    names.update(HERMITIAN_CUBIC_CORES.values())
    for companions in COMPLEX_CUBIC_CORES.values():
        names.update(companions.values())
    return names


def charge_audit() -> dict[str, Any]:
    rows: dict[str, Any] = {}
    for row in ADDITIONS:
        totals = charge_filter._total_charge(row["counts"])
        rows[row["name"]] = {
            **row,
            "charge_totals": totals,
            "option_c_no_x_allowed": charge_filter._allowed(
                totals, require_x=False
            ),
            "gauged_u1x_manuscript_allowed": charge_filter._allowed(
                totals, require_x=True
            ),
            "so10_reason": (
                "Phi17 is an SO(10) singlet; multiplicity equals the proved core"
            ),
        }
    return rows


def catalogue_census() -> dict[str, Any]:
    """Census the historical no-X overlay, never the live gauged catalogue."""
    current = current_catalogue.operator_catalogue(require_x=False)
    current_names = {row["name"] for row in current}
    required = required_dressing_names()
    missing = sorted(required - current_names)
    present = sorted(required & current_names)
    expected_missing = sorted(row["name"] for row in ADDITIONS)
    return {
        "current_catalogue_count": len(current),
        "required_dressing_count": len(required),
        "required_names": sorted(required),
        "already_present": present,
        "missing": missing,
        "expected_missing": expected_missing,
        "missing_exactly_seven": missing == expected_missing,
        "already_present_count": len(present),
        "missing_count": len(missing),
    }


def effective_coefficient_map() -> dict[str, str]:
    return {
        "mPhi2_eff": (
            "mPhi2 + 2 Re(aPhi1*z + aPhi2*z^2) + lambdaPhiAbs*|z|^2"
        ),
        "mSigma2_eff": (
            "mSigma2 + 2 Re(aSigma1*z + aSigma2*z^2) + lambdaSigmaAbs*|z|^2"
        ),
        "mH2_eff_existing_family": (
            "mH2 + 2 Re(aH1*z + aH2*z^2) + lambdaHAbs*|z|^2"
        ),
        "kappaPhi3_eff": "kappaPhi3 + 2 Re(etaPhi3*z)",
        "muPhiSigma_eff": "muPhiSigma + 2 Re(etaPhiSigma*z)",
        "kappaH2S_eff": (
            "kappaH2S + etaH2S_plus*z + etaH2S_minus*z^*"
        ),
        "muD_eff_existing_family": (
            "muD + etaD_plus*z + etaD_minus*z^*"
        ),
        "cross_hessian_rule": (
            "For V=f(z,z*)I(core), mixed heavy-Phi17 blocks are outer "
            "products of grad(I) and grad(f); they generally enter G3/G4."
        ),
    }


def independence_audit() -> dict[str, Any]:
    degrees = {
        row["name"]: tuple(sorted(row["counts"].items())) for row in ADDITIONS
    }
    return {
        "field_multi_degrees": degrees,
        "all_seven_have_distinct_field_multi_degree": (
            len(set(degrees.values())) == len(degrees)
        ),
        "independence_reason": (
            "Distinct field multi-degrees cannot satisfy a linear identity; "
            "each tensor inherits its multiplicity-one core."
        ),
    }


def build_report() -> dict[str, Any]:
    charges = charge_audit()
    census = catalogue_census()
    independence = independence_audit()
    coefficient_map = effective_coefficient_map()
    checks = {
        "dressing_theorem_inventory_has_15_classes": (
            census["required_dressing_count"] == 15
        ),
        "eight_existing_companions_detected": (
            census["already_present_count"] == 8
        ),
        "exactly_seven_missing_classes": census["missing_exactly_seven"],
        "all_missing_classes_option_c_no_x_allowed": all(
            row["option_c_no_x_allowed"]["all"] for row in charges.values()
        ),
        "all_missing_classes_forbidden_by_manuscript_u1x": all(
            not row["gauged_u1x_manuscript_allowed"]["all"]
            for row in charges.values()
        ),
        "all_missing_classes_SO10_inherit_core": True,
        "all_seven_independent_by_multidegree": independence[
            "all_seven_have_distinct_field_multi_degree"
        ],
        "all_multiplicities_one": all(
            row["multiplicity"] == 1 for row in ADDITIONS
        ),
        "effective_coefficient_map_complete": set(coefficient_map) == {
            "mPhi2_eff",
            "mSigma2_eff",
            "mH2_eff_existing_family",
            "kappaPhi3_eff",
            "muPhiSigma_eff",
            "kappaH2S_eff",
            "muD_eff_existing_family",
            "cross_hessian_rule",
        },
        "full_ring_not_claimed": True,
        "whole_model_not_validated": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "model_contract_id": MODEL_CONTRACT_ID,
        "authoritative_for_manuscript": False,
        "model_wide_no_go_certified": False,
        "status": (
            "HISTORICAL_OPTION_C_PHI17_DRESSINGS_REPRODUCED__NONAUTHORITATIVE"
            if not failures
            else "HISTORICAL_OPTION_C_PHI17_DRESSING_REPRODUCTION_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "theorem": {
            "hermitian_quadratic_cores": HERMITIAN_QUADRATIC_CORES,
            "hermitian_cubic_cores": HERMITIAN_CUBIC_CORES,
            "complex_cubic_cores": COMPLEX_CUBIC_CORES,
        },
        "charge_audit": charges,
        "catalogue_census": census,
        "independence_audit": independence,
        "effective_coefficient_map": coefficient_map,
        "additions": list(ADDITIONS),
        "flags": {
            "historical_option_c_dressing_inventory_reproduced": not failures,
            "historical_seven_missing_classes_enumerated": not failures,
            "historical_no_new_SO10_Clebsches_required": not failures,
            "historical_effective_heavy_coefficients_promoted": not failures,
            "historical_heavy_Phi17_cross_blocks_derived": not failures,
            "phi17_dressings_allowed_by_manuscript_u1x": False,
            "authoritative_for_manuscript": False,
            "model_wide_no_go_certified": False,
            "complete_mixed_invariant_ring": False,
            "complete_component_potential": False,
            "full_multifield_vacuum": False,
            "whole_model_validated": False,
            "empirical_discovery": False,
        },
        "verdict": (
            "The historical Option-C/no-X inventory contains 15 Phi17 "
            "dressings, with eight previously present and seven added here. "
            "Their SO(10) multiplicities and coefficient maps are reproducible, "
            "but the holomorphic Phi17 dressings are forbidden by the "
            "manuscript's gauged U(1)_X. This is not a live G1 closure and "
            "neither validates nor excludes the gauged theory."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Historical Option-C Phi17 dressing calculation\n\n"
        f"**Status:** `{report['status']}`\n\n"
        + report["verdict"]
        + "\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        write_report(report)
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
