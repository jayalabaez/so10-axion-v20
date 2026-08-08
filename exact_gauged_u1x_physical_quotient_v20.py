#!/usr/bin/env python3
"""Exact physical-symmetry quotient certificate for the gauged-U(1)_X vacuum.

The live G3 implementation constructs the SO(10), U(1)_X, and accidental-PQ
orbit tangents in the canonical 486-real chart and diagnoses their rank with a
floating-point SVD.  This module supplies the missing exact certificate.

At the canonical hierarchy point the nonzero VEV *shapes* are

  Phi_210 = e_6789,
  H_10 = h e_6,
  Sigma_126bar = r Delta_R,
  S = r,
  Phi17 = x,

where ``h``, ``r``, and ``x`` are nonzero.  Before normalization,

  Delta_R ~ (e_0+i e_1)(e_2+i e_3)(e_4+i e_5)(e_67+e_89).

In the canonical interleaved chart the actual 486x47 tangent matrix is
``D M``.  ``M`` is the integer matrix built below and ``D`` is diagonal with
nonzero block factors

  (1, sqrt(2) h, r/2, sqrt(2) r, sqrt(2) x).

Thus ``rank(D M) = rank(M)`` without making any assumption about the relative
hierarchy scales.  Exact integer elimination produces both halves of a rank
certificate: a nonzero 38x38 minor and nine independent integer right-null
vectors for the 47 generators.  Consequently the gauged orbit has rank 37 and
its physical quotient has dimension 449, including the physical axion.  The
independent global-PQ tangent raises the full symmetry-orbit rank to 38, so the
massive/transverse quotient used for Hessian positivity has dimension
486-38=448.  Global PQ is not treated as a gauged, eaten direction.

The certificate is tied back to the live compiler by an explicit regression:
the live SO(10) orbit columns, U(1)_X tangent, and independently constructed PQ
tangent agree with ``D M`` at the actual canonical hierarchy state.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

import numpy as np

import gauged_u1x_g2_derivative_audit_v20 as g2_audit
import live_g2_canonical_486_field_chart_v20 as chart

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_GAUGED_U1X_PHYSICAL_QUOTIENT_V20.json"
OUT_MD = ROOT / "EXACT_GAUGED_U1X_PHYSICAL_QUOTIENT_V20.md"

N = 10
SO10_GENERATOR_COUNT = 45
FULL_GENERATOR_COUNT = 47
EXPECTED_SO10_RANK = 36
EXPECTED_GAUGE_RANK = 37
EXPECTED_FULL_RANK = 38
EXPECTED_NULLITY = 9
EXPECTED_GAUGE_QUOTIENT_DIMENSION = 449
EXPECTED_QUOTIENT_DIMENSION = 448

GaussianInteger = tuple[int, int]
ExactForm = dict[tuple[int, ...], GaussianInteger]

ZERO: GaussianInteger = (0, 0)
ONE: GaussianInteger = (1, 0)
I: GaussianInteger = (0, 1)

U1X_CHARGES = {
    "H10": -2,
    "Sigma126bar": -2,
    "S": 4,
    "Phi17": 17,
}
PQ_CHARGES = {
    "H10": -2,
    "Sigma126bar": -2,
    "S": 4,
    "Phi17": 0,
}


def _g_add(left: GaussianInteger, right: GaussianInteger) -> GaussianInteger:
    return (left[0] + right[0], left[1] + right[1])


def _g_neg(value: GaussianInteger) -> GaussianInteger:
    return (-value[0], -value[1])


def _g_mul(left: GaussianInteger, right: GaussianInteger) -> GaussianInteger:
    return (
        left[0] * right[0] - left[1] * right[1],
        left[0] * right[1] + left[1] * right[0],
    )


def _permutation_sign(sequence: tuple[int, ...]) -> int:
    inversions = sum(
        sequence[first] > sequence[second]
        for first in range(len(sequence))
        for second in range(first + 1, len(sequence))
    )
    return -1 if inversions % 2 else 1


def _one_form(index: int, coefficient: GaussianInteger = ONE) -> ExactForm:
    return {(index,): coefficient}


def _add_forms(*forms: ExactForm) -> ExactForm:
    output: ExactForm = {}
    for form in forms:
        for indices, coefficient in form.items():
            output[indices] = _g_add(output.get(indices, ZERO), coefficient)
    return {indices: value for indices, value in output.items() if value != ZERO}


def _scale_form(form: ExactForm, coefficient: GaussianInteger) -> ExactForm:
    return {
        indices: value
        for indices, source in form.items()
        if (value := _g_mul(coefficient, source)) != ZERO
    }


def _wedge(left: ExactForm, right: ExactForm) -> ExactForm:
    output: ExactForm = {}
    for left_indices, left_value in left.items():
        for right_indices, right_value in right.items():
            if set(left_indices).intersection(right_indices):
                continue
            sequence = left_indices + right_indices
            target = tuple(sorted(sequence))
            coefficient = _g_mul(left_value, right_value)
            if _permutation_sign(sequence) < 0:
                coefficient = _g_neg(coefficient)
            output[target] = _g_add(output.get(target, ZERO), coefficient)
    return {indices: value for indices, value in output.items() if value != ZERO}


def _interior(form: ExactForm, index: int) -> ExactForm:
    output: ExactForm = {}
    for indices, coefficient in form.items():
        if index not in indices:
            continue
        position = indices.index(index)
        target = indices[:position] + indices[position + 1 :]
        value = coefficient if position % 2 == 0 else _g_neg(coefficient)
        output[target] = _g_add(output.get(target, ZERO), value)
    return {indices: value for indices, value in output.items() if value != ZERO}


def _generator_action(form: ExactForm, first: int, second: int) -> ExactForm:
    if not 0 <= first < second < N:
        raise ValueError("generator requires 0 <= first < second < 10")
    return _add_forms(
        _wedge(_one_form(first), _interior(form, second)),
        _scale_form(
            _wedge(_one_form(second), _interior(form, first)), (-1, 0)
        ),
    )


@lru_cache(maxsize=1)
def _sigma_representatives() -> tuple[tuple[int, ...], ...]:
    representatives: list[tuple[int, ...]] = []
    seen: set[tuple[int, ...]] = set()
    universe = set(range(N))
    for initial in itertools.combinations(range(N), 5):
        if initial in seen:
            continue
        complement = tuple(sorted(universe.difference(initial)))
        seen.add(initial)
        seen.add(complement)
        representatives.append(min(initial, complement))
    if len(representatives) != chart.SIGMA_COMPLEX_DIM:
        raise AssertionError("exact Sigma representative count drifted")
    return tuple(representatives)


@lru_cache(maxsize=1)
def _canonical_exact_shapes() -> tuple[ExactForm, tuple[GaussianInteger, ...], ExactForm]:
    phi = {(6, 7, 8, 9): ONE}
    h = tuple(ONE if index == 6 else ZERO for index in range(N))

    z1 = _add_forms(_one_form(0), _one_form(1, I))
    z2 = _add_forms(_one_form(2), _one_form(3, I))
    z3 = _add_forms(_one_form(4), _one_form(5, I))
    omega3 = _wedge(_wedge(z1, z2), z3)
    j_right = _add_forms(
        _wedge(_one_form(6), _one_form(7)),
        _wedge(_one_form(8), _one_form(9)),
    )
    sigma_raw = _wedge(omega3, j_right)
    if len(sigma_raw) != 16:
        raise AssertionError("raw Delta_R support drifted")
    return phi, h, sigma_raw


def generator_labels(*, include_phases: bool = True) -> tuple[str, ...]:
    labels = tuple(
        f"SO10:T[{first},{second}]"
        for first, second in itertools.combinations(range(N), 2)
    )
    if include_phases:
        labels += ("U1X", "PQ")
    return labels


def _append_interleaved(output: list[int], values: Iterable[GaussianInteger]) -> None:
    for real, imaginary in values:
        output.extend((real, imaginary))


def _so10_column(first: int, second: int) -> tuple[int, ...]:
    phi, h, sigma_raw = _canonical_exact_shapes()
    delta_phi = _generator_action(phi, first, second)
    delta_h = [ZERO] * N
    delta_h[first] = h[second]
    delta_h[second] = _g_neg(h[first])
    delta_sigma = _generator_action(sigma_raw, first, second)

    output: list[int] = []
    for indices in chart.phi_indices():
        real, imaginary = delta_phi.get(indices, ZERO)
        if imaginary != 0:
            raise AssertionError("real Phi tangent acquired an imaginary part")
        output.append(real)
    _append_interleaved(output, delta_h)
    _append_interleaved(
        output,
        (delta_sigma.get(indices, ZERO) for indices in _sigma_representatives()),
    )
    output.extend((0, 0, 0, 0))
    if len(output) != chart.TOTAL_DIM:
        raise AssertionError("exact SO(10) tangent dimension drifted")
    return tuple(output)


def _phase_column(charges: dict[str, int]) -> tuple[int, ...]:
    _phi, h, sigma_raw = _canonical_exact_shapes()
    output = [0] * chart.PHI_DIM
    _append_interleaved(
        output,
        (_g_mul((0, charges["H10"]), coefficient) for coefficient in h),
    )
    _append_interleaved(
        output,
        (
            _g_mul(
                (0, charges["Sigma126bar"]),
                sigma_raw.get(indices, ZERO),
            )
            for indices in _sigma_representatives()
        ),
    )
    _append_interleaved(output, ((0, charges["S"]),))
    _append_interleaved(output, ((0, charges["Phi17"]),))
    if len(output) != chart.TOTAL_DIM:
        raise AssertionError("exact phase tangent dimension drifted")
    return tuple(output)


@lru_cache(maxsize=2)
def exact_integer_tangent_matrix(
    *, include_phases: bool = True
) -> tuple[tuple[int, ...], ...]:
    """Return the exact tangent matrix in canonical 486-row ordering.

    Columns follow :func:`generator_labels`.  Every entry is a Python integer;
    no floating-point rank decision enters this construction.
    """

    columns = [
        _so10_column(first, second)
        for first, second in itertools.combinations(range(N), 2)
    ]
    if include_phases:
        columns.extend((_phase_column(U1X_CHARGES), _phase_column(PQ_CHARGES)))
    return tuple(
        tuple(column[row] for column in columns)
        for row in range(chart.TOTAL_DIM)
    )


def _row_echelon_metadata(
    matrix: tuple[tuple[int, ...], ...]
) -> tuple[int, tuple[int, ...], tuple[int, ...]]:
    if not matrix:
        return 0, (), ()
    work = [[Fraction(value) for value in row] for row in matrix]
    origins = list(range(len(work)))
    column_count = len(work[0])
    pivot_columns: list[int] = []
    pivot_origins: list[int] = []
    pivot_row = 0
    for column in range(column_count):
        selected = next(
            (row for row in range(pivot_row, len(work)) if work[row][column]),
            None,
        )
        if selected is None:
            continue
        work[pivot_row], work[selected] = work[selected], work[pivot_row]
        origins[pivot_row], origins[selected] = origins[selected], origins[pivot_row]
        pivot = work[pivot_row][column]
        work[pivot_row] = [value / pivot for value in work[pivot_row]]
        for row in range(pivot_row + 1, len(work)):
            factor = work[row][column]
            if factor:
                work[row] = [
                    value - factor * source
                    for value, source in zip(work[row], work[pivot_row])
                ]
        pivot_columns.append(column)
        pivot_origins.append(origins[pivot_row])
        pivot_row += 1
        if pivot_row == len(work):
            break
    return pivot_row, tuple(pivot_origins), tuple(pivot_columns)


def _rref(
    rows: Iterable[Iterable[int]], column_count: int
) -> tuple[list[list[Fraction]], tuple[int, ...]]:
    work = [[Fraction(value) for value in row] for row in rows]
    pivot_columns: list[int] = []
    pivot_row = 0
    for column in range(column_count):
        selected = next(
            (row for row in range(pivot_row, len(work)) if work[row][column]),
            None,
        )
        if selected is None:
            continue
        work[pivot_row], work[selected] = work[selected], work[pivot_row]
        pivot = work[pivot_row][column]
        work[pivot_row] = [value / pivot for value in work[pivot_row]]
        for row in range(len(work)):
            if row == pivot_row:
                continue
            factor = work[row][column]
            if factor:
                work[row] = [
                    value - factor * source
                    for value, source in zip(work[row], work[pivot_row])
                ]
        pivot_columns.append(column)
        pivot_row += 1
        if pivot_row == len(work):
            break
    return work[:pivot_row], tuple(pivot_columns)


def _primitive_integer_vector(values: Iterable[Fraction]) -> tuple[int, ...]:
    fractions = tuple(values)
    denominator_lcm = math.lcm(*(value.denominator for value in fractions))
    integers = [
        value.numerator * (denominator_lcm // value.denominator)
        for value in fractions
    ]
    common = math.gcd(*(abs(value) for value in integers))
    if common:
        integers = [value // common for value in integers]
    first = next((value for value in integers if value), 0)
    if first < 0:
        integers = [-value for value in integers]
    return tuple(integers)


def _right_nullspace(
    matrix: tuple[tuple[int, ...], ...],
    independent_rows: tuple[int, ...],
) -> tuple[tuple[int, ...], ...]:
    column_count = len(matrix[0])
    reduced, pivots = _rref((matrix[row] for row in independent_rows), column_count)
    free_columns = tuple(column for column in range(column_count) if column not in pivots)
    vectors: list[tuple[int, ...]] = []
    for free in free_columns:
        vector = [Fraction(0) for _ in range(column_count)]
        vector[free] = Fraction(1)
        for row, pivot in enumerate(pivots):
            vector[pivot] = -reduced[row][free]
        vectors.append(_primitive_integer_vector(vector))
    return tuple(vectors)


def _bareiss_determinant(matrix: list[list[int]]) -> int:
    size = len(matrix)
    if size == 0:
        return 1
    work = [row[:] for row in matrix]
    sign = 1
    previous = 1
    for column in range(size - 1):
        selected = next(
            (row for row in range(column, size) if work[row][column] != 0),
            None,
        )
        if selected is None:
            return 0
        if selected != column:
            work[column], work[selected] = work[selected], work[column]
            sign *= -1
        pivot = work[column][column]
        for row in range(column + 1, size):
            for target in range(column + 1, size):
                numerator = (
                    work[row][target] * pivot
                    - work[row][column] * work[column][target]
                )
                if numerator % previous:
                    raise ArithmeticError("Bareiss exact division failed")
                work[row][target] = numerator // previous
            work[row][column] = 0
        previous = pivot
    return sign * work[-1][-1]


def _matrix_vector_product_is_zero(
    matrix: tuple[tuple[int, ...], ...], vector: tuple[int, ...]
) -> bool:
    return all(
        sum(value * coefficient for value, coefficient in zip(row, vector)) == 0
        for row in matrix
    )


def _null_vector_report(
    vectors: tuple[tuple[int, ...], ...], labels: tuple[str, ...]
) -> list[dict[str, Any]]:
    return [
        {
            "nonzero_coefficients": {
                label: coefficient
                for label, coefficient in zip(labels, vector)
                if coefficient
            },
            "primitive_integer_vector": list(vector),
        }
        for vector in vectors
    ]


def _phase_tangent(state: Any, charges: dict[str, int]) -> np.ndarray:
    tangent = np.zeros(chart.TOTAL_DIM, dtype=float)

    def block(values: Iterable[complex], charge: int) -> np.ndarray:
        varied = 1j * charge * np.asarray(tuple(values), dtype=complex).reshape(-1)
        output = np.empty(2 * varied.size, dtype=float)
        output[0::2] = chart.SQRT2 * varied.real
        output[1::2] = chart.SQRT2 * varied.imag
        return output

    tangent[chart.H_SLICE] = block(state.h, charges["H10"])
    tangent[chart.SIGMA_SLICE] = block(
        chart.sigma_coordinates(state.sigma), charges["Sigma126bar"]
    )
    tangent[chart.S_SLICE] = block((state.s,), charges["S"])
    tangent[chart.X_SLICE] = block((state.x,), charges["Phi17"])
    return tangent


def live_compiler_binding_audit() -> dict[str, Any]:
    """Compare ``D M`` directly with the live 486-coordinate tangents."""

    state = g2_audit.physical_hierarchy_state()
    exact = np.asarray(exact_integer_tangent_matrix(), dtype=float)
    actual = np.column_stack(
        (
            chart.gauge_orbit_matrix(state),
            g2_audit.u1x_tangent(state),
            _phase_tangent(state, PQ_CHARGES),
        )
    )

    h = float(np.real(state.h[6]))
    r = float(np.real(state.s))
    x = float(np.real(state.x))
    scales = np.empty(chart.TOTAL_DIM, dtype=float)
    scales[chart.PHI_SLICE] = 1.0
    scales[chart.H_SLICE] = chart.SQRT2 * h
    scales[chart.SIGMA_SLICE] = r / 2.0
    scales[chart.S_SLICE] = chart.SQRT2 * r
    scales[chart.X_SLICE] = chart.SQRT2 * x
    if not np.all(np.isfinite(scales)) or np.any(scales == 0.0):
        raise ArithmeticError("canonical hierarchy row scaling is not invertible")

    expected = scales[:, None] * exact
    residual = actual - expected
    unscaled_residual = actual / scales[:, None] - exact
    maximum_absolute_residual = float(np.max(np.abs(residual), initial=0.0))
    maximum_unscaled_residual = float(
        np.max(np.abs(unscaled_residual), initial=0.0)
    )
    relative_residual = maximum_absolute_residual / max(
        float(np.max(np.abs(actual), initial=0.0)), np.finfo(float).tiny
    )
    return {
        "live_matrix_shape": list(actual.shape),
        "exact_matrix_shape": list(exact.shape),
        "generator_order": list(generator_labels()),
        "row_block_scales": {
            "Phi210": "1",
            "H10": "sqrt(2) * h",
            "Sigma126bar": "r / 2",
            "S": "sqrt(2) * r",
            "Phi17": "sqrt(2) * x",
        },
        "all_block_scales_nonzero": bool(np.all(scales != 0.0)),
        "maximum_absolute_residual": maximum_absolute_residual,
        "maximum_unscaled_residual": maximum_unscaled_residual,
        "maximum_relative_residual": relative_residual,
        "compiler_binding_passes": maximum_unscaled_residual < 1.0e-12,
        "live_sources": [
            "live_g2_canonical_486_field_chart_v20.gauge_orbit_matrix",
            "gauged_u1x_g2_derivative_audit_v20.u1x_tangent",
            "gauged_u1x_g2_derivative_audit_v20.physical_hierarchy_state",
        ],
    }


@lru_cache(maxsize=1)
def exact_quotient_certificate() -> dict[str, Any]:
    so10_matrix = exact_integer_tangent_matrix(include_phases=False)
    full_matrix = exact_integer_tangent_matrix(include_phases=True)
    gauge_matrix = tuple(row[:-1] for row in full_matrix)
    so10_labels = generator_labels(include_phases=False)
    full_labels = generator_labels(include_phases=True)
    gauge_labels = full_labels[:-1]

    so10_rank, so10_rows, so10_columns = _row_echelon_metadata(so10_matrix)
    gauge_rank, gauge_rows, gauge_columns = _row_echelon_metadata(gauge_matrix)
    full_rank, full_rows, full_columns = _row_echelon_metadata(full_matrix)
    so10_minor = [
        [so10_matrix[row][column] for column in so10_columns]
        for row in so10_rows
    ]
    full_minor = [
        [full_matrix[row][column] for column in full_columns]
        for row in full_rows
    ]
    gauge_minor = [
        [gauge_matrix[row][column] for column in gauge_columns]
        for row in gauge_rows
    ]
    so10_determinant = _bareiss_determinant(so10_minor)
    gauge_determinant = _bareiss_determinant(gauge_minor)
    full_determinant = _bareiss_determinant(full_minor)

    so10_null = _right_nullspace(so10_matrix, so10_rows)
    gauge_null = _right_nullspace(gauge_matrix, gauge_rows)
    full_null = _right_nullspace(full_matrix, full_rows)
    so10_null_rank, _rows, _columns = _row_echelon_metadata(so10_null)
    gauge_null_rank, _rows, _columns = _row_echelon_metadata(gauge_null)
    full_null_rank, _rows, _columns = _row_echelon_metadata(full_null)
    all_full_null_residuals_zero = all(
        _matrix_vector_product_is_zero(full_matrix, vector) for vector in full_null
    )
    phase_coefficients_vanish = all(vector[-2:] == (0, 0) for vector in full_null)

    s_imaginary_row = chart.S_SLICE.start + 1
    x_imaginary_row = chart.X_SLICE.start + 1
    phase_minor = (
        (full_matrix[s_imaginary_row][-2], full_matrix[s_imaginary_row][-1]),
        (full_matrix[x_imaginary_row][-2], full_matrix[x_imaginary_row][-1]),
    )
    phase_determinant = (
        phase_minor[0][0] * phase_minor[1][1]
        - phase_minor[0][1] * phase_minor[1][0]
    )

    checks = {
        "exact_matrix_shape_is_486x47": (
            len(full_matrix) == chart.TOTAL_DIM
            and len(full_matrix[0]) == FULL_GENERATOR_COUNT
        ),
        "all_tangent_entries_are_integers": all(
            isinstance(value, int) for row in full_matrix for value in row
        ),
        "SO10_nonzero_36x36_minor": (
            so10_rank == EXPECTED_SO10_RANK and so10_determinant != 0
        ),
        "SO10_has_nine_exact_stabilizer_vectors": (
            len(so10_null) == EXPECTED_NULLITY
            and so10_null_rank == EXPECTED_NULLITY
            and all(
                _matrix_vector_product_is_zero(so10_matrix, vector)
                for vector in so10_null
            )
        ),
        "U1X_and_PQ_phase_minor_is_nonzero": phase_determinant == -68,
        "gauge_nonzero_37x37_minor": (
            gauge_rank == EXPECTED_GAUGE_RANK and gauge_determinant != 0
        ),
        "gauge_has_nine_exact_stabilizer_vectors": (
            len(gauge_null) == EXPECTED_NULLITY
            and gauge_null_rank == EXPECTED_NULLITY
            and all(
                _matrix_vector_product_is_zero(gauge_matrix, vector)
                for vector in gauge_null
            )
        ),
        "gauge_quotient_dimension_is_449": (
            chart.TOTAL_DIM - gauge_rank == EXPECTED_GAUGE_QUOTIENT_DIMENSION
        ),
        "full_nonzero_38x38_minor": (
            full_rank == EXPECTED_FULL_RANK and full_determinant != 0
        ),
        "full_has_nine_independent_exact_null_vectors": (
            len(full_null) == EXPECTED_NULLITY
            and full_null_rank == EXPECTED_NULLITY
            and all_full_null_residuals_zero
        ),
        "full_nullspace_contains_no_U1X_or_PQ_coefficient": (
            phase_coefficients_vanish
        ),
        "physical_quotient_dimension_is_448": (
            chart.TOTAL_DIM - full_rank == EXPECTED_QUOTIENT_DIMENSION
        ),
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "arithmetic_domain": "Z with exact Gaussian-integer tensor construction",
        "canonical_chart_dimension": chart.TOTAL_DIM,
        "generator_count": FULL_GENERATOR_COUNT,
        "generator_order": list(full_labels),
        "exact_row_scaling_identity": (
            "M_live = diag(1, sqrt(2)h, r/2, sqrt(2)r, sqrt(2)x) M_Z"
        ),
        "nonzero_scale_assumptions": ["h != 0", "r != 0", "x != 0"],
        "SO10": {
            "rank": so10_rank,
            "stabilizer_dimension": SO10_GENERATOR_COUNT - so10_rank,
            "minor": {
                "shape": [len(so10_rows), len(so10_columns)],
                "row_indices": list(so10_rows),
                "row_coordinate_names": [
                    chart.coordinate_names()[row] for row in so10_rows
                ],
                "column_indices": list(so10_columns),
                "column_generator_labels": [
                    so10_labels[column] for column in so10_columns
                ],
                "determinant": str(so10_determinant),
                "determinant_nonzero": so10_determinant != 0,
            },
            "right_nullspace": _null_vector_report(so10_null, so10_labels),
            "null_vector_rank": so10_null_rank,
        },
        "U1X_PQ_independence": {
            "rows": ["S.y", "Phi17.y"],
            "columns": ["U1X", "PQ"],
            "minor": [list(row) for row in phase_minor],
            "determinant": phase_determinant,
        },
        "gauged_symmetry": {
            "generators": "SO(10) plus U(1)_X",
            "rank": gauge_rank,
            "right_nullity": len(gauge_labels) - gauge_rank,
            "minor": {
                "shape": [len(gauge_rows), len(gauge_columns)],
                "row_indices": list(gauge_rows),
                "row_coordinate_names": [
                    chart.coordinate_names()[row] for row in gauge_rows
                ],
                "column_indices": list(gauge_columns),
                "column_generator_labels": [
                    gauge_labels[column] for column in gauge_columns
                ],
                "determinant": str(gauge_determinant),
                "determinant_nonzero": gauge_determinant != 0,
            },
            "right_nullspace": _null_vector_report(gauge_null, gauge_labels),
            "null_vector_rank": gauge_null_rank,
            "gauge_quotient_dimension_including_axion": (
                chart.TOTAL_DIM - gauge_rank
            ),
        },
        "full_removed_symmetry": {
            "generators": "SO(10) plus U(1)_X plus independent global PQ",
            "rank": full_rank,
            "right_nullity": FULL_GENERATOR_COUNT - full_rank,
            "minor": {
                "shape": [len(full_rows), len(full_columns)],
                "row_indices": list(full_rows),
                "row_coordinate_names": [
                    chart.coordinate_names()[row] for row in full_rows
                ],
                "column_indices": list(full_columns),
                "column_generator_labels": [
                    full_labels[column] for column in full_columns
                ],
                "determinant": str(full_determinant),
                "determinant_nonzero": full_determinant != 0,
            },
            "right_nullspace": _null_vector_report(full_null, full_labels),
            "all_null_residuals_exactly_zero": all_full_null_residuals_zero,
            "null_vector_rank": full_null_rank,
        },
        "gauge_quotient_dimension_including_axion": chart.TOTAL_DIM - gauge_rank,
        "massive_transverse_quotient_dimension": chart.TOTAL_DIM - full_rank,
        "physical_quotient_dimension": chart.TOTAL_DIM - full_rank,
        "checks": checks,
        "failures": failures,
        "certified": not failures,
    }


def build_report() -> dict[str, Any]:
    certificate = exact_quotient_certificate()
    binding = live_compiler_binding_audit()
    certified = bool(certificate["certified"] and binding["compiler_binding_passes"])
    return {
        "status": "EXACT_PHYSICAL_QUOTIENT_CERTIFIED" if certified else "CERTIFICATE_FAILED",
        "model_contract_id": g2_audit.MODEL_CONTRACT_ID,
        "certified": certified,
        "exact_certificate": certificate,
        "live_compiler_binding": binding,
        "gauge_quotient_dimension_including_axion": certificate[
            "gauge_quotient_dimension_including_axion"
        ],
        "massive_transverse_quotient_dimension": certificate[
            "massive_transverse_quotient_dimension"
        ],
        "physical_quotient_dimension": certificate["physical_quotient_dimension"],
    }


def report_passes(report: dict[str, Any]) -> bool:
    """Require both the exact proof and its live-compiler binding."""

    return bool(
        report.get("certified") is True
        and report.get("exact_certificate", {}).get("certified") is True
        and report.get("live_compiler_binding", {}).get(
            "compiler_binding_passes"
        )
        is True
    )


def render_json(report: dict[str, Any]) -> str:
    """Render a byte-stable, newline-terminated JSON artifact."""

    return json.dumps(report, indent=2, sort_keys=True) + "\n"


def render_markdown(report: dict[str, Any]) -> str:
    """Render the proof-critical metadata without dumping full null vectors."""

    certificate = report["exact_certificate"]
    so10 = certificate["SO10"]
    gauge = certificate["gauged_symmetry"]
    full = certificate["full_removed_symmetry"]
    phase = certificate["U1X_PQ_independence"]
    binding = report["live_compiler_binding"]
    verdict = (
        "The exact tangent certificate and live compiler binding both pass."
        if report_passes(report)
        else "FAIL-CLOSED: the exact certificate or live compiler binding failed."
    )
    return "\n".join(
        [
            "# Exact gauged-U(1)_X physical-quotient certificate",
            "",
            f"**Status:** `{report['status']}`",
            "",
            f"**Certified:** `{str(report_passes(report)).lower()}`",
            "",
            f"- SO(10) orbit rank: `{so10['rank']}` "
            f"(minor det `{so10['minor']['determinant']}`, "
            f"stabilizer `{so10['stabilizer_dimension']}`);",
            f"- SO(10)+U(1)_X gauge rank: `{gauge['rank']}` "
            f"(minor det `{gauge['minor']['determinant']}`);",
            "- gauge quotient including the physical axion: "
            f"`{report['gauge_quotient_dimension_including_axion']}`;",
            f"- SO(10)+U(1)_X+global-PQ rank: `{full['rank']}` "
            f"(minor det `{full['minor']['determinant']}`);",
            "- massive/transverse Hessian quotient: "
            f"`{report['massive_transverse_quotient_dimension']}`;",
            f"- U(1)_X/PQ independence minor determinant: "
            f"`{phase['determinant']}`;",
            "- live compiler maximum unscaled residual: "
            f"`{binding['maximum_unscaled_residual']}`.",
            "",
            verdict,
            "",
        ]
    )


def write_report(
    report: dict[str, Any],
    *,
    out_json: Path = OUT_JSON,
    out_md: Path = OUT_MD,
) -> None:
    """Write deterministic JSON and concise Markdown certificate artifacts."""

    Path(out_json).write_text(render_json(report), encoding="utf-8")
    Path(out_md).write_text(render_markdown(report), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write",
        action="store_true",
        help="write the deterministic JSON and Markdown certificate artifacts",
    )
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        write_report(report)
    print(render_json(report), end="")
    return 0 if report_passes(report) else 1


if __name__ == "__main__":
    raise SystemExit(main())
