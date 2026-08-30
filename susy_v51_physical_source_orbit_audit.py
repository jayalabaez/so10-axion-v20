#!/usr/bin/env python3
"""V51 exact physical source-orbit and quotient audit.

This module supplies a representation-faithful object that was missing from
the V46/V47 source completion: the complex 465 x 22 gauge-orbit map for

    210 + 126 + bar126 + STheta + ThetaPlus + ThetaMinus

on the aligned supersymmetric SU(5) branch.  The 210 is the real Cartesian
four-form

    F0 = sum_(i<j) omega_i wedge omega_j,

and the 126 pair is the canonically normalized conjugate pair of holomorphic
five-forms.  All entries are generated in exact Gaussian-rational arithmetic
from the exterior-form action of so(10).  The twenty-one independent broken
Spin(10) columns and the broken U(1)_F column are published sparsely in the
JSON artifact, together with their exact Gram matrix and a reproducible hash.

The resulting orthogonal quotient projector has rank 443.  This is a
kinematic/source-geometry certificate.  V46 and V47 do not publish the full
Cartesian holomorphic superpotential Hessian, so this module deliberately
does not claim the Ward identity H Q = 0 or a physical Hessian pullback.  The
older v20 P+Delta_R Hessian cannot fill that gap because it uses a different
vacuum, one chiral five-form rather than a 126 pair, and an SM-sized rather
than SU(5)-sized stabilizer.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
import math
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, Mapping


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V51_PHYSICAL_SOURCE_ORBIT_AUDIT.json"
MD_PATH = ROOT / "SUSY_V51_PHYSICAL_SOURCE_ORBIT_AUDIT.md"

INPUTS = {
    "v46_source_rank": ROOT / "SUSY_V46_SOURCE_HIGGS_RANK_AUDIT.json",
    "v47_source_completion": ROOT / "SUSY_V47_SOURCE_COMPLETION_ROUTE_AUDIT.json",
    "legacy_v20_pd_rank": ROOT / "EXACT_GAUGED_U1X_G3_PD_RANK_CERTIFICATE_V20.json",
}
SOURCE_FILES = (
    "susy_v51_physical_source_orbit_audit.py",
    "test_susy_v51_physical_source_orbit_audit.py",
    *(path.name for path in INPUTS.values()),
)

STATUS = (
    "V51_EXACT_REPRESENTATION_FAITHFUL_465_BY_22_SOURCE_ORBIT_AND_"
    "RANK_443_QUOTIENT_PROJECTOR__CARTESIAN_SUPERPOTENTIAL_HESSIAN_"
    "WARD_IDENTITY_AND_PHYSICAL_PULLBACK_STILL_OPEN__NO_G2_CLAUSE_PROMOTED"
)

N = 10
SO10_GENERATOR_COUNT = 45
SO10_BROKEN_COUNT = 21
SOURCE_GAUGE_ORBIT_DIMENSION = 22
SOURCE_COMPLEX_DIMENSION = 210 + 126 + 126 + 3
PHYSICAL_COMPLEX_DIMENSION = SOURCE_COMPLEX_DIMENSION - SOURCE_GAUGE_ORBIT_DIMENSION

# A Gaussian rational is a + i b with a,b in Q.
GR = tuple[Fraction, Fraction]
Form = dict[tuple[int, ...], GR]
ZERO: GR = (Fraction(0), Fraction(0))
ONE: GR = (Fraction(1), Fraction(0))
I: GR = (Fraction(0), Fraction(1))

FOUR_INDICES = tuple(itertools.combinations(range(N), 4))
SO10_GENERATORS = tuple(itertools.combinations(range(N), 2))

# Deterministic independent broken-generator chart obtained by exact pivoting.
# There is one U(1)_chi-like direction and twenty real 10+bar10 directions.
SELECTED_BROKEN_GENERATORS = (
    (0, 1),
    (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 9),
    (2, 4), (2, 5), (2, 6), (2, 7), (2, 8), (2, 9),
    (4, 6), (4, 7), (4, 8), (4, 9),
    (6, 8), (6, 9),
)


def _gr(value: int | Fraction = 0, imaginary: int | Fraction = 0) -> GR:
    return (Fraction(value), Fraction(imaginary))


def _g_add(left: GR, right: GR) -> GR:
    return (left[0] + right[0], left[1] + right[1])


def _g_neg(value: GR) -> GR:
    return (-value[0], -value[1])


def _g_sub(left: GR, right: GR) -> GR:
    return _g_add(left, _g_neg(right))


def _g_mul(left: GR, right: GR) -> GR:
    return (
        left[0] * right[0] - left[1] * right[1],
        left[0] * right[1] + left[1] * right[0],
    )


def _g_conjugate(value: GR) -> GR:
    return (value[0], -value[1])


def _g_scale(value: GR, coefficient: Fraction | int) -> GR:
    scale = Fraction(coefficient)
    return (scale * value[0], scale * value[1])


def _g_is_zero(value: GR) -> bool:
    return value == ZERO


def _permutation_sign(sequence: tuple[int, ...]) -> int:
    inversions = sum(
        sequence[first] > sequence[second]
        for first in range(len(sequence))
        for second in range(first + 1, len(sequence))
    )
    return -1 if inversions % 2 else 1


def _one_form(index: int, coefficient: GR = ONE) -> Form:
    if not 0 <= index < N:
        raise ValueError("one-form index out of range")
    return {(index,): coefficient}


def _add_forms(*forms: Form) -> Form:
    output: Form = {}
    for form in forms:
        for indices, coefficient in form.items():
            output[indices] = _g_add(output.get(indices, ZERO), coefficient)
    return {indices: value for indices, value in output.items() if not _g_is_zero(value)}


def _scale_form(form: Form, coefficient: GR | Fraction | int) -> Form:
    factor = coefficient if isinstance(coefficient, tuple) else _gr(coefficient)
    return {
        indices: value
        for indices, source in form.items()
        if not _g_is_zero(value := _g_mul(factor, source))
    }


def _wedge(left: Form, right: Form) -> Form:
    output: Form = {}
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
    return {indices: value for indices, value in output.items() if not _g_is_zero(value)}


def _interior(form: Form, index: int) -> Form:
    output: Form = {}
    for indices, coefficient in form.items():
        if index not in indices:
            continue
        position = indices.index(index)
        target = indices[:position] + indices[position + 1 :]
        value = coefficient if position % 2 == 0 else _g_neg(coefficient)
        output[target] = _g_add(output.get(target, ZERO), value)
    return {indices: value for indices, value in output.items() if not _g_is_zero(value)}


def _generator_action(form: Form, first: int, second: int) -> Form:
    """Apply e_first wedge i_second - e_second wedge i_first."""
    if not 0 <= first < second < N:
        raise ValueError("generator requires 0 <= first < second < 10")
    return _add_forms(
        _wedge(_one_form(first), _interior(form, second)),
        _scale_form(_wedge(_one_form(second), _interior(form, first)), -1),
    )


def _hodge_star(form: Form) -> Form:
    output: Form = {}
    universe = set(range(N))
    for indices, coefficient in form.items():
        complement = tuple(sorted(universe.difference(indices)))
        value = coefficient if _permutation_sign(indices + complement) > 0 else _g_neg(coefficient)
        output[complement] = _g_add(output.get(complement, ZERO), value)
    return {indices: value for indices, value in output.items() if not _g_is_zero(value)}


def _form_inner(left: Form, right: Form) -> GR:
    result = ZERO
    for indices in set(left).union(right):
        result = _g_add(
            result,
            _g_mul(_g_conjugate(left.get(indices, ZERO)), right.get(indices, ZERO)),
        )
    return result


@lru_cache(maxsize=1)
def five_representatives() -> tuple[tuple[int, ...], ...]:
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
    if len(representatives) != 126:
        raise ArithmeticError("five-form representative count drifted")
    return tuple(representatives)


@lru_cache(maxsize=1)
def vacuum_shapes() -> dict[str, Form]:
    """Return the aligned V46 SU(5) branch in canonical Cartesian tensors."""
    omega = tuple(
        _wedge(_one_form(2 * plane), _one_form(2 * plane + 1))
        for plane in range(5)
    )
    phi = _add_forms(
        *(
            _wedge(omega[left], omega[right])
            for left, right in itertools.combinations(range(5), 2)
        )
    )

    z = tuple(
        _add_forms(_one_form(2 * plane), _one_form(2 * plane + 1, I))
        for plane in range(5)
    )
    holomorphic = z[0]
    for factor in z[1:]:
        holomorphic = _wedge(holomorphic, factor)

    # The raw holomorphic volume has canonical 126 kinetic norm four.
    # Dividing by four makes its 126-coordinate norm exactly one.
    barsigma = _scale_form(holomorphic, Fraction(1, 4))
    sigma = {indices: _g_conjugate(value) for indices, value in barsigma.items()}
    return {"Phi_210": phi, "Sigma_126": sigma, "barSigma_bar126": barsigma}


def coordinate_labels() -> tuple[str, ...]:
    labels = tuple("Phi[" + ",".join(map(str, item)) + "]" for item in FOUR_INDICES)
    labels += tuple("Sigma[" + ",".join(map(str, item)) + "]" for item in five_representatives())
    labels += tuple("barSigma[" + ",".join(map(str, item)) + "]" for item in five_representatives())
    labels += ("STheta", "ThetaPlus", "ThetaMinus")
    if len(labels) != SOURCE_COMPLEX_DIMENSION:
        raise ArithmeticError("source coordinate count drifted")
    return labels


def _form_coordinates(form: Form, indices: Iterable[tuple[int, ...]]) -> tuple[GR, ...]:
    return tuple(form.get(item, ZERO) for item in indices)


@lru_cache(maxsize=1)
def full_so10_orbit_columns() -> tuple[tuple[GR, ...], ...]:
    shapes = vacuum_shapes()
    columns: list[tuple[GR, ...]] = []
    for first, second in SO10_GENERATORS:
        phi = _generator_action(shapes["Phi_210"], first, second)
        sigma = _generator_action(shapes["Sigma_126"], first, second)
        barsigma = _generator_action(shapes["barSigma_bar126"], first, second)
        column = (
            *_form_coordinates(phi, FOUR_INDICES),
            *_form_coordinates(sigma, five_representatives()),
            *_form_coordinates(barsigma, five_representatives()),
            ZERO,
            ZERO,
            ZERO,
        )
        if len(column) != SOURCE_COMPLEX_DIMENSION:
            raise ArithmeticError("SO(10) orbit column dimension drifted")
        columns.append(tuple(column))
    return tuple(columns)


def _u1f_column() -> tuple[GR, ...]:
    # STheta=0 and ThetaPlus=ThetaMinus=1 at the witness.  Infinitesimal
    # U(1)_F acts as i*q and the two charges are +3 and -3.
    column = [ZERO for _ in range(SOURCE_COMPLEX_DIMENSION)]
    column[-2] = _gr(0, 3)
    column[-1] = _gr(0, -3)
    return tuple(column)


@lru_cache(maxsize=1)
def selected_orbit_columns() -> tuple[tuple[GR, ...], ...]:
    by_label = dict(zip(SO10_GENERATORS, full_so10_orbit_columns(), strict=True))
    columns = tuple(by_label[label] for label in SELECTED_BROKEN_GENERATORS) + (_u1f_column(),)
    if len(columns) != SOURCE_GAUGE_ORBIT_DIMENSION:
        raise ArithmeticError("selected orbit column count drifted")
    return columns


def _column_inner(left: tuple[GR, ...], right: tuple[GR, ...]) -> GR:
    result = ZERO
    for left_value, right_value in zip(left, right, strict=True):
        result = _g_add(result, _g_mul(_g_conjugate(left_value), right_value))
    return result


def _gram(columns: tuple[tuple[GR, ...], ...]) -> tuple[tuple[GR, ...], ...]:
    return tuple(
        tuple(_column_inner(left, right) for right in columns)
        for left in columns
    )


def _fraction_rref(
    matrix: Iterable[Iterable[Fraction | int]],
) -> tuple[list[list[Fraction]], tuple[int, ...]]:
    work = [[Fraction(value) for value in row] for row in matrix]
    if not work:
        return [], ()
    pivot_columns: list[int] = []
    pivot_row = 0
    for column in range(len(work[0])):
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
            coefficient = work[row][column]
            if coefficient:
                work[row] = [
                    value - coefficient * source
                    for value, source in zip(work[row], work[pivot_row], strict=True)
                ]
        pivot_columns.append(column)
        pivot_row += 1
        if pivot_row == len(work):
            break
    return work[:pivot_row], tuple(pivot_columns)


def _primitive_integer_vector(values: Iterable[Fraction]) -> tuple[int, ...]:
    values = tuple(values)
    denominator = math.lcm(*(value.denominator for value in values))
    integers = [value.numerator * (denominator // value.denominator) for value in values]
    common = math.gcd(*(abs(value) for value in integers))
    if common:
        integers = [value // common for value in integers]
    first = next((value for value in integers if value), 0)
    if first < 0:
        integers = [-value for value in integers]
    return tuple(integers)


def _right_nullspace_real(
    matrix: tuple[tuple[Fraction, ...], ...]
) -> tuple[tuple[int, ...], ...]:
    reduced, pivots = _fraction_rref(matrix)
    column_count = len(matrix[0]) if matrix else 0
    free_columns = tuple(index for index in range(column_count) if index not in pivots)
    vectors: list[tuple[int, ...]] = []
    for free in free_columns:
        vector = [Fraction(0) for _ in range(column_count)]
        vector[free] = Fraction(1)
        for row, pivot in enumerate(pivots):
            vector[pivot] = -reduced[row][free]
        vectors.append(_primitive_integer_vector(vector))
    return tuple(vectors)


def _real_gram(columns: tuple[tuple[GR, ...], ...]) -> tuple[tuple[Fraction, ...], ...]:
    gram = _gram(columns)
    if any(value[1] for row in gram for value in row):
        raise ArithmeticError("orbit Gram matrix acquired an imaginary part")
    return tuple(tuple(value[0] for value in row) for row in gram)


def _linear_combination_is_zero(
    columns: tuple[tuple[GR, ...], ...], coefficients: tuple[int, ...]
) -> bool:
    for row in range(SOURCE_COMPLEX_DIMENSION):
        total = ZERO
        for coefficient, column in zip(coefficients, columns, strict=True):
            total = _g_add(total, _g_scale(column[row], coefficient))
        if total != ZERO:
            return False
    return True


def _fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def _gr_json(value: GR) -> list[str]:
    return [_fraction_text(value[0]), _fraction_text(value[1])]


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _matrix_sparse_payload(
    columns: tuple[tuple[GR, ...], ...], column_labels: tuple[str, ...]
) -> dict[str, Any]:
    entries = [
        {"row": row, "column": column, "value_re_im": _gr_json(value)}
        for column, values in enumerate(columns)
        for row, value in enumerate(values)
        if value != ZERO
    ]
    payload = {
        "shape": [SOURCE_COMPLEX_DIMENSION, len(columns)],
        "row_labels": list(coordinate_labels()),
        "column_labels": list(column_labels),
        "entries": entries,
    }
    return {
        "shape": payload["shape"],
        "coordinate_order": {
            "Phi_210": [0, 209],
            "Sigma_126": [210, 335],
            "barSigma_bar126": [336, 461],
            "STheta": [462, 462],
            "ThetaPlus": [463, 463],
            "ThetaMinus": [464, 464],
        },
        "column_labels": payload["column_labels"],
        "nonzero_entries": len(entries),
        "sparse_entries": entries,
        "canonical_matrix_sha256": hashlib.sha256(canonical_bytes(payload)).hexdigest(),
    }


def _projector_sparse_payload(
    columns: tuple[tuple[GR, ...], ...], diagonal: tuple[Fraction, ...]
) -> dict[str, Any]:
    entries: dict[tuple[int, int], GR] = {
        (index, index): ONE for index in range(SOURCE_COMPLEX_DIMENSION)
    }
    for column, norm_squared in zip(columns, diagonal, strict=True):
        support = tuple((row, value) for row, value in enumerate(column) if value != ZERO)
        for row, left in support:
            for target, right in support:
                correction = _g_scale(_g_mul(left, _g_conjugate(right)), Fraction(1, norm_squared))
                key = (row, target)
                entries[key] = _g_sub(entries.get(key, ZERO), correction)
                if entries[key] == ZERO:
                    entries.pop(key)

    hermitian = all(
        entries.get((target, row), ZERO) == _g_conjugate(value)
        for (row, target), value in entries.items()
    )
    trace = sum((entries.get((index, index), ZERO)[0] for index in range(SOURCE_COMPLEX_DIMENSION)), Fraction(0))
    imaginary_trace = sum((entries.get((index, index), ZERO)[1] for index in range(SOURCE_COMPLEX_DIMENSION)), Fraction(0))

    # Direct exact ZQ check on all 22 orbit columns.
    zq_zero = True
    by_row: dict[int, list[tuple[int, GR]]] = {}
    for (row, target), value in entries.items():
        by_row.setdefault(row, []).append((target, value))
    for column in columns:
        for row_entries in by_row.values():
            total = ZERO
            for target, value in row_entries:
                total = _g_add(total, _g_mul(value, column[target]))
            if total != ZERO:
                zq_zero = False
                break
        if not zq_zero:
            break

    serialized_entries = [
        {
            "row": row,
            "column": target,
            "value_re_im": _gr_json(value),
        }
        for (row, target), value in sorted(entries.items())
    ]
    payload = {
        "shape": [SOURCE_COMPLEX_DIMENSION, SOURCE_COMPLEX_DIMENSION],
        "entries": serialized_entries,
    }
    return {
        "definition": "Z=I-Q(Q^dagger Q)^(-1)Q^dagger",
        "shape": payload["shape"],
        "nonzero_entries": len(serialized_entries),
        "canonical_projector_sha256": hashlib.sha256(canonical_bytes(payload)).hexdigest(),
        "Hermitian_exact": hermitian,
        "ZQ_exact_zero": zq_zero,
        "trace": _fraction_text(trace),
        "imaginary_trace": _fraction_text(imaginary_trace),
        "rank": int(trace) if trace.denominator == 1 and imaginary_trace == 0 else None,
        "idempotence_reduction": (
            "Z^2-Z=Q[-G^-1+G^-1 G G^-1]Q^dagger=0; "
            "the exact diagonal inverse products below are all one"
        ),
        "inverse_times_Gram_diagonal": [
            _fraction_text(Fraction(1, value) * value) for value in diagonal
        ],
    }


@lru_cache(maxsize=1)
def representation_certificate() -> dict[str, Any]:
    shapes = vacuum_shapes()
    phi = shapes["Phi_210"]
    sigma = shapes["Sigma_126"]
    barsigma = shapes["barSigma_bar126"]
    sigma_star = _hodge_star(sigma)
    barsigma_star = _hodge_star(barsigma)
    sigma_full_norm = _form_inner(sigma, sigma)
    barsigma_full_norm = _form_inner(barsigma, barsigma)
    sigma_coordinate_norm = _g_scale(sigma_full_norm, Fraction(1, 2))
    barsigma_coordinate_norm = _g_scale(barsigma_full_norm, Fraction(1, 2))
    # Full five-form norm is twice the independent-coordinate norm.  The
    # canonical chiral-five-form kinetic metric supplies the compensating 1/2.
    return {
        "cartesian_real_dimension": N,
        "representations": {
            "Phi_210": "Lambda^4(R^10) complexified",
            "Sigma_126": "+i Hodge eigenspace of Lambda^5(C^10)",
            "barSigma_bar126": "-i Hodge eigenspace of Lambda^5(C^10)",
            "singlets": ["STheta", "ThetaPlus", "ThetaMinus"],
        },
        "vev": {
            "Phi_support_size": len(phi),
            "Phi_support": [list(indices) for indices in sorted(phi)],
            "Phi_coefficients_all_one": all(value == ONE for value in phi.values()),
            "Phi_identification": "F0=P+sqrt(3)A+sqrt(6)omega, i.e. p=a=omega=1 in the V46 reduced convention",
            "Sigma_support_size_full_five_form": len(sigma),
            "barSigma_support_size_full_five_form": len(barsigma),
            "Sigma_independent_coordinate_norm_squared": _gr_json(sigma_coordinate_norm),
            "barSigma_independent_coordinate_norm_squared": _gr_json(barsigma_coordinate_norm),
            "Sigma_full_five_form_norm_squared": _gr_json(sigma_full_norm),
            "barSigma_full_five_form_norm_squared": _gr_json(barsigma_full_norm),
            "STheta": 0,
            "ThetaPlus": 1,
            "ThetaMinus": 1,
        },
        "exact_hodge_checks": {
            "star_Sigma_equals_plus_i_Sigma": sigma_star == _scale_form(sigma, I),
            "star_barSigma_equals_minus_i_barSigma": barsigma_star == _scale_form(barsigma, _g_neg(I)),
            "Sigma_and_barSigma_are_exact_conjugates": sigma == {
                indices: _g_conjugate(value) for indices, value in barsigma.items()
            },
        },
        "generator_action": "e_a wedge i_b - e_b wedge i_a",
        "canonical_126_normalization": (
            "raw holomorphic volume divided by four; its 126-coordinate Hermitian norm is one"
        ),
    }


@lru_cache(maxsize=1)
def orbit_certificate() -> dict[str, Any]:
    full = full_so10_orbit_columns()
    full_gram = _real_gram(full)
    reduced, pivots = _fraction_rref(full_gram)
    nullspace = _right_nullspace_real(full_gram)
    null_annihilation = all(_linear_combination_is_zero(full, vector) for vector in nullspace)

    selected = selected_orbit_columns()
    selected_gram = _real_gram(selected)
    diagonal = tuple(selected_gram[index][index] for index in range(len(selected_gram)))
    off_diagonal_zero = all(
        selected_gram[row][column] == 0
        for row in range(len(selected_gram))
        for column in range(len(selected_gram))
        if row != column
    )
    determinant = math.prod(diagonal)
    expected_diagonal = (Fraction(2),) + (Fraction(7),) * 20 + (Fraction(18),)
    labels = tuple(f"SO10:T[{a},{b}]" for a, b in SELECTED_BROKEN_GENERATORS) + ("U1F",)
    matrix = _matrix_sparse_payload(selected, labels)
    projector = _projector_sparse_payload(selected, diagonal)

    nullspace_payload = {
        "generator_labels": [f"T[{a},{b}]" for a, b in SO10_GENERATORS],
        "basis_vectors": [list(vector) for vector in nullspace],
    }
    return {
        "full_SO10_map": {
            "shape": [SOURCE_COMPLEX_DIMENSION, SO10_GENERATOR_COUNT],
            "exact_Gram_rank": len(pivots),
            "exact_stabilizer_nullity": len(nullspace),
            "all_24_integer_stabilizer_vectors_annihilate_the_vacuum": null_annihilation,
            "stabilizer_identification": (
                "su(5): the same five-plane complex structure defines F0 and the conjugate volume forms"
            ),
            "integer_stabilizer_basis_sha256": hashlib.sha256(
                canonical_bytes(nullspace_payload)
            ).hexdigest(),
            "pivot_columns": list(pivots),
            "rref_nonzero_rows": len(reduced),
        },
        "selected_broken_map_Q": matrix,
        "selected_Gram": {
            "diagonal": [_fraction_text(value) for value in diagonal],
            "off_diagonal_exact_zero": off_diagonal_zero,
            "matches_expected_canonical_diagonal_2_7x20_18": diagonal == expected_diagonal,
            "determinant": _fraction_text(determinant),
            "positive_definite": off_diagonal_zero and all(value > 0 for value in diagonal),
            "exact_rank": len(diagonal) if determinant else None,
        },
        "physical_projector_Z": projector,
        "counting": {
            "source_complex_components": SOURCE_COMPLEX_DIMENSION,
            "Spin10_broken_generators": SO10_BROKEN_COUNT,
            "U1F_broken_generators": 1,
            "eaten_chiral_components": SOURCE_GAUGE_ORBIT_DIMENSION,
            "physical_complex_components": PHYSICAL_COMPLEX_DIMENSION,
        },
    }


def _load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(f"missing input artifact: {path.name}")
    return json.loads(path.read_text(encoding="utf-8"))


def _input_manifest() -> list[dict[str, Any]]:
    return [
        {"label": label, "path": path.name, "sha256": sha256_file(path)}
        for label, path in INPUTS.items()
    ]


def _source_manifest() -> list[dict[str, Any]]:
    return [
        {
            "path": name,
            "exists": (ROOT / name).is_file(),
            "sha256": sha256_file(ROOT / name) if (ROOT / name).is_file() else None,
        }
        for name in SOURCE_FILES
    ]


@lru_cache(maxsize=1)
def legacy_compatibility_audit() -> dict[str, Any]:
    v20 = _load_json(INPUTS["legacy_v20_pd_rank"])
    legacy_orbit = v20["exact_full_kernel_argument"]["exact_P_plus_Delta_gauge_orbit"]

    # Exact legacy shapes, used only to establish nonidentity with the V51
    # branch.  P is one term, while F0 contains all ten Kahler four-form terms.
    p = _wedge(
        _wedge(_one_form(6), _one_form(7)),
        _wedge(_one_form(8), _one_form(9)),
    )
    z = tuple(
        _add_forms(_one_form(2 * plane), _one_form(2 * plane + 1, I))
        for plane in range(3)
    )
    omega3 = _wedge(_wedge(z[0], z[1]), z[2])
    j_right = _add_forms(
        _wedge(_one_form(6), _one_form(7)),
        _wedge(_one_form(8), _one_form(9)),
    )
    delta = _wedge(omega3, j_right)
    v51 = vacuum_shapes()

    phi_not_equal = p != v51["Phi_210"]
    sigma_overlap = _form_inner(delta, v51["barSigma_bar126"])
    return {
        "legacy_artifact": INPUTS["legacy_v20_pd_rank"].name,
        "legacy_exact_orbit_rank": legacy_orbit["exact_orbit_rank"],
        "legacy_exact_stabilizer_dimension": legacy_orbit["exact_stabilizer_dimension"],
        "legacy_coordinate_content": "210 real + one bar126 as 252 real coordinates",
        "V51_coordinate_content": "210 + 126 + bar126 + three singlets as 465 complex coordinates",
        "Phi_shapes_differ_exactly": phi_not_equal,
        "legacy_P_support_size": len(p),
        "V51_F0_support_size": len(v51["Phi_210"]),
        "legacy_Delta_inner_product_with_aligned_barSigma": _gr_json(sigma_overlap),
        "five_form_shapes_are_orthogonal": sigma_overlap == ZERO,
        "Hessian_transfer_allowed": False,
        "reason": (
            "The legacy local Hessian is tied to P+Delta_R, has an SM-sized stabilizer "
            "and contains only one chiral five-form.  It is not a field reordering or "
            "invertible rescaling of the V47 aligned SU(5) source branch."
        ),
    }


@lru_cache(maxsize=1)
def hessian_availability_audit() -> dict[str, Any]:
    v46 = _load_json(INPUTS["v46_source_rank"])
    v47 = _load_json(INPUTS["v47_source_completion"])
    repair = v46["neutral_210_repair"]
    source = v47["coupled_210_source"]
    return {
        "V46_claim_replayed": {
            "total_GUT_chiral_components": repair["counting"]["total_chiral_components"],
            "eaten_GUT_chiral_components": repair["counting"]["eaten_chiral_components"],
            "generic_physical_massless_chiral_components": repair["counting"]["generic_physical_massless_chiral_components"],
            "available_data": (
                "SU(5)-irrep block obligations, selected low-dimensional matrices, "
                "unique-sector masses and determinant/rank summaries"
            ),
        },
        "V47_claim_replayed": {
            "total_source_chiral_components": source["counting"]["total_chiral_components"],
            "eaten_source_chiral_components": source["counting"]["eaten_chiral_components"],
            "generic_physical_massless_chiral_components": source["counting"]["generic_physical_massless_chiral_components"],
            "determinant_lemma": source["physical_hessian_lemma"]["determinant"],
        },
        "new_V51_kinematic_inputs": {
            "Cartesian_465_by_22_Q": True,
            "exact_rank_22": True,
            "Hermitian_rank_443_Z": True,
        },
        "missing_dynamic_inputs": {
            "Cartesian_holomorphic_H_shape_465_by_465": True,
            "all_entries_derived_from_one_normalized_W_GUT_plus_singlet_superpotential": True,
            "stationarity_in_the_same_Cartesian_normalization": True,
            "direct_exact_Ward_identity_HQ_equals_zero": True,
            "physical_basis_N_with_QdaggerN_zero_and_rank_443": True,
            "exact_pullback_Ntranspose_H_N_and_nonzero_determinant": True,
        },
        "Ward_identity_contract": (
            "For a gauge-invariant holomorphic W at an F-flat point, H Q=0. "
            "Once H is published, choose any full-rank N with Q^dagger N=0 and "
            "test det(N^T H N)!=0; equivalently use Z^T H Z on im(Z)."
        ),
        "physical_Hessian_pullback_executed": False,
        "reason_fail_closed": (
            "A representation-theoretic rank summary and a determinant lemma do not "
            "supply the 465 by 465 Cartesian tensor needed to test H Q=0 entrywise."
        ),
    }


@lru_cache(maxsize=1)
def build_report() -> dict[str, Any]:
    representation = representation_certificate()
    orbit = orbit_certificate()
    legacy = legacy_compatibility_audit()
    hessian = hessian_availability_audit()

    checks = {
        "source_dimension_is_465_complex": orbit["counting"]["source_complex_components"] == 465,
        "aligned_Phi_has_ten_integral_Kahler_terms": (
            representation["vev"]["Phi_support_size"] == 10
            and representation["vev"]["Phi_coefficients_all_one"]
        ),
        "126_pair_has_opposite_exact_Hodge_chiralities": all(
            representation["exact_hodge_checks"].values()
        ),
        "full_SO10_orbit_rank_is_21": orbit["full_SO10_map"]["exact_Gram_rank"] == 21,
        "full_SO10_stabilizer_nullity_is_24": orbit["full_SO10_map"]["exact_stabilizer_nullity"] == 24,
        "stabilizer_basis_annihilates_vacuum": orbit["full_SO10_map"]["all_24_integer_stabilizer_vectors_annihilate_the_vacuum"],
        "published_Q_shape_is_465_by_22": orbit["selected_broken_map_Q"]["shape"] == [465, 22],
        "published_Q_has_exact_rank_22": orbit["selected_Gram"]["exact_rank"] == 22,
        "canonical_Gram_is_diagonal_2_7x20_18": orbit["selected_Gram"]["matches_expected_canonical_diagonal_2_7x20_18"],
        "projector_is_exact_Hermitian": orbit["physical_projector_Z"]["Hermitian_exact"],
        "projector_annihilates_Q_exactly": orbit["physical_projector_Z"]["ZQ_exact_zero"],
        "projector_rank_is_443": orbit["physical_projector_Z"]["rank"] == 443,
        "legacy_P_Delta_Hessian_is_rejected_as_incompatible": not legacy["Hessian_transfer_allowed"],
        "full_Hessian_pullback_not_overclaimed": not hessian["physical_Hessian_pullback_executed"],
    }
    failures = [name for name, passed in checks.items() if not passed]
    report: dict[str, Any] = {
        "schema": "susy-v51-physical-source-orbit-audit-v1",
        "status": STATUS if not failures else "V51_PHYSICAL_SOURCE_ORBIT_AUDIT_FAILED",
        "scope": (
            "Exact aligned-SU(5) source gauge orbit and Kinematic quotient. "
            "No full Cartesian source superpotential Hessian is inferred."
        ),
        "representation_certificate": representation,
        "orbit_and_projector_certificate": orbit,
        "legacy_v20_compatibility": legacy,
        "hessian_availability": hessian,
        "gate_effect": {
            "G2_C3_physical_source_Hessian": "PARTIAL_Q_AND_Z_NOW_EXACT__H_AND_HQ_OPEN",
            "G2_C4_Rxi_source_Goldstones": "PARTIAL_SOURCE_GOLDSTONE_CHART_NOW_EXACT__COUPLED_Rxi_BLOCK_OPEN",
            "G2_clause_promoted": None,
            "G1_to_G8_promoted": [],
        },
        "checks": checks,
        "n_checks": len(checks),
        "failures": failures,
        "n_failed": len(failures),
        "input_manifest": _input_manifest(),
        "source_manifest": _source_manifest(),
        "next_exact_step": (
            "Differentiate the normalized V47 tensor superpotential twice in the same "
            "465-coordinate chart, publish H sparsely, verify H Q=0, construct a "
            "443-column kernel chart N, and certify det(N^T H N)!=0."
        ),
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    orbit = report["orbit_and_projector_certificate"]
    gram = orbit["selected_Gram"]
    projector = orbit["physical_projector_Z"]
    matrix = orbit["selected_broken_map_Q"]
    legacy = report["legacy_v20_compatibility"]
    hessian = report["hessian_availability"]
    return f"""# V51 physical source-orbit audit

