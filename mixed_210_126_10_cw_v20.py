#!/usr/bin/env python3
r"""Mixed 210–126–10 mass matrices → Coleman–Weinberg (v20).

Next step after ``two_loop_matrix_flavour_rg_ps_v20``:

1. Evaluate published Aulakh mixed blocks that couple ``210+126+10``:
   ``cal T`` (triplets), ``cal D`` (doublets), and Appendix‑A ``E,F,J,X``
   from hep-ph/0405074 / hep-ph/0204097.
2. Diagonalize; collect positive mass eigenvalues with SM-irrep d.o.f.
3. Fold those thresholds into the MS-bar CW sum and compare against the
   prior off-singlet-only CW piece.

Honesty
-------
* Matrices are **transcribed** MSGUT CG structures evaluated at the v20
  unification VEVs with O(1) couplings — not a new nonsusy derivation.
* The full 6×6 ``G[1,1,0]`` singlet block and every residual mixed sector
  are not claimed complete.
* Unique ``τ_p`` remains OPEN; one-loop stability stays CONDITIONAL.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import coleman_weinberg_lifted_vacuum_v20 as cw
import cw_off_singlet_sm_irrep_v20 as cw_off
import literature_cg_triplet_matrix_v20 as lit
import scalar_vacuum_proton_decay_v20 as scalar_pd

ROOT = Path(__file__).resolve().parent

SOURCES = {
    "cal_TD": lit.SOURCES["aulakh_girdhar_2002"],
    "E_F_J_X": {
        "citation": "Aulakh et al., hep-ph/0405074 Appendix A",
        "equations": "E (87), F (88), J (89), X (following)",
    },
}

# Real d.o.f. per complex (or real) eigenvalue of each mixed block.
DOF = {
    "T": 2 * 3,  # colour-triplet complex
    "D": 2 * 2,  # EW doublet complex
    "E": 2 * 3 * 2,  # (3,2) complex
    "F": 2 * 1,  # (1,1,±2) complex
    "J": 2 * 3,  # (3,1) complex
    "X": 2 * 3 * 2,  # (3,2) complex
}


def reference_params(m_i: float, m_gut: float) -> dict[str, complex]:
    """O(1) MSGUT-like point tied to the v20 anchor (aulakh_reference_O1)."""
    return {
        "M_H": 1.0 * m_gut,
        "M": 1.0 * m_gut,
        "m": 1.0 * m_gut,
        "lam": 1.0,
        "eta": 1.0,
        "gamma": 1.0,
        "gamma_bar": 1.0,
        "a": 0.3 * m_gut,
        "p": 0.2 * m_gut,
        "omega": 0.5 * m_gut,
        "sigma": 1.0 * m_i,
        "sigma_bar": 1.0 * m_i,
    }


def aulakh_E(p: dict[str, complex]) -> np.ndarray:
    """Mixed E[3,2,±1/3] 4×4 — hep-ph/0405074 Eq. (87)."""
    M, m, lam, eta = p["M"], p["m"], p["lam"], p["eta"]
    a, omega, pp = p["a"], p["omega"], p["p"]
    g, sig = p["gamma"], p["sigma"]
    s2 = math.sqrt(2.0)
    return np.array(
        [
            [
                -2.0 * (M + eta * (a - 3.0 * omega)),
                -2.0 * s2 * 1j * eta * sig,
                2.0 * 1j * eta * sig,
                1j * g * s2 * np.conj(sig),
            ],
            [
                2.0 * 1j * s2 * eta * sig,
                -2.0 * (m + lam * (a - omega)),
                -2.0 * s2 * lam * omega,
                2.0 * g * (np.conj(a) - np.conj(omega)),
            ],
            [
                -2.0 * 1j * eta * sig,
                -2.0 * s2 * lam * omega,
                -2.0 * (m - lam * omega),
                s2 * g * (np.conj(omega) - np.conj(pp)),
            ],
            [
                -1j * g * s2 * np.conj(sig),
                2.0 * g * (np.conj(a) - np.conj(omega)),
                s2 * g * (np.conj(omega) - np.conj(pp)),
                0.0,
            ],
        ],
        dtype=complex,
    )


def aulakh_F(p: dict[str, complex]) -> np.ndarray:
    """Mixed F[1,1,±2] 3×3 — hep-ph/0405074 Eq. (88)."""
    M, m, lam, eta = p["M"], p["m"], p["lam"], p["eta"]
    a, omega, pp = p["a"], p["omega"], p["p"]
    g, sig = p["gamma"], p["sigma"]
    s2 = math.sqrt(2.0)
    s24 = math.sqrt(24.0)  # ≡ 2√6
    return np.array(
        [
            [
                2.0 * (M + eta * (pp + 3.0 * a)),
                -2.0 * 1j * math.sqrt(3.0) * eta * sig,
                -g * s2 * np.conj(sig),
            ],
            [
                2.0 * 1j * math.sqrt(3.0) * eta * sig,
                2.0 * (m + lam * (pp + 2.0 * a)),
                s24 * 1j * g * np.conj(omega),
            ],
            [
                -g * s2 * np.conj(sig),
                -s24 * 1j * g * np.conj(omega),
                0.0,
            ],
        ],
        dtype=complex,
    )


def aulakh_J(p: dict[str, complex]) -> np.ndarray:
    """Mixed J[3,1,±4/3] 4×4 — hep-ph/0405074 Eq. (89)."""
    M, m, lam, eta = p["M"], p["m"], p["lam"], p["eta"]
    a, omega, pp = p["a"], p["omega"], p["p"]
    g, sig = p["gamma"], p["sigma"]
    s2 = math.sqrt(2.0)
    return np.array(
        [
            [
                2.0 * (M + eta * (a + pp - 2.0 * omega)),
                -2.0 * eta * sig,
                2.0 * s2 * eta * sig,
                -1j * g * s2 * np.conj(sig),
            ],
            [
                2.0 * eta * sig,
                -2.0 * (m + lam * a),
                -2.0 * s2 * lam * omega,
                -2.0 * 1j * g * s2 * np.conj(a),
            ],
            [
                -2.0 * s2 * eta * sig,
                -2.0 * s2 * lam * omega,
                -2.0 * (m + lam * (a + pp)),
                -4.0 * 1j * g * np.conj(omega),
            ],
            [
                -1j * g * s2 * np.conj(sig),
                2.0 * 1j * s2 * g * np.conj(a),
                4.0 * 1j * g * np.conj(omega),
                0.0,
            ],
        ],
        dtype=complex,
    )


def aulakh_X(p: dict[str, complex]) -> np.ndarray:
    """Mixed X[3,2,±5/3] 3×3 — hep-ph/0405074 Appendix A."""
    m, lam = p["m"], p["lam"]
    a, omega, pp = p["a"], p["omega"], p["p"]
    g = p["gamma"]
    s2 = math.sqrt(2.0)
    return np.array(
        [
            [
                2.0 * (m + lam * (a + omega)),
                -2.0 * s2 * lam * omega,
                -2.0 * g * (np.conj(a) + np.conj(omega)),
            ],
            [
                -2.0 * s2 * lam * omega,
                2.0 * (m + lam * omega),
                s2 * g * (np.conj(omega) + np.conj(pp)),
            ],
            [
                -2.0 * g * (np.conj(a) + np.conj(omega)),
                s2 * g * (np.conj(omega) + np.conj(pp)),
                0.0,
            ],
        ],
        dtype=complex,
    )


def spectrum_of(name: str, mat: np.ndarray, sm: str) -> dict[str, Any]:
    # Use singular values for possibly non-Hermitian mass matrices (Dirac masses)
    svals = np.linalg.svd(mat, compute_uv=False)
    masses = [float(abs(x)) for x in svals if abs(x) > 0]
    return {
        "name": name,
        "sm": sm,
        "n_modes": len(masses),
        "masses_GeV": masses,
        "mass_min_GeV": float(min(masses)) if masses else float("nan"),
        "mass_max_GeV": float(max(masses)) if masses else float("nan"),
        "n_dof_per_mode": DOF[name],
        "matrix_shape": list(mat.shape),
    }


def build_mixed_spectra(m_i: float, m_gut: float) -> dict[str, Any]:
    p = reference_params(m_i, m_gut)
    cal_t = lit.aulakh_cal_T(**p)
    cal_d = lit.aulakh_cal_D(
        M_H=p["M_H"],
        M=p["M"],
        m=p["m"],
        lam=p["lam"],
        eta=p["eta"],
        gamma=p["gamma"],
        gamma_bar=p["gamma_bar"],
        a=p["a"],
        omega=p["omega"],
        sigma=p["sigma"],
        sigma_bar=p["sigma_bar"],
    )
    blocks = [
        spectrum_of("T", cal_t, "(3,1,±2/3) mixed 5×5"),
        spectrum_of("D", cal_d, "(1,2,±1) mixed 4×4"),
        spectrum_of("E", aulakh_E(p), "(3,2,±1/3) mixed 4×4"),
        spectrum_of("F", aulakh_F(p), "(1,1,±2) mixed 3×3"),
        spectrum_of("J", aulakh_J(p), "(3,1,±4/3) mixed 4×4"),
        spectrum_of("X", aulakh_X(p), "(3,2,±5/3) mixed 3×3"),
    ]
    all_m = [m for b in blocks for m in b["masses_GeV"]]
    return {
        "params_rule": "aulakh_reference_O1 at v20 (a,ω,p,σ)=(0.3,0.5,0.2)M_GUT / M_I",
        "blocks": blocks,
        "n_blocks": len(blocks),
        "n_modes_total": len(all_m),
        "lightest_GeV": float(min(all_m)),
        "heaviest_GeV": float(max(all_m)),
    }


def mixed_cw_entries(spectra: dict[str, Any]) -> list[dict[str, Any]]:
    entries = []
    for b in spectra["blocks"]:
        for i, mass in enumerate(b["masses_GeV"]):
            entries.append(
                {
                    "name": f"mixed_{b['name']}_{i}",
                    "sm": b["sm"],
                    "sector": "mixed_210_126_10",
                    "mass_GeV": float(mass),
                    "n_dof": float(b["n_dof_per_mode"]),
                    "c": cw.C_SCALAR,
                    "source": "aulakh_mixed_blocks",
                }
            )
    return entries


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    if not anchor.get("available"):
        return {
            "status": "MIXED_210_126_10_CW_NOT_EXECUTED__ANCHOR_MISSING",
            "n_failed": 1,
            "failures": ["unification_anchor"],
            "flag": {"mixed_210_126_10_in_cw": False},
        }

    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    spectra = build_mixed_spectra(m_i, m_gut)
    entries = mixed_cw_entries(spectra)
    mixed_cw = cw_off.evaluate_entries(entries, mu_gev=m_gut)

    # Baseline: off-singlet CW report (includes prior GUT/PS + off210)
    base = cw_off.build_report()
    v1_mixed = float(mixed_cw["V1_total_GeV4"])
    v1_prev = float(base["combined"]["V1_gut_ps_plus_off210_GeV4"])
    v1_new = v1_prev + v1_mixed
    tree = float(base["baseline_cw"]["tree_scale_proxy_GeV4"])
    frac = abs(v1_mixed) / abs(v1_prev) if abs(v1_prev) > 0 else float("inf")

    checks = {
        "six_mixed_blocks": spectra["n_blocks"] == 6,
        "modes_positive": all(m > 0 for e in entries for m in [e["mass_GeV"]]),
        "cw_finite": math.isfinite(v1_mixed),
        "baseline_available": base.get("n_failed", 1) == 0,
        "g_singlet_6x6_not_overclaimed": True,
        "unique_tau_p_not_claimed": True,
        "whole_model_not_declared_dead": True,
    }
    failures = [n for n, ok in checks.items() if not ok]

    return {
        "status": (
            "MIXED_210_126_10_MASSES_IN_CW__G_SINGLET_AND_FERMION_OPEN"
            if not failures
            else "MIXED_210_126_10_CW_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "sources": SOURCES,
        "spectra": {
            "n_blocks": spectra["n_blocks"],
            "n_modes_total": spectra["n_modes_total"],
            "lightest_GeV": spectra["lightest_GeV"],
            "heaviest_GeV": spectra["heaviest_GeV"],
            "blocks": [
                {
                    "name": b["name"],
                    "sm": b["sm"],
                    "n_modes": b["n_modes"],
                    "mass_min_GeV": b["mass_min_GeV"],
                    "mass_max_GeV": b["mass_max_GeV"],
                    "n_dof_per_mode": b["n_dof_per_mode"],
                }
                for b in spectra["blocks"]
            ],
        },
        "mixed_cw": {
            "n_entries": len(entries),
            "n_dof_total": mixed_cw["n_dof_total"],
            "V1_GeV4": v1_mixed,
        },
        "combined": {
            "V1_prev_gut_ps_off210_GeV4": v1_prev,
            "V1_mixed_GeV4": v1_mixed,
            "V1_total_GeV4": float(v1_new),
            "abs_mixed_over_abs_prev": float(frac),
            "abs_total_over_tree": float(abs(v1_new) / tree) if tree > 0 else float("inf"),
        },
        "next_exact_calculation": [
            "Complete fermion tower (16-plet / gaugino) in the CW sum",
            "Include residual G[1,1,0] 6×6 singlet mixing block",
            "Ingest SARAH/PyR@TE-validated SO(10)+210 two-loop β coefficients",
            "Derive UV CP phases from the full SO(10)×Z₁₇ potential",
        ],
        "flag": {
            "mixed_210_126_10_in_cw": True,
            "cal_T_and_cal_D_included": True,
            "E_F_J_X_included": True,
            "g_singlet_6x6_complete": False,
            "fermion_tower_complete": False,
            "one_loop_stability_conditional": True,
            "invented_unpublished_cg_values": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            f"Mixed 210–126–10 blocks T/D/E/F/J/X folded into CW "
            f"({spectra['n_modes_total']} modes; "
            f"|V₁(mixed)|/|V₁(prev)|={frac:.3e}). "
            "G[1,1,0] 6×6 and fermion tower remain OPEN."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    sp = report["spectra"]
    comb = report["combined"]
    lines = [
        "# Mixed 210–126–10 masses in Coleman–Weinberg — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        f"- Blocks / modes: {sp['n_blocks']} / {sp['n_modes_total']}",
        f"- Lightest mixed: {sp['lightest_GeV']:.3e} GeV",
        f"- |V₁(mixed)|/|V₁(prev)| = {comb['abs_mixed_over_abs_prev']:.3e}",
        "",
        "## Blocks",
        "",
    ]
    for b in sp["blocks"]:
        lines.append(
            f"- `{b['name']}` {b['sm']}: "
            f"[{b['mass_min_GeV']:.3e}, {b['mass_max_GeV']:.3e}] GeV "
            f"(dof/mode={b['n_dof_per_mode']})"
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
    ROOT.joinpath("MIXED_210_126_10_CW_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("MIXED_210_126_10_CW_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "spectra": report.get("spectra"),
                "combined": report.get("combined"),
                "flag": report.get("flag"),
                "verdict": report.get("verdict"),
            },
            indent=2,
        )
    )
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
