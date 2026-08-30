#!/usr/bin/env python3
"""Conditional exact spectrum of the rebuilt physical-SM EFT Hessian.

This follow-up consumes the immutable rational Hessian reconstructed by
``physical_sm_vacuum_local_feasibility_v20``.  It is exact *on that
reconstructed lattice*, but it does not promote the upstream application to a
source-algebra theorem.

For the squared-stationarity EFT

    U = a(Vren+1)^2 + b ||grad Vren||^2,       a,b>0,

the target Hessian is ``H_U=2 b H^T H=2 b H^2``.  The canonical 486-real
coordinates obey ``T_kin=1/2 dq^T dq``, hence the generalized characteristic
problem is ``det(H_U-rho K)`` with ``K=I_486``.  ``rho`` denotes a tree-level
Hessian eigenvalue, not a pole mass.

The exact rational ``H`` splits into 43 coordinate components of size at most
30.  Their characteristic polynomials factor into 45 distinct monic
irreducibles over Q.  Exact eigenspace algebra assigns every factor to joint
``(12 C2[SU3_C], Q3^2)`` sectors.  Resultants under ``y=t^2`` give the exact
dimensionless spectrum ``y=rho/(2b)``.  All 448 nonzero roots are positive
because the upstream exact reconstructed-rank theorem shows ``H`` is
nonsingular on the quotient, while real symmetry gives ``t in R`` and
``y=t^2``; an
exact algebraic root-isolation proof for the sign of every root of ``H`` is
not claimed or required for the squared spectrum.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import sympy as sp
from scipy import sparse

import live_g2_canonical_486_field_chart_v20 as chart
import physical_sm_vacuum_local_feasibility_v20 as foundation

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "CONDITIONAL_PHYSICAL_SM_EFT_HESSIAN_SPECTRUM_V20.json"
OUT_MD = ROOT / "CONDITIONAL_PHYSICAL_SM_EFT_HESSIAN_SPECTRUM_V20.md"

STATUS = (
    "CONDITIONAL_EXACT_PHYSICAL_SM_EFT_HESSIAN_SPECTRUM__"
    "SOURCE_ALGEBRA_POLE_AND_RELEASE_CLOSURE_OPEN"
)
T = sp.Symbol("t")
Y = sp.Symbol("y")


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
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def source_bindings() -> dict[str, Any]:
    source = Path(foundation.__file__).resolve()
    report = foundation.OUT_JSON.resolve()
    frozen = json.loads(report.read_text(encoding="utf-8"))
    expected = {
        "foundation_core_sha256": "01f565d3382756bc467bfaa99d187188bc1bfc4060f2c3a472650f5e57537e80",
        "foundation_source_sha256": "629ea8c45f101f82b6b4e963fd1fb19dcc5735fe52a1d8efb1fb0812dbaa565c",
        "foundation_JSON_sha256": "ac575067550472afeae1d87503c04a47bf27386223a4417cf7c2341ad75af315",
        "foundation_sparse_Hessian_sha256": "58e39ea9a982ac71fd696de93d8d8bc51dd1e153399bfa6f7cbcc368fc6b7458",
    }
    actual = {
        "foundation_core_sha256": frozen["integrity"]["core_sha256"],
        "foundation_source_sha256": _raw_sha256(source),
        "foundation_JSON_sha256": _raw_sha256(report),
        "foundation_sparse_Hessian_sha256": frozen[
            "exact_reconstructed_Hessian_rank"
        ]["reconstruction"]["canonical_sparse_matrix_sha256"],
    }
    if actual != expected:
        raise ArithmeticError("conditional spectrum foundation binding drifted")
    return {
        "expected": expected,
        "actual": actual,
        "all_terminal_foundation_pins_match": True,
        "foundation_source_portable_lf_sha256": _portable_sha256(source),
    }


def kinetic_metric_certificate() -> dict[str, Any]:
    """Bind K=I to the canonical chart's executable kinetic identity."""
    basis_checks: list[bool] = []
    pair_checks: list[bool] = []
    zero = np.zeros(chart.TOTAL_DIM, dtype=float)
    for index in range(chart.TOTAL_DIM):
        vector = zero.copy()
        vector[index] = 1.0
        basis_checks.append(chart.coordinate_kinetic_quadratic(vector) == 0.5)
    # Polarize the executable quadratic form on adversarial cross-block pairs.
    pairs = ((0, 209), (209, 226), (226, 382), (382, 482), (482, 484), (483, 485))
    for first, second in pairs:
        left = zero.copy()
        right = zero.copy()
        left[first] = 1.0
        right[second] = 1.0
        bilinear = (
            chart.coordinate_kinetic_quadratic(left + right)
            - chart.coordinate_kinetic_quadratic(left)
            - chart.coordinate_kinetic_quadratic(right)
        )
        pair_checks.append(bilinear == 0.0)
    return {
        "source_function": "live_g2_canonical_486_field_chart_v20.coordinate_kinetic_quadratic",
        "source_identity": "coordinate_kinetic_quadratic(q)=1/2*q^T*q",
        "field_dimension": chart.TOTAL_DIM,
        "all_486_basis_norms_equal_one_half": all(basis_checks),
        "adversarial_cross_block_polarization_pairs": [list(pair) for pair in pairs],
        "all_adversarial_cross_terms_are_zero": all(pair_checks),
        "generalized_kinetic_metric": "K=I_486",
        "generalized_characteristic_equation": "det(H_U-rho*K)=0",
        "Euclidean_eigenproblem_is_canonically_normalized": all(basis_checks) and all(pair_checks),
    }


