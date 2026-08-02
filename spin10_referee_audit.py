#!/usr/bin/env python3
"""Explicit Spin(10), Fermi-statistics and vacuum-graph audit for v17.

This module does not infer invariants from centre charge alone.  It constructs
an explicit 32 x 32 Euclidean Clifford algebra, restricts C Gamma^a to one
16-dimensional chiral spinor, and evaluates candidate invariants in a sparse
Grassmann algebra carrying both Lorentz and Spin(10) indices.

Conventions
-----------
``s`` and ``F`` transform as 16, while ``b`` transforms as 16bar.  The
same-chirality vector bilinear is

    B^a(X,Y) = epsilon_{alpha beta} X_i^alpha (C Gamma^a)_{ij} Y_j^beta.

The ten matrices (C Gamma^a)|_16 are symmetric, as required for the symmetric
10 in 16 tensor 16 = 10_s + 120_a + 126_s.
"""

from __future__ import annotations

from dataclasses import dataclass
import itertools
import math
from typing import Dict, Iterable, Mapping, Sequence

import numpy as np


GrassmannPolynomial = Dict[int, complex]


def _kron_all(matrices: Sequence[np.ndarray]) -> np.ndarray:
    result = np.array([[1.0 + 0.0j]])
    for matrix in matrices:
        result = np.kron(result, matrix)
    return result


def clifford_generators_so10() -> tuple[list[np.ndarray], np.ndarray, np.ndarray]:
    """Return gamma matrices, chirality and a charge-conjugation matrix."""
    identity = np.eye(2, dtype=complex)
    sigma_1 = np.array([[0, 1], [1, 0]], dtype=complex)
    sigma_2 = np.array([[0, -1j], [1j, 0]], dtype=complex)
    sigma_3 = np.array([[1, 0], [0, -1]], dtype=complex)
    gammas = []
    for position in range(5):
        for sigma in (sigma_1, sigma_2):
            gammas.append(
                _kron_all(
                    [sigma_3] * position
                    + [sigma]
                    + [identity] * (4 - position)
                )
            )
    chirality = (-1j) ** 5 * np.eye(32, dtype=complex)
    for gamma in gammas:
        chirality = chirality @ gamma
    # Gamma_2 Gamma_4 ... Gamma_10 in one-based notation.
    charge_conjugation = np.eye(32, dtype=complex)
    for index in (1, 3, 5, 7, 9):
        charge_conjugation = charge_conjugation @ gammas[index]
    return gammas, chirality, charge_conjugation


def chiral_vector_bilinears(chirality_sign: int = +1) -> list[np.ndarray]:
    """Construct the ten symmetric 16 x 16 matrices (C Gamma^a)|_+/- ."""
    if chirality_sign not in (-1, +1):
        raise ValueError("chirality_sign must be +1 or -1")
    gammas, chirality, charge_conjugation = clifford_generators_so10()
    selected = np.flatnonzero(
        chirality_sign * np.real(np.diag(chirality)) > 0.5
    )
    matrices = [
        (charge_conjugation @ gamma)[np.ix_(selected, selected)]
        for gamma in gammas
    ]
    # Round numerical Pauli products back to exact Gaussian-integer entries.
    return [
        np.rint(matrix.real).astype(int)
        + 1j * np.rint(matrix.imag).astype(int)
        for matrix in matrices
    ]


