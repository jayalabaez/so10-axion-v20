#!/usr/bin/env python3
"""Validate scientific invariants of the generated fixed-v_R tan(beta) profile.

The high-dimensional Nelder-Mead trajectory is not byte-for-byte reproducible
across BLAS/LAPACK runner details, even with fixed RNG seeds. This verifier
checks the stable scientific content instead of comparing one optimizer
trajectory verbatim. Saved witnesses are independently reevaluated with a
small relative tolerance that covers measured cross-run linear-algebra drift
while remaining far below any physics decision threshold.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import tan_beta_profile_v20 as profile


ROOT = Path(__file__).resolve().parent
REPORT_PATH = ROOT / "TAN_BETA_PROFILE_V20_VERDICT.json"
EXPECTED_GRID = tuple(float(x) for x in profile.DEFAULT_GRID)
MAX_WITNESS_REL_DRIFT = 2.0e-3
MAX_WITNESS_ABS_DRIFT = 1.0e-6


def _finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(float(value))


def validate_report(report: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if report.get("status") != "PROFILE_COMPLETE":
        errors.append("status must be PROFILE_COMPLETE")

    points = report.get("points")
    if not isinstance(points, list) or len(points) != len(EXPECTED_GRID):
        return errors + [
            f"points must contain exactly {len(EXPECTED_GRID)} profile rows"
        ]

    seen_grid: list[float] = []
    ce: list[float] = []
    cp: list[float] = []
    cn: list[float] = []

    for index, row in enumerate(points):
        if not isinstance(row, dict):
            errors.append(f"point {index} is not an object")
            continue

        tan_beta = row.get("tan_beta")
        chi2 = row.get("chi2")
        v_r = row.get("v_r_GeV")
        nuisance = row.get("nuisance")

        if not _finite_number(tan_beta) or not 1.5 < float(tan_beta) < 50.0:
            errors.append(f"point {index} has invalid tan_beta")
            continue
        seen_grid.append(float(tan_beta))

        if not _finite_number(chi2) or float(chi2) < 0.0:
            errors.append(f"point {index} has invalid chi2")
            continue
        if not _finite_number(v_r) or float(v_r) <= 0.0:
            errors.append(f"point {index} has invalid v_r_GeV")
            continue
        if not isinstance(nuisance, list) or len(nuisance) != 12:
            errors.append(f"point {index} must contain 12 nuisance parameters")
            continue
        if not all(_finite_number(value) for value in nuisance):
            errors.append(f"point {index} nuisance vector is not finite")
            continue

        saved_chi2 = float(chi2)
        recomputed = float(
            profile.fixed_beta_chi2(
                np.asarray(nuisance, dtype=float),
                float(tan_beta),
                float(v_r),
            )
        )
        if not math.isclose(
            recomputed,
            saved_chi2,
            rel_tol=MAX_WITNESS_REL_DRIFT,
            abs_tol=MAX_WITNESS_ABS_DRIFT,
        ):
            scale = max(abs(saved_chi2), abs(recomputed), 1.0)
            relative_drift = abs(recomputed - saved_chi2) / scale
            errors.append(
                f"point {index} witness exceeds recomputation tolerance: "
                f"saved={saved_chi2:.12g}, recomputed={recomputed:.12g}, "
                f"relative_drift={relative_drift:.3e}"
            )

        coeff = row.get("fermion_coefficients")
        if not isinstance(coeff, dict):
            errors.append(f"point {index} lacks fermion coefficients")
            continue
        values = (
            coeff.get("C_e"),
            coeff.get("C_p_central"),
            coeff.get("C_n_central"),
        )
        if not all(_finite_number(value) for value in values):
            errors.append(f"point {index} has non-finite fermion coefficients")
            continue
        ce.append(float(values[0]))
        cp.append(float(values[1]))
        cn.append(float(values[2]))

    if len(seen_grid) == len(EXPECTED_GRID):
        for actual, expected in zip(seen_grid, EXPECTED_GRID):
            if not math.isclose(actual, expected, rel_tol=0.0, abs_tol=1e-12):
                errors.append(
                    f"profile grid drifted: expected {EXPECTED_GRID}, got {seen_grid}"
                )
                break

    valid_points = [
        row
        for row in points
        if isinstance(row, dict) and _finite_number(row.get("chi2"))
    ]
    if not valid_points:
        return errors + ["profile has no finite chi2 points"]

    computed_best = min(valid_points, key=lambda row: float(row["chi2"]))
    saved_best = report.get("best_profile_point")
    if not isinstance(saved_best, dict):
        errors.append("best_profile_point is missing")
    else:
        saved_tb = saved_best.get("tan_beta")
        saved_chi2 = saved_best.get("chi2")
        if not _finite_number(saved_tb) or not _finite_number(saved_chi2):
            errors.append("best_profile_point is not finite")
        else:
            if not math.isclose(
                float(saved_tb),
                float(computed_best["tan_beta"]),
                rel_tol=0.0,
                abs_tol=1e-12,
            ):
                errors.append("saved best tan_beta is not the profile minimum")
            if not math.isclose(
                float(saved_chi2),
                float(computed_best["chi2"]),
                rel_tol=1e-10,
                abs_tol=1e-8,
            ):
                errors.append("saved best chi2 is not the profile minimum")

    best_tb = float(computed_best["tan_beta"])
    best_chi2 = float(computed_best["chi2"])
    if not math.isclose(best_tb, 2.0, rel_tol=0.0, abs_tol=1e-12):
        errors.append(f"known best grid basin moved away from tan_beta=2: {best_tb}")
    if best_chi2 < 30.0:
        errors.append(
            f"single-scale benchmark became nominally viable: best chi2={best_chi2}"
        )
    if best_chi2 > 150.0:
        errors.append(
            f"optimizer failed to recover the known rejecting basin: best chi2={best_chi2}"
        )

    computed_viable = any(float(row["chi2"]) < 30.0 for row in valid_points)
    if bool(report.get("any_profile_point_viable_chi2_lt_30")) != computed_viable:
        errors.append("viability flag disagrees with the profile rows")
    if computed_viable:
        errors.append("a fixed-v_R profile point has chi2<30")

    if report.get("unique_tan_beta_demonstrated") is not False:
        errors.append("profile must not claim a unique tan_beta prediction")

    if len(ce) == len(points):
        if max(ce) - min(ce) <= 1e-2:
            errors.append("C_e does not vary materially across the profile")
        if max(cp) - min(cp) <= 1e-2:
            errors.append("C_p does not vary materially across the profile")
        if max(cn) - min(cn) <= 1e-2:
            errors.append("C_n does not vary materially across the profile")

    return errors


def main() -> int:
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    errors = validate_report(report)
    result = {
        "status": "PASS" if not errors else "FAIL",
        "n_errors": len(errors),
        "errors": errors,
        "best_tan_beta": report.get("best_profile_point", {}).get("tan_beta"),
        "best_chi2": report.get("best_profile_point", {}).get("chi2"),
        "max_witness_relative_drift": MAX_WITNESS_REL_DRIFT,
        "scientific_conclusion": (
            "The constrained v_R=v_S profile remains non-viable and does not "
            "establish a unique tan(beta)."
        ),
    }
    print(json.dumps(result, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