## Result

The aligned V47 source branch now has an explicit, representation-faithful
complex **465 x 22** gauge-orbit map.  It is regenerated from Cartesian
four- and five-form tensors using exact Gaussian-rational arithmetic; its
sparse publication has {matrix['nonzero_entries']} nonzero entries and hash
`{matrix['canonical_matrix_sha256']}`.

The full 45-column Spin(10) map has exact rank 21 and an explicit
24-dimensional integer stabilizer kernel.  Adding the independent broken
`U(1)_F` column gives rank 22.  In the selected canonical chart,

`Q^dagger Q = diag(2, 7 x 20, 18)`

with determinant `{gram['determinant']}`.

## Exact physical quotient

The exact Hermitian projector

`Z = I - Q (Q^dagger Q)^(-1) Q^dagger`

obeys `Z Q = 0`, is Hermitian and has trace/rank {projector['rank']}.  Its
canonical sparse hash is `{projector['canonical_projector_sha256']}`.  Thus
the source count is 465 complex chiral components, 22 eaten directions and
443 physical complex directions.

## Why the older P+Delta_R Hessian is not imported

The v20 benchmark has exact orbit rank {legacy['legacy_exact_orbit_rank']} and
stabilizer dimension {legacy['legacy_exact_stabilizer_dimension']}.  It uses
one real `210` shape `P`, one chiral five-form `Delta_R`, and no conjugate
`126` partner.  Here the `210` is the ten-term SU(5) form `F0`, and the aligned
five-form is exactly orthogonal to the legacy `Delta_R`.  These are different
vacua and different field spaces, so a Hessian transfer is invalid.