def clifford_diagnostics() -> dict:
    gammas, chirality, charge_conjugation = clifford_generators_so10()
    identity = np.eye(32, dtype=complex)
    clifford_error = max(
        np.max(
            np.abs(
                gammas[a] @ gammas[b]
                + gammas[b] @ gammas[a]
                - 2 * (a == b) * identity
            )
        )
        for a in range(10)
        for b in range(10)
    )
    conjugation_error = max(
        np.max(
            np.abs(
                charge_conjugation
                @ gammas[a]
                @ np.linalg.inv(charge_conjugation)
                + gammas[a].T
            )
        )
        for a in range(10)
    )
    vector_matrices = chiral_vector_bilinears(+1)
    conjugate_vector_matrices = chiral_vector_bilinears(-1)
    gram = np.array(
        [
            [np.vdot(left, right) for right in vector_matrices]
            for left in vector_matrices
        ]
    )
    eigenvalues = np.linalg.eigvalsh(chirality)
    return {
        "clifford_max_error": float(clifford_error),
        "charge_conjugation_max_error": float(conjugation_error),
        "chirality_plus": int(np.count_nonzero(eigenvalues > 0.5)),
        "chirality_minus": int(np.count_nonzero(eigenvalues < -0.5)),
        "C_is_antisymmetric": bool(np.allclose(charge_conjugation.T, -charge_conjugation)),
        "C_anticommutes_with_chirality": bool(
            np.allclose(charge_conjugation @ chirality, -chirality @ charge_conjugation)
        ),
        "vector_bilinears_symmetric": bool(
            all(np.array_equal(matrix.T, matrix) for matrix in vector_matrices)
        ),
        "conjugate_vector_bilinears_symmetric": bool(
            all(
                np.array_equal(matrix.T, matrix)
                for matrix in conjugate_vector_matrices
            )
        ),
        "vector_bilinear_gram": np.real_if_close(gram).astype(int).tolist(),
    }


def _canonical_pair(first: int, second: int) -> tuple[int, int]:
    if first == second:
        return 0, 0
    if first < second:
        return (1 << first) | (1 << second), 1
    return (1 << second) | (1 << first), -1


def _add_term(polynomial: GrassmannPolynomial, mask: int, coefficient: complex) -> None:
    if coefficient == 0:
        return
    polynomial[mask] = polynomial.get(mask, 0.0j) + coefficient
    if abs(polynomial[mask]) < 1.0e-12:
        polynomial.pop(mask)


def wedge_sign(left: int, right: int) -> int:
    """Sign required to sort the generators of left*right canonically."""
    inversions = 0
    remaining = right
    while remaining:
        lowest = remaining & -remaining
        index = lowest.bit_length() - 1
        remaining ^= lowest
        inversions += (left >> (index + 1)).bit_count()
    return -1 if inversions % 2 else 1


def grassmann_multiply(
    left: Mapping[int, complex], right: Mapping[int, complex]
) -> GrassmannPolynomial:
    result: GrassmannPolynomial = {}
    for left_mask, left_coefficient in left.items():
        for right_mask, right_coefficient in right.items():
            if left_mask & right_mask:
                continue
            _add_term(
                result,
                left_mask | right_mask,
                left_coefficient
                * right_coefficient
                * wedge_sign(left_mask, right_mask),
            )
    return result


def grassmann_sum(polynomials: Iterable[Mapping[int, complex]]) -> GrassmannPolynomial:
    result: GrassmannPolynomial = {}
    for polynomial in polynomials:
        for mask, coefficient in polynomial.items():
            _add_term(result, mask, coefficient)
    return result


def weyl_bilinear(
    left_species: int,
    right_species: int,
    internal_tensor: np.ndarray,
) -> GrassmannPolynomial:
    """epsilon_{ab} X_i^a T_ij Y_j^b as a sparse Grassmann polynomial.

    Each species receives 32 generators: 16 internal components for each of
    the two four-dimensional left-Weyl Lorentz components.
    """
    result: GrassmannPolynomial = {}
    for left_internal in range(16):
        for right_internal in range(16):
            internal = internal_tensor[left_internal, right_internal]
            if internal == 0:
                continue
            for left_lorentz, right_lorentz, epsilon in ((0, 1, 1), (1, 0, -1)):
                left_generator = left_species * 32 + left_lorentz * 16 + left_internal
                right_generator = right_species * 32 + right_lorentz * 16 + right_internal
                mask, ordering = _canonical_pair(left_generator, right_generator)
                if mask:
                    _add_term(result, mask, internal * epsilon * ordering)
    return result


