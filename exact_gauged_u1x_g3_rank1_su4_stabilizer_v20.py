#!/usr/bin/env python3
"""Exact SU(4) stabilizer infrastructure at the rank-one G3 endpoint.

Fix the live maximal-negative representatives

    h_- = (e0-i e1)/sqrt(2),
    Sigma = q/4,
    q = (e0+i e1)...(e8+i e9).

The common infinitesimal SO(10) stabilizer acts on the four complex planes
``(23),(45),(67),(89)``.  This module constructs its fifteen generators over
the integers, directly in the tracked SO(10) convention.  The joint H/Sigma
tangent map has shape 272x45.  A rank-30 minor modulo a prime gives an exact
rank lower bound over Q, while fifteen independent displayed kernel columns
give the matching upper bound.  Hence the complete tangent kernel is exactly
the displayed su(4).

The same generators are lifted to the live real 210 chart.  Their matrices
are integral and skew, and their commutators reproduce integral su(4)
structure constants (including Jacobi) exactly.  This is representation and
stabilizer infrastructure for the next Schur/SOS calculation.  It does not
construct that SDP, prove a bound for arbitrary Phi, or close G3.
"""
from __future__ import annotations

import argparse
import itertools
import json
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
from scipy import sparse

import exact_gauged_u1x_g3_su5_delta_pd_sos_v20 as rank_source
import exact_gauged_u1x_g3_su5_max_negative_rank1_su3_slice_v20 as endpoint_source
import exact_phisigma_casimir_projectors_v20 as projectors
import live_g2_exact_hsigma_hermitian_derivatives_v20 as hsigma_source

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_GAUGED_U1X_G3_RANK1_SU4_STABILIZER_V20.json"
OUT_MD = ROOT / "EXACT_GAUGED_U1X_G3_RANK1_SU4_STABILIZER_V20.md"

MODULAR_PRIME = 1_000_003
MODEL_CONTRACT_ID = endpoint_source.MODEL_CONTRACT_ID
STATUS = "EXACT_RANK1_SU4_STABILIZER_INFRASTRUCTURE_CERTIFIED"
OVERALL_STATE = "STABILIZER_INFRASTRUCTURE_CLOSED__ARBITRARY_PHI_SDP_OPEN"
COMPLEX_PLANES = ((2, 3), (4, 5), (6, 7), (8, 9))
OFFDIAGONAL_PAIRS = tuple(itertools.combinations(range(4), 2))
SU4_LABELS = (
    ("H1", "H2", "H3")
    + tuple(
        label
        for left, right in OFFDIAGONAL_PAIRS
        for label in (f"X{left + 1}{right + 1}", f"Y{left + 1}{right + 1}")
    )
)
GENERATOR_LOOKUP = {
    label: index for index, label in enumerate(projectors.GENERATOR_LABELS)
}

# These fifteen SO(10)-coefficient rows form a unimodular coordinate chart on
# the displayed su(4) lattice.  The determinant of the selected 15x15 block
# is checked exactly before it is used to reconstruct structure constants.
LIE_PIVOT_LABELS = (
    (2, 3),
    (2, 4),
    (2, 5),
    (2, 6),
    (2, 7),
    (2, 8),
    (2, 9),
    (4, 5),
    (4, 6),
    (4, 7),
    (4, 8),
    (4, 9),
    (6, 7),
    (6, 8),
    (6, 9),
)


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    return value


def _maximum_sparse_abs(matrix: sparse.spmatrix) -> int:
    return int(np.max(np.abs(matrix.data), initial=0))


def _sparse_residual_maximum(matrix: sparse.spmatrix) -> int:
    compact = matrix.tocsr()
    compact.eliminate_zeros()
    return _maximum_sparse_abs(compact)


def su4_generator_definitions() -> tuple[dict[str, Any], ...]:
    """Return the ordered integral su(4) basis in SO(10) ``G_ab`` labels."""
    rows: list[dict[str, Any]] = []
    for index in range(3):
        rows.append(
            {
                "label": f"H{index + 1}",
                "kind": "Cartan_difference",
                "so10_coefficients": {
                    COMPLEX_PLANES[index]: 1,
                    COMPLEX_PLANES[index + 1]: -1,
                },
            }
        )
    for left, right in OFFDIAGONAL_PAIRS:
        even_left, odd_left = COMPLEX_PLANES[left]
        even_right, odd_right = COMPLEX_PLANES[right]
        rows.extend(
            (
                {
                    "label": f"X{left + 1}{right + 1}",
                    "kind": "complex_linear_real",
                    "so10_coefficients": {
                        (even_left, even_right): 1,
                        (odd_left, odd_right): 1,
                    },
                },
                {
                    "label": f"Y{left + 1}{right + 1}",
                    "kind": "complex_linear_imaginary",
                    "so10_coefficients": {
                        (even_left, odd_right): 1,
                        (odd_left, even_right): -1,
                    },
                },
            )
        )
    if tuple(row["label"] for row in rows) != SU4_LABELS:
        raise ArithmeticError("ordered su(4) generator census drifted")
    return tuple(rows)


