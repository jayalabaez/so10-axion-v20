#!/usr/bin/env python3
"""Exact 486-real derivatives for the four 126bar self-projector quartics.

For the physical complex 126bar coordinate vector z and the four orthogonal
pair-Casimir projectors P_R on Sym^2(126bar), the authoritative invariants are

    I_R(z) = ||P_R(z z^T)||_F^2,
    R in {54, 1050bar, 2772bar, 4125}.

Writing A=P_R(zz^T), L_i=P_R(d_i z^T+z d_i^T) for the canonical real chart
basis d_i, the exact real derivatives are

    grad_i I_R = 2 Re <A,L_i>,
    Hess_ij I_R = 2 Re(<L_i,L_j> + <A,P_R(d_i d_j^T+d_j d_i^T)>).

Projector self-adjointness reduces the second term to a dense 252x252 matrix
without finite differences.  Every live singlet dressing is propagated by the
shared exact product rule.  This closes one G2 base family only.
"""
from __future__ import annotations

import argparse
import dataclasses
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np

import exact_126bar_self_quartic_basis_v20 as source
import live_g1_tensor_closure_ledger_v20 as ledger
import live_g2_arbitrary_component_potential_values_v20 as potential
import live_g2_canonical_486_field_chart_v20 as chart
import live_g2_exact_quadratic_family_derivatives_v20 as quadratic

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "LIVE_G2_EXACT_SIGMA_SELF_QUARTIC_DERIVATIVES_V20.json"
OUT_MD = ROOT / "LIVE_G2_EXACT_SIGMA_SELF_QUARTIC_DERIVATIVES_V20.md"
BASE_FAMILY = "126bar_self_projectors"
BASIS_LABELS = ("54", "1050bar", "2772bar", "4125")


def _jsonable(value: Any) -> Any:
    if dataclasses.is_dataclass(value):
        return _jsonable(dataclasses.asdict(value))
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, np.ndarray):
        return _jsonable(value.tolist())
    if isinstance(value, np.generic):
        return _jsonable(value.item())
    if isinstance(value, complex):
        return {"re": float(value.real), "im": float(value.imag)}
    return value


@lru_cache(maxsize=1)
def real_chart_basis() -> np.ndarray:
    """126x252 complex map from canonical real Sigma coordinates to z."""
    basis = np.zeros((chart.SIGMA_COMPLEX_DIM, chart.SIGMA_REAL_DIM), dtype=complex)
    scale = 1.0 / chart.SQRT2
    for index in range(chart.SIGMA_COMPLEX_DIM):
        basis[index, 2 * index] = scale
        basis[index, 2 * index + 1] = 1j * scale
    return basis


def _sigma_coordinates(q_sigma: np.ndarray) -> np.ndarray:
    block = np.asarray(q_sigma, dtype=float).reshape(chart.SIGMA_REAL_DIM)
    return real_chart_basis() @ block


@lru_cache(maxsize=2)
def _base_blocks_cached(
    q_sigma: tuple[float, ...],
) -> tuple[tuple[complex, np.ndarray, np.ndarray], ...]:
    block = np.asarray(q_sigma, dtype=float)
    z = _sigma_coordinates(block)
    pair = np.outer(z, z)
    powers = source._powers(pair)
    D = real_chart_basis()

    linear_images_by_label = {
        label: np.empty(
            (chart.SIGMA_COMPLEX_DIM, chart.SIGMA_COMPLEX_DIM, chart.SIGMA_REAL_DIM),
            dtype=complex,
        )
        for label in BASIS_LABELS
    }
    for column in range(chart.SIGMA_REAL_DIM):
        linear_pair = np.outer(D[:, column], z) + np.outer(z, D[:, column])
        linear_powers = source._powers(linear_pair)
        for label in BASIS_LABELS:
            linear_images_by_label[label][:, :, column] = source.project(
                label, linear_pair, linear_powers
            )

    rows: list[tuple[complex, np.ndarray, np.ndarray]] = []
    for label in BASIS_LABELS:
        projected = source.project(label, pair, powers)
        linear_images = linear_images_by_label[label]
        flattened = linear_images.reshape(-1, chart.SIGMA_REAL_DIM)
        value = float(np.vdot(projected, projected).real)
        gradient = 2.0 * np.real(
            np.einsum("ab,abi->i", np.conjugate(projected), linear_images, optimize=True)
        )
        first_term = 2.0 * np.real(flattened.conj().T @ flattened)
        second_term = 4.0 * np.real(D.T @ np.conjugate(projected) @ D)
        hessian = first_term + second_term
        rows.append(
            (
                complex(value),
                np.asarray(gradient, dtype=complex),
                np.asarray(0.5 * (hessian + hessian.T), dtype=complex),
            )
        )
    return tuple(rows)