def _coordinate_components(
    entries: dict[tuple[int, int], tuple[Fraction, Fraction]]
) -> tuple[tuple[int, ...], ...]:
    adjacency = [set() for _ in range(chart.TOTAL_DIM)]
    for first, second in entries:
        if first != second:
            adjacency[first].add(second)
            adjacency[second].add(first)
    unseen = set(range(chart.TOTAL_DIM))
    components: list[tuple[int, ...]] = []
    while unseen:
        root = min(unseen)
        unseen.remove(root)
        stack = [root]
        component = [root]
        while stack:
            current = stack.pop()
            for neighbor in sorted(adjacency[current].intersection(unseen)):
                unseen.remove(neighbor)
                stack.append(neighbor)
                component.append(neighbor)
        components.append(tuple(sorted(component)))
    return tuple(sorted(components, key=lambda row: (-len(row), row)))


def _fraction_sympy(value: Fraction) -> sp.Rational:
    return sp.Rational(value.numerator, value.denominator)


def _component_matrix(
    component: tuple[int, ...],
    entries: dict[tuple[int, int], tuple[Fraction, Fraction]],
) -> sp.ImmutableSparseMatrix:
    local: dict[tuple[int, int], sp.Rational] = {}
    for first_local, first in enumerate(component):
        for second_local, second in enumerate(component):
            rational, radical = entries.get(
                (first, second), (Fraction(0), Fraction(0))
            )
            if radical:
                raise ArithmeticError("aggregate Hessian is no longer rational")
            if rational:
                local[(first_local, second_local)] = _fraction_sympy(rational)
    return sp.ImmutableSparseMatrix(len(component), len(component), local)


def _poly_key(polynomial: sp.Poly) -> tuple[Fraction, ...]:
    monic = sp.Poly(polynomial, T, domain=sp.QQ).monic()
    return tuple(Fraction(int(value.p), int(value.q)) for value in monic.all_coeffs())


def _poly_from_key(key: tuple[Fraction, ...], variable: sp.Symbol) -> sp.Poly:
    degree = len(key) - 1
    expression = sum(
        _fraction_sympy(value) * variable ** (degree - index)
        for index, value in enumerate(key)
    )
    return sp.Poly(expression, variable, domain=sp.QQ)


