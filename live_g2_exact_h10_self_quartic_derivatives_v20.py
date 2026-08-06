#!/usr/bin/env python3
"""Exact 486-real derivatives for the authoritative H10 self quartics.

The live G1 family ``H_self_quartics`` contains

    I_1  = (Hdag H)^2,
    I_54 = |H.H|^2.

With canonical real coordinates H_i=(x_i+i y_i)/sqrt(2), both values,
gradients, and Hessians are elementary quartic polynomials.  This module maps
them to every authoritative live direction in the family, applies any exact
singlet dressing through the shared product rule, and emits live real-parameter
derivative tensors.

This closes one quartic base-family adapter only.  Across the stacked chain ten
of eighteen adapters are targeted; eight quartic families and G2 remain open.
"""
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

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "LIVE_G2_EXACT_H10_SELF_QUARTIC_DERIVATIVES_V20.json"
OUT_MD = ROOT / "LIVE_G2_EXACT_H10_SELF_QUARTIC_DERIVATIVES_V20.md"
BASE_FAMILY = "H_self_quartics"
BASIS_LABELS = ("I_1", "I_54")


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


def h_squared_jet(q_h: np.ndarray) -> tuple[complex, np.ndarray, np.ndarray]:
    block = np.asarray(q_h, dtype=float).reshape(chart.H_REAL_DIM)
    value = 0.0 + 0.0j
    gradient = np.zeros(chart.H_REAL_DIM, dtype=complex)
    hessian = np.zeros((chart.H_REAL_DIM, chart.H_REAL_DIM), dtype=complex)
    pair_hessian = np.asarray([[1.0, 1j], [1j, -1.0]], dtype=complex)
    for index in range(chart.H_COMPLEX_DIM):
        x_value = block[2 * index]
        y_value = block[2 * index + 1]
        coordinate = x_value + 1j * y_value
        value += 0.5 * coordinate**2
        gradient[2 * index] = coordinate
        gradient[2 * index + 1] = 1j * coordinate
        hessian[2 * index : 2 * index + 2, 2 * index : 2 * index + 2] = (
            pair_hessian
        )
    return value, gradient, hessian


def base_derivative(
    q: np.ndarray, basis_index: int
) -> tuple[complex, np.ndarray, np.ndarray]:
    coordinates = np.asarray(q, dtype=float).reshape(chart.TOTAL_DIM)
    q_h = coordinates[chart.H_SLICE]
    gradient = np.zeros(chart.TOTAL_DIM, dtype=complex)
    hessian = np.zeros((chart.TOTAL_DIM, chart.TOTAL_DIM), dtype=complex)

    if int(basis_index) == 0:
        norm = 0.5 * float(np.dot(q_h, q_h))
        value = norm**2
        gradient_h = 2.0 * norm * q_h
        hessian_h = 2.0 * np.outer(q_h, q_h) + 2.0 * norm * np.eye(
            chart.H_REAL_DIM
        )
    elif int(basis_index) == 1:
        pair, pair_gradient, pair_hessian = h_squared_jet(q_h)
        value = float(abs(pair) ** 2)
        gradient_h = 2.0 * np.real(np.conjugate(pair) * pair_gradient)
        hessian_h = 2.0 * np.real(
            np.conjugate(pair) * pair_hessian
            + np.outer(np.conjugate(pair_gradient), pair_gradient)
        )
    else:
        raise KeyError(f"unknown H self-quartic basis index {basis_index}")

    gradient[chart.H_SLICE] = gradient_h
    hessian[chart.H_SLICE, chart.H_SLICE] = hessian_h
    return complex(value), gradient, 0.5 * (hessian + hessian.T)


def selected_directions(
    state: potential.FieldState,
) -> tuple[potential.Direction, ...]:
    return tuple(
        row
        for row in potential.evaluate_directions(state)
        if row.base_family == BASE_FAMILY
    )


def direction_derivative(
    q: np.ndarray, direction: potential.Direction
) -> quadratic.DirectionDerivative:
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


def all_direction_derivatives(
    state: potential.FieldState,
) -> tuple[quadratic.DirectionDerivative, ...]:
    q = chart.pack(state)
    return tuple(
        direction_derivative(q, row) for row in selected_directions(state)
    )


def expected_direction_count() -> int:
    g1 = ledger.build_report()
    return sum(
        int(orbit["multiplicity"])
        for orbit in g1["operator_orbits"]
        if orbit["base_family"] == BASE_FAMILY
    )


def base_support_audit(q: np.ndarray) -> dict[str, Any]:
    rows: dict[str, Any] = {}
    active = np.zeros(chart.TOTAL_DIM, dtype=bool)
    active[chart.H_SLICE] = True
    for index, label in enumerate(BASIS_LABELS):
        _, gradient, hessian = base_derivative(q, index)
        inactive = ~active
        rows[label] = {
            "inactive_gradient_residual": float(
                np.max(np.abs(gradient[inactive]), initial=0.0)
            ),
            "inactive_Hessian_residual": float(
                max(
                    np.max(np.abs(hessian[inactive, :]), initial=0.0),
                    np.max(np.abs(hessian[:, inactive]), initial=0.0),
                )
            ),
        }
    return rows


