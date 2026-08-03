#!/usr/bin/env python3
"""Map one conditional complex family-orientation plane against NA62 and TWIST.

The overall norm of lam_Q_F and the other portal magnitudes are held at the
values of the generation-dependent texture.  The physically ordered-heavy
value of y_Q is recomputed from the full singular spectrum.  Only the direction

    lam_Q_F = kappa (cos(theta), exp(i phi) sin(theta), 0)

is varied.  This is a deterministic two-dimensional diagnostic inside the
F1-F2 subspace.  A grid fraction is not a probability or a UV posterior.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import channel_fcnc_rates_v20 as rates
import na62_pointwise_limit_v20 as na62
import physical_cf_matching_v20 as physical
import portal_boundary_heavy_spectrum_v20 as spectrum
import portal_tensors_abcd_v20 as portals
import twist_massless_limit_v20 as twist

ROOT = Path(__file__).resolve().parent
KAPPA = math.sqrt(1.0 + 0.01**2)
LAM_Q_R = 0.3
LAM_S_Q_RBAR = 0.2
DEFAULT_N_THETA = 61
DEFAULT_N_PHI = 96


def ordered_yq() -> float:
    scan = spectrum.solve_lightest_equals_vS()
    boundary = scan["unique_ordering_boundary"]
    if boundary is None:
        raise RuntimeError("ordered-heavy boundary was not uniquely solved")
    return float(boundary["y_Q"])


def family_vector(theta: float, phi: float, *, kappa: float = KAPPA) -> tuple[complex, complex, complex]:
    if not (math.isfinite(theta) and math.isfinite(phi) and math.isfinite(kappa)):
        raise ValueError("orientation inputs must be finite")
    if theta < 0.0 or theta > 0.5 * math.pi:
        raise ValueError("theta must lie in [0, pi/2]")
    if kappa <= 0.0:
        raise ValueError("kappa must be positive")
    return (
        complex(kappa * math.cos(theta), 0.0),
        complex(kappa * math.sin(theta) * math.cos(phi), kappa * math.sin(theta) * math.sin(phi)),
        0.0 + 0.0j,
    )


def portal_block(theta: float, phi: float, *, y_q: float) -> dict[str, Any]:
    return portals.build_abcd(
        portals.PortalCouplings(
            y_Q=y_q,
            lam_Q_F=family_vector(theta, phi),
            lam_Q_R=LAM_Q_R,
            lam_S_Q_Rbar=LAM_S_Q_RBAR,
        )
    )


def heavy_singular_values(block: dict[str, Any]) -> np.ndarray:
    top = np.hstack([np.asarray(block["A"], dtype=complex), np.asarray(block["C"], dtype=complex)])
    bottom = np.hstack([
        np.asarray(block["B"], dtype=complex),
        np.asarray([[block["D"]]], dtype=complex),
    ])
    values = np.sort(np.linalg.svd(np.vstack([top, bottom]), compute_uv=False))
    if values.shape != (3,) or np.min(values) <= 0.0 or not np.all(np.isfinite(values)):
        raise ValueError("expected three finite positive heavy singular values")
    return values


def experimental_limits() -> tuple[float, float]:
    anchor = na62.load_anchor()
    kaon = float(
        na62.observed_limit_at_mass(na62.TARGET_MASS_MEV, anchor)["observed_br_ul_90cl"]
    )
    muon = min(
        float(row["branching_ratio_upper_limit_90cl"])
        for row in twist.load_limits()["limits"]
    )
    return kaon, muon


def evaluate_orientation(
    theta: float,
    phi: float,
    *,
    y_q: float,
    bases: dict[str, Any],
    na62_limit: float,
    twist_limit: float,
) -> dict[str, Any]:
    block = portal_block(theta, phi, y_q=y_q)
    result = rates.scenario_rates(
        f"orientation_theta_{theta:.9e}_phi_{phi:.9e}", block, bases
    )
    br_k = float(result["K_to_pi_a"]["branching_ratio"])
    br_mu = float(result["mu_to_e_a"]["branching_ratio"])
    singular = heavy_singular_values(block)
    vector = family_vector(theta, phi)
    return {
        "theta_rad": float(theta),
        "phi_rad": float(phi % (2.0 * math.pi)),
        "lam_Q_F": [
            {"re": float(z.real), "im": float(z.imag), "abs": float(abs(z))}
            for z in vector
        ],
        "BR_K_to_pi_a": br_k,
        "NA62_ratio": float(br_k / na62_limit),
        "NA62_excluded": bool(br_k > na62_limit),
        "BR_mu_to_e_a": br_mu,
        "TWIST_ratio": float(br_mu / twist_limit),
        "TWIST_excluded_strongest_published_case": bool(br_mu > twist_limit),
        "lightest_heavy_singular_GeV": float(singular[0]),
        "lightest_heavy_over_vS": float(singular[0] / portals.VS),
    }


def _extreme(rows: list[dict[str, Any]], key: str, *, maximize: bool) -> dict[str, Any]:
    chooser = max if maximize else min
    return dict(chooser(rows, key=lambda row: float(row[key])))


def scan_orientation_plane(
    *,
    n_theta: int = DEFAULT_N_THETA,
    n_phi: int = DEFAULT_N_PHI,
) -> dict[str, Any]:
    if n_theta < 3 or n_phi < 4:
        raise ValueError("orientation grid is too small")
    y_q = ordered_yq()
    bases = physical.flavour_mass_bases()
    na62_limit, twist_limit = experimental_limits()
    theta_grid = np.linspace(0.0, 0.5 * math.pi, n_theta)
    phi_grid = np.linspace(0.0, 2.0 * math.pi, n_phi, endpoint=False)
    rows: list[dict[str, Any]] = []
    for theta in theta_grid:
        for phi in phi_grid:
            rows.append(
                evaluate_orientation(
                    float(theta),
                    float(phi),
                    y_q=y_q,
                    bases=bases,
                    na62_limit=na62_limit,
                    twist_limit=twist_limit,
                )
            )

    reference_theta = math.atan2(0.01, 1.0)
    reference = evaluate_orientation(
        reference_theta,
        0.0,
        y_q=y_q,
        bases=bases,
        na62_limit=na62_limit,
        twist_limit=twist_limit,
    )
    benchmark_rows = {
        "F1_aligned": evaluate_orientation(
            0.0, 0.0, y_q=y_q, bases=bases,
            na62_limit=na62_limit, twist_limit=twist_limit,
        ),
        "F2_aligned": evaluate_orientation(
            0.5 * math.pi, 0.0, y_q=y_q, bases=bases,
            na62_limit=na62_limit, twist_limit=twist_limit,
        ),
        "equal_real": evaluate_orientation(
            0.25 * math.pi, 0.0, y_q=y_q, bases=bases,
            na62_limit=na62_limit, twist_limit=twist_limit,
        ),
        "equal_quadrature": evaluate_orientation(
            0.25 * math.pi, 0.5 * math.pi, y_q=y_q, bases=bases,
            na62_limit=na62_limit, twist_limit=twist_limit,
        ),
        "original_direction": reference,
    }
    singular_values = np.asarray(
        [float(row["lightest_heavy_singular_GeV"]) for row in rows]
    )
    baseline = float(reference["lightest_heavy_singular_GeV"])
    max_spectrum_relative_drift = float(np.max(np.abs(singular_values / baseline - 1.0)))
    n_na62_excluded = sum(bool(row["NA62_excluded"]) for row in rows)
    n_twist_excluded = sum(
        bool(row["TWIST_excluded_strongest_published_case"]) for row in rows
    )
    return {
        "configuration": {
            "parameterization": "kappa*(cos(theta), exp(i phi) sin(theta), 0)",
            "kappa": KAPPA,
            "lam_Q_R": LAM_Q_R,
            "lam_S_Q_Rbar": LAM_S_Q_RBAR,
            "ordered_y_Q": y_q,
            "n_theta": n_theta,
            "n_phi": n_phi,
            "n_grid_points": len(rows),
            "theta_domain": [0.0, 0.5 * math.pi],
            "phi_domain": [0.0, 2.0 * math.pi],
            "phi_endpoint_duplicated": False,
        },
        "limits": {
            "NA62_observed_br_upper_limit_90cl": na62_limit,
            "TWIST_strongest_published_br_upper_limit_90cl": twist_limit,
        },
        "reference_original_direction": reference,
        "benchmarks": benchmark_rows,
        "extrema": {
            "min_NA62_ratio": _extreme(rows, "NA62_ratio", maximize=False),
            "max_NA62_ratio": _extreme(rows, "NA62_ratio", maximize=True),
            "min_TWIST_ratio": _extreme(rows, "TWIST_ratio", maximize=False),
            "max_TWIST_ratio": _extreme(rows, "TWIST_ratio", maximize=True),
        },
        "counts": {
            "n_grid_points": len(rows),
            "n_NA62_excluded": n_na62_excluded,
            "n_NA62_surviving": len(rows) - n_na62_excluded,
            "NA62_excluded_grid_fraction": float(n_na62_excluded / len(rows)),
            "n_TWIST_excluded": n_twist_excluded,
            "n_TWIST_surviving": len(rows) - n_twist_excluded,
            "TWIST_excluded_grid_fraction": float(n_twist_excluded / len(rows)),
            "grid_fraction_is_probability": False,
        },
        "heavy_spectrum": {
            "reference_lightest_heavy_singular_GeV": baseline,
            "reference_lightest_heavy_over_vS": float(reference["lightest_heavy_over_vS"]),
            "max_relative_drift_over_orientation_grid": max_spectrum_relative_drift,
            "orientation_invariant_at_fixed_norm": max_spectrum_relative_drift < 1.0e-10,
        },
        "grid_rows": rows,
    }


def build_report() -> dict[str, Any]:
    scan = scan_orientation_plane()
    counts = scan["counts"]
    extrema = scan["extrema"]
    reference = scan["reference_original_direction"]
    checks = {
        "ordered_heavy_point_used": math.isclose(
            float(scan["heavy_spectrum"]["reference_lightest_heavy_over_vS"]),
            1.0,
            rel_tol=1.0e-8,
        ),
        "original_direction_reproduced": math.isclose(
            float(reference["lam_Q_F"][0]["re"]), 1.0, rel_tol=1.0e-12
        ) and math.isclose(
            float(reference["lam_Q_F"][1]["re"]), 0.01, rel_tol=1.0e-12
        ),
        "orientation_preserves_heavy_spectrum": scan["heavy_spectrum"][
            "orientation_invariant_at_fixed_norm"
        ],
        "all_ratios_finite_positive": all(
            math.isfinite(float(row[key])) and float(row[key]) >= 0.0
            for row in scan["grid_rows"]
            for key in ("NA62_ratio", "TWIST_ratio")
        ),
        "na62_extrema_ordered": float(extrema["min_NA62_ratio"]["NA62_ratio"])
        <= float(extrema["max_NA62_ratio"]["NA62_ratio"]),
        "twist_extrema_ordered": float(extrema["min_TWIST_ratio"]["TWIST_ratio"])
        <= float(extrema["max_TWIST_ratio"]["TWIST_ratio"]),
        "count_accounting_na62": counts["n_NA62_excluded"]
        + counts["n_NA62_surviving"]
        == counts["n_grid_points"],
        "count_accounting_twist": counts["n_TWIST_excluded"]
        + counts["n_TWIST_surviving"]
        == counts["n_grid_points"],
        "grid_fraction_not_probability": not counts["grid_fraction_is_probability"],
        "full_three_family_orientation_not_claimed": True,
        "uv_posterior_not_claimed": True,
        "whole_model_exclusion_not_claimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]
    return {
        "status": (
            "CONDITIONAL_F1_F2_ORIENTATION_MAP_COMPLETE__EXPERIMENTAL_CLASSIFICATION_RECORDED__FULL_PORTAL_SPACE_OPEN"
            if not failures
            else "PORTAL_FAMILY_ORIENTATION_MAP_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "scan": scan,
        "flag": {
            "complex_F1_F2_orientation_plane_scanned": True,
            "ordered_heavy_boundary_used": True,
            "heavy_spectrum_orientation_invariant_at_fixed_norm": scan[
                "heavy_spectrum"
            ]["orientation_invariant_at_fixed_norm"],
            "NA62_has_excluded_grid_points": counts["n_NA62_excluded"] > 0,
            "NA62_has_surviving_grid_points": counts["n_NA62_surviving"] > 0,
            "TWIST_has_excluded_grid_points": counts["n_TWIST_excluded"] > 0,
            "TWIST_has_surviving_grid_points": counts["n_TWIST_surviving"] > 0,
            "grid_fraction_is_probability": False,
            "full_complex_three_family_orientation_scanned": False,
            "all_portal_magnitudes_and_phases_scanned": False,
            "portal_yukawa_posterior_derived": False,
            "component_specific_uv_chiral_currents_derived": False,
            "whole_v20_model_excluded": False,
        },
        "interpretation": (
            "At the ordered-heavy y_Q and fixed portal norm, the physical heavy "
            "singular spectrum is invariant under rotations of the complex F1-F2 "
            "portal direction, while the FCNC rates can change because the direction "
            "is projected into the charged-lepton and down-quark mass bases. The "
            "reported excluded-grid fraction is only a deterministic sampling summary, "
            "not a probability or UV measure."
        ),
        "remaining_for_full_portal_inference": [
            "include the complex F3 component",
            "vary all independent portal magnitudes and phases",
            "derive component-specific currents through threshold matching",
            "define and fit a UV prior or posterior",
            "include continuous experimental likelihood information",
        ],
    }


def write_markdown(report: dict[str, Any]) -> str:
    scan = report["scan"]
    counts = scan["counts"]
    extrema = scan["extrema"]
    return "\n".join(
        [
            "# Conditional portal family-orientation map — v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            f"- grid points: {counts['n_grid_points']}",
            f"- NA62 excluded grid points: {counts['n_NA62_excluded']}",
            f"- NA62 surviving grid points: {counts['n_NA62_surviving']}",
            f"- TWIST excluded grid points: {counts['n_TWIST_excluded']}",
            f"- min NA62 ratio: {extrema['min_NA62_ratio']['NA62_ratio']:.12e}",
            f"- max NA62 ratio: {extrema['max_NA62_ratio']['NA62_ratio']:.12e}",
            f"- min TWIST ratio: {extrema['min_TWIST_ratio']['TWIST_ratio']:.12e}",
            f"- max TWIST ratio: {extrema['max_TWIST_ratio']['TWIST_ratio']:.12e}",
            "",
            "The grid fraction is not a probability or UV posterior.",
            "",
            report["interpretation"],
            "",
        ]
    )


def main() -> int:
    report = build_report()
    ROOT.joinpath("PORTAL_FAMILY_ORIENTATION_MAP_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("PORTAL_FAMILY_ORIENTATION_MAP_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    scan = report["scan"]
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "configuration": scan["configuration"],
                "reference": scan["reference_original_direction"],
                "counts": scan["counts"],
                "extrema": scan["extrema"],
                "heavy_spectrum": scan["heavy_spectrum"],
                "flags": report["flag"],
            },
            indent=2,
        )
    )
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
