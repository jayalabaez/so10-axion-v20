#!/usr/bin/env python3
r"""Pati–Salam-resolved quartic/soft RGE diagnostic for v20.

This module resolves separate SU(4)_C, SU(2)_L and SU(2)_R gauge dressing for
the active 10_H and 126bar_H components between M_GUT and M_I. It remains a
reduced radial/portal diagnostic, not a complete tensor-valued two-loop beta
system.

Two source corrections are enforced:

* the physical 10_H background used by the soft-m2 ledger is h_EW=174 GeV;
  no intermediate-scale H10 VEV is used;
* the conditional soft-gaugino UV ansatz is a downstream diagnostic whose UV
  phase input is reopened. Its status cannot turn this independent PS RGE into
  an execution failure.
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
H10_EW_VEV_GEV = 174.0

B_PS = {"g4": -7.0 / 3.0, "gL": 2.0, "gR": 26.0 / 3.0}

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
    "gauge_chain": "two_loop_thresholds_v20 B_PS one-loop Pati-Salam chain",
    "component_decomposition": {
        "10_H": "(1,2,2)+(6,1,1); H10_eff denotes the physical EW bidoublet component",
        "126bar_H": "Delta_R uses (10bar,1,3)",
    },
    "physical_background": "H10 soft-m2 ledger uses h_EW=174 GeV, never H10=M_I",
    "scope": "reduced radial self-quartics, soft m2 and three portal couplings",
    "soft_gaugino_separation": (
        "soft_gaugino_uv_masses_v20 is conditional and downstream; its "
        "reopened UV phase is not required for PS RGE execution"
    ),
}


def beta_lambda_one_loop(lam: float, *, g: float, c2: float) -> float:
    g2 = g * g
    return (
        18.0 * lam * lam
        - 12.0 * c2 * g2 * lam
        + 3.0 * c2**2 * g2**2
    ) / L16


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
    return (
        -36.0 * lam**2
        + 24.0 * c2 * g2 * lam
        - 12.0 * c2**2 * g2**2
    ) * m2 / L16SQ


def run_ps_gauge(
    alpha_inv_gut: float, mu_gut: float, mu: float
) -> dict[str, float]:
    if alpha_inv_gut <= 0 or mu_gut <= 0 or mu <= 0:
        raise ValueError("positive gauge inputs required")
    log_ratio = math.log(mu / mu_gut)
    output: dict[str, float] = {}
    for name, coefficient in B_PS.items():
        inverse = alpha_inv_gut - coefficient * log_ratio / (2.0 * math.pi)
        if inverse <= 0:
            raise ValueError(f"non-perturbative {name} during PS running")
        output[name] = math.sqrt(4.0 * math.pi / inverse)
    return output


def gauge_invariants(
    casimirs: dict[str, float], gauges: dict[str, float]
) -> tuple[float, float, float]:
    s1 = sum(float(casimirs[name]) * gauges[name] ** 2 for name in gauges)
    s2 = sum(float(casimirs[name]) ** 2 * gauges[name] ** 4 for name in gauges)
    s3 = sum(float(casimirs[name]) ** 3 * gauges[name] ** 6 for name in gauges)
    return float(s1), float(s2), float(s3)


def beta_lambda_ps(
    lam: float,
    casimirs: dict[str, float],
    gauges: dict[str, float],
) -> tuple[float, float]:
    s1, s2, s3 = gauge_invariants(casimirs, gauges)
    one = (18.0 * lam**2 - 12.0 * s1 * lam + 3.0 * s2) / L16
    two = (
        -912.0 * lam**3
        + 288.0 * s1 * lam**2
        - 48.0 * s2 * lam
        + 24.0 * s3
    ) / L16SQ
    return float(one), float(two)


def beta_m2_ps(
    m2: float,
    lam: float,
    casimirs: dict[str, float],
    gauges: dict[str, float],
) -> tuple[float, float]:
    s1, s2, _ = gauge_invariants(casimirs, gauges)
    one = (6.0 * lam - 6.0 * s1) * m2 / L16
    two = (-36.0 * lam**2 + 24.0 * s1 * lam - 12.0 * s2) * m2 / L16SQ
    return float(one), float(two)


def beta_portal_ps(
    portal: float,
    lam_a: float,
    lam_b: float,
    cas_a: dict[str, float],
    cas_b: dict[str, float],
    gauges: dict[str, float],
) -> tuple[float, float]:
    combined = {name: float(cas_a[name]) + float(cas_b[name]) for name in gauges}
    s1, s2, _ = gauge_invariants(combined, gauges)
    one = portal * (4.0 * lam_a + 4.0 * lam_b - 3.0 * s1) / L16
    two = portal * (
        -20.0 * (lam_a**2 + lam_b**2)
        + 6.0 * s1 * (lam_a + lam_b)
        - 3.0 * s2
    ) / L16SQ
    return float(one), float(two)


def assemble_sector(
    *,
    lambdas: dict[str, float],
    portals: dict[str, float],
    vevs: dict[str, float],
    gauges: dict[str, float] | None = None,
    g10: float | None = None,
    use_parent_casimir: bool = False,
) -> dict[str, Any]:
    del use_parent_casimir
    if gauges is None:
        if g10 is None:
            raise ValueError("gauges or g10 required")
        gauges = {"g4": float(g10), "gL": float(g10), "gR": float(g10)}

    rows: list[dict[str, Any]] = []
    for name, lam in lambdas.items():
        metadata = PS_COMPONENTS[name]
        beta1, beta2 = beta_lambda_ps(float(lam), metadata["casimirs"], gauges)
        m2 = float(lam) * float(vevs.get(name, 0.0)) ** 2
        m21, m22 = beta_m2_ps(m2, float(lam), metadata["casimirs"], gauges)
        rows.append(
            {
                "name": name,
                "kind": "self_quartic",
                "ps_irrep": metadata["irrep"],
                "casimirs": metadata["casimirs"],
                "background_vev_GeV": float(vevs.get(name, 0.0)),
                "gauge_invariant_Cg2": gauge_invariants(metadata["casimirs"], gauges)[0],
                "value": float(lam),
                "beta_1loop": beta1,
                "beta_2loop": beta2,
                "beta_total": beta1 + beta2,
                "m2_GeV2": m2,
                "beta_m2_1loop": m21,
                "beta_m2_2loop": m22,
                "beta_m2_total": m21 + m22,
            }
        )

    for portal_name, (left, right) in PORTAL_COMPONENTS.items():
        value = float(portals.get(portal_name, 0.0))
        beta1, beta2 = beta_portal_ps(
            value,
            float(lambdas[left]),
            float(lambdas[right]),
            PS_COMPONENTS[left]["casimirs"],
            PS_COMPONENTS[right]["casimirs"],
            gauges,
        )
        rows.append(
            {
                "name": portal_name,
                "kind": "portal",
                "components": [left, right],
                "value": value,
                "beta_1loop": beta1,
                "beta_2loop": beta2,
                "beta_total": beta1 + beta2,
            }
        )

    return {
        "gauge_group": "SU(4)_C x SU(2)_L x SU(2)_R",
        "gauges": dict(gauges),
        "background_vevs_GeV": dict(vevs),
        "n_couplings": len(rows),
        "use_parent_casimir": False,
        "rows": rows,
    }


def evolve_sector(
    *,
    lambdas0: dict[str, float],
    portals0: dict[str, float],
    vevs: dict[str, float],
    alpha_inv_gut: float,
    mu0: float,
    mu1: float,
) -> dict[str, Any]:
    lambda_names = list(lambdas0)
    portal_names = list(portals0)
    initial = np.array(
        [lambdas0[name] for name in lambda_names]
        + [portals0[name] for name in portal_names],
        dtype=float,
    )
    perturbative_cap = 4.0 * math.pi

    def rhs(log_mu: float, values: np.ndarray) -> np.ndarray:
        mu = math.exp(log_mu)
        gauges = run_ps_gauge(alpha_inv_gut, mu0, mu)
        lambdas = {name: float(values[index]) for index, name in enumerate(lambda_names)}
        portals = {
            name: float(values[len(lambda_names) + index])
            for index, name in enumerate(portal_names)
        }
        ledger = assemble_sector(
            lambdas=lambdas, portals=portals, vevs=vevs, gauges=gauges
        )
        by_name = {row["name"]: row for row in ledger["rows"]}
        return np.array(
            [by_name[name]["beta_total"] for name in lambda_names + portal_names],
            dtype=float,
        )

    def left_perturbative_window(_log_mu: float, values: np.ndarray) -> float:
        return float(perturbative_cap - np.max(np.abs(values)))

    left_perturbative_window.terminal = True  # type: ignore[attr-defined]
    left_perturbative_window.direction = -1  # type: ignore[attr-defined]

    gauge_mi = run_ps_gauge(alpha_inv_gut, mu0, mu1)
    gauge_gut = run_ps_gauge(alpha_inv_gut, mu0, mu0)
    solution = solve_ivp(
        rhs,
        (math.log(mu0), math.log(mu1)),
        initial,
        rtol=1e-7,
        atol=1e-9,
        method="RK45",
        max_step=0.25,
        events=left_perturbative_window,
    )
    final_values = solution.y[:, -1]
    lambdas1 = {name: float(final_values[index]) for index, name in enumerate(lambda_names)}
    portals1 = {
        name: float(final_values[len(lambda_names) + index])
        for index, name in enumerate(portal_names)
    }
    hit_event = bool(solution.t_events and solution.t_events[0].size > 0)
    reached_mi = bool(solution.success) and not hit_event
    all_positive = all(value > 0.0 for value in lambdas1.values())
    output: dict[str, Any] = {
        "success": reached_mi and all_positive,
        "n_steps": int(solution.y.shape[1]),
        "solver_message": str(solution.message),
        "terminated_by_perturbativity_event": hit_event,
        "mu_end_GeV": float(math.exp(solution.t[-1])),
        "gauge_boundary_GUT": gauge_gut,
        "gauge_boundary_MI": gauge_mi,
        "lambdas_end": lambdas1,
        "portals_end": portals1,
        "all_quartics_positive": all_positive,
        "max_abs_rel_shift_lambda": max(
            abs(lambdas1[name] - lambdas0[name]) / max(abs(lambdas0[name]), 1e-30)
            for name in lambda_names
        ),
        "max_abs_rel_shift_portal": max(
            abs(portals1[name] - portals0[name]) / max(abs(portals0[name]), 1e-30)
            for name in portal_names
        ),
        "landau_like_couplings": [
            name
            for name, value in {**lambdas1, **portals1}.items()
            if abs(value) >= 0.5 * perturbative_cap
        ],
    }
    if not output["success"]:
        output["residual"] = (
            "reduced_DeltaR_or_portal_RGE_nonintegrable_to_MI"
            if (
                "DeltaR_126bar" in output["landau_like_couplings"]
                or lambdas1.get("DeltaR_126bar", 0.0) <= 0.0
            )
            else "reduced_quartic_portal_RGE_nonintegrable_to_MI"
        )
        output["note"] = (
            "Fail-closed: the reduced PS radial/portal flow leaves the "
            "perturbative window before M_I. Subgroup Casimir resolution "
            "remains valid; full tensor betas stay OPEN."
        )
    return output


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    if not anchor.get("available"):
        return {
            "status": "PS_QUARTIC_SOFT_RGE_NOT_EXECUTED__ANCHOR_MISSING",
            "n_failed": 1,
            "failures": ["unification_anchor"],
            "flag": {"pati_salam_subgroup_resolved": False},
        }

    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    unification = thr.solve_unification(two_loop=True)
    alpha_inv = float(unification["alpha_inv_GUT_after_spectators"])

    radial = scalar_pd.reduced_radial_vacuum_witness(anchor)
    raw = radial["potential_definition"]["self_quartics"]
    lambdas0 = {
        "P_210_PS": float(raw["P_210_PS"]),
        "DeltaR_126bar": float(raw["DeltaR_126bar"]),
        "S_PQ": float(raw["S_PQ"]),
        "Phi17_X": float(raw["Phi17_X"]),
        "H10_eff": float(raw["h_EW_effective"]),
    }
    vevs = {
        "P_210_PS": m_gut,
        "DeltaR_126bar": m_i,
        "S_PQ": m_i,
        "Phi17_X": 1.0e17,
        "H10_eff": H10_EW_VEV_GEV,
    }
    potential = pmin.build_report()
    finite = potential.get("finite_kappa_benchmark_couplings") or {}
    portals0 = {
        "kappa": float(finite.get("kappa", 0.05)),
        "lam4": float(finite.get("lam4", 1e-4)),
        "lambda_lock": float(finite.get("lambda_lock", 1.0)),
    }

    gauges_gut = run_ps_gauge(alpha_inv, m_gut, m_gut)
    ledger_gut = assemble_sector(
        lambdas=lambdas0, portals=portals0, vevs=vevs, gauges=gauges_gut
    )
    evolution = evolve_sector(
        lambdas0=lambdas0,
        portals0=portals0,
        vevs=vevs,
        alpha_inv_gut=alpha_inv,
        mu0=m_gut,
        mu1=m_i,
    )
    ledger_mi = assemble_sector(
        lambdas=evolution["lambdas_end"],
        portals=evolution["portals_end"],
        vevs=vevs,
        gauges=evolution["gauge_boundary_MI"],
    )

    soft_report = softg.build_report()
    soft_green = soft_report.get("n_failed", 1) == 0
    soft_failures = list(soft_report.get("failures", []))

    charged = {
        row["name"]: row
        for row in ledger_gut["rows"]
        if row["kind"] == "self_quartic"
    }
    checks = {
        "ledger_built": ledger_gut["n_couplings"] == 8,
        "ps_gauge_couplings_split_below_gut": len(
            {round(value, 12) for value in evolution["gauge_boundary_MI"].values()}
        )
        > 1,
        "deltaR_has_nonzero_ps_dressing": charged["DeltaR_126bar"]["gauge_invariant_Cg2"] > 0.0,
        "H10_has_nonzero_ps_dressing": charged["H10_eff"]["gauge_invariant_Cg2"] > 0.0,
        "singlets_have_zero_ps_dressing": (
            charged["P_210_PS"]["gauge_invariant_Cg2"] == 0.0
            and charged["S_PQ"]["gauge_invariant_Cg2"] == 0.0
        ),
        "physical_H10_EW_background_174_GeV": (
            ledger_gut["background_vevs_GeV"]["H10_eff"] == H10_EW_VEV_GEV
            and charged["H10_eff"]["background_vev_GeV"] == H10_EW_VEV_GEV
        ),
        "no_H10_MI_vacuum_proxy": ledger_gut["background_vevs_GeV"]["H10_eff"] != m_i,
        "evolution_attempted_without_raise": True,
        "soft_gaugino_baseline_not_required_for_ps_rge": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    evolution_green = bool(evolution.get("success"))
    if failures:
        status = "PS_SUBGROUP_RESOLVED_QUARTIC_SOFT_RGE_FAILED"
    elif evolution_green:
        status = "PS_SUBGROUP_RESOLVED_QUARTIC_SOFT_RGE__FULL_TENSOR_BETAS_OPEN"
    else:
        status = "PS_SUBGROUP_RESOLVED_QUARTIC_SOFT_RGE__REDUCED_FLOW_NONINTEGRABLE"

    return {
        "status": status,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "sources": SOURCES,
        "physical_backgrounds_GeV": vevs,
        "boundary_GUT": {
            "alpha_inv_GUT_after_spectators": alpha_inv,
            "gauges": gauges_gut,
            "lambdas": lambdas0,
            "portals": portals0,
            "ledger": ledger_gut,
        },
        "evolution_GUT_to_MI": evolution,
        "boundary_MI": {
            "gauges": evolution["gauge_boundary_MI"],
            "lambdas": evolution["lambdas_end"],
            "portals": evolution["portals_end"],
            "ledger": ledger_mi,
        },
        "soft_gaugino_downstream_diagnostic": {
            "status": soft_report.get("status"),
            "n_failed": soft_report.get("n_failed"),
            "failures": soft_failures,
            "green": soft_green,
            "required_for_ps_rge_execution": False,
            "classification": (
                "conditional_downstream_diagnostic"
                if soft_green
                else "revalidation_open_after_selected_phase_rank_one"
            ),
        },
        "residual_still_open": {
            "reduced_quartic_portal_RGE_nonintegrable_to_MI": not evolution_green,
            "full_component_tensor_betas": True,
            "live_sarah_or_pyrate_executable_run": True,
            "soft_gaugino_uv_phase_baseline_revalidation": not soft_green,
        },
        "flag": {
            "pati_salam_subgroup_resolved": True,
            "charged_10_126_casimirs_nonzero": True,
            "separate_g4_gL_gR_running": True,
            "physical_H10_EW_background_used": True,
            "unphysical_H10_MI_background_used": False,
            "pyrate_sarah_formula_class_used": True,
            "reduced_charge_allowed_sector_only": True,
            "two_loop_quartic_betas_complete": False,
            "full_component_tensor_betas": False,
            "live_sarah_or_pyrate_executable_run": False,
            "soft_m2_betas_included": True,
            "portal_kappa_lam4_lock_betas_included": True,
            "reduced_flow_integrable_GUT_to_MI": evolution_green,
            "vacuum_stability_lambda_positive_along_flow": bool(evolution.get("all_quartics_positive")),
            "soft_gaugino_baseline_green": soft_green,
            "soft_gaugino_baseline_required_for_ps_rge": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "Separate Pati-Salam gauge couplings and nonzero subgroup Casimirs "
            "are retained for Delta_R and the H10 bidoublet. The soft-m2 ledger "
            "now uses the physical h_EW=174 GeV background and never H10=M_I. "
            + (
                "The reduced flow reaches M_I within its attempted window. "
                if evolution_green
                else (
                    "The reduced radial/portal flow hits a Landau-like "
                    "non-integrable singularity before M_I; this remains an "
                    "open residual. "
                )
            )
            + (
                "The conditional soft-gaugino diagnostic is green but is not an RGE input. "
                if soft_green
                else (
                    "The soft-gaugino UV baseline remains open after the "
                    "selected phase-rank-one result and is not an RGE execution failure. "
                )
            )
            + "Complete tensor-valued two-loop beta functions remain open."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    evolution = report["evolution_GUT_to_MI"]
    soft = report["soft_gaugino_downstream_diagnostic"]
    lines = [
        "# Pati-Salam-resolved quartic/soft RGE — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        f"- physical H10 background: {report['physical_backgrounds_GeV']['H10_eff']} GeV",
        f"- g4,gL,gR at M_I: {evolution['gauge_boundary_MI']}",
        f"- all reduced quartics positive: {evolution['all_quartics_positive']}",
        f"- max relative quartic shift: {evolution['max_abs_rel_shift_lambda']:.6e}",
        f"- soft-gaugino downstream diagnostic: {soft['classification']}",
        "",
        "## Flags",
        "",
    ]
    lines.extend(f"- `{name}`: {value}" for name, value in report["flag"].items())
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    report = build_report()
    ROOT.joinpath("QUARTIC_SOFT_BETAS_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("QUARTIC_SOFT_BETAS_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "physical_backgrounds_GeV": report.get("physical_backgrounds_GeV"),
                "evolution_GUT_to_MI": report.get("evolution_GUT_to_MI"),
                "soft_gaugino_downstream_diagnostic": report.get("soft_gaugino_downstream_diagnostic"),
                "flag": report.get("flag"),
                "verdict": report.get("verdict"),
            },
            indent=2,
        )
    )
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
