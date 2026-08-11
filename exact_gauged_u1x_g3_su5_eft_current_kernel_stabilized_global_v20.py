#!/usr/bin/env python3
"""Exact EFT current-kernel stabilization of the SU(5)+Delta vacuum.

Let ``V0`` be the beta-zero member of the frozen SU(5)+Delta+chiral-H
candidate.  Its complete field-dependent gap is already an explicit sum of
nonnegative terms.  The only local defect is a six-dimensional transverse
kernel.  This theorem adds the gauge-invariant dimension-six operator

    V_EFT = gamma ||A_H Sigma||^2,             gamma = 1/20,

where ``A_H`` is the Hermitian 126bar current operator defined by

    I45(H,Sigma) = <Sigma,A_H Sigma>.

The selected Delta lies in ``ker A_H``.  Hence the new square and its first
jet vanish there.  An exact fixed-lattice calculation proves that its
Jacobian has rank six on the beta-zero nonsymmetry kernel, while annihilating
all 38 SO(10) x U(1)_X x PQ tangents.  The full Hessian is therefore PSD of
rank 448 and is strict on the physical quotient.

Globality is immediate from the sum of squares, but equality still requires
care.  The frozen global Phi theorem puts every Phi projector zero on the
signed Kahler cones.  The negative sheet has no nonzero mixed Sigma zero.
On the positive sheet the Sigma zero is a decomposable two-form z, the Hodge
square forces H into the positive C^5 chirality, and the exact current
current-endomorphism theorem gives the exact norm identity

    ||K_H Sigma(z)||^2 = N_H ||H wedge z||^2.

Thus ``K_H Sigma(z)=0`` says that the H line lies in the two-plane of z.  These
normalized flags form one SU(5) orbit; the two declared phase symmetries and
the central U(5) action remove the remaining phases.  The equality set is
exactly the selected symmetry orbit.

This is an EFT extension, not a member of the authoritative renormalizable
51-parameter pencil.  The renormalizable coefficients remain inside that
contract.  G4 and phenomenological EFT-scale matching are not claimed.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import math
from functools import lru_cache
from pathlib import Path
import sys
from typing import Any

import numpy as np


HERE = Path(__file__).resolve().parent
REPO = (
    HERE
    if (HERE / "exact_gauged_u1x_g3_su5_delta_hsx_extension_v20.py").is_file()
    else HERE.parent / "so10-axion-v20-reaudit"
)
for source in (HERE, REPO):
    if str(source) not in sys.path:
        sys.path.insert(0, str(source))

import exact_gauged_u1x_g3_su5_delta_hsx_extension_v20 as hsx
import exact_gauged_u1x_g3_su5_delta_hsx_exact_hessian_v20 as hessian_source
import exact_gauged_u1x_g3_su5_delta_pd_sos_v20 as pd_source
import exact_gauged_u1x_g3_su5_equality_orbit_v20 as equality_source
import exact_gauged_u1x_physical_quotient_v20 as quotient_source
import exact_h10_self_quartic_family_v20 as h10_source
import gauged_u1x_g2_derivative_audit_v20 as g2_audit
import live_g2_arbitrary_component_potential_values_v20 as potential
import live_g2_canonical_486_field_chart_v20 as chart
import live_g2_exact_hsigma_hermitian_derivatives_v20 as current_source
import live_g2_exact_quadratic_family_derivatives_v20 as derivatives

PHI_GLOBAL_MODULE = (
    "exact_phi_self_zero_global_signed_kaehler_classification_v20"
    if (HERE / "exact_phi_self_zero_global_signed_kaehler_classification_v20.py").is_file()
    else "prototype_phi_self_zero_global_signed_kaehler_classification"
)
phi_global = importlib.import_module(PHI_GLOBAL_MODULE)
PHI_GLOBAL_PATH = HERE / f"{PHI_GLOBAL_MODULE}.py"
PHI_GLOBAL_EXPECTED_RAW_SHA256 = (
    "6887429cebbe0e0ee9171b9346b85c671959c2fdbc2b5187efc73a52552b0883"
    if PHI_GLOBAL_MODULE == "exact_phi_self_zero_global_signed_kaehler_classification_v20"
    else "17038c6fb82ba565a16228f5f5c03026f0ab8e3ad7959792498c2785b9653066"
)
O6_MODULE = (
    "exact_hsigma_current_endomorphism_dimension6_stabilizer_v20"
    if (HERE / "exact_hsigma_current_endomorphism_dimension6_stabilizer_v20.py").is_file()
    else "prototype_exact_hsigma_current_endomorphism_dimension6_stabilizer"
)
o6_source = importlib.import_module(O6_MODULE)
O6_PATH = HERE / f"{O6_MODULE}.py"


STATUS = "EXACT_EFT_CURRENT_KERNEL_STABILIZED_GLOBAL_G3"
OUT_JSON = HERE / "EXACT_EFT_CURRENT_KERNEL_STABILIZED_GLOBAL_G3.json"
OUT_MD = HERE / "EXACT_EFT_CURRENT_KERNEL_STABILIZED_GLOBAL_G3.md"
EXPECTED_CORE_SHA256 = "2eca279488d92d8bd9eca974c0d598340124f025e62212cd8a188413a6e8b7d0"
EXPECTED_BASE_HESSIAN_SHA256 = (
    "194740e7e90eeee33d5d772ab549df969e9665e3aebc1580c3319f58eee36930"
)
EXPECTED_STABILIZED_HESSIAN_SHA256 = (
    "7ea54d59138f8e5b66aad3d1f1ecb707c65ac9bb0f0e118a597daaccc136b568"
)
EXPECTED_ORIGINAL_HESSIAN_SHA256 = (
    "b08fd08b570808162468f7b7c9a7ac0e8115f99259b84ae73bc2a32e7ec37428"
)
EXPECTED_SIGNED_CURRENT_NUMERATOR_SHA256 = (
    "1fe9326e73f0732feb5ecc808544ce22ae73f6b3ccc8ef059148941559ae25c4"
)
EXPECTED_JACOBIAN_SHA256 = (
    "a2f606e09324e21011b2a475bee8af47cb56963d23a70614657689214b788902"
)

GAMMA_NUMERATOR = 1
GAMMA_DENOMINATOR = 20
REMOVED_BETA_NUMERATOR = 1
REMOVED_BETA_DENOMINATOR = 20
RAW_HESSIAN_DENOMINATOR = 25_200_000
RAW_JACOBIAN_DENOMINATOR = 10
EXPECTED_BASE_RANK = 442
EXPECTED_BASE_NULLITY = 44
EXPECTED_FINAL_RANK = 448
EXPECTED_FINAL_NULLITY = 38
MODULAR_PRIMES = (1_000_003, 1_000_033)

EXPECTED_DEPENDENCY_SHA256 = {
    "global_signed_Kahler_classification": (
        PHI_GLOBAL_PATH,
        PHI_GLOBAL_EXPECTED_RAW_SHA256,
    ),
    "dimension_six_current_endomorphism": (
        O6_PATH,
        "c113abf41ca9527528dc00d248fdfa3fcae990e39ba4b76251ca197167cbad23",
    ),
    "Phi_Sigma_global_SOS": (
        REPO / "exact_gauged_u1x_g3_su5_delta_pd_sos_v20.py",
        "afc1dca43a6ec2a657a4ab8e3a846517edaaaf532f1c3fffd1a82c637d208c6b",
    ),
    "chiral_H_candidate_source": (
        REPO / "exact_gauged_u1x_g3_su5_delta_hsx_extension_v20.py",
        "c88a76c4bcc1f32ddce9eef15c87fe0a6794f7e0d7643ae774972a9b4b67c71f",
    ),
    "exact_Hessian_source": (
        REPO / "exact_gauged_u1x_g3_su5_delta_hsx_exact_hessian_v20.py",
        "cd4192713d8b3b13f6a9cf492f37d8615e3ead7a1a49fb3c30a1f6de235f7498",
    ),
    "fixed_F_equality_source": (
        REPO / "exact_gauged_u1x_g3_su5_equality_orbit_v20.py",
        (
            "53f8b5b6175f4c3a7a5b3ab49ef151be2baa91c4dcd3fdd4f4de07e15d002df6"
            if REPO == HERE
            else "f0f3efd4cb930825523d3b70c285d2a85c37b1c19bfdbcf1363597c6e9a4ba52"
        ),
    ),
    "H10_self_quartic_source": (
        REPO / "exact_h10_self_quartic_family_v20.py",
        "111de6af03b86af6e0ca3f125d150a5439cfdb90e3663d0dad46349584074936",
    ),
    "G2_contract": (
        REPO / "gauged_u1x_g2_derivative_audit_v20.py",
        "26e87e092986caf3fed729b97b6850d8500f9644603a70c5bc40ec4f843883e0",
    ),
    "live_potential_rows": (
        REPO / "live_g2_arbitrary_component_potential_values_v20.py",
        "997ab9e2a29c3125d47b006189b1ed69599644313b499754f7ee5e1e7e12d6bf",
    ),
    "live_coordinate_chart": (
        REPO / "live_g2_canonical_486_field_chart_v20.py",
        "85ae9470f3aa25c28fc03c083b6c1e150106a276e51044a590060d290ba7945e",
    ),
    "live_quadratic_derivatives": (
        REPO / "live_g2_exact_quadratic_family_derivatives_v20.py",
        "abdf1cf943908ff338208ce57bad4db2c70710ec36b9654eb56d06f3ca4aa9c8",
    ),
    "live_HSigma_current_derivatives": (
        REPO / "live_g2_exact_hsigma_hermitian_derivatives_v20.py",
        "bd15f4c15585e49e7884558992c3ca14a1e9777282e747f98f31fb2d8e32b1af",
    ),
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _jsonable(value: Any) -> Any:
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
    observed: dict[str, str] = {}
    for name, (path, expected) in EXPECTED_DEPENDENCY_SHA256.items():
        digest = _sha256(path)
        if digest != expected:
            raise ArithmeticError(
                f"dependency {name} drifted: expected {expected}, observed {digest}"
            )
        observed[name] = digest
    if o6_source.EXPECTED_CORE_SHA256 != (
        "598d916da16e746c8be30e979a13a27a47d1600e2dd4bee7b9cf9fc398ec9da1"
    ):
        raise ArithmeticError("the dimension-six theorem core pin drifted")
    if PHI_GLOBAL_MODULE.startswith("exact_") and getattr(
        phi_global, "EXPECTED_CORE_SHA256", None
    ) != "db493a74303a57862f09c2a92118ea3d66b8b12ecbaea9162155d4ab3baafecc":
        raise ArithmeticError("the production Phi theorem core pin drifted")
    return observed


def _rank_mod(matrix: np.ndarray, prime: int) -> int:
    work = np.asarray(matrix, dtype=np.int64).copy() % prime
    row = 0
    for column in range(work.shape[1]):
        candidates = np.flatnonzero(work[row:, column])
        if not candidates.size:
            continue
        pivot = row + int(candidates[0])
        work[[row, pivot]] = work[[pivot, row]]
        work[row] = work[row] * pow(int(work[row, column]), -1, prime) % prime
        active = np.flatnonzero(work[:, column])
        active = active[active != row]
        if active.size:
            work[active] = (
                work[active] - work[active, column, None] * work[row]
            ) % prime
        row += 1
        if row == work.shape[0]:
            break
    return row


def _gaussian_integer_parts(matrix: np.ndarray, label: str) -> tuple[np.ndarray, np.ndarray]:
    """Read an upstream source-declared Gaussian-integer tensor exactly."""
    value = np.asarray(matrix, dtype=complex)
    real = np.rint(value.real).astype(np.int64)
    imaginary = np.rint(value.imag).astype(np.int64)
    if np.max(np.abs(value - (real + 1j * imaginary)), initial=0.0) != 0.0:
        raise ArithmeticError(f"{label} left the exact Gaussian lattice")
    return real, imaginary


def _canonical_current_real_hessian(generator: np.ndarray, label: str) -> np.ndarray:
    """Return R with z^dag T z=(i/2)q^T Rq for z=(x+iy)/sqrt(2)."""
    real, imaginary = _gaussian_integer_parts(generator, label)
    dimension = real.shape[0]
    output = np.zeros((2 * dimension, 2 * dimension), dtype=np.int64)
    output[0::2, 0::2] = imaginary
    output[1::2, 1::2] = imaginary
    output[0::2, 1::2] = real
    output[1::2, 0::2] = -real
    if not np.array_equal(output, output.T):
        raise ArithmeticError(f"{label} did not realify to a symmetric current")
    return output


@lru_cache(maxsize=1)
def exact_signed_current_hessian_numerator() -> dict[str, Any]:
    """Exact raw Hessian of I45 at the target, with denominator 200.

    The upstream Fierz certificate proves that both generator families are
    Gaussian-integral.  In raw target coordinates h=(e_6+i e_7)/sqrt(2)
    becomes the two-entry integer vector below, while qSigma=y/10 and y is
    the frozen Gaussian-integer Delta vector.  Product-rule differentiation
    then gives, generator by generator,

      200 H_hh = (y^T R_S y) R_H,
      200 H_ss = (h^T R_H h) R_S,
      200 H_hs = 2 (R_H h)(R_S y)^T.
    """
    fierz = hsx.exact_hsigma_projector_fierz_certificate()
    if not fierz["source_binding_exact"]:
        raise ArithmeticError("the exact Gaussian current-generator source drifted")
    h_generators = tuple(
        _canonical_current_real_hessian(generator, f"H generator {index}")
        for index, generator in enumerate(current_source.h_generator_matrices())
    )
    sigma_generators = tuple(
        _canonical_current_real_hessian(generator, f"Sigma generator {index}")
        for index, generator in enumerate(current_source.sigma_generator_matrices())
    )
    if len(h_generators) != 45 or len(sigma_generators) != 45:
        raise ArithmeticError("the current generator census drifted")

    h = np.zeros(chart.H_REAL_DIM, dtype=np.int64)
    h[12] = 1
    h[15] = 1
    delta_real, delta_imaginary = hessian_source.delta_source.raw_delta_coordinates()
    y = np.empty(chart.SIGMA_REAL_DIM, dtype=np.int64)
    y[0::2] = delta_real
    y[1::2] = delta_imaginary
    if int(h @ h) != 2 or int(y @ y) != 8:
        raise ArithmeticError("the raw H/Delta target lattice drifted")

    numerator = np.zeros((chart.TOTAL_DIM, chart.TOTAL_DIM), dtype=np.int64)
    for r_h, r_sigma in zip(h_generators, sigma_generators, strict=True):
        h_quadratic = int(h @ r_h @ h)
        sigma_quadratic = int(y @ r_sigma @ y)
        numerator[chart.H_SLICE, chart.H_SLICE] += sigma_quadratic * r_h
        numerator[chart.SIGMA_SLICE, chart.SIGMA_SLICE] += h_quadratic * r_sigma
        cross = 2 * np.outer(r_h @ h, r_sigma @ y)
        numerator[chart.H_SLICE, chart.SIGMA_SLICE] += cross
        numerator[chart.SIGMA_SLICE, chart.H_SLICE] += cross.T

    payload = hashlib.sha256(
        np.asarray(numerator, dtype="<i8").tobytes()
    ).hexdigest()
    if not (
        np.array_equal(numerator, numerator.T)
        and np.count_nonzero(numerator) == 312
        and set(int(value) for value in np.unique(numerator)) == {-8, -2, 0, 2, 8}
        and payload == EXPECTED_SIGNED_CURRENT_NUMERATOR_SHA256
    ):
        raise ArithmeticError("the exact signed-current Hessian numerator drifted")
    return {
        "integer_matrix": numerator,
        "H_raw_target": h,
        "Sigma_raw_target": y,
        "H_generators": h_generators,
        "Sigma_generators": sigma_generators,
        "report": {
            "raw_Hessian_denominator": 200,
            "generator_count": len(h_generators),
            "integer_nonzero_count": int(np.count_nonzero(numerator)),
            "integer_entry_set": [int(value) for value in np.unique(numerator)],
            "payload_sha256": payload,
            "source_derivation_exact": True,
        },
    }


def exact_candidate_and_global_sos() -> dict[str, Any]:
    """Bind the beta-zero 51-vector and its explicit full-field SOS."""
    pd = pd_source.build_report()
    phi = phi_global.certificate()
    chiral = hsx.exact_phi_h_chiral_square_certificate()
    h10 = h10_source.build_report()
    o6_covariance = o6_source.exact_covariance_psd_and_uv_certificate()
    coefficients = dict(hsx.symbolic_coefficient_map())
    removed = coefficients.pop("lambda::O35_B02_H_Sigma_hermitian")
    contract = set(g2_audit.contract_selection()["parameter_ids"])
    if not (
        removed == "1/20"
        and len(coefficients) == 27
        and set(coefficients) <= contract
        and pd["n_failed"] == 0
        and pd["checks"]["global_lower_bound_exact"]
        and pd["checks"]["target_saturates_global_lower_bound_exactly"]
        and phi["scope"]["global_real_zero_locus_classified"]
        and chiral["source_binding_exact"]
        and h10["n_failed"] == 0
        and o6_covariance["global_PSD"] == "gamma O6>=0 for gamma>=0"
    ):
        raise ArithmeticError("the beta-zero global-SOS source chain failed")

    # In the pure-channel basis I1=|H.H|^2/10 and
    # I54=N_H^2-|H.H|^2/10.  Thus 11 I1+I54=N_H^2+|H.H|^2.
    if coefficients["lambda::O36_B01_H_self_quartics"] != "11" or coefficients[
        "lambda::O36_B02_H_self_quartics"
    ] != "1":
        raise ArithmeticError("the H self-square coefficients drifted")

    return {
        "model_contract_id": hsx.MODEL_CONTRACT_ID,
        "renormalizable_nonzero_parameter_count": len(coefficients),
        "all_renormalizable_parameters_in_authoritative_51_contract": True,
        "removed_signed_current_coefficient": {
            "parameter": "lambda::O35_B02_H_Sigma_hermitian",
            "old_value": removed,
            "new_value": "0",
        },
        "EFT_operator": {
            "formula": "gamma||A_H Sigma||^2",
            "Wilson_coefficient": "kappa=gamma/Lambda_EFT^2",
            "normalized_exact_point": "gamma=1/20, Lambda_EFT=1",
            "field_degree": 6,
            "field_content": "H^2 Hdag^2 Sigma Sigmadag",
            "inside_renormalizable_51_parameter_contract": False,
            "SO10_x_U1X_x_PQ_invariant": True,
            "nonnegative_for_all_fields": True,
        },
        "exact_full_field_gap": {
            "Phi_Sigma_part": pd["SOS_decomposition"]["formula"],
            "H_part": "(N_H-1)^2-1+|H.H|^2",
            "Phi_H_part": "2||P_chi(H wedge Phi)||^2",
            "S_part": "(|S|^2-1/25)^2-1/625",
            "Phi17_part": "(1/32)(|Phi17|^2-1)^2-1/32",
            "EFT_part": "(1/20)||A_H Sigma||^2",
            "all_omitted_terms": "none",
            "sum_of_nonnegative_residuals_plus_constant": True,
        },
        "global_lower_bound": "-1-r^4/8-1-1/625-1/32 at r=1/5",
        "selected_target_saturates_every_residual": True,
        "bounded_below_for_arbitrary_486_real_fields": True,
        "stationary_from_zero_residuals": True,
    }


@lru_cache(maxsize=1)
def _compiled_beta_zero() -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    state = hsx.candidate_state()
    q = chart.pack(state)
    selection = g2_audit.contract_selection()
    values = potential.evaluate_directions(state)
    by_direction = {row.direction_id: row for row in values}
    owners = g2_audit._adapter_modules_by_family()
    direction_rows = tuple(
        owners[by_direction[direction_id].base_family].direction_derivative(
            q, by_direction[direction_id]
        )
        for direction_id in sorted(selection["direction_ids"])
    )
    parameter_rows = derivatives.parameter_derivatives(direction_rows)
    by_parameter = {row.parameter_id: row for row in parameter_rows}
    coefficients = dict(hsx.numerical_coefficient_map())
    coefficients.pop("lambda::O35_B02_H_Sigma_hermitian")
    gradient = np.zeros(chart.TOTAL_DIM, dtype=float)
    hessian = np.zeros((chart.TOTAL_DIM, chart.TOTAL_DIM), dtype=float)
    for parameter_id, coefficient in coefficients.items():
        row = by_parameter[parameter_id]
        gradient += coefficient * np.asarray(row.gradient).real
        hessian += coefficient * np.asarray(row.hessian).real
    return gradient, 0.5 * (hessian + hessian.T), {
        "direction_row_count": len(direction_rows),
        "parameter_row_count": len(parameter_rows),
        "nonzero_renormalizable_parameter_count": len(coefficients),
    }


@lru_cache(maxsize=1)
def exact_current_kernel_jacobian() -> dict[str, Any]:
    """Construct J=d(A_H Sigma) on the fixed raw coordinate lattice."""
    exact_current = exact_signed_current_hessian_numerator()
    h = exact_current["H_raw_target"]
    y = exact_current["Sigma_raw_target"]
    integer = np.zeros((chart.SIGMA_REAL_DIM, chart.TOTAL_DIM), dtype=np.int64)
    for r_h, r_sigma in zip(
        exact_current["H_generators"],
        exact_current["Sigma_generators"],
        strict=True,
    ):
        h_quadratic = int(h @ r_h @ h)
        if h_quadratic % 2:
            raise ArithmeticError("a selected H current was not half-integral")
        integer[:, chart.H_SLICE] += np.outer(r_sigma @ y, r_h @ h)
        integer[:, chart.SIGMA_SLICE] += (h_quadratic // 2) * r_sigma

    # Independent live realification cross-check.  This does not choose any
    # integer cell: the matrix above was constructed in exact integer algebra.
    q = chart.pack(hsx.candidate_state())
    h_live = q[chart.H_SLICE]
    sigma = q[chart.SIGMA_SLICE]
    h_matrices, sigma_matrices = current_source.current_hessians()
    h_currents = 0.5 * np.einsum(
        "i,gij,j->g", h_live, h_matrices, h_live, optimize=True
    )
    a_h = np.einsum(
        "g,gij->ij", np.conjugate(h_currents), sigma_matrices, optimize=True
    )
    a_h = 0.5 * (a_h + a_h.T)
    h_images = np.einsum("gij,j->gi", h_matrices, h_live, optimize=True)
    live_jacobian = np.zeros((chart.SIGMA_REAL_DIM, chart.TOTAL_DIM), dtype=float)
    live_jacobian[:, chart.SIGMA_SLICE] = a_h.real
    for index in range(chart.H_REAL_DIM):
        derivative = np.einsum(
            "g,gij->ij",
            np.conjugate(h_images[:, index]),
            sigma_matrices,
            optimize=True,
        )
        derivative = 0.5 * (derivative + derivative.T)
        if np.max(np.abs(derivative.imag), initial=0.0) != 0.0:
            raise ArithmeticError("a current-operator derivative left the real chart")
        live_jacobian[:, chart.H_SLICE.start + index] = derivative.real @ sigma

    residual = a_h @ sigma
    scale = hessian_source.raw_coordinate_scale()
    scaled_live = live_jacobian * scale[None, :] * RAW_JACOBIAN_DENOMINATOR
    live_crosscheck_residual = float(
        np.max(np.abs(scaled_live - integer), initial=0.0)
    )
    payload = hashlib.sha256(np.asarray(integer, dtype="<i8").tobytes()).hexdigest()
    if not (
        np.max(np.abs(a_h.imag), initial=0.0) == 0.0
        and np.max(np.abs(residual), initial=0.0) == 0.0
        and live_crosscheck_residual == 0.0
        and set(np.unique(integer)) == {-1, 0, 1}
        and np.count_nonzero(integer) == 220
        and payload == EXPECTED_JACOBIAN_SHA256
    ):
        raise ArithmeticError("the EFT residual Jacobian lattice drifted")
    return {
        "integer_matrix": integer,
        "report": {
            "definition": "R(H,Sigma)=A_H Sigma",
            "current_convention": (
                "K_H=sum_g conjugate(Hdag T_10^g H)T_126bar^g is Hermitian; "
                "A_H is its canonical realification, with no extra factor of i"
            ),
            "I45_identity": "I45(H,Sigma)=<Sigma,A_H Sigma>",
            "selected_residual_max_abs": float(
                np.max(np.abs(residual), initial=0.0)
            ),
            "selected_first_jet_reason": "R=0 implies d||R||^2=2<J,R>=0",
            "raw_coordinate_denominator": RAW_JACOBIAN_DENOMINATOR,
            "exact_integer_source_derivation": True,
            "live_realification_crosscheck_residual": live_crosscheck_residual,
            "integer_nonzero_count": int(np.count_nonzero(integer)),
            "integer_entry_set": [int(value) for value in np.unique(integer)],
            "full_Jacobian_rank_mod_1000003": _rank_mod(integer, 1_000_003),
            "payload_sha256": payload,
        },
    }


@lru_cache(maxsize=1)
def exact_stabilized_hessian() -> dict[str, Any]:
    """Prove PSD and rank by an exact kernel-intersection certificate."""
    lattice = hessian_source.exact_source_lattice_derivation_certificate()
    if not (
        lattice["source_binding_exact"]
        and hessian_source.RAW_HESSIAN_DENOMINATOR
        == RAW_HESSIAN_DENOMINATOR
    ):
        raise ArithmeticError("the base Hessian lattice source drifted")
    original_integer, original_lattice = hessian_source.exact_raw_numerator()
    original_payload = hashlib.sha256(
        np.asarray(original_integer, dtype="<i8").tobytes()
    ).hexdigest()
    current_data = exact_signed_current_hessian_numerator()
    current_numerator = current_data["integer_matrix"]
    current_denominator = current_data["report"]["raw_Hessian_denominator"]
    removal_denominator = REMOVED_BETA_DENOMINATOR * current_denominator
    if RAW_HESSIAN_DENOMINATOR % removal_denominator:
        raise ArithmeticError("the signed-current subtraction left the exact lattice")
    if REMOVED_BETA_NUMERATOR != 1:
        raise ArithmeticError("the exact signed-current subtraction assumes numerator one")
    removal_factor = RAW_HESSIAN_DENOMINATOR // removal_denominator
    current_contribution = removal_factor * current_numerator
    current_contribution_payload = hashlib.sha256(
        np.asarray(current_contribution, dtype="<i8").tobytes()
    ).hexdigest()
    base_integer = original_integer - current_contribution

    # This float compilation is an independent diagnostic only.  It neither
    # selects the exact base numerator nor enters the PSD/rank proof.
    gradient, hessian, compiler = _compiled_beta_zero()
    scale = hessian_source.raw_coordinate_scale()
    scaled_gradient = gradient * scale * RAW_HESSIAN_DENOMINATOR
    scaled_hessian = (
        hessian * scale[:, None] * scale[None, :] * RAW_HESSIAN_DENOMINATOR
    )
    float_base_crosscheck = float(
        np.max(np.abs(scaled_hessian - base_integer), initial=0.0)
    )
    float_gradient_crosscheck = float(
        np.max(np.abs(scaled_gradient), initial=0.0)
    )
    components = hessian_source.support_components(base_integer, tolerance=0.0)
    ldl = tuple(
        hessian_source._exact_psd_ldl_block(
            base_integer[np.ix_(component, component)]
        )
        for component in components
    )
    base_psd = all(row["PSD"] for row in ldl)
    base_rank = sum(int(row["rank"] or 0) for row in ldl) if base_psd else None
    base_nullity = chart.TOTAL_DIM - base_rank if base_rank is not None else None

    jacobian_data = exact_current_kernel_jacobian()
    jacobian = jacobian_data["integer_matrix"]
    # ||R||^2=(1/2)||R_real||^2, so at R=0 the real Hessian is
    # gamma J_real^T J_real.  With J_raw=J_integer/10 and gamma=1/20,
    # the common-denominator numerator is D/2000 times J^T J.
    eft_denominator = GAMMA_DENOMINATOR * RAW_JACOBIAN_DENOMINATOR**2
    if RAW_HESSIAN_DENOMINATOR % eft_denominator:
        raise ArithmeticError("the EFT Hessian left the exact lattice")
    if GAMMA_NUMERATOR != 1:
        raise ArithmeticError("the exact EFT Hessian factor assumes numerator one")
    eft_integer_factor = RAW_HESSIAN_DENOMINATOR // eft_denominator
    stabilized = base_integer + eft_integer_factor * (jacobian.T @ jacobian)
    base_payload = hashlib.sha256(
        np.asarray(base_integer, dtype="<i8").tobytes()
    ).hexdigest()
    stabilized_payload = hashlib.sha256(
        np.asarray(stabilized, dtype="<i8").tobytes()
    ).hexdigest()
    if EXPECTED_BASE_HESSIAN_SHA256 and base_payload != EXPECTED_BASE_HESSIAN_SHA256:
        raise ArithmeticError("the beta-zero Hessian payload drifted")
    if (
        EXPECTED_STABILIZED_HESSIAN_SHA256
        and stabilized_payload != EXPECTED_STABILIZED_HESSIAN_SHA256
    ):
        raise ArithmeticError("the stabilized Hessian payload drifted")

    tangent, tangent_metadata = hessian_source.exact_symmetry_tangent_matrix()
    base_tangent_residual = int(
        np.max(np.abs(base_integer @ tangent), initial=0)
    )
    jacobian_tangent_residual = int(
        np.max(np.abs(jacobian @ tangent), initial=0)
    )
    stacked = np.vstack((base_integer, jacobian))
    ranks_mod = {str(prime): _rank_mod(stacked, prime) for prime in MODULAR_PRIMES}
    if not (
        lattice["source_binding_exact"]
        and original_lattice["numerator_symmetric"]
        and original_lattice["float_compiler_crosscheck_half_lattice_margin"] > 0.49
        and original_payload == EXPECTED_ORIGINAL_HESSIAN_SHA256
        and current_contribution_payload
        == "9e905164008449400464f33fee72d158808aff3c90490efa7d5ec2bdc79f4316"
        and np.array_equal(base_integer, base_integer.T)
        and base_psd
        and base_rank == EXPECTED_BASE_RANK
        and base_nullity == EXPECTED_BASE_NULLITY
        and tangent_metadata["source_binding"]
        and tangent_metadata["exact_rank"] == EXPECTED_FINAL_NULLITY
        and base_tangent_residual == 0
        and jacobian_tangent_residual == 0
        and all(rank == EXPECTED_FINAL_RANK for rank in ranks_mod.values())
        and np.array_equal(stabilized, stabilized.T)
    ):
        raise ArithmeticError("the exact stabilized-Hessian proof failed")

    return {
        "raw_coordinate_congruence": (
            "qPhi=x/sqrt(10), qH=u, qSigma=y/10, "
            "qS=sqrt(2)s/5, qPhi17=sqrt(2)z"
        ),
        "fixed_Hessian_denominator": RAW_HESSIAN_DENOMINATOR,
        "compiler": compiler,
        "exact_beta_zero_source": {
            "construction": (
                "source-bound beta=1/20 integer Hessian minus the exact "
                "coefficient-(1/20) signed-current Hessian numerator"
            ),
            "original_payload_sha256": original_payload,
            "signed_current_raw_denominator": current_denominator,
            "signed_current_coefficient": "1/20",
            "integer_subtraction_factor": removal_factor,
            "signed_current_contribution_payload_sha256": (
                current_contribution_payload
            ),
            "float_compiler_is_crosscheck_only": True,
            "float_base_scaled_crosscheck_max_abs": float_base_crosscheck,
            "float_gradient_scaled_crosscheck_max_abs": float_gradient_crosscheck,
        },
        "beta_zero_base": {
            "exact_PSD": base_psd,
            "exact_rank": base_rank,
            "exact_nullity": base_nullity,
            "support_component_count": len(components),
            "support_component_sizes": [len(component) for component in components],
            "maximum_LDL_numerator_bits": max(
                row["maximum_intermediate_numerator_bits"] for row in ldl
            ),
            "maximum_LDL_denominator_bits": max(
                row["maximum_intermediate_denominator_bits"] for row in ldl
            ),
            "payload_sha256": base_payload,
        },
        "EFT_Jacobian": jacobian_data["report"],
        "kernel_intersection": {
            "stack": "vertical stack of the beta-zero Hessian and integer J",
            "ranks_mod_primes": ranks_mod,
            "exact_symmetry_tangent_rank": tangent_metadata["exact_rank"],
            "base_tangent_residual": base_tangent_residual,
            "Jacobian_tangent_residual": jacobian_tangent_residual,
            "proof": (
                "modular rank 448 is a rational lower bound; the 38 independent "
                "symmetry tangents lie in both kernels and give the matching upper bound"
            ),
            "exact_intersection_nullity": EXPECTED_FINAL_NULLITY,
            "six_nonsymmetry_base_flats_lifted": True,
        },
        "stabilized": {
            "kappa": "gamma/Lambda_EFT^2",
            "normalized_exact_point": "gamma=1/20, Lambda_EFT=1",
            "raw_integer_formula": "Hgamma_integer=H0_integer+12600 J^T J",
            "realification_normalization": (
                "||R||^2=(1/2)||R_real||^2, hence Hessian=gamma J^T J"
            ),
            "sum_of_PSD_matrices": True,
            "exact_rank": EXPECTED_FINAL_RANK,
            "exact_nullity": EXPECTED_FINAL_NULLITY,
            "strict_on_448_dimensional_physical_quotient": True,
            "payload_sha256": stabilized_payload,
        },
    }


def exact_global_equality_orbit() -> dict[str, Any]:
    """Classify every equality of the enlarged global SOS."""
    phi = phi_global.certificate()
    old_equality = equality_source.build_report()
    fixed = hsx.fixed_f_mixed_kernel_global_certificate()
    orbit = hsx.exact_orbit_rank_certificate()
    o6 = o6_source.exact_plucker_restriction_certificate()
    plucker = old_equality["fixed_F_Plucker_classification"]
    negative = old_equality["negative_F_mixed_exclusion"]
    source_audit = fixed["source_audit"]
    if not (
        phi["scope"]["global_real_zero_locus_classified"]
        and plucker["fixed_F_Sigma_equality_is_one_orbit"]
        and negative["minus_F_global_equality_branch_excluded"]
        and source_audit["desired_chirality_wedge_coefficient_identity_exact"]
        and source_audit["chirality_cross_coefficient_tensor_zero_exact"]
        and fixed["equality_is_one_SU5_orbit"]
        and o6["all_canonical_polynomial_coefficients_exact"]
        and o6["exact_global_identity"]
        == "||K_H Sigma(z)||^2=||h||^2 ||h wedge z||^2"
        and o6["zero_condition"]
        == "for N_H>0 and decomposable z, O6=0 iff h wedge z=0"
        and o6["preserves_selected_global_equality_orbit"]
        and orbit["source_binding_exact"]
        and orbit["SO10_plus_U1X_plus_PQ_rank"] == 38
    ):
        raise ArithmeticError("the global equality-orbit source chain failed")
    return {
        "step_1_Phi": (
            "Phi residual zero and NPhi=1 imply Phi in SO10.F union SO10.(-F)"
        ),
        "step_2_signed_sheet": (
            "the -F mixed operator is invertible, while NSigma=1/25; hence only +F"
        ),
        "step_3_Sigma": (
            "at +F, mixed and Sigma-self zeros are normalized decomposable "
            "z in Lambda^2(C^5), one U(5) orbit"
        ),
        "step_4_H_chirality": (
            "the Hodge square forces h_minus=0 and (NH-1)^2 fixes ||h_plus||=1"
        ),
        "step_5_EFT_flag": {
            "exact_norm_identity": o6["exact_global_identity"],
            "coefficientwise_integer_guard": o6[
                "all_canonical_polynomial_coefficients_exact"
            ],
            "EFT_zero_equivalence": (
                "K_H Sigma(z)=0 iff h_plus wedge z=0 iff the H line lies "
                "in the two-plane of z"
            ),
            "orbit": "normalized incident line-in-two-plane flags form one SU5 orbit",
        },
        "step_6_phases": (
            "the central U5 action together with U1X and accidental PQ removes "
            "the Sigma, H, S and Phi17 phases; no phase modulus remains"
        ),
        "selected_full_symmetry_orbit_rank": orbit[
            "SO10_plus_U1X_plus_PQ_rank"
        ],
        "selected_stabilizer": "SU(3)_C x U(1)_em",
        "complete_global_equality_set": (
            "one SO(10) x U(1)_X x U(1)_PQ orbit of "
            "(F,H_chi,(1/5)Delta_R,S=1/5,Phi17=1)"
        ),
        "global_equality_orbit_classification_complete": True,
    }


def build_report() -> dict[str, Any]:
    core = {
        "status": STATUS,
        "dependencies": exact_dependency_guard(),
        "candidate_and_global_SOS": exact_candidate_and_global_sos(),
        "exact_stabilized_Hessian": exact_stabilized_hessian(),
        "exact_global_equality_orbit": exact_global_equality_orbit(),
        "scope_boundary": {
            "authoritative_renormalizable_51_parameter_model": False,
            "EFT_dimension_six_extension": True,
            "EFT_scale_matching_performed": False,
            "radiative_stability_performed": False,
            "G4_closed": False,
        },
        "closure_flags": {
            "arbitrary_486_real_field_global_lower_bound": True,
            "selected_target_global_minimum": True,
            "global_equality_orbit_unique_mod_declared_symmetries": True,
            "selected_target_exact_stationary": True,
            "full_Hessian_PSD_rank_448_nullity_38": True,
            "strict_local_minimum_on_physical_quotient": True,
            "G3_closed_for_EFT_extended_model": True,
            "G3_closed_for_original_renormalizable_model": False,
            "G4_closed": False,
        },
    }
    core["core_sha256"] = _canonical_sha256(core)
    return core


def _markdown(report: dict[str, Any]) -> str:
    hessian = report["exact_stabilized_Hessian"]
    base = hessian["beta_zero_base"]
    final = hessian["stabilized"]
    return "\n".join(
        (
            "# Exact EFT current-kernel stabilized global G3",
            "",
            f"- Status: `{report['status']}`",
            f"- Core SHA-256: `{report['core_sha256']}`",
            "- EFT operator: `kappa ||K_H Sigma||^2`, with "
            "`kappa=(1/20)/Lambda_EFT^2` (the exact Hessian uses `Lambda_EFT=1`).",
            "- Scope: dimension-six EFT extension; not the original renormalizable "
            "51-parameter model; G4 is not claimed.",
            "",
            "## Exact global result",
            "",
            "The beta-zero renormalizable potential is an explicit global sum of "
            "squares. The EFT term is gauge invariant and nonnegative, vanishes "
            "with its first jet at the selected vacuum, and its exact Pluecker "
            "restriction selects the incident line-in-two-plane flag. The complete "
            "zero set is one declared symmetry orbit.",
            "",
            "## Exact local result",
            "",
            f"- Beta-zero Hessian: PSD, rank {base['exact_rank']}, "
            f"nullity {base['exact_nullity']}.",
            f"- Stabilized Hessian: PSD, rank {final['exact_rank']}, "
            f"nullity {final['exact_nullity']}.",
            "- The exact modular kernel-intersection certificate proves that the "
            "six nonsymmetry beta-zero flats are lifted and the remaining 38 zero "
            "modes are precisely the symmetry tangents.",
            f"- Base payload: `{base['payload_sha256']}`",
            f"- Stabilized payload: `{final['payload_sha256']}`",
            "",
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--allow-unfrozen", action="store_true")
    parser.add_argument("--write", action="store_true")
    arguments = parser.parse_args()
    report = build_report()
    if not arguments.allow_unfrozen and report["core_sha256"] != EXPECTED_CORE_SHA256:
        raise ArithmeticError(
            f"core hash drift {report['core_sha256']} != {EXPECTED_CORE_SHA256}"
        )
    if arguments.write:
        OUT_JSON.write_text(
            json.dumps(_jsonable(report), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        OUT_MD.write_text(_markdown(report), encoding="utf-8")
    print(json.dumps(_jsonable(report), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
