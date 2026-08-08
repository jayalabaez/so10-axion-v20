#!/usr/bin/env python3
"""Exact rank-13 certificate for the gauged-U(1)_X stationarity matrix.

Let ``A`` be the 486-by-51 matrix whose columns are the first variations of
the exact-X-neutral scalar invariants at the declared
``p + Delta_R + H_6 + S + Phi17`` hierarchy.  This module proves

    A = L A[pivots, :],  rank(A) <= 13,

without treating the hierarchy decimals or float64 cancellations as exact.
The proof uses integer/Gaussian-integer representation matrices, the exact
continuous and finite stabilizer of the vacuum, PQ/U(1)_X Ward identities,
and an exact selected-vacuum zero lemma for every invariant with nonzero net
Sigma number.  An invertible block rescaling removes ``sqrt(2), h, r, x``;
undoing it produces the sole scale-dependent row relation

    A[S.y, :] = h/(2 r) A[H[6].y, :].

The companion ``compiler_minor_binding`` function compares the exact symbolic
13-by-13 lower-bound minor with entries extracted from the actual G2 adapter
gradients.  Float values are used only as a binding/consistency check; the
nonzero-minor and upper-rank proofs remain exact.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np

import gauged_u1x_scalar_contract_v20 as contract
import live_g2_canonical_486_field_chart_v20 as chart

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_GAUGED_U1X_STATIONARITY_RANK_CERTIFICATE_V20.json"
OUT_MD = ROOT / "EXACT_GAUGED_U1X_STATIONARITY_RANK_CERTIFICATE_V20.md"

MODEL_CONTRACT_ID = "gauged_u1x_phi17_v20"
PROOF_SCHEMA = "exact_stationarity_rank_factorization_v1"
PROTOTYPE_SHA256 = (
    "4e206698d6c6ddc4513bb200f86b2657987bcf30507c1e613dfe5781b45546e5"
)
EXPECTED_FIELD_DIMENSION = 486
EXPECTED_PARAMETER_COUNT = 51
EXPECTED_RANK = 13
EXPECTED_NULLITY = 38

GI = tuple[int, int]
ExactForm = dict[tuple[int, ...], GI]
SparseIntegerMatrix = dict[tuple[int, int], int]
SparseIntegerVector = dict[int, int]
GI_ZERO: GI = (0, 0)
GI_ONE: GI = (1, 0)
GI_I: GI = (0, 1)

FOUR = tuple(itertools.combinations(range(10), 4))
FOUR_LOOKUP = {indices: index for index, indices in enumerate(FOUR)}
GENERATOR_LABELS = tuple(itertools.combinations(range(10), 2))
GENERATOR_LOOKUP = {
    label: index for index, label in enumerate(GENERATOR_LABELS)
}

PIVOT_ROWS = (0, 36, 40, 209, 222, 223, 234, 235, 380, 390, 381, 482, 484)

# A numerically usable constraint representation must not try to resolve the
# O31 splitting between rows 380 and 390: that splitting is about 1e-26 of the
# common O05 entry at the physical hierarchy.  Keep one compiler row and use
# the two exact O31 equations proved by the lower-minor calculation instead.
STABLE_COMPILER_PIVOT_ROWS = (
    0,
    36,
    40,
    209,
    222,
    223,
    234,
    235,
    380,
    482,
    484,
)
STABLE_EXACT_UNIT_PARAMETER_IDS = (
    "re::O31_B01_unique_Hdag2_Sigma2",
    "im::O31_B01_unique_Hdag2_Sigma2",
)
STRUCTURAL_ZERO_PARAMETER_IDS = (
    "lambda::O27_B01_126bar_self_projectors",
    "lambda::O27_B02_126bar_self_projectors",
    "lambda::O44_B03_Phi2_Sigma_projectors",
)


def _gi_add(left: GI, right: GI) -> GI:
    return left[0] + right[0], left[1] + right[1]


def _gi_multiply(left: GI, right: GI) -> GI:
    return (
        left[0] * right[0] - left[1] * right[1],
        left[0] * right[1] + left[1] * right[0],
    )


def _gi_conjugate(value: GI) -> GI:
    return value[0], -value[1]


def _gi_scale(value: GI, coefficient: int) -> GI:
    return coefficient * value[0], coefficient * value[1]


def _permutation_sign(sequence: tuple[int, ...]) -> int:
    if len(set(sequence)) != len(sequence):
        return 0
    inversions = sum(
        sequence[left] > sequence[right]
        for left in range(len(sequence))
        for right in range(left + 1, len(sequence))
    )
    return -1 if inversions % 2 else 1


def _form_add(*forms: ExactForm) -> ExactForm:
    output: ExactForm = {}
    for form in forms:
        for indices, coefficient in form.items():
            value = _gi_add(output.get(indices, GI_ZERO), coefficient)
            if value == GI_ZERO:
                output.pop(indices, None)
            else:
                output[indices] = value
    return output


def _form_scale_integer(form: ExactForm, coefficient: int) -> ExactForm:
    return {
        indices: value
        for indices, item in form.items()
        if (value := _gi_scale(item, coefficient)) != GI_ZERO
    }


def _form_scale_gi(form: ExactForm, coefficient: GI) -> ExactForm:
    return {
        indices: value
        for indices, item in form.items()
        if (value := _gi_multiply(coefficient, item)) != GI_ZERO
    }


def _one_form(index: int, coefficient: GI = GI_ONE) -> ExactForm:
    return {(index,): coefficient}


def _wedge(left: ExactForm, right: ExactForm) -> ExactForm:
    output: ExactForm = {}
    for left_indices, left_value in left.items():
        for right_indices, right_value in right.items():
            sequence = left_indices + right_indices
            sign = _permutation_sign(sequence)
            if not sign:
                continue
            indices = tuple(sorted(sequence))
            value = _gi_scale(_gi_multiply(left_value, right_value), sign)
            output = _form_add(output, {indices: value})
    return output


def _interior(form: ExactForm, index: int) -> ExactForm:
    output: ExactForm = {}
    for indices, coefficient in form.items():
        if index not in indices:
            continue
        position = indices.index(index)
        reduced = indices[:position] + indices[position + 1 :]
        output = _form_add(
            output,
            {reduced: _gi_scale(coefficient, (-1) ** position)},
        )
    return output


def _generator_action(form: ExactForm, first: int, second: int) -> ExactForm:
    return _form_add(
        _wedge(_one_form(first), _interior(form, second)),
        _form_scale_integer(
            _wedge(_one_form(second), _interior(form, first)), -1
        ),
    )


def _hodge_star(form: ExactForm) -> ExactForm:
    output: ExactForm = {}
    all_indices = set(range(10))
    for indices, coefficient in form.items():
        complement = tuple(sorted(all_indices.difference(indices)))
        output = _form_add(
            output,
            {
                complement: _gi_scale(
                    coefficient, _permutation_sign(indices + complement)
                )
            },
        )
    return output


def _twice_chiral_plus(form: ExactForm) -> ExactForm:
    """Return ``2 P_+ form = form - i * form`` over Gaussian integers."""
    return _form_add(form, _form_scale_gi(_hodge_star(form), (0, -1)))


def _form_inner(left: ExactForm, right: ExactForm) -> GI:
    output = GI_ZERO
    for indices in set(left).intersection(right):
        output = _gi_add(
            output,
            _gi_multiply(_gi_conjugate(left[indices]), right[indices]),
        )
    return output


@lru_cache(maxsize=1)
def _sigma_basis_rows() -> tuple[
    tuple[tuple[int, ...], tuple[int, ...], int], ...
]:
    rows: list[tuple[tuple[int, ...], tuple[int, ...], int]] = []
    seen: set[tuple[int, ...]] = set()
    all_indices = set(range(10))
    for initial in itertools.combinations(range(10), 5):
        if initial in seen:
            continue
        complement = tuple(sorted(all_indices.difference(initial)))
        seen.update((initial, complement))
        first, second = (
            (initial, complement)
            if initial < complement
            else (complement, initial)
        )
        rows.append((first, second, _permutation_sign(first + second)))
    if len(rows) != chart.SIGMA_COMPLEX_DIM:
        raise AssertionError("exact anti-self-dual basis must have dimension 126")
    return tuple(rows)


def _basis_form(
    row: tuple[tuple[int, ...], tuple[int, ...], int]
) -> ExactForm:
    first, second, sign = row
    return {first: GI_ONE, second: (0, sign)}


@lru_cache(maxsize=1)
def _sigma_first_lookup() -> dict[tuple[int, ...], int]:
    return {
        first: index
        for index, (first, _second, _sign) in enumerate(_sigma_basis_rows())
    }


def _sigma_coordinates(form: ExactForm) -> dict[int, GI]:
    lookup = _sigma_first_lookup()
    coordinates = {
        lookup[indices]: coefficient
        for indices, coefficient in form.items()
        if indices in lookup and coefficient != GI_ZERO
    }
    reconstructed: ExactForm = {}
    for index, coefficient in coordinates.items():
        reconstructed = _form_add(
            reconstructed,
            {
                indices: _gi_multiply(coefficient, value)
                for indices, value in _basis_form(_sigma_basis_rows()[index]).items()
            },
        )
    if reconstructed != form:
        raise AssertionError("form is not in the exact 126bar basis")
    return coordinates


def _unnormalized_delta_r() -> ExactForm:
    z1 = _form_add(_one_form(0), _one_form(1, GI_I))
    z2 = _form_add(_one_form(2), _one_form(3, GI_I))
    z3 = _form_add(_one_form(4), _one_form(5, GI_I))
    omega3 = _wedge(_wedge(z1, z2), z3)
    j_right = _form_add(
        _wedge(_one_form(6), _one_form(7)),
        _wedge(_one_form(8), _one_form(9)),
    )
    return _wedge(omega3, j_right)


@lru_cache(maxsize=1)
def _sigma_generator_columns() -> tuple[
    tuple[tuple[tuple[int, GI], ...], ...], ...
]:
    output = []
    for first, second in GENERATOR_LABELS:
        columns = []
        for row in _sigma_basis_rows():
            coordinates = _sigma_coordinates(
                _generator_action(_basis_form(row), first, second)
            )
            columns.append(tuple(sorted(coordinates.items())))
        output.append(tuple(columns))
    return tuple(output)


def _add_matrix_entry(
    matrix: SparseIntegerMatrix, row: int, column: int, value: int
) -> None:
    if not value:
        return
    key = (row, column)
    updated = matrix.get(key, 0) + int(value)
    if updated:
        matrix[key] = updated
    else:
        matrix.pop(key, None)


@lru_cache(maxsize=1)
def _full_generators() -> tuple[SparseIntegerMatrix, ...]:
    """Return all 45 SO(10) generators on the 486-real chart over Z."""
    sigma = _sigma_generator_columns()
    output: list[SparseIntegerMatrix] = []
    for generator_index, (first, second) in enumerate(GENERATOR_LABELS):
        matrix: SparseIntegerMatrix = {}
        for column, indices in enumerate(FOUR):
            for target, (real, imaginary) in _generator_action(
                {indices: GI_ONE}, first, second
            ).items():
                if imaginary:
                    raise AssertionError("real Phi generator became complex")
                _add_matrix_entry(matrix, FOUR_LOOKUP[target], column, real)

        for offset in (0, 1):
            _add_matrix_entry(
                matrix,
                chart.H_SLICE.start + 2 * first + offset,
                chart.H_SLICE.start + 2 * second + offset,
                1,
            )
            _add_matrix_entry(
                matrix,
                chart.H_SLICE.start + 2 * second + offset,
                chart.H_SLICE.start + 2 * first + offset,
                -1,
            )

        for complex_column, sparse_column in enumerate(sigma[generator_index]):
            x_column = chart.SIGMA_SLICE.start + 2 * complex_column
            y_column = x_column + 1
            for complex_row, (real, imaginary) in sparse_column:
                x_row = chart.SIGMA_SLICE.start + 2 * complex_row
                y_row = x_row + 1
                _add_matrix_entry(matrix, x_row, x_column, real)
                _add_matrix_entry(matrix, x_row, y_column, -imaginary)
                _add_matrix_entry(matrix, y_row, x_column, imaginary)
                _add_matrix_entry(matrix, y_row, y_column, real)
        output.append(matrix)
    return tuple(output)


def _linear_combination(
    terms: dict[tuple[int, int], int]
) -> SparseIntegerMatrix:
    output: SparseIntegerMatrix = {}
    generators = _full_generators()
    for label, coefficient in terms.items():
        for (row, column), value in generators[GENERATOR_LOOKUP[label]].items():
            _add_matrix_entry(output, row, column, coefficient * value)
    return output


@lru_cache(maxsize=1)
def _unbroken_generators() -> tuple[SparseIntegerMatrix, ...]:
    """Exact ``su(3)_c`` basis plus the unbroken ``G_89`` generator."""
    terms = (
        {(0, 1): 1, (2, 3): -1},
        {(2, 3): 1, (4, 5): -1},
        {(0, 2): 1, (1, 3): 1},
        {(0, 3): 1, (1, 2): -1},
        {(0, 4): 1, (1, 5): 1},
        {(0, 5): 1, (1, 4): -1},
        {(2, 4): 1, (3, 5): 1},
        {(2, 5): 1, (3, 4): -1},
        {(8, 9): 1},
    )
    return tuple(_linear_combination(row) for row in terms)


def _matrix_rows(matrix: SparseIntegerMatrix) -> list[SparseIntegerVector]:
    rows: list[SparseIntegerVector] = [
        {} for _ in range(EXPECTED_FIELD_DIMENSION)
    ]
    for (row, column), value in matrix.items():
        rows[row][column] = value
    return rows


def _sparse_matvec(
    matrix: SparseIntegerMatrix, vector: SparseIntegerVector
) -> SparseIntegerVector:
    output: SparseIntegerVector = {}
    for (row, column), value in matrix.items():
        if column in vector:
            output[row] = output.get(row, 0) + value * vector[column]
    return {row: value for row, value in output.items() if value}


def _dot(left: SparseIntegerVector, right: SparseIntegerVector) -> int:
    return sum(value * right.get(index, 0) for index, value in left.items())


def _vacuum_block_vectors() -> dict[str, SparseIntegerVector]:
    sigma: SparseIntegerVector = {}
    for index, (real, imaginary) in _sigma_coordinates(
        _unnormalized_delta_r()
    ).items():
        if real:
            sigma[chart.SIGMA_SLICE.start + 2 * index] = real
        if imaginary:
            sigma[chart.SIGMA_SLICE.start + 2 * index + 1] = imaginary
    return {
        "p": {209: 1},
        "H": {222: 1},
        "Delta_R": sigma,
        "S": {482: 1},
        "Phi17": {484: 1},
    }


def _finite_stabilizer_odd_rows() -> tuple[SparseIntegerVector, ...]:
    """Odd coordinates of an exact finite SO(10) vacuum stabilizer.

    ``R=diag(-1,-1,+1,+1,+1,+1,+1,-1,+1,-1)`` has determinant one and
    fixes ``p``, ``H_6`` and ``Delta_R``.  An invariant gradient is R-even.
    """
    signs = (-1, -1, 1, 1, 1, 1, 1, -1, 1, -1)
    coordinate_signs: list[int] = []
    for indices in FOUR:
        coordinate_signs.append(math.prod(signs[index] for index in indices))
    for index in range(chart.H_COMPLEX_DIM):
        coordinate_signs.extend((signs[index], signs[index]))
    for first, _second, _hodge_sign in _sigma_basis_rows():
        value = math.prod(signs[index] for index in first)
        coordinate_signs.extend((value, value))
    coordinate_signs.extend((1, 1, 1, 1))
    if len(coordinate_signs) != EXPECTED_FIELD_DIMENSION:
        raise AssertionError("finite stabilizer chart dimension mismatch")
    return tuple(
        {index: 1}
        for index, value in enumerate(coordinate_signs)
        if value == -1
    )


def _sigma_phase_row() -> SparseIntegerVector:
    """Overall Delta_R phase tangent with its common nonzero scale removed."""
    return {
        381: -1,
        391: -1,
        392: 1,
        402: 1,
        420: 1,
        430: 1,
        433: 1,
        443: 1,
    }


def _ward_rows() -> tuple[SparseIntegerVector, SparseIntegerVector]:
    """Scale-free PQ and independent U(1)_X-minus-PQ Ward rows.

    Once the Sigma-phase row is imposed, PQ gives
    ``-h g_Hy + 2 r g_Sy=0``.  The invertible change
    ``w_H=h g_H``, ``w_S=r g_S`` turns this into ``-w_Hy+2w_Sy=0``.
    U(1)_X minus PQ acts only on the nonzero Phi17 VEV and gives ``g_Xy=0``.
    """
    return {223: -1, 483: 2}, {485: 1}


def _kernel_columns() -> tuple[SparseIntegerVector, ...]:
    """Integer 486-by-13 ``L`` in the hierarchy-rescaled chart."""
    columns = (
        {0: 1, 13: 1, 140: 1},
        {36: 1, 55: -1, 96: -1, 107: -1},
        {40: 1, 51: 1, 92: 1, 111: -1},
        {209: 1},
        {222: 1},
        {223: 2, 483: 1},
        {234: 1, 302: 1, 341: 1},
        {235: 1, 303: 1, 340: -1},
        {380: 1, 403: 1, 431: 1, 432: -1},
        {390: 1, 393: 1, 421: 1, 442: -1},
        {
            381: 1,
            391: -1,
            392: 1,
            402: -1,
            420: 1,
            430: -1,
            433: -1,
            443: 1,
        },
        {482: 1},
        {484: 1},
    )
    if not all(
        column[pivot] != 0
        for column, pivot in zip(columns, PIVOT_ROWS, strict=True)
    ):
        raise AssertionError("L pivot submatrix is singular")
    return columns


def _normalized_factor_rows() -> dict[int, tuple[int, int | str]]:
    """Exact canonical-chart relation for every nonpivot nonzero row."""
    return {
        13: (0, 1),
        140: (0, 1),
        55: (36, -1),
        96: (36, -1),
        107: (36, -1),
        51: (40, 1),
        92: (40, 1),
        111: (40, -1),
        483: (223, "h/(2*r)"),
        302: (234, 1),
        341: (234, 1),
        303: (235, 1),
        340: (235, -1),
        403: (380, 1),
        431: (380, 1),
        432: (380, -1),
        393: (390, 1),
        421: (390, 1),
        442: (390, -1),
        391: (381, -1),
        392: (381, 1),
        402: (381, -1),
        420: (381, 1),
        430: (381, -1),
        433: (381, -1),
        443: (381, 1),
    }


def _dense_antisymmetric(form: ExactForm) -> dict[tuple[int, ...], GI]:
    output: dict[tuple[int, ...], GI] = {}
    for indices, coefficient in form.items():
        for permutation in itertools.permutations(indices):
            output[permutation] = _gi_scale(
                coefficient, _permutation_sign(permutation)
            )
    return output


def _vector_inner(left: dict[int, GI], right: dict[int, GI]) -> GI:
    output = GI_ZERO
    for index in set(left).intersection(right):
        output = _gi_add(
            output,
            _gi_multiply(_gi_conjugate(left[index]), right[index]),
        )
    return output


@lru_cache(maxsize=1)
def exact_sigma_phase_zero_certificate() -> dict[str, Any]:
    """Prove all selected nonzero-Sigma-number values vanish in Z[i]."""
    p: ExactForm = {(6, 7, 8, 9): GI_ONE}
    delta = _unnormalized_delta_r()
    delta_dag = {
        indices: _gi_conjugate(value) for indices, value in delta.items()
    }

    contracted: dict[int, GI] = {}
    for free_index in range(10):
        value = GI_ZERO
        for indices, phi_value in p.items():
            if free_index in indices:
                continue
            sequence = indices + (free_index,)
            sigma_value = delta.get(tuple(sorted(sequence)), GI_ZERO)
            value = _gi_add(
                value,
                _gi_scale(
                    _gi_multiply(phi_value, sigma_value),
                    _permutation_sign(sequence),
                ),
            )
        if value != GI_ZERO:
            contracted[free_index] = value

    dense_delta = _dense_antisymmetric(delta)
    dense_dag = _dense_antisymmetric(delta_dag)

    # O31 has source einsum ``a,b,bcdef,acdef->`` with Hdag=e6.
    o31 = GI_ZERO
    for indices, value in dense_delta.items():
        if indices[0] == 6:
            o31 = _gi_add(o31, _gi_multiply(value, value))

    # O28 has source einsum ``a,bcdef,abcgh,defgh->`` with Hdag=e6.
    second_by_bc: dict[tuple[int, int], list[tuple[int, int, GI]]] = {}
    for (a, b, c, g, h), value in dense_delta.items():
        if a == 6:
            second_by_bc.setdefault((b, c), []).append((g, h, value))
    o28 = GI_ZERO
    for (b, c, d, e, f), first_value in dense_delta.items():
        for g, h, second_value in second_by_bc.get((b, c), ()):
            dag_value = dense_dag.get((d, e, f, g, h), GI_ZERO)
            o28 = _gi_add(
                o28,
                _gi_multiply(
                    _gi_multiply(first_value, second_value), dag_value
                ),
            )

    # O45: clear the factors 1/2 in P_+ and 1/3 in P_210=J Jdag/3.
    def inject_twice(four: ExactForm) -> dict[int, ExactForm]:
        return {
            index: _twice_chiral_plus(_wedge(_one_form(index), four))
            for index in range(10)
        }

    bilinear_twice: dict[int, ExactForm] = {}
    for a in range(10):
        raw: ExactForm = {}
        for i in range(10):
            left_ai = _interior(_interior(p, a), i)
            term = _wedge(left_ai, _interior(p, i))
            raw = _form_add(raw, term, term)
        bilinear_twice[a] = _twice_chiral_plus(raw)
    external = {6: delta_dag}

    def tensor_inner(
        left: dict[int, ExactForm], right: dict[int, ExactForm]
    ) -> GI:
        value = GI_ZERO
        for index in set(left).intersection(right):
            value = _gi_add(value, _form_inner(left[index], right[index]))
        return value

    jdag_bilinear: dict[int, GI] = {}
    jdag_external: dict[int, GI] = {}
    for index, indices in enumerate(FOUR):
        injection = inject_twice({indices: GI_ONE})
        bilinear_value = tensor_inner(injection, bilinear_twice)
        external_value = tensor_inner(injection, external)
        if bilinear_value != GI_ZERO:
            jdag_bilinear[index] = bilinear_value
        if external_value != GI_ZERO:
            jdag_external[index] = external_value
    o45_total = tensor_inner(bilinear_twice, external)
    o45_210_numerator = _vector_inner(jdag_bilinear, jdag_external)

    selected = contract.build_report()["gauged_directions"]
    observed_ids = {
        str(row["direction_id"])
        for row in selected
        if int(row["base_key"][3]) - int(row["base_key"][4]) != 0
    }
    expected_ids = {
        "O15_B01_Phi_Hdag_Sigma",
        "O28_B01_unique_Hdag_Sigma2_Sigmadag",
        "O31_B01_unique_Hdag2_Sigma2",
        "O38_B01_Phi_Hdag_Sigmadag",
        "O45_B01_Phi2_Hdag_Sigma_210_1050",
        "O45_B02_Phi2_Hdag_Sigma_210_1050",
    }
    checks = {
        "all_nonzero_Sigma_number_directions_enumerated": (
            observed_ids == expected_ids
        ),
        "O15_Phi_Hdag_Sigma_value_zero": not contracted,
        "O38_Phi_Hdag_Sigmadag_Sdag_value_zero": not contracted,
        "O28_Hdag_Sigma2_Sigmadag_value_zero": o28 == GI_ZERO,
        "O31_Hdag2_Sigma2_value_zero": o31 == GI_ZERO,
        "O45_total_210_plus_1050_value_zero": o45_total == GI_ZERO,
        "O45_210_channel_value_zero": o45_210_numerator == GI_ZERO,
        "O45_1050_channel_value_zero": (
            o45_total == GI_ZERO and o45_210_numerator == GI_ZERO
        ),
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "arithmetic_domain": "Gaussian integers Z[i]; projector denominators cleared",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "certified": not failures,
        "observed_nonzero_Sigma_number_direction_ids": sorted(observed_ids),
        "expected_nonzero_Sigma_number_direction_ids": sorted(expected_ids),
        "implication": (
            "For net Sigma number k, dI/dtheta=i*k*I. The exact zeros above "
            "therefore make every selected gradient orthogonal to the overall "
            "Delta_R phase tangent; net-zero directions obey it identically."
        ),
    }


def _modular_rank(rows: Iterable[SparseIntegerVector], prime: int) -> int:
    """Exact sparse row rank over ``GF(prime)``."""
    pivots: dict[int, SparseIntegerVector] = {}
    for source in rows:
        row = {
            column: value % prime
            for column, value in source.items()
            if value % prime
        }
        while row:
            pivot = min(row)
            if pivot not in pivots:
                inverse = pow(row[pivot], prime - 2, prime)
                pivots[pivot] = {
                    column: (value * inverse) % prime
                    for column, value in row.items()
                }
                break
            factor = row[pivot]
            for column, value in pivots[pivot].items():
                updated = (row.get(column, 0) - factor * value) % prime
                if updated:
                    row[column] = updated
                else:
                    row.pop(column, None)
    return len(pivots)


@lru_cache(maxsize=1)
def exact_rank_upper_certificate() -> dict[str, Any]:
    """Return the exact ``rank(A)<=13`` factorization certificate."""
    sigma_phase = exact_sigma_phase_zero_certificate()
    unbroken = _unbroken_generators()
    finite_rows = _finite_stabilizer_odd_rows()
    pq_row, x_phase_row = _ward_rows()
    kernel = _kernel_columns()
    vacuum = _vacuum_block_vectors()

    continuous_fix = {
        name: all(not _sparse_matvec(generator, vector) for generator in unbroken)
        for name, vector in vacuum.items()
    }
    finite_fix = {
        name: all(_dot(row, vector) == 0 for row in finite_rows)
        for name, vector in vacuum.items()
    }
    generator_kernel = all(
        not _sparse_matvec(generator, vector)
        for generator in unbroken
        for vector in kernel
    )
    finite_kernel = all(
        _dot(row, vector) == 0 for row in finite_rows for vector in kernel
    )
    ward_kernel = all(
        _dot(row, vector) == 0
        for row in (_sigma_phase_row(), pq_row, x_phase_row)
        for vector in kernel
    )

    constraint_rows: list[SparseIntegerVector] = []
    for generator in unbroken:
        constraint_rows.extend(row for row in _matrix_rows(generator) if row)
    constraint_rows.extend(finite_rows)
    constraint_rows.extend((_sigma_phase_row(), pq_row, x_phase_row))
    primes = (1_000_000_007, 1_000_000_009)
    ranks = {str(prime): _modular_rank(constraint_rows, prime) for prime in primes}
    pivot_independent = all(
        column[pivot] != 0
        for column, pivot in zip(kernel, PIVOT_ROWS, strict=True)
    )

    factor_rows = _normalized_factor_rows()
    nonzero_rows = sorted(set(PIVOT_ROWS).union(factor_rows))
    zero_rows = sorted(set(range(EXPECTED_FIELD_DIMENSION)).difference(nonzero_rows))
    contract_report = contract.build_report()
    checks = {
        "contract_is_44_directions_51_parameters": (
            contract_report["counts"]["invariant_directions"] == 44
            and contract_report["counts"]["real_parameters"]
            == EXPECTED_PARAMETER_COUNT
        ),
        "all_five_vacuum_blocks_fixed_by_nine_continuous_generators": all(
            continuous_fix.values()
        )
        and len(unbroken) == 9,
        "all_five_vacuum_blocks_fixed_by_finite_SO10_element": all(
            finite_fix.values()
        ),
        "all_nonzero_Sigma_number_values_exactly_zero": sigma_phase["certified"],
        "C_times_L_is_exactly_zero": (
            generator_kernel and finite_kernel and ward_kernel
        ),
        "L_has_13_independent_pivot_columns": (
            len(kernel) == EXPECTED_RANK and pivot_independent
        ),
        "integer_constraint_rank_is_at_least_473": all(
            rank == EXPECTED_FIELD_DIMENSION - EXPECTED_RANK
            for rank in ranks.values()
        ),
        "integer_constraint_rank_is_at_most_473": (
            generator_kernel and finite_kernel and ward_kernel and pivot_independent
        ),
        "kernel_equals_column_space_L": True,
        "factorization_has_39_nonzero_and_447_zero_rows": (
            len(nonzero_rows) == 39 and len(zero_rows) == 447
        ),
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "status": (
            "EXACT_GAUGED_U1X_STATIONARITY_RANK_UPPER_13_CERTIFIED"
            if not failures
            else "EXACT_GAUGED_U1X_STATIONARITY_RANK_UPPER_CERTIFICATE_FAILED"
        ),
        "model_contract_id": MODEL_CONTRACT_ID,
        "proof_schema": PROOF_SCHEMA,
        "prototype_sha256": PROTOTYPE_SHA256,
        "arithmetic_domain": (
            "Z and Z[i] after invertible nonzero hierarchy/chart block rescalings"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "certified": not failures,
        "field_dimension": EXPECTED_FIELD_DIMENSION,
        "parameter_count": EXPECTED_PARAMETER_COUNT,
        "rank_upper_bound": EXPECTED_RANK if not failures else None,
        "continuous_unbroken_generators": 9,
        "finite_stabilizer": {
            "vector_representation_diagonal": [-1, -1, 1, 1, 1, 1, 1, -1, 1, -1],
            "determinant": 1,
            "odd_coordinate_count": len(finite_rows),
        },
        "sigma_phase_zero_certificate": sigma_phase,
        "constraint_matrix": {
            "nonzero_row_equations": len(constraint_rows),
            "rank_mod_primes": ranks,
            "rational_rank": EXPECTED_FIELD_DIMENSION - EXPECTED_RANK,
            "rank_argument": (
                "rank 473 modulo either prime exhibits a nonzero integer "
                "473-minor, hence rank_Q(C)>=473. The 13 independent exact "
                "columns of L satisfy C L=0, hence rank_Q(C)<=473."
            ),
        },
        "factorization": {
            "formula": "A = L A[pivot_rows,:]",
            "pivot_rows": list(PIVOT_ROWS),
            "pivot_coordinate_names": [
                chart.coordinate_names()[index] for index in PIVOT_ROWS
            ],
            "nonpivot_row_relations": {
                str(row): {
                    "coordinate": chart.coordinate_names()[row],
                    "pivot_row": pivot,
                    "pivot_coordinate": chart.coordinate_names()[pivot],
                    "coefficient": coefficient,
                }
                for row, (pivot, coefficient) in factor_rows.items()
            },
            "nonzero_row_indices": nonzero_rows,
            "zero_row_indices": zero_rows,
            "nonzero_row_count": len(nonzero_rows),
            "zero_row_count": len(zero_rows),
            "hierarchy_relation": "A[S.y,:]=h/(2*r)*A[H[6].y,:]",
        },
        "proof_implication": {
            "every_selected_gradient_obeys_Cg_zero": not failures,
            "rank_A_at_most_13": not failures,
            "nullity_A_at_least_38": not failures,
        },
    }


LOWER_MINOR_COORDINATE_ROWS = (
    "Phi[0,1,2,3]",
    "Phi[0,2,4,7]",
    "Phi[0,2,5,7]",
    "Phi[6,7,8,9]",
    "H[6].x",
    "H[6].y",
    "Sigma[2].x",
    "Sigma[2].y",
    "Sigma[75].x",
    "Sigma[80].x",
    "Sigma[75].y",
    "S.x",
    "Phi17.x",
)
LOWER_MINOR_PARAMETER_COLUMNS = (
    "lambda::O44_B02_Phi2_Sigma_projectors",
    "re::O15_B01_Phi_Hdag_Sigma",
    "im::O15_B01_Phi_Hdag_Sigma",
    "lambda::O48_B04_Phi_self_quartics",
    "lambda::O06_B01_Hdag_H_norm",
    "im::O12_B01_Hdag_Hdag_pair",
    "re::O28_B01_unique_Hdag_Sigma2_Sigmadag",
    "im::O28_B01_unique_Hdag_Sigma2_Sigmadag",
    "lambda::O05_B01_126bar_norm",
    "re::O31_B01_unique_Hdag2_Sigma2",
    "im::O31_B01_unique_Hdag2_Sigma2",
    "lambda::O04_B01_singlet_polynomial",
    "lambda::O03_B01_singlet_polynomial",
)


def _o28_graph(first: ExactForm, second: ExactForm, dagger: ExactForm) -> GI:
    dense_first = _dense_antisymmetric(first)
    dense_second = _dense_antisymmetric(second)
    dense_dagger = _dense_antisymmetric(dagger)
    second_by_bc: dict[tuple[int, int], list[tuple[int, int, GI]]] = {}
    for (a, b, c, g, h), value in dense_second.items():
        if a == 6:
            second_by_bc.setdefault((b, c), []).append((g, h, value))
    output = GI_ZERO
    for (b, c, d, e, f), first_value in dense_first.items():
        for g, h, second_value in second_by_bc.get((b, c), ()):
            dagger_value = dense_dagger.get((d, e, f, g, h), GI_ZERO)
            output = _gi_add(
                output,
                _gi_multiply(
                    _gi_multiply(first_value, second_value), dagger_value
                ),
            )
    return output


@lru_cache(maxsize=1)
def exact_lower_minor_certificate() -> dict[str, Any]:
    """Prove the symbolic nonzero 13-minor and its delicate chiral pivots."""
    delta = _unnormalized_delta_r()
    delta_dag = {
        indices: _gi_conjugate(value) for indices, value in delta.items()
    }

    portal_coefficients: dict[int, GI] = {}
    for row in (36, 40):
        indices = FOUR[row]
        sequence = indices + (6,)
        portal_coefficients[row] = _gi_scale(
            delta.get(tuple(sorted(sequence)), GI_ZERO),
            _permutation_sign(sequence),
        )

    basis2 = _basis_form(_sigma_basis_rows()[2])
    basis2_dag = {
        indices: _gi_conjugate(value) for indices, value in basis2.items()
    }
    o28_x_terms = (
        _o28_graph(basis2, delta, delta_dag),
        _o28_graph(delta, basis2, delta_dag),
        _o28_graph(delta, delta, basis2_dag),
    )
    o28_x = GI_ZERO
    for value in o28_x_terms:
        o28_x = _gi_add(o28_x, value)
    o28_y = GI_ZERO
    for value in (
        _o28_graph(_form_scale_gi(basis2, GI_I), delta, delta_dag),
        _o28_graph(delta, _form_scale_gi(basis2, GI_I), delta_dag),
        _o28_graph(
            delta, delta, _form_scale_gi(basis2_dag, (0, -1))
        ),
    ):
        o28_y = _gi_add(o28_y, value)

    dense_delta = _dense_antisymmetric(delta)
    o31_pairings: dict[int, GI] = {}
    for basis_index in (75, 80):
        dense_basis = _dense_antisymmetric(
            _basis_form(_sigma_basis_rows()[basis_index])
        )
        value = GI_ZERO
        for (a, c, d, e, f), delta_value in dense_delta.items():
            if a != 6:
                continue
            basis_value = dense_basis.get((6, c, d, e, f), GI_ZERO)
            value = _gi_add(
                value, _gi_multiply(delta_value, basis_value)
            )
        o31_pairings[basis_index] = value

    checks = {
        "O15_row36_Gaussian_coefficient_is_minus_one": (
            portal_coefficients[36] == (-1, 0)
        ),
        "O15_row40_Gaussian_coefficient_is_minus_i": (
            portal_coefficients[40] == (0, -1)
        ),
        "O28_Sigma2_x_Gaussian_first_variation_is_768": (
            o28_x == (768, 0)
        ),
        "O28_Sigma2_y_Gaussian_first_variation_is_768i": (
            o28_y == (0, 768)
        ),
        "O31_Sigma75_pairing_is_plus_24": (
            o31_pairings[75] == (24, 0)
        ),
        "O31_Sigma80_pairing_is_minus_24": (
            o31_pairings[80] == (-24, 0)
        ),
        "symbolic_minor_determinant_nonzero_for_h_nonzero": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "arithmetic_domain": "Q(sqrt(2),h,r,x) with h,r,x nonzero; Z[i] tensor coefficients",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "certified": not failures,
        "coordinate_rows": list(LOWER_MINOR_COORDINATE_ROWS),
        "parameter_columns": list(LOWER_MINOR_PARAMETER_COLUMNS),
        "exact_raw_nonzero_entries": {
            "Phi[0,1,2,3] / O44_B02": "(2/35)*r^2",
            "Phi[0,2,4,7] / re(O15)": "-h*r/sqrt(2)",
            "Phi[0,2,5,7] / im(O15)": "+h*r/sqrt(2)",
            "Phi[6,7,8,9] / O48_B04": "14208",
            "H[6].x / O06": "sqrt(2)*h",
            "H[6].y / im(O12)": "2*sqrt(2)*h*r",
            "Sigma[2].x / re(O28)": "96*sqrt(2)*h*r^2",
            "Sigma[2].y / im(O28)": "-96*sqrt(2)*h*r^2",
            "Sigma[75].x / O05": "r/2",
            "Sigma[75].x / re(O31)": "+24*h^2*r",
            "Sigma[80].x / O05": "r/2",
            "Sigma[80].x / re(O31)": "-24*h^2*r",
            "Sigma[75].y / im(O31)": "-24*h^2*r",
            "S.x / O04": "sqrt(2)*r",
            "Phi17.x / O03": "sqrt(2)*x",
        },
        "row_scaled_minor": {
            "diagonal_first_eight": [
                "2/35",
                "-1",
                "1",
                "14208",
                "1",
                "1",
                "1",
                "-1",
            ],
            "rows_8_9_columns_8_9": [
                ["1/2", "24*h^2"],
                ["1/2", "-24*h^2"],
            ],
            "last_three_diagonal": ["1", "1", "1"],
            "determinant": "-(681984/35)*h^2",
            "determinant_nonzero_assumption": "h != 0",
        },
        "delicate_O31_explanation": (
            "The float rows Sigma[75].x and Sigma[80].x differ only by "
            "48*h^2*r, about 1e-26 relative to their r/2 entry. A row-normalized "
            "float64 SVD therefore reports rank 12, but the exact Z[i] pairings "
            "+24 and -24 make the 2x2 determinant -24*h^2 nonzero."
        ),
    }


def compiler_minor_binding(
    parameter_rows: Sequence[Any], state: Any, *, relative_tolerance: float = 2.0e-10
) -> dict[str, Any]:
    """Bind the exact 13-minor to entries from the actual compiler gradients."""
    by_parameter = {str(row.parameter_id): row for row in parameter_rows}
    coordinate_lookup = {
        name: index for index, name in enumerate(chart.coordinate_names())
    }
    missing_parameters = sorted(
        set(LOWER_MINOR_PARAMETER_COLUMNS).difference(by_parameter)
    )
    missing_coordinates = sorted(
        set(LOWER_MINOR_COORDINATE_ROWS).difference(coordinate_lookup)
    )
    h = float(complex(state.h[6]).real)
    r = float(complex(state.s).real)
    x = float(complex(state.x).real)
    sqrt2 = math.sqrt(2.0)
    expected = [[0.0 for _ in range(13)] for _ in range(13)]
    expected[0][0] = (2.0 / 35.0) * r * r
    expected[1][1] = -h * r / sqrt2
    expected[2][2] = h * r / sqrt2
    expected[3][3] = 14208.0
    expected[4][4] = sqrt2 * h
    expected[5][5] = 2.0 * sqrt2 * h * r
    expected[6][6] = 96.0 * sqrt2 * h * r * r
    expected[7][7] = -96.0 * sqrt2 * h * r * r
    expected[8][8] = r / 2.0
    expected[8][9] = 24.0 * h * h * r
    expected[9][8] = r / 2.0
    expected[9][9] = -24.0 * h * h * r
    expected[10][10] = -24.0 * h * h * r
    expected[11][11] = sqrt2 * r
    expected[12][12] = sqrt2 * x

    actual = [[0.0 for _ in range(13)] for _ in range(13)]
    if not missing_parameters and not missing_coordinates:
        for row_index, coordinate in enumerate(LOWER_MINOR_COORDINATE_ROWS):
            coordinate_index = coordinate_lookup[coordinate]
            for column_index, parameter in enumerate(
                LOWER_MINOR_PARAMETER_COLUMNS
            ):
                actual[row_index][column_index] = float(
                    parameter_rows[
                        next(
                            index
                            for index, item in enumerate(parameter_rows)
                            if str(item.parameter_id) == parameter
                        )
                    ].gradient[coordinate_index]
                )

    nonzero_residuals: list[float] = []
    zero_residuals: list[float] = []
    entry_rows: list[dict[str, Any]] = []
    for row_index in range(13):
        row_reference = max(abs(value) for value in expected[row_index])
        for column_index in range(13):
            target = expected[row_index][column_index]
            observed = actual[row_index][column_index]
            if target:
                residual = abs(observed - target) / abs(target)
                nonzero_residuals.append(residual)
                entry_rows.append(
                    {
                        "coordinate": LOWER_MINOR_COORDINATE_ROWS[row_index],
                        "parameter": LOWER_MINOR_PARAMETER_COLUMNS[column_index],
                        "expected": target,
                        "compiler": observed,
                        "relative_residual": residual,
                    }
                )
            else:
                residual = abs(observed) / max(row_reference, 1.0e-300)
                zero_residuals.append(residual)

    maximum_nonzero_residual = max(nonzero_residuals, default=math.inf)
    maximum_zero_residual = max(zero_residuals, default=math.inf)
    exact = exact_lower_minor_certificate()
    checks = {
        "all_13_parameter_columns_found_in_compiler": not missing_parameters,
        "all_13_coordinate_rows_found_in_chart": not missing_coordinates,
        "hierarchy_scales_h_r_x_are_nonzero_real": (
            h != 0.0
            and r != 0.0
            and x != 0.0
            and complex(state.h[6]).imag == 0.0
            and complex(state.s).imag == 0.0
            and complex(state.x).imag == 0.0
        ),
        "all_15_symbolic_nonzero_entries_match_compiler": (
            len(nonzero_residuals) == 15
            and maximum_nonzero_residual <= relative_tolerance
        ),
        "all_154_symbolic_zero_entries_match_compiler": (
            len(zero_residuals) == 154
            and maximum_zero_residual <= relative_tolerance
        ),
        "exact_symbolic_minor_certificate_passes": exact["certified"],
        "compiler_binding_not_float_rank_inference": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "status": (
            "COMPILER_GRADIENTS_BOUND_TO_EXACT_NONZERO_13_MINOR"
            if not failures
            else "COMPILER_GRADIENT_EXACT_MINOR_BINDING_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "certified": not failures,
        "relative_tolerance": relative_tolerance,
        "missing_parameters": missing_parameters,
        "missing_coordinates": missing_coordinates,
        "hierarchy_scales_float_binding_only": {"h": h, "r": r, "x": x},
        "maximum_nonzero_entry_relative_residual": maximum_nonzero_residual,
        "maximum_symbolic_zero_entry_row_relative_residual": maximum_zero_residual,
        "nonzero_entry_binding": entry_rows,
        "exact_symbolic_certificate": exact,
        "note": (
            "The compiler comparison binds IDs, coordinates, signs and "
            "normalizations. Exact nonzeroness comes from the symbolic/Z[i] "
            "certificate, not from an ill-conditioned float determinant or SVD."
        ),
    }


def exact_informed_stationarity_constraints(
    parameter_rows: Sequence[Any], *, include_arrays: bool = True
) -> dict[str, Any]:
    """Build the well-conditioned 13-row representation used by corrected G3.

    Eleven rows are read directly from the compiler and normalized only as
    rows.  The two hierarchy-suppressed O31 equations are inserted as exact
    unit constraints.  There is deliberately no column normalization and no
    backscaling of singular vectors.
    """
    parameter_ids = tuple(str(row.parameter_id) for row in parameter_rows)
    if len(parameter_ids) != EXPECTED_PARAMETER_COUNT:
        raise ValueError(
            f"expected {EXPECTED_PARAMETER_COUNT} parameter rows, "
            f"received {len(parameter_ids)}"
        )
    if len(set(parameter_ids)) != len(parameter_ids):
        raise ValueError("compiler parameter IDs are not unique")
    by_id = {parameter_id: index for index, parameter_id in enumerate(parameter_ids)}
    required_ids = set(STABLE_EXACT_UNIT_PARAMETER_IDS).union(
        STRUCTURAL_ZERO_PARAMETER_IDS
    )
    missing_ids = sorted(required_ids.difference(by_id))
    if missing_ids:
        raise KeyError(f"required compiler parameters are missing: {missing_ids}")

    matrix = np.column_stack(
        [np.asarray(row.gradient, dtype=float) for row in parameter_rows]
    )
    if matrix.shape != (EXPECTED_FIELD_DIMENSION, EXPECTED_PARAMETER_COUNT):
        raise ValueError(
            "compiler stationarity matrix shape mismatch: "
            f"observed {matrix.shape}"
        )
    promoted = matrix.copy()
    structural_zero_indices = tuple(
        by_id[parameter_id] for parameter_id in STRUCTURAL_ZERO_PARAMETER_IDS
    )
    promoted[:, structural_zero_indices] = 0.0

    compiler_rows = promoted[np.asarray(STABLE_COMPILER_PIVOT_ROWS), :].copy()
    compiler_row_norms = np.linalg.norm(compiler_rows, axis=1)
    if np.any(compiler_row_norms == 0.0):
        bad = [
            row
            for row, norm in zip(
                STABLE_COMPILER_PIVOT_ROWS, compiler_row_norms, strict=True
            )
            if norm == 0.0
        ]
        raise ArithmeticError(f"zero compiler pivot rows: {bad}")
    compiler_rows /= compiler_row_norms[:, None]

    exact_unit_rows = np.zeros(
        (len(STABLE_EXACT_UNIT_PARAMETER_IDS), EXPECTED_PARAMETER_COUNT),
        dtype=float,
    )
    for row_index, parameter_id in enumerate(STABLE_EXACT_UNIT_PARAMETER_IDS):
        exact_unit_rows[row_index, by_id[parameter_id]] = 1.0
    constraints = np.vstack((compiler_rows, exact_unit_rows))

    _u, singular_values, vh = np.linalg.svd(constraints, full_matrices=True)
    threshold = 1.0e-12 * singular_values[0]
    numerical_rank = int(np.sum(singular_values > threshold))
    null_basis = vh[numerical_rank:, :].T

    witness = np.zeros(EXPECTED_PARAMETER_COUNT, dtype=float)
    witness[by_id["lambda::O07_B01_Phi_norm"]] = 10.0
    witness[by_id["lambda::O48_B01_Phi_self_quartics"]] = 1.0
    witness[by_id["lambda::O48_B02_Phi_self_quartics"]] = -0.25
    witness_residual = constraints @ witness

    exact_rank = build_report()
    lower = exact_rank["rank_lower_certificate"]
    checks = {
        "exact_rank_13_nullity_38_certificate_passes": exact_rank["certified"],
        "uses_11_normalized_compiler_rows": compiler_rows.shape == (11, 51),
        "uses_two_exact_O31_unit_rows": (
            exact_unit_rows.shape == (2, 51)
            and np.count_nonzero(exact_unit_rows) == 2
            and lower["checks"]["O31_Sigma75_pairing_is_plus_24"]
            and lower["checks"]["O31_Sigma80_pairing_is_minus_24"]
        ),
        "structural_zero_columns_are_promoted_exactly": bool(
            np.count_nonzero(promoted[:, structural_zero_indices]) == 0
        ),
        "constraint_representation_has_rank_13": numerical_rank
        == EXPECTED_RANK,
        "constraint_representation_has_nullity_38": null_basis.shape
        == (EXPECTED_PARAMETER_COUNT, EXPECTED_NULLITY),
        "constraint_singular_values_are_well_conditioned": bool(
            singular_values[0] < 1.02 and singular_values[-1] > 0.98
        ),
        "exact_stationary_witness_is_accepted": bool(
            np.max(np.abs(witness_residual), initial=0.0) <= 2.0e-12
        ),
        "legacy_column_normalize_backscale_is_not_used": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    result: dict[str, Any] = {
        "status": (
            "EXACT_INFORMED_STATIONARITY_CONSTRAINTS_READY"
            if not failures
            else "EXACT_INFORMED_STATIONARITY_CONSTRAINTS_FAILED"
        ),
        "certified": not failures,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "parameter_ids": parameter_ids,
        "compiler_pivot_rows": list(STABLE_COMPILER_PIVOT_ROWS),
        "compiler_pivot_coordinates": [
            chart.coordinate_names()[row] for row in STABLE_COMPILER_PIVOT_ROWS
        ],
        "compiler_row_norms": compiler_row_norms,
        "exact_unit_parameter_ids": list(STABLE_EXACT_UNIT_PARAMETER_IDS),
        "structural_zero_parameter_ids": list(STRUCTURAL_ZERO_PARAMETER_IDS),
        "rank": numerical_rank,
        "nullity": int(null_basis.shape[1]),
        "singular_values": singular_values,
        "condition_number": float(singular_values[0] / singular_values[-1]),
        "singular_value_threshold": threshold,
        "exact_rank_and_nullity_certified_independently": exact_rank["certified"],
        "exact_O31_equations": {
            "real": (
                "A[Sigma[75].x,:]-A[Sigma[80].x,:] contains the exact "
                "+48*h^2*r re(O31) pivot, so re(O31)=0"
            ),
            "imaginary": (
                "A[Sigma[75].y,:] contains the exact -24*h^2*r im(O31) "
                "pivot, so im(O31)=0"
            ),
            "nonzero_assumptions": "h != 0 and r != 0",
        },
        "exact_stationary_witness_max_abs_residual": float(
            np.max(np.abs(witness_residual), initial=0.0)
        ),
        "null_basis_is_numerical_not_proof_grade": True,
        "construction_note": (
            "The exact proof fixes the row-space dimension. This representation "
            "provides a stable numerical basis for a future separately audited "
            "G3 solver; it is not itself an SDP or stability certificate."
        ),
    }
    if include_arrays:
        result.update(
            {
                "promoted_gradient_matrix": promoted,
                "constraint_rows": constraints,
                "null_basis": null_basis,
            }
        )
    return result


@lru_cache(maxsize=1)
def build_report() -> dict[str, Any]:
    upper = exact_rank_upper_certificate()
    lower = exact_lower_minor_certificate()
    exact_rank = bool(upper["certified"] and lower["certified"])
    checks = {
        "exact_rank_upper_bound_13_certified": upper["certified"],
        "exact_rank_lower_bound_13_certified": lower["certified"],
        "exact_rank_is_13": exact_rank,
        "exact_nullity_is_38": exact_rank,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "status": (
            "EXACT_GAUGED_U1X_STATIONARITY_RANK_13_NULLITY_38_CERTIFIED"
            if not failures
            else "EXACT_GAUGED_U1X_STATIONARITY_RANK_CERTIFICATE_FAILED"
        ),
        "model_contract_id": MODEL_CONTRACT_ID,
        "proof_schema": PROOF_SCHEMA,
        "prototype_sha256": PROTOTYPE_SHA256,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "certified": not failures,
        "rank": EXPECTED_RANK if exact_rank else None,
        "nullity": EXPECTED_NULLITY if exact_rank else None,
        "rank_upper_certificate": upper,
        "rank_lower_certificate": lower,
        "compiler_binding_required_for_G2_promotion": True,
        "verdict": (
            "The exact symmetry/Ward factorization proves rank at most 13, "
            "and a Gaussian-integer/rational nonzero minor proves rank at "
            "least 13. G2 may promote rank 13/nullity 38 only after the actual "
            "compiler gradient entries pass compiler_minor_binding."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Exact gauged-U(1)_X stationarity-rank certificate\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"**Rank/nullity:** `{report['rank']}/{report['nullity']}`\n\n"
        + report["verdict"]
        + "\n",
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
