#!/usr/bin/env python3
"""Exact 486-real derivatives for the four pure-Phi210 quartic moments.

The authoritative family ``Phi_self_quartics`` is the complete basis

    J_d(Phi) = <S, K^d S>,  S = phi phi^T,  d in {0,2,3,4},

where ``phi`` is the real 210-component four-form coordinate vector and ``K``
is the exact self-adjoint pair-Casimir operator on ``Sym^2(210)``.  Writing
``Y_d=K^d S`` gives the exact real-coordinate derivatives

    grad J_d = 4 Y_d phi,

    Hess J_d[:,j] = 4 [K^d(phi e_j^T + e_j phi^T) phi + Y_d e_j].

No finite-difference derivative or selected-vacuum proxy is used.  Every live
singlet dressing is propagated by the shared exact product rule.  This closes
one additional derivative adapter only; five quartic families and G2 remain
open.
"""
from __future__ import annotations

import argparse
import dataclasses
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np

import exact_210_self_invariant_basis_v20 as source
import exact_phisigma_casimir_projectors_v20 as projectors
import live_g1_tensor_closure_ledger_v20 as ledger
import live_g2_arbitrary_component_potential_values_v20 as potential
import live_g2_canonical_486_field_chart_v20 as chart
import live_g2_exact_quadratic_family_derivatives_v20 as quadratic

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "LIVE_G2_EXACT_PHI_SELF_QUARTIC_DERIVATIVES_V20.json"
OUT_MD = ROOT / "LIVE_G2_EXACT_PHI_SELF_QUARTIC_DERIVATIVES_V20.md"
BASE_FAMILY = "Phi_self_quartics"
BASIS_LABELS = ("J0", "J2", "J3", "J4")
MOMENT_DEGREES = (0, 2, 3, 4)


def _jsonable(value: Any) -> Any:
    if dataclasses.is_dataclass(value):
        return _jsonable(dataclasses.asdict(value))
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, complex):
        return {"re": float(value.real), "im": float(value.imag)}
    return value


def moment_powers(pair: np.ndarray) -> tuple[np.ndarray, ...]:
    """Return K^d(pair) for d=0..4 without constructing unused higher powers."""
    current = np.asarray(pair, dtype=complex)
    if current.shape != (chart.PHI_DIM, chart.PHI_DIM):
        raise ValueError("Phi pair matrix must be 210x210")
    rows = [current]
    for _ in range(max(MOMENT_DEGREES)):
        rows.append(projectors.pair_casimir(rows[-1]))
    return tuple(rows)


@lru_cache(maxsize=4)
def _base_block_cached(
    phi_coordinates: tuple[float, ...],
) -> tuple[tuple[complex, np.ndarray, np.ndarray], ...]:
    phi = np.asarray(phi_coordinates, dtype=float)
    if phi.shape != (chart.PHI_DIM,):
        raise ValueError("Phi block must contain exactly 210 real coordinates")

    pair = np.outer(phi, phi)
    powers = moment_powers(pair)
    values: dict[int, complex] = {}
    gradients: dict[int, np.ndarray] = {}
    hessians: dict[int, np.ndarray] = {
        degree: np.zeros((chart.PHI_DIM, chart.PHI_DIM), dtype=complex)
        for degree in MOMENT_DEGREES
    }

    for degree in MOMENT_DEGREES:
        image = powers[degree]
        values[degree] = complex(np.sum(pair * image))
        gradients[degree] = 4.0 * (image @ phi)

    for column in range(chart.PHI_DIM):
        basis = np.zeros(chart.PHI_DIM, dtype=float)
        basis[column] = 1.0
        linear_pair = np.outer(phi, basis) + np.outer(basis, phi)
        linear_powers = moment_powers(linear_pair)
        for degree in MOMENT_DEGREES:
            image = powers[degree]
            hessians[degree][:, column] = 4.0 * (
                linear_powers[degree] @ phi + image[:, column]
            )

    rows: list[tuple[complex, np.ndarray, np.ndarray]] = []
    for degree in MOMENT_DEGREES:
        gradient = np.asarray(gradients[degree], dtype=complex)
        hessian = np.asarray(hessians[degree], dtype=complex)
        rows.append(
            (
                values[degree],
                gradient,
                0.5 * (hessian + hessian.T),
            )
        )
    return tuple(rows)


