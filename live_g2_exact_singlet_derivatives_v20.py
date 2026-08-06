#!/usr/bin/env python3
"""Exact four-singlet second-order derivatives of the live G2 potential.

The corrected live potential contains 64 invariant directions and 91 real
couplings.  Its singlet dependence is entirely polynomial in

    S, Sdag, Phi17, Phi17dag.

Using the canonical real coordinates from the 486-field chart,

    S     = (q0 + i q1)/sqrt(2),
    Phi17 = (q2 + i q3)/sqrt(2),

this module propagates an exact second-order jet through every singlet monomial.
It emits, with per-direction and per-parameter provenance,

* the potential value;
* the complete four-entry singlet gradient;
* the complete symmetric 4x4 singlet Hessian.

The result is exact up to floating-point evaluation of the already-normalized
non-singlet tensor coefficients.  It is independently checked against central
finite differences of every distinct singlet monomial and against the full
64-direction potential value.

This closes only the four-singlet derivative block.  The remaining 482 field
derivatives, the full 486x486 Hessian, stationarity, the global vacuum, and G2
remain open.
"""
from __future__ import annotations

import argparse
import dataclasses
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

import numpy as np

import live_g2_arbitrary_component_potential_values_v20 as values
import live_g2_canonical_486_field_chart_v20 as chart

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "LIVE_G2_EXACT_SINGLET_DERIVATIVES_V20.json"
OUT_MD = ROOT / "LIVE_G2_EXACT_SINGLET_DERIVATIVES_V20.md"

SQRT2 = float(np.sqrt(2.0))
SINGLET_DIMENSION = 4
GLOBAL_INDICES = (482, 483, 484, 485)
SINGLET_LABELS = (
    "sqrt2_Re_S",
    "sqrt2_Im_S",
    "sqrt2_Re_Phi17",
    "sqrt2_Im_Phi17",
)
SINGLET_COUNT_KEYS = ("S", "Sb", "X", "Xb")


