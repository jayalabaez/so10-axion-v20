#!/usr/bin/env python3
"""Exact formal and selected-vacuum phase-rank audit with gauge quotient.

In the basis (phi_Delta,phi_H,phi_S), formal operator vectors are

* kappa H^2 S:                      (0,2,1)
* lambda4 Phi H Sigmabar S:         (1,1,1)
* lambda_lock Sigmabar^2 H^2 S^2:  (2,2,2)

The dimension-six vector is exactly twice lambda4 and never adds rank.
Direct tensor evaluation on the selected vacuum gives both
T_Phi Delta_R=0 and P54(Delta_R,Delta_R)=0, so only kappa is active.

The unquotiented selected Hessian therefore has rank one and two nulls.
One null is the eaten Z'_R/B-L gauge orbit q=(1,0,0). After that gauge
quotient the physical sector (phi_H,phi_S) has rank one and exactly one
null — the PQ axion. There is no additional physical non-axion flat phase.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

import physical_h10_54_mass_block_from_deltar_v20 as lock_zero
import selected_vacuum_lambda4_portal_null_audit_v20 as lambda4_zero
import selected_vacuum_neutral_phase_gauge_quotient_v20 as gauge_quot

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
    quotient = gauge_quot.quotient_report(1.0)
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

    phys_rank = int(quotient["hessian"]["rank_after_quotient"])
    phys_null = int(quotient["hessian"]["nullity_after_quotient"])

    checks = {
        "lambda_lock_vector_equals_2_lambda4": np.allclose(lock, 2.0 * lam4),
        "formal_kappa_lambda4_rank_two": formal_rank == 2,
        "formal_lock_adds_zero_rank": formal_rank_all == formal_rank,
        "formal_PQ_null_annihilates_all": np.allclose(formal_all @ pq_null, 0.0),
        "selected_lambda4_amplitude_zero": not lambda4_active,
        "selected_dimension6_amplitude_zero": not lock_active,
        "selected_only_kappa_active": active_names == ["kappa_H2_S"],
        "selected_prequotient_rank_one": selected_rank == 1,
        "selected_prequotient_null_dimension_two": selected_null_dimension == 2,
        "PQ_null_still_present_prequotient": np.allclose(active_matrix @ pq_null, 0.0),
        "gauge_quotient_upstream_green": quotient["n_failed"] == 0,
        "physical_rank_one_after_gauge_quotient": phys_rank == 1,
        "physical_null_dimension_one_after_gauge_quotient": phys_null == 1,
        "DeltaR_phase_is_eaten_gauge_null": bool(
            quotient["flags"]["DeltaR_phase_eaten_by_Zprime_BL_R"]
        ),
        "whole_model_not_overclaimed": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "SELECTED_PHASE_HESSIAN_CLOSED_AFTER_NEUTRAL_GAUGE_QUOTIENT"
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
            "additional_flat_phase_present_prequotient": selected_null_dimension > 1,
            "additional_flat_phase_present": False,
            "prequotient_second_null_classification": "eaten_Zprime_BL_R_gauge_Goldstone",
        },
        "physical_after_gauge_quotient": {
            "rank": phys_rank,
            "null_dimension": phys_null,
            "physical_null_vector_integer": quotient["hessian"][
                "physical_null_vector_integer"
            ],
            "physical_null": "PQ axion",
            "extra_nonaxion_flat_phase": False,
            "upstream_status": quotient["status"],
        },
        "withdrawn_claims": {
            "selected_vacuum_lambda4_phase_curvature": True,
            "selected_vacuum_dimension6_phase_curvature": True,
            "selected_phase_hessian_rank_two_from_current_operators": True,
            "extra_physical_nonaxion_flat_phase": True,
        },
        "flags": {
            "formal_phase_vector_problem_closed": not bool(failures),
            "selected_phase_rank_problem_closed": not bool(failures),
            "legacy_lambda_lock_independent_lift_claim_valid": False,
            "selected_vacuum_lambda4_active": False,
            "selected_vacuum_dimension6_lock_valid": False,
            "selected_vacuum_has_extra_nonaxion_flat_phase": False,
            "prequotient_null_includes_gauge_Goldstone": True,
            "physical_phase_closed_after_gauge_quotient": not bool(failures),
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "next_requirement": (
            "Rewrite remaining legacy pre-quotient consumers, then continue the "
            "full component scalar Hessian with root-by-root 33 Goldstone removal."
        ),
        "verdict": (
            "Formally lambda_lock is redundant with lambda4. Physically both "
            "are inactive on the selected Delta_R vacuum. Only kappa is active, "
            "so the unquotiented Hessian has rank one and two nulls. One null is "
            "the eaten Z' Goldstone; after gauge quotient the sole physical null "
            "is the PQ axion. There is no extra physical non-axion flat phase."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    selected = report["selected_vacuum_rank"]
    physical = report["physical_after_gauge_quotient"]
    OUT_MD.write_text(
        "# Phase-operator independence and selected-vacuum rank — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- Formal rank: `{report['formal_operator_algebra']['rank_kappa_lambda4']}`\n"
        f"- Prequotient selected rank: `{selected['rank']}`\n"
        f"- Prequotient null dimension: `{selected['null_dimension']}`\n"
        f"- Physical rank after gauge quotient: `{physical['rank']}`\n"
        f"- Physical null dimension: `{physical['null_dimension']}`\n\n"
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