def all_base_derivatives(
    q_phi: np.ndarray,
) -> tuple[tuple[complex, np.ndarray, np.ndarray], ...]:
    block = np.asarray(q_phi, dtype=float).reshape(chart.PHI_DIM)
    return _base_block_cached(tuple(float(value) for value in block))


def base_derivative(
    q: np.ndarray, basis_index: int
) -> tuple[complex, np.ndarray, np.ndarray]:
    coordinates = np.asarray(q, dtype=float).reshape(chart.TOTAL_DIM)
    index = int(basis_index)
    if not 0 <= index < len(BASIS_LABELS):
        raise KeyError(f"unknown Phi self-quartic basis index {basis_index}")
    value, phi_gradient, phi_hessian = all_base_derivatives(
        coordinates[chart.PHI_SLICE]
    )[index]
    gradient = np.zeros(chart.TOTAL_DIM, dtype=complex)
    hessian = np.zeros((chart.TOTAL_DIM, chart.TOTAL_DIM), dtype=complex)
    gradient[chart.PHI_SLICE] = phi_gradient
    hessian[chart.PHI_SLICE, chart.PHI_SLICE] = phi_hessian
    return complex(value), gradient, 0.5 * (hessian + hessian.T)


def selected_directions(
    state: potential.FieldState,
) -> tuple[potential.Direction, ...]:
    return tuple(
        row
        for row in potential.evaluate_directions(state)
        if row.base_family == BASE_FAMILY
    )


def direction_derivative(
    q: np.ndarray, direction: potential.Direction
) -> quadratic.DirectionDerivative:
    if direction.base_family != BASE_FAMILY:
        raise KeyError(f"direction {direction.direction_id} is not {BASE_FAMILY}")
    counts = dict(zip(potential.FIELD_ORDER, direction.counts, strict=True))
    base_value, base_gradient, base_hessian = base_derivative(
        q, direction.basis_index
    )
    dressing = quadratic.dressing_jet(q, counts)
    dressing_gradient, dressing_hessian = quadratic._embed_singlet_jet(dressing)
    value = base_value * dressing.value
    gradient = dressing.value * base_gradient + base_value * dressing_gradient
    hessian = (
        dressing.value * base_hessian
        + base_value * dressing_hessian
        + np.outer(base_gradient, dressing_gradient)
        + np.outer(dressing_gradient, base_gradient)
    )
    return quadratic.DirectionDerivative(
        direction_id=direction.direction_id,
        base_family=direction.base_family,
        self_conjugate=direction.self_conjugate,
        value=complex(value),
        gradient=gradient,
        hessian=0.5 * (hessian + hessian.T),
    )


def all_direction_derivatives(
    state: potential.FieldState,
) -> tuple[quadratic.DirectionDerivative, ...]:
    q = chart.pack(state)
    return tuple(
        direction_derivative(q, row) for row in selected_directions(state)
    )


def expected_direction_count() -> int:
    report = ledger.build_report()
    return sum(
        int(orbit["multiplicity"])
        for orbit in report["operator_orbits"]
        if orbit["base_family"] == BASE_FAMILY
    )


def source_normalization_audit(state: potential.FieldState) -> dict[str, Any]:
    q = chart.pack(state)
    observed = {}
    residuals = {}
    expected = source.quartic_invariants(state.phi)
    for index, label in enumerate(BASIS_LABELS):
        value, _, _ = base_derivative(q, index)
        observed[label] = complex(value)
        residuals[label] = float(abs(value - expected[label]))
    return {
        "observed": observed,
        "source": expected,
        "residuals": residuals,
        "maximum_residual": max(residuals.values()),
    }


