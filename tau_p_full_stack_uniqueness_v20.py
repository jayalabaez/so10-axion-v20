#!/usr/bin/env python3
"""Historical filename; authoritative result is a conditional selected-point audit.

Later signed-operator and Hessian audits invalidated the physical triplet
spectrum and full-vacuum closure used by the former uniqueness certificate.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import exact_xy_masses_component_vacuum_v20 as xyexact
import residual_lam210_eta_intra_v20 as residual

ROOT = Path(__file__).resolve().parent
RESIDUAL_NOW_CLOSED: list[str] = []
RESIDUAL_STILL_OPEN = [
    "complete_nonsusy_invariant_ring",
    "direct_component_mass_squared_matrix",
    "full_component_hessian_and_competing_extrema",
    "physical_triplet_threshold_spectrum",
    "validated_two_loop_component_threshold_matching",
    "complete_mass_basis_wilson_coefficients",
    "physical_phases_and_interference",
    "uncertainties_propagated",
    "exact_unique_proton_lifetime",
]


def build_report() -> dict[str, Any]:
    try:
        xy = xyexact.build_report()
        masses = dict(xy.get("masses") or {})
        gauge0 = dict(xy.get("gauge_lifetime") or {})
        selected = dict(gauge0.get("exact_mediator") or {})
        tau = float(selected.get("tau_e_years", float("nan")))
        mediator = float(masses.get("proton_decay_mediator_GeV", float("nan")))
    except Exception as exc:
        return {
            "status": "TAU_P_SELECTED_STACK_NOT_EXECUTED",
            "n_checks": 1,
            "n_failed": 1,
            "failures": ["selected_xy_evaluation"],
            "error": f"{type(exc).__name__}: {exc}",
            "flag": {
                "tau_p_unique_under_full_uv_stack": False,
                "exact_unique_proton_lifetime": False,
                "whole_model_excluded": False,
            },
        }

    try:
        old = residual.build_report()
        mixing = dict((old.get("spectrum_closed") or {}).get("mixing") or {})
        old_mt = mixing.get("lightest_abs_GeV")
    except Exception as exc:
        old_mt = None
        old = {"error": f"{type(exc).__name__}: {exc}"}

    finite = math.isfinite(tau) and tau > 0.0
    blockers = {name: True for name in RESIDUAL_STILL_OPEN}
    flags = {
        "tau_p_unique_under_full_uv_stack": False,
        "tau_p_unique_under_reduced_uv_vacuum_selection": False,
        "selected_xy_formula_evaluated": finite,
        "exact_XY_masses_used": False,
        "residual_spectrum_used": False,
        "physical_triplet_spectrum_complete": False,
        "exact_unique_proton_lifetime": False,
        "whole_model_excluded": False,
        "whole_model_validated": False,
        "historical_filename_compatibility_only": True,
    }
    checks = {
        "selected_gauge_lifetime_finite": finite,
        "full_stack_uniqueness_withdrawn": not flags["tau_p_unique_under_full_uv_stack"],
        "historical_scalar_spectrum_not_physical": not flags["residual_spectrum_used"],
        "blocking_residuals_nonempty": bool(blockers),
        "whole_model_not_excluded": not flags["whole_model_excluded"],
    }
    failures = [name for name, passed in checks.items() if not passed]
    passes = bool(selected.get("passes_SK", False))

    return {
        "status": (
            "TAU_P_SELECTED_STACK_CONDITIONAL__UNIQUE_LIFETIME_OPEN"
            if not failures else "TAU_P_SELECTED_STACK_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "gauge_lifetime": {
            "M_PD_mediator_GeV": mediator,
            "mediator_name": masses.get("proton_decay_mediator_name"),
            "uv_selected": selected,
            "conditional_only": True,
        },
        "scalar_lifetime": {
            "lightest_MT_GeV": old_mt,
            "physical_spectrum": False,
            "conditional_only": True,
            "contamination_source": "triplet_proxy_contamination_audit_v20",
            "historical_upstream_status": old.get("status"),
        },
        "certificate": {
            "closed_under_full_uv_stack": {
                "selected_point_inputs_available": finite,
                "full_physical_stack_closed": False,
                "physical_triplet_spectrum_closed": False,
            },
            "residual_now_closed": {},
            "residual_still_open": blockers,
            "selected_tau_e_years": tau,
            "selected_passes_SK": passes,
            "scalar_all_alpha_pass": False,
            "conditional_only": True,
            "interpretation": (
                "Selected VEV formulas are a conditional benchmark. The former "
                "full-stack uniqueness and physical triplet-spectrum claims are withdrawn."
            ),
        },
        "flag": flags,
        "checks": checks,
        "verdict": (
            f"Selected tau(p->e+pi0)={tau:.3e} yr (SK pass={passes}) is conditional; "
            "no unique full-stack or whole-model proton lifetime is derived."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    cert = report.get("certificate", {})
    return "\n".join([
        "# Conditional selected-stack proton decay — v20", "",
        f"**Status:** `{report['status']}`", "", report.get("verdict", ""), "",
        f"- Selected lifetime: {cert.get('selected_tau_e_years')} yr",
        "- Unique full-stack lifetime: **False**",
        "- Physical scalar-triplet spectrum: **False**", "",
    ])


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    report = build_report()
    ROOT.joinpath("TAU_P_FULL_STACK_UNIQUENESS_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2, default=str) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("TAU_P_FULL_STACK_UNIQUENESS_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(json.dumps(report, indent=2, default=str))
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