@dataclasses.dataclass(frozen=True)
class Jet2:
    """Complex value, gradient, and symmetric Hessian in four real variables."""

    value: complex
    gradient: np.ndarray
    hessian: np.ndarray

    def __post_init__(self) -> None:
        gradient = np.asarray(self.gradient, dtype=complex).reshape(
            SINGLET_DIMENSION
        )
        hessian = np.asarray(self.hessian, dtype=complex).reshape(
            SINGLET_DIMENSION, SINGLET_DIMENSION
        )
        object.__setattr__(self, "gradient", gradient)
        object.__setattr__(self, "hessian", hessian)

    @staticmethod
    def constant(value: complex) -> "Jet2":
        return Jet2(
            complex(value),
            np.zeros(SINGLET_DIMENSION, dtype=complex),
            np.zeros((SINGLET_DIMENSION, SINGLET_DIMENSION), dtype=complex),
        )

    @staticmethod
    def affine(value: complex, gradient: np.ndarray) -> "Jet2":
        return Jet2(
            complex(value),
            np.asarray(gradient, dtype=complex),
            np.zeros((SINGLET_DIMENSION, SINGLET_DIMENSION), dtype=complex),
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
        gradient = self.gradient * right.value + self.value * right.gradient
        hessian = (
            self.hessian * right.value
            + self.value * right.hessian
            + np.outer(self.gradient, right.gradient)
            + np.outer(right.gradient, self.gradient)
        )
        return Jet2(self.value * right.value, gradient, hessian)

    def __rmul__(self, other: "Jet2 | complex") -> "Jet2":
        return self.__mul__(other)

    def __pow__(self, exponent: int) -> "Jet2":
        power = int(exponent)
        if power < 0:
            raise ValueError("singlet polynomial exponents must be nonnegative")
        output = Jet2.constant(1.0)
        for _ in range(power):
            output = output * self
        return output


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


def canonical_singlet_coordinates(state: values.FieldState) -> np.ndarray:
    field = state.validated()
    return np.asarray(
        [
            SQRT2 * field.s.real,
            SQRT2 * field.s.imag,
            SQRT2 * field.x.real,
            SQRT2 * field.x.imag,
        ],
        dtype=float,
    )


def singlet_state_from_coordinates(
    reference: values.FieldState, coordinates: np.ndarray
) -> values.FieldState:
    field = reference.validated()
    q = np.asarray(coordinates, dtype=float).reshape(-1)
    if q.size != SINGLET_DIMENSION:
        raise ValueError("singlet coordinate vector must have length four")
    return values.FieldState(
        phi=field.phi,
        h=field.h,
        sigma=field.sigma,
        s=complex(q[0], q[1]) / SQRT2,
        x=complex(q[2], q[3]) / SQRT2,
    ).validated()


def singlet_variable_jets(coordinates: np.ndarray) -> dict[str, Jet2]:
    q = np.asarray(coordinates, dtype=float).reshape(-1)
    if q.size != SINGLET_DIMENSION:
        raise ValueError("singlet coordinate vector must have length four")
    basis = np.eye(SINGLET_DIMENSION, dtype=complex)
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


def singlet_exponents(direction: values.Direction) -> tuple[int, int, int, int]:
    counts = dict(zip(values.FIELD_ORDER, direction.counts, strict=True))
    return tuple(int(counts[key]) for key in SINGLET_COUNT_KEYS)


def monomial_jet(
    coordinates: np.ndarray, exponents: tuple[int, int, int, int]
) -> Jet2:
    variables = singlet_variable_jets(coordinates)
    output = Jet2.constant(1.0)
    for key, exponent in zip(SINGLET_COUNT_KEYS, exponents, strict=True):
        output = output * (variables[key] ** int(exponent))
    return output


def monomial_value(
    coordinates: np.ndarray, exponents: tuple[int, int, int, int]
) -> complex:
    q = np.asarray(coordinates, dtype=float).reshape(SINGLET_DIMENSION)
    scalar = {
        "S": complex(q[0], q[1]) / SQRT2,
        "Sb": complex(q[0], -q[1]) / SQRT2,
        "X": complex(q[2], q[3]) / SQRT2,
        "Xb": complex(q[2], -q[3]) / SQRT2,
    }
    output = 1.0 + 0.0j
    for key, exponent in zip(SINGLET_COUNT_KEYS, exponents, strict=True):
        output *= scalar[key] ** int(exponent)
    return complex(output)


def base_directions(reference: values.FieldState) -> tuple[values.Direction, ...]:
    field = reference.validated()
    unit = values.FieldState(
        phi=field.phi,
        h=field.h,
        sigma=field.sigma,
        s=1.0 + 0.0j,
        x=1.0 + 0.0j,
    ).validated()
    return values.evaluate_directions(unit)


def operator_jets(reference: values.FieldState) -> tuple[dict[str, Any], ...]:
    field = reference.validated()
    q = canonical_singlet_coordinates(field)
    bases = base_directions(field)
    actual = values.evaluate_directions(field)
    if [row.direction_id for row in bases] != [row.direction_id for row in actual]:
        raise AssertionError("direction ordering changed between unit and live singlets")
    rows: list[dict[str, Any]] = []
    for base, live in zip(bases, actual, strict=True):
        exponents = singlet_exponents(live)
        jet = complex(base.value) * monomial_jet(q, exponents)
        rows.append(
            {
                "direction_id": live.direction_id,
                "orbit_index": live.orbit_index,
                "basis_index": live.basis_index,
                "base_family": live.base_family,
                "basis_label": live.basis_label,
                "self_conjugate": live.self_conjugate,
                "degree": live.degree,
                "singlet_exponents": exponents,
                "base_value_at_unit_singlets": complex(base.value),
                "live_operator_value": complex(live.value),
                "jet": jet,
                "value_reconstruction_residual": float(abs(jet.value - live.value)),
            }
        )
    return tuple(rows)


def _real_jet(jet: Jet2, factor: complex = 1.0) -> dict[str, Any]:
    weighted = complex(factor) * jet
    return {
        "value": float(np.real(weighted.value)),
        "gradient": np.asarray(np.real(weighted.gradient), dtype=float),
        "hessian": np.asarray(np.real(weighted.hessian), dtype=float),
    }


def parameter_derivative_tensors(
    reference: values.FieldState,
) -> dict[str, dict[str, Any]]:
    output: dict[str, dict[str, Any]] = {}
    for row in operator_jets(reference):
        direction_id = str(row["direction_id"])
        jet = row["jet"]
        common = {
            "direction_id": direction_id,
            "orbit_index": int(row["orbit_index"]),
            "basis_index": int(row["basis_index"]),
            "base_family": str(row["base_family"]),
            "basis_label": str(row["basis_label"]),
            "singlet_exponents": tuple(row["singlet_exponents"]),
        }
        if bool(row["self_conjugate"]):
            name = f"lambda::{direction_id}"
            output[name] = {
                **common,
                "parameter_id": name,
                "component": "real",
                **_real_jet(jet),
            }
        else:
            real_name = f"re::{direction_id}"
            imag_name = f"im::{direction_id}"
            output[real_name] = {
                **common,
                "parameter_id": real_name,
                "component": "re",
                **_real_jet(jet, 2.0),
            }
            output[imag_name] = {
                **common,
                "parameter_id": imag_name,
                "component": "im",
                **_real_jet(jet, 2.0j),
            }
    return output


def potential_singlet_jet(
    reference: values.FieldState,
    coefficients: Mapping[str, float],
) -> dict[str, Any]:
    tensors = parameter_derivative_tensors(reference)
    unknown = sorted(set(coefficients).difference(tensors))
    if unknown:
        raise KeyError(f"unknown coefficient keys: {unknown}")
    value = 0.0
    gradient = np.zeros(SINGLET_DIMENSION, dtype=float)
    hessian = np.zeros((SINGLET_DIMENSION, SINGLET_DIMENSION), dtype=float)
    active: list[str] = []
    for parameter_id, tensor in tensors.items():
        coefficient = float(coefficients.get(parameter_id, 0.0))
        if coefficient != 0.0:
            active.append(parameter_id)
        value += coefficient * float(tensor["value"])
        gradient += coefficient * np.asarray(tensor["gradient"], dtype=float)
        hessian += coefficient * np.asarray(tensor["hessian"], dtype=float)
    return {
        "value": float(value),
        "gradient": gradient,
        "hessian": 0.5 * (hessian + hessian.T),
        "active_parameters": active,
        "parameter_tensors": tensors,
    }


def monomial_finite_difference_audit(
    coordinates: np.ndarray,
    exponents: Iterable[tuple[int, int, int, int]],
) -> dict[str, Any]:
    q = np.asarray(coordinates, dtype=float).reshape(SINGLET_DIMENSION)
    gradient_step = 1.0e-6
    hessian_step = 2.0e-4
    rows: list[dict[str, Any]] = []
    for powers in sorted(set(tuple(int(item) for item in row) for row in exponents)):
        jet = monomial_jet(q, powers)
        gradient_fd = np.empty(SINGLET_DIMENSION, dtype=complex)
        for i in range(SINGLET_DIMENSION):
            delta = np.zeros(SINGLET_DIMENSION)
            delta[i] = gradient_step
            gradient_fd[i] = (
                monomial_value(q + delta, powers)
                - monomial_value(q - delta, powers)
            ) / (2.0 * gradient_step)
        hessian_fd = np.empty(
            (SINGLET_DIMENSION, SINGLET_DIMENSION), dtype=complex
        )
        center = monomial_value(q, powers)
        for i in range(SINGLET_DIMENSION):
            delta_i = np.zeros(SINGLET_DIMENSION)
            delta_i[i] = hessian_step
            hessian_fd[i, i] = (
                monomial_value(q + delta_i, powers)
                - 2.0 * center
                + monomial_value(q - delta_i, powers)
            ) / (hessian_step**2)
            for j in range(i + 1, SINGLET_DIMENSION):
                delta_j = np.zeros(SINGLET_DIMENSION)
                delta_j[j] = hessian_step
                value = (
                    monomial_value(q + delta_i + delta_j, powers)
                    - monomial_value(q + delta_i - delta_j, powers)
                    - monomial_value(q - delta_i + delta_j, powers)
                    + monomial_value(q - delta_i - delta_j, powers)
                ) / (4.0 * hessian_step**2)
                hessian_fd[i, j] = value
                hessian_fd[j, i] = value
        rows.append(
            {
                "exponents": powers,
                "gradient_max_abs_residual": float(
                    np.max(np.abs(jet.gradient - gradient_fd))
                ),
                "hessian_max_abs_residual": float(
                    np.max(np.abs(jet.hessian - hessian_fd))
                ),
            }
        )
    return {
        "distinct_monomials": len(rows),
        "gradient_step": gradient_step,
        "hessian_step": hessian_step,
        "maximum_gradient_residual": max(
            row["gradient_max_abs_residual"] for row in rows
        ),
        "maximum_hessian_residual": max(
            row["hessian_max_abs_residual"] for row in rows
        ),
        "rows": rows,
    }


def combined_finite_difference_audit(
    reference: values.FieldState,
    coefficients: Mapping[str, float],
) -> dict[str, Any]:
    field = reference.validated()
    q = canonical_singlet_coordinates(field)
    bases = base_directions(field)
    base_map = {row.direction_id: row for row in bases}
    schema = values.parameter_schema(values.evaluate_directions(field))
    allowed = {row.parameter_id for row in schema}
    unknown = set(coefficients).difference(allowed)
    if unknown:
        raise KeyError(f"unknown coefficient keys: {sorted(unknown)}")

    def scalar(point: np.ndarray) -> float:
        rows: list[values.Direction] = []
        state = singlet_state_from_coordinates(field, point)
        for live in values.evaluate_directions(state):
            rows.append(live)
        return values.potential_value(tuple(rows), coefficients)

    exact = potential_singlet_jet(field, coefficients)
    gradient_step = 2.0e-6
    hessian_step = 3.0e-4
    gradient_fd = np.empty(SINGLET_DIMENSION, dtype=float)
    for i in range(SINGLET_DIMENSION):
        delta = np.zeros(SINGLET_DIMENSION)
        delta[i] = gradient_step
        gradient_fd[i] = (scalar(q + delta) - scalar(q - delta)) / (
            2.0 * gradient_step
        )
    hessian_fd = np.empty((SINGLET_DIMENSION, SINGLET_DIMENSION), dtype=float)
    center = scalar(q)
    for i in range(SINGLET_DIMENSION):
        delta_i = np.zeros(SINGLET_DIMENSION)
        delta_i[i] = hessian_step
        hessian_fd[i, i] = (
            scalar(q + delta_i) - 2.0 * center + scalar(q - delta_i)
        ) / (hessian_step**2)
        for j in range(i + 1, SINGLET_DIMENSION):
            delta_j = np.zeros(SINGLET_DIMENSION)
            delta_j[j] = hessian_step
            value = (
                scalar(q + delta_i + delta_j)
                - scalar(q + delta_i - delta_j)
                - scalar(q - delta_i + delta_j)
                + scalar(q - delta_i - delta_j)
            ) / (4.0 * hessian_step**2)
            hessian_fd[i, j] = value
            hessian_fd[j, i] = value
    return {
        "value_residual": float(abs(exact["value"] - center)),
        "gradient_max_abs_residual": float(
            np.max(np.abs(exact["gradient"] - gradient_fd))
        ),
        "hessian_max_abs_residual": float(
            np.max(np.abs(exact["hessian"] - hessian_fd))
        ),
        "gradient_step": gradient_step,
        "hessian_step": hessian_step,
    }


def build_report() -> dict[str, Any]:
    state = values.deterministic_state(2404)
    directions = values.evaluate_directions(state)
    parameters = values.parameter_schema(directions)
    coefficients = values.deterministic_coefficients(parameters)
    jets = operator_jets(state)
    tensors = parameter_derivative_tensors(state)
    combined = potential_singlet_jet(state, coefficients)
    direct_value = values.potential_value(directions, coefficients)
    exponents = [tuple(row["singlet_exponents"]) for row in jets]
    monomial_fd = monomial_finite_difference_audit(
        canonical_singlet_coordinates(state), exponents
    )
    combined_fd = combined_finite_difference_audit(state, coefficients)
    labels = chart.coordinate_labels()
    chart_labels = tuple(labels[index] for index in GLOBAL_INDICES)
    maximum_operator_value_residual = max(
        float(row["value_reconstruction_residual"]) for row in jets
    )
    maximum_parameter_hessian_asymmetry = max(
        float(
            np.max(
                np.abs(
                    np.asarray(row["hessian"], dtype=float)
                    - np.asarray(row["hessian"], dtype=float).T
                )
            )
        )
        for row in tensors.values()
    )
    checks = {
        "canonical_chart_executes": chart.build_report()["n_failed"] == 0,
        "all_64_operator_jets_constructed": len(jets) == 64,
        "all_91_parameter_tensors_constructed": len(tensors) == 91,
        "global_singlet_indices_are_482_to_485": GLOBAL_INDICES == (482, 483, 484, 485),
        "singlet_labels_match_canonical_chart": chart_labels == SINGLET_LABELS,
        "operator_values_reconstructed": maximum_operator_value_residual < 1.0e-10,
        "combined_value_matches_full_potential": abs(
            combined["value"] - direct_value
        )
        < 1.0e-9,
        "combined_gradient_has_four_entries": np.asarray(
            combined["gradient"]
        ).shape
        == (4,),
        "combined_Hessian_is_4x4": np.asarray(combined["hessian"]).shape
        == (4, 4),
        "combined_Hessian_symmetric": float(
            np.max(
                np.abs(
                    np.asarray(combined["hessian"])
                    - np.asarray(combined["hessian"]).T
                )
            )
        )
        < 1.0e-12,
        "all_parameter_Hessians_symmetric": maximum_parameter_hessian_asymmetry
        < 1.0e-12,
        "all_distinct_monomial_gradients_match_finite_difference": monomial_fd[
            "maximum_gradient_residual"
        ]
        < 2.0e-7,
        "all_distinct_monomial_Hessians_match_finite_difference": monomial_fd[
            "maximum_hessian_residual"
        ]
        < 3.0e-6,
        "combined_gradient_matches_full_potential_finite_difference": combined_fd[
            "gradient_max_abs_residual"
        ]
        < 2.0e-5,
        "combined_Hessian_matches_full_potential_finite_difference": combined_fd[
            "hessian_max_abs_residual"
        ]
        < 2.0e-3,
        "remaining_482_gradient_entries_not_claimed": True,
        "remaining_Hessian_blocks_not_claimed": True,
        "G2_not_claimed_closed": True,
        "whole_model_not_validated": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return _jsonable(
        {
            "status": (
                "LIVE_G2_EXACT_FOUR_SINGLET_DERIVATIVES_CLOSED__FULL_486_OPEN"
                if not failures
                else "LIVE_G2_EXACT_SINGLET_DERIVATIVES_FAILED"
            ),
            "overall_state": "PARTIAL",
            "n_checks": len(checks),
            "n_failed": len(failures),
            "failures": failures,
            "checks": checks,
            "scope": {
                "global_coordinate_indices": list(GLOBAL_INDICES),
                "coordinate_labels": list(SINGLET_LABELS),
                "singlet_gradient_entries_complete": 4,
                "singlet_symmetric_Hessian_entries_complete": 10,
                "full_gradient_entries_required": 486,
                "full_symmetric_Hessian_entries_required": 118341,
                "remaining_gradient_entries": 482,
                "full_G2_derivative_completion_fraction_by_gradient_entries": 4.0 / 486.0,
                "full_G2_derivative_completion_fraction_by_Hessian_entries": 10.0 / 118341.0,
            },
            "counts": {
                "operator_directions": len(jets),
                "real_parameters": len(tensors),
                "distinct_singlet_monomials": monomial_fd[
                    "distinct_monomials"
                ],
            },
            "combined_benchmark": {
                "potential_value": combined["value"],
                "gradient": combined["gradient"],
                "Hessian": combined["hessian"],
                "active_parameters": len(combined["active_parameters"]),
            },
            "maximum_operator_value_reconstruction_residual": (
                maximum_operator_value_residual
            ),
            "maximum_parameter_Hessian_asymmetry": (
                maximum_parameter_hessian_asymmetry
            ),
            "monomial_finite_difference_audit": monomial_fd,
            "combined_full_potential_finite_difference_audit": combined_fd,
            "parameter_derivative_tensors": tensors,
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
                "Extend the same per-direction derivative provenance to the 20 real "
                "H10 coordinates, then the 210 and physical 252-real 126bar blocks, "
                "before assembling the complete 486-real gradient and Hessian."
            ),
            "verdict": (
                "The potential now has an exact, parameter-resolved gradient and "
                "Hessian for all four singlet coordinates, covering all 64 operators "
                "and 91 real couplings. The other 482 gradient entries and all mixed/"
                "non-singlet Hessian blocks remain open, so G2 is still PARTIAL."
            ),
        }
    )


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Live G2 exact four-singlet derivatives\n\n"
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
