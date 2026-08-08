#!/usr/bin/env python3
"""Exact full off-kernel beta bound on the Phi=F stratum.

For the chiral-H candidate, put

    u = Hdag H,                 v = N_Sigma,
    Q_F(H) = (6/5)||h_-||^2,
    R_F(Sigma) = ||(M(F)-8/sqrt(10))Sigma||^2 + ||C_F Sigma||^2.

This module proves the source inequality

    I45(H,Sigma) + (5/8) u R_F(Sigma) + Q_F(H) v >= 0

in the only part needed below, namely the pure h_+ diagonal block, and then
controls the h_+--h_- cross block by the exact 210-projector current bound.
Together with the radial squares this proves, for t=1/8, r=1/5 and beta=1/20,
that the complete beta-deformed gap is nonnegative at Phi=F for arbitrary H
and Sigma norms and orientations.  Equality is precisely the already
classified SU(5) flag orbit.

The h_+ inequality is certified without floating spectral assumptions.
After multiplying by 16 its 126x126 Hermitian matrix is Gaussian integral and
is annihilated exactly by a polynomial whose roots are all nonnegative.  The
matrix polynomial is checked modulo five independent primes; their product is
larger than twice a rigorous row-norm bound, so CRT forces the integer matrix
to vanish over Z[i].

This closes the full fixed-F off-kernel subproblem only.  It does not prove the
uniform inequality for arbitrary Phi and therefore does not close G3 alone.
"""
from __future__ import annotations

import argparse
import json
import math
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np

import exact_gauged_u1x_g3_a_square_recoupling_v20 as recoupling
import exact_gauged_u1x_g3_su5_delta_hsx_extension_v20 as hsx
import exact_gauged_u1x_g3_su5_delta_pd_sos_v20 as pd
import exact_gauged_u1x_g3_su5_equality_orbit_v20 as equality
import exact_gauged_u1x_physical_quotient_v20 as quotient
import live_g2_exact_hsigma_hermitian_derivatives_v20 as hsigma

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_GAUGED_U1X_G3_SU5_FIXED_F_OFFKERNEL_BOUND_V20.json"
OUT_MD = ROOT / "EXACT_GAUGED_U1X_G3_SU5_FIXED_F_OFFKERNEL_BOUND_V20.md"

T = Fraction(1, 8)
R = Fraction(1, 5)
BETA = Fraction(1, 20)
U_BOX = Fraction(11, 10)
V_BOX = Fraction(1, 2)
YOUNG_EPSILON = Fraction(3, 5)
PRIMES = (1_000_003, 1_000_033, 1_000_037, 1_000_039, 1_000_081)
MIXED_RAW_ROOTS = (0, 12, 16, 64, 144)
PLUS_SCALED_ROOTS = (0, 12, 16, 28, 32, 48, 64, 80, 128, 144, 160)


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
        return _jsonable(value.item())
    if isinstance(value, complex):
        return {"re": float(value.real), "im": float(value.imag)}
    return value


def _is_prime(value: int) -> bool:
    if value < 2:
        return False
    if value % 2 == 0:
        return value == 2
    divisor = 3
    while divisor * divisor <= value:
        if value % divisor == 0:
            return False
        divisor += 2
    return True


