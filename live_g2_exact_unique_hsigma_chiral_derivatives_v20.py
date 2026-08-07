#!/usr/bin/env python3
"""Exact 486-real derivatives for the two unique chiral H-Sigma quartics.

The authoritative multiplicity-one families are

* ``unique_Hdag_Sigma2_Sigmadag`` with source contraction
  ``hbar_a Sigma_bcdef Sigma_abcgh Sigmabar_defgh``;
* ``unique_Hdag2_Sigma2`` with source contraction
  ``hbar_a hbar_b Sigma_bcdef Sigma_acdef``.

Both are multilinear Cartesian contractions. The implementation differentiates
those contractions analytically in the canonical 486-real chart. A cached dense
126bar basis is used only to contract exact coefficient tensors; no finite-
difference derivative, selected-vacuum proxy, fitted Clebsch, or autodiff engine
enters the promoted gradient or Hessian.
"""
from __future__ import annotations

import argparse
import dataclasses
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np

import exact_unique_hsigma_chiral_quartics_v20 as source
import live_g1_tensor_closure_ledger_v20 as ledger
import live_g2_arbitrary_component_potential_values_v20 as potential
import live_g2_canonical_486_field_chart_v20 as chart
import live_g2_exact_quadratic_family_derivatives_v20 as quadratic

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "LIVE_G2_EXACT_UNIQUE_HSIGMA_CHIRAL_DERIVATIVES_V20.json"
OUT_MD = ROOT / "LIVE_G2_EXACT_UNIQUE_HSIGMA_CHIRAL_DERIVATIVES_V20.md"
FAMILY_A = "unique_Hdag_Sigma2_Sigmadag"
FAMILY_B = "unique_Hdag2_Sigma2"
SELECTED_FAMILIES = (FAMILY_A, FAMILY_B)


def _jsonable(value: Any) -> Any:
    if dataclasses.is_dataclass(value):
        return _jsonable(dataclasses.asdict(value))
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, np.ndarray):
        return _jsonable(value.tolist())
    if isinstance(value, np.generic):
        return _jsonable(value.item())
    if isinstance(value, complex):
        return {"re": float(value.real), "im": float(value.imag)}
    return value


def _complex_chart_map(dimension: int) -> np.ndarray:
    output = np.zeros((dimension, 2 * dimension), dtype=complex)
    scale = 1.0 / chart.SQRT2
    for index in range(dimension):
        output[index, 2 * index] = scale
        output[index, 2 * index + 1] = 1j * scale
    return output


@lru_cache(maxsize=1)
def h_map() -> np.ndarray:
    return _complex_chart_map(chart.H_COMPLEX_DIM)


@lru_cache(maxsize=1)
def sigma_map() -> np.ndarray:
    return _complex_chart_map(chart.SIGMA_COMPLEX_DIM)


@lru_cache(maxsize=1)
def dense_sigma_basis() -> np.ndarray:
    return np.stack(
        [source.forms.dense_antisymmetric(form, 5) for form in chart.sigma_basis()]
    )


