#!/usr/bin/env python3
"""Exact all-64 G2 derivatives in the four canonical singlet coordinates.

For fixed non-singlet fields, every live invariant direction factors into its
value at unit singlets times a monomial in S, Sdag, Phi17, and Phi17dag.  On the
canonical 486-real chart,

    S     = (q_482 + i q_483)/sqrt(2),
    Phi17 = (q_484 + i q_485)/sqrt(2).

A second-order complex jet therefore gives exact analytic values, gradients,
and Hessians for all 64 directions and all 91 real potential parameters in
these four coordinates.  The construction is checked against finite
differences of every distinct monomial and of the assembled potential.

Only the 4-entry singlet gradient and 4x4 singlet Hessian are closed here.  The
remaining 482 gradient entries, all mixed/non-singlet Hessian blocks, the full
vacuum problem, and G2 remain open.
"""
from __future__ import annotations

import argparse
import dataclasses
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

import numpy as np

import live_g2_arbitrary_component_potential_values_v20 as potential
import live_g2_canonical_486_field_chart_v20 as chart

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "LIVE_G2_EXACT_SINGLET_DERIVATIVES_V20.json"
OUT_MD = ROOT / "LIVE_G2_EXACT_SINGLET_DERIVATIVES_V20.md"

SQRT2 = float(np.sqrt(2.0))
LOCAL_DIM = 4
GLOBAL_INDICES = (
    chart.S_SLICE.start,
    chart.S_SLICE.start + 1,
    chart.X_SLICE.start,
    chart.X_SLICE.start + 1,
)
EXPECTED_GLOBAL_INDICES = (482, 483, 484, 485)
SINGLET_LABELS = ("S.x", "S.y", "Phi17.x", "Phi17.y")
SINGLET_KEYS = ("S", "Sb", "X", "Xb")


@dataclasses.dataclass(frozen=True)
class Jet2:
    value: complex
    gradient: np.ndarray
    hessian: np.ndarray

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "gradient",
            np.asarray(self.gradient, dtype=complex).reshape(LOCAL_DIM),
        )
        object.__setattr__(
            self,
            "hessian",
            np.asarray(self.hessian, dtype=complex).reshape(LOCAL_DIM, LOCAL_DIM),
        )

    @staticmethod
    def constant(value: complex) -> "Jet2":
        return Jet2(
            complex(value),
            np.zeros(LOCAL_DIM, dtype=complex),
            np.zeros((LOCAL_DIM, LOCAL_DIM), dtype=complex),
        )

    @staticmethod
    def affine(value: complex, gradient: np.ndarray) -> "Jet2":
        return Jet2(
            complex(value),
            np.asarray(gradient, dtype=complex),
            np.zeros((LOCAL_DIM, LOCAL_DIM), dtype=complex),
        )

    def __add__(self, other: "Jet2 | complex") -> "Jet2":
        right = other if isinstance(other, Jet2) else Jet2.constant(other)
        return Jet2(
            self.value + right.value,
            self.gradient + right.gradient,
            self.hessian + right.hessian,
        )

    def __radd__(self, other: "Jet2 | complex") -> "Jet2":
        return self.__add__(other)

    def __mul__(self, other: "Jet2 | complex") -> "Jet2":
        right = other if isinstance(other, Jet2) else Jet2.constant(other)
        return Jet2(
            self.value * right.value,
            self.gradient * right.value + self.value * right.gradient,
            self.hessian * right.value
            + self.value * right.hessian
            + np.outer(self.gradient, right.gradient)
            + np.outer(right.gradient, self.gradient),
        )

    def __rmul__(self, other: "Jet2 | complex") -> "Jet2":
        return self.__mul__(other)

    def __pow__(self, exponent: int) -> "Jet2":
        power = int(exponent)
        if power < 0:
            raise ValueError("singlet exponents must be nonnegative")
        result = Jet2.constant(1.0)
        for _ in range(power):
            result = result * self
        return result


@dataclasses.dataclass(frozen=True)
class OperatorJet:
    direction_id: str
    orbit_index: int
    basis_index: int
    base_family: str
    basis_label: str
    self_conjugate: bool
    exponents: tuple[int, int, int, int]
    value: complex
    gradient: np.ndarray
    hessian: np.ndarray
    value_reconstruction_residual: float


