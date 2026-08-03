#!/usr/bin/env python3
"""Fail-closed v20 electron/nucleon coupling audit.

The aligned ERT-like benchmark is reproducible, including the exact reduced
(Phi,S) normalization and full central hadronic coefficients.  It is not the
full-v20 prediction: the physical projected light current is portal dependent
and may be flavour-off-diagonal.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

import full_fermion_matching_v20 as full


ROOT = Path(__file__).resolve().parent
VS_GEV = full.VS_GEV
VPHI_GEV = full.VPHI_GEV
X_PHI = full.X_PHI
X_S = full.X_S
N_COVER = full.N_COVER
N_PHYSICAL_WALL = 1
FA_GEV = full.FA_GEV
FA_APPROX_GEV = VS_GEV / N_COVER

MA_EV = 153.5e-6
ME_GEV = full.ME_GEV
MP_GEV = full.MP_GEV
MN_GEV = full.MN_GEV
GAE_TRGB_95CL = full.GAE_TRGB_95CL
SN1987A_QUADRATIC_BOUND = full.SN1987A_QUADRATIC_BOUND
FA_UNIVERSAL_SN_GEV = full.FA_UNIVERSAL_SN_GEV
MA_UNIVERSAL_SN_EV = 5.3e-2

TAN_BETA_V20 = full.TAN_BETA_COMMITTED
TAN_BETA_NATURAL = full.TAN_BETA_HIGH_EXAMPLE
TAN_BETA_SCAN = full.TAN_BETA_DECLARED_RANGE


def sn1987a_quadratic(*, g_an: float, g_ap: float) -> float:
    return full.sn1987a_quadratic(g_an=g_an, g_ap=g_ap)


def aligned_coefficients(tan_beta: float) -> dict:
    row = full.coefficients_at_tan_beta(tan_beta)
    return {
        **row,
        "C_p": row["C_p_central"],
        "C_n": row["C_n_central"],
        "g_ap": row["g_ap_central"],
        "g_an": row["g_an_central"],
        "SN1987A_quadratic_lhs": row["SN1987A_quadratic_lhs_central"],
        "SN1987A_amplitude_margin": row[
            "SN1987A_amplitude_margin_central"
        ],
    }


def exact_coefficients(tan_beta: float) -> dict:
    """Compatibility alias; exact only under aligned-current assumption."""
    return aligned_coefficients(tan_beta)


def ert_leading_extrapolation(
    tan_beta: float,
    *,
    acknowledge_not_full_matching: bool = False,
) -> dict:
    """Legacy rounded ERT Eq. (125) comparison."""
    if not acknowledge_not_full_matching:
        raise RuntimeError(
            "Legacy rounded ERT comparison, not full v20. Pass "
            "acknowledge_not_full_matching=True."
        )
    sin2, cos2 = full.beta_fractions(tan_beta)
    c_e = sin2 / N_COVER
    c_p = -0.47 + (3.0 / N_COVER) * (0.29 * cos2 - 0.15 * sin2)
    c_n = -0.02 + (3.0 / N_COVER) * (-0.14 * cos2 + 0.28 * sin2)
    g_ae = c_e * ME_GEV / FA_GEV
    g_ap = c_p * MP_GEV / FA_GEV
    g_an = c_n * MN_GEV / FA_GEV
    sn_lhs = sn1987a_quadratic(g_an=g_an, g_ap=g_ap)
    return {
        "classification": "LEGACY_ROUNDED_ERT_COMPARISON_NOT_FINAL",
        "tan_beta": tan_beta,
        "sin2_beta": sin2,
        "cos2_beta": cos2,
        "C_e": c_e,
        "C_p": c_p,
        "C_n": c_n,
        "g_ae": g_ae,
        "g_ap": g_ap,
        "g_an": g_an,
        "SN1987A_quadratic_lhs": sn_lhs,
        "SN1987A_amplitude_margin": math.sqrt(
            SN1987A_QUADRATIC_BOUND / sn_lhs
        ),
    }


def q_portal_one_family_diagnostic(
    *,
    lambda_q: float = 1.0,
    y_q: float = 1.0,
) -> dict:
    """One-family physical-current and Berry diagnostic."""
    if y_q == 0.0:
        raise ValueError("y_q must be nonzero")
    a = np.zeros((2, 5), dtype=complex)
    a[0, 3] = 1.0
    a[1, 4] = 1.0
    b = np.zeros((1, 5), dtype=complex)
    b[0, 0] = (lambda_q / y_q) * VS_GEV / VPHI_GEV
    c = np.zeros((2, 1), dtype=complex)
    row = full.portal_current_match(a, b, c, 1.0)
    eigen = np.linalg.eigvalsh(row["Q_projected"])
    return {
        "classification": "PHYSICAL_PROJECTED_CURRENT_DIAGNOSTIC",
        "mixing_ratio_abs": abs(lambda_q / y_q) * VS_GEV / VPHI_GEV,
        "Q_projected_eigenvalues": [float(x) for x in eigen],
        "projected_shift_norm": row["projected_shift_norm"],
        "berry_norm": row["berry_norm"],
        "moving_identity_error": row["moving_identity_error"],
        "physical_shift_is_zero": False,
        "message": (
            "Q_proj and the Berry connection sum to a coordinate identity, "
            "but Q_proj remains the portal-dependent regular current."
        ),
    }


def build_report() -> dict:
    matching = full.build_report()
    low = aligned_coefficients(TAN_BETA_V20)
    high = aligned_coefficients(TAN_BETA_NATURAL)
    envelope = matching["aligned_beta_envelope"]
    return {
        "status": (
            "ALIGNED_LEADING_BENCHMARK_REPRODUCED__"
            "FULL_PORTAL_FLAVOUR_MATCHING_OPEN"
        ),
        "correction_history": {
            "first_overclaim": (
                "Rounded N=17 formulas were called unique full-v20 values."
            ),
            "second_overclaim": (
                "The moving-frame identity Q_proj+A_B=I was then mistaken "
                "for a portal-independent physical current."
            ),
            "current_resolution": (
                "The physical projected current is Q_proj=I-4W and depends on "
                "the full A,B,C,D portals and their Yukawa alignment."
            ),
        },
        "normalization": {
            **matching["normalization"],
            "physical_gauge_inequivalent_wall_count": N_PHYSICAL_WALL,
        },
        "portal_current_status": matching["portal_current_result"],
        "aligned_symbolic_benchmark": matching["aligned_symbolic_benchmark"],
        "aligned_examples_not_full_predictions": {
            "tan_beta_1p5": low,
            "tan_beta_high": high,
        },
        "aligned_bound_checks_only": {
            "tan_beta_interval": envelope["tan_beta_interval"],
            "TRGB_safe_central": envelope["aligned_TRGB_safe_central"],
            "SN1987A_safe_central": envelope["aligned_SN1987A_safe_central"],
            "model_independent_SN_fa_pass": envelope[
                "model_independent_SN_fa_safe"
            ],
            "full_model_pass": None,
        },
        "one_family_diagnostic": q_portal_one_family_diagnostic(),
        "missing_for_full_v20_matching": matching["missing_for_full_matching"],
        "verdict": (
            "The exact reduced normalization and aligned-current central "
            "benchmark are reproducible, but arbitrary anomalon portals can "
            "change Q_proj and generate flavour dependence. Exact full-v20 "
            "C_e,C_p,C_n and a full stellar/SN verdict remain open."
        ),
    }


def main() -> int:
    report = build_report()
    (ROOT / "FERMION_COUPLINGS_150UEV_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    low = report["aligned_examples_not_full_predictions"]["tan_beta_1p5"]
    print(
        json.dumps(
            {
                "status": report["status"],
                "f_a_exact_GeV": report["normalization"]["f_a_GeV"],
                "aligned_tan_beta_1p5": {
                    "C_e": low["C_e"],
                    "C_p": low["C_p_central"],
                    "C_n": low["C_n_central"],
                },
                "full_model_pass": None,
                "verdict": report["verdict"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
