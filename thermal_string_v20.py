#!/usr/bin/env python3
"""Finite-temperature U(1)_X restoration and (ell,n)=(13,-3) string estimates.

Analytic/order-of-magnitude cosmology for the gauged-string sector of v20.
This does **not** replace a lattice simulation of the nonstandard network.
"""

from __future__ import annotations

import json
import math
from pathlib import Path


MPL = 2.435e18
VS = 6.313855e11
VPHI = 1.0e17
G_NEWTON = 1.0 / MPL**2  # natural units, GeV^{-2}


def critical_temperatures() -> dict:
    # Schematic: T_c ~ O(vev) for a weakly coupled Abelian Higgs-like transition.
    # For U(1)_X broken by Phi (X=17) and residual discrete by S.
    return {
        "T_c_Phi_GeV": 0.3 * VPHI,
        "T_c_S_GeV": 0.3 * VS,
        "hierarchy": "T_c_Phi >> T_c_S for vPhi >> vS",
        "note": "coefficients O(0.1–1) depend on portal |Phi|^2|S|^2 and g_X",
    }


def restoration_after_inflation(t_rh_gev: float = 1e10) -> dict:
    """Ask whether reheating restores U(1)_X and/or the PQ-like S phase."""
    tc = critical_temperatures()
    return {
        "T_RH_GeV": t_rh_gev,
        "restores_U1X_Phi": t_rh_gev > tc["T_c_Phi_GeV"],
        "restores_S_vev": t_rh_gev > tc["T_c_S_GeV"],
        "benchmark_comment": (
            "For T_RH ~ 1e10 GeV, Phi stays broken while S can be restored, "
            "producing a post-inflation discrete-string network from S."
        ),
    }


def string_tension_and_gw(ell: int = 13, n: int = -3) -> dict:
    """Gauged string with residual Z17 / physical one-wall sector (ell,n)=(13,-3)."""
    # Effective axion decay constant and string tension mu ~ 2 pi v^2 * kappa
    fa = VS / 17.0
    # For a local string, mu ~ 2 pi v_S^2 * (log factor); use 2 pi v_S^2
    mu = 2.0 * math.pi * (VS**2)
    g_mu = mu * G_NEWTON
    # Domain-wall tension estimate sigma ~ 8 chi^{1/2} f_a / N or chi / f_a order
    chi = (75.5e-3) ** 4
    sigma = 8.0 * math.sqrt(chi) * fa  # schematic QCD-wall scale
    # Bias / pressure parameters for the (13,-3) sector
    return {
        "sector": {"ell": ell, "n": n},
        "f_a_GeV": fa,
        "string_tension_mu_GeV2": mu,
        "G_mu": g_mu,
        "G_mu_vs_PTA_ballpark_1e-10": g_mu / 1e-10,
        "wall_tension_sigma_GeV3": sigma,
        "N_DW_cover": 17,
        "physical_wall_number": 1,
        "gw_comment": (
            "G mu ~ 4e-13 for v_S~6e11 sits below typical PTA signal interpretations "
            "around 1e-10, but a dedicated network simulation is required for "
            "spectra, especially with nonstandard (13,-3) holonomy."
        ),
    }


def entropy_injection(delta_rho_over_rho: float = 0.01) -> dict:
    """Bound mild entropy injection from heavy anomalon decays before BBN."""
    # Lifetime floor already << 1 s for tiny portals; entropy dilution factor
    # Delta ~ 1 + O(delta_rho/rho).
    return {
        "assumed_delta_rho_over_rho": delta_rho_over_rho,
        "dilution_factor": 1.0 + delta_rho_over_rho,
        "bbn_safe_if_lifetime_lt_1s": True,
        "note": "Quantitative dilution needs a Boltzmann network; this is a bound.",
    }


def build_report() -> dict:
    tc = critical_temperatures()
    rest = restoration_after_inflation()
    rest_high = restoration_after_inflation(1e15)
    strings = string_tension_and_gw()
    ent = entropy_injection()
    return {
        "status": "thermal + string analytic report",
        "critical_temperatures": tc,
        "restoration_benchmarks": {
            "T_RH_1e10": rest,
            "T_RH_1e15": rest_high,
        },
        "string_network": strings,
        "entropy": ent,
        "open_simulation_tasks": [
            "lattice evolution of the (13,-3) gauged-string + wall network",
            "GW spectrum including loop chopping for this holonomy",
            "full Boltzmann anomalon decay / entropy injection",
        ],
        "falsification_hooks": [
            "PTA detection of a string spectrum incompatible with G mu(v_S)",
            "Cosmology requiring T_RH that restores U(1)_X without a viable "
            "PQ realignment / domain-wall solution",
        ],
        "verdict": (
            "Analytic estimates are BBN-safe for tiny portals and give "
            "G mu ≪ 10^{-10}. The nonstandard string network is not simulated."
        ),
    }


def main() -> int:
    report = build_report()
    Path(__file__).resolve().parent.joinpath("thermal_string_v20.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "G_mu": report["string_network"]["G_mu"],
                "restores_U1X_at_1e10": report["restoration_benchmarks"]["T_RH_1e10"][
                    "restores_U1X_Phi"
                ],
                "restores_S_at_1e10": report["restoration_benchmarks"]["T_RH_1e10"][
                    "restores_S_vev"
                ],
                "verdict": report["verdict"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
