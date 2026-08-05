#!/usr/bin/env python3
r"""Exact neutral gauge quotient of the selected-vacuum phase Hessian.

The reduced phase basis used by ``multi_operator_phase_hessian_v20`` is

    (phi_DeltaR, phi_10, phi_S).

On the selected vacuum the Delta_R phase is not a physical scalar direction.
Delta_R is the SM-singlet component of the Pati--Salam (10,1,3) and its VEV
breaks the neutral combination orthogonal to hypercharge.  The corresponding
Z'_R/B-L vector eats one real Goldstone.  In this reduced basis that neutral
gauge orbit is represented by

    q_gauge = (1,0,0).

The ``phi_10`` coordinate is the common complex phase entering H_10^2 S; the
relative electroweak-doublet gauge phase is a separate SM Goldstone and is not
part of this three-coordinate reduced basis.

With the exact selected-vacuum tensor nulls enforced, only kappa H_10^2 S is
active, with phase vector

    g_kappa = (0,2,1).

Before gauge quotient the Hessian has rank one and two nulls.  One null is the
Z' gauge orbit.  Quotienting it leaves a two-dimensional physical phase space
(phi_10,phi_S) with rank one and exactly one null.  That null is the PQ axion.
There is no additional physical non-axion flat phase in this reduced sector.

The same subgroup argument explains the finite invariant-search zeros at every
polynomial dimension.  Let d,h,s be field-minus-conjugate powers of Delta_R,
H_10,S.  B-L neutrality of a nonzero selected-vacuum monomial forces d=0.
PQ/Z17 neutrality, -2 d -2 h +4 s=0, then gives h=2s, so every nonzero phase
vector is parallel to g_kappa.  This is gauge invariance plus PQ invariance,
not a physical phase-stabilization obstruction.

Scope
-----
* Exact for the reduced neutral phase coordinates and selected VEV content.
* Does not replace the full component scalar Hessian or root-by-root 33-mode
  Goldstone audit.
* Requires a nonzero positive kappa phase amplitude for the one massive
  physical CP-odd combination.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SELECTED_VACUUM_NEUTRAL_PHASE_GAUGE_QUOTIENT_V20.json"
OUT_MD = ROOT / "SELECTED_VACUUM_NEUTRAL_PHASE_GAUGE_QUOTIENT_V20.md"

FIELDS_FULL = ("phi_DeltaR_126bar", "phi_10_common", "phi_S")
FIELDS_PHYSICAL = ("phi_10_common", "phi_S")
Q_GAUGE_ZPRIME = np.array([1.0, 0.0, 0.0])
Q_PQ = np.array([1.0, 1.0, -2.0])
G_KAPPA = np.array([0.0, 2.0, 1.0])
PHYSICAL_EMBEDDING = np.array(
    [
        [0.0, 0.0],
        [1.0, 0.0],
        [0.0, 1.0],
    ]
)


def normalized_integer_vector(values: np.ndarray) -> list[int]:
    rounded = np.rint(values).astype(int)
    nz = [abs(int(v)) for v in rounded if int(v) != 0]
    if not nz:
        return [0 for _ in rounded]
    divisor = int(np.gcd.reduce(nz))
    rounded //= max(divisor, 1)
    pivot = next(int(v) for v in rounded if int(v) != 0)
    if pivot < 0:
        rounded = -rounded
    return [int(v) for v in rounded]


def phase_hessian(a_kappa: float = 1.0) -> np.ndarray:
    if a_kappa <= 0.0:
        raise ValueError("a_kappa must be positive for the stabilized reduced sector")
    return float(a_kappa) * np.outer(G_KAPPA, G_KAPPA)


def quotient_report(a_kappa: float = 1.0) -> dict[str, Any]:
    h_full = phase_hessian(a_kappa)
    h_phys = PHYSICAL_EMBEDDING.T @ h_full @ PHYSICAL_EMBEDDING
    eig_full = np.linalg.eigvalsh(h_full)
    eig_phys = np.linalg.eigvalsh(h_phys)
    tol = 1e-12 * max(float(np.max(np.abs(eig_full))), 1.0)

    rank_full = int(np.linalg.matrix_rank(h_full, tol=tol))
    rank_phys = int(np.linalg.matrix_rank(h_phys, tol=tol))
    null_full = 3 - rank_full
    null_phys = 2 - rank_phys

    pq_physical_representative = Q_PQ - Q_GAUGE_ZPRIME
    pq_projected = PHYSICAL_EMBEDDING.T @ pq_physical_representative
    g_phys = PHYSICAL_EMBEDDING.T @ G_KAPPA

    # The physical null vector of [[4,2],[2,1]] is (1,-2).
    _, _, vh = np.linalg.svd(h_phys)
    physical_null = vh[-1]
    if np.dot(physical_null, pq_projected) < 0:
        physical_null = -physical_null

    checks = {
        "kappa_is_gauge_invariant": abs(float(np.dot(G_KAPPA, Q_GAUGE_ZPRIME))) < 1e-12,
        "gauge_orbit_is_full_hessian_null": float(np.linalg.norm(h_full @ Q_GAUGE_ZPRIME)) < 1e-12,
        "full_reduced_rank_one": rank_full == 1,
        "full_reduced_nullity_two": null_full == 2,
        "gauge_quotient_rank_one": rank_phys == 1,
        "gauge_quotient_nullity_one": null_phys == 1,
        "projected_PQ_is_null": float(np.linalg.norm(h_phys @ pq_projected)) < 1e-12,
        "physical_null_is_projected_PQ": abs(
            abs(float(np.dot(physical_null, pq_projected)))
            / (float(np.linalg.norm(physical_null)) * float(np.linalg.norm(pq_projected)))
            - 1.0
        ) < 1e-12,
        "one_positive_physical_mode": int(np.sum(eig_phys > tol)) == 1,
        "no_negative_physical_mode": int(np.sum(eig_phys < -tol)) == 0,
        "original_PQ_differs_by_gauge_orbit": np.allclose(
            Q_PQ, pq_physical_representative + Q_GAUGE_ZPRIME
        ),
    }
    failures = [name for name, passed in checks.items() if not passed]

    return {
        "status": (
            "SELECTED_VACUUM_NEUTRAL_PHASE_CLOSED_AFTER_GAUGE_QUOTIENT"
            if not failures
            else "SELECTED_VACUUM_NEUTRAL_PHASE_GAUGE_QUOTIENT_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "basis": {
            "reduced_before_quotient": list(FIELDS_FULL),
            "physical_after_quotient": list(FIELDS_PHYSICAL),
            "neutral_gauge_orbit_Zprime": Q_GAUGE_ZPRIME.tolist(),
            "PQ_vector_before_quotient": Q_PQ.tolist(),
            "PQ_representative_after_gauge_choice": pq_physical_representative.tolist(),
            "PQ_vector_in_physical_basis": pq_projected.tolist(),
            "kappa_phase_vector_before_quotient": G_KAPPA.tolist(),
            "kappa_phase_vector_after_quotient": g_phys.tolist(),
            "physical_embedding": PHYSICAL_EMBEDDING.tolist(),
        },
        "hessian": {
            "A_kappa": float(a_kappa),
            "before_quotient": h_full.tolist(),
            "after_quotient": h_phys.tolist(),
            "eigenvalues_before_quotient": [float(x) for x in eig_full],
            "eigenvalues_after_quotient": [float(x) for x in eig_phys],
            "rank_before_quotient": rank_full,
            "nullity_before_quotient": null_full,
            "gauge_orbit_rank_removed": 1,
            "physical_phase_dimension": 2,
            "rank_after_quotient": rank_phys,
            "nullity_after_quotient": null_phys,
            "physical_null_vector_numeric": physical_null.tolist(),
            "physical_null_vector_integer": normalized_integer_vector(pq_projected),
        },
        "all_orders_selection_rule": {
            "field_difference_vector": ["d=Delta-Delta_dag", "h=H-H_dag", "s=S-S_dag"],
            "BL_neutrality_on_selected_VEVs": "d=0",
            "PQ_Z17_neutrality": "-2*d - 2*h + 4*s = 0",
            "combined_result": "(d,h,s)=s*(0,2,1)",
            "interpretation": (
                "Every nonzero selected-vacuum polynomial phase vector is parallel "
                "to kappa. The Delta phase absence is the eaten Z' gauge direction; "
                "after quotient the only remaining zero is PQ."
            ),
        },
        "flags": {
            "DeltaR_phase_eaten_by_Zprime_BL_R": True,
            "extra_nonaxion_flat_phase_present": False,
            "exactly_one_physical_PQ_null": not bool(failures),
            "reduced_neutral_phase_sector_closed_for_positive_kappa": not bool(failures),
            "finite_dimension_phase_search_required_for_closure": False,
            "full_component_scalar_hessian_complete": False,
            "root_by_root_33_goldstone_projection_complete": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "The two nulls of the unquotiented 3x3 phase Hessian are one neutral "
            "gauge Goldstone and one PQ axion. Removing the Z' gauge orbit leaves "
            "one massive physical CP-odd combination and exactly one PQ null. "
            "There is no additional physical phase-stabilization obstruction in "
            "this reduced selected-vacuum sector."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    h = report["hessian"]
    OUT_MD.write_text(
        "# Selected-vacuum neutral phase gauge quotient — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- Rank before quotient: `{h['rank_before_quotient']}`\n"
        f"- Nullity before quotient: `{h['nullity_before_quotient']}`\n"
        f"- Gauge directions removed: `{h['gauge_orbit_rank_removed']}`\n"
        f"- Physical rank: `{h['rank_after_quotient']}`\n"
        f"- Physical nullity: `{h['nullity_after_quotient']}`\n"
        f"- Physical null: `{h['physical_null_vector_integer']}` (PQ)\n\n"
        + report["verdict"]
        + "\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--A-kappa", type=float, default=1.0)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = quotient_report(args.A_kappa)
    if args.write:
        write_report(report)
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
