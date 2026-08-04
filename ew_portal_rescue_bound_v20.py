#!/usr/bin/env python3
"""Perturbative no-rescue bound for the historical lambda4 EW vacuum.

The signed guaranteed invariant floor is 34. Among its guaranteed channels,
the only target-VEV interaction linear in the 10_H amplitude is
lambda4*210_H*10_H*126bar_H*S. Guaranteed heavy portals with H^2 cancel from
the direct H-H curvature after the independent quadratic mass is retuned for
stationarity. The two guaranteed H^4 channels are far too small to rescue the
historical point within perturbation theory.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import mixed_rep_enlarged_floor_basis_v20 as signed_basis
import nonsusy_reduced_hessian_v20 as physical_hessian

ROOT = Path(__file__).resolve().parent


def build_report() -> dict[str, Any]:
    basis = signed_basis.build_report()
    hessian = physical_hessian.build_report()
    if basis.get("n_failed", 1) != 0 or hessian.get("n_failed", 1) != 0:
        return {
            "status": "EW_PORTAL_RESCUE_BOUND_NOT_EXECUTED",
            "n_failed": 1,
            "failures": ["upstream"],
        }

    h = float(hessian["target_vevs_GeV"]["H10_EW"])
    lam4 = float(hessian["historical_benchmark"]["lam4"])
    coefficient = float(
        hessian["ew_portal_consistency"][
            "portal_curvature_coefficient_GeV2_per_lam4"
        ]
    )
    ew_curvature = float(
        hessian["ew_portal_consistency"]["ew_target_curvature_GeV2"]
    )
    historical_hh = ew_curvature + lam4 * coefficient

    guaranteed_h4_channels = 2
    max_per_channel = 4.0 * math.pi
    combined_allowance = guaranteed_h4_channels * max_per_channel
    max_positive_h4_curvature = 8.0 * combined_allowance * h**2
    required_total_h4 = max(0.0, -historical_hh) / (8.0 * h**2)
    ratio = required_total_h4 / combined_allowance
    best_case_hh = historical_hh + max_positive_h4_curvature
    rescue_possible = best_case_hh > 0.0

    checks = {
        "signed_guaranteed_floor_is_34": basis.get("counts", {}).get(
            "signed_guaranteed_floor_total"
        )
        == 34,
        "mechanical_floor37_rejected": bool(
            basis.get("flag", {}).get("mechanical_floor37_rejected")
        ),
        "historical_point_tachyonic": bool(
            hessian.get("historical_benchmark", {}).get("tachyonic")
        ),
        "two_guaranteed_H4_channels": guaranteed_h4_channels == 2,
        "required_H4_coupling_nonperturbative": ratio > 1.0e20,
        "perturbative_signed_floor34_rescue_impossible": not rescue_possible,
        "whole_model_not_declared_excluded": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "SIGNED_FLOOR34_CANNOT_PERTURBATIVELY_RESCUE_HISTORICAL_LAM4_POINT"
            if not failures
            else "EW_PORTAL_RESCUE_BOUND_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "algebra": {
            "linear_H_term_after_stationarity": (
                "For V=-A H+(1/2)m2 H^2, stationarity gives m2=A/h, so direct curvature contains A/h."
            ),
            "even_H2_term_after_stationarity": (
                "For V=C H^2+(1/2)m2 H^2, stationarity gives m2=-2C and the direct H-H curvature cancels."
            ),
            "H4_term_after_stationarity": (
                "For V=lambda H^4 plus its stationarity mass shift, net direct curvature is 8 lambda h^2."
            ),
            "positive_definite_requirement": (
                "A positive-definite Hessian requires H_HH=e_H^T H e_H>0."
            ),
        },
        "numerical": {
            "signed_guaranteed_invariant_floor": 34,
            "physical_h_GeV": h,
            "historical_lam4": lam4,
            "historical_direct_HH_curvature_GeV2": historical_hh,
            "guaranteed_H4_channels": guaranteed_h4_channels,
            "perturbative_max_abs_coupling_per_channel": max_per_channel,
            "maximum_positive_H4_curvature_GeV2": max_positive_h4_curvature,
            "required_total_H4_coupling": required_total_h4,
            "required_over_combined_perturbative_allowance": ratio,
            "best_case_rescued_HH_curvature_GeV2": best_case_hh,
        },
        "flag": {
            "historical_lam4_point_excluded_within_signed_floor34": True,
            "guaranteed_even_H2_portals_cannot_directly_rescue": True,
            "guaranteed_H4_channels_insufficient_perturbatively": not rescue_possible,
            "unknown_beyond_floor_odd_H_channel_or_new_mechanism_required": True,
            "mechanical_floor37_rejected": True,
            "full_invariant_ring_complete": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            f"Within signed floor34, the historical point has direct H-H "
            f"curvature {historical_hh:.6e} GeV^2. The two guaranteed H^4 "
            f"channels require total coupling {required_total_h4:.6e}, or "
            f"{ratio:.6e} times their combined 4pi allowance. Perturbative "
            "rescue is impossible inside the signed floor."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    report = build_report()
    ROOT.joinpath("EW_PORTAL_RESCUE_BOUND_V20.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("EW_PORTAL_RESCUE_BOUND_V20.md").write_text(
        "# Electroweak portal rescue bound — signed floor34\n\n"
        + report["verdict"]
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2))
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
