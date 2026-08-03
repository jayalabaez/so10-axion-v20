#!/usr/bin/env python3
r"""Channel-level axion FCNC rates for the v20 candidate.

This module replaces norm-times-mass proxies with explicit two-body decay
formulae. It remains fail-closed about the pieces that are not yet derived.

Conventions
-----------

The fermion interaction is

    L = (partial_mu a / f_a) [fbar_L K_L gamma^mu f_L
                              + fbar_R K_R gamma^mu f_R].

For charged leptons, the exact two-body rate implemented here reduces in the
m_e -> 0 limit to Eq. (5) of arXiv:1908.00008:

    Gamma(mu -> e a) = m_mu^3 (|K_L|^2+|K_R|^2)
                       (1-m_a^2/m_mu^2)^2 /(32 pi f_a^2).

For K+ -> pi+ a, the implementation follows the left-handed-current
normalization and Eq. (5)/the decay-rate equation of arXiv:1901.02031.  For a
general left/right current, the pseudoscalar-to-pseudoscalar matrix element
depends on K_L+K_R because the axial current vanishes by parity.

The K->pi scalar form factor at the v20 axion mass is approximated by its
q^2=0 value, f_0(0)=f_+(0)=0.9704, from arXiv:1312.1228.  The difference at
m_a=153.5 micro-eV is negligible compared with the quoted lattice uncertainty.

Experimental references are deliberately used only as conservative comparison
scales, not digitized likelihoods:

* TWIST, arXiv:1409.0638: BR(mu+ -> e+ X0) limits up to 5.8e-5 below 13 MeV,
  depending on angular asymmetry.
* NA62, arXiv:2507.17286: pointwise K+ -> pi+ X limits reach the 1e-11 level.
  This repository uses 1e-10 as a conservative non-likelihood reference scale
  until the published pointwise curve and correlations are ingested.

Scientific scope
----------------

The family-space portal current can be rotated into left/right mass bases under
an explicit common-16-current assumption. Component-specific threshold effects,
a UV derivation of independent chiral currents, and pointwise experimental
likelihoods remain open. Therefore this module can produce conditional rates,
but cannot prove finite-model FCNC absence or unconditional exclusion.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import full_fermion_matching_v20 as matching
import physical_cf_matching_v20 as physical
import portal_tensors_abcd_v20 as portals


ROOT = Path(__file__).resolve().parent
HBAR_GEV_S = 6.582119569e-25

# Particle masses/lifetimes in GeV and seconds. Central values are sufficient
# for a rate hierarchy spanning many orders of magnitude.
M_E_GEV = 0.00051099895
M_MU_GEV = 0.1056583755
TAU_MU_S = 2.1969811e-6
M_K_CHARGED_GEV = 0.493677
M_PI_CHARGED_GEV = 0.13957039
TAU_K_CHARGED_S = 1.2380e-8

MA_V20_GEV = 153.5e-6 * 1e-9
F0_KPI_AT_ZERO = 0.9704
F0_KPI_UNCERTAINTY = 0.0032

# Conservative comparison scales only. They are not encoded likelihoods.
TWIST_CONSERVATIVE_BR_LIMIT = 5.8e-5
NA62_CONSERVATIVE_BR_SCALE = 1.0e-10


def _complex_payload(value: complex) -> dict[str, float]:
    return {"real": float(np.real(value)), "imag": float(np.imag(value))}


def kallen(x: float, y: float, z: float) -> float:
    """Kallen lambda(x,y,z), with tiny negative roundoff clipped to zero."""
    value = x * x + y * y + z * z - 2.0 * (x * y + x * z + y * z)
    if value < 0.0 and abs(value) < 1e-24 * max(x * x, y * y, z * z, 1.0):
        return 0.0
    return float(value)


def total_width_from_lifetime(tau_s: float) -> float:
    if tau_s <= 0.0:
        raise ValueError("lifetime must be positive")
    return HBAR_GEV_S / tau_s


def mu_to_ea_width(
    k_left: complex,
    k_right: complex,
    *,
    f_a_gev: float = matching.FA_GEV,
    m_a_gev: float = MA_V20_GEV,
    m_mu_gev: float = M_MU_GEV,
    m_e_gev: float = M_E_GEV,
) -> float:
    """Exact two-body width for derivative chiral mu-e couplings.

    The equation-of-motion amplitudes are

        A_L = m_mu K_R - m_e K_L,
        A_R = m_mu K_L - m_e K_R.

    The result includes finite m_e and m_a and spin averages the initial muon.
    """
    if f_a_gev <= 0.0:
        raise ValueError("f_a must be positive")
    if min(m_a_gev, m_mu_gev, m_e_gev) < 0.0:
        raise ValueError("masses must be non-negative")
    if m_a_gev + m_e_gev >= m_mu_gev:
        return 0.0

    a_left = m_mu_gev * k_right - m_e_gev * k_left
    a_right = m_mu_gev * k_left - m_e_gev * k_right
    lam = kallen(m_mu_gev**2, m_e_gev**2, m_a_gev**2)
    phase = math.sqrt(max(lam, 0.0))
    invariant = m_mu_gev**2 + m_e_gev**2 - m_a_gev**2
    spin_average = (
        0.5 * (abs(a_left) ** 2 + abs(a_right) ** 2) * invariant
        + 2.0
        * m_mu_gev
        * m_e_gev
        * float(np.real(a_left * np.conj(a_right)))
    )
    width = phase * spin_average / (16.0 * math.pi * m_mu_gev**3 * f_a_gev**2)
    return float(max(width, 0.0))


def mu_to_ea_massless_e_limit(
    k_left: complex,
    k_right: complex,
    *,
    f_a_gev: float = matching.FA_GEV,
    m_a_gev: float = MA_V20_GEV,
    m_mu_gev: float = M_MU_GEV,
) -> float:
    if m_a_gev >= m_mu_gev:
        return 0.0
    coupling = abs(k_left) ** 2 + abs(k_right) ** 2
    return float(
        m_mu_gev**3
        * coupling
        * (1.0 - m_a_gev**2 / m_mu_gev**2) ** 2
        / (32.0 * math.pi * f_a_gev**2)
    )


def kaon_to_pion_a_width(
    k_left_sd: complex,
    k_right_sd: complex,
    *,
    f_a_gev: float = matching.FA_GEV,
    m_a_gev: float = MA_V20_GEV,
    m_k_gev: float = M_K_CHARGED_GEV,
    m_pi_gev: float = M_PI_CHARGED_GEV,
    f0: float = F0_KPI_AT_ZERO,
) -> float:
    """Width for K+ -> pi+ a from dimensionless chiral flavor matrices.

    For the convention in the module docstring,

        g_L = K_L/f_a,  g_R = K_R/f_a,

    and the rate is obtained from the published pure-left formula by replacing
    g_sd with g_L+g_R. This is exact for the pseudoscalar-to-pseudoscalar vector
    current at this EFT order.
    """
    if f_a_gev <= 0.0:
        raise ValueError("f_a must be positive")
    if f0 <= 0.0:
        raise ValueError("f0 must be positive")
    if m_a_gev + m_pi_gev >= m_k_gev:
        return 0.0

    lambda_dimensionless = (
        1.0 - (m_a_gev + m_pi_gev) ** 2 / m_k_gev**2
    ) * (1.0 - (m_a_gev - m_pi_gev) ** 2 / m_k_gev**2)
    g_sum = (k_left_sd + k_right_sd) / f_a_gev
    width = (
        m_k_gev**3
        * abs(g_sum) ** 2
        * f0**2
        * math.sqrt(max(lambda_dimensionless, 0.0))
        * (1.0 - m_pi_gev**2 / m_k_gev**2) ** 2
        / (64.0 * math.pi)
    )
    return float(max(width, 0.0))


def _rotate(q: np.ndarray, unitary: np.ndarray) -> np.ndarray:
    return unitary.conj().T @ q @ unitary


def chiral_mass_basis_currents(
    q_family: np.ndarray,
    bases: dict[str, Any],
) -> dict[str, np.ndarray]:
    """Rotate one common family current into explicit chiral mass bases.

    For the symmetric charged-lepton matrix M=U D U^T used in the repository,
    U_eL=U and U_eR=U*. Quark rotations use the SVD left/right matrices already
    returned by ``physical.flavour_mass_bases``.
    """
    q = np.asarray(q_family, dtype=complex)
    u_e_left = np.asarray(bases["U_e"], dtype=complex)
    u_e_right = u_e_left.conj()
    u_d_left = np.asarray(bases["U_dL"], dtype=complex)
    u_d_right = np.asarray(bases["U_dR"], dtype=complex)
    u_u_left = np.asarray(bases["U_uL"], dtype=complex)
    u_u_right = np.asarray(bases["U_uR"], dtype=complex)
    return {
        "K_eL": _rotate(q, u_e_left),
        "K_eR": _rotate(q, u_e_right),
        "K_dL": _rotate(q, u_d_left),
        "K_dR": _rotate(q, u_d_right),
        "K_uL": _rotate(q, u_u_left),
        "K_uR": _rotate(q, u_u_right),
    }


def _portal_current(block: dict[str, np.ndarray]) -> np.ndarray:
    result = matching.portal_current_match(
        block["A"], block["B"], block["C"], block["D"]
    )
    return np.asarray(result["Q_projected"], dtype=complex)


def hierarchical_block() -> dict[str, np.ndarray]:
    return portals.build_abcd(
        portals.PortalCouplings(
            y_P=1.0,
            y_R=1.0,
            y_Q=1.0,
            lam_Q_F=(0.2, 0.2, 0.2),
            lam_Q_R=0.0,
            lam_S_Q_Rbar=0.0,
            y_F_Pbar=(0.0, 0.0, 0.0),
            y_F_Rbar=(0.0, 0.0, 0.0),
        )
    )


def generation_dependent_counterexample_block() -> dict[str, np.ndarray]:
    return portals.build_abcd(
        portals.PortalCouplings(
            y_Q=1.0e-6,
            lam_Q_F=(1.0, 0.01, 0.0),
            lam_Q_R=0.3,
            lam_S_Q_Rbar=0.2,
        )
    )


def scenario_rates(
    name: str,
    block: dict[str, np.ndarray],
    bases: dict[str, Any],
) -> dict[str, Any]:
    q = _portal_current(block)
    currents = chiral_mass_basis_currents(q, bases)

    # Ordering is (e,mu,tau) and (d,s,b); transitions use final,initial.
    k_e_left = complex(currents["K_eL"][0, 1])
    k_e_right = complex(currents["K_eR"][0, 1])
    k_sd_left = complex(currents["K_dL"][0, 1])
    k_sd_right = complex(currents["K_dR"][0, 1])

    gamma_mu = mu_to_ea_width(k_e_left, k_e_right)
    gamma_mu_approx = mu_to_ea_massless_e_limit(k_e_left, k_e_right)
    br_mu = gamma_mu / total_width_from_lifetime(TAU_MU_S)

    gamma_k = kaon_to_pion_a_width(k_sd_left, k_sd_right)
    br_k = gamma_k / total_width_from_lifetime(TAU_K_CHARGED_S)

    q_scalar_departure = float(
        np.linalg.norm(q - np.trace(q) * np.eye(3, dtype=complex) / 3.0)
    )
    return {
        "scenario": name,
        "family_current": {
            "scalar_departure": q_scalar_departure,
            "exactly_scalar_to_1e_14": q_scalar_departure <= 1.0e-14,
        },
        "mass_basis_couplings": {
            "K_eL_e_mu": _complex_payload(k_e_left),
            "K_eR_e_mu": _complex_payload(k_e_right),
            "K_dL_d_s": _complex_payload(k_sd_left),
            "K_dR_d_s": _complex_payload(k_sd_right),
            "common_16_family_current_assumed": True,
            "component_specific_threshold_current_derived": False,
        },
        "mu_to_e_a": {
            "partial_width_GeV": gamma_mu,
            "branching_ratio": br_mu,
            "massless_e_limit_width_GeV": gamma_mu_approx,
            "relative_exact_vs_massless_e": (
                abs(gamma_mu - gamma_mu_approx) / max(gamma_mu_approx, 1.0e-300)
            ),
            "twist_conservative_limit": TWIST_CONSERVATIVE_BR_LIMIT,
            "below_conservative_twist_limit": br_mu < TWIST_CONSERVATIVE_BR_LIMIT,
            "pointwise_angular_likelihood_implemented": False,
        },
        "K_to_pi_a": {
            "partial_width_GeV": gamma_k,
            "branching_ratio": br_k,
            "f0_at_zero": F0_KPI_AT_ZERO,
            "f0_uncertainty": F0_KPI_UNCERTAINTY,
            "na62_conservative_reference_scale": NA62_CONSERVATIVE_BR_SCALE,
            "below_conservative_na62_scale": br_k < NA62_CONSERVATIVE_BR_SCALE,
            "pointwise_na62_likelihood_implemented": False,
        },
    }


def build_report() -> dict[str, Any]:
    bases = physical.flavour_mass_bases()
    aligned = scenario_rates("aligned_limit", portals.aligned_limit_abcd(), bases)
    hierarchical = scenario_rates("hierarchical_universal", hierarchical_block(), bases)
    counterexample = scenario_rates(
        "generation_dependent_counterexample",
        generation_dependent_counterexample_block(),
        bases,
    )

    checks = {
        "aligned_mu_rate_zero": aligned["mu_to_e_a"]["partial_width_GeV"] < 1e-50,
        "aligned_kaon_rate_zero": aligned["K_to_pi_a"]["partial_width_GeV"] < 1e-50,
        "hierarchical_rates_finite": math.isfinite(
            hierarchical["mu_to_e_a"]["branching_ratio"]
        )
        and math.isfinite(hierarchical["K_to_pi_a"]["branching_ratio"]),
        "exact_mu_formula_matches_light_e_limit": hierarchical["mu_to_e_a"][
            "relative_exact_vs_massless_e"
        ]
        < 1e-3,
        "counterexample_is_more_flavour_violating": counterexample[
            "K_to_pi_a"
        ]["branching_ratio"]
        > hierarchical["K_to_pi_a"]["branching_ratio"],
        "no_pointwise_likelihood_claim": not hierarchical["K_to_pi_a"][
            "pointwise_na62_likelihood_implemented"
        ]
        and not hierarchical["mu_to_e_a"][
            "pointwise_angular_likelihood_implemented"
        ],
    }
    failures = [name for name, ok in checks.items() if not ok]
    return {
        "status": (
            "CHANNEL_LEVEL_FCNC_RATES_IMPLEMENTED__"
            "UV_COMPONENT_MATCHING_AND_POINTWISE_LIKELIHOODS_OPEN"
            if not failures
            else "CHANNEL_LEVEL_FCNC_RATE_FRAMEWORK_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "conventions": {
            "interaction": (
                "(partial a/f_a)(fbar_L K_L gamma f_L + "
                "fbar_R K_R gamma f_R)"
            ),
            "mu_rate_reference": "arXiv:1908.00008, Eqs. (2),(3),(5)",
            "kaon_rate_reference": "arXiv:1901.02031, Eqs. (5)-(7) and K->pi a rate",
            "form_factor_reference": "arXiv:1312.1228",
            "mu_limit_reference": "TWIST arXiv:1409.0638",
            "kaon_limit_reference": "NA62 arXiv:2507.17286",
        },
        "flavour_basis_source": {
            "tan_beta": float(bases["tan_beta"]),
            "v_r_GeV": float(bases["v_r_GeV"]),
            "chi2": float(bases["chi2"]),
            "natural_scale_viable": bool(bases["natural_scale_viable"]),
        },
        "aligned_limit": aligned,
        "hierarchical_benchmark": hierarchical,
        "generation_dependent_counterexample": counterexample,
        "flag": {
            "channel_level_amplitudes_implemented": True,
            "channel_level_branching_ratios_implemented": True,
            "left_right_mass_basis_rotations_implemented": True,
            "common_16_family_current_assumption": True,
            "component_specific_uv_chiral_currents_derived": False,
            "pointwise_experimental_likelihoods_implemented": False,
            "finite_model_fcnc_absence_proved": False,
            "unconditional_model_exclusion_claimed": False,
        },
        "remaining_for_closure": [
            "derive component-specific left/right PQ currents after all thresholds",
            "propagate the complete portal-Yukawa posterior rather than two examples",
            "ingest the pointwise TWIST angular-asymmetry likelihood",
            "ingest the pointwise NA62 K+->pi+X limit curve and correlations",
            "include form-factor covariance and matching-scale uncertainty",
        ],
        "verdict": (
            "The repository now computes explicit mu->e a and K->pi a partial "
            "widths and branching ratios from left/right mass-basis matrices. "
            "The hierarchical benchmark is conditionally testable, while a "
            "generation-dependent portal can be much more constrained. Full "
            "finite-model FCNC closure remains open because component-specific "
            "UV currents and pointwise experimental likelihoods are not fixed."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    h = report["hierarchical_benchmark"]
    c = report["generation_dependent_counterexample"]
    lines = [
        "# Channel-level FCNC rates — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        "## Hierarchical conditional benchmark",
        "",
        f"- BR(mu -> e a): {h['mu_to_e_a']['branching_ratio']:.6e}",
        f"- BR(K+ -> pi+ a): {h['K_to_pi_a']['branching_ratio']:.6e}",
        "- Pointwise experimental likelihoods: **not implemented**",
        "",
        "## Generation-dependent counterexample",
        "",
        f"- BR(mu -> e a): {c['mu_to_e_a']['branching_ratio']:.6e}",
        f"- BR(K+ -> pi+ a): {c['K_to_pi_a']['branching_ratio']:.6e}",
        "",
        "## Remaining for closure",
        "",
        *[f"- {item}" for item in report["remaining_for_closure"]],
        "",
        "## Verdict",
        "",
        report["verdict"],
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    report = build_report()
    ROOT.joinpath("CHANNEL_FCNC_RATES_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("CHANNEL_FCNC_RATES_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "failures": report["failures"],
                "hierarchical_BR": {
                    "mu_to_e_a": report["hierarchical_benchmark"]["mu_to_e_a"][
                        "branching_ratio"
                    ],
                    "K_to_pi_a": report["hierarchical_benchmark"]["K_to_pi_a"][
                        "branching_ratio"
                    ],
                },
                "counterexample_BR": {
                    "mu_to_e_a": report["generation_dependent_counterexample"][
                        "mu_to_e_a"
                    ]["branching_ratio"],
                    "K_to_pi_a": report["generation_dependent_counterexample"][
                        "K_to_pi_a"
                    ]["branching_ratio"],
                },
                "flag": report["flag"],
            },
            indent=2,
        )
    )
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