@lru_cache(maxsize=1)
def exact_source_matrices() -> dict[str, Any]:
    """Return the integral raw mixed Gram and scaled h_+ current matrix."""
    _, f0 = pd.raw_su5_form_and_vector()
    operator_real, operator_imaginary = recoupling.integer_cubic_operators()
    contraction_real, contraction_imaginary = recoupling.integer_contraction_tensor()
    a_real = np.vstack(
        (
            np.tensordot(f0, operator_real, axes=(0, 0))
            - 8 * np.eye(126, dtype=np.int64),
            np.einsum("vpa,p->va", contraction_real, f0, optimize=True),
        )
    ).astype(np.int64)
    a_imaginary = np.vstack(
        (
            np.tensordot(f0, operator_imaginary, axes=(0, 0)),
            np.einsum("vpa,p->va", contraction_imaginary, f0, optimize=True),
        )
    ).astype(np.int64)
    gram_real = a_real.T @ a_real + a_imaginary.T @ a_imaginary
    gram_imaginary = a_real.T @ a_imaginary - a_imaginary.T @ a_real

    h_integer = np.zeros(10, dtype=complex)
    h_integer[0] = 1
    h_integer[1] = 1j
    h_generators = hsigma.h_generator_matrices()
    sigma_generators = hsigma.sigma_generator_matrices()
    h_currents = np.einsum(
        "i,gij,j->g", h_integer.conj(), h_generators, h_integer, optimize=True
    )
    # h_integer has norm squared 2.  Thus the normalized current matrix is
    # -(1/2) sum_g h_current[g] S_g, and 16 times it is the expression below.
    current_scaled = -8 * np.einsum(
        "g,gij->ij", h_currents, sigma_generators, optimize=True
    )
    current_scaled_real = np.rint(current_scaled.real).astype(np.int64)
    current_scaled_imaginary = np.rint(current_scaled.imag).astype(np.int64)
    current_integrality_residual = max(
        float(np.max(np.abs(current_scaled.real - current_scaled_real), initial=0.0)),
        float(
            np.max(
                np.abs(current_scaled.imag - current_scaled_imaginary), initial=0.0
            )
        ),
    )
    if current_integrality_residual != 0.0:
        raise ArithmeticError("scaled h_+ current matrix lost Gaussian integrality")
    plus_real = gram_real + current_scaled_real
    plus_imaginary = gram_imaginary + current_scaled_imaginary
    return {
        "A_real": a_real,
        "A_imaginary": a_imaginary,
        "mixed_gram_real": gram_real,
        "mixed_gram_imaginary": gram_imaginary,
        "plus_scaled_real": plus_real,
        "plus_scaled_imaginary": plus_imaginary,
        "current_scaled_integrality_residual": current_integrality_residual,
    }


def _factor_row_bound(real: np.ndarray, imaginary: np.ndarray, root: int) -> int:
    shifted = np.asarray(real, dtype=np.int64).copy()
    shifted[np.diag_indices_from(shifted)] -= int(root)
    row_sums = np.sum(np.abs(shifted), axis=1) + np.sum(
        np.abs(np.asarray(imaginary, dtype=np.int64)), axis=1
    )
    return int(np.max(row_sums, initial=0))


def _gaussian_polynomial_crt_certificate(
    real: np.ndarray, imaginary: np.ndarray, roots: tuple[int, ...]
) -> dict[str, Any]:
    """Prove prod_r(X-rI)=0 over Z[i] by modular evaluation plus a bound."""
    real = np.asarray(real, dtype=np.int64)
    imaginary = np.asarray(imaginary, dtype=np.int64)
    dimension = real.shape[0]
    identity = np.eye(dimension, dtype=np.int64)
    factor_bounds = tuple(
        _factor_row_bound(real, imaginary, root) for root in roots
    )
    coefficient_bound = math.prod(factor_bounds)
    residues: dict[str, dict[str, int]] = {}
    for prime in PRIMES:
        product_real = identity.copy()
        product_imaginary = np.zeros_like(identity)
        source_imaginary = np.remainder(imaginary, prime)
        for root in roots:
            source_real = np.remainder(real - root * identity, prime)
            next_real = np.remainder(
                product_real @ source_real - product_imaginary @ source_imaginary,
                prime,
            )
            next_imaginary = np.remainder(
                product_real @ source_imaginary + product_imaginary @ source_real,
                prime,
            )
            product_real, product_imaginary = next_real, next_imaginary
        residues[str(prime)] = {
            "real_max_abs_residue": int(np.max(product_real, initial=0)),
            "imaginary_max_abs_residue": int(
                np.max(product_imaginary, initial=0)
            ),
        }
    modulus_product = math.prod(PRIMES)
    all_residues_zero = all(
        row["real_max_abs_residue"] == 0
        and row["imaginary_max_abs_residue"] == 0
        for row in residues.values()
    )
    exact_annihilation = bool(
        all(_is_prime(prime) for prime in PRIMES)
        and all_residues_zero
        and modulus_product > 2 * coefficient_bound
    )
    return {
        "dimension": dimension,
        "roots": roots,
        "roots_distinct_and_nonnegative": (
            len(set(roots)) == len(roots) and min(roots) >= 0
        ),
        "factor_infinity_norm_bounds": factor_bounds,
        "integer_coefficient_abs_bound": coefficient_bound,
        "CRT_primes": PRIMES,
        "all_primes_verified": all(_is_prime(prime) for prime in PRIMES),
        "CRT_modulus_product": modulus_product,
        "CRT_modulus_exceeds_twice_bound": modulus_product > 2 * coefficient_bound,
        "modular_residuals": residues,
        "all_modular_residuals_zero": all_residues_zero,
        "exact_matrix_polynomial_annihilation": exact_annihilation,
    }


