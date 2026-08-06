#!/usr/bin/env python3
"""Exact 486-real derivatives for the four real-210 self quartics."""
from __future__ import annotations

import argparse
import dataclasses
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
from scipy import sparse

import exact_210_self_invariant_basis_v20 as source
import exact_phisigma_casimir_projectors_v20 as projectors
import live_g1_tensor_closure_ledger_v20 as ledger
import live_g2_arbitrary_component_potential_values_v20 as potential
import live_g2_canonical_486_field_chart_v20 as chart
import live_g2_exact_quadratic_family_derivatives_v20 as quadratic

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "LIVE_G2_EXACT_PHI_SELF_QUARTIC_DERIVATIVES_V20.json"
OUT_MD = ROOT / "LIVE_G2_EXACT_PHI_SELF_QUARTIC_DERIVATIVES_V20.md"
BASE_FAMILY = "Phi_self_quartics"
BASIS_LABELS = ("J0", "J2", "J3", "J4")
DEGREES = (0, 2, 3, 4)


def _jsonable(value: Any) -> Any:
    if dataclasses.is_dataclass(value):
        return _jsonable(dataclasses.asdict(value))
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, complex):
        return {"re": float(value.real), "im": float(value.imag)}
    return value


@lru_cache(maxsize=1)
def pair_operator() -> sparse.csr_matrix:
    """Matrix of K on column-major vectorized 210x210 pair matrices."""
    result = sparse.csr_matrix((chart.PHI_DIM**2, chart.PHI_DIM**2), dtype=float)
    for generator in projectors.generator_matrices():
        result += sparse.kron(generator, generator, format="csr")
    return result


def _apply_power_to_columns(columns: np.ndarray, degree: int) -> np.ndarray:
    output = np.asarray(columns, dtype=float)
    for _ in range(degree):
        output = pair_operator() @ output
    return output


def _power_matrix(pair: np.ndarray, degree: int) -> np.ndarray:
    return _apply_power_to_columns(
        np.asarray(pair, dtype=float).reshape(-1, 1, order="F"), degree
    ).reshape(chart.PHI_DIM, chart.PHI_DIM, order="F")


def phi_quartic_derivatives(
    phi: np.ndarray, degree: int
) -> tuple[float, np.ndarray, np.ndarray]:
    """Return M_d=<S,K^d S> and its real-210 gradient and Hessian."""
    vector = np.asarray(phi, dtype=float).reshape(chart.PHI_DIM)
    pair = np.outer(vector, vector)
    image = _power_matrix(pair, degree)
    value = float(np.sum(pair * image))
    gradient = 4.0 * image @ vector

    basis = np.eye(chart.PHI_DIM)
    variations = (
        vector[:, None, None] * basis[None, :, :]
        + basis[:, None, :] * vector[None, :, None]
    )
    image_variations = _apply_power_to_columns(
        variations.reshape(chart.PHI_DIM**2, chart.PHI_DIM, order="F"), degree
    ).reshape(chart.PHI_DIM, chart.PHI_DIM, chart.PHI_DIM, order="F")
    hessian = 4.0 * (
        np.einsum("ija,j->ia", image_variations, vector, optimize=True) + image
    )
    return value, gradient, 0.5 * (hessian + hessian.T)


def base_derivative(q: np.ndarray, basis_index: int) -> tuple[complex, np.ndarray, np.ndarray]:
    index = int(basis_index)
    if index not in range(len(BASIS_LABELS)):
        raise KeyError(f"unknown Phi self-quartic basis index {basis_index}")
    coordinates = np.asarray(q, dtype=float).reshape(chart.TOTAL_DIM)
    value, local_gradient, local_hessian = phi_quartic_derivatives(
        coordinates[chart.PHI_SLICE], DEGREES[index]
    )
    gradient = np.zeros(chart.TOTAL_DIM, dtype=complex)
    hessian = np.zeros((chart.TOTAL_DIM, chart.TOTAL_DIM), dtype=complex)
    gradient[chart.PHI_SLICE] = local_gradient
    hessian[chart.PHI_SLICE, chart.PHI_SLICE] = local_hessian
    return complex(value), gradient, hessian


def selected_directions(state: potential.FieldState) -> tuple[potential.Direction, ...]:
    return tuple(row for row in potential.evaluate_directions(state) if row.base_family == BASE_FAMILY)


def direction_derivative(q: np.ndarray, direction: potential.Direction) -> quadratic.DirectionDerivative:
    if direction.base_family != BASE_FAMILY:
        raise KeyError(f"direction {direction.direction_id} is not {BASE_FAMILY}")
    counts = dict(zip(potential.FIELD_ORDER, direction.counts, strict=True))
    base_value, base_gradient, base_hessian = base_derivative(q, direction.basis_index)
    dressing = quadratic.dressing_jet(q, counts)
    dressing_gradient, dressing_hessian = quadratic._embed_singlet_jet(dressing)
    hessian = (
        dressing.value * base_hessian + base_value * dressing_hessian
        + np.outer(base_gradient, dressing_gradient)
        + np.outer(dressing_gradient, base_gradient)
    )
    return quadratic.DirectionDerivative(
        direction_id=direction.direction_id, base_family=direction.base_family,
        self_conjugate=direction.self_conjugate, value=complex(base_value * dressing.value),
        gradient=dressing.value * base_gradient + base_value * dressing_gradient,
        hessian=0.5 * (hessian + hessian.T),
    )


def all_direction_derivatives(state: potential.FieldState) -> tuple[quadratic.DirectionDerivative, ...]:
    q = chart.pack(state)
    return tuple(direction_derivative(q, row) for row in selected_directions(state))


def expected_direction_count() -> int:
    return sum(int(row["multiplicity"]) for row in ledger.build_report()["operator_orbits"]
               if row["base_family"] == BASE_FAMILY)