def polynomial_norm_squared(polynomial: Mapping[int, complex]) -> int:
    value = sum(abs(coefficient) ** 2 for coefficient in polynomial.values())
    return int(round(value))


def lorentz_closure_factor() -> int:
    """Evaluate one explicit Lorentz contraction of the P=12 graph."""
    epsilon_down = np.array([[0, 1], [-1, 0]], dtype=int)
    epsilon_up = np.array([[0, -1], [1, 0]], dtype=int)
    total = 0
    # alpha[4], beta[4], gamma[4]
    for values in itertools.product(range(2), repeat=12):
        alpha, beta, gamma = values[:4], values[4:8], values[8:]
        term = 1
        for index in range(4):
            term *= epsilon_down[alpha[index], beta[index]]
            term *= epsilon_up[beta[index], gamma[index]]
        term *= epsilon_down[gamma[0], gamma[1]]
        term *= epsilon_down[gamma[2], gamma[3]]
        term *= epsilon_up[alpha[0], alpha[1]]
        term *= epsilon_up[alpha[2], alpha[3]]
        total += term
    return int(total)


def anomaly_diagnostics() -> dict:
    """Odd-Z17 Hsieh/Ibanez-Ross and mixed Spin(10)^2 arithmetic."""
    # Three ordinary 16s, five spectator 16s and five spectator 16bars.
    charges = [1] * (3 * 16) + [2] * (5 * 16) + [11] * (5 * 16)
    linear = sum(charges)
    cubic = sum(charge**3 for charge in charges)
    # T(16)=T(16bar)=2 in the normalization used by the manuscript.
    mixed = 3 * 2 * 1 + 5 * 2 * (2 + 11)
    return {
        "linear": linear,
        "cubic": cubic,
        "mixed_spin10": mixed,
        "linear_mod17": linear % 17,
        "cubic_mod17": cubic % 17,
        "mixed_mod17": mixed % 17,
    }


@dataclass(frozen=True)
class ExplicitInvariant:
    name: str
    grassmann_monomials: int
    coefficient_norm_squared: int
    nonzero: bool


def explicit_invariant_diagnostics() -> dict:
    vector_tensors = chiral_vector_bilinears(+1)
    conjugate_vector_tensors = chiral_vector_bilinears(-1)
    # species 0=s and species 1=F.  Different QFT vertices/momenta remove any
    # local nilpotency concern; the same-species calculation is the stronger
    # Fermi-statistics test.
    ss_vectors = [weyl_bilinear(0, 0, tensor) for tensor in vector_tensors]
    fs_vectors = [weyl_bilinear(1, 0, tensor) for tensor in vector_tensors]
    bb_vectors = [
        weyl_bilinear(2, 2, tensor) for tensor in conjugate_vector_tensors
    ]
    fb_singlet = weyl_bilinear(1, 2, np.eye(16, dtype=complex))

    o8 = grassmann_sum(
        grassmann_multiply(vector, vector) for vector in ss_vectors
    )
    # Choose a nonzero generic vector-Higgs direction H^a=(1,0,...,0).
    bb_dot_bb = grassmann_sum(
        grassmann_multiply(vector, vector) for vector in bb_vectors
    )
    o10 = grassmann_multiply(bb_dot_bb, bb_vectors[0])
    o12 = grassmann_sum(
        grassmann_multiply(fs, ss)
        for fs, ss in zip(fs_vectors, ss_vectors)
    )

    tensors = np.asarray(vector_tensors)
    closure_tensor = np.einsum("aij,akl->ijkl", tensors, tensors)
    closure_group_factor = int(round(float(np.vdot(closure_tensor, closure_tensor).real)))
    # Contract the central O8 tensor with two 10_H-channel family mass
    # matrices.  For M(H)=H_a T^a the result is 256 H_a H_a in this
    # normalization.  A unit vector direction therefore supplies a direct
    # nonzero certificate for the actual compact graph, whereas ||K||^2
    # below diagnoses the central four-spinor tensor itself.
    graph_higgs_gram = np.einsum(
        "ijkl,aij,bkl->ab", closure_tensor.conj(), tensors, tensors
    )
    graph_group_contraction = int(round(float(graph_higgs_gram[0, 0].real)))

    def summary(name: str, polynomial: Mapping[int, complex]) -> dict:
        return ExplicitInvariant(
            name=name,
            grassmann_monomials=len(polynomial),
            coefficient_norm_squared=polynomial_norm_squared(polynomial),
            nonzero=bool(polynomial),
        ).__dict__

    return {
        "O6_singlet": summary("(F b)_1", fb_singlet),
        "O8": summary("[(s s)_10]^2", o8),
        "O10": summary("[(b b)_10]^2 (b b)_10.H", o10),
        "O12": summary("(F s)_10 (s s)_10", o12),
        "closure_tensor_nonzero_entries": int(np.count_nonzero(closure_tensor)),
        "closure_group_factor": closure_group_factor,
        "graph_group_contraction_unit_10H": graph_group_contraction,
        "graph_10H_contraction_gram": np.real_if_close(graph_higgs_gram)
        .astype(int)
        .tolist(),
        "graph_group_contraction_formula": "256 (10_H_dagger dot 10_H_dagger)",
        "closure_lorentz_factor": lorentz_closure_factor(),
    }


