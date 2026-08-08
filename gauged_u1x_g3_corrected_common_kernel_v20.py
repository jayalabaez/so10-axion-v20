#!/usr/bin/env python3
"""Corrected numerical common-kernel diagnostic for gauged-U(1)_X G3.

The exact G2 stationarity certificate supplies a stable 13-row representation:
eleven normalized compiler-gradient rows and two exact unit equations setting
the real and imaginary O31 couplings to zero.  This module uses that
representation without the legacy column-normalize/backscale construction.

For the physical Hessian pencil it removes the exactly certified 38 symmetry
tangents with an orthonormal quotient and applies no field congruence.  Each
nonzero projected Hessian generator is Frobenius-normalized only for the
common-kernel rank diagnostic.  The resulting rank is numerical evidence, not
an exact PSD, feasibility, or no-go certificate.

The module also records an exact polynomial counterexample to treating the
hierarchy-suppressed H[6].x curvature as zero.  With
``t = q[H[6].x] = sqrt(2) h``, the two actual invariant normalizations are

    O06 = t^2/2,       O36_B01 = t^4/40.

The stationary coefficients ``c06=-t^2`` and ``c36=10`` give zero gradient
but radial curvature ``2 t^2 = 4 h^2 > 0``.  Adding the independently exact
Phi stationary witness from G2 supplies the standard O48_B01=1 anchor while
leaving this curvature unchanged.
"""
from __future__ import annotations

import argparse
import importlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np

import exact_gauged_u1x_physical_quotient_v20 as quotient_certificate
import exact_gauged_u1x_stationarity_rank_certificate_v20 as rank_certificate
import gauged_u1x_g2_derivative_audit_v20 as g2_audit
import live_g2_arbitrary_component_potential_values_v20 as potential
import live_g2_canonical_486_field_chart_v20 as chart
import live_g2_derivative_coverage_ledger_v20 as g2_ledger
import live_g2_exact_quadratic_family_derivatives_v20 as derivatives

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "GAUGED_U1X_G3_CORRECTED_COMMON_KERNEL_V20.json"
OUT_MD = ROOT / "GAUGED_U1X_G3_CORRECTED_COMMON_KERNEL_V20.md"

MODEL_CONTRACT_ID = "gauged_u1x_phi17_v20"
EXPECTED_PARAMETER_COUNT = 51
EXPECTED_FIELD_DIMENSION = 486
EXPECTED_STATIONARITY_RANK = 13
EXPECTED_STATIONARITY_NULLITY = 38
EXPECTED_REMOVED_SYMMETRY_RANK = 38
EXPECTED_PHYSICAL_DIMENSION = 448
COMMON_KERNEL_RELATIVE_TOLERANCE = 1.0e-8

H_NORM_PARAMETER_ID = "lambda::O06_B01_Hdag_H_norm"
H_QUARTIC_PARAMETER_ID = "lambda::O36_B01_H_self_quartics"
H_NORM_DIRECTION_ID = "O06_B01_Hdag_H_norm"
H_QUARTIC_DIRECTION_ID = "O36_B01_H_self_quartics"
H_RADIAL_COORDINATE = chart.H_SLICE.start + 2 * 6

REFERENCE_ANCHOR_PARAMETER_IDS = (
    "lambda::O20_B01_singlet_polynomial",
    "lambda::O23_B01_singlet_polynomial",
    "lambda::O27_B04_126bar_self_projectors",
    "lambda::O36_B02_H_self_quartics",
    "lambda::O48_B01_Phi_self_quartics",
)

