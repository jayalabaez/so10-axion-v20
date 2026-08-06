#!/usr/bin/env python3
"""Exact 486-real derivatives of the two H10 self-quartic directions.

The closed G1 basis B13 contains

  I1  = (Hdag H)^2,
  I54 = |H.H|^2.

In canonical real coordinates H_i=(x_i+i y_i)/sqrt(2), let

  n = (1/2) q_H.q_H,
  y = (1/2) sum_i (x_i+i y_i)^2.

Then

  I1=n^2,
  grad I1=2 n q_H,
  Hess I1=2 q_H q_H^T + 2 n identity,

and

  grad I54 = 2 Re(y* grad y),
  Hess I54 = 2 Re(y* Hess y + grad y* outer grad y).

The exact dense derivatives are embedded in the canonical 486-real chart and
validated against the authoritative G1 value evaluator plus polynomial-exact
five-point directional reconstruction.

This closes B13 only. Together with B00-B04, six of eighteen base-family
derivative adapters are closed. G2 remains PARTIAL.
"""
from __future__ import annotations

import argparse
import dataclasses
import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

import numpy as np

import live_g2_arbitrary_component_potential_values_v20 as potential
import live_g2_canonical_486_field_chart_v20 as chart

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "LIVE_G2_EXACT_H10_SELF_QUARTIC_DERIVATIVES_V20.json"
OUT_MD = ROOT / "LIVE_G2_EXACT_H10_SELF_QUARTIC_DERIVATIVES_V20.md"
BASE_FAMILY = "B13_h_self_quartic"


@dataclasses.dataclass(frozen=True)
class Derivative:
    direction_id: str
    basis_index: int
    basis_label: str
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


def selected_directions(state: potential.FieldState) -> tuple[potential.Direction, ...]:
    return tuple(
        row for row in potential.evaluate_directions(state)
        if row.base_family == BASE_FAMILY
    )


def _h_squared_data(q_h: np.ndarray) -> tuple[complex, np.ndarray, np.ndarray]:
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
        hessian[2 * index : 2 * index + 2, 2 * index : 2 * index + 2] = pair_hessian
    return value, gradient, hessian


def base_derivatives(q: np.ndarray) -> tuple[Derivative, Derivative]:
    coordinates = np.asarray(q, dtype=float).reshape(chart.TOTAL_DIM)
    q_h = coordinates[chart.H_SLICE]
    n_value = 0.5 * float(np.dot(q_h, q_h))

    i1_gradient_h = 2.0 * n_value * q_h
    i1_hessian_h = 2.0 * np.outer(q_h, q_h) + 2.0 * n_value * np.eye(chart.H_REAL_DIM)

    y_value, y_gradient, y_hessian = _h_squared_data(q_h)
    i54_value = float(abs(y_value) ** 2)
    i54_gradient_h = 2.0 * np.real(np.conjugate(y_value) * y_gradient)
    i54_hessian_h = 2.0 * np.real(
        np.conjugate(y_value) * y_hessian
        + np.outer(np.conjugate(y_gradient), y_gradient)
    )

    def embed(value: float, gradient_h: np.ndarray, hessian_h: np.ndarray, index: int, label: str) -> Derivative:
        gradient = np.zeros(chart.TOTAL_DIM, dtype=float)
        hessian = np.zeros((chart.TOTAL_DIM, chart.TOTAL_DIM), dtype=float)
        gradient[chart.H_SLICE] = gradient_h
        hessian[chart.H_SLICE, chart.H_SLICE] = hessian_h
        return Derivative(
            direction_id="",
            basis_index=index,
            basis_label=label,
            value=float(value),
            gradient=gradient,
            hessian=0.5 * (hessian + hessian.T),
        )

    return (
        embed(n_value**2, i1_gradient_h, i1_hessian_h, 0, "I_1"),
        embed(i54_value, i54_gradient_h, i54_hessian_h, 1, "I_54"),
    )


def direction_derivatives(state: potential.FieldState) -> tuple[Derivative, ...]:
    directions = sorted(selected_directions(state), key=lambda row: row.basis_index)
    if len(directions) != 2 or [row.basis_index for row in directions] != [0, 1]:
        raise AssertionError("G1 B13 basis must contain exactly indices 0 and 1")
    base = base_derivatives(chart.pack(state))
    return tuple(
        dataclasses.replace(
            derivative,
            direction_id=direction.direction_id,
            basis_label=direction.basis_label,
        )
        for derivative, direction in zip(base, directions)
    )


def assemble(
    derivatives: tuple[Derivative, ...], coefficients: Mapping[str, float]
) -> dict[str, Any]:
    known = {f"lambda::{row.direction_id}" for row in derivatives}
    unknown = set(coefficients).difference(known)
    if unknown:
        raise KeyError(f"unknown H10 self-quartic coefficients: {sorted(unknown)}")
    value = 0.0
    gradient = np.zeros(chart.TOTAL_DIM, dtype=float)
    hessian = np.zeros((chart.TOTAL_DIM, chart.TOTAL_DIM), dtype=float)
    for row in derivatives:
        coefficient = float(coefficients.get(f"lambda::{row.direction_id}", 0.0))
        value += coefficient * row.value
        gradient += coefficient * row.gradient
        hessian += coefficient * row.hessian
    return {
        "value": float(value),
        "gradient": gradient,
        "hessian": 0.5 * (hessian + hessian.T),
    }


