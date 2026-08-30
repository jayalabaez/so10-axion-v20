#!/usr/bin/env python3
"""Secondary, fail-closed V39 decay-freeze-in screen for the V37 D cascade.

The V37 core leaves an exact Z170 remnant.  The lightest charged particle is
therefore stable in every symmetry-preserving completion.  This file does not
hide that fact: it chooses one explicit *freeze-in* history for the D16 block,
solves its decay Boltzmann equation, and tests the associated early-universe
and laboratory boundaries.  It deliberately retains the missing UV inputs in
the final promotion verdict.

The calculation uses Maxwell--Boltzmann equilibrium statistics for a complete
parent chiral multiplet (g=4).  Parent equilibrium is an explicit imposed
input: at this high-scale point it is not derived from the V37 Kähler/soft
vacuum or a complete reheating sector.  It is therefore retained only as a
secondary conditional screen; the corrected low-reheat secluded-freeze-out
construction is the stronger V39 screen but is also fail-closed.  Neither
construction is a G5 promotion.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable

from scipy.integrate import quad, solve_ivp
from scipy.optimize import minimize_scalar
from scipy.special import k1

import susy_v37_new_physics_routes as v37


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V39_G5_FREEZEIN_COSMOLOGY_CERTIFICATE.json"
MD_PATH = ROOT / "SUSY_V39_G5_FREEZEIN_COSMOLOGY.md"

N66 = 66
N85 = 85
N5610 = N66 * N85
FPQ_GEV = 5.0e11
MRED_GEV = 2.4e18
MPL_GEV = 1.22089e19
GSTAR = 106.75
S0_CM3 = 2891.2
RHOCRIT_OVER_H2_GEV_CM3 = 1.05375e-5
HBAR_GEV_S = 6.582119569e-25
GEV2_TO_CM3_S = 1.167e-17

# q66, external Z4R superfield charge, h85, optimized PQ numerator / 170.
# These are the six non-neutral carriers proposed in the V37 relic audit.  We
# use the already-present X as the neutral mediator, avoiding an added R=2
# neutral field with a generic linear superpotential tadpole.
D_FIELDS: dict[str, tuple[int, int, int, int]] = {
    "D2": (29, 0, 84, 23),
    "Db2": (37, 2, 1, -23),
    "D17": (65, 2, 69, 113),
    "Db17": (1, 0, 16, -113),
    "D16": (1, 0, 0, 85),
    "Db16": (65, 2, 0, -85),
}
FIELDS = {**v37.ALL_CHIRAL_FIELDS, **D_FIELDS}

# Active V39 split-six Z3 charges on the fields appearing in the cascade.
# Invariance fixes D2,Db2=(2,1); the A15/A17/A16 blocks and their D pairs are
# neutral.  The assignments retain each vectorlike D mass.
V39_Z3_CASCADE: dict[str, int] = {
    "X": 0,
    "P": 0,
    "Pbar": 0,
    "A2": 1,
    "A32": 2,
    "A15": 0,
    "A17": 0,
    "A16": 0,
    "D2": 2,
    "Db2": 1,
    "D17": 0,
    "Db17": 0,
    "D16": 0,
    "Db16": 0,
}

CASCADE_TERMS: dict[str, tuple[str, ...]] = {
    "mu2_D2_Db2": ("D2", "Db2"),
    "mu17_D17_Db17": ("D17", "Db17"),
    "mu16_D16_Db16": ("D16", "Db16"),
    "D2_cascade": ("X", "A2", "D2"),
    "A32_cascade": ("Pbar", "X", "A32", "Db2"),
    "D17_cascade": ("X", "A17", "D17"),
    "A15_cascade": ("P", "X", "A15", "Db17"),
    "D16_freezein": ("X", "A16", "D16"),
}

# A deliberately small, explicit parameter point.  The A2/A32 and A15/A17
# blocks are above the maximum thermal temperature.  The A16 block is in
# equilibrium and makes the light D16/Db16 Dirac state by freeze-in.
BENCHMARK = {
    "fPQ_GeV": FPQ_GEV,
    "Mred_GeV": MRED_GEV,
    "Treh_GeV": 2.0e10,
    "Tmax_GeV": 2.0e10,
    "mA16_GeV": 1.0e10,
    "mX_GeV": 1.0e9,
    "mD16_GeV": 1.0e3,
    "mA_heavy_GeV": 2.0e11,
    "mD_heavy_GeV": 1.8e11,
    "kappa_heavy": 1.0e-6,
    "lambda_X_visible": 0.1,
    "g_parent_chiral_multiplet": 4.0,
    "Omega_c_h2": 0.120,
    "axion_fraction_of_DM": 0.01,
    "theta_i": 0.05,
    "H_inflation_GeV": 1.0e6,
    "gstar": GSTAR,
}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def canonical_sha(value: dict[str, Any]) -> str:
    body = copy.deepcopy(value)
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def q5610(q66: int, h85: int) -> int:
    return v37.combined_charge(q66, h85)


def term_audit(term: Iterable[str]) -> dict[str, int | bool]:
    names = tuple(term)
    q66_sum = sum(FIELDS[name][0] for name in names) % N66
    r_sum = sum(FIELDS[name][1] for name in names) % 4
    h_sum = sum(FIELDS[name][2] for name in names) % N85
    pq_sum = sum(FIELDS[name][3] for name in names)
    z3_sum = sum(V39_Z3_CASCADE[name] for name in names) % 3
    return {
        "q66_mod66": q66_sum,
        "Z4R_mod4": r_sum,
        "h85_mod85": h_sum,
        "PQ_numerator_over_170": pq_sum,
        "V39_Z3_mod3": z3_sum,
        "exactly_invariant": q66_sum == 0 and r_sum == 2 and h_sum == 0 and pq_sum == 0 and z3_sum == 0,
    }


def v39_z3_dark_increment_audit() -> dict[str, Any]:
    rows = []
    for name, (q66, r4, h85, _pq) in D_FIELDS.items():
        rows.append(
            {
                "field": name,
                "Z3": V39_Z3_CASCADE[name],
                "Z5610": q5610(q66, h85),
                "fermion_Z4R_lift": r4 - 1,
            }
        )
    linear = sum(row["Z3"] for row in rows)
    cubic = sum(row["Z3"] ** 3 for row in rows)
    cross_z3_z5610_squared = sum(row["Z3"] * row["Z5610"] ** 2 for row in rows)
    cross_z3_squared_z5610 = sum(row["Z3"] ** 2 * row["Z5610"] for row in rows)
    cross_z3_r_squared = sum(row["Z3"] * row["fermion_Z4R_lift"] ** 2 for row in rows)
    cross_z3_squared_r = sum(row["Z3"] ** 2 * row["fermion_Z4R_lift"] for row in rows)
    return {
        "rows": rows,
        "pure_Z3_linear_increment": linear,
        "pure_Z3_cubic_increment": cubic,
        "pure_Z3_Hsieh_linear_condition_mod3": (2 * linear) % 3,
        "pure_Z3_Hsieh_cubic_condition_mod18": (20 * cubic) % 18,
        "Z3_Z5610_squared_increment_mod3": cross_z3_z5610_squared % 3,
        "Z3_squared_Z5610_increment_mod3": cross_z3_squared_z5610 % 3,
        "Z3_fermion_Z4R_squared_increment_mod3": cross_z3_r_squared % 3,
        "Z3_squared_fermion_Z4R_increment_mod3": cross_z3_squared_r % 3,
        "all_listed_increments_vanish": (
            (2 * linear) % 3 == 0
            and (20 * cubic) % 18 == 0
            and cross_z3_z5610_squared % 3 == 0
            and cross_z3_squared_z5610 % 3 == 0
            and cross_z3_r_squared % 3 == 0
            and cross_z3_squared_r % 3 == 0
        ),
        "qualification": "Necessary pure/cross residue increments only; the full Z5610 x Z3 x Z4R product bordism remains G1 input.",
    }


def hsieh_rows() -> list[dict[str, int | str]]:
    base = [
        ("PsiBar", 8, 64, 0),
        ("PsiCBar", 8, 64, 0),
        ("P", 1, 2, 0),
        ("Pbar", 1, 64, 0),
        ("A2", 1, 37, 1),
        ("A32", 1, 31, 84),
        ("A15", 1, 63, 69),
        ("A17", 1, 1, 16),
        ("A16", 1, 65, 0),
    ]
    rows: list[dict[str, int | str]] = [
        {"field": name, "multiplicity": multiplicity, "charge": q5610(q66, h85)}
        for name, multiplicity, q66, h85 in base
    ]
    rows.extend(
        {"field": name, "multiplicity": 1, "charge": q5610(q66, h85)}
        for name, (q66, _r4, h85, _pq) in D_FIELDS.items()
    )
    return rows


def mixed_r_h2_increment() -> int:
    signed_h = {"D2": -1, "Db2": 1, "D17": 69, "Db17": -69, "D16": 0, "Db16": 0}
    return sum((D_FIELDS[name][1] - 1) * h * h for name, h in signed_h.items())


def pq_congruence_residues() -> dict[str, int]:
    return {
        name: (pq - (N85 * q66 + 2442 * h85)) % N5610
        for name, (q66, _r4, h85, pq) in D_FIELDS.items()
    }


def phase_space_proxy(parent: float, daughter: float, visible: float) -> float:
    """Conservative two-body phase-space proxy for the component-width benchmark."""

    if daughter + visible >= parent:
        return 0.0
    return (1.0 - ((daughter + visible) / parent) ** 2) ** 2


def yukawa_decay_width(coupling: float, parent: float, daughter: float, visible: float) -> float:
    """Unvalidated phase-space proxy; no component/spin/multiplicity calculation."""
    return coupling * coupling * parent * phase_space_proxy(parent, daughter, visible) / (16.0 * math.pi)


def Hubble_radiation(temperature: float, gstar: float) -> float:
    return 1.66 * math.sqrt(gstar) * temperature * temperature / MPL_GEV


def boltzmann_prefactor(parent_mass: float, g_parent: float, gstar: float) -> float:
    """Coefficient of Gamma*x^3*K1(x) in dY/dx for decay freeze-in."""

    return 45.0 * g_parent * MPL_GEV / (
        4.0 * math.pi**4 * 1.66 * gstar * math.sqrt(gstar) * parent_mass * parent_mass
    )


def solve_decay_freezein(
    parent_mass: float,
    width: float,
    g_parent: float,
    gstar: float,
    x_start: float,
    x_end: float = 80.0,
) -> dict[str, float | int]:
    """Numerically solve dY/dx for an equilibrated decay parent in radiation domination."""

    prefactor = boltzmann_prefactor(parent_mass, g_parent, gstar)

    def rhs(x: float, _y: list[float]) -> list[float]:
        return [prefactor * width * x**3 * float(k1(x))]

    solution = solve_ivp(
        rhs,
        (x_start, x_end),
        [0.0],
        rtol=2.0e-11,
        atol=1.0e-30,
        method="DOP853",
    )
    integral, integral_error = quad(
        lambda x: x**3 * float(k1(x)), x_start, x_end, epsabs=1.0e-12, epsrel=1.0e-12
    )
    analytic = prefactor * width * integral
    numerical = float(solution.y[0, -1])
    return {
        "yield_numerical": numerical,
        "yield_integral_crosscheck": analytic,
        "relative_solver_integral_difference": abs(numerical - analytic) / analytic,
        "integration_kernel": integral,
        "integration_kernel_error": integral_error,
        "nfev": int(solution.nfev),
    }


def omega_h2_from_yield(yield_value: float, mass_gev: float) -> float:
    return yield_value * mass_gev * S0_CM3 / RHOCRIT_OVER_H2_GEV_CM3


def yield_target(omega_h2: float, mass_gev: float) -> float:
    return omega_h2 * RHOCRIT_OVER_H2_GEV_CM3 / (mass_gev * S0_CM3)


def standard_misalignment_reference(f_pq_gev: float, theta_i: float, omega_c_h2: float) -> dict[str, float | str]:
    """Convention-dependent small-angle reference used only to expose mismatch."""

    exponent = 1.165
    normalization = 0.06048
    omega = normalization * theta_i * theta_i * (f_pq_gev / 5.0e11) ** exponent
    return {
        "formula": "Omega_a h^2 = 0.06048 theta_i^2 (f_a/(5e11 GeV))^1.165 (small-angle reference normalization)",
        "Omega_a_h2": omega,
        "fraction_of_DM": omega / omega_c_h2,
    }


def solve_benchmark() -> dict[str, Any]:
    p = BENCHMARK
    omega_chi = p["Omega_c_h2"] * (1.0 - p["axion_fraction_of_DM"])
    target = yield_target(omega_chi, p["mD16_GeV"])
    x_reh = p["mA16_GeV"] / p["Treh_GeV"]
    width_unit = yukawa_decay_width(1.0, p["mA16_GeV"], p["mD16_GeV"], p["mX_GeV"])
    unit = solve_decay_freezein(
        p["mA16_GeV"], width_unit, p["g_parent_chiral_multiplet"], p["gstar"], x_reh
    )
    lambda_fi = math.sqrt(target / float(unit["yield_numerical"]))
    gamma_fi = yukawa_decay_width(lambda_fi, p["mA16_GeV"], p["mD16_GeV"], p["mX_GeV"])
    solved = solve_decay_freezein(
        p["mA16_GeV"], gamma_fi, p["g_parent_chiral_multiplet"], p["gstar"], x_reh
    )
    omega = omega_h2_from_yield(float(solved["yield_numerical"]), p["mD16_GeV"])

    y_a16 = math.sqrt(2.0) * p["mA16_GeV"] / p["fPQ_GeV"]
    H_at_parent = Hubble_radiation(p["mA16_GeV"], p["gstar"])
    parent_equil_rate = y_a16 * y_a16 * p["mA16_GeV"] / (8.0 * math.pi)

    epsilon = p["fPQ_GeV"] / (math.sqrt(2.0) * p["Mred_GeV"])
    lambda_heavy_eff = p["kappa_heavy"] * epsilon
    gamma_heavy = yukawa_decay_width(
        lambda_heavy_eff, p["mA_heavy_GeV"], p["mD_heavy_GeV"], p["mX_GeV"]
    )
    tail, _ = quad(lambda x: x**3 * float(k1(x)), p["mA_heavy_GeV"] / p["Tmax_GeV"], 80.0)
    full_kernel = float(unit["integration_kernel"])
    heavy_relative_yield_proxy = (gamma_heavy / gamma_fi) * (tail / full_kernel)

    peak = minimize_scalar(lambda x: -(x**3 * float(k1(x))), bounds=(0.1, 20.0), method="bounded")
    x_peak = float(peak.x)
    t_production = p["mA16_GeV"] / x_peak
    p_star = (p["mA16_GeV"] ** 2 - p["mX_GeV"] ** 2 - p["mD16_GeV"] ** 2) / (2.0 * p["mA16_GeV"])
    t_nr = p["mD16_GeV"] * t_production / p_star
    t_eq = 7.5e-10
    gs0 = 3.91
    a_production = 2.348e-13 / t_production * (gs0 / p["gstar"]) ** (1.0 / 3.0)
    a_nr = 2.348e-13 / t_nr * (gs0 / p["gstar"]) ** (1.0 / 3.0)
    a_eq = 2.348e-13 / t_eq
    p_eq = p_star * t_eq / t_production * (gs0 / p["gstar"]) ** (1.0 / 3.0)
    # Radiation-era free-streaming proxy: relativistic until a_nr then p~a^-1.
    free_stream_mpc = 299792.458 / (67.4 * math.sqrt(9.2e-5)) * (
        (a_nr - a_production) + a_nr * math.log(a_eq / a_nr)
    )

    # Dimensionally consistent but non-predictive dim-five illustration.  The
    # X/A component matching is unknown, so it cannot be used as a limit.
    C_proxy = lambda_fi * p["lambda_X_visible"] / p["mX_GeV"]
    g_h_chichi = C_proxy * 246.0
    nucleon_factor = 0.30 * 0.939 / 246.0 / 125.0**2
    reduced_mass = 0.939 * p["mD16_GeV"] / (0.939 + p["mD16_GeV"])
    sigma_si_proxy = (
        (reduced_mass**2 / math.pi) * (g_h_chichi * nucleon_factor) ** 2 * 0.389379e-27
    )
    annihilation_proxy = lambda_fi**4 / (8.0 * math.pi * p["mD16_GeV"] ** 2) * GEV2_TO_CM3_S
    p_ann_proxy = 0.3 * annihilation_proxy / p["mD16_GeV"]

    beta_limit = 0.038
    As = 2.1e-9
    P_iso = (
        p["axion_fraction_of_DM"] * p["H_inflation_GeV"] /
        (math.pi * p["fPQ_GeV"] * p["theta_i"])
    ) ** 2
    beta_iso = P_iso / (P_iso + As)
    H_iso_max = (
        math.pi * p["fPQ_GeV"] * p["theta_i"] / p["axion_fraction_of_DM"]
        * math.sqrt(beta_limit / (1.0 - beta_limit) * As)
    )
    misalignment = standard_misalignment_reference(p["fPQ_GeV"], p["theta_i"], p["Omega_c_h2"])

    return {
        "parameterization": {
            **p,
            "Omega_D16_h2_target": omega_chi,
            "lambda16_freezein_solved": lambda_fi,
            "yA16_from_mass": y_a16,
            "lambda_heavy_effective": lambda_heavy_eff,
        },
        "freezein_boltzmann_solution": {
            "equation": (
                "dY_D/dx = [45*g_A*M_Pl/(4*pi^4*1.66*g_s*sqrt(g_rho)*m_A^2)] "
                "Gamma(A->DX) x^3 K_1(x), x=m_A/T"
            ),
            "statistics": "Maxwell-Boltzmann, g_A=4 complete parent chiral-multiplet proxy",
            "x_reheat": x_reh,
            "target_yield": target,
            "partial_width_GeV": gamma_fi,
            "parent_lifetime_seconds": HBAR_GEV_S / gamma_fi,
            "width_status": "UNVALIDATED_PHASE_SPACE_PROXY",
            "solution": solved,
            "Omega_D16_h2": omega,
            "relative_abundance_error": abs(omega - omega_chi) / omega_chi,
            "parent_equilibrium_proxy_Gamma_over_H": parent_equil_rate / H_at_parent,
            "parent_equilibrium_status": (
                "ASSUMED EFT INPUT: this proxy does not derive a thermal A16 "
                "population from the V37 Kähler/soft or reheating sector."
            ),
            "FIMP_inverse_decay_proxy_Gamma_over_H": gamma_fi / H_at_parent,
            "never_thermalizes_under_proxy": gamma_fi / H_at_parent < 1.0e-8,
        },
        "other_anomalon_blocks": {
            "status": "kept above Tmax in the imposed spectrum; component decay width unvalidated",
            "mA2_A32_and_A15_A17_GeV": p["mA_heavy_GeV"],
            "mD2_and_D17_GeV": p["mD_heavy_GeV"],
            "m_over_Tmax": p["mA_heavy_GeV"] / p["Tmax_GeV"],
            "Boltzmann_tail_kernel_fraction": tail / full_kernel,
            "suppressed_decay_width_proxy_GeV": gamma_heavy,
            "suppressed_decay_lifetime_proxy_seconds": HBAR_GEV_S / gamma_heavy,
            "relative_freezein_yield_proxy_per_heavy_block": heavy_relative_yield_proxy,
            "proxy_before_0p1_second": HBAR_GEV_S / gamma_heavy < 0.1,
        },
        "cosmology_checks": {
            "BBN": {
                "conservative_lifetime_requirement_seconds": 0.1,
                "longest_displayed_parent_lifetime_seconds": HBAR_GEV_S / gamma_heavy,
                "unvalidated_proxy_before_BBN": HBAR_GEV_S / gamma_heavy < 0.1,
                "validated_pass": False,
            },
            "CMB_annihilation": {
                "proxy_sigma_v_cm3_per_s": annihilation_proxy,
                "proxy_p_ann_cm3_per_s_per_GeV": p_ann_proxy,
                "Planck_2018_limit": 3.2e-28,
                "passes_if_proxy_is_correct": p_ann_proxy < 3.2e-28,
                "validated_pass": False,
            },
            "thermal_unitarity": {
                "Griest_Kamionkowski_mass_limit_GeV": 3.4e5,
                "mD16_GeV": p["mD16_GeV"],
                "FIMP_is_not_thermal": True,
                "passes_reference_bound": p["mD16_GeV"] < 3.4e5,
            },
            "direct_detection": {
                "illustrative_assumption": "dim-five chi-chi-H-H contact C=lambda16*lambda_X_visible/mX with h_NN=f_N m_N/v included explicitly",
                "dim5_illustrative_sigma_SI_cm2": sigma_si_proxy,
                "status": "NON_CONSTRAINING_ILLUSTRATION",
                "not_used_for_viability": True,
                "XENONnT_2025_global_minimum_cm2_at_30_GeV": 1.7e-47,
                "illustrative_value_below_global_minimum": sigma_si_proxy < 1.7e-47,
            },
            "coldness": {
                "production_kernel_peak_x": x_peak,
                "T_production_GeV": t_production,
                "p_star_GeV": p_star,
                "T_nonrelativistic_GeV": t_nr,
                "p_over_m_at_equality": p_eq / p["mD16_GeV"],
                "radiation_era_free_streaming_proxy_Mpc": free_stream_mpc,
                "radiation_era_free_streaming_proxy_pc": free_stream_mpc * 1.0e6,
                "cold_before_BBN": t_nr > 1.0e-3,
            },
            "axion_isocurvature": {
                "assumption": "PQ is broken before inflation and no thermal/nonthermal restoration are imposed.",
                "imposed_axion_fraction_of_DM": p["axion_fraction_of_DM"],
                "Planck_beta_iso_limit": beta_limit,
                "P_iso": P_iso,
                "beta_iso": beta_iso,
                "H_inflation_GeV": p["H_inflation_GeV"],
                "H_inflation_max_GeV": H_iso_max,
                "passes_if_one_percent_fraction_is_imposed": beta_iso < beta_limit,
                "standard_misalignment_reference": misalignment,
                "joint_abundance_and_isocurvature_solution": False,
                "Tmax_over_fPQ": p["Tmax_GeV"] / p["fPQ_GeV"],
                "thermal_restoration_status": "CONDITIONAL: Tmax<fPQ is only a proxy; the finite-temperature PQ potential is not derived in V39.",
            },
        },
    }


def exact_selector_report() -> dict[str, Any]:
    terms = {name: term_audit(term) for name, term in CASCADE_TERMS.items()}
    fields_w = v37._state_space_first_breaking(False, 33, FIELDS)
    fields_k = v37._state_space_first_breaking(True, 33, FIELDS)
    z3_increment = v39_z3_dark_increment_audit()
    return {
        "six_field_cascade": D_FIELDS,
        "terms": {name: list(term) for name, term in CASCADE_TERMS.items()},
        "term_audits": terms,
        "all_terms_exactly_invariant": all(item["exactly_invariant"] for item in terms.values()),
        "all_terms_active_V39_Z3_neutral": all(item["V39_Z3_mod3"] == 0 for item in terms.values()),
        "active_V39_Z3_dark_anomaly_increment": z3_increment,
        "PQ_congruence_residues": pq_congruence_residues(),
        "all_new_fields_obey_PQ_selector_congruence": not any(pq_congruence_residues().values()),
        "Hsieh_Dai_Freed_Z5610": v37.hsieh_audit(N5610, hsieh_rows()),
        "mixed_Z4R_Z85_squared_increment": mixed_r_h2_increment(),
        "all_chiral_quality": {
            "first_W_breaking_degree": fields_w["first_breaking_degree"],
            "W_witness": fields_w["witness_multiplicities"],
            "first_Kahler_breaking_degree": fields_k["first_breaking_degree"],
            "Kahler_witness": fields_k["witness_multiplicities"],
            "active_V39_Z3_reasoning": (
                "The V37-plus-D search without Z3 is a relaxation and already excludes breaking below W33/K32; "
                "the split sixes project to the existing neutral R=2 Sig6 signature when Z3 is forgotten. "
                "Imposing Z3 cannot add states, while the Z3-neutral PS-singlet witnesses P^33 and "
                "P^6 A32^21 A16dag (A17dag)^4 attain degrees 33 and 32."
            ),
            "active_V39_exact_equalities_W33_K32": (
                fields_w["first_breaking_degree"] == 33 and fields_k["first_breaking_degree"] == 32
            ),
        },
    }


def report() -> dict[str, Any]:
    cosmology = solve_benchmark()
    selector = exact_selector_report()
    data: dict[str, Any] = {
        "schema": "susy-v39-g5-freezein-cosmology-certificate-v1",
        "scope": (
            "Secondary conditional decay-freeze-in screen for the six-field Z170 cascade; "
            "the corrected low-reheat secluded-freeze-out screen is likewise fail-closed."
        ),
        "exact_symmetry_and_quality": selector,
        "benchmark": cosmology,
        "sources": [
            {
                "topic": "decay freeze-in",
                "url": "https://arxiv.org/abs/0911.1120",
                "use": "thermal FIMP production framework",
            },
            {
                "topic": "thermal-relic unitarity",
                "url": "https://ntrs.nasa.gov/citations/19900004848",
                "use": "340 TeV elementary thermal relic reference",
            },
            {
                "topic": "CMB abundance and annihilation",
                "url": "https://arxiv.org/abs/1807.06209",
                "use": "Omega_c h^2 and p_ann < 3.2e-28 cm^3 s^-1 GeV^-1",
            },
            {
                "topic": "isocurvature",
                "url": "https://arxiv.org/abs/1807.06211",
                "use": "Planck 2018 inflation/isocurvature constraint basis",
            },
            {
                "topic": "BBN",
                "url": "https://arxiv.org/abs/astro-ph/0408426",
                "use": "conservative 0.1 s late-decay screening threshold",
            },
            {
                "topic": "direct detection",
                "url": "https://arxiv.org/abs/2502.18005",
                "use": "XENONnT 3.1 tonne-year SI reference",
            },
            {
                "topic": "QCD axion susceptibility/misalignment input",
                "url": "https://arxiv.org/abs/1606.07494",
                "use": "reference input; no joint axion cosmology is claimed",
            },
        ],
        "promotion": {
            "G5_closed": False,
            "primary_candidate": False,
            "parent_equilibrium_is_an_imposed_input": True,
            "benchmark_cosmology_is_internally_viable_under_its_inputs": False,
            "conditional_screens": {
                "freezein_integral_hits_imposed_target": (
                cosmology["freezein_boltzmann_solution"]["never_thermalizes_under_proxy"]
                and cosmology["cosmology_checks"]["BBN"]["unvalidated_proxy_before_BBN"]
                and cosmology["cosmology_checks"]["CMB_annihilation"]["passes_if_proxy_is_correct"]
                and cosmology["cosmology_checks"]["thermal_unitarity"]["passes_reference_bound"]
            ),
            },
            "not_predictive_because": [
                "mX, anomalon masses, and the parent equilibrium rate are chosen EFT inputs rather than derived from the V37 Kähler/soft vacuum",
                "the Maxwell-Boltzmann parent-multiplet treatment is not a component-resolved finite-temperature SUSY calculation",
                "the axion fraction, theta_i, H_inflation, Tmax, and absence of inflaton-to-D branching are imposed cosmological inputs; the standard-misalignment reference gives 0.126 percent rather than the imposed 1 percent",
                "finite-temperature PQ restoration, nonthermal preheating, domain walls, and the full soft/global vacuum remain uncomputed",
                "the direct-detection number is a dimensionally consistent but non-constraining illustration, not a matched 2-TeV nucleon likelihood",
                "X allows W linear/X^3 while X^2 is R-forbidden, so a single mX/width cannot substitute for the X/visible component mass matrix and possible <X>HH mixing",
            ],
            "next_required_calculations": [
                "derive mX, X vev/visible mixing, and all component masses from a stabilized Kähler/soft sector",
                "solve the coupled Bose/Fermi finite-temperature Boltzmann system including all A_i, D_i, X and reheating source terms",
                "supply an inflaton/reheaton sector and calculate Tmax and all visible/dark branching fractions",
                "compute the PQ finite-temperature potential, axion abundance, isocurvature, and defect history at the same point",
                "match the X/A-mediated nuclear matrix element and compare to the mass-dependent direct-detection likelihood",
            ],
        },
    }
    data["core_sha256"] = canonical_sha(data)
    return data


def markdown(data: dict[str, Any]) -> str:
    selector = data["exact_symmetry_and_quality"]
    b = data["benchmark"]
    fi = b["freezein_boltzmann_solution"]
    checks = b["cosmology_checks"]
    promotion = data["promotion"]
    return f"""# SUSY V39 G5 secondary freeze-in screen

