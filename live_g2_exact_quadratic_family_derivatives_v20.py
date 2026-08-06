#!/usr/bin/env python3
"""Exact 486-real derivatives for five authoritative quadratic G2 families.

This module differentiates every live direction whose G1 base-family ID is

* ``singlet_polynomial``;
* ``126bar_norm``;
* ``Hdag_Hdag_pair``;
* ``Hdag_H_norm``;
* ``Phi_norm``.

Every allowed S/Sdag/Phi17/Phi17dag dressing is included.  Each selected
operator factors as F(q)=B(u)D(s,x), so its exact dense derivatives follow from

    grad F = D grad B + B grad D,
    Hess F = D Hess B + B Hess D
             + grad B outer grad D + grad D outer grad B.

Coverage is tied to the authoritative G1 orbit ledger.  Every selected family
must have a nonzero expected and observed direction count; zero-direction
vacuous success is forbidden.

This closes five of eighteen base-family derivative adapters only.  The other
thirteen families, complete all-64 derivatives, and G2 remain open.
"""
from __future__ import annotations

import argparse
import dataclasses
import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, Mapping

import numpy as np

import live_g1_tensor_closure_ledger_v20 as ledger
import live_g2_arbitrary_component_potential_values_v20 as potential
import live_g2_canonical_486_field_chart_v20 as chart

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "LIVE_G2_EXACT_QUADRATIC_FAMILY_DERIVATIVES_V20.json"
OUT_MD = ROOT / "LIVE_G2_EXACT_QUADRATIC_FAMILY_DERIVATIVES_V20.md"

SELECTED_FAMILIES = (
    "singlet_polynomial",
    "126bar_norm",
    "Hdag_Hdag_pair",
    "Hdag_H_norm",
    "Phi_norm",
)
SINGLET_GLOBAL_INDICES = np.asarray(
    [
        chart.S_SLICE.start,
        chart.S_SLICE.start + 1,
        chart.X_SLICE.start,
        chart.X_SLICE.start + 1,
    ],
    dtype=int,
)


@dataclasses.dataclass(frozen=True)
class SmallJet2:
    value: complex
    gradient: np.ndarray
    hessian: np.ndarray

    @staticmethod
    def constant(value: complex) -> "SmallJet2":
        return SmallJet2(
            complex(value),
            np.zeros(4, dtype=complex),
            np.zeros((4, 4), dtype=complex),
        )

    @staticmethod
    def linear(value: complex, gradient: np.ndarray) -> "SmallJet2":
        return SmallJet2(
            complex(value),
            np.asarray(gradient, dtype=complex).reshape(4),
            np.zeros((4, 4), dtype=complex),
        )

    def __mul__(self, other: "SmallJet2") -> "SmallJet2":
        return SmallJet2(
            self.value * other.value,
            self.gradient * other.value + self.value * other.gradient,
            self.hessian * other.value
            + self.value * other.hessian
            + np.outer(self.gradient, other.gradient)
            + np.outer(other.gradient, self.gradient),
        )

    def __pow__(self, exponent: int) -> "SmallJet2":
        power = int(exponent)
        if power < 0:
            raise ValueError("monomial exponents must be nonnegative")
        result = SmallJet2.constant(1.0)
        for _ in range(power):
            result = result * self
        return result


@dataclasses.dataclass(frozen=True)
class DirectionDerivative:
    direction_id: str
    base_family: str
    self_conjugate: bool
    value: complex
    gradient: np.ndarray
    hessian: np.ndarray


@dataclasses.dataclass(frozen=True)
class ParameterDerivative:
    parameter_id: str
    direction_id: str
    component: str
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
    if isinstance(value, complex):
        return {"re": float(value.real), "im": float(value.imag)}
    return value


def selected_directions(
    state: potential.FieldState,
) -> tuple[potential.Direction, ...]:
    return tuple(
        row
        for row in potential.evaluate_directions(state)
        if row.base_family in SELECTED_FAMILIES
    )


