#!/usr/bin/env python3
"""Low-energy electron and nucleon coupling audit for the v20 150 ueV axion.

This implements the SO(10)xU(1)_PQ matching formulas of Ernst, Ringwald
and Tamarit (JHEP 02 (2018) 103, Eq. 6.3), adapted to the v20 anomaly
normalization. The relevant denominator is the covering-space color
anomaly/domain-wall number N_cover=17, not the physical one-wall count
after quotienting by the gauged Z17.

Scope: leading current matching for the three light chiral families.
It does not re-fit anomalon portal matrices or reproduce supernova
likelihoods from raw simulation data.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

VS_GEV = 6.313855e11
N_COVER = 17
N_PHYSICAL_WALL = 1
FA_GEV = VS_GEV / N_COVER
MA_EV = 153.5e-6
ME_GEV = 0.00051099895
MP_GEV = 0.93827208816
MN_GEV = 0.93956542052

# Conservative published comparison anchors.
GAE_TRGB_95CL = 1.3e-13
GAN_GENERIC_SN_ENVELOPE = 1.0e-9
MA_CANONICAL_SN_EV = 1.0e-2
FA_UNIVERSAL_SN_GEV = 1.1e8
MA_UNIVERSAL_SN_EV = 5.3e-2

TAN_BETA_V20 = 1.5000000000002063
TAN_BETA_NATURAL = 41.338069578693386
TAN_BETA_SCAN = (1.5, 50.0)


def coefficients(tan_beta: float) -> dict:
    if tan_beta <= 0:
        raise ValueError("tan_beta must be positive")
    sin2 = tan_beta * tan_beta / (1.0 + tan_beta * tan_beta)
    cos2 = 1.0 / (1.0 + tan_beta * tan_beta)

    # ERT Eq. (6.3), with N_DW -> N_cover=17.
    c_e = sin2 / N_COVER
    c_p = -0.47 + (3.0 / N_COVER) * (0.29 * cos2 - 0.15 * sin2)
    c_n = -0.02 + (3.0 / N_COVER) * (-0.14 * cos2 + 0.28 * sin2)
    sigma_c_nucleon = math.hypot(0.03, (3.0 / N_COVER) * 0.02)

    g_ae = c_e * ME_GEV / FA_GEV
    g_ap = c_p * MP_GEV / FA_GEV
    g_an = c_n * MN_GEV / FA_GEV
    sigma_g_ap = sigma_c_nucleon * MP_GEV / FA_GEV
    sigma_g_an = sigma_c_nucleon * MN_GEV / FA_GEV

    return {
        "tan_beta": tan_beta,
        "sin2_beta": sin2,
        "cos2_beta": cos2,
        "tree_quark_coefficients": {
            "C_u0": cos2 / N_COVER,
            "C_d0": sin2 / N_COVER,
        },
        "C_e": c_e,
        "C_p": c_p,
        "C_n": c_n,
        "sigma_C_p_hadronic": sigma_c_nucleon,
        "sigma_C_n_hadronic": sigma_c_nucleon,
        "g_ae": g_ae,
        "g_ap": g_ap,
        "g_an": g_an,
        "sigma_g_ap_hadronic": sigma_g_ap,
        "sigma_g_an_hadronic": sigma_g_an,
        "electron_margin_limit_over_prediction": GAE_TRGB_95CL / abs(g_ae),
        "sn_generic_margin_limit_over_max_nucleon": (
            GAN_GENERIC_SN_ENVELOPE / max(abs(g_ap), abs(g_an))
        ),
    }


def build_report() -> dict:
    v20 = coefficients(TAN_BETA_V20)
    natural = coefficients(TAN_BETA_NATURAL)
    lo = coefficients(TAN_BETA_SCAN[0])
    hi = coefficients(TAN_BETA_SCAN[1])
    max_gae = max(abs(lo["g_ae"]), abs(hi["g_ae"]))
    max_gan = max(abs(lo["g_an"]), abs(hi["g_an"]))
    max_gap = max(abs(lo["g_ap"]), abs(hi["g_ap"]))

    return {
        "status": "PASS_WITH_STATED_MATCHING_ASSUMPTIONS",
        "normalization": {
            "v_S_GeV": VS_GEV,
            "covering_color_anomaly_N": N_COVER,
            "physical_domain_wall_count_after_Z17_quotient": N_PHYSICAL_WALL,
            "f_a_GeV": FA_GEV,
            "warning": (
                "Local derivative couplings use the covering anomaly N=17. "
                "Substituting the physical one-wall count N=1 would overstate "
                "the tree fermion coefficients by a factor of 17."
            ),
        },
        "benchmarks": {
            "v20_single_scale_fit": v20,
            "natural_1e14_fit": natural,
        },
        "tan_beta_envelope_1p5_to_50": {
            "g_ae_abs_min": min(abs(lo["g_ae"]), abs(hi["g_ae"])),
            "g_ae_abs_max": max_gae,
            "g_ap_abs_min": min(abs(lo["g_ap"]), abs(hi["g_ap"])),
            "g_ap_abs_max": max_gap,
            "g_an_central_abs_min": min(abs(lo["g_an"]), abs(hi["g_an"])),
            "g_an_central_abs_max": max_gan,
            "note": "The quoted hadronic uncertainty on C_n is comparable to its central value.",
        },
        "published_bound_checks": {
            "TRGB_electron": {
                "limit_95CL": GAE_TRGB_95CL,
                "largest_prediction_in_scan": max_gae,
                "safety_factor": GAE_TRGB_95CL / max_gae,
                "passes": max_gae < GAE_TRGB_95CL,
            },
            "generic_SN_nucleon_envelope": {
                "indicative_excluded_above": GAN_GENERIC_SN_ENVELOPE,
                "largest_predicted_abs_nucleon_coupling": max(max_gap, max_gan),
                "safety_factor": GAN_GENERIC_SN_ENVELOPE / max(max_gap, max_gan),
                "passes": max(max_gap, max_gan) < GAN_GENERIC_SN_ENVELOPE,
                "caveat": "Envelope comparison, not a reproduction of the SN likelihood.",
            },
            "canonical_QCD_axion_SN_mass": {
                "literature_scale_eV": MA_CANONICAL_SN_EV,
                "v20_mass_eV": MA_EV,
                "safety_factor": MA_CANONICAL_SN_EV / MA_EV,
                "passes": MA_EV < MA_CANONICAL_SN_EV,
            },
            "universal_SN_QCD_axion": {
                "f_a_lower_GeV_68CL": FA_UNIVERSAL_SN_GEV,
                "v20_f_a_GeV": FA_GEV,
                "f_a_safety_factor": FA_GEV / FA_UNIVERSAL_SN_GEV,
                "mass_upper_eV_68CL": MA_UNIVERSAL_SN_EV,
                "v20_mass_eV": MA_EV,
                "mass_safety_factor": MA_UNIVERSAL_SN_EV / MA_EV,
                "passes": FA_GEV > FA_UNIVERSAL_SN_GEV and MA_EV < MA_UNIVERSAL_SN_EV,
            },
        },
        "assumptions": [
            "The three light chiral families inherit the ordinary 16_F PQ current at leading order.",
            "Anomalon-induced light-family admixtures do not introduce order-one non-universal PQ charges.",
            "The standard two-Higgs SO(10) current matching and the repository tan(beta) convention apply.",
            "Hadronic matching uses the ERT Eq. (6.3) numerical coefficients and uncertainties.",
        ],
        "verdict": (
            "The electron and nucleon coupling gap is closed at leading order: "
            "the v20 benchmark passes the published TRGB and supernova envelopes "
            "by large margins. The 37 GHz photon/local-DM benchmark remains open. "
            "This does not establish the cosmological abundance or prove the model."
        ),
    }


def main() -> int:
    report = build_report()
    out = Path(__file__).resolve().parent / "FERMION_COUPLINGS_150UEV_VERDICT.json"
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "f_a_GeV": report["normalization"]["f_a_GeV"],
        "v20": report["benchmarks"]["v20_single_scale_fit"],
        "checks": report["published_bound_checks"],
        "verdict": report["verdict"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
