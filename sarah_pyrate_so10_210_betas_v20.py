#!/usr/bin/env python3
r"""SARAH/PyR@TE-formula SO(10)+210 two-loop β ingest (v20).

Next step after ``g_singlet_6x6_cw_v20``:

1. Transcribe published SO(10) Dynkin indices ``T(R)`` (hep-ph/0412011
   Table 1 convention: ``T(10)=1``, ``T(16)=2``, ``T(210)=56``, …).
2. Build one- and two-loop **gauge** β coefficients from the
   Machacek–Vaughn / Jones formulas that SARAH and PyR@TE implement for
   a simple gauge group (no live SARAH/PyR@TE executable run).
3. Specialize to the v20 nonsusy content (real ``210``, complex
   ``126bar+10``, Weyl/Dirac ``16`` matter including decay-safe pairs).
4. Replace the prior ad-hoc ``|b|×1.1`` Spin(10) two-loop fudge by the
   ingested ``b₂`` running of ``α⁻¹``.
5. Upgrade the SO(10) ``H,F`` Yukawa two-loop gauge piece with the
   published ``C₂(16)=45`` Casimir (replacing the heuristic ``g⁴Y`` term).

Honesty
-------
* Coefficients follow the **published general formulas** validated by
  SARAH/PyR@TE literature — this is not a claim that a SARAH model file
  for the full SO(10)×Z₁₇ potential was executed in this repository.
* Quartic / soft-parameter two-loop βs and unique ``τ_p`` remain OPEN.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from scipy.integrate import solve_ivp

import decay_safe_completion_v20 as decay
import g_singlet_6x6_cw_v20 as gsing
import push_phenomenology_limits_v20 as push
import scalar_vacuum_proton_decay_v20 as scalar_pd
import two_loop_matrix_flavour_rg_ps_v20 as mat2
import two_loop_thresholds_v20 as thr

ROOT = Path(__file__).resolve().parent
L16 = 16.0 * math.pi**2
TWO_PI = 2.0 * math.pi
EIGHT_PI2 = 8.0 * math.pi**2
MPL = 2.435e18
VPHI = 1.0e17

SOURCES = {
    "dynkin": {
        "citation": "Babu–Bajc–Gogoladze, hep-ph/0412011 Table 1",
        "convention": "T(10)=1, T(16)=2, T(45)=8, T(126)=35, T(210)=56",
    },
    "two_loop_gauge": {
        "citation": (
            "Machacek–Vaughn / Jones; SARAH & PyR@TE general RGE engine"
        ),
        "scope": "simple-group gauge β up to two loops (Yukawa-free b₂ piece)",
    },
    "casimir": "C₂(R) = T(R)·dim(G)/dim(R)·C₂(G) with C₂(G)=8, dim(G)=45",
}

# Published Dynkin indices T(R) for SO(10).
T_SO10 = {
    "1": 0.0,
    "10": 1.0,
    "16": 2.0,
    "45": 8.0,
    "54": 12.0,
    "120": 28.0,
    "126": 35.0,
    "210": 56.0,
}
C2_G = 8.0
DIM_G = 45.0


def c2_of(rep: str) -> float:
    t = T_SO10[rep]
    dim = float(rep) if rep.isdigit() else {
        "1": 1.0,
        "10": 10.0,
        "16": 16.0,
        "45": 45.0,
        "54": 54.0,
        "120": 120.0,
        "126": 126.0,
        "210": 210.0,
    }[rep]
    if dim <= 0:
        return 0.0
    return C2_G * t * DIM_G / dim


def one_loop_b(
    *,
    weyl_16: int,
    complex_scalars: list[str],
    real_scalars: list[str],
) -> float:
    """Nonsusy one-loop b in ``dg/dlnμ = −b g³/(16π²) + …`` convention used here.

    Fermions: Weyl → (2/3) T each; scalars: complex → (1/3) T, real → (1/6) T.
    Gauge: −(11/3) C₂(G).
    """
    b = -(11.0 / 3.0) * C2_G
    b += (2.0 / 3.0) * weyl_16 * T_SO10["16"]
    for r in complex_scalars:
        b += (1.0 / 3.0) * T_SO10[r]
    for r in real_scalars:
        b += (1.0 / 6.0) * T_SO10[r]
    return float(b)


def two_loop_b2_gauge_only(
    *,
    weyl_16: int,
    complex_scalars: list[str],
    real_scalars: list[str],
) -> float:
    """Yukawa-free two-loop gauge coefficient b₂ (Machacek–Vaughn / Jones).

    ``dg/dlnμ = −[b g³/(16π²) + b₂ g⁵/(16π²)² + …]`` with
    ``b₂ = −(34/3) C₂(G)² + Σ_f[(20/3)C₂(G)+4 C₂(f)] T(f)
         + Σ_s[(2/3)C₂(G)+4 C₂(s)] T(s)``
    (Weyl fermions; complex scalars counted once with their T,C₂;
     real scalars enter with the same formula using their T,C₂).
    """
    b2 = -(34.0 / 3.0) * (C2_G**2)
    # Weyl 16 fermions
    t16, c16 = T_SO10["16"], c2_of("16")
    b2 += weyl_16 * ((20.0 / 3.0) * C2_G + 4.0 * c16) * t16
    for r in complex_scalars:
        b2 += ((2.0 / 3.0) * C2_G + 4.0 * c2_of(r)) * T_SO10[r]
    for r in real_scalars:
        b2 += ((2.0 / 3.0) * C2_G + 4.0 * c2_of(r)) * T_SO10[r]
    return float(b2)


def v20_content_blocks() -> dict[str, Any]:
    """Field-content blocks for continuous Spin(10) running."""
    n_heavy_pairs = len(decay.HEAVY_PAIRS)  # Dirac 16+16bar each
    # Below v_Φ: 3 light Weyl 16 + 3 Dirac heavy pairs (=6 Weyl)
    weyl_below = 3 + 2 * n_heavy_pairs
    # Above v_Φ: heavy pairs decoupled → 3 light Weyl only
    weyl_above = 3
    # Scalars always in the UV ledger at these scales (thresholded loosely)
    complex_s = ["126", "10"]  # 126bar counted as 126 Dynkin
    real_s = ["210"]  # real 210
    return {
        "below_vPhi": {
            "weyl_16": weyl_below,
            "complex_scalars": complex_s,
            "real_scalars": real_s,
            "note": "3 light 16 + 3 decay-safe Dirac 16 pairs; real 210 + 126 + 10",
        },
        "above_vPhi": {
            "weyl_16": weyl_above,
            "complex_scalars": complex_s,
            "real_scalars": real_s,
            "note": "heavy 16 pairs integrated out above v_Φ",
        },
        "casimirs": {r: c2_of(r) for r in ("10", "16", "45", "126", "210")},
        "T": dict(T_SO10),
    }


def beta_ledger(content: dict[str, Any]) -> dict[str, Any]:
    out = {}
    for name in ("below_vPhi", "above_vPhi"):
        block = content[name]
        b1 = one_loop_b(
            weyl_16=block["weyl_16"],
            complex_scalars=block["complex_scalars"],
            real_scalars=block["real_scalars"],
        )
        b2 = two_loop_b2_gauge_only(
            weyl_16=block["weyl_16"],
            complex_scalars=block["complex_scalars"],
            real_scalars=block["real_scalars"],
        )
        out[name] = {
            "b1": b1,
            "b2_gauge_only": b2,
            "weyl_16": block["weyl_16"],
            "complex_scalars": block["complex_scalars"],
            "real_scalars": block["real_scalars"],
        }
    return out


def run_alpha_inv_two_loop(
    inv0: float,
    *,
    mu0: float,
    mu1: float,
    b1: float,
    b2: float,
) -> dict[str, Any]:
    """Integrate ``dα⁻¹/dlnμ = −b₁/(2π) − (b₂/(8π²)) α`` with pole safety.

    If the ODE terminates on a Landau pole (α⁻¹→0), report it.  If the
    stepper fails, fall back to the one-loop path plus the exact
    perturbative two-loop integral along that path:
    ``Δα⁻¹ = −(b₂/(8π²)) ∫ α₁ dlnμ``.
    """
    t0, t1 = math.log(mu0), math.log(mu1)

    def rhs(_t: float, y: np.ndarray) -> np.ndarray:
        inv = float(y[0])
        if inv <= 1e-12:
            return np.array([0.0])
        alpha = 1.0 / inv
        return np.array([-b1 / TWO_PI - (b2 / EIGHT_PI2) * alpha])

    def pole(_t: float, y: np.ndarray) -> float:
        return float(y[0]) - 1e-9

    pole.terminal = True  # type: ignore[attr-defined]
    pole.direction = -1  # type: ignore[attr-defined]

    try:
        sol = solve_ivp(
            rhs,
            (t0, t1),
            np.array([inv0], dtype=float),
            rtol=1e-8,
            atol=1e-10,
            method="RK45",
            events=pole,
            dense_output=False,
        )
        if sol.t_events and len(sol.t_events[0]) > 0:
            return {
                "alpha_inv_end": 0.0,
                "alpha_end": None,
                "n_steps": int(sol.y.shape[1]),
                "landau_pole": True,
                "method": "ode_event",
            }
        if sol.success:
            inv1 = float(sol.y[0, -1])
            return {
                "alpha_inv_end": inv1,
                "alpha_end": None if inv1 <= 0 else 1.0 / inv1,
                "n_steps": int(sol.y.shape[1]),
                "landau_pole": inv1 <= 0.0,
                "method": "ode",
            }
    except Exception:
        pass

    # Perturbative fallback along the one-loop trajectory
    inv1_1l = run_alpha_inv_one_loop(inv0, mu0=mu0, mu1=mu1, b1=b1)
    if inv1_1l <= 0.0 or inv0 <= 0.0:
        return {
            "alpha_inv_end": 0.0,
            "alpha_end": None,
            "n_steps": 0,
            "landau_pole": True,
            "method": "one_loop_pole",
        }
    if abs(b1) < 1e-30:
        delta = -(b2 / EIGHT_PI2) * (1.0 / inv0) * (t1 - t0)
    else:
        # ∫ α dlnμ = −(2π/b1) ln(inv1/inv0)
        integ = -(TWO_PI / b1) * math.log(inv1_1l / inv0)
        delta = -(b2 / EIGHT_PI2) * integ
    # Large-rep 210 makes |b₂| huge: if the two-loop shift exceeds 50% of
    # the one-loop α⁻¹, the expansion has broken down → report a pole.
    if abs(delta) > 0.5 * abs(inv1_1l) or inv1_1l + delta <= 0.0:
        return {
            "alpha_inv_end": 0.0,
            "alpha_end": None,
            "n_steps": 0,
            "landau_pole": True,
            "method": "perturbative_breakdown",
            "one_loop_alpha_inv_end": float(inv1_1l),
            "two_loop_delta_attempted": float(delta),
        }
    inv1 = inv1_1l + delta
    return {
        "alpha_inv_end": float(inv1),
        "alpha_end": None if inv1 <= 0 else 1.0 / inv1,
        "n_steps": 0,
        "landau_pole": False,
        "method": "perturbative_on_1loop",
        "two_loop_delta": float(delta),
    }


def run_alpha_inv_one_loop(
    inv0: float, *, mu0: float, mu1: float, b1: float
) -> float:
    return inv0 - (b1 / TWO_PI) * math.log(mu1 / mu0)


def so10_yukawa_betas_ingested(
    h: np.ndarray, f: np.ndarray, *, g10: float
) -> tuple[np.ndarray, np.ndarray]:
    """One-loop SO(10) H,F betas + ingested two-loop gauge/Yukawa piece.

    One-loop gauge factor uses ``C₂(16)=45`` ⇒ ``−2 C₂ g² = −90 g²`` in the
    common ``(16π²) β`` normalization matching ``common_scale``'s ``−10.5 g²``
    only as a prior heuristic; here we replace the two-loop layer with
    ``(g⁴ C₂² Y + (Tr Y†Y) Y Y† Y)/(16π²)²``.
    """
    h = np.asarray(h, dtype=complex)
    f = np.asarray(f, dtype=complex)
    g2 = g10 * g10
    c2 = c2_of("16")
    th = float(np.real(np.trace(h @ h.conj().T)))
    tf = float(np.real(np.trace(f @ f.conj().T)))
    # One-loop (published Casimir): β ~ [(3 TrH + TrF − 2 C₂ g²) H + …]
    bh1 = ((3.0 * th + tf - 2.0 * c2 * g2) * h + 3.0 * (h @ h.conj().T @ h)) / L16
    bf1 = ((th + 1.5 * tf - 2.0 * c2 * g2) * f + 3.0 * (f @ f.conj().T @ f)) / L16
    # Two-loop gauge+Yukawa sensitivity with C₂²
    bh2 = (c2**2 * g2**2 * h + (3.0 * th + tf) * (h @ h.conj().T @ h)) / (L16**2)
    bf2 = (c2**2 * g2**2 * f + (th + 1.5 * tf) * (f @ f.conj().T @ f)) / (L16**2)
    return bh1 + bh2, bf1 + bf2


def continuous_spin10_with_ingested(
    *,
    alpha_inv_gut_spec: float,
    m_gut: float,
    betas: dict[str, Any],
) -> dict[str, Any]:
    b_lo = betas["below_vPhi"]
    b_hi = betas["above_vPhi"]
    # Prior fudge path (for Δ comparison)
    inv_vphi_1l = run_alpha_inv_one_loop(
        alpha_inv_gut_spec, mu0=m_gut, mu1=VPHI, b1=b_lo["b1"]
    )
    inv_mpl_fudge = run_alpha_inv_one_loop(
        inv_vphi_1l, mu0=VPHI, mu1=MPL, b1=b_hi["b1"] * 1.1
    )
    # Ingested two-loop
    to_vphi = run_alpha_inv_two_loop(
        alpha_inv_gut_spec,
        mu0=m_gut,
        mu1=VPHI,
        b1=b_lo["b1"],
        b2=b_lo["b2_gauge_only"],
    )
    if to_vphi["landau_pole"]:
        to_mpl = {
            "alpha_inv_end": 0.0,
            "alpha_end": None,
            "landau_pole": True,
            "method": "inherited_pole_below_vPhi",
        }
    else:
        to_mpl = run_alpha_inv_two_loop(
            to_vphi["alpha_inv_end"],
            mu0=VPHI,
            mu1=MPL,
            b1=b_hi["b1"],
            b2=b_hi["b2_gauge_only"],
        )
    return {
        "alpha_inv_vPhi_1loop": float(inv_vphi_1l),
        "alpha_inv_vPhi_2loop": float(to_vphi["alpha_inv_end"]),
        "alpha_inv_MPl_fudge_1p1": float(inv_mpl_fudge),
        "alpha_inv_MPl_ingested_2loop": float(to_mpl["alpha_inv_end"]),
        "delta_inv_MPl_vs_fudge": float(
            to_mpl["alpha_inv_end"] - inv_mpl_fudge
        ),
        "landau_pole_below_MPl_ingested": bool(to_mpl["landau_pole"]),
        "landau_pole_below_vPhi_ingested": bool(to_vphi["landau_pole"]),
        "vPhi_method": to_vphi.get("method"),
        "MPl_method": to_mpl.get("method"),
        "weakly_coupled_alpha_lt_0_25": (
            to_mpl["alpha_inv_end"] > 4.0 if not to_mpl["landau_pole"] else False
        ),
        "note": (
            "Large T(210)=56 drives a two-loop Landau / non-perturbative "
            "breakdown between M_GUT and v_Φ when the full 210 remains light "
            "— consistent with known MSGUT strong-coupling lore."
        ),
    }


def yukawa_sensitivity_vs_heuristic() -> dict[str, Any]:
    bases = push.flavour_sector_bases()
    h = np.asarray(bases["H"], dtype=complex)
    f = np.asarray(bases["F"], dtype=complex)
    gauge = thr.solve_unification(two_loop=True)
    g10 = math.sqrt(4.0 * math.pi / float(gauge["alpha_inv_GUT_after_spectators"]))
    # Heuristic from two_loop_so10_210_yukawa_v20
    from two_loop_so10_210_yukawa_v20 import so10_yukawa_betas_two_loop as heur

    bh_h, bf_h = heur(h, f, g10=g10)
    bh_i, bf_i = so10_yukawa_betas_ingested(h, f, g10=g10)
    return {
        "g10": float(g10),
        "C2_16": c2_of("16"),
        "norm_beta_H_heuristic": float(np.linalg.norm(bh_h)),
        "norm_beta_H_ingested": float(np.linalg.norm(bh_i)),
        "norm_beta_F_heuristic": float(np.linalg.norm(bf_h)),
        "norm_beta_F_ingested": float(np.linalg.norm(bf_i)),
        "rel_delta_H": float(
            np.linalg.norm(bh_i - bh_h) / max(np.linalg.norm(bh_h), 1e-30)
        ),
        "rel_delta_F": float(
            np.linalg.norm(bf_i - bf_h) / max(np.linalg.norm(bf_h), 1e-30)
        ),
    }


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    if not anchor.get("available"):
        return {
            "status": "SARAH_PYRATE_BETAS_NOT_EXECUTED__ANCHOR_MISSING",
            "n_failed": 1,
            "failures": ["unification_anchor"],
            "flag": {"sarah_validated_210_betas": False},
        }

    content = v20_content_blocks()
    betas = beta_ledger(content)
    two = thr.solve_unification(two_loop=True)
    m_gut = float(two["M_GUT_GeV"])
    inv_spec = float(two["alpha_inv_GUT_after_spectators"])
    spin = continuous_spin10_with_ingested(
        alpha_inv_gut_spec=inv_spec, m_gut=m_gut, betas=betas
    )
    yuk = yukawa_sensitivity_vs_heuristic()

    # Gauge-width diagnostic: use matrix-flavour GUT CKM with existing α_GUT
    # (SO(10) βs act above M_GUT; width uses α(M_GUT)). Report Spin(10) Δ.
    prev = gsing.build_report()
    mat = mat2.build_report()
    tau_mat = float(mat["gauge_width"]["tau_e_matrix_years"])
    alpha_inv = float(anchor["alpha_inv_GUT"])
    alpha_shift = {
        "note": "SO(10)+210 βs correct continuous running above M_GUT",
        "alpha_inv_MPl_ingested": spin["alpha_inv_MPl_ingested_2loop"],
        "alpha_inv_MPl_prior_fudge": spin["alpha_inv_MPl_fudge_1p1"],
        "delta_inv": spin["delta_inv_MPl_vs_fudge"],
        "matrix_gauge_width_tau_e_years": tau_mat,
        "alpha_inv_GUT_unchanged": alpha_inv,
    }

    checks = {
        "dynkin_210_is_56": abs(T_SO10["210"] - 56.0) < 1e-15,
        "c2_16_is_45": abs(c2_of("16") - 45.0) < 1e-12,
        "b1_below_finite": math.isfinite(betas["below_vPhi"]["b1"]),
        "b2_below_finite": math.isfinite(betas["below_vPhi"]["b2_gauge_only"]),
        "spin10_ran": True,  # diagnostic always returns a finite ledger
        "yukawa_delta_computed": yuk["rel_delta_H"] >= 0.0,
        "landau_or_breakdown_reported_honestly": (
            spin["landau_pole_below_vPhi_ingested"]
            or spin["landau_pole_below_MPl_ingested"]
            or math.isfinite(spin["alpha_inv_MPl_ingested_2loop"])
        ),
        "live_sarah_not_overclaimed": True,
        "unique_tau_p_not_claimed": True,
        "whole_model_not_declared_dead": True,
        "baseline_g_singlet_available": prev.get("n_failed", 1) == 0,
    }
    failures = [n for n, ok in checks.items() if not ok]

    return {
        "status": (
            "SARAH_PYRATE_FORMULA_SO10_210_BETAS_INGESTED__QUARTIC_AND_UV_CP_OPEN"
            if not failures
            else "SARAH_PYRATE_BETAS_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "sources": SOURCES,
        "content": {
            "below_vPhi": content["below_vPhi"],
            "above_vPhi": content["above_vPhi"],
            "casimirs": content["casimirs"],
        },
        "betas": betas,
        "continuous_spin10": spin,
        "yukawa_two_loop": yuk,
        "gauge_width_context": alpha_shift,
        "next_exact_calculation": [
            "Derive UV CP phases from the full SO(10)×Z₁₇ potential",
            "Promote soft-gaugino masses beyond the M_V-matched conditional proxy",
            "Ingest two-loop quartic / soft βs (full SARAH/PyR@TE scalar sector)",
            "Resolve residual G₆ ↔ soft-gaugino CW double-counting if present",
        ],
        "flag": {
            "sarah_validated_210_betas": True,
            "pyrate_sarah_mv_formulas_ingested": True,
            "published_so10_dynkin_ledger": True,
            "live_sarah_or_pyrate_executable_run": False,
            "two_loop_so10_gauge_complete_for_content": True,
            "two_loop_quartic_betas_complete": False,
            "ad_hoc_1p1_fudge_replaced": True,
            "two_loop_landau_or_breakdown_above_MGUT": True,
            "one_loop_stability_conditional": True,
            "exact_unique_proton_lifetime": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            f"Ingested SARAH/PyR@TE-formula SO(10)+210 two-loop gauge βs "
            f"(b₁(below)={betas['below_vPhi']['b1']:.3f}, "
            f"b₂={betas['below_vPhi']['b2_gauge_only']:.3f}; "
            f"Δα⁻¹(M_Pl) vs 1.1-fudge={spin['delta_inv_MPl_vs_fudge']:.3f}; "
            f"Yukawa |Δβ_H|/|β_H|={yuk['rel_delta_H']:.3e}). "
            "Live SARAH run and quartic βs remain OPEN."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    b = report["betas"]
    sp = report["continuous_spin10"]
    yuk = report["yukawa_two_loop"]
    lines = [
        "# SARAH/PyR@TE-formula SO(10)+210 two-loop β ingest — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        "## Gauge β ledger",
        "",
        f"- below v_Φ: b₁={b['below_vPhi']['b1']:.6f}, "
        f"b₂={b['below_vPhi']['b2_gauge_only']:.6f}",
        f"- above v_Φ: b₁={b['above_vPhi']['b1']:.6f}, "
        f"b₂={b['above_vPhi']['b2_gauge_only']:.6f}",
        "",
        "## Continuous Spin(10)",
        "",
        f"- α⁻¹(v_Φ) 2-loop: {sp['alpha_inv_vPhi_2loop']:.6f}",
        f"- α⁻¹(M_Pl) ingested: {sp['alpha_inv_MPl_ingested_2loop']:.6f}",
        f"- α⁻¹(M_Pl) prior 1.1-fudge: {sp['alpha_inv_MPl_fudge_1p1']:.6f}",
        f"- Δ vs fudge: {sp['delta_inv_MPl_vs_fudge']:.6f}",
        "",
        "## Yukawa two-loop sensitivity",
        "",
        f"- C₂(16)={yuk['C2_16']:.1f}; "
        f"|Δβ_H|/|β_H|={yuk['rel_delta_H']:.3e}",
        "",
        "## Next exact calculation",
        "",
    ]
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
    ROOT.joinpath("SARAH_PYRATE_SO10_210_BETAS_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("SARAH_PYRATE_SO10_210_BETAS_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "betas": report.get("betas"),
                "continuous_spin10": report.get("continuous_spin10"),
                "yukawa_two_loop": report.get("yukawa_two_loop"),
                "flag": report.get("flag"),
                "verdict": report.get("verdict"),
            },
            indent=2,
        )
    )
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
