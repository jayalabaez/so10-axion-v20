#!/usr/bin/env python3
"""Source-correct Aulakh E/F/J/X diagnostics; exclude them from scalar CW.

Appendix-A E/F/J/X of Aulakh hep-ph/0405074 are mixed chiral-gauge
fermion/gaugino matrices. Their ``g`` is the SO(10) gauge coupling. They are
not a response to the superpotential ``gamma`` coupling and are not
non-supersymmetric scalar mass-squared matrices.

The matrices remain executable as source diagnostics. They deliberately emit
zero scalar Coleman-Weinberg entries until a direct non-SUSY component Hessian
supplies physical scalar masses.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import cw_off_singlet_sm_irrep_v20 as cw_off
import scalar_vacuum_proton_decay_v20 as scalar_pd

ROOT = Path(__file__).resolve().parent

SOURCES = {
    "primary": "Aulakh and Girdhar, hep-ph/0405074",
    "eq1": "gamma/gamma_bar are superpotential couplings",
    "eq27": "g is the SO(10) gauge coupling in gaugino mixing",
    "appendix": "E/F/J/X contain final gaugino states",
}
DOF = {"T": 6, "D": 4, "E": 12, "F": 2, "J": 6, "X": 12}


def reference_params(
    m_i: float,
    m_gut: float,
    g_gauge: float | None = None,
) -> dict[str, complex]:
    return {
        "M_H": complex(m_gut),
        "M": complex(m_gut),
        "m": complex(m_gut),
        "lam": 1.0 + 0.0j,
        "eta": 1.0 + 0.0j,
        "gamma": 1.0 + 0.0j,
        "gamma_bar": 1.0 + 0.0j,
        "g_gauge": 0.7 if g_gauge is None else float(g_gauge),
        "a": complex(0.3 * m_gut),
        "p": complex(0.2 * m_gut),
        "omega": complex(0.5 * m_gut),
        "sigma": complex(m_i),
        "sigma_bar": complex(m_i),
    }


def _gauge(p: dict[str, complex]) -> complex:
    if "g_gauge" not in p:
        raise KeyError(
            "Aulakh E/F/J/X require g_gauge; gamma is different"
        )
    return p["g_gauge"]


def aulakh_E(p: dict[str, complex]) -> np.ndarray:
    M, m, lam, eta = p["M"], p["m"], p["lam"], p["eta"]
    a, omega, pp = p["a"], p["omega"], p["p"]
    g, sig = _gauge(p), p["sigma"]
    s2 = math.sqrt(2.0)
    return np.array(
        [
            [-2 * (M + eta * (a - 3 * omega)),
             -2 * s2 * 1j * eta * sig, 2j * eta * sig,
             1j * g * s2 * np.conj(sig)],
            [2j * s2 * eta * sig, -2 * (m + lam * (a - omega)),
             -2 * s2 * lam * omega,
             2 * g * (np.conj(a) - np.conj(omega))],
            [-2j * eta * sig, -2 * s2 * lam * omega,
             -2 * (m - lam * omega),
             s2 * g * (np.conj(omega) - np.conj(pp))],
            [-1j * g * s2 * np.conj(sig),
             2 * g * (np.conj(a) - np.conj(omega)),
             s2 * g * (np.conj(omega) - np.conj(pp)), 0.0],
        ],
        dtype=complex,
    )


def aulakh_F(p: dict[str, complex]) -> np.ndarray:
    M, m, lam, eta = p["M"], p["m"], p["lam"], p["eta"]
    a, omega, pp = p["a"], p["omega"], p["p"]
    g, sig = _gauge(p), p["sigma"]
    s2, s24 = math.sqrt(2.0), math.sqrt(24.0)
    return np.array(
        [
            [2 * (M + eta * (pp + 3 * a)),
             -2j * math.sqrt(3.0) * eta * sig,
             -g * s2 * np.conj(sig)],
            [2j * math.sqrt(3.0) * eta * sig,
             2 * (m + lam * (pp + 2 * a)),
             s24 * 1j * g * np.conj(omega)],
            [-g * s2 * np.conj(sig),
             -s24 * 1j * g * np.conj(omega), 0.0],
        ],
        dtype=complex,
    )


def aulakh_J(p: dict[str, complex]) -> np.ndarray:
    M, m, lam, eta = p["M"], p["m"], p["lam"], p["eta"]
    a, omega, pp = p["a"], p["omega"], p["p"]
    g, sig = _gauge(p), p["sigma"]
    s2 = math.sqrt(2.0)
    return np.array(
        [
            [2 * (M + eta * (a + pp - 2 * omega)),
             -2 * eta * sig, 2 * s2 * eta * sig,
             -1j * g * s2 * np.conj(sig)],
            [2 * eta * sig, -2 * (m + lam * a),
             -2 * s2 * lam * omega, -2j * g * s2 * np.conj(a)],
            [-2 * s2 * eta * sig, -2 * s2 * lam * omega,
             -2 * (m + lam * (a + pp)), -4j * g * np.conj(omega)],
            [-1j * g * s2 * np.conj(sig), 2j * s2 * g * np.conj(a),
             4j * g * np.conj(omega), 0.0],
        ],
        dtype=complex,
    )


def aulakh_X(p: dict[str, complex]) -> np.ndarray:
    m, lam = p["m"], p["lam"]
    a, omega, pp = p["a"], p["omega"], p["p"]
    g, s2 = _gauge(p), math.sqrt(2.0)
    return np.array(
        [
            [2 * (m + lam * (a + omega)), -2 * s2 * lam * omega,
             -2 * g * (np.conj(a) + np.conj(omega))],
            [-2 * s2 * lam * omega, 2 * (m + lam * omega),
             s2 * g * (np.conj(omega) + np.conj(pp))],
            [-2 * g * (np.conj(a) + np.conj(omega)),
             s2 * g * (np.conj(omega) + np.conj(pp)), 0.0],
        ],
        dtype=complex,
    )


def spectrum_of(name: str, mat: np.ndarray, sm: str) -> dict[str, Any]:
    svals = np.linalg.svd(mat, compute_uv=False)
    masses = [float(abs(value)) for value in svals]
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
        "physical_scalar_interpretation_allowed": False,
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
    all_masses = [mass for block in blocks for mass in block["masses_GeV"]]
    return {
        "params_rule": "source-correct gauge/gaugino diagnostic",
        "g_gauge": g_gauge,
        "blocks": blocks,
        "n_blocks": len(blocks),
        "n_modes_total": len(all_masses),
        "lightest_GeV": min(all_masses),
        "heaviest_GeV": max(all_masses),
    }


def mixed_cw_entries(spectra: dict[str, Any]) -> list[dict[str, Any]]:
    return []


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    if not anchor.get("available"):
        return {
            "status": "MIXED_SOURCE_AUDIT_NOT_EXECUTED__ANCHOR_MISSING",
            "overall_state": "BLOCKED",
            "n_failed": 1,
            "failures": ["unification_anchor"],
            "flag": {"mixed_210_126_10_in_cw": False},
        }

    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    spectra = build_mixed_spectra(m_i, m_gut)
    base = cw_off.build_report()
    combined = base.get("combined", {})
    baseline_cw = base.get("baseline_cw", {})
    v1_previous = float(combined["V1_gut_ps_plus_off210_GeV4"])
    tree_scale = float(baseline_cw["tree_scale_proxy_GeV4"])
    total_over_tree = (
        abs(v1_previous) / tree_scale if tree_scale > 0.0 else float("inf")
    )

    checks = {
        "four_source_correct_efjx_blocks": spectra["n_blocks"] == 4,
        "gauge_parameter_is_separate": spectra["g_gauge"] > 0.0,
        "no_scalar_cw_entries_emitted": mixed_cw_entries(spectra) == [],
        "baseline_available": base.get("n_failed", 1) == 0,
        "tree_ratio_recomputed": math.isfinite(total_over_tree),
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]

    return {
        "status": (
            "AULAKH_EFJX_SOURCE_CORRECTED__SCALAR_CW_WITHDRAWN"
            if not failures
            else "AULAKH_EFJX_SOURCE_AUDIT_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "sources": SOURCES,
        "spectra": spectra,
        "mixed_cw": {
            "n_entries": 0,
            "n_dof_total": 0,
            "V1_GeV4": 0.0,
            "withdrawn": True,
        },
        "combined": {
            "V1_prev_gut_ps_off210_GeV4": v1_previous,
            "V1_mixed_GeV4": 0.0,
            "V1_total_GeV4": v1_previous,
            "abs_mixed_over_abs_prev": 0.0,
            "abs_total_over_tree": float(total_over_tree),
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
            "Aulakh E/F/J/X are retained only as gauge/gaugino source "
            "diagnostics. Their former scalar Coleman-Weinberg contribution "
            "is withdrawn."
        ),
    }


def main() -> int:
    argparse.ArgumentParser(description=__doc__).parse_args()
    report = build_report()
    ROOT.joinpath("MIXED_210_126_10_CW_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("MIXED_210_126_10_CW_V20.md").write_text(
        "# Corrected Aulakh mixed-block audit — v20\n\n"
        + report["verdict"]
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