@dataclasses.dataclass(frozen=True)
class ParameterJet:
    parameter_id: str
    direction_id: str
    component: str
    base_family: str
    exponents: tuple[int, int, int, int]
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


def local_coordinates(state: potential.FieldState) -> np.ndarray:
    q = chart.pack(state.validated())
    return np.asarray(q[list(GLOBAL_INDICES)], dtype=float)


def state_with_local_coordinates(
    reference: potential.FieldState, local: np.ndarray
) -> potential.FieldState:
    q = chart.pack(reference.validated())
    values = np.asarray(local, dtype=float).reshape(-1)
    if values.size != LOCAL_DIM:
        raise ValueError("singlet coordinate vector must have length four")
    q[list(GLOBAL_INDICES)] = values
    return chart.unpack(q)


def variable_jets(local: np.ndarray) -> dict[str, Jet2]:
    q = np.asarray(local, dtype=float).reshape(-1)
    if q.size != LOCAL_DIM:
        raise ValueError("singlet coordinate vector must have length four")
    basis = np.eye(LOCAL_DIM, dtype=complex)
    return {
        "S": Jet2.affine(
            complex(q[0], q[1]) / SQRT2,
            (basis[0] + 1j * basis[1]) / SQRT2,
        ),
        "Sb": Jet2.affine(
            complex(q[0], -q[1]) / SQRT2,
            (basis[0] - 1j * basis[1]) / SQRT2,
        ),
        "X": Jet2.affine(
            complex(q[2], q[3]) / SQRT2,
            (basis[2] + 1j * basis[3]) / SQRT2,
        ),
        "Xb": Jet2.affine(
            complex(q[2], -q[3]) / SQRT2,
            (basis[2] - 1j * basis[3]) / SQRT2,
        ),
    }


def exponents(direction: potential.Direction) -> tuple[int, int, int, int]:
    counts = dict(zip(potential.FIELD_ORDER, direction.counts, strict=True))
    return tuple(int(counts[key]) for key in SINGLET_KEYS)


def monomial_jet(local: np.ndarray, powers: tuple[int, int, int, int]) -> Jet2:
    factors = variable_jets(local)
    result = Jet2.constant(1.0)
    for key, power in zip(SINGLET_KEYS, powers, strict=True):
        result = result * (factors[key] ** int(power))
    return result


def monomial_value(local: np.ndarray, powers: tuple[int, int, int, int]) -> complex:
    q = np.asarray(local, dtype=float).reshape(LOCAL_DIM)
    factors = {
        "S": complex(q[0], q[1]) / SQRT2,
        "Sb": complex(q[0], -q[1]) / SQRT2,
        "X": complex(q[2], q[3]) / SQRT2,
        "Xb": complex(q[2], -q[3]) / SQRT2,
    }
    result = 1.0 + 0.0j
    for key, power in zip(SINGLET_KEYS, powers, strict=True):
        result *= factors[key] ** int(power)
    return complex(result)


def unit_singlet_directions(
    reference: potential.FieldState,
) -> tuple[potential.Direction, ...]:
    field = reference.validated()
    state = potential.FieldState(
        phi=field.phi,
        h=field.h,
        sigma=field.sigma,
        s=1.0 + 0.0j,
        x=1.0 + 0.0j,
    ).validated()
    return potential.evaluate_directions(state)


def operator_jets(reference: potential.FieldState) -> tuple[OperatorJet, ...]:
    field = reference.validated()
    local = local_coordinates(field)
    bases = unit_singlet_directions(field)
    live = potential.evaluate_directions(field)
    if [row.direction_id for row in bases] != [row.direction_id for row in live]:
        raise AssertionError("direction order changed under unit-singlet substitution")
    output: list[OperatorJet] = []
    for base, actual in zip(bases, live, strict=True):
        powers = exponents(actual)
        jet = complex(base.value) * monomial_jet(local, powers)
        output.append(
            OperatorJet(
                direction_id=actual.direction_id,
                orbit_index=actual.orbit_index,
                basis_index=actual.basis_index,
                base_family=actual.base_family,
                basis_label=actual.basis_label,
                self_conjugate=actual.self_conjugate,
                exponents=powers,
                value=jet.value,
                gradient=jet.gradient,
                hessian=0.5 * (jet.hessian + jet.hessian.T),
                value_reconstruction_residual=float(abs(jet.value - actual.value)),
            )
        )
    return tuple(output)


