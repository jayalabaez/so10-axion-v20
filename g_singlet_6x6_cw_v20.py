#!/usr/bin/env python3
"""Source-correct Aulakh cal-G diagnostic; withdraw it from scalar CW.

Aulakh cal G[1,1,0] is a supersymmetric mixed chiral/gaugino fermion mass
matrix. Its sixth state is a gaugino combination. Earlier repository versions
assigned one real scalar degree of freedom to each singular value and inserted
them into a non-supersymmetric scalar Coleman-Weinberg potential. That is a
category error.

This module preserves the published matrix and algebraic null diagnostics for
source comparison. It emits zero scalar-CW entries. A physical singlet scalar
loop requires the eigenvalues of the direct non-SUSY component mass-squared
matrix derived from the complete scalar potential.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import fermion_tower_cw_v20 as ftn
import mixed_210_126_10_cw_v20 as mixed
import scalar_vacuum_proton_decay_v20 as scalar_pd

ROOT = Path(__file__).resolve().parent
DOF_G_SINGLET = 1.0  # historical compatibility only; never used for scalar CW

SOURCES = {
    "cal_G": {
        "citation": (
            "Aulakh & Girdhar, Nucl. Phys. B 711 (2005) 275 "
            "[hep-ph/0405074]"
        ),
        "equation": "Appendix A Eq. (102), mixed chiral/gaugino G[1,1,0]",
    },
    "source_correction": (
        "G6 is a gaugino combination; cal G is a fermion mass matrix and "
        "cannot be inserted as a non-SUSY scalar CW spectrum"
    ),
}


def aulakh_cal_G(
    *,
    m: complex,
    M: complex,
    lam: complex,
    eta: complex,
    a: complex,
    p: complex,
    omega: complex,
    sigma: complex,
    sigma_bar: complex,
    g_gauge: float,
) -> np.ndarray:
    """Published SUSY cal-G fermion/gaugino matrix, overall factor 2."""
    s2 = math.sqrt(2.0)
    s3 = math.sqrt(3.0)
    s5 = math.sqrt(5.0)
    s6 = math.sqrt(6.0)
    s32 = math.sqrt(1.5)
    sig, sb = sigma, sigma_bar
    block = np.array(
        [
            [m, 0.0, s6 * lam * omega, 1j * eta * sb / s2,
             -1j * eta * sig / s2, 0.0],
            [0.0, m + 2.0 * lam * a, 2.0 * s2 * lam * omega,
             1j * eta * sb * s32, -1j * eta * sig * s32, 0.0],
            [s6 * lam * omega, 2.0 * s2 * lam * omega,
             m + lam * (p + 2.0 * a), -1j * eta * s3 * sb,
             1j * s3 * eta * sig, 0.0],
            [1j * eta * sb / s2, 1j * eta * sb * s32,
             -1j * eta * s3 * sb, 0.0,
             M + eta * (p + 3.0 * a - 6.0 * omega),
             s5 * g_gauge * np.conj(sig) / 2.0],
            [-1j * eta * sig / s2, -1j * eta * sig * s32,
             1j * eta * s3 * sig,
             M + eta * (p + 3.0 * a - 6.0 * omega), 0.0,
             s5 * g_gauge * np.conj(sb) / 2.0],
            [0.0, 0.0, 0.0,
             s5 * g_gauge * np.conj(sig) / 2.0,
             s5 * g_gauge * np.conj(sb) / 2.0, 0.0],
        ],
        dtype=complex,
    )
    return 2.0 * block


def chiral_5x5(cal_g: np.ndarray) -> np.ndarray:
    return cal_g[:5, :5].copy()


def null_vector_residual(
    g5: np.ndarray, sigma: complex, sigma_bar: complex
) -> dict[str, Any]:
    """Formal SUSY chiral-block null diagnostic; no scalar interpretation."""
    v = np.array([0.0, 0.0, 0.0, sigma, sigma_bar], dtype=complex)
    nv = float(np.linalg.norm(v))
    if nv == 0.0:
        return {
            "ok": False,
            "residual_rel_Frobenius": float("inf"),
            "physical_scalar_interpretation_allowed": False,
        }
    v /= nv
    denom = np.linalg.norm(g5, ord="fro") / 5.0 + 1e-30
    residual = float(np.linalg.norm(g5 @ v) / denom)
    svals = np.linalg.svd(g5, compute_uv=False)
    ratio = float(min(svals) / (max(svals) + 1e-30))
    return {
        "ok": residual < 1e-6 or ratio < 1e-8,
        "residual_rel_Frobenius": residual,
        "singular_values_GeV": [float(x) for x in svals],
        "lightest_over_heaviest": ratio,
        "physical_scalar_interpretation_allowed": False,
    }


def spectrum_6x6(cal_g: np.ndarray) -> dict[str, Any]:
    svals = np.linalg.svd(cal_g, compute_uv=False)
    masses = [float(abs(x)) for x in svals]
    return {
        "n_modes": len(masses),
        "masses_GeV": masses,
        "mass_min_GeV": float(min(masses)),
        "mass_max_GeV": float(max(masses)),
        "det_abs": float(abs(np.linalg.det(cal_g))),
        "physical_type": "SUSY chiral/gaugino fermion diagnostic",
        "physical_scalar_interpretation_allowed": False,
    }


def cw_entries(masses: list[float]) -> list[dict[str, Any]]:
    """Never emit scalar-CW entries from the SUSY cal-G spectrum."""
    return []


def _cal_g_from_params(
    p: dict[str, complex], g_gauge: float
) -> np.ndarray:
    return aulakh_cal_G(
        m=p["m"],
        M=p["M"],
        lam=p["lam"],
        eta=p["eta"],
        a=p["a"],
        p=p["p"],
        omega=p["omega"],
        sigma=p["sigma"],
        sigma_bar=p["sigma_bar"],
        g_gauge=g_gauge,
    )


def goldstone_compatible_params(
    p: dict[str, complex]
) -> dict[str, complex]:
    """Published SUSY F-flat diagnostic slice; not a non-SUSY vacuum proof."""
    out = dict(p)
    out["M"] = -p["eta"] * (
        p["p"] + 3.0 * p["a"] - 6.0 * p["omega"]
    )
    out["physical_use"] = "SUSY source diagnostic only"
    return out


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    if not anchor.get("available"):
        return {
            "status": "G_SINGLET_SOURCE_AUDIT_NOT_EXECUTED__ANCHOR_MISSING",
            "overall_state": "BLOCKED",
            "n_failed": 1,
            "failures": ["unification_anchor"],
            "flag": {"scalar_CW_contribution_withdrawn": False},
        }

    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    g_gauge = math.sqrt(
        4.0 * math.pi / float(anchor["alpha_inv_GUT"])
    )
    p0 = mixed.reference_params(m_i, m_gut, g_gauge)
    p = goldstone_compatible_params(p0)
    matrix = _cal_g_from_params(p, g_gauge)
    null = null_vector_residual(
        chiral_5x5(matrix), p["sigma"], p["sigma_bar"]
    )
    spectrum = spectrum_6x6(matrix)

    previous = ftn.build_report()
    baseline_ok = previous.get("n_failed", 1) == 0
    v1_previous = (
        float(previous["combined"]["V1_after_fermion_tower_GeV4"])
        if baseline_ok
        else None
    )

    checks = {
        "published_matrix_is_6x6": matrix.shape == (6, 6),
        "gaugino_state_explicit": True,
        "formal_susy_chiral_null_diagnostic_executes": isinstance(
            null.get("ok"), bool
        ),
        "no_scalar_cw_entries_emitted": cw_entries(
            spectrum["masses_GeV"]
        ) == [],
        "fermion_tower_baseline_available": baseline_ok,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]

    return {
        "status": (
            "CAL_G_SOURCE_CORRECTED__SCALAR_CW_WITHDRAWN"
            if not failures
            else "CAL_G_SOURCE_CORRECTION_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "sources": SOURCES,
        "params": {
            "g_gauge": g_gauge,
            "M_GUT_GeV": m_gut,
            "M_I_GeV": m_i,
            "rule": "SUSY F-flat source diagnostic only",
        },
        "chiral_5x5_null": null,
        "spectrum": {
            **spectrum,
            "n_modes_in_cw": 0,
            "masses_in_cw_GeV": [],
            "n_dof_per_mode": None,
            "withdrawn_from_scalar_CW": True,
        },
        "g_singlet_cw": {
            "n_entries": 0,
            "n_dof_total": 0,
            "V1_GeV4": 0.0,
            "withdrawn": True,
        },
        "combined": {
            "V1_prev_fermion_stack_GeV4": v1_previous,
            "V1_g_singlet_GeV4": 0.0,
            "V1_total_GeV4": v1_previous,
            "abs_g_over_abs_prev": 0.0,
            "abs_total_over_tree": previous.get("combined", {}).get(
                "abs_total_over_tree"
            ),
        },
        "remaining_blockers": {
            "direct_nonsusy_singlet_mass_squared_matrix": True,
            "physical_scalar_CW_spectrum": True,
            "global_vacuum_and_full_hessian": True,
        },
        "flag": {
            "g_singlet_6x6_complete": False,
            "cal_G_eq102_transcribed": True,
            "cal_G_susy_chiral_gaugino_diagnostic_only": True,
            "chiral_5x5_null_verified_as_susy_diagnostic": bool(
                null.get("ok")
            ),
            "goldstone_compatible_M_slice_is_susy_only": True,
            "g6_gaugino_admixture_identified": True,
            "scalar_CW_contribution_withdrawn": True,
            "soft_gaugino_overlap_subtracted": False,
            "direct_nonsusy_singlet_hessian_required": True,
            "exact_unique_proton_lifetime": False,
            "whole_model_excluded": False,
            "whole_model_validated": False,
        },
        "verdict": (
            "Aulakh cal G is retained as a SUSY chiral/gaugino source "
            "diagnostic, but its singular values are withdrawn from the "
            "non-SUSY scalar Coleman-Weinberg potential."
        ),
    }


def main() -> int:
    argparse.ArgumentParser(description=__doc__).parse_args()
    report = build_report()
    ROOT.joinpath("G_SINGLET_6x6_CW_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("G_SINGLET_6x6_CW_V20.md").write_text(
        "# cal G source correction — v20\n\n" + report["verdict"] + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
