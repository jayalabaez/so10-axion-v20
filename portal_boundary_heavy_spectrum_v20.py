#!/usr/bin/env python3
"""Resolve the physical heavy singular spectrum on the conditional portal ray.

The bare D=y_Q v_Phi/sqrt(2) entry is not a physical mass eigenvalue when the
S-induced B and C portals are large.  This module computes the three nonzero
singular values of the full 3x6 mass matrix [[A,C],[B,D]] and solves the point
where the lightest heavy singular value equals v_S.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Callable

import numpy as np

import na62_pointwise_limit_v20 as na62
import physical_cf_matching_v20 as physical
import portal_constraint_ray_v20 as ray
import portal_tensors_abcd_v20 as portals
import twist_massless_limit_v20 as twist

ROOT = Path(__file__).resolve().parent


def heavy_spectrum(y_q: float) -> dict[str, Any]:
    block = ray.portal_block(y_q)
    top = np.hstack([np.asarray(block["A"], dtype=complex), np.asarray(block["C"], dtype=complex)])
    bottom = np.hstack([
        np.asarray(block["B"], dtype=complex),
        np.asarray([[block["D"]]], dtype=complex),
    ])
    matrix = np.vstack([top, bottom])
    singular = np.sort(np.linalg.svd(matrix, compute_uv=False))
    if singular.shape != (3,) or not np.all(np.isfinite(singular)) or np.min(singular) <= 0.0:
        raise ValueError("full heavy mass matrix must have three positive singular values")
    bare_d = abs(complex(block["D"]))
    return {
        "y_Q": float(y_q),
        "bare_D_GeV": float(bare_d),
        "bare_D_over_vS": float(bare_d / portals.VS),
        "heavy_singular_values_GeV_ascending": [float(x) for x in singular],
        "lightest_heavy_singular_GeV": float(singular[0]),
        "lightest_heavy_over_vS": float(singular[0] / portals.VS),
        "heaviest_heavy_singular_GeV": float(singular[-1]),
        "matrix_rank": int(np.linalg.matrix_rank(matrix)),
        "mass_matrix_shape": list(matrix.shape),
    }


def _bisect_log(function: Callable[[float], float], lower: float, upper: float) -> float:
    if lower <= 0.0 or upper <= lower:
        raise ValueError("invalid positive root interval")
    f_lower = function(lower)
    f_upper = function(upper)
    if f_lower == 0.0:
        return lower
    if f_upper == 0.0:
        return upper
    if f_lower * f_upper > 0.0:
        raise ValueError("root is not bracketed")
    lo, hi = math.log10(lower), math.log10(upper)
    for _ in range(120):
        mid = 0.5 * (lo + hi)
        y = 10.0**mid
        f_mid = function(y)
        if abs(f_mid) <= 1.0e-10:
            return y
        if f_lower * f_mid <= 0.0:
            hi = mid
            f_upper = f_mid
        else:
            lo = mid
            f_lower = f_mid
    return 10.0 ** (0.5 * (lo + hi))


def solve_lightest_equals_vS(
    *, y_min: float = ray.DEFAULT_Y_MIN, y_max: float = ray.DEFAULT_Y_MAX, n_grid: int = 241
) -> dict[str, Any]:
    grid = np.logspace(math.log10(y_min), math.log10(y_max), n_grid)
    rows = [heavy_spectrum(float(y)) for y in grid]
    ratios = [float(row["lightest_heavy_over_vS"]) for row in rows]
    monotonic = all(
        right >= left * (1.0 - 1.0e-8) - 1.0e-15
        for left, right in zip(ratios, ratios[1:])
    )
    brackets: list[tuple[float, float]] = []
    for left, right in zip(rows, rows[1:]):
        f_left = float(left["lightest_heavy_over_vS"]) - 1.0
        f_right = float(right["lightest_heavy_over_vS"]) - 1.0
        if f_left == 0.0:
            brackets.append((float(left["y_Q"]), float(left["y_Q"])))
        elif f_left * f_right < 0.0:
            brackets.append((float(left["y_Q"]), float(right["y_Q"])))
    roots = []
    for lower, upper in brackets:
        if lower == upper:
            y_root = lower
        else:
            y_root = _bisect_log(
                lambda y: heavy_spectrum(y)["lightest_heavy_over_vS"] - 1.0,
                lower,
                upper,
            )
        roots.append(heavy_spectrum(y_root))
    return {
        "n_crossings": len(roots),
        "monotonic_nondecreasing": monotonic,
        "crossing_brackets": [[a, b] for a, b in brackets],
        "crossings": roots,
        "unique_ordering_boundary": roots[0] if monotonic and len(roots) == 1 else None,
        "low_endpoint": rows[0],
        "high_endpoint": rows[-1],
    }


def build_report() -> dict[str, Any]:
    ray_report = ray.build_report()
    boundary = ray_report["form_factor_boundary_band"]["f0_central"]
    y_boundary = float(boundary["y_Q"])
    spectrum_at_na62 = heavy_spectrum(y_boundary)
    ordering = solve_lightest_equals_vS()
    ordering_boundary = ordering["unique_ordering_boundary"]

    bases = physical.flavour_mass_bases()
    anchor = na62.load_anchor()
    na62_limit = float(
        na62.observed_limit_at_mass(na62.TARGET_MASS_MEV, anchor)["observed_br_ul_90cl"]
    )
    twist_limit = min(
        float(row["branching_ratio_upper_limit_90cl"])
        for row in twist.load_limits()["limits"]
    )
    ordered_point = None
    if ordering_boundary is not None:
        ordered_point = ray.evaluate_point(
            float(ordering_boundary["y_Q"]),
            bases,
            f0=ray.rates.F0_KPI_AT_ZERO,
            na62_limit=na62_limit,
            twist_limit=twist_limit,
        )

    checks = {
        "full_mass_matrix_rank_three": spectrum_at_na62["matrix_rank"] == 3,
        "bare_D_not_equal_lightest_singular": not math.isclose(
            spectrum_at_na62["bare_D_GeV"],
            spectrum_at_na62["lightest_heavy_singular_GeV"],
            rel_tol=1.0e-3,
        ),
        "spectrum_ordering_curve_monotonic": ordering["monotonic_nondecreasing"],
        "unique_lightest_equals_vS_boundary": ordering_boundary is not None,
        "ordering_boundary_rechecks": ordering_boundary is not None
        and math.isclose(
            float(ordering_boundary["lightest_heavy_over_vS"]), 1.0, rel_tol=1.0e-8
        ),
        "ordered_threshold_point_survives_NA62": ordered_point is not None
        and ordered_point["NA62_survives"],
        "ordered_threshold_point_survives_TWIST": ordered_point is not None
        and ordered_point["TWIST_survives_strongest_published_case"],
        "physical_Q_like_eigenstate_not_overidentified": True,
        "piecewise_threshold_matching_not_claimed_complete": True,
    }
    failures = [name for name, ok in checks.items() if not ok]
    return {
        "status": (
            "FULL_HEAVY_SINGULAR_SPECTRUM_RESOLVED__ORDERING_BOUNDARY_SOLVED__PIECEWISE_MATCHING_OPEN"
            if not failures
            else "HEAVY_SPECTRUM_BOUNDARY_AUDIT_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "na62_survival_boundary": {
            "y_Q": y_boundary,
            "rate_result": boundary,
            "heavy_spectrum": spectrum_at_na62,
        },
        "lightest_heavy_equals_vS_scan": ordering,
        "ordered_threshold_point_rate_result": ordered_point,
        "flag": {
            "bare_D_is_not_a_physical_mass_eigenvalue": True,
            "full_three_heavy_singular_values_computed": True,
            "lightest_heavy_equals_vS_boundary_solved": ordering_boundary is not None,
            "all_heavy_singular_values_above_vS_at_ordered_point": ordering_boundary is not None,
            "ordered_point_survives_NA62": bool(ordered_point and ordered_point["NA62_survives"]),
            "ordered_point_survives_TWIST": bool(
                ordered_point and ordered_point["TWIST_survives_strongest_published_case"]
            ),
            "individual_Q_like_mass_eigenstate_uniquely_identified": False,
            "piecewise_threshold_matching_complete": False,
            "whole_v20_model_excluded": False,
        },
        "interpretation": (
            "The rate boundary is a valid boundary in the input Yukawa y_Q, but "
            "D=y_Q v_Phi/sqrt(2) must not be called the physical Q mass when B/C "
            "mixing is large. The basis-independent three-heavy singular spectrum "
            "is now computed. A separate conditional y_Q point enforces the "
            "lightest heavy singular value >= v_S and is checked against NA62 and "
            "TWIST. Full piecewise component matching remains open."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    na62_s = report["na62_survival_boundary"]["heavy_spectrum"]
    ordering = report["lightest_heavy_equals_vS_scan"]["unique_ordering_boundary"]
    lines = [
        "# Heavy spectrum at the conditional portal boundary — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        f"- NA62 boundary y_Q: {report['na62_survival_boundary']['y_Q']:.12e}",
        f"- Bare D at NA62 boundary: {na62_s['bare_D_GeV']:.12e} GeV",
        f"- Lightest heavy singular value: {na62_s['lightest_heavy_singular_GeV']:.12e} GeV",
        f"- Lightest heavy / v_S: {na62_s['lightest_heavy_over_vS']:.9g}",
    ]
    if ordering is not None:
        lines += [
            f"- y_Q where lightest heavy = v_S: {ordering['y_Q']:.12e}",
            f"- Bare D there: {ordering['bare_D_GeV']:.12e} GeV",
        ]
    lines += ["", "## Interpretation", "", report["interpretation"], ""]
    return "\n".join(lines)


def main() -> int:
    report = build_report()
    ROOT.joinpath("PORTAL_BOUNDARY_HEAVY_SPECTRUM_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("PORTAL_BOUNDARY_HEAVY_SPECTRUM_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(json.dumps({
        "status": report["status"],
        "n_failed": report["n_failed"],
        "na62_boundary_spectrum": report["na62_survival_boundary"]["heavy_spectrum"],
        "ordering_boundary": report["lightest_heavy_equals_vS_scan"]["unique_ordering_boundary"],
        "ordered_point": report["ordered_threshold_point_rate_result"],
        "flags": report["flag"],
    }, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
