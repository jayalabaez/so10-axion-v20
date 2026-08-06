#!/usr/bin/env python3
"""Combine the gauge falsification gate with the canonical signed scalar proxy."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable

import nonsusy_charge_allowed_mt_v20 as signed_mt2
import proton_decay_falsification_gate_v20 as gauge_gate

ROOT = Path(__file__).resolve().parent


def build_report(
    *,
    gauge_loader: Callable[[], dict[str, Any]] = gauge_gate.build_report,
    scalar_loader: Callable[[], dict[str, Any]] = signed_mt2.build_report,
) -> dict[str, Any]:
    gauge = gauge_loader()
    scalar = scalar_loader()
    sflag = dict(scalar.get("flag") or {})
    conditional_scalar_failures = int(scalar.get("n_excluded_by_ps_mu_K0", 0) or 0)
    checks = {
        "gauge_gate_executes": gauge.get("n_failed", 1) == 0,
        "signed_scalar_gate_executes": scalar.get("n_failed", 1) == 0,
        "scalar_uses_mass_squared": bool(sflag.get("mass_squared_matrix_used")),
        "forbidden_210_10dag10_absent": bool(sflag.get("forbidden_210_10dag10_absent")),
        "forbidden_10_126_S_absent": bool(sflag.get("forbidden_10_126_S_absent")),
        "component_cg_remains_open": not bool(sflag.get("physical_component_CG_complete")),
        "physical_triplet_spectrum_remains_open": not bool(sflag.get("physical_triplet_spectrum_complete")),
        "no_unique_proton_lifetime": not bool(gauge["classification"]["exact_unique_proton_lifetime_derived"]),
        "whole_model_not_excluded": not bool(gauge["classification"]["whole_model_excluded_by_proton_decay"]),
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "status": (
            "PROTON_DECAY_GAUGE_PLUS_SIGNED_SCALAR_CONDITIONAL"
            if not failures else "PROTON_DECAY_SIGNED_SCALAR_BRIDGE_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "gauge": {
            "conditional_points_below_limit": gauge["classification"]["conditional_points_below_limit"],
            "conditional_points_above_limit": gauge["classification"]["conditional_points_above_limit"],
            "benchmarks": gauge.get("benchmarks", {}),
        },
        "signed_scalar": {
            "status": scalar.get("status"),
            "n_scenarios": int(scalar.get("n_scenarios", 0) or 0),
            "n_conditionally_excluded": conditional_scalar_failures,
            "excluded_scenario_names": scalar.get("excluded_scenario_names", []),
            "lightest_scenario": scalar.get("lightest_scenario"),
            "physical_component_CG_complete": bool(sflag.get("physical_component_CG_complete")),
            "physical_triplet_spectrum_complete": bool(sflag.get("physical_triplet_spectrum_complete")),
            "conditional_only": True,
        },
        "classification": {
            "proton_decay_observed": False,
            "conditional_gauge_points_fail": bool(gauge["classification"]["conditional_points_below_limit"]),
            "conditional_scalar_points_fail": conditional_scalar_failures > 0,
            "exact_unique_proton_lifetime_derived": False,
            "whole_model_excluded_by_proton_decay": False,
            "authoritative_answer": "GAUGE_AND_SIGNED_SCALAR_CONDITIONAL_POINTS_ONLY__MODEL_VERDICT_OPEN",
        },
        "checks": checks,
        "next_exact_calculation": scalar.get("next_exact_calculation", []),
        "verdict": (
            "Gauge and signed scalar scans contain conditional failures, but the "
            "scalar component CG coefficients and physical triplet spectrum are open. "
            "No proton-decay discovery or unique whole-model exclusion is derived."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    report = build_report()
    ROOT.joinpath("PROTON_DECAY_SIGNED_SCALAR_BRIDGE_V20.json").write_text(
        json.dumps(report, indent=2, default=str) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2, default=str))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