def _su4_coefficient_matrix_for_planes(
    complex_planes: tuple[tuple[int, int], ...]
) -> np.ndarray:
    """Construct the same ordered su(4) basis on any four complex planes."""
    if len(complex_planes) != 4:
        raise ValueError("an su(4) embedding requires four complex planes")
    matrix = np.zeros((len(projectors.GENERATOR_LABELS), 15), dtype=np.int64)
    for index in range(3):
        matrix[GENERATOR_LOOKUP[complex_planes[index]], index] = 1
        matrix[GENERATOR_LOOKUP[complex_planes[index + 1]], index] = -1
    column = 3
    for left, right in OFFDIAGONAL_PAIRS:
        even_left, odd_left = complex_planes[left]
        even_right, odd_right = complex_planes[right]
        matrix[GENERATOR_LOOKUP[(even_left, even_right)], column] = 1
        matrix[GENERATOR_LOOKUP[(odd_left, odd_right)], column] = 1
        column += 1
        matrix[GENERATOR_LOOKUP[(even_left, odd_right)], column] = 1
        matrix[GENERATOR_LOOKUP[(odd_left, even_right)], column] = -1
        column += 1
    return matrix


@lru_cache(maxsize=1)
def su4_coefficient_matrix() -> np.ndarray:
    """45x15 integer matrix whose columns are the displayed generators."""
    matrix = np.zeros((len(projectors.GENERATOR_LABELS), 15), dtype=np.int64)
    for column, row in enumerate(su4_generator_definitions()):
        for label, coefficient in row["so10_coefficients"].items():
            matrix[GENERATOR_LOOKUP[label], column] = int(coefficient)
    if not np.array_equal(
        matrix, _su4_coefficient_matrix_for_planes(COMPLEX_PLANES)
    ):
        raise ArithmeticError("public su(4) definitions disagree with their lattice")
    matrix.setflags(write=False)
    return matrix


def _gaussian_integer_parts(
    value: np.ndarray, *, label: str
) -> tuple[np.ndarray, np.ndarray]:
    observed = np.asarray(value, dtype=complex)
    real = np.rint(observed.real).astype(np.int64)
    imaginary = np.rint(observed.imag).astype(np.int64)
    residual = max(
        float(np.max(np.abs(observed.real - real), initial=0.0)),
        float(np.max(np.abs(observed.imag - imaginary), initial=0.0)),
    )
    if residual != 0.0:
        raise ArithmeticError(f"{label} is not exactly Gaussian-integral")
    return real, imaginary


@lru_cache(maxsize=1)
def _tracked_generator_sources() -> dict[str, Any]:
    if tuple(hsigma_source.PAIRS) != tuple(projectors.GENERATOR_LABELS):
        raise ArithmeticError(
            "H/Sigma and Phi sources disagree on the ordered SO(10) generators"
        )
    h_real, h_imaginary = _gaussian_integer_parts(
        hsigma_source.h_generator_matrices(), label="H generators"
    )
    sigma_real, sigma_imaginary = _gaussian_integer_parts(
        hsigma_source.sigma_generator_matrices(), label="Sigma generators"
    )
    if np.any(h_imaginary):
        raise ArithmeticError("the real-vector SO(10) action became complex")

    observed_phi = projectors.generator_matrices()
    phi: list[sparse.csr_matrix] = []
    phi_integrality_residual = 0.0
    for index, observed in enumerate(observed_phi):
        rounded = np.rint(observed.data).astype(np.int64)
        phi_integrality_residual = max(
            phi_integrality_residual,
            float(np.max(np.abs(observed.data - rounded), initial=0.0)),
        )
        phi.append(
            sparse.csr_matrix(
                (rounded, observed.indices.copy(), observed.indptr.copy()),
                shape=observed.shape,
                dtype=np.int64,
            )
        )
        if phi[-1].shape != (210, 210):
            raise ArithmeticError(f"Phi generator {index} has the wrong shape")
    if phi_integrality_residual != 0.0:
        raise ArithmeticError("the live Phi210 action is not integral")

    h_skew_residual = int(
        np.max(np.abs(h_real + np.swapaxes(h_real, 1, 2)), initial=0)
    )
    sigma_antihermitian_residual = max(
        int(
            np.max(
                np.abs(sigma_real + np.swapaxes(sigma_real, 1, 2)),
                initial=0,
            )
        ),
        int(
            np.max(
                np.abs(
                    sigma_imaginary
                    - np.swapaxes(sigma_imaginary, 1, 2)
                ),
                initial=0,
            )
        ),
    )
    phi_skew_residual = max(
        (_sparse_residual_maximum(matrix + matrix.T) for matrix in phi),
        default=0,
    )
    return {
        "H_real": h_real,
        "Sigma_real": sigma_real,
        "Sigma_imaginary": sigma_imaginary,
        "Phi": tuple(phi),
        "H_skew_residual": h_skew_residual,
        "Sigma_antihermitian_residual": sigma_antihermitian_residual,
        "Phi_integrality_residual": phi_integrality_residual,
        "Phi_skew_residual": phi_skew_residual,
        "generator_order_exact": True,
    }


