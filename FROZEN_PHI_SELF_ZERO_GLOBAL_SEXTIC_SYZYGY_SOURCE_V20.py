#!/usr/bin/env python3
"""Exact global sextic syzygy for the real-210 self-zero problem.

For a four-form ``Phi`` let ``N=||Phi||^2``, ``B=*(Phi wedge Phi)``,
``D=9 N^2/5-||B||^2``, and let ``G=O_Phi^T O_Phi`` be the 45 by 45
orbit Gram matrix.  Put

    S = tr(G (G-6 N I/5)^2),
    C = 5 I3(Phi)^2-18 N^3.

This module proves the following polynomial identity over Q:

    C = sum_i c_i X_i + (1405/64) N D + (35/1536) S,

where each ``X_i=tr(q_r q_a q_b)`` contains one of the live pair-Casimir
residuals ``q_54`` or ``q_4125``.  Consequently, on their common zero set,

    5 I3^2-18 N^3 = (1405/64) N D + (35/1536) S.            (1)

The proof is finite and exact.  Racah--Speiser gives
``mult_1 Sym^6(210)=18``.  Fifteen displayed ideal contractions together
with ``N D``, ``S``, and ``N^3`` have an 18 by 18 evaluation matrix of
full rank modulo every certificate prime.  The proposed identity vanishes
on those 18 integral samples modulo 18 primes.  Their product exceeds twice
an explicit, precomputed integer height bound after all denominators are
cleared, so all 18 evaluations vanish over Q.  Unisolvence and the invariant
dimension then prove the polynomial identity.

Equation (1) is a strict global reduction, not the global zero-locus
classification.  For real Phi, G is positive semidefinite and hence S>=0,
but no sign for D or C is asserted here.  G3 and G4 therefore remain open.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import sys
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np


HERE = Path(__file__).resolve().parent
REPO = HERE.parent / "so10-axion-v20-reaudit"
for source in (HERE, REPO):
    if str(source) not in sys.path:
        sys.path.insert(0, str(source))

import exact_210_self_invariant_basis_v20 as invariants
import exact_gauged_u1x_g3_su5_phi_su3_slice_v20 as covariants
import exact_phisigma_bose_channel_census_v20 as census
import exact_phisigma_casimir_projectors_v20 as projectors


STATUS = "EXACT_GLOBAL_PHI_ZERO_SEXTIC_SYZYGY__CLASSIFICATION_OPEN"
EXPECTED_CORE_SHA256 = "18aa95ddbbdccb4852ccac256310c5d8992eb84d6594ab0a2231afd83beb0955"
EXPECTED_DEPENDENCY_SHA256 = {
    "self_invariant_basis": (
        REPO / "exact_210_self_invariant_basis_v20.py",
        "e905911f3589a78fb0c510060ca0ff6997d0963305c48f91f7a37cccbcfb4772",
    ),
    "live_pair_projectors": (
        REPO / "exact_phisigma_casimir_projectors_v20.py",
        "f4b7b6eea2bb0c4423ff52bc8b4abb082ad77eaba524a1de0a345c9eae1e2400",
    ),
    "D5_weight_census": (
        REPO / "exact_phisigma_bose_channel_census_v20.py",
        "393059f5f7860463e1e5f8f41696c79aebd3a28559778ab6fd50827642dd2bfc",
    ),
    "wedge_square_covariant_identity": (
        REPO / "exact_gauged_u1x_g3_su5_phi_su3_slice_v20.py",
        "dd4eef8d455601b3527e0dbe46b10cf09ab9224282e73b65a0e98a289fefd0a8",
    ),
}

PRIMES = (
    1_000_003,
    1_001_017,
    1_002_049,
    1_003_087,
    1_004_089,
    1_005_101,
    1_006_123,
    1_007_129,
    1_008_131,
    1_009_139,
    1_010_143,
    1_011_163,
    1_012_171,
    1_013_197,
    1_014_199,
    1_015_207,
    1_016_221,
    1_017_227,
)
SAMPLE_SEED = 20_260_810
SAMPLE_COUNT = 18
SAMPLE_COORDINATE_BOUND = 3

CHANNELS = tuple(projectors.SPECTRAL_EIGENVALUES)
FEATURE_LABELS = tuple(
    (residual, left, right)
    for residual in ("54", "4125")
    for left_index, left in enumerate(CHANNELS)
    for right in CHANNELS[left_index:]
)
PIVOT_FEATURES = (2, 8, 15, 17, 21, 22, 41, 49, 57, 58, 59, 60, 62, 63, 64)

# In the orientation C=sum c_i X_i+alpha*N*D+beta*S.
IDEAL_COEFFICIENTS = {
    2: Fraction(4_714_775, 336),
    8: Fraction(12_251_075, 336),
    15: Fraction(-359_795, 14),
    17: Fraction(-2_630_225, 294),
    21: Fraction(26_972_325, 112),
    22: Fraction(-12_460_725, 392),
    41: Fraction(-3_226_215, 56),
    49: Fraction(-437_325, 64),
    57: Fraction(-65_356_545, 3_136),
    58: Fraction(-21_146_355, 448),
    59: Fraction(2_555_205, 784),
    60: Fraction(-12_722_895, 3_136),
    62: Fraction(31_875, 392),
    63: Fraction(416_775, 196),
    64: Fraction(-622_395, 392),
}
ND_COEFFICIENT = Fraction(1_405, 64)
S_COEFFICIENT = Fraction(35, 1_536)

TWO_INDICES = tuple(itertools.combinations(range(10), 2))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def _jsonable(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    return value


def _fraction_mod(value: Fraction, prime: int) -> int:
    return value.numerator % prime * pow(value.denominator % prime, -1, prime) % prime


def _rank_mod_prime(matrix: np.ndarray, prime: int) -> int:
    work = np.remainder(np.asarray(matrix, dtype=np.int64), prime).copy()
    row = 0
    for column in range(work.shape[1]):
        candidates = np.flatnonzero(work[row:, column])
        if candidates.size == 0:
            continue
        pivot = row + int(candidates[0])
        work[[row, pivot]] = work[[pivot, row]]
        work[row] = work[row] * pow(int(work[row, column]), -1, prime) % prime
        for target in range(work.shape[0]):
            if target == row or not work[target, column]:
                continue
            work[target] = (
                work[target] - work[target, column] * work[row]
            ) % prime
        row += 1
        if row == work.shape[0]:
            break
    return row


def _four_form_operator(vector: np.ndarray, prime: int) -> np.ndarray:
    matrix = np.zeros((45, 45), dtype=np.int64)
    for row, left in enumerate(TWO_INDICES):
        for column, right in enumerate(TWO_INDICES):
            if set(left).intersection(right):
                continue
            sequence = left + right
            indices = tuple(sorted(sequence))
            inversions = sum(
                sequence[i] > sequence[j]
                for i in range(4)
                for j in range(i + 1, 4)
            )
            sign = -1 if inversions & 1 else 1
            matrix[row, column] = sign * vector[projectors.FOUR_INDEX[indices]]
    return matrix % prime


def _projector_coefficients(prime: int) -> dict[str, tuple[int, ...]]:
    return {
        name: tuple(
            _fraction_mod(value, prime)
            for value in projectors.projector_polynomial(eigenvalue)
        )
        for name, eigenvalue in projectors.SPECTRAL_EIGENVALUES.items()
    }


def _project(
    powers: list[np.ndarray], coefficients: tuple[int, ...], prime: int
) -> np.ndarray:
    output = np.zeros_like(powers[0])
    for coefficient, power in zip(coefficients, powers, strict=True):
        output = (output + coefficient * power) % prime
    return output


def _hodge_square_mod(vector: np.ndarray, prime: int) -> np.ndarray:
    output = np.zeros(45, dtype=np.int64)
    for left, right, target, coefficient in covariants._disjoint_four_form_pairs():
        output[target] = (
            output[target] + coefficient * vector[left] * vector[right]
        ) % prime
    return output


def _sample_vectors() -> tuple[np.ndarray, ...]:
    rng = np.random.default_rng(SAMPLE_SEED)
    return tuple(
        rng.integers(
            -SAMPLE_COORDINATE_BOUND,
            SAMPLE_COORDINATE_BOUND + 1,
            size=210,
            dtype=np.int64,
        )
        for _ in range(SAMPLE_COUNT)
    )


def _evaluate_mod(
    vector: np.ndarray,
    prime: int,
    coefficients: dict[str, tuple[int, ...]],
) -> tuple[list[int], int, int, int, int]:
    values = np.remainder(np.asarray(vector, dtype=np.int64), prime)
    pair = np.outer(values, values) % prime
    powers = [pair]
    for _ in range(7):
        powers.append(invariants.integer_pair_casimir(powers[-1]) % prime)
    channels = {
        name: _project(powers, coefficients[name], prime) for name in CHANNELS
    }

    features: list[int] = []
    for residual_name in ("54", "4125"):
        residual = channels[residual_name]
        products = [(residual @ channels[name]) % prime for name in CHANNELS]
        for left_index in range(len(CHANNELS)):
            for right_index in range(left_index, len(CHANNELS)):
                value = np.sum(
                    products[left_index] * channels[CHANNELS[right_index]].T,
                    dtype=np.int64,
                )
                features.append(int(value % prime))

    norm = int(values @ values % prime)
    hodge_square = _hodge_square_mod(values, prime)
    hodge_norm = int(hodge_square @ hodge_square % prime)
    defect = (9 * pow(5, -1, prime) * norm * norm - hodge_norm) % prime
    norm_defect = norm * defect % prime

    orbit = np.column_stack(
        [generator @ values for generator in invariants.integer_generators()]
    ) % prime
    gram = orbit.T @ orbit % prime
    shifted = (
        5 * gram - 6 * norm * np.eye(45, dtype=np.int64)
    ) % prime
    scalar = (
        int(np.trace((gram @ shifted % prime) @ shifted % prime))
        * pow(25, -1, prime)
        % prime
    )

    four_operator = _four_form_operator(values, prime)
    squared = four_operator @ four_operator % prime
    cubic = int(np.trace(squared @ four_operator % prime))
    cubic_defect = (5 * cubic * cubic - 18 * norm**3) % prime
    return features, norm_defect, scalar, norm**3 % prime, cubic_defect


def _weight_add(
    left: tuple[int, ...], right: tuple[int, ...], scale: int
) -> tuple[int, ...]:
    return tuple(left[index] + scale * right[index] for index in range(5))


@lru_cache(maxsize=1)
def _degree_six_dimension_report() -> dict[str, int]:
    degree = 6
    weight_multiplicities = Counter(census.FOUR_FORM_WEIGHTS)
    dynamic: list[Counter[tuple[int, ...]]] = [Counter() for _ in range(degree + 1)]
    dynamic[0][(0, 0, 0, 0, 0)] = 1
    for weight, multiplicity in weight_multiplicities.items():
        updated: list[Counter[tuple[int, ...]]] = [
            Counter() for _ in range(degree + 1)
        ]
        for current_degree in range(degree + 1):
            for current_weight, count in dynamic[current_degree].items():
                for copies in range(degree - current_degree + 1):
                    coefficient = (
                        math.comb(multiplicity + copies - 1, copies)
                        if copies
                        else 1
                    )
                    updated[current_degree + copies][
                        _weight_add(current_weight, weight, copies)
                    ] += count * coefficient
        dynamic = updated
    weights = dynamic[degree]
    rho = tuple(int(value) for value in census.RHO)
    multiplicity = 0
    for permutation, signs, parity in census.WEYL_ELEMENTS:
        transformed = tuple(
            signs[axis] * rho[permutation[axis]] for axis in range(5)
        )
        target = tuple(rho[axis] - transformed[axis] for axis in range(5))
        multiplicity += parity * weights.get(target, 0)
    return {
        "distinct_210_weights": len(weight_multiplicities),
        "total_210_weight_multiplicity": sum(weight_multiplicities.values()),
        "distinct_Sym6_weights": len(weights),
        "trivial_multiplicity": int(multiplicity),
    }


def _height_report() -> dict[str, Any]:
    coordinate_bound = SAMPLE_COORDINATE_BOUND
    vector_dimension = 210
    generator_count = 45
    generator_row_nnz = max(
        int(np.diff(generator.indptr).max(initial=0))
        for generator in invariants.integer_generators()
    )
    generator_max_entry = max(
        int(np.max(np.abs(generator.data), initial=0))
        for generator in invariants.integer_generators()
    )
    if (generator_count, generator_row_nnz, generator_max_entry) != (45, 1, 1):
        raise ArithmeticError("live generator sparsity used by the height bound drifted")
    casimir_entry_factor = generator_count * generator_row_nnz**2

    projector_denominator = 1
    projector_bounds: dict[str, Fraction] = {}
    for name, eigenvalue in projectors.SPECTRAL_EIGENVALUES.items():
        polynomial = projectors.projector_polynomial(eigenvalue)
        projector_denominator = math.lcm(
            projector_denominator,
            *(coefficient.denominator for coefficient in polynomial),
        )
        projector_bounds[name] = coordinate_bound**2 * sum(
            abs(coefficient) * casimir_entry_factor**degree
            for degree, coefficient in enumerate(polynomial)
        )

    triple_sum_bound = Fraction(0)
    feature_bounds: dict[str, Fraction] = {}
    for feature_index, coefficient in IDEAL_COEFFICIENTS.items():
        residual, left, right = FEATURE_LABELS[feature_index]
        bound = (
            vector_dimension**3
            * projector_bounds[residual]
            * projector_bounds[left]
            * projector_bounds[right]
        )
        feature_bounds[str(feature_index)] = bound
        triple_sum_bound += abs(coefficient) * bound

    norm_bound = vector_dimension * coordinate_bound**2
    hodge_component_bound = 2 * 35 * coordinate_bound**2
    hodge_norm_bound = 45 * hodge_component_bound**2
    defect_bound = Fraction(9, 5) * norm_bound**2 + hodge_norm_bound
    norm_defect_bound = norm_bound * defect_bound

    orbit_entry_bound = generator_row_nnz * coordinate_bound
    gram_entry_bound = vector_dimension * orbit_entry_bound**2
    shifted_entry_bound = gram_entry_bound + Fraction(6, 5) * norm_bound
    scalar_bound = 45**3 * gram_entry_bound * shifted_entry_bound**2

    cubic_bound = 45**3 * coordinate_bound**3
    cubic_defect_bound = 5 * cubic_bound**2 + 18 * norm_bound**3

    relation_denominator = math.lcm(
        *(coefficient.denominator for coefficient in IDEAL_COEFFICIENTS.values()),
        ND_COEFFICIENT.denominator,
        S_COEFFICIENT.denominator,
    )
    clearing_multiplier = relation_denominator * projector_denominator**3 * 25
    residual_bound = clearing_multiplier * (
        triple_sum_bound
        + abs(ND_COEFFICIENT) * norm_defect_bound
        + abs(S_COEFFICIENT) * scalar_bound
        + cubic_defect_bound
    )
    if residual_bound.denominator != 1:
        raise ArithmeticError("cleared residual height bound is not integral")
    prime_product = math.prod(PRIMES)
    return {
        "sample_coordinate_abs_bound": coordinate_bound,
        "live_generator_count": generator_count,
        "live_generator_max_row_nnz": generator_row_nnz,
        "live_generator_max_abs_entry": generator_max_entry,
        "pair_Casimir_entry_growth_factor": casimir_entry_factor,
        "global_projector_coefficient_denominator": projector_denominator,
        "relation_coefficient_denominator": relation_denominator,
        "integer_clearing_multiplier": clearing_multiplier,
        "cleared_residual_abs_upper_bound": int(residual_bound),
        "prime_product": prime_product,
        "prime_product_exceeds_twice_bound": prime_product > 2 * residual_bound,
        "all_modular_int64_products_safe": max(PRIMES) ** 2 * 210 < np.iinfo(np.int64).max,
    }


@lru_cache(maxsize=1)
def _crt_report() -> dict[str, Any]:
    samples = _sample_vectors()
    prime_rows: list[dict[str, int]] = []
    for prime in PRIMES:
        projector_coefficients = _projector_coefficients(prime)
        ideal_coefficients = {
            index: _fraction_mod(value, prime)
            for index, value in IDEAL_COEFFICIENTS.items()
        }
        alpha = _fraction_mod(ND_COEFFICIENT, prime)
        beta = _fraction_mod(S_COEFFICIENT, prime)
        evaluation_rows: list[list[int]] = []
        residuals: list[int] = []
        for vector in samples:
            features, norm_defect, scalar, norm_cubed, cubic_defect = _evaluate_mod(
                vector, prime, projector_coefficients
            )
            evaluation_rows.append(
                [features[index] for index in PIVOT_FEATURES]
                + [norm_defect, scalar, norm_cubed]
            )
            rhs = sum(
                ideal_coefficients[index] * features[index]
                for index in PIVOT_FEATURES
            )
            rhs += alpha * norm_defect + beta * scalar
            residuals.append((cubic_defect - rhs) % prime)
        prime_rows.append(
            {
                "prime": prime,
                "evaluation_rank": _rank_mod_prime(
                    np.asarray(evaluation_rows, dtype=np.int64), prime
                ),
                "maximum_relation_residual": max(residuals),
            }
        )
    return {
        "sample_seed": SAMPLE_SEED,
        "sample_count": SAMPLE_COUNT,
        "basis_columns": [
            *(f"X_{index}" for index in PIVOT_FEATURES),
            "N*D",
            "S",
            "N^3",
        ],
        "prime_rows": prime_rows,
        "all_evaluation_ranks": [row["evaluation_rank"] for row in prime_rows],
        "all_maximum_relation_residuals": [
            row["maximum_relation_residual"] for row in prime_rows
        ],
    }


def build_core() -> dict[str, Any]:
    dimension = _degree_six_dimension_report()
    height = _height_report()
    crt = _crt_report()
    checks = {
        "Sym6_invariant_dimension_is_18": dimension["trivial_multiplicity"] == 18,
        "candidate_basis_has_18_columns": len(crt["basis_columns"]) == 18,
        "all_18_sample_evaluation_matrices_have_rank_18": set(
            crt["all_evaluation_ranks"]
        )
        == {18},
        "relation_is_zero_mod_every_certificate_prime": set(
            crt["all_maximum_relation_residuals"]
        )
        == {0},
        "CRT_product_exceeds_twice_the_integer_height_bound": height[
            "prime_product_exceeds_twice_bound"
        ],
        "modular_dense_products_are_int64_safe": height[
            "all_modular_int64_products_safe"
        ],
        "all_ideal_coefficients_are_for_pivot_features": set(IDEAL_COEFFICIENTS)
        == set(PIVOT_FEATURES),
    }
    failures = [name for name, passed in checks.items() if not passed]
    coefficient_rows = [
        {
            "feature_index": index,
            "feature": FEATURE_LABELS[index],
            "coefficient": IDEAL_COEFFICIENTS[index],
        }
        for index in PIVOT_FEATURES
    ]
    return {
        "status": STATUS if not failures else "GLOBAL_SEXTIC_CERTIFICATE_FAILED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "degree_six_invariant_census": dimension,
        "identity": {
            "left": "5*I3^2-18*N^3",
            "ideal_terms": coefficient_rows,
            "N_D_coefficient": ND_COEFFICIENT,
            "S_coefficient": S_COEFFICIENT,
            "D_definition": "9*N^2/5-||*(Phi wedge Phi)||^2",
            "S_definition": "tr(G*(G-6*N*I_45/5)^2)",
            "G_definition": "O_Phi^T*O_Phi",
            "common_zero_reduction": (
                "5*I3^2-18*N^3=(1405/64)*N*D+(35/1536)*S"
            ),
        },
        "unisolvent_CRT_certificate": crt,
        "integer_height_certificate": height,
        "proof_logic": (
            "The exact D5 Racah-Speiser count gives an 18-dimensional sextic "
            "invariant space. The displayed 18 invariants have rank 18 modulo "
            "a certificate prime, hence are independent over Q and form a "
            "basis. After the displayed integer clearing multiplier is applied, "
            "the relation residual at each of the 18 samples is an integer of "
            "absolute value below the certified bound and is divisible by the "
            "full prime product; it is therefore zero. Unisolvence proves the "
            "global polynomial identity over Q."
        ),
        "real_consequence": {
            "G_is_positive_semidefinite": True,
            "S_is_nonnegative": True,
            "S_zero_consequence": (
                "spec(G) subset {0,6*N/5}; for N>0, tr(G)=24*N then rank(G)=20"
            ),
        },
        "scope": {
            "global_polynomial_identity_proved": not failures,
            "common_zero_sextic_reduction_proved": not failures,
            "D_nonnegative_proved_here": False,
            "D_zero_on_common_zero_set_proved": False,
            "cubic_sharp_inequality_proved": False,
            "global_common_zero_locus_classified": False,
            "G3_closed": False,
            "G4_closed": False,
        },
        "verdict": (
            "The global common-zero problem is reduced exactly to the two real "
            "scalars D and S through the certified sextic identity. This does "
            "not by itself prove D=0, S=0, or the signed-Kahler classification."
        ),
    }


def build_report() -> dict[str, Any]:
    dependency_hashes = {
        name: _sha256(path)
        for name, (path, _expected) in EXPECTED_DEPENDENCY_SHA256.items()
    }
    dependency_checks = {
        name: dependency_hashes[name] == expected
        for name, (_path, expected) in EXPECTED_DEPENDENCY_SHA256.items()
    }
    core = build_core()
    core_hash = _canonical_sha256(_jsonable(core))
    return {
        **core,
        "source_binding": {
            "dependency_sha256": dependency_hashes,
            "dependency_checks": dependency_checks,
            "core_sha256": core_hash,
            "expected_core_sha256": EXPECTED_CORE_SHA256,
            "core_hash_matches": core_hash == EXPECTED_CORE_SHA256,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--print-core-hash", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.print_core_hash:
        print(report["source_binding"]["core_sha256"])
        return 0
    print(json.dumps(_jsonable(report), indent=2, sort_keys=True))
    dependencies_ok = all(report["source_binding"]["dependency_checks"].values())
    return 0 if (
        report["n_failed"] == 0
        and dependencies_ok
        and report["source_binding"]["core_hash_matches"]
    ) else 1


if __name__ == "__main__":
    raise SystemExit(main())