def _singlet_linear_jets(q: np.ndarray) -> dict[str, SmallJet2]:
    local = np.asarray(q, dtype=float).reshape(chart.TOTAL_DIM)[
        SINGLET_GLOBAL_INDICES
    ]
    inv = 1.0 / np.sqrt(2.0)
    return {
        "S": SmallJet2.linear(
            (local[0] + 1j * local[1]) * inv,
            np.asarray([inv, 1j * inv, 0.0, 0.0], dtype=complex),
        ),
        "Sb": SmallJet2.linear(
            (local[0] - 1j * local[1]) * inv,
            np.asarray([inv, -1j * inv, 0.0, 0.0], dtype=complex),
        ),
        "X": SmallJet2.linear(
            (local[2] + 1j * local[3]) * inv,
            np.asarray([0.0, 0.0, inv, 1j * inv], dtype=complex),
        ),
        "Xb": SmallJet2.linear(
            (local[2] - 1j * local[3]) * inv,
            np.asarray([0.0, 0.0, inv, -1j * inv], dtype=complex),
        ),
    }


def dressing_jet(q: np.ndarray, counts: Mapping[str, int]) -> SmallJet2:
    factors = _singlet_linear_jets(q)
    result = SmallJet2.constant(1.0)
    for name in ("S", "Sb", "X", "Xb"):
        result = result * (factors[name] ** int(counts.get(name, 0)))
    return result


def _empty_complex_derivatives() -> tuple[np.ndarray, np.ndarray]:
    return (
        np.zeros(chart.TOTAL_DIM, dtype=complex),
        np.zeros((chart.TOTAL_DIM, chart.TOTAL_DIM), dtype=complex),
    )


def base_derivative(
    q: np.ndarray, base_family: str
) -> tuple[complex, np.ndarray, np.ndarray]:
    coordinates = np.asarray(q, dtype=float).reshape(chart.TOTAL_DIM)
    gradient, hessian = _empty_complex_derivatives()

    if base_family == "singlet_polynomial":
        return 1.0 + 0.0j, gradient, hessian

    if base_family == "126bar_norm":
        block = coordinates[chart.SIGMA_SLICE]
        value = 0.5 * float(np.dot(block, block))
        gradient[chart.SIGMA_SLICE] = block
        hessian[chart.SIGMA_SLICE, chart.SIGMA_SLICE] = np.eye(
            chart.SIGMA_REAL_DIM
        )
        return complex(value), gradient, hessian

    if base_family == "Hdag_Hdag_pair":
        block = coordinates[chart.H_SLICE]
        value = 0.0 + 0.0j
        pair_hessian = np.asarray(
            [[1.0, -1j], [-1j, -1.0]], dtype=complex
        )
        for index in range(chart.H_COMPLEX_DIM):
            x_value = block[2 * index]
            y_value = block[2 * index + 1]
            conjugate_coordinate = x_value - 1j * y_value
            value += 0.5 * conjugate_coordinate**2
            start = chart.H_SLICE.start + 2 * index
            gradient[start] = conjugate_coordinate
            gradient[start + 1] = -1j * conjugate_coordinate
            hessian[start : start + 2, start : start + 2] = pair_hessian
        return value, gradient, hessian

    if base_family == "Hdag_H_norm":
        block = coordinates[chart.H_SLICE]
        value = 0.5 * float(np.dot(block, block))
        gradient[chart.H_SLICE] = block
        hessian[chart.H_SLICE, chart.H_SLICE] = np.eye(chart.H_REAL_DIM)
        return complex(value), gradient, hessian

    if base_family == "Phi_norm":
        block = coordinates[chart.PHI_SLICE]
        value = float(np.dot(block, block))
        gradient[chart.PHI_SLICE] = 2.0 * block
        hessian[chart.PHI_SLICE, chart.PHI_SLICE] = 2.0 * np.eye(chart.PHI_DIM)
        return complex(value), gradient, hessian

    raise KeyError(f"base family {base_family} is not in this derivative gate")


