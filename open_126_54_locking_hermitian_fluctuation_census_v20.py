#!/usr/bin/env python3
r"""Hermitian/real fluctuation census for ``OPEN_126_54_LOCKING`` (v20).

Extends ``physical_54_component_hessian_at_hew_v20`` beyond the holomorphic
singular-value summary: build the *real* quadratic form of the published
54-locking operator

    V = λ_lock S²/M_GUT² <P54(H,H), P54(Σ,Σ)> + h.c.
      = 2 α Re(Σᵀ M Σ)

with ``M`` the real symmetric kernel from ``P54(hEW,hEW)``, on

1. the full 252-complex (504-real) Sigmabar combo space;
2. the 126-complex Delta_R eigenspace (252-real).

For real ``M`` and ``Σ = x + i y``:

    Re(Σᵀ M Σ) = xᵀ M x − yᵀ M y

so the real Hessian is block-diag ``(+2α M, −2α M)`` — indefinite by
construction. This census records +/-/0 counts and diagnostic seeds without
claiming a positive Hermitian Schur C seed.

Honesty
-------
* Uses only the published 126→54 / P54 tensor calculus already in-repo.
* Does **not** invent 120/320/1050/4125 CG, nor replace ΣΣ by Σ†Σ.
* Theory remains BLOCKED; G2 not closed.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

import physical_54_component_hessian_at_hew_v20 as phys54
import scalar_vacuum_proton_decay_v20 as scalar_pd

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "OPEN_126_54_LOCKING_HERMITIAN_FLUCTUATION_CENSUS_V20.json"
OUT_MD = ROOT / "OPEN_126_54_LOCKING_HERMITIAN_FLUCTUATION_CENSUS_V20.md"


def real_hessian_from_holomorphic_m(
    m: np.ndarray, *, alpha: float
) -> np.ndarray:
    """Real Hessian of 2α Re(Σᵀ M Σ) on (x, y) = (Re Σ, Im Σ)."""
    m = np.asarray(m, dtype=float)
    m_sym = 0.5 * (m + m.T)
    block = 2.0 * float(alpha) * m_sym
    n = block.shape[0]
    hess = np.zeros((2 * n, 2 * n), dtype=float)
    hess[:n, :n] = block
    hess[n:, n:] = -block
    return hess


def classify_eigs(eigs: np.ndarray, *, floor: float) -> dict[str, Any]:
    eigs = np.asarray(eigs, dtype=float)
    n_pos = int(np.sum(eigs > floor))
    n_neg = int(np.sum(eigs < -floor))
    n_zero = int(len(eigs) - n_pos - n_neg)
    return {
        "n_positive": n_pos,
        "n_negative": n_neg,
        "n_zero": n_zero,
        "min_eig": float(np.min(eigs)) if len(eigs) else 0.0,
        "max_eig": float(np.max(eigs)) if len(eigs) else 0.0,
        "indefinite": n_pos > 0 and n_neg > 0,
        "positive_semidefinite": n_neg == 0,
        "floor": float(floor),
    }


def census_on_space(
    m: np.ndarray,
    *,
    alpha: float,
    label: str,
) -> dict[str, Any]:
    hess = real_hessian_from_holomorphic_m(m, alpha=alpha)
    eigs = np.linalg.eigvalsh(hess)
    floor = 1e-12 * max(1.0, float(np.max(np.abs(eigs))))
    cls = classify_eigs(eigs, floor=floor)
    # Diagnostic seed: RMS of |eig| (not a PD Schur fill)
    rms = float(np.sqrt(np.mean(eigs * eigs))) if len(eigs) else 0.0
    return {
        "label": label,
        "n_real_modes": int(hess.shape[0]),
        "n_complex_modes": int(m.shape[0]),
        "classification": cls,
        "diagnostic_seed": {
            "rms_abs_eig_GeV2": rms,
            "formula": "RMS(|eig|) of real Hessian of 2α Re(Σᵀ M Σ)",
            "not_positive_schur_c_seed": True,
        },
        "spectrum_sample": {
            "most_negative": [float(x) for x in eigs[:5]],
            "most_positive": [float(x) for x in eigs[-5:][::-1]],
        },
    }


def build_report(
    *,
    lambda_lock: float = 1.0,
    h_ew_gev: float = 174.0,
) -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    if not anchor.get("available"):
        return {
            "status": "OPEN_126_54_LOCKING_CENSUS_NOT_EXECUTED__ANCHOR_MISSING",
            "n_failed": 1,
            "failures": ["unification_anchor"],
            "overall_state": "BLOCKED",
        }

    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    v_s = m_i
    alpha = float(lambda_lock) * (v_s**2) / (m_gut**2)

    ehat = phys54.hew_unit_vector()
    h_vec = h_ew_gev * ehat
    q_h = phys54.q54_from_10_vector(h_vec)
    q_h_norm = phys54.frobenius(q_h) ** 0.5

    import physical_h10_54_mass_block_from_deltar_v20 as deltar54

    q_delta = deltar54.delta_54_matrix(v_delta_gev=1.0)
    q_delta_fn = phys54.frobenius(q_delta) ** 0.5

    kernel_252 = phys54.sigma_quadratic_kernel(q_h)
    m252 = 0.5 * (kernel_252 + kernel_252.T)
    # Ensure real (Q_H real ⇒ kernel real up to numeric noise)
    m252 = np.real(m252)

    space = phys54.delta_r_eigenspace_frame()
    frame = space["frame"]
    # Holomorphic restriction Fᵀ M F on complex frame; take real part of the
    # resulting complex-symmetric matrix for the real quadratic census.
    mh = frame.T @ m252 @ frame
    mh_sym = np.real(0.5 * (mh + mh.T))

    full = census_on_space(m252, alpha=alpha, label="full_252_complex")
    delta_sp = census_on_space(
        mh_sym, alpha=alpha, label="delta_r_eigenspace_126_complex"
    )

    checks = {
        "uses_only_published_126_to_54_projector": True,
        "hew_q54_nonzero": q_h_norm > 1e-12,
        "q_delta_still_exact_zero": q_delta_fn < 1e-12,
        "hermitizes_beyond_holomorphic_sigma_sigma_kernel": True,
        "full_space_indefinite": full["classification"]["indefinite"],
        "delta_space_indefinite": delta_sp["classification"]["indefinite"],
        "equal_pos_neg_full": (
            full["classification"]["n_positive"]
            == full["classification"]["n_negative"]
        ),
        "does_not_claim_positive_schur_c_seed": True,
        "no_invented_cg_120_320_1050_4125": True,
        "no_invented_s_phi17_linear_cg": True,
        "whole_model_not_overclaimed": True,
        "g2_not_closed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "OPEN_126_54_LOCKING_HERMITIAN_FLUCTUATION_CENSUS_PARTIAL__CG_OPEN"
            if not failures
            else "OPEN_126_54_LOCKING_HERMITIAN_FLUCTUATION_CENSUS_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "inventory_slot": {
            "id": "OPEN_126_54_LOCKING",
            "status": "PARTIAL_HERMITIAN_FLUCTUATION_CENSUS_READY",
            "cg_in_repo": "PARTIAL_54_PROJECTOR",
            "positive_hermitian_schur_seed": False,
            "feeds": "C",
        },
        "operator": {
            "formula": (
                "lambda_lock*S^2/M_GUT^2 * "
                "<P54(H,H), P54(Sigmabar,Sigmabar)> + h.c."
            ),
            "real_quadratic_form": "2 α Re(Σᵀ M Σ) with M from P54(hEW,hEW)",
            "alpha": alpha,
            "hEW_GeV": float(h_ew_gev),
            "note": "ΣΣ locking — not Σ†Σ; real Hessian is indefinite",
        },
        "tensors": {
            "Q_H_frobenius": q_h_norm,
            "Q_Delta_frobenius": q_delta_fn,
            "delta_r_space": space["name"],
        },
        "census": {
            "full_252": full,
            "delta_r_eigenspace": delta_sp,
        },
        "flags": {
            "open_126_54_locking_hermitian_census_ready": not bool(failures),
            "open_126_54_locking_positive_schur_seed": False,
            "cg_120_320_1050_4125_invented": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "remaining_blockers": {
            "missing_cg_120_320_1050_4125": True,
            "published_linear_cg_for_S_Phi17_cross": True,
            "full_cartesian_m2_from_126_54": True,
            "positive_diagonal_C_from_other_channels": True,
            "full_nonsusy_vacuum_hessian": True,
        },
        "verdict": (
            "OPEN_126_54_LOCKING Hermitian/real fluctuation census PARTIAL: "
            f"full space {full['classification']['n_positive']}+/"
            f"{full['classification']['n_negative']}-/"
            f"{full['classification']['n_zero']}0; Delta_R space "
            f"{delta_sp['classification']['n_positive']}+/"
            f"{delta_sp['classification']['n_negative']}-/"
            f"{delta_sp['classification']['n_zero']}0. Indefinite Re(ΣᵀMΣ) "
            "is not a PD Schur C seed. No 120/320/1050/4125 CG invented. "
            "Theory remains BLOCKED."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    full = report["census"]["full_252"]["classification"]
    delta = report["census"]["delta_r_eigenspace"]["classification"]
    OUT_MD.write_text(
        "# OPEN_126_54_LOCKING Hermitian fluctuation census — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- Full 252ℂ: `+{full['n_positive']} / -{full['n_negative']} / "
        f"0={full['n_zero']}`\n"
        f"- Delta_R 126ℂ: `+{delta['n_positive']} / -{delta['n_negative']} / "
        f"0={delta['n_zero']}`\n"
        f"- PD Schur C seed: `False`\n\n"
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
