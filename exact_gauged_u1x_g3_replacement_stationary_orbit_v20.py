#!/usr/bin/env python3
"""Exact replacement-orbit stationarity and symmetry certificate for G3.

The exact global counterexample to the original ``Delta_R`` candidate uses a
Gaussian-integer vector ``z`` in the canonical physical 126bar chart.  This
module asks the next logically distinct question: after optimizing its norm,
is that lower-energy ray itself a stationary orbit, and is it locally stable?

The proof-grade part establishes, directly from the live source tensors,

* ``grad W(z) = 33 z`` in all 126 complex (252 real) coordinates;
* at ``Sigma=(5 r/(3 sqrt(22))) z`` the self and radial gradients cancel;
* ``(A_P-2)z=0`` and ``C_P z=0``, so every mixed-square first derivative
  vanishes in both the 210 and 126bar blocks;
* the unchanged P/H/S/Phi17 square factors remain at their zero loci; and
* exact orbit ranks are 39 for SO(10), 40 after gauged U(1)_X, and 41 after
  independent global PQ.  The physical quotient therefore has dimension 445.

The Hessian classification is deliberately kept separate.  A live 486-field
compiler recomputation at the well-conditioned representative h=r=x=1 finds
all 445 transverse eigenvalues positive.  That is strong numerical evidence,
not an exact Q(sqrt(22)) LDL certificate.  Consequently neither a proof-grade
strict-local-minimum claim nor global minimality/G3 closure is made here.
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
import exact_gauged_u1x_g3_global_counterexample_v20 as counterexample
import exact_gauged_u1x_g3_sos_bfb_stationarity_v20 as sos_source
import exact_gauged_u1x_physical_quotient_v20 as quotient_source
import gauged_u1x_g2_derivative_audit_v20 as g2_audit
import gauged_u1x_g3_sos_candidate_v20 as candidate_source
import live_g2_arbitrary_component_potential_values_v20 as potential
import live_g2_canonical_486_field_chart_v20 as chart

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_GAUGED_U1X_G3_REPLACEMENT_STATIONARY_ORBIT_V20.json"
OUT_MD = ROOT / "EXACT_GAUGED_U1X_G3_REPLACEMENT_STATIONARY_ORBIT_V20.md"

MODEL_CONTRACT_ID = "gauged_u1x_phi17_v20"
RAW_GRADIENT_EIGENVALUE = Fraction(33)
SIGMA_DIRECTION_SCALE_SQUARED_OVER_R2 = Fraction(25, 198)
SIGMA_NORM_SQUARED_OVER_R2 = Fraction(100, 99)
RADIAL_COEFFICIENT = Fraction(25, 12)
EXPECTED_SO10_RANK = 39
EXPECTED_GAUGE_RANK = 40
EXPECTED_FULL_SYMMETRY_RANK = 41
EXPECTED_QUOTIENT_DIMENSION = chart.TOTAL_DIM - EXPECTED_FULL_SYMMETRY_RANK
TARGET_SELECTED_GAUGE_ORBIT_RANK = 37

# Zero-based indices in the interleaved 252-real canonical Sigma chart.
# Each list defines an integer vector of norm squared eight.
DELTA_OBSTRUCTION_TANGENTS = {
    "A": ((153, 1), (159, -1), (164, -1), (170, 1),
          (192, -1), (198, 1), (205, -1), (211, 1)),
    "B": ((155, 1), (157, 1), (166, -1), (168, -1),
          (194, -1), (196, -1), (207, -1), (209, -1)),
}

# Frozen only as a reproducibility record.  ``--recompute-heavy`` rebuilds
# these values from all 27 nonzero parameter rows in the live compiler.
RECORDED_UNIT_SCALE_HESSIAN = {
    "evidence_kind": "live_486_field_compiler_float64_unit_scale_representative",
    "recomputed_in_this_invocation": False,
    "proof_grade": False,
    "h_equals_r_equals_x": 1.0,
    "full_gradient_max_abs_residual": 3.870681553053146e-12,
    "full_gradient_norm": 3.871610988938769e-12,
    "numerical_symmetry_orbit_rank": 41,
    "orbit_smallest_nonzero_singular_value": 0.7672854808611275,
    "orbit_largest_null_singular_value": 1.8102423882161914e-15,
    "stationary_Hessian_symmetry_max_abs_residual": 1.2198020371556595e-12,
    "transverse_dimension": 445,
    "minimum_transverse_eigenvalue": 0.005260942760879879,
    "maximum_transverse_eigenvalue": 9.010101010104878,
    "negative_transverse_eigenvalues_below_minus_1e_minus_10": 0,
    "zero_transverse_eigenvalues_at_1e_minus_10": 0,
    "P_plus_Sigma": {
        "SO10_orbit_rank": 36,
        "transverse_dimension": 426,
        "minimum_transverse_eigenvalue": 0.00526094276087761,
        "negative_eigenvalues_below_minus_1e_minus_10": 0,
        "zero_eigenvalues_at_1e_minus_10": 0,
    },
    "strict_local_minimum_high_confidence_numeric": True,
    "strict_local_minimum_proof_grade": False,
    "limitation": (
        "Unit-scale float64 inertia is well conditioned, but an exact direct "
        "Q(sqrt(22)) source assembly/LDL certificate has not been completed."
    ),
}


def _projected_witness_pairs() -> dict[str, tuple[np.ndarray, np.ndarray, int]]:
    real, imaginary = counterexample._witness_arrays()
    pair_real = np.outer(real, real) - np.outer(imaginary, imaginary)
    pair_imaginary = np.outer(real, imaginary) + np.outer(imaginary, real)
    powers = [(pair_real, pair_imaginary)]
    for _ in range(3):
        powers.append(counterexample._sigma_pair_casimir(*powers[-1]))
    return {
        channel: counterexample._project_from_powers(tuple(powers), channel)
        for channel in counterexample.PROJECTOR_CHANNELS
    }


@lru_cache(maxsize=1)
def exact_sigma_stationarity_certificate() -> dict[str, Any]:
    """Certify the complete 252-real Sigma first derivative exactly."""
    z_real, z_imaginary = counterexample._witness_arrays()
    projected = _projected_witness_pairs()
    gradient_real = [Fraction(0) for _ in range(chart.SIGMA_COMPLEX_DIM)]
    gradient_imaginary = [Fraction(0) for _ in range(chart.SIGMA_COMPLEX_DIM)]
    for channel, weight in counterexample.SIGMA_SELF_WEIGHTS.items():
        matrix_real, matrix_imaginary, denominator = projected[channel]
        for index in range(chart.SIGMA_COMPLEX_DIM):
            scalar_real = Fraction(
                int(
                    matrix_real[:, index] @ z_real
                    + matrix_imaginary[:, index] @ z_imaginary
                ),
                denominator,
            )
            scalar_imaginary = Fraction(
                int(
                    matrix_real[:, index] @ z_imaginary
                    - matrix_imaginary[:, index] @ z_real
                ),
                denominator,
            )
            gradient_real[index] += 4 * weight * scalar_real
            gradient_imaginary[index] -= 4 * weight * scalar_imaginary

    residual_real = tuple(
        gradient_real[index] - RAW_GRADIENT_EIGENVALUE * int(z_real[index])
        for index in range(chart.SIGMA_COMPLEX_DIM)
    )
    residual_imaginary = tuple(
        gradient_imaginary[index]
        - RAW_GRADIENT_EIGENVALUE * int(z_imaginary[index])
        for index in range(chart.SIGMA_COMPLEX_DIM)
    )
    raw_norm_squared = int(z_real @ z_real + z_imaginary @ z_imaginary)
    raw_weighted_quartic = (
        counterexample.EXPECTED_WITNESS_WEIGHTED_QUARTIC
        * raw_norm_squared**2
    )
    scaled_gradient_coefficient = (
        SIGMA_DIRECTION_SCALE_SQUARED_OVER_R2 * RAW_GRADIENT_EIGENVALUE
    )
    radial_gradient_coefficient = 2 * RADIAL_COEFFICIENT
    return {
        "raw_vector": "z in the canonical physical -i-Hodge 126bar chart",
        "raw_norm_squared": raw_norm_squared,
        "raw_weighted_quartic": raw_weighted_quartic,
        "exact_gradient_identity": "grad W(z)=33 z",
        "gradient_eigenvalue": RAW_GRADIENT_EIGENVALUE,
        "nonzero_raw_gradient_coordinates": sum(
            bool(value) for value in gradient_real + gradient_imaginary
        ),
        "gradient_identity_residual_real": residual_real,
        "gradient_identity_residual_imaginary": residual_imaginary,
        "maximum_gradient_identity_residual": max(
            map(abs, residual_real + residual_imaginary), default=Fraction(0)
        ),
        "replacement_field": "Sigma=(5 r/(3 sqrt(22))) z",
        "direction_scale_squared_over_r2": SIGMA_DIRECTION_SCALE_SQUARED_OVER_R2,
        "Sigma_norm_squared_over_r2": SIGMA_NORM_SQUARED_OVER_R2,
        "scaled_self_gradient_coefficient_over_r2": scaled_gradient_coefficient,
        "radial_mass_gradient_coefficient_over_r2": radial_gradient_coefficient,
        "full_252_real_gradient_cancellation": (
            scaled_gradient_coefficient == radial_gradient_coefficient
            and not any(residual_real + residual_imaginary)
        ),
        "source_binding_exact": True,
    }


def exact_full_stationarity_certificate() -> dict[str, Any]:
    sigma = exact_sigma_stationarity_certificate()
    mixed = counterexample.exact_mixed_kernel_certificate()
    parameters = counterexample.exact_candidate_source_certificate()
    phi = sos_source.exact_phi_certificate()
    elementary = sos_source.exact_elementary_certificate()
    mixed_zero = (
        mixed["C_P_z_norm_squared"] == 0
        and mixed["A_P_minus_2_z_norm_squared"] == 0
    )
    complete_map = (
        parameters["model_contract_id"] == MODEL_CONTRACT_ID
        and parameters["nonzero_parameter_count"] == 27
        and parameters["expanded_map_equals_declared_map"]
    )
    proof_complete = bool(
        sigma["full_252_real_gradient_cancellation"]
        and mixed_zero
        and complete_map
        and phi["P_stationary_from_vanishing_square_gradients"]
        and elementary["expanded_coefficients_equal_declared_27"]
        and all(value == "0" for value in elementary["selected_square_values"].values())
    )
    return {
        "model_contract_id": MODEL_CONTRACT_ID,
        "complete_nonzero_parameter_count": parameters["nonzero_parameter_count"],
        "complete_27_parameter_map_source_bound": complete_map,
        "Sigma_252_real_coordinates": sigma,
        "mixed_square_zero_locus": {
            "A_P_minus_2_z_norm_squared": mixed[
                "A_P_minus_2_z_norm_squared"
            ],
            "C_P_z_norm_squared": mixed["C_P_z_norm_squared"],
            "all_Phi_and_Sigma_mixed_square_gradients_zero": mixed_zero,
            "source_binding_exact": mixed["source_binding_exact"],
        },
        "P_210_stationarity": phi["P_stationary_from_vanishing_square_gradients"],
        "H_S_Phi17_zero_square_values": elementary["selected_square_values"],
        "replacement_changes_only_Sigma": True,
        "full_486_gradient_exactly_zero": proof_complete,
        "source_binding_exact": proof_complete,
    }


def _tangent_complex_arrays(
    support: tuple[tuple[int, int], ...],
) -> tuple[np.ndarray, np.ndarray]:
    real = np.zeros(chart.SIGMA_COMPLEX_DIM, dtype=np.int64)
    imaginary = np.zeros(chart.SIGMA_COMPLEX_DIM, dtype=np.int64)
    for coordinate, sign in support:
        target = real if coordinate % 2 == 0 else imaginary
        target[coordinate // 2] = sign
    return real, imaginary


def _holomorphic_pair(
    left_real: np.ndarray,
    left_imaginary: np.ndarray,
    right_real: np.ndarray,
    right_imaginary: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    return (
        np.outer(left_real, right_real)
        - np.outer(left_imaginary, right_imaginary),
        np.outer(left_real, right_imaginary)
        + np.outer(left_imaginary, right_real),
    )


def _project_sigma_pair(
    pair: tuple[np.ndarray, np.ndarray], channel: str
) -> tuple[np.ndarray, np.ndarray, int]:
    powers = [pair]
    for _ in range(3):
        powers.append(counterexample._sigma_pair_casimir(*powers[-1]))
    return counterexample._project_from_powers(tuple(powers), channel)


def _scaled_projector_inner(
    left: tuple[np.ndarray, np.ndarray, int],
    right: tuple[np.ndarray, np.ndarray, int],
    left_scale: int,
    right_scale: int,
) -> Fraction:
    left_real, left_imaginary, left_denominator = left
    right_real, right_imaginary, right_denominator = right
    numerator = sum(
        int(a) * int(b)
        for a, b in zip(left_real.flat, right_real.flat, strict=True)
    ) + sum(
        int(a) * int(b)
        for a, b in zip(
            left_imaginary.flat, right_imaginary.flat, strict=True
        )
    )
    return Fraction(
        numerator,
        left_denominator
        * right_denominator
        * left_scale
        * right_scale,
    )


@lru_cache(maxsize=1)
def exact_delta_two_tangent_certificate() -> dict[str, Any]:
    """Bind the twofold Delta curvature obstruction to explicit tensors."""
    delta_real, delta_imaginary = sos_source.raw_delta_coordinates()
    p_vector, _ = counterexample._pati_salam_vector()
    contraction_real, contraction_imaginary = (
        counterexample.mixed_source.integer_contraction_tensor()
    )
    operator_real, operator_imaginary = (
        counterexample.mixed_source.integer_cubic_operators()
    )
    matrix_real = np.tensordot(p_vector, operator_real, axes=(0, 0))
    matrix_imaginary = np.tensordot(p_vector, operator_imaginary, axes=(0, 0))
    delta_pair = _holomorphic_pair(
        delta_real, delta_imaginary, delta_real, delta_imaginary
    )

    records: dict[str, Any] = {}
    tangent_arrays: list[tuple[np.ndarray, np.ndarray]] = []
    for name, support in DELTA_OBSTRUCTION_TANGENTS.items():
        tangent_real, tangent_imaginary = _tangent_complex_arrays(support)
        tangent_arrays.append((tangent_real, tangent_imaginary))
        left = _holomorphic_pair(
            delta_real,
            delta_imaginary,
            tangent_real,
            tangent_imaginary,
        )
        right = _holomorphic_pair(
            tangent_real,
            tangent_imaginary,
            delta_real,
            delta_imaginary,
        )
        linear_pair = (left[0] + right[0], left[1] + right[1])
        tangent_pair = _holomorphic_pair(
            tangent_real,
            tangent_imaginary,
            tangent_real,
            tangent_imaginary,
        )
        q_norm_squared = int(
            tangent_real @ tangent_real
            + tangent_imaginary @ tangent_imaginary
        )
        signatures: dict[str, Fraction] = {}
        for channel in counterexample.PROJECTOR_CHANNELS:
            projected_delta = _project_sigma_pair(delta_pair, channel)
            projected_linear = _project_sigma_pair(linear_pair, channel)
            projected_tangent = _project_sigma_pair(tangent_pair, channel)
            invariant_at_delta = _scaled_projector_inner(
                projected_delta, projected_delta, 8, 8
            )
            second_derivative = 2 * _scaled_projector_inner(
                projected_linear, projected_linear, 4, 4
            ) + 4 * _scaled_projector_inner(
                projected_delta, projected_tangent, 8, 2
            )
            signatures[channel] = (
                second_derivative
                - 2 * invariant_at_delta * q_norm_squared
            ) / q_norm_squared

        c_real = (
            np.einsum(
                "vpa,p,a->v",
                contraction_real,
                p_vector,
                tangent_real,
                optimize=True,
            )
            - np.einsum(
                "vpa,p,a->v",
                contraction_imaginary,
                p_vector,
                tangent_imaginary,
                optimize=True,
            )
        )
        c_imaginary = (
            np.einsum(
                "vpa,p,a->v",
                contraction_real,
                p_vector,
                tangent_imaginary,
                optimize=True,
            )
            + np.einsum(
                "vpa,p,a->v",
                contraction_imaginary,
                p_vector,
                tangent_real,
                optimize=True,
            )
        )
        a_real = (
            matrix_real @ tangent_real
            - matrix_imaginary @ tangent_imaginary
            - 2 * tangent_real
        )
        a_imaginary = (
            matrix_real @ tangent_imaginary
            + matrix_imaginary @ tangent_real
            - 2 * tangent_imaginary
        )
        records[name] = {
            "canonical_interleaved_support": support,
            "q_norm_squared": q_norm_squared,
            "channel_Hessian_signatures": signatures,
            "A_P_minus_2_tangent_norm_squared": int(
                a_real @ a_real + a_imaginary @ a_imaginary
            ),
            "C_P_tangent_norm_squared": int(
                c_real @ c_real + c_imaginary @ c_imaginary
            ),
        }

    tangent_inner = int(
        tangent_arrays[0][0] @ tangent_arrays[1][0]
        + tangent_arrays[0][1] @ tangent_arrays[1][1]
    )
    expected_signature = {
        "54": Fraction(0),
        "1050bar": Fraction(0),
        "2772bar": Fraction(4, 3),
        "4125": Fraction(-4, 3),
    }

    # Prove that both directions add rank beyond the P+Delta gauge orbit.
    delta_state = potential.FieldState(
        phi=direct.singlet_basis()["p"],
        h=np.zeros(chart.H_COMPLEX_DIM, dtype=complex),
        sigma=chart.sigma_from_coordinates(delta_real + 1j * delta_imaginary),
        s=0j,
        x=0j,
    ).validated()
    gauge = chart.gauge_orbit_matrix(delta_state)
    gauge[chart.SIGMA_SLICE, :] /= chart.SQRT2
    gauge_integer = np.rint(gauge).astype(np.int64)
    embedded = np.zeros((chart.TOTAL_DIM, 2), dtype=np.int64)
    for column, support in enumerate(DELTA_OBSTRUCTION_TANGENTS.values()):
        for coordinate, sign in support:
            embedded[chart.SIGMA_SLICE.start + coordinate, column] = sign
    gauge_rank = _exact_rank(gauge_integer)[0]
    extended_rank = _exact_rank(np.column_stack((gauge_integer, embedded)))[0]
    certified = bool(
        tangent_inner == 0
        and gauge_rank == 33
        and extended_rank == 35
        and all(
            record["channel_Hessian_signatures"] == expected_signature
            and record["A_P_minus_2_tangent_norm_squared"] == 0
            and record["C_P_tangent_norm_squared"] == 0
            for record in records.values()
        )
    )
    return {
        "coordinate_convention": (
            "zero-based interleaved real coordinates inside the 252-real "
            "canonical physical 126bar block"
        ),
        "tangents": records,
        "tangent_inner_product": tangent_inner,
        "common_channel_signature": expected_signature,
        "P_plus_Delta_SO10_gauge_rank": gauge_rank,
        "rank_after_adding_both_tangents": extended_rank,
        "both_tangents_non_gauge": extended_rank - gauge_rank == 2,
        "multiplicity_two_curvature": (
            "m2=(4/3)(lambda_2772bar-lambda_4125)"
        ),
        "source_binding_exact": certified,
    }


@lru_cache(maxsize=1)
def exact_o44_endpoint_values() -> dict[str, Any]:
    """Evaluate all six individual O44 values with integer/Fraction tensors."""
    import exact_gauged_u1x_g3_pd_rank_certificate_v20 as pd_source
    import exact_phisigma_casimir_projectors_v20 as phi_projectors

    p_vector, _ = counterexample._pati_salam_vector()
    initial = np.outer(p_vector, p_vector).reshape(-1, 1)
    casimir = pd_source._phi_pair_casimir_integer()
    powers = [initial]
    for _ in range(7):
        powers.append(np.asarray(casimir @ powers[-1], dtype=np.int64))
    tensor_real, tensor_imaginary = (
        counterexample.mixed_source.integer_contraction_tensor()
    )

    def values(sigma_real: np.ndarray, sigma_imaginary: np.ndarray) -> dict[str, Fraction]:
        image_real = np.einsum(
            "vpa,a->vp", tensor_real, sigma_real, optimize=True
        ) - np.einsum("vpa,a->vp", tensor_imaginary, sigma_imaginary, optimize=True)
        image_imaginary = np.einsum(
            "vpa,a->vp", tensor_real, sigma_imaginary, optimize=True
        ) + np.einsum("vpa,a->vp", tensor_imaginary, sigma_real, optimize=True)
        output: dict[str, Fraction] = {}
        for channel, eigenvalue in phi_projectors.COMMON_CHANNEL_EIGENVALUES.items():
            polynomial = phi_projectors.projector_polynomial(eigenvalue)
            denominator = math.lcm(*(value.denominator for value in polynomial))
            projected = sum(
                (
                    int(coefficient * denominator)
                    * powers[index].reshape(chart.PHI_DIM, chart.PHI_DIM)
                    for index, coefficient in enumerate(polynomial)
                ),
                np.zeros((chart.PHI_DIM, chart.PHI_DIM), dtype=np.int64),
            )
            numerator = int(
                np.einsum(
                    "vi,ij,vj->",
                    image_real,
                    projected,
                    image_real,
                    optimize=True,
                )
                + np.einsum(
                    "vi,ij,vj->",
                    image_imaginary,
                    projected,
                    image_imaginary,
                    optimize=True,
                )
            )
            output[channel] = Fraction(numerator, 8 * denominator)
        return output

    delta_real, delta_imaginary = sos_source.raw_delta_coordinates()
    z_real, z_imaginary = counterexample._witness_arrays()
    delta_values = values(delta_real, delta_imaginary)
    z_values = values(z_real, z_imaginary)
    expected = {
        "1": Fraction(1, 21),
        "45": Fraction(0),
        "210": Fraction(0),
        "770": Fraction(-2, 15),
        "5940": Fraction(0),
        "8910": Fraction(3, 35),
    }
    return {
        "channel_order": tuple(phi_projectors.COMMON_CHANNEL_EIGENVALUES),
        "Delta_R_values": delta_values,
        "z_values": z_values,
        "expected_common_values": expected,
        "all_six_individual_O44_values_equal_exactly": (
            delta_values == z_values == expected
        ),
        "source_binding": (
            "integer 210 pair Casimir, Fraction spectral projectors, and "
            "Gaussian-integer Phi-Sigma contraction tensor"
        ),
        "source_binding_exact": delta_values == z_values == expected,
    }


@lru_cache(maxsize=1)
def exact_fixed_p_gap_curvature_no_go() -> dict[str, Any]:
    tangents = exact_delta_two_tangent_certificate()
    o44 = exact_o44_endpoint_values()
    delta_mixed = sos_source.exact_mixed_certificate()
    z_mixed = counterexample.exact_mixed_kernel_certificate()

    # Raw Gaussian carriers make every support-zero assertion exact; the
    # common normalization is irrelevant for a zero.
    delta_real, delta_imaginary = sos_source.raw_delta_coordinates()
    z_real, z_imaginary = counterexample._witness_arrays()
    h = np.zeros(chart.H_COMPLEX_DIM, dtype=complex)
    h[6] = 1
    raw_states = (
        potential.FieldState(
            phi=direct.singlet_basis()["p"],
            h=h,
            sigma=chart.sigma_from_coordinates(delta_real + 1j * delta_imaginary),
            s=1 + 0j,
            x=1 + 0j,
        ).validated(),
        potential.FieldState(
            phi=direct.singlet_basis()["p"],
            h=h,
            sigma=chart.sigma_from_coordinates(z_real + 1j * z_imaginary),
            s=1 + 0j,
            x=1 + 0j,
        ).validated(),
    )
    raw_values = tuple(
        {row.direction_id: row.value for row in potential.evaluate_directions(state)}
        for state in raw_states
    )
    exact_zero_sigma_h_directions = (
        "O15_B01_Phi_Hdag_Sigma",
        "O28_B01_unique_Hdag_Sigma2_Sigmadag",
        "O31_B01_unique_Hdag2_Sigma2",
        "O35_B02_H_Sigma_hermitian",
        "O38_B01_Phi_Hdag_Sigmadag",
        "O45_B01_Phi2_Hdag_Sigma_210_1050",
        "O45_B02_Phi2_Hdag_Sigma_210_1050",
    )
    support_zero = {
        direction_id: (
            raw_values[0][direction_id] == 0j
            and raw_values[1][direction_id] == 0j
        )
        for direction_id in exact_zero_sigma_h_directions
    }

    selection = g2_audit.contract_selection()
    exact_parameter_differences = {
        parameter_id: Fraction(0) for parameter_id in selection["parameter_ids"]
    }
    exact_parameter_differences[
        "lambda::O27_B03_126bar_self_projectors"
    ] = Fraction(-1, 6)
    exact_parameter_differences[
        "lambda::O27_B04_126bar_self_projectors"
    ] = Fraction(1, 6)
    nonzero = {
        key: value for key, value in exact_parameter_differences.items() if value
    }
    o14_equal = bool(
        delta_mixed["M_P_Delta_minus_2_Delta_max_abs"] == 0
        and z_mixed["A_P_minus_2_z_norm_squared"] == 0
    )
    certified = bool(
        tangents["source_binding_exact"]
        and o44["source_binding_exact"]
        and o14_equal
        and all(support_zero.values())
        and len(exact_parameter_differences) == 51
        and len(nonzero) == 2
    )
    return {
        "scope": "equal unit Sigma norm, Phi=P, identical H/S/Phi17",
        "exact_X_parameter_count": len(exact_parameter_differences),
        "exact_parameter_value_difference_z_minus_Delta": exact_parameter_differences,
        "number_of_exact_zero_parameter_differences": sum(
            value == 0 for value in exact_parameter_differences.values()
        ),
        "number_of_exact_nonzero_parameter_differences": len(nonzero),
        "nonzero_differences": nonzero,
        "O14_values_equal_to_two_exactly": o14_equal,
        "all_six_O44_endpoint_values": o44,
        "Gaussian_support_zero_directions": support_zero,
        "same_norm_gap": (
            "V(z)-V(Delta)=(lambda_4125-lambda_2772bar)/6"
        ),
        "multiplicity_two_curvature": tangents["multiplicity_two_curvature"],
        "gap_equals_minus_one_eighth_curvature": True,
        "three_cases": {
            "m2_positive": "Delta is locally curved upward but z is strictly lower",
            "m2_zero": "Delta has two additional non-gauge flat directions and ties z",
            "m2_negative": "Delta has two tachyonic non-gauge directions",
        },
        "selected_fixed_P_Delta_strict_local_and_global_minimum_possible": False,
        "theorem_scope_warning": (
            "This excludes the fixed Phi=P, Delta_R orbit, not a general "
            "SM-preserving Phi=(p,a,omega) branch."
        ),
        "explicit_two_tangent_source_binding": tangents,
        "source_binding_exact": certified,
    }


def _exact_rank(matrix: np.ndarray) -> tuple[int, tuple[int, ...], tuple[int, ...]]:
    rows = tuple(tuple(int(value) for value in row) for row in matrix)
    return quotient_source._row_echelon_metadata(rows)


@lru_cache(maxsize=1)
def exact_orbit_rank_certificate() -> dict[str, Any]:
    """Compute exact ranks after an invertible field-block row rescaling."""
    z_real, z_imaginary = counterexample._witness_arrays()
    h = np.zeros(chart.H_COMPLEX_DIM, dtype=complex)
    h[6] = 1
    standardized = potential.FieldState(
        phi=direct.singlet_basis()["p"],
        h=h,
        sigma=chart.sigma_from_coordinates(z_real + 1j * z_imaginary),
        s=1 + 0j,
        x=1 + 0j,
    ).validated()
    observed = np.column_stack(
        (
            chart.gauge_orbit_matrix(standardized),
            g2_audit.u1x_tangent(standardized),
            quotient_source._phase_tangent(
                standardized, quotient_source.PQ_CHARGES
            ),
        )
    )
    integer_carrier = observed.copy()
    for block in (
        chart.H_SLICE,
        chart.SIGMA_SLICE,
        chart.S_SLICE,
        chart.X_SLICE,
    ):
        integer_carrier[block, :] /= chart.SQRT2
    rounded = np.rint(integer_carrier).astype(np.int64)
    exact_lattice_residual = float(
        np.max(np.abs(integer_carrier - rounded), initial=0.0)
    )
    if exact_lattice_residual != 0.0:
        raise ArithmeticError("replacement orbit left the exact integer lattice")

    so10_rank, so10_rows, so10_columns = _exact_rank(rounded[:, :45])
    gauge_rank, gauge_rows, gauge_columns = _exact_rank(rounded[:, :46])
    full_rank, full_rows, full_columns = _exact_rank(rounded)
    pd_rows = np.concatenate(
        (
            np.arange(chart.PHI_SLICE.start, chart.PHI_SLICE.stop),
            np.arange(chart.SIGMA_SLICE.start, chart.SIGMA_SLICE.stop),
        )
    )
    pd_rank, pd_pivot_rows, pd_pivot_columns = _exact_rank(
        rounded[pd_rows, :45]
    )
    full_minor = [
        [int(rounded[row, column]) for column in full_columns]
        for row in full_rows
    ]
    full_minor_determinant = quotient_source._bareiss_determinant(full_minor)
    certified = bool(
        exact_lattice_residual == 0
        and pd_rank == 36
        and so10_rank == EXPECTED_SO10_RANK
        and gauge_rank == EXPECTED_GAUGE_RANK
        and full_rank == EXPECTED_FULL_SYMMETRY_RANK
        and full_minor_determinant != 0
    )
    return {
        "method": (
            "exact integer row echelon after invertible nonzero block-row "
            "rescaling of Phi/H/Sigma/S/Phi17"
        ),
        "integer_orbit_matrix_shape": list(rounded.shape),
        "exact_integer_lattice_residual": exact_lattice_residual,
        "P_plus_Sigma_SO10": {
            "rank": pd_rank,
            "right_nullity": 45 - pd_rank,
            "pivot_row_indices_in_PD_chart": list(pd_pivot_rows),
            "pivot_column_indices": list(pd_pivot_columns),
        },
        "SO10": {
            "rank": so10_rank,
            "right_nullity": 45 - so10_rank,
            "pivot_row_indices": list(so10_rows),
            "pivot_column_indices": list(so10_columns),
        },
        "SO10_plus_U1X": {
            "rank": gauge_rank,
            "right_nullity": 46 - gauge_rank,
            "pivot_row_indices": list(gauge_rows),
            "pivot_column_indices": list(gauge_columns),
        },
        "SO10_plus_U1X_plus_PQ": {
            "rank": full_rank,
            "right_nullity": 47 - full_rank,
            "pivot_row_indices": list(full_rows),
            "pivot_column_indices": list(full_columns),
            "nonzero_minor_determinant": str(full_minor_determinant),
        },
        "physical_quotient_dimension": chart.TOTAL_DIM - full_rank,
        "actual_replacement_rank_preserved": (
            "The actual nonzero h,r,x and 5r/(3sqrt(22)) factors differ "
            "only by an invertible diagonal row scaling."
        ),
        "source_binding_exact": certified,
    }


def recompute_live_unit_scale_hessian() -> dict[str, Any]:
    """Rebuild the 486 Hessian through all 27 live compiler parameter rows."""
    import live_g2_exact_quadratic_family_derivatives_v20 as derivatives

    z_real, z_imaginary = counterexample._witness_arrays()
    sigma_scale = 5.0 / (3.0 * math.sqrt(22.0))
    h = np.zeros(chart.H_COMPLEX_DIM, dtype=complex)
    h[6] = 1.0
    state = potential.FieldState(
        phi=direct.singlet_basis()["p"],
        h=h,
        sigma=chart.sigma_from_coordinates(
            sigma_scale * (z_real + 1j * z_imaginary)
        ),
        s=1 + 0j,
        x=1 + 0j,
    ).validated()
    selection = g2_audit.contract_selection()
    selected_ids = set(selection["direction_ids"])
    needed_ids = {
        parameter_id.split("::", 1)[1]
        for parameter_id in candidate_source.symbolic_nonzero_coefficients()
    }
    values = potential.evaluate_directions(state)
    by_id = {row.direction_id: row for row in values}
    owners = g2_audit._adapter_modules_by_family()
    coordinates = chart.pack(state)
    direction_rows = tuple(
        owners[by_id[direction_id].base_family].direction_derivative(
            coordinates, by_id[direction_id]
        )
        for direction_id in sorted(needed_ids)
        if direction_id in selected_ids
    )
    parameter_rows = derivatives.parameter_derivatives(direction_rows)
    by_parameter = {row.parameter_id: row for row in parameter_rows}
    coefficients = candidate_source.full_coefficient_vector(
        {"h": 1.0, "r": 1.0, "x": 1.0}
    )
    nonzero = {key: value for key, value in coefficients.items() if value}
    missing = sorted(set(nonzero).difference(by_parameter))
    if missing:
        raise KeyError(f"replacement Hessian is missing compiler rows: {missing}")

    gradient = np.zeros(chart.TOTAL_DIM, dtype=float)
    hessian = np.zeros((chart.TOTAL_DIM, chart.TOTAL_DIM), dtype=float)
    for parameter_id, coefficient in nonzero.items():
        row = by_parameter[parameter_id]
        gradient += coefficient * np.asarray(row.gradient).real
        hessian += coefficient * np.asarray(row.hessian).real
    hessian = 0.5 * (hessian + hessian.T)

    orbit = np.column_stack(
        (
            chart.gauge_orbit_matrix(state),
            g2_audit.u1x_tangent(state),
            quotient_source._phase_tangent(state, quotient_source.PQ_CHARGES),
        )
    )
    complete, singular_values, _ = np.linalg.svd(orbit, full_matrices=True)
    numerical_rank = int(
        np.sum(singular_values > 1.0e-10 * singular_values[0])
    )
    quotient = complete[:, numerical_rank:]
    transverse = quotient.T @ hessian @ quotient
    transverse = 0.5 * (transverse + transverse.T)
    eigenvalues = np.linalg.eigvalsh(transverse)

    pd_indices = np.concatenate(
        (
            np.arange(chart.PHI_SLICE.start, chart.PHI_SLICE.stop),
            np.arange(chart.SIGMA_SLICE.start, chart.SIGMA_SLICE.stop),
        )
    )
    pd_orbit = chart.gauge_orbit_matrix(state)[pd_indices]
    pd_complete, pd_singular_values, _ = np.linalg.svd(
        pd_orbit, full_matrices=True
    )
    pd_rank = int(
        np.sum(pd_singular_values > 1.0e-10 * pd_singular_values[0])
    )
    pd_quotient = pd_complete[:, pd_rank:]
    pd_hessian = hessian[np.ix_(pd_indices, pd_indices)]
    pd_transverse = pd_quotient.T @ pd_hessian @ pd_quotient
    pd_eigenvalues = np.linalg.eigvalsh(
        0.5 * (pd_transverse + pd_transverse.T)
    )
    numerical_pass = bool(
        numerical_rank == EXPECTED_FULL_SYMMETRY_RANK
        and quotient.shape[1] == EXPECTED_QUOTIENT_DIMENSION
        and eigenvalues[0] > 1.0e-4
        and not np.any(eigenvalues <= 0)
        and pd_rank == 36
        and pd_eigenvalues[0] > 1.0e-4
    )
    return {
        "evidence_kind": "live_486_field_compiler_float64_unit_scale_representative",
        "recomputed_in_this_invocation": True,
        "proof_grade": False,
        "h_equals_r_equals_x": 1.0,
        "parameter_rows_assembled": len(parameter_rows),
        "nonzero_parameter_count": len(nonzero),
        "full_gradient_max_abs_residual": float(
            np.max(np.abs(gradient), initial=0.0)
        ),
        "full_gradient_norm": float(np.linalg.norm(gradient)),
        "numerical_symmetry_orbit_rank": numerical_rank,
        "orbit_smallest_nonzero_singular_value": float(
            singular_values[numerical_rank - 1]
        ),
        "orbit_largest_null_singular_value": float(
            singular_values[numerical_rank]
        ),
        "stationary_Hessian_symmetry_max_abs_residual": float(
            np.max(np.abs(hessian @ complete[:, :numerical_rank]), initial=0.0)
        ),
        "transverse_dimension": int(quotient.shape[1]),
        "minimum_transverse_eigenvalue": float(eigenvalues[0]),
        "maximum_transverse_eigenvalue": float(eigenvalues[-1]),
        "negative_transverse_eigenvalues_below_minus_1e_minus_10": int(
            np.sum(eigenvalues < -1.0e-10)
        ),
        "zero_transverse_eigenvalues_at_1e_minus_10": int(
            np.sum(np.abs(eigenvalues) <= 1.0e-10)
        ),
        "P_plus_Sigma": {
            "SO10_orbit_rank": pd_rank,
            "transverse_dimension": int(pd_quotient.shape[1]),
            "minimum_transverse_eigenvalue": float(pd_eigenvalues[0]),
            "negative_eigenvalues_below_minus_1e_minus_10": int(
                np.sum(pd_eigenvalues < -1.0e-10)
            ),
            "zero_eigenvalues_at_1e_minus_10": int(
                np.sum(np.abs(pd_eigenvalues) <= 1.0e-10)
            ),
        },
        "strict_local_minimum_high_confidence_numeric": numerical_pass,
        "strict_local_minimum_proof_grade": False,
        "limitation": RECORDED_UNIT_SCALE_HESSIAN["limitation"],
    }


def build_report(*, recompute_heavy: bool = False) -> dict[str, Any]:
    stationarity = exact_full_stationarity_certificate()
    orbit = exact_orbit_rank_certificate()
    no_go = exact_fixed_p_gap_curvature_no_go()
    counter = counterexample.build_report()
    hessian = (
        recompute_live_unit_scale_hessian()
        if recompute_heavy
        else dict(RECORDED_UNIT_SCALE_HESSIAN)
    )
    checks = {
        "exact_lower_energy_witness_source_bound": counter["flags"][
            "lower_energy_field_witness_exactly_certified"
        ],
        "replacement_full_486_gradient_exact": stationarity[
            "full_486_gradient_exactly_zero"
        ],
        "replacement_orbit_ranks_exact_39_40_41": (
            orbit["SO10"]["rank"] == EXPECTED_SO10_RANK
            and orbit["SO10_plus_U1X"]["rank"] == EXPECTED_GAUGE_RANK
            and orbit["SO10_plus_U1X_plus_PQ"]["rank"]
            == EXPECTED_FULL_SYMMETRY_RANK
        ),
        "replacement_physical_quotient_dimension_445": orbit[
            "physical_quotient_dimension"
        ]
        == EXPECTED_QUOTIENT_DIMENSION,
        "full_51_fixed_P_gap_curvature_no_go_exact": no_go[
            "source_binding_exact"
        ],
        "replacement_has_wrong_target_gauge_orbit_rank": (
            orbit["SO10_plus_U1X"]["rank"] == 40
            and orbit["SO10_plus_U1X"]["rank"]
            != TARGET_SELECTED_GAUGE_ORBIT_RANK
        ),
        "live_unit_scale_hessian_has_445_positive_transverse_modes": (
            hessian["strict_local_minimum_high_confidence_numeric"]
            and hessian["transverse_dimension"] == EXPECTED_QUOTIENT_DIMENSION
            and hessian["minimum_transverse_eigenvalue"] > 0
        ),
        "Hessian_claim_not_promoted_to_exact_proof": not hessian[
            "strict_local_minimum_proof_grade"
        ],
        "global_minimum_not_claimed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "status": (
            "EXACT_REPLACEMENT_STATIONARY_ORBIT__NUMERIC_STRICT_LOCAL_MINIMUM__GLOBAL_OPEN"
            if not failures
            else "REPLACEMENT_STATIONARY_ORBIT_AUDIT_FAILED"
        ),
        "overall_state": "LOWER_STATIONARY_ORBIT_FOUND__GLOBAL_MINIMUM_OPEN",
        "model_contract_id": MODEL_CONTRACT_ID,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "exact_stationarity": stationarity,
        "exact_symmetry_orbit": orbit,
        "exact_fixed_P_gap_curvature_no_go": no_go,
        "live_hessian_classification": hessian,
        "exact_energy_relation": counter["exact_energy_comparison"],
        "flags": {
            "replacement_is_lower_than_selected_Delta_exact": counter["flags"][
                "lower_energy_field_witness_exactly_certified"
            ],
            "replacement_full_stationarity_exact": stationarity[
                "full_486_gradient_exactly_zero"
            ],
            "replacement_symmetry_orbit_rank_exact": orbit[
                "source_binding_exact"
            ],
            "replacement_target_gauge_symmetry_correct": False,
            "replacement_gauge_orbit_rank_40_not_target_37": (
                orbit["SO10_plus_U1X"]["rank"] == 40
            ),
            "selected_fixed_P_Delta_orbit_excluded_by_gap_curvature_no_go": no_go[
                "source_binding_exact"
            ],
            "replacement_strict_local_minimum_high_confidence_numeric": hessian[
                "strict_local_minimum_high_confidence_numeric"
            ],
            "replacement_strict_local_minimum_proof_grade": False,
            "replacement_global_minimum_established": False,
            "replacement_global_uniqueness_established": False,
            "all_competing_stationary_orbits_exhausted": False,
            "G3_closed": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
            "whole_theory_excluded": False,
        },
        "next_required_test": (
            "Construct the direct Q(sqrt(22)) source-bound replacement Hessian, "
            "certify PSD/rank 445 after the 41-dimensional symmetry quotient, "
            "then globally compare this orbit against every remaining stationary orbit."
        ),
        "interpretation": (
            "The old Delta_R orbit is not global, but its exact lower-energy "
            "counterexample is itself an exact stationary orbit.  Its live "
            "well-conditioned Hessian is strictly positive on 445 transverse "
            "directions.  However its gauge-orbit rank is 40 rather than the "
            "target 37, so it has the wrong unbroken gauge symmetry.  The exact "
            "gap-curvature identity separately excludes the fixed P+Delta_R "
            "orbit. General Phi=(p,a,omega) branches remain open, so G3 is not closed."
        ),
    }


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, np.generic):
        return value.item()
    return value


def render_markdown(report: dict[str, Any]) -> str:
    hessian = report["live_hessian_classification"]
    orbit = report["exact_symmetry_orbit"]
    return "\n".join(
        [
            "# Exact G3 replacement stationary-orbit audit — v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["interpretation"],
            "",
            "## Exact results",
            "",
            "- full 486-gradient: exactly zero from the complete 27-parameter SOS map;",
            "- 126bar identity: `grad W(z)=33 z` in all 252 real coordinates;",
            "- SO(10), gauge, and full-symmetry orbit ranks: "
            f"`{orbit['SO10']['rank']}`, `{orbit['SO10_plus_U1X']['rank']}`, "
            f"`{orbit['SO10_plus_U1X_plus_PQ']['rank']}`;",
            f"- physical quotient dimension: `{orbit['physical_quotient_dimension']}`.",
            f"- replacement gauge rank: `{orbit['SO10_plus_U1X']['rank']}` "
            f"(target `{TARGET_SELECTED_GAUGE_ORBIT_RANK}`): **wrong symmetry**.",
            "",
            "## Numerical Hessian classification",
            "",
            f"- transverse dimension: `{hessian['transverse_dimension']}`;",
            f"- minimum eigenvalue: `{hessian['minimum_transverse_eigenvalue']:.15g}`;",
            f"- negative/zero modes at 1e-10: "
            f"`{hessian['negative_transverse_eigenvalues_below_minus_1e_minus_10']}` / "
            f"`{hessian['zero_transverse_eigenvalues_at_1e_minus_10']}`;",
            "- proof grade: **false** (direct Q(sqrt(22)) LDL remains open).",
            "",
            "## G3 consequence",
            "",
            "This is an exact lower stationary orbit and a high-confidence numerical "
            "strict local minimum, but it has the wrong unbroken gauge symmetry. "
            "The exact two-tangent identity excludes the fixed P+Delta_R orbit. "
            "General SM-preserving Phi branches remain open, so G3 remains open.",
            "",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--write",
        action="store_true",
        help="accepted for consistency; this standalone artifact is always written",
    )
    parser.add_argument("--recompute-heavy", action="store_true")
    args = parser.parse_args()
    report = build_report(recompute_heavy=args.recompute_heavy)
    OUT_JSON.write_text(json.dumps(_jsonable(report), indent=2) + "\n")
    OUT_MD.write_text(render_markdown(report))
    print(json.dumps(_jsonable(report), indent=2))


if __name__ == "__main__":
    main()
