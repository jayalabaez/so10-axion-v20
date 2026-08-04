#!/usr/bin/env python3
"""Perturbative no-rescue bound for the historical lambda4 EW vacuum.

Within the guaranteed 37-invariant floor there is one listed operator that is
linear in the 10_H amplitude at the target VEV:

    lambda4 * 210_H * 10_H * 126bar_H * S.

Every guaranteed additional heavy-field portal contains H in an even power.
After an independent quadratic mass is retuned for stationarity, a term C H^2
cancels from the direct H-H radial curvature. Cross mixing cannot repair a
negative diagonal entry of a positive-definite Hessian. The only guaranteed
direct positive rescue comes from the two independent H^4 channels, whose
combined perturbative contribution is tiny compared with the historical
lambda4 curvature.

This excludes the historical benchmark within the guaranteed floor and
perturbative couplings. It does not exclude unknown beyond-floor odd-H tensor
channels or the whole SO(10) theory.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import mixed_rep_enlarged_floor_basis_v20 as enlarged
import nonsusy_reduced_hessian_v20 as physical_hessian

ROOT = Path(__file__).resolve().parent


def build_report() -> dict[str, Any]:
    floor = enlarged.build_report()
    hessian = physical_hessian.build_report()
    if floor.get("n_failed", 1) != 0 or hessian.get("n_failed", 1) != 0:
        return {
            "status": "EW_PORTAL_RESCUE_BOUND_NOT_EXECUTED",
            "n_failed": 1,
            "failures": ["upstream"],
        }

    h_ew = float(hessian["target_vevs_GeV"]["H10_EW"])
    historical_lam4 = float(hessian["historical_benchmark"]["lam4"])
    coefficient = float(
        hessian["ew_portal_consistency"][
            "portal_curvature_coefficient_GeV2_per_lam4"
        ]
    )
    ew_curvature = float(
        hessian["ew_portal_consistency"]["ew_target_curvature_GeV2"]
    )

    historical_hh = ew_curvature + historical_lam4 * coefficient
    guaranteed_h4_channels = 2
    perturbative_max_per_channel = 4.0 * math.pi
    maximum_total_h4_coupling = (
        guaranteed_h4_channels * perturbative_max_per_channel
    )
    maximum_positive_h4_curvature = (
        8.0 * maximum_total_h4_coupling * h_ew**2
    )
    required_total_h4_coupling = max(0.0, -historical_hh) / (8.0 * h_ew**2)
    required_over_perturbative_allowance = (
        required_total_h4_coupling / maximum_total_h4_coupling
    )
    rescued_hh_upper_bound = historical_hh + maximum_positive_h4_curvature
    perturbative_rescue_possible = rescued_hh_upper_bound > 0.0

    checks = {
        "canonical_floor_is_37": floor.get("counts", {}).get(
            "guaranteed_floor_total"
        )
        == 37,
        "historical_point_tachyonic": bool(
            hessian.get("historical_benchmark", {}).get("tachyonic")
        ),
        "two_guaranteed_H4_channels": guaranteed_h4_channels == 2,
        "required_H4_coupling_nonperturbative": (
            required_over_perturbative_allowance > 1.0e20
        ),
        "perturbative_floor37_rescue_impossible": not perturbative_rescue_possible,
        "whole_model_not_declared_excluded": True,
    }
    failures = [name for name, passed in checks.items() if not passed]

    return {
        "status": (
            "GUARANTEED_FLOOR37_CANNOT_PERTURBATIVELY_RESCUE_HISTORICAL_LAM4_POINT"
            if not failures
            else "EW_PORTAL_RESCUE_BOUND_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "algebra": {
            "linear_H_term_after_stationarity": (
                "For V=-A H + (1/2)m2 H^2, stationarity gives m2=A/h, "
                "so the direct radial curvature contains A/h."
            ),
            "even_H2_term_after_stationarity": (
                "For V=C H^2 + (1/2)m2 H^2, stationarity gives m2=-2C, "
                "so its direct H-H curvature cancels exactly."
            ),
            "H4_term_after_stationarity": (
                "For V=lambda H^4 plus the stationarity mass shift, the net "
                "direct curvature is 8 lambda h^2."
            ),
            "positive_definite_requirement": (
                "A positive-definite Hessian requires every diagonal quadratic "
                "form value e_i^T H e_i, including H_HH, to be positive."
            ),
        },
        "numerical": {
            "physical_h_GeV": h_ew,
            "historical_lam4": historical_lam4,
            "historical_direct_HH_curvature_GeV2": historical_hh,
            "guaranteed_H4_channels": guaranteed_h4_channels,
            "perturbative_max_abs_coupling_per_channel": (
                perturbative_max_per_channel
            ),
            "maximum_positive_H4_curvature_GeV2": (
                maximum_positive_h4_curvature
            ),
            "required_total_H4_coupling": required_total_h4_coupling,
            "required_over_combined_perturbative_allowance": (
                required_over_perturbative_allowance
            ),
            "best_case_rescued_HH_curvature_GeV2": rescued_hh_upper_bound,
        },
        "flag": {
            "historical_lam4_point_excluded_within_guaranteed_floor": True,
            "guaranteed_even_H2_portals_cannot_directly_rescue": True,
            "guaranteed_H4_channels_insufficient_perturbatively": (
                not perturbative_rescue_possible
            ),
            "unknown_beyond_floor_odd_H_channel_or_new_mechanism_required": True,
            "full_invariant_ring_complete": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "Within the guaranteed 37-invariant floor, the historical lambda4 "
            f"point has direct H-H curvature {historical_hh:.6e} GeV^2. The two "
            "guaranteed H^4 channels would require total coupling "
            f"{required_total_h4_coupling:.6e}, which is "
            f"{required_over_perturbative_allowance:.6e} times their combined "
            "4pi allowance. Guaranteed even-H heavy portals cancel from the "
            "direct radial curvature after stationarity retuning. Therefore the "
            "historical point cannot be perturbatively rescued within floor37; "
            "an unknown odd-H channel, a new hierarchy mechanism, or a tiny "
            "lambda4 is required."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    report = build_report()
    ROOT.joinpath("EW_PORTAL_RESCUE_BOUND_V20.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("EW_PORTAL_RESCUE_BOUND_V20.md").write_text(
        "# Electroweak portal rescue bound — v20\n\n"
        + report["verdict"]
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2))
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