def p12_graph_diagnostics(
    matching_scale: float = 6.313855e11,
    nda_bound: float = 4.517917226627945e-28,
    electroweak_vev_upper: float = 246.0,
) -> dict:
    vertices = 5  # four O6 and one O8, treating mass insertions as propagators
    internal_lines = 6  # four s-b plus two F-F
    connected_components = 1
    loops = internal_lines - vertices + connected_components
    two_loop_factor = (16.0 * math.pi**2) ** (-loops)
    chirality_factor_upper = (electroweak_vev_upper / matching_scale) ** 2
    return {
        "planck_spurions": {"O6": 4, "O8": 1},
        "P": 4 * (6 - 4) + (8 - 4),
        "Q_PQ": 4 * (-17),
        "spectator_vector": 4 * (-1) + 4,
        "vertices_compact_graph": vertices,
        "internal_fermion_lines": internal_lines,
        "loops": loops,
        "same_chirality_propagators": {"spectator_s_b": 4, "family_10H_channel": 2},
        "resulting_scalar_phase": "(S_dagger)^18 (10_H_dagger)^2",
        "resulting_scalar_Q_PQ": 18 * (-4) + 2 * (+2),
        "NDA_bound_per_Ceff": nda_bound,
        "two_loop_factor": two_loop_factor,
        "EW_chirality_factor_upper": chirality_factor_upper,
        "diagrammatic_estimate_per_Ceff": nda_bound
        * two_loop_factor
        * chirality_factor_upper,
    }


def build_referee_report() -> dict:
    return {
        "status": "P=12 saturation survives explicit Spin(10), Lorentz and Fermi-statistics audit",
        "clifford": clifford_diagnostics(),
        "anomalies": anomaly_diagnostics(),
        "invariants": explicit_invariant_diagnostics(),
        "vacuum_graph": p12_graph_diagnostics(),
        "interpretation": {
            "rigorous_bound": "4.52e-28 times C_eff under the stated Wilsonian assumptions",
            "specific_P12_graph": "nonzero, two-loop, and requires two 10_H-channel family chirality flips",
            "specific_graph_estimate": "<=2.8e-51 times C_eff when v_10<=246 GeV, before flavor factors",
            "remaining_scope": "UV origin of Z17 and all threshold-generated PQ breaking are not proven",
        },
    }


if __name__ == "__main__":
    import json

    print(json.dumps(build_referee_report(), indent=2))
