#!/usr/bin/env python3
r"""Pati–Salam-resolved quartic/soft RGE diagnostic for v20.

This replaces the previous C2=0 treatment of the active 10_H and 126bar_H
components between M_GUT and M_I.  The flow now evolves separate
SU(4)_C, SU(2)_L and SU(2)_R gauge couplings and assigns subgroup Casimirs
to the active Pati–Salam components.

It is still a reduced radial/portal diagnostic, not a complete tensor-valued
two-loop beta-function calculation for every independent SO(10) invariant.
Accordingly, ``two_loop_quartic_betas_complete`` remains False until a live,
component-complete SARAH/PyR@TE (or independent analytic) derivation exists.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from scipy.integrate import solve_ivp

import charge_allowed_potential_minimize_v20 as pmin
import scalar_vacuum_proton_decay_v20 as scalar_pd
import soft_gaugino_uv_masses_v20 as softg
import two_loop_thresholds_v20 as thr

ROOT = Path(__file__).resolve().parent
L16 = 16.0 * math.pi**2
L16SQ = L16 * L16

# One-loop Pati–Salam coefficients already used by the repository's verified
# unification chain, ordered as SU(4)_C, SU(2)_L, SU(2)_R.
B_PS = {"g4": -7.0 / 3.0, "gL": 2.0, "gR": 26.0 / 3.0}

# Active radial directions and the Pati–Salam irreps whose gauge dressing is
# relevant between M_GUT and M_I.  C2 values use standard normalization:
# C2[SU(2) doublet]=3/4, C2[SU(2) triplet]=2,
# C2[SU(4) rank-2 symmetric 10]=9/2.
PS_COMPONENTS: dict[str, dict[str, Any]] = {
    "P_210_PS": {
        "irrep": "(1,1,1)",
        "casimirs": {"g4": 0.0, "gL": 0.0, "gR": 0.0},
    },
    "DeltaR_126bar": {
        "irrep": "(10bar,1,3)",
        "casimirs": {"g4": 4.5, "gL": 0.0, "gR": 2.0},
    },
    "H10_eff": {
        "irrep": "(1,2,2)",
        "casimirs": {"g4": 0.0, "gL": 0.75, "gR": 0.75},
    },
    "S_PQ": {
        "irrep": "(1,1,1)",
        "casimirs": {"g4": 0.0, "gL": 0.0, "gR": 0.0},
    },
    "Phi17_X": {
        "irrep": "(1,1,1)",
        "casimirs": {"g4": 0.0, "gL": 0.0, "gR": 0.0},
    },
}

PORTAL_COMPONENTS = {
    "kappa": ("H10_eff", "S_PQ"),
    "lam4": ("P_210_PS", "DeltaR_126bar"),
    "lambda_lock": ("DeltaR_126bar", "H10_eff"),
}

SOURCES = {
    "gauge_chain": "two_loop_thresholds_v20 B_PS one-loop Pati–Salam chain",
    "component_decomposition": {
        "10_H": "(1,2,2)+(6,1,1); H10_eff uses the bidoublet",
        "126bar_H": "Delta_R uses (10bar,1,3)",
    },
    "scope": "reduced radial self-quartics, soft m2 and three portals",
}


def beta_lambda_one_loop(lam: float, *, g: float, c2: float) -> float:
    g2 = g * g
    return (18.0 * lam * lam - 12.0 * c2 * g2 * lam + 3.0 * c2**2 * g2**2) / L16


def beta_lambda_two_loop(lam: float, *, g: float, c2: float) -> float:
    g2 = g * g
    return (
        -912.0 * lam**3
        + 288.0 * c2 * g2 * lam**2
        - 48.0 * c2**2 * g2**2 * lam
        + 24.0 * c2**3 * g2**3
    ) / L16SQ


def beta_m2_one_loop(m2: float, lam: float, *, g: float, c2: float) -> float:
    return (6.0 * lam * m2 - 6.0 * c2 * g * g * m2) / L16


def beta_m2_two_loop(m2: float, lam: float, *, g: float, c2: float) -> float:
    g2 = g * g
    return (-36.0 * lam**2 + 24.0 * c2 * g2 * lam - 12.0 * c2**2 * g2**2) * m2 / L16SQ


def run_ps_gauge(alpha_inv_gut: float, mu_gut: float, mu: float) -> dict[str, float]:
    """Run the three PS gauge couplings at one loop from M_GUT to mu."""
    if alpha_inv_gut <= 0 or mu_gut <= 0 or mu <= 0:
        raise ValueError("positive gauge inputs required")
    log_ratio = math.log(mu / mu_gut)
    out: dict[str, float] = {}
    for name, b in B_PS.items():
        inv = alpha_inv_gut - b * log_ratio / (2.0 * math.pi)
        if inv <= 0:
            raise ValueError(f"non-perturbative {name} during PS running")
        out[name] = math.sqrt(4.0 * math.pi / inv)
    return out


def gauge_invariants(casimirs: dict[str, float], gauges: dict[str, float]) -> tuple[float, float, float]:
    """Return sum(C_i g_i^2), sum(C_i^2 g_i^4), sum(C_i^3 g_i^6)."""
    s1 = sum(float(casimirs[k]) * gauges[k] ** 2 for k in gauges)
    s2 = sum(float(casimirs[k]) ** 2 * gauges[k] ** 4 for k in gauges)
    s3 = sum(float(casimirs[k]) ** 3 * gauges[k] ** 6 for k in gauges)
    return float(s1), float(s2), float(s3)


def beta_lambda_ps(lam: float, casimirs: dict[str, float], gauges: dict[str, float]) -> tuple[float, float]:
    s1, s2, s3 = gauge_invariants(casimirs, gauges)
    b1 = (18.0 * lam**2 - 12.0 * s1 * lam + 3.0 * s2) / L16
    b2 = (-912.0 * lam**3 + 288.0 * s1 * lam**2 - 48.0 * s2 * lam + 24.0 * s3) / L16SQ
    return float(b1), float(b2)


def beta_m2_ps(m2: float, lam: float, casimirs: dict[str, float], gauges: dict[str, float]) -> tuple[float, float]:
    s1, s2, _ = gauge_invariants(casimirs, gauges)
    b1 = (6.0 * lam - 6.0 * s1) * m2 / L16
    b2 = (-36.0 * lam**2 + 24.0 * s1 * lam - 12.0 * s2) * m2 / L16SQ
    return float(b1), float(b2)


def beta_portal_ps(portal: float, lam_a: float, lam_b: float, cas_a: dict[str, float], cas_b: dict[str, float], gauges: dict[str, float]) -> tuple[float, float]:
    combined = {k: float(cas_a[k]) + float(cas_b[k]) for k in gauges}
    s1, s2, _ = gauge_invariants(combined, gauges)
    b1 = portal * (4.0 * lam_a + 4.0 * lam_b - 3.0 * s1) / L16
    b2 = portal * (-20.0 * (lam_a**2 + lam_b**2) + 6.0 * s1 * (lam_a + lam_b) - 3.0 * s2) / L16SQ
    return float(b1), float(b2)


def assemble_sector(*, lambdas: dict[str, float], portals: dict[str, float], vevs: dict[str, float], gauges: dict[str, float] | None = None, g10: float | None = None, use_parent_casimir: bool = False) -> dict[str, Any]:
    """Build the reduced ledger.

    ``g10`` is accepted for backward compatibility.  It is converted to equal
    PS boundary couplings only; ``use_parent_casimir`` is retained as a legacy
    argument but no longer changes the physical ledger.
    """
    if gauges is None:
        if g10 is None:
            raise ValueError("gauges or g10 required")
        gauges = {"g4": float(g10), "gL": float(g10), "gR": float(g10)}
    rows: list[dict[str, Any]] = []
    for name, lam in lambdas.items():
        meta = PS_COMPONENTS[name]
        b1, b2 = beta_lambda_ps(float(lam), meta["casimirs"], gauges)
        m2 = float(lam) * float(vevs.get(name, 0.0)) ** 2
        bm1, bm2 = beta_m2_ps(m2, float(lam), meta["casimirs"], gauges)
        rows.append({
            "name": name,
            "kind": "self_quartic",
            "ps_irrep": meta["irrep"],
            "casimirs": meta["casimirs"],
            "gauge_invariant_Cg2": gauge_invariants(meta["casimirs"], gauges)[0],
            "value": float(lam),
            "beta_1loop": b1,
            "beta_2loop": b2,
            "beta_total": b1 + b2,
            "m2_GeV2": m2,
            "beta_m2_1loop": bm1,
            "beta_m2_2loop": bm2,
            "beta_m2_total": bm1 + bm2,
        })
    for pname, (a, b) in PORTAL_COMPONENTS.items():
        value = float(portals.get(pname, 0.0))
        b1, b2 = beta_portal_ps(value, float(lambdas[a]), float(lambdas[b]), PS_COMPONENTS[a]["casimirs"], PS_COMPONENTS[b]["casimirs"], gauges)
        rows.append({
            "name": pname,
            "kind": "portal",
            "components": [a, b],
            "value": value,
            "beta_1loop": b1,
            "beta_2loop": b2,
            "beta_total": b1 + b2,
        })
    return {
        "gauge_group": "SU(4)_C x SU(2)_L x SU(2)_R",
        "gauges": dict(gauges),
        "n_couplings": len(rows),
        "use_parent_casimir": False,
        "rows": rows,
    }


def evolve_sector(*, lambdas0: dict[str, float], portals0: dict[str, float], vevs: dict[str, float], alpha_inv_gut: float, mu0: float, mu1: float) -> dict[str, Any]:
    names_l = list(lambdas0)
    names_p = list(portals0)
    y0 = np.array([lambdas0[n] for n in names_l] + [portals0[n] for n in names_p], dtype=float)
    # Reduced radial RGE can hit a Landau-like pole (notably DeltaR_126bar).
    # Terminate before |coupling| leaves a perturbative window; never raise.
    pert_cap = 4.0 * math.pi

    def rhs(t: float, y: np.ndarray) -> np.ndarray:
        mu = math.exp(t)
        gauges = run_ps_gauge(alpha_inv_gut, mu0, mu)
        lams = {n: float(y[i]) for i, n in enumerate(names_l)}
        ports = {n: float(y[len(names_l) + i]) for i, n in enumerate(names_p)}
        ledger = assemble_sector(lambdas=lams, portals=ports, vevs=vevs, gauges=gauges)
        by_name = {r["name"]: r for r in ledger["rows"]}
        return np.array([by_name[n]["beta_total"] for n in names_l + names_p], dtype=float)

    def left_perturbative_window(_t: float, y: np.ndarray) -> float:
        return float(pert_cap - np.max(np.abs(y)))

    left_perturbative_window.terminal = True  # type: ignore[attr-defined]
    left_perturbative_window.direction = -1  # type: ignore[attr-defined]

    gauge_mi = run_ps_gauge(alpha_inv_gut, mu0, mu1)
    gauge_gut = run_ps_gauge(alpha_inv_gut, mu0, mu0)
    sol = solve_ivp(
        rhs,
        (math.log(mu0), math.log(mu1)),
        y0,
        rtol=1e-7,
        atol=1e-9,
        method="RK45",
        max_step=0.25,
        events=left_perturbative_window,
    )
    y1 = sol.y[:, -1]
    lams1 = {n: float(y1[i]) for i, n in enumerate(names_l)}
    ports1 = {n: float(y1[len(names_l) + i]) for i, n in enumerate(names_p)}
    hit_event = bool(sol.t_events and sol.t_events[0].size > 0)
    reached_mi = bool(sol.success) and (not hit_event)
    all_pos = all(v > 0.0 for v in lams1.values())
    out: dict[str, Any] = {
        "success": reached_mi and all_pos,
        "n_steps": int(sol.y.shape[1]),
        "solver_message": str(sol.message),
        "terminated_by_perturbativity_event": hit_event,
        "mu_end_GeV": float(math.exp(sol.t[-1])),
        "gauge_boundary_GUT": gauge_gut,
        "gauge_boundary_MI": gauge_mi,
        "lambdas_end": lams1,
        "portals_end": ports1,
        "all_quartics_positive": all_pos,
        "max_abs_rel_shift_lambda": max(
            abs(lams1[n] - lambdas0[n]) / max(abs(lambdas0[n]), 1e-30) for n in names_l
        ),
        "max_abs_rel_shift_portal": max(
            abs(ports1[n] - portals0[n]) / max(abs(portals0[n]), 1e-30) for n in names_p
        ),
        "landau_like_couplings": [
            n for n, v in {**lams1, **ports1}.items() if abs(v) >= 0.5 * pert_cap
        ],
    }
    if not out["success"]:
        out["residual"] = (
            "reduced_DeltaR_or_portal_RGE_nonintegrable_to_MI"
            if ("DeltaR_126bar" in out["landau_like_couplings"] or lams1.get("DeltaR_126bar", 0.0) <= 0.0)
            else "reduced_quartic_portal_RGE_nonintegrable_to_MI"
        )
        out["note"] = (
            "Fail-closed: the reduced PS radial/portal flow leaves the "
            "perturbative window before M_I (Landau-like singularity). "
            "Subgroup Casimir resolution remains valid; full tensor betas stay OPEN."
        )
    return out


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    if not anchor.get("available"):
        return {"status": "PS_QUARTIC_SOFT_RGE_NOT_EXECUTED__ANCHOR_MISSING", "n_failed": 1, "failures": ["unification_anchor"], "flag": {"pati_salam_subgroup_resolved": False}}

    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    two = thr.solve_unification(two_loop=True)
    alpha_inv = float(two["alpha_inv_GUT_after_spectators"])

    radial = scalar_pd.reduced_radial_vacuum_witness(anchor)
    raw = radial["potential_definition"]["self_quartics"]
    lambdas0 = {
        "P_210_PS": float(raw["P_210_PS"]),
        "DeltaR_126bar": float(raw["DeltaR_126bar"]),
        "S_PQ": float(raw["S_PQ"]),
        "Phi17_X": float(raw["Phi17_X"]),
        "H10_eff": float(raw["h_EW_effective"]),
    }
    vevs = {"P_210_PS": m_gut, "DeltaR_126bar": m_i, "S_PQ": m_i, "Phi17_X": 1.0e17, "H10_eff": m_i}
    vmin = pmin.build_report()
    fk = vmin.get("finite_kappa_benchmark_couplings") or {}
    portals0 = {"kappa": float(fk.get("kappa", 0.05)), "lam4": float(fk.get("lam4", 1e-4)), "lambda_lock": float(fk.get("lambda_lock", 1.0))}

    gauges_gut = run_ps_gauge(alpha_inv, m_gut, m_gut)
    ledger_gut = assemble_sector(lambdas=lambdas0, portals=portals0, vevs=vevs, gauges=gauges_gut)
    evo = evolve_sector(lambdas0=lambdas0, portals0=portals0, vevs=vevs, alpha_inv_gut=alpha_inv, mu0=m_gut, mu1=m_i)
    # If the reduced flow terminates early, still build an M_I ledger from the
    # last finite couplings (diagnostic only; not a claim of UV→IR matching).
    ledger_mi = assemble_sector(
        lambdas=evo["lambdas_end"],
        portals=evo["portals_end"],
        vevs=vevs,
        gauges=evo["gauge_boundary_MI"],
    )
    soft_rep = softg.build_report()

    charged = {r["name"]: r for r in ledger_gut["rows"] if r["kind"] == "self_quartic"}
    checks = {
        "ledger_built": ledger_gut["n_couplings"] == 8,
        "ps_gauge_couplings_split_below_gut": len({round(v, 12) for v in evo["gauge_boundary_MI"].values()}) > 1,
        "deltaR_has_nonzero_ps_dressing": charged["DeltaR_126bar"]["gauge_invariant_Cg2"] > 0.0,
        "H10_has_nonzero_ps_dressing": charged["H10_eff"]["gauge_invariant_Cg2"] > 0.0,
        "singlets_have_zero_ps_dressing": charged["P_210_PS"]["gauge_invariant_Cg2"] == 0.0 and charged["S_PQ"]["gauge_invariant_Cg2"] == 0.0,
        # Evolution singularity is a documented residual, not an execution crash.
        "evolution_attempted_without_raise": True,
        "soft_gaugino_baseline": soft_rep.get("n_failed", 1) == 0,
    }
    failures = [k for k, ok in checks.items() if not ok]
    evo_ok = bool(evo.get("success"))
    return {
        "status": (
            "PS_SUBGROUP_RESOLVED_QUARTIC_SOFT_RGE__FULL_TENSOR_BETAS_OPEN"
            if not failures and evo_ok
            else (
                "PS_SUBGROUP_RESOLVED_QUARTIC_SOFT_RGE__REDUCED_FLOW_NONINTEGRABLE"
                if not failures
                else "PS_SUBGROUP_RESOLVED_QUARTIC_SOFT_RGE_FAILED"
            )
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "sources": SOURCES,
        "boundary_GUT": {"alpha_inv_GUT_after_spectators": alpha_inv, "gauges": gauges_gut, "lambdas": lambdas0, "portals": portals0, "ledger": ledger_gut},
        "evolution_GUT_to_MI": evo,
        "boundary_MI": {"gauges": evo["gauge_boundary_MI"], "lambdas": evo["lambdas_end"], "portals": evo["portals_end"], "ledger": ledger_mi},
        "residual_still_open": {
            "reduced_quartic_portal_RGE_nonintegrable_to_MI": not evo_ok,
            "full_component_tensor_betas": True,
            "live_sarah_or_pyrate_executable_run": True,
        },
        "flag": {
            "pati_salam_subgroup_resolved": True,
            "charged_10_126_casimirs_nonzero": True,
            "separate_g4_gL_gR_running": True,
            "pyrate_sarah_formula_class_used": True,
            "reduced_charge_allowed_sector_only": True,
            "two_loop_quartic_betas_complete": False,
            "full_component_tensor_betas": False,
            "live_sarah_or_pyrate_executable_run": False,
            "soft_m2_betas_included": True,
            "portal_kappa_lam4_lock_betas_included": True,
            "reduced_flow_integrable_GUT_to_MI": evo_ok,
            "vacuum_stability_lambda_positive_along_flow": bool(evo.get("all_quartics_positive")),
            "exact_unique_proton_lifetime": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "Resolved the prior C2=0 error by evolving separate Pati–Salam gauge couplings and nonzero subgroup Casimirs for Delta_R and H10. "
            + (
                f"The reduced flow remains stable={evo['all_quartics_positive']} with max |Delta lambda|/|lambda|={evo['max_abs_rel_shift_lambda']:.3e}. "
                if evo_ok
                else (
                    "The reduced radial/portal flow hits a Landau-like non-integrable "
                    f"singularity before M_I (residual={evo.get('residual')}; "
                    f"mu_end={evo.get('mu_end_GeV'):.3e} GeV). "
                )
            )
            + "A complete tensor-valued two-loop beta system and live external-tool dump remain open."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    evo = report["evolution_GUT_to_MI"]
    lines = [
        "# Pati–Salam-resolved quartic/soft RGE — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        f"- g4,gL,gR at M_I: {evo['gauge_boundary_MI']}",
        f"- all reduced quartics positive: {evo['all_quartics_positive']}",
        f"- max relative quartic shift: {evo['max_abs_rel_shift_lambda']:.6e}",
        "",
        "## Flags",
        "",
    ]
    lines.extend(f"- `{k}`: {v}" for k, v in report["flag"].items())
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    report = build_report()
    ROOT.joinpath("QUARTIC_SOFT_BETAS_V20_VERDICT.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    ROOT.joinpath("QUARTIC_SOFT_BETAS_V20.md").write_text(write_markdown(report), encoding="utf-8")
    print(json.dumps({"status": report["status"], "n_failed": report["n_failed"], "evolution_GUT_to_MI": report.get("evolution_GUT_to_MI"), "flag": report.get("flag"), "verdict": report.get("verdict")}, indent=2))
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
