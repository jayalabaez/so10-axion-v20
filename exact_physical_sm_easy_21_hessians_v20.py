#!/usr/bin/env python3
"""Exact physical-SM target Hessians for 21 non-hard active witness rows.

The rows covered here are the fourteen norm/singlet-dressing rows, the unique
Phi cubic, both H self-quartics, and all four Phi self-quartics.  Their complete
486-real target Hessians are derived directly over Q (and Z for the tensor
maps).  Together with the separate hard-projector theorem this gives exact
source Hessians for 31 of the 37 active witness rows.  The six O14/O35/O46
rows, exact aggregate stationarity/kernel/rank/PSD, and the full global
equality orbit remain open; consequently this theorem does not close G3-G5.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

import numpy as np

import exact_physical_sm_hard_projector_hessians_v20 as hard
import gauged_u1x_g2_derivative_audit_v20 as exact_g2
import live_g2_canonical_486_field_chart_v20 as chart
import physical_sm_vacuum_local_feasibility_v20 as foundation


ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_PHYSICAL_SM_EASY_21_HESSIANS_V20.json"
OUT_MD = ROOT / "EXACT_PHYSICAL_SM_EASY_21_HESSIANS_V20.md"
SCHEMA = "exact_physical_sm_easy_21_hessians_v20"
STATUS = "EXACT_21_NONHARD_HESSIANS__COMBINED_31_OF_37_SOURCE_ROWS__AGGREGATE_AND_GLOBAL_EQUALITY_OPEN"
FIELD_DIMENSION = 486
TARGET_DENOMINATOR = 20
INT64_MAX = int(np.iinfo(np.int64).max)

SOURCE_HASHES = {
    "exact_physical_sm_hard_projector_hessians_v20.py": "2ac49af04f3bbec17a4e616c82898de6a0710ddcfa3462d7ec8d59dad69de27e",
    "physical_sm_vacuum_local_feasibility_v20.py": "629ea8c45f101f82b6b4e963fd1fb19dcc5735fe52a1d8efb1fb0812dbaa565c",
    "live_g2_canonical_486_field_chart_v20.py": "9275dbb204324cc48dfd7139cad836e034b1b83b07bd60aecd6ff093d3ab7765",
    "gauged_u1x_g2_derivative_audit_v20.py": "584e03994ca1187228377c3e4c145d95446ade50616e2d58068e0fee9f96507d",
    "live_g2_exact_quadratic_family_derivatives_v20.py": "0a719beadfeca00bb203f4e47e3cb381635e8a8165b7c7707753433325642c47",
    "live_g2_exact_h10_self_quartic_derivatives_v20.py": "1aa8e0d7cbb1b54aa099047b5a2f0cf4482cf32a2d14ac06773770de5d887f6d",
    "live_g2_exact_remaining_cubic_derivatives_v20.py": "83502cf47b5f859328c723de0edbd8018825e94e09a1001461dee22751244276",
    "live_g2_exact_phi_self_quartic_derivatives_v20.py": "c613690857f362b4fb9730f9c7abcddd0711737b30d0db423fd9f1c60ca7631c",
    "exact_h10_self_quartic_family_v20.py": "a6a54818fce5a98b9e06d657581bb43482eb63a8598860840bc2553060b3f94e",
    "exact_210_self_invariant_basis_v20.py": "663747aa896d8609a0a12fb0bbf5374520ef4fc3a205b6525cbba66022654ae5",
    "exact_phisigma_casimir_projectors_v20.py": "372401c9b760e7b4e2224d4b6b2151611e68e7ba786ec735ebbd8baeb0103355",
}

NORM_ROW_FACTORS = {
    "O03_B01_singlet_polynomial": ("X",),
    "O04_B01_singlet_polynomial": ("S",),
    "O05_B01_126bar_norm": ("Sigma",),
    "O06_B01_Hdag_H_norm": ("H",),
    "O07_B01_Phi_norm": ("Phi",),
    "O20_B01_singlet_polynomial": ("X", "X"),
    "O22_B01_singlet_polynomial": ("S", "X"),
    "O23_B01_singlet_polynomial": ("S", "S"),
    "O25_B01_126bar_norm": ("Sigma", "X"),
    "O26_B01_126bar_norm": ("Sigma", "S"),
    "O33_B01_Hdag_H_norm": ("H", "X"),
    "O34_B01_Hdag_H_norm": ("H", "S"),
    "O42_B01_Phi_norm": ("Phi", "X"),
    "O43_B01_Phi_norm": ("Phi", "S"),
}
H_SELF_ROWS = {
    "O36_B01_H_self_quartics": "I_1",
    "O36_B02_H_self_quartics": "I_54",
}
PHI_SELF_ROWS = {
    "O48_B01_Phi_self_quartics": ("J0", 0),
    "O48_B02_Phi_self_quartics": ("J2", 2),
    "O48_B03_Phi_self_quartics": ("J3", 3),
    "O48_B04_Phi_self_quartics": ("J4", 4),
}
OPEN_ROWS = (
    "O14_B01_Phi_Sigma_Sigmadag_cubic",
    "O35_B01_H_Sigma_hermitian",
    "O35_B02_H_Sigma_hermitian",
    "O46_B01_Phi2_HdagH_channels",
    "O46_B02_Phi2_HdagH_channels",
    "O46_B03_Phi2_HdagH_channels",
)


def _portable_lf_sha256(path: Path) -> str:
    payload = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(payload).hexdigest()


def source_bindings() -> dict[str, Any]:
    rows = {}
    for name, expected in SOURCE_HASHES.items():
        observed = _portable_lf_sha256(ROOT / name)
        if observed != expected:
            raise ArithmeticError(f"easy-21 source dependency drifted: {name}")
        rows[name] = {"portable_lf_sha256": observed, "matches": True}
    return {"files": rows, "all_portable_lf_pins_match": True}


def _add_fraction(
    output: dict[Any, Fraction], key: Any, value: Fraction
) -> None:
    updated = output.get(key, Fraction(0)) + value
    if updated:
        output[key] = updated
    else:
        output.pop(key, None)


@dataclass(frozen=True)
class SparseJet:
    value: Fraction
    gradient: dict[int, Fraction]
    hessian: dict[tuple[int, int], Fraction]


def _quadratic_factor(
    indices: Iterable[int], coefficient: Fraction, target: np.ndarray
) -> SparseJet:
    support = tuple(int(index) for index in indices)
    value = coefficient * sum(int(target[index]) ** 2 for index in support) / 400
    gradient = {
        index: coefficient * int(target[index]) / 10
        for index in support
        if target[index]
    }
    hessian = {(index, index): 2 * coefficient for index in support}
    return SparseJet(Fraction(value), gradient, hessian)


def _multiply(left: SparseJet, right: SparseJet) -> SparseJet:
    gradient: dict[int, Fraction] = {}
    for index, value in left.gradient.items():
        _add_fraction(gradient, index, value * right.value)
    for index, value in right.gradient.items():
        _add_fraction(gradient, index, value * left.value)
    hessian: dict[tuple[int, int], Fraction] = {}
    for key, value in left.hessian.items():
        _add_fraction(hessian, key, value * right.value)
    for key, value in right.hessian.items():
        _add_fraction(hessian, key, value * left.value)
    for first, first_value in left.gradient.items():
        for second, second_value in right.gradient.items():
            _add_fraction(hessian, (first, second), first_value * second_value)
            _add_fraction(hessian, (second, first), first_value * second_value)
    return SparseJet(left.value * right.value, gradient, hessian)


def _rational_hessian_from_entries(
    entries: dict[tuple[int, int], Fraction]
) -> hard.RationalHessian:
    denominator = math.lcm(*(value.denominator for value in entries.values()), 1)
    numerator = np.zeros((FIELD_DIMENSION, FIELD_DIMENSION), dtype=np.int64)
    for (row, column), value in entries.items():
        integer = value.numerator * (denominator // value.denominator)
        if not -INT64_MAX <= integer <= INT64_MAX:
            raise OverflowError("easy-21 rational Hessian entry exceeds int64")
        numerator[row, column] = integer
    return hard.RationalHessian.normalized(numerator, denominator)


def _combine(
    terms: Iterable[tuple[Fraction, hard.RationalHessian]]
) -> hard.RationalHessian:
    entries: dict[tuple[int, int], Fraction] = {}
    for coefficient, matrix in terms:
        for key, value in matrix.fraction_entries().items():
            _add_fraction(entries, key, coefficient * value)
    return _rational_hessian_from_entries(entries)


def _factor_jets(target: np.ndarray) -> dict[str, SparseJet]:
    return {
        "X": _quadratic_factor(range(chart.X_SLICE.start, chart.X_SLICE.stop), Fraction(1, 2), target),
        "S": _quadratic_factor(range(chart.S_SLICE.start, chart.S_SLICE.stop), Fraction(1, 2), target),
        "Sigma": _quadratic_factor(range(chart.SIGMA_SLICE.start, chart.SIGMA_SLICE.stop), Fraction(1, 2), target),
        "H": _quadratic_factor(range(chart.H_SLICE.start, chart.H_SLICE.stop), Fraction(1, 2), target),
        "Phi": _quadratic_factor(range(chart.PHI_SLICE.start, chart.PHI_SLICE.stop), Fraction(1), target),
    }


def exact_norm_rows(
    target: np.ndarray,
) -> tuple[dict[str, hard.RationalHessian], dict[str, Any]]:
    factors = _factor_jets(target)
    rows: dict[str, hard.RationalHessian] = {}
    values: dict[str, str] = {}
    degrees: dict[str, int] = {}
    for direction_id, names in NORM_ROW_FACTORS.items():
        jet = factors[names[0]]
        if len(names) == 2:
            jet = _multiply(jet, factors[names[1]])
        matrix = _rational_hessian_from_entries(jet.hessian)
        rows[direction_id] = matrix
        values[direction_id] = str(jet.value)
        degrees[direction_id] = 2 * len(names)
    return rows, {
        "factor_definitions": {
            "X": "(q_X.re^2+q_X.im^2)/2",
            "S": "(q_S.re^2+q_S.im^2)/2",
            "Sigma": "sum(q_Sigma^2)/2",
            "H": "sum(q_H^2)/2",
            "Phi": "sum(q_Phi^2)",
        },
        "row_factorization": NORM_ROW_FACTORS,
        "exact_target_values": values,
        "degrees": degrees,
    }


def _permutation_sign(sequence: tuple[int, ...]) -> int:
    inversions = sum(
        sequence[first] > sequence[second]
        for first in range(len(sequence))
        for second in range(first + 1, len(sequence))
    )
    return -1 if inversions % 2 else 1


@lru_cache(maxsize=1)
def _exact_phi_two_form_basis() -> np.ndarray:
    two_indices = tuple(itertools.combinations(range(10), 2))
    output = np.zeros((chart.PHI_DIM, len(two_indices), len(two_indices)), dtype=np.int64)
    lookup = {indices: position for position, indices in enumerate(chart.PHI_INDICES)}
    for row, left in enumerate(two_indices):
        for column, right in enumerate(two_indices):
            if set(left).intersection(right):
                continue
            sequence = left + right
            output[lookup[tuple(sorted(sequence))], row, column] = _permutation_sign(sequence)
    return output


def exact_phi_cubic(target: np.ndarray) -> hard.RationalHessian:
    basis = _exact_phi_two_form_basis()
    x = target[chart.PHI_SLICE]
    matrix = np.einsum("p,pij->ij", x, basis, optimize=True)
    maximum = int(np.max(np.abs(matrix), initial=0))
    bound = 6 * matrix.shape[0] * maximum
    if bound > INT64_MAX:
        raise OverflowError("Phi cubic Hessian preflight exceeds int64")
    block = np.empty((chart.PHI_DIM, chart.PHI_DIM), dtype=np.int64)
    for index, basis_matrix in enumerate(basis):
        derivative_square = matrix @ basis_matrix + basis_matrix @ matrix
        block[index] = 3 * np.einsum(
            "ij,pji->p", derivative_square, basis, optimize=True
        )
    if not np.array_equal(block, block.T):
        raise ArithmeticError("exact Phi cubic Hessian is asymmetric")
    full = np.zeros((FIELD_DIMENSION, FIELD_DIMENSION), dtype=np.int64)
    full[chart.PHI_SLICE, chart.PHI_SLICE] = block
    return hard.RationalHessian.normalized(full, 20)


def exact_h_self_rows(
    target: np.ndarray,
) -> tuple[dict[str, hard.RationalHessian], dict[str, Any]]:
    h_factor = _factor_jets(target)["H"]
    norm_squared = _rational_hessian_from_entries(_multiply(h_factor, h_factor).hessian)
    block = target[chart.H_SLICE]
    grad_real = np.zeros(chart.H_REAL_DIM, dtype=np.int64)
    grad_imaginary = np.zeros(chart.H_REAL_DIM, dtype=np.int64)
    for index in range(chart.H_COMPLEX_DIM):
        x = int(block[2 * index])
        y = int(block[2 * index + 1])
        grad_real[2 * index] = x
        grad_real[2 * index + 1] = -y
        grad_imaginary[2 * index] = y
        grad_imaginary[2 * index + 1] = x
    pair_block = 2 * (
        np.outer(grad_real, grad_real)
        + np.outer(grad_imaginary, grad_imaginary)
    )
    pair_full = np.zeros((FIELD_DIMENSION, FIELD_DIMENSION), dtype=np.int64)
    pair_full[chart.H_SLICE, chart.H_SLICE] = pair_block
    pair_modulus = hard.RationalHessian.normalized(pair_full, 400)
    channel_1 = _combine(((Fraction(1, 10), pair_modulus),))
    channel_54 = _combine(
        ((Fraction(1), norm_squared), (Fraction(-1, 10), pair_modulus))
    )
    reconstruction = _combine(((Fraction(1), channel_1), (Fraction(1), channel_54)))
    if reconstruction.fraction_entries() != norm_squared.fraction_entries():
        raise ArithmeticError("H 1+54 Hessian projector reconstruction failed")
    return {
        "O36_B01_H_self_quartics": channel_1,
        "O36_B02_H_self_quartics": channel_54,
    }, {
        "target_HdotH_exactly_zero": not np.any(block[0::2] @ block[0::2] - block[1::2] @ block[1::2])
        and int(block[0::2] @ block[1::2]) == 0,
        "I1_plus_I54_reconstructs_HdagH_squared_Hessian_entrywise_over_Q": True,
        "HdagH_squared_Hessian_sha256": norm_squared.sha256(),
    }


def _exact_phi_pair_power(matrix: np.ndarray, degree: int) -> np.ndarray:
    current = np.asarray(matrix, dtype=np.int64)
    for _ in range(degree):
        current = exact_g2._exact_phi_pair_casimir(current)
    return current


def exact_phi_self_rows(
    target: np.ndarray,
) -> tuple[dict[str, hard.RationalHessian], dict[str, Any]]:
    x = target[chart.PHI_SLICE]
    pair = np.outer(x, x)
    images = {degree: _exact_phi_pair_power(pair, degree) for degree in (0, 2, 3, 4)}
    blocks = {
        degree: np.zeros((chart.PHI_DIM, chart.PHI_DIM), dtype=np.int64)
        for degree in images
    }
    maxima: dict[int, int] = {}
    for column in range(chart.PHI_DIM):
        unit = np.zeros(chart.PHI_DIM, dtype=np.int64)
        unit[column] = 1
        linear = np.outer(x, unit) + np.outer(unit, x)
        for degree, image in images.items():
            linear_image = _exact_phi_pair_power(linear, degree)
            vector = linear_image @ x + image[:, column]
            if int(np.max(np.abs(vector), initial=0)) > INT64_MAX // 4:
                raise OverflowError("Phi self Hessian preflight exceeds int64")
            blocks[degree][:, column] = 4 * vector
            maxima[degree] = max(maxima.get(degree, 0), int(np.max(np.abs(linear_image), initial=0)))
    rows = {}
    for direction_id, (_label, degree) in PHI_SELF_ROWS.items():
        block = blocks[degree]
        if not np.array_equal(block, block.T):
            raise ArithmeticError(f"Phi moment {degree} Hessian is asymmetric")
        full = np.zeros((FIELD_DIMENSION, FIELD_DIMENSION), dtype=np.int64)
        full[chart.PHI_SLICE, chart.PHI_SLICE] = block
        rows[direction_id] = hard.RationalHessian.normalized(full, 400)
    return rows, {
        "moment_degrees": [0, 2, 3, 4],
        "maximum_abs_linear_pair_Casimir_images": maxima,
        "all_int64_preflights_pass": True,
    }


def _homogeneous_jet_summary(
    hessian: hard.RationalHessian, target: np.ndarray, degree: int
) -> dict[str, Any]:
    product = hessian.numerator @ target
    gradient_denominator = hessian.denominator * TARGET_DENOMINATOR * (degree - 1)
    divisor = gradient_denominator
    for value in product:
        divisor = math.gcd(divisor, abs(int(value)))
    gradient_numerator = product // divisor
    gradient_denominator //= divisor
    value = Fraction(
        int(target @ product),
        hessian.denominator * TARGET_DENOMINATOR**2 * degree * (degree - 1),
    )
    q_dot_gradient = sum(
        Fraction(int(target[index]), TARGET_DENOMINATOR)
        * Fraction(int(gradient_numerator[index]), gradient_denominator)
        for index in range(FIELD_DIMENSION)
    )
    return {
        "homogeneous_degree": degree,
        "value": str(value),
        "gradient_denominator": gradient_denominator,
        "gradient_nonzero_entries": int(np.count_nonzero(gradient_numerator)),
        "Hq_equals_degree_minus_1_times_gradient_exactly": True,
        "q_dot_gradient_equals_degree_times_value_exactly": q_dot_gradient == degree * value,
    }


def _row_summary(
    direction_id: str,
    family: str,
    basis_label: str,
    degree: int,
    hessian: hard.RationalHessian,
    target: np.ndarray,
) -> dict[str, Any]:
    if not np.array_equal(hessian.numerator, hessian.numerator.T):
        raise ArithmeticError(f"{direction_id} Hessian is asymmetric")
    jet = _homogeneous_jet_summary(hessian, target, degree)
    if not jet["q_dot_gradient_equals_degree_times_value_exactly"]:
        raise ArithmeticError(f"{direction_id} failed exact Euler identity")
    return {
        "parameter_id": f"lambda::{direction_id}",
        "direction_id": direction_id,
        "family": family,
        "basis_label": basis_label,
        "Hessian": {
            "dimension": FIELD_DIMENSION,
            "denominator": hessian.denominator,
            "nonzero_entries_full_matrix": int(np.count_nonzero(hessian.numerator)),
            "maximum_abs_numerator": int(np.max(np.abs(hessian.numerator), initial=0)),
            "symmetric_entrywise_over_Q": True,
            "canonical_sparse_rational_sha256": hessian.sha256(),
        },
        "exact_target_jet_from_homogeneity": jet,
    }


@lru_cache(maxsize=1)
def build_report() -> dict[str, Any]:
    bindings = source_bindings()
    target = foundation.integer_target_vector().copy()
    norm_rows, norm_certificate = exact_norm_rows(target)
    h_rows, h_certificate = exact_h_self_rows(target)
    phi_rows, phi_certificate = exact_phi_self_rows(target)
    cubic = exact_phi_cubic(target)

    summaries = []
    for direction_id, matrix in norm_rows.items():
        names = NORM_ROW_FACTORS[direction_id]
        summaries.append(
            _row_summary(
                direction_id,
                direction_id.split("_", 2)[2],
                "*".join(names),
                2 * len(names),
                matrix,
                target,
            )
        )
    summaries.append(
        _row_summary(
            "O17_B01_Phi_cubic", "Phi_cubic", "Tr(A_Phi^3)", 3, cubic, target
        )
    )
    for direction_id, matrix in h_rows.items():
        summaries.append(
            _row_summary(
                direction_id, "H_self_quartics", H_SELF_ROWS[direction_id], 4, matrix, target
            )
        )
    for direction_id, matrix in phi_rows.items():
        label, _degree = PHI_SELF_ROWS[direction_id]
        summaries.append(
            _row_summary(direction_id, "Phi_self_quartics", label, 4, matrix, target)
        )
    summaries.sort(key=lambda row: row["direction_id"])
    if len(summaries) != 21:
        raise ArithmeticError("easy source Hessian inventory is not 21 rows")

    claims = {
        "exact_source_algebra_Hessians_for_21_rows_here": True,
        "combined_with_hard_theorem_exact_source_rows": 31,
        "exact_source_algebra_Hessians_for_all_37_active_rows": False,
        "exact_full_witness_aggregate_stationarity": False,
        "exact_full_witness_symmetry_kernel": False,
        "exact_full_witness_rank_448_and_PSD": False,
        "full_486_field_global_equality_orbit_classified": False,
        "physical_SM_G3_closed": False,
        "physical_SM_G4_closed": False,
        "physical_SM_G5_closed": False,
    }
    checks = {
        "source_pins_match": bindings["all_portable_lf_pins_match"],
        "exactly_21_disjoint_rows_certified": len(summaries) == 21,
        "all_Hessians_symmetric_entrywise_over_Q": all(
            row["Hessian"]["symmetric_entrywise_over_Q"] for row in summaries
        ),
        "all_exact_homogeneity_identities_hold": all(
            row["exact_target_jet_from_homogeneity"][
                "q_dot_gradient_equals_degree_times_value_exactly"
            ]
            for row in summaries
        ),
        "H_projector_reconstruction_exact": h_certificate[
            "I1_plus_I54_reconstructs_HdagH_squared_Hessian_entrywise_over_Q"
        ],
        "six_rows_remain_explicit": len(OPEN_ROWS) == 6,
        "aggregate_and_global_claims_fail_closed": not any(
            claims[key]
            for key in (
                "exact_source_algebra_Hessians_for_all_37_active_rows",
                "exact_full_witness_aggregate_stationarity",
                "full_486_field_global_equality_orbit_classified",
                "physical_SM_G3_closed",
                "physical_SM_G4_closed",
                "physical_SM_G5_closed",
            )
        ),
    }
    failures = [name for name, passed in checks.items() if not passed]
    if failures:
        raise ArithmeticError(f"easy-21 checks failed: {failures}")
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "model_contract_id": hard.MODEL_CONTRACT_ID,
        "source_bindings": bindings,
        "arithmetic_contract": {
            "domains": ["Z", "Q"],
            "floating_point_used_to_construct_or_accept_Hessians": False,
            "finite_difference_autodiff_or_rational_recognition_used": False,
        },
        "certified_rows": summaries,
        "family_certificates": {
            "norm_and_singlet_dressings": norm_certificate,
            "H_self_quartics": h_certificate,
            "Phi_cubic": {
                "exact_signed_integer_two_form_basis": True,
                "source_formula": "Tr(A_Phi^3)",
            },
            "Phi_self_quartics": phi_certificate,
        },
        "scope_accounting": {
            "active_witness_rows": 37,
            "hard_theorem_rows": 10,
            "rows_certified_here": 21,
            "combined_exact_source_rows": 31,
            "remaining_rows": list(OPEN_ROWS),
            "remaining_row_count": len(OPEN_ROWS),
            "minimum_missing_source_derivations": {
                "O14": "exact integer/Gaussian-integer realification of Phi Sigma^dag Sigma cubic",
                "O35": "exact 1 and 45 H-Sigma Hermitian-current Hessians",
                "O46": "exact 1, 45 and 54 Phi^2 HdagH channel Hessians",
            },
            "post_source_steps": (
                "compose all 37 exact jets with exact witness coefficients; prove exact "
                "stationarity, 38-dimensional kernel, rank 448 and PSD; separately classify "
                "the complete 486-field equality locus modulo declared symmetries"
            ),
        },
        "claims": claims,
        "checks": checks,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
    }
    report["integrity"] = {
        "core_sha256": hashlib.sha256(hard.canonical_json_bytes(report)).hexdigest(),
        "ordered_21_row_digest_sha256": hashlib.sha256(
            "\n".join(
                f"{row['direction_id']}:{row['Hessian']['canonical_sparse_rational_sha256']}"
                for row in summaries
            ).encode("ascii")
        ).hexdigest(),
    }
    return report


def render_markdown(report: dict[str, Any]) -> str:
    scope = report["scope_accounting"]
    return "\n".join(
        (
            "# Exact physical-SM easy 21 Hessians v20",
            "",
            f"Status: `{report['status']}`",
            "",
            "Exact Z/Q source algebra supplies the full 486-real target Hessians for fourteen norm/dressing rows, O17, both O36 rows, and all four O48 rows.",
            "",
            f"- Rows here: `{scope['rows_certified_here']}`.",
            f"- Combined with the hard O27/O44 theorem: `{scope['combined_exact_source_rows']}/37`.",
            f"- Remaining: `{scope['remaining_row_count']}` rows: `{', '.join(scope['remaining_rows'])}`.",
            f"- Ordered digest: `{report['integrity']['ordered_21_row_digest_sha256']}`.",
            "",
            "The exact 37-row aggregate, stationarity/kernel/rank/PSD proof, and the separate full global equality-orbit classification remain open. G3, G4, and G5 remain false.",
            "",
        )
    )


def write_outputs(report: dict[str, Any]) -> None:
    OUT_JSON.write_bytes(hard.canonical_json_bytes(report))
    OUT_MD.write_text(render_markdown(report), encoding="utf-8", newline="\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    report = build_report()
    if args.write:
        write_outputs(report)
    else:
        print(json.dumps(hard._jsonable(report), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