@lru_cache(maxsize=1)
def exact_generator_definition_certificate() -> dict[str, Any]:
    definitions = su4_generator_definitions()
    coefficients = su4_coefficient_matrix()
    coefficient_rank = rank_source._rank_mod_prime(
        coefficients, MODULAR_PRIME
    )
    displayed = []
    for row in definitions:
        displayed.append(
            {
                "label": row["label"],
                "kind": row["kind"],
                "definition": " + ".join(
                    f"{coefficient:+d} G_{first}{second}"
                    for (first, second), coefficient in row[
                        "so10_coefficients"
                    ].items()
                ).lstrip("+"),
                "so10_coefficients": {
                    f"G_{first}{second}": coefficient
                    for (first, second), coefficient in row[
                        "so10_coefficients"
                    ].items()
                },
            }
        )
    all_support_is_in_complement = all(
        first >= 2
        for row in definitions
        for first, _ in row["so10_coefficients"]
    )
    all_coefficients_are_signed_units = bool(
        np.all(np.isin(coefficients, (-1, 0, 1)))
    )
    return {
        "complex_planes": COMPLEX_PLANES,
        "ordered_labels": SU4_LABELS,
        "Cartan_generator_count": 3,
        "offdiagonal_generator_count": 12,
        "generator_count": len(definitions),
        "coefficient_matrix_shape": coefficients.shape,
        "coefficient_rank_mod_prime": coefficient_rank,
        "prime": MODULAR_PRIME,
        "all_support_is_in_indices_2_through_9": all_support_is_in_complement,
        "all_coefficients_are_signed_units": all_coefficients_are_signed_units,
        "definitions": displayed,
        "proof_grade": bool(
            COMPLEX_PLANES == ((2, 3), (4, 5), (6, 7), (8, 9))
            and len(definitions) == 15
            and coefficient_rank == 15
            and all_support_is_in_complement
            and all_coefficients_are_signed_units
        ),
    }


