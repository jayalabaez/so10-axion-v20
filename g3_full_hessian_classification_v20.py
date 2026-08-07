#!/usr/bin/env python3
"""Exact local G3 Hessian and symmetry-quotient classification.

This is the second G3 layer after the 486x91 stationarity-feasibility gate.
It reuses every exact G2 derivative adapter at the same physical hierarchy
candidate, assembles the stationary witness's dense 486x486 Hessian, removes
the 36 stage-resolved SO(10)->U(1)_EM gauge tangents, removes the independent
global-PQ tangent, and classifies the remaining 449 real directions.

The quotient inertia is evaluated after a diagonal congruence equilibration.
Congruence preserves inertia while avoiding a false loss of the electroweak
and intermediate-scale blocks in a matrix whose physical scales span roughly
28 orders of magnitude.  This module is deliberately local: it does not turn
a positive local Hessian into a global-minimum or boundedness claim.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any, Mapping

import numpy as np

import g3_full_stationarity_feasibility_v20 as first_order
import live_g2_canonical_486_field_chart_v20 as chart
import live_g2_derivative_coverage_ledger_v20 as g2

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "G3_FULL_HESSIAN_CLASSIFICATION_V20.json"
OUT_MD = ROOT / "G3_FULL_HESSIAN_CLASSIFICATION_V20.md"

PQ_CHARGES = {
    "Phi210": 0.0,
    "H10": -2.0,
    "Sigma126bar": -2.0,
    "S": 4.0,
    "Phi17": 0.0,
}


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, np.ndarray):
        return _jsonable(value.tolist())
    if isinstance(value, np.generic):
        return _jsonable(value.item())
    return value


def _orthonormal_image(
    matrix: np.ndarray,
    *,
    relative_tolerance: float = 1.0e-10,
    column_relative_tolerance: float = 0.0,
) -> tuple[np.ndarray, np.ndarray]:
    value = np.asarray(matrix, dtype=float)
    if value.ndim != 2:
        raise ValueError("image matrix must be two-dimensional")
    norms = np.linalg.norm(value, axis=0)
    column_floor = float(column_relative_tolerance) * float(
        np.max(norms, initial=0.0)
    )
    active = norms > column_floor
    if not np.any(active):
        return np.zeros((value.shape[0], 0)), np.asarray([], dtype=float)
    normalized = value[:, active] / norms[active]
    u, singular, _vh = np.linalg.svd(normalized, full_matrices=False)
    threshold = relative_tolerance * singular[0]
    rank = int(np.sum(singular > threshold))
    return u[:, :rank], singular


def stage_resolved_gauge_basis() -> dict[str, Any]:
    """Construct the physical 36-column gauge-orbit basis without scale loss."""
    pre = first_order.physical_candidate(electroweak=False)
    physical = first_order.physical_candidate(electroweak=True)
    pre_orbit = chart.gauge_orbit_matrix(pre)
    physical_orbit = chart.gauge_orbit_matrix(physical)

    pre_basis, pre_singular = _orthonormal_image(pre_orbit)
    pre_rank = pre_basis.shape[1]
    _u, singular_raw, vh = np.linalg.svd(pre_orbit, full_matrices=True)
    raw_threshold = 1.0e-10 * singular_raw[0]
    raw_rank = int(np.sum(singular_raw > raw_threshold))
    if raw_rank != pre_rank:
        raise ArithmeticError(
            f"pre-EW rank disagreement: raw={raw_rank}, normalized={pre_rank}"
        )
    unbroken_generators = vh[pre_rank:, :].T
    increment = (physical_orbit - pre_orbit) @ unbroken_generators
    increment -= pre_basis @ (pre_basis.T @ increment)
    increment_basis, increment_singular = _orthonormal_image(
        increment, column_relative_tolerance=1.0e-10
    )
    combined = np.column_stack((pre_basis, increment_basis))
    gauge_basis, combined_singular = _orthonormal_image(combined)
    return {
        "basis": gauge_basis,
        "pre_rank": pre_rank,
        "increment_rank": int(increment_basis.shape[1]),
        "total_rank": int(gauge_basis.shape[1]),
        "pre_normalized_singular_values": pre_singular,
        "increment_normalized_singular_values": increment_singular,
        "combined_singular_values": combined_singular,
        "orthonormality_residual": float(
            np.max(
                np.abs(
                    gauge_basis.T @ gauge_basis
                    - np.eye(gauge_basis.shape[1])
                ),
                initial=0.0,
            )
        ),
    }


def pq_tangent(state=None) -> np.ndarray:
    """Return d/dalpha of the declared global-PQ action in canonical units."""
    value = state or first_order.physical_candidate(electroweak=True)
    tangent = np.zeros(chart.TOTAL_DIM, dtype=float)

    def complex_block(vector: np.ndarray, charge: float) -> np.ndarray:
        z = np.asarray(vector, dtype=complex).reshape(-1)
        varied = 1j * float(charge) * z
        output = np.empty(2 * z.size, dtype=float)
        output[0::2] = chart.SQRT2 * varied.real
        output[1::2] = chart.SQRT2 * varied.imag
        return output

    tangent[chart.H_SLICE] = complex_block(value.h, PQ_CHARGES["H10"])
    sigma = chart.sigma_coordinates(value.sigma)
    tangent[chart.SIGMA_SLICE] = complex_block(
        sigma, PQ_CHARGES["Sigma126bar"]
    )
    tangent[chart.S_SLICE] = complex_block(
        np.asarray([value.s]), PQ_CHARGES["S"]
    )
    tangent[chart.X_SLICE] = complex_block(
        np.asarray([value.x]), PQ_CHARGES["Phi17"]
    )
    return tangent


def physical_quotient_basis() -> dict[str, Any]:
    gauge = stage_resolved_gauge_basis()
    gauge_basis = np.asarray(gauge["basis"], dtype=float)
    pq = pq_tangent()
    pq_after_gauge = pq - gauge_basis @ (gauge_basis.T @ pq)
    pq_raw_norm = float(np.linalg.norm(pq))
    pq_physical_norm = float(np.linalg.norm(pq_after_gauge))
    if pq_physical_norm <= 0.0:
        raise ArithmeticError("declared global-PQ tangent is entirely gauge-eaten")
    axion = pq_after_gauge / pq_physical_norm
    symmetry = np.column_stack((gauge_basis, axion))
    symmetry_basis, singular = _orthonormal_image(symmetry)
    if symmetry_basis.shape[1] != 37:
        raise ArithmeticError(
            f"expected 36 gauge plus one PQ direction, got {symmetry_basis.shape[1]}"
        )
    _u, _s, vh = np.linalg.svd(symmetry_basis.T, full_matrices=True)
    quotient = vh[symmetry_basis.shape[1] :, :].T
    return {
        "gauge": gauge,
        "axion": axion,
        "symmetry_basis": symmetry_basis,
        "quotient": quotient,
        "pq_raw_norm": pq_raw_norm,
        "pq_after_gauge_norm": pq_physical_norm,
        "pq_gauge_overlap_fraction": float(
            np.linalg.norm(gauge_basis.T @ pq) / max(pq_raw_norm, 1.0e-300)
        ),
        "symmetry_singular_values": singular,
        "symmetry_orthonormality_residual": float(
            np.max(
                np.abs(symmetry_basis.T @ symmetry_basis - np.eye(37)),
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
            np.max(np.abs(symmetry_basis.T @ quotient), initial=0.0)
        ),
    }


def stationary_coefficients() -> dict[str, Any]:
    state = first_order.physical_candidate(electroweak=True)
    parameters = first_order.parameter_gradient_rows(state)
    coefficients = first_order.stationary_coefficient_vector(parameters)
    return {
        "state": state,
        "parameters": parameters,
        "vector": coefficients,
        "map": {
            row.parameter_id: float(coefficient)
            for row, coefficient in zip(parameters, coefficients, strict=True)
        },
    }


def _direction_contribution(
    row, coefficients: Mapping[str, float]
) -> tuple[float, np.ndarray, np.ndarray, tuple[str, ...]]:
    if row.self_conjugate:
        parameter_id = f"lambda::{row.direction_id}"
        coefficient = float(coefficients[parameter_id])
        return (
            coefficient * float(row.value.real),
            coefficient * np.asarray(row.gradient.real, dtype=float),
            coefficient * np.asarray(row.hessian.real, dtype=float),
            (parameter_id,),
        )
    real_id = f"re::{row.direction_id}"
    imag_id = f"im::{row.direction_id}"
    real_coefficient = float(coefficients[real_id])
    imag_coefficient = float(coefficients[imag_id])
    return (
        real_coefficient * 2.0 * float(row.value.real)
        - imag_coefficient * 2.0 * float(row.value.imag),
        real_coefficient * 2.0 * np.asarray(row.gradient.real, dtype=float)
        - imag_coefficient * 2.0 * np.asarray(row.gradient.imag, dtype=float),
        real_coefficient * 2.0 * np.asarray(row.hessian.real, dtype=float)
        - imag_coefficient * 2.0 * np.asarray(row.hessian.imag, dtype=float),
        (real_id, imag_id),
    )


def assemble_exact_hessian(
    state, coefficients: Mapping[str, float]
) -> dict[str, Any]:
    """Stream all ten G2 adapters into one dense witness Hessian."""
    value = 0.0
    gradient = np.zeros(chart.TOTAL_DIM, dtype=float)
    hessian = np.zeros((chart.TOTAL_DIM, chart.TOTAL_DIM), dtype=float)
    seen_directions: set[str] = set()
    seen_parameters: set[str] = set()
    timings: dict[str, float] = {}
    counts: dict[str, int] = {}
    for adapter_name, declared_families, adapter in g2.ADAPTERS:
        started = time.perf_counter()
        rows = tuple(adapter(state))
        timings[adapter_name] = time.perf_counter() - started
        counts[adapter_name] = len(rows)
        observed_families = {row.base_family for row in rows}
        if not observed_families.issubset(set(declared_families)):
            raise AssertionError(
                f"adapter {adapter_name} emitted undeclared families "
                f"{sorted(observed_families.difference(declared_families))}"
            )
        for row in rows:
            if row.direction_id in seen_directions:
                raise AssertionError(f"duplicate G2 direction {row.direction_id}")
            seen_directions.add(row.direction_id)
            row_value, row_gradient, row_hessian, parameter_ids = (
                _direction_contribution(row, coefficients)
            )
            value += row_value
            gradient += row_gradient
            hessian += row_hessian
            seen_parameters.update(parameter_ids)
    missing = set(coefficients).difference(seen_parameters)
    extra = seen_parameters.difference(coefficients)
    if missing or extra:
        raise AssertionError(
            f"G2 parameter partition mismatch: missing={sorted(missing)}, "
            f"extra={sorted(extra)}"
        )
    hessian = 0.5 * (hessian + hessian.T)
    return {
        "value": float(value),
        "gradient": gradient,
        "hessian": hessian,
        "direction_count": len(seen_directions),
        "parameter_count": len(seen_parameters),
        "adapter_direction_counts": counts,
        "adapter_seconds": timings,
        "maximum_hessian_asymmetry": float(
            np.max(np.abs(hessian - hessian.T), initial=0.0)
        ),
    }


def equilibrate_congruence(
    matrix: np.ndarray, *, iterations: int = 12
) -> dict[str, Any]:
    """Diagonally equilibrate a symmetric matrix without changing inertia."""
    balanced = np.asarray(matrix, dtype=float).copy()
    scale = np.ones(balanced.shape[0], dtype=float)
    for _ in range(int(iterations)):
        row_scale = np.max(np.abs(balanced), axis=1, initial=0.0)
        active = row_scale > 0.0
        if not np.any(active):
            break
        floor = max(float(np.max(row_scale)) * 1.0e-300, 1.0e-300)
        factor = np.ones_like(row_scale)
        factor[active] = 1.0 / np.sqrt(np.maximum(row_scale[active], floor))
        factor = np.clip(factor, 1.0e-8, 1.0e8)
        balanced = factor[:, None] * balanced * factor[None, :]
        scale *= factor
    return {
        "matrix": 0.5 * (balanced + balanced.T),
        "diagonal_scale": scale,
        "scale_min": float(np.min(scale)),
        "scale_max": float(np.max(scale)),
        "scale_condition_ratio": float(np.max(scale) / np.min(scale)),
    }


def classify_hessian(hessian: np.ndarray, quotient_data: dict[str, Any]) -> dict[str, Any]:
    gauge = np.asarray(quotient_data["gauge"]["basis"], dtype=float)
    axion = np.asarray(quotient_data["axion"], dtype=float)
    quotient = np.asarray(quotient_data["quotient"], dtype=float)
    projected = quotient.T @ hessian @ quotient
    projected = 0.5 * (projected + projected.T)
    balanced = equilibrate_congruence(projected)
    eigenvalues = np.linalg.eigvalsh(balanced["matrix"])
    spectral_scale = float(np.max(np.abs(eigenvalues), initial=0.0))
    tolerance = max(1.0e-11 * spectral_scale, 1.0e-13)
    negative = eigenvalues < -tolerance
    zero = np.abs(eigenvalues) <= tolerance
    positive = eigenvalues > tolerance
    return {
        "full_shape": list(hessian.shape),
        "gauge_dimension": int(gauge.shape[1]),
        "axion_dimension": 1,
        "massive_physical_dimension": int(quotient.shape[1]),
        "gauge_annihilation_max_abs": float(
            np.max(np.abs(hessian @ gauge), initial=0.0)
        ),
        "axion_annihilation_max_abs": float(
            np.max(np.abs(hessian @ axion), initial=0.0)
        ),
        "projected_symmetry_residual": float(
            np.max(np.abs(projected - projected.T), initial=0.0)
        ),
        "equilibration": {
            key: value
            for key, value in balanced.items()
            if key not in {"matrix", "diagonal_scale"}
        },
        "inertia_tolerance": tolerance,
        "negative_modes": int(np.sum(negative)),
        "additional_zero_modes": int(np.sum(zero)),
        "positive_modes": int(np.sum(positive)),
        "minimum_equilibrated_eigenvalue": float(eigenvalues[0]),
        "maximum_equilibrated_eigenvalue": float(eigenvalues[-1]),
        "most_negative_eigenvalues": eigenvalues[: min(12, len(eigenvalues))],
        "smallest_absolute_eigenvalues": eigenvalues[
            np.argsort(np.abs(eigenvalues))[: min(12, len(eigenvalues))]
        ],
    }


def build_report() -> dict[str, Any]:
    started = time.perf_counter()
    stationary = stationary_coefficients()
    exact = assemble_exact_hessian(stationary["state"], stationary["map"])
    quotient = physical_quotient_basis()
    classification = classify_hessian(exact["hessian"], quotient)

    fast_gradient = np.column_stack(
        [row.gradient for row in stationary["parameters"]]
    ) @ stationary["vector"]
    exact_gradient = np.asarray(exact["gradient"], dtype=float)
    gradient_difference = float(np.linalg.norm(fast_gradient - exact_gradient))
    gradient_scale = max(
        float(np.linalg.norm(fast_gradient)),
        float(np.linalg.norm(exact_gradient)),
    )
    gradient_cross_tolerance = 1.0e-10 + 1.0e-8 * gradient_scale
    gradient_cross_ratio = gradient_difference / gradient_cross_tolerance
    locally_positive = (
        classification["negative_modes"] == 0
        and classification["additional_zero_modes"] == 0
    )
    checks = {
        "all_64_G2_directions_reassembled": exact["direction_count"] == 64,
        "all_91_real_parameters_reassembled": exact["parameter_count"] == 91,
        "dense_Hessian_is_486x486": exact["hessian"].shape == (486, 486),
        "dense_Hessian_is_symmetric": exact["maximum_hessian_asymmetry"] < 1.0e-12,
        "fast_and_dense_stationary_gradients_agree": gradient_cross_ratio <= 1.0,
        "stationary_gradient_remains_zero": float(np.linalg.norm(exact_gradient)) < 1.0e-8,
        "stage_resolved_gauge_rank_is_36": quotient["gauge"]["total_rank"] == 36,
        "global_PQ_is_independent_after_gauge_projection": quotient["pq_after_gauge_norm"] > 0.0,
        "massive_physical_quotient_dimension_is_449": classification["massive_physical_dimension"] == 449,
        "no_negative_physical_modes": classification["negative_modes"] == 0,
        "no_unintended_physical_zero_modes": classification["additional_zero_modes"] == 0,
        "global_minimum_not_inferred_from_local_Hessian": True,
        "complete_BFB_not_inferred_from_local_Hessian": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    execution_failures = [
        name
        for name in failures
        if name
        not in {"no_negative_physical_modes", "no_unintended_physical_zero_modes"}
    ]
    local_state = (
        "STRICT_LOCAL_MINIMUM_MODULO_GAUGE_AND_PQ"
        if locally_positive
        else (
            "PHYSICAL_SADDLE"
            if classification["negative_modes"] > 0
            else "PHYSICAL_FLAT_DIRECTIONS_REMAIN"
        )
    )
    return _jsonable(
        {
            "status": (
                f"G3_FULL_HESSIAN_{local_state}__GLOBAL_BFB_OPEN"
                if not execution_failures
                else "G3_FULL_HESSIAN_EXECUTION_FAILED"
            ),
            "overall_state": "PARTIAL" if not execution_failures else "EXECUTION_FAIL",
            "local_classification": local_state,
            "n_checks": len(checks),
            "n_failed": len(failures),
            "failures": failures,
            "checks": checks,
            "coverage": {
                "base_families": 18,
                "directions": exact["direction_count"],
                "real_parameters": exact["parameter_count"],
                "real_field_dimension": chart.TOTAL_DIM,
            },
            "assembly": {
                "potential_value": exact["value"],
                "stationary_gradient_norm": float(np.linalg.norm(exact_gradient)),
                "stationary_gradient_max_abs": float(
                    np.max(np.abs(exact_gradient), initial=0.0)
                ),
                "fast_dense_gradient_difference_norm": gradient_difference,
                "fast_dense_gradient_mixed_tolerance": gradient_cross_tolerance,
                "fast_dense_gradient_tolerance_ratio": gradient_cross_ratio,
                "maximum_Hessian_asymmetry": exact["maximum_hessian_asymmetry"],
                "adapter_direction_counts": exact["adapter_direction_counts"],
                "adapter_seconds": exact["adapter_seconds"],
                "wall_seconds": time.perf_counter() - started,
            },
            "symmetry_quotient": {
                "gauge": {
                    key: value
                    for key, value in quotient["gauge"].items()
                    if key != "basis"
                },
                "pq_charges": PQ_CHARGES,
                "pq_raw_norm": quotient["pq_raw_norm"],
                "pq_after_gauge_norm": quotient["pq_after_gauge_norm"],
                "pq_gauge_overlap_fraction": quotient["pq_gauge_overlap_fraction"],
                "symmetry_orthonormality_residual": quotient[
                    "symmetry_orthonormality_residual"
                ],
                "quotient_orthonormality_residual": quotient[
                    "quotient_orthonormality_residual"
                ],
                "symmetry_quotient_overlap": quotient[
                    "symmetry_quotient_overlap"
                ],
            },
            "physical_Hessian": classification,
            "flags": {
                "G1_closed": True,
                "G2_closed": True,
                "full_486x486_stationary_Hessian_assembled": not execution_failures,
                "all_36_gauge_directions_quotiented": not execution_failures,
                "intended_PQ_axion_direction_quotiented": not execution_failures,
                "strict_local_physical_minimum": locally_positive,
                "complete_potential_BFB": False,
                "global_competing_extrema_exhausted": False,
                "G3_closed": False,
                "whole_model_validated": False,
                "whole_model_excluded": False,
                "empirical_discovery": False,
            },
            "next_exact_target": (
                "If the witness is a saddle, optimize within the 77-dimensional "
                "stationarity nullspace subject to perturbativity and complete-BFB "
                "constraints. If it is locally positive, construct a stratified "
                "BFB certificate and enumerate all competing stationary strata."
            ),
            "verdict": (
                "The full G2 Hessian has been assembled and classified on the "
                "449-dimensional space remaining after 36 gauge tangents and the "
                "independent PQ direction are removed. This is an exact local "
                f"classification ({local_state}); global preference and complete "
                "boundedness remain separate requirements."
            ),
        }
    )


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    hessian = report["physical_Hessian"]
    OUT_MD.write_text(
        "# G3 full Hessian classification — v20\n\n"
        f"**Status:** `{report['status']}`  \n"
        f"**Local classification:** `{report['local_classification']}`\n\n"
        f"- full Hessian: `{hessian['full_shape'][0]} x {hessian['full_shape'][1]}`;\n"
        f"- gauge directions removed: `{hessian['gauge_dimension']}`;\n"
        f"- PQ directions removed: `{hessian['axion_dimension']}`;\n"
        f"- massive physical dimension: `{hessian['massive_physical_dimension']}`;\n"
        f"- negative modes: `{hessian['negative_modes']}`;\n"
        f"- extra zero modes: `{hessian['additional_zero_modes']}`.\n\n"
        "This is a local theorem. Complete boundedness and global competing-"
        "extrema classification remain open, so G3 is not closed.\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        write_report(report)
    print(json.dumps(report, indent=2))
    return 0 if report["overall_state"] != "EXECUTION_FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