def all_base_derivatives(
    q_sigma: np.ndarray,
) -> tuple[tuple[complex, np.ndarray, np.ndarray], ...]:
    block = np.asarray(q_sigma, dtype=float).reshape(chart.SIGMA_REAL_DIM)
    return _base_blocks_cached(tuple(float(value) for value in block))


def base_derivative(
    q: np.ndarray, basis_index: int
) -> tuple[complex, np.ndarray, np.ndarray]:
    coordinates = np.asarray(q, dtype=float).reshape(chart.TOTAL_DIM)
    index = int(basis_index)
    if not 0 <= index < len(BASIS_LABELS):
        raise KeyError(f"unknown Sigma self-quartic basis index {basis_index}")
    value, sigma_gradient, sigma_hessian = all_base_derivatives(
        coordinates[chart.SIGMA_SLICE]
    )[index]
    gradient = np.zeros(chart.TOTAL_DIM, dtype=complex)
    hessian = np.zeros((chart.TOTAL_DIM, chart.TOTAL_DIM), dtype=complex)
    gradient[chart.SIGMA_SLICE] = sigma_gradient
    hessian[chart.SIGMA_SLICE, chart.SIGMA_SLICE] = sigma_hessian
    return value, gradient, 0.5 * (hessian + hessian.T)


def _orbit_rows() -> tuple[tuple[int, dict[str, Any], tuple[int, ...], dict[str, Any]], ...]:
    rows: list[tuple[int, dict[str, Any], tuple[int, ...], dict[str, Any]]] = []
    for orbit_index, orbit in enumerate(
        potential.census.orbits(potential.census.census(False))
    ):
        counts_tuple = tuple(int(item) for item in orbit["orbit_key"])
        counts = dict(zip(potential.FIELD_ORDER, counts_tuple, strict=True))
        base_key = tuple(counts[name] for name in potential.NON_SINGLET_ORDER)
        base = ledger.BASE_FAMILIES[base_key]
        rows.append((orbit_index, orbit, counts_tuple, base))
    return tuple(rows)


def selected_directions(state: potential.FieldState) -> tuple[potential.Direction, ...]:
    """Construct only this family's directions without evaluating all 64 invariants."""
    value = state.validated()
    q = chart.pack(value)
    z = chart._unpack_complex_interleaved(q[chart.SIGMA_SLICE])
    source_values = source.quartics(z)
    directions: list[potential.Direction] = []
    for orbit_index, orbit, counts_tuple, base in _orbit_rows():
        if base["id"] != BASE_FAMILY:
            continue
        counts = dict(zip(potential.FIELD_ORDER, counts_tuple, strict=True))
        dressing = potential._dressing(value, counts)
        for basis_index, label in enumerate(base["basis"]):
            directions.append(
                potential.Direction(
                    direction_id=potential._direction_id(
                        orbit_index, basis_index, base["id"]
                    ),
                    orbit_index=orbit_index,
                    basis_index=basis_index,
                    representative=orbit["representative"],
                    members=tuple(orbit["members"]),
                    self_conjugate=bool(orbit["self_conjugate"]),
                    degree=int(orbit["degree"]),
                    base_key=tuple(
                        counts[name] for name in potential.NON_SINGLET_ORDER
                    ),
                    base_family=base["id"],
                    basis_label=str(label),
                    source_modules=tuple(base["sources"]),
                    normalization=str(base["normalization"]),
                    counts=counts_tuple,
                    value=complex(source_values[str(label)] * dressing),
                )
            )
    return tuple(directions)


def live_parameter_ids_from_g1() -> set[str]:
    output: set[str] = set()
    for orbit_index, orbit, _counts_tuple, base in _orbit_rows():
        for basis_index, _label in enumerate(base["basis"]):
            direction_id = potential._direction_id(
                orbit_index, basis_index, base["id"]
            )
            if bool(orbit["self_conjugate"]):
                output.add(f"lambda::{direction_id}")
            else:
                output.add(f"re::{direction_id}")
                output.add(f"im::{direction_id}")
    return output


