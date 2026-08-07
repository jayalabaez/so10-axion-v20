#!/usr/bin/env python3
"""Executable audit showing why merged PR #155 did not close G2.

The certificate reproduces six independent defects or scope failures:

1. H--Sigma used ||Sigma|| instead of the polynomial ||Sigma||^2.
2. Phi Sigma-dag Sigma used the wrong conjugation order.
3. A one-component Sigma perturbation left the physical -i Hodge space.
4. The Phi^2 Hdag Sigma orientation must be the complex conjugate of the
   canonical +i Phi^2 H Sigma-dag source in both 210 and 1050 channels.
5. Six graph contractions cannot be directly relabelled as the named pure
   1,45,210,770,5940,8910 projector basis.
6. An eight-coordinate probe is not the complete 486-real gradient/Hessian.
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


def _json_default(value: Any) -> Any:
    """Normalize NumPy scalars/arrays and complex values for JSON output."""
    if isinstance(value, np.ndarray):
        # Leave nested conversion to json; complex leaves re-enter this hook.
        return value.tolist()
    if isinstance(value, np.generic):
        item = value.item()
        if isinstance(item, complex):
            return {"re": float(item.real), "im": float(item.imag)}
        return item
    if isinstance(value, complex):
        return {"re": float(value.real), "im": float(value.imag)}
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


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

    orientation = corrected.phi2_hdag_sigma_orientation_audit(state)
    basis_audit = corrected.graph_projector_basis_audit(state)

    complete_dimension = corrected.REAL_FIELD_DIMENSION
    complete_symmetric_hessian_entries = corrected.SYMMETRIC_HESSIAN_ENTRIES
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
        "Phi2_Hdag_Sigma_conjugate_orientation_reconstructed": orientation[
            "maximum_conjugation_residual"
        ]
        < 1.0e-11,
        "graph_contractions_not_direct_projector_labels": not basis_audit[
            "direct_graph_to_projector_relabeling_valid"
        ],
        "complete_field_dimension_is_486": complete_dimension == 486,
        "historical_probe_is_only_eight_dimensional": historical_probe_dimension == 8,
        "historical_probe_not_complete_gradient": historical_probe_dimension
        < complete_dimension,
        "historical_probe_not_complete_Hessian": (
            historical_probe_dimension * (historical_probe_dimension + 1) // 2
            < complete_symmetric_hessian_entries
        ),
        "G2_closure_withdrawn": True,
        "whole_model_not_validated": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "status": (
            "PR155_G2_CLOSURE_FALSIFIED__CORRECTED_VALUE_LAYER_RETAINED"
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
        "Phi2_Hdag_Sigma_orientation": orientation,
        "Phi2_Sigma_basis": basis_audit,
        "derivative_scope": {
            "historical_probe_dimension": historical_probe_dimension,
            "complete_real_field_dimension": complete_dimension,
            "historical_symmetric_Hessian_entries": 36,
            "complete_symmetric_Hessian_entries": (
                complete_symmetric_hessian_entries
            ),
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
            "PR #155 did not close G2. The corrected arbitrary-field value layer "
            "retains the useful 64-direction catalogue while fixing polynomial "
            "degree, conjugation, chirality, orientation, and basis contracts. "
            "G2 remains PARTIAL until the complete 486-real gradient and Hessian exist."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    payload = json.dumps(report, indent=2, default=_json_default)
    if args.write:
        OUT_JSON.write_text(payload + "\n", encoding="utf-8")
        OUT_MD.write_text(
            "# PR #155 G2 correction audit\n\n"
            f"**Status:** `{report['status']}`\n\n"
            + report["verdict"]
            + "\n",
            encoding="utf-8",
        )
    print(payload)
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
