#!/usr/bin/env python3
"""Exact all-37 source aggregate at the physical-SM target.

The hard-10, easy-21 and last-six source theorems provide every active row's
complete 486-real target Hessian over Q.  This module weights those exact rows
by the frozen rational witness and proves, without rational recognition or a
floating-point acceptance test:

* the exact aggregate value is -1 and gradient is zero;
* the exact source aggregate is entrywise identical to the historical
  reconstructed-rational matrix (same canonical sparse serialization);
* all 47 declared generator columns annihilate the Hessian and their tangent
  span has exact dimension 38;
* a nonzero rank-448 modular minor proves rank 448, hence the kernel is exactly
  the symmetry tangent span;
* a fraction-free exact symmetric Bareiss/LDL elimination on that 448x448
  principal minor has 448 strictly positive pivots.  The minor is positive
  definite, so the full symmetric rank-448 Hessian is positive semidefinite.

This closes the source-bound local stationary Hessian problem.  It does not
classify the global equality locus in all 486 fields and therefore does not,
by itself, close physical G3, G4, or G5.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

import numpy as np

import exact_physical_sm_easy_21_hessians_v20 as easy
import exact_physical_sm_hard_projector_hessians_v20 as hard
import exact_physical_sm_last_six_hessians_v20 as last
import physical_sm_vacuum_local_feasibility_v20 as foundation


ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_PHYSICAL_SM_37_ROW_AGGREGATE_V20.json"
OUT_MD = ROOT / "EXACT_PHYSICAL_SM_37_ROW_AGGREGATE_V20.md"
SCHEMA = "exact_physical_sm_37_row_aggregate_v20"
STATUS = "EXACT_ALL_37_SOURCE_AGGREGATE_STATIONARY_KERNEL_RANK_PSD__GLOBAL_EQUALITY_ORBIT_OPEN"
FIELD_DIMENSION = 486
TARGET_DENOMINATOR = 20
AGGREGATE_DENOMINATOR = 6_300_103_327_590
EXPECTED_SPARSE_SHA256 = "58e39ea9a982ac71fd696de93d8d8bc51dd1e153399bfa6f7cbcc368fc6b7458"
EXPECTED_PIVOT_HASH_CHAIN = "58b41d4c2be5fbc31b0ada79b653e84561e0db629a3d600053d44d760824c259"

SOURCE_HASHES = {
    "exact_physical_sm_hard_projector_hessians_v20.py": "2ac49af04f3bbec17a4e616c82898de6a0710ddcfa3462d7ec8d59dad69de27e",
    "exact_physical_sm_easy_21_hessians_v20.py": "e8b6fcf9bc459ee4c05a74d41cae6d9a82680de88683ba5ffcc4ceb30fe73311",
    "exact_physical_sm_last_six_hessians_v20.py": "78d712d3573ec3377a331eb52dbf429452aa1c7ed82aeb7eeb0aa5900b3774ce",
    "EXACT_PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_V20.json": "b8a498926d1ba6a7f07f9c64b56443a14fba098514a8d5cb3e8358bbf7baabfa",
    "EXACT_PHYSICAL_SM_EASY_21_HESSIANS_V20.json": "bea6bb1b519eb42a610b6a0c66a6b7178e4f1f912aa154035aacecc815089ae8",
    "EXACT_PHYSICAL_SM_LAST_SIX_HESSIANS_V20.json": "fe1a92c3bc8e809c41abb88a85f3cf0198c88f7a70482b3f26359d6df78907c5",
    "physical_sm_vacuum_local_feasibility_v20.py": "629ea8c45f101f82b6b4e963fd1fb19dcc5735fe52a1d8efb1fb0812dbaa565c",
    "PHYSICAL_SM_VACUUM_LOCAL_FEASIBILITY_V20.json": "ac575067550472afeae1d87503c04a47bf27386223a4417cf7c2341ad75af315",
}

WITNESS_COEFFICIENTS = {
    "O03_B01_singlet_polynomial": "-89207490960/210003444253",
    "O04_B01_singlet_polynomial": "-7826687400/210003444253",
    "O05_B01_126bar_norm": "11015601260/210003444253",
    "O06_B01_Hdag_H_norm": "-153934744950/210003444253",
    "O07_B01_Phi_norm": "-1107212577224/1050017221265",
    "O14_B01_Phi_Sigma_Sigmadag_cubic": "-4483045420/210003444253",
    "O17_B01_Phi_cubic": "588000/210003444253",
    "O20_B01_singlet_polynomial": "26520070500/210003444253",
    "O22_B01_singlet_polynomial": "-471540300/210003444253",
    "O23_B01_singlet_polynomial": "262509061500/210003444253",
    "O25_B01_126bar_norm": "-1177316700/210003444253",
    "O26_B01_126bar_norm": "121684500/210003444253",
    "O27_B01_126bar_self_projectors": "4200/210003444253",
    "O27_B02_126bar_self_projectors": "8241555000/210003444253",
    "O27_B03_126bar_self_projectors": "263008662000/210003444253",
    "O27_B04_126bar_self_projectors": "1050508662000/210003444253",
    "O33_B01_Hdag_H_norm": "45394307700/210003444253",
    "O34_B01_Hdag_H_norm": "-903665700/210003444253",
    "O35_B01_H_Sigma_hermitian": "16325379000/210003444253",
    "O35_B02_H_Sigma_hermitian": "-20192346300/210003444253",
    "O36_B01_H_self_quartics": "90370188300/210003444253",
    "O36_B02_H_self_quartics": "39889411800/210003444253",
    "O42_B01_Phi_norm": "17326089900/210003444253",
    "O43_B01_Phi_norm": "-1536672900/210003444253",
    "O44_B01_Phi2_Sigma_projectors": "5851780200/210003444253",
    "O44_B02_Phi2_Sigma_projectors": "1287057800/210003444253",
    "O44_B03_Phi2_Sigma_projectors": "69872371800/210003444253",
    "O44_B04_Phi2_Sigma_projectors": "37366736400/210003444253",
    "O44_B05_Phi2_Sigma_projectors": "-74559424800/210003444253",
    "O44_B06_Phi2_Sigma_projectors": "-39819378900/210003444253",
    "O46_B01_Phi2_HdagH_channels": "57854223000/210003444253",
    "O46_B02_Phi2_HdagH_channels": "-32388300/210003444253",
    "O46_B03_Phi2_HdagH_channels": "-10500071400/210003444253",
    "O48_B01_Phi_self_quartics": "47581800/210003444253",
    "O48_B02_Phi_self_quartics": "173733000/210003444253",
    "O48_B03_Phi_self_quartics": "-2747637900/210003444253",
    "O48_B04_Phi_self_quartics": "170068500/210003444253",
}

ROW_DEGREES = {
    **{row: 2 * len(factors) for row, factors in easy.NORM_ROW_FACTORS.items()},
    "O17_B01_Phi_cubic": 3,
    **{row: 4 for row in easy.H_SELF_ROWS},
    **{row: 4 for row in easy.PHI_SELF_ROWS},
    **{row: degree for row, (_family, _label, degree) in last.ROWS.items()},
    **{row: 4 for row in hard.O27_CHANNEL_TO_ROW.values()},
    **{row: 4 for row in hard.O44_CHANNEL_TO_ROW.values()},
}


def _portable_lf_sha256(path: Path) -> str:
    payload = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(payload).hexdigest()


def source_bindings() -> dict[str, Any]:
    rows = {}
    for name, expected in SOURCE_HASHES.items():
        observed = _portable_lf_sha256(ROOT / name)
        if observed != expected:
            raise ArithmeticError(f"all-37 aggregate dependency drifted: {name}")
        rows[name] = {"portable_lf_sha256": observed, "matches": True}
    return {"files": rows, "all_portable_lf_pins_match": True}


@lru_cache(maxsize=1)
def exact_source_rows() -> dict[str, hard.RationalHessian]:
    target = foundation.integer_target_vector()
    o27, _ = hard.exact_o27_hessians()
    o44, _ = hard.exact_o44_hessians()
    rows = {hard.O27_CHANNEL_TO_ROW[channel]: matrix for channel, matrix in o27.items()}
    rows.update({hard.O44_CHANNEL_TO_ROW[channel]: matrix for channel, matrix in o44.items()})
    easy_rows: dict[str, hard.RationalHessian] = {}
    easy_rows.update(easy.exact_norm_rows(target)[0])
    easy_rows["O17_B01_Phi_cubic"] = easy.exact_phi_cubic(target)
    easy_rows.update(easy.exact_h_self_rows(target)[0])
    easy_rows.update(easy.exact_phi_self_rows(target)[0])
    rows.update(easy_rows)
    rows.update(last.exact_rows()[0])
    if set(rows) != set(WITNESS_COEFFICIENTS) or set(rows) != set(ROW_DEGREES):
        raise ArithmeticError("all-37 exact row inventory does not match witness")
    return rows


@lru_cache(maxsize=1)
def exact_aggregate() -> tuple[hard.RationalHessian, dict[str, Any]]:
    rows = exact_source_rows()
    coefficients = {key: Fraction(value) for key, value in WITNESS_COEFFICIENTS.items()}
    terms = ((coefficients[key], rows[key]) for key in sorted(rows))
    aggregate = easy._combine(terms)
    if aggregate.denominator != AGGREGATE_DENOMINATOR:
        raise ArithmeticError("aggregate denominator drifted")
    serialization = "".join(
        f"{first},{second},{value},0\n"
        for (first, second), value in sorted(aggregate.fraction_entries().items())
    ).encode("ascii")
    source_sha = hashlib.sha256(serialization).hexdigest()
    if source_sha != EXPECTED_SPARSE_SHA256:
        raise ArithmeticError("source-derived aggregate sparse SHA drifted")
    return aggregate, {
        "active_row_count": len(rows),
        "nonzero_entries": int(np.count_nonzero(aggregate.numerator)),
        "denominator": aggregate.denominator,
        "maximum_abs_numerator": int(np.max(np.abs(aggregate.numerator), initial=0)),
        "canonical_sparse_Q_sqrt2_serialization_sha256": source_sha,
        "expected_historical_reconstructed_sparse_sha256": EXPECTED_SPARSE_SHA256,
        "entrywise_identity_to_historical_reconstructed_rational_aggregate": source_sha == EXPECTED_SPARSE_SHA256,
    }


def exact_stationarity(aggregate: hard.RationalHessian) -> dict[str, Any]:
    target = foundation.integer_target_vector()
    gradient: list[Fraction] = [Fraction(0) for _ in range(FIELD_DIMENSION)]
    value = Fraction(0)
    per_row_values = {}
    rows = exact_source_rows()
    for direction_id, matrix in rows.items():
        degree = ROW_DEGREES[direction_id]
        product = matrix.numerator @ target
        row_gradient_denominator = matrix.denominator * TARGET_DENOMINATOR * (degree - 1)
        coefficient = Fraction(WITNESS_COEFFICIENTS[direction_id])
        for index, item in enumerate(product):
            if item:
                gradient[index] += coefficient * Fraction(int(item), row_gradient_denominator)
        row_value = Fraction(
            int(target @ product),
            matrix.denominator * TARGET_DENOMINATOR**2 * degree * (degree - 1),
        )
        per_row_values[direction_id] = str(row_value)
        value += coefficient * row_value
    zero_indices = [index for index, item in enumerate(gradient) if item]
    if zero_indices or value != -1:
        raise ArithmeticError("exact source aggregate is not stationary with V=-1")
    # A separate consistency identity checks the aggregate Hq against the
    # degree-weighted source gradients; mixed degrees prevent using one Euler factor.
    aggregate_product = aggregate.numerator @ target
    source_hq = [Fraction(0) for _ in range(FIELD_DIMENSION)]
    for direction_id, matrix in rows.items():
        coefficient = Fraction(WITNESS_COEFFICIENTS[direction_id])
        product = matrix.numerator @ target
        for index, item in enumerate(product):
            if item:
                source_hq[index] += coefficient * Fraction(
                    int(item), matrix.denominator * TARGET_DENOMINATOR
                )
    aggregate_hq = [
        Fraction(int(item), aggregate.denominator * TARGET_DENOMINATOR)
        for item in aggregate_product
    ]
    return {
        "exact_potential_value": str(value),
        "exact_gradient_nonzero_entries": len(zero_indices),
        "exact_gradient_is_zero": not zero_indices,
        "aggregate_Hq_matches_weighted_source_Hq_entrywise": aggregate_hq == source_hq,
        "construction": "row gradients and values recovered exactly from each homogeneous source Hessian via Hq=(d-1)grad and q.grad=dV",
        "per_row_exact_target_values": per_row_values,
    }


def _fraction_mod(value: Fraction, prime: int) -> int:
    return value.numerator % prime * pow(value.denominator % prime, -1, prime) % prime


def _determinant_mod_prime(matrix: np.ndarray, prime: int) -> int:
    work = np.asarray(matrix, dtype=np.int64).copy() % prime
    determinant = 1
    for column in range(work.shape[0]):
        candidates = np.flatnonzero(work[column:, column])
        if not candidates.size:
            return 0
        selected = column + int(candidates[0])
        if selected != column:
            work[[column, selected]] = work[[selected, column]]
            determinant = -determinant
        pivot = int(work[column, column])
        determinant = determinant * pivot % prime
        work[column] = work[column] * pow(pivot, -1, prime) % prime
        below = np.flatnonzero(work[column + 1 :, column]) + column + 1
        if below.size:
            work[below] = (
                work[below] - work[below, column, None] * work[column, None, :]
            ) % prime
    return determinant % prime


def _modular_rank_and_minor(
    aggregate: hard.RationalHessian, prime: int = 1009
) -> tuple[dict[str, Any], tuple[int, ...]]:
    work = np.asarray(aggregate.numerator % prime, dtype=np.int64)
    original = work.copy()
    origins = np.arange(FIELD_DIMENSION)
    pivot_rows: list[int] = []
    pivot_columns: list[int] = []
    rank = 0
    for column in range(FIELD_DIMENSION):
        candidates = np.flatnonzero(work[rank:, column])
        if not candidates.size:
            continue
        selected = rank + int(candidates[0])
        if selected != rank:
            work[[rank, selected]] = work[[selected, rank]]
            origins[[rank, selected]] = origins[[selected, rank]]
        pivot = int(work[rank, column])
        work[rank] = work[rank] * pow(pivot, -1, prime) % prime
        below = np.flatnonzero(work[rank + 1 :, column]) + rank + 1
        if below.size:
            work[below] = (
                work[below] - work[below, column, None] * work[rank, None, :]
            ) % prime
        pivot_rows.append(int(origins[rank]))
        pivot_columns.append(column)
        rank += 1
        if rank == FIELD_DIMENSION:
            break
    if tuple(pivot_rows) != tuple(pivot_columns):
        raise ArithmeticError("modular rank pivot is not the required principal minor")
    minor = original[np.ix_(pivot_rows, pivot_columns)]
    determinant = _determinant_mod_prime(minor, prime)
    return {
        "prime": prime,
        "rank": rank,
        "principal_pivot_indices": pivot_rows,
        "principal_minor_determinant_mod_prime": determinant,
        "principal_minor_is_nonzero": determinant != 0,
    }, tuple(pivot_rows)


def exact_kernel_and_rank(
    aggregate: hard.RationalHessian,
) -> tuple[dict[str, Any], tuple[int, ...]]:
    tangents = np.asarray(foundation.exact_integer_tangent_matrix(), dtype=object)
    image = aggregate.numerator.astype(object) @ tangents
    columns_annihilated = [not any(image[:, column]) for column in range(image.shape[1])]
    symmetry = foundation.exact_symmetry_certificate()
    exact_tangent_rank = symmetry["orbits"]["SO10_x_U1X_x_PQ"]["exact_rank"]
    modular, pivots = _modular_rank_and_minor(aggregate)
    rank = 448 if all(columns_annihilated) and exact_tangent_rank == 38 and modular["rank"] == 448 else None
    if rank != 448:
        raise ArithmeticError("exact source aggregate rank/kernel proof failed")
    return {
        "exact_generator_column_count": tangents.shape[1],
        "all_47_generator_columns_annihilated_entrywise": all(columns_annihilated),
        "annihilated_generator_columns": sum(columns_annihilated),
        "exact_symmetry_tangent_span_dimension": exact_tangent_rank,
        "rank_upper_bound_from_38_kernel_vectors": 448,
        "modular_lower_bound_certificate": modular,
        "exact_rank": rank,
        "exact_nullity": FIELD_DIMENSION - rank,
        "kernel_equals_exact_symmetry_tangent_span": rank == 448 and exact_tangent_rank == 38,
    }, pivots


def exact_positive_principal_minor(
    aggregate: hard.RationalHessian, pivots: tuple[int, ...]
) -> dict[str, Any]:
    # Bareiss symmetric elimination: at step k the pivot equals the k+1
    # leading principal determinant (up to positive inherited factors).  The
    # exact recurrence uses only divisible integer operations.
    sys.set_int_max_str_digits(max(sys.get_int_max_str_digits(), 100_000))
    matrix = aggregate.numerator.astype(object)[np.ix_(pivots, pivots)].copy()
    previous = 1
    pivot_hashes: list[str] = []
    minimum_sign = 1
    divisibility_checks = 0
    final_pivot = 0
    for index in range(len(pivots)):
        pivot = int(matrix[index, index])
        final_pivot = pivot
        minimum_sign = min(minimum_sign, 1 if pivot > 0 else 0 if pivot == 0 else -1)
        if pivot <= 0:
            raise ArithmeticError(f"exact LDL/Bareiss pivot {index} is not positive")
        pivot_hashes.append(hashlib.sha256(str(pivot).encode("ascii")).hexdigest())
        if index + 1 < len(pivots):
            column = matrix[index + 1 :, index].copy()
            numerator = pivot * matrix[index + 1 :, index + 1 :] - np.outer(column, column)
            if previous != 1:
                for value in numerator.flat:
                    divisibility_checks += 1
                    if int(value) % previous:
                        raise ArithmeticError("fraction-free LDL division is not exact")
                numerator = numerator // previous
            matrix[index + 1 :, index + 1 :] = numerator
        previous = pivot
    chain = hashlib.sha256(("\n".join(pivot_hashes) + "\n").encode("ascii")).hexdigest()
    if chain != EXPECTED_PIVOT_HASH_CHAIN:
        raise ArithmeticError("exact positive-pivot hash chain drifted")
    return {
        "method": "fraction-free symmetric Bareiss/LDL on the rank-448 principal minor",
        "principal_minor_dimension": len(pivots),
        "strictly_positive_exact_pivot_count": len(pivot_hashes),
        "all_exact_pivots_strictly_positive": minimum_sign == 1,
        "exact_divisibility_checks": divisibility_checks,
        "positive_pivot_sha256_chain": chain,
        "expected_positive_pivot_sha256_chain": EXPECTED_PIVOT_HASH_CHAIN,
        "final_pivot_decimal_digit_count": len(str(abs(final_pivot))),
        "final_pivot_sha256": pivot_hashes[-1],
        "principal_minor_is_positive_definite_by_Sylvester": minimum_sign == 1,
        "full_Hessian_is_PSD_logic": "the symmetric 486x486 Hessian has exact rank 448 and contains an exact positive-definite 448x448 principal submatrix; Cauchy interlacing gives at least 448 positive eigenvalues and rank leaves the other 38 exactly zero",
        "full_Hessian_is_positive_semidefinite": minimum_sign == 1,
        "full_Hessian_is_positive_definite_mod_kernel": minimum_sign == 1,
    }


@lru_cache(maxsize=1)
def build_report() -> dict[str, Any]:
    bindings = source_bindings()
    aggregate, assembly = exact_aggregate()
    stationarity = exact_stationarity(aggregate)
    kernel_rank, pivots = exact_kernel_and_rank(aggregate)
    positivity = exact_positive_principal_minor(aggregate, pivots)
    claims = {
        "all_37_active_Hessians_derived_from_exact_source_algebra": True,
        "exact_source_aggregate_value_minus_one_and_stationary": True,
        "exact_source_aggregate_kernel_is_38_dimensional_symmetry_span": True,
        "exact_source_aggregate_rank_is_448": True,
        "exact_source_aggregate_is_PSD_and_strictly_positive_mod_symmetry": True,
        "full_486_field_global_equality_orbit_classified": False,
        "physical_SM_G3_closed": False,
        "physical_SM_G4_closed": False,
        "physical_SM_G5_closed": False,
    }
    checks = {
        "source_pins_match": bindings["all_portable_lf_pins_match"],
        "all_37_rows_present": assembly["active_row_count"] == 37,
        "source_aggregate_matches_historical_reconstruction_entrywise": assembly[
            "entrywise_identity_to_historical_reconstructed_rational_aggregate"
        ],
        "exact_value_and_stationarity": stationarity["exact_potential_value"] == "-1"
        and stationarity["exact_gradient_is_zero"],
        "exact_source_Hq_consistency": stationarity[
            "aggregate_Hq_matches_weighted_source_Hq_entrywise"
        ],
        "all_generator_columns_annihilated": kernel_rank[
            "all_47_generator_columns_annihilated_entrywise"
        ],
        "exact_rank_and_kernel": kernel_rank["exact_rank"] == 448
        and kernel_rank["kernel_equals_exact_symmetry_tangent_span"],
        "exact_PSD": positivity["full_Hessian_is_positive_semidefinite"],
        "global_equality_and_G3_G4_G5_fail_closed": not any(
            claims[key]
            for key in (
                "full_486_field_global_equality_orbit_classified",
                "physical_SM_G3_closed",
                "physical_SM_G4_closed",
                "physical_SM_G5_closed",
            )
        ),
    }
    failures = [key for key, value in checks.items() if not value]
    if failures:
        raise ArithmeticError(f"all-37 aggregate checks failed: {failures}")
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "model_contract_id": hard.MODEL_CONTRACT_ID,
        "source_bindings": bindings,
        "arithmetic_contract": {
            "domains": ["Z", "Gaussian integers Z[i]", "Q"],
            "floating_point_used_to_construct_or_accept_any_claim": False,
            "finite_difference_autodiff_or_rational_recognition_used": False,
        },
        "witness": {
            "coefficient_count": len(WITNESS_COEFFICIENTS),
            "exact_rational_coefficients": WITNESS_COEFFICIENTS,
            "row_homogeneous_degrees": ROW_DEGREES,
        },
        "source_aggregate_assembly": assembly,
        "exact_stationarity": stationarity,
        "exact_kernel_and_rank": kernel_rank,
        "exact_PSD_certificate": positivity,
        "scope_boundary": {
            "source_bound_local_stationary_Hessian_problem_complete": True,
            "global_equality_orbit_classification_complete": False,
            "remaining_derivation": "classify every full 486-field equality/zero point of the selected globally nonnegative completion modulo SO(10) x U(1)_X x PQ and discrete exact symmetries",
            "reason_local_PSD_does_not_imply_global_equality_uniqueness": "the Hessian controls only a neighborhood of the target orbit; disconnected or nonlocal equality components require a global polynomial-ideal/SOS classification",
        },
        "claims": claims,
        "checks": checks,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
    }
    report["integrity"] = {
        "core_sha256": hashlib.sha256(hard.canonical_json_bytes(report)).hexdigest(),
        "aggregate_sparse_sha256": assembly["canonical_sparse_Q_sqrt2_serialization_sha256"],
        "positive_pivot_hash_chain": positivity["positive_pivot_sha256_chain"],
    }
    return report


def render_markdown(report: dict[str, Any]) -> str:
    assembly = report["source_aggregate_assembly"]
    rank = report["exact_kernel_and_rank"]
    psd = report["exact_PSD_certificate"]
    return "\n".join(
        (
            "# Exact physical-SM 37-row aggregate v20",
            "",
            f"Status: `{report['status']}`",
            "",
            "All 37 active source Hessians are assembled with the exact rational witness. The target has exact V=-1 and zero gradient. The 486x486 aggregate is exactly symmetric, has the 38-dimensional symmetry tangent span as its full kernel, rank 448, and is PSD with strict positivity on the quotient.",
            "",
            f"- Nonzero aggregate entries: `{assembly['nonzero_entries']}`.",
            f"- Sparse exact-Q SHA: `{assembly['canonical_sparse_Q_sqrt2_serialization_sha256']}`.",
            f"- Exact rank/nullity: `{rank['exact_rank']}/{rank['exact_nullity']}`.",
            f"- Exact positive pivots: `{psd['strictly_positive_exact_pivot_count']}`.",
            f"- Positive-pivot hash chain: `{psd['positive_pivot_sha256_chain']}`.",
            "",
            "This closes the source-bound local stationary Hessian problem. The full 486-field global equality-orbit classification remains separate and open, so this artifact does not claim physical G3, G4, or G5 closed.",
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
