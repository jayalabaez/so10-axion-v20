#!/usr/bin/env python3
"""Fail-closed proton-decay falsification gate for SO(10)-axion v20.

A numerical point may fail an experimental limit without excluding the full
model. Whole-model exclusion requires a unique vacuum/spectrum, consistently
matched Wilson coefficients, flavour rotations, phases, and uncertainties.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parent
HBAR_GEV_S = 6.582119569e-25
SECONDS_PER_YEAR = 365.25 * 24.0 * 3600.0
SUPER_K_EPI0_LIMIT_YEARS = 2.4e34

SOURCES = {
    "experiment": {
        "citation": "Super-Kamiokande, Phys. Rev. D 102, 112011 (2020)",
        "arxiv": "2010.16098",
        "channel": "p -> e+ pi0",
        "limit_90CL_years": SUPER_K_EPI0_LIMIT_YEARS,
        "observation": "no p -> e+ pi0 candidates in the reported search",
    },
    "hadronic": {
        "citation": "Aoki et al., Phys. Rev. D 96, 014506 (2017)",
        "arxiv": "1705.01338",
    },
    "scalar": {
        "citation": "Patel and Shukla, JHEP 08 (2022) 042",
        "arxiv": "2203.07748",
    },
}


def _positive(name: str, value: float) -> float:
    value = float(value)
    if not math.isfinite(value) or value <= 0.0:
        raise ValueError(f"{name} must be positive and finite")
    return value


def gauge_lifetime_years(
    m_x_gev: float,
    alpha_inv_gut: float,
    *,
    f_pi_gev: float = 0.139,
    m_p_gev: float = 0.9382720813,
    alpha_h_gev3: float = 0.012,
    a_r: float = 2.726,
    f_q: float = 7.6,
) -> float:
    """Literature-normalized dimension-six p->e+pi0 benchmark in years."""
    m_x_gev = _positive("m_x_gev", m_x_gev)
    alpha_inv_gut = _positive("alpha_inv_gut", alpha_inv_gut)
    f_pi_gev = _positive("f_pi_gev", f_pi_gev)
    m_p_gev = _positive("m_p_gev", m_p_gev)
    alpha_h_gev3 = _positive("alpha_h_gev3", alpha_h_gev3)
    a_r = _positive("a_r", a_r)
    f_q = _positive("f_q", f_q)
    alpha_gut = 1.0 / alpha_inv_gut
    tau_gev_inv = (
        (4.0 / math.pi)
        * (f_pi_gev**2 / m_p_gev)
        * (m_x_gev**4 / alpha_gut**2)
        / (alpha_h_gev3**2 * a_r**2 * f_q)
    )
    return tau_gev_inv * HBAR_GEV_S / SECONDS_PER_YEAR


def required_vector_mass_gev(limit_years: float, alpha_inv_gut: float, **kw: float) -> float:
    limit_years = _positive("limit_years", limit_years)
    return (limit_years / gauge_lifetime_years(1.0, alpha_inv_gut, **kw)) ** 0.25


def classify_point(
    lifetime_years: float,
    *,
    limit_years: float = SUPER_K_EPI0_LIMIT_YEARS,
    derivation_complete: bool = False,
) -> dict[str, Any]:
    lifetime_years = _positive("lifetime_years", lifetime_years)
    limit_years = _positive("limit_years", limit_years)
    below = lifetime_years < limit_years
    if derivation_complete:
        status = "EXCLUDED_BY_CHANNEL" if below else "SURVIVES_CHANNEL"
    else:
        status = "CONDITIONAL_POINT_BELOW_LIMIT" if below else "CONDITIONAL_POINT_ABOVE_LIMIT"
    return {
        "lifetime_years": lifetime_years,
        "limit_years": limit_years,
        "margin_over_limit": lifetime_years / limit_years,
        "point_below_limit": below,
        "derivation_complete": bool(derivation_complete),
        "model_status": status,
        "whole_model_excluded": bool(derivation_complete and below),
    }


def _load_anchor() -> dict[str, Any]:
    try:
        import two_loop_thresholds_v20 as thresholds
        one = thresholds.solve_unification(two_loop=False)
        two = thresholds.solve_unification(two_loop=True)
        return {
            "available": True,
            "one_loop": {"M_GUT_GeV": float(one["M_GUT_GeV"]), "alpha_inv_GUT": float(one["alpha_inv_GUT"])},
            "two_loop_proxy": {"M_GUT_GeV": float(two["M_GUT_GeV"]), "alpha_inv_GUT": float(two["alpha_inv_GUT"])},
        }
    except Exception as exc:
        return {"available": False, "error": f"{type(exc).__name__}: {exc}"}


def _selected_xy_evidence() -> dict[str, Any]:
    try:
        import exact_xy_masses_component_vacuum_v20 as xy
        report = xy.build_report()
        flags = dict(report.get("flag") or {})
        mass = float((report.get("masses") or {}).get("proton_decay_mediator_GeV", float("nan")))
        anchor = _load_anchor()
        alpha_inv = float(anchor.get("one_loop", {}).get("alpha_inv_GUT", float("nan")))
        return {
            "available": math.isfinite(mass) and mass > 0 and math.isfinite(alpha_inv),
            "M_X_GeV": mass,
            "alpha_inv_GUT": alpha_inv,
            "unique_vev_ratios_from_full_potential": bool(flags.get("unique_vev_ratios_from_full_potential", False)),
            "exact_unique_proton_lifetime": bool(flags.get("exact_unique_proton_lifetime", False)),
            "scope": "published mass formula at selected VEV ratios; not a unique full-vacuum prediction",
        }
    except Exception as exc:
        return {"available": False, "error": f"{type(exc).__name__}: {exc}"}


def _legacy_semantic_audit() -> dict[str, Any]:
    try:
        import tau_p_full_stack_uniqueness_v20 as legacy
        report = legacy.build_report()
        flags = dict(report.get("flag") or {})
        residual = dict((report.get("certificate") or {}).get("residual_still_open") or {})
        selected_unique = bool(flags.get("tau_p_unique_under_full_uv_stack"))
        exact_unique = bool(flags.get("exact_unique_proton_lifetime"))
        hessian_open = bool(residual.get("full_component_hessian_and_competing_extrema"))
        return {
            "available": True,
            "legacy_status": report.get("status"),
            "claims_tau_unique_under_full_uv_stack": selected_unique,
            "claims_exact_unique": exact_unique,
            "full_component_hessian_and_competing_extrema_open": hessian_open,
            "semantic_overclaim_detected": bool(selected_unique and (not exact_unique or hessian_open)),
            "authoritative": False,
        }
    except Exception as exc:
        return {"available": False, "error": f"{type(exc).__name__}: {exc}", "authoritative": False}


def _benchmark(name: str, mass: float, alpha_inv: float, scope: str) -> dict[str, Any]:
    result = classify_point(gauge_lifetime_years(mass, alpha_inv))
    return {
        "name": name,
        "M_X_GeV": mass,
        "alpha_inv_GUT": alpha_inv,
        "scope": scope,
        "canonical_literature_normalization": result,
        "required_M_X_for_current_limit_GeV": required_vector_mass_gev(SUPER_K_EPI0_LIMIT_YEARS, alpha_inv),
    }


def build_report(
    *,
    anchor_loader: Callable[[], dict[str, Any]] = _load_anchor,
    selected_xy_loader: Callable[[], dict[str, Any]] = _selected_xy_evidence,
    legacy_loader: Callable[[], dict[str, Any]] = _legacy_semantic_audit,
) -> dict[str, Any]:
    anchor, selected, legacy = anchor_loader(), selected_xy_loader(), legacy_loader()
    benchmarks: dict[str, Any] = {}
    failures: list[str] = []
    if anchor.get("available"):
        one, two = anchor["one_loop"], anchor["two_loop_proxy"]
        benchmarks["one_loop_unification_anchor"] = _benchmark(
            "one_loop_unification_anchor", float(one["M_GUT_GeV"]), float(one["alpha_inv_GUT"]), "conditional M_X=M_GUT benchmark"
        )
        benchmarks["two_loop_calibrated_proxy"] = _benchmark(
            "two_loop_calibrated_proxy", float(two["M_GUT_GeV"]), float(two["alpha_inv_GUT"]), "calibrated proxy, not validated component-threshold matching"
        )
    else:
        failures.append("unification_anchor_unavailable")
    if selected.get("available"):
        benchmarks["selected_vev_xy_mass"] = _benchmark(
            "selected_vev_xy_mass", float(selected["M_X_GeV"]), float(selected["alpha_inv_GUT"]), str(selected["scope"])
        )

    readiness = {
        "full_component_vacuum_and_competing_extrema": False,
        "unique_vev_ratios_from_full_potential": bool(selected.get("unique_vev_ratios_from_full_potential", False)),
        "validated_two_loop_component_threshold_matching": False,
        "unique_physical_XY_masses": False,
        "complete_mass_basis_gauge_flavour_wilson_coefficients": False,
        "complete_scalar_triplet_masses_mixings_and_yukawas": False,
        "physical_phases_and_interference": False,
        "uncertainties_propagated": False,
    }
    exact_unique = all(readiness.values())
    below = [k for k, v in benchmarks.items() if v["canonical_literature_normalization"]["point_below_limit"]]
    above = [k for k, v in benchmarks.items() if k not in below]
    checks = {
        "mass_fourth_power_scaling": math.isclose(gauge_lifetime_years(2e15, 37) / gauge_lifetime_years(1e15, 37), 16.0, rel_tol=1e-12),
        "inverse_coupling_squared_scaling": math.isclose(gauge_lifetime_years(1e15, 40) / gauge_lifetime_years(1e15, 20), 4.0, rel_tol=1e-12),
        "conditional_points_never_exclude_model": all(not v["canonical_literature_normalization"]["whole_model_excluded"] for v in benchmarks.values()),
        "unique_prediction_fail_closed": not exact_unique,
        "legacy_certificate_not_authoritative": not legacy.get("authoritative", False),
    }
    failures.extend(k for k, ok in checks.items() if not ok)
    return {
        "status": "PROTON_DECAY_FALSIFICATION_GATE_PASS__NO_UNIQUE_MODEL_PREDICTION" if not failures else "PROTON_DECAY_FALSIFICATION_GATE_FAILED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "sources": SOURCES,
        "experimental_reference": SOURCES["experiment"],
        "benchmarks": benchmarks,
        "selected_xy_evidence": selected,
        "legacy_semantic_audit": legacy,
        "prediction_readiness": readiness,
        "classification": {
            "proton_decay_observed": False,
            "conditional_points_below_limit": below,
            "conditional_points_above_limit": above,
            "exact_unique_proton_lifetime_derived": exact_unique,
            "whole_model_excluded_by_proton_decay": False,
            "authoritative_answer": "NO_PROTON_DECAY_DISCOVERY__CONDITIONAL_BENCHMARKS_ONLY__FULL_MODEL_VERDICT_OPEN",
        },
        "checks": checks,
        "verdict": "No proton decay has been found. Benchmarks below the limit falsify those assumed points, not the whole v20 model. A unique verdict remains open until the full vacuum/spectrum, operator running, flavour contractions, phases and uncertainties are derived consistently.",
    }


def write_markdown(report: dict[str, Any]) -> str:
    lines = ["# Proton-decay falsification gate — v20", "", f"**Status:** `{report['status']}`", "", report["verdict"], "", "## Conditional benchmarks", ""]
    for name, row in report["benchmarks"].items():
        result = row["canonical_literature_normalization"]
        lines += [
            f"### {name}",
            f"- M_X: {row['M_X_GeV']:.6e} GeV",
            f"- lifetime: {result['lifetime_years']:.6e} yr",
            f"- margin over limit: {result['margin_over_limit']:.6e}x",
            f"- status: `{result['model_status']}`",
            f"- scope: {row['scope']}",
            "",
        ]
    lines += ["## Missing inputs", ""]
    lines += [f"- [{'x' if ready else ' '}] `{key}`" for key, ready in report["prediction_readiness"].items()]
    lines += ["", "## Legacy audit", "", f"- semantic overclaim detected: **{report['legacy_semantic_audit'].get('semantic_overclaim_detected', False)}**", "- legacy uniqueness certificates are non-authoritative.", ""]
    return "\n".join(lines)


def main() -> int:
    report = build_report()
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    for name in ("PROTON_DECAY_FALSIFICATION_GATE_V20_VERDICT.json", "CURRENT_MAIN_PROTON_DECAY_EVALUATION_V20_VERDICT.json"):
        ROOT.joinpath(name).write_text(payload, encoding="utf-8")
    markdown = write_markdown(report)
    for name in ("PROTON_DECAY_FALSIFICATION_GATE_V20.md", "CURRENT_MAIN_PROTON_DECAY_EVALUATION_V20.md"):
        ROOT.joinpath(name).write_text(markdown, encoding="utf-8")
    print(payload, end="")
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