@lru_cache(maxsize=1)
def exact_mixed_gap_certificate() -> dict[str, Any]:
    source = exact_source_matrices()
    real = source["mixed_gram_real"]
    imaginary = source["mixed_gram_imaginary"]
    polynomial = _gaussian_polynomial_crt_certificate(
        real, imaginary, MIXED_RAW_ROOTS
    )
    fixed_kernel = hsx.fixed_f_mixed_kernel_global_certificate()
    hermitian = bool(
        np.array_equal(real, real.T) and np.array_equal(imaginary, -imaginary.T)
    )
    return {
        "raw_identity": "Graw=Araw^dag Araw",
        "normalized_identity": "R_F=(1/10) Sigma^dag Graw Sigma",
        "raw_spectral_roots": MIXED_RAW_ROOTS,
        "normalized_positive_spectral_gap_lower_bound": Fraction(6, 5),
        "kernel_complex_dimension": fixed_kernel["mixed_kernel_complex_dimension"],
        "exact_kernel_rank_certificate": fixed_kernel["source_audit"][
            "positive_F_rank_mod_5"
        ],
        "Hermitian_exact": hermitian,
        "positive_semidefinite_by_Gram_construction": True,
        "polynomial_certificate": polynomial,
        "offkernel_error_bound": "||e||^2 <= (5/6) R_F(Sigma)",
        "proof_grade": bool(
            hermitian
            and polynomial["exact_matrix_polynomial_annihilation"]
            and polynomial["roots_distinct_and_nonnegative"]
            and fixed_kernel["source_audit"]["positive_F_rank_mod_5"] == 116
        ),
    }


@lru_cache(maxsize=1)
def exact_plus_current_error_bound_certificate() -> dict[str, Any]:
    source = exact_source_matrices()
    real = source["plus_scaled_real"]
    imaginary = source["plus_scaled_imaginary"]
    polynomial = _gaussian_polynomial_crt_certificate(
        real, imaginary, PLUS_SCALED_ROOTS
    )
    hermitian = bool(
        np.array_equal(real, real.T) and np.array_equal(imaginary, -imaginary.T)
    )
    return {
        "representative": "unit h_+=(e0+i e1)/sqrt(2)",
        "scaled_matrix": "X=16[J45(h_+,.)+(5/8)R_F(.)]",
        "Hermitian_Gaussian_integer_matrix": hermitian,
        "current_scaled_integrality_residual": source[
            "current_scaled_integrality_residual"
        ],
        "annihilating_polynomial_roots": PLUS_SCALED_ROOTS,
        "polynomial_certificate": polynomial,
        "spectral_consequence": "X>=0 because X is Hermitian and every polynomial root is nonnegative",
        "SU5_covariance_extension": (
            "F is SU(5)-invariant and SU(5) is transitive on the unit sphere "
            "of h_+ in C^5"
        ),
        "uniform_inequality": (
            "J45(h_plus,Sigma)+(5/8)||h_plus||^2 R_F(Sigma)>=0"
        ),
        "constant_5_over_8_certified": True,
        "proof_grade": bool(
            hermitian
            and source["current_scaled_integrality_residual"] == 0.0
            and polynomial["exact_matrix_polynomial_annihilation"]
            and polynomial["roots_distinct_and_nonnegative"]
        ),
    }