def _embed_singlet_jet(jet: SmallJet2) -> tuple[np.ndarray, np.ndarray]:
    gradient = np.zeros(chart.TOTAL_DIM, dtype=complex)
    hessian = np.zeros((chart.TOTAL_DIM, chart.TOTAL_DIM), dtype=complex)
    gradient[SINGLET_GLOBAL_INDICES] = jet.gradient
    hessian[np.ix_(SINGLET_GLOBAL_INDICES, SINGLET_GLOBAL_INDICES)] = jet.hessian
    return gradient, hessian


def direction_derivative(
    q: np.ndarray, direction: potential.Direction
) -> DirectionDerivative:
    if direction.base_family not in SELECTED_FAMILIES:
        raise KeyError(f"direction {direction.direction_id} is not covered")
    counts = dict(zip(potential.FIELD_ORDER, direction.counts, strict=True))
    base_value, base_gradient, base_hessian = base_derivative(
        q, direction.base_family
    )
    dressing = dressing_jet(q, counts)
    dressing_gradient, dressing_hessian = _embed_singlet_jet(dressing)
    value = base_value * dressing.value
    gradient = dressing.value * base_gradient + base_value * dressing_gradient
    hessian = (
        dressing.value * base_hessian
        + base_value * dressing_hessian
        + np.outer(base_gradient, dressing_gradient)
        + np.outer(dressing_gradient, base_gradient)
    )
    return DirectionDerivative(
        direction_id=direction.direction_id,
        base_family=direction.base_family,
        self_conjugate=direction.self_conjugate,
        value=complex(value),
        gradient=gradient,
        hessian=0.5 * (hessian + hessian.T),
    )


def all_direction_derivatives(
    state: potential.FieldState,
) -> tuple[DirectionDerivative, ...]:
    q = chart.pack(state)
    return tuple(
        direction_derivative(q, direction)
        for direction in selected_directions(state)
    )


def parameter_derivatives(
    derivatives: Iterable[DirectionDerivative],
) -> tuple[ParameterDerivative, ...]:
    output: list[ParameterDerivative] = []
    for row in derivatives:
        if row.self_conjugate:
            output.append(
                ParameterDerivative(
                    parameter_id=f"lambda::{row.direction_id}",
                    direction_id=row.direction_id,
                    component="real",
                    value=float(row.value.real),
                    gradient=np.asarray(row.gradient.real, dtype=float),
                    hessian=np.asarray(row.hessian.real, dtype=float),
                )
            )
        else:
            output.append(
                ParameterDerivative(
                    parameter_id=f"re::{row.direction_id}",
                    direction_id=row.direction_id,
                    component="re",
                    value=float(2.0 * row.value.real),
                    gradient=np.asarray(2.0 * row.gradient.real, dtype=float),
                    hessian=np.asarray(2.0 * row.hessian.real, dtype=float),
                )
            )
            output.append(
                ParameterDerivative(
                    parameter_id=f"im::{row.direction_id}",
                    direction_id=row.direction_id,
                    component="im",
                    value=float(-2.0 * row.value.imag),
                    gradient=np.asarray(-2.0 * row.gradient.imag, dtype=float),
                    hessian=np.asarray(-2.0 * row.hessian.imag, dtype=float),
                )
            )
    return tuple(output)


def assemble(
    derivatives: Iterable[ParameterDerivative], coefficients: Mapping[str, float]
) -> dict[str, Any]:
    rows = tuple(derivatives)
    known = {row.parameter_id for row in rows}
    unknown = set(coefficients).difference(known)
    if unknown:
        raise KeyError(f"unknown derivative coefficients: {sorted(unknown)}")
    value = 0.0
    gradient = np.zeros(chart.TOTAL_DIM, dtype=float)
    hessian = np.zeros((chart.TOTAL_DIM, chart.TOTAL_DIM), dtype=float)
    for row in rows:
        coefficient = float(coefficients.get(row.parameter_id, 0.0))
        value += coefficient * row.value
        gradient += coefficient * row.gradient
        hessian += coefficient * row.hessian
    return {
        "value": float(value),
        "gradient": gradient,
        "hessian": 0.5 * (hessian + hessian.T),
    }


