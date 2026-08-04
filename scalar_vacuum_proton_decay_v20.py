#!/usr/bin/env python3
"""Fail-closed scalar-vacuum witness and proton-decay stress test for v20.

This module deliberately separates three levels of statement:

1. A constructive, globally stable *reduced radial singlet-direction* potential
   can realize the assumed hierarchy. This is a real mathematical witness.
2. The complete SO(10) scalar potential is not available because the independent
   tensor contractions and component mass matrices for 210_H, 10_H and
   \bar{126}_H have not been supplied/derived. Therefore the full vacuum and
   heavy spectrum remain open.
3. Gauge-mediated proton decay can be calculated as an anchored benchmark and
   threshold envelope. Scalar-mediated decay is evaluated as a source-backed
   conditional mass/coupling stress test; exact channel widths remain open until
   the color-triplet mass/mixing matrices and mass-basis Yukawa contractions are
   derived from the complete scalar potential.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parent
HBAR_GEV_S = 6.582119569e-25
SECONDS_PER_YEAR = 365.25 * 24.0 * 3600.0
SK_EPI0_LIMIT_YR = 2.4e34

SOURCE_LEDGER = {
    "scalar_vacuum_210": {
        "citation": "D. Chang and A. Kumar, Phys. Rev. D 33 (1986) 2695",
        "doi": "10.1103/PhysRevD.33.2695",
        "scope": "The 210-dimensional Higgs can possess parameter regions with Pati-Salam-type minima; this does not provide the complete v20 210+126bar+10+singlet potential.",
    },
    "scalar_proton_decay": {
        "citation": "K. M. Patel and S. K. Shukla, JHEP 08 (2022) 042",
        "arxiv": "2203.07748",
        "scope": "In 10_H+126bar_H models the relevant tree-level d=6 scalar mediators are color triplets T(3,1,-1/3); scalar/gauge width scaling is approximately ((y_eff/g_GUT)*(M_X/M_T))^4.",
    },
    "super_k_epi0": {
        "citation": "Super-Kamiokande, Phys. Rev. D 102 (2020) 112011",
        "doi": "10.1103/PhysRevD.102.112011",
        "limit_90CL_years": SK_EPI0_LIMIT_YR,
    },
}


def _unification_anchor() -> dict[str, float]:
    """Load the repository's current gauge-chain anchor."""
    try:
        import two_loop_thresholds_v20 as thresholds
        one = thresholds.solve_unification(two_loop=False)
        two = thresholds.solve_unification(two_loop=True)
    except Exception as exc:  # fail closed, but preserve a diagnostic payload
        return {
            "available": False,
            "error": f"{type(exc).__name__}: {exc}",
            "M_I_GeV": float("nan"),
            "M_GUT_GeV": float("nan"),
            "alpha_inv_GUT": float("nan"),
            "M_GUT_two_loop_proxy_GeV": float("nan"),
            "alpha_inv_GUT_two_loop_proxy": float("nan"),
        }
    return {
        "available": True,
        "M_I_GeV": float(one["M_I_GeV"]),
        "M_GUT_GeV": float(one["M_GUT_GeV"]),
        "alpha_inv_GUT": float(one["alpha_inv_GUT"]),
        "M_GUT_two_loop_proxy_GeV": float(two["M_GUT_GeV"]),
        "alpha_inv_GUT_two_loop_proxy": float(two["alpha_inv_GUT"]),
    }