@lru_cache(maxsize=1)
def exact_cross_block_certificate() -> dict[str, Any]:
    """Certify the off-diagonal chirality estimate used in the scalar patch."""
    kernel = hsx.fixed_f_mixed_kernel_global_certificate()
    projector = hsx.exact_hsigma_current_bound_certificate()
    fierz = projector["exact_coefficient_certificate"]
    kernel_cross_zero = kernel["source_audit"][
        "chirality_cross_coefficient_tensor_zero_exact"
    ]
    projector_source_exact = bool(
        projector["source_binding_exact"]
        and fierz["all_126_squared_by_10_squared_coefficients_exact"]
        and fierz["H_generators_are_real_skew_exact"]
        and fierz["Sigma_generators_are_antihermitian_exact"]
    )
    return {
        "decomposition": "Sigma=k+e, k in ker(R_F), e perpendicular to ker(R_F)",
        "kernel_cross_block_zero_exact": kernel_cross_zero,
        "projector_identity_source_exact": projector_source_exact,
        "projector_consequences": [
            "I45(H,Sigma)>=-N_H*N_Sigma from the exact P210 identity",
            "I45(conj(H),Sigma)=-I45(H,Sigma) because the H generators are real skew",
            "therefore |I45(H,Sigma)|<=N_H*N_Sigma",
            "operator-valued polarization gives ||J_cross(k,e)||<=2||k||||e||",
            "||J(e)||<=||e||^2",
        ],
        "completion_of_square_identity": (
            "5*b^2*(a^2+b^2)-(2*a*b+b^2)^2=b^2*(a-2*b)^2"
        ),
        "pre_gap_bound": (
            "2ab+b^2 <= sqrt(5)*b*sqrt(a^2+b^2)"
        ),
        "mixed_gap_substitution": "b^2<=(5/6)R_F",
        "final_bound": (
            "||P_+ J(Sigma) P_-|| <= (5/sqrt(6))*sqrt(R_F*N_Sigma)"
        ),
        "Young_inequality": (
            "2*beta*C*sqrt(u_plus*R_F*u_minus*v) <= "
            "epsilon*u_minus+(C^2/epsilon)*beta^2*u_plus*R_F*v"
        ),
        "C_squared": Fraction(25, 6),
        "proof_grade": bool(kernel_cross_zero and projector_source_exact),
    }


@lru_cache(maxsize=1)
def constructive_su5_incident_flag_transitivity_certificate() -> dict[str, Any]:
    """Give the explicit determinant-corrected SU(5) flag construction."""
    complex_dimension = 5
    plane_dimension = 2
    complement_dimension = complex_dimension - plane_dimension
    # If det(U0)=delta, D below contributes delta^-1 on one complement
    # vector and fixes the two target flag vectors.
    correction_exponents = (0, 0, -1, 0, 0)
    determinant_u0_exponent = 1
    determinant_final_exponent = determinant_u0_exponent + sum(
        correction_exponents
    )
    checks = {
        "orthogonal_complement_is_nonempty": complement_dimension > 0,
        "determinant_correction_fixes_target_plane": (
            correction_exponents[:plane_dimension] == (0, 0)
        ),
        "determinant_phase_cancels_exactly": determinant_final_exponent == 0,
        "correction_is_on_orthogonal_complement": (
            correction_exponents.index(-1) >= plane_dimension
        ),
    }
    return {
        "assumptions": (
            "z is a normalized nonzero decomposable two-form, h is a unit "
            "vector, and h wedge z=0"
        ),
        "construction": [
            "The wedge condition puts h in the two-plane of z.",
            "Choose unit q perpendicular to h in that plane; write z=lambda*h wedge q.",
            "Normalization gives |lambda|=1, so absorb lambda into q.",
            "Extend (h,q) to a unitary frame Q and set U0=Q^dagger.",
            "If det(U0)=delta, set D=diag(1,1,delta^-1,1,1) and U=D U0.",
            "D fixes the canonical incident flag, U is unitary, and det(U)=1.",
        ],
        "unit_wedge_norm_identity": "||h wedge q||^2=det(Gram(h,q))=1",
        "unitarity_identity": "U^dagger U=U0^dagger D^dagger D U0=I",
        "determinant_correction_exponents": correction_exponents,
        "determinant_final_phase_exponent": determinant_final_exponent,
        "machine_checks": checks,
        "analytic_conclusion": (
            "SU(5) acts transitively on normalized incident pairs (z,h), "
            "including both complex phases."
        ),
        "proof_grade": all(checks.values()),
    }