@lru_cache(maxsize=1)
def exact_stabilizer_tangent_certificate() -> dict[str, Any]:
    """Prove that the joint H/Sigma tangent kernel is exactly su(4)."""
    sources = _tracked_generator_sources()
    endpoint = endpoint_source.exact_rank1_residual_source()
    sigma_real = np.asarray(endpoint["sigma_integer_real"], dtype=np.int64)
    sigma_imaginary = np.asarray(
        endpoint["sigma_integer_imaginary"], dtype=np.int64
    )

    # h_- differs from this Gaussian-integer numerator only by sqrt(2).  The
    # Sigma endpoint differs from q only by 4.  Nonzero rescaling of either
    # tangent block does not change their common kernel.
    h_real = np.zeros(10, dtype=np.int64)
    h_imaginary = np.zeros(10, dtype=np.int64)
    h_real[0] = 1
    h_imaginary[1] = -1

    tangent_columns: list[np.ndarray] = []
    for generator in range(len(projectors.GENERATOR_LABELS)):
        h_image_real = sources["H_real"][generator] @ h_real
        h_image_imaginary = sources["H_real"][generator] @ h_imaginary
        sigma_image_real = (
            sources["Sigma_real"][generator] @ sigma_real
            - sources["Sigma_imaginary"][generator] @ sigma_imaginary
        )
        sigma_image_imaginary = (
            sources["Sigma_real"][generator] @ sigma_imaginary
            + sources["Sigma_imaginary"][generator] @ sigma_real
        )
        tangent_columns.append(
            np.concatenate(
                (
                    h_image_real,
                    h_image_imaginary,
                    sigma_image_real,
                    sigma_image_imaginary,
                )
            )
        )
    tangent = np.column_stack(tangent_columns).astype(np.int64)
    displayed_kernel = su4_coefficient_matrix()
    kernel_residual = tangent @ displayed_kernel
    tangent_rank = rank_source._rank_mod_prime(tangent, MODULAR_PRIME)
    displayed_rank = rank_source._rank_mod_prime(
        displayed_kernel, MODULAR_PRIME
    )
    nullity = tangent.shape[1] - tangent_rank

    # The older SU(4) used in the local SU(5)-Phi component audit acts on
    # (01),(23),(45),(67).  It is the wrong embedding here because h_- lives
    # in (01).  Keep this exact negative control so a future offset regression
    # cannot silently pass merely because both embeddings have dimension 15.
    old_offset_zero_planes = ((0, 1), (2, 3), (4, 5), (6, 7))
    old_offset_zero_kernel = _su4_coefficient_matrix_for_planes(
        old_offset_zero_planes
    )
    old_h_residual = tangent[:20, :] @ old_offset_zero_kernel
    old_sigma_residual = tangent[20:, :] @ old_offset_zero_kernel
    old_h_maximum = int(np.max(np.abs(old_h_residual), initial=0))
    old_sigma_maximum = int(np.max(np.abs(old_sigma_residual), initial=0))
    old_joint_maximum = max(old_h_maximum, old_sigma_maximum)

    endpoint_binding_exact = bool(
        endpoint["source_binding_exact"]
        and endpoint["endpoint_binding"]["proof_grade"]
        and endpoint["sigma_integer_norm_squared"] == 16
        and endpoint["endpoint_binding"]["canonical_normalization"]
        == "Sigma=q/4"
        and endpoint["endpoint_binding"]["normalized_kinetic_norm_squared"]
        == 1
    )
    proof_grade = bool(
        sources["H_skew_residual"] == 0
        and sources["Sigma_antihermitian_residual"] == 0
        and sources["generator_order_exact"]
        and endpoint_binding_exact
        and tangent.shape == (272, 45)
        and tangent_rank == 30
        and displayed_kernel.shape == (45, 15)
        and displayed_rank == 15
        and not np.any(kernel_residual)
        and nullity == 15
        and old_h_maximum > 0
        and old_joint_maximum > 0
    )
    return {
        "fixed_endpoint": {
            "H": "h_-=(e0-i e1)/sqrt(2)",
            "Sigma": "q/4",
            "q": endpoint["endpoint_binding"]["representative"],
            "integer_tangent_numerators": (
                "e0-i e1 for H and q for Sigma; independent nonzero "
                "block rescalings preserve the common tangent kernel"
            ),
            "H_numerator_norm_squared": int(h_real @ h_real + h_imaginary @ h_imaginary),
            "q_coordinate_norm_squared": int(
                sigma_real @ sigma_real + sigma_imaginary @ sigma_imaginary
            ),
            "endpoint_binding_exact": endpoint_binding_exact,
        },
        "source_actions": {
            "SO10_generator_count": len(projectors.GENERATOR_LABELS),
            "H_action_shape": sources["H_real"].shape,
            "Sigma_action_shape": sources["Sigma_real"].shape,
            "H_generators_integral_real_skew": sources["H_skew_residual"] == 0,
            "Sigma_generators_Gaussian_integral_antihermitian": (
                sources["Sigma_antihermitian_residual"] == 0
            ),
            "ordered_generator_labels_match_exactly": sources[
                "generator_order_exact"
            ],
        },
        "joint_tangent_coordinate_order": (
            "Re(H)[10], Im(H)[10], Re(Sigma)[126], Im(Sigma)[126]"
        ),
        "joint_tangent_shape": tangent.shape,
        "joint_tangent_max_abs_entry": int(
            np.max(np.abs(tangent), initial=0)
        ),
        "joint_tangent_rank_mod_prime": tangent_rank,
        "rank_lower_bound_over_Q_R": tangent_rank,
        "prime": MODULAR_PRIME,
        "displayed_kernel_shape": displayed_kernel.shape,
        "displayed_kernel_rank_mod_prime": displayed_rank,
        "displayed_kernel_residual_max_abs": int(
            np.max(np.abs(kernel_residual), initial=0)
        ),
        "kernel_upper_bound_on_tangent_rank": 45 - displayed_rank,
        "exact_tangent_rank_over_Q_R": tangent_rank if proof_grade else None,
        "exact_tangent_nullity": nullity if proof_grade else None,
        "kernel_exhaustion_identity": (
            "ker[d(SO10.(h_-,q/4))] = span_Z{H1,H2,H3,Xij,Yij} tensor R"
        ),
        "explicit_kernel_is_complete": proof_grade,
        "wrong_offset_zero_SU4_negative_control": {
            "complex_planes": old_offset_zero_planes,
            "H_tangent_residual_max_abs": old_h_maximum,
            "Sigma_tangent_residual_max_abs": old_sigma_maximum,
            "joint_tangent_residual_max_abs": old_joint_maximum,
            "does_not_stabilize_fixed_h_minus": old_h_maximum > 0,
            "wrong_embedding_rejected_exactly": old_joint_maximum > 0,
        },
        "proof_grade": proof_grade,
    }