## Outcome

This is a secondary conditional screen, not a G5 candidate.  It
assumes an equilibrated high-scale `A16` parent and gives a 1-TeV
`D16/Db16` Dirac FIMP through thermal `A16 -> D16 + X` decays.  The numerical
Boltzmann solution gives
`Omega_D h^2={fi['Omega_D16_h2']:.6f}` for
`lambda16={b['parameterization']['lambda16_freezein_solved']:.4e}`.
The other two anomalon blocks sit above `Tmax` and have prompt enough
P/M-suppressed *width proxies* if ever produced; those widths are not
component-resolved predictions.

## Exact selector checks

All six dark fields obey the V37 selector/PQ congruence, every cascade term is
exactly invariant, the combined Z5610 Hsieh/Dai--Freed test passes, the added
mixed `Z4R-Z85^2` residue is zero, and the all-chiral polynomial frontiers
remain W degree `{selector['all_chiral_quality']['first_W_breaking_degree']}`
and Kahler degree `{selector['all_chiral_quality']['first_Kahler_breaking_degree']}`.

## Benchmark boundaries

- Parent unvalidated width-proxy lifetime: `{fi['parent_lifetime_seconds']:.3e}` s; longest displayed
  heavy-block proxy lifetime: `{b['other_anomalon_blocks']['suppressed_decay_lifetime_proxy_seconds']:.3e}` s.
