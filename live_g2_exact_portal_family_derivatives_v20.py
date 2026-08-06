#!/usr/bin/env python3
"""Exact 486-real derivatives for both Phi Hdag 126bar portal families.

The two authoritative G1 base families are

* ``Phi_Hdag_Sigma``;
* ``Phi_Hdag_Sigmadag``.

In canonical complex coefficients their undressed invariants are

    I_- = Hdag_e Phi_p Sigma_A C[e,p,A],
    I_+ = Hdag_e Phi_p Sigma_A^* Cdag[e,p,A],

where C and Cdag are independently constructed from the physical -i 126bar
basis and its explicitly conjugated +i basis.  The identity Cdag=conjugate(C)
is then an executable orientation check rather than an assumption.

Since each invariant is trilinear, the complete gradient and Hessian contain
only exact linear and cross-bilinear blocks.  Every live singlet dressing is
included by the exact product rule from the first five derivative families.
This closes these two adapters only; eleven of eighteen families remain.
"""
from __future__ import annotations

import argparse
import dataclasses
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np

import direct_phi_h_sigmabar_tensor_v20 as direct
import live_g1_tensor_closure_ledger_v20 as ledger
import live_g2_arbitrary_component_potential_values_v20 as potential
import live_g2_canonical_486_field_chart_v20 as chart
import live_g2_exact_quadratic_family_derivatives_v20 as quadratic

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "LIVE_G2_EXACT_PORTAL_FAMILY_DERIVATIVES_V20.json"
OUT_MD = ROOT / "LIVE_G2_EXACT_PORTAL_FAMILY_DERIVATIVES_V20.md"

SELECTED_FAMILIES = (
    "Phi_Hdag_Sigmadag",
    "Phi_Hdag_Sigma",
)
SQRT2 = float(np.sqrt(2.0))
INV_SQRT2 = 1.0 / SQRT2


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


def conjugate_form(form: direct.Form) -> direct.Form:
    return {indices: np.conjugate(value) for indices, value in form.items()}


def _build_tensor(sigma_states: tuple[direct.Form, ...]) -> np.ndarray:
    tensor = np.zeros(
        (chart.H_COMPLEX_DIM, chart.PHI_DIM, chart.SIGMA_COMPLEX_DIM),
        dtype=complex,
    )
    for phi_index, indices in enumerate(chart.phi_indices()):
        phi = {indices: 1.0 + 0.0j}
        for sigma_index, sigma in enumerate(sigma_states):
            image = direct.contract(phi, sigma)
            for vector_index in range(chart.H_COMPLEX_DIM):
                tensor[vector_index, phi_index, sigma_index] = image.get(
                    (vector_index,), 0.0
                )
    return tensor


@lru_cache(maxsize=1)
def portal_tensor() -> np.ndarray:
    """C[e,p,A] in the physical -i 126bar basis."""
    return _build_tensor(tuple(chart.sigma_basis()))


@lru_cache(maxsize=1)
def portal_tensor_dagger_direct() -> np.ndarray:
    """Cdag[e,p,A] built independently in the conjugated +i basis."""
    return _build_tensor(
        tuple(conjugate_form(state) for state in chart.sigma_basis())
    )