@lru_cache(maxsize=1)
def exact_factorization() -> dict[str, Any]:
    entries, reconstruction = foundation.reconstructed_exact_hessian()
    if not reconstruction["aggregate_matrix_is_rational"]:
        raise ArithmeticError("conditional spectrum requires rational H")
    components = _coordinate_components(entries)
    factor_lookup: dict[tuple[Fraction, ...], int] = {}
    factor_keys: list[tuple[Fraction, ...]] = []
    component_data: list[dict[str, Any]] = []
    matrices: list[sp.ImmutableSparseMatrix] = []
    global_exponents: Counter[int] = Counter()
    for component_index, component in enumerate(components):
        matrix = _component_matrix(component, entries)
        matrices.append(matrix)
        factors: list[dict[str, int]] = []
        for expression, exponent in sp.factor_list(matrix.charpoly(T).as_expr())[1]:
            key = _poly_key(sp.Poly(expression, T, domain=sp.QQ))
            if key not in factor_lookup:
                factor_lookup[key] = len(factor_keys)
                factor_keys.append(key)
            factor_id = factor_lookup[key]
            factors.append({"factor_id": factor_id, "exponent": int(exponent)})
            global_exponents[factor_id] += int(exponent)
        component_data.append(
            {
                "component_id": component_index,
                "dimension": len(component),
                "coordinate_indices": list(component),
                "factors": factors,
            }
        )

    factor_reports: list[dict[str, Any]] = []
    for factor_id, key in enumerate(factor_keys):
        polynomial = _poly_from_key(key, T)
        root_count = int(polynomial.degree())
        real_root_count = int(sp.Poly(polynomial, T).count_roots(-sp.oo, sp.oo))
        roots = sorted(float(sp.re(root)) for root in sp.nroots(polynomial, n=30, maxsteps=200))
        factor_reports.append(
            {
                "factor_id": factor_id,
                "degree": root_count,
                "coefficients_monic_descending": [str(value) for value in key],
                "global_exponent": global_exponents[factor_id],
                "real_root_count_exact": real_root_count,
                "all_roots_real": real_root_count == root_count,
                "minimum_root_numeric": roots[0],
                "maximum_root_numeric": roots[-1],
            }
        )

    return {
        "entries": entries,
        "components": components,
        "matrices": matrices,
        "factor_keys": factor_keys,
        "component_reports": component_data,
        "factor_reports": factor_reports,
        "global_exponents": global_exponents,
    }


def _exact_commutator_stats(
    entries: dict[tuple[int, int], tuple[Fraction, Fraction]],
    operator: sparse.spmatrix,
) -> dict[str, Any]:
    h_rows: dict[int, list[tuple[int, Fraction]]] = defaultdict(list)
    for (first, second), (rational, radical) in entries.items():
        if radical:
            raise ArithmeticError("commutator left rational field")
        h_rows[first].append((second, rational))
    g_rows: dict[int, list[tuple[int, int]]] = defaultdict(list)
    csr = operator.tocsr()
    for row in range(csr.shape[0]):
        for index in range(csr.indptr[row], csr.indptr[row + 1]):
            g_rows[row].append((int(csr.indices[index]), int(csr.data[index])))
    hg: dict[tuple[int, int], Fraction] = {}
    gh: dict[tuple[int, int], Fraction] = {}
    for (first, second), (rational, _radical) in entries.items():
        for target, coefficient in g_rows.get(second, ()):
            hg[(first, target)] = hg.get((first, target), Fraction(0)) + rational * coefficient
    for first, row in g_rows.items():
        for middle, coefficient in row:
            for target, rational in h_rows.get(middle, ()):
                gh[(first, target)] = gh.get((first, target), Fraction(0)) + coefficient * rational
    keys = set(hg).union(gh)
    residuals = {
        key: hg.get(key, Fraction(0)) - gh.get(key, Fraction(0))
        for key in keys
        if hg.get(key, Fraction(0)) != gh.get(key, Fraction(0))
    }
    return {
        "operator_nonzero_entries": int(csr.nnz),
        "H_times_operator_nonzero_candidates": len(hg),
        "operator_times_H_nonzero_candidates": len(gh),
        "nonzero_exact_commutator_entries": len(residuals),
        "commutes_exactly": not residuals,
    }