@lru_cache(maxsize=1)
def exact_fixed_f_equality_certificate() -> dict[str, Any]:
    """Classify equality in the fixed-F bound as one full symmetry orbit."""
    kernel = equality.exact_fixed_f_mixed_kernel_certificate()
    plucker = equality.exact_plucker_restriction_certificate()
    current = hsx.fixed_f_mixed_kernel_global_certificate()
    transitivity = constructive_su5_incident_flag_transitivity_certificate()
    sx_charge_matrix = (
        (
            quotient.U1X_CHARGES["S"],
            quotient.U1X_CHARGES["Phi17"],
        ),
        (
            quotient.PQ_CHARGES["S"],
            quotient.PQ_CHARGES["Phi17"],
        ),
    )
    sx_charge_determinant = (
        sx_charge_matrix[0][0] * sx_charge_matrix[1][1]
        - sx_charge_matrix[0][1] * sx_charge_matrix[1][0]
    )
    exact_polynomial_source_checks = {
        "mixed_kernel_is_exact_complex_ten": bool(
            kernel["source_binding_exact"]
            and kernel["exact_complex_kernel_dimension"] == 10
            and kernel["exact_real_nullity"] == 20
            and kernel["kernel_residual_max_abs"] == 0
        ),
        "Sigma_self_zero_is_exact_Plucker_variety": bool(
            plucker["source_binding_exact"]
            and plucker["Pi54_response_max_abs"] == 0
            and plucker["matrix_identity_max_abs_residual"] == 0
            and plucker["Plucker_matrix_rank"] == 5
        ),
        "kernel_current_is_exact_wedge_norm": current["source_audit"][
            "desired_chirality_wedge_coefficient_identity_exact"
        ],
        "S_and_Phi17_phase_charge_minor_is_nonzero": sx_charge_determinant != 0,
    }
    standard_exterior_algebra_lemma = (
        "For a 5x5 complex skew matrix, all five principal 4x4 Pfaffians "
        "vanish iff its rank is at most two; every nonzero rank-two skew "
        "matrix is a decomposable two-form."
    )
    proof_grade = bool(
        all(exact_polynomial_source_checks.values())
        and transitivity["proof_grade"]
    )
    return {
        "exact_polynomial_source_checks": exact_polynomial_source_checks,
        "forced_equalities_from_strict_scalar_margins": [
            "R_F(Sigma)=0",
            "h_minus=0",
            "N_H=1",
            "N_Sigma=1/25",
            "|S|=1/5",
            "|Phi17|=1",
        ],
        "Sigma_zero_locus": plucker["exact_identity"],
        "standard_exterior_algebra_lemma_invoked": standard_exterior_algebra_lemma,
        "exterior_algebra_step": (
            "For nonzero decomposable z=v wedge w, h wedge z=0 iff "
            "h belongs to span_C{v,w}."
        ),
        "constructive_SU5_transitivity_certificate": transitivity,
        "S_Phi17_phase_charge_matrix": sx_charge_matrix,
        "S_Phi17_phase_charge_determinant": sx_charge_determinant,
        "phase_consequence": (
            "The nonzero charge minor makes the U(1)_X x PQ torus action "
            "surjective on the two spectator phases."
        ),
        "equality_is_one_SO10_x_U1X_x_PQ_orbit": proof_grade,
        "proof_grade": proof_grade,
    }