def deterministic_coefficients(
    derivatives: Iterable[ParameterDerivative],
) -> dict[str, float]:
    return {
        row.parameter_id: (((index * 13 + 7) % 31) - 15) / 9.0
        for index, row in enumerate(derivatives)
    }


def selected_potential_value(
    q: np.ndarray,
    coefficient_map: Mapping[str, float],
    selected_ids: set[str],
) -> float:
    state = chart.unpack(q)
    rows = tuple(
        row
        for row in potential.evaluate_directions(state)
        if row.direction_id in selected_ids
    )
    return potential.potential_value(rows, coefficient_map)


def five_point_directional_audit(
    state: potential.FieldState,
    derivatives: tuple[ParameterDerivative, ...],
    coefficients: Mapping[str, float],
) -> dict[str, Any]:
    q = chart.pack(state)
    assembled = assemble(derivatives, coefficients)
    rng = np.random.default_rng(2504)
    direction = rng.normal(size=chart.TOTAL_DIM)
    direction /= np.linalg.norm(direction)
    step = 0.05
    selected_ids = {row.direction_id for row in derivatives}

    def evaluate(offset: float) -> float:
        return selected_potential_value(
            q + offset * direction, coefficients, selected_ids
        )

    f_m2 = evaluate(-2.0 * step)
    f_m1 = evaluate(-step)
    f_0 = evaluate(0.0)
    f_p1 = evaluate(step)
    f_p2 = evaluate(2.0 * step)
    numerical_first = (
        f_m2 - 8.0 * f_m1 + 8.0 * f_p1 - f_p2
    ) / (12.0 * step)
    numerical_second = (
        -f_p2 + 16.0 * f_p1 - 30.0 * f_0 + 16.0 * f_m1 - f_m2
    ) / (12.0 * step**2)
    analytic_first = float(np.dot(assembled["gradient"], direction))
    analytic_second = float(direction @ assembled["hessian"] @ direction)
    return {
        "step": step,
        "value_residual": abs(f_0 - assembled["value"]),
        "analytic_first": analytic_first,
        "numerical_first": numerical_first,
        "first_residual": abs(analytic_first - numerical_first),
        "analytic_second": analytic_second,
        "numerical_second": numerical_second,
        "second_residual": abs(analytic_second - numerical_second),
    }


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


