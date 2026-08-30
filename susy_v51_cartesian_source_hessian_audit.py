#!/usr/bin/env python3
"""V51 exact Cartesian source-superpotential Hessian audit.

This module differentiates one normalized renormalizable source
superpotential in the exact 465-complex-coordinate chart published by
``susy_v51_physical_source_orbit_audit``.  The GUT part is

  W_G = m/(4!) Phi Phi + lambda/(4!) Phi Phi Phi
      + M/(2*5!) Sigma barSigma
      + eta/(2*4!) Phi Sigma barSigma.

The factors of one half in the chiral-five-form contractions are required
because the 126 coordinates retain one representative from each Hodge-paired
five-form component.  They are independently calibrated by recovering

  W_red = m(p^2+3a^2+6w^2)
        + 2 lambda(a^3+3 p w^2+6 a w^2)
        + M sigma barsigma
        + eta sigma barsigma(p+3a+6w).

At the exact V46 witness

  m=-7/2, M=-10, lambda=eta=p=a=w=sigma=barsigma=1,

all 462 Cartesian GUT F terms vanish.  The source-singlet completion uses the
explicit matching-scale point

  W_Theta = STheta(ThetaPlus ThetaMinus - 1),

or kappa=1, f1=-1, f2=0, m1=M1=0 at STheta=0 and
ThetaPlus=ThetaMinus=1.  The zero cross couplings are a tuned witness, not a
selector-symmetry prediction.

The complete complex-symmetric 465 x 465 Hessian is published as exact
Gaussian-rational sparse data with common denominator four.  It annihilates
all 45 Spin(10) orbit columns and the U(1)_F column exactly.  Reduction modulo
13, using i -> 5, gives rank 443.  Together with the exact rank-22 orbit in
its kernel this proves characteristic-zero rank 443 and nullity 22.  A
443-dimensional physical pullback is also certified nondegenerate modulo 13.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

import numpy as np
from scipy import sparse

import susy_v51_physical_source_orbit_audit as orbit


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V51_CARTESIAN_SOURCE_HESSIAN_AUDIT.json"
MD_PATH = ROOT / "SUSY_V51_CARTESIAN_SOURCE_HESSIAN_AUDIT.md"

INPUTS = {
    "v51_orbit": ROOT / "SUSY_V51_PHYSICAL_SOURCE_ORBIT_AUDIT.json",
    "v46_source_rank": ROOT / "SUSY_V46_SOURCE_HIGGS_RANK_AUDIT.json",
    "v47_source_completion": ROOT / "SUSY_V47_SOURCE_COMPLETION_ROUTE_AUDIT.json",
}
SOURCE_FILES = (
    "susy_v51_cartesian_source_hessian_audit.py",
    "test_susy_v51_cartesian_source_hessian_audit.py",
    "susy_v51_physical_source_orbit_audit.py",
    *(path.name for path in INPUTS.values()),
)

STATUS = (
    "V51_EXACT_NORMALIZED_CARTESIAN_465_SOURCE_HESSIAN_RANK_443_NULLITY_22__"
    "ALL_SPIN10_AND_U1F_WARD_COLUMNS_EXACTLY_NULL__PHYSICAL_443_PULLBACK_"
    "NONDEGENERATE__TUNED_MATCHING_SCALE_WITNESS_NOT_SELECTOR_PROTECTED__"
    "NO_G2_CLAUSE_PROMOTED"
)

GUT_DIMENSION = 210 + 126 + 126
SOURCE_DIMENSION = 465
HESSIAN_DENOMINATOR = 4
MODULAR_PRIME = 13
MODULAR_I = 5
THREE_INDICES = tuple(itertools.combinations(range(10), 3))
TWO_INDICES = tuple(itertools.combinations(range(10), 2))


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_hashed_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(f"missing input artifact: {path.name}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if "core_sha256" in payload and canonical_sha(payload) != payload["core_sha256"]:
        raise RuntimeError(f"bad input core hash: {path.name}")
    return payload


def _complex_from_gr(value: orbit.GR) -> complex:
    return complex(float(value[0]), float(value[1]))


def _form_bilinear(left: orbit.Form, right: orbit.Form) -> orbit.GR:
    """Holomorphic tensor contraction, with no complex conjugation."""
    result = orbit.ZERO
    for indices in set(left).union(right):
        result = orbit._g_add(
            result,
            orbit._g_mul(left.get(indices, orbit.ZERO), right.get(indices, orbit.ZERO)),
        )
    return result


def _gaussian_integer_parts(values: np.ndarray, *, label: str) -> tuple[np.ndarray, np.ndarray]:
    array = np.asarray(values, dtype=complex)
    real = np.rint(array.real).astype(np.int64)
    imaginary = np.rint(array.imag).astype(np.int64)
    residual = max(
        float(np.max(np.abs(array.real - real), initial=0.0)),
        float(np.max(np.abs(array.imag - imaginary), initial=0.0)),
    )
    if residual != 0.0:
        raise ArithmeticError(f"{label} left the Gaussian-integer lattice: {residual}")
    return real, imaginary


def _chiral_basis(chirality: str) -> tuple[orbit.Form, ...]:
    """Canonical independent-coordinate Hodge basis with representative 1."""
    if chirality not in {"+i", "-i"}:
        raise ValueError(chirality)
    universe = set(range(10))
    result: list[orbit.Form] = []
    for representative in orbit.five_representatives():
        complement = tuple(sorted(universe.difference(representative)))
        sign = orbit._permutation_sign(representative + complement)
        imaginary = -sign if chirality == "+i" else sign
        result.append(
            {
                representative: orbit.ONE,
                complement: orbit._gr(0, imaginary),
            }
        )
    return tuple(result)


def _double_interior(form: orbit.Form, first: int, second: int) -> orbit.Form:
    return orbit._interior(orbit._interior(form, first), second)


def _double_interior_matrix(
    basis: tuple[orbit.Form, ...], pair: tuple[int, int]
) -> sparse.csr_matrix:
    three_index = {indices: row for row, indices in enumerate(THREE_INDICES)}
    rows: list[int] = []
    columns: list[int] = []
    values: list[complex] = []
    for column, state in enumerate(basis):
        for indices, value in _double_interior(state, pair[0], pair[1]).items():
            rows.append(three_index[indices])
            columns.append(column)
            values.append(_complex_from_gr(value))
    return sparse.csr_matrix(
        (values, (rows, columns)), shape=(len(THREE_INDICES), 126), dtype=complex
    )


def _phi_operator_basis() -> np.ndarray:
    """Return B_I with (B_I)_[ab],[cd]=(e_I)_abcd."""
    index = {indices: position for position, indices in enumerate(orbit.FOUR_INDICES)}
    basis = np.zeros((210, 45, 45), dtype=np.int8)
    for row, left in enumerate(TWO_INDICES):
        for column, right in enumerate(TWO_INDICES):
            if set(left).intersection(right):
                continue
            sequence = left + right
            indices = tuple(sorted(sequence))
            basis[index[indices], row, column] = orbit._permutation_sign(sequence)
    return basis


def _vacuum_coordinate_vectors() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    shapes = orbit.vacuum_shapes()
    phi = np.asarray(
        [
            _complex_from_gr(shapes["Phi_210"].get(indices, orbit.ZERO))
            for indices in orbit.FOUR_INDICES
        ],
        dtype=complex,
    )
    sigma = np.asarray(
        [
            _complex_from_gr(shapes["Sigma_126"].get(indices, orbit.ZERO))
            for indices in orbit.five_representatives()
        ],
        dtype=complex,
    )
    barsigma = np.asarray(
        [
            _complex_from_gr(shapes["barSigma_bar126"].get(indices, orbit.ZERO))
            for indices in orbit.five_representatives()
        ],
        dtype=complex,
    )
    return phi, sigma, barsigma


@lru_cache(maxsize=1)
def _gut_tensor_data() -> dict[str, np.ndarray]:
    """Build every Hessian block from the normalized tensor contractions."""
    phi0_complex, sigma0, barsigma0 = _vacuum_coordinate_vectors()
    phi0_real, phi0_imaginary = _gaussian_integer_parts(phi0_complex, label="Phi vacuum")
    if np.any(phi0_imaginary):
        raise ArithmeticError("aligned Phi vacuum must be real")
    phi0 = phi0_real

    phi_basis = _phi_operator_basis()
    a0 = np.tensordot(phi0, phi_basis, axes=1).astype(np.int64)

    # Hessian of (lambda/3) Tr(A_Phi^3):
    # Tr[A(B_I B_J+B_J B_I)].
    left_products = np.einsum("ab,ibc->iac", a0, phi_basis, optimize=True)
    ordered = (
        left_products.reshape(210, -1)
        @ phi_basis.transpose(0, 2, 1).reshape(210, -1).T
    ).astype(np.int64)
    phi_hessian = -7 * np.eye(210, dtype=np.int64) + ordered + ordered.T

    # Gradient of (lambda/3) Tr(A^3) is Tr(A^2 B_I).
    cubic_gradient = np.einsum(
        "ab,bc,ica->i", a0, a0, phi_basis, optimize=True
    ).astype(np.int64)

    sigma_basis = _chiral_basis("+i")
    barsigma_basis = _chiral_basis("-i")
    d_sigma = {
        pair: _double_interior_matrix(sigma_basis, pair)
        for pair in TWO_INDICES
    }
    d_barsigma = {
        pair: _double_interior_matrix(barsigma_basis, pair)
        for pair in TWO_INDICES
    }

    phi_sigma_cross = np.zeros((210, 126), dtype=complex)
    phi_barsigma_cross = np.zeros((210, 126), dtype=complex)
    eta_phi_gradient = np.zeros(210, dtype=complex)
    sigma_barsigma = sparse.csr_matrix((126, 126), dtype=complex)

    for phi_index, (i, j, k, ell) in enumerate(orbit.FOUR_INDICES):
        # This is the half-normalized independent-coordinate form of
        # (1/4!) Phi_ijkl Sigma_ijmno barSigma_klmno.
        operator = (
            d_sigma[(i, j)].T @ d_barsigma[(k, ell)]
            - d_sigma[(i, k)].T @ d_barsigma[(j, ell)]
            + d_sigma[(i, ell)].T @ d_barsigma[(j, k)]
        ).tocsr()
        phi_sigma_cross[phi_index] = operator @ barsigma0
        phi_barsigma_cross[phi_index] = operator.T @ sigma0
        eta_phi_gradient[phi_index] = sigma0 @ (operator @ barsigma0)
        if phi0[phi_index]:
            sigma_barsigma = sigma_barsigma + int(phi0[phi_index]) * operator

    sigma_barsigma_dense = sigma_barsigma.toarray()
    sigma_barsigma_block = -10 * np.eye(126, dtype=complex) + sigma_barsigma_dense

    gradient_phi = -7 * phi0 + cubic_gradient + eta_phi_gradient
    gradient_sigma = sigma_barsigma_block @ barsigma0
    gradient_barsigma = sigma_barsigma_block.T @ sigma0

    return {
        "phi0": phi0,
        "sigma0": sigma0,
        "barsigma0": barsigma0,
        "phi_operator_basis": phi_basis,
        "a0": a0,
        "phi_hessian": phi_hessian,
        "phi_sigma_cross": phi_sigma_cross,
        "phi_barsigma_cross": phi_barsigma_cross,
        "sigma_barsigma_block": sigma_barsigma_block,
        "gradient_phi": gradient_phi,
        "gradient_sigma": gradient_sigma,
        "gradient_barsigma": gradient_barsigma,
    }


@lru_cache(maxsize=1)
def exact_scaled_hessian() -> tuple[np.ndarray, np.ndarray]:
    """Return H_REAL*4 and H_IMAG*4 as exact int64 matrices."""
    data = _gut_tensor_data()
    hessian = np.zeros((SOURCE_DIMENSION, SOURCE_DIMENSION), dtype=complex)
    hessian[:210, :210] = data["phi_hessian"]
    hessian[:210, 210:336] = data["phi_sigma_cross"]
    hessian[210:336, :210] = data["phi_sigma_cross"].T
    hessian[:210, 336:462] = data["phi_barsigma_cross"]
    hessian[336:462, :210] = data["phi_barsigma_cross"].T
    hessian[210:336, 336:462] = data["sigma_barsigma_block"]
    hessian[336:462, 210:336] = data["sigma_barsigma_block"].T

    # Tuned but allowed V47 matching-scale point:
    # W_Theta=STheta(ThetaPlus ThetaMinus-1).
    hessian[462:465, 462:465] = np.asarray(
        [[0, 1, 1], [1, 0, 0], [1, 0, 0]], dtype=complex
    )
    return _gaussian_integer_parts(
        HESSIAN_DENOMINATOR * hessian,
        label="four-times Cartesian source Hessian",
    )


def _scaled_orbit_matrix(*, all_so10_columns: bool) -> tuple[np.ndarray, np.ndarray]:
    columns = (
        orbit.full_so10_orbit_columns()
        if all_so10_columns
        else orbit.selected_orbit_columns()[:-1]
    )
    columns = tuple(columns) + (orbit._u1f_column(),)
    real = np.zeros((SOURCE_DIMENSION, len(columns)), dtype=np.int64)
    imaginary = np.zeros_like(real)
    for column_index, column in enumerate(columns):
        for row, value in enumerate(column):
            scaled_real = value[0] * HESSIAN_DENOMINATOR
            scaled_imaginary = value[1] * HESSIAN_DENOMINATOR
            if scaled_real.denominator != 1 or scaled_imaginary.denominator != 1:
                raise ArithmeticError("orbit map misses denominator-four lattice")
            real[row, column_index] = scaled_real.numerator
            imaginary[row, column_index] = scaled_imaginary.numerator
    return real, imaginary


def _gaussian_matrix_product(
    left_real: np.ndarray,
    left_imaginary: np.ndarray,
    right_real: np.ndarray,
    right_imaginary: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    return (
        left_real @ right_real - left_imaginary @ right_imaginary,
        left_real @ right_imaginary + left_imaginary @ right_real,
    )


def _modular_rref_metadata(
    matrix: np.ndarray, prime: int
) -> tuple[int, tuple[int, ...], int | None]:
    work = np.asarray(matrix, dtype=np.int64).copy() % prime
    rows, columns = work.shape
    pivot_columns: list[int] = []
    pivot_row = 0
    determinant = 1
    swap_sign = 1
    for column in range(columns):
        candidates = np.flatnonzero(work[pivot_row:, column])
        if candidates.size == 0:
            continue
        selected = pivot_row + int(candidates[0])
        if selected != pivot_row:
            work[[pivot_row, selected]] = work[[selected, pivot_row]]
            swap_sign = -swap_sign
        pivot = int(work[pivot_row, column])
        determinant = (determinant * pivot) % prime
        inverse = pow(pivot, -1, prime)
        work[pivot_row] = (work[pivot_row] * inverse) % prime
        factors = work[:, column].copy()
        factors[pivot_row] = 0
        nonzero_rows = np.flatnonzero(factors)
        if nonzero_rows.size:
            work[nonzero_rows] = (
                work[nonzero_rows]
                - factors[nonzero_rows, None] * work[pivot_row]
            ) % prime
        pivot_columns.append(column)
        pivot_row += 1
        if pivot_row == rows:
            break
    square_determinant: int | None = None
    if rows == columns:
        square_determinant = (
            swap_sign * determinant % prime if pivot_row == rows else 0
        )
    return pivot_row, tuple(pivot_columns), square_determinant


def _matrix_sparse_payload(real: np.ndarray, imaginary: np.ndarray) -> dict[str, Any]:
    entries = [
        [row, column, int(real[row, column]), int(imaginary[row, column])]
        for row in range(SOURCE_DIMENSION)
        for column in range(row, SOURCE_DIMENSION)
        if real[row, column] or imaginary[row, column]
    ]
    payload = {
        "shape": [SOURCE_DIMENSION, SOURCE_DIMENSION],
        "common_denominator": HESSIAN_DENOMINATOR,
        "storage": "upper triangle; reflect without conjugation because H^T=H",
        "coordinate_labels": list(orbit.coordinate_labels()),
        "entries_row_column_scaled_real_scaled_imaginary": entries,
    }
    return {
        **payload,
        "upper_triangle_nonzero_entries": len(entries),
        "full_matrix_nonzero_entries": int(np.count_nonzero((real != 0) | (imaginary != 0))),
        "canonical_H_sha256": hashlib.sha256(canonical_bytes(payload)).hexdigest(),
    }


def normalization_certificate() -> dict[str, Any]:
    data = _gut_tensor_data()
    phi_basis = data["phi_operator_basis"]

    # Raw Aulakh p,a,omega basis: 1, 3 and 6 equal-weight Kahler terms.
    planes = tuple((2 * index, 2 * index + 1) for index in range(5))
    phi_index = {indices: position for position, indices in enumerate(orbit.FOUR_INDICES)}
    p_vector = np.zeros(210, dtype=np.int64)
    a_vector = np.zeros(210, dtype=np.int64)
    omega_vector = np.zeros(210, dtype=np.int64)
    p_vector[phi_index[tuple(sorted(planes[3] + planes[4]))]] = 1
    for left, right in itertools.combinations(range(3), 2):
        a_vector[phi_index[tuple(sorted(planes[left] + planes[right]))]] = 1
    for left in range(3):
        for right in range(3, 5):
            omega_vector[phi_index[tuple(sorted(planes[left] + planes[right]))]] = 1

    vectors = {"p": p_vector, "a": a_vector, "omega": omega_vector}
    operators = {
        name: np.tensordot(vector, phi_basis, axes=1).astype(np.int64)
        for name, vector in vectors.items()
    }
    cubic_coefficients: dict[str, int] = {}
    names = tuple(vectors)
    for first in names:
        for second in names:
            for third in names:
                powers = tuple(sorted((first, second, third)))
                label = "*".join(powers)
                value = int(np.trace(operators[first] @ operators[second] @ operators[third]))
                cubic_coefficients[label] = cubic_coefficients.get(label, 0) + value
    for label, value in tuple(cubic_coefficients.items()):
        quotient, remainder = divmod(value, 3)
        if remainder:
            raise ArithmeticError("Tr(A^3)/3 coefficient left Z")
        cubic_coefficients[label] = quotient
    cubic_coefficients = {
        label: value for label, value in cubic_coefficients.items() if value
    }

    # Rebuild the three eta operators by summing the same exact K_I blocks.
    sigma_basis = _chiral_basis("+i")
    barsigma_basis = _chiral_basis("-i")
    d_sigma = {pair: _double_interior_matrix(sigma_basis, pair) for pair in TWO_INDICES}
    d_barsigma = {pair: _double_interior_matrix(barsigma_basis, pair) for pair in TWO_INDICES}
    eta_coefficients: dict[str, int] = {}
    sigma0 = data["sigma0"]
    barsigma0 = data["barsigma0"]
    for name, vector in vectors.items():
        operator = sparse.csr_matrix((126, 126), dtype=complex)
        for coefficient, (i, j, k, ell) in zip(vector, orbit.FOUR_INDICES, strict=True):
            if not coefficient:
                continue
            operator += int(coefficient) * (
                d_sigma[(i, j)].T @ d_barsigma[(k, ell)]
                - d_sigma[(i, k)].T @ d_barsigma[(j, ell)]
                + d_sigma[(i, ell)].T @ d_barsigma[(j, k)]
            )
        value = sigma0 @ (operator @ barsigma0)
        real, imaginary = _gaussian_integer_parts(np.asarray([value]), label=f"eta {name}")
        if imaginary[0]:
            raise ArithmeticError("eta reduced coefficient became imaginary")
        eta_coefficients[name] = int(real[0])

    sigma_pair_full = _form_bilinear(
        orbit.vacuum_shapes()["Sigma_126"],
        orbit.vacuum_shapes()["barSigma_bar126"],
    )
    pair_coefficient = orbit._g_scale(sigma_pair_full, 1 / 2)
    return {
        "tensor_superpotential": (
            "m/(4!) Phi_ijkl Phi_ijkl + lambda/(4!) Phi_ijkl Phi_klmn Phi_mnij "
            "+ M/(2*5!) Sigma_ijklm barSigma_ijklm "
            "+ eta/(2*4!) Phi_ijkl Sigma_ijmno barSigma_klmno"
        ),
        "half_factor_reason": (
            "A chiral five-form has two Hodge-related full tensor components per "
            "independent 126 coordinate.  The explicit 1/2 removes that double count."
        ),
        "quadratic_Phi_weights_p_a_omega": {
            name: int(vector @ vector) for name, vector in vectors.items()
        },
        "cubic_Tr_A3_over_3_nonzero_coefficients": cubic_coefficients,
        "Sigma_barSigma_half_contraction_at_unit_singlets_re_im": [
            str(pair_coefficient[0]), str(pair_coefficient[1])
        ],
        "eta_linear_coefficients_p_a_omega": eta_coefficients,
        "recovered_reduced_W": (
            "m(p^2+3a^2+6omega^2)+2lambda(a^3+3p omega^2+6a omega^2)"
            "+M sigma barsigma+eta sigma barsigma(p+3a+6omega)"
        ),
    }


def stationarity_certificate() -> dict[str, Any]:
    data = _gut_tensor_data()
    gradients = np.concatenate(
        (
            data["gradient_phi"],
            data["gradient_sigma"],
            data["gradient_barsigma"],
            np.asarray(
                [1 * 1 - 1, 0 * 1, 0 * 1],
                dtype=complex,
            ),
        )
    )
    scaled_real, scaled_imaginary = _gaussian_integer_parts(
        16 * gradients, label="sixteen-times source F terms"
    )
    return {
        "parameters": {
            "m": "-7/2",
            "M": -10,
            "lambda": 1,
            "eta": 1,
            "p": 1,
            "a": 1,
            "omega": 1,
            "sigma": 1,
            "barsigma": 1,
            "kappa": 1,
            "STheta": 0,
            "ThetaPlus": 1,
            "ThetaMinus": 1,
            "f1": -1,
            "f2": 0,
            "m1": 0,
            "M1": 0,
        },
        "matching_scale_tuning": (
            "m1=M1=0 is an allowed parameter point but is not enforced by the V47 "
            "symmetry audit and is not claimed radiatively stable."
        ),
        "scaled_F_term_denominator": 16,
        "maximum_abs_scaled_real_F_term": int(np.max(np.abs(scaled_real), initial=0)),
        "maximum_abs_scaled_imaginary_F_term": int(np.max(np.abs(scaled_imaginary), initial=0)),
        "all_465_F_terms_exact_zero": not np.any(scaled_real) and not np.any(scaled_imaginary),
        "D_flatness": "|sigma|=|barsigma| and |ThetaPlus|=|ThetaMinus|",
    }


@lru_cache(maxsize=1)
def hessian_certificate() -> dict[str, Any]:
    real, imaginary = exact_scaled_hessian()
    symmetric = np.array_equal(real, real.T) and np.array_equal(imaginary, imaginary.T)

    all_q_real, all_q_imaginary = _scaled_orbit_matrix(all_so10_columns=True)
    ward_real, ward_imaginary = _gaussian_matrix_product(
        real, imaginary, all_q_real, all_q_imaginary
    )
    ward_exact = not np.any(ward_real) and not np.any(ward_imaginary)

    h_mod = (real + MODULAR_I * imaginary) % MODULAR_PRIME
    full_rank_mod, _full_pivots, full_determinant_mod = _modular_rref_metadata(
        h_mod, MODULAR_PRIME
    )

    selected_q_real, selected_q_imaginary = _scaled_orbit_matrix(
        all_so10_columns=False
    )
    q_mod = (selected_q_real + MODULAR_I * selected_q_imaginary) % MODULAR_PRIME
    q_rank_mod, pivot_rows, _ = _modular_rref_metadata(q_mod.T, MODULAR_PRIME)
    free_rows = tuple(index for index in range(SOURCE_DIMENSION) if index not in pivot_rows)
    pullback_mod = h_mod[np.ix_(free_rows, free_rows)]
    pullback_rank_mod, _pullback_pivots, pullback_determinant_mod = _modular_rref_metadata(
        pullback_mod, MODULAR_PRIME
    )

    q_pivot_minor = q_mod[np.ix_(pivot_rows, tuple(range(22)))]
    q_minor_rank, _, q_minor_determinant = _modular_rref_metadata(
        q_pivot_minor, MODULAR_PRIME
    )
    pullback_payload = {
        "prime": MODULAR_PRIME,
        "i_image": MODULAR_I,
        "free_rows": list(free_rows),
        "matrix": pullback_mod.tolist(),
    }

    sparse_hessian = _matrix_sparse_payload(real, imaginary)
    return {
        "published_H": sparse_hessian,
        "exact_structure": {
            "complex_symmetric_H_transpose_equals_H": symmetric,
            "common_denominator": HESSIAN_DENOMINATOR,
            "maximum_abs_scaled_entry": int(
                max(np.max(np.abs(real), initial=0), np.max(np.abs(imaginary), initial=0))
            ),
        },
        "Ward_identity": {
            "tested_columns": "45 Spin(10) generators plus U(1)_F",
            "scaled_product": "(4H)(4Q)=16 H Q",
            "maximum_abs_real_residual": int(np.max(np.abs(ward_real), initial=0)),
            "maximum_abs_imaginary_residual": int(np.max(np.abs(ward_imaginary), initial=0)),
            "HQ_exact_zero_all_46_columns": ward_exact,
        },
        "exact_rank_proof": {
            "finite_field": "F13 with i mapped to 5 because 5^2=-1 mod 13",
            "denominator_four_invertible_mod_13": pow(4, -1, MODULAR_PRIME) == 10,
            "rank_H_mod_13": full_rank_mod,
            "determinant_H_mod_13": full_determinant_mod,
            "rank_Q_mod_13": q_rank_mod,
            "characteristic_zero_upper_bound_from_22_exact_null_columns": SOURCE_DIMENSION - 22,
            "characteristic_zero_lower_bound_from_modular_minor": full_rank_mod,
            "exact_rank_H": 443 if ward_exact and q_rank_mod == 22 and full_rank_mod == 443 else None,
            "exact_nullity_H": 22 if ward_exact and q_rank_mod == 22 and full_rank_mod == 443 else None,
            "kernel_equals_gauge_orbit": ward_exact and q_rank_mod == 22 and full_rank_mod == 443,
        },
        "physical_pullback": {
            "pivot_rows_for_Q": list(pivot_rows),
            "free_rows": list(free_rows),
            "Q_pivot_minor_rank_mod_13": q_minor_rank,
            "Q_pivot_minor_determinant_mod_13": q_minor_determinant,
            "physical_section": "N=Z E_free, with Z from the V51 orbit audit",
            "identity": (
                "HQ=0 and H^T=H imply Z^T H Z=H, hence N^T H N=H[free,free]"
            ),
            "shape": [len(free_rows), len(free_rows)],
            "rank_mod_13": pullback_rank_mod,
            "determinant_mod_13": pullback_determinant_mod,
            "nondegenerate_over_characteristic_zero": (
                pullback_rank_mod == 443 and pullback_determinant_mod not in (None, 0)
            ),
            "canonical_mod13_pullback_sha256": hashlib.sha256(
                canonical_bytes(pullback_payload)
            ).hexdigest(),
        },
        "supersymmetric_scalar_consequence": {
            "holomorphic_object": "H_IJ=W_IJ",
            "F_term_scalar_mass_squared": "M_F^2=H^dagger H at the exact F-flat point",
            "rank_on_source_chiral_space": 443 if full_rank_mod == 443 else None,
            "positive_definite_on_443_dimensional_physical_quotient": (
                ward_exact and full_rank_mod == 443 and pullback_rank_mod == 443
            ),
            "scope_exclusion": (
                "This does not include the coupled bulk gauge, adjoint-chiral, ghost "
                "and gauge-fixing Rxi block."
            ),
        },
    }


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
def build_report() -> dict[str, Any]:
    orbit_report = _load_hashed_json(INPUTS["v51_orbit"])
    normalization = normalization_certificate()
    stationarity = stationarity_certificate()
    hessian = hessian_certificate()
    exact_rank = hessian["exact_rank_proof"]
    pullback = hessian["physical_pullback"]

    checks = {
        "input_orbit_map_is_exact_rank_22": (
            orbit_report["orbit_and_projector_certificate"]["selected_Gram"]["exact_rank"] == 22
        ),
        "Phi_quadratic_reduces_to_1_3_6": normalization["quadratic_Phi_weights_p_a_omega"] == {
            "p": 1, "a": 3, "omega": 6
        },
        "Phi_cubic_reduces_exactly": normalization["cubic_Tr_A3_over_3_nonzero_coefficients"] == {
            "a*a*a": 2, "a*omega*omega": 12, "omega*omega*p": 6
        },
        "five_form_pair_half_factor_reduces_to_one": normalization[
            "Sigma_barSigma_half_contraction_at_unit_singlets_re_im"
        ] == ["1", "0"],
        "eta_reduces_to_1_3_6": normalization["eta_linear_coefficients_p_a_omega"] == {
            "p": 1, "a": 3, "omega": 6
        },
        "all_source_F_terms_exact_zero": stationarity["all_465_F_terms_exact_zero"],
        "H_is_complex_symmetric": hessian["exact_structure"]["complex_symmetric_H_transpose_equals_H"],
        "H_has_exact_denominator_four": hessian["exact_structure"]["common_denominator"] == 4,
        "all_46_Ward_columns_exactly_null": hessian["Ward_identity"]["HQ_exact_zero_all_46_columns"],
        "exact_H_rank_is_443": exact_rank["exact_rank_H"] == 443,
        "exact_H_nullity_is_22": exact_rank["exact_nullity_H"] == 22,
        "kernel_equals_gauge_orbit": exact_rank["kernel_equals_gauge_orbit"],
        "physical_pullback_is_443_by_443": pullback["shape"] == [443, 443],
        "physical_pullback_is_nondegenerate": pullback["nondegenerate_over_characteristic_zero"],
        "F_term_scalar_mass_squared_positive_on_source_quotient": hessian[
            "supersymmetric_scalar_consequence"
        ]["positive_definite_on_443_dimensional_physical_quotient"],
        "tuned_witness_not_promoted_to_symmetry_prediction": (
            "not enforced" in stationarity["matching_scale_tuning"]
        ),
    }
    failures = [name for name, passed in checks.items() if not passed]
    report: dict[str, Any] = {
        "schema": "susy-v51-cartesian-source-hessian-audit-v1",
        "status": STATUS if not failures else "V51_CARTESIAN_SOURCE_HESSIAN_AUDIT_FAILED",
        "scope": (
            "One exact normalized renormalizable matching-scale source witness; "
            "not radiative naturalness, the bulk Rxi system, or the full G2 clause."
        ),
        "normalization_certificate": normalization,
        "stationarity_certificate": stationarity,
        "hessian_certificate": hessian,
        "gate_effect": {
            "G2_C3_physical_source_Hessian": "SOURCE_SUBBLOCK_CLOSED_AT_EXPLICIT_TUNED_WITNESS",
            "G2_C4_source_Goldstone_Ward": "SOURCE_SUBBLOCK_CLOSED_HQ_ZERO_AND_22_KERNEL",
            "still_open_for_C3_C4": [
                "coupled five-Goldstone bulk/source Rxi block",
                "normalized physical invariant-tensor lift for all V49 operator families",
                "endpoint auxiliary representations, charges and anomaly-safe pairing",
                "radiative stability or UV explanation of m1=M1=0",
            ],
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
            "Embed this exact 22-dimensional source Goldstone kernel into the finite-moose "
            "gauge/adjoint-chiral system and construct the coupled Rxi quadratic block; "
            "separately replace the tuned m1=M1=0 point by a radiatively controlled mediator "
            "or calculate the induced matching correction."
        ),
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    hessian = report["hessian_certificate"]
    published = hessian["published_H"]
    rank = hessian["exact_rank_proof"]
    ward = hessian["Ward_identity"]
    pullback = hessian["physical_pullback"]
    stationarity = report["stationarity_certificate"]
    return f"""# V51 Cartesian source Hessian audit

