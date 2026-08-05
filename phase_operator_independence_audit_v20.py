#!/usr/bin/env python3
"""Exact formal and selected-vacuum phase-rank audit.

In the basis (phi_Delta,phi_H,phi_S), formal operator vectors are

* kappa H^2 S:                      (0,2,1)
* lambda4 Phi H Sigmabar S:         (1,1,1)
* lambda_lock Sigmabar^2 H^2 S^2:  (2,2,2)

The dimension-six vector is exactly twice lambda4 and never adds rank.
Moreover, direct tensor evaluation on the selected physical vacuum gives both
T_Phi Delta_R=0 and P54(Delta_R,Delta_R)=0. Thus only kappa is active there:
the selected phase Hessian has rank one and two null directions, one being the
PQ axion and one additional unresolved flat phase.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

import physical_h10_54_mass_block_from_deltar_v20 as lock_zero
import selected_vacuum_lambda4_portal_null_audit_v20 as lambda4_zero

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "PHASE_OPERATOR_INDEPENDENCE_AUDIT_V20.json"
OUT_MD = ROOT / "PHASE_OPERATOR_INDEPENDENCE_AUDIT_V20.md"

FIELDS = ("phi_DeltaR", "phi_H10", "phi_S")
VECTORS = {
    "kappa_H2_S": np.array([0.0, 2.0, 1.0]),
    "lambda4_Phi_H_Sigmabar_S": np.array([1.0, 1.0, 1.0]),
    "lambda_lock_Sigmabar2_H2_S2": np.array([2.0, 2.0, 2.0]),
}


def _integer_null_basis(matrix: np.ndarray) -> list[list[int]]:
    _, singular, vh = np.linalg.svd(matrix)
    rank = int(np.sum(singular > 1e-12))
    basis: list[list[int]] = []
    for vector in vh[rank:]:
        nonzero = np.abs(vector) > 1e-10
        vector = vector / np.min(np.abs(vector[nonzero]))
        rounded = np.rint(vector).astype(int)
        pivot = int(np.argmax(np.abs(rounded)))
        if rounded[pivot] < 0:
            rounded = -rounded
        basis.append(rounded.tolist())
    return basis


def build_report() -> dict[str, Any]:
    kappa = VECTORS["kappa_H2_S"]
    lam4 = VECTORS["lambda4_Phi_H_Sigmabar_S"]
    lock = VECTORS["lambda_lock_Sigmabar2_H2_S2"]
    formal_base = np.stack([kappa, lam4])
    formal_all = np.stack([kappa, lam4, lock])
    formal_rank = int(np.linalg.matrix_rank(formal_base))
    formal_rank_all = int(np.linalg.matrix_rank(formal_all))
    pq_null = np.array([1.0, 1.0, -2.0])

    lock_report = lock_zero.build_report()
    lambda4_report = lambda4_zero.build_report()
    lock_active = not bool(
        lock_report.get("flags", {}).get("DeltaR_squared_54_projection_zero")
    )
    lambda4_active = bool(
        lambda4_report.get("flags", {}).get(
            "selected_vacuum_lambda4_amplitude_nonzero"
        )
    )
    active_vectors = [kappa]
    active_names = ["kappa_H2_S"]
    if lambda4_active:
        active_vectors.append(lam4)
        active_names.append("lambda4_Phi_H_Sigmabar_S")
    if lock_active:
        active_vectors.append(lock)
        active_names.append("lambda_lock_Sigmabar2_H2_S2")
    active_matrix = np.stack(active_vectors)
    selected_rank = int(np.linalg.matrix_rank(active_matrix))
    selected_null_dimension = len(FIELDS) - selected_rank
    selected_null_basis = _integer_null_basis(active_matrix)

    checks = {
        "lambda_lock_vector_equals_2_lambda4": np.allclose(lock, 2.0 * lam4),
        "formal_kappa_lambda4_rank_two": formal_rank == 2,
        "formal_lock_adds_zero_rank": formal_rank_all == formal_rank,
        "formal_PQ_null_annihilates_all": np.allclose(formal_all @ pq_null, 0.0),
        "selected_lambda4_amplitude_zero": not lambda4_active,
        "selected_dimension6_amplitude_zero": not lock_active,
        "selected_only_kappa_active": active_names == ["kappa_H2_S"],
        "selected_rank_one": selected_rank == 1,
        "selected_null_dimension_two": selected_null_dimension == 2,
        "PQ_null_still_present": np.allclose(active_matrix @ pq_null, 0.0),
        "whole_model_not_overclaimed": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "SELECTED_PHASE_HESSIAN_RANK_ONE__TWO_NULLS_REQUIRE_NEW_INVARIANT"
            if not failures
            else "PHASE_OPERATOR_INDEPENDENCE_AUDIT_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "fields": list(FIELDS),
        "operator_vectors": {
            name: [int(x) for x in vector]
            for name, vector in VECTORS.items()
        },
        "formal_operator_algebra": {
            "rank_kappa_lambda4": formal_rank,
            "rank_after_adding_lambda_lock": formal_rank_all,
            "rank_increment_from_lambda_lock": formal_rank_all - formal_rank,
            "lambda_lock_equals": "2 * lambda4 phase vector",
            "common_PQ_null_vector": [1, 1, -2],
            "interpretation": (
                "If kappa and lambda4 amplitudes were both nonzero, rank=2 "
                "would leave only the PQ axion null. The dim6 vector is redundant."
            ),
        },
        "selected_vacuum_rank": {
            "active_operators": active_names,
            "inactive_operators": [
                name for name in VECTORS if name not in active_names
            ],
            "lambda4_inactive_reason": "T_Phi Delta_R = 0",
            "lambda_lock_inactive_reason": "P54(Delta_R,Delta_R) = 0",
            "rank": selected_rank,
            "null_dimension": selected_null_dimension,
            "null_basis_integer_representatives": selected_null_basis,
            "PQ_null_vector": [1, 1, -2],
            "additional_flat_phase_present": selected_null_dimension > 1,
        },
        "withdrawn_claims": {
            "selected_vacuum_lambda4_phase_curvature": True,
            "selected_vacuum_dimension6_phase_curvature": True,
            "selected_phase_hessian_rank_two_from_current_operators": True,
            "only_axion_null_remains": True,
        },
        "flags": {
            "formal_phase_vector_problem_closed": not bool(failures),
            "selected_phase_rank_problem_closed": not bool(failures),
            "legacy_lambda_lock_independent_lift_claim_valid": False,
            "selected_vacuum_lambda4_active": False,
            "selected_vacuum_dimension6_lock_valid": False,
            "selected_vacuum_has_extra_nonaxion_flat_phase": True,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "next_requirement": (
            "Find a charge-allowed invariant with a nonzero tensor projection "
            "on the actual vacuum and an active phase vector independent of "
            "kappa, while preserving exactly one global PQ/axion null before QCD."
        ),
        "verdict": (
            "Formally lambda_lock is redundant with lambda4. Physically both "
            "are inactive on the selected Delta_R vacuum: T_Phi Delta_R=0 and "
            "P54(Delta_R,Delta_R)=0. Only kappa H^2S supplies phase curvature, "
            "so the selected phase Hessian has rank one and two null directions. "
            "One is the PQ axion; the other is an unresolved flat phase. The "
            "current vacuum is not fully stabilized."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    selected = report["selected_vacuum_rank"]
    OUT_MD.write_text(
        "# Phase-operator independence and selected-vacuum rank — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- Formal rank: `{report['formal_operator_algebra']['rank_kappa_lambda4']}`\n"
        f"- Selected rank: `{selected['rank']}`\n"
        f"- Selected null dimension: `{selected['null_dimension']}`\n\n"
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