@lru_cache(maxsize=1)
def build_report() -> dict[str, Any]:
    value_layer = potential.build_report()
    chart_report = chart.build_report()
    state = potential.deterministic_state(2504)
    directions = selected_directions(state)
    analytic = all_direction_derivatives(state)
    parameters = parameter_derivatives(analytic)
    coefficients = deterministic_coefficients(parameters)
    combined = assemble(parameters, coefficients)
    directional = five_point_directional_audit(
        state, parameters, coefficients
    )

    evaluated = {row.direction_id: row for row in directions}
    value_residuals = {
        row.direction_id: float(abs(row.value - evaluated[row.direction_id].value))
        for row in analytic
    }
    hessian_symmetry = max(
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
    family_counts = {
        family: sum(row.base_family == family for row in analytic)
        for family in SELECTED_FAMILIES
    }
    expected_counts = expected_family_counts()
    actual_families = {row.base_family for row in analytic}
    live_parameter_ids = {
        row.parameter_id
        for row in potential.parameter_schema(
            potential.evaluate_directions(state)
        )
    }
    parameter_ids = {row.parameter_id for row in parameters}

    checks = {
        "corrected_value_layer_executes": value_layer["n_failed"] == 0,
        "canonical_chart_executes": chart_report["n_failed"] == 0,
        "authoritative_selected_family_ids_exist": set(SELECTED_FAMILIES).issubset(
            {row["id"] for row in ledger.BASE_FAMILIES.values()}
        ),
        "exactly_five_nonzero_base_families_selected": (
            actual_families == set(SELECTED_FAMILIES)
            and all(count > 0 for count in family_counts.values())
        ),
        "expected_G1_counts_are_nonzero": all(
            count > 0 for count in expected_counts.values()
        ),
        "every_expected_direction_differentiated": family_counts == expected_counts,
        "direction_count_is_nonzero": len(analytic) > 0,
        "parameter_count_is_nonzero": len(parameters) > 0,
        "all_direction_values_match_authoritative_evaluator": max(
            value_residuals.values()
        ) < 1.0e-10,
        "all_parameter_derivatives_belong_to_live_91_schema": (
            parameter_ids.issubset(live_parameter_ids)
            and len(parameter_ids) == len(parameters)
        ),
        "all_Hessians_symmetric": hessian_symmetry < 1.0e-12,
        "self_conjugate_derivatives_real": self_imaginary < 1.0e-10,
        "combined_value_matches_authoritative_potential": directional[
            "value_residual"
        ] < 1.0e-9,
        "five_point_first_derivative_reconstruction": directional[
            "first_residual"
        ] < 1.0e-8,
        "five_point_second_derivative_reconstruction": directional[
            "second_residual"
        ] < 1.0e-7,
        "combined_Hessian_finite": bool(np.all(np.isfinite(combined["hessian"]))),
        "combined_gradient_finite": bool(np.all(np.isfinite(combined["gradient"]))),
        "remaining_13_base_families_not_claimed": True,
        "G2_not_closed": True,
        "whole_model_not_validated": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return _jsonable(
        {
            "status": (
                "G2_EXACT_DERIVATIVES_5_OF_18_BASE_FAMILIES_CLOSED"
                if not failures
                else "G2_QUADRATIC_FAMILY_DERIVATIVES_FAILED"
            ),
            "overall_state": "PARTIAL" if not failures else "EXECUTION_FAIL",
            "n_checks": len(checks),
            "n_failed": len(failures),
            "failures": failures,
            "checks": checks,
            "coverage": {
                "base_families_closed": list(SELECTED_FAMILIES),
                "base_family_count_closed": len(SELECTED_FAMILIES),
                "base_family_count_total": len(ledger.BASE_FAMILIES),
                "expected_direction_counts": expected_counts,
                "observed_direction_counts": family_counts,
                "direction_count_closed": len(analytic),
                "parameter_count_closed": len(parameters),
                "real_field_dimension": chart.TOTAL_DIM,
                "Hessian_shape": [chart.TOTAL_DIM, chart.TOTAL_DIM],
            },
            "maximum_direction_value_residual": max(value_residuals.values()),
            "maximum_Hessian_symmetry_residual": hessian_symmetry,
            "maximum_self_conjugate_imaginary_residual": self_imaginary,
            "directional_reconstruction": directional,
            "combined_derivative_norms": {
                "gradient": float(np.linalg.norm(combined["gradient"])),
                "Hessian_frobenius": float(np.linalg.norm(combined["hessian"])),
                "Hessian_rank": int(
                    np.linalg.matrix_rank(combined["hessian"], 1.0e-10)
                ),
            },
            "flags": {
                "five_authoritative_nonzero_family_adapters_closed": not failures,
                "all_selected_direction_gradients_exact": not failures,
                "all_selected_direction_Hessians_exact": not failures,
                "all_64_direction_gradients_complete": False,
                "all_64_direction_Hessians_complete": False,
                "G2_closed": False,
                "whole_model_validated": False,
                "empirical_discovery": False,
            },
            "next_exact_target": (
                "Differentiate Phi_Sigma_Sigmadag_cubic and Phi_cubic, then the "
                "Phi_Hdag_Sigmadag and Phi_Hdag_Sigma portal families."
            ),
            "verdict": (
                "Five authoritative nonzero G1 base families now have exact dense "
                "486-gradients and 486x486 Hessians with all live singlet dressings. "
                "Thirteen families remain, so G2 stays PARTIAL."
            ),
        }
    )


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Exact derivatives for five G2 base families\n\n"
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
