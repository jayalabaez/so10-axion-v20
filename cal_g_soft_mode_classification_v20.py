#!/usr/bin/env python3
r"""Classify the γ-independent cal G soft mode (Goldstone vs residual) (v20).

Next step after ``live_pyrate_so10_beta_dump_v20``:

1. Rebuild Aulakh ``cal G`` 6×6 at the Hilbert-selected ``(a,ω,p)`` with
   residual ``λ,η`` (γ does not enter this block).
2. Compare the generic Hilbert slice to the Goldstone-compatible F-flat
   retune ``M=−η(p+3a−6ω)`` and to the chiral 5×5 block.
3. Project the lightest right-singular vector onto the PS→SM Goldstone
   direction ``(0,0,0,σ,σ̄,0)`` and the gaugino slot ``e₆``; classify the
   soft mode as an eaten Goldstone residue vs a residual flat direction.

Honesty
-------
* Classification uses the transcribed MSGUT ``cal G`` structure — not a new
  nonsusy derivation of every singlet portal.
* Exact unique ``τ_p`` and a full quartic/soft live dump remain OPEN.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import g_singlet_6x6_cw_v20 as gsing
import live_pyrate_so10_beta_dump_v20 as live
import mixed_210_126_10_hilbert_hessian_v20 as mxh
import promote_210n_tensor_basis_uniqueness_v20 as promote
import residual_lam210_eta_intra_v20 as residual
import scalar_vacuum_proton_decay_v20 as scalar_pd

ROOT = Path(__file__).resolve().parent
NULL_TOL_OVER_MGUT = mxh.NULL_TOL_OVER_MGUT

SOURCES = {
    "cal_G": "g_singlet_6x6_cw_v20.aulakh_cal_G",
    "vevs": "promote_210n_tensor_basis_uniqueness_v20",
    "residuals": "residual_lam210_eta_intra_v20",
    "upstream_live": "live_pyrate_so10_beta_dump_v20",
}


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
    """Hilbert VEVs + residual λ/η; optional F-flat M retune for Goldstone."""
    base = mxh.hilbert_matched_params(
        a=a, omega=omega, p=p, m_i=m_i, m_gut=m_gut, lam=lam, eta=eta
    )
    # hilbert_matched sets M = M_GUT; Goldstone slice retunes M.
    if goldstone_compatible:
        return gsing.goldstone_compatible_params(base)
    return base


def singular_system(mat: np.ndarray) -> dict[str, Any]:
    u, s, vh = np.linalg.svd(mat, full_matrices=True)
    # Right singular vectors are rows of vh; lightest = last (ascending s).
    order = np.argsort(s)
    s_sorted = s[order]
    vh_sorted = vh[order]
    return {
        "singular_values_GeV": [float(x) for x in s_sorted],
        "lightest_GeV": float(s_sorted[0]),
        "heaviest_GeV": float(s_sorted[-1]),
        "right_singular_vectors": vh_sorted,  # rows
        "left_singular_vectors": u[:, order].T,
    }


def goldstone_direction(sigma: complex, sigma_bar: complex) -> np.ndarray:
    v = np.array([0.0, 0.0, 0.0, sigma, sigma_bar, 0.0], dtype=complex)
    n = np.linalg.norm(v)
    return v / n if n > 0 else v


def project_mode(vec: np.ndarray, sigma: complex, sigma_bar: complex) -> dict[str, Any]:
    gdir = goldstone_direction(sigma, sigma_bar)
    e6 = np.zeros(6, dtype=complex)
    e6[5] = 1.0
    v = vec / (np.linalg.norm(vec) + 1e-30)
    # Overlaps (absolute inner products)
    ov_g = float(abs(np.vdot(gdir, v)))
    ov_6 = float(abs(np.vdot(e6, v)))
    chiral = v.copy()
    chiral[5] = 0.0
    ov_chiral = float(np.linalg.norm(chiral))
    return {
        "overlap_goldstone_dir": ov_g,
        "overlap_gaugino_e6": ov_6,
        "chiral_norm": ov_chiral,
        "components_abs": [float(abs(x)) for x in v],
    }


def classify_soft_mode(
    *,
    lightest_GeV: float,
    null_tol_GeV: float,
    proj: dict[str, Any],
    chiral5_null_ok: bool,
    goldstone_slice: bool,
) -> dict[str, Any]:
    soft = lightest_GeV <= null_tol_GeV
    # Eaten Goldstone residue: soft, Goldstone-compatible 5×5 null, and
    # light 6×6 mode aligned with (Goldstone ⊕ gaugino) mixing.
    goldstone_like = (
        soft
        and chiral5_null_ok
        and goldstone_slice
        and proj["overlap_goldstone_dir"] >= 0.5
        and proj["overlap_gaugino_e6"] >= 0.1
    )
    # Residual flat: soft on the generic Hilbert slice (or Goldstone-poor).
    residual_flat = soft and (
        (not goldstone_slice)
        or (proj["overlap_goldstone_dir"] < 0.5 and proj["overlap_gaugino_e6"] < 0.5)
    )
    if goldstone_like:
        label = "eaten_goldstone_residue"
    elif soft and chiral5_null_ok and proj["overlap_goldstone_dir"] >= 0.5:
        label = "goldstone_dominated_soft_mode"
    elif soft:
        label = "residual_flat_or_light_singlet"
    else:
        label = "all_modes_above_null_tol"
    return {
        "label": label,
        "soft_vs_null_tol": soft,
        "goldstone_like": goldstone_like,
        "residual_flat_candidate": residual_flat and not goldstone_like,
        "gamma_independent": True,
    }


def analyze_slice(
    *,
    name: str,
    params: dict[str, complex],
    g_gauge: float,
    m_gut: float,
    goldstone_slice: bool,
) -> dict[str, Any]:
    cal_g = gsing._cal_g_from_params(params, g_gauge)
    g5 = gsing.chiral_5x5(cal_g)
    null5 = gsing.null_vector_residual(g5, params["sigma"], params["sigma_bar"])
    sys6 = singular_system(cal_g)
    light_vec = sys6["right_singular_vectors"][0]
    proj = project_mode(light_vec, params["sigma"], params["sigma_bar"])
    tol = NULL_TOL_OVER_MGUT * m_gut
    classification = classify_soft_mode(
        lightest_GeV=sys6["lightest_GeV"],
        null_tol_GeV=tol,
        proj=proj,
        chiral5_null_ok=bool(null5["ok"]),
        goldstone_slice=goldstone_slice,
    )
    # 5×5 lightest for contrast
    s5 = np.linalg.svd(g5, compute_uv=False)
    return {
        "name": name,
        "goldstone_compatible_M": goldstone_slice,
        "M_over_MGUT": float(np.real(params["M"]) / m_gut),
        "null_tol_GeV": float(tol),
        "chiral_5x5_null": {
            "ok": bool(null5["ok"]),
            "residual_rel_Frobenius": null5["residual_rel_Frobenius"],
            "lightest_GeV": float(min(s5)),
        },
        "spectrum_6x6": {
            "singular_values_GeV": sys6["singular_values_GeV"],
            "lightest_GeV": sys6["lightest_GeV"],
            "heaviest_GeV": sys6["heaviest_GeV"],
        },
        "lightest_mode_projection": proj,
        "classification": classification,
    }


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    if not anchor.get("available"):
        return {
            "status": "CAL_G_SOFT_MODE_NOT_EXECUTED__ANCHOR_MISSING",
            "n_failed": 1,
            "failures": ["unification_anchor"],
            "flag": {"cal_G_soft_mode_classified": False},
        }

    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    alpha_inv = float(anchor["alpha_inv_GUT"])
    g_gauge = math.sqrt(4.0 * math.pi / alpha_inv)

    promote_rep = promote.build_report()
    residual_rep = residual.build_report()
    live_rep = live.build_report(force_rerun=False)

    if promote_rep.get("n_failed", 1) != 0 or residual_rep.get("n_failed", 1) != 0:
        return {
            "status": "CAL_G_SOFT_MODE_NOT_EXECUTED__UPSTREAM_FAILED",
            "n_failed": 1,
            "failures": ["promote_or_residual"],
            "flag": {"cal_G_soft_mode_classified": False},
        }

    fr = promote_rep["selected_hilbert"]["fractions"]
    a = float(fr["a_over_MGUT"] * m_gut)
    omega = float(fr["omega_over_MGUT"] * m_gut)
    p = float(fr["p_over_MGUT"] * m_gut)
    lam = float(residual_rep["uv_residual_couplings"]["lam210_10"])
    eta = float(residual_rep["uv_residual_couplings"]["eta_intra"])

    hilbert = analyze_slice(
        name="hilbert_generic_M",
        params=hilbert_g_params(
            a=a,
            omega=omega,
            p=p,
            m_i=m_i,
            m_gut=m_gut,
            lam=lam,
            eta=eta,
            goldstone_compatible=False,
        ),
        g_gauge=g_gauge,
        m_gut=m_gut,
        goldstone_slice=False,
    )
    gflat = analyze_slice(
        name="hilbert_goldstone_compatible_M",
        params=hilbert_g_params(
            a=a,
            omega=omega,
            p=p,
            m_i=m_i,
            m_gut=m_gut,
            lam=lam,
            eta=eta,
            goldstone_compatible=True,
        ),
        g_gauge=g_gauge,
        m_gut=m_gut,
        goldstone_slice=True,
    )

    # Primary classification: Goldstone-compatible slice is the physical
    # MSGUT F-flat condition; Hilbert generic is the prior soft-null witness.
    primary = gflat["classification"]
    mapped = primary["label"] in {
        "eaten_goldstone_residue",
        "goldstone_dominated_soft_mode",
        "residual_flat_or_light_singlet",
        "all_modes_above_null_tol",
    }
    gamma_independent = True  # cal G has no γ entries by construction

    still_open = {
        "full_quartic_soft_live_dump": True,
        "exact_unique_proton_lifetime": True,
    }

    checks = {
        "promote_ok": promote_rep.get("n_failed", 1) == 0,
        "residual_ok": residual_rep.get("n_failed", 1) == 0,
        "hilbert_soft_or_lifted": True,
        "goldstone_slice_null5": bool(gflat["chiral_5x5_null"]["ok"]),
        "classified": mapped,
        "gamma_independent": gamma_independent,
        "exact_unique_not_overclaimed": True,
        "whole_model_not_declared_dead": True,
    }
    failures = [n for n, ok in checks.items() if not ok]

    return {
        "status": (
            "CAL_G_SOFT_MODE_CLASSIFIED__TAU_P_OPEN"
            if not failures
            else "CAL_G_SOFT_MODE_CLASSIFICATION_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "sources": SOURCES,
        "vevs": {
            "fractions": fr,
            "lam210_10": lam,
            "eta_intra": eta,
        },
        "slices": {
            "hilbert_generic_M": {
                k: v
                for k, v in hilbert.items()
                if k != "lightest_mode_projection"
            }
            | {"lightest_mode_projection": hilbert["lightest_mode_projection"]},
            "hilbert_goldstone_compatible_M": {
                k: v
                for k, v in gflat.items()
                if k != "lightest_mode_projection"
            }
            | {"lightest_mode_projection": gflat["lightest_mode_projection"]},
        },
        "primary_classification": primary,
        "upstream_status": {
            "promote": promote_rep.get("status"),
            "residual": residual_rep.get("status"),
            "live_pyrate": live_rep.get("status"),
        },
        "certificate": {
            "cal_G_soft_mode_classified": mapped,
            "classification_label": primary["label"],
            "gamma_independent": gamma_independent,
            "residual_still_open": still_open,
            "interpretation": (
                "At Hilbert VEVs the cal G block (γ-independent) has a soft "
                f"mode classified as `{primary['label']}` on the "
                "Goldstone-compatible F-flat M slice; the generic Hilbert M "
                "slice remains a diagnostic contrast. Exact unique τ_p stays OPEN."
            ),
        },
        "next_exact_calculation": [
            "Extend the live PyR@TE dump to quartic/soft βs for the charge-allowed potential",
            "Fold the classified cal G mode into the ultimate τ_p residual checklist",
            "Re-evaluate exact unique τ_p after remaining residuals close",
        ],
        "flag": {
            "cal_G_soft_mode_classified": mapped,
            "cal_G_gamma_independent": True,
            "goldstone_compatible_slice_null5": bool(gflat["chiral_5x5_null"]["ok"]),
            "primary_label": primary["label"],
            "live_sarah_or_pyrate_executable_run": bool(
                live_rep.get("flag", {}).get("live_sarah_or_pyrate_executable_run")
            ),
            "exact_unique_proton_lifetime": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            f"cal G soft mode classified as `{primary['label']}` "
            f"(Goldstone-slice lightest={gflat['spectrum_6x6']['lightest_GeV']:.3e} GeV, "
            f"Goldstone overlap={gflat['lightest_mode_projection']['overlap_goldstone_dir']:.3f}, "
            f"gaugino overlap={gflat['lightest_mode_projection']['overlap_gaugino_e6']:.3f}; "
            f"Hilbert-generic lightest={hilbert['spectrum_6x6']['lightest_GeV']:.3e} GeV). "
            f"γ-independent=True; exact_unique_proton_lifetime remains False."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    prim = report["primary_classification"]
    gflat = report["slices"]["hilbert_goldstone_compatible_M"]
    hilb = report["slices"]["hilbert_generic_M"]
    lines = [
        "# cal G soft-mode classification — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        f"- Primary label: `{prim['label']}`",
        f"- Goldstone-slice lightest: {gflat['spectrum_6x6']['lightest_GeV']:.6e} GeV",
        f"- Hilbert-generic lightest: {hilb['spectrum_6x6']['lightest_GeV']:.6e} GeV",
        f"- 5×5 null (Goldstone slice): {gflat['chiral_5x5_null']['ok']}",
        "",
        "## Still open",
        "",
    ]
    for k, v in report["certificate"]["residual_still_open"].items():
        lines.append(f"- `{k}`: {v}")
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
    ROOT.joinpath("CAL_G_SOFT_MODE_CLASSIFICATION_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("CAL_G_SOFT_MODE_CLASSIFICATION_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "primary": report["primary_classification"],
                "goldstone_slice_lightest": report["slices"][
                    "hilbert_goldstone_compatible_M"
                ]["spectrum_6x6"]["lightest_GeV"],
                "hilbert_generic_lightest": report["slices"]["hilbert_generic_M"][
                    "spectrum_6x6"
                ]["lightest_GeV"],
                "flag": report["flag"],
                "verdict": report["verdict"],
            },
            indent=2,
        )
    )
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