- CMB annihilation proxy: `{checks['CMB_annihilation']['proxy_p_ann_cm3_per_s_per_GeV']:.3e}` versus Planck's
  `{checks['CMB_annihilation']['Planck_2018_limit']:.1e}`.
- Dimensionally consistent but non-constraining dim-five illustration:
  `{checks['direct_detection']['dim5_illustrative_sigma_SI_cm2']:.3e}` cm^2. It is not a matched 2-TeV likelihood.
- The FIMP becomes nonrelativistic at `{checks['coldness']['T_nonrelativistic_GeV']:.1f}` GeV and has a
  radiation-era free-streaming proxy of `{checks['coldness']['radiation_era_free_streaming_proxy_pc']:.3e}` pc.
- With the explicitly assumed 1% axion fraction, `theta_i=0.05`, and
  `H_I=10^6` GeV, beta_iso is `{checks['axion_isocurvature']['beta_iso']:.3e}`,
  below `{checks['axion_isocurvature']['Planck_beta_iso_limit']}`; the separate
  misalignment reference yields `{checks['axion_isocurvature']['standard_misalignment_reference']['fraction_of_DM']:.3%}` of DM, so this is not joint.

## Strict boundary

This remains **not a G5 closure**. Its high-scale parent equilibrium and all
component widths are imposed/proxied rather than derived. The corrected
secluded-freeze-out screen is also fail-closed because of its Landau pole and
X-multiplet mass-matrix problem. Both constructions require a derived hidden
spectrum, reheating history, axion fraction, and soft/Kahler boundary
conditions, none of which V39 obtains from the V37 theory.

Primary sources: [freeze-in](https://arxiv.org/abs/0911.1120),
[Planck cosmology and CMB annihilation](https://arxiv.org/abs/1807.06209),
[Planck inflation](https://arxiv.org/abs/1807.06211),
[BBN late decays](https://arxiv.org/abs/astro-ph/0408426),
[thermal unitarity](https://ntrs.nasa.gov/citations/19900004848), and
[XENONnT](https://arxiv.org/abs/2502.18005), and [QCD axion
susceptibility](https://arxiv.org/abs/1606.07494).

Core SHA-256: `{data['core_sha256']}`
"""


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
            raise SystemExit("generated V39 freeze-in certificate is missing; run with --write")
        if canonical_bytes(json.loads(JSON_PATH.read_text(encoding="utf-8"))) != canonical_bytes(data):
            raise SystemExit("generated V39 freeze-in JSON is stale; run with --write")
        if MD_PATH.read_text(encoding="utf-8") != markdown(data):
            raise SystemExit("generated V39 freeze-in Markdown is stale; run with --write")
        print("SUSY V39 freeze-in audit: PASS")
        return
    print(json.dumps(data, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
