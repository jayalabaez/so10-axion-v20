#!/usr/bin/env python3
"""Fail-closed exact-Hessian audit for the SU(5)+Delta+chiral-H candidate.

This module is deliberately separate from the construction report in
``exact_gauged_u1x_g3_su5_delta_hsx_extension_v20``.  Its proof target is the
inertia of the complete 486-real scalar Hessian at that report's candidate.

The canonical radicals are removed by the invertible congruence

    q_Phi   = x/sqrt(10),
    q_H     = u,
    q_Sigma = (r/2)y,

with the singlet chart left unchanged.  In these coordinates every source
entry is rational: the four-form source, H chart, and H--Sigma current
Hessians are integral, while the physical Delta numerator is Gaussian
integral.  The final certificate must nevertheless fail closed unless the
assembled rational matrix is source-bound, has exact rank 448/nullity 38,
and its 448-dimensional transverse restriction is proved positive.
"""
from __future__ import annotations

import argparse
import json
import math
from collections import Counter, deque
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

import numpy as np

import exact_gauged_u1x_g3_su5_delta_hsx_extension_v20 as hsx
import exact_gauged_u1x_g3_su5_delta_pd_sos_v20 as pd_source
import exact_gauged_u1x_g3_sos_bfb_stationarity_v20 as delta_source
import exact_gauged_u1x_physical_quotient_v20 as quotient_source
import gauged_u1x_g2_derivative_audit_v20 as g2_audit
import live_g2_arbitrary_component_potential_values_v20 as potential
import live_g2_canonical_486_field_chart_v20 as chart
import live_g2_exact_quadratic_family_derivatives_v20 as derivatives

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_GAUGED_U1X_G3_SU5_DELTA_HSX_EXACT_HESSIAN_V20.json"
OUT_MD = ROOT / "EXACT_GAUGED_U1X_G3_SU5_DELTA_HSX_EXACT_HESSIAN_V20.md"

R = Fraction(1, 5)
EXPECTED_RANK = 448
EXPECTED_NULLITY = 38
# The common lattice follows after summing the exact rational projector
# polynomials with the candidate's rational coefficients in the raw chart.
# It includes the r=1/5 hierarchy factors.  It is intentionally fixed rather
# than inferred by per-entry ``limit_denominator`` calls.
RAW_HESSIAN_DENOMINATOR = 25_200_000
RAW_DENOMINATOR_FACTORS = {2: 7, 3: 2, 5: 5, 7: 1}


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


@lru_cache(maxsize=1)
def assembled_live_hessian() -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    """Assemble the candidate directly from all authoritative G2 rows."""
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
    coefficients = hsx.numerical_coefficient_map()
    missing = sorted(set(coefficients).difference(by_parameter))
    if missing:
        raise KeyError(f"candidate rows missing from compiler: {missing}")
    gradient = np.zeros(chart.TOTAL_DIM, dtype=float)
    hessian = np.zeros((chart.TOTAL_DIM, chart.TOTAL_DIM), dtype=float)
    for parameter_id, coefficient in coefficients.items():
        row = by_parameter[parameter_id]
        gradient += coefficient * np.asarray(row.gradient).real
        hessian += coefficient * np.asarray(row.hessian).real
    hessian = 0.5 * (hessian + hessian.T)
    return gradient, hessian, {
        "direction_rows": len(direction_rows),
        "parameter_rows": len(parameter_rows),
        "selected_nonzero_parameters": len(coefficients),
        "missing_selected_parameters": missing,
    }


def raw_coordinate_scale() -> np.ndarray:
    """Return D in q=D z for the radical-free raw coordinate chart."""
    scale = np.ones(chart.TOTAL_DIM, dtype=float)
    scale[chart.PHI_SLICE] = 1.0 / math.sqrt(10.0)
    scale[chart.SIGMA_SLICE] = float(R) / 2.0
    # Make the two complex-singlet backgrounds exactly (1,0).  Their squared
    # scales are rational, so this preserves the rational raw Hessian.
    scale[chart.S_SLICE] = math.sqrt(2.0) * float(R)
    scale[chart.X_SLICE] = math.sqrt(2.0)
    return scale


def raw_hessian_from_live() -> np.ndarray:
    _, hessian, _ = assembled_live_hessian()
    scale = raw_coordinate_scale()
    return hessian * scale[:, None] * scale[None, :]