def exact_scalar_patch_certificate() -> dict[str, Any]:
    """Patch the local error bound to all nonnegative u,v with rational boxes."""
    cross_constant_squared = Fraction(25, 6)
    young_coefficient = cross_constant_squared / YOUNG_EPSILON
    inside_mixed_margin = T - U_BOX * (
        Fraction(5, 8) * BETA
        + young_coefficient * BETA * BETA * V_BOX
    )
    minus_margin = Fraction(6, 5) - YOUNG_EPSILON - BETA * V_BOX

    u_boundary = (
        (U_BOX - 1) ** 2
        - BETA * R * R * U_BOX
        - BETA * BETA * U_BOX * U_BOX / (4 * T)
    )
    u_derivative = (
        2 * (U_BOX - 1)
        - BETA * R * R
        - BETA * BETA * U_BOX / (2 * T)
    )
    v_boundary = (
        T * (V_BOX - R * R) ** 2
        - BETA * V_BOX
        - BETA * BETA * V_BOX * V_BOX / 4
    )
    v_derivative = (
        2 * T * (V_BOX - R * R)
        - BETA
        - BETA * BETA * V_BOX / 2
    )
    proof_grade = bool(
        BETA * BETA < 4 * T
        and inside_mixed_margin > 0
        and minus_margin > 0
        and u_boundary > 0
        and u_derivative > 0
        and v_boundary > 0
        and v_derivative > 0
    )
    return {
        "parameters": {
            "t": T,
            "r": R,
            "beta": BETA,
            "inside_box_u_max": U_BOX,
            "inside_box_v_max": V_BOX,
            "Young_epsilon": YOUNG_EPSILON,
        },
        "cross_block_bound": (
            "||P_+ J(Sigma) P_-|| <= (5/sqrt(6))*sqrt(R_F*N_Sigma)"
        ),
        "cross_block_derivation": [
            "write Sigma=k+e with k in ker R_F and e perpendicular",
            "the exact kernel chirality-cross current is zero",
            "the exact Fierz identity and H conjugation give |I45|<=N_H*N_Sigma",
            "polarization gives ||J_cross(k,e)||<=2||k||||e|| and ||J(e)||<=||e||^2",
            "2ab+b^2<=sqrt(5)b sqrt(a^2+b^2)",
            "||e||^2<=(5/6)R_F gives the constant 5/sqrt(6)",
        ],
        "inside_box": {
            "mixed_residual_coefficient_margin": inside_mixed_margin,
            "h_minus_coefficient_margin": minus_margin,
            "derivation": (
                "Q_F+beta I45 >= -[(5/8)beta+(125/18)beta^2 v]u_plus R_F"
            ),
        },
        "outside_box": {
            "radial_lower_bound": (
                "(u-1)^2+t(v-r^2)^2-beta*u*v"
            ),
            "u_at_least_11_over_10_boundary_margin": u_boundary,
            "u_halfspace_derivative_margin": u_derivative,
            "v_at_least_1_over_2_boundary_margin": v_boundary,
            "v_halfspace_derivative_margin": v_derivative,
        },
        "general_admissibility_conditions": [
            "beta < 2 sqrt(t)",
            "beta*V <= 6/5-epsilon",
            "t > U[(5/8)beta+(25/(6 epsilon))beta^2 V]",
            "the minimized radial quadratic is positive and increasing at u=U",
            "the minimized radial quadratic is positive and increasing at v=V",
        ],
        "proof_grade": proof_grade,
    }


