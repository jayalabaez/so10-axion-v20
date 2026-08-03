#!/usr/bin/env python3
"""Solve the conditional NA62 survival boundary on one v20 portal ray.

The ray keeps the displayed generation-dependent texture fixed,

    lam_Q_F = (1, 0.01, 0), lam_Q_R = 0.3, lam_S_Q_Rbar = 0.2,

and varies only the positive Phi-sector mass Yukawa y_Q.  This is a
one-dimensional conditional diagnostic.  It is not a scan of the full portal
parameter space, a UV posterior, or a whole-model exclusion.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Callable

import numpy as np

import channel_fcnc_rates_v20 as rates
import na62_pointwise_limit_v20 as na62
import physical_cf_matching_v20 as physical
import portal_tensors_abcd_v20 as portals
import twist_massless_limit_v20 as twist

ROOT = Path(__file__).resolve().parent
TEXTURE = {
    "lam_Q_F": (1.0, 0.01, 0.0),
    "lam_Q_R": 0.3,
    "lam_S_Q_Rbar": 0.2,
}
DEFAULT_Y_MIN = 1.0e-8
DEFAULT_Y_MAX = 1.0e-2
DEFAULT_N_GRID = 241


def _complex_from_payload(value: dict[str, Any]) -> complex:
    return complex(float(value["real"]), float(value["imag"]))


def portal_block(y_q: float) -> dict[str, Any]:
    if not math.isfinite(y_q) or y_q <= 0.0:
        raise ValueError("y_Q must be finite and positive")
    return portals.build_abcd(
        portals.PortalCouplings(
            y_Q=y_q,
            lam_Q_F=TEXTURE["lam_Q_F"],
            lam_Q_R=TEXTURE["lam_Q_R"],
            lam_S_Q_Rbar=TEXTURE["lam_S_Q_Rbar"],
        )
    )


def evaluate_point(
    y_q: float,
    bases: dict[str, Any],
    *,
    f0: float = rates.F0_KPI_AT_ZERO,
    na62_limit: float,
    twist_limit: float,
) -> dict[str, Any]:
    scenario = rates.scenario_rates(
        f"generation_dependent_yQ_{y_q:.9e}", portal_block(y_q), bases
    )
    k_left = _complex_from_payload(scenario["mass_basis_couplings"]["K_dL_d_s"])
    k_right = _complex_from_payload(scenario["mass_basis_couplings"]["K_dR_d_s"])
    gamma_k = rates.kaon_to_pion_a_width(k_left, k_right, f0=f0)
    br_k = gamma_k / rates.total_width_from_lifetime(rates.TAU_K_CHARGED_S)
    br_mu = float(scenario["mu_to_e_a"]["branching_ratio"])
    return {
        "y_Q": float(y_q),
        "M_Q_GeV": float(abs(y_q) * portals.VPHI / math.sqrt(2.0)),
        "M_Q_over_vS": float(abs(y_q) * portals.VPHI / (math.sqrt(2.0) * portals.VS)),
        "epsilon_QF": [
            float(abs(lam) * portals.VS / (abs(y_q) * portals.VPHI))
            for lam in TEXTURE["lam_Q_F"]
        ],
        "epsilon_QR": float(abs(TEXTURE["lam_Q_R"]) * portals.VS / (abs(y_q) * portals.VPHI)),
        "epsilon_SQRbar": float(abs(TEXTURE["lam_S_Q_Rbar"]) * portals.VS / (abs(y_q) * portals.VPHI)),
        "K_L_plus_K_R_abs": float(abs(k_left + k_right)),
        "BR_K_to_pi_a": float(br_k),
        "NA62_observed_limit_90cl": float(na62_limit),
        "NA62_ratio": float(br_k / na62_limit),
        "NA62_survives": bool(br_k <= na62_limit),
        "BR_mu_to_e_a": br_mu,
        "TWIST_strongest_limit_90cl": float(twist_limit),
        "TWIST_ratio": float(br_mu / twist_limit),
        "TWIST_survives_strongest_published_case": bool(br_mu <= twist_limit),
        "f0": float(f0),
    }


def _crossing_intervals(rows: list[dict[str, Any]], key: str) -> list[tuple[float, float]]:
    intervals: list[tuple[float, float]] = []
    for left, right in zip(rows, rows[1:]):
        f_left = float(left[key]) - 1.0
        f_right = float(right[key]) - 1.0
        if f_left == 0.0:
            intervals.append((float(left["y_Q"]), float(left["y_Q"])))
        elif f_left * f_right < 0.0:
            intervals.append((float(left["y_Q"]), float(right["y_Q"])))
    if rows and float(rows[-1][key]) == 1.0:
        intervals.append((float(rows[-1]["y_Q"]), float(rows[-1]["y_Q"])))
    return intervals


def _bisect_log(
    function: Callable[[float], float],
    lower: float,
    upper: float,
    *,
    max_iter: int = 100,
    ratio_tolerance: float = 1.0e-10,
) -> float:
    if lower <= 0.0 or upper <= 0.0 or lower > upper:
        raise ValueError("invalid positive bisection interval")
    if lower == upper:
        return lower
    f_lower = function(lower) - 1.0
    f_upper = function(upper) - 1.0
    if f_lower == 0.0:
        return lower
    if f_upper == 0.0:
        return upper
    if f_lower * f_upper > 0.0:
        raise ValueError("bisection interval does not bracket a crossing")
    lo = math.log10(lower)
    hi = math.log10(upper)
    for _ in range(max_iter):
        mid = 0.5 * (lo + hi)
        y_mid = 10.0**mid
        f_mid = function(y_mid) - 1.0
        if abs(f_mid) <= ratio_tolerance:
            return y_mid
        if f_lower * f_mid <= 0.0:
            hi = mid
            f_upper = f_mid
        else:
            lo = mid
            f_lower = f_mid
    return 10.0 ** (0.5 * (lo + hi))


def _monotonic_nonincreasing(values: list[float], *, relative_slack: float = 1.0e-8) -> bool:
    return all(
        right <= left * (1.0 + relative_slack) + 1.0e-15
        for left, right in zip(values, values[1:])
    )


def scan_ray(
    *,
    y_min: float = DEFAULT_Y_MIN,
    y_max: float = DEFAULT_Y_MAX,
    n_grid: int = DEFAULT_N_GRID,
    f0: float = rates.F0_KPI_AT_ZERO,
) -> dict[str, Any]:
    if y_min <= 0.0 or y_max <= y_min or n_grid < 3:
        raise ValueError("invalid portal-ray scan configuration")
    bases = physical.flavour_mass_bases()
    anchor = na62.load_anchor()
    limit_result = na62.observed_limit_at_mass(na62.TARGET_MASS_MEV, anchor)
    na62_limit = float(limit_result["observed_br_ul_90cl"])
    twist_limits = twist.load_limits()
    twist_limit = min(
        float(row["branching_ratio_upper_limit_90cl"])
        for row in twist_limits["limits"]
    )
    y_grid = np.logspace(math.log10(y_min), math.log10(y_max), n_grid)
    rows = [
        evaluate_point(
            float(y), bases, f0=f0, na62_limit=na62_limit, twist_limit=twist_limit
        )
        for y in y_grid
    ]

    def ratio_at(y_q: float) -> float:
        return float(
            evaluate_point(
                y_q, bases, f0=f0, na62_limit=na62_limit, twist_limit=twist_limit
            )["NA62_ratio"]
        )

    intervals = _crossing_intervals(rows, "NA62_ratio")
    roots = [_bisect_log(ratio_at, lo, hi) for lo, hi in intervals]
    root_rows = [
        evaluate_point(
            root, bases, f0=f0, na62_limit=na62_limit, twist_limit=twist_limit
        )
        for root in roots
    ]
    ratios = [float(row["NA62_ratio"]) for row in rows]
    monotonic = _monotonic_nonincreasing(ratios)
    unique_survival_boundary = root_rows[0] if monotonic and len(root_rows) == 1 else None
    return {
        "configuration": {
            "y_Q_min": y_min,
            "y_Q_max": y_max,
            "n_grid": n_grid,
            "f0": f0,
            "texture": {
                "lam_Q_F": list(TEXTURE["lam_Q_F"]),
                "lam_Q_R": TEXTURE["lam_Q_R"],
                "lam_S_Q_Rbar": TEXTURE["lam_S_Q_Rbar"],
            },
        },
        "na62_limit": limit_result,
        "twist_strongest_published_limit_90cl": twist_limit,
        "reference_yQ_1e_minus_6": evaluate_point(
            1.0e-6, bases, f0=f0, na62_limit=na62_limit, twist_limit=twist_limit
        ),
        "low_endpoint": rows[0],
        "high_endpoint": rows[-1],
        "n_crossings": len(root_rows),
        "crossing_brackets": [[lo, hi] for lo, hi in intervals],
        "crossings": root_rows,
        "na62_ratio_monotonic_nonincreasing": monotonic,
        "unique_survival_boundary": unique_survival_boundary,
        "grid_rows": rows,
    }


def build_report() -> dict[str, Any]:
    central = scan_ray(f0=rates.F0_KPI_AT_ZERO)
    low_f0 = scan_ray(f0=rates.F0_KPI_AT_ZERO - rates.F0_KPI_UNCERTAINTY)
    high_f0 = scan_ray(f0=rates.F0_KPI_AT_ZERO + rates.F0_KPI_UNCERTAINTY)
    boundaries = {
        "f0_minus_1sigma": low_f0["unique_survival_boundary"],
        "f0_central": central["unique_survival_boundary"],
        "f0_plus_1sigma": high_f0["unique_survival_boundary"],
    }
    central_boundary = boundaries["f0_central"]
    boundary_values = [
        boundaries[name]["y_Q"] if boundaries[name] is not None else math.nan
        for name in ("f0_minus_1sigma", "f0_central", "f0_plus_1sigma")
    ]
    reference = central["reference_yQ_1e_minus_6"]
    checks = {
        "reference_point_excluded_by_NA62": not reference["NA62_survives"],
        "reference_point_survives_TWIST": reference[
            "TWIST_survives_strongest_published_case"
        ],
        "central_curve_monotonic": central["na62_ratio_monotonic_nonincreasing"],
        "central_unique_boundary_found": central_boundary is not None,
        "central_boundary_rechecks": central_boundary is not None
        and abs(float(central_boundary["NA62_ratio"]) - 1.0) < 1.0e-8,
        "high_yQ_endpoint_survives": central["high_endpoint"]["NA62_survives"],
        "f0_band_boundaries_found": all(math.isfinite(value) for value in boundary_values),
        "higher_f0_requires_no_smaller_yQ": all(
            right >= left * (1.0 - 1.0e-8)
            for left, right in zip(boundary_values, boundary_values[1:])
        ),
        "whole_model_not_called_excluded": True,
        "full_portal_space_not_called_scanned": True,
    }
    failures = [name for name, ok in checks.items() if not ok]
    return {
        "status": (
            "CONDITIONAL_PORTAL_RAY_SCANNED__NA62_SURVIVAL_BOUNDARY_SOLVED__FULL_PORTAL_SPACE_OPEN"
            if not failures
            else "PORTAL_RAY_BOUNDARY_AUDIT_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "central_scan": central,
        "form_factor_boundary_band": boundaries,
        "flag": {
            "one_dimensional_conditional_ray_scanned": True,
            "all_crossings_searched": True,
            "central_NA62_survival_boundary_solved": central_boundary is not None,
            "form_factor_uncertainty_propagated": True,
            "reference_generation_dependent_point_excluded": not reference[
                "NA62_survives"
            ],
            "reference_generation_dependent_point_survives_TWIST": reference[
                "TWIST_survives_strongest_published_case"
            ],
            "full_portal_parameter_space_scanned": False,
            "portal_yukawa_posterior_derived": False,
            "component_specific_uv_chiral_currents_derived": False,
            "full_correlated_likelihood_implemented": False,
            "whole_v20_model_excluded": False,
        },
        "interpretation": (
            "Along the explicitly fixed generation-dependent texture, varying only y_Q "
            "produces a conditional NA62 survival boundary. Points on the heavier-Q side "
            "of the verified monotonic crossing survive the pointwise kaon limit. This is "
            "not a full portal-space result because all other portal magnitudes, phases, "
            "component currents, and UV priors remain unfixed."
        ),
        "remaining_for_model_level_statement": [
            "scan all independent portal magnitudes and phases",
            "derive component-specific left/right currents through all thresholds",
            "fit or derive a UV portal-Yukawa posterior",
            "include correlated experimental and form-factor nuisance information",
        ],
    }


def write_markdown(report: dict[str, Any]) -> str:
    boundary = report["form_factor_boundary_band"]["f0_central"]
    low = report["form_factor_boundary_band"]["f0_minus_1sigma"]
    high = report["form_factor_boundary_band"]["f0_plus_1sigma"]
    reference = report["central_scan"]["reference_yQ_1e_minus_6"]
    lines = [
        "# Conditional NA62 portal-ray boundary — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        "## Fixed ray",
        "",
        "- `lam_Q_F = (1, 0.01, 0)`",
        "- `lam_Q_R = 0.3`",
        "- `lam_S_Q_Rbar = 0.2`",
        "- only positive `y_Q` is varied",
        "",
        "## Result",
        "",
        f"- Reference `y_Q=1e-6` NA62 ratio: {reference['NA62_ratio']:.9g}",
        f"- Reference survives strongest TWIST benchmark: **{reference['TWIST_survives_strongest_published_case']}**",
    ]
    if boundary is not None and low is not None and high is not None:
        lines += [
            f"- Central survival boundary `y_Q`: {boundary['y_Q']:.12e}",
            f"- Boundary `M_Q`: {boundary['M_Q_GeV']:.12e} GeV",
            f"- `f0` one-sigma boundary band: [{low['y_Q']:.12e}, {high['y_Q']:.12e}]",
            f"- Muon BR at central boundary: {boundary['BR_mu_to_e_a']:.12e}",
        ]
    lines += [
        "",
        "## Scope",
        "",
        report["interpretation"],
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    report = build_report()
    ROOT.joinpath("PORTAL_CONSTRAINT_RAY_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("PORTAL_CONSTRAINT_RAY_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    summary = {
        "status": report["status"],
        "n_failed": report["n_failed"],
        "reference": report["central_scan"]["reference_yQ_1e_minus_6"],
        "boundary_band": report["form_factor_boundary_band"],
        "flags": report["flag"],
    }
    print(json.dumps(summary, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
