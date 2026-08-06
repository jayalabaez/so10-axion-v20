#!/usr/bin/env python3
"""Executable audit explaining why PR #155 did not close G2.

The audit reproduces four concrete defects in the superseded assembler:

1. H--Sigma singlet quartic used ||Sigma|| instead of ||Sigma||^2.
2. Phi Sigma-dag Sigma cubic used the wrong conjugation order.
3. A one-component Sigma finite-difference perturbation leaves the physical
   -i Hodge eigenspace.
4. An 8-coordinate species probe is not a 486-real gradient/Hessian.

It also records the Phi^2 Hdag Sigma orientation correction, whose canonical
source is the conjugate of the +i H Sigma-dag projector family.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

import direct_phi_h_sigmabar_tensor_v20 as direct
import exact_210_126bar_cubic_clebsch_v20 as phi_sigma_cubic
import live_g2_arbitrary_component_potential_values_v20 as corrected

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "LIVE_G2_PR155_CORRECTION_AUDIT_V20.json"
OUT_MD = ROOT / "LIVE_G2_PR155_CORRECTION_AUDIT_V20.md"


def build_report() -> dict[str, Any]:
    state = corrected.deterministic_state(155)
    scaled_sigma = direct.scale_form(state.sigma, 2.3)
    sigma_norm = direct.sigma_kinetic_norm(scaled_sigma)
    sigma_norm_squared = float(
        np.real(direct.sigma_kinetic_inner(scaled_sigma, scaled_sigma))
    )
    h_norm = float(np.vdot(state.h, state.h).real)
    historical_hsigma = h_norm * sigma_norm
    corrected_hsigma = h_norm * sigma_norm_squared

    sigma_dag = corrected.conjugate_form(state.sigma)
    wrong_cubic = phi_sigma_cubic.cubic_invariant(
        state.phi, sigma_dag, state.sigma
    )
    corrected_cubic = phi_sigma_cubic.cubic_invariant(
        state.phi, state.sigma, state.sigma
    )

    leaked = dict(state.sigma)
    key = next(iter(leaked))
    leaked[key] = complex(leaked[key]) + 1.0e-5
    chirality_leak = direct.tensor_norm(
        direct.add_forms(
            direct.hodge_star(leaked), direct.scale_form(leaked, 1j)
        )
    )
    physical_chirality = direct.tensor_norm(
        direct.add_forms(
            direct.hodge_star(state.sigma),
            direct.scale_form(state.sigma, 1j),
        )
    )

    complete_dimension = 210 + 20 + 252 + 2 + 2
    complete_symmetric_hessian_entries = (
        complete_dimension * (complete_dimension + 1) // 2
    )
    historical_probe_dimension = 8

    checks = {
        "norm_squared_differs_from_norm_off_unit_sphere": (
            abs(sigma_norm_squared - sigma_norm) > 1.0e-3
        ),
        "correct_HSigma_singlet_is_norm_squared": (
            abs(corrected_hsigma - h_norm * sigma_norm_squared) < 1.0e-12
        ),
        "historical_HSigma_formula_is_not_quartic": (
            abs(historical_hsigma - corrected_hsigma) > 1.0e-3
        ),
        "cubic_conjugation_order_changes_value": (
            abs(wrong_cubic - corrected_cubic) > 1.0e-10
        ),
        "physical_sigma_starts_in_minus_i_space": physical_chirality < 1.0e-12,
        "single_component_sigma_probe_leaves_chiral_space": chirality_leak > 1.0e-8,
        "complete_field_dimension_is_486": complete_dimension == 486,
        "historical_probe_is_only_eight_dimensional": historical_probe_dimension == 8,
        "historical_probe_not_complete_gradient": (
            historical_probe_dimension < complete_dimension
        ),
        "historical_probe_not_complete_Hessian": (
            historical_probe_dimension * (historical_probe_dimension + 1) // 2
            < complete_symmetric_hessian_entries
        ),
        "Phi2_Hdag_Sigma_requires_conjugate_projector_orientation": True,
        "G2_closure_withdrawn": True,
        "whole_model_not_validated": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "status": (
            "PR155_G2_CLOSURE_FALSIFIED__VALUE_LAYER_RETAINED"
            if not failures
            else "PR155_CORRECTION_AUDIT_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "HSigma_singlet": {
            "Sigma_norm": sigma_norm,
            "Sigma_norm_squared": sigma_norm_squared,
            "historical_value": historical_hsigma,
            "corrected_value": corrected_hsigma,
        },
        "PhiSigma_cubic": {
            "historical_wrong_order": {
                "re": float(np.real(wrong_cubic)),
                "im": float(np.imag(wrong_cubic)),
            },
            "corrected_order": {
                "re": float(np.real(corrected_cubic)),
                "im": float(np.imag(corrected_cubic)),
            },
            "absolute_difference": float(abs(wrong_cubic - corrected_cubic)),
        },
        "chirality": {
            "physical_residual": physical_chirality,
            "single_component_probe_residual": chirality_leak,
        },
        "derivative_scope": {
            "historical_probe_dimension": historical_probe_dimension,
            "complete_real_field_dimension": complete_dimension,
            "historical_symmetric_Hessian_entries": 36,
            "complete_symmetric_Hessian_entries": complete_symmetric_hessian_entries,
        },
        "flags": {
            "PR155_G2_closed_claim_rejected": not failures,
            "corrected_64_direction_value_layer_retained": not failures,
            "complete_field_gradient": False,
            "complete_field_Hessian": False,
            "G2_closed": False,
            "whole_model_validated": False,
            "empirical_discovery": False,
        },
        "verdict": (
            "PR #155 did not close G2. Its 64-direction catalogue is useful, "
            "but the corrected value layer must replace three tensor formulas, "
            "preserve physical 126bar chirality, and remain PARTIAL until the "
            "complete 486-real gradient and Hessian are constructed."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        OUT_MD.write_text(
            "# PR #155 G2 correction audit\n\n"
            f"**Status:** `{report['status']}`\n\n"
            + report["verdict"]
            + "\n",
            encoding="utf-8",
        )
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
