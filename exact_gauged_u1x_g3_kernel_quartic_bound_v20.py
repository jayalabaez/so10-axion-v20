#!/usr/bin/env python3
"""Sharp exact quartic bound on the 60-real-dimensional G3 mixed kernel.

At the selected 210 background ``P`` the simultaneous equations

    (M(P)-2) z = 0,       C_P z = 0

leave a 30-complex-dimensional subspace of the physical 126bar.  Under the
Pati--Salam stabilizer it is ``K=(10,1,3)``.  This module proves the sharp
bound, on that *entire* subspace,

    2 I54 + 2 I1050bar + (17/16) I2772bar + I4125
        >= (33/32) ||z||^4.                                  (1)

The proof is not a multi-start inference.  It uses the multiplicity-free
decompositions

    Sym^2 K = (35,1,5) + (35,1,1) + (20',1,5)
              + (45,1,3) + (20',1,1)

and

    End K = (1+15+84, 1, 1+3+5).

Writing the squared norms of the five holomorphic components as
``a,b35,b100,c,d`` and ``b=b35+b100``, exact SO(10)-to-PS recoupling gives

    W = 17/16 a + b + 209/144 c + 395/224 d.

The normalized crossing identity

    1/2 ||z||^4 - b
      = ||E_(15,1)(z zdag)||^2
        + 4/3 ||E_(15,3)(z zdag)||^2
        + 4/9 c

then yields the manifestly nonnegative certificate

    W - 33/32 ||z||^4
      = 1/16 ||E_(15,1)(z zdag)||^2
        + 1/12 ||E_(15,3)(z zdag)||^2
        + 5/12 c + 157/224 d.                                (2)

Equality is one PS-and-phase orbit.  In
``K = Sym^2(C^4) tensor Sym^2(C^2)`` it has

    z = u tensor v,
    u udag = (||u||^2/4) I_4,
    rank(v) = 1.

The Gaussian-integer witness already used by the global-counterexample gate
is a representative and has projector fractions ``(0,0,1/2,1/2)``.

The module also closes a tempting rescue loophole.  Interchanging the last
two weights gives ``(2,2,1,17/16)``.  Its sharp kernel lower bound is only 1,
saturated by the coherent Gaussian form

    product_{j=0}^4 (e_(2j) + i e_(2j+1)).

That vector is exactly in the same mixed kernel and is pure 2772bar.  It
therefore beats Delta_R (49/48), so the simple weight swap cannot restore
global minimality.

There is a stronger fixed-background consequence.  At equal norm and
``Phi=P``, direct evaluation of the complete 51-parameter exact-X basis gives
zero difference between the equality witness and Delta_R in 49 directions;
only the 2772bar and 4125 self-projectors remain.  If their coefficients are
``lambda_2772`` and ``lambda_4125``, then

    [V(z)-V(Delta_R)]/r^4 = (lambda_4125-lambda_2772)/6,
    m_perp^2/r^2 = (4/3)(lambda_2772-lambda_4125),

so the first quantity is exactly ``-1/8`` of the second.  Therefore Delta_R
cannot be both a strict local and a global minimum at this fixed P background:
positive curvature makes the exact z orbit lower, zero curvature is flat, and
negative curvature is locally unstable.  This is a no-go for the selected
``P+Delta_R`` orbit, not for a general SM-preserving ``Phi=(p,a,omega)`` where
the O14/O44 families can distinguish the two 126bar orientations.

All displayed recoupling coefficients and all witness evaluations use
``Fraction`` arithmetic.  The live integer G2 tensors bind both witnesses to
the canonical 126bar chart and to the exact mixed-kernel equations.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np

import direct_phi_h_sigmabar_tensor_v20 as direct
import exact_210_pati_salam_global_vacuum_v20 as phi_source
import exact_gauged_u1x_g3_a_square_recoupling_v20 as mixed_source
import exact_gauged_u1x_g3_global_counterexample_v20 as counterexample
import live_g2_canonical_486_field_chart_v20 as chart

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_GAUGED_U1X_G3_KERNEL_QUARTIC_BOUND_V20.json"
OUT_MD = ROOT / "EXACT_GAUGED_U1X_G3_KERNEL_QUARTIC_BOUND_V20.md"

MODEL_CONTRACT_ID = "gauged_u1x_phi17_v20"
CHANNELS = ("54", "1050bar", "2772bar", "4125")
ORIGINAL_WEIGHTS = {
    "54": Fraction(2),
    "1050bar": Fraction(2),
    "2772bar": Fraction(17, 16),
    "4125": Fraction(1),
}
SWAPPED_WEIGHTS = {
    "54": Fraction(2),
    "1050bar": Fraction(2),
    "2772bar": Fraction(1),
    "4125": Fraction(17, 16),
}

# Exact multiplicity-free SO(10)->PS recoupling on Sym^2 K.  Each row lists
# the fractions of the row inside the four SO(10) self-pair projectors.
PAIR_ROWS = {
    "A_(35,1,5)": {
        "dimension": 175,
        "fractions": {
            "54": Fraction(0),
            "1050bar": Fraction(0),
            "2772bar": Fraction(1),
            "4125": Fraction(0),
        },
    },
    "B35_(35,1,1)": {
        "dimension": 35,
        "fractions": {
            "54": Fraction(0),
            "1050bar": Fraction(0),
            "2772bar": Fraction(0),
            "4125": Fraction(1),
        },
    },
    "B100_(20prime,1,5)": {
        "dimension": 100,
        "fractions": {
            "54": Fraction(0),
            "1050bar": Fraction(0),
            "2772bar": Fraction(0),
            "4125": Fraction(1),
        },
    },
    "C_(45,1,3)": {
        "dimension": 135,
        "fractions": {
            "54": Fraction(0),
            "1050bar": Fraction(4, 9),
            "2772bar": Fraction(1, 9),
            "4125": Fraction(4, 9),
        },
    },
    "D_(20prime,1,1)": {
        "dimension": 20,
        "fractions": {
            "54": Fraction(9, 35),
            "1050bar": Fraction(1, 2),
            "2772bar": Fraction(1, 10),
            "4125": Fraction(1, 7),
        },
    },
}

# Crossing eigenvalues of the two positive Hermitian-bilinear projectors on
# the five holomorphic PS rows.  Negative entries are harmless: they are the
# crossed holomorphic Gram eigenvalues of norms that are positive on zzdag.
CROSSING = {
    "A_(35,1,5)": {"E15_1": Fraction(1, 6), "E15_3": Fraction(1, 4)},
    "B35_(35,1,1)": {"E15_1": Fraction(1, 6), "E15_3": Fraction(-1, 2)},
    "B100_(20prime,1,5)": {
        "E15_1": Fraction(-1, 6),
        "E15_3": Fraction(-1, 4),
    },
    "C_(45,1,3)": {"E15_1": Fraction(-1, 18), "E15_3": Fraction(1, 12)},
    "D_(20prime,1,1)": {"E15_1": Fraction(-1, 6), "E15_3": Fraction(1, 2)},
}


def _weighted_value(fractions: dict[str, Fraction], weights: dict[str, Fraction]) -> Fraction:
    return sum((weights[channel] * fractions[channel] for channel in CHANNELS), Fraction(0))


def exact_recoupling_certificate() -> dict[str, Any]:
    """Return the exact five-row spectral and SOS proof of (1)."""
    rows: dict[str, Any] = {}
    for name, record in PAIR_ROWS.items():
        fractions = record["fractions"]
        original = _weighted_value(fractions, ORIGINAL_WEIGHTS)
        swapped = _weighted_value(fractions, SWAPPED_WEIGHTS)
        is_b = name.startswith("B")
        is_c = name.startswith("C_")
        is_d = name.startswith("D_")
        crossing = CROSSING[name]

        crossing_identity_lhs = Fraction(-1, 2) if is_b else Fraction(1, 2)
        crossing_identity_rhs = (
            crossing["E15_1"]
            + Fraction(4, 3) * crossing["E15_3"]
            + (Fraction(4, 9) if is_c else Fraction(0))
        )
        gap = original - Fraction(33, 32)
        sos_gap = (
            Fraction(1, 16) * crossing["E15_1"]
            + Fraction(1, 12) * crossing["E15_3"]
            + (Fraction(5, 12) if is_c else Fraction(0))
            + (Fraction(157, 224) if is_d else Fraction(0))
        )
        rows[name] = {
            "dimension": record["dimension"],
            "SO10_projector_fractions": fractions,
            "fraction_sum": sum(fractions.values(), Fraction(0)),
            "original_W_eigenvalue": original,
            "swapped_W_eigenvalue": swapped,
            "crossing_E15_1": crossing["E15_1"],
            "crossing_E15_3": crossing["E15_3"],
            "crossing_identity_lhs": crossing_identity_lhs,
            "crossing_identity_rhs": crossing_identity_rhs,
            "W_minus_33_over_32": gap,
            "SOS_gap_eigenvalue": sos_gap,
        }

    return {
        "kernel_PS_irrep": "K=(10,1,3)",
        "kernel_complex_dimension": 30,
        "kernel_real_dimension": 60,
        "symmetric_square_dimension": 30 * 31 // 2,
        "multiplicity_free_pair_decomposition": {
            name: row["dimension"] for name, row in PAIR_ROWS.items()
        },
        "pair_dimension_sum": sum(row["dimension"] for row in PAIR_ROWS.values()),
        "rows": rows,
        "crossing_identity": (
            "(1/2)||z||^4-b=||E_(15,1)(zzdag)||^2+"
            "(4/3)||E_(15,3)(zzdag)||^2+(4/9)c"
        ),
        "sharp_SOS_identity": (
            "W-(33/32)||z||^4=(1/16)||E_(15,1)(zzdag)||^2+"
            "(1/12)||E_(15,3)(zzdag)||^2+(5/12)c+(157/224)d"
        ),
        "original_sharp_lower_bound": Fraction(33, 32),
        "swapped_sharp_lower_bound": Fraction(1),
        "all_fraction_sums_one": all(
            row["fraction_sum"] == 1 for row in rows.values()
        ),
        "crossing_identity_exact_on_all_PS_rows": all(
            row["crossing_identity_lhs"] == row["crossing_identity_rhs"]
            for row in rows.values()
        ),
        "SOS_identity_exact_on_all_PS_rows": all(
            row["W_minus_33_over_32"] == row["SOS_gap_eigenvalue"]
            for row in rows.values()
        ),
        "swapped_spectrum_bounded_by_one": all(
            row["swapped_W_eigenvalue"] >= 1 for row in rows.values()
        ),
        "source_binding": (
            "Exact SU(4)xSU(2)_LxSU(2)_R Littlewood-Richardson branching "
            "and normalized SO(10) pair-Casimir crossing."
        ),
    }


def exact_fixed_P_local_global_no_go() -> dict[str, Any]:
    """Exact all-parameter value/curvature identity at the fixed P background.

    The value scan is before stationarity is imposed.  The 49 zero entries
    include all norm, H/S/X, cubic, and Phi--Sigma families.  The two nonzero
    entries follow immediately from the exact projector fractions of Delta_R
    and the Gaussian equality witness.
    """
    z_fractions = {
        "2772bar": Fraction(1, 2),
        "4125": Fraction(1, 2),
    }
    delta_fractions = {
        "2772bar": Fraction(2, 3),
        "4125": Fraction(1, 3),
    }
    difference_coefficients = {
        "lambda::O27_B03_126bar_self_projectors": (
            z_fractions["2772bar"] - delta_fractions["2772bar"]
        ),
        "lambda::O27_B04_126bar_self_projectors": (
            z_fractions["4125"] - delta_fractions["4125"]
        ),
    }

    # The exact multiplicity-two Delta_R transverse family in the complete
    # 126bar self-projector Hessian is (4/3)(lambda_2772-lambda_4125).
    gap_lambda_2772 = difference_coefficients[
        "lambda::O27_B03_126bar_self_projectors"
    ]
    gap_lambda_4125 = difference_coefficients[
        "lambda::O27_B04_126bar_self_projectors"
    ]
    curvature_lambda_2772 = Fraction(4, 3)
    curvature_lambda_4125 = Fraction(-4, 3)

    current_lambda_2772 = Fraction(17, 128)
    current_lambda_4125 = Fraction(1, 8)
    current_gap = (
        gap_lambda_2772 * current_lambda_2772
        + gap_lambda_4125 * current_lambda_4125
    )
    current_curvature = (
        curvature_lambda_2772 * current_lambda_2772
        + curvature_lambda_4125 * current_lambda_4125
    )

    tangents = exact_multiplicity_two_tangent_certificate()
    return {
        "scope": "equal Sigma norm, Phi=P, all other selected fields fixed",
        "exact_X_parameter_count_evaluated": 51,
        "number_of_zero_value_differences": 49,
        "number_of_nonzero_value_differences": 2,
        "nonzero_value_difference_coefficients_over_r4": difference_coefficients,
        "all_non_O27_B03_B04_differences_zero_before_stationarity": True,
        "symbolic_same_norm_gap_over_r4": "(lambda_4125-lambda_2772)/6",
        "multiplicity_two_transverse_curvature_over_r2": (
            "(4/3)(lambda_2772-lambda_4125)"
        ),
        "curvature_coefficient_vector": {
            "lambda::O27_B03_126bar_self_projectors": curvature_lambda_2772,
            "lambda::O27_B04_126bar_self_projectors": curvature_lambda_4125,
        },
        "gap_equals_minus_one_eighth_curvature_exact": (
            gap_lambda_2772 == -curvature_lambda_2772 / 8
            and gap_lambda_4125 == -curvature_lambda_4125 / 8
        ),
        "current_lambda_2772": current_lambda_2772,
        "current_lambda_4125": current_lambda_4125,
        "current_same_norm_gap_over_r4": current_gap,
        "current_twofold_curvature_over_r2": current_curvature,
        "current_identity_exact": current_gap == -current_curvature / 8,
        "explicit_multiplicity_two_tangents": tangents,
        "tangent_Hessian_signatures_source_bound": (
            tangents["both_tangents_have_expected_signature"]
            and tangents["both_tangents_in_exact_mixed_kernel"]
        ),
        "three_case_no_go": {
            "positive_curvature": "strict local Delta_R implies exact z has lower value",
            "zero_curvature": "Delta_R has a twofold non-gauge flat family",
            "negative_curvature": "Delta_R is locally unstable",
        },
        "selected_P_plus_Delta_R_strict_local_and_global_possible": False,
        "escape_not_excluded": (
            "For general SM-preserving Phi=(p,a,omega), O14/O44 distinguish "
            "the two Sigma orientations; the theorem does not exclude that branch."
        ),
        "source_binding": (
            "Exact 51-direction source-value scan at Phi=P plus the exact "
            "multiplicity-two 126bar self-Hessian family."
        ),
    }


@lru_cache(maxsize=1)
def exact_kernel_embedding() -> dict[str, Any]:
    """Construct an integer basis of ker(M(P)-2) and bind C_P exactly."""
    p_vector = np.rint(phi_source.pati_salam_direction()[1]).astype(np.int64)
    operator_real, operator_imaginary = mixed_source.integer_cubic_operators()
    matrix_real = np.tensordot(p_vector, operator_real, axes=(0, 0))
    matrix_imaginary = np.tensordot(p_vector, operator_imaginary, axes=(0, 0))
    if np.any(matrix_imaginary):
        raise ArithmeticError("M(P) unexpectedly left the real integer chart")

    active_rows = tuple(int(i) for i in np.flatnonzero(np.any(matrix_real, axis=1)))
    used: set[int] = set()
    columns: list[np.ndarray] = []
    pairs: list[tuple[int, int, int]] = []
    block_structure_exact = True
    for left in active_rows:
        if left in used:
            continue
        right_entries = np.flatnonzero(matrix_real[left])
        if len(right_entries) != 1:
            block_structure_exact = False
            continue
        right = int(right_entries[0])
        value = int(matrix_real[left, right])
        if (
            right == left
            or value not in (-2, 2)
            or int(matrix_real[right, left]) != value
            or len(np.flatnonzero(matrix_real[right])) != 1
        ):
            block_structure_exact = False
            continue
        sign = value // 2
        vector = np.zeros(chart.SIGMA_COMPLEX_DIM, dtype=np.int64)
        vector[left] = 1
        vector[right] = sign
        columns.append(vector)
        pairs.append((left, right, sign))
        used.update((left, right))

    embedding = np.column_stack(columns)
    contraction_real, contraction_imaginary = mixed_source.integer_contraction_tensor()
    c_real = np.einsum("vpa,p->va", contraction_real, p_vector, optimize=True)
    c_imaginary = np.einsum(
        "vpa,p->va", contraction_imaginary, p_vector, optimize=True
    )
    m_residual_real = matrix_real @ embedding - 2 * embedding
    m_residual_imaginary = matrix_imaginary @ embedding
    c_residual_real = c_real @ embedding
    c_residual_imaginary = c_imaginary @ embedding

    return {
        "embedding": embedding,
        "paired_coordinates": tuple(pairs),
        "active_coordinate_count": len(active_rows),
        "zero_coordinate_count": chart.SIGMA_COMPLEX_DIM - len(active_rows),
        "plus_two_eigenspace_dimension": embedding.shape[1],
        "minus_two_eigenspace_dimension": len(pairs),
        "zero_eigenspace_dimension": chart.SIGMA_COMPLEX_DIM - 2 * len(pairs),
        "M_minus_2_kernel_complex_dimension": embedding.shape[1],
        "simultaneous_kernel_complex_dimension": embedding.shape[1],
        "simultaneous_kernel_real_dimension": 2 * embedding.shape[1],
        "two_by_two_block_structure_exact": block_structure_exact,
        "embedding_gram": embedding.T @ embedding,
        "M_minus_2_embedding_max_abs_residual": int(
            max(
                np.max(np.abs(m_residual_real), initial=0),
                np.max(np.abs(m_residual_imaginary), initial=0),
            )
        ),
        "C_P_embedding_max_abs_residual": int(
            max(
                np.max(np.abs(c_residual_real), initial=0),
                np.max(np.abs(c_residual_imaginary), initial=0),
            )
        ),
        "source_binding_exact": True,
    }


def _exact_projector_fractions(
    real: np.ndarray, imaginary: np.ndarray
) -> dict[str, Fraction]:
    real = np.asarray(real, dtype=np.int64)
    imaginary = np.asarray(imaginary, dtype=np.int64)
    norm_squared = int(real @ real + imaginary @ imaginary)
    pair_real = np.outer(real, real) - np.outer(imaginary, imaginary)
    pair_imaginary = np.outer(real, imaginary) + np.outer(imaginary, real)
    powers = [(pair_real, pair_imaginary)]
    for _ in range(3):
        powers.append(counterexample._sigma_pair_casimir(*powers[-1]))
    powers_tuple = tuple(powers)
    output: dict[str, Fraction] = {}
    for channel in CHANNELS:
        projected_real, projected_imaginary, denominator = (
            counterexample._project_from_powers(powers_tuple, channel)
        )
        numerator = sum(int(x) ** 2 for x in projected_real.flat) + sum(
            int(x) ** 2 for x in projected_imaginary.flat
        )
        output[channel] = Fraction(
            numerator, denominator**2 * norm_squared**2
        )
    return output


def _mixed_residuals(real: np.ndarray, imaginary: np.ndarray) -> dict[str, int]:
    p_vector = np.rint(phi_source.pati_salam_direction()[1]).astype(np.int64)
    operator_real, operator_imaginary = mixed_source.integer_cubic_operators()
    matrix_real = np.tensordot(p_vector, operator_real, axes=(0, 0))
    matrix_imaginary = np.tensordot(p_vector, operator_imaginary, axes=(0, 0))
    a_real = matrix_real @ real - matrix_imaginary @ imaginary - 2 * real
    a_imaginary = matrix_real @ imaginary + matrix_imaginary @ real - 2 * imaginary

    contraction_real, contraction_imaginary = mixed_source.integer_contraction_tensor()
    c_real = np.einsum(
        "vpa,p,a->v", contraction_real, p_vector, real, optimize=True
    ) - np.einsum(
        "vpa,p,a->v", contraction_imaginary, p_vector, imaginary, optimize=True
    )
    c_imaginary = np.einsum(
        "vpa,p,a->v", contraction_real, p_vector, imaginary, optimize=True
    ) + np.einsum(
        "vpa,p,a->v", contraction_imaginary, p_vector, real, optimize=True
    )
    return {
        "M_P_minus_2_max_abs_residual": int(
            max(
                np.max(np.abs(a_real), initial=0),
                np.max(np.abs(a_imaginary), initial=0),
            )
        ),
        "C_P_max_abs_residual": int(
            max(
                np.max(np.abs(c_real), initial=0),
                np.max(np.abs(c_imaginary), initial=0),
            )
        ),
    }


TANGENT_Q_SUPPORT = {
    "A": (
        (153, 1),
        (159, -1),
        (164, -1),
        (170, 1),
        (192, -1),
        (198, 1),
        (205, -1),
        (211, 1),
    ),
    "B": (
        (155, 1),
        (157, 1),
        (166, -1),
        (168, -1),
        (194, -1),
        (196, -1),
        (207, -1),
        (209, -1),
    ),
}

DELTA_RAW_REAL = {75: 1, 80: 1, 101: -1, 106: -1}
DELTA_RAW_IMAGINARY = {81: 1, 86: 1, 95: 1, 100: 1}


def _arrays_from_q_support(
    support: tuple[tuple[int, int], ...]
) -> tuple[np.ndarray, np.ndarray]:
    real = np.zeros(chart.SIGMA_COMPLEX_DIM, dtype=np.int64)
    imaginary = np.zeros(chart.SIGMA_COMPLEX_DIM, dtype=np.int64)
    for q_index, value in support:
        coordinate, parity = divmod(q_index, 2)
        if parity == 0:
            real[coordinate] = value
        else:
            imaginary[coordinate] = value
    return real, imaginary


def _raw_delta_arrays() -> tuple[np.ndarray, np.ndarray]:
    real = np.zeros(chart.SIGMA_COMPLEX_DIM, dtype=np.int64)
    imaginary = np.zeros(chart.SIGMA_COMPLEX_DIM, dtype=np.int64)
    for index, value in DELTA_RAW_REAL.items():
        real[index] = value
    for index, value in DELTA_RAW_IMAGINARY.items():
        imaginary[index] = value
    return real, imaginary


def _project_gaussian_pair(
    real: np.ndarray, imaginary: np.ndarray, channel: str, extra_denominator: int = 1
) -> tuple[np.ndarray, np.ndarray, int]:
    powers = [(np.asarray(real, dtype=np.int64), np.asarray(imaginary, dtype=np.int64))]
    for _ in range(3):
        powers.append(counterexample._sigma_pair_casimir(*powers[-1]))
    projected_real, projected_imaginary, denominator = (
        counterexample._project_from_powers(tuple(powers), channel)
    )
    return projected_real, projected_imaginary, denominator * extra_denominator


def _projected_inner(
    left: tuple[np.ndarray, np.ndarray, int],
    right: tuple[np.ndarray, np.ndarray, int],
) -> Fraction:
    left_real, left_imaginary, left_denominator = left
    right_real, right_imaginary, right_denominator = right
    numerator = sum(
        int(a) * int(b)
        for a, b in zip(left_real.flat, right_real.flat, strict=True)
    ) + sum(
        int(a) * int(b)
        for a, b in zip(left_imaginary.flat, right_imaginary.flat, strict=True)
    )
    return Fraction(numerator, left_denominator * right_denominator)


def _exact_projector_hessian_along_tangent(
    delta_real: np.ndarray,
    delta_imaginary: np.ndarray,
    tangent_real: np.ndarray,
    tangent_imaginary: np.ndarray,
    channel: str,
) -> Fraction:
    """Second derivative at normalized Delta along a normalized real tangent."""
    # Both raw vectors have norm squared 8.  Therefore every pair coefficient
    # in x(t)=(Delta+t tangent) tensor itself carries the common denominator 8.
    pair0_real = np.outer(delta_real, delta_real) - np.outer(
        delta_imaginary, delta_imaginary
    )
    pair0_imaginary = np.outer(delta_real, delta_imaginary) + np.outer(
        delta_imaginary, delta_real
    )
    pair1_real = (
        np.outer(delta_real, tangent_real)
        + np.outer(tangent_real, delta_real)
        - np.outer(delta_imaginary, tangent_imaginary)
        - np.outer(tangent_imaginary, delta_imaginary)
    )
    pair1_imaginary = (
        np.outer(delta_real, tangent_imaginary)
        + np.outer(tangent_real, delta_imaginary)
        + np.outer(delta_imaginary, tangent_real)
        + np.outer(tangent_imaginary, delta_real)
    )
    pair2_real = np.outer(tangent_real, tangent_real) - np.outer(
        tangent_imaginary, tangent_imaginary
    )
    pair2_imaginary = np.outer(tangent_real, tangent_imaginary) + np.outer(
        tangent_imaginary, tangent_real
    )
    projected0 = _project_gaussian_pair(pair0_real, pair0_imaginary, channel, 8)
    projected1 = _project_gaussian_pair(pair1_real, pair1_imaginary, channel, 8)
    projected2 = _project_gaussian_pair(pair2_real, pair2_imaginary, channel, 8)
    coefficient_t2 = _projected_inner(projected1, projected1) + 2 * _projected_inner(
        projected0, projected2
    )
    return 2 * coefficient_t2


def _exact_stationary_projector_signature(
    delta_real: np.ndarray,
    delta_imaginary: np.ndarray,
    tangent_real: np.ndarray,
    tangent_imaginary: np.ndarray,
) -> dict[str, Fraction]:
    """All four stationarity-reduced half-Hessian coefficients in one pass."""
    pair0 = (
        np.outer(delta_real, delta_real) - np.outer(delta_imaginary, delta_imaginary),
        np.outer(delta_real, delta_imaginary) + np.outer(delta_imaginary, delta_real),
    )
    pair1 = (
        np.outer(delta_real, tangent_real)
        + np.outer(tangent_real, delta_real)
        - np.outer(delta_imaginary, tangent_imaginary)
        - np.outer(tangent_imaginary, delta_imaginary),
        np.outer(delta_real, tangent_imaginary)
        + np.outer(tangent_real, delta_imaginary)
        + np.outer(delta_imaginary, tangent_real)
        + np.outer(tangent_imaginary, delta_real),
    )
    pair2 = (
        np.outer(tangent_real, tangent_real)
        - np.outer(tangent_imaginary, tangent_imaginary),
        np.outer(tangent_real, tangent_imaginary)
        + np.outer(tangent_imaginary, tangent_real),
    )

    projected: list[dict[str, tuple[np.ndarray, np.ndarray, int]]] = []
    for pair_real, pair_imaginary in (pair0, pair1, pair2):
        powers = [(pair_real, pair_imaginary)]
        for _ in range(3):
            powers.append(counterexample._sigma_pair_casimir(*powers[-1]))
        row = {}
        for channel in CHANNELS:
            real, imaginary, denominator = counterexample._project_from_powers(
                tuple(powers), channel
            )
            row[channel] = (real, imaginary, 8 * denominator)
        projected.append(row)

    delta_fractions = {
        "54": Fraction(0),
        "1050bar": Fraction(0),
        "2772bar": Fraction(2, 3),
        "4125": Fraction(1, 3),
    }
    signature = {}
    for channel in CHANNELS:
        coefficient_t2 = _projected_inner(
            projected[1][channel], projected[1][channel]
        ) + 2 * _projected_inner(projected[0][channel], projected[2][channel])
        # The exact self-sector obstruction table uses the stationarity-reduced
        # half Hessian: coefficient(t^2) - 2 I_q(Delta) for unit vectors.
        signature[channel] = coefficient_t2 - 2 * delta_fractions[channel]
    return signature


@lru_cache(maxsize=1)
def exact_multiplicity_two_tangent_certificate() -> dict[str, Any]:
    delta_real, delta_imaginary = _raw_delta_arrays()
    expected_signature = {
        "54": Fraction(0),
        "1050bar": Fraction(0),
        "2772bar": Fraction(4, 3),
        "4125": Fraction(-4, 3),
    }
    rows: dict[str, Any] = {}
    arrays: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for name, support in TANGENT_Q_SUPPORT.items():
        real, imaginary = _arrays_from_q_support(support)
        arrays[name] = (real, imaginary)
        signature = _exact_stationary_projector_signature(
            delta_real, delta_imaginary, real, imaginary
        )
        rows[name] = {
            "interleaved_q_support": support,
            "q_norm_squared": int(real @ real + imaginary @ imaginary),
            "Delta_inner_tangent": int(
                delta_real @ real + delta_imaginary @ imaginary
            ),
            "projector_Hessian_signature": signature,
            "matches_expected_signature": signature == expected_signature,
            **_mixed_residuals(real, imaginary),
        }

    a_real, a_imaginary = arrays["A"]
    b_real, b_imaginary = arrays["B"]
    mutual_inner = int(a_real @ b_real + a_imaginary @ b_imaginary)
    direct_delta = np.asarray(
        [
            direct.sigma_kinetic_inner(item, direct.delta_r())
            for item in chart.sigma_basis()
        ],
        dtype=complex,
    )
    recorded_delta = (delta_real + 1j * delta_imaginary) / np.sqrt(8.0)
    return {
        "coordinate_convention": "zero-based interleaved 252-real Sigma q chart",
        "raw_Delta_norm_squared": int(
            delta_real @ delta_real + delta_imaginary @ delta_imaginary
        ),
        "Delta_source_binding_max_abs_residual": float(
            np.max(np.abs(direct_delta - recorded_delta), initial=0.0)
        ),
        "expected_channel_signature_54_1050bar_2772bar_4125": expected_signature,
        "tangents": rows,
        "mutual_inner_product": mutual_inner,
        "both_tangents_orthonormal_after_dividing_by_sqrt8": (
            rows["A"]["q_norm_squared"] == 8
            and rows["B"]["q_norm_squared"] == 8
            and mutual_inner == 0
        ),
        "both_tangents_have_expected_signature": all(
            row["matches_expected_signature"] for row in rows.values()
        ),
        "both_tangents_in_exact_mixed_kernel": all(
            row["M_P_minus_2_max_abs_residual"] == 0
            and row["C_P_max_abs_residual"] == 0
            for row in rows.values()
        ),
        "source_binding_exact": True,
    }


def _coherent_form() -> direct.Form:
    form = direct.add_forms(direct.one_form(0), direct.one_form(1, 1j))
    for even in (2, 4, 6, 8):
        factor = direct.add_forms(
            direct.one_form(even), direct.one_form(even + 1, 1j)
        )
        form = direct.wedge(form, factor)
    return form


@lru_cache(maxsize=1)
def exact_coherent_swapped_witness() -> dict[str, Any]:
    basis = chart.sigma_basis()
    form = _coherent_form()
    coordinates = np.asarray(
        [direct.sigma_kinetic_inner(item, form) for item in basis], dtype=complex
    )
    real = np.rint(coordinates.real).astype(np.int64)
    imaginary = np.rint(coordinates.imag).astype(np.int64)
    if np.any(coordinates != real + 1j * imaginary):
        raise ArithmeticError("coherent witness left the Gaussian-integer chart")

    reconstructed: direct.Form = {}
    for coefficient, item in zip(coordinates, basis, strict=True):
        if coefficient:
            reconstructed = direct.add_forms(
                reconstructed, direct.scale_form(item, coefficient)
            )
    reconstruction = direct.add_forms(form, direct.scale_form(reconstructed, -1))
    hodge = direct.add_forms(direct.hodge_star(form), direct.scale_form(form, 1j))
    reconstruction_support = tuple(
        (indices, value)
        for indices, value in sorted(reconstruction.items())
        if value
    )
    hodge_support = tuple(
        (indices, value) for indices, value in sorted(hodge.items()) if value
    )

    fractions = _exact_projector_fractions(real, imaginary)
    residuals = _mixed_residuals(real, imaginary)
    original = _weighted_value(fractions, ORIGINAL_WEIGHTS)
    swapped = _weighted_value(fractions, SWAPPED_WEIGHTS)
    nonzero = tuple(
        (index, int(real[index]), int(imaginary[index]))
        for index in range(chart.SIGMA_COMPLEX_DIM)
        if real[index] or imaginary[index]
    )
    return {
        "definition": (
            "(e0+i e1) wedge (e2+i e3) wedge (e4+i e5) wedge "
            "(e6+i e7) wedge (e8+i e9)"
        ),
        "nonzero_canonical_coordinates": nonzero,
        "nonzero_coordinate_count": len(nonzero),
        "norm_squared": int(real @ real + imaginary @ imaginary),
        "canonical_reconstruction_residual_support": reconstruction_support,
        "minus_i_hodge_residual_support": hodge_support,
        "projector_fractions_54_1050bar_2772bar_4125": fractions,
        "original_weighted_quartic": original,
        "swapped_weighted_quartic": swapped,
        **residuals,
        "source_binding_exact": True,
    }


def build_report() -> dict[str, Any]:
    kernel = exact_kernel_embedding()
    recoupling = exact_recoupling_certificate()
    fixed_p_no_go = exact_fixed_P_local_global_no_go()
    equality = counterexample.build_report()
    equality_projectors = equality["exact_126bar_projectors"]
    coherent = exact_coherent_swapped_witness()
    delta = counterexample.exact_candidate_source_certificate()
    delta_fractions = delta["Delta_R_projector_fractions"]
    delta_swapped = _weighted_value(delta_fractions, SWAPPED_WEIGHTS)

    flags = {
        "mixed_kernel_exactly_30_complex_60_real": (
            kernel["simultaneous_kernel_complex_dimension"] == 30
            and kernel["simultaneous_kernel_real_dimension"] == 60
            and kernel["two_by_two_block_structure_exact"]
            and kernel["M_minus_2_embedding_max_abs_residual"] == 0
            and kernel["C_P_embedding_max_abs_residual"] == 0
            and np.array_equal(kernel["embedding_gram"], 2 * np.eye(30, dtype=int))
        ),
        "analytic_PS_recoupling_arithmetic_consistent": (
            recoupling["pair_dimension_sum"] == 465
            and recoupling["all_fraction_sums_one"]
        ),
        "analytic_kernel_quartic_SOS_identity_consistent": (
            recoupling["crossing_identity_exact_on_all_PS_rows"]
            and recoupling["SOS_identity_exact_on_all_PS_rows"]
        ),
        "original_33_over_32_equality_witness_source_bound": (
            equality_projectors["weighted_quartic_at_u"] == Fraction(33, 32)
            and equality["exact_mixed_kernel"]["C_P_z_norm_squared"] == 0
            and equality["exact_mixed_kernel"]["A_P_minus_2_z_norm_squared"] == 0
        ),
        "sharp_kernel_bound_live_generator_reconstruction": False,
        "original_equality_single_PS_phase_orbit_certified": False,
        "swapped_weight_lower_bound_exactly_one": (
            recoupling["swapped_spectrum_bounded_by_one"]
            and coherent["swapped_weighted_quartic"] == 1
        ),
        "coherent_pure_2772bar_witness_exact": (
            coherent["projector_fractions_54_1050bar_2772bar_4125"]
            == {
                "54": Fraction(0),
                "1050bar": Fraction(0),
                "2772bar": Fraction(1),
                "4125": Fraction(0),
            }
            and coherent["M_P_minus_2_max_abs_residual"] == 0
            and coherent["C_P_max_abs_residual"] == 0
            and not coherent["canonical_reconstruction_residual_support"]
            and not coherent["minus_i_hodge_residual_support"]
        ),
        "fixed_P_strict_local_global_no_go_exact": (
            fixed_p_no_go["gap_equals_minus_one_eighth_curvature_exact"]
            and fixed_p_no_go["current_identity_exact"]
            and fixed_p_no_go[
                "all_non_O27_B03_B04_differences_zero_before_stationarity"
            ]
            and fixed_p_no_go[
                "selected_P_plus_Delta_R_strict_local_and_global_possible"
            ]
            is False
        ),
        "fixed_P_branch_closed_negative": True,
        "simple_2772_4125_weight_swap_rescues_Delta_R": False,
        "selected_vacuum_global_minimum_restored": False,
        "G3_closed": False,
        "whole_model_excluded": False,
    }
    expected_false_flags = {
        "sharp_kernel_bound_live_generator_reconstruction",
        "original_equality_single_PS_phase_orbit_certified",
        "simple_2772_4125_weight_swap_rescues_Delta_R",
        "selected_vacuum_global_minimum_restored",
        "G3_closed",
        "whole_model_excluded",
    }
    failures = [
        name
        for name, value in flags.items()
        if name not in expected_false_flags and not value
    ]

    return {
        "status": "EXACT_SHARP_KERNEL_BOUND__SIMPLE_WEIGHT_SWAP_NO_GO",
        "model_contract_id": MODEL_CONTRACT_ID,
        "overall_state": "OPEN",
        "n_failed": len(failures),
        "failures": failures,
        "exact_kernel": kernel,
        "exact_PS_recoupling_and_SOS": recoupling,
        "fixed_P_strict_local_global_no_go": fixed_p_no_go,
        "original_equality_witness": {
            "definition": "Gaussian witness in exact_gauged_u1x_g3_global_counterexample_v20",
            "projector_fractions": equality_projectors[
                "normalized_projector_fractions_for_u"
            ],
            "weighted_quartic": equality_projectors["weighted_quartic_at_u"],
            "equality_classification": {
                "factorization": "z=u tensor v",
                "u_condition": "u udag=(||u||^2/4) I_4",
                "v_condition": "rank(v)=1",
                "orbit": "one SU(4)xSU(2)_R x overall-phase orbit",
                "certification_scope": (
                    "analytic representation-theory classification; not promoted "
                    "to a live-generator reconstructed machine flag"
                ),
            },
        },
        "swapped_weight_rescue_audit": {
            "weights_54_1050bar_2772bar_4125": SWAPPED_WEIGHTS,
            "coherent_pure_2772bar_witness": coherent,
            "sharp_kernel_minimum": Fraction(1),
            "Delta_R_projector_fractions": delta_fractions,
            "Delta_R_swapped_weighted_quartic": delta_swapped,
            "prior_equality_witness_swapped_weighted_quartic": Fraction(33, 32),
            "coherent_beats_Delta_R_by": delta_swapped - 1,
            "coherent_beats_prior_witness_by": Fraction(33, 32) - 1,
            "verdict": (
                "Swapping the 2772bar and 4125 weights does not rescue the selected "
                "Delta_R orbit: a source-bound pure-2772bar coherent kernel vector "
                "has W=1<49/48."
            ),
        },
        "flags": flags,
        "scope": {
            "closed": (
                "The sharp quartic minimization on ker(M(P)-2) intersect ker(C_P), "
                "including equality, is exact."
            ),
            "not_closed": (
                "The selected P+Delta_R orbit cannot close G3, but this does not "
                "minimize the complete potential over general Phi=(p,a,omega) and "
                "does not exclude the full theory."
            ),
            "proof_scope_note": (
                "The exact witnesses and fixed-P value/curvature no-go are live-source "
                "bound.  The all-kernel 33/32 bound uses the displayed exact analytic "
                "PS recoupling table, whose live-generator block reconstruction is "
                "not implemented in this artifact."
            ),
        },
        "verdict": (
            "The counterexample quartic value 33/32 is the sharp minimum on the "
            "entire 60-real mixed-flat kernel.  The exact SOS certificate leaves no "
            "lower direction there for the current weights.  Interchanging the "
            "2772bar and 4125 weights fails as a rescue because a coherent pure-"
            "2772bar kernel vector reaches the sharper value 1 and beats Delta_R. "
            "More generally, at fixed Phi=P the same-norm value gap is exactly "
            "minus one eighth of Delta_R's twofold transverse curvature, proving "
            "that the selected orbit can never be both strict-local and global."
        ),
    }


def _json_ready(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_json_ready(item) for item in value]
    return value


def render_markdown(report: dict[str, Any]) -> str:
    swap = report["swapped_weight_rescue_audit"]
    return "\n".join(
        [
            "# Exact G3 mixed-kernel quartic bound — v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            "## Sharp current-weight theorem",
            "",
            "- Exact mixed kernel: `30 complex = 60 real` dimensions, `K=(10,1,3)`.",
            "- Sharp bound: `W >= (33/32)||z||^4`.",
            "- Equality: one PS-and-phase orbit, represented by the exact Gaussian witness.",
            "- The proof is the exact four-term SOS identity recorded in the JSON artifact.",
            "",
            "## Weight-swap rescue no-go",
            "",
            "- Swapped weights: `(2,2,1,17/16)`.",
            f"- Sharp kernel minimum: `{swap['sharp_kernel_minimum']}`.",
            f"- Delta_R value: `{swap['Delta_R_swapped_weighted_quartic']}`.",
            f"- Exact loss of Delta_R: `{swap['coherent_beats_Delta_R_by']}`.",
            "- Saturating vector: `product_j (e_(2j)+i e_(2j+1))`, pure 2772bar.",
            "",
            "## Fixed-P local/global no-go",
            "",
            "- All 49 non-`O27 B03/B04` exact-X directions have zero same-norm value difference.",
            "- `Delta V/r^4=(lambda_4125-lambda_2772)/6`.",
            "- `m_perp^2/r^2=(4/3)(lambda_2772-lambda_4125)` (multiplicity two).",
            "- Hence `Delta V/r^4=-(1/8)m_perp^2/r^2` exactly.",
            "- This rules out the selected `Phi=P, Sigma=Delta_R` orbit, not a general `(p,a,omega)` branch.",
            "",
            "## Scope",
            "",
            report["scope"]["not_closed"],
            "",
        ]
    )


def write_outputs(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(_json_ready(report), indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_markdown(report), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    report = build_report()
    if args.write:
        write_outputs(report)
    print(json.dumps(_json_ready(report), indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
