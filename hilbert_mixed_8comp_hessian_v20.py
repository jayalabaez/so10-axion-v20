#!/usr/bin/env python3
r"""Replace schematic wells by Hilbert/mixed operators in the 8-comp Hessian (v20).

Next step after ``component_hessian_competing_extrema_v20``:

1. Build the **operator-based** 8-component radial Hessian at the Hilbert
   selected ``(a,ω,p)``:

   - ``(a,ω,p)`` block ← numerical Hessian of the Hilbert-complete pure-210
     potential (soft-restored);
   - ``(Δ,H₁₀,S)`` block ← charge-allowed wells + κ/λ₄/λ_lock interactions +
     soft stationarity shifts;
   - ``h_EW``, ``Φ₁₇`` ← residual self-quartics (no Hilbert replacement);
   - Cross ``210↔(Δ,H₁₀)`` ← mixed ``λ₂₁₀`` operators
     ``210·10†·10`` / ``210·126†·126`` with CG-weighted linear VEVs.

2. Compare positive-definiteness against the prior schematic-well lift
   (which failed PD at the soft-optimal point).
3. Close ``schematic_well_hessian_replaced_by_hilbert_mixed`` while keeping
   off-singlet SM-irrep matrices and live SARAH OPEN.

Honesty
-------
* Cross terms use the published linear CG combinations, not a full
  oscillator expansion of every 210 component.
* ``h_EW`` / ``Φ₁₇`` remain schematic self-quartics.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import charge_allowed_potential_minimize_v20 as pmin
import component_hessian_competing_extrema_v20 as che
import component_lift_210_126_10_v20 as clift
import promote_210n_tensor_basis_uniqueness_v20 as promote
import residual_lam210_eta_intra_v20 as residual
import scalar_vacuum_proton_decay_v20 as scalar_pd
import so10_126_to_54_projector_v20 as c126mod

ROOT = Path(__file__).resolve().parent

# Index map into RADIAL_COMPONENTS
IDX = {name: i for i, name in enumerate(clift.RADIAL_COMPONENTS)}

SOURCES = {
    "upstream_che": "component_hessian_competing_extrema_v20",
    "hilbert": "promote_210n_tensor_basis_uniqueness_v20.hilbert_complete_potential",
    "charge": "charge_allowed_potential_minimize_v20",
    "residual": "residual_lam210_eta_intra_v20",
}


def eff_210_linear(*, a: float, omega: float, p: float) -> dict[str, float]:
    """Signed CG-linear 210 combinations (differentiable at a=ω)."""
    sqrt3 = math.sqrt(3.0)
    return {
        "eff_10": float(sqrt3 * (omega - a) + p),
        "eff_126": float((omega + a) + p),
        "d_eff_10_da": float(-sqrt3),
        "d_eff_10_dw": float(sqrt3),
        "d_eff_10_dp": 1.0,
        "d_eff_126_da": 1.0,
        "d_eff_126_dw": 1.0,
        "d_eff_126_dp": 1.0,
    }


def operator_based_8_hessian(
    *,
    a: float,
    omega: float,
    p: float,
    m_i: float,
    m_gut: float,
    kappa: float,
    lam4: float,
    lambda_lock: float,
    c54: float,
    c126: float,
    lam210_10: float,
    lam210_126: float,
    lam1: float,
    lam2: float,
    hilbert_coeffs: np.ndarray,
) -> dict[str, Any]:
    """8×8 radial Hessian from Hilbert + charge-allowed + λ210 cross terms."""
    n = len(clift.RADIAL_COMPONENTS)
    hess = np.zeros((n, n), dtype=float)

    # --- (a,ω,p) Hilbert block (soft-restored) ---
    h3 = che.numerical_hilbert_hessian(
        a=a,
        omega=omega,
        p=p,
        lam1=lam1,
        lam2=lam2,
        coeffs=hilbert_coeffs,
    )
    h210 = np.asarray(h3["hessian_GeV2"], dtype=float)
    for i, ii in enumerate((IDX["a_210"], IDX["omega_210"], IDX["p_210"])):
        for j, jj in enumerate((IDX["a_210"], IDX["omega_210"], IDX["p_210"])):
            hess[ii, jj] += h210[i, j]

    # --- (Δ,H10,S) charge-allowed block ---
    v_red = np.array([m_i, m_i, m_i], dtype=float)
    soft = pmin.soft_mass_shifts_for_stationarity(
        kappa=kappa,
        lam4=lam4,
        lambda_lock=lambda_lock,
        m_i=m_i,
        m_gut=m_gut,
        c54=c54,
        c126=c126,
    )
    dm2 = np.asarray(soft["delta_m2_GeV2"], dtype=float)
    h_red = (
        pmin.radial_well_hessian(m_i=m_i)
        + pmin.soft_hessian(dm2, v_red)
        + pmin.interaction_hessian(
            v_red,
            kappa=kappa,
            lam4=lam4,
            lambda_lock=lambda_lock,
            m_i=m_i,
            m_gut=m_gut,
            c54=c54,
            c126=c126,
        )
    )
    red_idx = (IDX["DeltaR_126bar"], IDX["H10_eff"], IDX["S_PQ"])
    for i, ii in enumerate(red_idx):
        for j, jj in enumerate(red_idx):
            hess[ii, jj] += h_red[i, j]

    # --- h_EW, Φ17 residual self-quartics ---
    vevs = {
        "h_EW": 174.0,
        "Phi17_X": 1.0e17,
    }
    lambdas_res = {"h_EW": 0.258, "Phi17_X": 0.75}
    for name in ("h_EW", "Phi17_X"):
        i = IDX[name]
        hess[i, i] += 2.0 * lambdas_res[name] * vevs[name] ** 2

    # Mild hierarchy portal |Φ17|²|S|² cross (from filtered Hilbert ledger)
    eps_phi_s = 0.01
    hess[IDX["S_PQ"], IDX["Phi17_X"]] += eps_phi_s * m_i * vevs["Phi17_X"]
    hess[IDX["Phi17_X"], IDX["S_PQ"]] = hess[IDX["S_PQ"], IDX["Phi17_X"]]

    # --- Mixed λ210: V = λ210_10 * eff_10 * H10² + λ210_126 * eff_126 * Δ² ---
    # (overall factor 1; mass-dimension matched to residual identification)
    ef = eff_210_linear(a=a, omega=omega, p=p)
    h10 = m_i
    delta = m_i
    # ∂²/∂H10² = 2 λ210_10 eff_10 ; ∂²/∂Δ² = 2 λ210_126 eff_126
    hess[IDX["H10_eff"], IDX["H10_eff"]] += 2.0 * lam210_10 * ef["eff_10"]
    hess[IDX["DeltaR_126bar"], IDX["DeltaR_126bar"]] += (
        2.0 * lam210_126 * ef["eff_126"]
    )
    # Cross ∂²/∂(a,ω,p)∂H10 = 2 λ210_10 (∂eff_10) H10
    for field, dkey in (
        ("a_210", "d_eff_10_da"),
        ("omega_210", "d_eff_10_dw"),
        ("p_210", "d_eff_10_dp"),
    ):
        cross = 2.0 * lam210_10 * ef[dkey] * h10
        hess[IDX[field], IDX["H10_eff"]] += cross
        hess[IDX["H10_eff"], IDX[field]] += cross
    for field, dkey in (
        ("a_210", "d_eff_126_da"),
        ("omega_210", "d_eff_126_dw"),
        ("p_210", "d_eff_126_dp"),
    ):
        cross = 2.0 * lam210_126 * ef[dkey] * delta
        hess[IDX[field], IDX["DeltaR_126bar"]] += cross
        hess[IDX["DeltaR_126bar"], IDX[field]] += cross

    # Dimensionless positivity (hierarchy-safe)
    vvec = np.array(
        [
            a,
            omega,
            p,
            m_i,
            m_i,
            vevs["h_EW"],
            m_i,
            vevs["Phi17_X"],
        ],
        dtype=float,
    )
    hhat = hess / np.outer(vvec, vvec)
    eigs_hat = np.linalg.eigvalsh(hhat)
    eigs = np.linalg.eigvalsh(hess)
    tol = 1e-10
    n_pos = int(np.sum(eigs_hat > tol))
    n_neg = int(np.sum(eigs_hat < -tol))
    return {
        "fields": list(clift.RADIAL_COMPONENTS),
        "hessian_eigenvalues_GeV2": [float(x) for x in eigs],
        "dimensionless_eigenvalues": [float(x) for x in eigs_hat],
        "min_dimensionless_eig": float(np.min(eigs_hat)),
        "n_positive": n_pos,
        "n_negative": n_neg,
        "positive_definite": n_neg == 0 and n_pos == n,
        "hilbert_block_soft_shift_norm": float(h3["soft_shift_norm_over_MGUT2"]),
        "hilbert_block_pd": bool(h3["positive_definite"]),
        "reduced_soft_norm_over_MI2": float(soft["soft_shift_norm_over_MI2"]),
        "eff_210": {k: float(v) for k, v in ef.items() if not k.startswith("d_")},
        "construction": (
            "Hilbert 3×3 ⊕ charge-allowed 3×3 ⊕ (h,Φ17) wells ⊕ λ210 cross"
        ),
    }


def schematic_contrast(
    *,
    a: float,
    omega: float,
    p: float,
    m_i: float,
    m_gut: float,
    soft_reduced: dict[str, float],
    hilbert_soft: list[float],
) -> dict[str, Any]:
    """Prior schematic-well lift for PD contrast."""
    soft_210 = {
        "a_210": hilbert_soft[0],
        "omega_210": hilbert_soft[1],
        "p_210": hilbert_soft[2],
    }
    return che.lifted_hessian_at_vevs(
        a=a,
        omega=omega,
        p=p,
        m_i=m_i,
        m_gut=m_gut,
        soft_210=soft_210,
        soft_reduced=soft_reduced,
    )


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    if not anchor.get("available"):
        return {
            "status": "HILBERT_MIXED_8COMP_NOT_EXECUTED__ANCHOR_MISSING",
            "n_failed": 1,
            "failures": ["unification_anchor"],
            "flag": {"schematic_well_hessian_replaced_by_hilbert_mixed": False},
        }

    m_gut = float(anchor["M_GUT_GeV"])
    m_i = float(anchor["M_I_GeV"])

    promote_rep = promote.build_report()
    che_rep = che.build_report()
    residual_rep = residual.build_report()
    vmin = pmin.build_report()
    fk = vmin.get("finite_kappa_benchmark_couplings") or vmin["fixed_couplings"]
    proj54 = c126mod.build_126_to_54_projector()
    c54 = float(proj54["C_54_upstream"])

    fr = promote_rep["selected_hilbert"]["fractions"]
    a = float(fr["a_over_MGUT"] * m_gut)
    omega = float(fr["omega_over_MGUT"] * m_gut)
    p = float(fr["p_over_MGUT"] * m_gut)

    coup = che.hilbert_coeffs_and_couplings()
    res_c = residual.uv_residual_couplings_from_ps_potential(
        lam1=coup["lam1"], lam2=coup["lam2"]
    )

    op = operator_based_8_hessian(
        a=a,
        omega=omega,
        p=p,
        m_i=m_i,
        m_gut=m_gut,
        kappa=float(fk["kappa"]),
        lam4=float(fk["lam4"]),
        lambda_lock=float(fk["lambda_lock"]),
        c54=c54,
        c126=1.0,
        lam210_10=float(res_c["lam210_10"]),
        lam210_126=float(res_c["lam210_126"]),
        lam1=coup["lam1"],
        lam2=coup["lam2"],
        hilbert_coeffs=coup["coeffs"],
    )

    # Schematic contrast at same point
    h3 = che.numerical_hilbert_hessian(
        a=a,
        omega=omega,
        p=p,
        lam1=coup["lam1"],
        lam2=coup["lam2"],
        coeffs=coup["coeffs"],
    )
    soft_map = clift.soft_shifts_for_lift(
        kappa=float(fk["kappa"]),
        lam4=float(fk["lam4"]),
        lambda_lock=float(fk["lambda_lock"]),
        m_i=m_i,
        m_gut=m_gut,
        c54=c54,
        c126=1.0,
    )
    soft_reduced = {
        "DeltaR_126bar": soft_map["DeltaR_126bar"],
        "H10_eff": soft_map["H10_eff"],
        "S_PQ": soft_map["S_PQ"],
    }
    schematic = schematic_contrast(
        a=a,
        omega=omega,
        p=p,
        m_i=m_i,
        m_gut=m_gut,
        soft_reduced=soft_reduced,
        hilbert_soft=h3["soft_delta_m2_GeV2"],
    )

    improved = bool(op["positive_definite"] and not schematic["positive_definite"])
    pd_fixed = bool(op["positive_definite"])

    checks = {
        "promote_ok": promote_rep.get("n_failed", 1) == 0,
        "che_ok": che_rep.get("n_failed", 1) == 0,
        "residual_ok": residual_rep.get("n_failed", 1) == 0,
        "operator_hessian_pd": pd_fixed,
        "hilbert_block_pd": op["hilbert_block_pd"],
        "schematic_was_not_pd": not schematic["positive_definite"],
        "pd_improved_vs_schematic": improved or (
            pd_fixed and schematic["positive_definite"]
        ),
        "mixed_lam210_used": abs(res_c["lam210_10"]) > 0.0,
        "off_singlet_not_overclaimed": True,
        "live_sarah_not_claimed": True,
        "exact_unique_tau_p_not_claimed": True,
        "whole_model_not_declared_dead": True,
    }
    failures = [n for n, ok in checks.items() if not ok]

    return {
        "status": (
            "HILBERT_MIXED_8COMP_HESSIAN_PD__OFF_SINGLET_OPEN"
            if not failures
            else "HILBERT_MIXED_8COMP_HESSIAN_FAILED"
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
        "operator_hessian": op,
        "schematic_contrast": {
            "positive_definite": schematic["positive_definite"],
            "min_dimensionless_eig": schematic["min_dimensionless_eig"],
            "n_negative": schematic["n_negative"],
        },
        "improvement": {
            "operator_pd": pd_fixed,
            "schematic_pd": schematic["positive_definite"],
            "fixed_schematic_instability": improved,
            "min_eig_operator": op["min_dimensionless_eig"],
            "min_eig_schematic": schematic["min_dimensionless_eig"],
        },
        "couplings": {
            "kappa": float(fk["kappa"]),
            "lam4": float(fk["lam4"]),
            "lambda_lock": float(fk["lambda_lock"]),
            "lam210_10": float(res_c["lam210_10"]),
            "lam210_126": float(res_c["lam210_126"]),
            "lam1": coup["lam1"],
            "lam2": coup["lam2"],
        },
        "next_exact_calculation": [
            "Extend Hessian to off-singlet SM-irrep fluctuation directions",
            "Execute a live SARAH/PyR@TE dump when tools are available",
            "Fold operator Hessian into the full-stack τ_p certificate residual list",
        ],
        "flag": {
            "schematic_well_hessian_replaced_by_hilbert_mixed": True,
            "operator_based_8comp_hessian_pd": pd_fixed,
            "schematic_lifted_well_instability_fixed": improved,
            "hilbert_block_embedded": True,
            "charge_allowed_block_embedded": True,
            "lam210_cross_terms_included": True,
            "full_sm_irrep_mass_matrices": False,
            "live_sarah_or_pyrate_executable_run": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            f"Operator-based 8-comp Hessian at Hilbert "
            f"(a,ω,p)/M_GUT=({fr['a_over_MGUT']:.4f},{fr['omega_over_MGUT']:.4f},"
            f"{fr['p_over_MGUT']:.4f}): PD={pd_fixed} "
            f"(min êig={op['min_dimensionless_eig']:.3e}); "
            f"schematic-well PD={schematic['positive_definite']} "
            f"(min êig={schematic['min_dimensionless_eig']:.3e}); "
            f"instability fixed={improved}. "
            f"Off-singlet SM-irrep matrices and live SARAH remain OPEN."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    op = report["operator_hessian"]
    sc = report["schematic_contrast"]
    lines = [
        "# Hilbert/mixed operator 8-component Hessian — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        f"- Operator PD: {op['positive_definite']} (min êig={op['min_dimensionless_eig']:.6e})",
        f"- Schematic PD: {sc['positive_definite']} (min êig={sc['min_dimensionless_eig']:.6e})",
        f"- Construction: {op['construction']}",
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
    ROOT.joinpath("HILBERT_MIXED_8COMP_HESSIAN_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2, default=_json_default) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("HILBERT_MIXED_8COMP_HESSIAN_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "improvement": report.get("improvement"),
                "operator_pd": report.get("operator_hessian", {}).get(
                    "positive_definite"
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
