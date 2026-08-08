#!/usr/bin/env python3
"""Exact rank-one maximal-negative bound on the dangerous SU(3) slice.

Fix ``H=h_-`` and the normalized explicit decomposable pure-spinor endpoint

    Sigma=(e0+i e1)...(e8+i e9)/4.

In ``z=sqrt(10) Phi`` coordinates consider the four-real-dimensional slice

    z = x e01 w1 + y e01(w2+w3+w4)
        + a w1(w2+w3+w4) + b(w2w3+w2w4+w3w4),

where ``wi=e_(2i)e_(2i+1)`` on the eight-dimensional complement.  This is a
four-dimensional sub-slice of the full 16-real-dimensional SU(3)-fixed space
and contains the lowest rank-one anchor found by the full deterministic
search.  Direct contraction of the live tensors gives

    A(x,y,a,b) = P + (9/10) Q_chi + R_rank1/32,

with ``R_rank1=||A_mix z-b_mix||^2/160``.  The polynomial is reconstructed
exactly from the live pair-Casimir projectors and Gaussian-integer residual
arrays.  A stored rational 15x15 Gram matrix in monomials of degree at most
two has an exact positive LDL decomposition and proves

    A(x,y,a,b) >= 3/200.

The threshold ``3/200`` is sufficient for the same radial patch as the
pure-Delta proof, so the full ``u,v`` gap on this slice has minimum 1/5000.
This is deliberately not a proof for arbitrary real Phi at the rank-one
endpoint, nor for arbitrary Sigma in the full complex 35, and does not close
G3 by itself.
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

import direct_phi_h_sigmabar_tensor_v20 as direct
import exact_126bar_self_quartic_basis_v20 as sigma_self
import exact_gauged_u1x_g3_a_square_recoupling_v20 as mixed_source
import exact_gauged_u1x_g3_pd_rank_certificate_v20 as rank_source
import exact_gauged_u1x_g3_sos_bfb_stationarity_v20 as delta_source
import exact_gauged_u1x_g3_su5_max_negative_zero_residual_bound_v20 as zero_source
import exact_mixed_45_triplet_channel_v20 as current_source
import exact_phisigma_casimir_projectors_v20 as projectors
import live_g2_canonical_486_field_chart_v20 as chart

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_GAUGED_U1X_G3_SU5_MAX_NEGATIVE_RANK1_SU3_SLICE_V20.json"
OUT_MD = ROOT / "EXACT_GAUGED_U1X_G3_SU5_MAX_NEGATIVE_RANK1_SU3_SLICE_V20.md"
MODEL_CONTRACT_ID = delta_source.MODEL_CONTRACT_ID

ANCHOR_TARGET = Fraction(3, 200)
RESTRICTED_GLOBAL_MINIMUM = Fraction(1, 5_000)
GRAM_DENOMINATOR = 240_000_000
INT64_MAX = int(np.iinfo(np.int64).max)
STATUS = "EXACT_RANK1_SU3_DANGEROUS_SLICE_BOUND_CERTIFIED"
OVERALL_STATE = "CLOSED_RANK1_SU3_SLICE__ARBITRARY_RANK1_PHI_OPEN"

N_VARIABLES = 4
ZERO_EXPONENT = (0, 0, 0, 0)
LINEAR_EXPONENTS = tuple(
    tuple(int(row == column) for column in range(N_VARIABLES))
    for row in range(N_VARIABLES)
)
QUADRATIC_EXPONENTS = tuple(
    tuple(
        LINEAR_EXPONENTS[left][column]
        + LINEAR_EXPONENTS[right][column]
        for column in range(N_VARIABLES)
    )
    for left in range(N_VARIABLES)
    for right in range(left, N_VARIABLES)
)
SOS_MONOMIAL_EXPONENTS = (
    (ZERO_EXPONENT,) + LINEAR_EXPONENTS + QUADRATIC_EXPONENTS
)

EXPECTED_ANCHOR_POLYNOMIAL = {
    (0, 0, 0, 0): Fraction(6, 5),
    (0, 0, 0, 1): Fraction(-3, 10),
    (0, 0, 1, 0): Fraction(-3, 10),
    (0, 1, 0, 0): Fraction(-3, 10),
    (1, 0, 0, 0): Fraction(-1, 10),
    (0, 0, 0, 2): Fraction(-87, 400),
    (0, 0, 1, 1): Fraction(153, 200),
    (0, 0, 2, 0): Fraction(-87, 400),
    (0, 1, 0, 1): Fraction(9, 40),
    (0, 1, 1, 0): Fraction(9, 40),
    (0, 2, 0, 0): Fraction(-39, 80),
    (1, 0, 0, 1): Fraction(3, 40),
    (1, 0, 1, 0): Fraction(3, 40),
    (1, 1, 0, 0): Fraction(3, 40),
    (2, 0, 0, 0): Fraction(-3, 16),
    (0, 0, 0, 4): Fraction(343, 3_000),
    (0, 0, 2, 2): Fraction(43, 250),
    (0, 0, 4, 0): Fraction(343, 3_000),
    (0, 2, 0, 2): Fraction(43, 250),
    (0, 2, 2, 0): Fraction(461, 3_000),
    (0, 4, 0, 0): Fraction(343, 3_000),
    (1, 1, 1, 1): Fraction(-4, 75),
    (2, 0, 0, 2): Fraction(27, 500),
    (2, 0, 2, 0): Fraction(217, 3_000),
    (2, 2, 0, 0): Fraction(217, 3_000),
    (4, 0, 0, 0): Fraction(7, 500),
}

SOS_GRAM_NUMERATOR = np.asarray(
    (
        (284400000, -12000000, -36000000, -36000000, -36000000, -25330440, 4877312, 5800343, 5732295, -67843279, 17666730, 17768865, -41759860, 68432434, -41471413),
        (-12000000, 5660880, 4122688, 3199657, 3267705, 0, -3276608, -2586844, -2789380, 2953355, 272142, 234915, 1764183, -562210, 1878306),
        (-36000000, 4122688, 18686558, 9333270, 9231135, 3276608, -2953355, -266343, -124333, 0, -7134173, -7113032, 4878411, -4420647, 4737184),
        (-36000000, 3199657, 9333270, 31319720, 23367566, 2586844, -5799, -1764183, 123729, 7134173, -4878411, 2637521, 0, -7541635, 7376629),
        (-36000000, 3267705, 9231135, 23367566, 30742826, 2789380, -110582, 438481, -1878306, 7113032, 1783126, -4737184, 7541635, -7376629, 0),
        (-25330440, 0, 3276608, 2586844, 2789380, 3360000, 0, 0, 0, 5811622, -1777444, -1918144, 3510778, -7229921, 2219723),
        (4877312, -3276608, -2953355, -5799, -110582, 0, 5736756, 1777444, 1918144, 0, 1468716, 1638397, -338161, -1078173, -5554),
        (5800343, -2586844, -266343, -1764183, 438481, 0, 1777444, 10338444, 7229921, -1468716, 338161, -3197843, 0, 1728080, -1511357),
        (5732295, -2789380, -124333, 123729, -1878306, 0, 1918144, 7229921, 8520554, -1638397, -2123984, 5554, -1728080, 1511357, 0),
        (-67843279, 2953355, 0, 7134173, 7113032, 5811622, 0, -1468716, -1638397, 27440000, 0, 0, 6943182, -16587080, 8224765),
        (17666730, 272142, -7134173, -4878411, 1783126, -1777444, 1468716, 338161, -2123984, 0, 22993636, 16587080, 0, 5110562, -5018347),
        (17768865, 234915, -7113032, 2637521, -4737184, -1918144, 1638397, -3197843, 5554, 0, 16587080, 24830470, -5110562, 5018347, 0),
        (-41759860, 1764183, 4878411, 0, 7541635, 3510778, -338161, 0, -1728080, 6943182, 0, -5110562, 27440000, 0, -75087),
        (68432434, -562210, -4420647, -7541635, -7376629, -7229921, -1078173, 1728080, 1511357, -16587080, 5110562, 5018347, 0, 41430174, 0),
        (-41471413, 1878306, 4737184, 7376629, 0, 2219723, -5554, -1511357, 0, 8224765, -5018347, 0, -75087, 0, 27440000),
    ),
    dtype=np.int64,
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


def _add_exponents(
    left: tuple[int, ...], right: tuple[int, ...]
) -> tuple[int, ...]:
    return tuple(
        first + second for first, second in zip(left, right, strict=True)
    )


def _add_coefficient(
    polynomial: dict[tuple[int, ...], Fraction],
    exponent: tuple[int, ...],
    value: Fraction,
) -> None:
    polynomial[exponent] = polynomial.get(exponent, Fraction(0)) + value


def _require_int64_bound(label: str, absolute_bound: int) -> int:
    """Fail before an exact integer contraction could overflow ``int64``."""
    bound = int(absolute_bound)
    if bound > INT64_MAX:
        raise OverflowError(
            f"{label} has conservative bound {bound} exceeding {INT64_MAX}"
        )
    return bound


def _maximum_abs_integer(value: np.ndarray) -> int:
    return int(np.max(np.abs(np.asarray(value, dtype=np.int64)), initial=0))


def _exact_sigma_self_projector_quartics(
    sigma_real: np.ndarray, sigma_imaginary: np.ndarray
) -> dict[str, Fraction]:
    """Evaluate all live Sigma self-projectors over Gaussian integers."""
    pair_real = np.outer(sigma_real, sigma_real) - np.outer(
        sigma_imaginary, sigma_imaginary
    )
    pair_imaginary = np.outer(sigma_real, sigma_imaginary) + np.outer(
        sigma_imaginary, sigma_real
    )
    powers = [(pair_real, pair_imaginary)]
    for _ in range(3):
        powers.append(delta_source._sigma_pair_casimir(*powers[-1]))

    output: dict[str, Fraction] = {}
    for channel in sigma_self.CHANNELS:
        polynomial = sigma_self._poly(channel)
        denominator = math.lcm(
            *(coefficient.denominator for coefficient in polynomial)
        )
        projected_real = sum(
            (
                int(coefficient * denominator) * powers[degree][0]
                for degree, coefficient in enumerate(polynomial)
            ),
            np.zeros_like(pair_real),
        )
        projected_imaginary = sum(
            (
                int(coefficient * denominator) * powers[degree][1]
                for degree, coefficient in enumerate(polynomial)
            ),
            np.zeros_like(pair_imaginary),
        )
        numerator = sum(
            int(value) ** 2 for value in projected_real.flat
        ) + sum(int(value) ** 2 for value in projected_imaginary.flat)
        output[channel] = Fraction(numerator, denominator**2)
    return output


@lru_cache(maxsize=1)
def exact_rank1_residual_source() -> dict[str, Any]:
    endpoint: direct.Form = {(): 1.0 + 0.0j}
    for first, second in ((0, 1), (2, 3), (4, 5), (6, 7), (8, 9)):
        endpoint = direct.wedge(
            endpoint,
            direct.add_forms(
                direct.one_form(first),
                direct.scale_form(direct.one_form(second), 1j),
            ),
        )
    observed_coordinates = chart.sigma_coordinates(endpoint)
    sigma_real = np.rint(observed_coordinates.real).astype(np.int64)
    sigma_imaginary = np.rint(observed_coordinates.imag).astype(np.int64)
    coordinate_integrality_residual = float(
        np.max(
            np.abs(
                observed_coordinates
                - (sigma_real + 1j * sigma_imaginary)
            ),
            initial=0.0,
        )
    )
    operator_real, operator_imaginary = mixed_source.integer_cubic_operators()
    contraction_real, contraction_imaginary = (
        mixed_source.integer_contraction_tensor()
    )
    m_real = (
        np.einsum("pab,b->pa", operator_real, sigma_real, optimize=True)
        - np.einsum(
            "pab,b->pa", operator_imaginary, sigma_imaginary, optimize=True
        )
    )
    m_imaginary = (
        np.einsum(
            "pab,b->pa", operator_real, sigma_imaginary, optimize=True
        )
        + np.einsum(
            "pab,b->pa", operator_imaginary, sigma_real, optimize=True
        )
    )
    c_real = (
        np.einsum("vpa,a->vp", contraction_real, sigma_real, optimize=True)
        - np.einsum(
            "vpa,a->vp", contraction_imaginary, sigma_imaginary, optimize=True
        )
    )
    c_imaginary = (
        np.einsum(
            "vpa,a->vp", contraction_real, sigma_imaginary, optimize=True
        )
        + np.einsum(
            "vpa,a->vp", contraction_imaginary, sigma_real, optimize=True
        )
    )
    mixed = np.vstack(
        (m_real.T, m_imaginary.T, c_real, c_imaginary)
    ).astype(np.int64)
    target = np.concatenate(
        (
            8 * sigma_real,
            8 * sigma_imaginary,
            np.zeros(20, dtype=np.int64),
        )
    )
    chiral, integrality_residual = zero_source._integral_chiral_wedge_rows()
    z0 = np.zeros(chart.PHI_DIM, dtype=np.int64)
    index = {indices: position for position, indices in enumerate(chart.PHI_INDICES)}
    for indices in (
        (0, 1, 2, 3),
        (0, 1, 4, 5),
        (0, 1, 6, 7),
        (0, 1, 8, 9),
    ):
        z0[index[indices]] = 1
    q_norm_squared = int(
        sigma_real @ sigma_real + sigma_imaginary @ sigma_imaginary
    )
    reconstructed_endpoint = chart.sigma_from_coordinates(
        sigma_real + 1j * sigma_imaginary
    )
    coordinate_reconstruction_residual = direct.tensor_norm(
        direct.add_forms(
            endpoint,
            direct.scale_form(reconstructed_endpoint, -1.0),
        )
    )
    hodge_residual = direct.tensor_norm(
        direct.add_forms(
            direct.hodge_star(endpoint),
            direct.scale_form(endpoint, 1j),
        )
    )
    kinetic_norm_squared = complex(
        direct.sigma_kinetic_inner(endpoint, endpoint)
    )
    generator_real, generator_imaginary = (
        delta_source.integer_sigma_generators()
    )
    # integer_sigma_generators follows combinations(range(10), 2), so row 0
    # is T_01.  K=i T_01 is the normalized Hermitian current operator.
    k_real = -generator_imaginary[0]
    k_imaginary = generator_real[0]
    k_sigma_real = (
        k_real @ sigma_real - k_imaginary @ sigma_imaginary
    )
    k_sigma_imaginary = (
        k_real @ sigma_imaginary + k_imaginary @ sigma_real
    )
    maximal_negative_current_residual = max(
        _maximum_abs_integer(k_sigma_real + sigma_real),
        _maximum_abs_integer(k_sigma_imaginary + sigma_imaginary),
    )

    h_raw: direct.Form = {(0,): 1.0 + 0.0j, (1,): -1j}
    h_current = current_source.hermitian_current_45(
        h_raw, kinetic_factor=1.0
    )
    sigma_current = current_source.hermitian_current_45(
        endpoint, kinetic_factor=0.5
    )
    raw_current = complex(direct.tensor_inner(h_current, sigma_current))
    raw_h_norm_squared = complex(direct.tensor_inner(h_raw, h_raw))
    raw_h_norm_integer = int(round(raw_h_norm_squared.real))
    raw_sigma_norm_integer = int(round(kinetic_norm_squared.real))
    raw_current_integer = int(round(raw_current.real))
    current_rationalization_residual = max(
        abs(raw_h_norm_squared.imag),
        abs(raw_h_norm_squared.real - raw_h_norm_integer),
        abs(kinetic_norm_squared.imag),
        abs(kinetic_norm_squared.real - raw_sigma_norm_integer),
        abs(raw_current.imag),
        abs(raw_current.real - raw_current_integer),
    )
    normalized_current = Fraction(
        raw_current_integer,
        raw_h_norm_integer * raw_sigma_norm_integer,
    )

    raw_self_projectors = _exact_sigma_self_projector_quartics(
        sigma_real, sigma_imaginary
    )
    normalized_self_projectors = {
        channel: value / q_norm_squared**2
        for channel, value in raw_self_projectors.items()
    }
    expected_normalized_self_projectors = {
        "54": Fraction(0),
        "1050bar": Fraction(0),
        "4125": Fraction(0),
        "2772bar": Fraction(1),
    }
    endpoint_binding = {
        "representative": (
            "q=(e0+i e1)(e2+i e3)(e4+i e5)"
            "(e6+i e7)(e8+i e9)"
        ),
        "decomposable_five_form_by_construction": True,
        "source_dependency": (
            "tracked chart, integer current generator, exact Sigma "
            "pair-Casimir projectors, and direct Hermitian current"
        ),
        "coordinate_reconstruction_residual": (
            coordinate_reconstruction_residual
        ),
        "anti_self_dual_hodge_residual": hodge_residual,
        "raw_kinetic_norm_squared": kinetic_norm_squared.real,
        "raw_kinetic_norm_squared_imaginary_abs": abs(
            kinetic_norm_squared.imag
        ),
        "canonical_normalization": "Sigma=q/4",
        "normalized_kinetic_norm_squared": Fraction(q_norm_squared, 16),
        "current_operator": "K=i*T_01",
        "K_plus_identity_action_max_abs_residual": (
            maximal_negative_current_residual
        ),
        "raw_H_norm_squared": raw_h_norm_integer,
        "raw_current": raw_current_integer,
        "raw_current_imaginary_abs": abs(raw_current.imag),
        "current_rationalization_residual": (
            current_rationalization_residual
        ),
        "normalized_I45": normalized_current,
        "raw_self_projector_quartics": raw_self_projectors,
        "normalized_self_projector_quartics": (
            normalized_self_projectors
        ),
        "self_projector_completeness_exact": (
            sum(raw_self_projectors.values()) == q_norm_squared**2
        ),
        "proof_grade": bool(
            coordinate_integrality_residual == 0.0
            and coordinate_reconstruction_residual == 0.0
            and hodge_residual == 0.0
            and kinetic_norm_squared == complex(16, 0)
            and q_norm_squared == 16
            and Fraction(q_norm_squared, 16) == 1
            and maximal_negative_current_residual == 0
            and raw_h_norm_integer == 2
            and raw_sigma_norm_integer == 16
            and raw_current_integer == -32
            and current_rationalization_residual == 0.0
            and normalized_current == -1
            and normalized_self_projectors
            == expected_normalized_self_projectors
            and sum(raw_self_projectors.values()) == q_norm_squared**2
        ),
    }
    return {
        "sigma_integer_real": sigma_real,
        "sigma_integer_imaginary": sigma_imaginary,
        "sigma_integer_norm_squared": q_norm_squared,
        "sigma_coordinate_integrality_residual": coordinate_integrality_residual,
        "normalized_sigma": "Sigma=q/4",
        "endpoint_binding": endpoint_binding,
        "mixed": mixed,
        "target": target,
        "chiral": chiral,
        "particular_solution": z0,
        "mixed_shape": mixed.shape,
        "chiral_shape": chiral.shape,
        "target_norm_squared": int(target @ target),
        "mixed_particular_residual": int(
            np.max(np.abs(mixed @ z0 - target), initial=0)
        ),
        "chiral_particular_residual": int(
            np.max(np.abs(chiral @ z0), initial=0)
        ),
        "chiral_integrality_residual": integrality_residual,
        "normalizations": {
            "Q_chi": "||A_chi z||^2/40",
            "R_rank1": "||A_mix z-b||^2/160",
            "anchor_residual": (
                "(9/10)Q_chi+R_rank1/32="
                "9||A_chi z||^2/400+||A_mix z-b||^2/5120"
            ),
        },
        "source_binding_exact": bool(
            endpoint_binding["proof_grade"]
            and q_norm_squared == 16
            and coordinate_integrality_residual == 0.0
            and mixed.shape == (272, 210)
            and chiral.shape == (504, 210)
            and int(target @ target) == 1_024
            and not np.any(mixed @ z0 - target)
            and not np.any(chiral @ z0)
            and integrality_residual == 0.0
        ),
    }


@lru_cache(maxsize=1)
def exact_su3_slice_basis() -> np.ndarray:
    index = {indices: position for position, indices in enumerate(chart.PHI_INDICES)}
    basis = np.zeros((chart.PHI_DIM, N_VARIABLES), dtype=np.int64)
    basis[index[(0, 1, 2, 3)], 0] = 1
    for indices in ((0, 1, 4, 5), (0, 1, 6, 7), (0, 1, 8, 9)):
        basis[index[indices], 1] = 1
    for indices in ((2, 3, 4, 5), (2, 3, 6, 7), (2, 3, 8, 9)):
        basis[index[indices], 2] = 1
    for indices in ((4, 5, 6, 7), (4, 5, 8, 9), (6, 7, 8, 9)):
        basis[index[indices], 3] = 1
    return basis


@lru_cache(maxsize=1)
def exact_affine_kernel_certificate() -> dict[str, Any]:
    """Classify the exact linear common-zero space before quartic control."""
    source = exact_rank1_residual_source()
    combined = np.vstack((source["mixed"], source["chiral"]))
    nullspace = zero_source._exact_fraction_nullspace(combined)
    basis = np.asarray(nullspace["basis"], dtype=np.int64)
    z0 = np.asarray(source["particular_solution"], dtype=np.int64)
    plane_counts = np.asarray(
        [len(set(indices).intersection((0, 1))) for indices in chart.PHI_INDICES],
        dtype=np.int64,
    )
    column_plane_counts = tuple(
        tuple(
            int(value)
            for value in np.unique(
                plane_counts[np.flatnonzero(basis[:, column])]
            )
        )
        for column in range(basis.shape[1])
    )
    count_zero = sum(values == (0,) for values in column_plane_counts)
    count_one = sum(values == (1,) for values in column_plane_counts)
    count_two = sum(values == (2,) for values in column_plane_counts)
    return {
        "combined_matrix_shape": combined.shape,
        "exact_rank": nullspace["rank"],
        "exact_nullity": nullspace["nullity"],
        "integral_kernel_basis_shape": basis.shape,
        "maximum_basis_denominator": nullspace[
            "maximum_basis_denominator"
        ],
        "maximum_basis_numerator_abs": nullspace[
            "maximum_basis_numerator_abs"
        ],
        "basis_residual_max_abs": nullspace["basis_residual_max_abs"],
        "kernel_column_plane_count_census": {
            "no_0_or_1_index": count_zero,
            "exactly_one_of_0_or_1": count_one,
            "both_0_and_1": count_two,
        },
        "particular_solution_norm_squared": int(z0 @ z0),
        "particular_solution_dot_kernel_max_abs": int(
            np.max(np.abs(z0 @ basis), initial=0)
        ),
        "minimum_norm_affine_solution": "z0=e0123+e0145+e0167+e0189",
        "minimum_physical_N_Phi": Fraction(int(z0 @ z0), 10),
        "geometric_interpretation": (
            "15 directions in e01 wedge Lambda2(W), 35 directions in "
            "Lambda4(W), and no direction with exactly one of e0,e1"
        ),
        "proof_grade": bool(
            combined.shape == (776, 210)
            and nullspace["rank"] == 160
            and nullspace["nullity"] == 50
            and basis.shape == (210, 50)
            and nullspace["maximum_basis_denominator"] == 1
            and nullspace["maximum_basis_numerator_abs"] == 1
            and nullspace["basis_residual_max_abs"] == 0
            and (count_zero, count_one, count_two) == (35, 0, 15)
            and int(z0 @ z0) == 4
            and not np.any(z0 @ basis)
        ),
    }


@lru_cache(maxsize=1)
def _slice_pair_columns() -> np.ndarray:
    basis = exact_su3_slice_basis()
    columns: list[np.ndarray] = []
    for left in range(N_VARIABLES):
        for right in range(left, N_VARIABLES):
            pair = np.outer(basis[:, left], basis[:, right])
            if left != right:
                pair += pair.T
            columns.append(pair.ravel())
    return np.column_stack(columns).astype(np.int64)


@lru_cache(maxsize=1)
def exact_angular_gram() -> dict[str, Any]:
    columns = _slice_pair_columns()
    polynomials = [
        projectors.projector_polynomial(
            projectors.SPECTRAL_EIGENVALUES[channel]
        )
        for channel in ("54", "4125")
    ]
    coefficients = tuple(
        sum(polynomial[degree] for polynomial in polynomials)
        for degree in range(8)
    )
    denominator = math.lcm(
        *(coefficient.denominator for coefficient in coefficients)
    )
    numerators = tuple(
        int(coefficient * denominator) for coefficient in coefficients
    )
    operator = rank_source._phi_pair_casimir_integer()
    operator_row_l1 = int(
        np.max(
            np.asarray(abs(operator).sum(axis=1)).reshape(-1),
            initial=0,
        )
    )
    current = columns
    current_bound = _maximum_abs_integer(current)
    power_bounds = [current_bound]
    observed_power_maxima = [current_bound]
    response_bound = _require_int64_bound(
        "SU3-slice projector response initialization",
        abs(numerators[0]) * current_bound,
    )
    response = numerators[0] * current
    for numerator in numerators[1:]:
        current_bound = _require_int64_bound(
            "SU3-slice pair-Casimir power",
            operator_row_l1 * _maximum_abs_integer(current),
        )
        current = operator @ current
        observed_current = _maximum_abs_integer(current)
        if observed_current > current_bound:
            raise ArithmeticError(
                "observed pair-Casimir power exceeds its exact row-L1 bound"
            )
        power_bounds.append(current_bound)
        observed_power_maxima.append(observed_current)
        response_bound = _require_int64_bound(
            "SU3-slice projector response accumulation",
            response_bound + abs(numerator) * current_bound,
        )
        response += numerator * current
    column_l1 = int(np.max(np.sum(np.abs(columns), axis=0), initial=0))
    gram_bound = _require_int64_bound(
        "SU3-slice exact angular Gram",
        column_l1 * response_bound,
    )
    gram = np.asarray(columns.T @ response, dtype=np.int64)
    observed_response_maximum = _maximum_abs_integer(response)
    observed_gram_maximum = _maximum_abs_integer(gram)
    overflow_preflight = {
        "pair_Casimir_maximum_row_l1": operator_row_l1,
        "power_absolute_bounds": tuple(power_bounds),
        "observed_power_absolute_maxima": tuple(observed_power_maxima),
        "response_accumulation_absolute_bound": response_bound,
        "observed_response_absolute_maximum": observed_response_maximum,
        "slice_pair_column_maximum_l1": column_l1,
        "Gram_absolute_bound": gram_bound,
        "observed_Gram_absolute_maximum": observed_gram_maximum,
        "int64_limit": INT64_MAX,
        "proof_grade": bool(
            len(power_bounds) == len(numerators) == 8
            and all(
                observed <= bound
                for observed, bound in zip(
                    observed_power_maxima, power_bounds, strict=True
                )
            )
            and observed_response_maximum <= response_bound
            and observed_gram_maximum <= gram_bound
            and gram_bound <= INT64_MAX
        ),
    }
    return {
        "gram_numerator": gram,
        "denominator": denominator,
        "projector_polynomial_numerators": numerators,
        "symmetric_exact": bool(np.array_equal(gram, gram.T)),
        "int64_overflow_preflight": overflow_preflight,
    }


@lru_cache(maxsize=1)
def exact_anchor_polynomial() -> dict[tuple[int, ...], Fraction]:
    basis = exact_su3_slice_basis()
    residual = exact_rank1_residual_source()
    polynomial: dict[tuple[int, ...], Fraction] = {}

    norm_coefficients = tuple(
        Fraction(int(value), 10) for value in np.diag(basis.T @ basis)
    )
    _add_coefficient(polynomial, ZERO_EXPONENT, Fraction(1))
    squares = tuple(
        tuple(2 * value for value in exponent)
        for exponent in LINEAR_EXPONENTS
    )
    for left, left_coefficient in enumerate(norm_coefficients):
        _add_coefficient(
            polynomial, squares[left], -2 * left_coefficient
        )
        for right in range(left, N_VARIABLES):
            coefficient = left_coefficient * norm_coefficients[right]
            if left != right:
                coefficient *= 2
            _add_coefficient(
                polynomial,
                _add_exponents(squares[left], squares[right]),
                coefficient,
            )

    angular = exact_angular_gram()
    angular_gram = angular["gram_numerator"]
    angular_denominator = int(angular["denominator"])
    for left, left_exponent in enumerate(QUADRATIC_EXPONENTS):
        for right in range(left, len(QUADRATIC_EXPONENTS)):
            coefficient = Fraction(
                int(angular_gram[left, right]),
                100 * angular_denominator,
            )
            if left != right:
                coefficient *= 2
            _add_coefficient(
                polynomial,
                _add_exponents(
                    left_exponent, QUADRATIC_EXPONENTS[right]
                ),
                coefficient,
            )

    mixed = residual["mixed"]
    target = residual["target"]
    chiral = residual["chiral"]
    quadratic = (
        Fraction(9, 400) * (basis.T @ chiral.T @ chiral @ basis)
        + Fraction(1, 5_120) * (basis.T @ mixed.T @ mixed @ basis)
    )
    linear = Fraction(-2, 5_120) * (basis.T @ mixed.T @ target)
    _add_coefficient(
        polynomial, ZERO_EXPONENT, Fraction(int(target @ target), 5_120)
    )
    for index, exponent in enumerate(LINEAR_EXPONENTS):
        _add_coefficient(polynomial, exponent, Fraction(linear[index]))
    for left, left_exponent in enumerate(LINEAR_EXPONENTS):
        for right in range(left, N_VARIABLES):
            coefficient = Fraction(quadratic[left, right])
            if left != right:
                coefficient *= 2
            _add_coefficient(
                polynomial,
                _add_exponents(left_exponent, LINEAR_EXPONENTS[right]),
                coefficient,
            )
    return {
        exponent: coefficient
        for exponent, coefficient in polynomial.items()
        if coefficient
    }


def _gram_polynomial() -> dict[tuple[int, ...], Fraction]:
    output: dict[tuple[int, ...], Fraction] = {}
    for row, left in enumerate(SOS_MONOMIAL_EXPONENTS):
        for column, right in enumerate(SOS_MONOMIAL_EXPONENTS):
            _add_coefficient(
                output,
                _add_exponents(left, right),
                Fraction(
                    int(SOS_GRAM_NUMERATOR[row, column]),
                    GRAM_DENOMINATOR,
                ),
            )
    return {
        exponent: coefficient
        for exponent, coefficient in output.items()
        if coefficient
    }


def _exact_ldl_pivots() -> tuple[Fraction, ...]:
    dimension = SOS_GRAM_NUMERATOR.shape[0]
    matrix = tuple(
        tuple(
            Fraction(int(SOS_GRAM_NUMERATOR[row, column]), GRAM_DENOMINATOR)
            for column in range(dimension)
        )
        for row in range(dimension)
    )
    lower = [
        [Fraction(int(row == column)) for column in range(dimension)]
        for row in range(dimension)
    ]
    diagonal: list[Fraction] = []
    for pivot in range(dimension):
        value = matrix[pivot][pivot] - sum(
            lower[pivot][column] ** 2 * diagonal[column]
            for column in range(pivot)
        )
        if not value:
            raise ArithmeticError("rational SOS Gram matrix has a zero LDL pivot")
        diagonal.append(value)
        for row in range(pivot + 1, dimension):
            lower[row][pivot] = (
                matrix[row][pivot]
                - sum(
                    lower[row][column]
                    * lower[pivot][column]
                    * diagonal[column]
                    for column in range(pivot)
                )
            ) / value
    return tuple(diagonal)


@lru_cache(maxsize=1)
def exact_sos_certificate() -> dict[str, Any]:
    observed = exact_anchor_polynomial()
    expected_shifted = dict(observed)
    expected_shifted[ZERO_EXPONENT] -= ANCHOR_TARGET
    expected_shifted = {
        exponent: coefficient
        for exponent, coefficient in expected_shifted.items()
        if coefficient
    }
    gram_polynomial = _gram_polynomial()
    pivots = _exact_ldl_pivots()
    return {
        "variables": ("x", "y", "a", "b"),
        "monomial_order": (
            "1", "x", "y", "a", "b", "x2", "xy", "xa", "xb",
            "y2", "ya", "yb", "a2", "ab", "b2",
        ),
        "anchor_polynomial": observed,
        "expected_anchor_polynomial": EXPECTED_ANCHOR_POLYNOMIAL,
        "anchor_polynomial_source_binding_exact": (
            observed == EXPECTED_ANCHOR_POLYNOMIAL
        ),
        "Gram_shape": SOS_GRAM_NUMERATOR.shape,
        "Gram_denominator": GRAM_DENOMINATOR,
        "Gram_symmetric_exact": bool(
            np.array_equal(SOS_GRAM_NUMERATOR, SOS_GRAM_NUMERATOR.T)
        ),
        "Gram_polynomial_identity_exact": (
            gram_polynomial == expected_shifted
        ),
        "LDL_pivot_count": len(pivots),
        "LDL_all_pivots_strictly_positive": all(pivot > 0 for pivot in pivots),
        "smallest_LDL_pivot": min(pivots),
        "largest_LDL_pivot": max(pivots),
        "identity": "anchor-3/200=m(x,y,a,b)^T Gram m(x,y,a,b)",
        "strict_anchor_lower_bound": ANCHOR_TARGET,
        "proof_grade": bool(
            observed == EXPECTED_ANCHOR_POLYNOMIAL
            and SOS_GRAM_NUMERATOR.shape == (15, 15)
            and np.array_equal(SOS_GRAM_NUMERATOR, SOS_GRAM_NUMERATOR.T)
            and gram_polynomial == expected_shifted
            and len(pivots) == 15
            and all(pivot > 0 for pivot in pivots)
        ),
    }


@lru_cache(maxsize=1)
def exact_attaining_slice_witness() -> dict[str, Any]:
    """Evaluate the claimed equality point from the exact live arrays."""
    coordinates = np.asarray((-1, 1, -1, 1), dtype=np.int64)
    basis = exact_su3_slice_basis()
    z = basis @ coordinates
    angular = exact_angular_gram()
    pair_coordinates = np.asarray(
        [
            coordinates[left] * coordinates[right]
            for left in range(N_VARIABLES)
            for right in range(left, N_VARIABLES)
        ],
        dtype=np.int64,
    )
    norm_phi = Fraction(int(z @ z), 10)
    angular_projectors = Fraction(
        int(
            pair_coordinates
            @ angular["gram_numerator"]
            @ pair_coordinates
        ),
        100 * int(angular["denominator"]),
    )
    phi_gap = (norm_phi - 1) ** 2 + angular_projectors
    residual = exact_rank1_residual_source()
    chiral_vector = residual["chiral"] @ z
    mixed_vector = residual["mixed"] @ z - residual["target"]
    q_chi = Fraction(int(chiral_vector @ chiral_vector), 40)
    r_rank1 = Fraction(int(mixed_vector @ mixed_vector), 160)
    anchor = phi_gap + Fraction(9, 10) * q_chi + r_rank1 / 32

    live = zero_source.live_hsx_coefficient_binding_certificate()
    sigma_scale = Fraction(live["PD_sigma_scale"])
    sigma_target = Fraction(live["live_selected_sigma_norm_squared"])
    sigma_quartic = Fraction(
        live["live_symbolic_sigma_quartic_coefficients"]["O27_B03"]
    )
    beta = Fraction(live["live_beta_coefficient"])
    u = Fraction(1)
    v = Fraction(0)
    radial = (
        (u - 1) ** 2
        + sigma_quartic * (v - sigma_target) ** 2
        - beta * u * v
    )
    full_gap = phi_gap + u * q_chi + v * sigma_scale * r_rank1 + radial
    return {
        "u": u,
        "v": v,
        "x_y_a_b": tuple(int(value) for value in coordinates),
        "raw_z_norm_squared": int(z @ z),
        "N_Phi": norm_phi,
        "I54_plus_I4125": angular_projectors,
        "P": phi_gap,
        "Q_chi": q_chi,
        "mixed_residual_norm_squared": int(mixed_vector @ mixed_vector),
        "R_rank1": r_rank1,
        "anchor": anchor,
        "radial_value": radial,
        "full_gap": full_gap,
        "proof_grade": bool(
            live["proof_grade"]
            and angular["int64_overflow_preflight"]["proof_grade"]
            and norm_phi == 1
            and angular_projectors == 0
            and phi_gap == 0
            and q_chi == 0
            and r_rank1 == Fraction(8, 5)
            and anchor == Fraction(1, 20)
            and sigma_scale == Fraction(1, 8)
            and sigma_target == Fraction(1, 25)
            and sigma_quartic == Fraction(1, 8)
            and beta == Fraction(1, 20)
            and radial == RESTRICTED_GLOBAL_MINIMUM
            and full_gap == RESTRICTED_GLOBAL_MINIMUM
        ),
    }


@lru_cache(maxsize=1)
def exact_radial_patch_certificate() -> dict[str, Any]:
    live = zero_source.live_hsx_coefficient_binding_certificate()
    reference = zero_source.exact_current_and_radial_certificate()
    endpoint = exact_rank1_residual_source()["endpoint_binding"]
    witness = exact_attaining_slice_witness()

    sigma_quartic = Fraction(
        live["live_symbolic_sigma_quartic_coefficients"]["O27_B03"]
    )
    sigma_target = Fraction(live["live_selected_sigma_norm_squared"])
    beta = Fraction(live["live_beta_coefficient"])
    sigma_scale = Fraction(live["PD_sigma_scale"])
    anchor_u = Fraction(9, 10)
    anchor_v = Fraction(1, 4)

    radial_denominator = 4 * sigma_quartic - beta * beta
    radial_v_star = (
        4 * sigma_quartic * sigma_target + 2 * beta
    ) / radial_denominator
    radial_u_star = 1 + beta * radial_v_star / 2
    radial_global_minimum = (
        (radial_u_star - 1) ** 2
        + sigma_quartic * (radial_v_star - sigma_target) ** 2
        - beta * radial_u_star * radial_v_star
    )

    low_u_v_minimizer = (
        sigma_target + beta * anchor_u / (2 * sigma_quartic)
    )
    low_u_minimum = (
        (anchor_u - 1) ** 2
        + sigma_quartic * (low_u_v_minimizer - sigma_target) ** 2
        - beta * anchor_u * low_u_v_minimizer
    )
    reduced_derivative_at_anchor = (
        2 * (anchor_u - 1)
        - beta * sigma_target
        - beta * beta * anchor_u / (2 * sigma_quartic)
    )

    # Coefficients are ordered as u^2, uv, u, v^2, v, constant.
    small_v_left = (
        Fraction(1),
        -beta,
        Fraction(-2),
        sigma_quartic,
        -2 * sigma_quartic * sigma_target + 4 * ANCHOR_TARGET,
        Fraction(1)
        + sigma_quartic * sigma_target * sigma_target
        - RESTRICTED_GLOBAL_MINIMUM,
    )
    small_v_linear = small_v_left[4] - beta
    small_v_quadratic = sigma_quartic - beta * beta / 4
    small_v_right = (
        Fraction(1),
        -beta,
        Fraction(-2),
        beta * beta / 4 + small_v_quadratic,
        beta + small_v_linear,
        Fraction(1),
    )

    low_v_domination = {
        "P_coefficient_margin_at_v_equals_1_over_4": 1 - 4 * anchor_v,
        "Q_coefficient_margin_at_u_equals_9_over_10_v_equals_1_over_4": (
            anchor_u - 4 * anchor_v * Fraction(9, 10)
        ),
        "R_coefficient_identity": (
            sigma_scale == 4 * Fraction(1, 32)
        ),
        "proof_grade": bool(
            anchor_v == Fraction(1, 4)
            and anchor_u == Fraction(9, 10)
            and 1 - 4 * anchor_v == 0
            and anchor_u - 4 * anchor_v * Fraction(9, 10) == 0
            and sigma_scale == 4 * Fraction(1, 32)
        ),
    }
    high_v_domination = {
        "Q_coefficient_margin_at_u_equals_9_over_10": (
            anchor_u - Fraction(9, 10)
        ),
        "R_coefficient_margin_at_v_equals_1_over_4": (
            anchor_v * sigma_scale - Fraction(1, 32)
        ),
        "proof_grade": bool(
            anchor_u - Fraction(9, 10) == 0
            and anchor_v * sigma_scale - Fraction(1, 32) == 0
        ),
    }
    large_v_margin = (
        ANCHOR_TARGET
        + radial_global_minimum
        - RESTRICTED_GLOBAL_MINIMUM
    )
    low_u_margin = low_u_minimum - RESTRICTED_GLOBAL_MINIMUM
    return {
        "live_source_binding": {
            "HSX_PD_coefficients_proof_grade": live["proof_grade"],
            "rank1_endpoint_proof_grade": endpoint["proof_grade"],
            "reference_radial_certificate_proof_grade": reference[
                "proof_grade"
            ],
            "Sigma_quartic_coefficient": sigma_quartic,
            "Sigma_target_norm_squared": sigma_target,
            "beta_I45": beta,
            "mixed_residual_scale": sigma_scale,
            "rank1_normalized_I45": endpoint["normalized_I45"],
            "rank1_self_projector_quartics": endpoint[
                "normalized_self_projector_quartics"
            ],
        },
        "radial_current_polynomial": (
            "g=(u-1)^2+(1/8)(v-1/25)^2-(1/20)uv"
        ),
        "radial_global_minimizer": {
            "u": radial_u_star,
            "v": radial_v_star,
        },
        "radial_global_minimum": radial_global_minimum,
        "low_u_v_minimizer_at_u_equals_9_over_10": low_u_v_minimizer,
        "low_u_reduced_derivative_at_9_over_10": (
            reduced_derivative_at_anchor
        ),
        "small_v_region": "u>=9/10 and 0<=v<=1/4",
        "small_v_coefficient_domination": low_v_domination,
        "small_v_completion": (
            "gap-1/5000 >= (u-1-v/40)^2 + "
            "(4*anchor-3/50)*v + 199*v^2/1600"
        ),
        "small_v_left_coefficients_u2_uv_u_v2_v_1": small_v_left,
        "small_v_right_coefficients_u2_uv_u_v2_v_1": small_v_right,
        "small_v_polynomial_identity_exact": (
            small_v_left == small_v_right
        ),
        "small_v_linear_coefficient": small_v_linear,
        "small_v_quadratic_coefficient": small_v_quadratic,
        "large_v_region": "u>=9/10 and v>=1/4",
        "large_v_coefficient_domination": high_v_domination,
        "large_v_margin_above_1_over_5000": large_v_margin,
        "low_u_region": "0<=u<=9/10 and all v>=0",
        "low_u_minimum": low_u_minimum,
        "low_u_margin_above_1_over_5000": low_u_margin,
        "quadrant_partition": {
            "region_1": "0<=u<=9/10, all v>=0",
            "region_2": "u>=9/10, 0<=v<=1/4",
            "region_3": "u>=9/10, v>=1/4",
            "shared_boundaries_included": True,
            "covers_every_u_v_nonnegative": True,
        },
        "attaining_slice_point": witness,
        "restricted_global_minimum": RESTRICTED_GLOBAL_MINIMUM,
        "proof_grade": bool(
            live["proof_grade"]
            and endpoint["proof_grade"]
            and endpoint["normalized_I45"] == -1
            and endpoint["normalized_self_projector_quartics"]["54"] == 0
            and endpoint["normalized_self_projector_quartics"]["1050bar"]
            == 0
            and reference["proof_grade"]
            and reference["global_minimum"] == radial_global_minimum
            and sigma_quartic == Fraction(1, 8)
            and sigma_target == Fraction(1, 25)
            and beta == Fraction(1, 20)
            and sigma_scale == Fraction(1, 8)
            and radial_denominator == Fraction(199, 400)
            and radial_u_star == Fraction(1001, 995)
            and radial_v_star == Fraction(48, 199)
            and radial_global_minimum == Fraction(-7_001, 995_000)
            and reduced_derivative_at_anchor == Fraction(-211, 1_000)
            and reduced_derivative_at_anchor < 0
            and low_u_minimum == Fraction(83, 20_000)
            and small_v_left == small_v_right
            and small_v_linear == 0
            and small_v_quadratic > 0
            and low_v_domination["proof_grade"]
            and high_v_domination["proof_grade"]
            and large_v_margin > 0
            and low_u_margin > 0
            and witness["proof_grade"]
            and witness["full_gap"] == RESTRICTED_GLOBAL_MINIMUM
        ),
    }


def build_report() -> dict[str, Any]:
    residual = exact_rank1_residual_source()
    affine_kernel = exact_affine_kernel_certificate()
    angular = exact_angular_gram()
    sos = exact_sos_certificate()
    radial = exact_radial_patch_certificate()
    basis = exact_su3_slice_basis()
    checks = {
        "rank1_live_residual_source_exact": residual["source_binding_exact"],
        "explicit_endpoint_current_and_self_projectors_exactly": residual[
            "endpoint_binding"
        ]["proof_grade"],
        "slice_basis_Gram_exact": bool(
            np.array_equal(
                basis.T @ basis,
                np.diag((1, 3, 3, 3)).astype(np.int64),
            )
        ),
        "rank1_common_affine_kernel_rank160_nullity50_exact": affine_kernel[
            "proof_grade"
        ],
        "angular_projector_Gram_symmetric_exact": angular["symmetric_exact"],
        "angular_projector_int64_overflow_preflight_exact": angular[
            "int64_overflow_preflight"
        ]["proof_grade"],
        "anchor_polynomial_reconstructed_exactly": sos[
            "anchor_polynomial_source_binding_exact"
        ],
        "rational_SOS_polynomial_identity_exact": sos[
            "Gram_polynomial_identity_exact"
        ],
        "rational_SOS_Gram_positive_definite_exact": sos[
            "LDL_all_pivots_strictly_positive"
        ],
        "anchor_at_least_3_over_200_exact": sos["proof_grade"],
        "radial_patch_global_minimum_1_over_5000_exact": radial[
            "proof_grade"
        ],
        "attaining_slice_witness_evaluated_from_live_arrays_exact": radial[
            "attaining_slice_point"
        ]["proof_grade"],
        "arbitrary_rank1_Phi_proved": False,
        "arbitrary_Sigma35_proved": False,
        "G3_closed": False,
    }
    failed = [name for name, value in checks.items() if name not in {
        "arbitrary_rank1_Phi_proved", "arbitrary_Sigma35_proved", "G3_closed"
    } and not value]
    return {
        "status": STATUS if not failed else "RANK1_SU3_SLICE_CERTIFICATE_FAILED",
        "overall_state": OVERALL_STATE,
        "model_contract_id": MODEL_CONTRACT_ID,
        "scope": {
            "H_fixed_to_h_minus": True,
            "Sigma_fixed_to_normalized_explicit_decomposable_pure_spinor": (
                True
            ),
            "Phi_restricted_to_four_real_SU3_fixed_variables": True,
            "Phi_slice_real_dimension": 4,
            "full_SU3_fixed_space_real_dimension": 16,
            "full_SU3_fixed_space_proved": False,
            "u_v_arbitrary_nonnegative": True,
            "arbitrary_real_Phi": False,
            "arbitrary_max_negative_Sigma": False,
            "G3_closed": False,
            "whole_model_excluded": False,
        },
        "residual_source": residual,
        "affine_kernel": affine_kernel,
        "slice": {
            "definition": (
                "z=x e01w1+y e01(w2+w3+w4)+a w1(w2+w3+w4)"
                "+b(w2w3+w2w4+w3w4)"
            ),
            "basis_Gram": basis.T @ basis,
        },
        "angular_source": {
            "projector_polynomial_numerators": angular[
                "projector_polynomial_numerators"
            ],
            "projector_polynomial_denominator": angular["denominator"],
            "Gram_symmetric_exact": angular["symmetric_exact"],
            "int64_overflow_preflight": angular[
                "int64_overflow_preflight"
            ],
        },
        "SOS": sos,
        "radial_patch": radial,
        "checks": checks,
        "failed_checks": failed,
        "n_failed": len(failed),
    }


def render_markdown(report: dict[str, Any]) -> str:
    checks = report["checks"]
    lines = [
        "# Exact rank-one maximal-negative SU(3)-slice bound",
        "",
        f"Status: **{report['status']}**",
        "",
        "The live explicit decomposable pure-spinor source and the 54/4125 "
        "pair-Casimir projectors reconstruct the four-variable anchor "
        "polynomial exactly.",
        "A rational 15x15 Gram matrix has fifteen strictly positive exact LDL "
        "pivots and proves `anchor >= 3/200`.  The radial patch then gives the "
        "restricted global minimum `1/5000` for all nonnegative `u,v`.",
        "",
        "This closes only a four-dimensional sub-slice of the full "
        "16-real-dimensional SU(3)-fixed space.  Arbitrary real Phi at this "
        "explicit endpoint, the full maximal-negative Sigma-35 family, and "
        "G3 remain open.",
        "",
        "## Checks",
        "",
    ]
    lines.extend(
        f"- `{name}`: **{'PASS' if value else 'OPEN'}**"
        for name, value in checks.items()
    )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    report = build_report()
    if args.write:
        OUT_JSON.write_text(
            json.dumps(_jsonable(report), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        OUT_MD.write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps(_jsonable(report), indent=2, sort_keys=True))
    return int(report["n_failed"] != 0)


if __name__ == "__main__":
    raise SystemExit(main())
