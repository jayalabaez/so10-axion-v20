#!/usr/bin/env python3
"""Fail-closed source-algebra and equality frontier for physical-SM G3--G5.

The corrected physical-SM target has a reconstructed exact stationary
coefficient witness and a reconstructed rational 486-real Hessian.  This
audit answers two narrower questions without promoting that reconstruction:

* what fixed rational lattices are *observed* in the live source rows; and
* whether the squared-stationarity EFT has another equality point on the
  exact radial line ``q=t q_star``.

The radial restriction is exact.  Homogeneity gives

    V(t q_star) = A2 t^2 + A3 t^3 + A4 t^4,

and the frozen rational witness yields ``gcd(V+1,dV/dt)=t-1``.  Thus the
target is the only radial zero of ``V+1`` that is also stationary.  This is
not a classification of the full 486-field equality locus.

The row-lattice census is deliberately diagnostic.  It recognizes values,
gradients and Hessians returned by the complete 44-direction/51-parameter
compiler, but it does not derive their denominators from the projector source
formulas.  In particular, the much smaller reduced denominator of the summed
Hessian follows from cancellations that are not yet source-proved.  G3, G4
and G5 therefore remain false for the physical-SM application.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import sympy as sp

import live_g2_arbitrary_component_potential_values_v20 as potential
import physical_sm_vacuum_local_feasibility_v20 as foundation


ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "PHYSICAL_SM_SOURCE_ALGEBRA_EQUALITY_FRONTIER_V20.json"
OUT_MD = ROOT / "PHYSICAL_SM_SOURCE_ALGEBRA_EQUALITY_FRONTIER_V20.md"

SCHEMA = "physical_sm_source_algebra_equality_frontier_v20"
STATUS = "RADIAL_EQUALITY_CLOSED__FULL_SOURCE_ALGEBRA_AND_EQUALITY_ORBIT_OPEN"
MODEL_CONTRACT_ID = foundation.MODEL_CONTRACT_ID
EXPECTED_FOUNDATION_CORE_SHA256 = (
    "01f565d3382756bc467bfaa99d187188bc1bfc4060f2c3a472650f5e57537e80"
)

VALUE_DENOMINATOR_BOUND = 100_000
SOURCE_ROW_DENOMINATOR_BOUND = 12_600
EXPECTED_SOURCE_HESSIAN_ROW_LCM = 126_000
EXPECTED_AGGREGATE_HESSIAN_LCM = 6_300_103_327_590


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    return value


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(_jsonable(value), sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def _raw_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _portable_sha256(path: Path) -> str:
    raw = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(raw).hexdigest()


def source_bindings() -> dict[str, Any]:
    source = Path(foundation.__file__).resolve()
    frozen = json.loads(
        (ROOT / "PHYSICAL_SM_VACUUM_LOCAL_FEASIBILITY_V20.json").read_text(
            encoding="utf-8"
        )
    )
    observed_core = frozen["integrity"]["core_sha256"]
    if observed_core != EXPECTED_FOUNDATION_CORE_SHA256:
        raise ArithmeticError("physical-SM foundation core drifted")
    return {
        "foundation": {
            "source": source.name,
            "source_raw_sha256": _raw_sha256(source),
            "source_portable_lf_sha256": _portable_sha256(source),
            "json": "PHYSICAL_SM_VACUUM_LOCAL_FEASIBILITY_V20.json",
            "core_sha256": observed_core,
            "expected_core_sha256": EXPECTED_FOUNDATION_CORE_SHA256,
            "core_pin_matches": observed_core == EXPECTED_FOUNDATION_CORE_SHA256,
        }
    }


@lru_cache(maxsize=1)
def stationary_data() -> tuple[
    tuple[Any, ...], tuple[str, ...], tuple[Fraction, ...], np.ndarray, np.ndarray
]:
    rows = foundation.compiler_parameter_rows()
    parameter_ids = tuple(row.parameter_id for row in rows)
    values = np.asarray([float(row.value) for row in rows], dtype=float)
    gradients = np.column_stack(
        [np.asarray(row.gradient, dtype=float) for row in rows]
    )
    coefficients, reconstruction = (
        foundation.exact_reconstructed_stationary_coefficients(
            gradients, values, parameter_ids
        )
    )
    if not reconstruction["exact_reconstructed_stationarity"]:
        raise ArithmeticError("upstream reconstructed stationarity failed")
    return rows, parameter_ids, coefficients, values, gradients


def _recognize_rational(value: float, bound: int) -> tuple[Fraction, float]:
    exact = Fraction(float(value)).limit_denominator(bound)
    return exact, abs(float(exact) - float(value))


def _lcm(values: Iterable[int]) -> int:
    result = 1
    for value in values:
        result = math.lcm(result, int(value))
    return result


def _array_lattice(
    array: np.ndarray, *, denominator_bound: int, zero_tolerance: float = 1.0e-13
) -> dict[str, Any]:
    source = np.asarray(array, dtype=float).ravel()
    active = source[np.abs(source) > zero_tolerance]
    fractions: list[Fraction] = []
    maximum_residual = 0.0
    for value in active:
        exact, residual = _recognize_rational(float(value), denominator_bound)
        if residual >= 1.0e-10:
            raise ArithmeticError("compiler entry left the declared rational scout")
        fractions.append(exact)
        maximum_residual = max(maximum_residual, residual)
    denominators = sorted({value.denominator for value in fractions})
    return {
        "nonzero_entry_count": len(fractions),
        "distinct_denominator_count": len(denominators),
        "maximum_entry_denominator": max(denominators, default=1),
        "observed_denominator_lcm": _lcm(denominators),
        "maximum_reconstruction_residual": maximum_residual,
        "continued_fraction_denominator_bound": denominator_bound,
        "source_derived_denominator_bound": False,
        "proof_grade": False,
    }


@lru_cache(maxsize=1)
def observed_source_row_lattice_census() -> dict[str, Any]:
    rows, parameter_ids, coefficients, _values, _gradients = stationary_data()
    support = tuple(
        (row, coefficient)
        for row, coefficient in zip(rows, coefficients, strict=True)
        if coefficient
    )
    value_census = _array_lattice(
        np.asarray([float(row.value) for row, _coefficient in support]),
        denominator_bound=VALUE_DENOMINATOR_BOUND,
    )
    gradient_census = _array_lattice(
        np.concatenate(
            [np.asarray(row.gradient, dtype=float).ravel() for row, _ in support]
        ),
        denominator_bound=SOURCE_ROW_DENOMINATOR_BOUND,
    )
    hessian_census = _array_lattice(
        np.concatenate(
            [np.asarray(row.hessian, dtype=float).ravel() for row, _ in support]
        ),
        denominator_bound=SOURCE_ROW_DENOMINATOR_BOUND,
    )
    coefficient_denominator_lcm = _lcm(
        coefficient.denominator for _row, coefficient in support
    )
    naive_source_hessian_product_lattice = (
        coefficient_denominator_lcm * hessian_census["observed_denominator_lcm"]
    )

    entries, aggregate = foundation.reconstructed_exact_hessian()
    if any(radical for _rational, radical in entries.values()):
        raise ArithmeticError("physical-SM aggregate Hessian ceased to be rational")
    aggregate_lcm = _lcm(
        rational.denominator for rational, _radical in entries.values()
    )
    if aggregate_lcm != EXPECTED_AGGREGATE_HESSIAN_LCM:
        raise ArithmeticError("aggregate reconstructed Hessian LCM drifted")
    if hessian_census["observed_denominator_lcm"] != EXPECTED_SOURCE_HESSIAN_ROW_LCM:
        raise ArithmeticError("observed source-row Hessian LCM drifted")

    return {
        "evidence_kind": "float_compiler_rational_lattice_census_only",
        "supported_parameter_count": len(support),
        "supported_parameter_ids": [row.parameter_id for row, _ in support],
        "all_supported_parameters_are_Hermitian_lambda_components": all(
            row.parameter_id.startswith("lambda::") for row, _ in support
        ),
        "value_rows": value_census,
        "gradient_rows": gradient_census,
        "Hessian_rows": hessian_census,
        "coefficient_denominator_lcm": coefficient_denominator_lcm,
        "naive_source_Hessian_product_lattice_denominator": (
            naive_source_hessian_product_lattice
        ),
        "reconstructed_aggregate_Hessian_nonzero_entries": len(entries),
        "reconstructed_aggregate_Hessian_denominator_lcm": aggregate_lcm,
        "aggregate_to_coefficient_lcm_ratio": str(
            Fraction(aggregate_lcm, coefficient_denominator_lcm)
        ),
        "aggregate_denominator_is_strictly_smaller_than_naive_product": (
            aggregate_lcm < naive_source_hessian_product_lattice
        ),
        "aggregate_cancellation_source_proved": False,
        "direct_exact_projector_arithmetic_used_for_rows": False,
        "source_algebra_derivation_complete": False,
        "proof_grade": False,
        "limitation": (
            "The live rows are recognized on rational lattices, but their "
            "denominator bounds and the aggregate cancellation have not been "
            "derived from exact projector formulas."
        ),
    }


@lru_cache(maxsize=1)
def exact_radial_equality_certificate() -> dict[str, Any]:
    rows, _parameter_ids, coefficients, _values, _gradients = stationary_data()
    directions = {
        row.direction_id: row
        for row in potential.evaluate_directions(foundation.target_state())
    }
    homogeneous_coefficients = {2: Fraction(0), 3: Fraction(0), 4: Fraction(0)}
    maximum_value_residual = 0.0
    for row, coefficient in zip(rows, coefficients, strict=True):
        if not coefficient:
            continue
        exact_value, residual = _recognize_rational(
            float(row.value), VALUE_DENOMINATOR_BOUND
        )
        maximum_value_residual = max(maximum_value_residual, residual)
        degree = int(directions[row.direction_id].degree)
        homogeneous_coefficients[degree] += coefficient * exact_value

    t = sp.Symbol("t")
    polynomial = sum(
        sp.Rational(value.numerator, value.denominator) * t**degree
        for degree, value in homogeneous_coefficients.items()
    )
    derivative = sp.diff(polynomial, t)
    equality_polynomial = sp.expand(polynomial + 1)
    gcd = sp.Poly(derivative, t, domain=sp.QQ).gcd(
        sp.Poly(equality_polynomial, t, domain=sp.QQ)
    )
    gcd_monic = gcd.monic()
    expected = sp.Poly(t - 1, t, domain=sp.QQ)
    stationary_roots = sp.solve(derivative, t)
    stationary_values = {
        str(root): str(sp.factor(polynomial.subs(t, root)))
        for root in stationary_roots
    }
    coefficient_sum = sum(homogeneous_coefficients.values())

    return {
        "evidence_kind": "exact_Q_homogeneity_and_univariate_polynomial_gcd",
        "radial_line": "q=t*q_star with real t",
        "homogeneous_coefficients": {
            f"A{degree}": str(value)
            for degree, value in homogeneous_coefficients.items()
        },
        "coefficient_sum_V_at_t1": str(coefficient_sum),
        "V_of_t_factorized": str(sp.factor(polynomial)),
        "dV_dt_factorized": str(sp.factor(derivative)),
        "V_plus_1_factorized": str(sp.factor(equality_polynomial)),
        "gcd_V_plus_1_and_dV_dt_monic": str(gcd_monic.as_expr()),
        "stationary_roots": [str(root) for root in stationary_roots],
        "stationary_values": stationary_values,
        "maximum_live_value_reconstruction_residual": maximum_value_residual,
        "V_at_t1_is_minus_one": coefficient_sum == -1,
        "target_is_stationary_on_radial_line": sp.expand(derivative).subs(t, 1) == 0,
        "target_is_only_radial_stationary_equality_point": gcd_monic == expected,
        "full_486_field_equality_orbit_classified": False,
        "physical_SM_G3_closed": False,
        "physical_SM_G4_closed": False,
        "physical_SM_G5_closed": False,
    }


def _core_payload(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": report["schema"],
        "status": report["status"],
        "model_contract_id": report["model_contract_id"],
        "source_bindings": report["source_bindings"],
        "source_row_lattice_frontier": report["source_row_lattice_frontier"],
        "exact_radial_equality": report["exact_radial_equality"],
        "closure_claims": report["closure_claims"],
        "next_required_calculation": report["next_required_calculation"],
    }


def build_report() -> dict[str, Any]:
    source = observed_source_row_lattice_census()
    radial = exact_radial_equality_certificate()
    claims = {
        "radial_stationary_equality_classified_exactly": radial[
            "target_is_only_radial_stationary_equality_point"
        ],
        "direct_source_algebra_stationary_Hessian_available": False,
        "complete_global_equality_orbit_proved": False,
        "physical_SM_G3_closed": False,
        "physical_SM_G4_closed": False,
        "physical_SM_G5_closed": False,
        "old_formal_U1_89_EFT_scope_promoted": False,
    }
    checks = {
        "foundation_core_pin_matches": source_bindings()["foundation"][
            "core_pin_matches"
        ],
        "all_37_nonzero_witness_parameters_are_Hermitian": source[
            "all_supported_parameters_are_Hermitian_lambda_components"
        ]
        and source["supported_parameter_count"] == 37,
        "observed_source_Hessian_row_lcm_is_126000": source["Hessian_rows"][
            "observed_denominator_lcm"
        ]
        == EXPECTED_SOURCE_HESSIAN_ROW_LCM,
        "aggregate_reconstructed_Hessian_lcm_is_frozen": source[
            "reconstructed_aggregate_Hessian_denominator_lcm"
        ]
        == EXPECTED_AGGREGATE_HESSIAN_LCM,
        "aggregate_cancellation_remains_fail_closed": not source[
            "aggregate_cancellation_source_proved"
        ],
        "exact_radial_gcd_is_t_minus_1": radial[
            "target_is_only_radial_stationary_equality_point"
        ],
        "full_equality_orbit_remains_fail_closed": not radial[
            "full_486_field_equality_orbit_classified"
        ],
        "physical_G3_G4_G5_remain_false": not any(
            claims[name]
            for name in (
                "physical_SM_G3_closed",
                "physical_SM_G4_closed",
                "physical_SM_G5_closed",
            )
        ),
    }
    failures = [name for name, passed in checks.items() if not passed]
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "model_contract_id": MODEL_CONTRACT_ID,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "source_bindings": source_bindings(),
        "source_row_lattice_frontier": source,
        "exact_radial_equality": radial,
        "closure_claims": claims,
        "next_required_calculation": [
            "replace every active float projector row by exact integer/Fraction arithmetic and prove the fixed row lattices before evaluation",
            "prove the summed stationary Hessian numerator and its rank/PSD without continued-fraction reconstruction",
            "solve or exclude all non-radial common zeros of Vren+1 and grad(Vren), modulo SO(10)xU(1)_XxPQ",
        ],
    }
    report["integrity"] = {
        "core_sha256": hashlib.sha256(
            canonical_json_bytes(_core_payload(report))
        ).hexdigest()
    }
    return report


def render_markdown(report: dict[str, Any]) -> str:
    radial = report["exact_radial_equality"]
    lattice = report["source_row_lattice_frontier"]
    return "\n".join(
        [
            "# Physical-SM source-algebra and equality frontier -- v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            "The exact radial restriction closes one strict subproblem: `gcd(V(t q*)+1,dV/dt)=t-1`, so `t=1` is the only radial stationary equality point.",
            "",
            f"- nonzero Hermitian witness parameters: `{lattice['supported_parameter_count']}`;",
            f"- observed source-Hessian row LCM: `{lattice['Hessian_rows']['observed_denominator_lcm']}` (diagnostic, not source-derived);",
            f"- reconstructed aggregate Hessian LCM: `{lattice['reconstructed_aggregate_Hessian_denominator_lcm']}`;",
            f"- radial polynomial: `{radial['V_of_t_factorized']}`;",
            f"- radial stationary/equality gcd: `{radial['gcd_V_plus_1_and_dV_dt_monic']}`.",
            "",
            "The complete projector-exact Hessian numerator and the non-radial 486-field equality-orbit classification remain open. Physical G3, G4, and G5 are not closed. The historical U(1)_89 EFT scope is not promoted.",
            "",
            f"Core SHA-256: `{report['integrity']['core_sha256']}`.",
        ]
    ) + "\n"


def write_outputs() -> dict[str, Any]:
    report = build_report()
    OUT_JSON.write_text(
        json.dumps(_jsonable(report), indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    OUT_MD.write_text(render_markdown(report), encoding="utf-8", newline="\n")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    report = write_outputs() if args.write else build_report()
    print(json.dumps(_jsonable(report), indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
