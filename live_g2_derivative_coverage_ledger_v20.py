#!/usr/bin/env python3
"""Authoritative coverage ledger for exact full-coordinate G2 derivatives.

This module consolidates the stacked exact derivative adapters and compares
them against the live G1 catalogue of 18 base families, 64 invariant
directions, and 91 real potential parameters.  It fails closed on

* duplicate family ownership;
* duplicate or missing direction IDs;
* vacuous zero-direction adapters;
* disagreement with authoritative G1 multiplicities;
* parameter IDs outside the live 91-real schema;
* inconsistent dense derivative shapes;
* failed combined value/gradient/Hessian reconstruction.

At this stage twelve base families have draft implementations of complete
486-real gradients and 486x486 Hessians.  Six quartic families remain.  This
ledger does not promote those implementations without execution and does not
close G2, stationarity, the vacuum problem, or any downstream gate.
"""
from __future__ import annotations

import argparse
import dataclasses
import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable

import numpy as np

import live_g1_tensor_closure_ledger_v20 as g1
import live_g2_arbitrary_component_potential_values_v20 as potential
import live_g2_canonical_486_field_chart_v20 as chart
import live_g2_exact_quadratic_family_derivatives_v20 as quadratic
import live_g2_exact_portal_family_derivatives_v20 as portal
import live_g2_exact_remaining_cubic_derivatives_v20 as cubic
import live_g2_exact_h10_self_quartic_derivatives_v20 as h10
import live_g2_exact_hsigma_hermitian_derivatives_v20 as hsigma
import live_g2_exact_phi2_hdagh_derivatives_v20 as phi2h

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "LIVE_G2_DERIVATIVE_COVERAGE_LEDGER_V20.json"
OUT_MD = ROOT / "LIVE_G2_DERIVATIVE_COVERAGE_LEDGER_V20.md"

Adapter = Callable[[potential.FieldState], tuple[quadratic.DirectionDerivative, ...]]

ADAPTERS: tuple[tuple[str, tuple[str, ...], Adapter], ...] = (
    ("quadratic_families", tuple(quadratic.SELECTED_FAMILIES), quadratic.all_direction_derivatives),
    ("portal_families", tuple(portal.SELECTED_FAMILIES), portal.all_direction_derivatives),
    ("remaining_cubic_families", tuple(cubic.SELECTED_FAMILIES), cubic.all_direction_derivatives),
    ("H10_self_quartics", (h10.BASE_FAMILY,), h10.all_direction_derivatives),
    ("H_Sigma_hermitian", (hsigma.BASE_FAMILY,), hsigma.all_direction_derivatives),
    ("Phi2_HdagH_channels", (phi2h.BASE_FAMILY,), phi2h.all_direction_derivatives),
)

EXPECTED_REMAINING_FAMILIES = (
    "126bar_self_projectors",
    "unique_Hdag_Sigma2_Sigmadag",
    "unique_Hdag2_Sigma2",
    "Phi2_Sigma_projectors",
    "Phi2_Hdag_Sigma_210_1050",
    "Phi_self_quartics",
)


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


def all_live_families() -> tuple[str, ...]:
    return tuple(row["id"] for row in g1.BASE_FAMILIES.values())


def covered_families() -> tuple[str, ...]:
    output: list[str] = []
    for _, families, _ in ADAPTERS:
        output.extend(families)
    return tuple(output)


def family_owners() -> dict[str, list[str]]:
    output: dict[str, list[str]] = {}
    for adapter_name, families, _ in ADAPTERS:
        for family in families:
            output.setdefault(family, []).append(adapter_name)
    return output


def g1_family_direction_counts() -> dict[str, int]:
    report = g1.build_report()
    counts = {family: 0 for family in all_live_families()}
    for orbit in report["operator_orbits"]:
        counts[str(orbit["base_family"])] += int(orbit["multiplicity"])
    return counts


