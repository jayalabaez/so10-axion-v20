#!/usr/bin/env python3
"""Fail-closed low-energy fermion-coupling audit for the v20 150 ueV axion.

Correction of the first implementation
--------------------------------------
The earlier version evaluated the Ernst-Ringwald-Tamarit (ERT) SO(10)
formula after replacing its anomaly/domain-wall normalization by the v20
covering-space value 17 and then labelled the result a completed v20
matching. The arithmetic of that evaluation is reproducible, but the
scientific inference was too strong.

This file therefore distinguishes:

1. quantities fixed by the v20 manuscript, including the exact physical
   axion direction and f_a;
2. an ERT-like *leading-current extrapolation* for the three light families;
3. the still-missing matching through the full v20 heavy-light mass matrix.

The extrapolation is useful as a benchmark, but it is not a proof that the
complete v20 model has those exact C_e, C_p and C_n values.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

VS_GEV = 6.313855e11
VPHI_GEV = 1.0e17
X_PHI = 17.0
X_S = 4.0
N_COVER = 17.0
N_PHYSICAL_WALL = 1

# Exact projection in axion_so10_theory_v20.tex, Eq. (axionprojection).
D_GEV = math.hypot(X_PHI * VPHI_GEV, X_S * VS_GEV)
FA_GEV = VS_GEV * VPHI_GEV / D_GEV
FA_APPROX_GEV = VS_GEV / N_COVER

MA_EV = 153.5e-6
ME_GEV = 0.00051099895
MP_GEV = 0.93827208816
MN_GEV = 0.93956542052

# Published comparison anchors.
GAE_TRGB_95CL = 1.3e-13
SN1987A_QUADRATIC_BOUND = 8.26e-19
FA_UNIVERSAL_SN_GEV = 1.1e8
MA_UNIVERSAL_SN_EV = 5.3e-2

TAN_BETA_V20 = 1.5000000000002063
TAN_BETA_NATURAL = 41.338069578693386
TAN_BETA_SCAN = (1.5, 50.0)


def ert_leading_extrapolation(
    tan_beta: float,
    *,
    acknowledge_not_full_matching: bool = False,
) -> dict:
    """Evaluate the ERT-like leading-current benchmark with N_cover=17.

    This is deliberately gated. Calling code must acknowledge that the
    result does not include the v20 anomalon/light-family diagonalization.
    """
    if not acknowledge_not_full_matching:
        raise RuntimeError(
            "This is an ERT-like leading-current extrapolation, not the full "
            "v20 heavy-light matching. Pass acknowledge_not_full_matching=True."
        )
    if tan_beta <= 0.0:
        raise ValueError("tan_beta must be positive")

    sin2 = tan_beta * tan_beta / (1.0 + tan_beta * tan_beta)
    cos2 = 1.0 / (1.0 + tan_beta * tan_beta)

    # ERT JHEP 02 (2018) 103, Eq. (6.3), evaluated with the v20
    # covering-space anomaly normalization. This is conditional on the
    # light families retaining the ordinary SO(10) PQ current.
    c_e = sin2 / N_COVER
    c_p = -0.47 + (3.0 / N_COVER) * (0.29 * cos2 - 0.15 * sin2)
    c_n = -0.02 + (3.0 / N_COVER) * (-0.14 * cos2 + 0.28 * sin2)

    # Illustrative uncorrelated propagation of the quoted ERT uncertainties.
    sigma_c_nucleon = math.hypot(0.03, (3.0 / N_COVER) * 0.02)

    g_ae = c_e * ME_GEV / FA_GEV
    g_ap = c_p * MP_GEV / FA_GEV
    g_an = c_n * MN_GEV / FA_GEV

    sn_lhs = sn1987a_quadratic(g_an=g_an, g_ap=g_ap)
    return {
        "classification": "PROVISIONAL_ERT_LEADING_CURRENT_EXTRAPOLATION",
        "tan_beta": tan_beta,
        "sin2_beta": sin2,
        "cos2_beta": cos2,
        "tree_quark_coefficients_if_no_portal_current_shift": {
            "C_u0": cos2 / N_COVER,
            "C_d0": sin2 / N_COVER,
        },
        "C_e": c_e,
        "C_p": c_p,
        "C_n": c_n,
        "sigma_C_p_hadronic_illustrative": sigma_c_nucleon,
        "sigma_C_n_hadronic_illustrative": sigma_c_nucleon,
        "g_ae": g_ae,
        "g_ap": g_ap,
        "g_an": g_an,
        "TRGB_limit_over_abs_g_ae": GAE_TRGB_95CL / abs(g_ae),
        "SN1987A_quadratic_lhs": sn_lhs,
        "SN1987A_bound_over_lhs": SN1987A_QUADRATIC_BOUND / sn_lhs,
        "SN1987A_amplitude_margin": math.sqrt(SN1987A_QUADRATIC_BOUND / sn_lhs),
    }


def sn1987a_quadratic(*, g_an: float, g_ap: float) -> float:
    """Combined nucleon-coupling form used in the indicative SN1987A bound."""
    return g_an**2 + 0.61 * g_ap**2 + 0.53 * g_an * g_ap


def q_portal_one_family_diagnostic(
    *,
    lambda_q: float = 1.0,
    y_q: float = 1.0,
) -> dict:
    """One-family diagnostic for the Qbar-F-S^dagger portal.

    For M_Q = y_q v_Phi/sqrt(2) and m_mix = lambda_q v_S/sqrt(2),
    r=m_mix/M_Q. In a two-state current projection, the light-state PQ
    charge shift is -4 sin^2(eta), where tan(eta)=r. The full v20 problem
    is a three-family 6x3 matrix and cannot be replaced by this diagnostic.
    """
    if y_q == 0.0:
        raise ValueError("y_q must be non-zero")
    r = abs(lambda_q / y_q) * VS_GEV / VPHI_GEV
    sin2_eta = r * r / (1.0 + r * r)
    return {
        "classification": "DIAGNOSTIC_NOT_FULL_MATCHING",
        "mixing_ratio_abs": r,
        "sin2_eta": sin2_eta,
        "light_PQ_charge_shift": -4.0 * sin2_eta,
        "message": (
            "Order-one lambda_q/y_q makes this correction tiny, but the "
            "repository does not fix the portal matrix or y_q, so it cannot "
            "be set to zero in a final model verdict."
        ),
    }


def build_report() -> dict:
    v20 = ert_leading_extrapolation(
        TAN_BETA_V20, acknowledge_not_full_matching=True
    )
    natural = ert_leading_extrapolation(
        TAN_BETA_NATURAL, acknowledge_not_full_matching=True
    )
    lo = ert_leading_extrapolation(
        TAN_BETA_SCAN[0], acknowledge_not_full_matching=True
    )
    hi = ert_leading_extrapolation(
        TAN_BETA_SCAN[1], acknowledge_not_full_matching=True
    )

    max_gae = max(abs(lo["g_ae"]), abs(hi["g_ae"]))
    max_sn_lhs = max(
        lo["SN1987A_quadratic_lhs"], hi["SN1987A_quadratic_lhs"]
    )

    return {
        "status": "PROVISIONAL_LEADING_CURRENT_ONLY__FULL_V20_MATCHING_OPEN",
        "correction": {
            "previous_error": (
                "The previous report promoted an ERT-like N=17 substitution "
                "to a completed v20 fermion matching and called the coupling "
                "gap closed."
            ),
            "what_survives": (
                "The numerical ERT-like benchmark is arithmetically "
                "reproducible and uses the correct covering-space anomaly "
                "normalization together with the exact v20 f_a projection."
            ),
            "what_does_not_survive": (
                "The PASS/full-model verdict. The v20 portal matrices and "
                "heavy-light diagonalization are not fixed, so exact low-energy "
                "C_e, C_p and C_n are not yet uniquely derived."
            ),
        },
        "normalization": {
            "v_S_GeV": VS_GEV,
            "v_Phi_GeV": VPHI_GEV,
            "covering_QCD_anomaly_normalization": N_COVER,
            "physical_gauge_inequivalent_wall_count": N_PHYSICAL_WALL,
            "f_a_exact_GeV": FA_GEV,
            "f_a_vS_over_17_GeV": FA_APPROX_GEV,
            "relative_projection_correction": FA_GEV / FA_APPROX_GEV - 1.0,
            "clarification": (
                "The physical wall count N_wall=1 does not replace the "
                "covering anomaly 17 in local coupling normalization. "
                "Nevertheless, choosing 17 is only one part of the matching."
            ),
        },
        "conditional_benchmarks": {
            "tan_beta_1p5_fit_point": v20,
            "tan_beta_41p34_comparison": natural,
        },
        "conditional_bound_checks": {
            "TRGB_electron": {
                "limit_95CL": GAE_TRGB_95CL,
                "largest_ERT_like_prediction_tanbeta_1p5_to_50": max_gae,
                "limit_over_prediction": GAE_TRGB_95CL / max_gae,
                "conditional_pass": max_gae < GAE_TRGB_95CL,
                "full_model_pass": None,
            },
            "SN1987A_correlated_nucleon": {
                "inequality": (
                    "g_an^2 + 0.61 g_ap^2 + 0.53 g_an g_ap < 8.26e-19"
                ),
                "bound": SN1987A_QUADRATIC_BOUND,
                "largest_ERT_like_lhs_tanbeta_1p5_to_50": max_sn_lhs,
                "bound_over_lhs": SN1987A_QUADRATIC_BOUND / max_sn_lhs,
                "amplitude_margin": math.sqrt(
                    SN1987A_QUADRATIC_BOUND / max_sn_lhs
                ),
                "conditional_pass": max_sn_lhs < SN1987A_QUADRATIC_BOUND,
                "full_model_pass": None,
                "caveat": (
                    "The supernova inequality is itself indicative and the "
                    "couplings inserted here are provisional."
                ),
            },
            "universal_QCD_axion_SN": {
                "f_a_lower_GeV_68CL": FA_UNIVERSAL_SN_GEV,
                "v20_f_a_exact_GeV": FA_GEV,
                "mass_upper_eV_68CL": MA_UNIVERSAL_SN_EV,
                "v20_mass_eV": MA_EV,
                "passes_model_independent_bound": (
                    FA_GEV > FA_UNIVERSAL_SN_GEV
                    and MA_EV < MA_UNIVERSAL_SN_EV
                ),
            },
        },
        "portal_mixing_diagnostic_order_one": q_portal_one_family_diagnostic(),
        "missing_for_full_v20_matching": [
            "Specify the complete generation-dependent Phi and S portal matrices.",
            "Diagonalize the full axion-dependent 6x3 heavy-light 16/bar16 mass matrix.",
            "Project the physical axion current onto the three light mass eigenstates.",
            "Run quark coefficients through thresholds and RG evolution.",
            "Propagate correlated hadronic uncertainties into C_p and C_n.",
        ],
        "full_matching_under_stated_ansatz": {
            "module": "full_fermion_matching_v20.py",
            "doc": "FULL_FERMION_MATCHING_V20.md",
            "note": (
                "Unique C_e, C_p, C_n exist only after declaring the "
                "manuscript-minimal flavour-universal unit-Yukawa ansatz; "
                "see that module for the closed derivation."
            ),
        },
        "verdict": (
            "The provisional ERT-like leading-current benchmark lies well "
            "below the displayed electron and nucleon bounds, and the universal "
            "supernova QCD-axion bound is passed. Exact unique C_e, C_p, C_n are "
            "not fixed by charges alone; under the stated manuscript-minimal "
            "universal ansatz they are derived in full_fermion_matching_v20.py "
            "(portal shifts negligible). The 37 GHz photon benchmark remains "
            "an open direct-search target."
        ),
    }


def main() -> int:
    report = build_report()
    out = Path(__file__).resolve().parent / "FERMION_COUPLINGS_150UEV_VERDICT.json"
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": report["status"],
                "f_a_exact_GeV": report["normalization"]["f_a_exact_GeV"],
                "conditional_v20": report["conditional_benchmarks"][
                    "tan_beta_1p5_fit_point"
                ],
                "verdict": report["verdict"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
