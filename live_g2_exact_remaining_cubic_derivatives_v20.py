#!/usr/bin/env python3
"""Exact 486-real derivatives for the remaining two cubic G2 families.

This module closes derivative adapters for

* ``Phi_cubic`` with I3=Tr(A_Phi^3);
* ``Phi_Sigma_Sigmadag_cubic`` with I=Sigma^dag M(Phi) Sigma.

For the pure-210 cubic, the exact gradient and Hessian follow from matrix
calculus.  For the mixed cubic, 210 Hermitian 126x126 coefficient operators are
constructed directly from the double-interior contraction used by the
authoritative evaluator.  Canonical realification then gives the complete
252-real Sigma block and all Phi-Sigma cross derivatives.

All live singlet dressings are included by exact product rules.  Together with
the parent derivative PRs this targets nine of eighteen base families; nine
quartic families and G2 remain open.
"""
from __future__ import annotations

import argparse
import dataclasses
import itertools
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np

import direct_phi_h_sigmabar_tensor_v20 as direct
import exact_210_126bar_cubic_clebsch_v20 as phi_sigma_source
import exact_210_self_invariant_basis_v20 as phi_self
import live_g1_tensor_closure_ledger_v20 as ledger
import live_g2_arbitrary_component_potential_values_v20 as potential
import live_g2_canonical_486_field_chart_v20 as chart
import live_g2_exact_quadratic_family_derivatives_v20 as quadratic

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "LIVE_G2_EXACT_REMAINING_CUBIC_DERIVATIVES_V20.json"
OUT_MD = ROOT / "LIVE_G2_EXACT_REMAINING_CUBIC_DERIVATIVES_V20.md"

SELECTED_FAMILIES = (
    "Phi_Sigma_Sigmadag_cubic",
    "Phi_cubic",
)
THREE_INDICES = tuple(itertools.combinations(range(10), 3))
THREE_INDEX = {indices: index for index, indices in enumerate(THREE_INDICES)}
SQRT2 = float(np.sqrt(2.0))


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


@lru_cache(maxsize=1)
def phi_two_form_basis() -> np.ndarray:
    return np.asarray(
        [
            phi_self.two_form_matrix({indices: 1.0 + 0.0j})
            for indices in chart.PHI_INDICES
        ],
        dtype=float,
    )


def _double_interior_coordinates(
    state: direct.Form, first: int, second: int
) -> np.ndarray:
    form = direct.interior(direct.interior(state, first), second)
    return np.asarray(
        [form.get(indices, 0.0) for indices in THREE_INDICES],
        dtype=complex,
    )


@lru_cache(maxsize=1)
def double_interior_table() -> np.ndarray:
    """D[i,j,A,k] for the exact physical 126bar basis."""
    table = np.zeros(
        (10, 10, chart.SIGMA_COMPLEX_DIM, len(THREE_INDICES)),
        dtype=complex,
    )
    for first in range(10):
        for second in range(10):
            if first == second:
                continue
            for state_index, state in enumerate(chart.sigma_basis()):
                table[first, second, state_index] = (
                    _double_interior_coordinates(state, first, second)
                )
    return table


@lru_cache(maxsize=1)
def phi_sigma_operators() -> np.ndarray:
    """M[p,A,B] for Phi_p Sigma_A^dag Sigma_B."""
    table = double_interior_table()
    operators = np.empty(
        (chart.PHI_DIM, chart.SIGMA_COMPLEX_DIM, chart.SIGMA_COMPLEX_DIM),
        dtype=complex,
    )
    for phi_index, (a, b, c, d) in enumerate(chart.PHI_INDICES):
        first = table[a, b].conj() @ table[c, d].T
        second = table[a, c].conj() @ table[b, d].T
        third = table[a, d].conj() @ table[b, c].T
        operators[phi_index] = 2.0 * (first - second + third)
    return operators


def realify_hermitian_interleaved(matrix: np.ndarray) -> np.ndarray:
    value = np.asarray(matrix, dtype=complex).reshape(
        chart.SIGMA_COMPLEX_DIM, chart.SIGMA_COMPLEX_DIM
    )
    real = value.real
    imaginary = value.imag
    output = np.zeros(
        (chart.SIGMA_REAL_DIM, chart.SIGMA_REAL_DIM), dtype=float
    )
    u = 2 * np.arange(chart.SIGMA_COMPLEX_DIM)
    v = u + 1
    output[np.ix_(u, u)] = real
    output[np.ix_(u, v)] = -imaginary
    output[np.ix_(v, u)] = imaginary
    output[np.ix_(v, v)] = real
    return output


