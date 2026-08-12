#!/usr/bin/env python3
"""Exact tree-level physical scalar spectrum for the stabilized EFT vacuum.

This theorem diagonalizes the source-bound 486-real-field Hessian as an exact
generalized eigenvalue problem.  It keeps the radical-free coordinate
congruence explicit, factors every invariant support block over ``Q``, and
classifies every algebraic mass eigenspace under the exact unbroken
``SU(3)_C x U(1)_em`` stabilizer.

The result is deliberately scoped.  It is an exact normalized tree-level EFT
spectrum at ``gamma=1/20`` and ``Lambda_EFT=1``.  It is not a pole-mass,
matching, running, or uncertainty theorem for the original renormalizable
model.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Iterable

import numpy as np
import sympy as sp


HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import exact_gauged_u1x_g3_su5_delta_hsx_exact_hessian_v20 as hessian_source
import exact_gauged_u1x_g3_su5_eft_current_kernel_stabilized_global_v20 as eft
import exact_gauged_u1x_stationarity_rank_certificate_v20 as stationarity
import final_g4_eft_mathematical_gate_v20 as g4_gate
import live_g2_canonical_486_field_chart_v20 as chart


STATUS = "EXACT_EFT_TREE_LEVEL_PHYSICAL_SCALAR_SPECTRUM"
MODEL_CONTRACT_ID = (
    "gauged_u1x_phi17_v20_eft_o6_current_kernel_gamma_1_over_20"
)
OUT_JSON = HERE / "EXACT_EFT_PHYSICAL_SCALAR_SPECTRUM_V20.json"
OUT_MD = HERE / "EXACT_EFT_PHYSICAL_SCALAR_SPECTRUM_V20.md"

EXPECTED_CORE_SHA256 = (
    "abb704133c8be22b424ba20e23387d6f30412e6c82ab3a214e88bd8df5bef9cc"
)
EXPECTED_HESSIAN_PAYLOAD_SHA256 = (
    "7ea54d59138f8e5b66aad3d1f1ecb707c65ac9bb0f0e118a597daaccc136b568"
)
EXPECTED_G4_CORE_SHA256 = (
    "931a152aed49eb28bf415a1aca093e923850cf68db3f40ccf1d2027b447a8c09"
)

RAW_HESSIAN_DENOMINATOR = 25_200_000
# One hundred times the kinetic metric in the radical-free z chart.
KINETIC_WEIGHTS = {
    "Phi210": 10,
    "H10": 100,
    "Sigma126bar": 1,
    "S": 8,
    "Phi17": 200,
}


def _f(coefficients: Iterable[int], exponent: int = 1) -> tuple[tuple[int, ...], int]:
    return tuple(int(value) for value in coefficients), int(exponent)


# Primitive factors in the physical mass-squared variable x.  Exponents are
# the multiplicity of each algebraic root in the indicated real stabilizer
# sector.  This is both the frozen target and a compact exact spectrum table.
EXPECTED_SECTORS: dict[str, dict[str, Any]] = {
    "C0_Q0": {
        "casimir12": 0,
        "charge_squared": 0,
        "irrep": "1",
        "dimension": 24,
        "kernel_dimension": 4,
        "factors": (
            _f((1, 0), 4), _f((50, -1)), _f((8, -1)), _f((25, -4)),
            _f((14400, -32656, 6019), 2), _f((10500, -2141), 2),
            _f((14400, -27616, 12387), 2),
            _f((11390625, -176478750, 828210825, -1246452890, 568011024)),
            _f((1, -4)), _f((5, -26), 2),
        ),
    },
    "C0_Q1": {
        "casimir12": 0,
        "charge_squared": 1,
        "irrep": "1",
        "dimension": 24,
        "kernel_dimension": 4,
        "factors": (
            _f((1, 0), 4), _f((72000, -62480, 301), 2),
            _f((72000, -375680, 55661), 2), _f((5250, -1333), 4),
            _f((12500, -53725, 54929), 2), _f((20, -37), 2),
            _f((45, -106), 2),
        ),
    },
    "C16_Q0": {
        "casimir12": 16,
        "charge_squared": 0,
        "irrep": "3+3bar",
        "dimension": 102,
        "kernel_dimension": 18,
        "factors": (
            _f((1, 0), 18), _f((250, -13), 6),
            _f((270000, -2171100, 4711017, -3214490, 396160), 6),
            _f((63000, -15943), 6), _f((450, -361), 12),
            _f((63000, -53743), 6), _f((20250, -81765, 80143), 6),
            _f((3125, -12850, 12971), 6), _f((1, -2), 6),
        ),
    },
    "C16_Q1": {
        "casimir12": 16,
        "charge_squared": 1,
        "irrep": "3+3bar",
        "dimension": 96,
        "kernel_dimension": 12,
        "factors": (
            _f((1, 0), 12), _f((900, -47), 6), _f((63000, -12793), 6),
            _f((22500, -43475, 19269), 6), _f((63000, -50593), 6),
            _f((900, -767), 12), _f((20250, -122265, 90448), 6),
            _f((1, -1), 6), _f((225, -383), 6), _f((50, -93), 6),
            _f((1, -2), 12),
        ),
    },
    "C36_Q0": {
        "casimir12": 36,
        "charge_squared": 0,
        "irrep": "8",
        "dimension": 56,
        "kernel_dimension": 0,
        "factors": (
            _f((2025, -12105, 8728), 8), _f((450, -383), 16),
            _f((45, -28), 8), _f((450, -833), 16),
        ),
    },
    "C36_Q1": {
        "casimir12": 36,
        "charge_squared": 1,
        "irrep": "8",
        "dimension": 64,
        "kernel_dimension": 0,
        "factors": (
            _f((900, -721), 16), _f((45, -73), 16),
            _f((900, -1621), 16), _f((1, -2), 16),
        ),
    },
    "C40_Q0": {
        "casimir12": 40,
        "charge_squared": 0,
        "irrep": "6+6bar",
        "dimension": 48,
        "kernel_dimension": 0,
        "factors": (
            _f((31500, -25253), 12), _f((45, -73), 12),
            _f((5, -9), 12), _f((1, -2), 12),
        ),
    },
    "C40_Q1": {
        "casimir12": 40,
        "charge_squared": 1,
        "irrep": "6+6bar",
        "dimension": 72,
        "kernel_dimension": 0,
        "factors": (
            _f((900, -227), 12), _f((45, -28), 12),
            _f((20, -37), 24), _f((900, -1667), 12),
            _f((1, -5), 12),
        ),
    },
}


def _sha256_array(value: np.ndarray) -> str:
    return hashlib.sha256(np.asarray(value, dtype="<i8").tobytes()).hexdigest()


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def _primitive_factor(poly: sp.Poly) -> tuple[int, ...]:
    _denominator, integer_poly = poly.clear_denoms(convert=True)
    _content, primitive = integer_poly.primitive()
    if primitive.LC() < 0:
        primitive = -primitive
    return tuple(int(value) for value in primitive.all_coeffs())


def _poly_from_coefficients(coefficients: tuple[int, ...], x: sp.Symbol) -> sp.Poly:
    return sp.Poly.from_list(list(coefficients), gens=x, domain=sp.QQ)


def _evaluate_matrix_polynomial(poly: sp.Poly, matrix: sp.Matrix) -> sp.Matrix:
    identity = sp.eye(matrix.rows)
    result = sp.zeros(matrix.rows)
    for coefficient in poly.all_coeffs():
        result = result * matrix + coefficient * identity
    return result


def _kinetic_weight_vector() -> np.ndarray:
    weights = np.empty(chart.TOTAL_DIM, dtype=np.int64)
    weights[chart.PHI_SLICE] = KINETIC_WEIGHTS["Phi210"]
    weights[chart.H_SLICE] = KINETIC_WEIGHTS["H10"]
    weights[chart.SIGMA_SLICE] = KINETIC_WEIGHTS["Sigma126bar"]
    weights[chart.S_SLICE] = KINETIC_WEIGHTS["S"]
    weights[chart.X_SLICE] = KINETIC_WEIGHTS["Phi17"]
    return weights


@lru_cache(maxsize=1)
def _exact_stabilized_numerator() -> np.ndarray:
    original, _lattice = hessian_source.exact_raw_numerator()
    current = eft.exact_signed_current_hessian_numerator()
    current_denominator = int(current["report"]["raw_Hessian_denominator"])
    removal_denominator = eft.REMOVED_BETA_DENOMINATOR * current_denominator
    if RAW_HESSIAN_DENOMINATOR % removal_denominator:
        raise ArithmeticError("signed-current subtraction left the exact lattice")
    base = original - (
        RAW_HESSIAN_DENOMINATOR // removal_denominator
    ) * current["integer_matrix"]
    jacobian = eft.exact_current_kernel_jacobian()["integer_matrix"]
    eft_denominator = eft.GAMMA_DENOMINATOR * eft.RAW_JACOBIAN_DENOMINATOR**2
    if RAW_HESSIAN_DENOMINATOR % eft_denominator:
        raise ArithmeticError("EFT Hessian addition left the exact lattice")
    stabilized = base + (
        RAW_HESSIAN_DENOMINATOR // eft_denominator
    ) * (jacobian.T @ jacobian)
    if _sha256_array(stabilized) != EXPECTED_HESSIAN_PAYLOAD_SHA256:
        raise ArithmeticError("stabilized Hessian payload drifted")
    return np.asarray(stabilized, dtype=np.int64)


@lru_cache(maxsize=1)
def _stabilizer_operators() -> tuple[np.ndarray, np.ndarray]:
    matrices: list[np.ndarray] = []
    for sparse in stationarity._unbroken_generators():
        dense = np.zeros((chart.TOTAL_DIM, chart.TOTAL_DIM), dtype=np.int64)
        for (row, column), value in sparse.items():
            dense[row, column] = value
        matrices.append(dense)
    t = matrices
    casimir12 = -(
        4 * (t[0] @ t[0])
        + 2 * (t[0] @ t[1])
        + 2 * (t[1] @ t[0])
        + 4 * (t[1] @ t[1])
        + sum(3 * (t[index] @ t[index]) for index in range(2, 8))
    )
    charge_squared = -(t[8] @ t[8])
    return casimir12, charge_squared


def _casimir_projector(casimir: sp.Matrix, eigenvalue: int) -> sp.Matrix:
    result = sp.eye(casimir.rows)
    for other in (0, 16, 36, 40):
        if other != eigenvalue:
            result = result * (casimir - other * sp.eye(casimir.rows)) / (
                eigenvalue - other
            )
    return result


def _crt_spectral_projectors(
    matrix: sp.Matrix,
    factors: tuple[sp.Poly, ...],
    x: sp.Symbol,
) -> dict[tuple[int, ...], sp.Matrix]:
    squarefree = sp.Poly(1, x, domain=sp.QQ)
    for factor in factors:
        squarefree *= factor
    projectors: dict[tuple[int, ...], sp.Matrix] = {}
    for factor in factors:
        quotient = squarefree.exquo(factor)
        inverse = sp.invert(quotient, factor)
        idempotent = (quotient * inverse).rem(squarefree)
        projectors[_primitive_factor(factor)] = _evaluate_matrix_polynomial(
            idempotent, matrix
        )
    return projectors


def _factor_records(
    counts: dict[tuple[int, ...], int],
) -> list[dict[str, Any]]:
    x = sp.Symbol("x")
    records: list[dict[str, Any]] = []
    for coefficients, exponent in sorted(
        counts.items(), key=lambda item: (len(item[0]), item[0])
    ):
        poly = _poly_from_coefficients(coefficients, x)
        degree = poly.degree()
        if coefficients == (1, 0):
            intervals = [{"lower": "0", "upper": "0", "approx": 0.0}]
        elif degree == 1:
            root = sp.Rational(-coefficients[1], coefficients[0])
            intervals = [
                {
                    "lower": str(root),
                    "upper": str(root),
                    "approx": float(root),
                }
            ]
        else:
            isolated = sp.intervals(poly, eps=sp.Rational(1, 10**12))
            intervals = []
            for (lower, upper), multiplicity in isolated:
                if multiplicity != 1:
                    raise ArithmeticError("a primitive mass factor is not square-free")
                intervals.append(
                    {
                        "lower": str(lower),
                        "upper": str(upper),
                        "approx": float((lower + upper) / 2),
                    }
                )
        records.append(
            {
                "primitive_coefficients_high_to_low": list(coefficients),
                "degree": degree,
                "root_multiplicity": exponent,
                "root_count": degree,
                "mass_squared_root_intervals": intervals,
                "mass_definition": "m=sqrt(x) in the normalized tree-level units",
            }
        )
    return records


@lru_cache(maxsize=1)
def exact_spectrum_certificate() -> dict[str, Any]:
    matrix = _exact_stabilized_numerator()
    weights = _kinetic_weight_vector()
    components = hessian_source.support_components(matrix, tolerance=0.0)
    casimir12, charge_squared = _stabilizer_operators()
    kinetic = np.diag(weights)

    if not (
        np.array_equal(matrix, matrix.T)
        and np.all(weights > 0)
        and np.count_nonzero(matrix @ casimir12 - casimir12 @ matrix) == 0
        and np.count_nonzero(matrix @ charge_squared - charge_squared @ matrix) == 0
        and np.count_nonzero(casimir12 @ charge_squared - charge_squared @ casimir12)
        == 0
        and np.count_nonzero(kinetic @ casimir12 - casimir12 @ kinetic) == 0
        and np.count_nonzero(kinetic @ charge_squared - charge_squared @ kinetic)
        == 0
    ):
        raise ArithmeticError("the exact stabilizer/pencil commutant drifted")
    identity = np.eye(chart.TOTAL_DIM, dtype=np.int64)
    casimir_minimal = (
        casimir12
        @ (casimir12 - 16 * identity)
        @ (casimir12 - 36 * identity)
        @ (casimir12 - 40 * identity)
    )
    if np.count_nonzero(casimir_minimal) or np.count_nonzero(
        charge_squared @ (charge_squared - identity)
    ):
        raise ArithmeticError("the exact stabilizer spectrum drifted")

    x = sp.Symbol("x")
    observed: dict[str, dict[tuple[int, ...], int]] = {
        key: defaultdict(int) for key in EXPECTED_SECTORS
    }
    global_counts: dict[tuple[int, ...], int] = defaultdict(int)
    component_signatures: list[dict[str, Any]] = []

    for component_index, component_tuple in enumerate(components):
        component = list(component_tuple)
        rational_matrix = sp.Matrix(
            [
                [
                    sp.Rational(
                        100 * int(matrix[row, column]),
                        RAW_HESSIAN_DENOMINATOR * int(weights[row]),
                    )
                    for column in component
                ]
                for row in component
            ]
        )
        charpoly = sp.Poly(rational_matrix.charpoly(x).as_expr(), x, domain=sp.QQ)
        factor_list = sp.factor_list(charpoly.as_expr())[1]
        factors = tuple(sp.Poly(factor, x, domain=sp.QQ) for factor, _ in factor_list)
        multiplicities = {
            _primitive_factor(sp.Poly(factor, x, domain=sp.QQ)): int(exponent)
            for factor, exponent in factor_list
        }
        for factor, exponent in multiplicities.items():
            global_counts[factor] += exponent

        spectral_projectors = _crt_spectral_projectors(rational_matrix, factors, x)
        cblock = sp.Matrix(casimir12[np.ix_(component, component)])
        qblock = sp.Matrix(charge_squared[np.ix_(component, component)])
        component_sector_dimensions: dict[str, int] = {}
        for sector, expected in EXPECTED_SECTORS.items():
            cprojector = _casimir_projector(cblock, int(expected["casimir12"]))
            qprojector = qblock if expected["charge_squared"] else sp.eye(len(component)) - qblock
            sector_projector = cprojector * qprojector
            sector_dimension = int(sp.trace(sector_projector))
            if sector_dimension:
                component_sector_dimensions[sector] = sector_dimension
            for factor, projector in spectral_projectors.items():
                dimension = sp.trace(sector_projector * projector)
                if dimension:
                    degree = len(factor) - 1
                    exponent = sp.Rational(dimension, degree)
                    if exponent.q != 1:
                        raise ArithmeticError("nonintegral exact sector multiplicity")
                    observed[sector][factor] += int(exponent)
        component_signatures.append(
            {
                "component": component_index,
                "dimension": len(component),
                "sector_dimensions": component_sector_dimensions,
                "factor_count": len(factors),
            }
        )

    expected_counts: dict[str, dict[tuple[int, ...], int]] = {
        sector: {factor: exponent for factor, exponent in row["factors"]}
        for sector, row in EXPECTED_SECTORS.items()
    }
    if {key: dict(value) for key, value in observed.items()} != expected_counts:
        raise ArithmeticError("the exact per-sector mass factor table drifted")

    sector_reports: dict[str, Any] = {}
    for sector, expected in EXPECTED_SECTORS.items():
        counts = expected_counts[sector]
        degree = sum((len(factor) - 1) * exponent for factor, exponent in counts.items())
        zero_dimension = counts.get((1, 0), 0)
        if degree != expected["dimension"] or zero_dimension != expected["kernel_dimension"]:
            raise ArithmeticError("the exact sector dimension census drifted")
        sector_reports[sector] = {
            "casimir12": expected["casimir12"],
            "standard_SU3_quadratic_Casimir": str(
                sp.Rational(expected["casimir12"], 12)
            ),
            "SU3C_irrep": expected["irrep"],
            "U1em_charge_squared": expected["charge_squared"],
            "U1em_charge_interpretation": (
                "neutral" if expected["charge_squared"] == 0 else "|q_em|=1"
            ),
            "full_real_dimension": degree,
            "zero_dimension": zero_dimension,
            "massive_real_dimension": degree - zero_dimension,
            "primitive_factors": _factor_records(counts),
        }

    total_degree = sum((len(factor) - 1) * exponent for factor, exponent in global_counts.items())
    zero_multiplicity = global_counts.get((1, 0), 0)
    distinct_roots = sum(len(factor) - 1 for factor in global_counts)
    nonlinear_factors = [factor for factor in global_counts if len(factor) > 2]
    no_negative_roots = all(
        len(
            {
                sp.sign(coefficient)
                for coefficient in sp.Poly(
                _poly_from_coefficients(factor, x).as_expr().subs(x, -x),
                x,
                domain=sp.QQ,
                ).all_coeffs()
                if coefficient
            }
        )
        == 1
        for factor in global_counts
        if factor != (1, 0)
    )
    # The transformed-coefficient test above is a compact Descartes certificate
    # for absence of negative roots.  Reality follows exactly because this is a
    # symmetric pencil with a positive-definite kinetic metric.
    if not (
        total_degree == 486
        and zero_multiplicity == 38
        and distinct_roots == 61
        and len(global_counts) == 45
        and no_negative_roots
    ):
        raise ArithmeticError("the global exact mass census drifted")

    g4 = g4_gate.build_report()
    g4_geometry = g4["exact_EFT_witness_quotient_geometry"]
    g4_hessian = g4["exact_Hessian_classification"]
    if not (
        g4["core_sha256"] == EXPECTED_G4_CORE_SHA256
        and g4["classification"]["mathematical_G4_closed_for_EFT_model"]
        and g4_geometry["gauge_quotient_dimension_including_axion"] == 449
        and g4_geometry["independent_PQ_axion_dimension"] == 1
        and g4_hessian["massive_transverse_dimension"] == 448
    ):
        raise ArithmeticError("the exact G4 quotient dependency drifted")

    return {
        "model_contract_id": MODEL_CONTRACT_ID,
        "normalization": {
            "gamma": "1/20",
            "Lambda_EFT": "1",
            "raw_Hessian_denominator": RAW_HESSIAN_DENOMINATOR,
            "kinetic_metric_times_100": KINETIC_WEIGHTS,
            "generalized_pencil": "det(M-252000*x*K100)=0",
            "physical_mass_squared_variable": "x",
        },
        "source_binding": {
            "stabilized_Hessian_payload_sha256": _sha256_array(matrix),
            "expected_stabilized_Hessian_payload_sha256": EXPECTED_HESSIAN_PAYLOAD_SHA256,
            "EFT_G4_core_sha256": g4["core_sha256"],
        },
        "exact_factorization": {
            "support_component_count": len(components),
            "support_component_sizes": [len(component) for component in components],
            "support_component_type_count": len(
                {
                    tuple(
                        sorted(
                            (factor, exponent)
                            for factor, exponent in {
                                _primitive_factor(sp.Poly(f, x, domain=sp.QQ)): int(e)
                                for f, e in sp.factor_list(
                                    sp.Matrix(
                                        [
                                            [
                                                sp.Rational(
                                                    100 * int(matrix[r, c]),
                                                    RAW_HESSIAN_DENOMINATOR * int(weights[r]),
                                                )
                                                for c in component
                                            ]
                                            for r in component
                                        ]
                                    ).charpoly(x).as_expr()
                                )[1]
                            }.items()
                        )
                    )
                    for component in components
                }
            ),
            "primitive_factor_count": len(global_counts),
            "distinct_mass_squared_root_count_including_zero": distinct_roots,
            "total_algebraic_degree": total_degree,
            "zero_multiplicity": zero_multiplicity,
            "positive_massive_multiplicity": total_degree - zero_multiplicity,
            "nonlinear_primitive_factor_count": len(nonlinear_factors),
            "all_roots_real_from_symmetric_positive_metric_pencil": True,
            "no_negative_roots_by_p_of_minus_x_coefficient_certificate": no_negative_roots,
            "all_nonzero_roots_strictly_positive": True,
        },
        "stabilizer_provenance": {
            "unbroken_group": "SU(3)_C x U(1)_em",
            "casimir_definition": (
                "C=-[4T0^2+2T0T1+2T1T0+4T1^2+3*sum(T2^2,...,T7^2)]"
            ),
            "casimir12_eigenvalues": [0, 16, 36, 40],
            "charge_squared_eigenvalues": [0, 1],
            "operators_commute_exactly_with_Hessian_and_kinetic_metric": True,
            "sector_reports": sector_reports,
        },
        "mixing_classification": {
            "complete": True,
            "basis_free_definition": (
                "E_(c,q,f,r)=ker(A-r I) intersect image(P_c(C) P_q(Q^2)); "
                "A=(100/25200000) K100^-1 M"
            ),
            "casimir_projectors": (
                "P_c=product_(d!=c)(C-dI)/(c-d), c in {0,16,36,40}"
            ),
            "charge_projectors": "P_0=I-Q^2, P_1=Q^2",
            "mass_projectors": "exact CRT idempotents over the primitive Q[x] factors",
            "projector_traces_reproduce_every_sector_factor_exponent": True,
            "component_signatures": component_signatures,
        },
        "physical_quotient": {
            "ambient_real_dimension": 486,
            "Hessian_kernel_dimension": 38,
            "gauged_tangent_dimension": 37,
            "physical_PQ_axion_count": 1,
            "gauge_quotient_dimension": 449,
            "massive_positive_dimension": 448,
            "all_38_zero_modes_are_unphysical": False,
            "explanation": (
                "37 zero modes are gauge tangents; the remaining exact zero mode is "
                "the physical PQ axion.  The other 448 gauge-quotient modes have m^2>0."
            ),
        },
        "uncertainty_scope": {
            "exact_algebraic_tree_level_uncertainty": "0",
            "root_intervals_are_rendering_certificates_not_physical_errors": True,
            "absolute_scale_and_Wilson_matching_complete": False,
            "loop_and_pole_mass_corrections_complete": False,
            "renormalization_scheme_and_running_complete": False,
            "physical_threshold_uncertainties_complete": False,
        },
        "scope": {
            "EFT_tree_level_mathematical_spectrum_complete": True,
            "authoritative_renormalizable_G6_closed": False,
            "EFT_release_G6_verified": False,
            "authoritative_G6_acceptance_satisfied": False,
        },
    }


def build_report() -> dict[str, Any]:
    certificate = exact_spectrum_certificate()
    decisive = {
        "model_contract_id": certificate["model_contract_id"],
        "normalization": certificate["normalization"],
        "source_binding": certificate["source_binding"],
        "exact_factorization": certificate["exact_factorization"],
        "stabilizer_provenance": certificate["stabilizer_provenance"],
        "mixing_classification": certificate["mixing_classification"],
        "physical_quotient": certificate["physical_quotient"],
        "uncertainty_scope": certificate["uncertainty_scope"],
        "scope": certificate["scope"],
    }
    core = _canonical_sha256(decisive)
    return {
        "status": STATUS,
        "core_sha256": core,
        "classification": {
            "EFT_dimension6_tree_level_mathematical_G6_closed": True,
            "EFT_release_G6_verified": False,
            "renormalizable_authoritative_G6_closed": False,
        },
        **decisive,
    }


def render_markdown(report: dict[str, Any]) -> str:
    factor = report["exact_factorization"]
    quotient = report["physical_quotient"]
    lines = [
        "# Exact EFT physical scalar spectrum",
        "",
        f"- Status: `{report['status']}`",
        f"- Core SHA256: `{report['core_sha256']}`",
        f"- Contract: `{report['model_contract_id']}`",
        "",
        "## Exact census",
        "",
        f"- Support blocks/types: {factor['support_component_count']} / {factor['support_component_type_count']}",
        f"- Primitive factors / distinct roots: {factor['primitive_factor_count']} / {factor['distinct_mass_squared_root_count_including_zero']}",
        f"- Hessian kernel: {quotient['Hessian_kernel_dimension']}",
        f"- Gauge tangents: {quotient['gauged_tangent_dimension']}",
        f"- Physical PQ axions: {quotient['physical_PQ_axion_count']}",
        f"- Positive massive modes: {quotient['massive_positive_dimension']}",
        "",
        "## Scope",
        "",
        "The exact normalized tree-level EFT spectrum, residual-group provenance, "
        "and algebraic mixing subspaces are complete.  Absolute matching, running, "
        "pole masses, and physical threshold uncertainties remain open; therefore "
        "release and authoritative renormalizable G6 remain false.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--allow-unfrozen", action="store_true")
    args = parser.parse_args()
    report = build_report()
    if not args.allow_unfrozen:
        if not EXPECTED_CORE_SHA256:
            raise ArithmeticError("EXPECTED_CORE_SHA256 is not frozen")
        if report["core_sha256"] != EXPECTED_CORE_SHA256:
            raise ArithmeticError(
                f"core drifted: {report['core_sha256']} != {EXPECTED_CORE_SHA256}"
            )
    if args.write:
        OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        OUT_MD.write_text(render_markdown(report))
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
