#!/usr/bin/env python3
"""Fail-closed V39 six-field secluded-freeze-out cosmology screen.

The stable D16/Db16 Dirac fermion is screened with a total-D-plus-Dbar
Maxwell--Boltzmann Boltzmann equation and an illustrative DDbar -> XX proxy.
All TeV masses, soft terms, X-multiplet data, amplitudes, and reheating data
are imposed EFT inputs.  The screen must not be promoted: the corrected
coupling has a one-loop Landau pole far below fPQ absent new threshold dynamics,
and the component X/soft/vacuum construction is not available.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq
from scipy.special import kn

import susy_v39_g5_freezein_cosmology as fi


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V39_G5_SECLUDED_FREEZEOUT_CERTIFICATE.json"
MD_PATH = ROOT / "SUSY_V39_G5_SECLUDED_FREEZEOUT.md"
MPL_GEV = 1.22089e19
S0_CM3 = 2891.2
RHOCRIT_OVER_H2_GEV_CM3 = 1.05375e-5
HBAR_GEV_S = 6.582119569e-25
GEV2_TO_CM3_S = 1.167e-17

BENCHMARK = {
    "fPQ_GeV": 5.0e11,
    "Treh_GeV": 1.0e7,
    "Tmax_GeV": 1.0e7,
    "mD16_GeV": 2.0e3,
    "mA16_GeV": 3.5e3,
    "mX_GeV": 1.0e3,
    "mD16_scalar_soft_GeV": 3.0e3,
    "lambda_X_visible": 3.0e-6,
    "g_chi_dirac": 4.0,
    "mA_heavy_GeV": 1.0e9,
    "mD_heavy_GeV": 9.0e8,
    "kappa_heavy": 1.0e-6,
    "Mred_GeV": 2.4e18,
    "Omega_c_h2": 0.120,
    "axion_fraction_of_DM": 0.01,
    "theta_i": 0.05,
    "H_inflation_GeV": 1.0e6,
    "gstar": 106.75,
}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def canonical_sha(value: dict[str, Any]) -> str:
    body = copy.deepcopy(value)
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def Hubble_radiation(temperature: float, gstar: float) -> float:
    return 1.66 * math.sqrt(gstar) * temperature * temperature / MPL_GEV


def equilibrium_yield(x: float, g_chi: float, gstar: float) -> float:
    return 45.0 * g_chi * x * x * float(kn(2, x)) / (4.0 * math.pi**4 * gstar)


def target_yield(omega_h2: float, mass_gev: float) -> float:
    return omega_h2 * RHOCRIT_OVER_H2_GEV_CM3 / (mass_gev * S0_CM3)


def omega_h2_from_yield(yield_value: float, mass_gev: float) -> float:
    return yield_value * mass_gev * S0_CM3 / RHOCRIT_OVER_H2_GEV_CM3


def annihilation_proxy(lambda_dark: float, mass_d: float, mass_a: float, mass_x: float) -> float:
    """s-wave D Dbar -> X X proxy through A16; full SUSY matching is open."""

    if mass_x >= mass_d:
        return 0.0
    denominator = (mass_a * mass_a + mass_d * mass_d - mass_x * mass_x) ** 2
    return lambda_dark**4 * mass_d**2 * math.sqrt(1.0 - (mass_x / mass_d) ** 2) / (8.0 * math.pi * denominator)


def solve_freezeout(mass_d: float, sigma_v_gev2: float, g_chi: float, gstar: float) -> dict[str, Any]:
    """Solve the total-D-plus-Dbar yield equation in radiation domination.

    g_chi=4 counts both Dirac particle and antiparticle spin states.  Thus a
    DDbar annihilation removes two particles while n_D=n_Dbar=n_total/2, and
    the total-yield RHS carries the explicit factor one half.
    """

    coefficient = 0.264 * gstar / math.sqrt(gstar) * MPL_GEV * mass_d * sigma_v_gev2

    def rhs(x: float, y: np.ndarray) -> np.ndarray:
        yeq = equilibrium_yield(x, g_chi, gstar)
        return np.array([-0.5 * coefficient * (y[0] * y[0] - yeq * yeq) / (x * x)])

    grid = np.geomspace(1.0, 1.0e5, 1200)
    solution = solve_ivp(
        rhs,
        (1.0, 1.0e5),
        [equilibrium_yield(1.0, g_chi, gstar)],
        method="BDF",
        t_eval=grid,
        rtol=2.0e-8,
        atol=1.0e-30,
    )
    ratios = []
    for x, y in zip(solution.t, solution.y[0]):
        yeq = equilibrium_yield(float(x), g_chi, gstar)
        ratios.append(y / yeq if yeq else math.inf)
    indices = np.flatnonzero(np.asarray(ratios) >= 1.5)
    return {
        "yield_final": float(solution.y[0, -1]),
        "Omega_h2": omega_h2_from_yield(float(solution.y[0, -1]), mass_d),
        "x_freezeout_proxy_Y_over_Yeq_1p5": float(solution.t[indices[0]]) if len(indices) else None,
        "nfev": int(solution.nfev),
        "njev": int(solution.njev),
        "coefficient": coefficient,
        "total_D_plus_Dbar_annihilation_factor": 0.5,
    }


def unvalidated_two_body_width_proxy(coupling: float, parent: float, daughter: float, visible: float) -> float:
    """Toy phase-space width only; not a component-resolved SUSY prediction."""
    if daughter + visible >= parent:
        return 0.0
    phase = (1.0 - ((daughter + visible) / parent) ** 2) ** 2
    return coupling * coupling * parent * phase / (16.0 * math.pi)


def direct_detection_dim5_illustration(
    lambda_dark: float, lambda_visible: float, mass_x: float, mass_d: float
) -> float:
    """Dimensionally consistent dim-five-contact illustration, not a prediction.

    Assuming C chi-chi H^dagger H with C=lambda_dark*lambda_visible/mX,
    h_chichi=C v and the Higgs-nucleon vertex f_N m_N/v are used explicitly.
    The previous expression omitted this 1/v factor.  This contact is neither
    derived from the X/A component theory nor matched to nucleons, so the
    returned number must never serve as a direct-detection viability test.
    """

    vev = 246.0
    m_nucleon = 0.939
    f_nucleon = 0.30
    m_higgs = 125.0
    contact = lambda_dark * lambda_visible / mass_x
    h_chichi = contact * vev
    h_nucleon = f_nucleon * m_nucleon / vev
    reduced_mass = mass_d * m_nucleon / (mass_d + m_nucleon)
    amplitude = h_chichi * h_nucleon / (m_higgs * m_higgs)
    return reduced_mass * reduced_mass / math.pi * amplitude * amplitude * 0.389379e-27


def one_loop_landau_pole(lambda_dark: float, reference_scale_gev: float) -> dict[str, float]:
    """Integrate beta_lambda=3 lambda^3/(16 pi^2), with no threshold rescue."""

    beta_prefactor = 3.0 / (16.0 * math.pi * math.pi)
    log_pole_over_reference = 1.0 / (2.0 * beta_prefactor * lambda_dark * lambda_dark)
    return {
        "beta_prefactor": beta_prefactor,
        "log_pole_over_reference": log_pole_over_reference,
        "pole_GeV": reference_scale_gev * math.exp(log_pole_over_reference),
    }


def standard_misalignment_reference(f_pq_gev: float, theta_i: float, omega_c_h2: float) -> dict[str, float | str]:
    """Expose, but do not solve, the small-angle pre-inflation misalignment fit.

    The explicit normalization is a convention-dependent review reference.  It
    gives the requested 0.126 percent DM at the stated point, illustrating why
    the separately imposed one-percent axion fraction is not a joint solution.
    """

    exponent = 1.165
    normalization = 0.06048
    omega = normalization * theta_i * theta_i * (f_pq_gev / 5.0e11) ** exponent
    return {
        "formula": "Omega_a h^2 = 0.06048 theta_i^2 (f_a/(5e11 GeV))^1.165 (small-angle reference normalization)",
        "reference_normalization": normalization,
        "exponent": exponent,
        "Omega_a_h2": omega,
        "fraction_of_DM": omega / omega_c_h2,
    }


def solve_benchmark() -> dict[str, Any]:
    p = BENCHMARK
    omega_d = p["Omega_c_h2"] * (1.0 - p["axion_fraction_of_DM"])
    y_target = target_yield(omega_d, p["mD16_GeV"])

    def residual(lambda_dark: float) -> float:
        sigma = annihilation_proxy(lambda_dark, p["mD16_GeV"], p["mA16_GeV"], p["mX_GeV"])
        return solve_freezeout(p["mD16_GeV"], sigma, p["g_chi_dirac"], p["gstar"])["yield_final"] - y_target

    lambda_dark = brentq(residual, 0.2, 2.0, xtol=1.0e-10, rtol=1.0e-10)
    sigma_v = annihilation_proxy(lambda_dark, p["mD16_GeV"], p["mA16_GeV"], p["mX_GeV"])
    freezeout = solve_freezeout(p["mD16_GeV"], sigma_v, p["g_chi_dirac"], p["gstar"])
    gamma_a16 = unvalidated_two_body_width_proxy(
        lambda_dark, p["mA16_GeV"], p["mD16_GeV"], p["mX_GeV"]
    )
    gamma_x = p["lambda_X_visible"] ** 2 * p["mX_GeV"] / (8.0 * math.pi)
    rate_x = gamma_x / Hubble_radiation(p["mX_GeV"], p["gstar"])
    entropy_at_mD = 2.0 * math.pi**2 * p["gstar"] * p["mD16_GeV"] ** 3 / 45.0
    yD_eq_total = equilibrium_yield(1.0, p["g_chi_dirac"], p["gstar"])
    nD_eq_total = yD_eq_total * entropy_at_mD
    # The physical per-D relaxation rate uses n_Dbar=n_total/2.  The second
    # quantity retains one more factor 1/2 as a deliberately conservative
    # convention screen; both are enormous if the proxy amplitude is physical.
    rate_d_tagged = (0.5 * nD_eq_total * sigma_v) / Hubble_radiation(p["mD16_GeV"], p["gstar"])
    rate_d_conservative = 0.5 * rate_d_tagged
    epsilon = p["fPQ_GeV"] / (math.sqrt(2.0) * p["Mred_GeV"])
    gamma_heavy = unvalidated_two_body_width_proxy(
        p["kappa_heavy"] * epsilon, p["mA_heavy_GeV"], p["mD_heavy_GeV"], p["mX_GeV"]
    )
    tau_heavy = HBAR_GEV_S / gamma_heavy
    sigma_cm3s = sigma_v * GEV2_TO_CM3_S
    p_ann = (1.0 - p["axion_fraction_of_DM"]) ** 2 * sigma_cm3s / p["mD16_GeV"]
    sigma_si = direct_detection_dim5_illustration(
        lambda_dark, p["lambda_X_visible"], p["mX_GeV"], p["mD16_GeV"]
    )
    x_freeze = float(freezeout["x_freezeout_proxy_Y_over_Yeq_1p5"] or 25.0)
    vrel_freeze = math.sqrt(6.0 / x_freeze)
    sigma_v_swave_unitarity = 4.0 * math.pi / (p["mD16_GeV"] ** 2 * vrel_freeze)
    landau = one_loop_landau_pole(lambda_dark, p["mD16_GeV"])
    x_operator_selection = {
        "linear_X": fi.term_audit(("X",)),
        "quadratic_X2": fi.term_audit(("X", "X")),
        "cubic_X3": fi.term_audit(("X", "X", "X")),
    }
    misalignment = standard_misalignment_reference(
        p["fPQ_GeV"], p["theta_i"], p["Omega_c_h2"]
    )
    beta_limit = 0.038
    scalar_amplitude = 2.1e-9
    P_iso = (p["axion_fraction_of_DM"] * p["H_inflation_GeV"] / (math.pi * p["fPQ_GeV"] * p["theta_i"])) ** 2
    beta_iso = P_iso / (P_iso + scalar_amplitude)
    H_iso_max = math.pi * p["fPQ_GeV"] * p["theta_i"] / p["axion_fraction_of_DM"] * math.sqrt(beta_limit / (1.0 - beta_limit) * scalar_amplitude)
    P_iso_misalignment = (
        float(misalignment["fraction_of_DM"]) * p["H_inflation_GeV"] /
        (math.pi * p["fPQ_GeV"] * p["theta_i"])
    ) ** 2
    beta_iso_misalignment = P_iso_misalignment / (P_iso_misalignment + scalar_amplitude)
    return {
        "parameterization": {
            **p,
            "Omega_D16_h2_target": omega_d,
            "target_yield": y_target,
            "lambda_dark_solved": lambda_dark,
            "yA16_from_mass": math.sqrt(2.0) * p["mA16_GeV"] / p["fPQ_GeV"],
            "scalar_soft_input_status": (
                "ILLUSTRATIVE_ONLY: no soft/vacuum mass matrix or coannihilation "
                "calculation turns this input into a scalar-mass eigenvalue."
            ),
        },
        "thermalization_and_decay": {
            "D_Dbar_to_XX_proxy_rate_over_H_at_T_equal_mD": rate_d_tagged,
            "D_Dbar_to_XX_proxy_rate_over_H_conservative_extra_half": rate_d_conservative,
            "D_equilibrium_total_density_GeV3_at_T_equal_mD": nD_eq_total,
            "D_equilibrium_yield_total_at_x_one": yD_eq_total,
            "Dirac_pair_density_factor": 0.5,
            "proxy_rate_is_large_if_component_amplitude_is_real": rate_d_conservative > 10.0,
            "thermalization_status": (
                "CONDITIONAL: the DDbar->XX component amplitude, X multiplet spectrum, "
                "and visible equilibration are not calculated."
            ),
            "A16_unvalidated_width_proxy_GeV": gamma_a16,
            "A16_unvalidated_lifetime_proxy_seconds": HBAR_GEV_S / gamma_a16,
            "X_visible_unvalidated_width_proxy_GeV": gamma_x,
            "X_visible_unvalidated_lifetime_proxy_seconds": HBAR_GEV_S / gamma_x,
            "X_visible_width_proxy_rate_over_H_at_mX": rate_x,
            "widths_are_component_unvalidated": True,
        },
        "X_multiplet_structural_blocker": {
            "selection_audits": x_operator_selection,
            "linear_X_allowed": bool(x_operator_selection["linear_X"]["exactly_invariant"]),
            "cubic_X3_allowed": bool(x_operator_selection["cubic_X3"]["exactly_invariant"]),
            "quadratic_X2_forbidden_by_Z4R": not bool(x_operator_selection["quadratic_X2"]["exactly_invariant"]),
            "status": "BLOCKER",
            "reason": (
                "A single imposed mX and width do not define the X scalar/fermion mass matrix. "
                "If psi_X obtains mass through <X>, lambda_X <X> H H simultaneously changes "
                "visible-sector Higgs mixing; a solved F+D+soft vacuum is required."
            ),
        },
        "freezeout_boltzmann_solution": {
            "equation": "dY_total/dx = -0.5*[0.264*(g_s/sqrt(g_rho))*M_Pl*m_D*<sigma v>/x^2]*(Y_total^2-Yeq_total^2)",
            "statistics": (
                "Maxwell-Boltzmann, total stable Dirac D+Dbar g=4; scalar spectrum, "
                "mass matrix, and coannihilations are uncomputed."
            ),
            "component_amplitude_status": "UNCOMPUTED: DDbar->XX is an illustrative EFT proxy.",
            "sigma_v_proxy_GeV_minus2": sigma_v,
            "sigma_v_proxy_cm3_per_s": sigma_cm3s,
            **freezeout,
            "relative_abundance_error": abs(freezeout["Omega_h2"] - omega_d) / omega_d,
        },
        "heavy_blocks": {
            "mA_heavy_over_Tmax": p["mA_heavy_GeV"] / p["Tmax_GeV"],
            "mD_heavy_over_Tmax": p["mD_heavy_GeV"] / p["Tmax_GeV"],
            "Boltzmann_tail_proxy_exp_minus_m_over_T": math.exp(-p["mA_heavy_GeV"] / p["Tmax_GeV"]),
            "P_over_M_unvalidated_width_proxy_GeV": gamma_heavy,
            "P_over_M_unvalidated_lifetime_proxy_seconds": tau_heavy,
            "proxy_decays_before_0p1_second": tau_heavy < 0.1,
            "component_width_status": "UNVALIDATED: no Kallen/spin/multiplicity/component calculation.",
        },
        "constraints": {
            "BBN": {
                "conservative_lifetime_seconds": 0.1,
                "longest_displayed_lifetime_seconds": max(tau_heavy, HBAR_GEV_S / gamma_a16, HBAR_GEV_S / gamma_x),
                "unvalidated_width_proxy_is_before_screen": max(tau_heavy, HBAR_GEV_S / gamma_a16, HBAR_GEV_S / gamma_x) < 0.1,
                "validated_pass": False,
                "status": "UNVALIDATED_COMPONENT_WIDTHS",
            },
            "CMB_annihilation": {
                "p_ann_worstcase_feff_one_cm3_per_s_per_GeV": p_ann,
                "Planck_2018_limit": 3.2e-28,
                "passes_if_swave_proxy_and_visible_deposition": p_ann < 3.2e-28,
                "validated_pass": False,
                "status": "CONDITIONAL_ON_COMPONENT_AMPLITUDE_AND_X_DECAYS",
            },
            "thermal_unitarity": {
                "Griest_Kamionkowski_reference_mass_GeV": 3.4e5,
                "mD16_GeV": p["mD16_GeV"],
                "reference_mass_passes": p["mD16_GeV"] < 3.4e5,
                "freezeout_vrel_proxy": vrel_freeze,
                "s_wave_sigma_v_unitarity_GeV_minus2": sigma_v_swave_unitarity,
                "sigma_v_over_s_wave_unitarity": sigma_v / sigma_v_swave_unitarity,
                "coupling_loop_factor_lambda_squared_over_4pi": lambda_dark**2 / (4.0 * math.pi),
                "passes": (
                    p["mD16_GeV"] < 3.4e5
                    and sigma_v < sigma_v_swave_unitarity
                    and lambda_dark**2 / (4.0 * math.pi) < 1.0
                ),
            },
            "direct_detection": {
                "dim5_illustrative_sigma_SI_cm2": sigma_si,
                "matching": "C=lambda_D lambda_X/mX, h_chichi=C v, h_NN=f_N m_N/v; the required 1/v is explicit.",
                "status": "NON_CONSTRAINING_ILLUSTRATION",
                "not_used_for_viability": True,
                "XENONnT_2025_global_minimum_cm2_at_30_GeV": 1.7e-47,
                "illustrative_value_below_global_minimum": sigma_si < 1.7e-47,
                "reason": (
                    "The 30-GeV global minimum is not the 2-TeV likelihood, and the dim-five "
                    "contact/X-A component matching is not derived."
                ),
            },
            "axion_isocurvature_and_PQ": {
                "assumption": "PQ broken before inflation and no thermal/nonthermal restoration are imposed, not derived.",
                "imposed_axion_fraction_of_DM": p["axion_fraction_of_DM"],
                "imposed_fraction_beta_iso": beta_iso,
                "Planck_beta_iso_limit": beta_limit,
                "H_inflation_GeV": p["H_inflation_GeV"],
                "H_inflation_max_GeV_if_one_percent_fraction_is_imposed": H_iso_max,
                "isocurvature_screen_passes_if_one_percent_fraction_is_imposed": beta_iso < beta_limit,
                "standard_misalignment_reference": misalignment,
                "misalignment_fraction_beta_iso": beta_iso_misalignment,
                "misalignment_fraction_vs_imposed_ratio": float(misalignment["fraction_of_DM"]) / p["axion_fraction_of_DM"],
                "joint_abundance_and_isocurvature_solution": False,
                "Tmax_over_fPQ": p["Tmax_GeV"] / p["fPQ_GeV"],
                "PQ_restoration": "CONDITIONAL: Tmax/fPQ is small, but the finite-temperature PQ potential is not derived.",
            },
            "one_loop_lambda_running": {
                "equation": "d lambda_D/d ln(mu) = 3 lambda_D^3/(16 pi^2)",
                "reference_scale_GeV": p["mD16_GeV"],
                **landau,
                "fPQ_GeV": p["fPQ_GeV"],
                "pole_below_fPQ": landau["pole_GeV"] < p["fPQ_GeV"],
                "perturbative_to_fPQ_without_new_threshold_or_dynamics": False,
                "status": "HARD_UV_BLOCKER",
            },
        },
    }


def report() -> dict[str, Any]:
    exact = fi.exact_selector_report()
    benchmark = solve_benchmark()
    constraints = benchmark["constraints"]
    data: dict[str, Any] = {
        "schema": "susy-v39-g5-secluded-freezeout-certificate-v2-corrected-fail-closed",
        "scope": (
            "Corrected V39 six-field D-cascade freeze-out screen.  It reproduces an imposed low-energy "
            "target under illustrative proxies, but is UV-blocked and cannot be a G5 candidate or promotion."
        ),
        "exact_symmetry_and_quality": exact,
        "benchmark": benchmark,
        "sources": [
            {"topic": "freeze-out/freeze-in framework", "url": "https://arxiv.org/abs/0911.1120"},
            {"topic": "thermal-relic unitarity", "url": "https://ntrs.nasa.gov/citations/19900004848"},
            {"topic": "Planck abundance and p_ann", "url": "https://arxiv.org/abs/1807.06209"},
            {"topic": "Planck inflation/isocurvature", "url": "https://arxiv.org/abs/1807.06211"},
            {"topic": "BBN late-decay screening", "url": "https://arxiv.org/abs/astro-ph/0408426"},
            {"topic": "XENONnT SI result", "url": "https://arxiv.org/abs/2502.18005"},
            {"topic": "QCD axion susceptibility/misalignment input", "url": "https://arxiv.org/abs/1606.07494"},
        ],
        "promotion": {
            "G5_closed": False,
            "G5_status": "OPEN__HARD_UV_BLOCKER_AND_UNDERIVED_COSMOLOGY",
            "candidate_passes_its_quantitative_proxies": False,
            "conditional_low_energy_screens": {
                "Boltzmann_solution_matches_imposed_D_target": benchmark["freezeout_boltzmann_solution"]["relative_abundance_error"] < 1.0e-8,
                "DDbar_rate_large_if_proxy_amplitude_is_physical": benchmark["thermalization_and_decay"]["proxy_rate_is_large_if_component_amplitude_is_real"],
                "BBN_width_screen_is_early_if_proxy_is_correct": constraints["BBN"]["unvalidated_width_proxy_is_before_screen"],
                "CMB_screen_passes_if_swave_proxy_is_correct": constraints["CMB_annihilation"]["passes_if_swave_proxy_and_visible_deposition"],
                "low_energy_partial_wave_screen_passes": constraints["thermal_unitarity"]["passes"],
            },
            "hard_fail_closed_blockers": [
                "The stated one-loop beta_lambda=3 lambda^3/(16 pi^2) reaches a Landau pole below fPQ absent a new threshold/dynamics.",
                "X has allowed linear and cubic superpotential terms while X^2 is R-forbidden; an imposed single mX/width cannot represent its component mass matrix or visible mixing.",
                "DDbar->XX, widths, X-visible equilibration, and direct detection lack a component-resolved calculation.",
                "The 1 percent axion fraction is imposed but the stated standard-misalignment reference gives about 0.126 percent, so abundance and isocurvature are not jointly solved.",
            ],
            "not_predictive_because": [
                "The light X and all component masses are imposed, not derived from a V37 Kähler/soft vacuum or X component mass matrix.",
                "The XX annihilation, widths, visible equilibration, and direct-detection formulas are illustrative EFT proxies, not component or nuclear matching calculations.",
                "The reheaton sector, Tmax, and direct dark branching are imposed rather than derived.",
                "PQ restoration, preheating, axion abundance, domain walls, the global soft vacuum, and a joint isocurvature history remain uncomputed.",
                "Z170 leaves D16/Db16 stable by construction; this point makes the relic acceptable but cannot remove it.",
            ],
            "next_required_calculations": [
                "supply new threshold/dynamics below the lambda_D Landau pole and run the complete coupled RGEs to fPQ",
                "derive the TeV X/A16/D scalar and fermion spectrum, X vev, and visible Higgs mixing from a stabilized UV/Kähler/soft sector",
                "derive full SUSY component annihilation amplitudes and solve coupled Bose/Fermi thermal Boltzmann equations",
                "match the X/A-mediated direct-detection amplitude to nucleons and use the mass-dependent likelihood",
                "construct an inflaton/reheaton model and calculate Tmax, branching fractions, and nonthermal D production",
                "compute the PQ finite-temperature potential and axion/isocurvature/defect history jointly with freeze-out",
            ],
        },
    }
    data["core_sha256"] = canonical_sha(data)
    return data


def markdown(data: dict[str, Any]) -> str:
    b = data["benchmark"]
    freeze = b["freezeout_boltzmann_solution"]
    checks = b["constraints"]
    exact = data["exact_symmetry_and_quality"]
    lines = [
        "# SUSY V39 G5 corrected secluded freeze-out screen",
        "",
        "## Result",
        "",
        "This corrected calculation is a fail-closed screen, not a viable G5 candidate.",
        "For an imposed 2-TeV D16/Db16 Dirac spectrum and an illustrative DDbar -> XX amplitude,",
        f"the total-yield Boltzmann equation gives Omega_D h^2={freeze['Omega_h2']:.6f} at lambda_dark={b['parameterization']['lambda_dark_solved']:.6f}.",
        (
            "Inputs: fPQ=5e11 GeV, Treh=Tmax=1e7 GeV, mD=2 TeV, mA16=3.5 TeV, "
            "mX=1 TeV, an unused illustrative D-scalar soft input=3 TeV, and lambda_XH=3e-6."
        ),
        "",
        "## Exact EFT checks",
        "",
        f"The six-field cascade preserves selector invariance, finite Z5610 anomaly tests, W degree {exact['all_chiral_quality']['first_W_breaking_degree']}, and Kahler degree {exact['all_chiral_quality']['first_Kahler_breaking_degree']}.",
        "",
        "## Conditional low-energy screens",
        "",
        f"- x_f={freeze['x_freezeout_proxy_Y_over_Yeq_1p5']:.2f}; <sigma v>={freeze['sigma_v_proxy_cm3_per_s']:.3e} cm^3/s.",
        f"- DDbar rate/H conditional proxy: {b['thermalization_and_decay']['D_Dbar_to_XX_proxy_rate_over_H_conservative_extra_half']:.3e}; it does not establish thermalization without the component amplitude.",
        f"- Longest unvalidated width-proxy lifetime: {checks['BBN']['longest_displayed_lifetime_seconds']:.3e} s.",
        f"- Conditional worst-case CMB p_ann: {checks['CMB_annihilation']['p_ann_worstcase_feff_one_cm3_per_s_per_GeV']:.3e} versus {checks['CMB_annihilation']['Planck_2018_limit']:.1e}.",
        f"- s-wave unitarity ratio: {checks['thermal_unitarity']['sigma_v_over_s_wave_unitarity']:.3e}; coupling loop factor: {checks['thermal_unitarity']['coupling_loop_factor_lambda_squared_over_4pi']:.3f}.",
        f"- Dimensionally consistent but non-constraining dim-five DD illustration: {checks['direct_detection']['dim5_illustrative_sigma_SI_cm2']:.3e} cm^2.",
        f"- Imposed-1%-fraction isocurvature beta: {checks['axion_isocurvature_and_PQ']['imposed_fraction_beta_iso']:.3e}; the independent misalignment reference gives {checks['axion_isocurvature_and_PQ']['standard_misalignment_reference']['fraction_of_DM']:.3%} of DM, not 1%.",
        f"- One-loop lambda_D Landau pole: {checks['one_loop_lambda_running']['pole_GeV']:.3e} GeV, below fPQ=5e11 GeV.",
        "",
        "## Strict boundary",
        "",
        "The corrected point fails closed. Its large lambda_D reaches a one-loop Landau pole below fPQ without a new threshold/dynamics. In addition, allowed W linear/X^3 terms and R-forbidden X^2 mean that a single imposed X mass/width cannot replace a solved X/visible mass matrix: an X vev would also induce lambda_X<X>HH mixing. Widths, thermalization, direct detection, reheating, PQ restoration, and the joint axion abundance/isocurvature history are all uncomputed component-level inputs.",
        "",
        "Sources: [freeze-in/out](https://arxiv.org/abs/0911.1120), [Planck cosmology](https://arxiv.org/abs/1807.06209), [Planck inflation](https://arxiv.org/abs/1807.06211), [BBN](https://arxiv.org/abs/astro-ph/0408426), [unitarity](https://ntrs.nasa.gov/citations/19900004848), [XENONnT](https://arxiv.org/abs/2502.18005), and [QCD axion susceptibility](https://arxiv.org/abs/1606.07494).",
        "",
        f"Core SHA-256: `{data['core_sha256']}`",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write and args.check:
        raise SystemExit("choose at most one of --write and --check")
    data = report()
    if args.write:
        JSON_PATH.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        MD_PATH.write_text(markdown(data), encoding="utf-8")
    if args.check:
        if not JSON_PATH.is_file() or not MD_PATH.is_file():
            raise SystemExit("generated V39 secluded-freezeout certificate is missing; run with --write")
        if canonical_bytes(json.loads(JSON_PATH.read_text(encoding="utf-8"))) != canonical_bytes(data):
            raise SystemExit("generated V39 secluded-freezeout JSON is stale; run with --write")
        if MD_PATH.read_text(encoding="utf-8") != markdown(data):
            raise SystemExit("generated V39 secluded-freezeout Markdown is stale; run with --write")
        print("SUSY V39 secluded-freezeout audit: PASS")
        return
    print(json.dumps(data, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