def reduced_radial_vacuum_witness(anchor: dict[str, float]) -> dict[str, Any]:
    """Construct a globally stable reduced radial potential.

    For radial fields r_i and target VEVs v_i,

        V = 1/4 sum_i lambda_i (r_i^2-v_i^2)^2
            + 1/4 sum_{i<j} eps_ij (r_i^2-v_i^2)(r_j^2-v_j^2).

    This is a renormalizable polynomial. If the normalized quartic matrix B,
    B_ii=lambda_i and B_ij=eps_ij/2, is positive definite, V>=0 globally and
    r_i^2=v_i^2 is a global minimum in this reduced radial subspace.
    """
    if not anchor.get("available"):
        return {
            "status": "REDUCED_VACUUM_NOT_EXECUTED__UNIFICATION_ANCHOR_MISSING",
            "flag": {
                "reduced_radial_global_minimum_proved": False,
                "complete_so10_scalar_potential": False,
                "full_component_hessian_computed": False,
            },
            "error": anchor.get("error"),
        }

    names = ["P_210_PS", "DeltaR_126bar", "S_PQ", "Phi17_X", "h_EW_effective"]
    vevs = np.array([
        anchor["M_GUT_GeV"],
        anchor["M_I_GeV"],
        anchor["M_I_GeV"],
        1.0e17,
        174.0,
    ], dtype=float)
    lambdas = np.array([0.55, 0.65, 0.45, 0.75, 0.258], dtype=float)
    eps = np.zeros((5, 5), dtype=float)
    for (i, j), value in {
        (0, 1): 0.05,
        (0, 2): 0.01,
        (0, 3): 0.02,
        (1, 2): 0.04,
        (1, 3): 0.01,
        (2, 3): 0.03,
    }.items():
        eps[i, j] = eps[j, i] = value

    b = np.diag(lambdas) + 0.5 * eps
    quartic_eigs = np.linalg.eigvalsh(b)
    hessian = np.diag(2.0 * lambdas * vevs**2) + eps * np.outer(vevs, vevs)
    hessian_eigs = np.linalg.eigvalsh(hessian)
    radial_masses = np.sqrt(np.clip(hessian_eigs, 0.0, None))
    positive_quartic = bool(np.min(quartic_eigs) > 0.0)
    positive_hessian = bool(np.min(hessian_eigs) > 0.0)

    return {
        "status": (
            "REDUCED_RADIAL_GLOBAL_MINIMUM_PROVED__FULL_SO10_POTENTIAL_OPEN"
            if positive_quartic and positive_hessian
            else "REDUCED_RADIAL_VACUUM_FAILED"
        ),
        "potential_definition": {
            "fields": names,
            "target_vevs_GeV": dict(zip(names, map(float, vevs))),
            "self_quartics": dict(zip(names, map(float, lambdas))),
            "cross_quartics_epsilon": {
                f"{names[i]}__{names[j]}": float(eps[i, j])
                for i in range(len(names))
                for j in range(i + 1, len(names))
                if eps[i, j] != 0.0
            },
            "form": "V=1/4 sum lambda_i(r_i^2-v_i^2)^2 + 1/4 sum eps_ij(r_i^2-v_i^2)(r_j^2-v_j^2)",
        },
        "proof": {
            "normalized_quartic_eigenvalues": [float(x) for x in quartic_eigs],
            "quartic_matrix_positive_definite": positive_quartic,
            "stationarity_gradient_exactly_zero": True,
            "radial_hessian_eigenvalues_GeV2": [float(x) for x in hessian_eigs],
            "radial_hessian_positive_definite": positive_hessian,
            "radial_mass_eigenvalues_GeV": [float(x) for x in radial_masses],
            "global_reduced_radial_minimum": positive_quartic,
            "argument": "With q_i=r_i^2-v_i^2, V=(1/4) q^T B q. Positive-definite B implies V>=0 and q=0 is global in the reduced radial subspace.",
        },
        "hierarchy": {
            "max_over_min_vev": float(np.max(vevs) / np.min(vevs)),
            "M_GUT_over_M_I": float(anchor["M_GUT_GeV"] / anchor["M_I_GeV"]),
            "vPhi_over_M_GUT": float(1.0e17 / anchor["M_GUT_GeV"]),
        },
        "missing_full_theory_inputs": [
            "complete independent SO(10) invariant basis and normalizations for 210_H^3 and all 210_H^4 contractions",
            "all independent 210_H 126bar_H^dagger 126bar_H, 210_H 10_H^dagger 10_H and mixed quartic contractions",
            "full Pati-Salam/SM component branching and Clebsch-normalized mass matrices",
            "phase-sector Hessian including the dimension-six 126bar_H^2 10_H^2 S^2 locking operator",
            "Goldstone counting and gauge-fixing across every component",
            "one-loop Coleman-Weinberg corrections and competing non-Pati-Salam extrema",
        ],
        "flag": {
            "reduced_radial_global_minimum_proved": positive_quartic and positive_hessian,
            "constructive_hierarchical_vacuum_witness": positive_quartic and positive_hessian,
            "complete_so10_scalar_potential": False,
            "complete_independent_invariant_basis": False,
            "full_component_hessian_computed": False,
            "full_physical_heavy_threshold_spectrum_computed": False,
            "pati_salam_vacuum_proved_in_full_field_space": False,
        },
        "verdict": (
            "The assumed hierarchy is not algebraically impossible: a renormalizable, bounded, globally stable reduced radial potential exists. This is not a proof that the complete 210+126bar+10+S+Phi17 SO(10) potential selects the desired vacuum."
        ),
    }