def j0_closed_form_audit(q: np.ndarray) -> dict[str, float]:
    coordinates = np.asarray(q, dtype=float).reshape(chart.TOTAL_DIM)
    phi = coordinates[chart.PHI_SLICE]
    value, gradient, hessian = base_derivative(coordinates, 0)
    norm = float(np.dot(phi, phi))
    expected_value = norm**2
    expected_gradient = 4.0 * norm * phi
    expected_hessian = 8.0 * np.outer(phi, phi) + 4.0 * norm * np.eye(
        chart.PHI_DIM
    )
    return {
        "value_residual": float(abs(value - expected_value)),
        "gradient_residual": float(
            np.max(np.abs(gradient[chart.PHI_SLICE] - expected_gradient))
        ),
        "Hessian_residual": float(
            np.max(
                np.abs(
                    hessian[chart.PHI_SLICE, chart.PHI_SLICE]
                    - expected_hessian
                )
            )
        ),
    }


def base_support_audit(q: np.ndarray) -> dict[str, Any]:
    active = np.zeros(chart.TOTAL_DIM, dtype=bool)
    active[chart.PHI_SLICE] = True
    rows = {}
    for index, label in enumerate(BASIS_LABELS):
        _, gradient, hessian = base_derivative(q, index)
        inactive = ~active
        rows[label] = {
            "inactive_gradient_residual": float(
                np.max(np.abs(gradient[inactive]), initial=0.0)
            ),
            "inactive_Hessian_residual": float(
                max(
                    np.max(np.abs(hessian[inactive, :]), initial=0.0),
                    np.max(np.abs(hessian[:, inactive]), initial=0.0),
                )
            ),
        }
    return rows