def exact_commutator_certificate() -> dict[str, Any]:
    factorization = exact_factorization()
    entries = factorization["entries"]
    standard = foundation.provenance._standard_sm_generator_basis()
    ancestry = foundation.provenance._ancestry_operators()
    operators = {
        **{f"SU3_generator_{index}": generator for index, generator in enumerate(standard[:8])},
        "Q3": ancestry["standard_Q3"],
        "Q3_squared": ancestry["standard_Q3_squared"],
        "12C2_SU3": ancestry["standard_12C2_SU3"],
    }
    reports = {
        name: _exact_commutator_stats(entries, operator)
        for name, operator in operators.items()
    }
    return {
        "operators": reports,
        "all_standard_SU3C_Q3_and_Casimir_commutators_vanish_exactly": all(
            report["commutes_exactly"] for report in reports.values()
        ),
    }


def _apply_sparse_integer_operator(
    operator: sparse.spmatrix, basis: sp.ImmutableSparseMatrix
) -> sp.ImmutableSparseMatrix:
    output: dict[tuple[int, int], sp.Expr] = {}
    coo = operator.tocoo()
    for first, second, coefficient in zip(coo.row, coo.col, coo.data):
        for column in range(basis.cols):
            value = basis[int(second), column]
            if value:
                key = (int(first), column)
                output[key] = output.get(key, 0) + int(coefficient) * value
    return sp.ImmutableSparseMatrix(chart.TOTAL_DIM, basis.cols, output)


def _evaluate_matrix_polynomial(
    matrix: sp.ImmutableSparseMatrix, key: tuple[Fraction, ...]
) -> sp.MatrixBase:
    identity = sp.eye(matrix.rows)
    result: sp.MatrixBase = _fraction_sympy(key[0]) * identity
    for coefficient in key[1:]:
        result = result * matrix + _fraction_sympy(coefficient) * identity
    return result


@lru_cache(maxsize=1)
def exact_sector_assignment() -> dict[str, Any]:
    data = exact_factorization()
    factor_keys = data["factor_keys"]
    occurrences: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for component in data["component_reports"]:
        for factor in component["factors"]:
            occurrences[factor["factor_id"]].append(
                (component["component_id"], factor["exponent"])
            )
    ancestry = foundation.provenance._ancestry_operators()
    color = ancestry["standard_12C2_SU3"]
    charge = ancestry["standard_Q3_squared"]
    color_values = (0, 16, 36, 40)
    charge_values = (0, 1, 4, 9, 16, 25, 36)
    sector_factors: dict[tuple[int, int], dict[int, int]] = defaultdict(dict)
    factor_assignments: list[dict[str, Any]] = []
    for factor_id, key in enumerate(factor_keys):
        columns: list[dict[int, sp.Expr]] = []
        for component_id, exponent in occurrences[factor_id]:
            component = data["components"][component_id]
            matrix = data["matrices"][component_id]
            kernel = _evaluate_matrix_polynomial(matrix, key).nullspace()
            expected = (len(key) - 1) * exponent
            if len(kernel) != expected:
                raise ArithmeticError("factor-kernel dimension drifted")
            for vector in kernel:
                columns.append(
                    {
                        component[row]: vector[row]
                        for row in range(len(component))
                        if vector[row]
                    }
                )
        basis_entries = {
            (row, column): value
            for column, vector in enumerate(columns)
            for row, value in vector.items()
        }
        basis = sp.ImmutableSparseMatrix(chart.TOTAL_DIM, len(columns), basis_entries)
        _rref, pivot_rows = basis.T.rref()
        pivot_rows = tuple(int(value) for value in pivot_rows[: basis.cols])
        square = basis.extract(pivot_rows, range(basis.cols))
        if square.det() == 0:
            raise ArithmeticError("factor basis row minor became singular")
        color_image = _apply_sparse_integer_operator(color, basis)
        charge_image = _apply_sparse_integer_operator(charge, basis)
        color_action = square.inv() * color_image.extract(pivot_rows, range(basis.cols))
        charge_action = square.inv() * charge_image.extract(pivot_rows, range(basis.cols))
        if color_image != basis * color_action or charge_image != basis * charge_action:
            raise ArithmeticError("standard operators do not preserve factor space")
        assignments: list[dict[str, int]] = []
        degree = len(key) - 1
        for color_value in color_values:
            for charge_value in charge_values:
                stacked = sp.Matrix.vstack(
                    color_action - color_value * sp.eye(basis.cols),
                    charge_action - charge_value * sp.eye(basis.cols),
                )
                dimension = basis.cols - stacked.rank()
                if not dimension:
                    continue
                if dimension % degree:
                    raise ArithmeticError("sector factor multiplicity is nonintegral")
                exponent = dimension // degree
                assignments.append(
                    {
                        "12C2_SU3": color_value,
                        "Q3_squared": charge_value,
                        "factor_exponent": exponent,
                        "subspace_dimension": dimension,
                    }
                )
                sector_factors[(color_value, charge_value)][factor_id] = exponent
        if sum(row["subspace_dimension"] for row in assignments) != basis.cols:
            raise ArithmeticError("factor sector dimensions do not exhaust factor space")
        factor_assignments.append(
            {
                "factor_id": factor_id,
                "total_factor_space_dimension": basis.cols,
                "exact_assignments": assignments,
            }
        )
    sector_reports: list[dict[str, Any]] = []
    for (color_value, charge_value), factors in sorted(sector_factors.items()):
        dimension = sum(
            (len(factor_keys[factor_id]) - 1) * exponent
            for factor_id, exponent in factors.items()
        )
        sector_reports.append(
            {
                "12C2_SU3": color_value,
                "Q3_squared": charge_value,
                "dimension": dimension,
                "H_factor_exponents": {
                    str(factor_id): exponent for factor_id, exponent in sorted(factors.items())
                },
            }
        )
    return {
        "method": "exact factor-kernel restriction and exact joint Casimir/Q3-squared eigenspace ranks",
        "factor_assignments": factor_assignments,
        "sector_reports": sector_reports,
        "sector_count": len(sector_reports),
        "sector_dimension_sum": sum(row["dimension"] for row in sector_reports),
        "all_factor_spaces_exactly_exhausted": True,
    }


