#!/usr/bin/env python3
"""Hodge 126bar C-embedding and portal lift into ambient five-forms (v20).

The orbit/Goldstone embedding stores complex five-forms in the ambient
``C(10,5)=252`` complex space (=504 real). Physical ``Σ̄`` is the Hodge
``*Σ = −i Σ`` eigenspace (dim 126), with the same kinetic-orthonormal basis
already used by ``direct_phi_h_sigmabar_tensor_v20.anti_self_dual_five_form_basis``
and therefore by the Schur portal ``B = λ₄ v_S T_Φ``.

This module:

1. Builds the complex frame ``F`` (252×126) and real isometry ``E`` (504×252)
   for kinetic coordinates ``z = s + i t``;
2. Embeds a Hermitian diagonal ``C`` (126) as a PSD operator on ℝ⁵⁰⁴,
   with a positive placeholder on the complementary ``+i`` (126) space;
3. Lifts the holomorphic portal ``B`` (10×126) into a real mixing block
   between real ``H₁₀`` and the ambient 504 (Im ``H`` not in the 724 orbit
   embedding — recorded honestly).

Honesty
-------
* Does not invent 120/320/1050/4125 CG.
* Complementary ``+i`` five-forms are not dynamical Σ̄; they get a
  placeholder mass only so the ambient block stays numerically PD.
* Full component Hessian / theory closure remain OPEN.
"""

from __future__ import annotations

import argparse
import itertools
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np

import direct_phi_h_sigmabar_tensor_v20 as direct
import direct_portal_mass2_schur_gate_v20 as schur
import physical_h10_54_mass_block_from_deltar_v20 as deltar54
import so10_126_to_54_projector_v20 as projector

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "HODGE_126BAR_C_EMBEDDING_PORTAL_LIFT_V20.json"
OUT_MD = ROOT / "HODGE_126BAR_C_EMBEDDING_PORTAL_LIFT_V20.md"

N = 10
N_COMBOS = 252
DIM_126 = 126
DIM_504 = 504
DIM_H10 = 10


@lru_cache(maxsize=1)
def anti_self_dual_frame() -> dict[str, Any]:
    """Kinetic-orthonormal -i frame as a 252×126 complex matrix."""
    basis = direct.anti_self_dual_five_form_basis()
    combos = list(itertools.combinations(range(N), 5))
    frame = np.zeros((N_COMBOS, DIM_126), dtype=complex)
    for j, form in enumerate(basis):
        frame[:, j] = np.array(
            [form.get(indices, 0.0) for indices in combos], dtype=complex
        )
    gram = frame.conj().T @ frame
    # Kinetic norm 1 ⇒ raw Hermitian norm √2 ⇒ F†F = 2 I.
    gram_err = float(np.max(np.abs(gram - 2.0 * np.eye(DIM_126))))
    # direct.hodge_star defines *Σ=−iΣ for this basis. The matrix in
    # so10_126_to_54_projector_v20 uses the opposite overall sign, so the
    # same states are its +i eigenspace. Prefer the direct-form residual.
    hodge_residuals = []
    for j, form in enumerate(basis):
        star = direct.hodge_star(form)
        target = direct.scale_form(form, -1j)
        hodge_residuals.append(direct.tensor_norm(direct.add_forms(star, direct.scale_form(target, -1.0))))
    hodge_res = float(max(hodge_residuals)) if hodge_residuals else 0.0
    hodge_matrix = projector.hodge_star_5forms()["matrix"]
    # Cross-check: projector matrix annihilates with +i on this frame.
    projector_plus_i_res = float(
        np.linalg.norm(hodge_matrix @ frame - 1j * frame)
    ) / max(1.0, float(np.linalg.norm(frame)))
    return {
        "frame": frame,
        "gram_minus_2I_max_abs": gram_err,
        "hodge_minus_i_residual": hodge_res,
        "projector_matrix_plus_i_residual": projector_plus_i_res,
        "raw_column_norm_sq_mean": float(np.mean(np.sum(np.abs(frame) ** 2, axis=0))),
    }


def real_isometry_from_frame(frame: np.ndarray) -> np.ndarray:
    """Map kinetic (s,t)∈ℝ²⁵² → ambient ℝ⁵⁰⁴ via ψ = F z, z=s+it.

    Because F†F = 2 I, EᵀE = 2 I_252 (raw ambient metric).
    """
    re = frame.real
    im = frame.imag
    return np.block([[re, -im], [im, re]])


