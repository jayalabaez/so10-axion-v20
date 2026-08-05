#!/usr/bin/env python3
"""Reopen proton-lifetime Hessian residuals after SUSY-matrix contamination.

The former report declared the mixed component Hessian closed after squaring
singular values of Aulakh chiral and chiral-gauge fermion matrices. Those are
not non-supersymmetric scalar mass-squared matrices. Any historical lifetime
is retained only as a conditional benchmark; no exact or Hessian-closed
proton lifetime is certified.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import mixed_210_126_10_hilbert_hessian_v20 as mxh
import tau_p_full_stack_uniqueness_v20 as taup

ROOT = Path(__file__).resolve().parent

HESSIAN_RESIDUALS_NOW_CLOSED: list[str] = []
RESIDUAL_STILL_OPEN = [
    "complete_nonsusy_invariant_ring",
    "direct_component_mass_squared_matrix",
    "global_vacuum_and_competing_extrema",
    "gauge_projected_full_component_hessian",
    "physical_triplet_threshold_spectrum",
    "exact_unique_proton_lifetime",
]


def _conditional_lifetime() -> tuple[dict[str, Any], str | None]:
    try:
        report = taup.build_report()
    except Exception as exc:
        return {
            "selected_tau_e_years": None,
            "selected_passes_SK": None,
            "scalar_all_alpha_pass": None,
            "M_PD_GeV": None,
            "conditional_only": True,
        }, f"tau_p_full_stack_exception: {exc}"

    cert = report.get("certificate", {})
    mediator = report.get("gauge_lifetime", {})
    return {
        "selected_tau_e_years": cert.get("selected_tau_e_years"),
        "selected_passes_SK": cert.get("selected_passes_SK"),
        "scalar_all_alpha_pass": cert.get("scalar_all_alpha_pass"),
        "M_PD_GeV": mediator.get("M_PD_mediator_GeV"),
        "conditional_only": True,
    }, None


def build_report() -> dict[str, Any]:
    mxh_report = mxh.build_report()
    lifetime, lifetime_warning = _conditional_lifetime()
    checks = {
        "mixed_susy_hessian_withdrawal_executes": (
            mxh_report.get("n_failed") == 0
        ),
        "mixed_hessian_closure_reopened": not mxh_report.get(
            "flag", {}
        ).get("mixed_210_126_10_complete", True),
        "historical_lifetime_labeled_conditional": lifetime[
            "conditional_only"
        ],
        "exact_unique_lifetime_not_claimed": True,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    hessian_open = {
        "full_component_hessian_and_competing_extrema": True,
        "operator_based_8comp_hessian_pd": True,
        "off_singlet_210_fluctuation_hessian": True,
        "mixed_210_126_10_off_singlet_mass_matrices": True,
    }
    return {
        "status": (
            "TAU_P_HESSIAN_CLOSURE_WITHDRAWN__DIRECT_NONSUSY_HESSIAN_OPEN"
            if not failures
            else "TAU_P_HESSIAN_WITHDRAWAL_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "warnings": [lifetime_warning] if lifetime_warning else [],
        "upstream_status": {
            "mixed_hilbert": mxh_report.get("status"),
            "historical_tau_p": "conditional benchmark only",
        },
        "lifetime": lifetime,
        "certificate": {
            "residual_now_closed": {},
            "hessian_residuals_closed": {
                name: False for name in hessian_open
            },
            "residual_still_open": {
                name: True for name in RESIDUAL_STILL_OPEN
            },
            "interpretation": (
                "The component-Hessian closure and any uniqueness derived from it "
                "are reopened. Historical tau_p values are conditional diagnostics "
                "until the direct non-SUSY scalar spectrum and thresholds exist."
            ),
        },
        "flag": {
            "hessian_residuals_folded_into_tau_p": False,
            "full_component_hessian_residual_closed": False,
            "tau_p_unique_under_full_uv_stack": False,
            "tau_p_unique_under_hessian_closed_stack": False,
            "selected_gauge_passes_SK": lifetime.get("selected_passes_SK"),
            "imported_susy_hessian_withdrawn": True,
            "exact_unique_proton_lifetime": False,
            "whole_model_excluded": False,
            "whole_model_validated": False,
        },
        "verdict": (
            "The proton-lifetime Hessian closure is withdrawn. Imported SUSY "
            "fermion/gaugino singular values cannot close the non-SUSY scalar "
            "Hessian; any historical lifetime remains conditional."
        ),
    }


def main() -> int:
    argparse.ArgumentParser(description=__doc__).parse_args()
    report = build_report()
    ROOT.joinpath("TAU_P_HESSIAN_RESIDUAL_CLOSURE_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("TAU_P_HESSIAN_RESIDUAL_CLOSURE_V20.md").write_text(
        "# Proton-lifetime Hessian correction — v20\n\n" + report["verdict"] + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