def authoritative_value(
    q: np.ndarray, coefficients: Mapping[str, float], direction_ids: set[str]
) -> float:
    state = chart.unpack(q)
    rows = tuple(
        row for row in potential.evaluate_directions(state)
        if row.direction_id in direction_ids
    )
    return potential.potential_value(rows, coefficients)


def directional_audit(state: potential.FieldState, derivatives: tuple[Derivative, ...]) -> dict[str, Any]:
    coefficients = {
        f"lambda::{derivatives[0].direction_id}": 0.73,
        f"lambda::{derivatives[1].direction_id}": -0.41,
    }
    assembled = assemble(derivatives, coefficients)
    q = chart.pack(state)
    rng = np.random.default_rng(1313)
    direction = rng.normal(size=chart.TOTAL_DIM)
    direction /= np.linalg.norm(direction)
    step = 0.05
    ids = {row.direction_id for row in derivatives}

    def evaluate(offset: float) -> float:
        return authoritative_value(q + offset * direction, coefficients, ids)

    fm2, fm1, f0, fp1, fp2 = (
        evaluate(-2 * step), evaluate(-step), evaluate(0.0), evaluate(step), evaluate(2 * step)
    )
    first = (fm2 - 8 * fm1 + 8 * fp1 - fp2) / (12 * step)
    second = (-fp2 + 16 * fp1 - 30 * f0 + 16 * fm1 - fm2) / (12 * step**2)
    analytic_first = float(assembled["gradient"] @ direction)
    analytic_second = float(direction @ assembled["hessian"] @ direction)
    return {
        "value_residual": abs(f0 - assembled["value"]),
        "first_residual": abs(first - analytic_first),
        "second_residual": abs(second - analytic_second),
        "analytic_first": analytic_first,
        "numerical_first": first,
        "analytic_second": analytic_second,
        "numerical_second": second,
    }


@lru_cache(maxsize=1)
def build_report() -> dict[str, Any]:
    value_layer = potential.build_report()
    chart_report = chart.build_report()
    state = potential.deterministic_state(1313)
    authoritative = sorted(selected_directions(state), key=lambda row: row.basis_index)
    derivatives = direction_derivatives(state)
    value_residuals = [
        abs(row.value - source.value)
        for row, source in zip(derivatives, authoritative)
    ]
    directional = directional_audit(state, derivatives)
    hessian_symmetry = max(
        float(np.max(np.abs(row.hessian - row.hessian.T))) for row in derivatives
    )
    support_residual = max(
        float(np.max(np.abs(row.gradient[: chart.H_SLICE.start]), initial=0.0))
        for row in derivatives
    )
    checks = {
        "corrected_value_layer_executes": value_layer["n_failed"] == 0,
        "canonical_chart_executes": chart_report["n_failed"] == 0,
        "G1_B13_has_exactly_two_directions": len(authoritative) == 2,
        "basis_indices_are_zero_and_one": [row.basis_index for row in authoritative] == [0, 1],
        "analytic_values_match_authoritative": max(value_residuals) < 1.0e-10,
        "both_Hessians_symmetric": hessian_symmetry < 1.0e-12,
        "derivatives_supported_only_on_H_block": support_residual < 1.0e-15,
        "five_point_value_reconstruction": directional["value_residual"] < 1.0e-9,
        "five_point_first_reconstruction": directional["first_residual"] < 1.0e-8,
        "five_point_second_reconstruction": directional["second_residual"] < 1.0e-7,
        "six_of_eighteen_not_full_G2": True,
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
                "direction_count": len(derivatives),
                "base_families_closed_total": 6,
                "base_families_total": 18,
                "real_field_dimension": chart.TOTAL_DIM,
                "Hessian_shape": [chart.TOTAL_DIM, chart.TOTAL_DIM],
            },
            "direction_rows": [
                {
                    "direction_id": row.direction_id,
                    "basis_index": row.basis_index,
                    "basis_label": row.basis_label,
                    "value": row.value,
                    "gradient_norm": float(np.linalg.norm(row.gradient)),
                    "Hessian_frobenius": float(np.linalg.norm(row.hessian)),
                    "Hessian_rank": int(np.linalg.matrix_rank(row.hessian, 1.0e-10)),
                }
                for row in derivatives
            ],
            "maximum_value_residual": max(value_residuals),
            "maximum_Hessian_symmetry_residual": hessian_symmetry,
            "directional_reconstruction": directional,
            "flags": {
                "I1_gradient_Hessian_exact": not failures,
                "I54_gradient_Hessian_exact": not failures,
                "B13_derivative_adapter_closed": not failures,
                "six_of_eighteen_base_derivative_adapters_closed": not failures,
                "all_64_direction_gradients_complete": False,
                "all_64_direction_Hessians_complete": False,
                "G2_closed": False,
                "whole_model_validated": False,
                "empirical_discovery": False,
            },
            "next_exact_target": (
                "Close cubic derivative adapters B05-B08 using their exact "
                "multilinear tensor maps on the canonical chart."
            ),
            "verdict": (
                "Both normalized H10 self-quartic directions now have exact "
                "486-gradients and Hessians. Combined derivative coverage is "
                "six of eighteen base families; G2 remains partial."
            ),
        }
    )


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# G2 exact H10 self-quartic derivatives\n\n"
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