## Result

The normalized V47 source superpotential has been differentiated in the same
465-complex-coordinate chart as the exact V51 orbit map.  At the explicit
V46 rational witness, all 465 F terms vanish exactly.  The full holomorphic
Hessian is complex symmetric, has common denominator four, and is published
with {published['upper_triangle_nonzero_entries']} nonzero upper-triangle
entries.  Its canonical hash is `{published['canonical_H_sha256']}`.

The exact Ward test uses every one of the 45 Spin(10) columns plus `U(1)_F`:
`(4H)(4Q)=0`.  The maximum real and imaginary residuals are
{ward['maximum_abs_real_residual']} and {ward['maximum_abs_imaginary_residual']}.

## Exact rank and physical pullback

Reduction over `F13`, with `i -> 5`, gives rank {rank['rank_H_mod_13']}.
The exact rank-22 orbit lies in the kernel, so the characteristic-zero Hessian
has rank **{rank['exact_rank_H']}** and nullity **{rank['exact_nullity_H']}**;
its kernel is exactly the gauge orbit.

Using `N=Z E_free`, the 443 x 443 physical pullback has determinant
`{pullback['determinant_mod_13']}` modulo 13 and is therefore nondegenerate in
characteristic zero.  Pullback hash:
`{pullback['canonical_mod13_pullback_sha256']}`.

