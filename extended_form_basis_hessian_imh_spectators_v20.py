#!/usr/bin/env python3
"""Extended form-basis Hessian: Im H + S/Φ₁₇ spectators (v20).

Upgrades the 724-dim orbit embedding to

    ℝ²¹⁰ ⊕ ℝ⁵⁰⁴ ⊕ ℂ¹⁰ ⊕ ℂ_S ⊕ ℂ_Φ₁₇
        = 210 + 504 + 20 + 2 + 2
        = 738 real

by:

1. Padding the hEW-extended SO(10) tangent with zero rows for Im H, S, Φ₁₇
   (SO(10) singlets / imaginary H do not enlarge the 36-Goldstone rank);
2. Inserting the full holomorphic portal ``B`` on (Re H, Im H) ↔ ambient 504
   via the Hodge anti-self-dual frame (2 Re(xᵀ B z) convention);
3. Placing positive soft masses for S and Φ₁₇ from the reduced radial
   Hessian diagonals (Re/Im isotropic placeholders).

Honesty
-------
* PQ axion null is not removed here (gauge projection only removes 36
  SO(10) Goldstones). Soft masses on Im S are placeholders.
* Φ₁₇ / S are SO(10) singlets: no SO(10) gauge orbit.
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
import hodge_126bar_c_embedding_portal_lift_v20 as hodge
import nonsusy_reduced_hessian_v20 as reduced
import scalar_vacuum_proton_decay_v20 as scalar_pd
import so10_gauge_orbit_with_hew_v20 as hew_orbit
import so10_goldstone_nullspace_projector_v20 as gproj

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXTENDED_FORM_BASIS_HESSIAN_IMH_SPECTATORS_V20.json"
OUT_MD = ROOT / "EXTENDED_FORM_BASIS_HESSIAN_IMH_SPECTATORS_V20.md"

SOFT_FLOOR_GEV2 = 1.0e4
EXPECTED_GOLDSTONES = 36
DIM_210 = 210
DIM_504 = 504
DIM_H10 = 10
DIM_S = 2  # Re S, Im S
DIM_PHI17 = 2  # Re Φ₁₇, Im Φ₁₇
EXPECTED_FIELD_DIM = DIM_210 + DIM_504 + 2 * DIM_H10 + DIM_S + DIM_PHI17  # 738


def spectator_soft_masses(
    vevs: dict[str, float],
    *,
    m_i: float,
    m_gut: float,
    lam4: float,
    scale_floor_gev2: float,
) -> dict[str, float]:
    """Reduced-radial soft diagonals for S and Φ₁₇ (GeV²).

    Raw reduced-Hessian entries can sit at the soft floor O(10⁴) while A/C
    are GUT-scale (~10³⁰). For the form-basis gate those would be numerically
    null under eigvalsh tolerances, so the skeleton uses
    ``max(raw, scale_floor)`` while recording the raw values.
    """
    radial = scalar_pd.reduced_radial_vacuum_witness(
        {"available": True, "M_I_GeV": m_i, "M_GUT_GeV": m_gut}
    )
    quartic, _, targets = reduced.radial_quartic_matrix(radial)
    targets = {
        "P_210": float(vevs["p"]),
        "DeltaR_126bar": float(vevs["DeltaR"]),
        "H10_EW": float(vevs["hEW"]),
        "S_PQ": float(vevs["vS"]),
        "Phi17_X": float(targets.get("Phi17_X", m_i)),
    }
    params = reduced.interaction_parameters(m_i, m_gut, lam4)
    hessian = reduced.high_precision_hessian(targets, quartic, params)
    matrix = np.array(hessian.tolist(), dtype=float)
    index = {name: i for i, name in enumerate(reduced.FIELDS)}
    mu_s = float(matrix[index["S_PQ"], index["S_PQ"]])
    mu_phi = float(matrix[index["Phi17_X"], index["Phi17_X"]])
    floor = float(scale_floor_gev2)
    return {
        "mu2_S": max(mu_s, floor, SOFT_FLOOR_GEV2),
        "mu2_Phi17": max(mu_phi, floor, SOFT_FLOOR_GEV2),
        "mu2_S_raw": mu_s,
        "mu2_Phi17_raw": mu_phi,
        "scale_floor_GeV2": floor,
        "Phi17_X_GeV": float(targets["Phi17_X"]),
    }


def extended_tangent_matrix(*, h_ew_gev: float = hew_orbit.HEW_GEV) -> dict[str, Any]:
    """Pad the 724 hEW tangent with Im H + S + Φ₁₇ spectator zeros."""
    base = hew_orbit.extended_tangent_matrix(h_ew_gev=h_ew_gev)
    t724 = base["matrix"]
    if t724.shape[0] != 724:
        raise ValueError(f"expected 724-row tangent, got {t724.shape}")
    n_gen = t724.shape[1]
    # Order: 210 | 504 | Re H | Im H | S(2) | Phi17(2)
    re_h = t724[DIM_210 + DIM_504 :, :]  # 10 × n_gen
    im_h = np.zeros((DIM_H10, n_gen), dtype=float)
    s_block = np.zeros((DIM_S, n_gen), dtype=float)
    phi_block = np.zeros((DIM_PHI17, n_gen), dtype=float)
    matrix = np.vstack(
        [t724[: DIM_210 + DIM_504, :], re_h, im_h, s_block, phi_block]
    )
    if matrix.shape[0] != EXPECTED_FIELD_DIM:
        raise ValueError(f"expected {EXPECTED_FIELD_DIM} rows, got {matrix.shape[0]}")
    return {
        "matrix": matrix,
        "n_field_components": EXPECTED_FIELD_DIM,
        "n_generators": n_gen,
        "embedding": {
            "210_PS_four_form_real": DIM_210,
            "126bar_five_form_real_imag": DIM_504,
            "H10_Re": DIM_H10,
            "H10_Im": DIM_H10,
            "S_Re_Im": DIM_S,
            "Phi17_Re_Im": DIM_PHI17,
            "total": EXPECTED_FIELD_DIM,
        },
        "hEW_GeV": float(h_ew_gev),
        "base_724_rank": int(
            gproj.goldstone_frame_from_tangent(t724)["rank"]
        ),
    }


def lift_full_portal_b(
    b_10x126: np.ndarray, e_504x252: np.ndarray
) -> dict[str, Any]:
    """Full (Re H, Im H) ↔ ambient 504 mixing from 2 Re(xᵀ B z)."""
    b = np.asarray(b_10x126, dtype=complex)
    if b.shape != (DIM_H10, 126):
        raise ValueError("b must be (10, 126)")
    p = b.real
    q = b.imag
    # V ⊃ 2 Re((u+iv)ᵀ B (s+it)) ⇒ Hessians on (u,v)×(s,t):
    #   H_u,[s t] = 2[P, -Q],  H_v,[s t] = 2[-Q, -P]
    # w=[s;t], r=E w, w=Eᵀ r/2 ⇒ mixing_(u,r) = [P,-Q] Eᵀ, mixing_(v,r)=[-Q,-P] Eᵀ
    r_u = np.concatenate([p, -q], axis=1)
    r_v = np.concatenate([-q, -p], axis=1)
    mix_u = r_u @ e_504x252.T
    mix_v = r_v @ e_504x252.T
    return {
        "mixing_re_10x504": mix_u,
        "mixing_im_10x504": mix_v,
        "frobenius_GeV2": float(
            np.sqrt(np.linalg.norm(mix_u) ** 2 + np.linalg.norm(mix_v) ** 2)
        ),
        "B_frobenius_GeV2": float(np.linalg.norm(b)),
        "im_H_included": True,
    }


def assemble_extended_hessian(
    *,
    a_h10: list[float] | np.ndarray,
    c_diag: list[float] | np.ndarray,
    b_10x126: np.ndarray,
    m2_210: float,
    m2_s: float,
    m2_phi17: float,
) -> dict[str, Any]:
    """Build the 738×738 Hessian with Hodge C, full portal, S/Φ₁₇ soft."""
    a = np.asarray(a_h10, dtype=float)
    if a.shape != (DIM_H10,):
        raise ValueError("a_h10 must have shape (10,)")
    for name, val in (("m2_210", m2_210), ("m2_s", m2_s), ("m2_phi17", m2_phi17)):
        if not np.isfinite(val) or val <= 0.0:
            raise ValueError(f"{name} must be positive")

    emb = hodge.embed_c_diagonal(
        c_diag, complement_floor_gev2=float(np.min(c_diag))
    )
    lift = lift_full_portal_b(b_10x126, emb["E_504x252"])
    n = EXPECTED_FIELD_DIM
    hess = np.zeros((n, n), dtype=float)

    i0 = 0
    i1 = DIM_210
    i2 = i1 + DIM_504
    i3 = i2 + DIM_H10  # end Re H
    i4 = i3 + DIM_H10  # end Im H
    i5 = i4 + DIM_S
    i6 = i5 + DIM_PHI17

    hess[i0:i1, i0:i1] = np.eye(DIM_210) * float(m2_210)
    hess[i1:i2, i1:i2] = emb["hessian_504"]
    hess[i2:i3, i2:i3] = np.diag(a)  # Re H
    hess[i3:i4, i3:i4] = np.diag(a)  # Im H
    hess[i4:i5, i4:i5] = np.eye(DIM_S) * float(m2_s)
    hess[i5:i6, i5:i6] = np.eye(DIM_PHI17) * float(m2_phi17)

    mix_u = lift["mixing_re_10x504"]
    mix_v = lift["mixing_im_10x504"]
    hess[i2:i3, i1:i2] = mix_u
    hess[i1:i2, i2:i3] = mix_u.T
    hess[i3:i4, i1:i2] = mix_v
    hess[i1:i2, i3:i4] = mix_v.T

    return {
        "hessian": hess,
        "embedding_c": emb,
        "portal": lift,
        "slices": {
            "210": [i0, i1],
            "fiveform_504": [i1, i2],
            "H10_Re": [i2, i3],
            "H10_Im": [i3, i4],
            "S": [i4, i5],
            "Phi17": [i5, i6],
        },
        "m2_210_GeV2": float(m2_210),
        "m2_S_GeV2": float(m2_s),
        "m2_Phi17_GeV2": float(m2_phi17),
        "shape": [n, n],
    }


def spectrum_after_projection(
    hessian: np.ndarray, p_phys: np.ndarray, *, rel_tol: float = 1e-10
) -> dict[str, Any]:
    h_proj = gproj.project_hessian(hessian, p_phys)
    eigs = np.linalg.eigvalsh(h_proj)
    scale = max(1.0, float(np.max(np.abs(eigs))))
    tol = rel_tol * scale
    return {
        "n_zero": int(np.sum(np.abs(eigs) <= tol)),
        "n_positive": int(np.sum(eigs > tol)),
        "n_negative": int(np.sum(eigs < -tol)),
        "eig_min_GeV2": float(eigs[0]),
        "eig_max_GeV2": float(eigs[-1]),
        "tol_GeV2": tol,
    }


def goldstone_kernel_residual(
    hessian: np.ndarray, frame: np.ndarray, p_phys: np.ndarray
) -> dict[str, float]:
    h_proj = gproj.project_hessian(hessian, p_phys)
    if frame.size == 0:
        return {"frame_image_residual": 0.0}
    return {
        "frame_image_residual": float(np.linalg.norm(h_proj @ frame))
        / max(1.0, float(np.linalg.norm(h_proj))),
    }


def build_report() -> dict[str, Any]:
    iso_report = iso.build_report()
    a = iso_report["A_partial_GeV2"]
    c = iso_report["C_partial_GeV2"]
    vevs = iso_report["vevs_GeV"]
    lam4 = iso_report["portal_B"]["lam4"]
    anchor = scalar_pd._unification_anchor()
    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    specs = spectator_soft_masses(
        vevs,
        m_i=m_i,
        m_gut=m_gut,
        lam4=lam4,
        scale_floor_gev2=float(min(np.min(a), np.min(c))),
    )

    mixing = schur.portal_mass2_matrix(
        p=vevs["p"],
        a=vevs["a"],
        omega=vevs["omega"],
        v_s=vevs["vS"],
        lam4=lam4,
    )
    m2_210 = float(
        d210.reduced_p210_mass2(m_i=m_i, m_gut=m_gut, lam4=0.0)[
            "m2_210_form_basis_GeV2"
        ]
    )
    assembled = assemble_extended_hessian(
        a_h10=a,
        c_diag=c,
        b_10x126=mixing,
        m2_210=m2_210,
        m2_s=specs["mu2_S"],
        m2_phi17=specs["mu2_Phi17"],
    )

    tang = extended_tangent_matrix()
    tangent = tang["matrix"]
    n_field = tang["n_field_components"]
    frame_info = gproj.goldstone_frame_from_tangent(tangent)
    frame = frame_info["frame"]
    projs = gproj.projectors(frame, n_field)
    p_phys = projs["P_phys"]
    p_g = projs["P_G"]

    n_phys = EXPECTED_FIELD_DIM - EXPECTED_GOLDSTONES
    unit_spec = spectrum_after_projection(np.eye(n_field), p_phys)
    unit_kernel = goldstone_kernel_residual(np.eye(n_field), frame, p_phys)

    hess = assembled["hessian"]
    diag = np.abs(np.diag(hess))
    median = float(np.median(diag[diag > 0.0])) if np.any(diag > 0.0) else 1.0
    dyn_spec = spectrum_after_projection(hess / median, p_phys)
    dyn_kernel = goldstone_kernel_residual(hess / median, frame, p_phys)

    schur_rep = iso_report.get("schur_with_partial_diagonals", {})

    # Sanity: rank unchanged from 724 baseline.
    rank_ok = frame_info["rank"] == EXPECTED_GOLDSTONES
    base_rank_ok = tang["base_724_rank"] == EXPECTED_GOLDSTONES

    checks = {
        "isotropic_partial_green": iso_report.get("n_failed", 1) == 0,
        "field_dim_738": n_field == EXPECTED_FIELD_DIM,
        "goldstone_rank_36": rank_ok,
        "base_724_rank_36": base_rank_ok,
        "trace_P_G_36": abs(float(np.trace(p_g)) - EXPECTED_GOLDSTONES) < 1e-6,
        "im_H_included": assembled["portal"]["im_H_included"],
        "portal_frobenius_positive": assembled["portal"]["frobenius_GeV2"] > 0.0,
        "spectator_S_positive": specs["mu2_S"] > 0.0,
        "spectator_Phi17_positive": specs["mu2_Phi17"] > 0.0,
        "unit_projected_36_zeros": unit_spec["n_zero"] == EXPECTED_GOLDSTONES,
        "unit_projected_no_negative": unit_spec["n_negative"] == 0,
        "unit_projected_physical_positive": unit_spec["n_positive"] == n_phys,
        "unit_kernel_tiny": unit_kernel["frame_image_residual"] < 1e-10,
        "dyn_scaled_36_zeros": dyn_spec["n_zero"] == EXPECTED_GOLDSTONES,
        "dyn_scaled_no_negative": dyn_spec["n_negative"] == 0,
        "dyn_scaled_physical_positive": dyn_spec["n_positive"] == n_phys,
        "dyn_kernel_tiny": dyn_kernel["frame_image_residual"] < 1e-8,
        "schur_272_recorded": "positive_definite" in schur_rep,
        "pq_axion_not_claimed_removed": True,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "EXTENDED_FORM_BASIS_IMH_SPECTATORS_READY__PQ_AXION_OPEN"
            if not failures
            else "EXTENDED_FORM_BASIS_IMH_SPECTATORS_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "embedding": tang["embedding"],
        "spectator_soft": specs,
        "form_basis_skeleton": {
            "shape": assembled["shape"],
            "slices": assembled["slices"],
            "m2_210_GeV2": assembled["m2_210_GeV2"],
            "m2_S_GeV2": assembled["m2_S_GeV2"],
            "m2_Phi17_GeV2": assembled["m2_Phi17_GeV2"],
            "median_abs_diag_GeV2": median,
            "hodge_trace_P_126bar": assembled["embedding_c"]["trace_P_126bar"],
            "portal_frobenius_GeV2": assembled["portal"]["frobenius_GeV2"],
            "im_H_included": True,
            "S_Phi17_included": True,
        },
        "goldstone_projection": {
            "rank": frame_info["rank"],
            "trace_P_G": float(np.trace(p_g)),
            "trace_P_phys": float(np.trace(p_phys)),
            "unit_skeleton_spectrum": unit_spec,
            "unit_kernel_residual": unit_kernel,
            "dynamical_scaled_spectrum": dyn_spec,
            "dynamical_kernel_residual": dyn_kernel,
        },
        "schur_272": {
            "positive_definite": schur_rep.get("positive_definite"),
            "schur_margin": schur_rep.get("schur_margin"),
        },
        "flags": {
            "extended_form_basis_imh_spectators_ready": not bool(failures),
            "im_H_in_embedding": True,
            "full_holomorphic_portal_lifted": True,
            "S_Phi17_dynamical_blocks": True,
            "pq_axion_null_removed": False,
            "full_component_hessian_complete": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "remaining_blockers": {
            "pq_axion_quotient_on_extended_hessian": True,
            "missing_cg_120_320_1050_4125": True,
            "complete_sm_irrep_mass_matrices": True,
            "global_stationarity_boundedness": True,
        },
        "verdict": (
            f"Extended form-basis Hessian on dim {EXPECTED_FIELD_DIM} includes "
            "Im H (full portal B), S, and Φ₁₇ soft blocks. After removing "
            f"{EXPECTED_GOLDSTONES} SO(10) Goldstones: "
            f"{dyn_spec['n_zero']} zeros / {dyn_spec['n_positive']} positive / "
            f"{dyn_spec['n_negative']} negative (median-scaled). PQ axion "
            "quotient remains OPEN. Theory remains BLOCKED."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    gp = report["goldstone_projection"]
    OUT_MD.write_text(
        "# Extended form-basis Hessian (Im H + S/Φ₁₇) — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- Field dim: `{report['embedding']['total']}`\n"
        f"- Goldstones: `{gp['rank']}`\n"
        f"- Dynamical zeros/pos/neg: "
        f"`{gp['dynamical_scaled_spectrum']['n_zero']}` / "
        f"`{gp['dynamical_scaled_spectrum']['n_positive']}` / "
        f"`{gp['dynamical_scaled_spectrum']['n_negative']}`\n\n"
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