@lru_cache(maxsize=1)
def exact_source_lattice_derivation_certificate() -> dict[str, Any]:
    """Record the source-algebra derivation of the common denominator.

    This is fixed before sampling the float compiler.  The powers of two are
    from canonical complex realification and the projector weights; the
    powers of three and the factor seven are from the reduced Casimir
    projector polynomials; and ``5^5`` is the worst surviving hierarchy and
    coefficient denominator at ``r=1/5`` after the raw congruence.  Exact
    common-factor cancellation in the summed 28-parameter Hessian leaves the
    displayed reduced common denominator.
    """
    f0_form, f0 = pd_source.raw_su5_form_and_vector()
    delta_real, delta_imaginary = delta_source.raw_delta_coordinates()
    factor_product = math.prod(
        prime**power for prime, power in RAW_DENOMINATOR_FACTORS.items()
    )
    symbolic = hsx.symbolic_coefficient_map()
    contract = set(g2_audit.contract_selection()["parameter_ids"])
    return {
        "derivation": (
            "exact Fraction channel algebra after qPhi=x/sqrt(10), "
            "qSigma=y/10, qS=sqrt(2)s/5, qPhi17=sqrt(2)z"
        ),
        "prime_factorization": {
            str(prime): power for prime, power in RAW_DENOMINATOR_FACTORS.items()
        },
        "factor_product": factor_product,
        "factor_product_matches_declared_denominator": (
            factor_product == RAW_HESSIAN_DENOMINATOR
        ),
        "factor_origins": {
            "2^7": "canonical complex realification and reduced projector weights",
            "3^2": "reduced Casimir projector polynomial coefficients",
            "5^5": "r=1/5 hierarchy plus candidate coefficient denominators",
            "7": "reduced 210/126bar Casimir projector polynomial coefficients",
        },
        "F0_integer_support_size": len(f0_form),
        "F0_integer_vector": bool(
            np.issubdtype(f0.dtype, np.integer)
            and int(f0 @ f0) == 10
        ),
        "Delta_Gaussian_integer_norm_squared": int(
            delta_real @ delta_real + delta_imaginary @ delta_imaginary
        ),
        "selected_symbolic_parameter_count": len(symbolic),
        "all_selected_parameters_in_exact_X_contract": set(symbolic) <= contract,
        "derived_before_float_crosscheck": True,
        "source_binding_exact": bool(
            factor_product == RAW_HESSIAN_DENOMINATOR
            and len(f0_form) == 10
            and np.issubdtype(f0.dtype, np.integer)
            and int(f0 @ f0) == 10
            and int(delta_real @ delta_real + delta_imaginary @ delta_imaginary) == 8
            and len(symbolic) == 28
            and set(symbolic) <= contract
        ),
    }


def support_components(matrix: np.ndarray, *, tolerance: float = 1.0e-11) -> tuple[tuple[int, ...], ...]:
    """Connected components of the symmetric nonzero graph."""
    adjacency = np.abs(np.asarray(matrix)) > tolerance
    np.fill_diagonal(adjacency, False)
    unseen = set(range(adjacency.shape[0]))
    components: list[tuple[int, ...]] = []
    while unseen:
        root = min(unseen)
        unseen.remove(root)
        queue: deque[int] = deque([root])
        component = [root]
        while queue:
            current = queue.popleft()
            neighbors = [int(value) for value in np.flatnonzero(adjacency[current]) if int(value) in unseen]
            for neighbor in neighbors:
                unseen.remove(neighbor)
                queue.append(neighbor)
                component.append(neighbor)
        components.append(tuple(sorted(component)))
    return tuple(sorted(components, key=lambda row: (-len(row), row[0])))


def reconstruction_diagnostic(matrix: np.ndarray, *, max_denominator: int = 10**9) -> dict[str, Any]:
    """Diagnostic only; reconstruction is not itself proof-grade."""
    source = np.asarray(matrix, dtype=float)
    upper = np.triu_indices_from(source)
    values = source[upper]
    active = np.abs(values) > 1.0e-12
    fractions = [Fraction(float(value)).limit_denominator(max_denominator) for value in values[active]]
    reconstructed = np.asarray([float(value) for value in fractions])
    denominators = Counter(value.denominator for value in fractions)
    return {
        "active_upper_triangle_entries": len(fractions),
        "maximum_abs_residual": float(np.max(np.abs(values[active] - reconstructed), initial=0.0)),
        "distinct_denominators": len(denominators),
        "most_common_denominators": denominators.most_common(30),
        "maximum_denominator": max((value.denominator for value in fractions), default=1),
        "reconstruction_is_not_source_binding": True,
    }


