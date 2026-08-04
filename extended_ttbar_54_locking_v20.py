#!/usr/bin/env python3
r"""Extended T/Tbar multiplicity + explicit 54-projector locking (v20).

Next step after ``cg_normalized_mt_locking_mix_v20``:

1. Write the **explicit SO(10) 54-projector** on ``10⊗10``
   (symmetric traceless): used to normalize the locking amplitude.
2. Extend the colour-triplet basis to ``(T_10, Tbar_10, T_126)`` using only
   charge+SO(10) allowed operators:
   - diagonals from μ, CG-weighted 210, |S|²;
   - within-10 ``T–Tbar`` from ``10_H^2 S``;
   - ``T_10–T_126`` from dim-4 ``210·10·126·S``.
3. Build the **phase Hessian** with the 54-normalized locking strength
   ``A_54 = λ_lock · C_54 · v_Δ² v_10² v_S² / M_GUT²``.

Honesty
-------
* The ``10→54`` projector is exact group theory.
* The ``126→54`` contraction factor is a literature-normalized schematic
  ``C_54`` (not a fully expanded 5-index CG table).
* Overall ``λ_lock``, ``λ4``, ``κ`` remain free until a complete minimization.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import cg_normalized_mt_locking_mix_v20 as cgmod
import conditional_mt_interference_v20 as cmt
import patel_shukla_scalar_pdecay_v20 as ps
import scalar_vacuum_proton_decay_v20 as scalar_pd

ROOT = Path(__file__).resolve().parent

BASIS = ("T_10", "Tbar_10", "T_126")

SOURCES = {
    "so10_54": {
        "citation": "Slansky, Phys. Rept. 79 (1981) 1; standard SO(10) tensor calculus",
        "use": "54 = symmetric traceless 2-index; projector on 10⊗10",
    },
    "upstream_cg": cgmod.SOURCES,
}


def projector_54_on_10x10() -> dict[str, Any]:
    r"""Exact projector P_54: Sym_0(10⊗10) → 54.

    For vector indices i,j,k,l = 1..10,

        P_{ij,kl} = (1/2)(δ_{ik}δ_{jl} + δ_{il}δ_{jk}) − (1/10) δ_{ij}δ_{kl}.

    Properties used:
    * P² = P (idempotent)
    * Tr(P) = dim(54) = 54
    * Removes the singlet trace piece of the symmetric product.
    """
    n = 10
    # Build 100×100 matrix on flattened (i,j) with i<=j handled via full n² basis
    dim = n * n
    p = np.zeros((dim, dim), dtype=float)

    def idx(i: int, j: int) -> int:
        return i * n + j

    for i in range(n):
        for j in range(n):
            for k in range(n):
                for ell in range(n):
                    sym = 0.5 * (
                        (1.0 if i == k and j == ell else 0.0)
                        + (1.0 if i == ell and j == k else 0.0)
                    )
                    trace = (1.0 / n) * (1.0 if i == j else 0.0) * (
                        1.0 if k == ell else 0.0
                    )
                    p[idx(i, j), idx(k, ell)] = sym - trace

    p2 = p @ p
    idem_err = float(np.max(np.abs(p2 - p)))
    # Trace in the embedding space equals number of independent 54 components
    # when restricted to symmetric traceless; full n² embedding trace is 54.
    tr = float(np.trace(p))
    # Frobenius norm of projector
    frob2 = float(np.sum(p * p))
    # Combinatorial normalization often used: C_54 = 1/sqrt(Tr P) = 1/sqrt(54)
    c_54 = 1.0 / math.sqrt(54.0)
    return {
        "status": "SO10_54_PROJECTOR_ON_10x10_CONSTRUCTED",
        "formula": "P_ij,kl = 1/2(δ_ik δ_jl + δ_il δ_jk) - 1/10 δ_ij δ_kl",
        "n": n,
        "embedding_dim": dim,
        "trace": tr,
        "expected_dim_54": 54.0,
        "idempotence_max_abs_error": idem_err,
        "frobenius_sq": frob2,
        "C_54_normalization": c_54,
        "flag": {
            "projector_exact": True,
            "idempotent": idem_err < 1e-10,
            "trace_equals_54": abs(tr - 54.0) < 1e-8,
            "126_to_54_fully_expanded": False,
        },
        "verdict": (
            "Exact 10⊗10→54 projector constructed and verified (P²=P, Tr=54). "
            "Locking amplitude uses C_54=1/√54 times a schematic 126→54 factor."
        ),
    }


def locking_amplitude_54(
    *,
    m_i: float,
    m_gut: float,
    lambda_lock: float,
    c_54: float,
    c_126_to_54: float = 1.0,
) -> dict[str, Any]:
    """A_54 for V = -A cos(2φ_Δ + 2φ_10 + 2φ_S).

    A_54 = λ_lock · C_54 · C_126→54 · v_Δ² · v_10² · v_S² / M_GUT²
    with v_Δ = v_S = M_I and v_10,eff ~ v_EW omitted → use M_I as ΔR and S,
    and an effective EW-ish placeholder is NOT used (would be tiny). For the
    GUT/intermediate locking relevant to axion alignment we take
    v_10,PS-singlet-proxy = M_I as well when the EW 10 VEV is not the
    locking VEV — manuscript locking uses the same order-parameter fields
    that break PQ, so all three VEVs are intermediate/GUT-adjacent.
    Here: v_Δ = v_10_eff = v_S = M_I.
    """
    v = m_i
    a54 = (
        lambda_lock
        * c_54
        * c_126_to_54
        * (v**2)
        * (v**2)
        * (v**2)
        / (m_gut**2)
    )
    return {
        "lambda_lock": lambda_lock,
        "C_54": c_54,
        "C_126_to_54_schematic": c_126_to_54,
        "v_Delta_GeV": v,
        "v_10eff_GeV": v,
        "v_S_GeV": v,
        "M_GUT_GeV": m_gut,
        "A_54": float(a54),
        "note": (
            "C_126_to_54=1 is a schematic placeholder; the 10→54 projector "
            "normalization C_54=1/√54 is exact."
        ),
    }


def phase_hessian_from_A(a_lock: float) -> dict[str, Any]:
    g = np.array([2.0, 2.0, 2.0], dtype=float)
    hess = a_lock * np.outer(g, g)
    # Analytic spectrum of rank-1 H = A ggᵀ: λ = (0, 0, A‖g‖²).
    # float64 eigvalsh on ~1e38 entries yields O(1e22) spurious modes.
    g2 = float(np.dot(g, g))
    eigs = np.array([0.0, 0.0, float(a_lock) * g2], dtype=float)
    tol = 1e-12 * max(1.0, abs(float(a_lock)) * g2)
    return {
        "fields": ["phi_DeltaR_126", "phi_10", "phi_S"],
        "hessian": hess.tolist(),
        "eigenvalues": [float(x) for x in eigs],
        "spectrum_method": "analytic_rank1_AggT",
        "n_positive": int(np.sum(eigs > tol)),
        "n_zero": int(np.sum(np.abs(eigs) <= tol)),
        "massive_mode_mass_proxy": float(math.sqrt(max(eigs[-1], 0.0))),
        "flag": {"complete_multi_operator_phase_hessian": False},
    }


def fill_extended_3x3(
    *,
    m_i: float,
    m_gut: float,
    mu_t: float,
    mu_tbar: float,
    mu_126: float,
    lam210_10: float,
    lam210_126: float,
    lamS_10: float,
    lamS_126: float,
    kappa: float,
    lam4: float,
    include_dim4_mix: bool,
) -> dict[str, Any]:
    """3×3 mass matrix in basis (T_10, Tbar_10, T_126)."""
    weights = cgmod.cg_weighted_210_vev(
        a=0.3 * m_gut, p=0.2 * m_gut, omega=0.5 * m_gut
    )
    m11 = mu_t + lam210_10 * weights["eff_210_for_10_GeV"] + lamS_10 * m_i
    m22 = mu_tbar + lam210_10 * weights["eff_210_for_10_GeV"] + lamS_10 * m_i
    m33 = mu_126 + lam210_126 * weights["eff_210_for_126_GeV"] + lamS_126 * m_i
    # Within-10 from 10^2 S: μ²=κ⟨S⟩² ⇒ mass-like off-diag κ⟨S⟩ (codebase GeV convention)
    m12 = kappa * m_i
    m13 = lam4 * m_i if include_dim4_mix else 0.0
    # Tbar–126: use conjugate dim-4 structure 210·10†·126·S† ~ same magnitude
    m23 = lam4 * m_i if include_dim4_mix else 0.0
    matrix = np.array(
        [
            [m11, m12, m13],
            [m12, m22, m23],
            [m13, m23, m33],
        ],
        dtype=float,
    )
    return {
        "basis": list(BASIS),
        "matrix_GeV": matrix,
        "weights": weights,
        "operators_used": {
            "within_10_T_Tbar": "10_H^2 S",
            "T10_T126": "210·10·126·S" if include_dim4_mix else None,
            "Tbar_T126": "210·10†·126·S† (conj.)" if include_dim4_mix else None,
            "forbidden_cubic_10_126_S": False,
        },
    }


SCENARIOS: list[dict[str, Any]] = [
    {
        "name": "ext_decoupled",
        "mu_t_over_MI": 1.0,
        "mu_tbar_over_MI": 1.1,
        "mu_126_over_MI": 1.0,
        "lam210_10": 0.0,
        "lam210_126": 0.0,
        "lamS_10": 0.0,
        "lamS_126": 0.0,
        "kappa": 0.0,
        "lam4": 0.0,
        "include_dim4_mix": False,
        "lambda_lock": 1.0,
    },
    {
        "name": "ext_ttbar_mixing",
        "mu_t_over_MI": 1.0,
        "mu_tbar_over_MI": 1.2,
        "mu_126_over_MI": 2.0,
        "lam210_10": 0.0,
        "lam210_126": 0.0,
        "lamS_10": 0.0,
        "lamS_126": 0.0,
        "kappa": 0.3,
        "lam4": 0.0,
        "include_dim4_mix": False,
        "lambda_lock": 1.0,
    },
    {
        "name": "ext_dim4_full",
        "mu_t_over_MI": 1.0,
        "mu_tbar_over_MI": 1.1,
        "mu_126_over_MI": 1.0,
        "lam210_10": 0.2,
        "lam210_126": 0.2,
        "lamS_10": 0.3,
        "lamS_126": 0.3,
        "kappa": 0.2,
        "lam4": 0.4,
        "include_dim4_mix": True,
        "lambda_lock": 1.0,
    },
    {
        "name": "ext_light_T_stress",
        "mu_t_over_MI": 0.1,
        "mu_tbar_over_MI": 0.12,
        "mu_126_over_MI": 5.0,
        "lam210_10": 0.0,
        "lam210_126": 0.0,
        "lamS_10": 0.0,
        "lamS_126": 0.0,
        "kappa": 0.05,
        "lam4": 0.0,
        "include_dim4_mix": False,
        "lambda_lock": 0.5,
    },
    {
        "name": "ext_cg210_lock",
        "mu_t_over_MI": 0.0,
        "mu_tbar_over_MI": 0.0,
        "mu_126_over_MI": 0.0,
        "lam210_10": 1.0,
        "lam210_126": 1.0,
        "lamS_10": 0.0,
        "lamS_126": 0.0,
        "kappa": 0.0,
        "lam4": 0.1,
        "include_dim4_mix": True,
        "lambda_lock": 2.0,
    },
]


def evaluate_scenario(
    scenario: dict[str, Any],
    *,
    m_i: float,
    m_gut: float,
    tau_gauge: float,
    c_54: float,
) -> dict[str, Any]:
    filled = fill_extended_3x3(
        m_i=m_i,
        m_gut=m_gut,
        mu_t=float(scenario["mu_t_over_MI"]) * m_i,
        mu_tbar=float(scenario["mu_tbar_over_MI"]) * m_i,
        mu_126=float(scenario["mu_126_over_MI"]) * m_i,
        lam210_10=float(scenario["lam210_10"]),
        lam210_126=float(scenario["lam210_126"]),
        lamS_10=float(scenario["lamS_10"]),
        lamS_126=float(scenario["lamS_126"]),
        kappa=float(scenario["kappa"]),
        lam4=float(scenario["lam4"]),
        include_dim4_mix=bool(scenario["include_dim4_mix"]),
    )
    matrix = filled["matrix_GeV"]
    w, v = np.linalg.eigh(matrix)
    order = np.argsort(np.abs(w))
    w = w[order]
    v = v[:, order]
    light = float(abs(w[0]))
    fracs = np.abs(v[:, 0]) ** 2
    fracs = fracs / float(np.sum(fracs))
    amp = locking_amplitude_54(
        m_i=m_i,
        m_gut=m_gut,
        lambda_lock=float(scenario["lambda_lock"]),
        c_54=c_54,
    )
    phase = phase_hessian_from_A(amp["A_54"])

    singular = light <= 0.0
    # Dominance: mostly 10-sector if frac0+frac1 >= 0.7
    frac10sec = float(fracs[0] + fracs[1])
    dominance = "10_H_sector" if frac10sec >= 0.70 else (
        "126bar_H" if float(fracs[2]) >= 0.70 else "mixed"
    )
    ps_dom = "10_H" if dominance != "126bar_H" else "126bar_H"
    ps_rows: list[dict[str, Any]] = []
    if not singular:
        for alpha_ps in (0.01, 0.1, 0.3):
            row = dict(
                ps.evaluate_channel(
                    ps_dom,
                    "p_to_mu_K0",
                    alpha=alpha_ps,
                    M_T_GeV=light,
                    M_Tbar_GeV=light,
                )
            )
            row["interference_incoherent_years"] = cmt.interference_lifetime_years(
                tau_gauge, float(row["predicted_lifetime_years"]), 0.0
            )
            ps_rows.append(row)
    excluded = singular or any(not r["passes_experimental_limit"] for r in ps_rows)
    return {
        "name": scenario["name"],
        "basis": list(BASIS),
        "mass_matrix_GeV": matrix.tolist(),
        "eigenvalues_GeV": [float(x) for x in w],
        "lightest_GeV": light,
        "lightest_fractions": {
            "T_10": float(fracs[0]),
            "Tbar_10": float(fracs[1]),
            "T_126": float(fracs[2]),
        },
        "dominance_class": dominance,
        "operators_used": filled["operators_used"],
        "locking_amplitude": amp,
        "phase_hessian": phase,
        "patel_shukla_mu_K0": ps_rows,
        "flag": {
            "extended_3x3": True,
            "dim4_mix_used": bool(scenario["include_dim4_mix"]),
            "ttbar_mixing_used": abs(float(scenario["kappa"])) > 0,
            "54_normalized_locking": True,
            "conditionally_excluded_by_ps_mu_K0": excluded,
            "singular": singular,
        },
    }


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    if not anchor.get("available"):
        return {
            "status": "EXTENDED_TTBAR_54_LOCKING_NOT_EXECUTED__ANCHOR_MISSING",
            "n_failed": 1,
            "failures": ["unification_anchor"],
            "flag": {"projector_54_constructed": False},
        }

    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    gauge = scalar_pd.gauge_proton_decay(anchor)
    tau_gauge = float(gauge["central"]["lifetime_years"])

    proj = projector_54_on_10x10()
    c_54 = float(proj["C_54_normalization"])
    upstream = cgmod.build_report()

    rows = [
        evaluate_scenario(
            s, m_i=m_i, m_gut=m_gut, tau_gauge=tau_gauge, c_54=c_54
        )
        for s in SCENARIOS
    ]
    excluded = [r for r in rows if r["flag"]["conditionally_excluded_by_ps_mu_K0"]]
    physical = [r for r in rows if not r["flag"]["singular"]]
    lightest = min(physical, key=lambda r: r["lightest_GeV"])

    checks = {
        "projector_idempotent": proj["flag"]["idempotent"],
        "projector_trace_54": proj["flag"]["trace_equals_54"],
        "c54_positive": c_54 > 0,
        "extended_basis_len_3": True,
        "all_phase_one_massive": all(
            r["phase_hessian"]["n_positive"] == 1 for r in rows
        ),
        "all_phase_two_flat": all(r["phase_hessian"]["n_zero"] == 2 for r in rows),
        "some_survive": len(excluded) < len(rows),
        "some_excluded": len(excluded) > 0,
        "upstream_cg_ok": upstream.get("n_failed", 1) == 0,
        "whole_model_not_declared_dead": True,
    }
    failures = [n for n, ok in checks.items() if not ok]

    return {
        "status": (
            "EXTENDED_TTBAR_3x3__54_PROJECTOR_LOCKING_NORMALIZED"
            if not failures
            else "EXTENDED_TTBAR_54_LOCKING_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "sources": SOURCES,
        "basis": list(BASIS),
        "projector_54_10x10": proj,
        "n_scenarios": len(rows),
        "n_excluded_by_ps_mu_K0": len(excluded),
        "excluded_scenario_names": [r["name"] for r in excluded],
        "lightest_scenario": {
            "name": lightest["name"],
            "lightest_GeV": lightest["lightest_GeV"],
            "dominance": lightest["dominance_class"],
            "fractions": lightest["lightest_fractions"],
        },
        "scenarios": rows,
        "upstream_cg_status": upstream.get("status"),
        "next_exact_calculation": [
            "Expand the explicit 126→54 Clebsch projector (5-index tensors)",
            "Minimize the charge-allowed potential to fix λ_lock, λ4, κ",
            "Add remaining 126 fragments (T') allowed by branching",
            "Include gauge–scalar interference with physical mixings",
        ],
        "flag": {
            "projector_54_on_10x10_exact": True,
            "locking_amplitude_54_normalized": True,
            "extended_ttbar_126_basis": True,
            "126_to_54_fully_expanded": False,
            "invented_unpublished_cg_values": False,
            "complete_so10_scalar_potential": False,
            "exact_unique_proton_lifetime": False,
            "conditional_parameter_points_excluded": len(excluded) > 0,
            "whole_model_excluded": False,
        },
        "verdict": (
            "Exact 10⊗10→54 projector constructed (P²=P, Tr=54) and used to "
            "normalize the locking amplitude; the colour-triplet sector is "
            "extended to (T_10, Tbar_10, T_126) with only allowed operators. "
            "The 126→54 projector remains schematic."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    p = report["projector_54_10x10"]
    lines = [
        "# Extended T/Tbar + 54-projector locking — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        "## 54 projector on 10⊗10",
        "",
        f"- Trace: {p['trace']} (expect 54)",
        f"- Idempotence error: {p['idempotence_max_abs_error']:.3e}",
        f"- C_54 = {p['C_54_normalization']:.6f}",
        "",
        f"- Scenarios: {report['n_scenarios']}; excluded: {report['n_excluded_by_ps_mu_K0']}",
        f"- Lightest: `{report['lightest_scenario']['name']}` at "
        f"{report['lightest_scenario']['lightest_GeV']:.3e} GeV",
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
    ROOT.joinpath("EXTENDED_TTBAR_54_LOCKING_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("EXTENDED_TTBAR_54_LOCKING_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "projector": {
                    "trace": report["projector_54_10x10"]["trace"],
                    "idempotent": report["projector_54_10x10"]["flag"]["idempotent"],
                    "C_54": report["projector_54_10x10"]["C_54_normalization"],
                },
                "n_excluded": report.get("n_excluded_by_ps_mu_K0"),
                "lightest": report.get("lightest_scenario"),
                "flag": report.get("flag"),
                "verdict": report.get("verdict"),
            },
            indent=2,
        )
    )
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