## Normalization and scope

The `1/2` factors in the `Sigma barSigma` and `Phi Sigma barSigma` tensor
contractions remove the double count from Hodge-paired five-form components.
They reproduce the V46 reduced coefficients `1,3,6` exactly.

This uses `m1=M1=0` at the matching scale.  {stationarity['matching_scale_tuning']}
It closes the explicit source-Hessian and source-Ward subproblems, but the
coupled bulk/source `Rxi` block, invariant-tensor lift, endpoint auxiliary
content and radiative control remain open.  No G2 clause or G gate is promoted.

Core SHA-256: `{report['core_sha256']}`
"""


def write_artifacts() -> dict[str, Any]:
    report = build_report()
    JSON_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")
    return report


def check_artifacts() -> None:
    if not JSON_PATH.is_file() or not MD_PATH.is_file():
        raise RuntimeError("missing V51 Cartesian-Hessian artifacts")
    observed = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    expected = build_report()
    if observed != expected:
        raise RuntimeError("V51 Cartesian-Hessian JSON artifact drifted")
    if observed.get("core_sha256") != canonical_sha(observed):
        raise RuntimeError("V51 Cartesian-Hessian core hash failed")
    if MD_PATH.read_text(encoding="utf-8") != render_markdown(expected):
        raise RuntimeError("V51 Cartesian-Hessian Markdown artifact drifted")


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
