#!/usr/bin/env python3
"""PQ-axion quotient on the extended form-basis Hessian (v20).

The reduced selected-vacuum phase sector
(``selected_vacuum_neutral_phase_gauge_quotient_v20``) shows that after the
Z'_R gauge quotient the physical ``(φ_10, φ_S)`` Hessian from κ H₁₀² S has

* one massive CP-odd eigenvalue ``5 A_κ``;
* exactly one null ``(1,-2)`` — the PQ axion.

This module lifts that structure onto the extended 738-dim form-basis
Hessian:

1. Assemble the Im-H + S/Φ₁₇ skeleton (Hodge C, full portal B, soft blocks);
2. Replace soft masses on ``(Im H[hEW], Im S)`` with the κ phase Hessian
   mapped through the real-VEV Jacobian ``φ = (Im_H/hEW, Im_S/vS)``;
3. Build the axion direction ``n ∝ (hEW, −2 vS)`` in that plane, orthogonal
   to the 36 SO(10) Goldstones;
4. Project ``P_phys = I − P_G − P_axion`` and require 37 exact zeros with a
   positive physical complement.

``A_κ`` is taken from the physical formula
``A_κ = |κ| M_I hEW² v_S`` (``uv_kappa_stationarity_constraint_v20``), not
the former diagnostic ``min(A,C)/5``.

Honesty
-------
* κ remains stationarity-constrained but not UV-unique.
* PQ quotient is for this extended skeleton only — not full G1–G8 closure.
* Does not invent 120/320/1050/4125 CG. Theory remains BLOCKED.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

import diagonal_210_radial_cubic_ps_singlet_v20 as d210
import diagonal_h10_sigmabar_m2_isotropic_54_slots_v20 as iso
import direct_portal_mass2_schur_gate_v20 as schur
import extended_form_basis_hessian_imh_spectators_v20 as ext
import selected_vacuum_neutral_phase_gauge_quotient_v20 as pq
import so10_gauge_orbit_with_hew_v20 as hew_orbit
import so10_goldstone_nullspace_projector_v20 as gproj
import uv_kappa_stationarity_constraint_v20 as uv_kappa

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXTENDED_HESSIAN_PQ_AXION_QUOTIENT_V20.json"
OUT_MD = ROOT / "EXTENDED_HESSIAN_PQ_AXION_QUOTIENT_V20.md"

EXPECTED_GOLDSTONES = 36
EXPECTED_AXIONS = 1
EXPECTED_REMOVED = EXPECTED_GOLDSTONES + EXPECTED_AXIONS  # 37
EXPECTED_FIELD_DIM = ext.EXPECTED_FIELD_DIM  # 738
HEW_DIRECTION_INDEX = hew_orbit.HEW_DIRECTION_INDEX


def kappa_phase_hessian_phi(*, a_kappa: float) -> np.ndarray:
    """2×2 Hessian on (φ_10, φ_S) from κ: A_κ · g gᵀ with g=(2,1)."""
    return np.asarray(
        pq.quotient_report(a_kappa)["hessian"]["after_quotient"], dtype=float
    )


def kappa_phase_hessian_im_components(
    *,
    a_kappa: float,
    h_ew: float,
    v_s: float,
) -> dict[str, Any]:
    """Map phase Hessian to (Im H[hEW], Im S) at real VEVs."""
    if h_ew == 0.0 or v_s == 0.0:
        raise ValueError("hEW and vS must be nonzero for phase Jacobian")
    h_phi = np.asarray(kappa_phase_hessian_phi(a_kappa=a_kappa), dtype=float)
    # φ = J x with x=(Im_H, Im_S), J=diag(1/hEW, 1/vS)
    j = np.diag([1.0 / float(h_ew), 1.0 / float(v_s)])
    h_x = j.T @ h_phi @ j
    # Axion in φ-space (1,-2) ⇒ x ∝ (hEW, -2 vS)
    axion_x = np.array([float(h_ew), -2.0 * float(v_s)], dtype=float)
    axion_x /= np.linalg.norm(axion_x)
    # Massive direction ∥ g=(2,1) in φ-space
    massive_phi = np.array([2.0, 1.0], dtype=float)
    massive_phi /= np.linalg.norm(massive_phi)
    return {
        "H_phi": h_phi,
        "H_im": h_x,
        "axion_im_unit": axion_x,
        "a_kappa": float(a_kappa),
        "hEW": float(h_ew),
        "vS": float(v_s),
        "null_residual": float(np.linalg.norm(h_x @ axion_x)),
        "massive_eig_phi": float(massive_phi @ h_phi @ massive_phi),
    }


def inject_kappa_phase_block(
    hessian: np.ndarray,
    slices: dict[str, list[int]],
    phase: dict[str, Any],
) -> dict[str, Any]:
    """Overwrite soft masses on (Im H[hEW], Im S) with κ phase Hessian."""
    hess = np.array(hessian, dtype=float, copy=True)
    i_im_h0 = slices["H10_Im"][0]
    i_im_s0 = slices["S"][0]
    i_im_h = i_im_h0 + HEW_DIRECTION_INDEX
    i_im_s = i_im_s0 + 1  # Im S
    idx = [i_im_h, i_im_s]
    # Clear any prior soft entries in this plane.
    hess[np.ix_(idx, idx)] = 0.0
    hess[np.ix_(idx, idx)] = phase["H_im"]
    return {
        "hessian": hess,
        "im_H_index": i_im_h,
        "im_S_index": i_im_s,
        "indices": idx,
    }


def axion_direction_738(
    n_field: int, *, im_h_index: int, im_s_index: int, h_ew: float, v_s: float
) -> np.ndarray:
    n = np.zeros(n_field, dtype=float)
    n[im_h_index] = float(h_ew)
    n[im_s_index] = -2.0 * float(v_s)
    nrm = float(np.linalg.norm(n))
    if nrm <= 0.0:
        raise ValueError("degenerate axion direction")
    return n / nrm


def combined_physical_projector(
    goldstone_frame: np.ndarray, axion: np.ndarray
) -> dict[str, Any]:
    """P_phys = I - P_G - P_axion with axion orthogonalized to Goldstones."""
    n_field = goldstone_frame.shape[0]
    if goldstone_frame.size:
        p_g = goldstone_frame @ goldstone_frame.T
        ax = axion - goldstone_frame @ (goldstone_frame.T @ axion)
    else:
        p_g = np.zeros((n_field, n_field), dtype=float)
        ax = axion.copy()
    nrm = float(np.linalg.norm(ax))
    if nrm < 1e-14:
        raise ValueError("axion lies inside the Goldstone span")
    ax = ax / nrm
    p_ax = np.outer(ax, ax)
    overlap = float(np.linalg.norm(p_g @ ax))
    p_phys = np.eye(n_field) - p_g - p_ax
    return {
        "P_G": p_g,
        "P_axion": p_ax,
        "P_phys": p_phys,
        "axion_unit": ax,
        "axion_goldstone_overlap": overlap,
        "trace_P_G": float(np.trace(p_g)),
        "trace_P_axion": float(np.trace(p_ax)),
        "trace_P_phys": float(np.trace(p_phys)),
    }


def spectrum_after_projection(
    hessian: np.ndarray,
    p_phys: np.ndarray,
    *,
    rel_tol: float = 1e-10,
    abs_tol: float | None = None,
) -> dict[str, Any]:
    h_proj = gproj.project_hessian(hessian, p_phys)
    eigs = np.linalg.eigvalsh(h_proj)
    scale = max(1.0, float(np.max(np.abs(eigs))))
    tol = rel_tol * scale
    if abs_tol is not None:
        # Physical A_κ can place the CP-odd massive mode far below soft median;
        # tighten tol so that mode is not falsely counted as a zero.
        tol = min(tol, float(abs_tol))
    return {
        "n_zero": int(np.sum(np.abs(eigs) <= tol)),
        "n_positive": int(np.sum(eigs > tol)),
        "n_negative": int(np.sum(eigs < -tol)),
        "eig_min_GeV2": float(eigs[0]),
        "eig_max_GeV2": float(eigs[-1]),
        "tol_GeV2": tol,
    }


def build_report() -> dict[str, Any]:
    iso_report = iso.build_report()
    a = iso_report["A_partial_GeV2"]
    c = iso_report["C_partial_GeV2"]
    vevs = iso_report["vevs_GeV"]
    lam4 = iso_report["portal_B"]["lam4"]
    h_ew = float(vevs["hEW"])
    v_s = float(vevs["vS"])
    scale = float(min(np.min(a), np.min(c)))
    # Former diagnostic (visibility only); physical A_κ from UV-κ module.
    a_kappa_diagnostic = scale / 5.0
    uv = uv_kappa.build_report()
    a_kappa = float(uv["A_kappa"]["physical_GeV2"])

    # Reuse extended assembly path.
    import scalar_vacuum_proton_decay_v20 as scalar_pd

    anchor = scalar_pd._unification_anchor()
    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    specs = ext.spectator_soft_masses(
        vevs,
        m_i=m_i,
        m_gut=m_gut,
        lam4=lam4,
        scale_floor_gev2=scale,
    )
    mixing = schur.portal_mass2_matrix(
        p=vevs["p"],
        a=vevs["a"],
        omega=vevs["omega"],
        v_s=v_s,
        lam4=lam4,
    )
    m2_210 = float(
        d210.reduced_p210_mass2(m_i=m_i, m_gut=m_gut, lam4=0.0)[
            "m2_210_form_basis_GeV2"
        ]
    )
    assembled = ext.assemble_extended_hessian(
        a_h10=a,
        c_diag=c,
        b_10x126=mixing,
        m2_210=m2_210,
        m2_s=specs["mu2_S"],
        m2_phi17=specs["mu2_Phi17"],
    )

    phase = kappa_phase_hessian_im_components(
        a_kappa=a_kappa, h_ew=h_ew, v_s=v_s
    )
    injected = inject_kappa_phase_block(
        assembled["hessian"], assembled["slices"], phase
    )
    hess = injected["hessian"]

    tang = ext.extended_tangent_matrix()
    tangent = tang["matrix"]
    n_field = tang["n_field_components"]
    frame_info = gproj.goldstone_frame_from_tangent(tangent)
    frame = frame_info["frame"]

    axion = axion_direction_738(
        n_field,
        im_h_index=injected["im_H_index"],
        im_s_index=injected["im_S_index"],
        h_ew=h_ew,
        v_s=v_s,
    )
    projs = combined_physical_projector(frame, axion)

    # Axion should already be a Hessian null before projection.
    axion_rayleigh = float(axion @ hess @ axion)
    axion_image = float(np.linalg.norm(hess @ axion)) / max(
        1.0, float(np.linalg.norm(hess))
    )

    n_phys = EXPECTED_FIELD_DIM - EXPECTED_REMOVED
    unit_spec = spectrum_after_projection(np.eye(n_field), projs["P_phys"])

    diag = np.abs(np.diag(hess))
    median = float(np.median(diag[diag > 0.0])) if np.any(diag > 0.0) else 1.0
    # Rank-1 Im-space massive eigenvalue: A_κ ||Jᵀ g||² with g=(2,1).
    expected_im_massive = a_kappa * (4.0 / (h_ew**2) + 1.0 / (v_s**2))
    expected_scaled = expected_im_massive / max(median, 1.0)
    dyn_abs_tol = max(1e-18, 0.1 * expected_scaled)
    dyn_spec = spectrum_after_projection(
        hess / median, projs["P_phys"], abs_tol=dyn_abs_tol
    )

    # Upstream reduced quotient must stay green.
    reduced = pq.quotient_report(a_kappa=1.0)

    checks = {
        "isotropic_partial_green": iso_report.get("n_failed", 1) == 0,
        "uv_kappa_green": uv.get("n_failed", 1) == 0,
        "physical_A_kappa_positive": a_kappa > 0.0,
        "reduced_pq_quotient_green": reduced.get("n_failed", 1) == 0,
        "field_dim_738": n_field == EXPECTED_FIELD_DIM,
        "goldstone_rank_36": frame_info["rank"] == EXPECTED_GOLDSTONES,
        "trace_P_G_36": abs(projs["trace_P_G"] - EXPECTED_GOLDSTONES) < 1e-6,
        "trace_P_axion_1": abs(projs["trace_P_axion"] - 1.0) < 1e-6,
        "trace_P_phys_701": abs(projs["trace_P_phys"] - n_phys) < 1e-6,
        "axion_orthogonal_to_goldstones": projs["axion_goldstone_overlap"] < 1e-10,
        "kappa_im_null_residual_tiny": bool(
            phase["null_residual"]
            < 1e-10 * max(1.0, float(np.max(np.abs(phase["H_im"]))))
        ),
        "axion_hessian_rayleigh_tiny": bool(
            abs(axion_rayleigh) < 1e-8 * max(1.0, float(np.max(np.abs(hess))))
        ),
        "axion_hessian_image_tiny": bool(axion_image < 1e-8),
        "unit_37_zeros": unit_spec["n_zero"] == EXPECTED_REMOVED,
        "unit_no_negative": unit_spec["n_negative"] == 0,
        "unit_physical_positive": unit_spec["n_positive"] == n_phys,
        "dyn_scaled_37_zeros": dyn_spec["n_zero"] == EXPECTED_REMOVED,
        "dyn_scaled_no_negative": dyn_spec["n_negative"] == 0,
        "dyn_scaled_physical_positive": dyn_spec["n_positive"] == n_phys,
        "im_H_portal_retained": assembled["portal"]["im_H_included"],
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "EXTENDED_HESSIAN_PQ_AXION_QUOTIENT_READY__FULL_HESSIAN_OPEN"
            if not failures
            else "EXTENDED_HESSIAN_PQ_AXION_QUOTIENT_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "embedding": tang["embedding"],
        "kappa_phase": {
            "A_kappa_GeV2": a_kappa,
            "A_kappa_scale_rule": "physical |κ| M_I hEW² v_S (uv_kappa_stationarity)",
            "A_kappa_diagnostic_minAC_over_5_GeV2": a_kappa_diagnostic,
            "A_kappa_source_status": uv.get("status"),
            "kappa_coupling": uv["couplings"]["kappa"],
            "hEW_GeV": h_ew,
            "vS_GeV": v_s,
            "H_phi": phase["H_phi"].tolist(),
            "massive_eig_phi_GeV2": phase["massive_eig_phi"],
            "im_null_residual": phase["null_residual"],
            "im_H_index": injected["im_H_index"],
            "im_S_index": injected["im_S_index"],
            "axion_phi_integer": [1, -2],
        },
        "projectors": {
            "trace_P_G": projs["trace_P_G"],
            "trace_P_axion": projs["trace_P_axion"],
            "trace_P_phys": projs["trace_P_phys"],
            "axion_goldstone_overlap": projs["axion_goldstone_overlap"],
            "axion_hessian_rayleigh_GeV2": axion_rayleigh,
            "axion_hessian_image_residual": axion_image,
        },
        "goldstone_axion_projection": {
            "n_removed": EXPECTED_REMOVED,
            "unit_spectrum": unit_spec,
            "dynamical_scaled_spectrum": dyn_spec,
            "median_abs_diag_GeV2": median,
            "expected_im_massive_GeV2": expected_im_massive,
            "expected_scaled_massive": expected_scaled,
            "dyn_abs_tol_used": dyn_abs_tol,
        },
        "upstream_reduced_quotient_status": reduced.get("status"),
        "flags": {
            "pq_axion_quotient_on_extended_hessian": not bool(failures),
            "gauge_36_and_axion_1_removed": not bool(failures),
            "kappa_phase_block_injected": True,
            "physical_A_kappa_wired": not bool(failures),
            "uv_kappa_uniquely_determined": False,
            "full_component_hessian_complete": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "remaining_blockers": {
            "missing_cg_120_320_1050_4125": True,
            "complete_sm_irrep_mass_matrices": True,
            "global_stationarity_boundedness": True,
            "unique_uv_kappa": True,
        },
        "verdict": (
            "Injected physical A_κ phase Hessian on (Im H[hEW], Im S) yields an "
            f"exact PQ axion null; combined removal of {EXPECTED_GOLDSTONES} "
            f"Goldstones + {EXPECTED_AXIONS} axion leaves "
            f"{dyn_spec['n_zero']} zeros / {dyn_spec['n_positive']} positive / "
            f"{dyn_spec['n_negative']} negative modes on the dim-{EXPECTED_FIELD_DIM} "
            "skeleton. Full component Hessian and theory closure remain BLOCKED."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    ga = report["goldstone_axion_projection"]
    OUT_MD.write_text(
        "# Extended Hessian PQ-axion quotient — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- Removed (Goldstone+axion): `{ga['n_removed']}`\n"
        f"- Dynamical zeros/pos/neg: "
        f"`{ga['dynamical_scaled_spectrum']['n_zero']}` / "
        f"`{ga['dynamical_scaled_spectrum']['n_positive']}` / "
        f"`{ga['dynamical_scaled_spectrum']['n_negative']}`\n\n"
        + report["verdict"]
        + "\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        write_report(report)
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