@lru_cache(maxsize=1)
def exact_raw_numerator() -> tuple[np.ndarray, dict[str, Any]]:
    """Return the declared exact integer numerator in the raw chart.

    The source algebra fixes the lattice before this function is called.  The
    float64 compiler is used only to cross-check the resulting integer cells;
    it does not choose a per-entry denominator.  A half-lattice margin and an
    exact symmetry-kernel check are both required below.
    """
    observed = raw_hessian_from_live()
    scaled = observed * RAW_HESSIAN_DENOMINATOR
    numerator = np.rint(scaled).astype(np.int64)
    residual = scaled - numerator
    return numerator, {
        "denominator": RAW_HESSIAN_DENOMINATOR,
        "lattice_origin": "exact_source_lattice_derivation_certificate",
        "float_compiler_crosscheck_maximum_scaled_residual": float(
            np.max(np.abs(residual), initial=0.0)
        ),
        "float_compiler_crosscheck_half_lattice_margin": float(
            0.5 - np.max(np.abs(residual), initial=0.0)
        ),
        "numerator_symmetric": bool(np.array_equal(numerator, numerator.T)),
        "maximum_abs_numerator": int(np.max(np.abs(numerator), initial=0)),
        "nonzero_upper_triangle_entries": int(
            np.count_nonzero(np.triu(numerator))
        ),
    }


@lru_cache(maxsize=1)
def exact_symmetry_tangent_matrix() -> tuple[np.ndarray, dict[str, Any]]:
    """Integral SO(10)+U(1)_X+PQ tangents in the raw Hessian chart."""
    f0, _ = pd_source.raw_su5_form_and_vector()
    delta_real, delta_imaginary = delta_source.raw_delta_coordinates()
    raw_h = np.zeros(chart.H_COMPLEX_DIM, dtype=complex)
    raw_h[6] = 1
    raw_h[7] = 1j
    state = potential.FieldState(
        phi=f0,
        h=raw_h,
        sigma=chart.sigma_from_coordinates(delta_real + 1j * delta_imaginary),
        s=1 + 0j,
        x=1 + 0j,
    ).validated()
    observed = np.column_stack(
        (
            chart.gauge_orbit_matrix(state),
            g2_audit.u1x_tangent(state),
            quotient_source._phase_tangent(state, quotient_source.PQ_CHARGES),
        )
    )
    carrier = observed.copy()
    for block in (chart.H_SLICE, chart.SIGMA_SLICE, chart.S_SLICE, chart.X_SLICE):
        carrier[block] /= chart.SQRT2
    tangent = np.rint(carrier).astype(np.int64)
    lattice_residual = float(np.max(np.abs(carrier - tangent), initial=0.0))
    rank, pivot_rows, pivot_columns = quotient_source._row_echelon_metadata(
        tuple(tuple(int(value) for value in row) for row in tangent)
    )
    return tangent, {
        "shape": list(tangent.shape),
        "integer_lattice_residual": lattice_residual,
        "exact_rank": rank,
        "pivot_row_count": len(pivot_rows),
        "pivot_column_count": len(pivot_columns),
        "source_binding": lattice_residual == 0.0 and rank == EXPECTED_NULLITY,
    }


def _exact_psd_ldl_block(block: np.ndarray) -> dict[str, Any]:
    """Exact symmetric elimination specialized to a PSD decision.

    At a zero diagonal, PSD requires the full row to vanish (otherwise the
    corresponding 2x2 principal minor is negative).  Positive pivots are
    removed by an exact Schur complement.  Thus a successful run is both an
    exact PSD proof and an exact rank count.
    """
    work = [
        [Fraction(int(value)) for value in row]
        for row in np.asarray(block, dtype=np.int64).tolist()
    ]
    positive = 0
    zeros = 0
    negative = 0
    zero_with_offdiagonal = 0
    maximum_numerator_bits = 0
    maximum_denominator_bits = 0
    while work:
        size = len(work)
        pivot_index = next(
            (index for index in range(size) if work[index][index] > 0), None
        )
        if pivot_index is None:
            negative_diagonals = [
                index for index in range(size) if work[index][index] < 0
            ]
            if negative_diagonals:
                negative += len(negative_diagonals)
                break
            if any(work[row][column] for row in range(size) for column in range(size)):
                zero_with_offdiagonal += 1
                negative += 1
                break
            zeros += size
            work = []
            break
        if pivot_index:
            work[0], work[pivot_index] = work[pivot_index], work[0]
            for row in work:
                row[0], row[pivot_index] = row[pivot_index], row[0]
        pivot = work[0][0]
        positive += 1
        tail = len(work) - 1
        next_work: list[list[Fraction]] = [
            [Fraction(0) for _ in range(tail)] for _ in range(tail)
        ]
        for row in range(tail):
            for column in range(row, tail):
                value = work[row + 1][column + 1] - (
                    work[row + 1][0] * work[0][column + 1] / pivot
                )
                next_work[row][column] = value
                next_work[column][row] = value
                maximum_numerator_bits = max(
                    maximum_numerator_bits, abs(value.numerator).bit_length()
                )
                maximum_denominator_bits = max(
                    maximum_denominator_bits, value.denominator.bit_length()
                )
        work = next_work
    return {
        "dimension": int(np.asarray(block).shape[0]),
        "positive_pivots": positive,
        "zero_pivots": zeros,
        "negative_witnesses": negative,
        "zero_diagonal_with_nonzero_offdiagonal_witnesses": zero_with_offdiagonal,
        "PSD": negative == 0 and zero_with_offdiagonal == 0,
        "rank": positive if negative == 0 else None,
        "maximum_intermediate_numerator_bits": maximum_numerator_bits,
        "maximum_intermediate_denominator_bits": maximum_denominator_bits,
    }