@lru_cache(maxsize=1)
def _su4_vector_actions() -> tuple[np.ndarray, ...]:
    sources = _tracked_generator_sources()
    coefficients = su4_coefficient_matrix()
    return tuple(
        np.einsum(
            "g,gij->ij",
            coefficients[:, column],
            sources["H_real"],
            dtype=np.int64,
        )
        for column in range(15)
    )


def _invert_unimodular(matrix: np.ndarray) -> np.ndarray:
    """Invert a small integer matrix exactly, requiring an integer inverse."""
    value = np.asarray(matrix, dtype=np.int64)
    if value.ndim != 2 or value.shape[0] != value.shape[1]:
        raise ValueError("unimodular inverse requires a square matrix")
    dimension = value.shape[0]
    augmented = [
        [Fraction(int(item)) for item in value[row]]
        + [Fraction(int(row == column)) for column in range(dimension)]
        for row in range(dimension)
    ]
    for column in range(dimension):
        pivot = next(
            (row for row in range(column, dimension) if augmented[row][column]),
            None,
        )
        if pivot is None:
            raise ArithmeticError("selected su(4) coordinate block is singular")
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        scale = augmented[column][column]
        augmented[column] = [item / scale for item in augmented[column]]
        for row in range(dimension):
            if row == column or not augmented[row][column]:
                continue
            scale = augmented[row][column]
            augmented[row] = [
                left - scale * right
                for left, right in zip(
                    augmented[row], augmented[column], strict=True
                )
            ]
    inverse_fractions = [row[dimension:] for row in augmented]
    if any(item.denominator != 1 for row in inverse_fractions for item in row):
        raise ArithmeticError("selected su(4) coordinate block is not unimodular")
    inverse = np.asarray(
        [[int(item) for item in row] for row in inverse_fractions],
        dtype=np.int64,
    )
    if not np.array_equal(value @ inverse, np.eye(dimension, dtype=np.int64)):
        raise ArithmeticError("exact su(4) lattice inverse reconstruction failed")
    return inverse


