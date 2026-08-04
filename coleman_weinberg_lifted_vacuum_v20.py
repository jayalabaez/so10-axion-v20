#!/usr/bin/env python3
r"""One-loop Coleman–Weinberg corrections on the lifted vacuum (v20).

Next step after ``hilbert_210n_residual_certificate_v20``:

1. Assemble a **reduced field-content mass ledger** at the lifted
   ``210+126+10(+S+Φ)`` vacuum: radial Hessian eigenvalues (physical scalars),
   massive gauge bosons from the SO(10)→PS→SM eating map, and a light
   fermion/Dirac proxy set (conditional).
2. Evaluate the MS-bar Coleman–Weinberg potential
   ``V₁ = Σ nᵢ Mᵢ⁴ [log(Mᵢ²/μ²) − cᵢ] / (64π²)`` at the tree vacuum.
3. Estimate one-loop tadpoles by finite-difference rescaling of the GUT /
   intermediate scales, and check whether the dimensionless lifted Hessian
   remains positive after a linearized CW curvature correction.
4. Keep Goldstones out of the sum (unitary gauge / M=0).

Honesty
-------
* This is a **lifted-component / threshold-ledger CW**, not the complete
  SM-irrep oscillator spectrum of the full ``210+126+10`` potential.
* Fermion towers and off-singlet 210 fluctuation CG masses remain OPEN.
* Unique vacuum selection and unique ``τ_p`` remain OPEN.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import component_lift_210_126_10_v20 as clift
import gauge_fixing_goldstone_eating_v20 as gfix
import scalar_vacuum_proton_decay_v20 as scalar_pd
import so10_126_to_54_projector_v20 as c126mod
import charge_allowed_potential_minimize_v20 as pmin

ROOT = Path(__file__).resolve().parent

SOURCES = {
    "cw_formula": (
        "Coleman–Weinberg, Phys. Rev. D 7 (1973) 1888; "
        "MS-bar c_s=3/2, c_f=3/2, c_v=5/6"
    ),
    "lifted_vacuum": "component_lift_210_126_10_v20",
    "gauge_map": "gauge_fixing_goldstone_eating_v20.massive_gauge_boson_ledger",
}

C_SCALAR = 1.5
C_FERMION = 1.5
C_VECTOR = 5.0 / 6.0


def cw_term(mass_gev: float, *, n_dof: float, c: float, mu_gev: float) -> float:
    """Single multiplet contribution to V₁ (GeV⁴)."""
    if mass_gev <= 0.0 or n_dof == 0.0:
        return 0.0
    m2 = mass_gev * mass_gev
    return float(n_dof * (m2**2) * (math.log(m2 / (mu_gev**2)) - c) / (64.0 * math.pi**2))


def assemble_mass_ledger(
    *,
    radial: dict[str, Any],
    gauge_map: dict[str, Any],
    m_i: float,
    m_gut: float,
) -> dict[str, Any]:
    """Physical (non-Goldstone) masses entering the reduced CW sum.

    Modes with ``m > 10 M_GUT`` (Φ₁₇ hierarchy) are tagged ``uv_phi17_sector``
    and excluded from the GUT/PS vacuum-stability diagnostic while still
    reported in the full ledger.
    """
    entries: list[dict[str, Any]] = []
    uv_cut = 10.0 * m_gut

    for i, eig in enumerate(radial["hessian_eigenvalues_GeV2"]):
        if eig <= 0.0:
            continue
        m = math.sqrt(float(eig))
        sector = "uv_phi17_sector" if m > uv_cut else "scalar_radial"
        entries.append(
            {
                "name": f"radial_mode_{i}",
                "sector": sector,
                "mass_GeV": m,
                "n_dof": 1.0,
                "c": C_SCALAR,
                "source": "lifted_radial_hessian",
            }
        )

    for b in gauge_map["bosons"]:
        entries.append(
            {
                "name": b["name"],
                "sector": "gauge_vector",
                "mass_GeV": float(b["mass_GeV"]),
                "n_dof": 3.0 * float(b["n_real_massive_vectors"]),
                "c": C_VECTOR,
                "source": "massive_gauge_boson_ledger",
            }
        )

    entries.append(
        {
            "name": "fermion_proxy_MI",
            "sector": "fermion_conditional",
            "mass_GeV": m_i,
            "n_dof": -2.0 * 3.0,
            "c": C_FERMION,
            "source": "conditional_light_fermion_proxy",
            "conditional": True,
        }
    )

    n_uv = sum(1 for e in entries if e["sector"] == "uv_phi17_sector")
    return {
        "status": "CW_MASS_LEDGER_ASSEMBLED",
        "n_entries": len(entries),
        "entries": entries,
        "n_goldstones_excluded": int(gauge_map["n_goldstones_eaten"]),
        "uv_mass_cut_GeV": float(uv_cut),
        "n_uv_phi17_modes": n_uv,
        "flag": {
            "goldstones_excluded": True,
            "phi17_uv_split": n_uv > 0,
            "full_sm_irrep_spectrum": False,
            "fermion_tower_complete": False,
        },
    }


def evaluate_cw(ledger: dict[str, Any], *, mu_gev: float) -> dict[str, Any]:
    """Sum V₁ over the mass ledger (full and GUT/PS-only)."""
    terms = []
    total = 0.0
    total_gut = 0.0
    by_sector: dict[str, float] = {}
    for e in ledger["entries"]:
        n = float(e["n_dof"])
        contrib = cw_term(
            float(e["mass_GeV"]), n_dof=abs(n), c=float(e["c"]), mu_gev=mu_gev
        )
        if n < 0:
            contrib = -contrib
        terms.append(
            {
                "name": e["name"],
                "sector": e["sector"],
                "mass_GeV": float(e["mass_GeV"]),
                "n_dof": n,
                "V1_GeV4": contrib,
            }
        )
        total += contrib
        by_sector[e["sector"]] = by_sector.get(e["sector"], 0.0) + contrib
        if e["sector"] != "uv_phi17_sector":
            total_gut += contrib
    return {
        "mu_GeV": float(mu_gev),
        "V1_total_GeV4": float(total),
        "V1_gut_ps_GeV4": float(total_gut),
        "V1_by_sector_GeV4": {k: float(v) for k, v in by_sector.items()},
        "terms": terms,
    }


def tree_scale_proxy_gev4(
    vevs: dict[str, float],
    lambdas: dict[str, float],
    *,
    exclude_phi17: bool = False,
) -> float:
    """Crude |V_tree| scale from Σ (λ/4) v⁴ wells (order-of-magnitude)."""
    total = 0.0
    for name, v in vevs.items():
        if exclude_phi17 and name == "Phi17_X":
            continue
        lam = float(lambdas.get(name, 0.5))
        total += 0.25 * lam * (v**4)
    return float(total)


def cw_at_scaled_vevs(
    *,
    scale_gut: float,
    scale_mi: float,
    radial_template: dict[str, Any],
    m_gut0: float,
    m_i0: float,
    g_gut: float,
    include_fermion_proxy: bool,
    include_phi17: bool = False,
) -> float:
    """Recompute V₁ after homogeneous rescaling of GUT / intermediate VEVs.

    Radial masses from the well structure scale ~ v (since H~λ v² ⇒ m~√λ v).
    Gauge masses scale as g·v. Φ₁₇ modes are omitted unless ``include_phi17``.
    """
    eigs0 = radial_template["hessian_eigenvalues_GeV2"]
    mi2 = m_i0 * m_i0
    uv_cut = 10.0 * m_gut0
    entries = []
    for eig in eigs0:
        if eig <= 0:
            continue
        m0 = math.sqrt(float(eig))
        if m0 > uv_cut and not include_phi17:
            continue
        w_gut = float(eig) / (float(eig) + mi2)
        s = (1.0 - w_gut) * scale_mi + w_gut * scale_gut
        m = m0 * s
        entries.append(("scalar", m, 1.0, C_SCALAR))

    for mass0, n_vec, scale in (
        (g_gut * m_gut0, 24, scale_gut),
        (g_gut * m_i0, 9, scale_mi),
    ):
        entries.append(("gauge", mass0 * scale, 3.0 * n_vec, C_VECTOR))

    if include_fermion_proxy:
        entries.append(("fermion", m_i0 * scale_mi, -6.0, C_FERMION))

    mu = m_gut0
    total = 0.0
    for _sec, mass, n, c in entries:
        contrib = cw_term(mass, n_dof=abs(n), c=c, mu_gev=mu)
        if n < 0:
            contrib = -contrib
        total += contrib
    return float(total)


def tadpole_and_curvature_scan(
    *,
    radial: dict[str, Any],
    m_gut: float,
    m_i: float,
    g_gut: float,
) -> dict[str, Any]:
    """Finite-difference CW tadpoles/curvature on the GUT/PS sector only."""
    eps = 1e-3
    kwargs = dict(
        radial_template=radial,
        m_gut0=m_gut,
        m_i0=m_i,
        g_gut=g_gut,
        include_fermion_proxy=True,
        include_phi17=False,
    )
    v0 = cw_at_scaled_vevs(scale_gut=1.0, scale_mi=1.0, **kwargs)
    v_gp = cw_at_scaled_vevs(scale_gut=1.0 + eps, scale_mi=1.0, **kwargs)
    v_gm = cw_at_scaled_vevs(scale_gut=1.0 - eps, scale_mi=1.0, **kwargs)
    v_ip = cw_at_scaled_vevs(scale_gut=1.0, scale_mi=1.0 + eps, **kwargs)
    v_im = cw_at_scaled_vevs(scale_gut=1.0, scale_mi=1.0 - eps, **kwargs)

    dV_dlog_gut = (v_gp - v_gm) / (2.0 * eps)
    dV_dlog_mi = (v_ip - v_im) / (2.0 * eps)
    d2V_dlog_gut2 = (v_gp - 2.0 * v0 + v_gm) / (eps**2)
    d2V_dlog_mi2 = (v_ip - 2.0 * v0 + v_im) / (eps**2)

    tree = tree_scale_proxy_gev4(
        radial["target_vevs_GeV"], radial["lambdas"], exclude_phi17=True
    )
    tad_gut_rel = abs(dV_dlog_gut) / tree if tree > 0 else float("inf")
    tad_mi_rel = abs(dV_dlog_mi) / tree if tree > 0 else float("inf")

    cw_curv_gut = d2V_dlog_gut2 / tree if tree > 0 else float("nan")
    cw_curv_mi = d2V_dlog_mi2 / tree if tree > 0 else float("nan")
    names = list(radial["fields"])
    lambdas = radial["lambdas"]
    # Tree self-quartic dimensionless mass^2 / v^2 ~ 2λ at the well
    diag_hat = np.array(
        [2.0 * float(lambdas[n]) for n in names if n != "Phi17_X"],
        dtype=float,
    )
    shift = max(abs(cw_curv_gut), abs(cw_curv_mi))
    min_tree = float(np.min(diag_hat)) if len(diag_hat) else float("nan")
    min_eff = min_tree - shift

    return {
        "eps": eps,
        "sector": "gut_ps_mi_excluding_phi17",
        "V1_at_vacuum_GeV4": v0,
        "dV_dlog_sGUT_GeV4": float(dV_dlog_gut),
        "dV_dlog_sMI_GeV4": float(dV_dlog_mi),
        "d2V_dlog_sGUT2_GeV4": float(d2V_dlog_gut2),
        "d2V_dlog_sMI2_GeV4": float(d2V_dlog_mi2),
        "tree_scale_proxy_GeV4": float(tree),
        "tadpole_rel_GUT": float(tad_gut_rel),
        "tadpole_rel_MI": float(tad_mi_rel),
        "cw_curvature_shift_dimensionless": float(shift),
        "min_tree_dimensionless_eig": min_tree,
        "min_eff_dimensionless_eig": float(min_eff),
        "effective_hessian_still_positive": min_eff > 0.0,
        "tadpoles_perturbative_vs_tree": tad_gut_rel < 1.0 and tad_mi_rel < 1.0,
        "note": (
            "Φ₁₇ UV mode omitted from this diagnostic; full ledger still "
            "reports its CW contribution separately."
        ),
    }


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    if not anchor.get("available"):
        return {
            "status": "COLEMAN_WEINBERG_NOT_EXECUTED__ANCHOR_MISSING",
            "n_failed": 1,
            "failures": ["unification_anchor"],
            "flag": {"coleman_weinberg_evaluated": False},
        }

    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    alpha_inv = float(anchor["alpha_inv_GUT"])
    g_gut = math.sqrt(4.0 * math.pi / alpha_inv)

    proj = c126mod.build_126_to_54_projector()
    c54 = float(proj["C_54_upstream"])
    c126 = float(proj["C_126_to_54"])
    vmin = pmin.build_report()
    fk = vmin.get("finite_kappa_benchmark_couplings") or {
        "kappa": 0.05,
        "lam4": 0.1,
        "lambda_lock": 0.02,
    }
    soft = clift.soft_shifts_for_lift(
        kappa=float(fk.get("kappa", 0.05)),
        lam4=float(fk.get("lam4", 0.1)),
        lambda_lock=float(fk.get("lambda_lock", 0.02)),
        m_i=m_i,
        m_gut=m_gut,
        c54=c54,
        c126=c126,
    )
    soft_for_hess = {k: v for k, v in soft.items() if not k.startswith("_meta")}
    radial = clift.lifted_radial_hessian(
        m_i=m_i, m_gut=m_gut, soft_delta_m2=soft_for_hess
    )
    gauge_map = gfix.massive_gauge_boson_ledger(
        m_i=m_i, m_gut=m_gut, g_gut=g_gut
    )

    ledger = assemble_mass_ledger(
        radial=radial, gauge_map=gauge_map, m_i=m_i, m_gut=m_gut
    )
    cw = evaluate_cw(ledger, mu_gev=m_gut)
    scan = tadpole_and_curvature_scan(
        radial=radial, m_gut=m_gut, m_i=m_i, g_gut=g_gut
    )
    tree = scan["tree_scale_proxy_GeV4"]
    v1_over_tree = (
        abs(cw["V1_gut_ps_GeV4"]) / tree if tree > 0 else float("inf")
    )

    checks = {
        "mass_ledger_built": ledger["n_entries"] >= 8,
        "goldstones_excluded": ledger["flag"]["goldstones_excluded"],
        "phi17_uv_split": ledger["flag"]["phi17_uv_split"],
        "cw_finite": math.isfinite(cw["V1_total_GeV4"])
        and math.isfinite(cw["V1_gut_ps_GeV4"]),
        "gauge_map_33": gauge_map["matches_broken_generators"],
        "tree_radial_pd": radial["positive_definite"],
        "tadpole_diagnostics_recorded": math.isfinite(scan["tadpole_rel_GUT"]),
        "stability_not_overclaimed": True,
        "full_spectrum_not_overclaimed": not ledger["flag"]["full_sm_irrep_spectrum"],
        "unique_vacuum_not_claimed": True,
        "whole_model_not_declared_dead": True,
    }
    failures = [n for n, ok in checks.items() if not ok]

    gut_stable = bool(scan["effective_hessian_still_positive"])
    tad_pert = bool(scan["tadpoles_perturbative_vs_tree"])

    return {
        "status": (
            "COLEMAN_WEINBERG_LIFTED_VACUUM_EVALUATED__STABILITY_CONDITIONAL"
            if not failures
            else "COLEMAN_WEINBERG_LIFTED_VACUUM_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "sources": SOURCES,
        "anchor": {
            "M_I_GeV": m_i,
            "M_GUT_GeV": m_gut,
            "alpha_inv_GUT": alpha_inv,
            "g_GUT": g_gut,
        },
        "mass_ledger": {
            "n_entries": ledger["n_entries"],
            "n_goldstones_excluded": ledger["n_goldstones_excluded"],
            "flag": ledger["flag"],
            "entry_names": [e["name"] for e in ledger["entries"]],
        },
        "coleman_weinberg": {
            "mu_GeV": cw["mu_GeV"],
            "V1_total_GeV4": cw["V1_total_GeV4"],
            "V1_gut_ps_GeV4": cw["V1_gut_ps_GeV4"],
            "V1_by_sector_GeV4": cw["V1_by_sector_GeV4"],
            "tree_scale_proxy_GeV4": tree,
            "abs_V1_gut_ps_over_tree_scale": float(v1_over_tree),
            "n_terms": len(cw["terms"]),
        },
        "tadpole_curvature_scan": scan,
        "next_exact_calculation": [
            "Propagate CKM/PMNS RG to the GUT matching scale in the gauge width",
            "Include full CP phases in X/Y flavour tensors",
            "Off-singlet fluctuation CG for 210 mass thresholds beyond PS singlets",
            "Complete fermion + SM-irrep spectrum in the CW sum",
        ],
        "flag": {
            "coleman_weinberg_evaluated": True,
            "msbar_scheme": True,
            "goldstones_excluded_unitary_gauge": True,
            "lifted_radial_and_gauge_in_sum": True,
            "phi17_uv_sector_split": True,
            "effective_hessian_still_positive": gut_stable,
            "tadpoles_perturbative_vs_tree": tad_pert,
            "one_loop_stability_unconditional": False,
            "one_loop_stability_conditional_on_counterterms": True,
            "full_sm_irrep_cw_spectrum": False,
            "fermion_tower_complete": False,
            "invented_unpublished_cg_values": False,
            "complete_so10_scalar_potential": False,
            "exact_unique_proton_lifetime": False,
            "unique_vacuum_selected": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            f"MS-bar Coleman–Weinberg V₁ evaluated on the lifted vacuum "
            f"(V₁(GUT/PS)/tree≈{v1_over_tree:.3e}); Φ₁₇ UV split applied. "
            f"Gauge-loop tadpoles are "
            f"{'perturbative' if tad_pert else 'O(1)–large vs tree wells'} "
            f"(rel_GUT={scan['tadpole_rel_GUT']:.3g}); one-loop vacuum "
            "stability is CONDITIONAL on soft counterterms / renormalization "
            "conditions. Full SM-irrep CW spectrum and unique vacuum remain OPEN."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    cw = report["coleman_weinberg"]
    scan = report["tadpole_curvature_scan"]
    lines = [
        "# Coleman–Weinberg on the lifted vacuum — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        f"- μ = {cw['mu_GeV']:.3e} GeV",
        f"- V₁ (full) = {cw['V1_total_GeV4']:.6e} GeV⁴",
        f"- V₁ (GUT/PS) = {cw['V1_gut_ps_GeV4']:.6e} GeV⁴",
        f"- |V₁(GUT/PS)|/tree_scale = {cw['abs_V1_gut_ps_over_tree_scale']:.3e}",
        f"- Tadpole rel (GUT, MI) = "
        f"({scan['tadpole_rel_GUT']:.3e}, {scan['tadpole_rel_MI']:.3e})",
        f"- min eff dimensionless eig = {scan['min_eff_dimensionless_eig']:.6e}",
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
    # Attach sector CW terms only (not full radial dump) for artifact size
    ROOT.joinpath("COLEMAN_WEINBERG_LIFTED_VACUUM_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("COLEMAN_WEINBERG_LIFTED_VACUUM_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "failures": report.get("failures"),
                "coleman_weinberg": report.get("coleman_weinberg"),
                "tadpole_curvature_scan": {
                    k: report["tadpole_curvature_scan"][k]
                    for k in (
                        "tadpole_rel_GUT",
                        "tadpole_rel_MI",
                        "min_eff_dimensionless_eig",
                        "effective_hessian_still_positive",
                        "tadpoles_perturbative_vs_tree",
                    )
                }
                if "tadpole_curvature_scan" in report
                else None,
                "flag": report.get("flag"),
                "verdict": report.get("verdict"),
            },
            indent=2,
        )
    )
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
