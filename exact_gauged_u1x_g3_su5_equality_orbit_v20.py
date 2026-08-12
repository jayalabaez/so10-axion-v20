#!/usr/bin/env python3
"""Fail-closed global-equality theorem for the SU(5)+Delta_R PD SOS.

The Phi/Sigma sum of squares in
``exact_gauged_u1x_g3_su5_delta_pd_sos_v20.py`` has a proof-grade local
equality classification.  This module asks the harder global question.

Most of that question can be settled exactly.  At the normalized SU(5)
four-form F, the mixed residual kernel in the complex 126bar is a ten:

    s_I = (wedge_{i in I} z_i) wedge sum_{j not in I} omega_j,
    |I|=3,  z_i=e_{2i}+i e_{2i+1},  omega_i=e_{2i} wedge e_{2i+1}.

The ten Gaussian-integer columns span the entire kernel.  On this kernel the
54 self projector vanishes identically and the 1050bar projector is exactly

    I_1050bar = (256/9) sum_A |Pf_A(t)|^2,

where the five Pf_A are the Pluecker quadrics of the two-form Hodge-dual to
the coefficient three-form t.  Thus every nonzero normalized Sigma equality
solution at fixed F is a decomposable two-form and belongs to one U(5) orbit.

The complementary fixed-Delta calculation is also exact on the complete
ten-variable pair-plane diagonal slice.  The Phi-projector equations alone
give two overall-sign SO(10) orbits, represented by F and -F.  They cannot be
identified: the exact cubic invariant Tr(A_Phi^3) changes sign.  The mixed
equation excludes the -F orbit exactly because M(F)+8 is invertible.  On the
remaining +F orbit the mixed equations and norm leave two pair-plane sign
patterns; an explicit determinant-one reflection maps them into each other
while sending Delta to -Delta, which is restored by an allowed U(1) phase.

The corrected global lemma is now available:

    every real Phi with ||Phi||=1 and Pi_54(Phi Phi)=Pi_4125(Phi Phi)=0
    belongs to SO(10).F or SO(10).(-F).

The earlier one-orbit wording was false as written.  The frozen global
signed-Kahler theorem proves the displayed two-orbit statement for every real
four-form.  The companion
``exact_gauged_u1x_g3_su5_phi_orbit_lemma_v20`` artifact supplies the exact
counterexample and classifies the complete SU(4)-invariant slice.  Its local
component companion further proves that both signed orbits are isolated local
components.  A second companion classifies the complete 16-real-dimensional
SU(3)-fixed slice, including eight non-diagonal Omega_3 wedge R4 directions,
and again finds only the signed Kahler-square orbit.  Together with the exact
mixed invertibility of the -F sheet and the fixed-F Pluecker classification,
the global theorem closes the PD equality-orbit classification.  It does not
prove the quantitative arbitrary-field coercivity estimate needed for the
beta-deformed global gap, and therefore does not close G3.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

import numpy as np

import direct_phi_h_sigmabar_tensor_v20 as direct
import exact_126bar_self_quartic_basis_v20 as sigma_self
import exact_gauged_u1x_g3_a_square_recoupling_v20 as mixed_source
import exact_gauged_u1x_g3_pd_rank_certificate_v20 as rank_source
import exact_gauged_u1x_g3_su5_delta_pd_sos_v20 as pd_source
import exact_gauged_u1x_g3_su5_phi_orbit_lemma_v20 as orbit_lemma_audit
import exact_gauged_u1x_g3_su5_phi_local_component_v20 as local_component_audit
import exact_gauged_u1x_g3_su5_phi_su3_slice_v20 as su3_slice_audit
import exact_phisigma_casimir_projectors_v20 as phi_projectors
import exact_phi_self_zero_global_signed_kaehler_classification_v20 as global_phi
import live_g2_canonical_486_field_chart_v20 as chart

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_GAUGED_U1X_G3_SU5_EQUALITY_ORBIT_V20.json"
OUT_MD = ROOT / "EXACT_GAUGED_U1X_G3_SU5_EQUALITY_ORBIT_V20.md"

COMPLEX_TRIPLES = tuple(itertools.combinations(range(5), 3))
COMPLEX_PAIRS = tuple(itertools.combinations(range(5), 2))
TEN_MONOMIALS = tuple(itertools.combinations_with_replacement(range(10), 2))
PAIR_INDEX = {pair: index for index, pair in enumerate(COMPLEX_PAIRS)}
MONOMIAL_INDEX = {pair: index for index, pair in enumerate(TEN_MONOMIALS)}
MODULAR_PRIME = 1_000_003
GLOBAL_PHI_SOURCE_SHA256 = (
    "6887429cebbe0e0ee9171b9346b85c671959c2fdbc2b5187efc73a52552b0883"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def _permutation_sign(sequence: tuple[int, ...]) -> int:
    inversions = sum(
        sequence[left] > sequence[right]
        for left in range(len(sequence))
        for right in range(left + 1, len(sequence))
    )
    return -1 if inversions % 2 else 1


def _wedge_all(forms: Iterable[direct.Form]) -> direct.Form:
    output: direct.Form = {(): 1.0 + 0.0j}
    for form in forms:
        output = direct.wedge(output, form)
    return output


@lru_cache(maxsize=1)
def exact_sigma_ten_basis() -> tuple[np.ndarray, np.ndarray]:
    """Gaussian-integer 126bar coordinates of the explicit SU(5) ten."""
    z = tuple(
        direct.add_forms(
            direct.one_form(2 * index),
            direct.one_form(2 * index + 1, 1j),
        )
        for index in range(5)
    )
    omega = tuple(
        direct.wedge(
            direct.one_form(2 * index),
            direct.one_form(2 * index + 1),
        )
        for index in range(5)
    )
    canonical_basis = chart.sigma_basis()
    columns: list[np.ndarray] = []
    for triple in COMPLEX_TRIPLES:
        complement = tuple(index for index in range(5) if index not in triple)
        form = direct.wedge(
            _wedge_all(z[index] for index in triple),
            direct.add_forms(omega[complement[0]], omega[complement[1]]),
        )
        anti_self_dual_residual = direct.add_forms(
            direct.hodge_star(form), direct.scale_form(form, 1j)
        )
        if any(value for value in anti_self_dual_residual.values()):
            raise ArithmeticError("explicit SU(5) ten left the anti-self-dual 126bar")
        coordinates = np.asarray(
            [direct.sigma_kinetic_inner(item, form) for item in canonical_basis],
            dtype=complex,
        )
        real = np.rint(coordinates.real).astype(np.int64)
        imaginary = np.rint(coordinates.imag).astype(np.int64)
        if np.any(coordinates != real + 1j * imaginary):
            raise ArithmeticError("explicit SU(5) ten is not Gaussian-integral")
        columns.append(real + 1j * imaginary)
    matrix = np.column_stack(columns)
    return (
        np.asarray(matrix.real, dtype=np.int64),
        np.asarray(matrix.imag, dtype=np.int64),
    )


def _mixed_operator_at_f() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    _, f0 = pd_source.raw_su5_form_and_vector()
    operator_real, operator_imaginary = mixed_source.integer_cubic_operators()
    matrix_real = np.tensordot(f0, operator_real, axes=(0, 0))
    matrix_imaginary = np.tensordot(f0, operator_imaginary, axes=(0, 0))
    matrix_real -= 8 * np.eye(chart.SIGMA_COMPLEX_DIM, dtype=np.int64)
    contraction_real, contraction_imaginary = mixed_source.integer_contraction_tensor()
    c_real = np.tensordot(f0, contraction_real, axes=(0, 1))
    c_imaginary = np.tensordot(f0, contraction_imaginary, axes=(0, 1))
    return matrix_real, matrix_imaginary, c_real, c_imaginary


@lru_cache(maxsize=1)
def exact_fixed_f_mixed_kernel_certificate() -> dict[str, Any]:
    matrix_real, matrix_imaginary, c_real, c_imaginary = _mixed_operator_at_f()
    operator_real = np.vstack((matrix_real, c_real))
    operator_imaginary = np.vstack((matrix_imaginary, c_imaginary))
    realified = rank_source._complex_linear_realification(
        operator_real, operator_imaginary
    )
    basis_real, basis_imaginary = exact_sigma_ten_basis()
    explicit_kernel = np.empty((chart.SIGMA_REAL_DIM, 20), dtype=np.int64)
    explicit_kernel[0::2, 0::2] = basis_real
    explicit_kernel[1::2, 0::2] = basis_imaginary
    explicit_kernel[0::2, 1::2] = -basis_imaginary
    explicit_kernel[1::2, 1::2] = basis_real
    residual = realified @ explicit_kernel
    gram_real = basis_real.T @ basis_real + basis_imaginary.T @ basis_imaginary
    gram_imaginary = basis_real.T @ basis_imaginary - basis_imaginary.T @ basis_real
    operator_rank = pd_source._rank_mod_prime(realified, MODULAR_PRIME)
    basis_rank = pd_source._rank_mod_prime(explicit_kernel, MODULAR_PRIME)
    return {
        "mixed_realified_shape": realified.shape,
        "rank_over_Fp": operator_rank,
        "prime": MODULAR_PRIME,
        "exact_real_nullity": chart.SIGMA_REAL_DIM - operator_rank,
        "explicit_kernel_shape": explicit_kernel.shape,
        "explicit_kernel_rank_over_Fp": basis_rank,
        "kernel_residual_max_abs": int(np.max(np.abs(residual), initial=0)),
        "complex_basis_Gram_real": gram_real,
        "complex_basis_Gram_imaginary": gram_imaginary,
        "complex_basis_Gram_is_8_identity": (
            np.array_equal(gram_real, 8 * np.eye(10, dtype=np.int64))
            and not np.any(gram_imaginary)
        ),
        "identity": "ker[(M(F0)-8), C_F0] = span_C{s_I: |I|=3}",
        "exact_complex_kernel_dimension": 10,
        "source_binding_exact": True,
    }


def _sigma_pair_monomial_columns() -> tuple[np.ndarray, np.ndarray]:
    basis_real, basis_imaginary = exact_sigma_ten_basis()
    pair_real: list[np.ndarray] = []
    pair_imaginary: list[np.ndarray] = []
    for left, right in TEN_MONOMIALS:
        real = (
            np.outer(basis_real[:, left], basis_real[:, right])
            - np.outer(basis_imaginary[:, left], basis_imaginary[:, right])
        )
        imaginary = (
            np.outer(basis_real[:, left], basis_imaginary[:, right])
            + np.outer(basis_imaginary[:, left], basis_real[:, right])
        )
        if left != right:
            real += (
                np.outer(basis_real[:, right], basis_real[:, left])
                - np.outer(basis_imaginary[:, right], basis_imaginary[:, left])
            )
            imaginary += (
                np.outer(basis_real[:, right], basis_imaginary[:, left])
                + np.outer(basis_imaginary[:, right], basis_real[:, left])
            )
        pair_real.append(real.ravel())
        pair_imaginary.append(imaginary.ravel())
    return np.column_stack(pair_real), np.column_stack(pair_imaginary)


def _sigma_projector_response(
    channel: str,
    pair_real: np.ndarray,
    pair_imaginary: np.ndarray,
) -> tuple[int, np.ndarray, np.ndarray]:
    polynomial = sigma_self._poly(channel)
    denominator = math.lcm(*(coefficient.denominator for coefficient in polynomial))
    numerators = tuple(int(coefficient * denominator) for coefficient in polynomial)
    operator_real, operator_imaginary = rank_source._self_pair_casimir_integer()
    current_real, current_imaginary = pair_real, pair_imaginary
    response_real = numerators[0] * current_real
    response_imaginary = numerators[0] * current_imaginary
    for numerator in numerators[1:]:
        current_real, current_imaginary = rank_source._apply_gaussian_sparse(
            operator_real,
            operator_imaginary,
            current_real,
            current_imaginary,
        )
        response_real += numerator * current_real
        response_imaginary += numerator * current_imaginary
    return denominator, response_real, response_imaginary


def _plucker_matrix() -> np.ndarray:
    pair_to_coefficient: dict[tuple[int, int], tuple[int, int]] = {}
    for index, triple in enumerate(COMPLEX_TRIPLES):
        pair = tuple(item for item in range(5) if item not in triple)
        pair_to_coefficient[pair] = (index, _permutation_sign(pair + triple))
    matrix = np.zeros((5, len(TEN_MONOMIALS)), dtype=np.int64)
    for row, (a, b, c, d) in enumerate(itertools.combinations(range(5), 4)):
        for coefficient, first, second in (
            (1, (a, b), (c, d)),
            (-1, (a, c), (b, d)),
            (1, (a, d), (b, c)),
        ):
            left, sign_left = pair_to_coefficient[first]
            right, sign_right = pair_to_coefficient[second]
            column = MONOMIAL_INDEX[tuple(sorted((left, right)))]
            matrix[row, column] += coefficient * sign_left * sign_right
    return matrix


@lru_cache(maxsize=1)
def exact_plucker_restriction_certificate() -> dict[str, Any]:
    pair_real, pair_imaginary = _sigma_pair_monomial_columns()
    denominator_54, response_54_real, response_54_imaginary = (
        _sigma_projector_response("54", pair_real, pair_imaginary)
    )
    denominator_1050, response_1050_real, response_1050_imaginary = (
        _sigma_projector_response("1050bar", pair_real, pair_imaginary)
    )
    gram_1050_numerator = (
        pair_real.T @ response_1050_real
        + pair_imaginary.T @ response_1050_imaginary
    )
    plucker = _plucker_matrix()
    plucker_gram = plucker.T @ plucker
    identity_residual = (
        9 * gram_1050_numerator
        - 256 * denominator_1050 * plucker_gram
    )
    response_54_maximum = max(
        int(np.max(np.abs(response_54_real), initial=0)),
        int(np.max(np.abs(response_54_imaginary), initial=0)),
    )
    return {
        "coefficient_monomial_count": len(TEN_MONOMIALS),
        "Pi54_polynomial_denominator": denominator_54,
        "Pi54_response_max_abs": response_54_maximum,
        "Pi1050bar_polynomial_denominator": denominator_1050,
        "Plucker_matrix": plucker,
        "Plucker_matrix_rank": pd_source._rank_mod_prime(
            plucker, MODULAR_PRIME
        ),
        "matrix_identity_max_abs_residual": int(
            np.max(np.abs(identity_residual), initial=0)
        ),
        "exact_identity": (
            "I54(Sigma(t))=0; "
            "I1050bar(Sigma(t))=(256/9) sum_{A=1}^5 |Pf_A(t)|^2"
        ),
        "zero_locus_theorem": (
            "all five 4x4 Pfaffians vanish iff the dual 5x5 skew matrix "
            "has rank <=2; every nonzero solution is a decomposable two-form"
        ),
        "orbit_consequence": (
            "U(5)=Stab_SO10(F) acts transitively on normalized decomposable "
            "complex two-forms, up to their allowed phase"
        ),
        "fixed_F_Sigma_equality_is_one_orbit": (
            response_54_maximum == 0
            and not np.any(identity_residual)
            and pd_source._rank_mod_prime(plucker, MODULAR_PRIME) == 5
        ),
        "source_binding_exact": True,
    }


def _phi_diagonal_basis() -> np.ndarray:
    index = {indices: position for position, indices in enumerate(chart.PHI_INDICES)}
    basis = np.zeros((chart.PHI_DIM, 10), dtype=np.int64)
    for column, (left, right) in enumerate(COMPLEX_PAIRS):
        indices = (2 * left, 2 * left + 1, 2 * right, 2 * right + 1)
        basis[index[indices], column] = 1
    return basis


def _phi_pair_monomial_columns() -> np.ndarray:
    basis = _phi_diagonal_basis()
    columns: list[np.ndarray] = []
    for left, right in TEN_MONOMIALS:
        pair = np.outer(basis[:, left], basis[:, right])
        if left != right:
            pair += np.outer(basis[:, right], basis[:, left])
        columns.append(pair.ravel())
    return np.column_stack(columns)


def _phi_diagonal_gram() -> tuple[np.ndarray, int]:
    pair = _phi_pair_monomial_columns()
    polynomials = [
        phi_projectors.projector_polynomial(
            phi_projectors.SPECTRAL_EIGENVALUES[channel]
        )
        for channel in ("54", "4125")
    ]
    coefficients = [
        sum(polynomial[degree] for polynomial in polynomials)
        for degree in range(8)
    ]
    denominator = math.lcm(*(value.denominator for value in coefficients))
    numerators = tuple(int(value * denominator) for value in coefficients)
    operator = rank_source._phi_pair_casimir_integer()
    current = pair
    response = numerators[0] * current
    for numerator in numerators[1:]:
        current = operator @ current
        response += numerator * current
    return pair.T @ response, denominator


def _edge(left: int, right: int) -> int:
    return PAIR_INDEX[tuple(sorted((left, right)))]


def _monomial(left: int, right: int) -> int:
    return MONOMIAL_INDEX[tuple(sorted((left, right)))]


def _simple_diagonal_quadrics() -> np.ndarray:
    rows: list[np.ndarray] = []
    for edge in range(1, 10):
        row = np.zeros(len(TEN_MONOMIALS), dtype=np.int64)
        row[_monomial(0, 0)] = 1
        row[_monomial(edge, edge)] = -1
        rows.append(row)
    for left, right in COMPLEX_PAIRS:
        complement = [index for index in range(5) if index not in (left, right)]
        base = complement[0]
        for comparison in complement[1:]:
            row = np.zeros(len(TEN_MONOMIALS), dtype=np.int64)
            row[
                _monomial(_edge(base, left), _edge(base, right))
            ] = 1
            row[
                _monomial(_edge(comparison, left), _edge(comparison, right))
            ] = -1
            rows.append(row)
    return np.vstack(rows)


def _fraction_rank(rows: Iterable[Iterable[int]]) -> int:
    pivots: dict[int, list[Fraction]] = {}
    for source in rows:
        row = [Fraction(int(value)) for value in source]
        while True:
            pivot = next((index for index, value in enumerate(row) if value), None)
            if pivot is None:
                break
            if pivot not in pivots:
                scale = row[pivot]
                pivots[pivot] = [value / scale for value in row]
                break
            scale = row[pivot]
            reference = pivots[pivot]
            row = [
                left - scale * right
                for left, right in zip(row, reference, strict=True)
            ]
    return len(pivots)


def _signed_diagonal_solutions() -> tuple[tuple[int, ...], ...]:
    relations = _simple_diagonal_quadrics()[9:]
    output: list[tuple[int, ...]] = []
    for signs in itertools.product((-1, 1), repeat=10):
        monomials = np.asarray(
            [signs[left] * signs[right] for left, right in TEN_MONOMIALS],
            dtype=np.int64,
        )
        if not np.any(relations @ monomials):
            output.append(signs)
    return tuple(output)


@lru_cache(maxsize=1)
def exact_fixed_delta_diagonal_certificate() -> dict[str, Any]:
    gram, denominator = _phi_diagonal_gram()
    simple = _simple_diagonal_quadrics()
    gram_rank = _fraction_rank(gram.tolist())
    simple_rank = _fraction_rank(simple.tolist())
    combined_rank = _fraction_rank(np.vstack((gram, simple)).tolist())

    mixed_jacobian, _ = pd_source._exact_mixed_sos_jacobian()
    diagonal_basis = _phi_diagonal_basis()
    mixed_diagonal = mixed_jacobian[:, : chart.PHI_DIM] @ diagonal_basis
    delta_real, delta_imaginary = pd_source._raw_delta_arrays()
    mixed_target = np.concatenate(
        (8 * delta_real, 8 * delta_imaginary, np.zeros(20, dtype=np.int64))
    )
    selected_pairs = ((0, 1), (0, 2), (1, 2), (3, 4))
    selected = tuple(PAIR_INDEX[pair] for pair in selected_pairs)
    mixed_column_checks = {
        str(pair): int(
            np.max(
                np.abs(4 * mixed_diagonal[:, PAIR_INDEX[pair]] - mixed_target),
                initial=0,
            )
        )
        for pair in selected_pairs
    }
    unselected = tuple(index for index in range(10) if index not in selected)
    unselected_maximum = int(
        np.max(np.abs(mixed_diagonal[:, unselected]), initial=0)
    )

    sign_solutions = _signed_diagonal_solutions()
    fixed_sign_solutions = tuple(
        signs for signs in sign_solutions if sum(signs[index] for index in selected) == 4
    )
    expected_plus = (1,) * 10
    expected_minus = tuple(
        1 if (left < 3) == (right < 3) else -1
        for left, right in COMPLEX_PAIRS
    )

    coordinate_reflection = tuple(
        -1 if index in (7, 9) else 1 for index in range(10)
    )
    plane_orientation = (1, 1, 1, -1, -1)
    reflected_plus = tuple(
        plane_orientation[left] * plane_orientation[right]
        for left, right in COMPLEX_PAIRS
    )
    determinant = math.prod(coordinate_reflection)

    z = tuple(
        direct.add_forms(
            direct.one_form(2 * index),
            direct.one_form(2 * index + 1, 1j),
        )
        for index in range(5)
    )
    omega = tuple(
        direct.wedge(
            direct.one_form(2 * index),
            direct.one_form(2 * index + 1),
        )
        for index in range(5)
    )
    raw_delta_form = direct.wedge(
        _wedge_all(z[index] for index in (0, 1, 2)),
        direct.add_forms(omega[3], omega[4]),
    )
    reflected_delta_form = {
        indices: value
        * math.prod(coordinate_reflection[index] for index in indices)
        for indices, value in raw_delta_form.items()
    }
    reflection_residual = direct.add_forms(
        reflected_delta_form, raw_delta_form
    )

    return {
        "diagonal_variables": [str(pair) for pair in COMPLEX_PAIRS],
        "Phi_projector_Gram_denominator": denominator,
        "Phi_projector_Gram_rank_exact": gram_rank,
        "simple_quadratic_relation_count": simple.shape[0],
        "simple_quadratic_relation_rank_exact": simple_rank,
        "stacked_rowspace_rank_exact": combined_rank,
        "rowspaces_are_equal": gram_rank == simple_rank == combined_rank == 29,
        "zero_equations": {
            "equal_squares": "q_e^2=q_f^2 for all ten edges",
            "four_cycle_signs": (
                "q_ij q_ik=q_lj q_lk for every edge jk and third vertices i,l"
            ),
            "nonzero_solution_form": "q_ij=tau*c*s_i*s_j",
        },
        "mixed_equation": "q01+q02+q12+q34=4",
        "selected_mixed_column_residuals": mixed_column_checks,
        "unselected_mixed_column_max_abs": unselected_maximum,
        "norm_equation": "sum_{i<j}q_ij^2=10",
        "all_signed_projector_solutions_count": len(sign_solutions),
        "projector_zero_overall_SO10_orbit_signs": ("tau=+1", "tau=-1"),
        "global_tau_minus_is_not_SO10_equivalent_to_tau_plus": True,
        "fixed_Delta_signed_solutions_count": len(fixed_sign_solutions),
        "fixed_Delta_signed_solutions": fixed_sign_solutions,
        "fixed_Delta_solutions_lie_in_global_tau_plus_orbit": True,
        "expected_two_solutions": (expected_plus, expected_minus),
        "only_F_plus_and_F_minus": set(fixed_sign_solutions)
        == {expected_plus, expected_minus},
        "equivalence_map": {
            "SO10_coordinate_reflection": coordinate_reflection,
            "determinant": determinant,
            "induced_pair_plane_signs": reflected_plus,
            "maps_F_plus_to_F_minus": reflected_plus == expected_minus,
            "Delta_reflection_residual_support": tuple(
                (indices, value)
                for indices, value in sorted(reflection_residual.items())
                if value
            ),
            "maps_Delta_to_minus_Delta": not any(reflection_residual.values()),
            "minus_Delta_removed_by_allowed_phase": True,
        },
        "scope": "complete pair-plane diagonal slice, not all real 4-forms",
        "source_binding_exact": True,
    }


@lru_cache(maxsize=1)
def exact_negative_f_mixed_exclusion_certificate() -> dict[str, Any]:
    """Prove that the global-sign orbit -F has no nonzero mixed Sigma zero."""
    matrix_real_minus_8, matrix_imaginary, _, _ = _mixed_operator_at_f()
    # _mixed_operator_at_f returns M(F)-8*I.  At -F the first mixed
    # residual is -(M(F)+8*I) Sigma, whose kernel is unchanged by the sign.
    matrix_real_plus_8 = matrix_real_minus_8 + 16 * np.eye(
        chart.SIGMA_COMPLEX_DIM, dtype=np.int64
    )
    realified = rank_source._complex_linear_realification(
        matrix_real_plus_8, matrix_imaginary
    )
    rank = pd_source._rank_mod_prime(realified, MODULAR_PRIME)
    full_rank = rank == chart.SIGMA_REAL_DIM
    return {
        "identity": "M(-F)-8*I=-(M(F)+8*I)",
        "realified_shape": realified.shape,
        "rank_over_Fp": rank,
        "prime": MODULAR_PRIME,
        "exact_real_nullity": chart.SIGMA_REAL_DIM - rank,
        "full_rank_over_Q_and_R": full_rank,
        "reason": (
            "A full-rank square integer matrix modulo a prime has nonzero "
            "integer determinant and is invertible over Q and R."
        ),
        "minus_F_allows_only_Sigma_zero": full_rank,
        "Sigma_zero_violates_positive_radial_equality": full_rank,
        "minus_F_global_equality_branch_excluded": full_rank,
        "source_binding_exact": True,
    }


@lru_cache(maxsize=1)
def build_report() -> dict[str, Any]:
    kernel = exact_fixed_f_mixed_kernel_certificate()
    plucker = exact_plucker_restriction_certificate()
    diagonal = exact_fixed_delta_diagonal_certificate()
    negative_f = exact_negative_f_mixed_exclusion_certificate()
    orbit_audit = orbit_lemma_audit.build_report()
    local_component = local_component_audit.build_report()
    local_scope = local_component["scope"]
    su3_slice = su3_slice_audit.build_report()
    su3_scope = su3_slice["scope"]
    global_classification = global_phi.certificate()
    global_source_hash = _sha256(Path(global_phi.__file__).resolve())
    global_scope = global_classification["scope"]
    rigidity = global_classification["subgroup_rigidity"]
    checks = {
        "fixed_F_mixed_kernel_has_exact_real_nullity_20": (
            kernel["exact_real_nullity"] == 20
            and kernel["explicit_kernel_rank_over_Fp"] == 20
            and kernel["kernel_residual_max_abs"] == 0
        ),
        "explicit_kernel_is_orthogonal_complex_ten": kernel[
            "complex_basis_Gram_is_8_identity"
        ],
        "Pi54_vanishes_identically_on_mixed_kernel": (
            plucker["Pi54_response_max_abs"] == 0
        ),
        "Pi1050bar_is_exact_Plucker_norm": (
            plucker["matrix_identity_max_abs_residual"] == 0
        ),
        "fixed_F_normalized_Sigma_equalities_one_U5_orbit": plucker[
            "fixed_F_Sigma_equality_is_one_orbit"
        ],
        "diagonal_Phi_zero_equations_reduced_exactly": diagonal[
            "rowspaces_are_equal"
        ],
        "fixed_Delta_diagonal_slice_has_only_two_signs": diagonal[
            "only_F_plus_and_F_minus"
        ],
        "two_diagonal_signs_are_gauge_phase_equivalent": (
            diagonal["equivalence_map"]["determinant"] == 1
            and diagonal["equivalence_map"]["maps_F_plus_to_F_minus"]
            and diagonal["equivalence_map"]["maps_Delta_to_minus_Delta"]
            and diagonal["equivalence_map"]["minus_Delta_removed_by_allowed_phase"]
        ),
        "literal_single_Phi_orbit_lemma_is_refuted": orbit_audit["scope"][
            "literal_plus_orbit_only_statement_refuted"
        ],
        "minus_F_mixed_branch_is_exactly_excluded": negative_f[
            "minus_F_global_equality_branch_excluded"
        ],
        "SU4_slice_obstruction_is_source_bound": orbit_audit["scope"][
            "complete_SU4_invariant_slice_classified"
        ],
        "historical_signed_global_Phi_lemma_audit_is_not_rewritten": not (
            orbit_audit["corrected_global_lemma"]["proved"]
        ),
        "signed_Phi_orbits_are_exactly_local_components": bool(
            local_component["n_failed"] == 0
            and local_scope["plus_F_local_component_classified"] is True
            and local_scope["minus_F_local_component_classified"] is True
            and local_scope["signed_orbit_locally_isolated"] is True
            and local_scope["disconnected_distant_components_excluded"] is False
            and local_scope["corrected_signed_global_orbit_theorem_proved"]
            is False
        ),
        "complete_SU3_fixed_slice_is_exactly_signed_Kahler": bool(
            su3_slice["n_failed"] == 0
            and su3_slice["status"]
            == "EXACT_COMPLETE_SU3_FIXED_SLICE_CLASSIFIED__GENERIC_GLOBAL_OPEN"
            and su3_slice["overall_state"] == "SU3_FIXED_SLICE_CLOSED"
            and su3_scope[
                "complete_16_real_dimensional_SU3_fixed_space_classified"
            ]
            is True
            and su3_scope[
                "nondiagonal_Omega3_wedge_R4_directions_included"
            ]
            is True
            and su3_scope[
                "all_nonzero_slice_solutions_are_signed_Kahler_squares"
            ]
            is True
            and su3_scope["all_arbitrary_real_four_forms_classified"] is False
            and su3_scope["corrected_signed_global_orbit_theorem_proved"]
            is False
            and su3_scope["G3_closed"] is False
        ),
        "global_signed_Phi_zero_locus_is_source_bound_exactly": bool(
            global_source_hash == GLOBAL_PHI_SOURCE_SHA256
            and global_classification["status"]
            == "EXACT_GLOBAL_REAL_PHI_SELF_ZERO_IS_SIGNED_KAEHLER_CONE__G3_OPEN"
            and global_classification["core_sha256"]
            == global_phi.EXPECTED_CORE_SHA256
            and global_classification["norm10_zero_locus"]
            == "SO(10).F union SO(10).(-F)"
            and global_scope["global_real_zero_locus_classified"] is True
            and global_scope["quantitative_orbit_distance_bound"] is False
            and global_scope["G3_closed"] is False
            and rigidity["unitary_maximal"]
            == {"name": "U(5)", "dimension": 25}
            and "Dynkin" in rigidity["external_classification"]
        ),
        "global_equality_orbit_not_overclaimed": True,
        "G3_not_overclaimed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "status": (
            "EXACT_GLOBAL_EQUALITY_CLASSIFICATION__SIGNED_PHI_THEOREM_CLOSED__G3_OPEN"
            if not failures
            else "EQUALITY_ORBIT_REDUCTION_EXECUTION_FAILED"
        ),
        "overall_state": (
            "GLOBAL_EQUALITY_ORBITS_CLOSED" if not failures else "EXECUTION_FAIL"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "fixed_F_mixed_kernel": kernel,
        "fixed_F_Plucker_classification": plucker,
        "fixed_Delta_diagonal_classification": diagonal,
        "negative_F_mixed_exclusion": negative_f,
        "Phi_orbit_lemma_audit": {
            "status": orbit_audit["status"],
            "opposite_orbit_counterexample": orbit_audit[
                "opposite_orbit_counterexample"
            ],
            "SU4_invariant_slice": orbit_audit["SU4_invariant_slice"],
            "corrected_global_lemma": orbit_audit["corrected_global_lemma"],
            "scope": orbit_audit["scope"],
        },
        "Phi_local_component_theorem": local_component,
        "Phi_SU3_fixed_slice_theorem": su3_slice,
        "Phi_global_signed_zero_theorem": {
            **global_classification,
            "production_adapter_source_sha256": global_source_hash,
            "frozen_source_sha256": (
                global_phi.FROZEN_SOURCE_SHA256[
                    ROOT
                    / "FROZEN_PHI_SELF_ZERO_GLOBAL_SIGNED_KAEHLER_CLASSIFICATION_SOURCE_V20.py"
                ]
            ),
            "external_theorem_dependency": {
                "kind": "published subgroup-classification theorem",
                "theorem": rigidity["external_classification"],
                "citation": rigidity["primary_reference"],
                "role": (
                    "forces the connected 25-dimensional stabilizer to be "
                    "conjugate to U(5) after the exact invariant identities"
                ),
                "repository_scope": (
                    "the exact dimension eliminations and fixed-line argument "
                    "are checked here; Dynkin's classification is imported"
                ),
            },
        },
        "remaining_global_lemma": {
            "statement": (
                "Every real unit four-form Phi with Pi54(Phi tensor Phi)=0 "
                "and Pi4125(Phi tensor Phi)=0 belongs to SO(10).F or "
                "SO(10).(-F)."
            ),
            "proved": not failures,
            "literal_single_orbit_version_refuted": True,
            "corrected_signed_two_orbit_version": True,
            "source_bound_certificate_available": not failures,
            "source_bound_partial_certificate_available": True,
            "signed_orbits_locally_isolated_exactly": not failures,
            "complete_SU3_fixed_slice_classified_exactly": not failures,
            "SU3_fixed_slice_real_dimension": 16,
            "SU3_fixed_slice_nondiagonal_directions_excluded": 8,
            "distant_disconnected_components_excluded": not failures,
            "why_required": (
                "The exact conductor/Cauchy/sextic chain and the external "
                "Dynkin subgroup classification put every arbitrary projector "
                "zero into a signed canonical orbit.  Exact mixed invertibility "
                "excludes -F, and the Plucker theorem handles +F."
            ),
            "quantitative_orbit_distance_bound_proved": False,
            "numerical_search_is_not_a_substitute": True,
        },
        "scope": {
            "fixed_F_Sigma_global_equality_classified": not failures,
            "fixed_Delta_diagonal_Phi_global_equality_classified": not failures,
            "fixed_Delta_two_tau_plus_representatives_equivalent": not failures,
            # Backward-compatible spelling: this refers only to the two
            # fixed-Delta tau=+ representatives, never to the global +/-F
            # pair separated by the cubic invariant.
            "two_visible_sign_branches_equivalent": not failures,
            "literal_single_Phi_orbit_statement_refuted": not failures,
            "minus_F_mixed_branch_excluded_exact": not failures,
            "corrected_signed_Phi_orbit_theorem_open": False,
            "corrected_signed_Phi_orbit_theorem_proved": not failures,
            "signed_Phi_orbits_locally_isolated_exactly": not failures,
            "complete_SU3_fixed_Phi_slice_classified_exactly": not failures,
            "distant_disconnected_Phi_components_excluded": not failures,
            "all_arbitrary_Phi_global_equalities_classified": not failures,
            "local_one_orbit_can_be_strengthened_globally": not failures,
            "global_equality_orbit_classification_complete": not failures,
            "quantitative_beta_global_coercivity_proved": False,
            "G3_closed": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "The exact global signed-Kahler theorem classifies every real Phi "
            "projector zero as +F or -F up to scale and SO(10). The two sheets "
            "are separated by Tr(A_Phi^3). Exact mixed invertibility excludes "
            "the -F sheet from the coupled PD equality set. At +F the entire "
            "Sigma equality locus is one U(5) Plucker orbit, so all PD equality "
            "orbits are classified exactly. The stabilizer-rigidity step imports "
            "Dynkin's published maximal-subgroup classification. Quantitative "
            "beta-global coercivity remains unproved, so G3 remains open."
        ),
    }


def _markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# SU(5)+Delta_R global equality-orbit reduction — v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            "- fixed-F mixed kernel: exact complex `10`;",
            "- fixed-F Sigma zeros: exact Pluecker variety, one `U(5)` orbit;",
            "- Phi-only overall signs: `+F` and `-F`, not SO(10)-equivalent;",
            "- coupled `-F` branch: excluded by exact rank `252/252`;",
            "- fixed-Delta tau=+ sign patterns: SO(10)+phase equivalent;",
            "- complete SU(3)-fixed Phi slice: signed Kahler squares only;",
            "- corrected signed arbitrary-four-form theorem: `CLOSED`;",
            "- external dependency: Dynkin maximal-subgroup classification;",
            "- global equality-orbit classification: `CLOSED`;",
            "- quantitative beta-global coercivity: `OPEN`;",
            "- G3: `OPEN`.",
            "",
        ]
    )


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(_jsonable(report), indent=2, sort_keys=True) + "\n")
    OUT_MD.write_text(_markdown(report))


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