def _state_blocks(q: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    coordinates = np.asarray(q, dtype=float).reshape(chart.TOTAL_DIM)
    h = chart._unpack_complex_interleaved(coordinates[chart.H_SLICE])
    sigma_coordinates = chart._unpack_complex_interleaved(
        coordinates[chart.SIGMA_SLICE]
    )
    sigma = chart.sigma_from_coordinates(sigma_coordinates)
    dense = source.forms.dense_antisymmetric(sigma, 5)
    return np.conjugate(h), dense, np.conjugate(dense)


def _embed(value, h_gradient, sigma_gradient, hh, hs, ss):
    gradient = np.zeros(chart.TOTAL_DIM, dtype=complex)
    hessian = np.zeros((chart.TOTAL_DIM, chart.TOTAL_DIM), dtype=complex)
    gradient[chart.H_SLICE] = h_gradient
    gradient[chart.SIGMA_SLICE] = sigma_gradient
    hessian[chart.H_SLICE, chart.H_SLICE] = hh
    hessian[chart.H_SLICE, chart.SIGMA_SLICE] = hs
    hessian[chart.SIGMA_SLICE, chart.H_SLICE] = hs.T
    hessian[chart.SIGMA_SLICE, chart.SIGMA_SLICE] = ss
    return complex(value), gradient, 0.5 * (hessian + hessian.T)


def family_a_base_derivative(q: np.ndarray):
    hbar, sigma, sigmabar = _state_blocks(q)
    E = dense_sigma_basis()
    Ebar = np.conjugate(E)
    Hbar_map = np.conjugate(h_map())
    D = sigma_map()
    Dbar = np.conjugate(D)

    value = source.invariant_hdag_sigma2_sigmadag(hbar, sigma, sigmabar)
    gh = np.einsum(
        "bcdef,abcgh,defgh->a", sigma, sigma, sigmabar, optimize="greedy"
    )
    gz1 = np.einsum(
        "a,ibcdef,abcgh,defgh->i", hbar, E, sigma, sigmabar, optimize="greedy"
    )
    gz2 = np.einsum(
        "a,bcdef,iabcgh,defgh->i", hbar, sigma, E, sigmabar, optimize="greedy"
    )
    gzbar = np.einsum(
        "a,bcdef,abcgh,idefgh->i", hbar, sigma, sigma, Ebar, optimize="greedy"
    )
    h_gradient = Hbar_map.T @ gh
    sigma_gradient = D.T @ (gz1 + gz2) + Dbar.T @ gzbar

    c_h1 = np.einsum(
        "ibcdef,abcgh,defgh->ai", E, sigma, sigmabar, optimize="greedy"
    )
    c_h2 = np.einsum(
        "bcdef,iabcgh,defgh->ai", sigma, E, sigmabar, optimize="greedy"
    )
    c_ht = np.einsum(
        "bcdef,abcgh,idefgh->ai", sigma, sigma, Ebar, optimize="greedy"
    )
    hs = Hbar_map.T @ (c_h1 @ D + c_h2 @ D + c_ht @ Dbar)

    c12 = np.einsum(
        "a,ibcdef,jabcgh,defgh->ij", hbar, E, E, sigmabar, optimize="greedy"
    )
    c1t = np.einsum(
        "a,ibcdef,abcgh,jdefgh->ij", hbar, E, sigma, Ebar, optimize="greedy"
    )
    c2t = np.einsum(
        "a,bcdef,iabcgh,jdefgh->ij", hbar, sigma, E, Ebar, optimize="greedy"
    )
    m12 = D.T @ c12 @ D
    m1t = D.T @ c1t @ Dbar
    m2t = D.T @ c2t @ Dbar
    ss = m12 + m12.T + m1t + m1t.T + m2t + m2t.T
    hh = np.zeros((chart.H_REAL_DIM, chart.H_REAL_DIM), dtype=complex)
    return _embed(value, h_gradient, sigma_gradient, hh, hs, ss)


def family_b_base_derivative(q: np.ndarray):
    hbar, sigma, _sigmabar = _state_blocks(q)
    E = dense_sigma_basis()
    Hbar_map = np.conjugate(h_map())
    D = sigma_map()

    value = source.invariant_hdag2_sigma2(hbar, sigma)
    c_hh = np.einsum("bcdef,acdef->ab", sigma, sigma, optimize="greedy")
    gh = (c_hh + c_hh.T) @ hbar
    gz1 = np.einsum(
        "a,b,ibcdef,acdef->i", hbar, hbar, E, sigma, optimize="greedy"
    )
    gz2 = np.einsum(
        "a,b,bcdef,iacdef->i", hbar, hbar, sigma, E, optimize="greedy"
    )
    h_gradient = Hbar_map.T @ gh
    sigma_gradient = D.T @ (gz1 + gz2)

    hh = Hbar_map.T @ (c_hh + c_hh.T) @ Hbar_map
    dc = np.einsum("ibcdef,acdef->iab", E, sigma, optimize="greedy")
    dc += np.einsum("bcdef,iacdef->iab", sigma, E, optimize="greedy")
    chs = np.einsum(
        "iab,b->ai", dc + np.transpose(dc, (0, 2, 1)), hbar, optimize=True
    )
    hs = Hbar_map.T @ chs @ D
    css = np.einsum(
        "a,b,ibcdef,jacdef->ij", hbar, hbar, E, E, optimize="greedy"
    )
    mss = D.T @ css @ D
    ss = mss + mss.T
    return _embed(value, h_gradient, sigma_gradient, hh, hs, ss)


def base_derivative(q: np.ndarray, base_family: str):
    if base_family == FAMILY_A:
        return family_a_base_derivative(q)
    if base_family == FAMILY_B:
        return family_b_base_derivative(q)
    raise KeyError(f"unsupported chiral H-Sigma family {base_family}")


def _orbit_rows():
    rows = []
    for orbit_index, orbit in enumerate(
        potential.census.orbits(potential.census.census(False))
    ):
        counts_tuple = tuple(int(item) for item in orbit["orbit_key"])
        counts = dict(zip(potential.FIELD_ORDER, counts_tuple, strict=True))
        base_key = tuple(counts[name] for name in potential.NON_SINGLET_ORDER)
        rows.append((orbit_index, orbit, counts_tuple, ledger.BASE_FAMILIES[base_key]))
    return tuple(rows)


def _source_value(state: potential.FieldState, family: str) -> complex:
    dense = source.forms.dense_antisymmetric(state.sigma, 5)
    hbar = np.conjugate(state.h)
    if family == FAMILY_A:
        return source.invariant_hdag_sigma2_sigmadag(hbar, dense, np.conjugate(dense))
    if family == FAMILY_B:
        return source.invariant_hdag2_sigma2(hbar, dense)
    raise KeyError(family)


def selected_directions(state: potential.FieldState):
    value = state.validated()
    source_values = {family: _source_value(value, family) for family in SELECTED_FAMILIES}
    directions = []
    for orbit_index, orbit, counts_tuple, base in _orbit_rows():
        if base["id"] not in SELECTED_FAMILIES:
            continue
        if len(base["basis"]) != 1:
            raise AssertionError(f"{base['id']} must be multiplicity one")
        counts = dict(zip(potential.FIELD_ORDER, counts_tuple, strict=True))
        dressing = potential._dressing(value, counts)
        directions.append(
            potential.Direction(
                direction_id=potential._direction_id(orbit_index, 0, base["id"]),
                orbit_index=orbit_index,
                basis_index=0,
                representative=orbit["representative"],
                members=tuple(orbit["members"]),
                self_conjugate=bool(orbit["self_conjugate"]),
                degree=int(orbit["degree"]),
                base_key=tuple(counts[name] for name in potential.NON_SINGLET_ORDER),
                base_family=base["id"],
                basis_label=str(base["basis"][0]),
                source_modules=tuple(base["sources"]),
                normalization=str(base["normalization"]),
                counts=counts_tuple,
                value=complex(source_values[base["id"]] * dressing),
            )
        )
    return tuple(directions)


def direction_derivative(q: np.ndarray, direction: potential.Direction):
    if direction.base_family not in SELECTED_FAMILIES:
        raise KeyError(f"direction {direction.direction_id} is not covered")
    counts = dict(zip(potential.FIELD_ORDER, direction.counts, strict=True))
    base_value, base_gradient, base_hessian = base_derivative(q, direction.base_family)
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


def all_direction_derivatives(state: potential.FieldState):
    q = chart.pack(state)
    return tuple(direction_derivative(q, row) for row in selected_directions(state))


def expected_family_counts() -> dict[str, int]:
    output = {family: 0 for family in SELECTED_FAMILIES}
    for _orbit_index, _orbit, _counts_tuple, base in _orbit_rows():
        if base["id"] in output:
            output[base["id"]] += len(base["basis"])
    return output


def live_parameter_ids_from_g1() -> set[str]:
    output = set()
    for orbit_index, orbit, _counts_tuple, base in _orbit_rows():
        for basis_index, _label in enumerate(base["basis"]):
            direction_id = potential._direction_id(orbit_index, basis_index, base["id"])
            if bool(orbit["self_conjugate"]):
                output.add(f"lambda::{direction_id}")
            else:
                output.add(f"re::{direction_id}")
                output.add(f"im::{direction_id}")
    return output


def targeted_value_layer_audit(state: potential.FieldState):
    dense = potential._dense_state(state)
    rows = {}
    for _orbit_index, _orbit, counts_tuple, base in _orbit_rows():
        if base["id"] not in SELECTED_FAMILIES:
            continue
        counts = dict(zip(potential.FIELD_ORDER, counts_tuple, strict=True))
        base_key = tuple(counts[name] for name in potential.NON_SINGLET_ORDER)
        authoritative = potential._base_values(state, base_key, dense)
        source_value = _source_value(state, base["id"])
        rows[base["id"]] = {
            "authoritative_value": authoritative[0],
            "source_value": source_value,
            "residual": float(abs(authoritative[0] - source_value)),
        }
    return {"families": rows, "maximum_residual": max(row["residual"] for row in rows.values())}


def targeted_directional_audit(state, directions, parameters, coefficients):
    q = chart.pack(state)
    assembled = quadratic.assemble(parameters, coefficients)
    by_direction = {row.direction_id: row for row in directions}
    rng = np.random.default_rng(3405)
    direction = rng.normal(size=chart.TOTAL_DIM)
    direction /= np.linalg.norm(direction)
    step = 0.02

    def evaluate(offset: float) -> float:
        shifted_state = chart.unpack(q + offset * direction)
        values = {family: _source_value(shifted_state, family) for family in SELECTED_FAMILIES}
        total = 0.0
        for parameter in parameters:
            row = by_direction[parameter.direction_id]
            value = values[row.base_family]
            coefficient = float(coefficients[parameter.parameter_id])
            if parameter.component == "re":
                total += coefficient * 2.0 * value.real
            elif parameter.component == "im":
                total += coefficient * -2.0 * value.imag
            else:
                total += coefficient * value.real
        return float(total)

    f_m2 = evaluate(-2.0 * step)
    f_m1 = evaluate(-step)
    f_0 = evaluate(0.0)
    f_p1 = evaluate(step)
    f_p2 = evaluate(2.0 * step)
    numerical_first = (f_m2 - 8.0 * f_m1 + 8.0 * f_p1 - f_p2) / (12.0 * step)
    numerical_second = (
        -f_p2 + 16.0 * f_p1 - 30.0 * f_0 + 16.0 * f_m1 - f_m2
    ) / (12.0 * step**2)
    analytic_first = float(np.dot(assembled["gradient"], direction))
    analytic_second = float(direction @ assembled["hessian"] @ direction)
    return {
        "step": step,
        "value_residual": float(abs(f_0 - assembled["value"])),
        "analytic_first": analytic_first,
        "numerical_first": float(numerical_first),
        "first_residual": float(abs(analytic_first - numerical_first)),
        "analytic_second": analytic_second,
        "numerical_second": float(numerical_second),
        "second_residual": float(abs(analytic_second - numerical_second)),
    }


@lru_cache(maxsize=1)
def build_report() -> dict[str, Any]:
    state = potential.deterministic_state(3404)
    q = chart.pack(state)
    directions = selected_directions(state)
    analytic = tuple(direction_derivative(q, row) for row in directions)
    parameters = quadratic.parameter_derivatives(analytic)
    coefficients = quadratic.deterministic_coefficients(parameters)
    combined = quadratic.assemble(parameters, coefficients)
    directional = targeted_directional_audit(state, directions, parameters, coefficients)
    value_layer = targeted_value_layer_audit(state)
    expected = expected_family_counts()
    observed = {family: sum(row.base_family == family for row in analytic) for family in SELECTED_FAMILIES}
    direction_lookup = {row.direction_id: row for row in directions}
    value_residuals = {
        row.direction_id: float(abs(row.value - direction_lookup[row.direction_id].value))
        for row in analytic
    }
    hessian_asymmetry = max(float(np.max(np.abs(row.hessian - row.hessian.T))) for row in analytic)
    live_parameter_ids = live_parameter_ids_from_g1()
    parameter_ids = {row.parameter_id for row in parameters}

    checks = {
        "both_authoritative_family_ids_exist": set(SELECTED_FAMILIES).issubset(
            {row["id"] for row in ledger.BASE_FAMILIES.values()}
        ),
        "both_G1_multiplicities_are_one": expected == {FAMILY_A: 1, FAMILY_B: 1},
        "both_directions_observed": observed == expected,
        "both_directions_non_self_conjugate": all(not row.self_conjugate for row in directions),
        "source_values_match_authoritative_value_layer": value_layer["maximum_residual"] < 1.0e-10,
        "analytic_direction_values_match_sources": max(value_residuals.values()) < 1.0e-10,
        "four_real_parameters_emitted": len(parameters) == 4,
        "parameter_ids_belong_to_live_91_schema": parameter_ids.issubset(live_parameter_ids)
        and len(parameter_ids) == len(parameters),
        "all_gradients_are_486": all(row.gradient.shape == (486,) for row in analytic),
        "all_Hessians_are_486x486": all(row.hessian.shape == (486, 486) for row in analytic),
        "all_dense_derivatives_finite": all(
            np.all(np.isfinite(row.gradient.real))
            and np.all(np.isfinite(row.gradient.imag))
            and np.all(np.isfinite(row.hessian.real))
            and np.all(np.isfinite(row.hessian.imag))
            for row in analytic
        ),
        "all_Hessians_symmetric": hessian_asymmetry < 1.0e-10,
        "combined_value_reconstructs": directional["value_residual"] < 1.0e-10,
        "combined_first_derivative_reconstructs": directional["first_residual"] < 1.0e-8,
        "combined_second_derivative_reconstructs": directional["second_residual"] < 1.0e-8,
        "combined_gradient_finite": bool(np.all(np.isfinite(combined["gradient"]))),
        "combined_Hessian_finite": bool(np.all(np.isfinite(combined["hessian"]))),
        "remaining_2_families_not_claimed": True,
        "G2_not_closed": True,
        "whole_model_not_validated": True,
    }
    failures = [name for name, ok in checks.items() if not ok]
    return _jsonable(
        {
            "status": "G2_EXACT_UNIQUE_HSIGMA_CHIRAL_DERIVATIVES_CLOSED"
            if not failures
            else "G2_UNIQUE_HSIGMA_CHIRAL_DERIVATIVES_FAILED",
            "overall_state": "PARTIAL" if not failures else "EXECUTION_FAIL",
            "n_checks": len(checks),
            "n_failed": len(failures),
            "failures": failures,
            "checks": checks,
            "coverage": {
                "base_families_closed_here": list(SELECTED_FAMILIES),
                "base_family_count_closed_here": 2,
                "cumulative_base_family_count_with_parents": 16,
                "base_family_count_total": len(ledger.BASE_FAMILIES),
                "remaining_base_families": 2,
                "expected_direction_counts": expected,
                "observed_direction_counts": observed,
                "parameter_count_closed_here": len(parameters),
                "real_field_dimension": chart.TOTAL_DIM,
                "Hessian_shape": [chart.TOTAL_DIM, chart.TOTAL_DIM],
            },
            "targeted_value_layer_audit": value_layer,
            "maximum_direction_value_residual": max(value_residuals.values()),
            "maximum_Hessian_asymmetry": hessian_asymmetry,
            "directional_reconstruction": directional,
            "combined_derivative_norms": {
                "gradient": float(np.linalg.norm(combined["gradient"])),
                "Hessian_frobenius": float(np.linalg.norm(combined["hessian"])),
            },
            "flags": {
                "both_unique_chiral_HSigma_adapters_closed": not failures,
                "cumulative_sixteen_of_eighteen_base_adapters_closed": not failures,
                "all_64_direction_gradients_complete": False,
                "all_64_direction_Hessians_complete": False,
                "G2_closed": False,
                "whole_model_validated": False,
                "empirical_discovery": False,
            },
            "next_exact_target": (
                "Differentiate Phi2_Sigma_projectors and Phi2_Hdag_Sigma_210_1050, "
                "then integrate all 18 families into the live 91-parameter ledger."
            ),
        }
    )


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Exact unique chiral H-Sigma derivatives — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        "Both multiplicity-one quartic families now have exact 486-real gradients "
        "and 486x486 Hessians. Two G2 base families remain.\n",
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
