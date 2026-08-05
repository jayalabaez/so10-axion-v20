#!/usr/bin/env python3
"""Withdraw physical cal-G scalar classification based on a SUSY gaugino matrix.

Aulakh cal G is a mixed chiral/gaugino fermion mass matrix. Its singular
vectors may be useful for checking the supersymmetric super-Higgs system, but
they cannot classify a physical light scalar or Goldstone of the present
non-supersymmetric potential. The scalar question must be answered by the
complete non-SUSY component mass-squared matrix after gauge projection.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

import mixed_210_126_10_hilbert_hessian_v20 as mxh

ROOT = Path(__file__).resolve().parent
NULL_TOL_OVER_MGUT = mxh.NULL_TOL_OVER_MGUT


def hilbert_g_params(
    *,
    a: float,
    omega: float,
    p: float,
    m_i: float,
    m_gut: float,
    lam: float,
    eta: float,
    goldstone_compatible: bool,
) -> dict[str, complex]:
    params = mxh.hilbert_matched_params(
        a=a,
        omega=omega,
        p=p,
        m_i=m_i,
        m_gut=m_gut,
        lam=lam,
        eta=eta,
    )
    params["goldstone_compatible_requested"] = bool(goldstone_compatible)
    params["physical_use"] = "SUSY cal-G source diagnostic only"
    return params


def singular_system(mat: np.ndarray) -> dict[str, Any]:
    u, s, vh = np.linalg.svd(mat, full_matrices=True)
    order = np.argsort(s)
    return {
        "singular_values_GeV": [float(x) for x in s[order]],
        "lightest_GeV": float(s[order][0]),
        "heaviest_GeV": float(s[order][-1]),
        "right_singular_vectors": vh[order],
        "left_singular_vectors": u[:, order].T,
        "physical_scalar_interpretation_allowed": False,
    }


def goldstone_direction(sigma: complex, sigma_bar: complex) -> np.ndarray:
    v = np.array([0.0, 0.0, 0.0, sigma, sigma_bar, 0.0], dtype=complex)
    n = np.linalg.norm(v)
    return v / n if n > 0 else v


def project_mode(
    vec: np.ndarray, sigma: complex, sigma_bar: complex
) -> dict[str, Any]:
    gdir = goldstone_direction(sigma, sigma_bar)
    v = vec / (np.linalg.norm(vec) + 1e-30)
    return {
        "overlap_formal_goldstone_direction": float(abs(np.vdot(gdir, v))),
        "physical_scalar_classification_allowed": False,
    }


def classify_soft_mode(**kwargs: Any) -> dict[str, Any]:
    return {
        "label": "withdrawn_susy_fermion_gaugino_diagnostic",
        "soft_vs_null_tol": False,
        "goldstone_like": False,
        "residual_flat_candidate": False,
        "gamma_independent": True,
        "physical_scalar_classification_allowed": False,
    }


def analyze_slice(**kwargs: Any) -> dict[str, Any]:
    return {
        "name": kwargs.get("name"),
        "withdrawn": True,
        "classification": classify_soft_mode(),
        "reason": "cal G is a SUSY chiral/gaugino fermion matrix",
    }


def build_report() -> dict[str, Any]:
    checks = {
        "cal_G_identified_as_susy_chiral_gaugino_matrix": True,
        "fermion_singular_vector_not_called_scalar_goldstone": True,
        "old_soft_mode_classification_withdrawn": True,
        "direct_nonsusy_singlet_hessian_required": True,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    primary = classify_soft_mode()
    return {
        "status": (
            "CAL_G_SCALAR_CLASSIFICATION_WITHDRAWN__SUSY_GAUGINO_MATRIX"
            if not failures
            else "CAL_G_SOURCE_WITHDRAWAL_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "slices": {
            "hilbert_generic_M": analyze_slice(name="hilbert_generic_M"),
            "hilbert_goldstone_compatible_M": analyze_slice(
                name="hilbert_goldstone_compatible_M"
            ),
        },
        "primary_classification": primary,
        "certificate": {
            "cal_G_soft_mode_classified": False,
            "classification_label": primary["label"],
            "gamma_independent": True,
            "withdrawn": True,
            "interpretation": (
                "No non-SUSY scalar mode is classified from cal G. The former "
                "Goldstone/residual-flat conclusion used a SUSY fermion/gaugino "
                "singular vector and is withdrawn."
            ),
        },
        "remaining_blockers": {
            "direct_nonsusy_singlet_mass_squared_block": True,
            "gauge_projected_full_component_hessian": True,
            "global_vacuum_and_boundedness": True,
        },
        "flag": {
            "cal_G_soft_mode_classified": False,
            "cal_G_gamma_independent": True,
            "cal_G_susy_gaugino_diagnostic_only": True,
            "old_goldstone_classification_valid": False,
            "primary_label": primary["label"],
            "exact_unique_proton_lifetime": False,
            "whole_model_excluded": False,
            "whole_model_validated": False,
        },
        "verdict": (
            "The cal G scalar soft-mode classification is withdrawn. cal G is a "
            "SUSY chiral/gaugino fermion matrix, not a non-SUSY scalar Hessian."
        ),
    }


def main() -> int:
    argparse.ArgumentParser(description=__doc__).parse_args()
    report = build_report()
    ROOT.joinpath("CAL_G_SOFT_MODE_CLASSIFICATION_V20.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("CAL_G_SOFT_MODE_CLASSIFICATION_V20.md").write_text(
        "# cal G source correction — v20\n\n" + report["verdict"] + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