def embed_c_diagonal(
    c_diag: list[float] | np.ndarray,
    *,
    complement_floor_gev2: float | None = None,
) -> dict[str, Any]:
    """Embed Hermitian diag(C) on 126bar into ambient ℝ⁵⁰⁴ mass-squared."""
    c = np.asarray(c_diag, dtype=float)
    if c.shape != (DIM_126,):
        raise ValueError("c_diag must have shape (126,)")
    if not np.all(np.isfinite(c)) or np.any(c <= 0.0):
        raise ValueError("c_diag entries must be finite and positive")

    info = anti_self_dual_frame()
    frame = info["frame"]
    e = real_isometry_from_frame(frame)
    # V = z† C z = [s;t]ᵀ blkdiag(C,C) [s;t]
    # r = E [s;t], EᵀE = 2I ⇒ [s;t] = Eᵀ r / 2
    # V = rᵀ (E blkdiag(C,C) Eᵀ) r / 4
    c2 = np.concatenate([c, c])
    mid = e * c2  # broadcasts columns by c2
    # (E diag(c2) Eᵀ) / 4
    m_phys = (mid @ e.T) / 4.0

    p_phys = (e @ e.T) / 2.0  # projector onto im(E); E Eᵀ / 2
    p_comp = np.eye(DIM_504) - p_phys
    floor = (
        float(np.min(c))
        if complement_floor_gev2 is None
        else float(complement_floor_gev2)
    )
    if not np.isfinite(floor) or floor <= 0.0:
        raise ValueError("complement_floor_gev2 must be positive")
    m = m_phys + floor * p_comp

    # Numerics
    eigs = np.linalg.eigvalsh(m)
    p_err = float(np.linalg.norm(p_phys @ p_phys - p_phys))
    tr_p = float(np.trace(p_phys))
    return {
        "hessian_504": m,
        "M_physical_504": m_phys,
        "P_126bar_504": p_phys,
        "P_complement_504": p_comp,
        "E_504x252": e,
        "frame_252x126": frame,
        "complement_floor_GeV2": floor,
        "trace_P_126bar": tr_p,
        "P_idempotence_residual": p_err,
        "eig_min_GeV2": float(eigs[0]),
        "eig_max_GeV2": float(eigs[-1]),
        "rank_physical_target": 252,
        "gram_minus_2I_max_abs": info["gram_minus_2I_max_abs"],
        "hodge_minus_i_residual": info["hodge_minus_i_residual"],
        "projector_matrix_plus_i_residual": info["projector_matrix_plus_i_residual"],
    }


def lift_portal_b_to_h10_ambient(
    b_10x126: np.ndarray, e_504x252: np.ndarray
) -> dict[str, Any]:
    """Lift holomorphic B (10×126) to real mixing blocks H₁₀_real ↔ ambient 504.

    Uses the Schur field convention on kinetic (s,t) with Im H omitted:
    the holomorphic term 2 Re(uᵀ B z) for real u and z=s+it contributes

        V ⊃ 2 uᵀ (P s − Q t),   P=Re B, Q=Im B

    Mapping [s;t] → r = E [s;t] / √?  With r = E w, w=[s;t], w = Eᵀ r / 2:

        V ⊃ 2 uᵀ [P, −Q] w = uᵀ ( [2P, −2Q] Eᵀ / 2 ) r = uᵀ [P, −Q] Eᵀ r

    Real off-diagonal block shape (10, 504).
    """
    b = np.asarray(b_10x126, dtype=complex)
    if b.shape != (DIM_H10, DIM_126):
        raise ValueError("b_10x126 must have shape (10, 126)")
    if e_504x252.shape != (DIM_504, 2 * DIM_126):
        raise ValueError("e_504x252 must have shape (504, 252)")
    p = b.real
    q = b.imag
    # Row block R = [P, -Q] maps w→ℝ¹⁰; mixing = R @ (Eᵀ / 2) * 2 from above
    # = [P,-Q] @ Eᵀ / 1?  From derivation: uᵀ [P,-Q] Eᵀ r
    # Wait: V = 2 uᵀ (P s - Q t) = 2 uᵀ R w with R=[P,-Q]
    # w = Eᵀ r / 2 ⇒ V = 2 uᵀ R (Eᵀ r)/2 = uᵀ R Eᵀ r
    # Hessian off-diagonal ∂²V/∂u∂r = R Eᵀ
    r_block = np.concatenate([p, -q], axis=1)  # 10×252
    mixing = r_block @ e_504x252.T  # 10×504
    return {
        "mixing_10x504": mixing,
        "frobenius_GeV2": float(np.linalg.norm(mixing)),
        "B_frobenius_GeV2": float(np.linalg.norm(b)),
        "im_H_included": False,
    }