def source_normalization_audit(state: potential.FieldState) -> dict[str, Any]:
    q = chart.pack(state)
    expected = source.quartic_invariants(state.phi)
    residuals = {label: float(abs(base_derivative(q, index)[0] - expected[label]))
                 for index, label in enumerate(BASIS_LABELS)}
    return {"source_values": expected, "residuals": residuals,
            "maximum_residual": max(residuals.values())}


def base_support_audit(q: np.ndarray) -> dict[str, dict[str, float]]:
    inactive = np.ones(chart.TOTAL_DIM, dtype=bool)
    inactive[chart.PHI_SLICE] = False
    result = {}
    for index, label in enumerate(BASIS_LABELS):
        _, gradient, hessian = base_derivative(q, index)
        result[label] = {
            "inactive_gradient_residual": float(np.max(np.abs(gradient[inactive]), initial=0.0)),
            "inactive_Hessian_residual": float(max(
                np.max(np.abs(hessian[inactive, :]), initial=0.0),
                np.max(np.abs(hessian[:, inactive]), initial=0.0))),
        }
    return result


@lru_cache(maxsize=1)
def build_report() -> dict[str, Any]:
    state = potential.deterministic_state(3404)
    q = chart.pack(state)
    directions = selected_directions(state)
    analytic = all_direction_derivatives(state)
    parameters = quadratic.parameter_derivatives(analytic)
    directional = quadratic.five_point_directional_audit(
        state, parameters, quadratic.deterministic_coefficients(parameters)
    )
    expected = {row.direction_id: row for row in directions}
    residuals = {row.direction_id: float(abs(row.value - expected[row.direction_id].value)) for row in analytic}
    normalization = source_normalization_audit(state)
    support = base_support_audit(q)
    support_residual = max(max(row.values()) for row in support.values())
    hessian_asymmetry = max(float(np.max(np.abs(row.hessian - row.hessian.T))) for row in analytic)
    self_imaginary = max([max(abs(row.value.imag), float(np.max(np.abs(row.gradient.imag))),
                              float(np.max(np.abs(row.hessian.imag))))
                          for row in analytic if row.self_conjugate] or [0.0])
    basis_indices = sorted({row.basis_index for row in directions})
    basis_labels = sorted({row.basis_label for row in directions})
    live_ids = {row.parameter_id for row in potential.parameter_schema(potential.evaluate_directions(state))}
    parameter_ids = {row.parameter_id for row in parameters}
    checks = {
        "authoritative_family_id_exists": BASE_FAMILY in {row["id"] for row in ledger.BASE_FAMILIES.values()},
        "expected_G1_direction_count_is_nonzero": expected_direction_count() > 0,
        "every_expected_direction_differentiated": len(analytic) == expected_direction_count(),
        "all_four_basis_indices_present": basis_indices == [0, 1, 2, 3],
        "all_four_basis_labels_present": basis_labels == sorted(BASIS_LABELS),
        "projector_values_match_authoritative_source": normalization["maximum_residual"] < 1.0e-10,
        "all_values_match_authoritative_evaluator": max(residuals.values()) < 1.0e-10,
        "all_parameter_ids_belong_to_live_schema": parameter_ids.issubset(live_ids) and len(parameter_ids) == len(parameters) and bool(parameters),
        "base_derivatives_supported_only_on_Phi": support_residual < 1.0e-12,
        "all_dense_Hessians_symmetric": hessian_asymmetry < 1.0e-10,
        "self_conjugate_derivatives_real": self_imaginary < 1.0e-10,
        "five_point_value_reconstruction": directional["value_residual"] < 1.0e-9,
        "five_point_first_derivative_reconstruction": directional["first_residual"] < 2.0e-7,
        "five_point_second_derivative_reconstruction": directional["second_residual"] < 2.0e-6,
        "G2_not_closed": True, "whole_model_not_validated": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return _jsonable({"status": "G2_EXACT_PHI_SELF_QUARTIC_DERIVATIVES_CLOSED" if not failures else "G2_PHI_SELF_QUARTIC_DERIVATIVES_FAILED",
        "overall_state": "PARTIAL" if not failures else "EXECUTION_FAIL", "n_checks": len(checks),
        "n_failed": len(failures), "failures": failures, "checks": checks,
        "coverage": {"base_family": BASE_FAMILY, "base_family_count_closed_here": 1,
            "cumulative_base_family_count_with_parents": 12, "base_family_count_total": len(ledger.BASE_FAMILIES),
            "remaining_base_families": 6, "expected_direction_count": expected_direction_count(),
            "observed_direction_count": len(analytic), "parameter_count_closed_here": len(parameters),
            "basis_indices": basis_indices, "basis_labels": basis_labels, "real_field_dimension": chart.TOTAL_DIM,
            "Hessian_shape": [chart.TOTAL_DIM, chart.TOTAL_DIM]},
        "source_normalization_audit": normalization, "base_support_audit": support,
        "maximum_base_support_residual": support_residual, "maximum_direction_value_residual": max(residuals.values()),
        "maximum_Hessian_asymmetry": hessian_asymmetry, "maximum_self_conjugate_imaginary_residual": self_imaginary,
        "directional_reconstruction": directional,
        "flags": {"authoritative_Phi_self_quartic_adapter_closed": not failures,
            "all_64_direction_gradients_complete": False, "all_64_direction_Hessians_complete": False,
            "G2_closed": False, "whole_model_validated": False, "empirical_discovery": False},
        "verdict": "The J0, J2, J3, and J4 real-210 self quartics have exact dense derivatives; G2 remains PARTIAL."})


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text("# Exact Phi self-quartic derivatives\n\n" + report["verdict"] + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        write_report(report)
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