def parameter_jets(operators: Iterable[OperatorJet]) -> tuple[ParameterJet, ...]:
    output: list[ParameterJet] = []
    for row in operators:
        common = {
            "direction_id": row.direction_id,
            "base_family": row.base_family,
            "exponents": row.exponents,
        }
        if row.self_conjugate:
            output.append(
                ParameterJet(
                    parameter_id=f"lambda::{row.direction_id}",
                    component="real",
                    value=float(row.value.real),
                    gradient=np.asarray(row.gradient.real, dtype=float),
                    hessian=np.asarray(row.hessian.real, dtype=float),
                    **common,
                )
            )
        else:
            output.append(
                ParameterJet(
                    parameter_id=f"re::{row.direction_id}",
                    component="re",
                    value=float(2.0 * row.value.real),
                    gradient=np.asarray(2.0 * row.gradient.real, dtype=float),
                    hessian=np.asarray(2.0 * row.hessian.real, dtype=float),
                    **common,
                )
            )
            output.append(
                ParameterJet(
                    parameter_id=f"im::{row.direction_id}",
                    component="im",
                    value=float(-2.0 * row.value.imag),
                    gradient=np.asarray(-2.0 * row.gradient.imag, dtype=float),
                    hessian=np.asarray(-2.0 * row.hessian.imag, dtype=float),
                    **common,
                )
            )
    return tuple(output)


def assemble(
    parameters: Iterable[ParameterJet], coefficients: Mapping[str, float]
) -> dict[str, Any]:
    rows = tuple(parameters)
    allowed = {row.parameter_id for row in rows}
    unknown = sorted(set(coefficients).difference(allowed))
    if unknown:
        raise KeyError(f"unknown coefficient keys: {unknown}")
    value = 0.0
    gradient = np.zeros(LOCAL_DIM, dtype=float)
    hessian = np.zeros((LOCAL_DIM, LOCAL_DIM), dtype=float)
    active: list[str] = []
    for row in rows:
        coefficient = float(coefficients.get(row.parameter_id, 0.0))
        if coefficient != 0.0:
            active.append(row.parameter_id)
        value += coefficient * row.value
        gradient += coefficient * row.gradient
        hessian += coefficient * row.hessian
    return {
        "value": float(value),
        "gradient": gradient,
        "hessian": 0.5 * (hessian + hessian.T),
        "active_parameters": active,
    }


def monomial_finite_difference_audit(
    local: np.ndarray,
    exponent_rows: Iterable[tuple[int, int, int, int]],
) -> dict[str, Any]:
    q = np.asarray(local, dtype=float).reshape(LOCAL_DIM)
    h1 = 1.0e-6
    h2 = 2.0e-4
    rows: list[dict[str, Any]] = []
    for powers in sorted(set(tuple(map(int, row)) for row in exponent_rows)):
        jet = monomial_jet(q, powers)
        gradient = np.empty(LOCAL_DIM, dtype=complex)
        hessian = np.empty((LOCAL_DIM, LOCAL_DIM), dtype=complex)
        center = monomial_value(q, powers)
        for i in range(LOCAL_DIM):
            ei = np.zeros(LOCAL_DIM)
            ei[i] = h1
            gradient[i] = (
                monomial_value(q + ei, powers) - monomial_value(q - ei, powers)
            ) / (2.0 * h1)
            di = np.zeros(LOCAL_DIM)
            di[i] = h2
            hessian[i, i] = (
                monomial_value(q + di, powers)
                - 2.0 * center
                + monomial_value(q - di, powers)
            ) / (h2**2)
            for j in range(i + 1, LOCAL_DIM):
                dj = np.zeros(LOCAL_DIM)
                dj[j] = h2
                mixed = (
                    monomial_value(q + di + dj, powers)
                    - monomial_value(q + di - dj, powers)
                    - monomial_value(q - di + dj, powers)
                    + monomial_value(q - di - dj, powers)
                ) / (4.0 * h2**2)
                hessian[i, j] = mixed
                hessian[j, i] = mixed
        rows.append(
            {
                "exponents": powers,
                "gradient_residual": float(np.max(np.abs(jet.gradient - gradient))),
                "Hessian_residual": float(np.max(np.abs(jet.hessian - hessian))),
            }
        )
    return {
        "distinct_monomials": len(rows),
        "maximum_gradient_residual": max(row["gradient_residual"] for row in rows),
        "maximum_Hessian_residual": max(row["Hessian_residual"] for row in rows),
        "rows": rows,
    }