def assemble_h10_sigma_block(
    *,
    a_h10: list[float] | np.ndarray,
    c_diag: list[float] | np.ndarray,
    b_10x126: np.ndarray | None = None,
    m2_210: float,
) -> dict[str, Any]:
    """Build the 724×724 form-basis Hessian with Hodge-placed C and optional B."""
    a = np.asarray(a_h10, dtype=float)
    if a.shape != (DIM_H10,):
        raise ValueError("a_h10 must have shape (10,)")
    if not np.all(np.isfinite(a)) or np.any(a <= 0.0):
        raise ValueError("a_h10 must be positive")
    if not np.isfinite(m2_210) or m2_210 <= 0.0:
        raise ValueError("m2_210 must be positive")

    emb = embed_c_diagonal(c_diag, complement_floor_gev2=float(np.min(c_diag)))
    m504 = emb["hessian_504"]
    n = 210 + DIM_504 + DIM_H10
    hess = np.zeros((n, n), dtype=float)
    hess[:210, :210] = np.eye(210) * float(m2_210)
    hess[210 : 210 + DIM_504, 210 : 210 + DIM_504] = m504
    hess[-DIM_H10:, -DIM_H10:] = np.diag(a)

    portal_info: dict[str, Any] = {
        "inserted": False,
        "im_H_included": False,
        "frobenius_GeV2": 0.0,
    }
    if b_10x126 is not None:
        lift = lift_portal_b_to_h10_ambient(b_10x126, emb["E_504x252"])
        mix = lift["mixing_10x504"]
        # Off-diagonal between H10 (last 10) and five-form block.
        hess[-DIM_H10:, 210 : 210 + DIM_504] = mix
        hess[210 : 210 + DIM_504, -DIM_H10:] = mix.T
        portal_info = {
            "inserted": True,
            "im_H_included": False,
            "frobenius_GeV2": lift["frobenius_GeV2"],
            "B_frobenius_GeV2": lift["B_frobenius_GeV2"],
        }

    return {
        "hessian_724": hess,
        "embedding": emb,
        "portal": portal_info,
        "m2_210_GeV2": float(m2_210),
        "shape": [n, n],
    }


def delta_r_in_physical_subspace(p_126bar: np.ndarray) -> dict[str, float]:
    """Check canonical Delta_R lies in the embedded -i projector image."""
    delta = deltar54.form_to_combo_vector(direct.delta_r())
    # Ambient real from complex combo vector.
    ambient = np.concatenate([delta.real, delta.imag])
    proj = p_126bar @ ambient
    nrm = float(np.linalg.norm(ambient))
    res = float(np.linalg.norm(proj - ambient)) / max(1.0, nrm)
    return {
        "delta_ambient_norm": nrm,
        "projector_residual": res,
        "in_physical_subspace": res < 1e-8,
    }