@lru_cache(maxsize=1)
def exact_lie_algebra_certificate() -> dict[str, Any]:
    coefficients = su4_coefficient_matrix()
    pivot_rows = tuple(GENERATOR_LOOKUP[label] for label in LIE_PIVOT_LABELS)
    pivot_block = coefficients[np.asarray(pivot_rows), :]
    pivot_inverse = _invert_unimodular(pivot_block)
    vector_actions = _su4_vector_actions()
    structure = np.zeros((15, 15, 15), dtype=np.int64)
    coefficient_reconstruction_maximum = 0
    vector_reconstruction_maximum = 0

    for left in range(15):
        for right in range(15):
            commutator = (
                vector_actions[left] @ vector_actions[right]
                - vector_actions[right] @ vector_actions[left]
            )
            bracket_coefficients = np.asarray(
                [commutator[first, second] for first, second in projectors.GENERATOR_LABELS],
                dtype=np.int64,
            )
            coordinates = pivot_inverse @ bracket_coefficients[
                np.asarray(pivot_rows)
            ]
            structure[left, right, :] = coordinates
            coefficient_reconstruction_maximum = max(
                coefficient_reconstruction_maximum,
                int(
                    np.max(
                        np.abs(coefficients @ coordinates - bracket_coefficients),
                        initial=0,
                    )
                ),
            )
            reconstructed = sum(
                (
                    int(coordinates[index]) * vector_actions[index]
                    for index in range(15)
                ),
                np.zeros((10, 10), dtype=np.int64),
            )
            vector_reconstruction_maximum = max(
                vector_reconstruction_maximum,
                int(np.max(np.abs(commutator - reconstructed), initial=0)),
            )

    antisymmetry_residual = int(
        np.max(
            np.abs(structure + np.swapaxes(structure, 0, 1)), initial=0
        )
    )
    jacobi_residual = 0
    for first in range(15):
        for second in range(15):
            for third in range(15):
                row = np.zeros(15, dtype=np.int64)
                for middle in range(15):
                    row += (
                        structure[second, third, middle]
                        * structure[first, middle, :]
                        + structure[third, first, middle]
                        * structure[second, middle, :]
                        + structure[first, second, middle]
                        * structure[third, middle, :]
                    )
                jacobi_residual = max(
                    jacobi_residual,
                    int(np.max(np.abs(row), initial=0)),
                )

    sparse_structure = []
    for left in range(15):
        for right in range(left + 1, 15):
            for output in np.flatnonzero(structure[left, right, :]):
                sparse_structure.append(
                    {
                        "left": SU4_LABELS[left],
                        "right": SU4_LABELS[right],
                        "output": SU4_LABELS[int(output)],
                        "coefficient": int(structure[left, right, output]),
                    }
                )
    nonzero_unordered_brackets = sum(
        bool(np.any(structure[left, right, :]))
        for left in range(15)
        for right in range(left + 1, 15)
    )
    maximum_structure_constant = int(np.max(np.abs(structure), initial=0))
    cartan_residual = int(np.max(np.abs(structure[:3, :3, :]), initial=0))
    proof_grade = bool(
        coefficient_reconstruction_maximum == 0
        and vector_reconstruction_maximum == 0
        and antisymmetry_residual == 0
        and jacobi_residual == 0
        and cartan_residual == 0
        and maximum_structure_constant == 2
        and nonzero_unordered_brackets == 84
    )
    return {
        "basis_labels": SU4_LABELS,
        "Lie_algebra_dimension": 15,
        "coordinate_pivot_labels": LIE_PIVOT_LABELS,
        "coordinate_block_unimodular": bool(
            np.array_equal(
                pivot_block @ pivot_inverse,
                np.eye(15, dtype=np.int64),
            )
        ),
        "structure_constants_integral": True,
        "maximum_abs_structure_constant": maximum_structure_constant,
        "nonzero_unordered_bracket_count": nonzero_unordered_brackets,
        "nonzero_structure_constant_count": len(sparse_structure),
        "coefficient_commutator_reconstruction_max_abs": (
            coefficient_reconstruction_maximum
        ),
        "vector_commutator_reconstruction_max_abs": (
            vector_reconstruction_maximum
        ),
        "Cartan_commutator_max_abs": cartan_residual,
        "antisymmetry_max_abs_residual": antisymmetry_residual,
        "Jacobi_max_abs_residual": jacobi_residual,
        "nonzero_structure_constants_for_left_less_than_right": sparse_structure,
        "proof_grade": proof_grade,
    }


@lru_cache(maxsize=1)
def exact_phi210_actions() -> tuple[sparse.csr_matrix, ...]:
    """Return the ordered fifteen exact integral actions on real Phi210."""
    sources = _tracked_generator_sources()
    coefficients = su4_coefficient_matrix()
    output: list[sparse.csr_matrix] = []
    for column in range(15):
        matrix = sparse.csr_matrix((210, 210), dtype=np.int64)
        for generator in np.flatnonzero(coefficients[:, column]):
            matrix = matrix + int(coefficients[generator, column]) * sources[
                "Phi"
            ][int(generator)]
        matrix.eliminate_zeros()
        output.append(matrix.astype(np.int64))
    return tuple(output)