@lru_cache(maxsize=1)
def squared_factorization() -> dict[str, Any]:
    data = exact_factorization()
    squared_lookup: dict[tuple[Fraction, ...], int] = {}
    squared_keys: list[tuple[Fraction, ...]] = []
    factor_map: dict[int, list[dict[str, int]]] = {}
    for factor_id, key in enumerate(data["factor_keys"]):
        source = _poly_from_key(key, T)
        resultant = sp.resultant(source.as_expr(), Y - T * T, T)
        mapped: list[dict[str, int]] = []
        for expression, exponent in sp.factor_list(resultant)[1]:
            polynomial = sp.Poly(expression, Y, domain=sp.QQ).monic()
            squared_key = tuple(
                Fraction(int(value.p), int(value.q))
                for value in polynomial.all_coeffs()
            )
            if squared_key not in squared_lookup:
                squared_lookup[squared_key] = len(squared_keys)
                squared_keys.append(squared_key)
            mapped.append(
                {
                    "squared_factor_id": squared_lookup[squared_key],
                    "map_exponent": int(exponent),
                }
            )
        factor_map[factor_id] = mapped
    squared_global: Counter[int] = Counter()
    for factor_id, exponent in data["global_exponents"].items():
        for mapped in factor_map[factor_id]:
            squared_global[mapped["squared_factor_id"]] += exponent * mapped["map_exponent"]
    squared_reports: list[dict[str, Any]] = []
    total_roots = 0
    zero_roots = 0
    positive_roots = 0
    for squared_id, key in enumerate(squared_keys):
        polynomial = _poly_from_key(key, Y)
        degree = int(polynomial.degree())
        exponent = squared_global[squared_id]
        total_roots += degree * exponent
        is_zero = degree == 1 and key == (Fraction(1), Fraction(0))
        if is_zero:
            zero_roots += exponent
            positive_count = 0
        else:
            # Every root is a square of a real H eigenvalue.  Rank(H)=448
            # excludes zero for nonzero factors.
            positive_count = degree * exponent
            positive_roots += positive_count
        squared_reports.append(
            {
                "squared_factor_id": squared_id,
                "degree": degree,
                "coefficients_monic_descending": [str(value) for value in key],
                "global_exponent": exponent,
                "root_count_with_multiplicity": degree * exponent,
                "positive_root_count_with_multiplicity": positive_count,
                "is_zero_factor": is_zero,
            }
        )
    # Exact collision audit: distinct monic irreducible Q factors are coprime.
    pairwise_gcd_degrees: list[int] = []
    for first in range(len(squared_keys)):
        for second in range(first + 1, len(squared_keys)):
            gcd = sp.gcd(
                _poly_from_key(squared_keys[first], Y),
                _poly_from_key(squared_keys[second], Y),
            )
            pairwise_gcd_degrees.append(int(gcd.degree()))
    sector_source = exact_sector_assignment()["sector_reports"]
    squared_sectors: list[dict[str, Any]] = []
    for sector in sector_source:
        exponents: Counter[int] = Counter()
        for factor_id_text, exponent in sector["H_factor_exponents"].items():
            factor_id = int(factor_id_text)
            for mapped in factor_map[factor_id]:
                exponents[mapped["squared_factor_id"]] += exponent * mapped["map_exponent"]
        squared_sectors.append(
            {
                "12C2_SU3": sector["12C2_SU3"],
                "Q3_squared": sector["Q3_squared"],
                "dimension": sector["dimension"],
                "y_factor_exponents": {
                    str(factor_id): exponent for factor_id, exponent in sorted(exponents.items())
                },
            }
        )
    return {
        "spectral_variable": "y=rho/(2b)",
        "map": "y=t^2 for each eigenvalue t of Hren",
        "source_to_squared_factor_map": {
            str(factor_id): mapped for factor_id, mapped in factor_map.items()
        },
        "squared_factor_reports": squared_reports,
        "squared_sector_reports": squared_sectors,
        "distinct_squared_irreducible_factor_count": len(squared_keys),
        "pairwise_squared_factor_gcd_maximum_degree": max(pairwise_gcd_degrees, default=0),
        "no_unrecorded_exact_squared_root_collisions": not any(pairwise_gcd_degrees),
        "total_root_count_with_multiplicity": total_roots,
        "zero_root_count_with_multiplicity": zero_roots,
        "positive_root_count_with_multiplicity": positive_roots,
        "strict_positivity_logic": (
            "all H roots are real because H is real symmetric; y=t^2; exact reconstructed rank(H)=448 leaves exactly 38 zero roots"
        ),
    }


