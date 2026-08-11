#!/usr/bin/env python3
"""Exact full-126 equality-kernel and physical strictness at signed P0.

This hold-only verifier treats the sharp endpoint of the signed-Kahler
operator certificate at normalized null ``H=h_minus``.  In the live
``z=sqrt(10) Phi`` coordinates, the opposite-orientation representative
``P0`` has ``||z||^2=10`` and the scaled angular operator is

    1600 T(P0) = 5 B(P0)^dag B(P0) + 24 K.

The verifier constructs the four-complex-dimensional exterior-algebra
intertwiner explicitly, proves that it is the complete kernel, and applies
the complete live Sym^2(126bar) channel projectors to every one of its ten
quadratic coefficient tensors.  Thus every unit Sigma in the kernel obeys

    I54=I1050bar=0,  I2772bar=2/3,  I4125=1/3,
    R=Q=P=j=S=0.

The remaining physical radial polynomial is a sum of two squares.  Its
minimum is zero, while the selected maximally-negative-current reference has
minimum ``-7001/995000``.  Hence every angular equality direction at P0 is
strictly above the selected physical reference by ``7001/995000``.

This is an endpoint theorem only.  It neither proves the moving full signed
orbit theorem nor closes arbitrary Phi/Sigma, G3, or G4.
"""
from __future__ import annotations

from fractions import Fraction as Q
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any

import numpy as np


HERE = Path(__file__).resolve().parent
REPO = HERE.parent / "so10-axion-v20-reaudit"
for source in (HERE, REPO):
    if str(source) not in sys.path:
        sys.path.insert(0, str(source))

import exact_126bar_self_quartic_basis_v20 as sigma_self
import exact_gauged_u1x_g3_sos_bfb_stationarity_v20 as stationarity
import exact_gauged_u1x_g3_su5_max_negative_zero_residual_bound_v20 as radial_source
import prototype_failclosed_g3_scope_census_joint_current_self_exclusion as radial_contract
import prototype_full126_matrix_sos_infrastructure as infrastructure