def gauge_proton_lifetime_years(
    m_x_gev: float,
    alpha_inv_gut: float,
    *,
    a_r: float = 2.5,
    hadronic_w_gev2: float = 0.11,
    v_ud: float = 0.9737,
) -> float:
    """Gauge-mediated p->e+pi0 benchmark used by the existing v20 pipeline."""
    if min(m_x_gev, alpha_inv_gut, a_r, hadronic_w_gev2) <= 0:
        raise ValueError("all scale/coupling inputs must be positive")
    m_p = 0.9382720813
    m_pi0 = 0.1349768
    alpha_gut = 1.0 / alpha_inv_gut
    kinematic = (1.0 - (m_pi0 / m_p) ** 2) ** 2
    coefficient = 4.0 * math.pi * alpha_gut / m_x_gev**2
    flavour_factor = 1.0 + (1.0 + v_ud**2) ** 2
    width = (
        m_p
        / (32.0 * math.pi)
        * kinematic
        * coefficient**2
        * a_r**2
        * hadronic_w_gev2**2
        * flavour_factor
    )
    return HBAR_GEV_S / width / SECONDS_PER_YEAR


def gauge_proton_decay(anchor: dict[str, float]) -> dict[str, Any]:
    if not anchor.get("available"):
        return {
            "status": "GAUGE_PROTON_DECAY_NOT_EXECUTED__UNIFICATION_ANCHOR_MISSING",
            "flag": {"gauge_boson_exchange_computed": False, "model_point_excluded": False},
            "error": anchor.get("error"),
        }
    m_gut = float(anchor["M_GUT_GeV"])
    alpha_inv = float(anchor["alpha_inv_GUT"])
    central = gauge_proton_lifetime_years(m_gut, alpha_inv)

    rows = []
    for mass_factor in (0.5, 0.75, 1.0, 1.5, 2.0):
        for a_r in (2.0, 2.5, 3.0):
            for w in (0.09, 0.11, 0.13):
                lifetime = gauge_proton_lifetime_years(
                    m_gut * mass_factor, alpha_inv, a_r=a_r, hadronic_w_gev2=w
                )
                rows.append(
                    {
                        "M_X_over_M_GUT": mass_factor,
                        "A_R": a_r,
                        "W_GeV2": w,
                        "lifetime_years": lifetime,
                        "passes_SK_e_pi0": lifetime >= SK_EPI0_LIMIT_YR,
                    }
                )
    min_row = min(rows, key=lambda r: r["lifetime_years"])
    max_row = max(rows, key=lambda r: r["lifetime_years"])
    central_required_factor = (SK_EPI0_LIMIT_YR / central) ** 0.25
    worst_reference = gauge_proton_lifetime_years(
        m_gut, alpha_inv, a_r=3.0, hadronic_w_gev2=0.13
    )
    worst_required_factor = (SK_EPI0_LIMIT_YR / worst_reference) ** 0.25

    return {
        "status": "GAUGE_PROTON_DECAY_ENVELOPE_COMPUTED__VECTOR_MASS_NORMALIZATION_OPEN",
        "input": {
            "M_GUT_GeV": m_gut,
            "alpha_inv_GUT": alpha_inv,
            "SK_p_to_e_pi0_90CL_years": SK_EPI0_LIMIT_YR,
        },
        "central": {
            "M_X_equals_M_GUT": True,
            "A_R": 2.5,
            "W_GeV2": 0.11,
            "lifetime_years": central,
            "passes_SK_e_pi0": central >= SK_EPI0_LIMIT_YR,
            "margin_over_SK": central / SK_EPI0_LIMIT_YR,
        },
        "envelope": {
            "n_points": len(rows),
            "minimum_lifetime_point": min_row,
            "maximum_lifetime_point": max_row,
            "all_points_pass_SK": all(r["passes_SK_e_pi0"] for r in rows),
            "M_X_over_M_GUT_required_central_hadronic": central_required_factor,
            "M_X_over_M_GUT_required_worst_hadronic": worst_required_factor,
        },
        "flag": {
            "gauge_boson_exchange_computed": True,
            "central_gauge_point_passes": central >= SK_EPI0_LIMIT_YR,
            "broad_threshold_envelope_fully_passes": all(r["passes_SK_e_pi0"] for r in rows),
            "exact_XY_mass_from_full_scalar_vacuum": False,
            "complete_gauge_flavour_rotations": False,
            "model_point_excluded": False,
        },
        "verdict": (
            "The central M_X=M_GUT gauge benchmark is above the Super-K limit, but a deliberately broad M_X=0.5 M_GUT/hadronic envelope contains excluded points. The full scalar vacuum must determine the actual X,Y masses before the gauge result is robust."
        ),
    }


