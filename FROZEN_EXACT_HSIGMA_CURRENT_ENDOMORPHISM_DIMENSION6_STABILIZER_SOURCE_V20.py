#!/usr/bin/env python3
"""Exact certificate for the positive dimension-six H--126bar stabilizer.

In the kinetic-orthonormal live conventions let

    j_H^g = H^dagger T_10^g H,
    K_H   = sum_g conjugate(j_H^g) T_126bar^g,
    R(H,Sigma) = K_H Sigma,
    O_6(H,Sigma) = ||R(H,Sigma)||^2.

The generators are anti-Hermitian, the currents are purely imaginary, and
``K_H`` is Hermitian.  Consequently ``O_6`` is an SO(10)-invariant,
globally nonnegative dimension-six operator.  It is also neutral under the
declared abelian symmetries.

At the selected representative

    H_chi = (e_6+i e_7)/sqrt(2),       Sigma = r Delta_R,

``K_H`` has spectrum ``(-1)^35, 0^56, (+1)^35`` and annihilates Delta_R.
The real Jacobian of ``R`` on the six old beta=0 colour quotient flats has
Gram ``r^2 I_6`` in unit complex-field directions.  After the canonical
486-real chart convention ``H=(x+i y)/sqrt(2)``, the Hessian of
``gamma O_6`` is ``gamma r^2 I_6`` on those unit real directions.  Thus
``r=1/5, gamma=1/20`` gives the exact lift ``1/500``.

On the complete +F Pluecker equality locus, write the desired-chirality
fields as ``h in C^5`` and ``z in Lambda^2 C^5``.  For decomposable z the
certificate proves

    ||K_H Sigma(z)||^2 = ||h||^2 ||h wedge z||^2.

Hence, once the scalar equations force ``||h||=1``, the new operator cuts the
beta=0 orientation continuum down exactly to the selected incident-flag
condition (the condition selected by the former beta=1/20 current quartic).
This module certifies the EFT operator and its local lift.  It does not by
itself recompile the full 486 Hessian, prove the remaining signed-Phi orbit
theorem, or close G3/G4.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np


HERE = Path(__file__).resolve().parent
SOURCE_DIR = (
    HERE
    if (HERE / "live_g2_exact_hsigma_hermitian_derivatives_v20.py").is_file()
    else HERE.parent / "so10-axion-v20-reaudit"
)
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

import exact_gauged_u1x_g3_sos_bfb_stationarity_v20 as delta_source
import exact_gauged_u1x_g3_su5_delta_hsx_extension_v20 as hsx_source
import exact_gauged_u1x_g3_su5_fixed_f_offkernel_bound_v20 as equality_source
import live_g2_canonical_486_field_chart_v20 as chart
import live_g2_exact_hsigma_hermitian_derivatives_v20 as current_source


STATUS = "EXACT_HSIGMA_CURRENT_ENDOMORPHISM_DIMENSION6_STABILIZER__G3_OPEN"
EXPECTED_CORE_SHA256 = "598d916da16e746c8be30e979a13a27a47d1600e2dd4bee7b9cf9fc398ec9da1"
EXPECTED_DEPENDENCY_SHA256 = {
    "live_g2_exact_hsigma_hermitian_derivatives_v20.py": (
        "bd15f4c15585e49e7884558992c3ca14a1e9777282e747f98f31fb2d8e32b1af"
    ),
    "live_g2_canonical_486_field_chart_v20.py": (
        "85ae9470f3aa25c28fc03c083b6c1e150106a276e51044a590060d290ba7945e"
    ),
    "exact_gauged_u1x_g3_sos_bfb_stationarity_v20.py": (
        "0b0fa1a937a1ff09856fbd735faf50be4fb59d2684289ff266eb6931c437cd90"
    ),
    "exact_gauged_u1x_g3_su5_delta_hsx_extension_v20.py": (
        "c88a76c4bcc1f32ddce9eef15c87fe0a6794f7e0d7643ae774972a9b4b67c71f"
    ),
    "exact_gauged_u1x_g3_su5_fixed_f_offkernel_bound_v20.py": (
        "77b976c0a4fc9984448a6092d75fd5c8168fb42c012609371bd75aef4e5ab117"
    ),
}

R_SELECTED = Q(1, 5)
GAMMA_SELECTED = Q(1, 20)

# Frozen +F mixed-kernel embedding from
# hsx_source.fixed_f_mixed_kernel_global_certificate().  Its columns have
# Gram 8 I_10 and correspond anti-linearly to the two-form basis below.
KERNEL_ROWS = (
    ((7, 1j), (8, -1), (11, -1), (12, -1j), (22, -1), (23, -1j), (26, -1j), (27, 1)),
    ((9, 1j), (10, -1), (13, -1), (14, -1j), (24, -1), (25, -1j), (28, -1j), (29, 1)),
    ((16, 1j), (17, -1), (18, -1), (19, -1j), (31, -1), (32, -1j), (33, -1j), (34, 1)),
    ((41, 1j), (42, -1), (43, -1), (44, -1j), (47, -1), (48, -1j), (49, -1j), (50, 1)),
    ((75, -1), (80, -1), (81, -1j), (86, -1j), (95, -1j), (100, -1j), (101, 1), (106, 1)),
    ((73, -1), (74, -1j), (87, -1), (88, -1j), (93, -1j), (94, 1), (107, -1j), (108, 1)),
    ((71, -1), (72, -1j), (89, -1), (90, -1j), (91, -1j), (92, 1), (109, -1j), (110, 1)),
    ((66, -1), (67, -1j), (68, -1j), (69, 1), (112, -1), (113, -1j), (114, -1j), (115, 1)),
    ((59, -1), (60, -1j), (63, -1j), (64, 1), (117, -1), (118, -1j), (121, -1j), (122, 1)),
    ((57, -1), (58, -1j), (61, -1j), (62, 1), (119, -1), (120, -1j), (123, -1j), (124, 1)),
)
TWO_FORM_PAIRS = (
    (0, 4),
    (0, 3),
    (0, 2),
    (0, 1),
    (3, 4),
    (2, 3),
    (2, 4),
    (1, 2),
    (1, 3),
    (1, 4),
)
TWO_FORM_PHASES = (1, -1, 1, -1, 1j, 1j, -1j, 1j, -1j, 1j)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _jsonable(value: Any) -> Any:
    if isinstance(value, Q):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    if isinstance(value, np.generic):
        return value.item()
    return value


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(_jsonable(value), sort_keys=True, separators=(",", ":")).encode(
            "ascii"
        )
    ).hexdigest()


def exact_dependency_guard() -> dict[str, str]:
    observed = {
        name: _sha256(SOURCE_DIR / name) for name in EXPECTED_DEPENDENCY_SHA256
    }
    if observed != EXPECTED_DEPENDENCY_SHA256:
        raise ArithmeticError(f"dependency raw hash drift: {observed}")
    fixed_kernel = hsx_source.fixed_f_mixed_kernel_global_certificate()
    fixed_equality = equality_source.exact_fixed_f_equality_certificate()
    if not fixed_kernel["proof_grade"]:
        raise ArithmeticError("the exact +F mixed-kernel source is no longer proof grade")
    if not fixed_equality["proof_grade"]:
        raise ArithmeticError("the exact +F Pluecker equality source is no longer proof grade")
    return observed


def _gaussian_integer_array(values: np.ndarray, label: str) -> np.ndarray:
    source = np.asarray(values, dtype=complex)
    rounded = np.rint(source.real).astype(np.int64) + 1j * np.rint(
        source.imag
    ).astype(np.int64)
    if not np.array_equal(source, rounded):
        raise ArithmeticError(f"{label} stopped being an exact Gaussian-integer array")
    return rounded


def _kernel_embedding() -> np.ndarray:
    embedding = np.zeros((chart.SIGMA_COMPLEX_DIM, 10), dtype=complex)
    for column, row in enumerate(KERNEL_ROWS):
        for index, value in row:
            embedding[index, column] = value
    return embedding


def _plus_embedding() -> np.ndarray:
    embedding = np.zeros((chart.H_COMPLEX_DIM, 5), dtype=complex)
    for index in range(5):
        embedding[2 * index, index] = 1
        embedding[2 * index + 1, index] = 1j
    return embedding


def exact_integer_source_certificate() -> dict[str, Any]:
    h_generators = _gaussian_integer_array(
        current_source.h_generator_matrices(), "10 generators"
    )
    sigma_generators = _gaussian_integer_array(
        current_source.sigma_generator_matrices(), "126bar generators"
    )
    if h_generators.shape != (45, 10, 10):
        raise ArithmeticError("the vector-generator census drifted")
    if sigma_generators.shape != (45, 126, 126):
        raise ArithmeticError("the 126bar-generator census drifted")
    h_antihermitian = np.array_equal(
        h_generators.conj().transpose(0, 2, 1), -h_generators
    )
    sigma_antihermitian = np.array_equal(
        sigma_generators.conj().transpose(0, 2, 1), -sigma_generators
    )
    h_real_skew = bool(
        h_antihermitian
        and not np.any(h_generators.imag)
        and np.array_equal(h_generators.transpose(0, 2, 1), -h_generators)
    )

    kernel = _kernel_embedding()
    plus = _plus_embedding()
    delta_real, delta_imaginary = delta_source.raw_delta_coordinates()
    delta_raw = _gaussian_integer_array(
        delta_real + 1j * delta_imaginary, "raw Delta_R"
    )
    kernel_gram = kernel.conj().T @ kernel
    plus_gram = plus.conj().T @ plus
    delta_is_kernel_pair_34 = np.array_equal(delta_raw, -kernel[:, 4])
    if not (
        h_real_skew
        and sigma_antihermitian
        and np.array_equal(kernel_gram, 8 * np.eye(10))
        and np.array_equal(plus_gram, 2 * np.eye(5))
        and delta_is_kernel_pair_34
        and int(np.vdot(delta_raw, delta_raw).real) == 8
    ):
        raise ArithmeticError("an exact source normalization identity failed")
    return {
        "generator_census": {"so10": 45, "H_complex": 10, "Sigma_complex": 126},
        "H_generators_real_skew_exact": h_real_skew,
        "Sigma_generators_antihermitian_exact": sigma_antihermitian,
        "plus_embedding_gram": "2 I5",
        "mixed_kernel_embedding_gram": "8 I10",
        "normalized_fields": {
            "H_plus(h)": "E_plus h/sqrt(2), so N_H=||h||^2",
            "Sigma(z)": (
                "E_kernel conjugate(z/phase)/sqrt(8), so N_Sigma=||z||^2"
            ),
            "Delta_R": "Delta_raw/sqrt(8)=-E_kernel[:,pair(3,4)]/sqrt(8)",
        },
        "Delta_raw_norm_squared": 8,
        "Delta_is_pair_34_kernel_vector_exact": delta_is_kernel_pair_34,
    }


def _selected_h_raw() -> np.ndarray:
    output = np.zeros(10, dtype=complex)
    output[6] = 1
    output[7] = 1j
    return output


def _selected_k_matrix() -> tuple[np.ndarray, np.ndarray]:
    h_generators = _gaussian_integer_array(
        current_source.h_generator_matrices(), "10 generators"
    )
    sigma_generators = _gaussian_integer_array(
        current_source.sigma_generator_matrices(), "126bar generators"
    )
    h_raw = _selected_h_raw()
    current_numerator = np.einsum(
        "i,gij,j->g", h_raw.conj(), h_generators, h_raw, optimize=True
    )
    # H_chi=h_raw/sqrt(2), so j=current_numerator/2.  Every numerator
    # entry is divisible by two in Z[i].
    current = current_numerator / 2
    _gaussian_integer_array(current, "selected normalized H current")
    k_matrix = np.einsum(
        "g,gij->ij", current.conj(), sigma_generators, optimize=True
    )
    return _gaussian_integer_array(k_matrix, "selected K_H"), current_numerator


def exact_selected_operator_certificate() -> dict[str, Any]:
    exact_integer_source_certificate()
    k_matrix, current_numerator = _selected_k_matrix()
    nonzero_currents = tuple(
        (int(index), complex(current_numerator[index]))
        for index in np.flatnonzero(current_numerator)
    )
    expected_generator_index = current_source.PAIRS.index((6, 7))
    if nonzero_currents != ((expected_generator_index, 2j),):
        raise ArithmeticError(f"selected current support drifted: {nonzero_currents}")
    identity = np.eye(126, dtype=complex)
    k_squared = k_matrix @ k_matrix
    minimal_polynomial_zero = np.array_equal(k_matrix @ k_squared, k_matrix)
    hermitian = np.array_equal(k_matrix.conj().T, k_matrix)
    trace_k = complex(np.trace(k_matrix))
    trace_k_squared = complex(np.trace(k_squared))
    if not (
        hermitian
        and minimal_polynomial_zero
        and trace_k == 0
        and trace_k_squared == 70
        and np.array_equal(identity @ k_matrix, k_matrix)
    ):
        raise ArithmeticError("the selected exact K_H spectral identities failed")
    # K^3=K gives eigenvalues in {-1,0,+1}.  Hermiticity diagonalizes K.
    # tr(K)=0 and tr(K^2)=70 then force 35,56,35 multiplicities.
    delta_real, delta_imaginary = delta_source.raw_delta_coordinates()
    delta_raw = delta_real + 1j * delta_imaginary
    delta_residual = k_matrix @ delta_raw
    delta_zero = not np.any(delta_residual)
    if not delta_zero:
        raise ArithmeticError("K_H stopped annihilating Delta_R")
    return {
        "definition": {
            "current": "j_H^g=H^dag T_10^g H",
            "endomorphism": "K_H=sum_g conjugate(j_H^g) T_126bar^g",
            "covariant_residual": "R(H,Sigma)=K_H Sigma",
            "operator": "O6=||R||^2",
        },
        "selected_H": "H_chi=(e6+i e7)/sqrt(2)",
        "selected_normalized_current": "j_H^(6,7)=i; every other component is zero",
        "K_H_Hermitian_exact": hermitian,
        "minimal_polynomial_identity": "K_H(K_H-I)(K_H+I)=0",
        "minimal_polynomial_zero_exact": minimal_polynomial_zero,
        "trace_K": 0,
        "trace_K_squared": 70,
        "exact_spectrum": {"-1": 35, "0": 56, "+1": 35},
        "K_H_Delta_R_zero_exact": delta_zero,
        "selected_O6": 0,
        "selected_value_and_gradient_zero": True,
    }


def exact_six_flat_jacobian_certificate() -> dict[str, Any]:
    exact_integer_source_certificate()
    h_generators = _gaussian_integer_array(
        current_source.h_generator_matrices(), "10 generators"
    )
    sigma_generators = _gaussian_integer_array(
        current_source.sigma_generator_matrices(), "126bar generators"
    )
    delta_real, delta_imaginary = delta_source.raw_delta_coordinates()
    delta_raw = delta_real + 1j * delta_imaginary
    h_raw = _selected_h_raw()
    images_raw: list[np.ndarray] = []
    derivative_supports: list[int] = []
    for colour_plane in range(3):
        u_raw = np.zeros(10, dtype=complex)
        u_raw[2 * colour_plane] = 1
        u_raw[2 * colour_plane + 1] = 1j
        for phase in (1, 1j):
            direction_raw = phase * u_raw
            derivative_numerator = np.einsum(
                "i,gij,j->g",
                direction_raw.conj(),
                h_generators,
                h_raw,
                optimize=True,
            ) + np.einsum(
                "i,gij,j->g",
                h_raw.conj(),
                h_generators,
                direction_raw,
                optimize=True,
            )
            derivative_current = derivative_numerator / 2
            _gaussian_integer_array(
                derivative_current, "normalized current derivative"
            )
            derivative_k = np.einsum(
                "g,gij->ij",
                derivative_current.conj(),
                sigma_generators,
                optimize=True,
            )
            derivative_k = _gaussian_integer_array(
                derivative_k, "current-endomorphism derivative"
            )
            image_raw = _gaussian_integer_array(
                derivative_k @ delta_raw, "flat Jacobian image"
            )
            images_raw.append(image_raw)
            derivative_supports.append(int(np.count_nonzero(derivative_current)))
    images = np.asarray(images_raw)
    complex_gram_raw = images.conj() @ images.T
    real_gram_raw = np.real(complex_gram_raw).astype(np.int64)
    real_gram_exact = np.array_equal(real_gram_raw, 8 * np.eye(6, dtype=np.int64))
    real_rank = int(np.linalg.matrix_rank(real_gram_raw))
    if not (real_gram_exact and real_rank == 6 and derivative_supports == [2] * 6):
        raise ArithmeticError("the exact six-flat Jacobian identity failed")

    canonical_lift = GAMMA_SELECTED * R_SELECTED * R_SELECTED
    if canonical_lift != Q(1, 500):
        raise ArithmeticError("the selected EFT lift normalization drifted")
    return {
        "flat_subspace": (
            "desired-chirality colour u_b=(e_(2b)+i e_(2b+1))/sqrt(2), "
            "and i u_b, b=0,1,2"
        ),
        "number_of_real_flats": 6,
        "raw_image_gram": "8 I6",
        "unit_complex_field_image_real_gram_at_unit_Delta": "I6",
        "real_Jacobian_rank": real_rank,
        "at_Sigma_r_Delta": "Gram_real(dR)=r^2 I6 for unit complex-field directions",
        "canonical_486_chart": "H=(x+i y)/sqrt(2)",
        "canonical_chart_Jacobian_gram": "(r^2/2) I6",
        "portal_Hessian_on_six_unit_real_flats": "gamma r^2 I6",
        "selected_r": R_SELECTED,
        "selected_gamma": GAMMA_SELECTED,
        "selected_exact_Hessian_lift": canonical_lift,
        "old_beta_one_twentieth_colour_lift": Q(1, 500),
        "matches_old_B02_flat_lift_exactly": canonical_lift == Q(1, 500),
    }


def _canonical_monomial_key(
    bar_first: int, hol_first: int, bar_second: int, hol_second: int
) -> tuple[tuple[int, int], tuple[int, int]]:
    return (
        tuple(sorted((bar_first, bar_second))),
        tuple(sorted((hol_first, hol_second))),
    )


def exact_plucker_restriction_certificate() -> dict[str, Any]:
    """Prove the global decomposable-z identity by a canonical slice.

    U(5) is transitive on unit decomposable two-forms.  Gauge covariance and
    homogeneity therefore reduce the identity to z=-i e_3 wedge e_4, which is
    precisely the live Delta_R kernel column.  The remaining statement is a
    quartic polynomial identity in arbitrary h in C^5.  We compare every
    Gaussian-integer monomial coefficient after clearing denominator 32.
    """

    exact_integer_source_certificate()
    h_generators = _gaussian_integer_array(
        current_source.h_generator_matrices(), "10 generators"
    )
    sigma_generators = _gaussian_integer_array(
        current_source.sigma_generator_matrices(), "126bar generators"
    )
    plus = _plus_embedding()
    delta_real, delta_imaginary = delta_source.raw_delta_coordinates()
    delta_raw = delta_real + 1j * delta_imaginary

    restricted_h_generators = np.einsum(
        "ia,gij,jb->gab",
        plus.conj(),
        h_generators,
        plus,
        optimize=True,
    )
    sigma_images = np.einsum(
        "gij,j->gi", sigma_generators, delta_raw, optimize=True
    )
    # H=E_plus h/sqrt(2), Sigma=Delta_raw/sqrt(8).  Since the H generators
    # are anti-Hermitian, conjugate(h^dag A h)=-(h^dag A h).  Thus the
    # coefficient vector below gives the numerator of K_H Sigma and the
    # squared norm has common denominator 2^2*8=32.
    residual_coefficients = -np.einsum(
        "gab,gi->abi", restricted_h_generators, sigma_images, optimize=True
    )
    residual_coefficients = _gaussian_integer_array(
        residual_coefficients, "canonical residual coefficients"
    )

    observed: defaultdict[
        tuple[tuple[int, int], tuple[int, int]], complex
    ] = defaultdict(complex)
    for a in range(5):
        for b in range(5):
            left = residual_coefficients[a, b]
            if not np.any(left):
                continue
            for c in range(5):
                for d in range(5):
                    right = residual_coefficients[c, d]
                    if not np.any(right):
                        continue
                    coefficient = complex(np.vdot(left, right))
                    if coefficient:
                        # conjugate(bar(h_a)h_b V_ab) times
                        # bar(h_c)h_d V_cd gives bars (b,c), holomorphic (a,d).
                        observed[_canonical_monomial_key(b, a, c, d)] += coefficient

    expected: defaultdict[
        tuple[tuple[int, int], tuple[int, int]], complex
    ] = defaultdict(complex)
    # Delta_R is the (3,4) two-form up to phase, so
    # ||h wedge z||^2=sum_{q=0}^2 |h_q|^2 for unit z.
    for p in range(5):
        for q in (0, 1, 2):
            expected[_canonical_monomial_key(p, p, q, q)] += 32

    all_keys = set(observed) | set(expected)
    mismatches = {
        key: (observed[key], expected[key])
        for key in all_keys
        if observed[key] != expected[key]
    }
    if mismatches:
        raise ArithmeticError(
            f"the cleared canonical Pluecker polynomial identity failed: {mismatches}"
        )
    fixed_equality = equality_source.exact_fixed_f_equality_certificate()
    if not fixed_equality["proof_grade"]:
        raise ArithmeticError("the incident-flag transitivity dependency drifted")
    return {
        "scope": (
            "Phi=+F, desired H chirality, Sigma in the exact complex-10 mixed "
            "kernel, and z decomposable"
        ),
        "kernel_identification": "Sigma kernel = Lambda^2(C^5)",
        "coordinate_map": "Sigma=E conjugate(z/phase)/sqrt(8)",
        "canonical_two_form": "Delta_R corresponds to z=-i e3 wedge e4",
        "cleared_denominator": 32,
        "observed_nonzero_canonical_monomials": len(observed),
        "expected_nonzero_canonical_monomials": len(expected),
        "all_canonical_polynomial_coefficients_exact": not mismatches,
        "covariant_homogeneous_extension": (
            "U(5) transitivity on nonzero decomposable two-forms plus SO(10) "
            "covariance and homogeneity"
        ),
        "exact_global_identity": "||K_H Sigma(z)||^2=||h||^2 ||h wedge z||^2",
        "zero_condition": (
            "for N_H>0 and decomposable z, O6=0 iff h wedge z=0"
        ),
        "beta0_equality_restriction": (
            "N_H=1, so O6=||h wedge z||^2 and its zero is exactly the "
            "incident-flag condition"
        ),
        "preserves_selected_global_equality_orbit": True,
    }


def exact_covariance_psd_and_uv_certificate() -> dict[str, Any]:
    exact_integer_source_certificate()
    return {
        "Hermiticity": (
            "T^g are anti-Hermitian and j_H^g is purely imaginary, hence "
            "conjugate(j_H^g) T_Sigma^g is Hermitian"
        ),
        "SO10_covariance": {
            "endomorphism": "K_(gH)=rho_Sigma(g) K_H rho_Sigma(g)^dag",
            "residual": "R(gH,gSigma)=rho_Sigma(g) R(H,Sigma)",
            "norm": "O6(gH,gSigma)=O6(H,Sigma)",
        },
        "abelian_symmetries": (
            "j_H is Hdag-H neutral; R carries the Sigma charge and ||R||^2 "
            "is neutral under U(1)_X and PQ"
        ),
        "mass_dimension": {"K_H": 2, "R": 3, "O6": 6},
        "global_PSD": "gamma O6>=0 for gamma>=0",
        "selected_stationarity": (
            "R=0 implies both the value and first derivative vanish; the "
            "selected Hessian is 2 gamma Re(J_R^dag J_R)>=0"
        ),
        "EFT_normalization": (
            "V_EFT=(gamma/Lambda^2)O6; Lambda is absorbed in the model units "
            "when gamma=1/20 is quoted"
        ),
        "canonical_realification": (
            "for Sigma=(x+i y)/sqrt(2), pack(K_H Sigma)=A_real q and "
            "||K_H Sigma||^2=(1/2)||A_real q||^2; at R=0 the canonical "
            "real Hessian is gamma J_real^T J_real"
        ),
        "UV_interpretation": (
            "O6 is the norm square of a covariant composite in the 126bar. "
            "It is admissible as a positive Wilson contact or auxiliary-square "
            "operator.  A healthy heavy field with only a linear X^dag R "
            "coupling generates a negative coefficient after tree-level "
            "elimination, so positive gamma is UV matching data; no standalone "
            "renormalizable single-mediator completion is claimed here."
        ),
    }


def build_report() -> dict[str, Any]:
    report = {
        "status": STATUS,
        "dependencies": exact_dependency_guard(),
        "scope": (
            "the dimension-six current-endomorphism stabilizer, its selected "
            "vacuum jet, and its restriction to the exact +F Pluecker locus"
        ),
        "integer_source_certificate": exact_integer_source_certificate(),
        "selected_operator_certificate": exact_selected_operator_certificate(),
        "six_flat_Jacobian_certificate": exact_six_flat_jacobian_certificate(),
        "Pluecker_restriction_certificate": exact_plucker_restriction_certificate(),
        "covariance_PSD_UV_certificate": exact_covariance_psd_and_uv_certificate(),
        "conclusion": (
            "gamma||K_H Sigma||^2 is a globally PSD gauge-invariant EFT "
            "operator; it vanishes on the selected incident flag and lifts all "
            "six old beta0 real colour flats by gamma r^2 in the canonical chart"
        ),
        "closure_flags": {
            "dimension6_operator_exact": True,
            "globally_PSD_for_gamma_nonnegative": True,
            "selected_vacuum_value_and_gradient_zero": True,
            "six_beta0_quotient_flats_lifted": True,
            "plus_F_incident_flag_zero_preserved": True,
            "full_486_Hessian_recompiled": False,
            "signed_Phi_global_equality_closed": False,
            "renormalizable_UV_completion_proved": False,
            "G3_closed": False,
            "G4_closed": False,
        },
        "claim_boundary": (
            "this exact EFT certificate must still be composed with the beta0 "
            "global SOS/equality census and the full symmetry quotient; it does "
            "not close G3 or G4 by itself"
        ),
    }
    report["core_sha256"] = _canonical_sha256(report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--allow-unfrozen", action="store_true")
    arguments = parser.parse_args()
    report = build_report()
    if (
        not arguments.allow_unfrozen
        and EXPECTED_CORE_SHA256 != "TO_BE_FROZEN"
        and report["core_sha256"] != EXPECTED_CORE_SHA256
    ):
        raise ArithmeticError(
            f"core hash drift {report['core_sha256']} != {EXPECTED_CORE_SHA256}"
        )
    print(json.dumps(_jsonable(report), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