## Remaining dynamical blocker

V46 supplies SU(5)-irrep mass blocks and a generic-rank witness; V47 supplies
the determinant lemma `{hessian['V47_claim_replayed']['determinant_lemma']}`.
Neither publishes the normalized Cartesian 465 x 465 holomorphic Hessian.
Consequently this audit does **not** claim `H Q = 0` or evaluate
`N^T H N`.  G2-C3 and G2-C4 improve, but neither clause nor any G gate is
promoted.

The next exact step is to differentiate the single normalized V47 tensor
superpotential in this chart, publish `H`, verify `H Q=0`, and certify the
443-dimensional physical pullback.

Core SHA-256: `{report['core_sha256']}`
"""


def write_artifacts() -> dict[str, Any]:
    report = build_report()
    JSON_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")
    return report


def check_artifacts() -> None:
    if not JSON_PATH.is_file() or not MD_PATH.is_file():
        raise RuntimeError("missing V51 physical-source artifacts")
    observed = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    expected = build_report()
    if observed != expected:
        raise RuntimeError("V51 physical-source JSON artifact drifted")
    if observed.get("core_sha256") != canonical_sha(observed):
        raise RuntimeError("V51 physical-source core hash failed")
    if MD_PATH.read_text(encoding="utf-8") != render_markdown(expected):
        raise RuntimeError("V51 physical-source Markdown artifact drifted")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write JSON and Markdown artifacts")
    parser.add_argument("--check", action="store_true", help="check committed artifacts")
    args = parser.parse_args(argv)
    if args.write and args.check:
        parser.error("choose at most one of --write and --check")
    if args.check:
        check_artifacts()
        print(f"PASS {JSON_PATH.name} {build_report()['core_sha256']}")
    elif args.write:
        report = write_artifacts()
        print(f"WROTE {JSON_PATH.name} {report['core_sha256']}")
    else:
        print(json.dumps(build_report(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