@lru_cache(maxsize=1)
def build_report() -> dict[str, Any]:
    state = potential.deterministic_state(3204)
    q = chart.pack(state)
    directions = selected_directions(state)
    analytic = all_direction_derivatives(state)
    parameters = quadratic.parameter_derivatives(analytic)
    coefficients = quadratic.deterministic_coefficients(parameters)
    directional = quadratic.five_point_directional_audit(
        state, parameters, coefficients
    )
    expected_rows = {row.direction_id: row for row in directions}
    value_residuals = {
        row.direction_id: float(abs(row.value - expected_rows[row.direction_id].value))
        for row in analytic
    }
    expected_count = expected_direction_count()
    basis_indices = sorted({row.basis_index for row in directions})
    basis_labels = sorted({row.basis_label for row in directions})
    normalization = source_normalization_audit(state)
    j0 = j0_closed_form_audit(q)
    support = base_support_audit(q)
    support_residual = max(max(row.values()) for row in support.values())
    hessian_asymmetry = max(
        float(np.max(np.abs(row.hessian - row.hessian.T))) for row in analytic
    )
    self_imaginary = max(
        [
            max(
                abs(row.value.imag),
                float(np.max(np.abs(row.gradient.imag))),
                float(np.max(np.abs(row.hessian.imag))),
            )
            for row in analytic
            if row.self_conjugate
        ]
        or [0.0]
    )
    live_parameter_ids = {
        row.parameter_id
        for row in potential.parameter_schema(potential.evaluate_directions(state))
    }
    parameter_ids = {row.parameter_id for row in parameters}

    checks = {
        "authoritative_family_id_exists": BASE_FAMILY
        in {row["id"] for row in ledger.BASE_FAMILIES.values()},
        "expected_G1_direction_count_is_nonzero": expected_count > 0,
        "observed_direction_count_is_nonzero": len(analytic) > 0,
        "every_expected_direction_differentiated": len(analytic) == expected_count,
        "all_four_basis_indices_present": basis_indices == [0, 1, 2, 3],
        "all_four_basis_labels_present": basis_labels == sorted(BASIS_LABELS),
        "all_values_match_authoritative_source": normalization[
            "maximum_residual"
        ] < 1.0e-8,
        "all_values_match_live_evaluator": max(value_residuals.values()) < 1.0e-8,
        "J0_value_closed_form": j0["value_residual"] < 1.0e-10,
        "J0_gradient_closed_form": j0["gradient_residual"] < 1.0e-9,
        "J0_Hessian_closed_form": j0["Hessian_residual"] < 1.0e-8,
        "all_parameter_ids_belong_to_live_schema": (
            parameter_ids.issubset(live_parameter_ids)
            and len(parameter_ids) == len(parameters)
            and len(parameters) > 0
        ),
        "base_derivatives_supported_only_on_Phi": support_residual < 1.0e-12,
        "all_dense_Hessians_symmetric": hessian_asymmetry < 1.0e-8,
        "self_conjugate_derivatives_real": self_imaginary < 1.0e-8,
        "five_point_value_reconstruction": directional["value_residual"] < 1.0e-7,
        "five_point_first_derivative_reconstruction": directional[
            "first_residual"
        ] < 5.0e-6,
        "five_point_second_derivative_reconstruction": directional[
            "second_residual"
        ] < 5.0e-5,
        "remaining_5_quartic_families_not_claimed": True,
        "G2_not_closed": True,
        "whole_model_not_validated": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return _jsonable(
        {
            "status": (
                "G2_EXACT_PHI_SELF_QUARTIC_DERIVATIVES_CLOSED"
                if not failures
                else "G2_PHI_SELF_QUARTIC_DERIVATIVES_FAILED"
            ),
            "overall_state": "PARTIAL" if not failures else "EXECUTION_FAIL",
            "n_checks": len(checks),
            "n_failed": len(failures),
            "failures": failures,
            "checks": checks,
            "coverage": {
                "base_family": BASE_FAMILY,
                "base_family_count_closed_here": 1,
                "cumulative_base_family_count_with_parents": 13,
                "base_family_count_total": len(ledger.BASE_FAMILIES),
                "remaining_base_families": 5,
                "expected_direction_count": expected_count,
                "observed_direction_count": len(analytic),
                "parameter_count_closed_here": len(parameters),
                "basis_indices": basis_indices,
                "basis_labels": basis_labels,
                "real_field_dimension": chart.TOTAL_DIM,
                "Hessian_shape": [chart.TOTAL_DIM, chart.TOTAL_DIM],
            },
            "source_normalization_audit": normalization,
            "J0_closed_form_audit": j0,
            "base_support_audit": support,
            "maximum_base_support_residual": support_residual,
            "maximum_direction_value_residual": max(value_residuals.values()),
            "maximum_Hessian_asymmetry": hessian_asymmetry,
            "maximum_self_conjugate_imaginary_residual": self_imaginary,
            "directional_reconstruction": directional,
            "flags": {
                "authoritative_Phi_self_quartic_adapter_closed": not failures,
                "all_four_pair_Casimir_moment_derivatives_exact": not failures,
                "cumulative_thirteen_of_eighteen_base_adapters_closed": not failures,
                "all_64_direction_gradients_complete": False,
                "all_64_direction_Hessians_complete": False,
                "G2_closed": False,
                "whole_model_validated": False,
                "empirical_discovery": False,
            },
            "next_exact_target": (
                "Differentiate the four 126bar self projectors, then the two unique "
                "H-Sigma chiral quartics and the two remaining Phi2 mixed families."
            ),
            "verdict": (
                "The complete four-direction pure-Phi210 quartic basis now has exact "
                "full-coordinate gradients and Hessians from the pair-Casimir "
                "linearization. Five adapters remain and G2 is still PARTIAL."
            ),
        }
    )


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Exact Phi210 self-quartic derivatives — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        + report["verdict"]
        + "\n\n"
        + f"**Next:** {report['next_exact_target']}\n",
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
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