def _phi_cubic_derivative(
    q: np.ndarray,
) -> tuple[complex, np.ndarray, np.ndarray]:
    coordinates = np.asarray(q, dtype=float).reshape(chart.TOTAL_DIM)
    phi = coordinates[chart.PHI_SLICE]
    basis = phi_two_form_basis()
    matrix = np.tensordot(phi, basis, axes=(0, 0))
    matrix_squared = matrix @ matrix
    value = float(np.trace(matrix_squared @ matrix))
    phi_gradient = 3.0 * np.einsum(
        "ij,pji->p", matrix_squared, basis, optimize=True
    )
    phi_hessian = np.empty((chart.PHI_DIM, chart.PHI_DIM), dtype=float)
    for index, basis_matrix in enumerate(basis):
        derivative_square = matrix @ basis_matrix + basis_matrix @ matrix
        phi_hessian[index] = 3.0 * np.einsum(
            "ij,pji->p", derivative_square, basis, optimize=True
        )
    gradient = np.zeros(chart.TOTAL_DIM, dtype=complex)
    hessian = np.zeros((chart.TOTAL_DIM, chart.TOTAL_DIM), dtype=complex)
    gradient[chart.PHI_SLICE] = phi_gradient
    hessian[chart.PHI_SLICE, chart.PHI_SLICE] = 0.5 * (
        phi_hessian + phi_hessian.T
    )
    return complex(value), gradient, hessian


def _phi_sigma_cubic_derivative(
    q: np.ndarray,
) -> tuple[complex, np.ndarray, np.ndarray]:
    coordinates = np.asarray(q, dtype=float).reshape(chart.TOTAL_DIM)
    phi = coordinates[chart.PHI_SLICE]
    sigma_real = coordinates[chart.SIGMA_SLICE]
    sigma = (sigma_real[0::2] + 1j * sigma_real[1::2]) / SQRT2
    operators = phi_sigma_operators()
    matrix = np.tensordot(phi, operators, axes=(0, 0))
    image = matrix @ sigma
    value = complex(np.vdot(sigma, image))
    phi_gradient = np.einsum(
        "a,pab,b->p", np.conjugate(sigma), operators, sigma, optimize=True
    )
    sigma_hessian = realify_hermitian_interleaved(matrix)
    sigma_gradient = sigma_hessian @ sigma_real
    operator_images = np.einsum("pab,b->pa", operators, sigma, optimize=True)
    phi_sigma_cross = np.empty(
        (chart.PHI_DIM, chart.SIGMA_REAL_DIM), dtype=float
    )
    phi_sigma_cross[:, 0::2] = SQRT2 * operator_images.real
    phi_sigma_cross[:, 1::2] = SQRT2 * operator_images.imag

    gradient = np.zeros(chart.TOTAL_DIM, dtype=complex)
    hessian = np.zeros((chart.TOTAL_DIM, chart.TOTAL_DIM), dtype=complex)
    gradient[chart.PHI_SLICE] = phi_gradient
    gradient[chart.SIGMA_SLICE] = sigma_gradient
    hessian[chart.SIGMA_SLICE, chart.SIGMA_SLICE] = sigma_hessian
    hessian[chart.PHI_SLICE, chart.SIGMA_SLICE] = phi_sigma_cross
    hessian[chart.SIGMA_SLICE, chart.PHI_SLICE] = phi_sigma_cross.T
    return value, gradient, hessian


def base_derivative(
    q: np.ndarray, base_family: str
) -> tuple[complex, np.ndarray, np.ndarray]:
    if base_family == "Phi_cubic":
        return _phi_cubic_derivative(q)
    if base_family == "Phi_Sigma_Sigmadag_cubic":
        return _phi_sigma_cubic_derivative(q)
    raise KeyError(f"base family {base_family} is not covered here")


def selected_directions(
    state: potential.FieldState,
) -> tuple[potential.Direction, ...]:
    return tuple(
        row
        for row in potential.evaluate_directions(state)
        if row.base_family in SELECTED_FAMILIES
    )