def reconstructed_potential_value(
    bases: tuple[potential.Direction, ...],
    local: np.ndarray,
    coefficients: Mapping[str, float],
) -> float:
    directions = tuple(
        dataclasses.replace(
            row,
            value=complex(row.value) * monomial_value(local, exponents(row)),
        )
        for row in bases
    )
    return potential.potential_value(directions, coefficients)


def combined_finite_difference_audit(
    reference: potential.FieldState,
    coefficients: Mapping[str, float],
) -> dict[str, Any]:
    field = reference.validated()
    q = local_coordinates(field)
    bases = unit_singlet_directions(field)
    exact = assemble(parameter_jets(operator_jets(field)), coefficients)
    h1 = 2.0e-6
    h2 = 3.0e-4

    def evaluate(point: np.ndarray) -> float:
        return reconstructed_potential_value(bases, point, coefficients)

    center = evaluate(q)
    gradient = np.empty(LOCAL_DIM, dtype=float)
    hessian = np.empty((LOCAL_DIM, LOCAL_DIM), dtype=float)
    for i in range(LOCAL_DIM):
        ei = np.zeros(LOCAL_DIM)
        ei[i] = h1
        gradient[i] = (evaluate(q + ei) - evaluate(q - ei)) / (2.0 * h1)
        di = np.zeros(LOCAL_DIM)
        di[i] = h2
        hessian[i, i] = (
            evaluate(q + di) - 2.0 * center + evaluate(q - di)
        ) / (h2**2)
        for j in range(i + 1, LOCAL_DIM):
            dj = np.zeros(LOCAL_DIM)
            dj[j] = h2
            mixed = (
                evaluate(q + di + dj)
                - evaluate(q + di - dj)
                - evaluate(q - di + dj)
                + evaluate(q - di - dj)
            ) / (4.0 * h2**2)
            hessian[i, j] = mixed
            hessian[j, i] = mixed
    return {
        "value_residual": float(abs(exact["value"] - center)),
        "gradient_residual": float(np.max(np.abs(exact["gradient"] - gradient))),
        "Hessian_residual": float(np.max(np.abs(exact["hessian"] - hessian))),
    }


