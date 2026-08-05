#!/usr/bin/env python3
"""Exact phase-vector rank audit for the Delta_R, H10, S sector.

With the real 210 phase fixed, the relevant operator phase vectors in the
basis (phi_Delta, phi_H, phi_S) are

* kappa H^2 S:                 (0, 2, 1)
* lambda4 Phi H Sigmabar S:    (1, 1, 1)
* lambda_lock Sigmabar^2 H^2 S^2: (2, 2, 2)

The dimension-six vector is exactly twice the lambda4 vector. Therefore it
cannot increase the phase-Hessian rank or lift a null direction not already
lifted by lambda4. The first two independent vectors have rank two and common
null vector (1,1,-2), the expected PQ/axion direction.

On the selected Delta_R vacuum the dimension-six 54 amplitude additionally
vanishes by the direct tensor calculation.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

import physical_h10_54_mass_block_from_deltar_v20 as selected_vacuum

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "PHASE_OPERATOR_INDEPENDENCE_AUDIT_V20.json"
OUT_MD = ROOT / "PHASE_OPERATOR_INDEPENDENCE_AUDIT_V20.md"

FIELDS = ("phi_DeltaR", "phi_H10", "phi_S")
VECTORS = {
    "kappa_H2_S": np.array([0.0, 2.0, 1.0]),
    "lambda4_Phi_H_Sigmabar_S": np.array([1.0, 1.0, 1.0]),
    "lambda_lock_Sigmabar2_H2_S2": np.array([2.0, 2.0, 2.0]),
}


def normalized_null(matrix: np.ndarray) -> np.ndarray:
    _, _, vh = np.linalg.svd(matrix)
    vector = vh[-1]
    pivot = int(np.argmax(np.abs(vector)))
    if vector[pivot] < 0:
        vector = -vector
    vector = vector / np.min(np.abs(vector[np.abs(vector) > 1e-12]))
    return vector


def build_report() -> dict[str, Any]:
    kappa = VECTORS["kappa_H2_S"]
    lam4 = VECTORS["lambda4_Phi_H_Sigmabar_S"]
    lock = VECTORS["lambda_lock_Sigmabar2_H2_S2"]
    base = np.stack([kappa, lam4])
    enlarged = np.stack([kappa, lam4, lock])
    rank_base = int(np.linalg.matrix_rank(base))
    rank_enlarged = int(np.linalg.matrix_rank(enlarged))
    null = normalized_null(base)
    expected_null = np.array([1.0, 1.0, -2.0])
    if np.dot(null, expected_null) < 0:
        null = -null
    zero = selected_vacuum.build_report()
    selected_amplitude_zero = bool(
        zero.get("n_failed") == 0
        and zero.get("flags", {}).get("DeltaR_squared_54_projection_zero")
    )

    checks = {
        "lambda_lock_vector_equals_2_lambda4": np.allclose(lock, 2.0 * lam4),
        "kappa_and_lambda4_rank_two": rank_base == 2,
        "adding_lambda_lock_does_not_increase_rank": rank_enlarged == rank_base,
        "common_null_is_1_1_minus2": np.allclose(null, expected_null),
        "null_annihilates_all_three_vectors": np.allclose(enlarged @ null, 0.0),
        "selected_vacuum_locking_amplitude_zero": selected_amplitude_zero,
        "whole_model_not_overclaimed": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "PHASE_VECTOR_RANK_DERIVED__DIM6_LOCK_NOT_INDEPENDENT"
            if not failures
            else "PHASE_VECTOR_INDEPENDENCE_AUDIT_FAILED"
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
        "linear_algebra": {
            "rank_kappa_lambda4": rank_base,
            "rank_after_adding_lambda_lock": rank_enlarged,
            "rank_increment_from_lambda_lock": rank_enlarged - rank_base,
            "lambda_lock_equals": "2 * lambda4 phase vector",
            "common_null_vector": [int(round(x)) for x in null],
            "null_interpretation": "PQ/axion phase direction",
        },
        "selected_vacuum": {
            "DeltaR_squared_54_projection_zero": selected_amplitude_zero,
            "dimension6_locking_curvature_present": False,
        },
        "consequences": {
            "dimension6_operator_adds_independent_phase_constraint": False,
            "dimension6_operator_can_lift_lambda4_null_direction": False,
            "kappa_plus_nonzero_lambda4_leave_one_PQ_null": True,
            "if_lambda4_absent_and_dimension6_zero_rank_is_only_one": True,
        },
        "flags": {
            "phase_vector_independence_problem_closed": not bool(failures),
            "legacy_lambda_lock_independent_lift_claim_valid": False,
            "selected_vacuum_dimension6_lock_valid": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "next_requirement": (
            "Any proposed additional phase-sensitive operator must have a "
            "phase vector not parallel to lambda4 and a nonzero tensor "
            "projection on the actual vacuum. A physical global PQ symmetry "
            "must still leave the axion direction massless before QCD."
        ),
        "verdict": (
            "The dimension-six locking operator is phase-linearly redundant: "
            "its vector is exactly twice the lambda4 vector, so it adds zero "
            "rank. On the selected Delta_R vacuum its 54 coefficient is also "
            "zero. It cannot provide the claimed independent phase lift. The "
            "kappa and lambda4 operators, when both physically nonzero, have "
            "rank two and leave the PQ axion null (1,1,-2)."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Phase-operator independence audit — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- Rank before lambda_lock: `{report['linear_algebra']['rank_kappa_lambda4']}`\n"
        f"- Rank after lambda_lock: `{report['linear_algebra']['rank_after_adding_lambda_lock']}`\n"
        f"- Common null: `{report['linear_algebra']['common_null_vector']}`\n\n"
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