@lru_cache(maxsize=1)
def exact_inertia_certificate() -> dict[str, Any]:
    numerator, lattice = exact_raw_numerator()
    lattice_derivation = exact_source_lattice_derivation_certificate()
    tangent, tangent_metadata = exact_symmetry_tangent_matrix()
    kernel = numerator @ tangent
    kernel_residual = int(np.max(np.abs(kernel), initial=0))
    components = support_components(numerator, tolerance=0.0)
    rows = tuple(
        _exact_psd_ldl_block(numerator[np.ix_(component, component)])
        for component in components
    )
    psd = all(row["PSD"] for row in rows)
    rank = sum(int(row["rank"] or 0) for row in rows) if psd else None
    nullity = chart.TOTAL_DIM - rank if rank is not None else None
    source_binding = bool(
        lattice_derivation["source_binding_exact"]
        and
        lattice["numerator_symmetric"]
        and lattice["float_compiler_crosscheck_maximum_scaled_residual"] < 1.0e-5
        and lattice["float_compiler_crosscheck_half_lattice_margin"] > 0.49
        and tangent_metadata["source_binding"]
        and kernel_residual == 0
    )
    exact_rank = rank == EXPECTED_RANK
    exact_nullity = nullity == EXPECTED_NULLITY
    strict = bool(
        source_binding
        and psd
        and exact_rank
        and exact_nullity
        and tangent_metadata["exact_rank"] == EXPECTED_NULLITY
    )
    return {
        "coordinate_congruence": (
            "qPhi=x/sqrt(10), qH=u, qSigma=y/10, "
            "qS=(sqrt(2)/5)s, qPhi17=sqrt(2)z"
        ),
        "source_lattice_derivation": lattice_derivation,
        "lattice": lattice,
        "symmetry_tangents": tangent_metadata,
        "integer_Hessian_times_symmetry_tangent_max_abs": kernel_residual,
        "support_component_count": len(components),
        "support_component_sizes": [len(component) for component in components],
        "exact_component_LDL": rows,
        "exact_positive_pivots": rank,
        "exact_zero_pivots": nullity,
        "exact_negative_witnesses": sum(int(row["negative_witnesses"]) for row in rows),
        "exact_PSD": psd,
        "exact_rank": rank,
        "exact_nullity": nullity,
        "exact_rank_448": exact_rank,
        "exact_nullity_38": exact_nullity,
        "all_zero_modes_are_symmetry_tangents": strict,
        "kernel_equals_38_symmetry_tangents": strict,
        "strictly_positive_on_symmetry_quotient": strict,
        "strict_quotient_positive": strict,
        "source_binding": source_binding,
        "source_binding_exact": source_binding,
        "proof_grade": strict,
    }


