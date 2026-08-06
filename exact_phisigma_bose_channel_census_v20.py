#!/usr/bin/env python3
"""Exact Bose-symmetric 210_H^2--126bar_H†126bar_H channel census.

The unrestricted tensor product 210 x 210 overcounts scalar quartics because
both 210_H factors are the same commuting real scalar.  The relevant object is
Sym^2(210).  This module verifies by a D5 Weyl-character identity that

    Sym^2(210) = 1 + 45 + 54 + 210 + 770
                 + 1050 + 1050bar + 4125 + 5940 + 8910.

Together with

    126 x 126bar = 1 + 45 + 210 + 770 + 5940 + 8910,

there are exactly six multiplicity-one Hermitian Phi-Phi-Sigma†-Sigma quartic
channels: 1, 45, 210, 770, 5940 and 8910.

The repository already has exact pure singlet and 45 channels and one further
independent recoupled contraction ||C_Phi Sigma||^2.  The latter has a nonzero
t2bar--t4bar entry, while the first two are diagonal, so the three exact
structures are linearly independent.  Exactly three independent quartic
directions therefore remain unresolved.  This is an operator census, not a
component-Clebsch derivation for those remaining directions.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable

import mpmath as mp
import numpy as np

import exact_mixed_45_triplet_channel_v20 as channel45
import exact_portal_norm_square_triplet_channel_v20 as contraction_c

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_PHISIGMA_BOSE_CHANNEL_CENSUS_V20.json"
OUT_MD = ROOT / "EXACT_PHISIGMA_BOSE_CHANNEL_CENSUS_V20.md"

# Dynkin labels use the D5 ordering in which the vector is (1,0,0,0,0)
# and the real four-form 210 is (0,0,0,1,1).
IRREPS: dict[str, dict[str, Any]] = {
    "1": {"dimension": 1, "label": (0, 0, 0, 0, 0)},
    "45": {"dimension": 45, "label": (0, 1, 0, 0, 0)},
    "54": {"dimension": 54, "label": (2, 0, 0, 0, 0)},
    "210": {"dimension": 210, "label": (0, 0, 0, 1, 1)},
    "770": {"dimension": 770, "label": (0, 2, 0, 0, 0)},
    "945": {"dimension": 945, "label": (1, 0, 1, 0, 0)},
    "1050": {"dimension": 1050, "label": (1, 0, 0, 0, 2)},
    "1050bar": {"dimension": 1050, "label": (1, 0, 0, 2, 0)},
    "4125": {"dimension": 4125, "label": (0, 0, 2, 0, 0)},
    "5940": {"dimension": 5940, "label": (0, 1, 0, 1, 1)},
    "6930": {"dimension": 6930, "label": None},
    "6930bar": {"dimension": 6930, "label": None},
    "8910": {"dimension": 8910, "label": (0, 0, 0, 2, 2)},
}

FULL_210_PRODUCT = {
    "1": 1,
    "45": 2,
    "54": 1,
    "210": 2,
    "770": 1,
    "945": 2,
    "1050": 1,
    "1050bar": 1,
    "4125": 1,
    "5940": 2,
    "6930": 1,
    "6930bar": 1,
    "8910": 1,
}

SYMMETRIC_210_PRODUCT = {
    "1": 1,
    "45": 1,
    "54": 1,
    "210": 1,
    "770": 1,
    "1050": 1,
    "1050bar": 1,
    "4125": 1,
    "5940": 1,
    "8910": 1,
}

ANTISYMMETRIC_210_PRODUCT = {
    "45": 1,
    "210": 1,
    "945": 2,
    "5940": 1,
    "6930": 1,
    "6930bar": 1,
}

SIGMA_ENDOMORPHISM = {
    "1": 1,
    "45": 1,
    "210": 1,
    "770": 1,
    "5940": 1,
    "8910": 1,
}

COMMON_QUARTIC_CHANNELS = {
    name: min(SYMMETRIC_210_PRODUCT[name], SIGMA_ENDOMORPHISM[name])
    for name in SYMMETRIC_210_PRODUCT
    if name in SIGMA_ENDOMORPHISM
}

# Fundamental weights in the orthonormal e_i basis, stored exactly.
FUNDAMENTAL_WEIGHTS = (
    (Fraction(1), Fraction(0), Fraction(0), Fraction(0), Fraction(0)),
    (Fraction(1), Fraction(1), Fraction(0), Fraction(0), Fraction(0)),
    (Fraction(1), Fraction(1), Fraction(1), Fraction(0), Fraction(0)),
    (
        Fraction(1, 2),
        Fraction(1, 2),
        Fraction(1, 2),
        Fraction(1, 2),
        Fraction(-1, 2),
    ),
    (
        Fraction(1, 2),
        Fraction(1, 2),
        Fraction(1, 2),
        Fraction(1, 2),
        Fraction(1, 2),
    ),
)
RHO = (Fraction(4), Fraction(3), Fraction(2), Fraction(1), Fraction(0))


def label_to_e(label: Iterable[int]) -> tuple[Fraction, ...]:
    coefficients = tuple(int(value) for value in label)
    if len(coefficients) != 5:
        raise ValueError("D5 Dynkin labels must have length five")
    return tuple(
        sum(
            Fraction(coefficients[index]) * FUNDAMENTAL_WEIGHTS[index][axis]
            for index in range(5)
        )
        for axis in range(5)
    )


def weyl_dimension(label: Iterable[int]) -> int:
    """Exact D5 Weyl dimension formula in orthonormal coordinates."""
    highest = label_to_e(label)
    shifted = tuple(highest[index] + RHO[index] for index in range(5))
    result = Fraction(1)
    for i in range(5):
        for j in range(i + 1, 5):
            numerator = shifted[i] ** 2 - shifted[j] ** 2
            denominator = RHO[i] ** 2 - RHO[j] ** 2
            result *= numerator / denominator
    if result.denominator != 1:
        raise AssertionError(f"nonintegral Weyl dimension {result}")
    return int(result)


def _weighted_dimension(decomposition: dict[str, int]) -> int:
    return sum(IRREPS[name]["dimension"] * multiplicity for name, multiplicity in decomposition.items())


def _permutation_sign(permutation: tuple[int, ...]) -> int:
    inversions = sum(
        1
        for i in range(len(permutation))
        for j in range(i + 1, len(permutation))
        if permutation[i] > permutation[j]
    )
    return -1 if inversions % 2 else 1


def _weyl_elements() -> tuple[tuple[tuple[int, ...], tuple[int, ...], int], ...]:
    rows: list[tuple[tuple[int, ...], tuple[int, ...], int]] = []
    for permutation in itertools.permutations(range(5)):
        sign_permutation = _permutation_sign(permutation)
        for signs in itertools.product((1, -1), repeat=5):
            if math.prod(signs) == 1:
                rows.append((permutation, signs, sign_permutation))
    return tuple(rows)


WEYL_ELEMENTS = _weyl_elements()


def _alternant(vector: Iterable[Fraction], point: tuple[mp.mpf, ...]) -> mp.mpf:
    values = tuple(mp.mpf(value.numerator) / value.denominator for value in vector)
    total = mp.mpf("0")
    for permutation, signs, parity in WEYL_ELEMENTS:
        exponent = sum(
            mp.mpf(signs[axis]) * values[permutation[axis]] * point[axis]
            for axis in range(5)
        )
        total += parity * mp.exp(exponent)
    return total


def weyl_character(label: Iterable[int], point: tuple[mp.mpf, ...]) -> mp.mpf:
    highest = label_to_e(label)
    shifted = tuple(highest[index] + RHO[index] for index in range(5))
    return _alternant(shifted, point) / _alternant(RHO, point)


def _vector_weights() -> tuple[tuple[int, ...], ...]:
    rows: list[tuple[int, ...]] = []
    for index in range(5):
        plus = [0] * 5
        minus = [0] * 5
        plus[index] = 1
        minus[index] = -1
        rows.extend((tuple(plus), tuple(minus)))
    return tuple(rows)


VECTOR_WEIGHTS = _vector_weights()
FOUR_FORM_WEIGHTS = tuple(
    tuple(sum(VECTOR_WEIGHTS[item][axis] for item in combination) for axis in range(5))
    for combination in itertools.combinations(range(10), 4)
)


def four_form_character(point: tuple[mp.mpf, ...]) -> mp.mpf:
    return sum(
        mp.exp(sum(mp.mpf(weight[axis]) * point[axis] for axis in range(5)))
        for weight in FOUR_FORM_WEIGHTS
    )


def symmetric_square_character(point: tuple[mp.mpf, ...]) -> mp.mpf:
    character = four_form_character(point)
    doubled = four_form_character(tuple(2 * value for value in point))
    return (character**2 + doubled) / 2


def decomposition_character(
    decomposition: dict[str, int], point: tuple[mp.mpf, ...]
) -> mp.mpf:
    total = mp.mpf("0")
    for name, multiplicity in decomposition.items():
        label = IRREPS[name]["label"]
        if label is None:
            raise ValueError(f"no Dynkin label recorded for {name}")
        total += multiplicity * weyl_character(label, point)
    return total


def _character_audit() -> dict[str, Any]:
    mp.mp.dps = 80
    points = (
        tuple(mp.mpf(value) for value in ("0.13", "0.07", "-0.04", "0.09", "-0.11")),
        tuple(mp.mpf(value) for value in ("-0.08", "0.12", "0.05", "-0.09", "0.03")),
    )
    # The only other dimension-compatible decomposition with the required
    # highest-weight 8910 replaces 1050+1050bar by 210+2*945.
    dimension_degenerate_alternative = dict(SYMMETRIC_210_PRODUCT)
    dimension_degenerate_alternative.pop("1050")
    dimension_degenerate_alternative.pop("1050bar")
    dimension_degenerate_alternative["210"] = 2
    dimension_degenerate_alternative["945"] = 2

    rows: list[dict[str, float]] = []
    maximum_identity_residual = mp.mpf("0")
    minimum_alternative_residual: mp.mpf | None = None
    for point in points:
        target = symmetric_square_character(point)
        proposed = decomposition_character(SYMMETRIC_210_PRODUCT, point)
        alternative = decomposition_character(dimension_degenerate_alternative, point)
        identity_residual = abs(target - proposed)
        alternative_residual = abs(target - alternative)
        maximum_identity_residual = max(maximum_identity_residual, identity_residual)
        minimum_alternative_residual = (
            alternative_residual
            if minimum_alternative_residual is None
            else min(minimum_alternative_residual, alternative_residual)
        )
        rows.append(
            {
                "target_character": float(target),
                "proposed_character": float(proposed),
                "identity_abs_residual": float(identity_residual),
                "alternative_abs_residual": float(alternative_residual),
            }
        )
    assert minimum_alternative_residual is not None
    return {
        "points": rows,
        "maximum_identity_abs_residual": float(maximum_identity_residual),
        "minimum_dimension_degenerate_alternative_abs_residual": float(
            minimum_alternative_residual
        ),
    }


def _resolved_span_audit() -> dict[str, Any]:
    p, a, omega = 0.9, 0.4, 0.7
    sigma45 = {
        name: channel45.sigma_component_coefficient(p, a, omega, name)
        for name in (
            "t2_triplet",
            "t2bar_antitriplet",
            "t4bar_antitriplet",
        )
    }
    values45 = np.asarray(list(sigma45.values()), dtype=float)
    exact_c = contraction_c.analytic_sigma_blocks(p, a, omega)
    offdiagonal_c = complex(exact_c["A_v_sigma_GeV2"][0, 1])
    singlet_vector = np.ones(3)
    matrix = np.column_stack((singlet_vector, values45))
    diagonal_span_rank = int(np.linalg.matrix_rank(matrix, tol=1.0e-12))
    full_exact_span_rank = diagonal_span_rank + int(abs(offdiagonal_c) > 1.0e-12)
    return {
        "benchmark": {"p": p, "a": a, "omega": omega},
        "sigma_45_diagonal_coefficients": sigma45,
        "singlet_45_diagonal_span_rank": diagonal_span_rank,
        "C_contraction_t2bar_t4bar_offdiagonal": {
            "re": float(offdiagonal_c.real),
            "im": float(offdiagonal_c.imag),
        },
        "exact_independent_span_rank": full_exact_span_rank,
        "unresolved_independent_directions": len(COMMON_QUARTIC_CHANNELS)
        - full_exact_span_rank,
    }


def build_report() -> dict[str, Any]:
    dimension_checks = {
        name: weyl_dimension(data["label"]) == data["dimension"]
        for name, data in IRREPS.items()
        if data["label"] is not None
    }
    character = _character_audit()
    span = _resolved_span_audit()

    symmetric_dimension = _weighted_dimension(SYMMETRIC_210_PRODUCT)
    antisymmetric_dimension = _weighted_dimension(ANTISYMMETRIC_210_PRODUCT)
    full_dimension = _weighted_dimension(FULL_210_PRODUCT)
    checks = {
        "all_recorded_D5_dimensions_exact": all(dimension_checks.values()),
        "full_product_dimension_210_squared": full_dimension == 210**2,
        "symmetric_square_dimension": symmetric_dimension == 210 * 211 // 2,
        "antisymmetric_square_dimension": antisymmetric_dimension == 210 * 209 // 2,
        "symmetric_plus_antisymmetric_reconstructs_full_product": all(
            SYMMETRIC_210_PRODUCT.get(name, 0)
            + ANTISYMMETRIC_210_PRODUCT.get(name, 0)
            == multiplicity
            for name, multiplicity in FULL_210_PRODUCT.items()
        ),
        "weyl_character_identity": character["maximum_identity_abs_residual"]
        < 1.0e-40,
        "dimension_degenerate_alternative_rejected": character[
            "minimum_dimension_degenerate_alternative_abs_residual"
        ]
        > 1.0e-6,
        "common_channels_exactly_six": set(COMMON_QUARTIC_CHANNELS)
        == {"1", "45", "210", "770", "5940", "8910"},
        "common_channels_multiplicity_one": all(
            multiplicity == 1 for multiplicity in COMMON_QUARTIC_CHANNELS.values()
        ),
        "singlet_and_45_linearly_independent": span[
            "singlet_45_diagonal_span_rank"
        ]
        == 2,
        "C_contraction_independent_by_offdiagonal": abs(
            span["C_contraction_t2bar_t4bar_offdiagonal"]["re"]
        )
        > 1.0e-12,
        "exact_span_rank_three": span["exact_independent_span_rank"] == 3,
        "exactly_three_quartic_directions_unresolved": span[
            "unresolved_independent_directions"
        ]
        == 3,
        "remaining_component_Clebsches_not_claimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]
    return {
        "status": (
            "EXACT_PHISIGMA_BOSE_CHANNEL_CENSUS__THREE_DIRECTIONS_REMAIN"
            if not failures
            else "EXACT_PHISIGMA_BOSE_CHANNEL_CENSUS_FAILED"
        ),
        "overall_state": "CLOSED_SUBPROBLEM" if not failures else "EXECUTION_FAIL",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "source_contract": {
            "full_tensor_product_table": "LieART tensor-product table, arXiv:1206.6379",
            "Bose_projection": "verified independently by D5 Weyl-character identity",
        },
        "representation_dimensions": dimension_checks,
        "decompositions": {
            "210_x_210": FULL_210_PRODUCT,
            "Sym2_210": SYMMETRIC_210_PRODUCT,
            "Lambda2_210": ANTISYMMETRIC_210_PRODUCT,
            "126_x_126bar": SIGMA_ENDOMORPHISM,
            "common_Bose_symmetric_quartic_channels": COMMON_QUARTIC_CHANNELS,
        },
        "dimension_audit": {
            "full": full_dimension,
            "symmetric": symmetric_dimension,
            "antisymmetric": antisymmetric_dimension,
        },
        "character_audit": character,
        "resolved_span_audit": span,
        "channel_accounting": {
            "total_independent_Hermitian_PhiSigma_quartics": 6,
            "exact_pure_singlet": True,
            "exact_pure_45": True,
            "exact_additional_recoupled_C_contraction": True,
            "exact_independent_span_dimension": 3,
            "remaining_independent_span_dimension": 3,
            "remaining_pure_irrep_assignment": (
                "open: the C-contraction must be recoupled before assigning a "
                "basis among 210,770,5940,8910"
            ),
        },
        "newly_closed_subproblem": {
            "Bose_symmetric_210_square_decomposition": not failures,
            "PhiSigma_quartic_channel_count": not failures,
            "remaining_independent_direction_count": not failures,
        },
        "remaining_blockers": {
            "recouple_C_contraction_into_pure_irrep_projectors": True,
            "derive_three_complementary_quartic_component_matrices": True,
            "all_mixing_relevant_210_states": True,
            "complete_component_potential": True,
            "unique_full_vacuum_and_Hessian": True,
            "physical_threshold_spectrum": True,
            "component_level_two_loop_matching": True,
            "exact_unique_proton_lifetime": True,
        },
        "flag": {
            "exact_PhiSigma_channel_census_complete": not failures,
            "all_PhiSigma_quartic_component_Clebsches_complete": False,
            "complete_component_potential": False,
            "physical_triplet_spectrum_complete": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
            "empirical_discovery": False,
        },
        "verdict": (
            "Bose symmetry reduces the apparent 210x210 inventory to six "
            "multiplicity-one PhiSigma quartic channels. The repository spans "
            "three independent directions exactly, so exactly three independent "
            "quartic directions remain to be derived."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    accounting = report["channel_accounting"]
    return "\n".join(
        [
            "# Exact Phi–Sigma Bose-symmetric channel census — v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            "- `Sym^2(210) = 1+45+54+210+770+1050+1050bar+4125+5940+8910`",
            "- Common with `126x126bar`: `1,45,210,770,5940,8910`.",
            f"- Exact span dimension: `{accounting['exact_independent_span_dimension']}`.",
            f"- Remaining independent directions: `{accounting['remaining_independent_span_dimension']}`.",
            "- This census does not yet supply the three missing component matrices.",
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