def kernel_and_physics_boundary() -> dict[str, Any]:
    frozen = json.loads(foundation.OUT_JSON.read_text(encoding="utf-8"))
    rank = frozen["exact_reconstructed_Hessian_rank"]
    symmetry = frozen["exact_symmetry"]
    gauge_rank = symmetry["orbits"]["SO10_x_U1X"]["exact_rank"]
    full_rank = symmetry["orbits"]["SO10_x_U1X_x_PQ"]["exact_rank"]
    return {
        "exact_reconstructed_H_rank": rank["exact_reconstructed_rank"],
        "exact_reconstructed_H_nullity": rank["exact_reconstructed_nullity"],
        "H_U_rank_for_b_positive": rank["exact_reconstructed_rank"],
        "H_U_nullity_for_b_positive": rank["exact_reconstructed_nullity"],
        "gauged_orbit_kernel_dimension": gauge_rank,
        "global_PQ_axion_kernel_dimension": full_rank - gauge_rank,
        "kernel_census": "37 gauged/eaten directions plus 1 global PQ axion",
        "massive_tree_Hessian_mode_count": 448,
        "rho_interpretation": "canonically normalized tree-level scalar Hessian eigenvalue",
        "rho_is_a_pole_mass_squared": False,
        "missing_for_pole_mass": [
            "dimensionful symmetry-breaking scale and b normalization",
            "loop self-energies and renormalization prescription",
            "RG evolution and component threshold matching",
        ],
        "physical_G6_closed": False,
        "release_G6_closed": False,
    }