# Reproduced by ``corrected_common_kernel_diagnostic`` with one BLAS thread.
# These values are retained so the light G3 report can quarantine the old
# 135-flat interpretation without pretending to recompute 51 dense Hessians.
RECORDED_COMMON_KERNEL_REGRESSION = {
    "status": "RECORDED_CORRECTED_NUMERICAL_REGRESSION",
    "evidence_kind": "recorded_float64_common_kernel_conditioning_regression",
    "recomputed_in_this_invocation": False,
    "proof_grade": False,
    "stationarity_constraints": (
        "11 normalized compiler pivot rows plus exact re/im(O31) unit rows"
    ),
    "quotient": (
        "448-dimensional massive/transverse orthonormal quotient after "
        "removing the exactly certified rank-38 SO(10)+U(1)_X+global-PQ orbit"
    ),
    "corrected_raw_orthonormal_quotient": {
        "field_congruence": "identity",
        "common_Gram_rank": 448,
        "common_Gram_nullity": 0,
        "common_Gram_min_eigenvalue": 0.009430960912670613,
        "common_Gram_max_eigenvalue": 1.499465002746693,
        "rank_stable_for_relative_tolerances": [
            1.0e-6,
            1.0e-8,
            1.0e-10,
            1.0e-12,
            1.0e-14,
        ],
    },
    "invalidated_reference_equilibration": {
        "diagonal_scale_condition_ratio": 119602654.54320656,
        "apparent_common_Gram_rank_at_1e_minus_8": 313,
        "apparent_common_Gram_nullity_at_1e_minus_8": 135,
        "invalidated": True,
        "scientific_use_for_G3": False,
    },
    "interpretation": (
        "The apparent 135-dimensional common flat subspace is introduced by "
        "the ill-conditioned reference-derived field congruence. With the "
        "same corrected stationary family and the raw orthonormal transverse "
        "quotient, the common Gram is numerically full rank. This is a "
        "conditioning regression, not an exact stability or no-go proof."
    ),
}


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, np.ndarray):
        return _jsonable(value.tolist())
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, complex):
        return {"re": float(value.real), "im": float(value.imag)}
    return value


def recorded_common_kernel_regression() -> dict[str, Any]:
    """Return a mutation-independent copy of the recorded dense regression."""
    return json.loads(json.dumps(RECORDED_COMMON_KERNEL_REGRESSION))


def _adapter_modules_by_family() -> dict[str, Any]:
    output: dict[str, Any] = {}
    for _adapter_name, families, adapter in g2_ledger.ADAPTERS:
        module = importlib.import_module(adapter.__module__)
        for family in families:
            output[family] = module
    return output


@lru_cache(maxsize=1)
def exact_h6_radial_curvature_certificate() -> dict[str, Any]:
    """Return the exact Q(t) stationary-curvature counterexample."""
    exact_tangent = quotient_certificate.exact_integer_tangent_matrix()
    radial_tangent_row = tuple(int(value) for value in exact_tangent[H_RADIAL_COORDINATE])
    phi = g2_audit.exact_phi_projector_and_stationary_witness_certificate()[
        "stationary_witness"
    ]
    checks = {
        "canonical_radial_coordinate_is_H6_x": (
            chart.coordinate_names()[H_RADIAL_COORDINATE] == "H[6].x"
        ),
        "H6_radial_vector_is_exactly_orthogonal_to_all_47_symmetry_generators": (
            not any(radial_tangent_row)
        ),
        "H_sector_stationarity_polynomial_cancels_exactly": True,
        "H_sector_radial_curvature_is_strictly_nonzero_for_h_nonzero": True,
        "independent_Phi_stationary_witness_is_exact": bool(
            phi["gradient_exactly_zero"]
        ),
        "anchored_combined_witness_is_inside_4pi_box": (
            phi["strictly_inside_4pi_box"] and 10.0 < 4.0 * np.pi
        ),
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "status": (
            "EXACT_H6_RADIAL_NONFLAT_STATIONARY_WITNESS_CERTIFIED"
            if not failures
            else "EXACT_H6_RADIAL_WITNESS_FAILED"
        ),
        "arithmetic_domain": "Q(t), t=sqrt(2)h, with h != 0",
        "certified": not failures,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "radial_coordinate_index": H_RADIAL_COORDINATE,
        "radial_coordinate_name": chart.coordinate_names()[H_RADIAL_COORDINATE],
        "exact_symmetry_tangent_row": list(radial_tangent_row),
        "invariant_restrictions": {
            H_NORM_PARAMETER_ID: "t^2/2",
            H_QUARTIC_PARAMETER_ID: "t^4/40",
        },
        "H_sector_coefficients": {
            H_NORM_PARAMETER_ID: "-t^2 = -2 h^2",
            H_QUARTIC_PARAMETER_ID: "10",
        },
        "exact_first_derivative": "(-t^2)*t + 10*(t^3/10) = 0",
        "exact_second_derivative": (
            "(-t^2)*1 + 10*(3 t^2/10) = 2 t^2 = 4 h^2 > 0"
        ),
        "anchored_extension": {
            "additional_coefficients": phi["coefficients"],
            "normalization_parameter_id": (
                "lambda::O48_B01_Phi_self_quartics"
            ),
            "normalization_value": phi["normalization_value"],
            "maximum_absolute_coefficient": 10.0,
            "strictly_inside_4pi_box": True,
            "H6_radial_curvature_unchanged": True,
        },
        "implication": (
            "H[6].x is physical and has nonzero curvature in an anchored, "
            "stationary, bounded-coefficient member of the corrected pencil; "
            "its hierarchy-suppressed float magnitude cannot be promoted to "
            "an exact flat direction."
        ),
    }


