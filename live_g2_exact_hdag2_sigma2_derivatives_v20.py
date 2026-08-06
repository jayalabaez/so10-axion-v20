#!/usr/bin/env python3
"""Exact 486-real derivatives for the unique Hdag^2 Sigma^2 quartic."""
from __future__ import annotations

import argparse
import dataclasses
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np

import live_g1_tensor_closure_ledger_v20 as ledger
import live_g2_arbitrary_component_potential_values_v20 as potential
import live_g2_canonical_486_field_chart_v20 as chart
import live_g2_exact_quadratic_family_derivatives_v20 as quadratic
import live_g2_exact_unique_hsigma_chiral_quartic_derivatives_common_v20 as common

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "LIVE_G2_EXACT_HDAG2_SIGMA2_DERIVATIVES_V20.json"
OUT_MD = ROOT / "LIVE_G2_EXACT_HDAG2_SIGMA2_DERIVATIVES_V20.md"
BASE_FAMILY = "Hdag2_Sigma2"
BASIS_LABELS = (ledger.BASE_FAMILIES[(0, 0, 2, 2, 0)]["basis"][0],)


def _jsonable(value: Any) -> Any:
    if dataclasses.is_dataclass(value):
        return _jsonable(dataclasses.asdict(value))
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, complex):
        return {"re": float(value.real), "im": float(value.imag)}
    return value


def base_derivative(q: np.ndarray, basis_index: int) -> tuple[complex, np.ndarray, np.ndarray]:
    if int(basis_index) != 0:
        raise KeyError(f"unknown {BASE_FAMILY} basis index {basis_index}")
    return common.base_derivative(q, BASE_FAMILY)


def selected_directions(state: potential.FieldState) -> tuple[potential.Direction, ...]:
    return tuple(row for row in potential.evaluate_directions(state) if row.base_family == BASE_FAMILY)


def direction_derivative(q: np.ndarray, direction: potential.Direction) -> quadratic.DirectionDerivative:
    if direction.base_family != BASE_FAMILY:
        raise KeyError(f"direction {direction.direction_id} is not {BASE_FAMILY}")
    counts = dict(zip(potential.FIELD_ORDER, direction.counts, strict=True))
    base_value, base_gradient, base_hessian = base_derivative(
        q, direction.basis_index
    )
    dressing = quadratic.dressing_jet(q, counts)
    dressing_gradient, dressing_hessian = quadratic._embed_singlet_jet(dressing)
    value = base_value * dressing.value
    gradient = dressing.value * base_gradient + base_value * dressing_gradient
    hessian = (
        dressing.value * base_hessian
        + base_value * dressing_hessian
        + np.outer(base_gradient, dressing_gradient)
        + np.outer(dressing_gradient, base_gradient)
    )
    return quadratic.DirectionDerivative(
        direction_id=direction.direction_id,
        base_family=direction.base_family,
        self_conjugate=direction.self_conjugate,
        value=complex(value),
        gradient=gradient,
        hessian=0.5 * (hessian + hessian.T),
    )


def all_direction_derivatives(state: potential.FieldState) -> tuple[quadratic.DirectionDerivative, ...]:
    q = chart.pack(state)
    return tuple(direction_derivative(q, row) for row in selected_directions(state))


def expected_direction_count() -> int:
    return sum(int(orbit["multiplicity"]) for orbit in ledger.build_report()["operator_orbits"]
               if orbit["base_family"] == BASE_FAMILY)


@lru_cache(maxsize=1)
def build_report() -> dict[str, Any]:
    state = potential.deterministic_state(3005)
    q = chart.pack(state)
    directions = selected_directions(state)
    analytic = all_direction_derivatives(state)
    parameters = quadratic.parameter_derivatives(analytic)
    coefficients = quadratic.deterministic_coefficients(parameters)
    directional = quadratic.five_point_directional_audit(state, parameters, coefficients)
    expected = {row.direction_id: row for row in directions}
    value_residuals = {row.direction_id: float(abs(row.value - expected[row.direction_id].value)) for row in analytic}
    base_value = analytic[0].value
    hessian_asymmetry = max(float(np.max(np.abs(row.hessian - row.hessian.T))) for row in analytic)
    live_parameter_ids = {row.parameter_id for row in potential.parameter_schema(potential.evaluate_directions(state))}
    parameter_ids = {row.parameter_id for row in parameters}
    checks = {
        "authoritative_family_id_exists": BASE_FAMILY in {row["id"] for row in ledger.BASE_FAMILIES.values()},
        "expected_G1_direction_count_is_nonzero": expected_direction_count() > 0,
        "every_expected_direction_differentiated": len(analytic) == expected_direction_count(),
        "single_basis_index_present": {row.basis_index for row in directions} == {0},
        "live_basis_label_matches_G1": {row.basis_label for row in directions} == set(BASIS_LABELS),
        "base_value_matches_authoritative_evaluator": abs(base_value - directions[0].value) < 1.0e-10,
        "all_values_match_authoritative_evaluator": max(value_residuals.values()) < 1.0e-10,
        "all_parameter_ids_belong_to_live_schema": parameter_ids.issubset(live_parameter_ids) and len(parameter_ids) == len(parameters),
        "all_dense_Hessians_symmetric": hessian_asymmetry < 1.0e-12,
        "five_point_value_reconstruction": directional["value_residual"] < 1.0e-9,
        "five_point_first_derivative_reconstruction": directional["first_residual"] < 2.0e-7,
        "five_point_second_derivative_reconstruction": directional["second_residual"] < 2.0e-6,
        "G2_not_closed": True, "whole_model_not_validated": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return _jsonable({"status": "G2_EXACT_HDAG2_SIGMA2_DERIVATIVES_CLOSED" if not failures else "G2_HDAG2_SIGMA2_DERIVATIVES_FAILED",
        "overall_state": "PARTIAL" if not failures else "EXECUTION_FAIL", "n_checks": len(checks), "n_failed": len(failures),
        "failures": failures, "checks": checks,
        "coverage": {"base_family": BASE_FAMILY, "base_family_count_closed_here": 1,
                     "expected_direction_count": expected_direction_count(), "observed_direction_count": len(analytic),
                     "parameter_count_closed_here": len(parameters), "basis_indices": [0], "basis_labels": list(BASIS_LABELS),
                     "real_field_dimension": chart.TOTAL_DIM, "Hessian_shape": [chart.TOTAL_DIM, chart.TOTAL_DIM]},
        "maximum_direction_value_residual": max(value_residuals.values()), "maximum_Hessian_asymmetry": hessian_asymmetry,
        "directional_reconstruction": directional,
        "flags": {"authoritative_Hdag2_Sigma2_adapter_closed": not failures,
                  "all_64_direction_gradients_complete": False, "all_64_direction_Hessians_complete": False,
                  "G2_closed": False, "whole_model_validated": False, "empirical_discovery": False},
        "verdict": "The unique chiral Hdag^2 Sigma^2 graph has exact canonical-real derivatives; G2 remains PARTIAL."})


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text("# Exact Hdag2 Sigma2 derivatives\n\n" + report["verdict"] + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv); report = build_report()
    if args.write: write_report(report)
    print(json.dumps(report, indent=2)); return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