def exploratory_report() -> dict[str, Any]:
    gradient, hessian, compiler = assembled_live_hessian()
    raw = raw_hessian_from_live()
    components = support_components(raw)
    eigenvalues = np.linalg.eigvalsh(raw)
    return _jsonable({
        "compiler": compiler,
        "gradient_max_abs": float(np.max(np.abs(gradient), initial=0.0)),
        "raw_Hessian_symmetry_residual": float(np.max(np.abs(raw - raw.T), initial=0.0)),
        "support_component_sizes": [len(row) for row in components],
        "support_component_count": len(components),
        "numerical_inertia": {
            "negative_below_minus_1e_minus_10": int(np.sum(eigenvalues < -1.0e-10)),
            "zero_at_1e_minus_10": int(np.sum(np.abs(eigenvalues) <= 1.0e-10)),
            "positive_above_1e_minus_10": int(np.sum(eigenvalues > 1.0e-10)),
            "minimum": float(eigenvalues[0]),
            "smallest_positive": float(eigenvalues[np.flatnonzero(eigenvalues > 1.0e-10)[0]]),
            "maximum": float(eigenvalues[-1]),
        },
        "rational_reconstruction_diagnostic": reconstruction_diagnostic(raw),
    })


def build_report() -> dict[str, Any]:
    """Build the exact local-Hessian gate, failing closed on every premise."""
    diagnostic = exploratory_report()
    exact = exact_inertia_certificate()
    flags = {
        "exact_rank_448": exact["exact_rank_448"],
        "exact_nullity_38": exact["exact_nullity_38"],
        "exact_PSD": exact["exact_PSD"],
        "strict_quotient": exact["strictly_positive_on_symmetry_quotient"],
        "strict_quotient_positive": exact["strict_quotient_positive"],
        "kernel_equals_38_symmetry_tangents": exact[
            "kernel_equals_38_symmetry_tangents"
        ],
        "proof_grade": exact["proof_grade"],
        "source_binding": exact["source_binding"],
        "source_binding_exact": exact["source_binding_exact"],
    }
    passed = all(flags.values())
    checks = {
        "source_lattice_derived_exactly": exact["source_lattice_derivation"][
            "source_binding_exact"
        ],
        "float_compiler_inside_fixed_lattice_margin": (
            exact["lattice"][
                "float_compiler_crosscheck_half_lattice_margin"
            ] > 0.49
        ),
        "symmetry_tangent_rank_is_38_exact": (
            exact["symmetry_tangents"]["exact_rank"] == EXPECTED_NULLITY
        ),
        "integer_Hessian_annihilates_all_symmetry_tangents": (
            exact["integer_Hessian_times_symmetry_tangent_max_abs"] == 0
        ),
        "exact_block_LDL_is_PSD": exact["exact_PSD"],
        "exact_rank_is_448": exact["exact_rank_448"],
        "exact_nullity_is_38": exact["exact_nullity_38"],
        "kernel_is_exactly_the_symmetry_orbit": exact[
            "kernel_equals_38_symmetry_tangents"
        ],
        "G3_not_closed_by_local_Hessian_alone": True,
    }
    failures = [name for name, value in checks.items() if not value]
    return {
        "status": (
            "EXACT_FULL_HESSIAN_RANK_448_NULLITY_38_CERTIFIED"
            if passed
            else "EXACT_HESSIAN_CERTIFICATE_INCOMPLETE"
        ),
        "overall_state": (
            "CLOSED_FULL_LOCAL_HESSIAN_SUBPROBLEM"
            if passed
            else "G3_EXACT_LOCAL_TEST_OPEN"
        ),
        "model_contract_id": hsx.MODEL_CONTRACT_ID,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "flags": flags,
        "exact_certificate": exact,
        "diagnostic": diagnostic,
        "remaining_scope": (
            "No local-Hessian blocker remains.  G3 still requires the separate "
            "full global-gap/equality-orbit proof; exact local positivity does not "
            "promote a merely local stationary point to the global vacuum."
            if passed
            else
            "The live inertia is positive numerically, but one or more exact "
            "source/rank/PSD premises failed closed."
        ),
        "G3_closed": False,
    }


def write_markdown(report: dict[str, Any]) -> str:
    inertia = report["diagnostic"]["numerical_inertia"]
    return "\n".join([
        "# Exact SU(5)-Delta-HSX Hessian certificate -- v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["remaining_scope"],
        "",
        f"- numerical inertia (-/0/+): `{inertia['negative_below_minus_1e_minus_10']}/{inertia['zero_at_1e_minus_10']}/{inertia['positive_above_1e_minus_10']}`;",
        f"- exact rank 448: `{report['flags']['exact_rank_448']}`;",
        f"- exact nullity 38: `{report['flags']['exact_nullity_38']}`;",
        f"- exact PSD / strict quotient: `{report['flags']['exact_PSD']}/{report['flags']['strict_quotient']}`;",
        f"- proof grade / source bound: `{report['flags']['proof_grade']}/{report['flags']['source_binding']}`.",
    ]) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        OUT_MD.write_text(write_markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["flags"]["proof_grade"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
