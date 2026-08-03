#!/usr/bin/env python3
"""Profile the constrained v20 flavour objective versus tan(beta).

The existing flavour fitter parameterizes

    tan(beta) = 1.5 + 48.5 sigmoid(x_0),

so it only explores 1.5 < tan(beta) < 50.  This script fixes tan(beta) at
selected values and minimizes the remaining twelve nuisance parameters at
the exact v20 scale v_R=v_S.  It tests whether the committed boundary point
tan(beta)~1.5 is a demonstrated unique numerical prediction.

This remains a benchmark profile of the repository's approximate objective,
not a global precision SO(10) flavour analysis.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

import flavour_clebsch_fit_v20 as flavour
import full_fermion_matching_v20 as matching


ROOT = Path(__file__).resolve().parent
DEFAULT_GRID = (1.500001, 2.0, 5.0, 10.0, 20.0, 30.0, 41.3, 49.0)


def beta_coordinate(tan_beta: float) -> float:
    """Inverse of the fitter's bounded logistic tan(beta) coordinate."""
    if not 1.5 < tan_beta < 50.0:
        raise ValueError("the current fitter only parameterizes 1.5 < tan_beta < 50")
    fraction = (tan_beta - 1.5) / 48.5
    return math.log(fraction / (1.0 - fraction))


def assemble_params(tan_beta: float, nuisance: np.ndarray) -> np.ndarray:
    nuisance = np.asarray(nuisance, dtype=float)
    if nuisance.shape != (12,):
        raise ValueError("nuisance must contain 12 parameters")
    return np.concatenate(([beta_coordinate(tan_beta)], nuisance))


def fixed_beta_chi2(
    nuisance: np.ndarray,
    tan_beta: float,
    v_r: float = flavour.VS,
) -> float:
    return flavour.chi2_from_params(assemble_params(tan_beta, nuisance), v_r)[0]


def optimize_fixed_beta(
    tan_beta: float,
    *,
    v_r: float = flavour.VS,
    seed: int = 20,
    starts: int = 6,
    maxiter: int = 5000,
    warm_starts: list[np.ndarray] | None = None,
) -> dict:
    """Multi-start Nelder-Mead profile point at fixed tan(beta)."""
    rng = np.random.default_rng(seed)
    initial: list[np.ndarray] = []
    if warm_starts:
        initial.extend(np.asarray(x, dtype=float).copy() for x in warm_starts)
    for _ in range(starts):
        x = rng.normal(size=12)
        # params[12] in the full vector is nuisance[-1] (Type-II exponent).
        x[-1] = rng.uniform(-13.0, -7.0)
        initial.append(x)

    best: tuple[float, np.ndarray, dict] | None = None
    for x0 in initial:
        result = minimize(
            lambda x: fixed_beta_chi2(x, tan_beta, v_r),
            x0,
            method="Nelder-Mead",
            options={
                "maxiter": maxiter,
                "xatol": 1e-9,
                "fatol": 1e-9,
            },
        )
        params = assemble_params(tan_beta, result.x)
        chi2, detail = flavour.chi2_from_params(params, v_r)
        if best is None or chi2 < best[0]:
            best = (float(chi2), result.x.copy(), detail)

    assert best is not None
    chi2, nuisance, detail = best
    obs = detail.get("observables", {})
    coeff = matching.coefficients_at_tan_beta(tan_beta)
    return {
        "tan_beta": tan_beta,
        "v_r_GeV": v_r,
        "chi2": chi2,
        "nuisance": nuisance.tolist(),
        "pulls": detail.get("pulls", {}),
        "observables": {
            key: obs.get(key)
            for key in (
                "sum_mnu_eV",
                "dm21_eV2",
                "dm31_eV2",
                "sin2_th12",
                "sin2_th23",
                "sin2_th13",
                "delta_cp_deg",
                "y10_max",
                "y126_max",
                "up_clebsch_mismatch",
                "perturbative_4pi",
            )
        },
        "fermion_coefficients": {
            "C_e": coeff["C_e"],
            "C_p_central": coeff["C_p_central"],
            "C_n_central": coeff["C_n_central"],
        },
    }