@lru_cache(maxsize=1)
def build_report() -> dict[str, Any]:
    state = potential.deterministic_state(2804)
    q = chart.pack(state)
    directions = selected_directions(state)
    analytic = all_direction_derivatives(state)
    parameters = quadratic.parameter_derivatives(analytic)
    coefficients = quadratic.deterministic_coefficients(parameters)
    directional = quadratic.five_point_directional_audit(
        state, parameters, coefficients
    )
    expected = {row.direction_id: row for row in directions}
    value_residuals = {
        row.direction_id: float(abs(row.value - expected[row.direction_id].value))
        for row in analytic
    }
    basis_indices = sorted({row.basis_index for row in directions})
    basis_labels = sorted({row.basis_label for row in directions})
    expected_count = expected_direction_count()
    support = base_support_audit(q)
    support_residual = max(
        max(row.values()) for row in support.values()
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
    live_parameter_ids = {
        row.parameter_id
        for row in potential.parameter_schema(
            potential.evaluate_directions(state)
        )
    }
    parameter_ids = {row.parameter_id for row in parameters}

    checks = {
        "authoritative_family_id_exists": BASE_FAMILY
        in {row["id"] for row in ledger.BASE_FAMILIES.values()},
        "expected_G1_direction_count_is_nonzero": expected_count > 0,
        "observed_direction_count_is_nonzero": len(analytic) > 0,
        "every_expected_direction_differentiated": len(analytic) == expected_count,
        "both_basis_indices_present": basis_indices == [0, 1],
        "both_basis_labels_present": basis_labels == sorted(BASIS_LABELS),
        "all_values_match_authoritative_evaluator": max(value_residuals.values())
        < 1.0e-10,
        "all_parameter_ids_belong_to_live_schema": (
            parameter_ids.issubset(live_parameter_ids)
            and len(parameter_ids) == len(parameters)
            and len(parameters) > 0
        ),
        "base_derivatives_supported_only_on_H": support_residual < 1.0e-12,
        "all_dense_Hessians_symmetric": hessian_asymmetry < 1.0e-12,
        "self_conjugate_derivatives_real": self_imaginary < 1.0e-10,
        "five_point_value_reconstruction": directional["value_residual"] < 1.0e-9,
        "five_point_first_derivative_reconstruction": directional[
            "first_residual"
        ] < 1.0e-8,
        "five_point_second_derivative_reconstruction": directional[
            "second_residual"
        ] < 1.0e-7,
        "remaining_8_quartic_families_not_claimed": True,
        "G2_not_closed": True,
        "whole_model_not_validated": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return _jsonable(
        {
            "status": (
                "G2_EXACT_H10_SELF_QUARTIC_DERIVATIVES_CLOSED"
                if not failures
                else "G2_H10_SELF_QUARTIC_DERIVATIVES_FAILED"
            ),
            "overall_state": "PARTIAL" if not failures else "EXECUTION_FAIL",
            "n_checks": len(checks),
            "n_failed": len(failures),
            "failures": failures,
            "checks": checks,
            "coverage": {
                "base_family": BASE_FAMILY,
                "base_family_count_closed_here": 1,
                "cumulative_base_family_count_with_parents": 10,
                "base_family_count_total": len(ledger.BASE_FAMILIES),
                "remaining_base_families": 8,
                "expected_direction_count": expected_count,
                "observed_direction_count": len(analytic),
                "parameter_count_closed_here": len(parameters),
                "basis_indices": basis_indices,
                "basis_labels": basis_labels,
                "real_field_dimension": chart.TOTAL_DIM,
                "Hessian_shape": [chart.TOTAL_DIM, chart.TOTAL_DIM],
            },
            "base_support_audit": support,
            "maximum_base_support_residual": support_residual,
            "maximum_direction_value_residual": max(value_residuals.values()),
            "maximum_Hessian_asymmetry": hessian_asymmetry,
            "maximum_self_conjugate_imaginary_residual": self_imaginary,
            "directional_reconstruction": directional,
            "flags": {
                "authoritative_H_self_quartic_adapter_closed": not failures,
                "I1_gradient_Hessian_exact": not failures,
                "I54_gradient_Hessian_exact": not failures,
                "cumulative_ten_of_eighteen_base_adapters_closed": not failures,
                "all_64_direction_gradients_complete": False,
                "all_64_direction_Hessians_complete": False,
                "G2_closed": False,
                "whole_model_validated": False,
                "empirical_discovery": False,
            },
            "next_exact_target": (
                "Differentiate Phi2_HdagH_channels and H_Sigma_hermitian, then "
                "continue through the remaining projector quartics."
            ),
            "verdict": (
                "Both normalized H10 self-quartic directions now have exact dense "
                "derivatives for every authoritative live copy. Eight base-family "
                "adapters remain, so G2 is still PARTIAL."
            ),
        }
    )


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Exact authoritative H10 self-quartic derivatives\n\n"
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
