#!/usr/bin/env python3
"""Exact 486-real derivatives of the unique 210_H cubic invariant.

The G1 basis B08 contains the unique real-four-form cubic

    I3(Phi) = Tr(A_Phi^3),

where A_Phi is the symmetric operator on the 45-dimensional two-form space,

    (A_Phi)_(ab),(cd) = Phi_abcd.

With A_i the operator associated with the i-th independent four-form
coordinate,

    grad_i I3 = 3 Tr(A^2 A_i),
    Hess_ij I3 = 3 Tr[A(A_i A_j + A_j A_i)].

This module constructs the complete dense 486-gradient and 486x486 Hessian,
checks the operator normalization against the authoritative G1 evaluator, and
validates first and second directional derivatives with polynomial-exact
five-point formulas.

This closes B08 only. Together with B00-B04 and B13, seven of eighteen base
family derivative adapters are closed. G2 remains PARTIAL.
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
import exact_210_self_invariant_basis_v20 as authoritative
import live_g2_arbitrary_component_potential_values_v20 as potential
import live_g2_canonical_486_field_chart_v20 as chart

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "LIVE_G2_EXACT_PHI_CUBIC_DERIVATIVES_V20.json"
OUT_MD = ROOT / "LIVE_G2_EXACT_PHI_CUBIC_DERIVATIVES_V20.md"
BASE_FAMILY = "B08_phi_cubic"
PAIR_BASIS = tuple(itertools.combinations(range(10), 2))
FOUR_BASIS = tuple(itertools.combinations(range(10), 4))


@dataclasses.dataclass(frozen=True)
class Derivative:
    direction_id: str
    value: float
    gradient: np.ndarray
    hessian: np.ndarray


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
    return value


def two_form_operator(phi: direct.Form) -> np.ndarray:
    matrix = np.zeros((len(PAIR_BASIS), len(PAIR_BASIS)), dtype=float)
    for row, left in enumerate(PAIR_BASIS):
        for column, right in enumerate(PAIR_BASIS):
            if set(left).intersection(right):
                continue
            sequence = left + right
            indices = tuple(sorted(sequence))
            coefficient = phi.get(indices, 0.0)
            value = coefficient * direct.permutation_sign(sequence)
            if abs(complex(value).imag) > 1.0e-12:
                raise ValueError("real 210 four-form produced complex operator")
            matrix[row, column] = float(complex(value).real)
    return matrix


@lru_cache(maxsize=1)
def basis_operators() -> np.ndarray:
    operators = np.empty((chart.PHI_DIM, len(PAIR_BASIS), len(PAIR_BASIS)), dtype=float)
    for index, four_indices in enumerate(FOUR_BASIS):
        operators[index] = two_form_operator({four_indices: 1.0 + 0.0j})
    return operators


def selected_direction(state: potential.FieldState) -> potential.Direction:
    rows = [
        row
        for row in potential.evaluate_directions(state)
        if row.base_family == BASE_FAMILY
    ]
    if len(rows) != 1:
        raise AssertionError(f"expected one B08 direction, found {len(rows)}")
    return rows[0]


def analytic_derivative(state: potential.FieldState) -> Derivative:
    q = chart.pack(state)
    phi_coordinates = q[chart.PHI_SLICE]
    operators = basis_operators()
    matrix = np.tensordot(phi_coordinates, operators, axes=(0, 0))
    matrix_squared = matrix @ matrix
    value = float(np.trace(matrix_squared @ matrix))

    gradient_phi = 3.0 * np.einsum(
        "ab,iab->i", matrix_squared, operators, optimize=True
    )
    ordered = np.einsum(
        "ab,ibc,jca->ij", matrix, operators, operators, optimize=True
    )
    hessian_phi = 3.0 * (ordered + ordered.T)

    gradient = np.zeros(chart.TOTAL_DIM, dtype=float)
    hessian = np.zeros((chart.TOTAL_DIM, chart.TOTAL_DIM), dtype=float)
    gradient[chart.PHI_SLICE] = gradient_phi
    hessian[chart.PHI_SLICE, chart.PHI_SLICE] = hessian_phi
    direction = selected_direction(state)
    return Derivative(
        direction_id=direction.direction_id,
        value=value,
        gradient=gradient,
        hessian=0.5 * (hessian + hessian.T),
    )


def authoritative_value(q: np.ndarray, direction_id: str) -> float:
    state = chart.unpack(q)
    direction = selected_direction(state)
    if direction.direction_id != direction_id:
        raise AssertionError("B08 direction ID changed across field states")
    return float(direction.value.real)


def directional_audit(state: potential.FieldState, derivative: Derivative) -> dict[str, Any]:
    q = chart.pack(state)
    rng = np.random.default_rng(808)
    direction = np.zeros(chart.TOTAL_DIM, dtype=float)
    direction[chart.PHI_SLICE] = rng.normal(size=chart.PHI_DIM)
    direction /= np.linalg.norm(direction)
    step = 0.05

    def evaluate(offset: float) -> float:
        return authoritative_value(q + offset * direction, derivative.direction_id)

    fm2, fm1, f0, fp1, fp2 = (
        evaluate(-2 * step), evaluate(-step), evaluate(0.0), evaluate(step), evaluate(2 * step)
    )
    first = (fm2 - 8 * fm1 + 8 * fp1 - fp2) / (12 * step)
    second = (-fp2 + 16 * fp1 - 30 * f0 + 16 * fm1 - fm2) / (12 * step**2)
    analytic_first = float(derivative.gradient @ direction)
    analytic_second = float(direction @ derivative.hessian @ direction)
    return {
        "value_residual": abs(f0 - derivative.value),
        "first_residual": abs(first - analytic_first),
        "second_residual": abs(second - analytic_second),
        "analytic_first": analytic_first,
        "numerical_first": first,
        "analytic_second": analytic_second,
        "numerical_second": second,
    }


def singlet_formula_audit() -> dict[str, Any]:
    basis = direct.singlet_basis()
    p, a, omega = 0.31, -0.47, 0.28
    phi = direct.add_forms(
        direct.scale_form(basis["p"], p),
        direct.scale_form(basis["a"], a),
        direct.scale_form(basis["omega"], omega),
    )
    operator_value = float(np.trace(np.linalg.matrix_power(two_form_operator(phi), 3)))
    source_value = float(authoritative.cubic_invariant(phi))
    closed_formula = (
        2.0 / np.sqrt(3.0) * a**3
        + 2.0 * np.sqrt(3.0) * a * omega**2
        + 3.0 * p * omega**2
    )
    return {
        "p": p,
        "a": a,
        "omega": omega,
        "operator_value": operator_value,
        "authoritative_value": source_value,
        "closed_formula": float(closed_formula),
        "operator_authoritative_residual": abs(operator_value - source_value),
        "operator_formula_residual": abs(operator_value - closed_formula),
    }


@lru_cache(maxsize=1)
def build_report() -> dict[str, Any]:
    value_layer = potential.build_report()
    chart_report = chart.build_report()
    state = potential.deterministic_state(808)
    derivative = analytic_derivative(state)
    source = selected_direction(state)
    directional = directional_audit(state, derivative)
    singlet = singlet_formula_audit()
    operators = basis_operators()

    outside = np.ones(chart.TOTAL_DIM, dtype=bool)
    outside[chart.PHI_SLICE] = False
    support_residual = max(
        float(np.max(np.abs(derivative.gradient[outside]), initial=0.0)),
        float(np.max(np.abs(derivative.hessian[np.ix_(outside, outside)]), initial=0.0)),
        float(np.max(np.abs(derivative.hessian[np.ix_(outside, ~outside)]), initial=0.0)),
    )
    checks = {
        "corrected_value_layer_executes": value_layer["n_failed"] == 0,
        "canonical_chart_executes": chart_report["n_failed"] == 0,
        "two_form_basis_has_dimension_45": len(PAIR_BASIS) == 45,
        "four_form_basis_has_dimension_210": len(FOUR_BASIS) == 210,
        "basis_operator_shape_exact": operators.shape == (210, 45, 45),
        "basis_operators_symmetric": np.max(
            np.abs(operators - np.swapaxes(operators, 1, 2))
        ) < 1.0e-12,
        "operator_value_matches_authoritative_G1": abs(
            derivative.value - source.value.real
        ) < 1.0e-10,
        "operator_matches_closed_singlet_formula": singlet[
            "operator_formula_residual"
        ] < 1.0e-12,
        "operator_matches_authoritative_singlet_value": singlet[
            "operator_authoritative_residual"
        ] < 1.0e-12,
        "Hessian_symmetric": np.max(
            np.abs(derivative.hessian - derivative.hessian.T)
        ) < 1.0e-12,
        "derivatives_supported_only_on_Phi_block": support_residual < 1.0e-15,
        "five_point_value_reconstruction": directional["value_residual"] < 1.0e-9,
        "five_point_first_reconstruction": directional["first_residual"] < 1.0e-8,
        "five_point_second_reconstruction": directional["second_residual"] < 1.0e-7,
        "seven_of_eighteen_not_full_G2": True,
        "whole_model_not_validated": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return _jsonable(
        {
            "status": (
                "G2_EXACT_PHI_CUBIC_DERIVATIVES_CLOSED"
                if not failures
                else "G2_PHI_CUBIC_DERIVATIVES_FAILED"
            ),
            "overall_state": "PARTIAL" if not failures else "EXECUTION_FAIL",
            "n_checks": len(checks),
            "n_failed": len(failures),
            "failures": failures,
            "checks": checks,
            "coverage": {
                "base_family": BASE_FAMILY,
                "direction_count": 1,
                "base_families_closed_total": 7,
                "base_families_total": 18,
                "real_field_dimension": chart.TOTAL_DIM,
                "Hessian_shape": [chart.TOTAL_DIM, chart.TOTAL_DIM],
            },
            "direction": {
                "direction_id": derivative.direction_id,
                "value": derivative.value,
                "gradient_norm": float(np.linalg.norm(derivative.gradient)),
                "Hessian_frobenius": float(np.linalg.norm(derivative.hessian)),
                "Hessian_rank": int(np.linalg.matrix_rank(derivative.hessian, 1.0e-10)),
            },
            "singlet_formula_audit": singlet,
            "directional_reconstruction": directional,
            "flags": {
                "B08_operator_normalization_exact": not failures,
                "B08_gradient_exact": not failures,
                "B08_Hessian_exact": not failures,
                "B08_derivative_adapter_closed": not failures,
                "seven_of_eighteen_base_derivative_adapters_closed": not failures,
                "all_64_direction_gradients_complete": False,
                "all_64_direction_Hessians_complete": False,
                "G2_closed": False,
                "whole_model_validated": False,
                "empirical_discovery": False,
            },
            "next_exact_target": (
                "Close mixed cubic derivative adapters B05-B07 using the "
                "exact Phi-Sigma and Phi-H-Sigma multilinear maps."
            ),
            "verdict": (
                "The unique 210_H cubic now has an exact 486-gradient and "
                "Hessian with independently verified operator normalization. "
                "Combined derivative coverage is seven of eighteen base families."
            ),
        }
    )


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# G2 exact 210 cubic derivatives\n\n"
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