def direction_derivative(
    q: np.ndarray, direction: potential.Direction
) -> quadratic.DirectionDerivative:
    if direction.base_family != BASE_FAMILY:
        raise KeyError(f"direction {direction.direction_id} is not {BASE_FAMILY}")
    counts = dict(zip(potential.FIELD_ORDER, direction.counts, strict=True))
    base_value, base_gradient, base_hessian = base_derivative(q, direction.basis_index)
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
    return sum(
        len(base["basis"])
        for _orbit_index, _orbit, _counts_tuple, base in _orbit_rows()
        if base["id"] == BASE_FAMILY
    )


def source_normalization_audit(state: potential.FieldState) -> dict[str, Any]:
    q = chart.pack(state)
    z = chart._unpack_complex_interleaved(q[chart.SIGMA_SLICE])
    expected = source.quartics(z)
    observed: dict[str, complex] = {}
    residuals: dict[str, float] = {}
    for index, label in enumerate(BASIS_LABELS):
        value, _, _ = base_derivative(q, index)
        observed[label] = value
        residuals[label] = float(abs(value - expected[label]))
    return {
        "observed": observed,
        "source": expected,
        "residuals": residuals,
        "maximum_residual": max(residuals.values()),
    }


def targeted_directional_audit(
    q: np.ndarray,
    directions: tuple[potential.Direction, ...],
    parameters: tuple[quadratic.ParameterDerivative, ...],
    coefficients: dict[str, float],
) -> dict[str, float]:
    """Independent five-point check using only the authoritative Sigma source."""
    assembled = quadratic.assemble(parameters, coefficients)
    by_direction = {row.direction_id: row for row in directions}
    weights: dict[str, float] = {}
    for parameter in parameters:
        direction = by_direction[parameter.direction_id]
        if not direction.self_conjugate or parameter.component != "real":
            raise AssertionError("Sigma self-projectors must be self-conjugate")
        weights[direction.basis_label] = float(coefficients[parameter.parameter_id])

    rng = np.random.default_rng(3305)
    direction = rng.normal(size=chart.TOTAL_DIM)
    direction /= np.linalg.norm(direction)
    step = 0.02

    def evaluate(offset: float) -> float:
        shifted = np.asarray(q, dtype=float) + offset * direction
        z = chart._unpack_complex_interleaved(shifted[chart.SIGMA_SLICE])
        values = source.quartics(z)
        return float(sum(weights[label] * values[label] for label in weights))

    f_m2 = evaluate(-2.0 * step)
    f_m1 = evaluate(-step)
    f_0 = evaluate(0.0)
    f_p1 = evaluate(step)
    f_p2 = evaluate(2.0 * step)
    numerical_first = (f_m2 - 8.0 * f_m1 + 8.0 * f_p1 - f_p2) / (12.0 * step)
    numerical_second = (
        -f_p2 + 16.0 * f_p1 - 30.0 * f_0 + 16.0 * f_m1 - f_m2
    ) / (12.0 * step**2)
    analytic_first = float(np.dot(assembled["gradient"], direction))
    analytic_second = float(direction @ assembled["hessian"] @ direction)
    return {
        "step": step,
        "value_residual": float(abs(f_0 - assembled["value"])),
        "analytic_first": analytic_first,
        "numerical_first": float(numerical_first),
        "first_residual": float(abs(analytic_first - numerical_first)),
        "analytic_second": analytic_second,
        "numerical_second": float(numerical_second),
        "second_residual": float(abs(analytic_second - numerical_second)),
    }


def base_support_audit(q: np.ndarray) -> dict[str, Any]:
    active = np.zeros(chart.TOTAL_DIM, dtype=bool)
    active[chart.SIGMA_SLICE] = True
    rows: dict[str, Any] = {}
    for index, label in enumerate(BASIS_LABELS):
        _, gradient, hessian = base_derivative(q, index)
        inactive = ~active
        rows[label] = {
            "inactive_gradient_residual": float(np.max(np.abs(gradient[inactive]), initial=0.0)),
            "inactive_Hessian_residual": float(max(
                np.max(np.abs(hessian[inactive, :]), initial=0.0),
                np.max(np.abs(hessian[:, inactive]), initial=0.0),
            )),
        }
    return rows