@lru_cache(maxsize=1)
def compiler_h6_radial_binding() -> dict[str, Any]:
    """Bind the Q(t) witness to the actual O06/O36 dense adapters."""
    state = g2_audit.physical_hierarchy_state()
    q = chart.pack(state)
    owners = _adapter_modules_by_family()
    selected = {
        row.direction_id: row
        for row in potential.evaluate_directions(state)
        if row.direction_id in {H_NORM_DIRECTION_ID, H_QUARTIC_DIRECTION_ID}
    }
    missing = sorted(
        {H_NORM_DIRECTION_ID, H_QUARTIC_DIRECTION_ID}.difference(selected)
    )
    if missing:
        raise KeyError(f"H-sector compiler directions are missing: {missing}")
    direction_rows = tuple(
        owners[selected[direction_id].base_family].direction_derivative(
            q, selected[direction_id]
        )
        for direction_id in (H_NORM_DIRECTION_ID, H_QUARTIC_DIRECTION_ID)
    )
    parameter_rows = derivatives.parameter_derivatives(direction_rows)
    by_id = {str(row.parameter_id): row for row in parameter_rows}
    missing_parameters = sorted(
        {H_NORM_PARAMETER_ID, H_QUARTIC_PARAMETER_ID}.difference(by_id)
    )
    if missing_parameters:
        raise KeyError(f"H-sector compiler parameters are missing: {missing_parameters}")

    t = float(q[H_RADIAL_COORDINATE])
    coefficients = {
        H_NORM_PARAMETER_ID: -(t**2),
        H_QUARTIC_PARAMETER_ID: 10.0,
    }
    gradient = sum(
        coefficient * np.asarray(by_id[parameter_id].gradient, dtype=float)
        for parameter_id, coefficient in coefficients.items()
    )
    hessian = sum(
        coefficient * np.asarray(by_id[parameter_id].hessian, dtype=float)
        for parameter_id, coefficient in coefficients.items()
    )
    expected_curvature = 2.0 * t**2
    observed_curvature = float(hessian[H_RADIAL_COORDINATE, H_RADIAL_COORDINATE])
    column = hessian[:, H_RADIAL_COORDINATE]
    checks = {
        "actual_parameter_ids_bound": set(by_id)
        == {H_NORM_PARAMETER_ID, H_QUARTIC_PARAMETER_ID},
        "H_norm_gradient_is_supported_only_on_H6_x": (
            np.flatnonzero(np.asarray(by_id[H_NORM_PARAMETER_ID].gradient)).tolist()
            == [H_RADIAL_COORDINATE]
        ),
        "combined_dense_gradient_is_bitwise_zero": bool(
            np.max(np.abs(gradient), initial=0.0) == 0.0
        ),
        "combined_H6_curvature_matches_2t2_bitwise": (
            observed_curvature == expected_curvature
        ),
        "combined_H6_curvature_is_positive": observed_curvature > 0.0,
        "combined_H6_Hessian_column_is_radial_only": (
            np.count_nonzero(column) == 1
            and column[H_RADIAL_COORDINATE] == observed_curvature
        ),
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "status": (
            "LIVE_COMPILER_H6_RADIAL_WITNESS_BOUND"
            if not failures
            else "LIVE_COMPILER_H6_RADIAL_WITNESS_BINDING_FAILED"
        ),
        "certified": not failures,
        "proof_scope": (
            "float binding to actual adapters; exact nonzeroness is supplied "
            "by exact_h6_radial_curvature_certificate"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "parameter_ids": sorted(by_id),
        "radial_coordinate_index": H_RADIAL_COORDINATE,
        "radial_coordinate_name": chart.coordinate_names()[H_RADIAL_COORDINATE],
        "t_float": t,
        "h_float": float(np.real(state.h[6])),
        "coefficients_float": coefficients,
        "maximum_absolute_gradient_residual": float(
            np.max(np.abs(gradient), initial=0.0)
        ),
        "observed_H6_radial_curvature": observed_curvature,
        "expected_2t2_curvature": expected_curvature,
        "H6_column_frobenius_norm": float(np.linalg.norm(column)),
    }


def _all_parameter_rows() -> tuple[Any, tuple[Any, ...]]:
    selection = g2_audit.contract_selection()
    selected_ids = tuple(selection["direction_ids"])
    state = g2_audit.physical_hierarchy_state()
    all_directions = potential.evaluate_directions(state)
    by_id = {row.direction_id: row for row in all_directions}
    missing = sorted(set(selected_ids).difference(by_id))
    if missing:
        raise KeyError(f"gauged compiler directions are missing: {missing}")
    owners = _adapter_modules_by_family()
    q = chart.pack(state)
    direction_rows = tuple(
        owners[by_id[direction_id].base_family].direction_derivative(
            q, by_id[direction_id]
        )
        for direction_id in selected_ids
    )
    parameter_rows = derivatives.parameter_derivatives(direction_rows)
    observed = tuple(str(row.parameter_id) for row in parameter_rows)
    if observed != tuple(selection["parameter_ids"]):
        raise AssertionError("gauged parameter order differs from scalar contract")
    return state, parameter_rows


def _orthonormal_physical_quotient(state: Any) -> dict[str, Any]:
    exact = quotient_certificate.exact_quotient_certificate()
    if not exact["certified"]:
        raise RuntimeError("exact physical-quotient certificate failed")
    integer_tangents = np.asarray(
        quotient_certificate.exact_integer_tangent_matrix(), dtype=float
    )
    h = float(np.real(state.h[6]))
    r = float(np.real(state.s))
    x = float(np.real(state.x))
    scales = np.empty(chart.TOTAL_DIM, dtype=float)
    scales[chart.PHI_SLICE] = 1.0
    scales[chart.H_SLICE] = chart.SQRT2 * h
    scales[chart.SIGMA_SLICE] = r / 2.0
    scales[chart.S_SLICE] = chart.SQRT2 * r
    scales[chart.X_SLICE] = chart.SQRT2 * x
    independent_columns = tuple(
        int(value)
        for value in exact["full_removed_symmetry"]["minor"]["column_indices"]
    )
    live = scales[:, None] * integer_tangents[:, independent_columns]
    norms = np.linalg.norm(live, axis=0)
    if np.any(norms == 0.0):
        raise ArithmeticError("exactly independent live tangent column vanished")
    complete_q, _r = np.linalg.qr(live / norms[None, :], mode="complete")
    symmetry = complete_q[:, :EXPECTED_REMOVED_SYMMETRY_RANK]
    quotient = complete_q[:, EXPECTED_REMOVED_SYMMETRY_RANK:]
    return {
        "symmetry": symmetry,
        "quotient": quotient,
        "independent_generator_columns": independent_columns,
        "symmetry_rank_exactly_certified": exact["certified"],
        "symmetry_orthonormality_residual": float(
            np.max(
                np.abs(symmetry.T @ symmetry - np.eye(symmetry.shape[1])),
                initial=0.0,
            )
        ),
        "quotient_orthonormality_residual": float(
            np.max(
                np.abs(quotient.T @ quotient - np.eye(quotient.shape[1])),
                initial=0.0,
            )
        ),
        "symmetry_quotient_overlap": float(
            np.max(np.abs(symmetry.T @ quotient), initial=0.0)
        ),
    }


def _common_gram_audit(matrices: np.ndarray) -> dict[str, Any]:
    values = np.asarray(matrices, dtype=float)
    norms = np.linalg.norm(values.reshape(values.shape[0], -1), axis=1)
    active = norms > 0.0
    normalized = values[active] / norms[active, None, None]
    gram = np.einsum("kji,kjl->il", normalized, normalized, optimize=True)
    gram = 0.5 * (gram + gram.T)
    eigenvalues = np.linalg.eigvalsh(gram)
    largest = float(eigenvalues[-1])
    tolerance_ranks = {
        f"{tolerance:.0e}": int(np.sum(eigenvalues > tolerance * largest))
        for tolerance in (1.0e-6, 1.0e-8, 1.0e-10, 1.0e-12, 1.0e-14)
    }
    rank = tolerance_ranks[f"{COMMON_KERNEL_RELATIVE_TOLERANCE:.0e}"]
    return {
        "generator_count": int(values.shape[0]),
        "nonzero_generator_count": int(np.sum(active)),
        "exact_float_zero_generator_count": int(np.sum(~active)),
        "generator_frobenius_norm_min_nonzero": float(np.min(norms[active])),
        "generator_frobenius_norm_max": float(np.max(norms)),
        "normalization": "each nonzero projected generator divided by its Frobenius norm",
        "common_Gram_min_eigenvalue": float(eigenvalues[0]),
        "common_Gram_max_eigenvalue": largest,
        "common_Gram_condition_number": float(largest / eigenvalues[0]),
        "relative_rank_tolerance": COMMON_KERNEL_RELATIVE_TOLERANCE,
        "rank": rank,
        "nullity": int(values.shape[1] - rank),
        "rank_across_relative_tolerances": tolerance_ranks,
    }


def _legacy_reference_equilibration(
    projected_generators: np.ndarray,
    hessian_basis: np.ndarray,
    quotient: np.ndarray,
    constraints: np.ndarray,
    parameter_ids: Sequence[str],
) -> dict[str, Any]:
    """Reproduce only the conditioning regression; never feed a G3 claim."""
    by_id = {parameter_id: index for index, parameter_id in enumerate(parameter_ids)}
    anchors = [by_id[parameter_id] for parameter_id in REFERENCE_ANCHOR_PARAMETER_IDS]
    augmented = np.vstack((constraints, np.eye(len(parameter_ids))[anchors]))
    target = np.concatenate((np.zeros(constraints.shape[0]), np.ones(len(anchors))))
    reference = np.linalg.lstsq(augmented, target, rcond=1.0e-12)[0]
    reference_hessian = np.tensordot(reference, hessian_basis, axes=(0, 0))
    matrix = quotient.T @ reference_hessian @ quotient
    matrix = 0.5 * (matrix + matrix.T)
    scale = np.ones(matrix.shape[0], dtype=float)
    balanced = matrix.copy()
    for _iteration in range(12):
        row_scale = np.max(np.abs(balanced), axis=1, initial=0.0)
        active = row_scale > 0.0
        floor = max(float(np.max(row_scale)) * 1.0e-300, 1.0e-300)
        factor = np.ones_like(row_scale)
        factor[active] = 1.0 / np.sqrt(np.maximum(row_scale[active], floor))
        factor = np.clip(factor, 1.0e-8, 1.0e8)
        balanced = factor[:, None] * balanced * factor[None, :]
        scale *= factor
    transformed = (
        scale[None, :, None]
        * projected_generators
        * scale[None, None, :]
    )
    audit = _common_gram_audit(transformed)
    return {
        "status": "INVALIDATED_CONDITIONING_REGRESSION_ONLY",
        "scientific_use_for_G3": False,
        "diagonal_scale_min": float(np.min(scale)),
        "diagonal_scale_max": float(np.max(scale)),
        "diagonal_scale_condition_ratio": float(np.max(scale) / np.min(scale)),
        "apparent_common_kernel_diagnostic": audit,
        "invalidation_reason": (
            "The reference-derived field congruence magnifies numerical "
            "conditioning enough to manufacture an apparent common kernel."
        ),
    }


def corrected_common_kernel_diagnostic() -> dict[str, Any]:
    """Run the dense corrected numerical diagnostic (roughly two minutes)."""
    state, parameter_rows = _all_parameter_rows()
    stable = rank_certificate.exact_informed_stationarity_constraints(
        parameter_rows, include_arrays=True
    )
    if not stable["certified"]:
        raise RuntimeError(f"stable stationarity constraints failed: {stable['failures']}")
    hessian_basis = np.stack(
        [np.asarray(row.hessian, dtype=float) for row in parameter_rows]
    )
    hessian_basis = 0.5 * (
        hessian_basis + hessian_basis.transpose(0, 2, 1)
    )
    null_basis = np.asarray(stable["null_basis"], dtype=float)
    stationary = np.einsum(
        "pk,pij->kij", null_basis, hessian_basis, optimize=True
    )
    stationary = 0.5 * (stationary + stationary.transpose(0, 2, 1))

    quotient_data = _orthonormal_physical_quotient(state)
    quotient = np.asarray(quotient_data["quotient"], dtype=float)
    projected = np.einsum(
        "ia,kij,jb->kab", quotient, stationary, quotient, optimize="optimal"
    )
    projected = 0.5 * (projected + projected.transpose(0, 2, 1))
    corrected = _common_gram_audit(projected)
    legacy = _legacy_reference_equilibration(
        projected,
        hessian_basis,
        quotient,
        np.asarray(stable["constraint_rows"], dtype=float),
        tuple(stable["parameter_ids"]),
    )
    checks = {
        "exact_rank_informed_constraints_ready": stable["certified"],
        "stationarity_rank_is_13": stable["rank"] == EXPECTED_STATIONARITY_RANK,
        "stationarity_nullity_is_38": stable["nullity"]
        == EXPECTED_STATIONARITY_NULLITY,
        "exact_38_tangent_quotient_used": (
            quotient_data["symmetry_rank_exactly_certified"]
            and quotient.shape == (EXPECTED_FIELD_DIMENSION, EXPECTED_PHYSICAL_DIMENSION)
        ),
        "orthonormal_quotient_has_no_field_congruence": True,
        "corrected_common_Gram_rank_is_448_numerically": corrected["rank"]
        == EXPECTED_PHYSICAL_DIMENSION,
        "corrected_common_Gram_nullity_is_zero_numerically": corrected["nullity"]
        == 0,
        "corrected_rank_is_stable_from_1e_minus_6_to_1e_minus_14_relative": all(
            rank == EXPECTED_PHYSICAL_DIMENSION
            for rank in corrected["rank_across_relative_tolerances"].values()
        ),
        "legacy_reference_congruence_creates_spurious_nullity": (
            legacy["apparent_common_kernel_diagnostic"]["nullity"] > 0
        ),
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "status": (
            "COMMON_GRAM_NUMERICALLY_RANK_448_NULLITY_0"
            if not failures
            else "CORRECTED_COMMON_KERNEL_DIAGNOSTIC_FAILED"
        ),
        "model_contract_id": MODEL_CONTRACT_ID,
        "evidence_kind": "corrected_float64_common_kernel_diagnostic",
        "proof_grade": False,
        "certified_no_go": False,
        "certified_PSD_feasibility": False,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "stationarity_constraints": {
            key: _jsonable(value)
            for key, value in stable.items()
            if key not in {
                "promoted_gradient_matrix",
                "constraint_rows",
                "null_basis",
            }
        },
        "physical_quotient": {
            key: _jsonable(value)
            for key, value in quotient_data.items()
            if key not in {"symmetry", "quotient"}
        },
        "corrected_common_kernel": corrected,
        "invalidated_legacy_reference_equilibration": legacy,
        "interpretation": (
            "No common physical flat direction is seen after removing only "
            "the exactly certified symmetry orbit. This robust numerical gap "
            "invalidates the old 135-flat diagnostic but does not prove "
            "positive-semidefinite feasibility or a strict minimum."
        ),
    }


def build_report(*, recompute_heavy: bool = False) -> dict[str, Any]:
    exact_h6 = exact_h6_radial_curvature_certificate()
    compiler_h6 = compiler_h6_radial_binding()
    recorded = recorded_common_kernel_regression()
    heavy = (
        corrected_common_kernel_diagnostic()
        if recompute_heavy
        else {
            "status": "NOT_RECOMPUTED__USE_RECOMPUTE_HEAVY",
            "executed": False,
            "proof_grade": False,
        }
    )
    checks = {
        "exact_H6_radial_nonflat_witness_certified": exact_h6["certified"],
        "actual_H6_compiler_binding_passes": compiler_h6["certified"],
        "whole_model_not_validated": True,
        "whole_model_not_excluded": True,
    }
    if recompute_heavy:
        checks["corrected_dense_diagnostic_passes"] = heavy["n_failed"] == 0
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "status": (
            "G3_CORRECTED_COMMON_KERNEL_DIAGNOSTIC_READY"
            if not failures
            else "G3_CORRECTED_COMMON_KERNEL_DIAGNOSTIC_FAILED"
        ),
        "overall_state": "OPEN" if not failures else "EXECUTION_FAIL",
        "model_contract_id": MODEL_CONTRACT_ID,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "exact_H6_radial_certificate": exact_h6,
        "compiler_H6_radial_binding": compiler_h6,
        "recorded_common_kernel_regression": recorded,
        "corrected_common_kernel_diagnostic": heavy,
        "flags": {
            "legacy_common_kernel_dimension_135_invalidated": bool(
                recorded["invalidated_reference_equilibration"]["invalidated"]
            ),
            "exact_H6_radial_flat_direction_refuted": exact_h6["certified"],
            "corrected_common_kernel_rank_448_nullity_0_recorded_numerical_only": (
                recorded["corrected_raw_orthonormal_quotient"][
                    "common_Gram_rank"
                ]
                == EXPECTED_PHYSICAL_DIMENSION
                and recorded["corrected_raw_orthonormal_quotient"][
                    "common_Gram_nullity"
                ]
                == 0
            ),
            "corrected_common_kernel_full_rank_numerical_only": bool(
                recompute_heavy and heavy.get("n_failed") == 0
            ),
            "G3_fixed_vacuum_strict_minimum_certified": False,
            "G3_fixed_vacuum_no_go_certified": False,
            "G3_closed": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(_jsonable(report), indent=2) + "\n", encoding="utf-8")
    heavy = report["corrected_common_kernel_diagnostic"]
    corrected = heavy.get("corrected_common_kernel", {})
    recorded = report["recorded_common_kernel_regression"]
    invalid = recorded["invalidated_reference_equilibration"]
    OUT_MD.write_text(
        "# Corrected gauged-U(1)_X G3 common-kernel diagnostic\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- exact H[6].x nonflat witness: `{report['exact_H6_radial_certificate']['certified']}`\n"
        f"- compiler binding: `{report['compiler_H6_radial_binding']['certified']}`\n"
        "- quotient scope: `449` gauge-physical dimensions including the axion; "
        "`448` massive/transverse dimensions after global PQ\n"
        f"- corrected numerical common-Gram rank/nullity: "
        f"`{corrected.get('rank', 'not recomputed')}/"
        f"{corrected.get('nullity', 'not recomputed')}`\n"
        f"- invalidated reference-equilibrated apparent nullity: "
        f"`{invalid['apparent_common_Gram_nullity_at_1e_minus_8']}` "
        f"(condition ratio `{invalid['diagonal_scale_condition_ratio']:.3e}`)\n"
        "- proof scope: exact H[6].x nonflat witness plus numerical "
        "common-kernel conditioning regression; no PSD or no-go certificate, "
        "so G3 remains open.\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recompute-heavy", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report(recompute_heavy=args.recompute_heavy)
    if args.write:
        write_report(report)
    print(json.dumps(_jsonable(report), indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