def build_report() -> dict[str, Any]:
    state = potential.deterministic_state(2404)
    live = potential.evaluate_directions(state)
    operators = operator_jets(state)
    parameters = parameter_jets(operators)
    schema = potential.parameter_schema(live)
    coefficients = potential.deterministic_coefficients(schema)
    combined = assemble(parameters, coefficients)
    direct_value = potential.potential_value(live, coefficients)
    monomial_audit = monomial_finite_difference_audit(
        local_coordinates(state), (row.exponents for row in operators)
    )
    combined_audit = combined_finite_difference_audit(state, coefficients)
    chart_report = chart.build_report()
    labels = chart.coordinate_names()
    selected_labels = tuple(labels[index] for index in GLOBAL_INDICES)
    parameter_ids = {row.parameter_id for row in parameters}
    schema_ids = {row.parameter_id for row in schema}
    maximum_operator_value_residual = max(
        row.value_reconstruction_residual for row in operators
    )
    maximum_Hessian_asymmetry = max(
        float(np.max(np.abs(row.hessian - row.hessian.T))) for row in parameters
    )
    checks = {
        "canonical_chart_executes": chart_report["n_failed"] == 0,
        "global_indices_are_482_to_485": GLOBAL_INDICES == EXPECTED_GLOBAL_INDICES,
        "coordinate_names_match_chart": selected_labels == SINGLET_LABELS,
        "all_64_operator_jets_constructed": len(operators) == 64,
        "all_91_parameter_jets_constructed": len(parameters) == 91,
        "parameter_ids_match_live_schema": parameter_ids == schema_ids,
        "operator_values_match_full_evaluator": maximum_operator_value_residual < 1.0e-10,
        "assembled_value_matches_full_potential": abs(combined["value"] - direct_value) < 1.0e-9,
        "all_parameter_Hessians_symmetric": maximum_Hessian_asymmetry < 1.0e-12,
        "all_monomial_gradients_match_finite_difference": monomial_audit[
            "maximum_gradient_residual"
        ] < 2.0e-7,
        "all_monomial_Hessians_match_finite_difference": monomial_audit[
            "maximum_Hessian_residual"
        ] < 3.0e-6,
        "assembled_gradient_matches_finite_difference": combined_audit[
            "gradient_residual"
        ] < 2.0e-5,
        "assembled_Hessian_matches_finite_difference": combined_audit[
            "Hessian_residual"
        ] < 2.0e-3,
        "remaining_482_gradient_entries_not_claimed": True,
        "remaining_Hessian_blocks_not_claimed": True,
        "G2_not_closed": True,
        "whole_model_not_validated": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return _jsonable(
        {
            "status": (
                "G2_EXACT_ALL64_FOUR_SINGLET_DERIVATIVES_CLOSED"
                if not failures
                else "G2_EXACT_SINGLET_DERIVATIVES_FAILED"
            ),
            "overall_state": "PARTIAL" if not failures else "EXECUTION_FAIL",
            "n_checks": len(checks),
            "n_failed": len(failures),
            "failures": failures,
            "checks": checks,
            "scope": {
                "global_indices": list(GLOBAL_INDICES),
                "coordinate_names": list(SINGLET_LABELS),
                "complete_gradient_entries": 4,
                "complete_symmetric_Hessian_entries": 10,
                "full_gradient_entries_required": chart.TOTAL_DIM,
                "full_symmetric_Hessian_entries_required": chart.SYMMETRIC_HESSIAN_ENTRIES,
                "remaining_gradient_entries": chart.TOTAL_DIM - 4,
            },
            "counts": {
                "operator_directions": len(operators),
                "real_parameters": len(parameters),
                "distinct_singlet_monomials": monomial_audit["distinct_monomials"],
            },
            "maximum_operator_value_reconstruction_residual": maximum_operator_value_residual,
            "maximum_parameter_Hessian_asymmetry": maximum_Hessian_asymmetry,
            "monomial_finite_difference_audit": monomial_audit,
            "combined_finite_difference_audit": combined_audit,
            "benchmark": {
                "potential_value": combined["value"],
                "gradient": combined["gradient"],
                "Hessian": combined["hessian"],
                "active_parameters": len(combined["active_parameters"]),
            },
            "parameter_provenance": parameters,
            "flags": {
                "all_64_operator_singlet_jets_complete": not failures,
                "all_91_parameter_singlet_derivatives_complete": not failures,
                "singlet_gradient_4_complete": not failures,
                "singlet_Hessian_4x4_complete": not failures,
                "complete_486_gradient": False,
                "complete_486_Hessian": False,
                "G2_closed": False,
                "stationarity_solved": False,
                "whole_model_validated": False,
                "empirical_discovery": False,
            },
            "next_exact_target": (
                "Combine this all-family singlet block with verified full-coordinate "
                "base-family derivatives, then extend analytic adapters through all "
                "eighteen G1 families."
            ),
            "verdict": (
                "All 64 live operators and all 91 real potential parameters now have "
                "exact derivatives with respect to the four canonical singlet "
                "coordinates. The remaining 482 gradient entries and non-singlet/"
                "mixed Hessian blocks remain open, so G2 is still PARTIAL."
            ),
        }
    )


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Exact all-64 four-singlet G2 derivatives\n\n"
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
