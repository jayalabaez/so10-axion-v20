#!/usr/bin/env python3
"""Fail-closed theorem bridge for the corrected fixed SU(4) endpoint.

The bridge combines three logically separate exact certificates: exhaustive
carrier/map plus physical-RHS reconstruction, exact affine/strict-PD Gram
verification, and a direct live-polynomial regression.  It proves only the
fixed H=h_- and Sigma=q/4 endpoint for arbitrary real Phi.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
import exact_gauged_u1x_g3_rank1_su4_corrected_positive_gram_primal_v21 as primal
if Path(primal.__file__).resolve() != (
    HERE / "exact_gauged_u1x_g3_rank1_su4_corrected_positive_gram_primal_v21.py"
).resolve():
    raise ImportError("runtime primal module escaped HERE")


SOURCE_REPORT = HERE / (
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_SOURCE_RECONSTRUCTION_V21.json"
)
EXACT_VERIFY_REPORT = HERE / (
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_POSITIVE_GRAM_VERIFY_V21.json"
)
LIVE_REPORT = HERE / (
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_LIVE_POLYNOMIAL_V21.json"
)
OVERFLOW_REPORT = HERE / (
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_ORDERED_SPECTRAL_OVERFLOW_V21.json"
)
OUTPUT = HERE / (
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_FIXED_ENDPOINT_THEOREM_V21.json"
)

EXPECTED_REPORT_RAW_SHA256 = {
    SOURCE_REPORT.name: "f0704cdd5199eadfdebc2cb916b353b3ee1000589ccbd480cc78883e8731b108",
    EXACT_VERIFY_REPORT.name: "b7cf3296b16176b2bf5e84fa39e0ba78d72f7f1740e046ce7665f33b3d18c49c",
    LIVE_REPORT.name: "2eab2223c9782535764485ad5d90898a8b90a7a97b2e4d714819acd06cd1a964",
    OVERFLOW_REPORT.name: "db332026626cdea336005c0630e06d4c128f0436b9a2a96a4eeed8e9f96495f2",
}
EXPECTED_MAP_SHA256 = primal.EXPECTED_MAP_NUMERATOR_CSR_SHA256
EXPECTED_TARGET_SHA256 = primal.EXPECTED_TARGET_NUMERATOR_SHA256
EXPECTED_COORDINATE_SHA256 = primal.EXPECTED_COORDINATE_SHA256
EXPECTED_LDL_SHA256 = primal.EXPECTED_LDL_PIVOT_SHA256
STATUS = "EXACT_RANK1_SU4_CORRECTED_FIXED_ENDPOINT_THEOREM_V21_PASS"


def raw_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_pinned(path: Path) -> dict[str, Any]:
    if path.resolve().parent != HERE.resolve():
        raise ArithmeticError("theorem input escaped HERE")
    expected = EXPECTED_REPORT_RAW_SHA256.get(path.name)
    if expected is None or raw_sha256(path) != expected:
        raise ArithmeticError(f"theorem input bytes drifted: {path.name}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ArithmeticError(f"theorem input is not an object: {path.name}")
    return value


def _validate_source(report: Mapping[str, Any]) -> None:
    carriers = report.get("carrier_exhaustion", {})
    coefficient_map = report.get("map", {})
    rhs = report.get("physical_RHS", {})
    boundary = report.get("generation_boundary", {})
    if not (
        report.get("status")
        == "EXACT_RANK1_SU4_CORRECTED_SOURCE_RECONSTRUCTION_V21_PASS"
        and carriers.get("augmented_linear_dimension") == 211
        and carriers.get("complete_real_carrier_dimension") == 22_366
        and carriers.get("complete_real_carrier_dimension_formula") == "211*212/2"
        and carriers.get("complex_isotypic_type_count") == 35
        and carriers.get("irreducible_carrier_copy_count") == 824
        and carriers.get("isotypic_block_count") == 22
        and carriers.get("carrier_transform_square_shape") == [22_366, 22_366]
        and carriers.get("carrier_transform_invertible_exact") is True
        and carriers.get("constant_t_squared_carrier_present_exact") is True
        and carriers.get("all_carrier_families_exhausted_exact") is True
        and carriers.get(
            "all_standard_columns_reconstructed_from_rank_one_positive_component_metrics"
        )
        is True
        and carriers.get("Schur_coordinate_count") == 19_594
        and carriers.get("Schur_coordinate_grade_counts")
        == [1, 4, 90, 1414, 18_085]
    ):
        raise ArithmeticError("carrier exhaustion/invertibility evidence drifted")
    grade_blocks = coefficient_map.get("grade_blocks")
    if not (
        coefficient_map.get("shape") == [6_585, 19_594]
        and coefficient_map.get("common_denominator") == 256
        and coefficient_map.get("nnz") == 138_550
        and coefficient_map.get("numerator_csr_sha256") == EXPECTED_MAP_SHA256
        and coefficient_map.get("full_column_reconstruction_count") == 19_594
        and coefficient_map.get("all_grade_ranks_surjective_at_primes_1000003_1000033")
        is True
        and [row.get("rank") for row in grade_blocks]
        == [1, 4, 45, 478, 6_057]
        and coefficient_map.get("complex_quartic_identity_columns_checked_exact")
        == 10_788
        and coefficient_map.get("complex_quartic_identity_mismatch_nnz") == 0
        and len(coefficient_map.get("corrected_grade01_changes", ())) == 4
        and "divided by 16" in coefficient_map.get("grade01_formula", "")
    ):
        raise ArithmeticError("exhaustive corrected carrier-map evidence drifted")
    if not (
        rhs.get("quartic_row_count") == 6_057
        and rhs.get("row_by_row_direct_evaluator_mismatch_count") == 0
        and rhs.get("ordered_spectral_quartic_common_denominator") == 1_125
        and rhs.get("ordered_spectral_quartic_numerator_sha256")
        == "9460ddb239c7af45124396b469d5d633a82d46b72b16427809f3cca4cc39dff4"
        and rhs.get("common_denominator") == 576_000
        and rhs.get("numerator_sha256") == EXPECTED_TARGET_SHA256
        and rhs.get("full_grade_lengths") == [1, 4, 45, 478, 6_057]
        and rhs.get("first_quartic_value_correct") == "27776/1125"
        and rhs.get("first_quartic_value_rejected_raw_schur") == "129568/3375"
    ):
        raise ArithmeticError("ordered-spectral physical-RHS evidence drifted")
    if not (
        boundary.get("prior_assembled_map_read") is False
        and boundary.get("prior_primal_certificate_read") is False
        and boundary.get("v20_physical_target_payload_read") is False
        and boundary.get("heavy_reconstruction_is_explicit_once_only") is True
    ):
        raise ArithmeticError("source reconstruction boundary drifted")


def _validate_exact_verify(report: Mapping[str, Any]) -> None:
    if not (
        report.get("status")
        == "EXACT_RANK1_SU4_CORRECTED_POSITIVE_GRAM_PRIMAL_V21_INDEPENDENT_VERIFY_PASS"
        and report.get("certificate_raw_sha256")
        == primal.EXPECTED_CERTIFICATE_RAW_SHA256
        and report.get("corrected_system_raw_sha256")
        == primal.EXPECTED_SYSTEM_RAW_SHA256
        and report.get("coefficient_map_numerator_csr_sha256")
        == EXPECTED_MAP_SHA256
        and report.get("target_numerator_int64_sha256") == EXPECTED_TARGET_SHA256
        and report.get("exact_coordinate_sha256") == EXPECTED_COORDINATE_SHA256
        and report.get("exact_LDL_pivot_sha256") == EXPECTED_LDL_SHA256
        and report.get("exact_coefficient_equalities_verified") == 6_585
        and report.get("exact_rational_coordinates_verified") == 19_594
        and report.get("strictly_positive_Gram_blocks_verified") == 22
        and len(report.get("block_diagnostics", ())) == 22
        and sum(
            int(row.get("positive_leading_principal_minor_count", -1))
            for row in report.get("block_diagnostics", ())
        )
        == 824
        and all(
            row.get("all_leading_principal_minors_strictly_positive") is True
            for row in report.get("block_diagnostics", ())
        )
    ):
        raise ArithmeticError("independent exact primal verification drifted")


def _validate_live(report: Mapping[str, Any]) -> None:
    expected_target = [
        "237/200",
        "-3183/10000",
        "-753023067/400000000",
        "0",
        "3063315748321207/3000000000000000",
    ]
    if not (
        report.get("status") == "EXACT_RANK1_SU4_CORRECTED_LIVE_POLYNOMIAL_V21_PASS"
        and report.get("source_raw_sha256")
        == "9e37096cb1d6a967ed739f459437e6796dc9d8340e32f6a2c1a59bcbee7a36cd"
        and report.get("certificate_raw_sha256")
        == primal.EXPECTED_CERTIFICATE_RAW_SHA256
        and report.get("reserve_subtracted_from_grade_zero") == "3/200"
        and report.get("reserve_changes_only_grade_zero_exact") is True
        and report.get("live_endpoint_target_A_minus_3_over_200_by_grade")
        == expected_target
        and report.get("direct_positive_carrier_norm_by_grade") == expected_target
        and report.get("exact_residual_by_grade") == ["0", "0", "0", "0", "0"]
        and report.get("target_and_carrier_total")
        == "15742745821207/3000000000000000"
        and len(report.get("block_contributions", ())) == 22
        and report.get("generation_boundary", {}).get("target_payload_read") is False
        and report.get("generation_boundary", {}).get(
            "runtime_relocation_claimed_by_this_source"
        )
        is False
        and report.get("exact_arithmetic_safety", {}).get(
            "physical_path_exceeds_signed_int64"
        )
        is True
        and report.get("exact_arithmetic_safety", {}).get(
            "fixed_width_physical_contraction_used"
        )
        is False
        and report.get("claim_boundary", {}).get(
            "complete_polynomial_identity_proved_by_this_regression"
        )
        is False
    ):
        raise ArithmeticError("direct live-polynomial regression drifted")


def _validate_overflow(report: Mapping[str, Any]) -> None:
    coarse = report.get("coarse_SU3_witness", {})
    sharp = report.get("sharp_SU3_witness", {})
    if not (
        report.get("status")
        == "EXACT_RANK1_SU4_CORRECTED_ORDERED_SPECTRAL_OVERFLOW_V21_PASS"
        and coarse.get("coordinate_numerators")
        == [-639, 1160, 1023, -909, 0, 0, 0, 0]
        and coarse.get("coordinate_denominator") == 1_000
        and coarse.get("raw_spectral_contraction_numerator")
        == "225852143492225949696"
        and coarse.get("raw_spectral_contraction_abs_bit_length") == 68
        and coarse.get("direct_ordered_spectral_quartic")
        == "3063315748321207/3000000000000000"
        and coarse.get("maximum_pair_numerator") == 1_345_600
        and coarse.get("maximum_response_entry") == 993_154_795_744_256
        and coarse.get("python_int_matmul_pass_count") == 7
        and coarse.get("scalar_contraction_exceeds_signed_int64") is True
        and sharp.get("coordinate_numerators")
        == [-638_721, 1_160_191, 1_022_535, -908_876, 0, 0, 0, 0]
        and sharp.get("coordinate_denominator") == 1_000_000
        and sharp.get("raw_spectral_contraction_numerator")
        == "225742872026058646911271963582464"
        and sharp.get("raw_spectral_contraction_abs_bit_length") == 108
        and sharp.get("direct_ordered_spectral_quartic")
        == "3061833659207609685754014263/3000000000000000000000000000"
        and sharp.get("maximum_pair_numerator") == 1_346_043_156_481
        and sharp.get("maximum_response_entry") == 992_985_043_863_140_488_960
        and sharp.get("python_int_matmul_pass_count") == 7
        and sharp.get("maximum_matmul_accumulator_bit_length") == 68
        and sharp.get("scalar_contraction_exceeds_signed_int64") is True
        and report.get("claim_boundary", {}).get(
            "fixed_width_physical_contraction_used"
        )
        is False
        and report.get("claim_boundary", {}).get("target_vector_read") is False
        and report.get("claim_boundary", {}).get("coefficient_map_read") is False
    ):
        raise ArithmeticError("ordered-spectral overflow sentinels drifted")


def build_report() -> dict[str, Any]:
    source = _load_pinned(SOURCE_REPORT)
    exact = _load_pinned(EXACT_VERIFY_REPORT)
    live = _load_pinned(LIVE_REPORT)
    overflow = _load_pinned(OVERFLOW_REPORT)
    _validate_source(source)
    _validate_exact_verify(exact)
    _validate_live(live)
    _validate_overflow(overflow)
    certificate = primal.load_certificate()
    matrix, _, target, _ = primal.load_system()
    if not (
        primal.sparse_sha256(matrix) == EXPECTED_MAP_SHA256
        and primal.int64_array_sha256(target) == EXPECTED_TARGET_SHA256
        and certificate["exact_primal_coordinates_sha256"]
        == EXPECTED_COORDINATE_SHA256
        and certificate["exact_verification"]["all_exact_LDL_pivots_sha256"]
        == EXPECTED_LDL_SHA256
    ):
        raise ArithmeticError("live theorem inputs disagreed with frozen canonical bytes")
    return {
        "status": STATUS,
        "theorem": {
            "fixed_endpoint": {
                "H": "h_-=(e0-i e1)/sqrt(2)",
                "Sigma": "q/4",
                "unbroken_stabilizer_used": "SU(4)",
            },
            "polynomial": "p(t,Phi)=A(t,Phi)-3*t^4/200",
            "complete_polynomial_identity_for_all_real_t_Phi": True,
            "identity_reason": (
                "all 19594 standard Gram columns were reconstructed from the complete "
                "positive-carrier basis in the full 6585-row chart; the corrected "
                "ordered-spectral RHS is the physical p chart; all 6585 rational "
                "coefficient equalities hold"
            ),
            "strict_positive_off_homogeneous_origin": True,
            "strictness_reason": (
                "the 22366-dimensional carrier transform is invertible on "
                "Sym^2(R plus Phi210), so (t,Phi)!=(0,0) has a nonzero carrier "
                "feature; all 22 exact Gram blocks are strictly positive definite"
            ),
            "at_t_equals_one": "A(Phi)>3/200 for every real Phi",
            "p_zero_set_at_t_equals_one": "empty",
        },
        "exact_evidence": {
            "map_numerator_csr_sha256": EXPECTED_MAP_SHA256,
            "target_numerator_sha256": EXPECTED_TARGET_SHA256,
            "exact_coordinate_sha256": EXPECTED_COORDINATE_SHA256,
            "exact_LDL_pivot_sha256": EXPECTED_LDL_SHA256,
            "coefficient_equalities": 6_585,
            "strict_positive_Gram_blocks": 22,
            "strict_positive_LDL_pivots": 824,
            "carrier_dimension": 22_366,
            "carrier_dimension_formula": "211*212/2",
            "source_report_raw_sha256": EXPECTED_REPORT_RAW_SHA256[SOURCE_REPORT.name],
            "exact_verify_report_raw_sha256": EXPECTED_REPORT_RAW_SHA256[
                EXACT_VERIFY_REPORT.name
            ],
            "live_report_raw_sha256": EXPECTED_REPORT_RAW_SHA256[LIVE_REPORT.name],
            "overflow_report_raw_sha256": EXPECTED_REPORT_RAW_SHA256[
                OVERFLOW_REPORT.name
            ],
        },
        "live_SU3_regression": {
            "scope": "independent point regression, not the source of the global identity",
            "target_and_carrier_total": "15742745821207/3000000000000000",
            "exact_grade_residuals": ["0", "0", "0", "0", "0"],
        },
        "overflow_audit_hardening": {
            "logical_role": "arithmetic-path hardening; not a premise of positivity",
            "coarse_raw_contraction": "225852143492225949696",
            "coarse_bit_length": 68,
            "sharp_raw_contraction": "225742872026058646911271963582464",
            "sharp_bit_length": 108,
            "both_exceed_signed_int64": True,
            "fixed_width_physical_contraction_used": False,
        },
        "claim_boundary": {
            "fixed_H_h_minus": True,
            "fixed_Sigma_q_over_4": True,
            "arbitrary_real_Phi_at_this_fixed_endpoint": True,
            "global_Sigma_proved": False,
            "general_H_proved": False,
            "full_H_proved": False,
            "full_Hessian_proved": False,
            "G3_closed": False,
        },
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-report", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write_report:
        if OUTPUT.resolve().parent != HERE.resolve():
            raise ArithmeticError("theorem output escaped HERE")
        OUTPUT.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
