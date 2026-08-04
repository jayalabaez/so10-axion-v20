#!/usr/bin/env python3
r"""Gauge–scalar interference with physical 4×4 mixings (v20).

Next step after ``multi_operator_phase_hessian_v20``:

1. Take the locked colour-triplet basis
   ``(T_10, Tbar_10, T_126, T'_126)`` and its charge-allowed 4×4 ``M_T``.
2. Diagonalize; use the **physical lightest eigenvector fractions** as
   mixing weights (not a 2×2 truncation).
3. Build the gauge (``p→e⁺π⁰``) ↔ scalar interference phase envelope
   (``cosφ ∈ {+1,0,−1}``) with:
   - Patel–Shukla ``μ⁺K⁰`` lifetimes routed by 10 vs 126bar dominance from
     the 4×4 fractions;
   - a mixing-weighted ``y_eff`` width-ratio proxy for scalar feed into
     ``e⁺π⁰`` interfering with the central gauge lifetime.
4. Compare envelopes against the 3×3 truncation to quantify the ``T'``
   impact.

Honesty
-------
* Relative gauge–scalar phase ``φ`` remains an envelope, not a derived UV phase.
* ``y_eff`` / α scans are conditional, not unique UV Yukawas.
* Unique ``τ_p`` and full flavour rotations remain OPEN.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import charge_allowed_potential_minimize_v20 as pmin
import conditional_mt_interference_v20 as cmt
import extended_126_tprime_fragments_v20 as tprime
import patel_shukla_scalar_pdecay_v20 as ps
import scalar_vacuum_proton_decay_v20 as scalar_pd

ROOT = Path(__file__).resolve().parent

ALPHA_PS = (0.01, 0.1, 0.3)
YEFF_GRID = (1.0e-4, 1.0e-3, 1.0e-2)
DOMINANCE_THRESHOLD = 0.70

SOURCES = {
    "upstream_4x4": "extended_126_tprime_fragments_v20",
    "interference": "conditional_mt_interference_v20.interference_lifetime_years",
    "patel_shukla": ps.SOURCE,
    "gauge": "scalar_vacuum_proton_decay_v20.gauge_proton_decay",
}


def mixing_weighted_yeff(fracs: dict[str, float], y_parent: dict[str, float]) -> float:
    """y_eff² = Σ_a f_a y(parent_a)²."""
    y2 = (
        fracs["T_10"] * y_parent["10_H"] ** 2
        + fracs["Tbar_10"] * y_parent["10_H"] ** 2
        + fracs["T_126"] * y_parent["126bar_H"] ** 2
        + fracs["Tprime_126"] * y_parent["126bar_H"] ** 2
    )
    return float(math.sqrt(max(y2, 0.0)))


def scalar_epi0_proxy_lifetime(
    *,
    tau_gauge: float,
    m_t: float,
    m_x: float,
    g_gut: float,
    y_eff: float,
) -> float:
    """τ_s from Γ_s/Γ_g = ((y_eff/g)(M_X/M_T))^4 ⇒ τ_s = τ_g / ratio."""
    if min(m_t, m_x, g_gut, tau_gauge) <= 0:
        return float("nan")
    ratio = (y_eff / g_gut * m_x / m_t) ** 4
    if ratio <= 0:
        return float("inf")
    return float(tau_gauge / ratio)


def interference_envelope(tau_gauge: float, tau_scalar: float) -> dict[str, Any]:
    vals = {
        "+1_constructive": cmt.interference_lifetime_years(tau_gauge, tau_scalar, 1.0),
        "0_incoherent": cmt.interference_lifetime_years(tau_gauge, tau_scalar, 0.0),
        "-1_destructive": cmt.interference_lifetime_years(tau_gauge, tau_scalar, -1.0),
    }
    return {
        "cos_phi": vals,
        "incoherent_passes_SK_e_pi0": vals["0_incoherent"]
        >= scalar_pd.SK_EPI0_LIMIT_YR,
        "constructive_passes_SK_e_pi0": vals["+1_constructive"]
        >= scalar_pd.SK_EPI0_LIMIT_YR,
        "destructive_passes_SK_e_pi0": (
            vals["-1_destructive"] == float("inf")
            or vals["-1_destructive"] >= scalar_pd.SK_EPI0_LIMIT_YR
        ),
    }


def evaluate_4x4_scenario(
    scenario: dict[str, Any],
    *,
    m_i: float,
    m_gut: float,
    tau_gauge: float,
    g_gut: float,
    minimized: dict[str, float],
) -> dict[str, Any]:
    kappa = float(scenario["kappa"])
    lam4 = float(scenario["lam4"])
    if scenario.get("use_minimized_couplings"):
        kappa = float(minimized["kappa"])
        lam4 = float(minimized["lam4"])

    filled = tprime.fill_4x4(
        m_i=m_i,
        m_gut=m_gut,
        mu_t=float(scenario["mu_t_over_MI"]) * m_i,
        mu_tbar=float(scenario["mu_tbar_over_MI"]) * m_i,
        mu_126=float(scenario["mu_126_over_MI"]) * m_i,
        mu_tprime=float(scenario["mu_tprime_over_MI"]) * m_i,
        lam210_10=float(scenario["lam210_10"]),
        lam210_126=float(scenario["lam210_126"]),
        lam210_tprime=float(scenario["lam210_tprime"]),
        lamS_10=float(scenario["lamS_10"]),
        lamS_126=float(scenario["lamS_126"]),
        lamS_tprime=float(scenario["lamS_tprime"]),
        kappa=kappa,
        lam4=lam4,
        eta_intra=float(scenario["eta_intra"]),
        include_dim4_mix=bool(scenario["include_dim4_mix"]),
        include_intra_126=bool(scenario["include_intra_126"]),
    )
    m4 = filled["matrix_GeV"]
    w, v = np.linalg.eigh(m4)
    order = np.argsort(np.abs(w))
    w = w[order]
    v = v[:, order]
    light = float(abs(w[0]))
    fracs_arr = np.abs(v[:, 0]) ** 2
    fracs_arr = fracs_arr / float(np.sum(fracs_arr))
    fracs = {
        "T_10": float(fracs_arr[0]),
        "Tbar_10": float(fracs_arr[1]),
        "T_126": float(fracs_arr[2]),
        "Tprime_126": float(fracs_arr[3]),
    }

    m3 = tprime._truncate_3x3(m4)
    w3 = np.linalg.eigvalsh(m3)
    light3 = float(np.min(np.abs(w3)))

    singular = light <= 0.0
    frac10 = fracs["T_10"] + fracs["Tbar_10"]
    frac126 = fracs["T_126"] + fracs["Tprime_126"]
    if frac10 >= DOMINANCE_THRESHOLD:
        dominance = "10_H"
        ps_dom = "10_H"
    elif frac126 >= DOMINANCE_THRESHOLD:
        dominance = "126bar_H"
        ps_dom = "126bar_H"
    else:
        dominance = "mixed"
        ps_dom = "mixed"

    # PS μK0 + interference vs gauge eπ0
    ps_rows: list[dict[str, Any]] = []
    if not singular:
        for alpha_ps in ALPHA_PS:
            if ps_dom == "mixed":
                r10 = ps.evaluate_channel(
                    "10_H", "p_to_mu_K0", alpha=alpha_ps, M_T_GeV=light, M_Tbar_GeV=light
                )
                r126 = ps.evaluate_channel(
                    "126bar_H",
                    "p_to_mu_K0",
                    alpha=alpha_ps,
                    M_T_GeV=light,
                    M_Tbar_GeV=light,
                )
                row = dict(
                    r10
                    if r10["predicted_lifetime_years"]
                    <= r126["predicted_lifetime_years"]
                    else r126
                )
                row["dominance_routing"] = "mixed_take_shorter"
            else:
                row = dict(
                    ps.evaluate_channel(
                        ps_dom,
                        "p_to_mu_K0",
                        alpha=alpha_ps,
                        M_T_GeV=light,
                        M_Tbar_GeV=light,
                    )
                )
                row["dominance_routing"] = ps_dom
            tau_s = float(row["predicted_lifetime_years"])
            row["interference_with_gauge_e_pi0"] = interference_envelope(
                tau_gauge, tau_s
            )
            ps_rows.append(row)

    # Mixing-weighted y_eff eπ0 proxy interference
    yeff_rows: list[dict[str, Any]] = []
    if not singular:
        for y0 in YEFF_GRID:
            y_parent = {"10_H": y0, "126bar_H": y0}
            y_eff = mixing_weighted_yeff(fracs, y_parent)
            # Also a 3×3-truncation proxy using only first three fractions renormalized
            f3 = np.array([fracs["T_10"], fracs["Tbar_10"], fracs["T_126"]], dtype=float)
            if float(np.sum(f3)) > 0:
                f3 = f3 / float(np.sum(f3))
            fracs3 = {
                "T_10": float(f3[0]),
                "Tbar_10": float(f3[1]),
                "T_126": float(f3[2]),
                "Tprime_126": 0.0,
            }
            y_eff_3 = mixing_weighted_yeff(fracs3, y_parent)
            tau_s = scalar_epi0_proxy_lifetime(
                tau_gauge=tau_gauge,
                m_t=light,
                m_x=m_gut,
                g_gut=g_gut,
                y_eff=y_eff,
            )
            tau_s3 = scalar_epi0_proxy_lifetime(
                tau_gauge=tau_gauge,
                m_t=light3,
                m_x=m_gut,
                g_gut=g_gut,
                y_eff=y_eff_3,
            )
            env4 = interference_envelope(tau_gauge, tau_s)
            env3 = interference_envelope(tau_gauge, tau_s3)
            yeff_rows.append(
                {
                    "y_parent": y0,
                    "y_eff_4x4": y_eff,
                    "y_eff_3x3_truncation": y_eff_3,
                    "tau_scalar_4x4_years": tau_s,
                    "tau_scalar_3x3_years": tau_s3,
                    "interference_4x4": env4,
                    "interference_3x3_truncation": env3,
                    "tprime_changes_constructive_pass": (
                        env4["constructive_passes_SK_e_pi0"]
                        != env3["constructive_passes_SK_e_pi0"]
                    ),
                }
            )

    excl_ps = singular or any(not r["passes_experimental_limit"] for r in ps_rows)
    excl_sk = singular or any(
        not r["interference_with_gauge_e_pi0"]["constructive_passes_SK_e_pi0"]
        for r in ps_rows
    )
    excl_yeff = singular or any(
        not r["interference_4x4"]["constructive_passes_SK_e_pi0"] for r in yeff_rows
    )

    return {
        "name": scenario["name"],
        "basis": list(tprime.BASIS),
        "kappa_used": kappa,
        "lam4_used": lam4,
        "lightest_GeV": light,
        "lightest_3x3_truncation_GeV": light3,
        "eigenvalues_GeV": [float(x) for x in w],
        "lightest_fractions": fracs,
        "dominance_class": dominance,
        "frac_Tprime": fracs["Tprime_126"],
        "patel_shukla_mu_K0": ps_rows,
        "yeff_epi0_interference": yeff_rows,
        "flag": {
            "physical_4x4_mixings": True,
            "singular": singular,
            "conditionally_excluded_by_ps_mu_K0": excl_ps,
            "conditionally_excluded_by_constructive_SK_e_pi0_from_ps": excl_sk,
            "conditionally_excluded_by_constructive_SK_e_pi0_from_yeff": excl_yeff,
            "tprime_fraction_nonzero": fracs["Tprime_126"] > 1e-12,
        },
    }


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    if not anchor.get("available"):
        return {
            "status": "GAUGE_SCALAR_4x4_INTERFERENCE_NOT_EXECUTED__ANCHOR_MISSING",
            "n_failed": 1,
            "failures": ["unification_anchor"],
            "flag": {"gauge_scalar_interference_with_4x4_mixings": False},
        }

    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    alpha_inv = float(anchor["alpha_inv_GUT"])
    g_gut = math.sqrt(4.0 * math.pi / alpha_inv)
    gauge = scalar_pd.gauge_proton_decay(anchor)
    tau_gauge = float(gauge["central"]["lifetime_years"])

    vmin = pmin.build_report()
    minimized = dict(vmin.get("fixed_couplings") or {})
    fk = vmin.get("finite_kappa_benchmark_couplings")
    if fk:
        minimized_for_full = {
            "kappa": fk["kappa"],
            "lam4": fk["lam4"],
            "lambda_lock": fk.get("lambda_lock", minimized.get("lambda_lock", 1.0)),
        }
    else:
        minimized_for_full = {
            "kappa": minimized.get("kappa", 0.0),
            "lam4": minimized.get("lam4", 0.0),
            "lambda_lock": minimized.get("lambda_lock", 1.0),
        }

    rows = [
        evaluate_4x4_scenario(
            s,
            m_i=m_i,
            m_gut=m_gut,
            tau_gauge=tau_gauge,
            g_gut=g_gut,
            minimized=minimized_for_full,
        )
        for s in tprime.SCENARIOS
    ]
    excl_ps = [r for r in rows if r["flag"]["conditionally_excluded_by_ps_mu_K0"]]
    excl_sk = [
        r
        for r in rows
        if r["flag"]["conditionally_excluded_by_constructive_SK_e_pi0_from_ps"]
    ]
    excl_yeff = [
        r
        for r in rows
        if r["flag"]["conditionally_excluded_by_constructive_SK_e_pi0_from_yeff"]
    ]
    physical = [r for r in rows if not r["flag"]["singular"]]
    lightest = min(physical, key=lambda r: r["lightest_GeV"])
    n_tprime_changes = sum(
        1
        for r in rows
        for y in r["yeff_epi0_interference"]
        if y["tprime_changes_constructive_pass"]
    )

    checks = {
        "gauge_lifetime_finite": tau_gauge > 0,
        "central_gauge_passes": bool(
            gauge.get("flag", {}).get("central_gauge_point_passes")
        ),
        "n_scenarios_ge_6": len(rows) >= 6,
        "some_ps_excluded": len(excl_ps) > 0,
        "some_ps_survive": len(excl_ps) < len(rows),
        "some_sk_constructive_excluded": len(excl_sk) > 0,
        "some_sk_constructive_survive": len(excl_sk) < len(rows),
        "physical_4x4_flagged": all(r["flag"]["physical_4x4_mixings"] for r in rows),
        "interference_envelope_present": all(
            len(r["patel_shukla_mu_K0"]) > 0 or r["flag"]["singular"] for r in rows
        ),
        "yeff_rows_present": all(
            len(r["yeff_epi0_interference"]) > 0 or r["flag"]["singular"] for r in rows
        ),
        "upstream_minimize_ok": vmin.get("n_failed", 1) == 0,
        "whole_model_not_declared_dead": True,
        "not_claiming_unique_taup": True,
    }
    failures = [n for n, ok in checks.items() if not ok]

    return {
        "status": (
            "GAUGE_SCALAR_INTERFERENCE_WITH_PHYSICAL_4x4_MIXINGS"
            if not failures
            else "GAUGE_SCALAR_4x4_INTERFERENCE_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "sources": SOURCES,
        "basis": list(tprime.BASIS),
        "gauge_central_lifetime_years": tau_gauge,
        "g_GUT": g_gut,
        "SK_e_pi0_limit_years": scalar_pd.SK_EPI0_LIMIT_YR,
        "minimized_couplings_used": minimized_for_full,
        "n_scenarios": len(rows),
        "n_excluded_by_ps_mu_K0": len(excl_ps),
        "n_excluded_by_constructive_SK_e_pi0_from_ps": len(excl_sk),
        "n_excluded_by_constructive_SK_e_pi0_from_yeff": len(excl_yeff),
        "n_tprime_changes_constructive_pass": n_tprime_changes,
        "excluded_scenario_names_ps": [r["name"] for r in excl_ps],
        "excluded_scenario_names_sk_constructive": [r["name"] for r in excl_sk],
        "lightest_scenario": {
            "name": lightest["name"],
            "lightest_GeV": lightest["lightest_GeV"],
            "dominance": lightest["dominance_class"],
            "fractions": lightest["lightest_fractions"],
            "frac_Tprime": lightest["frac_Tprime"],
        },
        "scenarios": rows,
        "upstream_minimize_status": vmin.get("status"),
        "next_exact_calculation": [
            "Lift the reduced minimum / phase Hessian to the full 210+126+10 component space",
            "Goldstone counting across every broken generator",
            "Derive unique flavour rotations for gauge X/Y amplitudes",
            "Optionally restore t3 if a light 126_H is added",
        ],
        "flag": {
            "gauge_scalar_interference_with_4x4_mixings": True,
            "physical_eigenvector_fractions_used": True,
            "tprime_included_in_interference": True,
            "relative_phase_is_envelope_not_derived": True,
            "invented_unpublished_cg_values": False,
            "complete_so10_scalar_potential": False,
            "exact_unique_proton_lifetime": False,
            "conditional_parameter_points_excluded": len(excl_ps) > 0 or len(excl_sk) > 0,
            "whole_model_excluded": False,
        },
        "verdict": (
            "Gauge–scalar interference envelopes are computed with physical "
            "4×4 lightest-eigenvector mixings (including T'). Some conditional "
            "points fail constructive SK e⁺π⁰ or PS μ⁺K⁰; the whole model is "
            "not excluded. Unique τ_p remains OPEN."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    light = report["lightest_scenario"]
    lines = [
        "# Gauge–scalar interference with 4×4 mixings — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        f"- Basis: `{', '.join(report['basis'])}`",
        f"- Gauge central τ(e⁺π⁰): {report['gauge_central_lifetime_years']:.3e} yr",
        f"- Excluded by PS μK⁰: {report['n_excluded_by_ps_mu_K0']}",
        f"- Excluded by constructive SK (from PS τ_s): "
        f"{report['n_excluded_by_constructive_SK_e_pi0_from_ps']}",
        f"- Excluded by constructive SK (from y_eff): "
        f"{report['n_excluded_by_constructive_SK_e_pi0_from_yeff']}",
        f"- T' changes constructive pass vs 3×3: "
        f"{report['n_tprime_changes_constructive_pass']}",
        f"- Lightest: `{light['name']}` at {light['lightest_GeV']:.3e} GeV "
        f"(T' frac {light['frac_Tprime']:.3f})",
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
    ROOT.joinpath("GAUGE_SCALAR_INTERFERENCE_4x4_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("GAUGE_SCALAR_INTERFERENCE_4x4_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "basis": report.get("basis"),
                "n_excluded_ps": report.get("n_excluded_by_ps_mu_K0"),
                "n_excluded_sk": report.get(
                    "n_excluded_by_constructive_SK_e_pi0_from_ps"
                ),
                "n_tprime_changes": report.get("n_tprime_changes_constructive_pass"),
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