@lru_cache(maxsize=1)
def build_report() -> dict[str, Any]:
    state = potential.deterministic_state(3304)
    q = chart.pack(state)
    directions = selected_directions(state)
    analytic = tuple(direction_derivative(q, row) for row in directions)
    parameters = quadratic.parameter_derivatives(analytic)
    coefficients = quadratic.deterministic_coefficients(parameters)
    directional = targeted_directional_audit(q, directions, parameters, coefficients)
    expected_rows = {row.direction_id: row for row in directions}
    value_residuals = {
        row.direction_id: float(abs(row.value - expected_rows[row.direction_id].value))
        for row in analytic
    }
    expected_count = expected_direction_count()
    basis_indices = sorted({row.basis_index for row in directions})
    basis_labels = sorted({row.basis_label for row in directions})
    normalization = source_normalization_audit(state)
    support = base_support_audit(q)
    support_residual = max(max(row.values()) for row in support.values())
    hessian_asymmetry = max(float(np.max(np.abs(row.hessian - row.hessian.T))) for row in analytic)
    self_imaginary = max([
        max(abs(row.value.imag), float(np.max(np.abs(row.gradient.imag))), float(np.max(np.abs(row.hessian.imag))))
        for row in analytic if row.self_conjugate
    ] or [0.0])
    live_parameter_ids = live_parameter_ids_from_g1()
    parameter_ids = {row.parameter_id for row in parameters}

    checks = {
        "authoritative_family_id_exists": BASE_FAMILY in {row["id"] for row in ledger.BASE_FAMILIES.values()},
        "expected_G1_direction_count_is_nonzero": expected_count > 0,
        "observed_direction_count_is_nonzero": len(analytic) > 0,
        "every_expected_direction_differentiated": len(analytic) == expected_count,
        "all_four_basis_indices_present": basis_indices == [0, 1, 2, 3],
        "all_four_basis_labels_present": basis_labels == sorted(BASIS_LABELS),
        "all_values_match_authoritative_source": normalization["maximum_residual"] < 1.0e-9,
        "all_values_match_live_evaluator": max(value_residuals.values()) < 1.0e-9,
        "all_parameter_ids_belong_to_live_schema": parameter_ids.issubset(live_parameter_ids) and len(parameter_ids) == len(parameters) and len(parameters) > 0,
        "base_derivatives_supported_only_on_Sigma": support_residual < 1.0e-12,
        "all_dense_Hessians_symmetric": hessian_asymmetry < 1.0e-8,
        "self_conjugate_derivatives_real": self_imaginary < 1.0e-8,
        "five_point_value_reconstruction": directional["value_residual"] < 1.0e-7,
        "five_point_first_derivative_reconstruction": directional["first_residual"] < 5.0e-6,
        "five_point_second_derivative_reconstruction": directional["second_residual"] < 5.0e-5,
        "remaining_4_quartic_families_not_claimed": True,
        "G2_not_closed": True,
        "whole_model_not_validated": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return _jsonable({
        "status": "G2_EXACT_SIGMA_SELF_QUARTIC_DERIVATIVES_CLOSED" if not failures else "G2_SIGMA_SELF_QUARTIC_DERIVATIVES_FAILED",
        "overall_state": "PARTIAL" if not failures else "EXECUTION_FAIL",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "coverage": {
            "base_family": BASE_FAMILY,
            "base_family_count_closed_here": 1,
            "cumulative_base_family_count_with_parents": 14,
            "base_family_count_total": len(ledger.BASE_FAMILIES),
            "remaining_base_families": 4,
            "expected_direction_count": expected_count,
            "observed_direction_count": len(analytic),
            "parameter_count_closed_here": len(parameters),
            "basis_indices": basis_indices,
            "basis_labels": basis_labels,
            "real_field_dimension": chart.TOTAL_DIM,
            "Hessian_shape": [chart.TOTAL_DIM, chart.TOTAL_DIM],
        },
        "source_normalization_audit": normalization,
        "maximum_direction_value_residual": max(value_residuals.values()),
        "maximum_Hessian_asymmetry": hessian_asymmetry,
        "maximum_self_conjugate_imaginary_residual": self_imaginary,
        "directional_reconstruction": directional,
        "flags": {
            "authoritative_126bar_self_projector_adapter_closed": not failures,
            "all_four_projector_derivatives_exact": not failures,
            "cumulative_fourteen_of_eighteen_base_adapters_closed": not failures,
            "all_64_direction_gradients_complete": False,
            "all_64_direction_Hessians_complete": False,
            "G2_closed": False,
            "whole_model_validated": False,
            "empirical_discovery": False,
        },
    })


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Exact 126bar self-projector derivatives — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        "All four arbitrary-field projector values, 486-real gradients, and "
        "486x486 Hessians are assembled analytically. G2 remains open.\n",
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
