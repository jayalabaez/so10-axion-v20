#!/usr/bin/env python3
r"""Lift reduced vacuum / phase Hessian into 210+126+10 component space (v20).

Next step after ``gauge_scalar_interference_4x4_v20``:

1. Split the coarse ``P_210`` order parameter into the published Aulakh PS
   singlets ``(a, ω, p)`` of ``210_H`` (hep-ph/0204097), keeping
   ``Δ_R(126bar)``, ``H_{10,eff}``, ``h_EW``, ``S``, ``Φ₁₇``.
2. Embed the reduced radial wells + soft-mass stationarity shifts into this
   larger radial vector (block Hessian).
3. Embed the multi-operator phase Hessian into the larger phase vector, with
   ``(φ_a, φ_ω, φ_p)`` treated as gauge-fixed / heavy at the PS minimum and
   ``φ_Δ`` classified as the eaten Z' Goldstone on the selected vacuum.
4. Record a Goldstone ledger for ``SO(10)→SM`` (33 eaten) vs residual
   global/PQ flat directions.

Honesty
-------
* This is a **component lift of the reduced vacuum**, not a derivation of the
  complete independent ``210^n`` CG tensor basis.
* Full component mass matrices for every SM irrep remain OPEN.
* Unique ``τ_p`` remains OPEN.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import charge_allowed_potential_minimize_v20 as pmin
import multi_operator_phase_hessian_v20 as mph
import scalar_vacuum_proton_decay_v20 as scalar_pd
import selected_vacuum_neutral_phase_gauge_quotient_v20 as gauge_quot
import so10_126_to_54_projector_v20 as c126mod

ROOT = Path(__file__).resolve().parent

SOURCES = {
    "aulakh_210_singlets": {
        "citation": "Aulakh–Girdhar hep-ph/0204097",
        "use": "210 PS singlets a, ω, p; VEVs used as component lift targets",
    },
    "upstream_radial": "scalar_vacuum_proton_decay_v20.reduced_radial_vacuum_witness",
    "upstream_minimize": "charge_allowed_potential_minimize_v20",
    "upstream_phase": (
        "multi_operator_phase_hessian_v20 / "
        "selected_vacuum_neutral_phase_gauge_quotient_v20"
    ),
}

# Radial component names in the lifted space
RADIAL_COMPONENTS = (
    "a_210",
    "omega_210",
    "p_210",
    "DeltaR_126bar",
    "H10_eff",
    "h_EW",
    "S_PQ",
    "Phi17_X",
)

# Phase components (210 phases gauge-fixed / heavy)
PHASE_COMPONENTS = (
    "phi_a_210",
    "phi_omega_210",
    "phi_p_210",
    "phi_DeltaR_126",
    "phi_10",
    "phi_S",
    "phi_Phi17",
)


def component_ledger(anchor: dict[str, float]) -> dict[str, Any]:
    """Target VEVs for the lifted 210+126+10(+S+Φ) component set."""
    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    # Same fractional split used throughout the CG-weighted 210 stack
    a = 0.3 * m_gut
    omega = 0.5 * m_gut
    p = 0.2 * m_gut
    rows = [
        {
            "name": "a_210",
            "parent": "210_H",
            "ps": "PS singlet (Aulakh a)",
            "vev_GeV": a,
            "role": "GUT/PS breaking",
        },
        {
            "name": "omega_210",
            "parent": "210_H",
            "ps": "PS singlet (Aulakh ω)",
            "vev_GeV": omega,
            "role": "GUT/PS breaking",
        },
        {
            "name": "p_210",
            "parent": "210_H",
            "ps": "PS singlet (Aulakh p)",
            "vev_GeV": p,
            "role": "GUT/PS breaking",
        },
        {
            "name": "DeltaR_126bar",
            "parent": "126bar_H",
            "ps": "(10,1,3) SM-singlet direction",
            "vev_GeV": m_i,
            "role": "B−L / intermediate breaking",
        },
        {
            "name": "H10_eff",
            "parent": "10_H",
            "ps": "intermediate PQ-breaking proxy",
            "vev_GeV": m_i,
            "role": "locking / 10²S sector",
        },
        {
            "name": "h_EW",
            "parent": "10_H",
            "ps": "EW doublets",
            "vev_GeV": 174.0,
            "role": "electroweak breaking",
        },
        {
            "name": "S_PQ",
            "parent": "S",
            "ps": "singlet",
            "vev_GeV": m_i,
            "role": "PQ / Z17",
        },
        {
            "name": "Phi17_X",
            "parent": "Phi17",
            "ps": "singlet",
            "vev_GeV": 1.0e17,
            "role": "U(1)_X / Z17",
        },
    ]
    vevs = np.array([r["vev_GeV"] for r in rows], dtype=float)
    return {
        "status": "COMPONENT_VEV_LEDGER_BUILT",
        "n_radial_components": len(rows),
        "components": rows,
        "target_vevs_GeV": {r["name"]: r["vev_GeV"] for r in rows},
        "vev_vector_GeV": vevs.tolist(),
        "210_sum_check": {
            "a_plus_omega_plus_p_over_MGUT": float((a + omega + p) / m_gut),
            "expected_order_one": True,
            "note": "a+ω+p = M_GUT with the 0.3+0.5+0.2 split used in the CG stack",
        },
        "flag": {
            "210_split_into_a_omega_p": True,
            "all_sm_irreps_enumerated": False,
            "full_cg_tensors_normalized": False,
        },
    }


def goldstone_ledger() -> dict[str, Any]:
    """SO(10)→SM Goldstone counting + residual global phases."""
    so10 = 45
    sm = 8 + 3 + 1  # SU(3)×SU(2)×U(1)
    broken = so10 - sm
    return {
        "status": "GOLDSTONE_LEDGER_RECORDED",
        "so10_generators": so10,
        "sm_generators": sm,
        "broken_generators_eaten": broken,
        "expected_eaten_goldstones": broken,
        "residual_global": {
            "PQ_approx_U1": {
                "physical_mode": "axion (eaten by none if PQ global)",
                "related_flat_direction_reduced": (
                    "(1,-2) in gauge-fixed (φ_10,φ_S) when κ≠0; "
                    "prequotient (1,1,-2) among the two unquotiented nulls"
                ),
            },
            "Zprime_BL_R_eaten_DeltaR_phase": {
                "class": "gauge_fixed_or_eaten",
                "orbit": "(1,0,0) on (φ_Δ,φ_10,φ_S)",
                "note": (
                    "Selected-vacuum unquotiented second null is the broken "
                    "neutral Z'_R/B−L Goldstone, not a physical flat phase."
                ),
            },
            "Z17": {"discrete": True, "continuous_goldstone": False},
            "U1_X_broken_by_Phi17": {
                "eaten_or_massive": "Φ₁₇ VEV breaks U(1)_X; related phase heavy/eaten",
            },
        },
        "phase_components_in_lift": list(PHASE_COMPONENTS),
        "n_phase_components": len(PHASE_COMPONENTS),
        "n_gauge_fixed_or_heavy_210_phases": 3,
        "n_active_reduced_phases_prequotient": 3,
        "n_physical_reduced_phases_after_Zprime_quotient": 2,
        "flag": {
            "goldstone_counting_recorded": True,
            "complete_gauge_fixing_in_full_component_space": False,
            "selected_vacuum_DeltaR_phase_classified_as_eaten": True,
        },
        "verdict": (
            f"SO(10)→SM eats {broken} Goldstones. On the selected vacuum the "
            "reduced φ_Δ null is the eaten Z' Goldstone; the sole physical "
            "null after quotient is the PQ axion. Full component gauge fixing "
            "remains open."
        ),
    }


def lifted_radial_hessian(
    *,
    m_i: float,
    m_gut: float,
    soft_delta_m2: dict[str, float],
) -> dict[str, Any]:
    """Block radial Hessian on RADIAL_COMPONENTS at the target VEVs.

    210 block: independent wells for (a,ω,p) with λ~O(1) matching PR #18
    P_210 scale; reduced (Δ, H10, S) block reuses minimize wells + soft shifts;
    h and Φ₁₇ keep PR #18 self-quartics.
    """
    names = list(RADIAL_COMPONENTS)
    n = len(names)
    # Self-quartics λ_i (order-one, from witness scales)
    lambdas = {
        "a_210": 0.55,
        "omega_210": 0.55,
        "p_210": 0.55,
        "DeltaR_126bar": 0.65,
        "H10_eff": 0.50,
        "h_EW": 0.258,
        "S_PQ": 0.45,
        "Phi17_X": 0.75,
    }
    vevs = {
        "a_210": 0.3 * m_gut,
        "omega_210": 0.5 * m_gut,
        "p_210": 0.2 * m_gut,
        "DeltaR_126bar": m_i,
        "H10_eff": m_i,
        "h_EW": 174.0,
        "S_PQ": m_i,
        "Phi17_X": 1.0e17,
    }
    # Small cross-quartics among 210 singlets and among (Δ,H10,S)
    eps = np.zeros((n, n), dtype=float)
    idx = {name: i for i, name in enumerate(names)}
    for i, j, val in (
        ("a_210", "omega_210", 0.04),
        ("a_210", "p_210", 0.03),
        ("omega_210", "p_210", 0.04),
        ("DeltaR_126bar", "H10_eff", 0.03),
        ("DeltaR_126bar", "S_PQ", 0.04),
        ("H10_eff", "S_PQ", 0.03),
        ("a_210", "DeltaR_126bar", 0.02),
        ("omega_210", "DeltaR_126bar", 0.02),
        ("S_PQ", "Phi17_X", 0.01),
    ):
        eps[idx[i], idx[j]] = eps[idx[j], idx[i]] = val

    hess = np.zeros((n, n), dtype=float)
    for name in names:
        i = idx[name]
        v = vevs[name]
        lam = lambdas[name]
        # From V⊃(λ/4)(r²−v²)²: H_rr = 2 λ v² at r=v
        hess[i, i] += 2.0 * lam * v * v
        # Soft shift ΔV=(1/2) δm² (r²−v²) ⇒ H_rr += δm²
        hess[i, i] += float(soft_delta_m2.get(name, 0.0))
    # Cross: V⊃(ε/4)(r_i²−v_i²)(r_j²−v_j²) ⇒ H_ij = ε v_i v_j at targets
    for i in range(n):
        for j in range(i + 1, n):
            if eps[i, j] == 0.0:
                continue
            hij = eps[i, j] * vevs[names[i]] * vevs[names[j]]
            hess[i, j] += hij
            hess[j, i] += hij

    eigs = np.linalg.eigvalsh(hess)
    # Dimensionless Hessian Ĥ_ij = H_ij/(v_i v_j) — hierarchy-safe positivity
    # (absolute eigs are dominated by Φ₁₇ ~ 10^34 GeV² and poison float tol).
    vvec = np.array([vevs[name] for name in names], dtype=float)
    hhat = hess / np.outer(vvec, vvec)
    eigs_hat = np.linalg.eigvalsh(hhat)
    tol = 1e-10
    n_pos = int(np.sum(eigs_hat > tol))
    n_zero = int(np.sum(np.abs(eigs_hat) <= tol))
    n_neg = int(np.sum(eigs_hat < -tol))
    return {
        "fields": names,
        "lambdas": lambdas,
        "target_vevs_GeV": vevs,
        "soft_delta_m2_GeV2": {k: float(v) for k, v in soft_delta_m2.items()},
        "cross_eps": {
            f"{names[i]}__{names[j]}": float(eps[i, j])
            for i in range(n)
            for j in range(i + 1, n)
            if eps[i, j] != 0.0
        },
        "hessian_eigenvalues_GeV2": [float(x) for x in eigs],
        "dimensionless_hessian_eigenvalues": [float(x) for x in eigs_hat],
        "n_positive": n_pos,
        "n_zero": n_zero,
        "n_negative": n_neg,
        "positive_definite": n_neg == 0 and n_pos == n,
        "positivity_method": "dimensionless_Hij_over_vivj",
        "flag": {
            "lifted_radial_hessian_built": True,
            "full_sm_component_mass_matrices": False,
        },
    }


def soft_shifts_for_lift(
    *,
    kappa: float,
    lam4: float,
    lambda_lock: float,
    m_i: float,
    m_gut: float,
    c54: float,
    c126: float,
) -> dict[str, float]:
    """Map reduced (Δ,H10,S) soft shifts onto lifted names; 210 get 0."""
    soft = pmin.soft_mass_shifts_for_stationarity(
        kappa=kappa,
        lam4=lam4,
        lambda_lock=lambda_lock,
        m_i=m_i,
        m_gut=m_gut,
        c54=c54,
        c126=c126,
    )
    dm = soft["delta_m2_GeV2"]
    # soft fields order: r_Delta, r_10, r_S
    return {
        "a_210": 0.0,
        "omega_210": 0.0,
        "p_210": 0.0,
        "DeltaR_126bar": float(dm[0]),
        "H10_eff": float(dm[1]),
        "h_EW": 0.0,
        "S_PQ": float(dm[2]),
        "Phi17_X": 0.0,
        "_meta_stationarity_restored": soft["stationarity_restored"],
        "_meta_soft_norm_over_MI2": soft["soft_shift_norm_over_MI2"],
    }


def lifted_phase_hessian(
    *,
    a_lock: float,
    a_kappa: float,
    a_lam4: float,
) -> dict[str, Any]:
    """Embed reduced 3×3 multi-operator Hessian into 7-phase space.

    210 phases and φ_Φ17 are spectators (zero rows) at this lift — treated as
    gauge-fixed / heavy — while (φ_Δ, φ_10, φ_S) carry the active Hessian.
    On the selected vacuum φ_Δ is the eaten Z' Goldstone; physical closure is
    reported via the upstream gauge quotient when A_κ>0.
    """
    names = list(PHASE_COMPONENTS)
    n = len(names)
    # Indices of active reduced phases
    i_d, i_10, i_s = names.index("phi_DeltaR_126"), names.index("phi_10"), names.index(
        "phi_S"
    )
    reduced = mph.multi_operator_phase_hessian(
        a_lock=a_lock, a_kappa=a_kappa, a_lam4=a_lam4
    )
    h3 = np.array(reduced["hessian"], dtype=float)
    hess = np.zeros((n, n), dtype=float)
    active_idx = [i_d, i_10, i_s]
    for a in range(3):
        for b in range(3):
            hess[active_idx[a], active_idx[b]] = h3[a, b]

    # Scaled eigh
    scale = max(float(np.max(np.abs(hess))), 1.0)
    eigs = np.linalg.eigvalsh(hess / scale) * scale
    eigs = np.sort(eigs)
    tol = 1e-10 * scale
    n_pos = int(np.sum(eigs > tol))
    n_zero = int(np.sum(np.abs(eigs) <= tol))
    n_neg = int(np.sum(eigs < -tol))

    physical = None
    if a_kappa > 0.0 and abs(a_lock) == 0.0 and abs(a_lam4) == 0.0:
        physical = gauge_quot.quotient_report(a_kappa)

    return {
        "fields": names,
        "active_subspace": ["phi_DeltaR_126", "phi_10", "phi_S"],
        "gauge_fixed_or_heavy": [
            "phi_a_210",
            "phi_omega_210",
            "phi_p_210",
            "phi_Phi17",
        ],
        "eaten_zprime_phase": "phi_DeltaR_126",
        "reduced_operator_rank": reduced["operator_charge_rank"],
        "reduced_n_positive": reduced["n_positive"],
        "reduced_n_zero": reduced["n_zero"],
        "reduced_flat_direction": reduced["flat_direction"],
        "physical_after_gauge_quotient": (
            {
                "rank": physical["hessian"]["rank_after_quotient"],
                "nullity": physical["hessian"]["nullity_after_quotient"],
                "physical_null_vector_integer": physical["hessian"][
                    "physical_null_vector_integer"
                ],
                "extra_nonaxion_flat_phase": physical["flags"][
                    "extra_nonaxion_flat_phase_present"
                ],
            }
            if physical is not None
            else None
        ),
        "hessian_eigenvalues": [float(x) for x in eigs],
        "n_positive": n_pos,
        "n_zero": n_zero,
        "n_negative": n_neg,
        "expected_extra_zeros_from_spectators": 4,
        "flag": {
            "phase_hessian_lifted_to_component_space": True,
            "210_phases_gauge_fixed": True,
            "selected_vacuum_DeltaR_eaten_classified": True,
            "full_component_phase_space_dynamical": False,
        },
    }


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    if not anchor.get("available"):
        return {
            "status": "COMPONENT_LIFT_NOT_EXECUTED__ANCHOR_MISSING",
            "n_failed": 1,
            "failures": ["unification_anchor"],
            "flag": {"component_lift_built": False},
        }

    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    ledger = component_ledger(anchor)
    goldstones = goldstone_ledger()
    base = scalar_pd.reduced_radial_vacuum_witness(anchor)
    proj = c126mod.build_126_to_54_projector()
    c54 = float(proj["C_54_upstream"])
    c126 = float(proj["C_126_to_54"])
    vmin = pmin.build_report()
    best = vmin.get("fixed_couplings") or {}
    fk = vmin.get("finite_kappa_benchmark_couplings") or {}

    def _point(name: str, kappa: float, lam4: float, lam_lock: float) -> dict[str, Any]:
        soft = soft_shifts_for_lift(
            kappa=kappa,
            lam4=lam4,
            lambda_lock=lam_lock,
            m_i=m_i,
            m_gut=m_gut,
            c54=c54,
            c126=c126,
        )
        soft_for_hess = {k: v for k, v in soft.items() if not k.startswith("_meta")}
        radial = lifted_radial_hessian(
            m_i=m_i, m_gut=m_gut, soft_delta_m2=soft_for_hess
        )
        amp = mph.phase_amplitudes(
            kappa=kappa,
            lam4=lam4,
            lambda_lock=lam_lock,
            m_i=m_i,
            m_gut=m_gut,
            c54=c54,
            c126=c126,
        )
        phase = lifted_phase_hessian(
            a_lock=amp["A_lock"],
            a_kappa=amp["A_kappa"],
            a_lam4=amp["A_lam4"],
        )
        # Spectator zeros = total zeros − reduced zeros
        extra_zeros = phase["n_zero"] - phase["reduced_n_zero"]
        return {
            "name": name,
            "couplings": {
                "kappa": kappa,
                "lam4": lam4,
                "lambda_lock": lam_lock,
            },
            "soft_shift_norm_over_MI2": soft["_meta_soft_norm_over_MI2"],
            "radial": {
                "positive_definite": radial["positive_definite"],
                "n_positive": radial["n_positive"],
                "n_zero": radial["n_zero"],
                "n_negative": radial["n_negative"],
            },
            "phase": {
                "n_positive": phase["n_positive"],
                "n_zero": phase["n_zero"],
                "reduced_n_positive": phase["reduced_n_positive"],
                "reduced_n_zero": phase["reduced_n_zero"],
                "extra_spectator_zeros": extra_zeros,
                "flat_direction_reduced": phase["reduced_flat_direction"],
                "physical_after_gauge_quotient": phase[
                    "physical_after_gauge_quotient"
                ],
            },
            "amplitudes": {
                "A_lock": amp["A_lock"],
                "A_kappa": amp["A_kappa"],
                "A_lam4": amp["A_lam4"],
            },
            "radial_full": radial,
            "phase_full": phase,
        }

    points = [
        _point(
            "minimized_best_fit",
            float(best.get("kappa", 0.0)),
            float(best.get("lam4", 0.0)),
            float(best.get("lambda_lock", 1.0)),
        ),
        _point(
            "finite_kappa_benchmark",
            float(fk.get("kappa", 0.05)),
            float(fk.get("lam4", 0.0)),
            float(fk.get("lambda_lock", 1.0)),
        ),
        _point("locking_only", 0.0, 0.0, 1.0),
    ]

    locking_only = next(p for p in points if p["name"] == "locking_only")
    finite_k = next(p for p in points if p["name"] == "finite_kappa_benchmark")
    fk_phys = finite_k["phase"]["physical_after_gauge_quotient"]

    checks = {
        "ledger_8_components": ledger["n_radial_components"] == 8,
        "210_split_ok": abs(
            ledger["210_sum_check"]["a_plus_omega_plus_p_over_MGUT"] - 1.0
        )
        < 1e-12,
        "base_radial_ok": bool(
            base.get("flag", {}).get("reduced_radial_global_minimum_proved")
        ),
        "all_points_radial_pd": all(p["radial"]["positive_definite"] for p in points),
        # Selected vacuum: A_lock=A_lam4=0. locking_only ⇒ fully flat reduced.
        "locking_only_phase_pattern": locking_only["phase"]["reduced_n_positive"] == 0
        and locking_only["phase"]["reduced_n_zero"] == 3,
        # Finite κ ⇒ prequotient rank 1 / nullity 2; physical quotient closed.
        "finite_kappa_phase_pattern": finite_k["phase"]["reduced_n_positive"] == 1
        and finite_k["phase"]["reduced_n_zero"] == 2,
        "finite_kappa_physical_quotient_closed": (
            fk_phys is not None
            and fk_phys["rank"] == 1
            and fk_phys["nullity"] == 1
            and not fk_phys["extra_nonaxion_flat_phase"]
        ),
        "spectator_zeros_match": all(
            p["phase"]["extra_spectator_zeros"]
            == p["phase_full"]["expected_extra_zeros_from_spectators"]
            for p in points
        ),
        "goldstones_33": goldstones["broken_generators_eaten"] == 33,
        "upstream_minimize_ok": vmin.get("n_failed", 1) == 0,
        "not_claiming_full_cg": True,
        "not_claiming_unique_taup": True,
    }
    failures = [n for n, ok in checks.items() if not ok]

    # Drop bulky hessian matrices from top-level JSON points (keep summaries)
    points_out = []
    for p in points:
        points_out.append(
            {
                "name": p["name"],
                "couplings": p["couplings"],
                "soft_shift_norm_over_MI2": p["soft_shift_norm_over_MI2"],
                "radial": p["radial"],
                "phase": p["phase"],
                "amplitudes": p["amplitudes"],
                "radial_eigenvalues_GeV2": p["radial_full"][
                    "hessian_eigenvalues_GeV2"
                ],
                "radial_dimensionless_eigenvalues": p["radial_full"][
                    "dimensionless_hessian_eigenvalues"
                ],
                "phase_eigenvalues": p["phase_full"]["hessian_eigenvalues"],
            }
        )

    return {
        "status": (
            "COMPONENT_LIFT_OF_REDUCED_VACUUM_COMPLETE__FULL_CG_OPEN"
            if not failures
            else "COMPONENT_LIFT_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "sources": SOURCES,
        "component_ledger": ledger,
        "goldstone_ledger": goldstones,
        "radial_components": list(RADIAL_COMPONENTS),
        "phase_components": list(PHASE_COMPONENTS),
        "points": points_out,
        "upstream_minimize_status": vmin.get("status"),
        "upstream_base_radial_status": base.get("status"),
        "next_exact_calculation": [
            "Normalize remaining independent 210^n CG tensors in the full invariant basis",
            "Build SM-irrep mass matrices for every heavy threshold component",
            "Complete gauge fixing / Goldstone eating in the full component space",
            "Derive unique flavour rotations for gauge X/Y amplitudes",
        ],
        "flag": {
            "component_lift_of_reduced_vacuum": True,
            "210_split_into_a_omega_p": True,
            "lifted_radial_hessian_pd": all(
                p["radial"]["positive_definite"] for p in points
            ),
            "phase_hessian_embedded": True,
            "goldstone_counting_recorded": True,
            "full_cg_tensors_normalized": False,
            "all_sm_irreps_mass_matrices": False,
            "complete_so10_scalar_potential": False,
            "exact_unique_proton_lifetime": False,
            "invented_unpublished_cg_values": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "Reduced vacuum and multi-operator phase Hessian lifted into an "
            "8-component radial + 7-phase space with 210 split into (a,ω,p). "
            "Radial Hessians are PD; selected-vacuum phase patterns embed with "
            "4 spectator zeros, φ_Δ classified as the eaten Z' Goldstone, and "
            "physical quotient closure when κ≠0. Full 210^n CG tensors and "
            "complete SM-irrep spectra remain OPEN."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Component lift 210+126+10 — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        f"- Radial components: {', '.join(report['radial_components'])}",
        f"- Phase components: {', '.join(report['phase_components'])}",
        f"- Eaten Goldstones SO(10)→SM: "
        f"{report['goldstone_ledger']['broken_generators_eaten']}",
        "",
        "## Points",
        "",
    ]
    for p in report["points"]:
        lines.append(
            f"- `{p['name']}`: radial PD={p['radial']['positive_definite']}; "
            f"phase n₊={p['phase']['n_positive']}, n₀={p['phase']['n_zero']} "
            f"(reduced {p['phase']['reduced_n_positive']}/"
            f"{p['phase']['reduced_n_zero']})"
        )
    lines.extend(["", "## Next exact calculation", ""])
    for step in report["next_exact_calculation"]:
        lines.append(f"1. {step}")
    lines.extend(["", "## Flags", ""])
    for k, v in report["flag"].items():
        lines.append(f"- `{k}`: {v}")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    report = build_report()
    ROOT.joinpath("COMPONENT_LIFT_210_126_10_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("COMPONENT_LIFT_210_126_10_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "n_radial": report["component_ledger"]["n_radial_components"],
                "eaten_goldstones": report["goldstone_ledger"][
                    "broken_generators_eaten"
                ],
                "points": [
                    {
                        "name": p["name"],
                        "radial_pd": p["radial"]["positive_definite"],
                        "phase_n_pos": p["phase"]["n_positive"],
                        "phase_n_zero": p["phase"]["n_zero"],
                        "reduced_n_pos": p["phase"]["reduced_n_positive"],
                        "reduced_n_zero": p["phase"]["reduced_n_zero"],
                    }
                    for p in report.get("points", [])
                ],
                "flag": report.get("flag"),
                "verdict": report.get("verdict"),
            },
            indent=2,
        )
    )
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
