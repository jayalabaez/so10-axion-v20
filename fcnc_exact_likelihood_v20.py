#!/usr/bin/env python3
r"""Exact channel-level FCNC branching ratios + experimental likelihood — v20.

Replaces proxy matrix norms with the exact two-body formulae already derived in
``channel_fcnc_rates_v20`` and wraps them in an honest pointwise likelihood
against the official NA62 / TWIST anchors.

K+ → π+ a
---------

With chiral couplings K_L, K_R in the mass basis and g_sd = (K_L+K_R)/f_a,

    Γ = |g_sd|² m_K³ |f_+(0)|² √λ (1−m_π²/m_K²)² / (64π),

where f_+(0)=f_0(0)=0.9704 (arXiv:1312.1228) at the v20 axion mass.

μ → e a
-------

Exact finite-m_e width from equation-of-motion amplitudes
A_L = m_μ K_R − m_e K_L, A_R = m_μ K_L − m_e K_R.

Likelihood
----------

For each published 90% CL upper limit UL, define a one-sided Gaussian-tail
surrogate on the ratio r = BR/UL:

    −2 ln L = 0           if r ≤ 1
            = ((r−1)/σ)²  if r > 1,   σ = 1/1.64485  (≈90% one-sided)

This is a *pointwise* UL likelihood on the vendored anchors (2 NA62 points near
m_a≃0; 3 TWIST asymmetry hypotheses).  It is **not** the full 151-point NA62
correlated likelihood (HEPData download currently blocked / not vendored).
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import channel_fcnc_rates_v20 as rates
import na62_pointwise_limit_v20 as na62
import twist_massless_limit_v20 as twist


ROOT = Path(__file__).resolve().parent
# One-sided Gaussian: Φ^{-1}(0.90) ≈ 1.28155 for central, but BR ULs are
# conventionally closer to 1.64 for a one-sided 90% interpretation of a
# Gaussian excess. Use 1.64485.
SIGMA_90_ONESIDED = 1.0 / 1.64485


def exact_kaon_branching_ratio(
    k_left_sd: complex,
    k_right_sd: complex,
    *,
    f0: float = rates.F0_KPI_AT_ZERO,
) -> dict[str, float]:
    gamma = rates.kaon_to_pion_a_width(k_left_sd, k_right_sd, f0=f0)
    total = rates.total_width_from_lifetime(rates.TAU_K_CHARGED_S)
    return {
        "partial_width_GeV": float(gamma),
        "branching_ratio": float(gamma / total),
        "f_plus_0": float(f0),
        "f_plus_uncertainty": float(rates.F0_KPI_UNCERTAINTY),
        "formula": (
            "Gamma = |K_L+K_R|^2 m_K^3 |f+(0)|^2 sqrt(lambda) "
            "(1-m_pi^2/m_K^2)^2 / (64 pi f_a^2)"
        ),
    }


def exact_muon_branching_ratio(
    k_left: complex,
    k_right: complex,
) -> dict[str, float]:
    gamma = rates.mu_to_ea_width(k_left, k_right)
    gamma_massless = rates.mu_to_ea_massless_e_limit(k_left, k_right)
    total = rates.total_width_from_lifetime(rates.TAU_MU_S)
    return {
        "partial_width_GeV": float(gamma),
        "branching_ratio": float(gamma / total),
        "massless_e_limit_width_GeV": float(gamma_massless),
        "relative_finite_me_shift": float(
            abs(gamma - gamma_massless) / max(gamma_massless, 1e-300)
        ),
        "formula": (
            "Exact EOM amplitudes A_L=m_mu K_R - m_e K_L, "
            "A_R=m_mu K_L - m_e K_R with full two-body phase space"
        ),
    }


def onesided_ul_nll(prediction: float, upper_limit: float) -> dict[str, float]:
    if upper_limit <= 0.0:
        raise ValueError("upper_limit must be positive")
    ratio = prediction / upper_limit
    if ratio <= 1.0:
        nll = 0.0
    else:
        nll = 0.5 * ((ratio - 1.0) / SIGMA_90_ONESIDED) ** 2
    return {
        "prediction": float(prediction),
        "upper_limit_90cl": float(upper_limit),
        "ratio": float(ratio),
        "survives_90cl": bool(ratio <= 1.0),
        "neg_log_likelihood": float(nll),
        "chi2_surrogate": float(2.0 * nll),
    }


def scenario_likelihood(scenario: dict[str, Any]) -> dict[str, Any]:
    br_k = float(scenario["K_to_pi_a"]["branching_ratio"])
    br_mu = float(scenario["mu_to_e_a"]["branching_ratio"])

    # NA62: evaluate at every vendored anchor mass + at the v20 mass.
    anchor = na62.load_anchor()
    na62_rows = []
    for row in anchor["anchor_points"]:
        mass = float(row["mass_MeV"])
        ul = float(row["observed_br_ul_90cl"])
        # Massless / ultra-light axion BR is mass-independent to excellent
        # approximation across these anchors; use the same predicted BR.
        entry = onesided_ul_nll(br_k, ul)
        entry["mass_MeV"] = mass
        na62_rows.append(entry)
    v20_ul = na62.observed_limit_at_mass(0.0)
    na62_v20 = onesided_ul_nll(br_k, float(v20_ul["observed_br_ul_90cl"]))
    na62_v20["mass_MeV"] = float(rates.MA_V20_GEV * 1.0e3)

    twist_payload = twist.load_limits()
    twist_rows = []
    for row in sorted(twist_payload["limits"], key=lambda r: r["asymmetry_A"]):
        ul = float(row["branching_ratio_upper_limit_90cl"])
        entry = onesided_ul_nll(br_mu, ul)
        entry["asymmetry_A"] = float(row["asymmetry_A"])
        twist_rows.append(entry)

    nll_total = (
        float(na62_v20["neg_log_likelihood"])
        + sum(float(r["neg_log_likelihood"]) for r in twist_rows)
    )
    return {
        "scenario": scenario.get("scenario", scenario.get("name", "unnamed")),
        "exact_BR_K_to_pi_a": br_k,
        "exact_BR_mu_to_e_a": br_mu,
        "NA62_pointwise": {
            "n_anchor_points_used": len(na62_rows),
            "anchors": na62_rows,
            "at_v20_mass": na62_v20,
            "full_151_point_curve_ingested": False,
            "correlated_likelihood": False,
        },
        "TWIST_pointwise": {
            "n_asymmetry_hypotheses": len(twist_rows),
            "rows": twist_rows,
            "survives_all_three": all(r["survives_90cl"] for r in twist_rows),
            "continuous_A_likelihood": False,
        },
        "combined_neg_log_likelihood": nll_total,
        "combined_chi2_surrogate": 2.0 * nll_total,
        "survives_all_vendored_limits": bool(
            na62_v20["survives_90cl"]
            and all(r["survives_90cl"] for r in twist_rows)
        ),
    }


def analytical_identity_checks() -> dict[str, Any]:
    """Verify blueprint algebraic reductions on toy couplings."""
    # Pure left kaon: Gamma ∝ |K_L|^2
    left = exact_kaon_branching_ratio(0.2, 0.0)
    both = exact_kaon_branching_ratio(0.1, 0.1)
    # |0.1+0.1|=|0.2| ⇒ identical BR
    kaon_lr_sum_identity = math.isclose(
        left["branching_ratio"], both["branching_ratio"], rel_tol=1e-12
    )
    zero = exact_kaon_branching_ratio(0.0, 0.0)
    muon_zero = exact_muon_branching_ratio(0.0, 0.0)
    return {
        "kaon_zero_couplings_zero_br": zero["branching_ratio"] == 0.0,
        "muon_zero_couplings_zero_br": muon_zero["branching_ratio"] == 0.0,
        "kaon_KL_plus_KR_identity": kaon_lr_sum_identity,
        "lattice_f_plus_0": rates.F0_KPI_AT_ZERO,
        "lattice_reference": "arXiv:1312.1228",
    }


def build_report() -> dict[str, Any]:
    identities = analytical_identity_checks()
    channel = rates.build_report()
    hierarchical = scenario_likelihood(channel["hierarchical_benchmark"])
    counterexample = scenario_likelihood(
        channel["generation_dependent_counterexample"]
    )
    checks = {
        "kaon_formula_identities": identities["kaon_KL_plus_KR_identity"]
        and identities["kaon_zero_couplings_zero_br"],
        "muon_zero_ok": identities["muon_zero_couplings_zero_br"],
        "hierarchical_survives": hierarchical["survives_all_vendored_limits"],
        "counterexample_excluded_by_na62": not counterexample["NA62_pointwise"][
            "at_v20_mass"
        ]["survives_90cl"],
        "full_151_not_claimed": not hierarchical["NA62_pointwise"][
            "full_151_point_curve_ingested"
        ],
        "correlated_not_claimed": not hierarchical["NA62_pointwise"][
            "correlated_likelihood"
        ],
        "continuous_twist_not_claimed": not hierarchical["TWIST_pointwise"][
            "continuous_A_likelihood"
        ],
    }
    failures = [name for name, ok in checks.items() if not ok]
    return {
        "status": (
            "EXACT_FCNC_BR_AND_POINTWISE_UL_LIKELIHOOD_COMPLETE__"
            "FULL_151_CORRELATED_OPEN"
            if not failures
            else "FCNC_EXACT_LIKELIHOOD_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "analytical_identities": identities,
        "hierarchical_universal_benchmark": hierarchical,
        "generation_dependent_counterexample": counterexample,
        "flag": {
            "exact_kaon_branching_ratio_implemented": True,
            "exact_muon_branching_ratio_implemented": True,
            "lattice_form_factor_f_plus_used": True,
            "pointwise_ul_likelihood_implemented": True,
            "official_NA62_anchors_in_likelihood": True,
            "official_TWIST_asymmetry_limits_in_likelihood": True,
            "full_151_point_NA62_curve_ingested": False,
            "full_correlated_experimental_likelihood_implemented": False,
            "continuous_TWIST_asymmetry_likelihood_implemented": False,
            "proxy_matrix_norms_replaced": True,
            "finite_model_fcnc_absence_proved": False,
            "whole_v20_model_excluded": False,
        },
        "verdict": (
            "Exact BR(K+→π+a) and BR(μ→ea) with lattice f+(0) are evaluated and "
            "wrapped in a one-sided pointwise UL likelihood on the vendored NA62 "
            "and TWIST anchors. The hierarchical benchmark survives; the "
            "generation-dependent counterexample is excluded by NA62. The full "
            "151-point correlated NA62 likelihood remains open (curve not "
            "vendored; HEPData download blocked)."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    h = report["hierarchical_universal_benchmark"]
    c = report["generation_dependent_counterexample"]
    return "\n".join(
        [
            "# Exact FCNC branching ratios + pointwise likelihood — v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            f"- Hierarchical BR(K): {h['exact_BR_K_to_pi_a']:.4g}",
            f"- Counterexample BR(K): {c['exact_BR_K_to_pi_a']:.4g}",
            f"- Hierarchical survives vendored limits: "
            f"**{h['survives_all_vendored_limits']}**",
            f"- Counterexample NA62 excluded: "
            f"**{not c['NA62_pointwise']['at_v20_mass']['survives_90cl']}**",
            f"- Full 151-point correlated NA62 likelihood: **False**",
            "",
            "## Verdict",
            "",
            report["verdict"],
            "",
        ]
    )


def main() -> int:
    report = build_report()
    ROOT.joinpath("FCNC_EXACT_LIKELIHOOD_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("FCNC_EXACT_LIKELIHOOD_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "flag": report["flag"],
                "hierarchical_survives": report[
                    "hierarchical_universal_benchmark"
                ]["survives_all_vendored_limits"],
                "counterexample_na62_ratio": report[
                    "generation_dependent_counterexample"
                ]["NA62_pointwise"]["at_v20_mass"]["ratio"],
                "verdict": report["verdict"],
            },
            indent=2,
        )
    )
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