@lru_cache(maxsize=1)
def exact_phi210_action_certificate() -> dict[str, Any]:
    actions = exact_phi210_actions()
    lie = exact_lie_algebra_certificate()
    structure_rows = lie[
        "nonzero_structure_constants_for_left_less_than_right"
    ]
    label_index = {label: index for index, label in enumerate(SU4_LABELS)}

    skew_residual = max(
        (_sparse_residual_maximum(matrix + matrix.T) for matrix in actions),
        default=0,
    )
    flattened = np.column_stack(
        [matrix.toarray().reshape(-1) for matrix in actions]
    ).astype(np.int64)
    action_rank = rank_source._rank_mod_prime(flattened, MODULAR_PRIME)
    commutator_residual = 0
    for left in range(15):
        for right in range(left + 1, 15):
            expected = sparse.csr_matrix((210, 210), dtype=np.int64)
            for row in structure_rows:
                if row["left"] == SU4_LABELS[left] and row["right"] == SU4_LABELS[right]:
                    expected = expected + int(row["coefficient"]) * actions[
                        label_index[row["output"]]
                    ]
            residual = actions[left] @ actions[right] - actions[right] @ actions[left] - expected
            commutator_residual = max(
                commutator_residual, _sparse_residual_maximum(residual)
            )
    integral_dtypes = all(
        np.issubdtype(matrix.dtype, np.integer) for matrix in actions
    )
    action_shapes = {matrix.shape for matrix in actions}
    proof_grade = bool(
        len(actions) == 15
        and action_shapes == {(210, 210)}
        and integral_dtypes
        and skew_residual == 0
        and action_rank == 15
        and commutator_residual == 0
        and lie["proof_grade"]
    )
    return {
        "representation": "real Lambda^4(R^10) = Phi210",
        "ordered_labels": SU4_LABELS,
        "action_count": len(actions),
        "action_shapes": sorted(action_shapes),
        "all_action_dtypes_integral": integral_dtypes,
        "total_nonzero_entries": sum(matrix.nnz for matrix in actions),
        "maximum_abs_action_entry": max(
            (_maximum_sparse_abs(matrix) for matrix in actions), default=0
        ),
        "skew_transpose_max_abs_residual": skew_residual,
        "flattened_action_rank_mod_prime": action_rank,
        "prime": MODULAR_PRIME,
        "Lie_commutator_reconstruction_max_abs": commutator_residual,
        "source_binding": (
            "direct_phi_h_sigmabar_tensor_v20 generator_action through the "
            "tracked exact Phi210 generator source"
        ),
        "proof_grade": proof_grade,
    }


def _build_report_from_certificates(
    *,
    generators: dict[str, Any],
    tangent: dict[str, Any],
    lie: dict[str, Any],
    phi210: dict[str, Any],
) -> dict[str, Any]:
    """Assemble the artifact while rechecking every acceptance predicate."""
    checks = {
        "fifteen_correct_shifted_SU4_generators_exact": bool(
            generators["proof_grade"]
            and generators["complex_planes"]
            == ((2, 3), (4, 5), (6, 7), (8, 9))
            and generators["generator_count"] == 15
            and generators["Cartan_generator_count"] == 3
            and generators["offdiagonal_generator_count"] == 12
            and generators["coefficient_rank_mod_prime"] == 15
        ),
        "fixed_h_minus_q_over_4_endpoint_bound_exact": bool(
            tangent["fixed_endpoint"]["endpoint_binding_exact"]
            and tangent["fixed_endpoint"]["H_numerator_norm_squared"] == 2
            and tangent["fixed_endpoint"]["q_coordinate_norm_squared"] == 16
        ),
        "joint_tangent_rank_30_modular_lower_bound_exact": bool(
            tangent["joint_tangent_shape"] == (272, 45)
            and tangent["joint_tangent_rank_mod_prime"] == 30
            and tangent["rank_lower_bound_over_Q_R"] == 30
            and tangent["prime"] == MODULAR_PRIME
        ),
        "explicit_fifteen_dimensional_kernel_upper_bound_exact": bool(
            tangent["displayed_kernel_shape"] == (45, 15)
            and tangent["displayed_kernel_rank_mod_prime"] == 15
            and tangent["displayed_kernel_residual_max_abs"] == 0
            and tangent["kernel_upper_bound_on_tangent_rank"] == 30
        ),
        "joint_stabilizer_kernel_exhausted_exactly_by_SU4": bool(
            tangent["proof_grade"]
            and tangent["exact_tangent_rank_over_Q_R"] == 30
            and tangent["exact_tangent_nullity"] == 15
            and tangent["explicit_kernel_is_complete"]
        ),
        "old_offset_zero_SU4_embedding_rejected_by_h_minus_exactly": bool(
            tangent["source_actions"][
                "ordered_generator_labels_match_exactly"
            ]
            and tangent["wrong_offset_zero_SU4_negative_control"][
                "does_not_stabilize_fixed_h_minus"
            ]
            and tangent["wrong_offset_zero_SU4_negative_control"][
                "H_tangent_residual_max_abs"
            ]
            > 0
            and tangent["wrong_offset_zero_SU4_negative_control"][
                "wrong_embedding_rejected_exactly"
            ]
        ),
        "integral_SU4_Lie_structure_constants_close_exactly": bool(
            lie["proof_grade"]
            and lie["Lie_algebra_dimension"] == 15
            and lie["coordinate_block_unimodular"]
            and lie["structure_constants_integral"]
            and lie["maximum_abs_structure_constant"] == 2
            and lie["coefficient_commutator_reconstruction_max_abs"] == 0
            and lie["vector_commutator_reconstruction_max_abs"] == 0
            and lie["antisymmetry_max_abs_residual"] == 0
            and lie["Jacobi_max_abs_residual"] == 0
        ),
        "Phi210_actions_integral_skew_faithful_and_Lie_exact": bool(
            phi210["proof_grade"]
            and phi210["action_count"] == 15
            and phi210["all_action_dtypes_integral"]
            and phi210["maximum_abs_action_entry"] == 1
            and phi210["skew_transpose_max_abs_residual"] == 0
            and phi210["flattened_action_rank_mod_prime"] == 15
            and phi210["Lie_commutator_reconstruction_max_abs"] == 0
        ),
    }
    failures = [name for name, passed in checks.items() if not passed]
    scope = {
        "infrastructure_only": True,
        "H_fixed_to_h_minus": True,
        "Sigma_fixed_to_normalized_explicit_decomposable_pure_spinor_q_over_4": True,
        "common_continuous_stabilizer_identified_as_SU4": not failures,
        "exact_Phi210_SU4_action_available_for_next_stage": not failures,
        "arbitrary_Phi_Schur_SOS_SDP_constructed": False,
        "arbitrary_Phi_Schur_SOS_SDP_feasible": False,
        "arbitrary_rank1_Phi_bound_proved": False,
        "arbitrary_max_negative_Sigma_proved": False,
        "G3_closed": False,
        "whole_model_excluded": False,
    }
    return {
        "status": STATUS if not failures else "RANK1_SU4_STABILIZER_INFRASTRUCTURE_FAILED",
        "overall_state": OVERALL_STATE if not failures else "EXECUTION_FAIL",
        "model_contract_id": MODEL_CONTRACT_ID,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failed_checks": failures,
        "checks": checks,
        "scope": scope,
        "generator_basis": generators,
        "joint_stabilizer_tangent": tangent,
        "Lie_algebra": lie,
        "Phi210_action": phi210,
        "next_exact_target": (
            "Construct the full SU(4)-equivariant multiplicity/intertwiner "
            "decomposition of the arbitrary-Phi rank-one anchor, then solve "
            "and rationalize its Schur/SOS SDP."
        ),
        "verdict": (
            "The exact common continuous stabilizer Lie algebra of fixed h_- "
            "and the explicit q/4 rank-one endpoint is the displayed su(4), "
            "with integral Lie structure and exact skew actions on Phi210. "
            "This certifies only the representation infrastructure; no "
            "arbitrary-Phi SDP or G3 closure is claimed."
        ),
    }


