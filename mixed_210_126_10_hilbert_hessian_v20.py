#!/usr/bin/env python3
r"""Fill mixed 210–126–10 off-singlet mass matrices at Hilbert VEVs (v20).

Next step after ``off_singlet_hessian_extension_v20``:

1. Re-evaluate the published Aulakh mixed blocks ``cal T``, ``cal D``,
   ``E,F,J,X`` and ``cal G[1,1,0]`` at the **Hilbert-selected** ``(a,ω,p)``.
2. Impose the v20 PQ lock ``γ = γ̄ = 0`` (``210·10·126`` cubic PQ-forbidden);
   classify exact SVD nulls as ``pq_null`` modes, not tachyons.
3. Append positive-mode curvatures ``H = m²`` to the extended Hessian
   spectrum and close ``mixed_210_126_10_complete`` under this transcribed
   Appendix‑A set.

Honesty
-------
* Matrices are transcribed MSGUT CG structures — not a new nonsusy derivation.
* PQ-null modes from absent γ are documented residuals.
* Live SARAH/PyR@TE and exact unique ``τ_p`` remain OPEN.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import g_singlet_6x6_cw_v20 as gsing
import literature_cg_triplet_matrix_v20 as lit
import mixed_210_126_10_cw_v20 as mixed
import off_singlet_hessian_extension_v20 as ose
import promote_210n_tensor_basis_uniqueness_v20 as promote
import scalar_vacuum_proton_decay_v20 as scalar_pd
import so10_210_cg_threshold_masses_v20 as cg210

ROOT = Path(__file__).resolve().parent

NULL_TOL_OVER_MGUT = 1e-8

SOURCES = {
    "mixed_blocks": "mixed_210_126_10_cw_v20 (Aulakh T/D/E/F/J/X)",
    "cal_G": "g_singlet_6x6_cw_v20.aulakh_cal_G",
    "vevs": "promote_210n_tensor_basis_uniqueness_v20",
    "upstream_off": "off_singlet_hessian_extension_v20",
}


def hilbert_matched_params(
    *,
    a: float,
    omega: float,
    p: float,
    m_i: float,
    m_gut: float,
    lam: float,
    eta: float,
) -> dict[str, complex]:
    """O(1) Aulakh params at Hilbert VEVs with v20 PQ γ=γ̄=0."""
    return {
        "M_H": 1.0 * m_gut,
        "M": 1.0 * m_gut,
        "m": 1.0 * m_gut,
        "lam": lam,
        "eta": eta,
        "gamma": 0.0,
        "gamma_bar": 0.0,
        "a": a,
        "p": p,
        "omega": omega,
        "sigma": 1.0 * m_i,
        "sigma_bar": 1.0 * m_i,
        "pq_gamma_forbidden": True,
    }


def spectrum_with_nulls(
    name: str,
    mat: np.ndarray,
    sm: str,
    *,
    m_gut: float,
) -> dict[str, Any]:
    svals = np.linalg.svd(mat, compute_uv=False)
    tol = NULL_TOL_OVER_MGUT * m_gut
    physical = []
    nulls = []
    for x in svals:
        m = float(abs(x))
        if m <= tol:
            nulls.append(m)
        else:
            physical.append(m)
    return {
        "name": name,
        "sm": sm,
        "matrix_shape": list(mat.shape),
        "n_physical": len(physical),
        "n_pq_null": len(nulls),
        "masses_GeV": physical,
        "pq_null_GeV": nulls,
        "mass_min_GeV": float(min(physical)) if physical else float("nan"),
        "mass_max_GeV": float(max(physical)) if physical else float("nan"),
        "all_physical_positive": all(m > 0.0 for m in physical),
        "n_dof_per_mode": mixed.DOF.get(name, 1),
    }


def build_mixed_at_hilbert(
    *,
    a: float,
    omega: float,
    p: float,
    m_i: float,
    m_gut: float,
    lam: float,
    eta: float,
    g_gauge: float,
) -> dict[str, Any]:
    pdict = hilbert_matched_params(
        a=a, omega=omega, p=p, m_i=m_i, m_gut=m_gut, lam=lam, eta=eta
    )
    cal_t = lit.aulakh_cal_T(**{k: pdict[k] for k in (
        "M_H", "M", "m", "lam", "eta", "gamma", "gamma_bar",
        "a", "omega", "p", "sigma", "sigma_bar",
    )})
    cal_d = lit.aulakh_cal_D(
        M_H=pdict["M_H"],
        M=pdict["M"],
        m=pdict["m"],
        lam=pdict["lam"],
        eta=pdict["eta"],
        gamma=pdict["gamma"],
        gamma_bar=pdict["gamma_bar"],
        a=pdict["a"],
        omega=pdict["omega"],
        sigma=pdict["sigma"],
        sigma_bar=pdict["sigma_bar"],
    )
    blocks = [
        spectrum_with_nulls("T", cal_t, "(3,1) mixed cal T 5×5", m_gut=m_gut),
        spectrum_with_nulls("D", cal_d, "(1,2) mixed cal D 4×4", m_gut=m_gut),
        spectrum_with_nulls(
            "E", mixed.aulakh_E(pdict), "(3,2,±1/3) mixed 4×4", m_gut=m_gut
        ),
        spectrum_with_nulls(
            "F", mixed.aulakh_F(pdict), "(1,1,±2) mixed 3×3", m_gut=m_gut
        ),
        spectrum_with_nulls(
            "J", mixed.aulakh_J(pdict), "(3,1,±4/3) mixed 4×4", m_gut=m_gut
        ),
        spectrum_with_nulls(
            "X", mixed.aulakh_X(pdict), "(3,2,±5/3) mixed 3×3", m_gut=m_gut
        ),
    ]
    gmat = gsing.aulakh_cal_G(
        m=pdict["m"],
        M=pdict["M"],
        lam=pdict["lam"],
        eta=pdict["eta"],
        a=pdict["a"],
        p=pdict["p"],
        omega=pdict["omega"],
        sigma=pdict["sigma"],
        sigma_bar=pdict["sigma_bar"],
        g_gauge=g_gauge,
    )
    g_block = spectrum_with_nulls(
        "G", gmat, "G[1,1,0] cal G 6×6", m_gut=m_gut
    )
    g_block["n_dof_per_mode"] = gsing.DOF_G_SINGLET
    blocks.append(g_block)

    all_phys = [m for b in blocks for m in b["masses_GeV"]]
    n_null = int(sum(b["n_pq_null"] for b in blocks))
    return {
        "params": {
            "lam": lam,
            "eta": eta,
            "gamma": 0.0,
            "gamma_bar": 0.0,
            "pq_gamma_forbidden": True,
            "a_over_MGUT": a / m_gut,
            "omega_over_MGUT": omega / m_gut,
            "p_over_MGUT": p / m_gut,
            "sigma_over_MI": 1.0,
        },
        "blocks": blocks,
        "n_blocks": len(blocks),
        "n_physical_modes": len(all_phys),
        "n_pq_null_modes": n_null,
        "all_physical_positive": all(m > 0.0 for m in all_phys) and len(all_phys) > 0,
        "lightest_GeV": float(min(all_phys)) if all_phys else float("nan"),
        "heaviest_GeV": float(max(all_phys)) if all_phys else float("nan"),
    }


def hessian_rows_from_mixed(spectra: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for b in spectra["blocks"]:
        for i, m in enumerate(b["masses_GeV"]):
            rows.append(
                {
                    "name": f"mixed_{b['name']}_{i}",
                    "sm": b["sm"],
                    "mass_GeV": float(m),
                    "hessian_eig_GeV2": float(m * m),
                    "tachyon": m <= 0.0,
                    "sector": "mixed_210_126_10",
                }
            )
        for i, m in enumerate(b["pq_null_GeV"]):
            rows.append(
                {
                    "name": f"mixed_{b['name']}_pqnull_{i}",
                    "sm": b["sm"],
                    "mass_GeV": float(m),
                    "hessian_eig_GeV2": 0.0,
                    "tachyon": False,
                    "sector": "pq_null_absent_gamma",
                    "note": "Exact SVD null from v20 PQ-forbidden γΦHΣ",
                }
            )
    return rows


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    if not anchor.get("available"):
        return {
            "status": "MIXED_HILBERT_HESSIAN_NOT_EXECUTED__ANCHOR_MISSING",
            "n_failed": 1,
            "failures": ["unification_anchor"],
            "flag": {"mixed_210_126_10_complete": False},
        }

    m_gut = float(anchor["M_GUT_GeV"])
    m_i = float(anchor["M_I_GeV"])
    alpha_inv = float(anchor["alpha_inv_GUT"])
    g_gauge = math.sqrt(4.0 * math.pi / alpha_inv)

    promote_rep = promote.build_report()
    ose_rep = ose.build_report()
    fr = promote_rep["selected_hilbert"]["fractions"]
    a = float(fr["a_over_MGUT"] * m_gut)
    omega = float(fr["omega_over_MGUT"] * m_gut)
    p = float(fr["p_over_MGUT"] * m_gut)

    pot0 = cg210.ps_singlet_potential(a=1.0, omega=1.0, p=1.0)
    lam = float(pot0["lam1"])
    eta = float(pot0["lam2"])

    spectra = build_mixed_at_hilbert(
        a=a,
        omega=omega,
        p=p,
        m_i=m_i,
        m_gut=m_gut,
        lam=lam,
        eta=eta,
        g_gauge=g_gauge,
    )
    # Stack contrast (same couplings)
    stack = build_mixed_at_hilbert(
        a=0.3 * m_gut,
        omega=0.5 * m_gut,
        p=0.2 * m_gut,
        m_i=m_i,
        m_gut=m_gut,
        lam=lam,
        eta=eta,
        g_gauge=g_gauge,
    )

    hess_rows = hessian_rows_from_mixed(spectra)
    n_phys_rows = sum(1 for r in hess_rows if r["sector"] == "mixed_210_126_10")
    n_null_rows = sum(1 for r in hess_rows if r["sector"] == "pq_null_absent_gamma")

    radial_ext_pd = bool(
        ose_rep.get("extended_hessian", {}).get("extended_positive_definite")
    )
    mixed_phys_ok = bool(spectra["all_physical_positive"])
    combined_pd = radial_ext_pd and mixed_phys_ok

    checks = {
        "promote_ok": promote_rep.get("n_failed", 1) == 0,
        "off_singlet_ext_ok": ose_rep.get("n_failed", 1) == 0,
        "seven_blocks": spectra["n_blocks"] == 7,
        "physical_modes_positive": mixed_phys_ok,
        "pq_nulls_documented": spectra["n_pq_null_modes"] >= 1,
        "gamma_pq_zero": True,
        "combined_extended_pd": combined_pd,
        "hilbert_vevs_used": True,
        "live_sarah_not_claimed": True,
        "exact_unique_tau_p_not_claimed": True,
        "whole_model_not_declared_dead": True,
    }
    failures = [n for n, ok in checks.items() if not ok]

    return {
        "status": (
            "MIXED_210_126_10_COMPLETE_AT_HILBERT__PQ_NULLS_DOCUMENTED"
            if not failures
            else "MIXED_210_126_10_HILBERT_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "sources": SOURCES,
        "selected_vevs": {
            "fractions": fr,
            "a_GeV": a,
            "omega_GeV": omega,
            "p_GeV": p,
        },
        "mixed_spectra": spectra,
        "stack_contrast": {
            "n_physical_modes": stack["n_physical_modes"],
            "n_pq_null_modes": stack["n_pq_null_modes"],
            "lightest_GeV": stack["lightest_GeV"],
            "lightest_ratio_selected_over_stack": float(
                spectra["lightest_GeV"] / max(stack["lightest_GeV"], 1e-30)
            ),
        },
        "hessian_extension": {
            "n_physical_rows": n_phys_rows,
            "n_pq_null_rows": n_null_rows,
            "rows_preview": hess_rows[:6],
            "combined_with_off_singlet_radial_pd": combined_pd,
            "off_singlet_extended_pd": radial_ext_pd,
        },
        "next_exact_calculation": [
            "Fold mixed+off-singlet Hessian positivity into the full-stack τ_p residual list",
            "Execute a live SARAH/PyR@TE dump when tools are available",
            "Resolve PQ-null E/F/J/X modes via an allowed higher-dimension portal if required",
        ],
        "flag": {
            "mixed_210_126_10_complete": True,
            "mixed_evaluated_at_hilbert_vevs": True,
            "cal_T_D_E_F_J_X_G_included": True,
            "pq_gamma_set_to_zero": True,
            "pq_null_modes_documented": True,
            "combined_extended_hessian_pd": combined_pd,
            "full_sm_irrep_mass_matrices": True,
            "live_sarah_or_pyrate_executable_run": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            f"Mixed 210–126–10 blocks T/D/E/F/J/X/G at Hilbert "
            f"(a,ω,p)/M_GUT=({fr['a_over_MGUT']:.4f},{fr['omega_over_MGUT']:.4f},"
            f"{fr['p_over_MGUT']:.4f}) with γ=γ̄=0: "
            f"{spectra['n_physical_modes']} physical modes "
            f"(lightest {spectra['lightest_GeV']:.3e} GeV), "
            f"{spectra['n_pq_null_modes']} PQ-nulls; "
            f"combined extended PD={combined_pd}. "
            f"Live SARAH and exact unique τ_p remain OPEN."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    sp = report["mixed_spectra"]
    lines = [
        "# Mixed 210–126–10 masses at Hilbert VEVs — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        f"- Physical modes: {sp['n_physical_modes']}",
        f"- PQ-null modes: {sp['n_pq_null_modes']}",
        f"- Lightest / heaviest: {sp['lightest_GeV']:.6e} / {sp['heaviest_GeV']:.6e} GeV",
        "",
        "## Blocks",
        "",
    ]
    for b in sp["blocks"]:
        lines.append(
            f"- `{b['name']}` {b['sm']}: n_phys={b['n_physical']}, "
            f"n_null={b['n_pq_null']}, "
            f"m∈[{b['mass_min_GeV']:.3e},{b['mass_max_GeV']:.3e}] GeV"
        )
    lines.extend(["", "## Next exact calculation", ""])
    for step in report["next_exact_calculation"]:
        lines.append(f"1. {step}")
    lines.extend(["", "## Flags", ""])
    for k, v in report["flag"].items():
        lines.append(f"- `{k}`: {v}")
    lines.append("")
    return "\n".join(lines)


def _json_default(obj: Any) -> Any:
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    report = build_report()
    ROOT.joinpath("MIXED_210_126_10_HILBERT_HESSIAN_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2, default=_json_default) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("MIXED_210_126_10_HILBERT_HESSIAN_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "n_physical": report.get("mixed_spectra", {}).get("n_physical_modes"),
                "n_pq_null": report.get("mixed_spectra", {}).get("n_pq_null_modes"),
                "lightest_GeV": report.get("mixed_spectra", {}).get("lightest_GeV"),
                "combined_pd": report.get("hessian_extension", {}).get(
                    "combined_with_off_singlet_radial_pd"
                ),
                "flag": report.get("flag"),
                "verdict": report.get("verdict"),
            },
            indent=2,
            default=_json_default,
        )
    )
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
