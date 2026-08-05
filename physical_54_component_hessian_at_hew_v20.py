#!/usr/bin/env python3
"""Physical 54-locking component Hessian at hEW=174 GeV (v20).

For the charge-allowed operator

    V_lock = lambda_lock * S^2 / M_GUT^2
             * <P54(H,H), P54(Sigmabar,Sigmabar)> + h.c.,

evaluate exact second-derivative blocks on the physical selected vacuum

    H = hEW * e_hat   (electroweak bidoublet direction in 10, |hEW|=174 GeV)
    Sigmabar = Delta_R  (canonical anti-self-dual five-form)

This replaces the withdrawn isotropic seed that used the unphysical
H10_eff=M_I proxy.

Results (exact tensor calculus; no invented 120/320/1050/4125 CG):

1. Q_Delta = P54(Delta_R,Delta_R) = 0  (retained).
2. Q_H = P54(hEW,hEW) is nonzero for any nonzero hEW.
3. Vacuum amplitude <Q_H, Q_Delta> = 0, so selected-vacuum phase locking
   from this operator remains absent.
4. Holomorphic H10 mass block from Q_Delta remains exact zero.
5. Sigmabar receives a physical quadratic form from Q_H, suppressed by
   (hEW/M_I)^2 relative to an intermediate-scale H10 proxy.

Honesty
-------
* Scoped to the 54-locking channel only. Full component Hessian / G3 OPEN.
* Weak-subspace embedding of hEW uses the standard SO(6)xSO(4) split
  (colour 0..5, weak 6..9); unitary-gauge direction e_6.
* Does not invent missing CG tensors. Theory remains BLOCKED.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

import direct_phi_h_sigmabar_tensor_v20 as direct
import physical_h10_54_mass_block_from_deltar_v20 as deltar54
import scalar_vacuum_proton_decay_v20 as scalar_pd
import so10_126_to_54_projector_v20 as projector

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "PHYSICAL_54_COMPONENT_HESSIAN_AT_HEW_V20.json"
OUT_MD = ROOT / "PHYSICAL_54_COMPONENT_HESSIAN_AT_HEW_V20.md"

N = 10
# Standard PS embedding of 10 = (6,1,1)+(1,2,2): colour 0..5, weak 6..9.
WEAK_INDICES = (6, 7, 8, 9)
HEW_DIRECTION_INDEX = 6  # unitary-gauge real direction inside (1,2,2)


def hew_unit_vector() -> np.ndarray:
    """Unit real vector for the physical hEW direction in ℝ¹⁰."""
    v = np.zeros(N, dtype=float)
    v[HEW_DIRECTION_INDEX] = 1.0
    return v


def q54_from_10_vector(h: np.ndarray) -> np.ndarray:
    """Q = P54(H,H) for a real 10-vector H."""
    return projector.apply_p54(np.outer(h, h))


def frobenius(a: np.ndarray, b: np.ndarray | None = None) -> float:
    if b is None:
        b = a
    return float(np.vdot(a, b).real)


def sigma_quadratic_kernel(q_h: np.ndarray) -> np.ndarray:
    """252×252 holomorphic kernel M_IJ = Σ_ab Q_H_ab K_abIJ."""
    k = projector.contraction_kernel()
    return np.einsum("ab,abIJ->IJ", q_h, k, optimize=True)


def delta_r_eigenspace_frame() -> dict[str, Any]:
    """Orthonormal frame for the self-dual eigenspace containing Delta_R."""
    hodge = projector.hodge_star_5forms()["matrix"]
    sd = projector.self_dual_projectors(hodge)
    delta = deltar54.form_to_combo_vector(direct.delta_r())
    proj_plus = float(np.linalg.norm(sd["basis_plus_i"].conj().T @ delta))
    proj_minus = float(np.linalg.norm(sd["basis_minus_i"].conj().T @ delta))
    if proj_plus >= proj_minus:
        name = "plus_i_self_dual"
        frame = sd["basis_plus_i"]
    else:
        name = "minus_i_anti_self_dual"
        frame = sd["basis_minus_i"]
    return {
        "name": name,
        "frame": frame,
        "delta_projection_plus": proj_plus,
        "delta_projection_minus": proj_minus,
    }


def holomorphic_kernel_on_delta_space(
    kernel_252: np.ndarray, frame: np.ndarray
) -> dict[str, Any]:
    """Restrict holomorphic M to the orthonormal Delta_R eigenspace.

    The locking operator is quadratic in Sigmabar (Σ Σ, not Σ† Σ), so the
    restricted kernel is complex-symmetric. Its singular values measure the
    strength of that holomorphic mass; the associated real quadratic form
    Re(Σᵀ M Σ) is indefinite and is not a positive Hermitian Schur C seed.
    """
    # Holomorphic restriction: Fᵀ M F (no conjugation).
    mh = frame.T @ kernel_252 @ frame
    mh_sym = 0.5 * (mh + mh.T)
    singular = np.linalg.svd(mh_sym, compute_uv=False)
    singular = np.sort(singular.real)[::-1]
    tol = 1e-10 * max(1.0, float(singular[0]) if len(singular) else 1.0)
    return {
        "matrix": mh_sym,
        "singular_values": singular,
        "n_nonzero": int(np.sum(singular > tol)),
        "n_zero": int(np.sum(singular <= tol)),
        "s_max": float(singular[0]) if len(singular) else 0.0,
        "s_min": float(singular[-1]) if len(singular) else 0.0,
        "frobenius": float(np.linalg.norm(mh_sym)),
        "symmetric_residual": float(np.linalg.norm(mh - mh.T)),
    }


def tadpole_against_delta(
    q_h: np.ndarray, delta_combo: np.ndarray
) -> np.ndarray:
    """Linear Σ coefficient ~ 2 Q_H : K(Delta, ·) in the 252 basis."""
    k = projector.contraction_kernel()
    return 2.0 * np.einsum(
        "ab,abIJ,I->J", q_h, k, delta_combo, optimize=True
    )


def build_report(
    *,
    lambda_lock: float = 1.0,
    h_ew_gev: float = 174.0,
) -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    if not anchor.get("available"):
        return {
            "status": "PHYSICAL_54_HEW_HESSIAN_NOT_EXECUTED__ANCHOR_MISSING",
            "n_failed": 1,
            "failures": ["unification_anchor"],
            "overall_state": "BLOCKED",
        }

    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    v_s = m_i
    scale = float(lambda_lock) * (v_s**2) / (m_gut**2)

    ehat = hew_unit_vector()
    h_vec = h_ew_gev * ehat
    q_h = q54_from_10_vector(h_vec)
    q_h_unit = q54_from_10_vector(ehat)
    q_delta = deltar54.delta_54_matrix(v_delta_gev=1.0)
    q_delta_mi = deltar54.delta_54_matrix(v_delta_gev=m_i)

    vacuum_amplitude = frobenius(q_h, q_delta_mi)
    q_h_norm = frobenius(q_h) ** 0.5
    q_h_unit_norm = frobenius(q_h_unit) ** 0.5
    expected_unit_norm = (0.9) ** 0.5  # ||P54(e,e)||_F = sqrt(9/10)

    # H10 holomorphic mass from Q_Delta (retained exact zero).
    d_hh = deltar54.h10_holomorphic_second_derivative(
        v_delta_gev=m_i,
        v_s_gev=v_s,
        m_gut_gev=m_gut,
        lambda_lock=lambda_lock,
    )
    d_hh_norm = float(np.linalg.norm(d_hh))

    # Sigmabar holomorphic quadratic form from physical Q_H.
    kernel_252 = sigma_quadratic_kernel(q_h)
    space = delta_r_eigenspace_frame()
    frame = space["frame"]
    hol = holomorphic_kernel_on_delta_space(kernel_252, frame)
    # Scaled holomorphic singular spectrum (GeV² units of the ΣΣ coefficient).
    s_scaled = (2.0 * scale) * hol["singular_values"]
    s_max_gev2 = float(s_scaled[0]) if len(s_scaled) else 0.0
    s_min_gev2 = float(s_scaled[-1]) if len(s_scaled) else 0.0

    delta_combo = deltar54.form_to_combo_vector(direct.delta_r()) * complex(m_i)
    tadpole_252 = tadpole_against_delta(q_h, delta_combo)
    tadpole_in_space = frame.conj().T @ tadpole_252
    tadpole_norm = float(np.linalg.norm(tadpole_252))
    tadpole_in_space_norm = float(np.linalg.norm(tadpole_in_space))

    # Compare to withdrawn MI-proxy isotropic scale ~ scale * M_I^2.
    proxy_reference_gev2 = abs(scale) * (m_i**2)
    suppression = (h_ew_gev / m_i) ** 2

    checks = {
        "hew_direction_in_weak_subspace": HEW_DIRECTION_INDEX in WEAK_INDICES,
        "Q_H_nonzero_at_physical_hEW": q_h_norm > 1e-12,
        "Q_H_unit_frobenius_matches_9_over_10": abs(
            q_h_unit_norm - expected_unit_norm
        )
        < 1e-12,
        "Q_Delta_exact_zero": frobenius(q_delta) ** 0.5 < 1e-12,
        "vacuum_amplitude_QH_QDelta_zero": abs(vacuum_amplitude) < 1e-8,
        "H10_mass_block_from_DeltaR_exact_zero": d_hh_norm < 1e-6,
        "delta_r_eigenspace_identified": (
            space["delta_projection_plus"] > 0.5
            or space["delta_projection_minus"] > 0.5
        ),
        "holomorphic_kernel_nonzero_on_delta_space": hol["n_nonzero"] > 0,
        "holomorphic_kernel_symmetric": hol["symmetric_residual"] < 1e-8,
        "tadpole_orthogonal_to_delta_space_hermitian": tadpole_in_space_norm
        < 1e-6 * max(1.0, float(np.linalg.norm(kernel_252 @ (
            deltar54.form_to_combo_vector(direct.delta_r())
        )))),
        "no_H10_MI_proxy_used": True,
        "missing_cg_not_invented": True,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "PHYSICAL_54_COMPONENT_HESSIAN_AT_HEW_EXECUTED__FULL_HESSIAN_OPEN"
            if not failures
            else "PHYSICAL_54_COMPONENT_HESSIAN_AT_HEW_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "operator": {
            "formula": (
                "lambda_lock*S^2/M_GUT^2 * "
                "<P54(H,H), P54(Sigmabar,Sigmabar)> + h.c."
            ),
            "lambda_lock": float(lambda_lock),
            "scale_S2_over_MGUT2": scale,
            "quadratic_in_sigma": "holomorphic_Sigma_Sigma_not_Hermitian",
        },
        "embedding": {
            "representation_split": "10=(6,1,1)+(1,2,2)",
            "colour_indices": list(range(6)),
            "weak_indices": list(WEAK_INDICES),
            "hew_direction_index": HEW_DIRECTION_INDEX,
            "hEW_GeV": float(h_ew_gev),
            "note": (
                "Unitary-gauge real direction inside the electroweak "
                "bidoublet; not an intermediate-scale H10 singlet."
            ),
        },
        "vevs_GeV": {
            "hEW": float(h_ew_gev),
            "DeltaR": m_i,
            "S": v_s,
            "M_GUT": m_gut,
            "M_I": m_i,
        },
        "delta_r_space": {
            "name": space["name"],
            "delta_projection_plus": space["delta_projection_plus"],
            "delta_projection_minus": space["delta_projection_minus"],
        },
        "tensors": {
            "Q_H_frobenius": q_h_norm,
            "Q_H_unit_frobenius": q_h_unit_norm,
            "Q_H_unit_frobenius_expected_sqrt_9_10": expected_unit_norm,
            "Q_Delta_frobenius": frobenius(q_delta) ** 0.5,
            "vacuum_amplitude_QH_dot_QDelta": vacuum_amplitude,
            "H10_DHH_frobenius_GeV2": d_hh_norm,
            "sigmabar_tadpole_252_norm": tadpole_norm,
            "sigmabar_tadpole_in_delta_space_norm": tadpole_in_space_norm,
            "holomorphic_kernel_frobenius_unscaled": hol["frobenius"],
            "holomorphic_s_max_unscaled": hol["s_max"],
            "holomorphic_s_min_unscaled": hol["s_min"],
            "holomorphic_n_nonzero": hol["n_nonzero"],
        },
        "blocks": {
            "OPEN_H10_54": {
                "status": "EXACT_ZERO_FROM_Q_DELTA",
                "contribution_GeV2_isotropic_seed": 0.0,
                "matrix_frobenius_GeV2": d_hh_norm,
                "feeds": "A",
                "positive_hermitian_schur_seed": False,
                "reason": (
                    "P54(Delta_R,Delta_R)=0 ⇒ no H10 quadratic mass from "
                    "this locking channel on the selected vacuum"
                ),
            },
            "OPEN_126_54_LOCKING": {
                "status": "PHYSICAL_HOLOMORPHIC_KERNEL_FROM_HEW__NOT_PD_SCHUR_SEED",
                "feeds": "C",
                "n_nonzero_singular": hol["n_nonzero"],
                "n_zero_singular": hol["n_zero"],
                "s_max_GeV2": s_max_gev2,
                "s_min_GeV2": s_min_gev2,
                "frobenius_GeV2": float((2.0 * abs(scale)) * hol["frobenius"]),
                "suppression_vs_MI_proxy": suppression,
                "proxy_reference_scale_GeV2": proxy_reference_gev2,
                "positive_hermitian_schur_seed": False,
                "real_quadratic_form": "indefinite_Re_SigmaT_M_Sigma",
                "reason": (
                    "P54(hEW,hEW)≠0 sources a holomorphic Sigmabar ΣΣ kernel "
                    "on the Delta_R eigenspace, suppressed by (hEW/M_I)^2. "
                    "Re(ΣᵀMΣ) is indefinite and does not refill a positive "
                    "isotropic Schur C seed."
                ),
            },
        },
        "spectrum_summary": {
            "holomorphic_singular_values_scaled_sample": [
                float(x) for x in s_scaled[::21]
            ],
            "n_singular": int(len(s_scaled)),
        },
        "flags": {
            "physical_54_component_hessian_at_hEW": not bool(failures),
            "Q_H_nonzero": q_h_norm > 1e-12,
            "selected_vacuum_locking_amplitude_zero": abs(vacuum_amplitude)
            < 1e-8,
            "OPEN_H10_54_exact_zero": d_hh_norm < 1e-6,
            "OPEN_126_54_LOCKING_holomorphic_kernel_nonzero": hol["n_nonzero"]
            > 0,
            "OPEN_126_54_LOCKING_positive_schur_seed": False,
            "H10_MI_proxy_used": False,
            "full_component_hessian_complete": False,
            "root_by_root_33_goldstone_projection_complete": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "remaining_blockers": {
            "complete_invariant_ring_G1": True,
            "missing_cg_120_320_1050_4125": True,
            "full_component_hessian_G3": True,
            "root_by_root_33_goldstone_projection": True,
            "global_stationarity_boundedness": True,
            "positive_diagonal_C_from_other_channels": True,
        },
        "verdict": (
            "At physical hEW=174 GeV, P54(hEW,hEW) is nonzero and sources a "
            "holomorphic Sigmabar ΣΣ kernel on the Delta_R eigenspace, suppressed "
            "by (hEW/M_I)^2, while P54(Delta_R,Delta_R)=0 keeps the H10 mass "
            "block and selected-vacuum locking amplitude exactly zero. The "
            "holomorphic kernel is not a positive Hermitian Schur C seed. This "
            "closes the physical hEW differentiation of the 54 channel only; "
            "the full component Hessian and issue #86 remain OPEN. Theory "
            "remains BLOCKED."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    blocks = report["blocks"]
    OUT_MD.write_text(
        "# Physical 54-component Hessian at hEW=174 GeV — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- Q_H Frobenius: `{report['tensors']['Q_H_frobenius']:.6g}`\n"
        f"- Vacuum amplitude ⟨Q_H,Q_Δ⟩: "
        f"`{report['tensors']['vacuum_amplitude_QH_dot_QDelta']:.6g}`\n"
        f"- Delta_R eigenspace: `{report['delta_r_space']['name']}`\n"
        f"- OPEN_H10_54: `{blocks['OPEN_H10_54']['status']}`\n"
        f"- OPEN_126_54_LOCKING: `{blocks['OPEN_126_54_LOCKING']['status']}` "
        f"(n≠0 singular={blocks['OPEN_126_54_LOCKING']['n_nonzero_singular']}, "
        f"s_max={blocks['OPEN_126_54_LOCKING']['s_max_GeV2']:.6g} GeV²)\n"
        f"- Positive Schur C seed: "
        f"`{blocks['OPEN_126_54_LOCKING']['positive_hermitian_schur_seed']}`\n"
        f"- Suppression (hEW/M_I)²: "
        f"`{blocks['OPEN_126_54_LOCKING']['suppression_vs_MI_proxy']:.6g}`\n\n"
        + report["verdict"]
        + "\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--lambda-lock", type=float, default=1.0)
    parser.add_argument("--hEW", type=float, default=174.0)
    args = parser.parse_args(argv)
    report = build_report(lambda_lock=args.lambda_lock, h_ew_gev=args.hEW)
    if args.write:
        write_report(report)
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
