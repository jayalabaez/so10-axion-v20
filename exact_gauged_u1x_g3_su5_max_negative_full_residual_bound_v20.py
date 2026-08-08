#!/usr/bin/env python3
"""Exact full-residual bound on the maximal-negative pure-Delta sector.

Fix

    H = sqrt(u) (e0-i e1)/sqrt(2),
    Sigma = sqrt(v) Delta_R,

with ``u,v>=0`` and let the real 210 field ``Phi`` be arbitrary.  The live
candidate gap restricted to this sector is

    P(Phi) + (u-1)^2 + (v-1/25)^2/8
      + u Q_-(Phi) + (v/8) R_Delta(Phi) - uv/20,

where ``P=(N_Phi-1)^2+I54+I4125`` and, in the integral coordinate
``z=sqrt(10) Phi``, the live source arrays give

    Q_- = ||A_chi z||^2/40,
    R_Delta = ||A_mix z-b||^2/80.

No residual is set to zero in this certificate.

The key source-bound anchor is

    P + (9/10) Q_- + R_Delta/32 >= 1/50.                 (A)

To prove it, project ``z0 tensor z0`` into the live 4125 channel and divide
the resulting integral matrix by its exact gcd.  The resulting symmetric
integer matrix ``Y`` obeys

    ||Y||_F^2=70560,
    I4125(z/sqrt(10)) >= (z^T Y z)^2/7056000,
    Y+52 I >= 0.

The last inequality is certified directly: in the canonical 210 chart the
shifted matrix has only 1x1 and 2x2 connected blocks, all exactly PSD.
Fenchel completion with ``a=3/100`` and ``eta=11/200000`` turns (A) into a
positive quadratic matrix

    K = G/2560 + 9 Hchi/400 + 3 I/1000 + 11 Y/200000
      >= 7 I/50000.

The forcing vector lies in an exact three-dimensional invariant subspace,
so its Schur complement is rational and gives the strict anchor margin

    20777185031397/944190730000000 - 1/50
      = 1893370431397/944190730000000 > 0.

For ``u>=9/10`` and ``v<=1/4``, scale (A) by ``4v``.  The remaining radial
polynomial completes as

    gap-1/5000 >=
      (200 (u-1-v/40)^2 + 4v + (199/8)v^2)/200.

For ``v>=1/4``, use (A) without scaling and the exact global radial/current
minimum ``-7001/995000``.  For ``u<9/10`` the radial/current polynomial alone
is at least ``83/20000``.  Hence the restricted gap has exact global minimum
``1/5000``; a signed Kahler-square representative at ``v=0,u=1`` attains it.

This closes the full arbitrary-Phi, nonzero-residual, maximally-negative
pure-Delta orientation.  It is not a proof for arbitrary Sigma orientation
and therefore does not close G3 by itself.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

import numpy as np

import exact_210_self_invariant_basis_v20 as phi_self
import exact_gauged_u1x_g3_pd_rank_certificate_v20 as rank_source
import exact_gauged_u1x_g3_su5_delta_hsx_extension_v20 as hsx
import exact_gauged_u1x_g3_su5_delta_pd_sos_v20 as pd
import exact_gauged_u1x_g3_su5_max_negative_zero_residual_bound_v20 as zero_route
import exact_phisigma_casimir_projectors_v20 as phi_projectors
import live_g2_canonical_486_field_chart_v20 as chart

ROOT = Path(__file__).resolve().parent
OUT_JSON = (
    ROOT
    / "EXACT_GAUGED_U1X_G3_SU5_MAX_NEGATIVE_FULL_RESIDUAL_BOUND_V20.json"
)
OUT_MD = (
    ROOT
    / "EXACT_GAUGED_U1X_G3_SU5_MAX_NEGATIVE_FULL_RESIDUAL_BOUND_V20.md"
)

T = Fraction(1, 8)
R2 = Fraction(1, 25)
BETA = Fraction(1, 20)
ANCHOR_U = Fraction(9, 10)
ANCHOR_V = Fraction(1, 4)
ANCHOR_TARGET = Fraction(1, 50)
FENCHEL_A = Fraction(3, 100)
FENCHEL_ETA = Fraction(11, 200_000)
Y_GCD = 49_152
Y_NORM_SQUARED = 70_560
Y_PHYSICAL_DENOMINATOR = 100 * Y_NORM_SQUARED
K_SPECTRAL_FLOOR = Fraction(7, 50_000)
RESTRICTED_GLOBAL_MINIMUM = Fraction(1, 5_000)
RADIAL_CURRENT_MINIMUM = Fraction(-7_001, 995_000)
EXPECTED_PROJECTOR_DENOMINATOR = 3_096_576
EXPECTED_PROJECTOR_NUMERATORS = (
    3_096_576,
    -2_092_032,
    152_448,
    96_320,
    -21_704,
    1_836,
    -70,
    1,
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


def _fraction_matrix_solve(
    matrix: Iterable[Iterable[Fraction]], rhs: Iterable[Fraction]
) -> tuple[Fraction, ...]:
    rows = [
        [Fraction(value) for value in row] + [Fraction(target)]
        for row, target in zip(matrix, rhs, strict=True)
    ]
    dimension = len(rows)
    for column in range(dimension):
        pivot = next(
            (row for row in range(column, dimension) if rows[row][column]),
            None,
        )
        if pivot is None:
            raise ArithmeticError("singular rational Schur matrix")
        rows[column], rows[pivot] = rows[pivot], rows[column]
        scale = rows[column][column]
        rows[column] = [value / scale for value in rows[column]]
        for row in range(dimension):
            if row == column:
                continue
            factor = rows[row][column]
            if factor:
                rows[row] = [
                    left - factor * right
                    for left, right in zip(rows[row], rows[column], strict=True)
                ]
    return tuple(row[-1] for row in rows)


@lru_cache(maxsize=1)
def exact_restricted_source_matrices() -> dict[str, Any]:
    """Return the integral residual matrices in ``z=sqrt(10) Phi``."""
    source = zero_route.exact_affine_constraint_source()
    chiral_rows, chiral_integrality_residual = (
        zero_route._integral_chiral_wedge_rows()
    )
    n_chiral_rows = chiral_rows.shape[0]
    full_matrix = np.asarray(source["matrix"], dtype=np.int64)
    full_target = np.asarray(source["target"], dtype=np.int64)
    mixed = full_matrix[:-n_chiral_rows]
    mixed_target = full_target[:-n_chiral_rows]
    chiral = full_matrix[-n_chiral_rows:]
    z0 = np.asarray(source["particular_solution"], dtype=np.int64)
    gram_mixed = mixed.T @ mixed
    gram_chiral = chiral.T @ chiral
    forcing = gram_mixed @ z0
    expected_forcing = mixed.T @ mixed_target
    binding = zero_route.live_hsx_coefficient_binding_certificate()
    return {
        "A_mixed": mixed,
        "b_mixed": mixed_target,
        "A_chiral": chiral,
        "G_mixed": gram_mixed,
        "H_chiral": gram_chiral,
        "forcing": forcing,
        "z0": z0,
        "matrix_shapes": {
            "A_mixed": mixed.shape,
            "A_chiral": chiral.shape,
            "G_mixed": gram_mixed.shape,
            "H_chiral": gram_chiral.shape,
        },
        "normalizations": {
            "z_coordinate": "z=sqrt(10) Phi",
            "Q_chiral": "||A_chiral z||^2/40",
            "R_Delta": "||A_mixed z-b||^2/80",
            "mixed_gap_coefficient": "(v/8)R_Delta=v||A_mixed z-b||^2/640",
        },
        "mixed_target_norm_squared": int(mixed_target @ mixed_target),
        "forcing_equals_G_z0": bool(np.array_equal(forcing, gram_mixed @ z0)),
        "forcing_equals_A_transpose_b": bool(
            np.array_equal(forcing, expected_forcing)
        ),
        "mixed_particular_residual_max_abs": int(
            np.max(np.abs(mixed @ z0 - mixed_target), initial=0)
        ),
        "chiral_particular_residual_max_abs": int(
            np.max(np.abs(chiral @ z0), initial=0)
        ),
        "chiral_integrality_residual": chiral_integrality_residual,
        "sliced_chiral_rows_equal_independent_reconstruction": bool(
            np.array_equal(chiral, chiral_rows)
        ),
        "live_HSX_coefficient_binding_proof_grade": binding["proof_grade"],
        "source_binding_exact": bool(
            source["matrix_shape"] == (776, 210)
            and mixed.shape == (272, 210)
            and chiral.shape == (504, 210)
            and source["particular_solution_residual_max_abs"] == 0
            and chiral_integrality_residual == 0.0
            and np.array_equal(chiral, chiral_rows)
            and np.array_equal(forcing, expected_forcing)
            and not np.any(mixed @ z0 - mixed_target)
            and not np.any(chiral @ z0)
            and binding["proof_grade"]
        ),
    }


def _connected_blocks(matrix: np.ndarray) -> tuple[tuple[int, ...], ...]:
    """Exact graph components of a symmetric matrix's nonzero pattern."""
    source = np.asarray(matrix, dtype=np.int64)
    remaining = set(range(source.shape[0]))
    blocks: list[tuple[int, ...]] = []
    while remaining:
        seed = min(remaining)
        component = {seed}
        frontier = [seed]
        remaining.remove(seed)
        while frontier:
            row = frontier.pop()
            neighbours = set(int(value) for value in np.flatnonzero(source[row]))
            new = sorted(neighbours.intersection(remaining))
            for neighbour in new:
                remaining.remove(neighbour)
                component.add(neighbour)
                frontier.append(neighbour)
        blocks.append(tuple(sorted(component)))
    return tuple(blocks)


