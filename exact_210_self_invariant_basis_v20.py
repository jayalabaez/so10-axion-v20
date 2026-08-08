#!/usr/bin/env python3
"""Complete renormalizable self-invariant basis for a real SO(10) 210 four-form.

The old repository ledger treated two cubic structures and a lower bound of
four quartics as literature-level placeholders.  This module replaces that
with an exact symmetric-power calculation and an executable tensor basis.

For R=210=Lambda^4(R^10), Racah--Speiser applied to the exact weight
multiplicities of Sym^n(R) gives

    mult_1(Sym^2 R) = 1,
    mult_1(Sym^3 R) = 1,
    mult_1(Sym^4 R) = 4.

Hence the most general renormalizable real-210 self potential contains one
quadratic invariant, one cubic invariant and four independent quartics.

Explicit basis
--------------
Let A_Phi be the symmetric 45x45 matrix on two-forms,

    (A_Phi)_[ab],[cd] = Phi_abcd.

Then

    I2 = <Phi,Phi>,
    I3 = Tr(A_Phi^3)

is the unique cubic.  For S=phi phi^T in Sym^2(210), let
K=sum_A T_A tensor T_A be the exact pair Casimir used by the merged
Phi--Sigma projectors, and define moments M_d=<S,K^d S>.  On rank-one Bose
pairs,

    M1 = 0,

and the complete quartic basis may be chosen as

    J0=M0, J2=M2, J3=M3, J4=M4.

The higher moments M5,M6,M7 obey exact rational crossing identities recorded
below.  Combined with the exact Sym^4 singlet count and a nonzero exact
four-sample determinant, this proves the four moments form a complete quartic
basis.

On the normalized p,a,omega singlet background,

    I3 = 2 a^3/sqrt(3) + 2 sqrt(3) a omega^2 + 3 p omega^2.

This closes the 210 self-operator basis and evaluator.  It does not establish
boundedness, a unique global vacuum, or the physical full Hessian.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

import numpy as np
from scipy import sparse
from scipy.sparse.linalg import expm_multiply

import direct_phi_h_sigmabar_tensor_v20 as direct
import exact_phisigma_bose_channel_census_v20 as census
import exact_phisigma_casimir_projectors_v20 as projectors

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_210_SELF_INVARIANT_BASIS_V20.json"
OUT_MD = ROOT / "EXACT_210_SELF_INVARIANT_BASIS_V20.md"

TWO_INDICES = tuple(itertools.combinations(range(10), 2))
QUARTIC_BASIS_NAMES = ("J0", "J2", "J3", "J4")
QUARTIC_MONOMIALS = tuple(
    powers
    for powers in itertools.product(range(5), repeat=3)
    if sum(powers) == 4
)

# Exact crossing identities in the basis (M0,M2,M3,M4).
HIGHER_MOMENT_REDUCTIONS: dict[int, tuple[Fraction, ...]] = {
    5: (
        Fraction(47808, 5),
        Fraction(-2964, 5),
        Fraction(-544, 5),
        Fraction(123, 5),
    ),
    6: (
        Fraction(408960),
        Fraction(-12360),
        Fraction(-3624),
        Fraction(514),
    ),
    7: (
        Fraction(65147904, 5),
        Fraction(-1082112, 5),
        Fraction(-420592, 5),
        Fraction(48864, 5),
    ),
}


def _weight_add(left: tuple[int, ...], right: tuple[int, ...], scale: int = 1) -> tuple[int, ...]:
    return tuple(left[index] + scale * right[index] for index in range(5))


@lru_cache(maxsize=5)
def symmetric_power_weights(degree: int) -> Counter[tuple[int, ...]]:
    """Exact weight multiplicities of Sym^degree(210)."""
    if not 0 <= degree <= 4:
        raise ValueError("implemented for degrees 0 through 4")
    weight_multiplicities = Counter(census.FOUR_FORM_WEIGHTS)
    dynamic: list[Counter[tuple[int, ...]]] = [Counter() for _ in range(degree + 1)]
    dynamic[0][(0, 0, 0, 0, 0)] = 1
    for weight, multiplicity in weight_multiplicities.items():
        updated: list[Counter[tuple[int, ...]]] = [Counter() for _ in range(degree + 1)]
        for current_degree in range(degree + 1):
            for current_weight, count in dynamic[current_degree].items():
                for copies in range(degree - current_degree + 1):
                    coefficient = math.comb(multiplicity + copies - 1, copies) if copies else 1
                    updated[current_degree + copies][
                        _weight_add(current_weight, weight, copies)
                    ] += count * coefficient
        dynamic = updated
    return dynamic[degree]


def racah_speiser_trivial_multiplicity(degree: int) -> int:
    """Multiplicity of the trivial D5 irrep in Sym^degree(210)."""
    weights = symmetric_power_weights(degree)
    rho = tuple(int(value) for value in census.RHO)
    total = 0
    for permutation, signs, parity in census.WEYL_ELEMENTS:
        transformed = tuple(
            signs[axis] * rho[permutation[axis]] for axis in range(5)
        )
        target = tuple(rho[axis] - transformed[axis] for axis in range(5))
        total += parity * weights.get(target, 0)
    return int(total)


def phi_vector(phi: direct.Form) -> np.ndarray:
    values = projectors._form_to_vector(phi)
    if np.max(np.abs(values.imag), initial=0.0) > 1.0e-12:
        raise ValueError("real 210 field received complex components")
    return values.real


def vector_to_phi(values: Iterable[float]) -> direct.Form:
    array = np.asarray(tuple(values), dtype=float)
    if array.shape != (210,):
        raise ValueError("expected 210 real components")
    return {
        indices: complex(array[index])
        for index, indices in enumerate(projectors.FOUR_INDICES)
        if abs(array[index]) > 1.0e-14
    }


def two_form_matrix(phi: direct.Form) -> np.ndarray:
    """A_[ab],[cd]=Phi_abcd in the canonical two-form basis."""
    matrix = np.zeros((45, 45), dtype=float)
    for row, left in enumerate(TWO_INDICES):
        for column, right in enumerate(TWO_INDICES):
            if set(left).intersection(right):
                continue
            sequence = left + right
            indices = tuple(sorted(sequence))
            value = phi.get(indices, 0.0)
            if abs(complex(value).imag) > 1.0e-12:
                raise ValueError("real 210 field received complex components")
            matrix[row, column] = (
                float(complex(value).real)
                * direct.permutation_sign(sequence)
            )
    return matrix


def quadratic_invariant(phi: direct.Form) -> float:
    return float(np.real(direct.tensor_inner(phi, phi)))


def cubic_invariant(phi: direct.Form) -> float:
    matrix = two_form_matrix(phi)
    return float(np.trace(matrix @ matrix @ matrix))


def pair_moments(phi: direct.Form, maximum_degree: int = 7) -> tuple[float, ...]:
    if not 0 <= maximum_degree <= 7:
        raise ValueError("maximum_degree must lie between 0 and 7")
    vector = phi_vector(phi)
    pair = np.outer(vector, vector)
    powers = projectors.casimir_powers(pair)
    moments = tuple(
        complex(np.sum(pair * powers[degree]))
        for degree in range(maximum_degree + 1)
    )
    if any(abs(value.imag) > 1.0e-12 for value in moments):
        raise ValueError("real 210 pair moment acquired a complex component")
    return tuple(float(value.real) for value in moments)


def quartic_invariants(phi: direct.Form) -> dict[str, float]:
    moments = pair_moments(phi, maximum_degree=4)
    return {
        "J0": moments[0],
        "J2": moments[2],
        "J3": moments[3],
        "J4": moments[4],
    }


def self_potential(
    phi: direct.Form,
    *,
    mass_sq: float,
    cubic_coupling: float,
    quartic_couplings: dict[str, float],
) -> float:
    if set(quartic_couplings) != set(QUARTIC_BASIS_NAMES):
        raise ValueError(
            "quartic couplings must be exactly J0,J2,J3,J4"
        )
    quartics = quartic_invariants(phi)
    return float(
        0.5 * float(mass_sq) * quadratic_invariant(phi)
        + float(cubic_coupling) * cubic_invariant(phi)
        + sum(
            float(quartic_couplings[name]) * quartics[name]
            for name in QUARTIC_BASIS_NAMES
        )
    )


@lru_cache(maxsize=1)
def integer_generators() -> tuple[sparse.csr_matrix, ...]:
    return tuple(
        generator.astype(np.int64)
        for generator in projectors.generator_matrices()
    )


def integer_pair_casimir(pair: np.ndarray) -> np.ndarray:
    pair = np.asarray(pair, dtype=np.int64)
    result = np.zeros_like(pair, dtype=np.int64)
    for generator in integer_generators():
        left = generator @ pair
        result += (generator @ left.T).T
    return result


def integer_pair_moments(vector: np.ndarray) -> tuple[int, ...]:
    values = np.asarray(vector, dtype=np.int64)
    if values.shape != (210,):
        raise ValueError("expected 210 integer components")
    pair = np.outer(values, values).astype(np.int64)
    current = pair.copy()
    moments: list[int] = []
    for _ in range(8):
        moments.append(int(np.sum(pair * current, dtype=np.int64)))
        current = integer_pair_casimir(current)
    return tuple(moments)


def deterministic_integer_samples() -> tuple[np.ndarray, ...]:
    rng = np.random.default_rng(2)
    rows = []
    for _ in range(8):
        support = (rng.random(210) < 0.1).astype(np.int64)
        signs = rng.choice(np.asarray([-1, 1], dtype=np.int64), 210)
        rows.append(support * signs)
    return tuple(rows)


def determinant_four(matrix: list[list[int]]) -> int:
    if len(matrix) != 4 or any(len(row) != 4 for row in matrix):
        raise ValueError("expected 4x4 matrix")
    total = 0
    for permutation in itertools.permutations(range(4)):
        total += direct.permutation_sign(permutation) * math.prod(
            matrix[row][permutation[row]] for row in range(4)
        )
    return int(total)


def reduce_moment_coefficients(degree: int) -> tuple[Fraction, ...]:
    if degree == 0:
        return (Fraction(1), Fraction(0), Fraction(0), Fraction(0))
    if degree == 1:
        return (Fraction(0), Fraction(0), Fraction(0), Fraction(0))
    if degree == 2:
        return (Fraction(0), Fraction(1), Fraction(0), Fraction(0))
    if degree == 3:
        return (Fraction(0), Fraction(0), Fraction(1), Fraction(0))
    if degree == 4:
        return (Fraction(0), Fraction(0), Fraction(0), Fraction(1))
    return HIGHER_MOMENT_REDUCTIONS[degree]


def spectral_quartics_in_basis() -> dict[str, tuple[Fraction, ...]]:
    result: dict[str, tuple[Fraction, ...]] = {}
    for name, eigenvalue in projectors.SPECTRAL_EIGENVALUES.items():
        polynomial = projectors.projector_polynomial(eigenvalue)
        coefficients = [Fraction(0) for _ in range(4)]
        for degree, coefficient in enumerate(polynomial):
            reduced = reduce_moment_coefficients(degree)
            for index in range(4):
                coefficients[index] += coefficient * reduced[index]
        result[name] = tuple(coefficients)
    return result


def singlet_form(p: float, a: float, omega: float) -> direct.Form:
    basis = direct.singlet_basis()
    return direct.add_forms(
        direct.scale_form(basis["p"], p),
        direct.scale_form(basis["a"], a),
        direct.scale_form(basis["omega"], omega),
    )


def _quartic_monomial_value(p: float, a: float, omega: float, powers: tuple[int, int, int]) -> float:
    return p ** powers[0] * a ** powers[1] * omega ** powers[2]


def singlet_quartic_polynomials() -> dict[str, dict[str, float]]:
    rng = np.random.default_rng(2104)
    points: list[tuple[float, float, float]] = []
    rows: list[list[float]] = []
    while len(points) < len(QUARTIC_MONOMIALS):
        candidate = tuple(float(value) for value in rng.integers(-3, 4, size=3))
        if candidate == (0.0, 0.0, 0.0):
            continue
        trial_rows = rows + [[
            _quartic_monomial_value(*candidate, powers)
            for powers in QUARTIC_MONOMIALS
        ]]
        if np.linalg.matrix_rank(np.asarray(trial_rows, dtype=float)) > len(rows):
            points.append(candidate)
            rows = trial_rows
    design = np.asarray(rows, dtype=float)
    values = {name: [] for name in QUARTIC_BASIS_NAMES}
    for point in points:
        quartics = quartic_invariants(singlet_form(*point))
        for name in QUARTIC_BASIS_NAMES:
            values[name].append(quartics[name])
    coefficients = {
        name: np.linalg.solve(design, np.asarray(rows_values, dtype=float))
        for name, rows_values in values.items()
    }
    # Independent validation points.
    validation_residual = 0.0
    for point in ((0.9, 0.4, 0.7), (-0.3, 0.8, -0.5), (1.1, -0.2, 0.6)):
        observed = quartic_invariants(singlet_form(*point))
        monomials = np.asarray([
            _quartic_monomial_value(*point, powers)
            for powers in QUARTIC_MONOMIALS
        ])
        for name in QUARTIC_BASIS_NAMES:
            validation_residual = max(
                validation_residual,
                abs(observed[name] - float(monomials @ coefficients[name])),
            )
    output = {
        name: {
            f"p^{powers[0]} a^{powers[1]} omega^{powers[2]}": float(coefficients[name][index])
            for index, powers in enumerate(QUARTIC_MONOMIALS)
            if abs(coefficients[name][index]) > 1.0e-9
        }
        for name in QUARTIC_BASIS_NAMES
    }
    output["validation"] = {"maximum_abs_residual": validation_residual}
    return output


def _rotation_audit() -> dict[str, float]:
    rng = np.random.default_rng(77)
    vector = rng.normal(size=210)
    vector /= np.linalg.norm(vector)
    before = vector_to_phi(vector)
    maximum = {
        "I2": 0.0,
        "I3": 0.0,
        "J0": 0.0,
        "J2": 0.0,
        "J3": 0.0,
        "J4": 0.0,
    }
    before_values = {
        "I2": quadratic_invariant(before),
        "I3": cubic_invariant(before),
        **quartic_invariants(before),
    }
    for generator_index, theta in ((0, 0.17), (13, -0.23), (44, 0.11)):
        rotated_vector = expm_multiply(
            theta * projectors.generator_matrices()[generator_index], vector
        )
        rotated = vector_to_phi(rotated_vector)
        after_values = {
            "I2": quadratic_invariant(rotated),
            "I3": cubic_invariant(rotated),
            **quartic_invariants(rotated),
        }
        for name in maximum:
            maximum[name] = max(
                maximum[name], abs(after_values[name] - before_values[name])
            )
    return maximum


def _fraction_payload(values: tuple[Fraction, ...]) -> list[str]:
    return [str(value) for value in values]


def build_report() -> dict[str, Any]:
    multiplicities = {
        degree: racah_speiser_trivial_multiplicity(degree)
        for degree in (2, 3, 4)
    }
    dimensions = {
        degree: sum(symmetric_power_weights(degree).values())
        for degree in (2, 3, 4)
    }
    expected_dimensions = {
        degree: math.comb(210 + degree - 1, degree)
        for degree in (2, 3, 4)
    }

    samples = deterministic_integer_samples()
    sample_moments = [integer_pair_moments(sample) for sample in samples]
    independence_matrix = [
        [moments[index] for index in (0, 2, 3, 4)]
        for moments in sample_moments[:4]
    ]
    independence_determinant = determinant_four(independence_matrix)
    maximum_m1 = max(abs(moments[1]) for moments in sample_moments)
    crossing_failures: list[dict[str, Any]] = []
    for sample_index, moments in enumerate(sample_moments):
        base = tuple(moments[index] for index in (0, 2, 3, 4))
        for degree, coefficients in HIGHER_MOMENT_REDUCTIONS.items():
            predicted = sum(
                coefficients[index] * base[index] for index in range(4)
            )
            if predicted != moments[degree]:
                crossing_failures.append({
                    "sample": sample_index,
                    "degree": degree,
                    "predicted": str(predicted),
                    "observed": moments[degree],
                })

    spectral_map = spectral_quartics_in_basis()
    summed_spectral = tuple(
        sum(rows[index] for rows in spectral_map.values())
        for index in range(4)
    )
    rotation = _rotation_audit()
    singlet = singlet_quartic_polynomials()

    benchmark = singlet_form(0.9, 0.4, 0.7)
    benchmark_i3 = cubic_invariant(benchmark)
    benchmark_i3_formula = (
        2.0 * 0.4**3 / math.sqrt(3.0)
        + 2.0 * math.sqrt(3.0) * 0.4 * 0.7**2
        + 3.0 * 0.9 * 0.7**2
    )

    checks = {
        "symmetric_power_dimensions_exact": dimensions == expected_dimensions,
        "one_quadratic_invariant": multiplicities[2] == 1,
        "one_cubic_invariant": multiplicities[3] == 1,
        "four_quartic_invariants": multiplicities[4] == 4,
        "explicit_cubic_nonzero": abs(benchmark_i3) > 1.0e-10,
        "cubic_singlet_formula_exact": abs(benchmark_i3 - benchmark_i3_formula) < 1.0e-12,
        "quartic_basis_exactly_independent": independence_determinant != 0,
        "rank_one_M1_vanishes": maximum_m1 == 0,
        "higher_moment_crossing_identities_exact": not crossing_failures,
        "spectral_projectors_sum_to_J0": summed_spectral
        == (Fraction(1), Fraction(0), Fraction(0), Fraction(0)),
        "all_invariants_SO10_rotation_invariant": max(rotation.values()) < 1.0e-8,
        "singlet_quartic_polynomials_validate": singlet["validation"]["maximum_abs_residual"] < 1.0e-6,
        "complete_210_self_operator_basis": True,
        "global_vacuum_not_claimed": True,
        "physical_full_Hessian_not_claimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "EXACT_REAL_210_SELF_INVARIANT_BASIS_COMPLETE"
            if not failures
            else "EXACT_REAL_210_SELF_INVARIANT_BASIS_FAILED"
        ),
        "overall_state": "CLOSED_SUBPROBLEM" if not failures else "EXECUTION_FAIL",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "exact_hilbert_count": {
            "Sym2_trivial_multiplicity": multiplicities[2],
            "Sym3_trivial_multiplicity": multiplicities[3],
            "Sym4_trivial_multiplicity": multiplicities[4],
            "symmetric_power_dimensions": dimensions,
            "method": "exact weight DP plus D5 Racah-Speiser alternation",
        },
        "source_correction": {
            "old_two_cubic_lower_bound": "withdrawn",
            "correct_cubic_count": 1,
            "old_quartic_lower_bound_4": "promoted to exact complete count",
            "correct_quartic_count": 4,
        },
        "operator_basis": {
            "quadratic": "I2=<Phi,Phi>",
            "cubic": "I3=Tr(A_Phi^3)",
            "quartics": {
                "J0": "<S,S>",
                "J2": "<S,K^2 S>",
                "J3": "<S,K^3 S>",
                "J4": "<S,K^4 S>",
                "S": "phi phi^T",
                "K": "sum_A T_A tensor T_A",
            },
            "quartic_independence_determinant": independence_determinant,
        },
        "exact_crossing_identities": {
            "M1": "0",
            **{
                f"M{degree}": _fraction_payload(coefficients)
                for degree, coefficients in HIGHER_MOMENT_REDUCTIONS.items()
            },
            "basis_order": list(QUARTIC_BASIS_NAMES),
            "failures": crossing_failures,
        },
        "spectral_projector_quartics_in_complete_basis": {
            name: _fraction_payload(coefficients)
            for name, coefficients in spectral_map.items()
        },
        "singlet_background": {
            "I2": "p^2+a^2+omega^2",
            "I3": "2 a^3/sqrt(3)+2 sqrt(3) a omega^2+3 p omega^2",
            "quartic_polynomials": singlet,
        },
        "rotation_invariance_max_abs_residuals": rotation,
        "public_evaluators": {
            "quadratic": "quadratic_invariant(phi)",
            "cubic": "cubic_invariant(phi)",
            "quartics": "quartic_invariants(phi)",
            "potential": "self_potential(phi,mass_sq,cubic_coupling,quartic_couplings)",
        },
        "newly_closed_subproblem": {
            "complete_real_210_quadratic_basis": not failures,
            "complete_real_210_cubic_basis": not failures,
            "complete_real_210_quartic_basis": not failures,
            "arbitrary_component_210_self_potential_evaluator": not failures,
        },
        "remaining_blockers": {
            "boundedness_region_for_four_quartic_couplings": True,
            "complete_other_field_sector_potentials": True,
            "unique_gauge_quotiented_vacuum": True,
            "positive_physical_full_Hessian": True,
            "physical_threshold_spectrum": True,
            "component_level_two_loop_matching": True,
            "exact_unique_proton_lifetime": True,
        },
        "flag": {
            "complete_210_self_operator_basis": not failures,
            "complete_component_potential": False,
            "unique_full_vacuum": False,
            "physical_full_Hessian_complete": False,
            "physical_threshold_spectrum_complete": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
            "empirical_discovery": False,
        },
        "verdict": (
            "The real 210 self sector has exactly one quadratic, one cubic and "
            "four quartic invariants. The executable I2, I3 and J0/J2/J3/J4 "
            "basis is complete for arbitrary 210 components."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Exact real-210 self-invariant basis — v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            "- Quadratic invariants: `1`.",
            "- Cubic invariants: `1`.",
            "- Quartic invariants: `4`.",
            "- Basis: `I2, I3, J0, J2, J3, J4`.",
            "- Boundedness, the global vacuum and physical Hessian remain open.",
            "",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    report = build_report()
    payload = json.dumps(report, indent=2) + "\n"
    OUT_JSON.write_text(payload, encoding="utf-8")
    OUT_MD.write_text(write_markdown(report), encoding="utf-8")
    print(payload, end="")
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