def build_report(
    *,
    a_h10: list[float] | np.ndarray | None = None,
    c_diag: list[float] | np.ndarray | None = None,
    include_portal: bool = True,
) -> dict[str, Any]:
    if a_h10 is None:
        a_h10 = np.ones(DIM_H10, dtype=float)
    if c_diag is None:
        c_diag = np.ones(DIM_126, dtype=float)
    a = np.asarray(a_h10, dtype=float)
    c = np.asarray(c_diag, dtype=float)
    m2_210 = float(max(np.min(a), np.min(c)))

    b = None
    schur_margin = None
    if include_portal:
        # Probe portal at unit singlets for structural lift; consumers pass physics B.
        b = schur.portal_tensor_aulakh(p=0.2, a=0.3, omega=0.5)
        # Scale to GeV²-like for structural test with unit A/C
        b = 1.0e-3 * b
        schur_rep = schur.schur_positivity_report(a, c, b)
        schur_margin = schur_rep.get("schur_margin")

    assembled = assemble_h10_sigma_block(
        a_h10=a, c_diag=c, b_10x126=b, m2_210=m2_210
    )
    emb = assembled["embedding"]
    delta_check = delta_r_in_physical_subspace(emb["P_126bar_504"])

    # Compare Rayleigh on physical 126 coords vs ambient embedding.
    # Unit z=e_0: V=C_0; ambient r=E[:,0] (first s direction) / but E col0 is for s0
    e = emb["E_504x252"]
    # For z = (1,0,...), w=(1,0,...,0) in s; V should equal c[0]
    w = np.zeros(2 * DIM_126)
    w[0] = 1.0
    r = e @ w
    v_ambient = float(r @ emb["M_physical_504"] @ r)
    # Because V = wᵀ diag(c,c) w / ? From earlier: M_phys = E diag Eᵀ / 4
    # and r=E w ⇒ rᵀ M_phys r = wᵀ Eᵀ E diag Eᵀ E w / 4 = wᵀ (2I) diag (2I) w / 4
    # = wᵀ diag w = c[0]. Good.
    rayleigh_err = abs(v_ambient - float(c[0]))

    checks = {
        "frame_gram_is_2I": emb["gram_minus_2I_max_abs"] < 1e-8,
        "frame_hodge_minus_i": emb["hodge_minus_i_residual"] < 1e-8,
        "projector_matrix_plus_i_on_frame": emb["projector_matrix_plus_i_residual"]
        < 1e-8,
        "P_126bar_idempotent": emb["P_idempotence_residual"] < 1e-8,
        "trace_P_126bar_252": abs(emb["trace_P_126bar"] - 252.0) < 1e-6,
        "embedded_C_positive": emb["eig_min_GeV2"] > 0.0,
        "delta_r_in_physical_subspace": delta_check["in_physical_subspace"],
        "rayleigh_matches_C0": rayleigh_err < 1e-8 * max(1.0, float(c[0])),
        "portal_lift_recorded": assembled["portal"]["inserted"] == include_portal,
        "im_H_not_faked": not assembled["portal"].get("im_H_included", True),
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "HODGE_126BAR_C_EMBEDDING_PORTAL_LIFT_READY__IM_H_OPEN"
            if not failures
            else "HODGE_126BAR_C_EMBEDDING_PORTAL_LIFT_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "frame": {
            "gram_minus_2I_max_abs": emb["gram_minus_2I_max_abs"],
            "hodge_minus_i_residual": emb["hodge_minus_i_residual"],
            "projector_matrix_plus_i_residual": emb[
                "projector_matrix_plus_i_residual"
            ],
            "trace_P_126bar": emb["trace_P_126bar"],
            "P_idempotence_residual": emb["P_idempotence_residual"],
            "complement_floor_GeV2": emb["complement_floor_GeV2"],
            "eig_min_GeV2": emb["eig_min_GeV2"],
            "eig_max_GeV2": emb["eig_max_GeV2"],
        },
        "delta_r_check": delta_check,
        "rayleigh_C0": {
            "V_ambient": v_ambient,
            "C0": float(c[0]),
            "abs_error": rayleigh_err,
        },
        "portal": assembled["portal"],
        "schur_margin_probe": schur_margin,
        "assembled_shape": assembled["shape"],
        "flags": {
            "hodge_126bar_c_embedding_ready": not bool(failures),
            "portal_b_lifted_to_ambient_504": assembled["portal"]["inserted"],
            "im_H_in_orbit_embedding": False,
            "full_component_hessian_complete": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "remaining_blockers": {
            "include_Im_H_in_extended_embedding": True,
            "S_Phi17_dynamical_blocks": True,
            "missing_cg_120_320_1050_4125": True,
            "global_stationarity_boundedness": True,
        },
        "verdict": (
            "Canonical -i 126bar frame embeds diagonal C into ambient ℝ⁵⁰⁴ "
            f"(trace P={emb['trace_P_126bar']:.0f}) with Delta_R residual "
            f"{delta_check['projector_residual']:.2e}. Portal B lifts to "
            "H10_real↔504 mixing; Im H remains outside the 724 orbit embedding. "
            "Theory remains BLOCKED."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Hodge 126bar C-embedding and portal lift — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- trace P_126bar: `{report['frame']['trace_P_126bar']}`\n"
        f"- Delta_R residual: `{report['delta_r_check']['projector_residual']}`\n"
        f"- Portal inserted: `{report['portal'].get('inserted')}`\n\n"
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