def direction_derivative(
    q: np.ndarray, direction: potential.Direction
) -> quadratic.DirectionDerivative:
    if direction.base_family not in SELECTED_FAMILIES:
        raise KeyError(f"direction {direction.direction_id} is not covered")
    counts = dict(zip(potential.FIELD_ORDER, direction.counts, strict=True))
    base_value, base_gradient, base_hessian = base_derivative(
        q, direction.base_family
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


def all_direction_derivatives(
    state: potential.FieldState,
) -> tuple[quadratic.DirectionDerivative, ...]:
    q = chart.pack(state)
    return tuple(
        direction_derivative(q, row) for row in selected_directions(state)
    )


def expected_family_counts() -> dict[str, int]:
    g1 = ledger.build_report()
    return {
        family: sum(
            int(orbit["multiplicity"])
            for orbit in g1["operator_orbits"]
            if orbit["base_family"] == family
        )
        for family in SELECTED_FAMILIES
    }


def coefficient_audit() -> dict[str, Any]:
    phi_basis = phi_two_form_basis()
    operators = phi_sigma_operators()
    hermiticity = float(
        np.max(np.abs(operators - np.swapaxes(operators.conj(), 1, 2)))
    )
    phi_matrix_symmetry = float(
        np.max(np.abs(phi_basis - np.swapaxes(phi_basis, 1, 2)))
    )
    return {
        "Phi_two_form_basis_shape": list(phi_basis.shape),
        "Phi_two_form_basis_symmetry_residual": phi_matrix_symmetry,
        "PhiSigma_operator_shape": list(operators.shape),
        "PhiSigma_operator_Hermiticity_residual": hermiticity,
        "PhiSigma_nonzero_entries": int(
            np.count_nonzero(np.abs(operators) > 1.0e-14)
        ),
        "PhiSigma_frobenius_norm": float(np.linalg.norm(operators)),
    }


def base_support_audit(q: np.ndarray) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for family in SELECTED_FAMILIES:
        _, gradient, hessian = base_derivative(q, family)
        if family == "Phi_cubic":
            active = np.zeros(chart.TOTAL_DIM, dtype=bool)
            active[chart.PHI_SLICE] = True
            forbidden = 0.0
        else:
            active = np.zeros(chart.TOTAL_DIM, dtype=bool)
            active[chart.PHI_SLICE] = True
            active[chart.SIGMA_SLICE] = True
            forbidden = float(
                np.max(np.abs(hessian[chart.PHI_SLICE, chart.PHI_SLICE]))
            )
        inactive = ~active
        output[family] = {
            "inactive_gradient_residual": float(
                np.max(np.abs(gradient[inactive]), initial=0.0)
            ),
            "inactive_Hessian_residual": float(
                max(
                    np.max(np.abs(hessian[inactive, :]), initial=0.0),
                    np.max(np.abs(hessian[:, inactive]), initial=0.0),
                )
            ),
            "forbidden_block_residual": forbidden,
        }
    return output


@lru_cache(maxsize=1)
def build_report() -> dict[str, Any]:
    state = potential.deterministic_state(2704)
    q = chart.pack(state)
    directions = selected_directions(state)
    analytic = all_direction_derivatives(state)
    parameters = quadratic.parameter_derivatives(analytic)
    coefficients = quadratic.deterministic_coefficients(parameters)
    directional = quadratic.five_point_directional_audit(
        state, parameters, coefficients
    )
    evaluated = {row.direction_id: row for row in directions}
    value_residuals = {
        row.direction_id: float(abs(row.value - evaluated[row.direction_id].value))
        for row in analytic
    }
    expected_counts = expected_family_counts()
    actual_counts = {
        family: sum(row.base_family == family for row in analytic)
        for family in SELECTED_FAMILIES
    }
    coefficient = coefficient_audit()
    support = base_support_audit(q)
    support_residual = max(
        max(
            row["inactive_gradient_residual"],
            row["inactive_Hessian_residual"],
            row["forbidden_block_residual"],
        )
        for row in support.values()
    )
    hessian_asymmetry = max(
        float(np.max(np.abs(row.hessian - row.hessian.T))) for row in analytic
    )
    self_imaginary = max(
        [
            max(
                abs(row.value.imag),
                float(np.max(np.abs(row.gradient.imag))),
                float(np.max(np.abs(row.hessian.imag))),
            )
            for row in analytic
            if row.self_conjugate
        ]
        or [0.0]
    )
    full_parameter_ids = {
        row.parameter_id
        for row in potential.parameter_schema(
            potential.evaluate_directions(state)
        )
    }
    parameter_ids = {row.parameter_id for row in parameters}

    checks = {
        "Phi_two_form_basis_shape_is_210x45x45": coefficient[
            "Phi_two_form_basis_shape"
        ] == [210, 45, 45],
        "Phi_two_form_basis_is_symmetric": coefficient[
            "Phi_two_form_basis_symmetry_residual"
        ] < 1.0e-15,
        "PhiSigma_operator_shape_is_210x126x126": coefficient[
            "PhiSigma_operator_shape"
        ] == [210, 126, 126],
        "PhiSigma_operators_are_Hermitian": coefficient[
            "PhiSigma_operator_Hermiticity_residual"
        ] < 1.0e-12,
        "PhiSigma_operator_is_nonzero": coefficient[
            "PhiSigma_nonzero_entries"
        ] > 0,
        "authoritative_family_ids_exist": set(SELECTED_FAMILIES).issubset(
            {row["id"] for row in ledger.BASE_FAMILIES.values()}
        ),
        "both_families_have_nonzero_expected_counts": all(
            count > 0 for count in expected_counts.values()
        ),
        "both_families_have_nonzero_observed_counts": all(
            count > 0 for count in actual_counts.values()
        ),
        "all_expected_directions_differentiated": actual_counts == expected_counts,
        "all_values_match_authoritative_evaluator": max(value_residuals.values())
        < 1.0e-9,
        "all_parameter_ids_belong_to_live_schema": (
            parameter_ids.issubset(full_parameter_ids)
            and len(parameter_ids) == len(parameters)
            and len(parameters) > 0
        ),
        "base_derivative_support_is_exact": support_residual < 1.0e-11,
        "all_dense_Hessians_symmetric": hessian_asymmetry < 1.0e-11,
        "self_conjugate_derivatives_are_real": self_imaginary < 1.0e-9,
        "five_point_value_reconstruction": directional["value_residual"] < 1.0e-8,
        "five_point_first_derivative_reconstruction": directional[
            "first_residual"
        ] < 2.0e-7,
        "five_point_second_derivative_reconstruction": directional[
            "second_residual"
        ] < 2.0e-6,
        "remaining_9_quartic_families_not_claimed": True,
        "G2_not_closed": True,
        "whole_model_not_validated": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return _jsonable(
        {
            "status": (
                "G2_EXACT_DERIVATIVES_ALL_CUBIC_BASE_FAMILIES_CLOSED"
                if not failures
                else "G2_REMAINING_CUBIC_DERIVATIVES_FAILED"
            ),
            "overall_state": "PARTIAL" if not failures else "EXECUTION_FAIL",
            "n_checks": len(checks),
            "n_failed": len(failures),
            "failures": failures,
            "checks": checks,
            "coverage": {
                "base_families_closed": list(SELECTED_FAMILIES),
                "base_family_count_closed_here": 2,
                "cumulative_base_family_count_with_parents": 9,
                "base_family_count_total": len(ledger.BASE_FAMILIES),
                "expected_direction_counts": expected_counts,
                "observed_direction_counts": actual_counts,
                "direction_count_closed_here": len(analytic),
                "parameter_count_closed_here": len(parameters),
                "remaining_base_families": 9,
                "real_field_dimension": chart.TOTAL_DIM,
                "Hessian_shape": [chart.TOTAL_DIM, chart.TOTAL_DIM],
            },
            "coefficient_audit": coefficient,
            "base_support_audit": support,
            "maximum_base_support_residual": support_residual,
            "maximum_direction_value_residual": max(value_residuals.values()),
            "maximum_Hessian_asymmetry": hessian_asymmetry,
            "maximum_self_conjugate_imaginary_residual": self_imaginary,
            "directional_reconstruction": directional,
            "flags": {
                "remaining_two_cubic_base_adapters_closed": not failures,
                "all_cubic_base_adapters_closed_cumulatively": not failures,
                "cumulative_nine_of_eighteen_base_adapters_closed": not failures,
                "all_64_direction_gradients_complete": False,
                "all_64_direction_Hessians_complete": False,
                "G2_closed": False,
                "whole_model_validated": False,
                "empirical_discovery": False,
            },
            "next_exact_target": (
                "Differentiate the nine quartic base families, beginning with "
                "H10 self quartics and Phi2 HdagH channels."
            ),
            "verdict": (
                "The pure 210 cubic and mixed 210-126bar Hermitian cubic now have "
                "exact dense derivatives for every live dressing. All cubic base "
                "families are covered across the stacked derivative chain; nine "
                "quartic families remain and G2 is still PARTIAL."
            ),
        }
    )


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Exact derivatives for remaining cubic G2 families\n\n"
        f"**Status:** `{report['status']}`\n\n"
        + report["verdict"]
        + "\n\n"
        + f"**Next:** {report['next_exact_target']}\n",
        encoding="utf-8",
    )


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
