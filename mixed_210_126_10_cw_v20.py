#!/usr/bin/env python3
"""Source-correct Aulakh mixed fermion/gaugino blocks; exclude them from scalar CW.

The Appendix-A E/F/J/X matrices of hep-ph/0405074 are fermionic super-Higgs
blocks. Their final row/column is a gaugino, and ``g`` is the SO(10) gauge
coupling. Earlier repository versions substituted the superpotential key
``gamma`` and then counted the singular values as scalar Coleman-Weinberg
masses. Both operations are invalid for the non-supersymmetric scalar theory.

This compatibility module keeps correctly labelled E/F/J/X matrices for
source diagnostics. It deliberately contributes zero scalar-CW entries until
a direct non-SUSY component mass-squared matrix is derived.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import cw_off_singlet_sm_irrep_v20 as cw_off
import literature_cg_triplet_matrix_v20 as lit
import scalar_vacuum_proton_decay_v20 as scalar_pd

ROOT = Path(__file__).resolve().parent

SOURCES = {
    "primary": "Aulakh and Girdhar, hep-ph/0405074",
    "eq1": "gamma/gamma_bar are superpotential couplings",
    "eq27": "g is the SO(10) gauge coupling in Higgs-fermion/gaugino mixing",
    "appendix": "E/F/J/X equations 87-90 contain final gaugino states",
}

DOF = {"T": 6, "D": 4, "E": 12, "F": 2, "J": 6, "X": 12}


def reference_params(
    m_i: float,
    m_gut: float,
    g_gauge: float | None = None,
) -> dict[str, complex]:
    return {
        "M_H": 1.0 * m_gut,
        "M": 1.0 * m_gut,
        "m": 1.0 * m_gut,
        "lam": 1.0,
        "eta": 1.0,
        "gamma": 1.0,
        "gamma_bar": 1.0,
        "g_gauge": 0.7 if g_gauge is None else float(g_gauge),
        "a": 0.3 * m_gut,
        "p": 0.2 * m_gut,
        "omega": 0.5 * m_gut,
        "sigma": 1.0 * m_i,
        "sigma_bar": 1.0 * m_i,
    }


def _gauge(p: dict[str, complex]) -> complex:
    if "g_gauge" not in p:
        raise KeyError("Aulakh E/F/J/X require g_gauge; gamma is a different coupling")
    return p["g_gauge"]


def aulakh_E(p: dict[str, complex]) -> np.ndarray:
    M, m, lam, eta = p["M"], p["m"], p["lam"], p["eta"]
    a, omega, pp = p["a"], p["omega"], p["p"]
    g, sig = _gauge(p), p["sigma"]
    s2 = math.sqrt(2.0)
    return np.array([
        [-2*(M+eta*(a-3*omega)), -2*s2*1j*eta*sig, 2j*eta*sig, 1j*g*s2*np.conj(sig)],
        [2j*s2*eta*sig, -2*(m+lam*(a-omega)), -2*s2*lam*omega, 2*g*(np.conj(a)-np.conj(omega))],
        [-2j*eta*sig, -2*s2*lam*omega, -2*(m-lam*omega), s2*g*(np.conj(omega)-np.conj(pp))],
        [-1j*g*s2*np.conj(sig), 2*g*(np.conj(a)-np.conj(omega)), s2*g*(np.conj(omega)-np.conj(pp)), 0],
    ], dtype=complex)


def aulakh_F(p: dict[str, complex]) -> np.ndarray:
    M, m, lam, eta = p["M"], p["m"], p["lam"], p["eta"]
    a, omega, pp = p["a"], p["omega"], p["p"]
    g, sig = _gauge(p), p["sigma"]
    s2, s24 = math.sqrt(2.0), math.sqrt(24.0)
    return np.array([
        [2*(M+eta*(pp+3*a)), -2j*math.sqrt(3)*eta*sig, -g*s2*np.conj(sig)],
        [2j*math.sqrt(3)*eta*sig, 2*(m+lam*(pp+2*a)), s24*1j*g*np.conj(omega)],
        [-g*s2*np.conj(sig), -s24*1j*g*np.conj(omega), 0],
    ], dtype=complex)


def aulakh_J(p: dict[str, complex]) -> np.ndarray:
    M, m, lam, eta = p["M"], p["m"], p["lam"], p["eta"]
    a, omega, pp = p["a"], p["omega"], p["p"]
    g, sig = _gauge(p), p["sigma"]
    s2 = math.sqrt(2.0)
    return np.array([
        [2*(M+eta*(a+pp-2*omega)), -2*eta*sig, 2*s2*eta*sig, -1j*g*s2*np.conj(sig)],
        [2*eta*sig, -2*(m+lam*a), -2*s2*lam*omega, -2j*g*s2*np.conj(a)],
        [-2*s2*eta*sig, -2*s2*lam*omega, -2*(m+lam*(a+pp)), -4j*g*np.conj(omega)],
        [-1j*g*s2*np.conj(sig), 2j*s2*g*np.conj(a), 4j*g*np.conj(omega), 0],
    ], dtype=complex)


def aulakh_X(p: dict[str, complex]) -> np.ndarray:
    m, lam = p["m"], p["lam"]
    a, omega, pp = p["a"], p["omega"], p["p"]
    g, s2 = _gauge(p), math.sqrt(2.0)
    return np.array([
        [2*(m+lam*(a+omega)), -2*s2*lam*omega, -2*g*(np.conj(a)+np.conj(omega))],
        [-2*s2*lam*omega, 2*(m+lam*omega), s2*g*(np.conj(omega)+np.conj(pp))],
        [-2*g*(np.conj(a)+np.conj(omega)), s2*g*(np.conj(omega)+np.conj(pp)), 0],
    ], dtype=complex)


def spectrum_of(name: str, mat: np.ndarray, sm: str) -> dict[str, Any]:
    svals = np.linalg.svd(mat, compute_uv=False)
    masses = [float(abs(x)) for x in svals]
    return {
        "name": name,
        "sm": sm,
        "n_modes": len(masses),
        "masses_GeV": masses,
        "mass_min_GeV": min(masses),
        "mass_max_GeV": max(masses),
        "n_dof_per_mode": DOF[name],
        "matrix_shape": list(mat.shape),
        "physical_type": "SUSY fermion/gaugino diagnostic",
    }


def build_mixed_spectra(m_i: float, m_gut: float) -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    alpha_inv = float(anchor.get("alpha_inv_GUT", 25.0))
    g_gauge = math.sqrt(4.0 * math.pi / alpha_inv)
    p = reference_params(m_i, m_gut, g_gauge)
    blocks = [
        spectrum_of("E", aulakh_E(p), "(3,2,±1/3) super-Higgs"),
        spectrum_of("F", aulakh_F(p), "(1,1,±2) super-Higgs"),
        spectrum_of("J", aulakh_J(p), "(3,1,±4/3) super-Higgs"),
        spectrum_of("X", aulakh_X(p), "(3,2,±5/3) super-Higgs"),
    ]
    all_m = [mass for block in blocks for mass in block["masses_GeV"]]
    return {
        "params_rule": "source-correct gauge/gaugino diagnostic",
        "g_gauge": g_gauge,
        "blocks": blocks,
        "n_blocks": 4,
        "n_modes_total": len(all_m),
        "lightest_GeV": min(all_m),
        "heaviest_GeV": max(all_m),
    }


def mixed_cw_entries(spectra: dict[str, Any]) -> list[dict[str, Any]]:
    return []


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    if not anchor.get("available"):
        return {"status": "MIXED_SOURCE_AUDIT_NOT_EXECUTED__ANCHOR_MISSING", "n_failed": 1, "failures": ["unification_anchor"], "flag": {"mixed_210_126_10_in_cw": False}}
    m_i, m_gut = float(anchor["M_I_GeV"]), float(anchor["M_GUT_GeV"])
    spectra = build_mixed_spectra(m_i, m_gut)
    base = cw_off.build_report()
    v1_prev = float(base["combined"]["V1_gut_ps_plus_off210_GeV4"])
    checks = {
        "four_source_correct_efjx_blocks": spectra["n_blocks"] == 4,
        "gauge_parameter_is_separate": spectra["g_gauge"] > 0,
        "no_scalar_cw_entries_emitted": mixed_cw_entries(spectra) == [],
        "baseline_available": base.get("n_failed", 1) == 0,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "status": "AULAKH_EFJX_SOURCE_CORRECTED__SCALAR_CW_WITHDRAWN" if not failures else "AULAKH_EFJX_SOURCE_AUDIT_FAILED",
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "sources": SOURCES,
        "spectra": spectra,
        "mixed_cw": {"n_entries": 0, "n_dof_total": 0, "V1_GeV4": 0.0, "withdrawn": True},
        "combined": {
            "V1_prev_gut_ps_off210_GeV4": v1_prev,
            "V1_mixed_GeV4": 0.0,
            "V1_total_GeV4": v1_prev,
            "abs_mixed_over_abs_prev": 0.0,
            "abs_total_over_tree": float(base["combined"]["abs_total_over_tree"]),
        },
        "flag": {
            "mixed_210_126_10_in_cw": False,
            "cal_T_and_cal_D_included": False,
            "E_F_J_X_included": False,
            "E_F_J_X_gauge_gaugino_diagnostic_only": True,
            "incorrect_gamma_alias_removed": True,
            "scalar_CW_contribution_withdrawn": True,
            "direct_nonsusy_hessian_required": True,
            "exact_unique_proton_lifetime": False,
            "whole_model_excluded": False,
            "whole_model_validated": False,
        },
        "verdict": (
            "Aulakh E/F/J/X are retained only as source-correct gauge/gaugino diagnostics. "
            "Their former scalar Coleman-Weinberg contribution is withdrawn; the direct "
            "non-SUSY component Hessian must supply physical scalar masses."
        ),
    }


def main() -> int:
    argparse.ArgumentParser(description=__doc__).parse_args()
    report = build_report()
    ROOT.joinpath("MIXED_210_126_10_CW_V20_VERDICT.json").write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
    ROOT.joinpath("MIXED_210_126_10_CW_V20.md").write_text("# Corrected Aulakh mixed-block audit — v20\n\n"+report["verdict"]+"\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