def build_report() -> dict[str, Any]:
    factorization = exact_factorization()
    sector = exact_sector_assignment()
    squared = squared_factorization()
    kinetic = kinetic_metric_certificate()
    commutators = exact_commutator_certificate()
    boundary = kernel_and_physics_boundary()
    report: dict[str, Any] = {
        "schema": "conditional_physical_sm_eft_hessian_spectrum_v1",
        "status": STATUS,
        "source_binding": {
            "self_path": Path(__file__).name,
            "self_sha256": _raw_sha256(Path(__file__)),
            "foundation": source_bindings(),
            "kinetic_chart_path": Path(chart.__file__).name,
            "kinetic_chart_sha256": _raw_sha256(Path(chart.__file__)),
        },
        "closure_claims": {
            "conditional_reconstructed_tree_Hessian_factorization": True,
            "conditional_reconstructed_tree_Hessian_sector_assignment": True,
            "conditional_reconstructed_squared_EFT_spectrum": True,
            "source_bound_physical_G6": False,
            "pole_spectrum_G6": False,
            "release_G6": False,
        },
        "kinetic_normalization": kinetic,
        "exact_standard_commutators": commutators,
        "Hren_factorization": {
            "field_dimension": chart.TOTAL_DIM,
            "coordinate_component_count": len(factorization["components"]),
            "component_size_census": {
                str(size): count
                for size, count in sorted(
                    Counter(map(len, factorization["components"])).items()
                )
            },
            "maximum_component_size": max(map(len, factorization["components"])),
            "distinct_irreducible_factor_count": len(factorization["factor_keys"]),
            "factor_reports": factorization["factor_reports"],
            "component_reports": factorization["component_reports"],
            "characteristic_degree_sum": sum(
                row["degree"] * row["global_exponent"]
                for row in factorization["factor_reports"]
            ),
        },
        "exact_sector_assignment": sector,
        "squared_EFT_spectrum": squared,
        "kernel_and_physics_boundary": boundary,
        "proof_boundary": {
            "exact_on_reconstructed_rational_Hessian": True,
            "upstream_denominator_bound_source_derived": False,
            "upstream_source_algebra_derivation_complete": False,
            "tree_level_only": True,
            "pole_and_release_claims": False,
        },
    }
    decisive = dict(report)
    report["integrity"] = {
        "core_sha256": hashlib.sha256(canonical_json_bytes(decisive)).hexdigest()
    }
    return report


def render_markdown(report: dict[str, Any]) -> str:
    h = report["Hren_factorization"]
    squared = report["squared_EFT_spectrum"]
    boundary = report["kernel_and_physics_boundary"]
    return "\n".join(
        [
            "# Conditional physical-SM EFT Hessian spectrum v20",
            "",
            f"- Status: `{report['status']}`",
            f"- Core SHA-256: `{report['integrity']['core_sha256']}`",
            f"- Canonical kinetic metric: `{report['kinetic_normalization']['generalized_kinetic_metric']}`.",
            f"- Exact coordinate components: `{h['coordinate_component_count']}` (maximum size `{h['maximum_component_size']}`).",
            f"- Distinct irreducible H factors: `{h['distinct_irreducible_factor_count']}`.",
            f"- Exact standard sectors: `{report['exact_sector_assignment']['sector_count']}`; dimension sum `{report['exact_sector_assignment']['sector_dimension_sum']}`.",
            f"- Squared EFT roots: `{squared['positive_root_count_with_multiplicity']}` positive plus `{squared['zero_root_count_with_multiplicity']}` zero.",
            f"- Kernel: `{boundary['kernel_census']}`.",
            "",
            "The spectral variable is `y=rho/(2b)`, where `rho` is a canonically normalized tree-level Hessian eigenvalue. It is not a pole mass squared. The exact result is conditional on the upstream reconstructed rational Hessian; source-algebra, loop, scale, threshold, and release closure remain open.",
            "",
        ]
    )


def write_outputs() -> dict[str, Any]:
    report = build_report()
    OUT_JSON.write_bytes(
        json.dumps(_jsonable(report), indent=2, sort_keys=True).encode("utf-8")
        + b"\n"
    )
    OUT_MD.write_text(render_markdown(report), encoding="utf-8", newline="\n")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--allow-unfrozen", action="store_true")
    args = parser.parse_args()
    report = write_outputs() if args.write else build_report()
    if not args.write and OUT_JSON.exists():
        frozen = json.loads(OUT_JSON.read_text(encoding="utf-8"))
        if frozen != report and not args.allow_unfrozen:
            raise ArithmeticError("frozen conditional physical-SM spectrum drifted")
    print(json.dumps(_jsonable(report), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