def scalar_triplet_stress(anchor: dict[str, float], gauge: dict[str, Any]) -> dict[str, Any]:
    if not anchor.get("available") or not gauge.get("central"):
        return {
            "status": "SCALAR_TRIPLET_STRESS_NOT_EXECUTED",
            "flag": {"scalar_exchange_computed": False, "model_point_excluded": False},
        }
    m_x = float(anchor["M_GUT_GeV"])
    m_i = float(anchor["M_I_GeV"])
    alpha = 1.0 / float(anchor["alpha_inv_GUT"])
    g_gut = math.sqrt(4.0 * math.pi * alpha)
    tau_gauge = float(gauge["central"]["lifetime_years"])

    def ratio(y_eff: float, m_t: float) -> float:
        return (abs(y_eff) / g_gut * m_x / m_t) ** 4

    def total_lifetime(y_eff: float, m_t: float) -> float:
        return tau_gauge / (1.0 + ratio(y_eff, m_t))

    y_grid = (1.0e-5, 1.0e-4, 1.0e-3)
    mass_grid = (m_i, 1.0e12, 1.0e13, m_x)
    rows = []
    for y_eff in y_grid:
        for m_t in mass_grid:
            lifetime = total_lifetime(y_eff, m_t)
            rows.append(
                {
                    "y_eff": y_eff,
                    "M_T_GeV": m_t,
                    "M_T_over_M_X": m_t / m_x,
                    "Gamma_scalar_over_Gamma_gauge": ratio(y_eff, m_t),
                    "combined_lifetime_years": lifetime,
                    "passes_SK_e_pi0_proxy": lifetime >= SK_EPI0_LIMIT_YR,
                }
            )

    available_width_ratio = tau_gauge / SK_EPI0_LIMIT_YR - 1.0
    required_masses = {}
    for y_eff in y_grid:
        if available_width_ratio <= 0:
            required = float("inf")
        else:
            required = (
                abs(y_eff)
                / g_gut
                * m_x
                / available_width_ratio ** 0.25
            )
        required_masses[f"y_eff_{y_eff:.0e}"] = required

    reference = next(
        r for r in rows if r["y_eff"] == 1.0e-4 and r["M_T_GeV"] == m_i
    )
    any_proxy_excluded = any(not r["passes_SK_e_pi0_proxy"] for r in rows)
    return {
        "status": "SCALAR_TRIPLET_CONDITIONAL_STRESS_COMPLETE__EXACT_WIDTHS_OPEN",
        "method": {
            "width_ratio": "Gamma_scalar/Gamma_gauge=((y_eff/g_GUT)*(M_X/M_T))^4",
            "source": SOURCE_LEDGER["scalar_proton_decay"],
            "interpretation": "This is a leading scaling stress test, not the exact Patel-Shukla channel likelihood.",
        },
        "input": {
            "g_GUT": g_gut,
            "M_X_GeV": m_x,
            "M_I_GeV": m_i,
            "gauge_lifetime_years": tau_gauge,
        },
        "grid": rows,
        "triplet_mass_lower_bounds_GeV_for_SK_proxy": required_masses,
        "reference_MI_y1e4": reference,
        "missing_exact_inputs": [
            "complete color-triplet mass and mixing matrices from 10_H and 126bar_H",
            "Clebsch-normalized triplet couplings in the physical fermion basis",
            "operator mixing and RG factors for every chirality structure",
            "channel-specific lattice matrix elements and correlated uncertainties",
            "interference between gauge and multiple scalar amplitudes",
        ],
        "flag": {
            "scalar_scaling_stress_computed": True,
            "conditional_MI_triplet_y1e4_excluded": not reference["passes_SK_e_pi0_proxy"],
            "some_stress_grid_points_excluded": any_proxy_excluded,
            "exact_scalar_exchange_computed": False,
            "channel_ratios_computed": False,
            "complete_operator_running_and_hadronic_matching": False,
            "model_point_excluded": False,
        },
        "verdict": (
            "A color triplet at M_I with y_eff=1e-4 would give a combined proxy lifetime below the current p->e+pi0 bound. This conditionally kills that triplet-mass/coupling point, not the full model. Exact scalar masses and mixings are outputs of the still-missing full potential."
        ),
    }


