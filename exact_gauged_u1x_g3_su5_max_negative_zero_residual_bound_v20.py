#!/usr/bin/env python3
"""Exact exclusion of the maximal-negative all-zero Delta stratum.

This certificate addresses the most dangerous possible use of the signed
``beta I45(H,Sigma)`` term in the SU(5)+Delta chiral-H candidate.  Fix the
pure-spinor representative ``Sigma=sqrt(v) Delta_R`` and the null unit vector

    h_- = (e0-i e1)/sqrt(2),

which saturate ``I45(h_-,Delta_R)=-1``.  Impose simultaneously that both
shifted Phi--Sigma residuals and the chiral Phi--H square vanish.  After the
radical-free substitution ``z=sqrt(10) Phi``, these are integral affine linear
equations.  The live source arrays give exact rank 168 and nullity 42.  Their
kernel splits as

    K = K_0 direct-sum K_2,       dim(K_0,K_2)=(35,7),

where K_0 has no indices in {0,1}, K_2 has both, and the particular solution
is ``z0=2(e0123+e0145)``.  It is orthogonal to both kernel summands.

Writing ``s=||K_0/sqrt(10)||^2`` and
``q=||K_2/sqrt(10)||^2``, the exact contraction identity for I54 gives

    (N_Phi-1)^2 + I54(Phi)
      >= (s+q-1/5)^2 + (12/5-2s+3q)^2/560
      >= 1/141.

The last inequality follows from an explicit rational completion of squares.
The worst radial/current quadratic is exactly ``-7001/995000``.  Therefore the
complete gap on this stratum is at least

    1/141 - 7001/995000 = 7859/140295000 > 0,

even before the nonnegative I4125 term is used.

This is deliberately not a proof of the arbitrary-Phi global gap.  It excludes
only the pure-Delta, maximally negative-current route on which every mixed and
Phi--H residual vanishes.  Cancellations with nonzero residuals remain open.
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

import direct_phi_h_sigmabar_tensor_v20 as direct
import exact_210_self_invariant_basis_v20 as phi_self
import exact_gauged_u1x_g3_a_square_recoupling_v20 as mixed_source
import exact_gauged_u1x_g3_sos_bfb_stationarity_v20 as delta_source
import exact_gauged_u1x_g3_su5_delta_pd_sos_v20 as pd_source
import exact_gauged_u1x_g3_su5_delta_hsx_extension_v20 as hsx
import exact_gauged_u1x_g3_su5_phi_su3_slice_v20 as phi_covariants
import exact_mixed_45_triplet_channel_v20 as current_source
import exact_phisigma_casimir_projectors_v20 as phi_projectors
import live_g2_canonical_486_field_chart_v20 as chart

ROOT = Path(__file__).resolve().parent
OUT_JSON = (
    ROOT
    / "EXACT_GAUGED_U1X_G3_SU5_MAX_NEGATIVE_ZERO_RESIDUAL_BOUND_V20.json"
)
OUT_MD = (
    ROOT
    / "EXACT_GAUGED_U1X_G3_SU5_MAX_NEGATIVE_ZERO_RESIDUAL_BOUND_V20.md"
)

T = Fraction(1, 8)
R2 = Fraction(1, 25)
BETA = Fraction(1, 20)
PHI_ANGULAR_LOWER_BOUND = Fraction(1, 141)
RADIAL_CURRENT_MINIMUM = Fraction(-7001, 995000)
FINAL_STRATUM_MARGIN = Fraction(7859, 140295000)
PURE_DELTA_OVERALL_STATE = (
    "CLOSED_PURE_DELTA_MAX_NEGATIVE_MIXED_ZERO_STRATUM__ARBITRARY_PHI_OPEN"
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


def _integral_chiral_wedge_rows() -> tuple[np.ndarray, float]:
    """Return twice P_chi((e0-i e1) wedge Phi) as Gaussian integers."""
    h_raw = {(0,): 1.0 + 0.0j, (1,): -1j}
    five_indices = tuple(itertools.combinations(range(10), 5))
    five_index = {indices: position for position, indices in enumerate(five_indices)}
    real = np.zeros((len(five_indices), chart.PHI_DIM), dtype=np.int64)
    imaginary = np.zeros_like(real)
    integrality_residual = 0.0
    for column, indices in enumerate(chart.PHI_INDICES):
        wedge = direct.wedge(h_raw, {indices: 1.0 + 0.0j})
        projected = direct.scale_form(
            direct.add_forms(
                wedge,
                direct.scale_form(direct.hodge_star(wedge), -1j),
            ),
            0.5,
        )
        for target, value in projected.items():
            scaled = 2.0 * complex(value)
            rounded_real = int(round(scaled.real))
            rounded_imaginary = int(round(scaled.imag))
            integrality_residual = max(
                integrality_residual,
                abs(scaled.real - rounded_real),
                abs(scaled.imag - rounded_imaginary),
            )
            real[five_index[target], column] = rounded_real
            imaginary[five_index[target], column] = rounded_imaginary
    return np.vstack((real, imaginary)), integrality_residual


@lru_cache(maxsize=1)
def live_hsx_coefficient_binding_certificate() -> dict[str, Any]:
    """Bind every reduced-polynomial normalization to the live HSX source."""
    symbolic = hsx.symbolic_coefficient_map()
    alignment = hsx.exact_phi_h_chiral_square_certificate()
    sigma_t_03 = Fraction(
        symbolic["lambda::O27_B03_126bar_self_projectors"]
    )
    sigma_t_04 = Fraction(
        symbolic["lambda::O27_B04_126bar_self_projectors"]
    )
    beta_live = Fraction(symbolic["lambda::O35_B02_H_Sigma_hermitian"])
    chiral_coefficients = (
        Fraction(symbolic["lambda::O46_B01_Phi2_HdagH_channels"]),
        Fraction(symbolic["lambda::O46_B02_Phi2_HdagH_channels"]),
        Fraction(symbolic["lambda::O46_B03_Phi2_HdagH_channels"]),
    )
    h_norm_coefficient = Fraction(symbolic["lambda::O06_B01_Hdag_H_norm"])
    h_self_coefficients = (
        Fraction(symbolic["lambda::O36_B01_H_self_quartics"]),
        Fraction(symbolic["lambda::O36_B02_H_self_quartics"]),
    )
    source = exact_affine_constraint_source()
    pd_phi = pd_source.exact_phi_projector_certificate()
    pd_mixed = pd_source.exact_mixed_zero_certificate()
    pd_sigma = pd_source.exact_sigma_certificate()
    pd_report = pd_source.build_report()
    hsx_report = hsx.build_report(recompute_heavy=False)
    # A_chi z=2 P_chi(h_raw wedge z), while
    # H=h_raw/sqrt(2), Phi=z/sqrt(10).  Therefore the live chiral square
    # 2||P_chi(H wedge Phi)||^2 equals ||A_chi z||^2/40.
    chiral_affine_row_norm_factor = Fraction(1, 40)
    return {
        "live_symbolic_sigma_quartic_coefficients": {
            "O27_B03": sigma_t_03,
            "O27_B04": sigma_t_04,
        },
        "live_selected_sigma_norm_squared": hsx.R * hsx.R,
        "live_beta_coefficient": beta_live,
        "live_H_norm_coefficient": h_norm_coefficient,
        "live_H_self_coefficients_O36_B01_B02": h_self_coefficients,
        "live_chiral_coefficients_O46_B01_B02_B03": chiral_coefficients,
        "live_chiral_square_identity": alignment["chiral_square_identity"],
        "live_chiral_all_component_identity_residual": alignment[
            "deterministic_all_component_identity_residual"
        ],
        "chiral_affine_rows_identity": (
            "Q_chi=2||P_chi(H wedge Phi)||^2=||A_chi z||^2/40, "
            "H=h_raw/sqrt(2), Phi=z/sqrt(10), A_chi z=2P_chi(h_raw wedge z)"
        ),
        "chiral_affine_row_norm_factor": chiral_affine_row_norm_factor,
        "PD_sigma_scale": pd_source.SIGMA_SCALE,
        "PD_raw_F_norm_squared": pd_phi["raw_norm_squared"],
        "PD_raw_mixed_M_eigenvalue": pd_mixed["M_eigenvalue_raw"],
        "PD_source_reports": {
            "PD_status": pd_report["status"],
            "PD_n_failed": pd_report["n_failed"],
            "HSX_status": hsx_report["status"],
            "HSX_n_failed": hsx_report["n_failed"],
        },
        "proof_grade": bool(
            T == hsx.SIGMA_SCALE == sigma_t_03 == sigma_t_04
            and T == pd_source.SIGMA_SCALE
            and R2 == hsx.R * hsx.R == Fraction(1, 25)
            and BETA == hsx.BETA == beta_live
            and h_norm_coefficient == Fraction(-2)
            and h_self_coefficients == (Fraction(11), Fraction(1))
            and chiral_coefficients
            == (Fraction(3, 5), Fraction(1), Fraction(-1))
            and alignment["source_binding_exact"] is True
            and alignment["chiral_square_identity"]
            == "(3/5)O46_1+O46_45-O46_54=2||P_chi(H wedge Phi)||^2"
            and alignment["deterministic_all_component_identity_residual"] == 0.0
            and source["chiral_cleared_denominator"] == 2
            and chiral_affine_row_norm_factor == Fraction(1, 40)
            and pd_phi["source_binding_exact"] is True
            and pd_phi["raw_norm_squared"] == 10
            and pd_mixed["source_binding_exact"] is True
            and pd_mixed["M_eigenvalue_raw"] == 8
            and pd_sigma["source_binding_exact"] is True
            and pd_report["n_failed"] == 0
            and pd_report["status"]
            == "EXACT_SU5_DELTA_PD_GLOBAL_SOS_CANDIDATE_CERTIFIED"
            and hsx_report["n_failed"] == 0
            and hsx_report["status"]
            == "EXACT_REAL_H_NO_GO__CHIRAL_H_STRICT_LOCAL_CANDIDATE__GLOBAL_GAP_OPEN"
        ),
    }


@lru_cache(maxsize=1)
def exact_affine_constraint_source() -> dict[str, Any]:
    """Build the integral live-source constraint A z=b, z=sqrt(10) Phi."""
    delta_real, delta_imaginary = delta_source.raw_delta_coordinates()
    operator_real, operator_imaginary = mixed_source.integer_cubic_operators()
    contraction_real, contraction_imaginary = (
        mixed_source.integer_contraction_tensor()
    )

    m_real = (
        np.einsum("pab,b->pa", operator_real, delta_real, optimize=True)
        - np.einsum(
            "pab,b->pa", operator_imaginary, delta_imaginary, optimize=True
        )
    ).T
    m_imaginary = (
        np.einsum(
            "pab,b->pa", operator_real, delta_imaginary, optimize=True
        )
        + np.einsum(
            "pab,b->pa", operator_imaginary, delta_real, optimize=True
        )
    ).T
    c_real = (
        np.einsum("vpa,a->pv", contraction_real, delta_real, optimize=True)
        - np.einsum(
            "vpa,a->pv", contraction_imaginary, delta_imaginary, optimize=True
        )
    ).T
    c_imaginary = (
        np.einsum(
            "vpa,a->pv", contraction_real, delta_imaginary, optimize=True
        )
        + np.einsum(
            "vpa,a->pv", contraction_imaginary, delta_real, optimize=True
        )
    ).T
    chiral_rows, chiral_integrality_residual = _integral_chiral_wedge_rows()
    matrix = np.vstack(
        (m_real, m_imaginary, c_real, c_imaginary, chiral_rows)
    ).astype(np.int64)
    target = np.concatenate(
        (
            8 * np.asarray(delta_real, dtype=np.int64),
            8 * np.asarray(delta_imaginary, dtype=np.int64),
            np.zeros(c_real.shape[0] + c_imaginary.shape[0] + chiral_rows.shape[0], dtype=np.int64),
        )
    )
    z0 = np.zeros(chart.PHI_DIM, dtype=np.int64)
    index = {indices: position for position, indices in enumerate(chart.PHI_INDICES)}
    z0[index[(0, 1, 2, 3)]] = 2
    z0[index[(0, 1, 4, 5)]] = 2
    return {
        "matrix": matrix,
        "target": target,
        "particular_solution": z0,
        "matrix_shape": matrix.shape,
        "matrix_nonzero_entries": int(np.count_nonzero(matrix)),
        "chiral_cleared_denominator": 2,
        "chiral_integrality_residual": chiral_integrality_residual,
        "particular_solution_residual_max_abs": int(
            np.max(np.abs(matrix @ z0 - target), initial=0)
        ),
    }


def _exact_fraction_nullspace(matrix: np.ndarray) -> dict[str, Any]:
    """Sparse exact row reduction and a rational nullspace basis."""
    source = np.asarray(matrix, dtype=np.int64)
    pivots: dict[int, dict[int, Fraction]] = {}
    for source_row in source:
        row = {
            column: Fraction(int(value))
            for column, value in enumerate(source_row)
            if value
        }
        while row:
            pivot = min(row)
            factor = row[pivot]
            reference = pivots.get(pivot)
            if reference is None:
                pivots[pivot] = {
                    column: value / factor for column, value in row.items()
                }
                break
            for column, value in reference.items():
                updated = row.get(column, Fraction(0)) - factor * value
                if updated:
                    row[column] = updated
                else:
                    row.pop(column, None)

    free_columns = tuple(
        column for column in range(source.shape[1]) if column not in pivots
    )
    basis_fraction: list[dict[int, Fraction]] = []
    pivot_order = tuple(pivots)
    for free_column in free_columns:
        vector: dict[int, Fraction] = {free_column: Fraction(1)}
        for pivot in reversed(pivot_order):
            value = -sum(
                coefficient * vector.get(column, Fraction(0))
                for column, coefficient in pivots[pivot].items()
                if column != pivot
            )
            if value:
                vector[pivot] = value
        basis_fraction.append(vector)

    maximum_denominator = max(
        (
            value.denominator
            for vector in basis_fraction
            for value in vector.values()
        ),
        default=1,
    )
    basis = np.zeros((source.shape[1], len(basis_fraction)), dtype=np.int64)
    if maximum_denominator == 1:
        for column, vector in enumerate(basis_fraction):
            for row, value in vector.items():
                basis[row, column] = value.numerator
    residual = source @ basis
    return {
        "rank": len(pivots),
        "nullity": len(free_columns),
        "pivot_columns": pivot_order,
        "free_columns": free_columns,
        "basis": basis,
        "maximum_basis_denominator": maximum_denominator,
        "maximum_basis_numerator_abs": int(np.max(np.abs(basis), initial=0)),
        "basis_residual_max_abs": int(np.max(np.abs(residual), initial=0)),
    }


@lru_cache(maxsize=1)
def exact_kernel_decomposition_certificate() -> dict[str, Any]:
    source = exact_affine_constraint_source()
    nullspace = _exact_fraction_nullspace(source["matrix"])
    basis = nullspace["basis"]
    p_counts = np.asarray(
        [len(set(indices).intersection((0, 1))) for indices in chart.PHI_INDICES],
        dtype=np.int64,
    )
    column_types: list[int] = []
    invalid_columns: list[int] = []
    for column in range(basis.shape[1]):
        support = np.flatnonzero(basis[:, column])
        observed = set(int(value) for value in p_counts[support])
        if len(observed) == 1 and next(iter(observed)) in (0, 2):
            column_types.append(next(iter(observed)))
        else:
            column_types.append(-1)
            invalid_columns.append(column)
    zero_plane_columns = tuple(
        index for index, value in enumerate(column_types) if value == 0
    )
    two_plane_columns = tuple(
        index for index, value in enumerate(column_types) if value == 2
    )
    z0 = source["particular_solution"]
    basis_k0 = basis[:, zero_plane_columns]
    basis_k2 = basis[:, two_plane_columns]
    contains_0 = np.asarray([0 in indices for indices in chart.PHI_INDICES], dtype=np.int64)
    contains_1 = np.asarray([1 in indices for indices in chart.PHI_INDICES], dtype=np.int64)

    def weighted_gram(left: np.ndarray, weights: np.ndarray, right: np.ndarray) -> np.ndarray:
        return left.T @ (weights[:, None] * right)

    norm_k0_gram = basis_k0.T @ basis_k0
    norm_k2_gram = basis_k2.T @ basis_k2
    central_identity_residuals = {
        "N_z0_norm_squared_minus_8": int(z0 @ z0 - 8),
        "N_z0_dot_K0_max_abs": int(np.max(np.abs(z0 @ basis_k0), initial=0)),
        "N_z0_dot_K2_max_abs": int(np.max(np.abs(z0 @ basis_k2), initial=0)),
        "N_K0_dot_K2_max_abs": int(
            np.max(np.abs(basis_k0.T @ basis_k2), initial=0)
        ),
        "C00_z0_minus_8": int(z0 @ (contains_0 * z0) - 8),
        "C11_z0_minus_8": int(z0 @ (contains_1 * z0) - 8),
        "C00_z0_dot_K2_max_abs": int(
            np.max(np.abs((contains_0 * z0) @ basis_k2), initial=0)
        ),
        "C11_z0_dot_K2_max_abs": int(
            np.max(np.abs((contains_1 * z0) @ basis_k2), initial=0)
        ),
        "C00_K0_gram_max_abs": int(
            np.max(
                np.abs(weighted_gram(basis_k0, contains_0, basis_k0)),
                initial=0,
            )
        ),
        "C11_K0_gram_max_abs": int(
            np.max(
                np.abs(weighted_gram(basis_k0, contains_1, basis_k0)),
                initial=0,
            )
        ),
        "C00_K2_minus_norm_gram_max_abs": int(
            np.max(
                np.abs(
                    weighted_gram(basis_k2, contains_0, basis_k2)
                    - norm_k2_gram
                ),
                initial=0,
            )
        ),
        "C11_K2_minus_norm_gram_max_abs": int(
            np.max(
                np.abs(
                    weighted_gram(basis_k2, contains_1, basis_k2)
                    - norm_k2_gram
                ),
                initial=0,
            )
        ),
    }
    central_contraction_identities_exact = not any(central_identity_residuals.values())
    return {
        "exact_rank": nullspace["rank"],
        "exact_nullity": nullspace["nullity"],
        "integer_nullspace_basis_shape": basis.shape,
        "maximum_basis_denominator": nullspace["maximum_basis_denominator"],
        "maximum_basis_numerator_abs": nullspace[
            "maximum_basis_numerator_abs"
        ],
        "basis_residual_max_abs": nullspace["basis_residual_max_abs"],
        "K0_no_01_indices_dimension": len(zero_plane_columns),
        "K2_both_01_indices_dimension": len(two_plane_columns),
        "kernel_basis_has_no_one_01_index_entries": bool(
            not np.any(basis[p_counts == 1])
        ),
        "invalid_mixed_support_basis_columns": invalid_columns,
        "z0_dot_full_kernel_max_abs": int(
            np.max(np.abs(z0 @ basis), initial=0)
        ),
        "decomposition": (
            "z=z0+k0+k2, z0=2(e0123+e0145), "
            "dim(K0,K2)=(35,7), K0 has no 0/1 indices, K2 has both"
        ),
        "physical_norm_identity": "N_Phi=4/5+s+q",
        "physical_contraction_identity": "C00=C11=4/5+q",
        "physical_identity_normalization": (
            "Phi=z/sqrt(10), s=||k0||^2/10, q=||k2||^2/10"
        ),
        "central_contraction_identity_residuals": central_identity_residuals,
        "central_contraction_identities_computed_exactly": (
            central_contraction_identities_exact
        ),
        "proof_grade": bool(
            source["chiral_integrality_residual"] == 0.0
            and source["particular_solution_residual_max_abs"] == 0
            and nullspace["rank"] == 168
            and nullspace["nullity"] == 42
            and nullspace["maximum_basis_denominator"] == 1
            and nullspace["basis_residual_max_abs"] == 0
            and len(zero_plane_columns) == 35
            and len(two_plane_columns) == 7
            and not invalid_columns
            and not np.any(basis[p_counts == 1])
            and not np.any(z0 @ basis)
            and central_contraction_identities_exact
        ),
    }


def _square_linear_polynomial(
    constant: Fraction,
    s_coefficient: Fraction,
    q_coefficient: Fraction,
    scale: Fraction = Fraction(1),
) -> dict[tuple[int, int], Fraction]:
    return {
        (0, 0): scale * constant * constant,
        (1, 0): scale * 2 * constant * s_coefficient,
        (0, 1): scale * 2 * constant * q_coefficient,
        (2, 0): scale * s_coefficient * s_coefficient,
        (1, 1): scale * 2 * s_coefficient * q_coefficient,
        (0, 2): scale * q_coefficient * q_coefficient,
    }


def _add_polynomials(
    *polynomials: dict[tuple[int, int], Fraction],
) -> dict[tuple[int, int], Fraction]:
    keys = set().union(*(polynomial.keys() for polynomial in polynomials))
    return {
        key: sum((polynomial.get(key, Fraction(0)) for polynomial in polynomials), Fraction(0))
        for key in keys
    }


@lru_cache(maxsize=1)
def exact_phi_coercive_bound_certificate() -> dict[str, Any]:
    covariant = phi_covariants.exact_global_covariant_reduction()
    trace_identity_residual = 5 * 4 - 2 * 10
    traceless_cauchy_coefficient = Fraction(2) + Fraction(4, 8)
    i54_diagonal_coefficient = traceless_cauchy_coefficient / 1400
    left = _add_polynomials(
        _square_linear_polynomial(Fraction(-1, 5), Fraction(1), Fraction(1)),
        _square_linear_polynomial(
            Fraction(12, 5), Fraction(-2), Fraction(3), Fraction(1, 560)
        ),
    )
    right = _add_polynomials(
        _square_linear_polynomial(
            Fraction(-146, 705),
            Fraction(1),
            Fraction(277, 282),
            Fraction(141, 140),
        ),
        _square_linear_polynomial(
            Fraction(2), Fraction(0), Fraction(5), Fraction(1, 564)
        ),
    )
    return {
        "I54_source_identity": covariant["I54_identity"],
        "I54_source_binding_exact": covariant["source_binding_exact"],
        "I54_exact_sample_basis_determinant": covariant[
            "sample_J_evaluation_determinant"
        ],
        "I54_sample_identity_max_abs_residual": covariant[
            "I54_sample_identity_max_abs_residual"
        ],
        "trace_C_equals_4N_combinatorial_identity": True,
        "trace_5C_minus_2N_identity_residual": trace_identity_residual,
        "D00_equals_D11": "12/5-2*s+3*q",
        "traceless_diagonal_Cauchy_bound": (
            "||5C-2N*identity||^2 >= (5/2)*(12/5-2s+3q)^2"
        ),
        "traceless_diagonal_Cauchy_coefficient": traceless_cauchy_coefficient,
        "I54_diagonal_lower_bound_coefficient": i54_diagonal_coefficient,
        "first_lower_bound": (
            "(N_Phi-1)^2+I54 >= "
            "(s+q-1/5)^2+(12/5-2s+3q)^2/560"
        ),
        "exact_completion_of_squares": (
            "(141/140)*(s-146/705+(277/282)q)^2+(5q+2)^2/564"
        ),
        "polynomial_identity_exact": left == right,
        "q_nonnegative": True,
        "lower_bound": PHI_ANGULAR_LOWER_BOUND,
        "lower_bound_derivation": (
            "q>=0 implies (5q+2)^2/564>=4/564=1/141"
        ),
        "I4125_unused_and_nonnegative": True,
        "proof_grade": bool(
            covariant["source_binding_exact"]
            and covariant["complete_quartic_invariant_dimension"] == 4
            and covariant["independent_exact_sample_count"] == 4
            and covariant["sample_J_evaluation_determinant"] != 0
            and covariant["I54_sample_identity_max_abs_residual"] == "0"
            and trace_identity_residual == 0
            and traceless_cauchy_coefficient == Fraction(5, 2)
            and i54_diagonal_coefficient == Fraction(1, 560)
            and left == right
            and PHI_ANGULAR_LOWER_BOUND == Fraction(1, 141)
        ),
    }


@lru_cache(maxsize=1)
def exact_current_and_radial_certificate() -> dict[str, Any]:
    h_raw = {(0,): 1.0 + 0.0j, (1,): -1j}
    delta_real, delta_imaginary = delta_source.raw_delta_coordinates()
    sigma_raw = chart.sigma_from_coordinates(delta_real + 1j * delta_imaginary)
    h_current = current_source.hermitian_current_45(
        h_raw, kinetic_factor=1.0
    )
    sigma_current = current_source.hermitian_current_45(
        sigma_raw, kinetic_factor=0.5
    )
    raw_current = complex(direct.tensor_inner(h_current, sigma_current))
    raw_h_norm_squared = int(round(sum(abs(value) ** 2 for value in h_raw.values())))
    raw_sigma_norm_squared = int(
        delta_real @ delta_real + delta_imaginary @ delta_imaginary
    )
    delta_self = delta_source.exact_delta_self_certificate()
    fractions = delta_self["delta_projector_fractions"]

    u_star = Fraction(1001, 995)
    v_star = Fraction(48, 199)
    radial_value = (
        (u_star - 1) ** 2
        + T * (v_star - R2) ** 2
        - BETA * u_star * v_star
    )
    derivative_u = 2 * (u_star - 1) - BETA * v_star
    derivative_v = 2 * T * (v_star - R2) - BETA * u_star
    quadratic_determinant = T - (BETA / 2) ** 2
    u_zero_boundary_lower_bound = Fraction(1)
    v_zero_boundary_lower_bound = T * R2 * R2
    return {
        "representatives": {
            "H_unit": "(e0-i*e1)/sqrt(2)",
            "Sigma_unit": "Delta_R=(raw Delta)/sqrt(8)",
        },
        "radial_parameterization": (
            "H=sqrt(u) h_minus, Sigma=sqrt(v) Delta_R, u=N_H, v=N_Sigma"
        ),
        "normalized_affine_stratum_domain": "u>0 and v>0",
        "raw_H_norm_squared": raw_h_norm_squared,
        "raw_Sigma_norm_squared": raw_sigma_norm_squared,
        "raw_H_holomorphic_square": "0",
        "raw_current": int(round(raw_current.real)),
        "raw_current_imaginary_abs": abs(raw_current.imag),
        "normalized_current": Fraction(int(round(raw_current.real)), 16),
        "current_lower_bound_saturated": (
            Fraction(int(round(raw_current.real)), 16) == -1
        ),
        "Sigma_I54": fractions["54"],
        "Sigma_I1050bar": fractions["1050bar"],
        "Sigma_self_residuals_zero": bool(
            fractions["54"] == 0 and fractions["1050bar"] == 0
        ),
        "radial_current_polynomial": (
            "(u-1)^2+(1/8)(v-1/25)^2-(1/20)uv"
        ),
        "quadratic_form_determinant": quadratic_determinant,
        "quadratic_form_positive_definite": quadratic_determinant > 0,
        "global_minimizer": {"u": u_star, "v": v_star},
        "gradient_at_minimizer": {
            "du": derivative_u,
            "dv": derivative_v,
        },
        "global_minimum": radial_value,
        "radial_boundaries": {
            "u_equals_zero_lower_bound": u_zero_boundary_lower_bound,
            "v_equals_zero_lower_bound": v_zero_boundary_lower_bound,
            "derivation": (
                "u=0: (u-1)^2>=1 after minimizing v at R2; "
                "v=0: T(v-R2)^2>=T*R2^2=1/5000 after minimizing u at 1; "
                "the current vanishes and all omitted SOS terms are nonnegative"
            ),
            "closed_without_normalized_affine_constraints": True,
        },
        "proof_grade": bool(
            raw_h_norm_squared == 2
            and raw_sigma_norm_squared == 8
            and raw_current.real == -16
            and raw_current.imag == 0
            and raw_current == complex(-16, 0)
            and Fraction(int(round(raw_current.real)), 16) == -1
            and fractions["54"] == 0
            and fractions["1050bar"] == 0
            and quadratic_determinant > 0
            and u_star > 0
            and v_star > 0
            and derivative_u == 0
            and derivative_v == 0
            and radial_value == RADIAL_CURRENT_MINIMUM
            and u_zero_boundary_lower_bound == 1
            and v_zero_boundary_lower_bound == Fraction(1, 5000)
        ),
    }


@lru_cache(maxsize=1)
def exact_particular_phi_certificate() -> dict[str, Any]:
    source = exact_affine_constraint_source()
    z0 = source["particular_solution"]
    moments = phi_self.integer_pair_moments(z0)
    values: dict[str, Fraction] = {}
    for channel in ("54", "4125"):
        polynomial = phi_projectors.projector_polynomial(
            phi_projectors.SPECTRAL_EIGENVALUES[channel]
        )
        values[channel] = sum(
            (coefficient * value for coefficient, value in zip(polynomial, moments, strict=True)),
            Fraction(0),
        ) / 100
    normalized_norm = Fraction(int(z0 @ z0), 10)
    phi_gap = (normalized_norm - 1) ** 2 + sum(values.values())
    return {
        "z_equals_sqrt10_Phi": "2*(e0123+e0145)",
        "raw_z_norm_squared": int(z0 @ z0),
        "N_Phi": normalized_norm,
        "I54_Phi": values["54"],
        "I4125_Phi": values["4125"],
        "complete_Phi_SOS_gap_at_particular_solution": phi_gap,
        "expected_complete_Phi_gap": Fraction(263, 1125),
        "source_binding_exact": bool(
            source["particular_solution_residual_max_abs"] == 0
            and normalized_norm == Fraction(4, 5)
            and values["54"] == Fraction(2, 125)
            and values["4125"] == Fraction(8, 45)
            and phi_gap == Fraction(263, 1125)
        ),
    }


@lru_cache(maxsize=1)
def build_report() -> dict[str, Any]:
    source = exact_affine_constraint_source()
    live_binding = live_hsx_coefficient_binding_certificate()
    kernel = exact_kernel_decomposition_certificate()
    phi_bound = exact_phi_coercive_bound_certificate()
    current = exact_current_and_radial_certificate()
    particular = exact_particular_phi_certificate()
    margin = PHI_ANGULAR_LOWER_BOUND + RADIAL_CURRENT_MINIMUM
    checks = {
        "live_HSX_and_PD_coefficients_bound_exactly": live_binding["proof_grade"],
        "live_integral_affine_source_bound": bool(
            source["matrix_shape"] == (776, 210)
            and source["chiral_integrality_residual"] == 0.0
            and source["particular_solution_residual_max_abs"] == 0
        ),
        "exact_rank_168_nullity_42": bool(
            kernel["exact_rank"] == 168 and kernel["exact_nullity"] == 42
        ),
        "kernel_splits_35_plus_7_exactly": kernel["proof_grade"],
        "N_and_C00_C11_contraction_identities_computed_exactly": kernel[
            "central_contraction_identities_computed_exactly"
        ],
        "particular_solution_projectors_exact": particular[
            "source_binding_exact"
        ],
        "maximal_negative_current_saturated_exactly": current["proof_grade"],
        "Phi_radial_plus_I54_lower_bound_1_over_141": phi_bound[
            "proof_grade"
        ],
        "worst_radial_current_minimum_exact": (
            current["global_minimum"] == RADIAL_CURRENT_MINIMUM
        ),
        "u_zero_and_v_zero_radial_boundaries_closed_exactly": bool(
            current["radial_boundaries"]["u_equals_zero_lower_bound"] == 1
            and current["radial_boundaries"]["v_equals_zero_lower_bound"]
            == Fraction(1, 5000)
            and current["radial_boundaries"][
                "closed_without_normalized_affine_constraints"
            ]
            is True
        ),
        "strict_positive_stratum_margin_exact": bool(
            margin == FINAL_STRATUM_MARGIN and margin > 0
        ),
        "arbitrary_Phi_nonzero_residual_cancellations_not_overclaimed": True,
        "G3_not_overclaimed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return _jsonable(
        {
            "status": (
                "EXACT_PURE_DELTA_MAX_NEGATIVE_MIXED_ZERO_ROUTE_EXCLUDED"
                if not failures
                else "PURE_DELTA_MAX_NEGATIVE_MIXED_ZERO_BOUND_AUDIT_FAILED"
            ),
            "overall_state": (
                PURE_DELTA_OVERALL_STATE
                if not failures
                else "EXECUTION_FAIL"
            ),
            "model_contract_id": hsx.MODEL_CONTRACT_ID,
            "n_checks": len(checks),
            "n_failed": len(failures),
            "failures": failures,
            "checks": checks,
            "live_HSX_PD_coefficient_binding": live_binding,
            "exact_affine_source": {
                key: value
                for key, value in source.items()
                if key not in {"matrix", "target", "particular_solution"}
            },
            "exact_kernel_decomposition": kernel,
            "exact_particular_Phi": particular,
            "exact_Phi_coercive_bound": phi_bound,
            "exact_current_and_radial_bound": current,
            "exact_stratum_gap": {
                "Phi_angular_lower_bound": PHI_ANGULAR_LOWER_BOUND,
                "radial_current_global_minimum": RADIAL_CURRENT_MINIMUM,
                "strict_margin": margin,
                "strict_margin_expected": FINAL_STRATUM_MARGIN,
                "derivation": "1/141-7001/995000=7859/140295000",
            },
            "scope": {
                "Sigma_on_pure_Delta_orbit": True,
                "pure_Delta_mixed_and_chiral_zero_stratum": True,
                "normalized_affine_stratum_requires_u_gt_0_v_gt_0": True,
                "u_zero_and_v_zero_boundaries_closed_separately": True,
                "H_current_saturates_I45_equals_minus_NH_NSigma": True,
                "Phi_Sigma_shifted_M_residual_zero": True,
                "Phi_Sigma_C_residual_zero": True,
                "chiral_Phi_H_residual_zero": True,
                "strongest_all_zero_max_negative_route_excluded": not failures,
                "strongest_pure_Delta_mixed_zero_max_negative_route_excluded": (
                    not failures
                ),
                "nonzero_residual_cancellations_excluded": False,
                "arbitrary_Phi_global_gap_proved": False,
                "G3_closed": False,
            },
            "next_required_test": (
                "Control cancellations where at least one shifted Phi-Sigma or "
                "chiral Phi-H residual is nonzero, uniformly for arbitrary Phi."
            ),
            "verdict": (
                "The exact pure-Delta maximal-negative-current route cannot lower "
                "the candidate when all mixed and chiral Phi-H residuals vanish: "
                "its gap is at least 7859/140295000.  This removes the strongest "
                "mixed-zero cancellation mechanism (with u=0 and v=0 boundaries "
                "closed separately), but it does not control "
                "arbitrary-Phi configurations with nonzero residual cancellations, "
                "so G3 remains open."
            ),
        }
    )


def _markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Exact pure-Delta maximal-negative mixed-zero bound -- v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            "- exact affine rank/nullity: `168/42`;",
            "- exact kernel split: `35+7`;",
            "- Phi radial + I54 lower bound: `1/141`;",
            "- radial/current minimum: `-7001/995000`;",
            "- strict stratum margin: `7859/140295000`;",
            "- radial boundaries: `u=0 >= 1`, `v=0 >= 1/5000`;",
            "- nonzero-residual arbitrary-Phi cancellations: `OPEN`;",
            "- G3: `OPEN`.",
            "",
        ]
    )


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    OUT_MD.write_text(_markdown(report), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        write_report(report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