def run_profile(
    *,
    grid: tuple[float, ...] = DEFAULT_GRID,
    seed: int = 20260803,
    starts: int = 6,
    maxiter: int = 5000,
) -> dict:
    rows: list[dict] = []
    warm: list[np.ndarray] = []
    flavour_json = ROOT / "flavour_clebsch_fit_v20.json"
    reference: dict | None = None
    if flavour_json.exists():
        saved = json.loads(flavour_json.read_text(encoding="utf-8"))
        reference = saved.get("v20_single_scale_point")
        params = (reference or {}).get("params")
        if isinstance(params, list) and len(params) == 13:
            warm.append(np.asarray(params[1:], dtype=float))
    for index, tan_beta in enumerate(grid):
        row = optimize_fixed_beta(
            tan_beta,
            seed=seed + 101 * index,
            starts=starts,
            maxiter=maxiter,
            warm_starts=warm[-2:],
        )
        rows.append(row)
        warm.append(np.asarray(row["nuisance"], dtype=float))
    # Deep-polish the best profile point.  This deterministic continuation is
    # important because the objective has broad saturated tanh/phase valleys.
    initial_best = min(rows, key=lambda row: row["chi2"])
    polished = optimize_fixed_beta(
        initial_best["tan_beta"],
        seed=seed + 99991,
        starts=0,
        maxiter=maxiter * 6,
        warm_starts=[np.asarray(initial_best["nuisance"], dtype=float)],
    )
    if polished["chi2"] < initial_best["chi2"]:
        rows[rows.index(initial_best)] = polished
    best = min(rows, key=lambda row: row["chi2"])
    low = min(rows, key=lambda row: abs(row["tan_beta"] - 1.500001))
    reference = reference or {
        "observables": {"tan_beta": None},
        "chi2": float("inf"),
    }
    reference_tan_beta = reference.get("observables", {}).get("tan_beta")
    materially_distinct = bool(
        reference_tan_beta is not None
        and abs(best["tan_beta"] - reference_tan_beta) > 1.0
    )
    improves_reference = best["chi2"] + 1e-6 < float(reference["chi2"])
    return {
        "status": "PROFILE_COMPLETE",
        "method": (
            "fixed-tan(beta) multi-start Nelder-Mead profile of the repository's "
            "12-nuisance constrained 10+126 objective at v_R=v_S"
        ),
        "grid": list(grid),
        "starts_per_point": starts,
        "maxiter": maxiter,
        "corrected_multistart_reference": {
            "tan_beta": reference_tan_beta,
            "chi2": reference["chi2"],
        },
        "points": rows,
        "best_profile_point": best,
        "low_boundary_profile_point": low,
        "corrected_profile_improves_reference": bool(improves_reference),
        "profile_best_materially_distinct_tan_beta": materially_distinct,
        "any_profile_point_viable_chi2_lt_30": any(
            row["chi2"] < 30.0 for row in rows
        ),
        "unique_tan_beta_demonstrated": False,
        "reason": (
            "The corrected Takagi/charged-lepton-basis objective is bounded by "
            "construction, underconstrained, omits CKM and common-scale RG "
            "inputs, and does not establish a unique physical tan(beta)."
        ),
    }


def write_markdown(report: dict) -> str:
    best = report["best_profile_point"]
    lines = [
        "# tan(beta) profile at the exact v20 scale",
        "",
        f"**Status:** `{report['status']}`",
        "",
        f"- Unique tan(beta) demonstrated: **{report['unique_tan_beta_demonstrated']}**",
        f"- Profile improves corrected multistart reference: **{report['corrected_profile_improves_reference']}**",
        f"- Profile best has materially distinct tan(beta): **{report['profile_best_materially_distinct_tan_beta']}**",
        f"- Any fixed-v_R profile point with chi2<30: **{report['any_profile_point_viable_chi2_lt_30']}**",
        f"- Best profile point: tan(beta)={best['tan_beta']:.6g}, chi2={best['chi2']:.6g}",
        "",
        "| tan(beta) | chi2 | perturbative | aligned C_e | aligned C_p central | aligned C_n central |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["points"]:
        c = row["fermion_coefficients"]
        lines.append(
            f"| {row['tan_beta']:.6g} | {row['chi2']:.6g} | "
            f"{row['observables']['perturbative_4pi']} | {c['C_e']:.7g} | "
            f"{c['C_p_central']:.7g} | {c['C_n_central']:.7g} |"
        )
    lines += [
        "",
        "## Scope",
        "",
        report["reason"],
        "",
        "The coefficient columns assume aligned projected current and are not",
        "full-v20 portal-matched predictions.",
        "",
        "This profiles the repository's constrained benchmark objective; it is not",
        "a complete global SO(10) flavour fit with full threshold/RG treatment.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    print("=== FIXED-v_R TAN(BETA) PROFILE ===", flush=True)
    report = run_profile()
    ROOT.joinpath("TAN_BETA_PROFILE_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("TAN_BETA_PROFILE_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    best = report["best_profile_point"]
    print(
        json.dumps(
            {
                "status": report["status"],
                "best_tan_beta": best["tan_beta"],
                "best_chi2": best["chi2"],
                "corrected_profile_improves_reference": report[
                    "corrected_profile_improves_reference"
                ],
                "any_profile_point_viable_chi2_lt_30": report[
                    "any_profile_point_viable_chi2_lt_30"
                ],
                "unique_tan_beta_demonstrated": False,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