def build_report() -> dict[str, Any]:
    return _build_report_from_certificates(
        generators=exact_generator_definition_certificate(),
        tangent=exact_stabilizer_tangent_certificate(),
        lie=exact_lie_algebra_certificate(),
        phi210=exact_phi210_action_certificate(),
    )


def render_markdown(report: dict[str, Any]) -> str:
    tangent = report["joint_stabilizer_tangent"]
    lie = report["Lie_algebra"]
    phi210 = report["Phi210_action"]
    return "\n".join(
        [
            "# Exact rank-one SU(4) stabilizer infrastructure",
            "",
            f"Status: **{report['status']}**",
            "",
            report["verdict"],
            "",
            "## Exact result",
            "",
            "- fixed endpoint: `H=h_-`, `Sigma=q/4`;",
            "- complex planes: `(23),(45),(67),(89)`;",
            "- joint tangent matrix: `272 x 45`;",
            f"- exact tangent rank/nullity: `{tangent['exact_tangent_rank_over_Q_R']}/{tangent['exact_tangent_nullity']}`;",
            "- displayed kernel: all `15` SU(4) generators, exactly exhaustive;",
            f"- nonzero unordered Lie brackets: `{lie['nonzero_unordered_bracket_count']}`;",
            f"- largest integral structure coefficient: `{lie['maximum_abs_structure_constant']}`;",
            f"- Phi210 action matrices: `{phi210['action_count']}` integral skew `210 x 210` matrices;",
            f"- Phi210 total nonzero entries: `{phi210['total_nonzero_entries']}`;",
            "",
            "## Scope",
            "",
            "- SU(4) stabilizer/action infrastructure: **CLOSED**;",
            "- arbitrary-Phi Schur/SOS SDP: **OPEN**;",
            "- arbitrary-rank-one-Phi bound: **OPEN**;",
            "- arbitrary maximal-negative Sigma: **OPEN**;",
            "- G3: **OPEN**.",
            "",
            f"Next: {report['next_exact_target']}",
            "",
        ]
    )


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(
        json.dumps(_jsonable(report), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    OUT_MD.write_text(render_markdown(report), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        write_report(report)
    print(json.dumps(_jsonable(report), indent=2, sort_keys=True))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