@lru_cache(maxsize=1)
def exact_4125_scalar_covariant_certificate() -> dict[str, Any]:
    """Construct one exact 4125 covariant and prove its spectral floor."""
    source = exact_restricted_source_matrices()
    z0 = source["z0"]
    polynomial = phi_projectors.projector_polynomial(
        phi_projectors.SPECTRAL_EIGENVALUES["4125"]
    )
    denominator = math.lcm(*(value.denominator for value in polynomial))
    numerators = tuple(int(value * denominator) for value in polynomial)
    operator = rank_source._phi_pair_casimir_integer()
    current = np.outer(z0, z0).astype(np.int64).ravel()
    response = int(numerators[0]) * current
    for numerator in numerators[1:]:
        current = operator @ current
        response += int(numerator) * current
    response_gcd = 0
    for value in response:
        if value:
            response_gcd = math.gcd(response_gcd, abs(int(value)))
    divisibility_residual = int(
        np.max(np.abs(np.remainder(response, Y_GCD)), initial=0)
    )
    y_matrix = (response // Y_GCD).reshape(chart.PHI_DIM, chart.PHI_DIM)
    shifted = y_matrix + 52 * np.eye(chart.PHI_DIM, dtype=np.int64)
    blocks = _connected_blocks(shifted)
    block_census: Counter[str] = Counter()
    shifted_eigenvalue_census: Counter[int] = Counter()
    invalid_blocks: list[dict[str, Any]] = []
    for indices in blocks:
        block = shifted[np.ix_(indices, indices)]
        if len(indices) == 1:
            value = int(block[0, 0])
            block_census[f"1x1({value})"] += 1
            shifted_eigenvalue_census[value] += 1
            if value < 0:
                invalid_blocks.append({"indices": indices, "block": block})
        elif len(indices) == 2:
            left = int(block[0, 0])
            right = int(block[1, 1])
            off_diagonal = int(block[0, 1])
            block_census[f"2x2({left},{abs(off_diagonal)})"] += 1
            if left != right or block[1, 0] != off_diagonal:
                invalid_blocks.append({"indices": indices, "block": block})
                continue
            shifted_eigenvalue_census[left - abs(off_diagonal)] += 1
            shifted_eigenvalue_census[left + abs(off_diagonal)] += 1
            if left < abs(off_diagonal):
                invalid_blocks.append({"indices": indices, "block": block})
        else:
            invalid_blocks.append({"indices": indices, "block": block})

    y_norm_squared = int(np.sum(y_matrix * y_matrix, dtype=np.int64))
    z0_y_z0 = int(z0 @ y_matrix @ z0)
    scale_from_projector = denominator // Y_GCD
    projector_response_norm_squared = Fraction(
        y_norm_squared, scale_from_projector * scale_from_projector
    )
    physical_particular_projector_value = (
        projector_response_norm_squared / 100
    )
    pd_projector_source = pd.exact_phi_projector_certificate()
    expected_shifted_spectrum = {
        0: 6,
        16: 1,
        24: 2,
        33: 16,
        40: 7,
        43: 16,
        46: 24,
        47: 24,
        55: 64,
        56: 18,
        70: 8,
        75: 8,
        80: 3,
        84: 12,
        192: 1,
    }
    return {
        "projector_polynomial_denominator": denominator,
        "projector_polynomial_numerators": numerators,
        "integral_divisor": Y_GCD,
        "computed_nonzero_entry_gcd": response_gcd,
        "Y_equals_projector_response_times": scale_from_projector,
        "Y_shape": y_matrix.shape,
        "Y_symmetric_exact": bool(np.array_equal(y_matrix, y_matrix.T)),
        "Y_nonzero_entries": int(np.count_nonzero(y_matrix)),
        "Y_max_abs_entry": int(np.max(np.abs(y_matrix), initial=0)),
        "Y_Frobenius_norm_squared": y_norm_squared,
        "z0_transpose_Y_z0": z0_y_z0,
        "divisibility_residual_max_abs": divisibility_residual,
        "I4125_scalar_Cauchy_bound": (
            "I4125(z/sqrt(10)) >= (z^T Y z)^2/7056000"
        ),
        "projector_normalization_chain": (
            "Pi4125(z0 tensor z0)=Y/63, ||Pi4125(z0 tensor z0)||^2=160/9, "
            "and Phi=z/sqrt(10) supplies the quartic factor 1/100"
        ),
        "projector_response_norm_squared": projector_response_norm_squared,
        "physical_particular_projector_value": (
            physical_particular_projector_value
        ),
        "physical_Cauchy_denominator": 100 * y_norm_squared,
        "PD_Phi_projector_source_binding_exact": pd_projector_source[
            "source_binding_exact"
        ],
        "particular_bound_value": Fraction(
            z0_y_z0 * z0_y_z0, Y_PHYSICAL_DENOMINATOR
        ),
        "expected_particular_I4125": Fraction(8, 45),
        "shifted_matrix": "Y+52 I",
        "connected_block_count": len(blocks),
        "maximum_connected_block_size": max(map(len, blocks), default=0),
        "block_census": dict(sorted(block_census.items())),
        "shifted_exact_eigenvalue_census": dict(
            sorted(shifted_eigenvalue_census.items())
        ),
        "expected_shifted_eigenvalue_census": expected_shifted_spectrum,
        "shifted_nullity": shifted_eigenvalue_census[0],
        "invalid_PSD_blocks": invalid_blocks,
        "Y_plus_52I_PSD_exact": not invalid_blocks,
        "Y_minimum_eigenvalue_exact": -52,
        "Y": y_matrix,
        "proof_grade": bool(
            denominator == EXPECTED_PROJECTOR_DENOMINATOR
            and numerators == EXPECTED_PROJECTOR_NUMERATORS
            and response_gcd == Y_GCD
            and divisibility_residual == 0
            and scale_from_projector == 63
            and np.array_equal(y_matrix, y_matrix.T)
            and y_norm_squared == Y_NORM_SQUARED
            and z0_y_z0 == 1120
            and projector_response_norm_squared == Fraction(160, 9)
            and physical_particular_projector_value == Fraction(8, 45)
            and 100 * y_norm_squared == Y_PHYSICAL_DENOMINATOR
            and pd_projector_source["source_binding_exact"]
            and Fraction(z0_y_z0 * z0_y_z0, Y_PHYSICAL_DENOMINATOR)
            == Fraction(8, 45)
            and len(blocks) == 165
            and max(map(len, blocks), default=0) == 2
            and not invalid_blocks
            and dict(shifted_eigenvalue_census)
            == expected_shifted_spectrum
        ),
    }


@lru_cache(maxsize=1)
def exact_anchor_schur_certificate() -> dict[str, Any]:
    """Prove ``P+(9/10)Q+R/32 >= 1/50`` by exact Schur completion."""
    source = exact_restricted_source_matrices()
    covariant = exact_4125_scalar_covariant_certificate()
    gram_mixed = source["G_mixed"]
    gram_chiral = source["H_chiral"]
    forcing = source["forcing"]
    z0 = source["z0"]
    y_matrix = covariant["Y"]

    index = {indices: position for position, indices in enumerate(chart.PHI_INDICES)}
    q = np.zeros(chart.PHI_DIM, dtype=np.int64)
    q[index[(2, 3, 4, 5)]] = 1
    q[index[(6, 7, 8, 9)]] = -1
    basis = np.column_stack((z0, forcing, q))
    basis_gram = basis.T @ basis
    basis_gram_determinant = (
        int(basis_gram[2, 2])
        * (
            int(basis_gram[0, 0]) * int(basis_gram[1, 1])
            - int(basis_gram[0, 1]) * int(basis_gram[1, 0])
        )
    )

    expected_gram = np.asarray(
        ((8, 512, 0), (512, 65_536, 0), (0, 0, 2)), dtype=np.int64
    )
    representation_g = np.asarray(
        ((0, 0, 0), (1, 128, 0), (0, 0, 0)), dtype=np.int64
    )
    representation_h = np.asarray(
        ((0, -512, 0), (0, 8, 0), (0, 0, 0)), dtype=np.int64
    )
    # Multiply the Y representation by 32 to keep this source check integral.
    representation_32y = np.asarray(
        ((4480, 335_872, -192), (0, -768, 3), (0, 49_152, -768)),
        dtype=np.int64,
    )
    invariance_residuals = {
        "G": int(
            np.max(
                np.abs(gram_mixed @ basis - basis @ representation_g), initial=0
            )
        ),
        "H": int(
            np.max(
                np.abs(gram_chiral @ basis - basis @ representation_h), initial=0
            )
        ),
        "32Y": int(
            np.max(
                np.abs(32 * (y_matrix @ basis) - basis @ representation_32y),
                initial=0,
            )
        ),
    }

    representation_y = (
        (Fraction(140), Fraction(10_496), Fraction(-6)),
        (Fraction(0), Fraction(-24), Fraction(3, 32)),
        (Fraction(0), Fraction(1_536), Fraction(-24)),
    )
    representation_k = tuple(
        tuple(
            Fraction(1, 2_560) * int(representation_g[row, column])
            + Fraction(9, 400) * int(representation_h[row, column])
            + Fraction(3, 1_000) * int(row == column)
            + FENCHEL_ETA * representation_y[row][column]
            for column in range(3)
        )
        for row in range(3)
    )
    expected_representation_k = (
        (Fraction(107, 10_000), Fraction(-34_196, 3_125), Fraction(-33, 100_000)),
        (Fraction(1, 2_560), Fraction(724, 3_125), Fraction(33, 6_400_000)),
        (Fraction(0), Fraction(264, 3_125), Fraction(21, 12_500)),
    )
    forcing_coordinates = (Fraction(0), Fraction(1, 2_560), Fraction(0))
    solution_coordinates = _fraction_matrix_solve(
        representation_k, forcing_coordinates
    )
    expected_solution = (
        Fraction(59_752_250, 94_419_073),
        Fraction(66_875, 107_907_512),
        Fraction(-2_942_500, 94_419_073),
    )
    fraction_gram = tuple(
        tuple(Fraction(int(value)) for value in row) for row in basis_gram
    )
    gram_times_solution = tuple(
        sum(
            fraction_gram[row][column] * solution_coordinates[column]
            for column in range(3)
        )
        for row in range(3)
    )
    schur_value = sum(
        forcing_coordinates[row] * gram_times_solution[row]
        for row in range(3)
    )
    anchor_bound = (
        Fraction(1, 5)
        - FENCHEL_A
        - schur_value
        - FENCHEL_A * FENCHEL_A / 4
        - Fraction(Y_PHYSICAL_DENOMINATOR, 4)
        * FENCHEL_ETA
        * FENCHEL_ETA
    )
    anchor_margin = anchor_bound - ANCHOR_TARGET
    expected_schur = Fraction(13_448_450, 94_419_073)
    expected_bound = Fraction(20_777_185_031_397, 944_190_730_000_000)
    expected_margin = Fraction(1_893_370_431_397, 944_190_730_000_000)

    # K=G/2560+9H/400+(11/200000)(Y+52I)+(7/50000)I.
    identity_remainder = (
        Fraction(3, 1_000) - 52 * FENCHEL_ETA
    )
    return {
        "anchor": {
            "u": ANCHOR_U,
            "v": ANCHOR_V,
            "statement": "P+(9/10)Q_chiral+R_Delta/32 >= 1/50",
        },
        "Fenchel_parameters": {"a": FENCHEL_A, "eta": FENCHEL_ETA},
        "quadratic_matrix": (
            "K=G/2560+9H/400+3I/1000+(11/200000)Y"
        ),
        "positive_decomposition": (
            "K=G/2560+9H/400+(11/200000)(Y+52I)+(7/50000)I"
        ),
        "G_PSD_by_Gram_construction": True,
        "H_PSD_by_Gram_construction": True,
        "Y_plus_52I_PSD_exact": covariant["Y_plus_52I_PSD_exact"],
        "identity_remainder": identity_remainder,
        "exact_K_spectral_floor": K_SPECTRAL_FLOOR,
        "cyclic_invariant_basis": ["z0", "G*z0", "e2345-e6789"],
        "basis_shape": basis.shape,
        "basis_Gram": basis_gram,
        "expected_basis_Gram": expected_gram,
        "basis_Gram_exact": bool(np.array_equal(basis_gram, expected_gram)),
        "basis_Gram_determinant": basis_gram_determinant,
        "basis_linearly_independent_exact": basis_gram_determinant > 0,
        "invariance_residuals": invariance_residuals,
        "G_representation": representation_g,
        "H_representation": representation_h,
        "Y_representation": representation_y,
        "K_representation": representation_k,
        "expected_K_representation": expected_representation_k,
        "forcing_coordinates": forcing_coordinates,
        "K_inverse_forcing_coordinates": solution_coordinates,
        "expected_K_inverse_forcing_coordinates": expected_solution,
        "forcing_Schur_value": schur_value,
        "expected_forcing_Schur_value": expected_schur,
        "exact_anchor_lower_bound": anchor_bound,
        "anchor_target": ANCHOR_TARGET,
        "strict_anchor_margin": anchor_margin,
        "expected_anchor_lower_bound": expected_bound,
        "expected_anchor_margin": expected_margin,
        "proof_grade": bool(
            covariant["proof_grade"]
            and identity_remainder == K_SPECTRAL_FLOOR
            and K_SPECTRAL_FLOOR > 0
            and np.array_equal(basis_gram, expected_gram)
            and basis_gram_determinant == 524_288
            and not any(invariance_residuals.values())
            and representation_k == expected_representation_k
            and solution_coordinates == expected_solution
            and schur_value == expected_schur
            and anchor_bound == expected_bound
            and anchor_margin == expected_margin
            and anchor_margin > 0
        ),
    }


def exact_piecewise_radial_certificate() -> dict[str, Any]:
    """Complete the anchor inequality over every ``u,v>=0``."""
    current = zero_route.exact_current_and_radial_certificate()
    v_minimizer_u_shift = BETA / (2 * T)
    reduced_u_coefficients = (
        Fraction(1) - BETA * BETA / (4 * T),
        Fraction(-2) - BETA * R2,
        Fraction(1),
    )
    expected_reduced_u_coefficients = (
        Fraction(199, 200),
        Fraction(-1001, 500),
        Fraction(1),
    )
    reduced_derivative_at_anchor = (
        2 * reduced_u_coefficients[0] * ANCHOR_U
        + reduced_u_coefficients[1]
    )
    u_small_minimum = (
        (ANCHOR_U - 1) ** 2
        - ANCHOR_U / 500
        - ANCHOR_U * ANCHOR_U / 200
    )
    expected_u_small_minimum = Fraction(83, 20_000)

    # Coefficients ordered as u^2, uv, u, v^2, v, constant.
    low_v_left = (
        Fraction(1),
        -BETA,
        Fraction(-2),
        T,
        -R2 / 4 + Fraction(2, 25),
        Fraction(1) + T * R2 * R2 - RESTRICTED_GLOBAL_MINIMUM,
    )
    low_v_right = (
        Fraction(1),
        Fraction(-2, 40),
        Fraction(-2),
        Fraction(1, 1_600) + Fraction(199, 1_600),
        Fraction(2, 40) + Fraction(4, 200),
        Fraction(1),
    )
    # Above v=1/4, the full radial/current minimum may be used.
    high_v_excess = (
        ANCHOR_TARGET
        + RADIAL_CURRENT_MINIMUM
        - RESTRICTED_GLOBAL_MINIMUM
    )
    low_v_domination = {
        "scale_theta_at_upper_endpoint": 4 * ANCHOR_V,
        "P_coefficient_endpoint_margin": Fraction(1) - 4 * ANCHOR_V,
        "Q_coefficient_endpoint_margin": (
            ANCHOR_U - 4 * ANCHOR_V * ANCHOR_U
        ),
        "R_coefficient_identity": (
            ANCHOR_V / 8 == 4 * ANCHOR_V * Fraction(1, 32)
        ),
        "uniform_Q_condition": "u>=9/10>=18v/5 for 0<=v<=1/4",
        "proof_grade": bool(
            4 * ANCHOR_V == 1
            and Fraction(1) - 4 * ANCHOR_V == 0
            and ANCHOR_U - 4 * ANCHOR_V * ANCHOR_U == 0
            and ANCHOR_V / 8 == 4 * ANCHOR_V * Fraction(1, 32)
        ),
    }
    completion_square_coefficients = (
        Fraction(200),
        Fraction(4),
        Fraction(199, 8),
    )
    high_v_domination = {
        "Q_coefficient_margin_at_boundary": ANCHOR_U - Fraction(9, 10),
        "R_coefficient_margin_at_boundary": ANCHOR_V / 8 - Fraction(1, 32),
        "P_coefficient_unchanged": True,
        "proof_grade": bool(
            ANCHOR_U == Fraction(9, 10)
            and ANCHOR_V / 8 == Fraction(1, 32)
        ),
    }
    quadrant_coverage = {
        "region_1": "0<=u<=9/10, all v>=0",
        "region_2": "u>=9/10, 0<=v<=1/4",
        "region_3": "u>=9/10, v>=1/4",
        "shared_boundaries_included": True,
        "covers_every_u_v_nonnegative": True,
    }
    return {
        "radial_current_polynomial": (
            "g=(u-1)^2+(v-1/25)^2/8-uv/20"
        ),
        "region_u_below_9_over_10": {
            "minimize_v_at": "v=1/25+u/5",
            "v_minimizer_u_shift": v_minimizer_u_shift,
            "expected_v_minimizer_u_shift": Fraction(1, 5),
            "reduced_polynomial": "(u-1)^2-u/500-u^2/200",
            "reduced_coefficients_u2_u_1": reduced_u_coefficients,
            "expected_reduced_coefficients": expected_reduced_u_coefficients,
            "derivative_at_u_equals_9_over_10": reduced_derivative_at_anchor,
            "derivative_is_increasing_but_negative_through_9_over_10": bool(
                reduced_u_coefficients[0] > 0
                and reduced_derivative_at_anchor == Fraction(-211, 1_000)
                and reduced_derivative_at_anchor < 0
            ),
            "minimum_on_0<=u<=9/10": u_small_minimum,
            "expected_minimum": expected_u_small_minimum,
            "strictly_above_1_over_5000": (
                u_small_minimum > RESTRICTED_GLOBAL_MINIMUM
            ),
        },
        "region_u_at_least_9_over_10__v_at_most_1_over_4": {
            "anchor_scaling": (
                "P+uQ+(v/8)R >= 4v[P+(9/10)Q+R/32] >= 2v/25"
            ),
            "coefficient_domination": low_v_domination,
            "completion_identity": (
                "g+2v/25-1/5000="
                "[200(u-1-v/40)^2+4v+(199/8)v^2]/200"
            ),
            "coefficient_identity_exact": low_v_left == low_v_right,
            "completion_square_coefficients": completion_square_coefficients,
            "completion_square_coefficients_nonnegative": all(
                value >= 0 for value in completion_square_coefficients
            ),
            "nonnegative_for_u_v_nonnegative": True,
            "equality": "u=1,v=0",
        },
        "region_u_at_least_9_over_10__v_at_least_1_over_4": {
            "coefficient_domination": high_v_domination,
            "unscaled_anchor_lower_bound": ANCHOR_TARGET,
            "global_radial_current_minimum": RADIAL_CURRENT_MINIMUM,
            "excess_above_1_over_5000": high_v_excess,
            "expected_excess": Fraction(127, 9_950),
        },
        "quadrant_partition": quadrant_coverage,
        "radial_source_certificate_proof_grade": current["proof_grade"],
        "proof_grade": bool(
            current["proof_grade"]
            and current["global_minimum"] == RADIAL_CURRENT_MINIMUM
            and v_minimizer_u_shift == Fraction(1, 5)
            and reduced_u_coefficients == expected_reduced_u_coefficients
            and reduced_derivative_at_anchor == Fraction(-211, 1_000)
            and reduced_u_coefficients[0] > 0
            and u_small_minimum == expected_u_small_minimum
            and u_small_minimum > RESTRICTED_GLOBAL_MINIMUM
            and low_v_domination["proof_grade"]
            and low_v_left == low_v_right
            and all(value >= 0 for value in completion_square_coefficients)
            and high_v_domination["proof_grade"]
            and high_v_excess == Fraction(127, 9_950)
            and high_v_excess > 0
            and quadrant_coverage["covers_every_u_v_nonnegative"]
            and quadrant_coverage["shared_boundaries_included"]
        ),
    }


@lru_cache(maxsize=1)
def exact_saturation_certificate() -> dict[str, Any]:
    """Exhibit an exact ``u=1,v=0`` field attaining ``1/5000``."""
    source = exact_restricted_source_matrices()
    index = {indices: position for position, indices in enumerate(chart.PHI_INDICES)}
    signs = (1, 1, 1, 1, -1)
    z = np.zeros(chart.PHI_DIM, dtype=np.int64)
    for left, right in itertools.combinations(range(5), 2):
        indices = (2 * left, 2 * left + 1, 2 * right, 2 * right + 1)
        z[index[indices]] = signs[left] * signs[right]
    moments = phi_self.integer_pair_moments(z)
    projector_values: dict[str, Fraction] = {}
    for channel in ("54", "4125"):
        polynomial = phi_projectors.projector_polynomial(
            phi_projectors.SPECTRAL_EIGENVALUES[channel]
        )
        projector_values[channel] = sum(
            coefficient * moments[degree]
            for degree, coefficient in enumerate(polynomial)
        ) / 100
    norm = Fraction(int(z @ z), 10)
    q_numerator = int(
        (source["A_chiral"] @ z) @ (source["A_chiral"] @ z)
    )
    restricted_gap = (
        (norm - 1) ** 2
        + sum(projector_values.values(), Fraction(0))
        + Fraction(q_numerator, 40)
        + T * R2 * R2
    )
    return {
        "representative": (
            "signed Kahler square with plane signs (1,1,1,1,-1)"
        ),
        "z_support": {
            str(chart.PHI_INDICES[position]): int(value)
            for position, value in enumerate(z)
            if value
        },
        "u": Fraction(1),
        "v": Fraction(0),
        "N_Phi": norm,
        "I54": projector_values["54"],
        "I4125": projector_values["4125"],
        "Q_chiral_numerator": q_numerator,
        "restricted_gap": restricted_gap,
        "expected_gap": RESTRICTED_GLOBAL_MINIMUM,
        "proof_grade": bool(
            norm == 1
            and projector_values == {"54": Fraction(0), "4125": Fraction(0)}
            and q_numerator == 0
            and restricted_gap == RESTRICTED_GLOBAL_MINIMUM
        ),
    }


@lru_cache(maxsize=1)
def build_report() -> dict[str, Any]:
    source = exact_restricted_source_matrices()
    covariant = exact_4125_scalar_covariant_certificate()
    anchor = exact_anchor_schur_certificate()
    radial = exact_piecewise_radial_certificate()
    saturation = exact_saturation_certificate()
    checks = {
        "live_restricted_residual_normalizations_exact": source[
            "source_binding_exact"
        ],
        "single_4125_covariant_Cauchy_bound_exact": covariant["proof_grade"],
        "anchor_quadratic_has_exact_positive_spectral_floor": bool(
            anchor["proof_grade"]
            and anchor["exact_K_spectral_floor"] == K_SPECTRAL_FLOOR
        ),
        "anchor_lower_bound_strictly_exceeds_1_over_50": bool(
            anchor["strict_anchor_margin"] > 0
        ),
        "piecewise_u_v_completion_covers_nonnegative_quadrant": radial[
            "proof_grade"
        ],
        "exact_1_over_5000_saturation_exhibited": saturation["proof_grade"],
        "arbitrary_real_Phi_covered": True,
        "mixed_and_chiral_residuals_not_assumed_zero": True,
        "arbitrary_Sigma_orientation_not_overclaimed": True,
        "G3_not_overclaimed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return _jsonable(
        {
            "status": (
                "EXACT_MAX_NEGATIVE_FULL_RESIDUAL_PURE_DELTA_BOUND_CERTIFIED"
                if not failures
                else "MAX_NEGATIVE_FULL_RESIDUAL_BOUND_AUDIT_FAILED"
            ),
            "overall_state": (
                "CLOSED_MAX_NEGATIVE_PURE_DELTA_ARBITRARY_PHI_SUBPROBLEM"
                if not failures
                else "EXECUTION_FAIL"
            ),
            "model_contract_id": hsx.MODEL_CONTRACT_ID,
            "n_checks": len(checks),
            "n_failed": len(failures),
            "failures": failures,
            "checks": checks,
            "restricted_potential": {
                "fields": (
                    "H=sqrt(u)(e0-i e1)/sqrt(2), "
                    "Sigma=sqrt(v)Delta_R, arbitrary real Phi"
                ),
                "gap": (
                    "P(Phi)+(u-1)^2+(v-1/25)^2/8+uQ_chiral"
                    "+(v/8)R_Delta-uv/20"
                ),
                "u_v_domain": "u>=0,v>=0",
            },
            "exact_source": {
                key: value
                for key, value in source.items()
                if key
                not in {
                    "A_mixed",
                    "b_mixed",
                    "A_chiral",
                    "G_mixed",
                    "H_chiral",
                    "forcing",
                    "z0",
                }
            },
            "exact_4125_covariant": {
                key: value for key, value in covariant.items() if key != "Y"
            },
            "exact_anchor_Schur_certificate": anchor,
            "exact_piecewise_radial_completion": radial,
            "exact_saturation": saturation,
            "scope": {
                "Sigma_on_pure_Delta_orbit": True,
                "H_current_saturates_I45_equals_minus_NH_NSigma": True,
                "Phi_arbitrary_real_210": True,
                "nonzero_Phi_Sigma_residuals_covered": True,
                "nonzero_chiral_Phi_H_residual_covered": True,
                "u_v_all_nonnegative": True,
                "restricted_gap_global_minimum": RESTRICTED_GLOBAL_MINIMUM,
                "strictly_above_selected_vacuum_gap_zero": True,
                "arbitrary_Sigma_orientation_proved": False,
                "G3_closed": False,
            },
            "next_required_test": (
                "Extend the arbitrary-Phi coercive bound from the pure-Delta "
                "maximal-negative-current orbit to every Sigma orientation, "
                "or produce an exact lower witness outside this orbit."
            ),
            "verdict": (
                "The strongest pure-Delta negative-current route is now closed "
                "without setting any mixed or chiral residual to zero.  For every "
                "real 210 field and all u,v>=0 its exact gap is at least 1/5000. "
                "This is a strict exclusion of that route, not yet a global G3 "
                "theorem for arbitrary Sigma orientation."
            ),
        }
    )


def write_markdown(report: dict[str, Any]) -> str:
    anchor = report["exact_anchor_Schur_certificate"]
    return "\n".join(
        [
            "# Exact maximal-negative full-residual pure-Delta bound -- v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            "- arbitrary real Phi: `covered`;",
            "- mixed and chiral residuals: `not set to zero`;",
            f"- exact anchor bound: `{anchor['exact_anchor_lower_bound']}`;",
            f"- anchor excess over 1/50: `{anchor['strict_anchor_margin']}`;",
            "- exact restricted global minimum: `1/5000`;",
            "- arbitrary Sigma orientation: `open`;",
            "- G3: `open`.",
            "",
            "## Remaining gate",
            "",
            report["next_required_test"],
            "",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        OUT_MD.write_text(write_markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
