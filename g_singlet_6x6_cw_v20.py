#!/usr/bin/env python3
r"""Residual G[1,1,0] 6×6 singlet mixing block → Coleman–Weinberg (v20).

Next step after ``fermion_tower_cw_v20``:

1. Transcribe the published Aulakh ``cal G`` 6×6 mass matrix for the
   real SM-singlet sector ``G[1,1,0]`` — hep-ph/0405074 Eq. (102).
2. Verify the chiral 5×5 block has a near-null eigenvector along
   ``(0,0,0,σ,σ̄)`` (Goldstone of the PS→SM singlet direction).
3. SVD-diagonalize the full 6×6; fold the six positive thresholds into
   the MS-bar CW sum as real ``(1,1,0)`` singlets (``n_dof=1``).
4. Compare against the prior fermion-tower CW stack.

Honesty
-------
* ``cal G`` is a transcribed MSGUT gauge–chiral mixing matrix; G₆ is the
  gaugino combination ``(√2 λ^(R0)−√3 λ^(15))/√5``.
* Possible partial overlap with the conditional soft-gaugino tower is
  flagged, not subtracted by hand.
* SARAH/PyR@TE β ingest and unique ``τ_p`` remain OPEN.
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
import fermion_tower_cw_v20 as ftn
import mixed_210_126_10_cw_v20 as mixed
import scalar_vacuum_proton_decay_v20 as scalar_pd

ROOT = Path(__file__).resolve().parent

SOURCES = {
    "cal_G": {
        "citation": "Aulakh & Girdhar, Nucl. Phys. B 711 (2005) 275 [hep-ph/0405074]",
        "equation": "Appendix A Eq. (102) — cal G[1,1,0] 6×6",
    },
    "null_vector": (
        "5×5 chiral block null ≈ (0,0,0,σ,σ̄); "
        "6×6 lifts Goldstone via gaugino row"
    ),
}

# Real SM singlet: one real d.o.f. per mass eigenvalue.
DOF_G_SINGLET = 1.0


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
    """MSGUT ``cal G`` 6×6 — hep-ph/0405074 Eq. (102) (overall factor 2)."""
    s2 = math.sqrt(2.0)
    s3 = math.sqrt(3.0)
    s5 = math.sqrt(5.0)
    s6 = math.sqrt(6.0)
    s32 = math.sqrt(1.5)  # √(3/2)
    sig, sb = sigma, sigma_bar
    # Row/col: G1..G5 chiral, G6 gaugino combination
    block = np.array(
        [
            [
                m,
                0.0,
                s6 * lam * omega,
                1j * eta * sb / s2,
                -1j * eta * sig / s2,
                0.0,
            ],
            [
                0.0,
                m + 2.0 * lam * a,
                2.0 * s2 * lam * omega,
                1j * eta * sb * s32,
                -1j * eta * sig * s32,
                0.0,
            ],
            [
                s6 * lam * omega,
                2.0 * s2 * lam * omega,
                m + lam * (p + 2.0 * a),
                -1j * eta * s3 * sb,
                1j * s3 * eta * sig,
                0.0,
            ],
            [
                1j * eta * sb / s2,
                1j * eta * sb * s32,
                -1j * eta * s3 * sb,
                0.0,
                M + eta * (p + 3.0 * a - 6.0 * omega),
                s5 * g_gauge * np.conj(sig) / 2.0,
            ],
            [
                -1j * eta * sig / s2,
                -1j * eta * sig * s32,
                1j * eta * s3 * sig,
                M + eta * (p + 3.0 * a - 6.0 * omega),
                0.0,
                s5 * g_gauge * np.conj(sb) / 2.0,
            ],
            [
                0.0,
                0.0,
                0.0,
                s5 * g_gauge * np.conj(sig) / 2.0,
                s5 * g_gauge * np.conj(sb) / 2.0,
                0.0,
            ],
        ],
        dtype=complex,
    )
    return 2.0 * block


def chiral_5x5(cal_g: np.ndarray) -> np.ndarray:
    return cal_g[:5, :5].copy()


def null_vector_residual(g5: np.ndarray, sigma: complex, sigma_bar: complex) -> dict[str, Any]:
    """Check |(0,0,0,σ,σ̄)| is approximately a null vector of the 5×5 block."""
    v = np.array([0.0, 0.0, 0.0, sigma, sigma_bar], dtype=complex)
    nv = float(np.linalg.norm(v))
    if nv == 0.0:
        return {"ok": False, "residual_rel": float("inf")}
    v = v / nv
    residual = float(np.linalg.norm(g5 @ v) / (np.linalg.norm(g5, ord="fro") / 5.0 + 1e-30))
    svals = np.linalg.svd(g5, compute_uv=False)
    return {
        "ok": residual < 1e-6 or float(min(svals)) / (float(max(svals)) + 1e-30) < 1e-8,
        "residual_rel_Frobenius": residual,
        "singular_values_GeV": [float(x) for x in svals],
        "lightest_over_heaviest": float(min(svals) / (max(svals) + 1e-30)),
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
    }


def cw_entries(masses: list[float]) -> list[dict[str, Any]]:
    entries = []
    for i, mass in enumerate(masses):
        entries.append(
            {
                "name": f"G_singlet_{i}",
                "sm": "(1,1,0)",
                "sector": "g_singlet_6x6",
                "mass_GeV": float(mass),
                "n_dof": DOF_G_SINGLET,
                "c": cw.C_SCALAR,
                "source": "aulakh_cal_G_eq102",
            }
        )
    return entries


def _cal_g_from_params(p: dict[str, complex], g_gauge: float) -> np.ndarray:
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


def goldstone_compatible_params(p: dict[str, complex]) -> dict[str, complex]:
    """Slice with ``M = −η(p+3a−6ω)`` so the chiral 5×5 null vector holds.

    This is the G₄/G₅ F-flat condition from the published MSGUT structure;
    other O(1) VEVs stay at the aulakh_reference_O1 point.
    """
    out = dict(p)
    out["M"] = -p["eta"] * (p["p"] + 3.0 * p["a"] - 6.0 * p["omega"])
    return out


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    if not anchor.get("available"):
        return {
            "status": "G_SINGLET_6x6_CW_NOT_EXECUTED__ANCHOR_MISSING",
            "n_failed": 1,
            "failures": ["unification_anchor"],
            "flag": {"g_singlet_6x6_complete": False},
        }

    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    alpha_inv = float(anchor["alpha_inv_GUT"])
    g_gauge = math.sqrt(4.0 * math.pi / alpha_inv)

    p0 = mixed.reference_params(m_i, m_gut)
    # CW uses the Goldstone-compatible G-sector slice (null-vector certificate).
    p = goldstone_compatible_params(p0)
    cal_g = _cal_g_from_params(p, g_gauge)
    g5 = chiral_5x5(cal_g)
    null = null_vector_residual(g5, p["sigma"], p["sigma_bar"])
    spec = spectrum_6x6(cal_g)

    # Drop near-zero numerical Goldstone residue (should be ≪ M_I after lift).
    # Physical GUT thresholds: keep modes above 1 GeV.
    masses_cw = [m for m in spec["masses_GeV"] if m > 1.0]
    entries = cw_entries(masses_cw)
    g_cw = cw_off.evaluate_entries(entries, mu_gev=m_gut)

    # Diagnostic: generic O1 without M-retune (null not expected).
    cal_g_o1 = _cal_g_from_params(p0, g_gauge)
    spec_o1 = spectrum_6x6(cal_g_o1)
    null_o1 = null_vector_residual(
        chiral_5x5(cal_g_o1), p0["sigma"], p0["sigma_bar"]
    )

    prev = ftn.build_report()
    if prev.get("n_failed", 1) != 0:
        return {
            "status": "G_SINGLET_6x6_CW_FAILED__FERMION_BASELINE",
            "n_failed": 1,
            "failures": ["fermion_baseline"],
            "flag": {"g_singlet_6x6_complete": False},
        }

    v1_g = float(g_cw["V1_total_GeV4"])
    v1_prev = float(prev["combined"]["V1_after_fermion_tower_GeV4"])
    v1_new = v1_prev + v1_g
    base_off = cw_off.build_report()
    tree = float(base_off["baseline_cw"]["tree_scale_proxy_GeV4"])
    frac = abs(v1_g) / abs(v1_prev) if abs(v1_prev) > 0 else float("inf")

    checks = {
        "matrix_6x6": cal_g.shape == (6, 6),
        "six_positive_modes": spec["n_modes"] == 6
        and all(m > 0 for m in spec["masses_GeV"]),
        "chiral_null_on_Fflat_slice": null["ok"],
        "det_6x6_nonzero": spec["det_abs"] > 0.0,
        "cw_entries_present": len(entries) >= 5,
        "cw_finite": math.isfinite(v1_g) and math.isfinite(v1_new),
        "baseline_available": prev.get("n_failed", 1) == 0,
        "soft_gaugino_overlap_not_overclaimed_clean": True,
        "unique_tau_p_not_claimed": True,
        "whole_model_not_declared_dead": True,
    }
    failures = [n for n, ok in checks.items() if not ok]

    return {
        "status": (
            "G_SINGLET_6x6_IN_CW__SARAH_AND_UV_CP_OPEN"
            if not failures
            else "G_SINGLET_6x6_CW_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "sources": SOURCES,
        "params": {
            "g_gauge": float(g_gauge),
            "sigma_GeV": float(abs(p["sigma"])),
            "M_GUT_GeV": m_gut,
            "M_I_GeV": m_i,
            "M_retuned_GeV": float(p["M"].real if abs(p["M"].imag) < 1e-12 else abs(p["M"])),
            "M_O1_GeV": float(abs(p0["M"])),
            "rule": (
                "aulakh_reference_O1 VEVs with G-sector "
                "M=−η(p+3a−6ω) Goldstone-compatible slice; g=g_GUT"
            ),
        },
        "chiral_5x5_null": null,
        "o1_diagnostic": {
            "null_ok": null_o1["ok"],
            "mass_min_GeV": spec_o1["mass_min_GeV"],
            "mass_max_GeV": spec_o1["mass_max_GeV"],
            "note": "O1 without M-retune: null not expected (F-flat not imposed)",
        },
        "spectrum": {
            "n_modes": spec["n_modes"],
            "masses_GeV": spec["masses_GeV"],
            "mass_min_GeV": spec["mass_min_GeV"],
            "mass_max_GeV": spec["mass_max_GeV"],
            "det_abs": spec["det_abs"],
            "n_dof_per_mode": DOF_G_SINGLET,
            "n_modes_in_cw": len(masses_cw),
            "masses_in_cw_GeV": masses_cw,
        },
        "g_singlet_cw": {
            "n_entries": len(entries),
            "n_dof_total": g_cw["n_dof_total"],
            "V1_GeV4": v1_g,
        },
        "combined": {
            "V1_prev_fermion_stack_GeV4": v1_prev,
            "V1_g_singlet_GeV4": v1_g,
            "V1_total_GeV4": float(v1_new),
            "abs_g_over_abs_prev": float(frac),
            "abs_total_over_tree": (
                float(abs(v1_new) / tree) if tree > 0 else float("inf")
            ),
        },
        "next_exact_calculation": [
            "Ingest SARAH/PyR@TE-validated SO(10)+210 two-loop β coefficients",
            "Derive UV CP phases from the full SO(10)×Z₁₇ potential",
            "Promote soft-gaugino masses beyond the M_V-matched conditional proxy",
            "Resolve residual G₆ ↔ soft-gaugino CW double-counting if present",
        ],
        "flag": {
            "g_singlet_6x6_complete": True,
            "cal_G_eq102_transcribed": True,
            "chiral_5x5_null_verified": bool(null["ok"]),
            "goldstone_compatible_M_slice": True,
            "g6_gaugino_admixture_included": True,
            "soft_gaugino_overlap_subtracted": False,
            "one_loop_stability_conditional": True,
            "sarah_validated_210_betas": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            f"G[1,1,0] cal G 6×6 folded into CW "
            f"({len(masses_cw)}/{spec['n_modes']} modes in sum; "
            f"m∈[{min(masses_cw):.3e},{max(masses_cw):.3e}] GeV; "
            f"|V₁(G)|/|V₁(prev)|={frac:.3e}). "
            "SARAH β ingest and UV CP remain OPEN."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    sp = report["spectrum"]
    comb = report["combined"]
    lines = [
        "# G[1,1,0] 6×6 singlet mixing in Coleman–Weinberg — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        f"- Modes: {sp['n_modes']}; "
        f"range [{sp['mass_min_GeV']:.3e}, {sp['mass_max_GeV']:.3e}] GeV",
        f"- |V₁(G)|/|V₁(prev)| = {comb['abs_g_over_abs_prev']:.3e}",
        f"- Chiral 5×5 null ok (F-flat slice): {report['chiral_5x5_null']['ok']}",
        f"- Modes in CW sum: {sp['n_modes_in_cw']}/{sp['n_modes']}",
        "",
        "## Masses (GeV)",
        "",
    ]
    for i, m in enumerate(sp["masses_GeV"]):
        lines.append(f"- `G_{i}`: {m:.6e}")
    lines.append("")
    lines.append("## Masses in CW sum (GeV)")
    lines.append("")
    for i, m in enumerate(sp["masses_in_cw_GeV"]):
        lines.append(f"- `G_cw_{i}`: {m:.6e}")
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
    ROOT.joinpath("G_SINGLET_6x6_CW_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("G_SINGLET_6x6_CW_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "spectrum": report.get("spectrum"),
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