def _complex_blocks(q: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    coordinates = np.asarray(q, dtype=float).reshape(chart.TOTAL_DIM)
    phi = coordinates[chart.PHI_SLICE].copy()
    h_block = coordinates[chart.H_SLICE]
    sigma_block = coordinates[chart.SIGMA_SLICE]
    h = (h_block[0::2] + 1j * h_block[1::2]) * INV_SQRT2
    sigma = (sigma_block[0::2] + 1j * sigma_block[1::2]) * INV_SQRT2
    return phi, h, sigma


def base_derivative(
    q: np.ndarray, base_family: str
) -> tuple[complex, np.ndarray, np.ndarray]:
    if base_family not in SELECTED_FAMILIES:
        raise KeyError(f"base family {base_family} is not a portal adapter")
    phi, h, sigma_coordinates = _complex_blocks(q)
    coefficient = portal_tensor()
    sigma_v_factor = 1j * INV_SQRT2
    if base_family == "Phi_Hdag_Sigmadag":
        coefficient = portal_tensor_dagger_direct()
        sigma_coordinates = np.conjugate(sigma_coordinates)
        sigma_v_factor = -1j * INV_SQRT2

    hdag = np.conjugate(h)
    value = np.einsum(
        "e,p,a,epa->",
        hdag,
        phi,
        sigma_coordinates,
        coefficient,
        optimize=True,
    )
    gradient = np.zeros(chart.TOTAL_DIM, dtype=complex)
    hessian = np.zeros((chart.TOTAL_DIM, chart.TOTAL_DIM), dtype=complex)

    vector_image = np.einsum(
        "p,a,epa->e", phi, sigma_coordinates, coefficient, optimize=True
    )
    phi_gradient = np.einsum(
        "e,a,epa->p", hdag, sigma_coordinates, coefficient, optimize=True
    )
    sigma_gradient = np.einsum(
        "e,p,epa->a", hdag, phi, coefficient, optimize=True
    )
    gradient[chart.PHI_SLICE] = phi_gradient
    h_x = chart.H_SLICE.start + 2 * np.arange(chart.H_COMPLEX_DIM)
    h_y = h_x + 1
    sigma_u = chart.SIGMA_SLICE.start + 2 * np.arange(chart.SIGMA_COMPLEX_DIM)
    sigma_v = sigma_u + 1
    gradient[h_x] = INV_SQRT2 * vector_image
    gradient[h_y] = -1j * INV_SQRT2 * vector_image
    gradient[sigma_u] = INV_SQRT2 * sigma_gradient
    gradient[sigma_v] = sigma_v_factor * sigma_gradient

    h_phi = np.einsum(
        "a,epa->ep", sigma_coordinates, coefficient, optimize=True
    )
    sigma_phi = np.einsum(
        "e,epa->ap", hdag, coefficient, optimize=True
    )
    h_sigma = np.einsum("p,epa->ea", phi, coefficient, optimize=True)
    phi_indices = np.arange(chart.PHI_SLICE.start, chart.PHI_SLICE.stop)

    def symmetric_block(rows: np.ndarray, columns: np.ndarray, block: np.ndarray) -> None:
        hessian[np.ix_(rows, columns)] = block
        hessian[np.ix_(columns, rows)] = block.T

    symmetric_block(h_x, phi_indices, INV_SQRT2 * h_phi)
    symmetric_block(h_y, phi_indices, -1j * INV_SQRT2 * h_phi)
    symmetric_block(sigma_u, phi_indices, INV_SQRT2 * sigma_phi)
    symmetric_block(sigma_v, phi_indices, sigma_v_factor * sigma_phi)

    h_x_factor = INV_SQRT2
    h_y_factor = -1j * INV_SQRT2
    sigma_u_factor = INV_SQRT2
    symmetric_block(h_x, sigma_u, h_x_factor * sigma_u_factor * h_sigma)
    symmetric_block(h_x, sigma_v, h_x_factor * sigma_v_factor * h_sigma)
    symmetric_block(h_y, sigma_u, h_y_factor * sigma_u_factor * h_sigma)
    symmetric_block(h_y, sigma_v, h_y_factor * sigma_v_factor * h_sigma)

    return complex(value), gradient, 0.5 * (hessian + hessian.T)


def selected_directions(
    state: potential.FieldState,
) -> tuple[potential.Direction, ...]:
    return tuple(
        row
        for row in potential.evaluate_directions(state)
        if row.base_family in SELECTED_FAMILIES
    )


def direction_derivative(
    q: np.ndarray, direction: potential.Direction
) -> quadratic.DirectionDerivative:
    if direction.base_family not in SELECTED_FAMILIES:
        raise KeyError(f"direction {direction.direction_id} is not a portal")
    counts = dict(zip(potential.FIELD_ORDER, direction.counts, strict=True))
    base_value, base_gradient, base_hessian = base_derivative(
        q, direction.base_family
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


def expected_family_counts() -> dict[str, int]:
    g1 = ledger.build_report()
    return {
        family: sum(
            int(orbit["multiplicity"])
            for orbit in g1["operator_orbits"]
            if orbit["base_family"] == family
        )
        for family in SELECTED_FAMILIES
    }


def base_support_audit(q: np.ndarray) -> dict[str, Any]:
    active = np.zeros(chart.TOTAL_DIM, dtype=bool)
    active[chart.PHI_SLICE] = True
    active[chart.H_SLICE] = True
    active[chart.SIGMA_SLICE] = True
    rows: dict[str, Any] = {}
    for family in SELECTED_FAMILIES:
        _, gradient, hessian = base_derivative(q, family)
        inactive = ~active
        same_blocks = {
            "PhiPhi": float(
                np.max(np.abs(hessian[chart.PHI_SLICE, chart.PHI_SLICE]))
            ),
            "HH": float(np.max(np.abs(hessian[chart.H_SLICE, chart.H_SLICE]))),
            "SigmaSigma": float(
                np.max(np.abs(hessian[chart.SIGMA_SLICE, chart.SIGMA_SLICE]))
            ),
        }
        rows[family] = {
            "inactive_gradient_residual": float(
                np.max(np.abs(gradient[inactive]), initial=0.0)
            ),
            "inactive_Hessian_residual": float(
                max(
                    np.max(np.abs(hessian[inactive, :]), initial=0.0),
                    np.max(np.abs(hessian[:, inactive]), initial=0.0),
                )
            ),
            "same_field_Hessian_residual": max(same_blocks.values()),
            "same_field_blocks": same_blocks,
        }
    return rows


@lru_cache(maxsize=1)
def build_report() -> dict[str, Any]:
    state = potential.deterministic_state(2604)
    q = chart.pack(state)
    directions = selected_directions(state)
    analytic = all_direction_derivatives(state)
    parameters = quadratic.parameter_derivatives(analytic)
    coefficients = quadratic.deterministic_coefficients(parameters)
    directional = quadratic.five_point_directional_audit(
        state, parameters, coefficients
    )
    evaluated = {row.direction_id: row for row in directions}
    value_residuals = {
        row.direction_id: float(abs(row.value - evaluated[row.direction_id].value))
        for row in analytic
    }
    actual_counts = {
        family: sum(row.base_family == family for row in analytic)
        for family in SELECTED_FAMILIES
    }
    expected_counts = expected_family_counts()
    tensor = portal_tensor()
    tensor_dagger = portal_tensor_dagger_direct()
    tensor_conjugation_residual = float(
        np.max(np.abs(tensor_dagger - np.conjugate(tensor)))
    )
    tensor_nonzero = int(np.count_nonzero(np.abs(tensor) > 1.0e-14))
    support = base_support_audit(q)
    maximum_support_residual = max(
        max(
            row["inactive_gradient_residual"],
            row["inactive_Hessian_residual"],
            row["same_field_Hessian_residual"],
        )
        for row in support.values()
    )
    maximum_hessian_asymmetry = max(
        float(np.max(np.abs(row.hessian - row.hessian.T))) for row in analytic
    )
    full_parameter_ids = {
        row.parameter_id
        for row in potential.parameter_schema(
            potential.evaluate_directions(state)
        )
    }
    parameter_ids = {row.parameter_id for row in parameters}

    checks = {
        "portal_tensor_shape_is_10x210x126": tensor.shape == (10, 210, 126),
        "direct_Sigmadag_tensor_has_same_shape": tensor_dagger.shape == tensor.shape,
        "portal_tensor_is_nonzero": tensor_nonzero > 0,
        "Sigmadag_tensor_is_independently_exact_conjugate": tensor_conjugation_residual
        < 1.0e-15,
        "authoritative_family_ids_exist": set(SELECTED_FAMILIES).issubset(
            {row["id"] for row in ledger.BASE_FAMILIES.values()}
        ),
        "both_families_have_nonzero_expected_counts": all(
            count > 0 for count in expected_counts.values()
        ),
        "both_families_have_nonzero_observed_counts": all(
            count > 0 for count in actual_counts.values()
        ),
        "all_expected_portal_directions_differentiated": actual_counts
        == expected_counts,
        "all_portal_values_match_authoritative_evaluator": max(
            value_residuals.values()
        ) < 1.0e-10,
        "all_portal_parameter_ids_belong_to_live_schema": (
            parameter_ids.issubset(full_parameter_ids)
            and len(parameter_ids) == len(parameters)
            and len(parameters) > 0
        ),
        "base_derivatives_have_only_expected_cross_blocks": maximum_support_residual
        < 1.0e-12,
        "all_dense_Hessians_symmetric": maximum_hessian_asymmetry < 1.0e-12,
        "five_point_value_reconstruction": directional["value_residual"] < 1.0e-9,
        "five_point_first_derivative_reconstruction": directional[
            "first_residual"
        ] < 1.0e-8,
        "five_point_second_derivative_reconstruction": directional[
            "second_residual"
        ] < 1.0e-7,
        "remaining_11_base_families_not_claimed": True,
        "G2_not_closed": True,
        "whole_model_not_validated": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return _jsonable(
        {
            "status": (
                "G2_EXACT_DERIVATIVES_2_PORTAL_FAMILIES_CLOSED"
                if not failures
                else "G2_PORTAL_FAMILY_DERIVATIVES_FAILED"
            ),
            "overall_state": "PARTIAL" if not failures else "EXECUTION_FAIL",
            "n_checks": len(checks),
            "n_failed": len(failures),
            "failures": failures,
            "checks": checks,
            "coverage": {
                "base_families_closed": list(SELECTED_FAMILIES),
                "base_family_count_closed_here": 2,
                "cumulative_base_family_count_with_parent": 7,
                "base_family_count_total": len(ledger.BASE_FAMILIES),
                "expected_direction_counts": expected_counts,
                "observed_direction_counts": actual_counts,
                "direction_count_closed_here": len(analytic),
                "parameter_count_closed_here": len(parameters),
                "real_field_dimension": chart.TOTAL_DIM,
                "Hessian_shape": [chart.TOTAL_DIM, chart.TOTAL_DIM],
            },
            "portal_tensor": {
                "shape": list(tensor.shape),
                "nonzero_entries": tensor_nonzero,
                "frobenius_norm": float(np.linalg.norm(tensor)),
                "direct_Sigmadag_conjugation_residual": tensor_conjugation_residual,
            },
            "base_support_audit": support,
            "maximum_base_support_residual": maximum_support_residual,
            "maximum_direction_value_residual": max(value_residuals.values()),
            "maximum_Hessian_asymmetry": maximum_hessian_asymmetry,
            "directional_reconstruction": directional,
            "flags": {
                "two_portal_base_derivative_adapters_closed": not failures,
                "all_portal_direction_gradients_exact": not failures,
                "all_portal_direction_Hessians_exact": not failures,
                "cumulative_seven_of_eighteen_base_adapters_closed": not failures,
                "all_64_direction_gradients_complete": False,
                "all_64_direction_Hessians_complete": False,
                "G2_closed": False,
                "whole_model_validated": False,
                "empirical_discovery": False,
            },
            "next_exact_target": (
                "Differentiate Phi_Sigma_Sigmadag_cubic and Phi_cubic on the "
                "same canonical chart, then move to quartic base families."
            ),
            "verdict": (
                "Both trilinear 210_H 10_Hdag 126bar portal families now have "
                "exact dense 486-gradients and 486x486 Hessians for every live "
                "singlet dressing. Eleven base families remain, so G2 is PARTIAL."
            ),
        }
    )


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Exact derivatives for both cubic portal families\n\n"
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
