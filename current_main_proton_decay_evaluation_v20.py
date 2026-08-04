#!/usr/bin/env python3
"""Consolidated proton-decay evaluation on the current v20 main tree.

This module intentionally separates:

* the central gauge X/Y benchmark;
* the broad X/Y threshold and hadronic envelope;
* low-scale CKM/PMNS flavour rotations and conditional UV CP phases;
* physical 4x4 colour-triplet mixing scans and scalar/gauge interference;
* exact model-level exclusion.

A failing conditional point is not promoted to a whole-model failure while the
full scalar vacuum, unique X/Y masses, triplet Yukawa contractions and UV phases
remain underdetermined.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import gauge_scalar_interference_4x4_v20 as gs4
import patel_shukla_scalar_pdecay_v20 as ps
import sarah_pyrate_so10_210_betas_v20 as sarah
import scalar_vacuum_proton_decay_v20 as scalar_pd
import uv_cp_phases_from_potential_v20 as uvcp
import xy_flavour_rotations_gauge_v20 as xy

ROOT = Path(__file__).resolve().parent


def _finite_lifetimes(obj: Any, path: str = "") -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            child = f"{path}.{key}" if path else str(key)
            key_lower = str(key).lower()
            if (
                isinstance(value, (int, float))
                and not isinstance(value, bool)
                and "lifetime" in key_lower
                and "year" in key_lower
                and math.isfinite(float(value))
                and float(value) > 0.0
            ):
                out.append({"path": child, "years": float(value)})
            out.extend(_finite_lifetimes(value, child))
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            out.extend(_finite_lifetimes(value, f"{path}[{i}]"))
    return out


def _boolean_keys(obj: Any, needle: str, path: str = "") -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            child = f"{path}.{key}" if path else str(key)
            if needle.lower() in str(key).lower() and isinstance(value, bool):
                out.append({"path": child, "value": value})
            out.extend(_boolean_keys(value, needle, child))
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            out.extend(_boolean_keys(value, needle, f"{path}[{i}]"))
    return out


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    gauge = scalar_pd.gauge_proton_decay(anchor)
    xy_report = xy.build_report()
    uv_report = uvcp.build_report()
    ps_report = ps.build_report()
    gs_report = gs4.build_report()
    sarah_report = sarah.build_report()

    sk_limit = float(scalar_pd.SK_EPI0_LIMIT_YR)
    central = gauge.get("central", {})
    envelope = gauge.get("envelope", {})
    central_tau = float(central.get("lifetime_years", float("nan")))
    central_margin = central_tau / sk_limit if math.isfinite(central_tau) else float("nan")

    xy_lifetimes = dict(xy_report.get("lifetimes") or {})
    uv_width = dict(uv_report.get("gauge_width") or {})
    uv_lifetimes = _finite_lifetimes(uv_width, "uv_cp.gauge_width")

    n_scenarios = int(gs_report.get("n_scenarios", 0) or 0)
    n_excl_ps = int(gs_report.get("n_excluded_by_ps_mu_K0", 0) or 0)
    n_excl_sk_ps = int(
        gs_report.get("n_excluded_by_constructive_SK_e_pi0_from_ps", 0) or 0
    )
    n_excl_sk_yeff = int(
        gs_report.get("n_excluded_by_constructive_SK_e_pi0_from_yeff", 0) or 0
    )

    scalar_lifetimes = _finite_lifetimes(
        {"patel_shukla": ps_report, "gauge_scalar_4x4": gs_report}
    )
    scalar_values = [row["years"] for row in scalar_lifetimes]
    scalar_min = min(scalar_values) if scalar_values else None
    scalar_max = max(scalar_values) if scalar_values else None

    gauge_envelope_min = dict(envelope.get("minimum_lifetime_point") or {})
    broad_gauge_contains_excluded = bool(
        gauge_envelope_min
        and float(gauge_envelope_min.get("lifetime_years", float("inf"))) < sk_limit
    )
    some_scalar_points_excluded = any(
        x > 0 for x in (n_excl_ps, n_excl_sk_ps, n_excl_sk_yeff)
    )
    all_scalar_points_excluded = bool(
        n_scenarios > 0
        and n_excl_ps == n_scenarios
        and n_excl_sk_ps == n_scenarios
        and n_excl_sk_yeff == n_scenarios
    )

    exact_xy_mass = bool(
        gauge.get("flag", {}).get("exact_XY_mass_from_full_scalar_vacuum", False)
    )
    exact_unique_tau_flags = _boolean_keys(
        {"uv": uv_report, "ps": ps_report, "gs4": gs_report},
        "exact_unique_proton_lifetime",
    )
    exact_unique_tau = bool(exact_unique_tau_flags) and all(
        row["value"] for row in exact_unique_tau_flags
    )

    landau_flags = _boolean_keys(sarah_report, "landau")
    any_landau_or_breakdown = any(row["value"] for row in landau_flags)

    whole_model_excluded = bool(
        exact_xy_mass and exact_unique_tau and central_tau < sk_limit
    )

    checks = {
        "unification_anchor_available": bool(anchor.get("available")),
        "central_gauge_lifetime_finite": math.isfinite(central_tau) and central_tau > 0,
        "central_gauge_benchmark_passes_SK": central_tau >= sk_limit,
        "conditional_failures_preserved": broad_gauge_contains_excluded
        or some_scalar_points_excluded,
        "not_all_4x4_scalar_scenarios_excluded": not all_scalar_points_excluded,
        "unique_lifetime_not_overclaimed": not exact_unique_tau,
        "whole_model_not_falsely_excluded": not whole_model_excluded,
    }
    failures = [name for name, passed in checks.items() if not passed]

    status = (
        "CURRENT_MAIN_PROTON_DECAY_EVALUATED__CONDITIONAL_POINTS_FAIL__"
        "WHOLE_MODEL_NOT_EXCLUDED__UNIQUE_LIFETIME_OPEN"
        if not failures
        else "CURRENT_MAIN_PROTON_DECAY_EVALUATION_FAILED"
    )

    return {
        "status": status,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "main_anchor": anchor,
        "experimental_reference": {
            "channel": "p_to_e_plus_pi0",
            "Super_K_90CL_lower_limit_years": sk_limit,
            "source": scalar_pd.SOURCE_LEDGER["super_k_epi0"],
        },
        "gauge_XY": {
            "central": central,
            "central_margin_over_SK": central_margin,
            "envelope": envelope,
            "broad_envelope_contains_excluded_points": broad_gauge_contains_excluded,
            "xy_flavour_lifetimes": xy_lifetimes,
            "conditional_uv_cp_lifetimes": uv_lifetimes,
            "exact_XY_mass_from_full_vacuum": exact_xy_mass,
        },
        "scalar_triplets_and_interference": {
            "n_scenarios": n_scenarios,
            "n_excluded_by_Patel_Shukla_mu_K0": n_excl_ps,
            "n_excluded_by_constructive_SK_from_PS_scalar_lifetime": n_excl_sk_ps,
            "n_excluded_by_constructive_SK_from_yeff_proxy": n_excl_sk_yeff,
            "excluded_scenario_names_Patel_Shukla": gs_report.get(
                "excluded_scenario_names_ps", []
            ),
            "excluded_scenario_names_SK_constructive": gs_report.get(
                "excluded_scenario_names_sk_constructive", []
            ),
            "lightest_scenario": gs_report.get("lightest_scenario"),
            "n_collected_conditional_lifetimes": len(scalar_lifetimes),
            "minimum_collected_conditional_lifetime_years": scalar_min,
            "maximum_collected_conditional_lifetime_years": scalar_max,
            "some_conditional_points_excluded": some_scalar_points_excluded,
            "all_conditional_points_excluded": all_scalar_points_excluded,
        },
        "high_scale_caveat": {
            "sarah_pyrate_status": sarah_report.get("status"),
            "landau_or_perturbative_breakdown_flags": landau_flags,
            "any_landau_or_breakdown": any_landau_or_breakdown,
            "note": (
                "This affects confidence in extrapolating the GUT anchor; it is "
                "not by itself an experimental proton-decay exclusion."
            ),
        },
        "classification": {
            "central_gauge_benchmark_fails": central_tau < sk_limit,
            "some_threshold_or_scalar_parameter_points_fail": (
                broad_gauge_contains_excluded or some_scalar_points_excluded
            ),
            "whole_model_excluded_by_proton_decay": whole_model_excluded,
            "exact_unique_proton_lifetime_derived": exact_unique_tau,
            "answer_to_do_we_have_a_fail": (
                "YES_CONDITIONAL_PARAMETER_POINTS_FAIL__NO_WHOLE_MODEL_FAILURE"
                if broad_gauge_contains_excluded or some_scalar_points_excluded
                else "NO_CURRENT_PROTON_DECAY_FAILURE"
            ),
        },
        "checks": checks,
        "verdict": (
            "The central gauge X/Y benchmark survives the current p->e+pi0 "
            "limit. The broad X/Y mass/hadronic envelope and several conditional "
            "4x4 scalar-triplet scenarios contain excluded points. Because the "
            "full vacuum has not produced unique X/Y and triplet masses, Yukawa "
            "contractions and interference phases simultaneously, proton decay "
            "does not yet exclude the whole v20 model and no unique lifetime is "
            "available."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    gauge = report["gauge_XY"]
    scalar = report["scalar_triplets_and_interference"]
    cls = report["classification"]
    return "\n".join(
        [
            "# Current-main proton-decay evaluation — v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            f"- Central gauge lifetime: {gauge['central']['lifetime_years']:.6e} yr",
            f"- Super-K p→e⁺π⁰ limit: {report['experimental_reference']['Super_K_90CL_lower_limit_years']:.6e} yr",
            f"- Central margin: {gauge['central_margin_over_SK']:.4f}×",
            f"- Broad gauge envelope contains excluded points: **{gauge['broad_envelope_contains_excluded_points']}**",
            f"- 4×4 scenarios: {scalar['n_scenarios']}",
            f"- Excluded by Patel–Shukla μ⁺K⁰: {scalar['n_excluded_by_Patel_Shukla_mu_K0']}",
            f"- Excluded by constructive SK envelope: {scalar['n_excluded_by_constructive_SK_from_PS_scalar_lifetime']}",
            f"- Whole model excluded: **{cls['whole_model_excluded_by_proton_decay']}**",
            f"- Exact unique proton lifetime: **{cls['exact_unique_proton_lifetime_derived']}**",
            "",
            "## Verdict",
            "",
            report["verdict"],
            "",
        ]
    )


def main() -> int:
    report = build_report()
    ROOT.joinpath("CURRENT_MAIN_PROTON_DECAY_EVALUATION_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2, default=str) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("CURRENT_MAIN_PROTON_DECAY_EVALUATION_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(json.dumps(report, indent=2, default=str))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