def build_reports() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    anchor = _unification_anchor()
    vacuum = reduced_radial_vacuum_witness(anchor)
    gauge = gauge_proton_decay(anchor)
    scalar = scalar_triplet_stress(anchor, gauge)
    proton_excluded = bool(gauge.get("flag", {}).get("model_point_excluded"))
    proton = {
        "status": "PROTON_DECAY_CONDITIONAL_STRESS_COMPLETE__FULL_CALCULATION_OPEN",
        "sources": SOURCE_LEDGER,
        "unification_anchor": anchor,
        "gauge": gauge,
        "scalar": scalar,
        "flag": {
            "gauge_boson_exchange_computed": bool(
                gauge.get("flag", {}).get("gauge_boson_exchange_computed")
            ),
            "scalar_exchange_computed": False,
            "scalar_scaling_stress_computed": bool(
                scalar.get("flag", {}).get("scalar_scaling_stress_computed")
            ),
            "channel_ratios_computed": False,
            "complete_operator_running_and_hadronic_matching": False,
            "exact_XY_and_triplet_masses_from_full_vacuum": False,
            "conditional_parameter_points_excluded": bool(
                scalar.get("flag", {}).get("some_stress_grid_points_excluded")
            ),
            "model_point_excluded": proton_excluded,
        },
        "verdict": (
            "The central gauge benchmark survives, while broad threshold and scalar-triplet stress tests contain excluded conditional points. No unique v20 proton lifetime is available until the full scalar spectrum and triplet couplings are derived."
        ),
    }
    combined = {
        "status": "SCALAR_VACUUM_AND_PROTON_DECAY_EXECUTED__FULL_CLOSURE_BLOCKED",
        "scalar_vacuum": vacuum,
        "proton_decay": proton,
        "hard_results": {
            "reduced_radial_vacuum_witness_exists": bool(
                vacuum.get("flag", {}).get("constructive_hierarchical_vacuum_witness")
            ),
            "central_gauge_proton_point_passes": bool(
                gauge.get("flag", {}).get("central_gauge_point_passes")
            ),
            "broad_gauge_envelope_fully_passes": bool(
                gauge.get("flag", {}).get("broad_threshold_envelope_fully_passes")
            ),
            "MI_triplet_y1e4_proxy_passes": not bool(
                scalar.get("flag", {}).get("conditional_MI_triplet_y1e4_excluded")
            ),
        },
        "full_scalar_potential_completed": False,
        "unique_proton_decay_prediction_completed": False,
        "whole_model_excluded": False,
        "whole_model_validated": False,
    }
    return vacuum, proton, combined


def write_markdown(vacuum: dict[str, Any], proton: dict[str, Any], combined: dict[str, Any]) -> str:
    gauge = proton.get("gauge", {})
    scalar = proton.get("scalar", {})
    central = gauge.get("central", {})
    ref = scalar.get("reference_MI_y1e4", {})
    lines = [
        "# Scalar vacuum and proton decay — v20",
        "",
        f"**Status:** `{combined['status']}`",
        "",
        "## Executed hard results",
        "",
        f"- Reduced radial global vacuum witness: **{combined['hard_results']['reduced_radial_vacuum_witness_exists']}**",
        f"- Complete SO(10) scalar potential: **False**",
        f"- Central gauge proton point passes Super-K: **{combined['hard_results']['central_gauge_proton_point_passes']}**",
        f"- Broad gauge threshold envelope fully passes: **{combined['hard_results']['broad_gauge_envelope_fully_passes']}**",
    ]
    if central:
        lines += [
            f"- Central gauge lifetime: `{central['lifetime_years']:.6e}` yr",
            f"- Central margin over Super-K: `{central['margin_over_SK']:.6g}`",
        ]
    if ref:
        lines += [
            f"- Conditional M_T=M_I, y_eff=1e-4 lifetime: `{ref['combined_lifetime_years']:.6e}` yr",
            f"- That conditional point passes Super-K: **{ref['passes_SK_e_pi0_proxy']}**",
        ]
    lines += [
        "",
        "## Interpretation",
        "",
        vacuum.get("verdict", ""),
        "",
        proton.get("verdict", ""),
        "",
        "The reduced witness proves feasibility only in five radial order-parameter directions. The exact SO(10) component Hessian and the color-triplet spectrum remain the decisive missing calculations.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    vacuum, proton, combined = build_reports()
    ROOT.joinpath("SCALAR_VACUUM_V20_VERDICT.json").write_text(
        json.dumps(vacuum, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("PROTON_DECAY_V20_VERDICT.json").write_text(
        json.dumps(proton, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("SCALAR_VACUUM_PROTON_DECAY_V20_VERDICT.json").write_text(
        json.dumps(combined, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("SCALAR_VACUUM_PROTON_DECAY_V20.md").write_text(
        write_markdown(vacuum, proton, combined), encoding="utf-8"
    )
    print(json.dumps(combined, indent=2))
    anchor_ok = bool(proton.get("unification_anchor", {}).get("available"))
    internal_ok = bool(vacuum.get("flag", {}).get("reduced_radial_global_minimum_proved"))
    return 0 if anchor_ok and internal_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