def evaluate_adapter_rows(
    state: potential.FieldState,
) -> dict[str, tuple[quadratic.DirectionDerivative, ...]]:
    return {
        name: tuple(adapter(state))
        for name, _, adapter in ADAPTERS
    }


def flatten_rows(
    adapter_rows: dict[str, tuple[quadratic.DirectionDerivative, ...]],
) -> tuple[quadratic.DirectionDerivative, ...]:
    return tuple(
        row
        for adapter_name, _, _ in ADAPTERS
        for row in adapter_rows[adapter_name]
    )


def expected_covered_directions(
    state: potential.FieldState,
) -> tuple[potential.Direction, ...]:
    families = set(covered_families())
    return tuple(
        row
        for row in potential.evaluate_directions(state)
        if row.base_family in families
    )


def remaining_directions(
    state: potential.FieldState,
) -> tuple[potential.Direction, ...]:
    families = set(covered_families())
    return tuple(
        row
        for row in potential.evaluate_directions(state)
        if row.base_family not in families
    )


def adapter_coverage_rows(
    adapter_rows: dict[str, tuple[quadratic.DirectionDerivative, ...]],
    expected_counts: dict[str, int],
) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for adapter_name, declared_families, _ in ADAPTERS:
        rows = adapter_rows[adapter_name]
        observed = {
            family: sum(row.base_family == family for row in rows)
            for family in declared_families
        }
        expected = {family: expected_counts[family] for family in declared_families}
        output[adapter_name] = {
            "declared_families": list(declared_families),
            "expected_direction_counts": expected,
            "observed_direction_counts": observed,
            "direction_count": len(rows),
            "all_expected_counts_positive": all(value > 0 for value in expected.values()),
            "all_observed_counts_positive": all(value > 0 for value in observed.values()),
            "counts_match": observed == expected,
        }
    return output


def dense_shape_audit(
    rows: tuple[quadratic.DirectionDerivative, ...],
) -> dict[str, Any]:
    bad_gradient = [
        row.direction_id for row in rows if np.asarray(row.gradient).shape != (486,)
    ]
    bad_hessian = [
        row.direction_id
        for row in rows
        if np.asarray(row.hessian).shape != (486, 486)
    ]
    nonfinite = [
        row.direction_id
        for row in rows
        if not (
            np.all(np.isfinite(np.asarray(row.gradient).real))
            and np.all(np.isfinite(np.asarray(row.gradient).imag))
            and np.all(np.isfinite(np.asarray(row.hessian).real))
            and np.all(np.isfinite(np.asarray(row.hessian).imag))
        )
    ]
    asymmetry = {
        row.direction_id: float(
            np.max(np.abs(np.asarray(row.hessian) - np.asarray(row.hessian).T))
        )
        for row in rows
    }
    return {
        "bad_gradient_shapes": bad_gradient,
        "bad_Hessian_shapes": bad_hessian,
        "nonfinite_directions": nonfinite,
        "maximum_Hessian_asymmetry": max(asymmetry.values()) if asymmetry else 0.0,
        "per_direction_Hessian_asymmetry": asymmetry,
    }