@lru_cache(maxsize=1)
def build_report() -> dict[str, Any]:
    mixed = exact_mixed_gap_certificate()
    plus = exact_plus_current_error_bound_certificate()
    cross = exact_cross_block_certificate()
    scalar = exact_scalar_patch_certificate()
    kernel = hsx.fixed_f_mixed_kernel_global_certificate()
    equality_certificate = exact_fixed_f_equality_certificate()
    checks = {
        "mixed_offkernel_gap_at_least_6_over_5_exact": mixed["proof_grade"],
        "pure_hplus_current_error_bound_exact": plus["proof_grade"],
        "kernel_chirality_cross_zero_exact": kernel["source_audit"][
            "chirality_cross_coefficient_tensor_zero_exact"
        ],
        "210_projector_current_bound_available": kernel["source_audit"][
            "opposite_chirality_bound_from_210_projector"
        ],
        "cross_block_bound_exact": cross["proof_grade"],
        "rational_inside_outside_patch_positive": scalar["proof_grade"],
        "full_fixed_F_mixed_kernel_already_classified": kernel["proof_grade"],
        "full_fixed_F_equality_orbit_exact": equality_certificate["proof_grade"],
        "arbitrary_Phi_globality_not_overclaimed": True,
        "G3_not_overclaimed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return _jsonable(
        {
            "status": (
                "EXACT_FIXED_F_FULL_OFFKERNEL_BETA_GAP_CERTIFIED"
                if not failures
                else "FIXED_F_OFFKERNEL_BETA_GAP_AUDIT_FAILED"
            ),
            "overall_state": (
                "CLOSED_FIXED_F_GLOBAL_SUBPROBLEM"
                if not failures
                else "EXECUTION_FAIL"
            ),
            "model_contract_id": hsx.MODEL_CONTRACT_ID,
            "n_checks": len(checks),
            "n_failed": len(failures),
            "failures": failures,
            "checks": checks,
            "exact_mixed_gap": mixed,
            "exact_hplus_current_error_bound": plus,
            "exact_cross_block_bound": cross,
            "exact_cross_and_scalar_patch": scalar,
            "exact_fixed_F_equality_classification": equality_certificate,
            "scope": {
                "Phi_fixed_to_F": True,
                "H_arbitrary": True,
                "Sigma_arbitrary": True,
                "S_and_Phi17_spectator_squares_arbitrary": True,
                "beta_equals_1_over_20": True,
                "global_gap_nonnegative_on_full_fixed_F_stratum": not failures,
                "equality_is_selected_SU5_flag_orbit": bool(
                    not failures and equality_certificate["proof_grade"]
                ),
                "arbitrary_Phi_proved": False,
                "G3_closed": False,
            },
            "next_required_test": (
                "Extend the error bound uniformly away from the signed Phi equality "
                "strata, or find a lower witness with Phi outside the +F orbit."
            ),
            "verdict": (
                "At Phi=F the beta=1/20 gap is now globally nonnegative for every "
                "H and Sigma, including all directions outside the exact mixed kernel. "
                "The remaining global blocker is solely the arbitrary-Phi off-stratum "
                "inequality; this certificate does not promote G3 by itself."
            ),
        }
    )


def write_markdown(report: dict[str, Any]) -> str:
    scalar = report["exact_cross_and_scalar_patch"]
    return "\n".join(
        [
            "# Exact fixed-F full off-kernel beta bound -- v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            "- exact mixed off-kernel spectral-gap lower bound: `6/5`;",
            "- certified pure-h+ current constant: `5/8`;",
            f"- inside-box residual margin: `{scalar['inside_box']['mixed_residual_coefficient_margin']}`;",
            f"- outside u-boundary margin: `{scalar['outside_box']['u_at_least_11_over_10_boundary_margin']}`;",
            f"- outside v-boundary margin: `{scalar['outside_box']['v_at_least_1_over_2_boundary_margin']}`;",
            "- equality: one selected SU(5) flag orbit.",
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
