#!/usr/bin/env python3
"""Search the exact G3 stationarity family for a tachyon-free local witness.

The first G3 gate leaves a large affine family of couplings satisfying all 486
tadpole equations.  Its original least-squares member is a physical saddle.
This module builds the 91 exact parameter Hessians and performs a cutting-plane
semidefinite search inside the anchored stationarity family:

* one positive Phi self-quartic fixes the otherwise homogeneous coupling
  scale, while the other couplings may explore the full stationary nullspace;
* every real coupling is bounded by 4*pi;
* the 36 gauge tangents and the physical PQ tangent are removed;
* successive minimum-eigenvector cuts maximize a certified lower bound on the
  equilibrated 449-dimensional physical Hessian.

The search either provides a fully rechecked local witness or an honest
bounded-search failure.  Neither outcome proves complete boundedness or global
vacuum preference.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import linprog

import g3_full_hessian_classification_v20 as hessian_gate
import g3_full_stationarity_feasibility_v20 as first_order
import live_g2_canonical_486_field_chart_v20 as chart
import live_g2_derivative_coverage_ledger_v20 as g2

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "G3_STATIONARY_STABILITY_SEARCH_V20.json"
OUT_MD = ROOT / "G3_STATIONARY_STABILITY_SEARCH_V20.md"
COUPLING_BOUND = float(4.0 * np.pi)
POSITIVE_ANCHOR_FLOOR = 1.0e-3
EFFECTIVE_STATIONARITY_RANK = 14


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


def exact_parameter_basis(state, parameter_ids: tuple[str, ...]) -> dict[str, Any]:
    """Stream G2 adapters into aligned value, gradient, and Hessian bases."""
    index = {parameter_id: offset for offset, parameter_id in enumerate(parameter_ids)}
    if len(index) != len(parameter_ids):
        raise ValueError("parameter IDs must be unique")
    n_parameters = len(parameter_ids)
    values = np.zeros(n_parameters, dtype=float)
    gradients = np.zeros((n_parameters, chart.TOTAL_DIM), dtype=float)
    hessians = np.zeros(
        (n_parameters, chart.TOTAL_DIM, chart.TOTAL_DIM), dtype=float
    )
    seen: set[str] = set()
    seen_directions: set[str] = set()
    timings: dict[str, float] = {}

    def register(
        parameter_id: str,
        value: float,
        gradient: np.ndarray,
        hessian: np.ndarray,
    ) -> None:
        if parameter_id in seen:
            raise AssertionError(f"duplicate parameter derivative {parameter_id}")
        if parameter_id not in index:
            raise AssertionError(f"unexpected parameter derivative {parameter_id}")
        offset = index[parameter_id]
        values[offset] = float(value)
        gradients[offset] = np.asarray(gradient, dtype=float)
        dense = np.asarray(hessian, dtype=float)
        hessians[offset] = 0.5 * (dense + dense.T)
        seen.add(parameter_id)

    for adapter_name, declared_families, adapter in g2.ADAPTERS:
        started = time.perf_counter()
        rows = tuple(adapter(state))
        timings[adapter_name] = time.perf_counter() - started
        for row in rows:
            if row.base_family not in declared_families:
                raise AssertionError(
                    f"adapter {adapter_name} emitted {row.base_family}"
                )
            if row.direction_id in seen_directions:
                raise AssertionError(f"duplicate direction {row.direction_id}")
            seen_directions.add(row.direction_id)
            if row.self_conjugate:
                register(
                    f"lambda::{row.direction_id}",
                    row.value.real,
                    row.gradient.real,
                    row.hessian.real,
                )
            else:
                register(
                    f"re::{row.direction_id}",
                    2.0 * row.value.real,
                    2.0 * row.gradient.real,
                    2.0 * row.hessian.real,
                )
                register(
                    f"im::{row.direction_id}",
                    -2.0 * row.value.imag,
                    -2.0 * row.gradient.imag,
                    -2.0 * row.hessian.imag,
                )
    missing = set(parameter_ids).difference(seen)
    if missing:
        raise AssertionError(f"missing parameter derivatives: {sorted(missing)}")
    return {
        "values": values,
        "gradients": gradients,
        "hessians": hessians,
        "direction_count": len(seen_directions),
        "parameter_count": len(seen),
        "adapter_seconds": timings,
    }


def stationarity_affine_family(
    gradient_basis: np.ndarray,
    parameter_ids: tuple[str, ...],
) -> dict[str, Any]:
    """Build c=c0+Zy with exact tadpoles and the five anchors fixed."""
    A = np.asarray(gradient_basis, dtype=float).T
    column_norms = np.linalg.norm(A, axis=0)
    active = column_norms > 0.0
    normalized = A[:, active] / column_norms[active]
    _u, singular, vh = np.linalg.svd(normalized, full_matrices=False)
    threshold = 1.0e-10 * singular[0]
    raw_stationarity_rank = int(np.sum(singular > threshold))
    # Two projector gradients vanish analytically on the Delta_R ray and are
    # represented only by ~1e-30 floating roundoff in the dense adapters.  If
    # those columns are independently normalized, that roundoff creates a
    # spurious fifteenth singular direction.  The promoted analytic gradients,
    # mixed-tolerance crosscheck, and exact absolute tadpole recheck fix the
    # effective physical rank at 14.
    stationarity_rank = min(raw_stationarity_rank, EFFECTIVE_STATIONARITY_RANK)
    stationarity_rows = np.zeros((stationarity_rank, A.shape[1]), dtype=float)
    stationarity_rows[:, active] = (
        vh[:stationarity_rank] * column_norms[active][None, :]
    )
    row_norms = np.linalg.norm(stationarity_rows, axis=1)
    stationarity_rows /= row_norms[:, None]

    by_id = {parameter_id: index for index, parameter_id in enumerate(parameter_ids)}
    anchor_indices = np.asarray(
        [by_id[parameter_id] for parameter_id in first_order.STATIONARITY_ANCHOR_PARAMETER_IDS],
        dtype=int,
    )
    anchors = np.zeros((len(anchor_indices), len(parameter_ids)), dtype=float)
    anchors[np.arange(len(anchor_indices)), anchor_indices] = 1.0
    constraints = np.vstack((stationarity_rows, anchors))
    target = np.concatenate(
        (np.zeros(stationarity_rank), np.ones(len(anchor_indices)))
    )
    c0 = np.linalg.lstsq(constraints, target, rcond=1.0e-12)[0]
    _uc, constraint_singular, _vh_constraint = np.linalg.svd(
        constraints, full_matrices=True
    )
    constraint_threshold = 1.0e-10 * constraint_singular[0]
    constraint_rank = int(np.sum(constraint_singular > constraint_threshold))
    _us, stationarity_constraint_singular, vh_stationarity = np.linalg.svd(
        stationarity_rows, full_matrices=True
    )
    stationarity_constraint_threshold = (
        1.0e-10 * stationarity_constraint_singular[0]
    )
    stationarity_constraint_rank = int(
        np.sum(stationarity_constraint_singular > stationarity_constraint_threshold)
    )
    null_basis = vh_stationarity[stationarity_constraint_rank:, :].T

    residual = A @ c0
    relative_residual = float(
        np.linalg.norm(residual)
        / max(np.linalg.norm(A, ord="fro") * np.linalg.norm(c0), 1.0e-300)
    )
    return {
        "A": A,
        "c0": c0,
        "null_basis": null_basis,
        "search_base": np.zeros(len(parameter_ids), dtype=float),
        "raw_stationarity_rank": raw_stationarity_rank,
        "stationarity_rank": stationarity_rank,
        "constraint_rank": constraint_rank,
        "affine_dimension": int(null_basis.shape[1]),
        "stationarity_singular_values": singular,
        "stationarity_relative_residual": relative_residual,
        "stationarity_max_abs_residual": float(
            np.max(np.abs(residual), initial=0.0)
        ),
        "anchor_indices": anchor_indices,
        "anchor_max_abs_residual": float(
            np.max(np.abs(c0[anchor_indices] - 1.0), initial=0.0)
        ),
    }


def _projected_matrix(
    coefficients: np.ndarray,
    hessian_basis: np.ndarray,
    congruence_basis: np.ndarray,
) -> np.ndarray:
    full = np.tensordot(coefficients, hessian_basis, axes=(0, 0))
    projected = congruence_basis.T @ full @ congruence_basis
    return 0.5 * (projected + projected.T)


def _cut_coefficients(
    vector: np.ndarray,
    hessian_basis: np.ndarray,
    congruence_basis: np.ndarray,
) -> np.ndarray:
    lifted = congruence_basis @ np.asarray(vector, dtype=float)
    return np.einsum(
        "i,pij,j->p", lifted, hessian_basis, lifted, optimize=True
    )


def _lp_iteration(
    c0: np.ndarray,
    null_basis: np.ndarray,
    cuts: list[np.ndarray],
    *,
    coupling_bound: float,
    anchor_indices: np.ndarray,
    positive_anchor_floor: float | None,
    normalization_index: int | None,
    target_margin: float,
) -> dict[str, Any]:
    n_free = null_basis.shape[1]
    objective = np.zeros(n_free, dtype=float)
    rows: list[np.ndarray] = []
    rhs: list[float] = []

    # |c0+Zy| <= coupling_bound.
    for matrix, bound in (
        (null_basis, coupling_bound - c0),
        (-null_basis, coupling_bound + c0),
    ):
        rows.extend(matrix)
        rhs.extend(np.asarray(bound, dtype=float))

    if positive_anchor_floor is not None:
        for anchor_index in np.asarray(anchor_indices, dtype=int):
            rows.append(-null_basis[anchor_index])
            rhs.append(float(c0[anchor_index] - positive_anchor_floor))

    # a.(c0+Zy) >= target_margin for every accumulated Rayleigh direction.
    for cut in cuts:
        free = np.asarray(cut, dtype=float) @ null_basis
        base = float(np.asarray(cut, dtype=float) @ c0)
        row = -free
        bound = base - float(target_margin)
        scale = max(float(np.max(np.abs(row), initial=0.0)), abs(bound), 1.0)
        rows.append(row / scale)
        rhs.append(bound / scale)

    A_eq = None
    b_eq = None
    if normalization_index is not None:
        A_eq = np.asarray([null_basis[int(normalization_index)]], dtype=float)
        b_eq = np.asarray([1.0 - c0[int(normalization_index)]], dtype=float)

    common = dict(
        c=objective,
        A_ub=np.asarray(rows, dtype=float),
        b_ub=np.asarray(rhs, dtype=float),
        A_eq=A_eq,
        b_eq=b_eq,
        bounds=[(None, None)] * n_free,
        options={
            "dual_feasibility_tolerance": 1.0e-8,
            "primal_feasibility_tolerance": 1.0e-8,
        },
    )
    result = linprog(method="highs-ds", **common)
    if result.status == 4:
        result = linprog(method="highs-ipm", **common)
    if not result.success:
        return {
            "success": False,
            "status": int(result.status),
            "message": str(result.message),
        }
    y = np.asarray(result.x, dtype=float)
    coefficients = c0 + null_basis @ y
    return {
        "success": True,
        "status": int(result.status),
        "message": str(result.message),
        "coefficients": coefficients,
        "free_coordinates": y,
    }


def stability_search(
    family: dict[str, Any],
    hessian_basis: np.ndarray,
    quotient_data: dict[str, Any],
    *,
    max_iterations: int = 24,
    positive_anchor_floor: float | None = None,
    normalization_index: int | None = None,
    target_margin: float = 1.0e-8,
) -> dict[str, Any]:
    initial = np.asarray(family["c0"], dtype=float)
    search_base = np.asarray(family["search_base"], dtype=float)
    null_basis = np.asarray(family["null_basis"], dtype=float)
    quotient = np.asarray(quotient_data["quotient"], dtype=float)

    raw0 = quotient.T @ np.tensordot(initial, hessian_basis, axes=(0, 0)) @ quotient
    equilibrium = hessian_gate.equilibrate_congruence(raw0)
    diagonal_scale = np.asarray(equilibrium["diagonal_scale"], dtype=float)
    congruence = quotient * diagonal_scale[None, :]
    matrix = _projected_matrix(initial, hessian_basis, congruence)
    eigenvalues, eigenvectors = np.linalg.eigh(matrix)
    initial_eigenvalues = eigenvalues.copy()

    cuts: list[np.ndarray] = []
    seed_count = min(80, eigenvectors.shape[1])
    for vector in eigenvectors[:, :seed_count].T:
        cuts.append(_cut_coefficients(vector, hessian_basis, congruence))

    history: list[dict[str, Any]] = []
    best_coefficients = initial.copy()
    best_eigenvalues = eigenvalues.copy()
    best_minimum = float(eigenvalues[0])
    termination = "iteration_limit"
    for iteration in range(int(max_iterations)):
        lp = _lp_iteration(
            search_base,
            null_basis,
            cuts,
            coupling_bound=COUPLING_BOUND,
            anchor_indices=np.asarray(family["anchor_indices"], dtype=int),
            positive_anchor_floor=positive_anchor_floor,
            normalization_index=normalization_index,
            target_margin=target_margin,
        )
        if not lp["success"]:
            termination = (
                "finite_rayleigh_cut_problem_infeasible"
                if lp["status"] == 2
                else "linear_outer_problem_numerical_failure"
            )
            history.append({"iteration": iteration, **lp})
            break
        coefficients = np.asarray(lp["coefficients"], dtype=float)
        matrix = _projected_matrix(coefficients, hessian_basis, congruence)
        eigenvalues, eigenvectors = np.linalg.eigh(matrix)
        minimum = float(eigenvalues[0])
        negative_modes = int(np.sum(eigenvalues < -1.0e-9))
        history.append(
            {
                "iteration": iteration,
                "cut_count": len(cuts),
                "target_margin": target_margin,
                "rechecked_minimum_eigenvalue": minimum,
                "negative_modes": negative_modes,
                "max_abs_coefficient": float(np.max(np.abs(coefficients))),
            }
        )
        if minimum > best_minimum:
            best_minimum = minimum
            best_coefficients = coefficients.copy()
            best_eigenvalues = eigenvalues.copy()
        if minimum >= 0.999 * target_margin:
            termination = "strict_local_witness_found"
            best_coefficients = coefficients.copy()
            best_eigenvalues = eigenvalues.copy()
            best_minimum = minimum
            break
        violating = np.flatnonzero(eigenvalues < target_margin)
        add_indices = violating[: min(180, len(violating))]
        if not len(add_indices):
            add_indices = np.arange(min(24, eigenvectors.shape[1]))
        for vector in eigenvectors[:, add_indices].T:
            cuts.append(_cut_coefficients(vector, hessian_basis, congruence))

    tolerance = max(
        1.0e-11 * float(np.max(np.abs(best_eigenvalues), initial=0.0)),
        1.0e-13,
    )
    return {
        "termination": termination,
        "target_margin": target_margin,
        "positive_anchor_floor": positive_anchor_floor,
        "normalization_index": normalization_index,
        "iterations": len(history),
        "history": history,
        "initial": {
            "minimum_eigenvalue": float(initial_eigenvalues[0]),
            "negative_modes": int(np.sum(initial_eigenvalues < -tolerance)),
            "zero_modes": int(np.sum(np.abs(initial_eigenvalues) <= tolerance)),
        },
        "best": {
            "minimum_eigenvalue": best_minimum,
            "maximum_eigenvalue": float(best_eigenvalues[-1]),
            "negative_modes": int(np.sum(best_eigenvalues < -tolerance)),
            "zero_modes": int(np.sum(np.abs(best_eigenvalues) <= tolerance)),
            "positive_modes": int(np.sum(best_eigenvalues > tolerance)),
            "max_abs_coefficient": float(np.max(np.abs(best_coefficients))),
            "nonzero_coefficients": int(np.sum(np.abs(best_coefficients) > 1.0e-12)),
            "coefficients": best_coefficients,
            "smallest_eigenvalues": best_eigenvalues[: min(20, len(best_eigenvalues))],
        },
        "fixed_equilibration": {
            "scale_min": equilibrium["scale_min"],
            "scale_max": equilibrium["scale_max"],
            "scale_condition_ratio": equilibrium["scale_condition_ratio"],
        },
    }


def build_report(
    *, max_iterations: int = 24, target_margin: float = 1.0e-8
) -> dict[str, Any]:
    started = time.perf_counter()
    state = first_order.physical_candidate(electroweak=True)
    fast_parameters = first_order.parameter_gradient_rows(state)
    parameter_ids = tuple(row.parameter_id for row in fast_parameters)
    basis = exact_parameter_basis(state, parameter_ids)
    family = stationarity_affine_family(basis["gradients"], parameter_ids)
    quotient = hessian_gate.physical_quotient_basis()
    normalization_index = parameter_ids.index(
        "lambda::O48_B01_Phi_self_quartics"
    )
    search = stability_search(
        family,
        basis["hessians"],
        quotient,
        max_iterations=max_iterations,
        positive_anchor_floor=None,
        normalization_index=normalization_index,
        target_margin=target_margin,
    )
    coefficients = np.asarray(search["best"]["coefficients"], dtype=float)
    exact_gradient = basis["gradients"].T @ coefficients
    anchor_indices = np.asarray(family["anchor_indices"], dtype=int)
    locally_positive = (
        search["best"]["negative_modes"] == 0
        and search["best"]["zero_modes"] == 0
        and search["best"]["minimum_eigenvalue"]
        > max(0.999 * target_margin, 1.0e-10)
    )
    checks = {
        "all_64_directions_in_basis": basis["direction_count"] == 64,
        "all_91_parameters_in_basis": basis["parameter_count"] == 91,
        "effective_stationarity_rank_matches_first_order": family["stationarity_rank"] == 14,
        "anchored_affine_family_nonempty": family["affine_dimension"] > 0,
        "positive_normalization_anchor_fixed": abs(
            coefficients[normalization_index] - 1.0
        )
        < 1.0e-8,
        "all_couplings_perturbative": float(np.max(np.abs(coefficients)))
        <= COUPLING_BOUND + 1.0e-8,
        "all_486_tadpoles_remain_zero": float(
            np.max(np.abs(exact_gradient), initial=0.0)
        )
        < 1.0e-8,
        "physical_quotient_dimension_is_449": quotient["quotient"].shape[1] == 449,
        "strict_local_witness_found": locally_positive,
        "complete_BFB_not_claimed": True,
        "global_minimum_not_claimed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    execution_failures = [
        name for name in failures if name != "strict_local_witness_found"
    ]
    coefficient_map = {
        parameter_id: float(value)
        for parameter_id, value in zip(parameter_ids, coefficients, strict=True)
        if abs(value) > 1.0e-12
    }
    result = {
        key: value for key, value in search.items() if key != "best"
    }
    result["best"] = {
        key: value for key, value in search["best"].items() if key != "coefficients"
    }
    result["best"]["coefficient_map"] = coefficient_map
    return _jsonable(
        {
            "status": (
                "G3_STATIONARY_STRICT_LOCAL_WITNESS_FOUND__GLOBAL_BFB_OPEN"
                if locally_positive and not execution_failures
                else (
                    "G3_STATIONARY_STABILITY_SEARCH_NO_LOCAL_WITNESS"
                    if not execution_failures
                    else "G3_STATIONARY_STABILITY_SEARCH_EXECUTION_FAILED"
                )
            ),
            "overall_state": "PARTIAL" if not execution_failures else "EXECUTION_FAIL",
            "n_checks": len(checks),
            "n_failed": len(failures),
            "failures": failures,
            "checks": checks,
            "coverage": {
                "base_families": 18,
                "directions": basis["direction_count"],
                "real_parameters": basis["parameter_count"],
                "real_field_dimension": 486,
                "massive_physical_dimension": 449,
            },
            "stationarity_family": {
                "stationarity_rank": family["stationarity_rank"],
                "raw_dense_normalized_rank": family["raw_stationarity_rank"],
                "constraint_rank_with_anchors": family["constraint_rank"],
                "affine_dimension": family["affine_dimension"],
                "initial_relative_residual": family[
                    "stationarity_relative_residual"
                ],
                "initial_max_abs_residual": family[
                    "stationarity_max_abs_residual"
                ],
                "anchor_max_abs_residual": family["anchor_max_abs_residual"],
            },
            "search": result,
            "final_stationarity": {
                "gradient_norm": float(np.linalg.norm(exact_gradient)),
                "gradient_max_abs": float(
                    np.max(np.abs(exact_gradient), initial=0.0)
                ),
                "minimum_of_five_reference_anchors": float(
                    np.min(coefficients[anchor_indices], initial=np.inf)
                ),
                "normalization_parameter": parameter_ids[normalization_index],
                "normalization_residual": abs(
                    coefficients[normalization_index] - 1.0
                ),
            },
            "performance": {
                "adapter_seconds": basis["adapter_seconds"],
                "wall_seconds": time.perf_counter() - started,
            },
            "flags": {
                "G1_closed": True,
                "G2_closed": True,
                "full_stationarity_affine_family_constructed": not execution_failures,
                "strict_local_physical_minimum_found": locally_positive,
                "complete_potential_BFB": False,
                "global_competing_extrema_exhausted": False,
                "G3_closed": False,
                "whole_model_validated": False,
                "whole_model_excluded": False,
                "empirical_discovery": False,
            },
            "verdict": (
                "The original anchored stationary member is a saddle. The exact "
                "cutting-plane search either supplies the reported perturbative "
                "tachyon-free member or records a bounded local-search failure. "
                "Complete BFB and global competing-extrema proofs remain mandatory "
                "before G3 can close."
            ),
        }
    )


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    best = report["search"]["best"]
    OUT_MD.write_text(
        "# G3 stationary stability search — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- affine stationarity dimension: `{report['stationarity_family']['affine_dimension']}`;\n"
        f"- search termination: `{report['search']['termination']}`;\n"
        f"- best minimum physical eigenvalue: `{best['minimum_eigenvalue']}`;\n"
        f"- negative modes: `{best['negative_modes']}`;\n"
        f"- extra zero modes: `{best['zero_modes']}`;\n"
        f"- max |coupling|: `{best['max_abs_coefficient']}`.\n\n"
        "This local search does not prove complete boundedness or global vacuum "
        "preference; G3 remains open until both are certified.\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--max-iterations", type=int, default=24)
    parser.add_argument("--target-margin", type=float, default=1.0e-8)
    args = parser.parse_args(argv)
    report = build_report(
        max_iterations=args.max_iterations,
        target_margin=args.target_margin,
    )
    if args.write:
        write_report(report)
    print(json.dumps(report, indent=2))
    return 0 if report["overall_state"] != "EXECUTION_FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