@lru_cache(maxsize=1)
def build_report() -> dict[str, Any]:
    state = potential.deterministic_state(3104)
    live_directions = potential.evaluate_directions(state)
    live_parameters = potential.parameter_schema(live_directions)
    live_parameter_ids = {row.parameter_id for row in live_parameters}
    expected_counts = g1_family_direction_counts()
    owners = family_owners()
    covered = covered_families()
    all_families = all_live_families()
    adapter_rows = evaluate_adapter_rows(state)
    rows = flatten_rows(adapter_rows)
    expected_rows = expected_covered_directions(state)
    remaining_rows = remaining_directions(state)
    expected_ids = {row.direction_id for row in expected_rows}
    actual_ids = [row.direction_id for row in rows]
    actual_id_set = set(actual_ids)
    duplicate_ids = sorted(
        {direction_id for direction_id in actual_ids if actual_ids.count(direction_id) > 1}
    )
    parameters = quadratic.parameter_derivatives(rows)
    parameter_ids = [row.parameter_id for row in parameters]
    parameter_id_set = set(parameter_ids)
    duplicate_parameter_ids = sorted(
        {parameter_id for parameter_id in parameter_ids if parameter_ids.count(parameter_id) > 1}
    )
    expected_parameter_ids = {
        row.parameter_id for row in potential.parameter_schema(expected_rows)
    }
    remaining_parameter_ids = {
        row.parameter_id for row in potential.parameter_schema(remaining_rows)
    }
    coefficients = quadratic.deterministic_coefficients(parameters)
    combined = quadratic.assemble(parameters, coefficients)
    directional = quadratic.five_point_directional_audit(
        state, parameters, coefficients
    )
    shape_audit = dense_shape_audit(rows)
    adapter_coverage = adapter_coverage_rows(adapter_rows, expected_counts)
    remaining_families = tuple(
        family for family in all_families if family not in set(covered)
    )
    ownership_duplicates = {
        family: names for family, names in owners.items() if len(names) != 1
    }
    family_direction_coverage = {
        family: {
            "expected": expected_counts[family],
            "observed": sum(row.base_family == family for row in rows),
        }
        for family in covered
    }
    value_lookup = {row.direction_id: row.value for row in live_directions}
    value_residuals = {
        row.direction_id: float(abs(row.value - value_lookup[row.direction_id]))
        for row in rows
    }

    checks = {
        "authoritative_G1_has_18_base_families": len(all_families) == 18,
        "covered_family_count_is_12": len(covered) == 12,
        "covered_families_unique": len(set(covered)) == len(covered),
        "every_covered_family_has_exactly_one_owner": not ownership_duplicates,
        "every_covered_family_is_authoritative": set(covered).issubset(set(all_families)),
        "all_adapter_expected_counts_positive": all(
            row["all_expected_counts_positive"] for row in adapter_coverage.values()
        ),
        "all_adapter_observed_counts_positive": all(
            row["all_observed_counts_positive"] for row in adapter_coverage.values()
        ),
        "all_adapter_counts_match_G1": all(
            row["counts_match"] for row in adapter_coverage.values()
        ),
        "no_duplicate_direction_ids": not duplicate_ids,
        "actual_direction_ids_equal_expected_covered_set": actual_id_set == expected_ids,
        "all_direction_values_match_live_evaluator": max(value_residuals.values()) < 1.0e-9,
        "all_gradient_shapes_are_486": not shape_audit["bad_gradient_shapes"],
        "all_Hessian_shapes_are_486x486": not shape_audit["bad_Hessian_shapes"],
        "all_dense_derivatives_finite": not shape_audit["nonfinite_directions"],
        "all_dense_Hessians_symmetric": shape_audit["maximum_Hessian_asymmetry"] < 1.0e-9,
        "no_duplicate_parameter_ids": not duplicate_parameter_ids,
        "covered_parameter_ids_equal_live_subset": parameter_id_set == expected_parameter_ids,
        "covered_parameter_ids_inside_live_91_schema": parameter_id_set.issubset(live_parameter_ids),
        "remaining_parameter_ids_disjoint": parameter_id_set.isdisjoint(remaining_parameter_ids),
        "covered_and_remaining_parameters_partition_live_schema": (
            parameter_id_set | remaining_parameter_ids
        ) == live_parameter_ids,
        "combined_gradient_has_486_entries": np.asarray(combined["gradient"]).shape == (486,),
        "combined_Hessian_is_486x486": np.asarray(combined["hessian"]).shape == (486, 486),
        "combined_value_matches_five_point_center": directional["value_residual"] < 1.0e-8,
        "combined_first_derivative_reconstructs": directional["first_residual"] < 5.0e-7,
        "combined_second_derivative_reconstructs": directional["second_residual"] < 5.0e-6,
        "remaining_family_count_is_6": len(remaining_families) == 6,
        "remaining_family_set_matches_declared_frontier": set(remaining_families)
        == set(EXPECTED_REMAINING_FAMILIES),
        "remaining_directions_nonzero": len(remaining_rows) > 0,
        "remaining_parameters_nonzero": len(remaining_parameter_ids) > 0,
        "complete_64_direction_derivatives_not_claimed": len(rows) < 64,
        "G2_not_closed": True,
        "whole_model_not_validated": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return _jsonable(
        {
            "status": (
                "G2_DERIVATIVE_COVERAGE_12_OF_18_FAMILIES_ASSEMBLED"
                if not failures
                else "G2_DERIVATIVE_COVERAGE_LEDGER_FAILED"
            ),
            "overall_state": "PARTIAL" if not failures else "EXECUTION_FAIL",
            "n_checks": len(checks),
            "n_failed": len(failures),
            "failures": failures,
            "checks": checks,
            "coverage": {
                "base_families_total": len(all_families),
                "base_families_implemented": len(covered),
                "base_families_remaining": len(remaining_families),
                "implemented_families": list(covered),
                "remaining_families": list(remaining_families),
                "directions_total": len(live_directions),
                "directions_implemented": len(rows),
                "directions_remaining": len(remaining_rows),
                "real_parameters_total": len(live_parameters),
                "real_parameters_implemented": len(parameter_id_set),
                "real_parameters_remaining": len(remaining_parameter_ids),
                "real_field_dimension": chart.TOTAL_DIM,
                "symmetric_Hessian_entries": chart.SYMMETRIC_HESSIAN_ENTRIES,
            },
            "adapter_coverage": adapter_coverage,
            "family_direction_coverage": family_direction_coverage,
            "family_owners": owners,
            "duplicate_family_owners": ownership_duplicates,
            "duplicate_direction_ids": duplicate_ids,
            "missing_expected_direction_ids": sorted(expected_ids - actual_id_set),
            "unexpected_direction_ids": sorted(actual_id_set - expected_ids),
            "duplicate_parameter_ids": duplicate_parameter_ids,
            "missing_expected_parameter_ids": sorted(
                expected_parameter_ids - parameter_id_set
            ),
            "unexpected_parameter_ids": sorted(
                parameter_id_set - expected_parameter_ids
            ),
            "maximum_direction_value_residual": max(value_residuals.values()),
            "dense_shape_audit": shape_audit,
            "combined_derivative_norms": {
                "gradient": float(np.linalg.norm(combined["gradient"])),
                "Hessian_frobenius": float(np.linalg.norm(combined["hessian"])),
                "Hessian_rank": int(np.linalg.matrix_rank(combined["hessian"], 1.0e-10)),
            },
            "combined_directional_reconstruction": directional,
            "flags": {
                "twelve_full_coordinate_family_adapters_implemented": not failures,
                "all_implemented_direction_gradients_assembled": not failures,
                "all_implemented_direction_Hessians_assembled": not failures,
                "all_64_direction_gradients_complete": False,
                "all_64_direction_Hessians_complete": False,
                "G2_closed": False,
                "G3_closed": False,
                "G4_closed": False,
                "G5_closed": False,
                "G6_closed": False,
                "G7_closed": False,
                "G8_closed": False,
                "whole_model_validated": False,
                "whole_model_excluded": False,
                "empirical_discovery": False,
            },
            "next_exact_target": (
                "Implement and verify the six remaining quartic adapters: "
                + ", ".join(remaining_families)
                + "."
            ),
            "verdict": (
                "The draft derivative chain covers twelve of eighteen authoritative "
                "base families with full 486-real gradients and Hessians and one "
                "combined fail-closed assembly. Six quartic families remain. Hosted "
                "execution is still required before promotion, and G2 remains PARTIAL."
            ),
        }
    )


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Live G2 derivative coverage ledger\n\n"
        f"**Status:** `{report['status']}`\n\n"
        + report["verdict"]
        + "\n\n"
        + "## Remaining families\n\n"
        + "\n".join(f"- `{name}`" for name in report["coverage"]["remaining_families"])
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