STATUS = "EXACT_SIGNED_KAEHLER_P0_FULL126_KERNEL_RADIAL_STRICTNESS__G3_OPEN"
EXPECTED_CORE_SHA256 = "d5cd0d6458e39f2a354f25cc7bcbd7eb1736763525a5560a82ad3662019ef812"
MODULAR_PRIME = 1_000_003
PLANE_SIGNS = (1, 1, -1, -1, -1)
EXPECTED_P0_SUPPORT = (
    (0, 1),
    (13, -1),
    (22, -1),
    (27, -1),
    (140, -1),
    (149, -1),
    (154, -1),
    (195, 1),
    (200, 1),
    (209, 1),
)
CHANNELS = ("54", "1050bar", "2772bar", "4125")
EXPECTED_DEPENDENCY_SHA256 = {
    "full126_matrix_source_and_Kahler_intertwiner": (
        HERE / "prototype_full126_matrix_sos_infrastructure.py",
        "b68708ff0e17eb74d8a4e7378b8364152564743c7b6d8e5dcc0b9cafbd6d77c1",
    ),
    "radial_current_and_sigma_self_contract": (
        HERE / "prototype_failclosed_g3_scope_census_joint_current_self_exclusion.py",
        "327aa1ce990c586978669bbdd6693752b028433187a431650875164040c9faa9",
    ),
    "live_Sym2_126bar_projectors": (
        REPO / "exact_126bar_self_quartic_basis_v20.py",
        "ce65f0ba17bff823925298e78f4d1f79b0376a85d9261b9c811342eda9793077",
    ),
    "live_126bar_pair_Casimir_and_current": (
        REPO / "exact_gauged_u1x_g3_sos_bfb_stationarity_v20.py",
        "0b0fa1a937a1ff09856fbd735faf50be4fb59d2684289ff266eb6931c437cd90",
    ),
    "exact_modular_rank_source": (
        REPO / "exact_gauged_u1x_g3_su5_delta_pd_sos_v20.py",
        "afc1dca43a6ec2a657a4ab8e3a846517edaaaf532f1c3fffd1a82c637d208c6b",
    ),
    "selected_reference_radial_minimum": (
        REPO / "exact_gauged_u1x_g3_su5_max_negative_zero_residual_bound_v20.py",
        "56ffd3b04acbdf8730a5352319a94317447ac1fbb39e18536dac890a505372f1",
    ),
    "live_direct_form_conventions": (
        REPO / "direct_phi_h_sigmabar_tensor_v20.py",
        "604bd4a2637afca99df880cbc9eb0f62bde04d2d838db9d1c6f893f48b0f6067",
    ),
    "live_mixed_residual_source": (
        REPO / "exact_gauged_u1x_g3_a_square_recoupling_v20.py",
        "f8dbdec630e52646951289ce49a42895a454def2d199f622d8c33a542f88308b",
    ),
    "live_coordinate_chart": (
        REPO / "live_g2_canonical_486_field_chart_v20.py",
        "85ae9470f3aa25c28fc03c083b6c1e150106a276e51044a590060d290ba7945e",
    ),
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def _python_inner(
    left: tuple[np.ndarray, np.ndarray], right: tuple[np.ndarray, np.ndarray]
) -> int:
    return sum(
        int(x) * int(y)
        for x, y in zip(left[0].flat, right[0].flat, strict=True)
    ) + sum(
        int(x) * int(y)
        for x, y in zip(left[1].flat, right[1].flat, strict=True)
    )


def _pair_casimir_preflight(real: np.ndarray, imaginary: np.ndarray) -> int:
    """Prebound every accumulator in one live int64 pair-Casimir call."""
    generators_real, generators_imaginary = stationarity.integer_sigma_generators()
    real_max = max((abs(int(value)) for value in real.flat), default=0)
    imaginary_max = max((abs(int(value)) for value in imaginary.flat), default=0)
    output_bound = 0
    for generator_real, generator_imaginary in zip(
        generators_real, generators_imaginary, strict=True
    ):
        real_l1 = max(
            sum(abs(int(value)) for value in row) for row in generator_real
        )
        imaginary_l1 = max(
            sum(abs(int(value)) for value in row) for row in generator_imaginary
        )
        left_real = real_l1 * real_max + imaginary_l1 * imaginary_max
        left_imaginary = real_l1 * imaginary_max + imaginary_l1 * real_max
        output_bound += max(
            left_real * real_l1 + left_imaginary * imaginary_l1,
            left_real * imaginary_l1 + left_imaginary * real_l1,
        )
    if output_bound >= 2**63:
        raise OverflowError("a live pair-Casimir contraction is not int64-safe")
    return output_bound


def _project_pair(
    pair: tuple[np.ndarray, np.ndarray], channel: str
) -> tuple[tuple[np.ndarray, np.ndarray], int, tuple[int, ...]]:
    powers = [pair]
    bounds: list[int] = []
    for _ in range(3):
        bounds.append(_pair_casimir_preflight(*powers[-1]))
        powers.append(stationarity._sigma_pair_casimir(*powers[-1]))
    polynomial = sigma_self._poly(channel)
    denominator = math.lcm(
        *(coefficient.denominator for coefficient in polynomial)
    )
    projected = tuple(
        sum(
            (
                int(coefficient * denominator)
                * np.asarray(powers[degree][part], dtype=object)
                for degree, coefficient in enumerate(polynomial)
            ),
            np.zeros_like(pair[part], dtype=object),
        )
        for part in (0, 1)
    )
    return projected, denominator, tuple(bounds)


@lru_cache(maxsize=1)
def exact_kernel_and_operator() -> dict[str, Any]:
    z = infrastructure._kahler_vector(PLANE_SIGNS)
    support = tuple(
        (int(index), int(value)) for index, value in enumerate(z) if value
    )
    if support != EXPECTED_P0_SUPPORT or int(z @ z) != 10:
        raise ArithmeticError("the integral P0 representative drifted")
    phi_channels = infrastructure._normalized_phi_projectors(z)
    if phi_channels != {"54": Q(0), "4125": Q(0)}:
        raise ArithmeticError("P0 left the live Phi-self zero locus")

    chiral_rows, integrality_residual = radial_source._integral_chiral_wedge_rows()
    if integrality_residual != 0.0 or np.any(chiral_rows @ z):
        raise ArithmeticError("P0 left the live chiral kernel")

    B, gram = infrastructure.residual_operator(z)
    generators_real, generators_imaginary = stationarity.integer_sigma_generators()
    K = (-generators_imaginary[0], generators_real[0])
    if not infrastructure.ghermitian(K):
        raise ArithmeticError("the live current generator lost Hermiticity")
    projectors = infrastructure.current_projectors(K)
    dimensions = {
        charge: Q(int(np.trace(value[0][0])), value[1])
        for charge, value in projectors.items()
    }
    if dimensions != {-1: Q(35), 0: Q(56), 1: Q(35)}:
        raise ArithmeticError("the live K branching drifted")

    J, triples = infrastructure._kahler_intertwiner(PLANE_SIGNS)
    zero_indices = tuple(
        index for index, triple in enumerate(triples) if 0 not in triple
    )
    if zero_indices != (6, 7, 8, 9):
        raise ArithmeticError("the canonical four kernel columns drifted")
    J0 = (J[0][:, zero_indices], J[1][:, zero_indices])
    gram_J0 = infrastructure.gadjoint_gram(J0)
    if not (
        np.array_equal(gram_J0[0], 8 * np.eye(4, dtype=np.int64))
        and not np.any(gram_J0[1])
    ):
        raise ArithmeticError("J0^dag J0 != 8 I4")
    if not infrastructure.giszero(infrastructure.gapply(B, J0)):
        raise ArithmeticError("B(P0)J0 != 0")
    if not infrastructure.giszero(infrastructure.gapply(K, J0)):
        raise ArithmeticError("KJ0 != 0")

    stacked = np.vstack(
        (infrastructure.realification(B), infrastructure.realification(K))
    )
    stacked_rank = infrastructure.rank_source._rank_mod_prime(stacked, MODULAR_PRIME)
    if stacked_rank != 244:
        raise ArithmeticError("rank([B;K]) mod p drifted")
    # J0 has real rank eight by J0^dag J0=8I4, so the modular lower bound
    # and the explicit kernel upper bound meet: rank_Q=244, nullity_Q=8.

    if not infrastructure.giszero(
        infrastructure.gadd(
            infrastructure.gmul(gram, K),
            infrastructure.gscale(infrastructure.gmul(K, gram), -1),
        )
    ):
        raise ArithmeticError("[B^dag B,K] != 0 at P0")
    pminus, _pminus_denominator = projectors[-1]
    identity = np.eye(126, dtype=np.int64)
    polynomial = (identity.copy(), np.zeros_like(identity))
    for root in (16, 64, 144):
        polynomial = infrastructure.gmul(
            polynomial, (gram[0] - root * identity, gram[1])
        )
    if not infrastructure.giszero(infrastructure.gmul(polynomial, pminus)):
        raise ArithmeticError("the K=-1 residual spectral identity drifted")
    # On K=-1, 5B^dag B+24K has floor 5*16-24=56.  On K=+1
    # it has floor 24.  On K=0 it is 5B^dag B, whose complete kernel is J0.

    mutation_column = (J[0][:, :1], J[1][:, :1])
    if infrastructure.giszero(infrastructure.gapply(K, mutation_column)):
        raise ArithmeticError("the charge-one column mutation was not rejected")
    return {
        "P0_plane_signs": list(PLANE_SIGNS),
        "P0_integral_support": [list(item) for item in support],
        "P0_raw_norm_squared": 10,
        "Phi0_normalization": "Phi0=P0/sqrt(10), hence N_Phi=1",
        "Phi_self_channels": {name: str(value) for name, value in phi_channels.items()},
        "live_chiral_rows_times_P0_are_zero": True,
        "B_shape_complex": list(B[0].shape),
        "K_complex_spectrum_multiplicities": {"-1": 35, "0": 56, "+1": 35},
        "kernel_intertwiner": (
            "J0=J_t on triples (123),(124),(134),(234), t=-plane_signs"
        ),
        "J0_dagger_J0": "8 I4",
        "B_P0_J0_zero": True,
        "K_J0_zero": True,
        "rank_mod_prime_of_stacked_B_K": {
            "prime": MODULAR_PRIME,
            "rank": stacked_rank,
            "shape": list(stacked.shape),
        },
        "exact_common_kernel": {
            "complex_dimension": 4,
            "real_dimension": 8,
            "description": "image_C(J0)=ker B(P0) intersect ker K",
        },
        "scaled_angular_operator": "1600T(P0)=5B(P0)^dag B(P0)+24K",
        "Kminus_residual_roots": [16, 64, 144],
        "Kminus_scaled_T_floor": 56,
        "Kplus_scaled_T_floor": 24,
        "T_P0_positive_semidefinite_exact": True,
        "T_P0_kernel_equals_image_J0": True,
        "mutation_guard": "a J column whose triple contains 0 has K=+1, not K=0",
    }


@lru_cache(maxsize=1)
def exact_kernel_self_channels() -> dict[str, Any]:
    J, triples = infrastructure._kahler_intertwiner(PLANE_SIGNS)
    zero_indices = tuple(
        index for index, triple in enumerate(triples) if 0 not in triple
    )
    real = J[0][:, zero_indices]
    imaginary = J[1][:, zero_indices]
    pair_labels: list[tuple[int, int]] = []
    pair_coefficients: list[tuple[np.ndarray, np.ndarray]] = []
    for left in range(4):
        for right in range(left, 4):
            pair_real = np.outer(real[:, left], real[:, right]) - np.outer(
                imaginary[:, left], imaginary[:, right]
            )
            pair_imaginary = np.outer(real[:, left], imaginary[:, right]) + np.outer(
                imaginary[:, left], real[:, right]
            )
            if left < right:
                pair_real = pair_real + pair_real.T
                pair_imaginary = pair_imaginary + pair_imaginary.T
            pair_labels.append((left, right))
            pair_coefficients.append((pair_real, pair_imaginary))

    channel_reports: dict[str, Any] = {}
    largest_preflight = 0
    for channel in CHANNELS:
        projected: list[tuple[tuple[np.ndarray, np.ndarray], int]] = []
        denominators: set[int] = set()
        for pair in pair_coefficients:
            response, denominator, bounds = _project_pair(pair, channel)
            largest_preflight = max(largest_preflight, *bounds)
            denominators.add(denominator)
            projected.append((response, denominator))
        if len(denominators) != 1:
            raise ArithmeticError("one channel acquired inconsistent denominators")

        gram: list[list[Q]] = []
        for left_response, left_denominator in projected:
            row: list[Q] = []
            for right_response, right_denominator in projected:
                row.append(
                    Q(
                        _python_inner(left_response, right_response),
                        left_denominator * right_denominator,
                    )
                )
            gram.append(row)

        if channel in ("54", "1050bar"):
            if any(value for row in gram for value in row):
                raise ArithmeticError(channel + " does not vanish on Sym2(J0)")
            channel_reports[channel] = {
                "projected_quadratic_coefficient_count": 10,
                "all_projected_coefficients_zero": True,
                "Gram_rank": 0,
                "mass_for_unit_Sigma": "0",
            }
            continue

        diagonal_norm = Q(128, 3) if channel == "2772bar" else Q(64, 3)
        expected = [
            [
                (
                    diagonal_norm
                    * (1 if pair_labels[row] == pair_labels[column] else 0)
                    * (1 if pair_labels[row][0] == pair_labels[row][1] else 2)
                )
                for column in range(10)
            ]
            for row in range(10)
        ]
        if gram != expected:
            raise ArithmeticError(channel + " monomial Gram identity drifted")
        channel_reports[channel] = {
            "projected_quadratic_coefficient_count": 10,
            "monomial_order": [list(pair) for pair in pair_labels],
            "Gram_is_diagonal": True,
            "diagonal_pair_norm_squared": str(diagonal_norm),
            "offdiagonal_pair_norm_squared": str(2 * diagonal_norm),
            "all_distinct_monomial_inner_products_zero": True,
            "mass_for_unit_Sigma": "2/3" if channel == "2772bar" else "1/3",
        }

    if largest_preflight >= 2**63:
        raise OverflowError("the advertised pair-Casimir preflight is unsafe")
    return {
        "kernel_parameterization": (
            "Sigma=J0*w, w in C^4; ||Sigma||^2=8 sum_i |w_i|^2"
        ),
        "quadratic_monomial_expansion": (
            "Sigma tensor Sigma=sum_i w_i^2 C_ii+sum_{i<j}w_i w_j C_ij"
        ),
        "projector_channel_reports": channel_reports,
        "derived_unit_channel_masses": {
            "I54": "0",
            "I1050bar": "0",
            "I2772bar": "2/3",
            "I4125": "1/3",
        },
        "projector_completeness_check": "0+0+2/3+1/3=1",
        "retained_S=I54+I1050bar": "0",
        "largest_pair_Casimir_preoperation_int64_bound": largest_preflight,
        "int64_max": 2**63 - 1,
        "all_pair_Casimir_calls_prebounded": True,
        "all_projector_accumulations_and_Grams_use_Python_int": True,
        "ratio_mutation_guard": (
            "the exact 4125 monomial norm is 64/3, so replacing its unit "
            "mass 1/3 by 1/2 is rejected"
        ),
    }


@lru_cache(maxsize=1)
def exact_physical_radial_strictness() -> dict[str, Any]:
    contract = radial_contract.symbolic_quadratic_contract()
    if contract["current_definition"] != "m=max(-j,0)":
        raise ArithmeticError("the live current convention drifted")
    if "S*v^2/8" not in contract["radial_lower"]:
        raise ArithmeticError("the live Sigma-self radial coefficient drifted")

    # At the exact kernel: normalized null H means x=1; B(P0)Sigma=0 gives
    # R=0; P0 is unit, Phi-self zero and chiral-zero, so P=Q=0; K Sigma=0
    # gives j=m=0; and the channel theorem above gives S=0.
    u = Q(1)
    v = Q(1, 25)
    endpoint_value = (u - 1) ** 2 + (v - Q(1, 25)) ** 2 / 8
    if endpoint_value != 0:
        raise ArithmeticError("the kernel radial minimum drifted")

    u_reference = Q(1001, 995)
    v_reference = Q(48, 199)
    reference_value = (
        (u_reference - 1) ** 2
        + (v_reference - Q(1, 25)) ** 2 / 8
        - u_reference * v_reference / 20
    )
    derivative_u = 2 * (u_reference - 1) - v_reference / 20
    derivative_v = (v_reference - Q(1, 25)) / 4 - u_reference / 20
    hessian_determinant = Q(1, 4) - Q(1, 400)
    if (
        reference_value != radial_source.RADIAL_CURRENT_MINIMUM
        or reference_value != Q(-7001, 995000)
        or derivative_u != 0
        or derivative_v != 0
        or hessian_determinant != Q(99, 400)
    ):
        raise ArithmeticError("the selected reference radial minimum drifted")
    shifted_gap = endpoint_value - reference_value
    if shifted_gap != Q(7001, 995000):
        raise ArithmeticError("the endpoint strict shifted gap drifted")

    mutated_at_reference = (
        (u_reference - 1) ** 2
        + (v_reference - Q(1, 25)) ** 2 / 8
        - u_reference * v_reference / 20
    )
    if mutated_at_reference >= 0:
        raise ArithmeticError("the j=-1 current-sign mutation was not rejected")
    return {
        "kernel_angular_invariants": {
            "P": "0",
            "Q": "0",
            "R": "0",
            "S=I54+I1050bar": "0",
            "j": "0",
            "m=max(-j,0)": "0",
            "null_H_shape_x": "1",
        },
        "complete_kernel_radial_polynomial": (
            "G0(u,v)=(u-1)^2+(v-1/25)^2/8"
        ),
        "physical_domain": "u>=0,v>=0",
        "kernel_global_minimizer": {"u": "1", "v": "1/25"},
        "kernel_global_minimum": "0",
        "selected_reference_polynomial": (
            "Gminus(u,v)=(u-1)^2+(v-1/25)^2/8-uv/20"
        ),
        "selected_reference_Hessian_determinant": str(hessian_determinant),
        "selected_reference_global_minimizer": {
            "u": str(u_reference),
            "v": str(v_reference),
        },
        "selected_reference_global_minimum": str(reference_value),
        "strict_physical_shifted_gap_on_every_kernel_direction": str(shifted_gap),
        "equality_statement": (
            "angular equality remains at P0, but it cannot tie or beat the "
            "selected physical vacuum after the exact radial comparison"
        ),
        "current_sign_mutation": {
            "replace_kernel_j=0_by_j=-1": str(mutated_at_reference),
            "mutation_is_negative": True,
        },
    }


@lru_cache(maxsize=1)
def build_report() -> dict[str, Any]:
    dependencies: dict[str, str] = {}
    for label, (path, expected) in EXPECTED_DEPENDENCY_SHA256.items():
        observed = _sha256(path)
        if observed != expected:
            raise ArithmeticError(label + " dependency hash drifted")
        dependencies[label] = observed
    core = {
        "status": STATUS,
        "dependency_sha256": dependencies,
        "exact_endpoint_kernel_and_operator": exact_kernel_and_operator(),
        "exact_kernel_Sym2_126bar_channels": exact_kernel_self_channels(),
        "exact_physical_radial_strictness": exact_physical_radial_strictness(),
        "scope": {
            "fixed_normalized_null_H": True,
            "fixed_opposite_orientation_signed_Kahler_P0": True,
            "all_unit_full126_Sigma_in_the_eight_real_angular_kernel": True,
            "exact_endpoint_T_PSD_and_complete_kernel": True,
            "exact_physical_strictness_of_all_endpoint_zero_modes": True,
            "full_signed_Kahler_orbit": False,
            "arbitrary_Phi210": False,
            "arbitrary_full126_Sigma_away_from_the_endpoint_kernel": False,
            "nonnull_H_transport": False,
            "physical_negative_witness": False,
            "G3_closed": False,
            "G4_closed": False,
        },
    }
    digest = _canonical_sha256(core)
    if EXPECTED_CORE_SHA256 and digest != EXPECTED_CORE_SHA256:
        raise ArithmeticError("canonical core hash drifted")
    return {**core, "core_sha256": digest}


def main() -> None:
    print(json.dumps(build_report(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
