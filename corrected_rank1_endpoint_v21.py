#!/usr/bin/env python3
"""Fast, fail-closed central view of the audited corrected rank-one endpoint.

The publication directory is byte-frozen and relocation-self-contained.  This
module is deliberately only a central consumer: ordinary validation checks the
frozen bytes and exact reports, while the explicit heavy regeneration entrypoint
is reserved for the full re-audit workflow.

The theorem proved here is restricted to H=h_- and Sigma=q/4, with arbitrary
real Phi.  It does not close G3, vary H or Sigma, or classify the full Hessian.
"""
from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
PUBLICATION_ROOT = ROOT / "corrected_rank1_publication_v21"
MANIFEST_PATH = (
    PUBLICATION_ROOT
    / "EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_PUBLICATION_V21_MANIFEST.json"
)
THEOREM_PATH = (
    PUBLICATION_ROOT
    / "EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_FIXED_ENDPOINT_THEOREM_V21.json"
)
SOURCE_REPORT_PATH = (
    PUBLICATION_ROOT
    / "EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_SOURCE_RECONSTRUCTION_V21.json"
)
VERIFY_REPORT_PATH = (
    PUBLICATION_ROOT
    / "EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_POSITIVE_GRAM_VERIFY_V21.json"
)
LIVE_REPORT_PATH = (
    PUBLICATION_ROOT
    / "EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_LIVE_POLYNOMIAL_V21.json"
)
OVERFLOW_REPORT_PATH = (
    PUBLICATION_ROOT
    / "EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_ORDERED_SPECTRAL_OVERFLOW_V21.json"
)

EXPECTED_MANIFEST_RAW_SHA256 = (
    "7ecf96a12321b9df5e7d118ce0fb83e65ad9859516b520936408ec4d46a11017"
)
EXPECTED_MAP_SHA256 = (
    "1834c8439fa3e44459f7ba871420a4351cd0b4de194dec6f5c4a84c1f39d3a16"
)
EXPECTED_TARGET_SHA256 = (
    "14debcfaf02d4b8c20d1d43a2e1f82d6a7390e28428fc63dd21a9c5f90aec0cf"
)
EXPECTED_CERTIFICATE_RAW_SHA256 = (
    "dd40a508a08c219117ddefaf574652a24f0e1f868d011e05f558ecafc9600e03"
)
EXPECTED_COORDINATE_SHA256 = (
    "7a36b579821e135fb7283d02e696153cc78907048e73ca5dce0dd260abdc3147"
)
EXPECTED_LDL_SHA256 = (
    "bc8626c201d626aa33a97f707bfa963ae887fe9abb64a0fab728343825a430c2"
)
EXPECTED_SYSTEM_RAW_SHA256 = (
    "25ec946b1e9bca50cfe4e31ac9bb58f5d8d0f4a24b83dc11fdeec0d68a80c6f3"
)


def _parse_json_bytes(payload: bytes, name: str) -> dict[str, Any]:
    value = json.loads(payload.decode("utf-8"))
    if not isinstance(value, dict):
        raise ArithmeticError(f"expected JSON object: {name}")
    return value


def _canonical_json_bytes(value: Any) -> bytes:
    """Serialize with JSON's type distinctions for injected-value comparison."""
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _validated_publication_uncached() -> dict[str, Any]:
    """Validate the complete frozen byte inventory without source regeneration."""
    if MANIFEST_PATH.parent.resolve() != PUBLICATION_ROOT.resolve():
        raise ArithmeticError("publication manifest escaped its fixed directory")
    manifest_payload = MANIFEST_PATH.read_bytes()
    if hashlib.sha256(manifest_payload).hexdigest() != EXPECTED_MANIFEST_RAW_SHA256:
        raise ArithmeticError("corrected publication manifest hash mismatch")
    manifest = _parse_json_bytes(manifest_payload, MANIFEST_PATH.name)
    inventory = manifest.get("inventory", {})
    if (
        manifest.get("schema")
        != "so10-rank1-su4-corrected-positive-gram-publication-v21"
        or manifest.get("status")
        != "EXACT_RANK1_SU4_CORRECTED_PUBLICATION_V21_INVENTORY_FROZEN"
        or manifest.get("inventory_count") != 18
        or len(inventory) != 18
        or manifest.get("manifest_self_excluded_by_definition") is not True
    ):
        raise ArithmeticError("corrected publication manifest schema drifted")

    expected_names = set(inventory) | {MANIFEST_PATH.name}
    actual_entries = list(PUBLICATION_ROOT.iterdir())
    if any(not path.is_file() for path in actual_entries):
        raise ArithmeticError("corrected publication contains a non-file entry")
    if {path.name for path in actual_entries} != expected_names:
        raise ArithmeticError("corrected publication inventory is not exact")
    verified_payloads: dict[str, bytes] = {}
    for name, row in inventory.items():
        path = (PUBLICATION_ROOT / name).resolve()
        if path.parent != PUBLICATION_ROOT.resolve() or not path.is_file():
            raise ArithmeticError(f"invalid publication inventory path: {name}")
        if set(row) != {"raw_sha256", "role", "size_bytes"}:
            raise ArithmeticError(f"invalid publication inventory row: {name}")
        payload = path.read_bytes()
        if len(payload) != row["size_bytes"]:
            raise ArithmeticError(f"publication size mismatch: {name}")
        if hashlib.sha256(payload).hexdigest() != row["raw_sha256"]:
            raise ArithmeticError(f"publication byte hash mismatch: {name}")
        verified_payloads[name] = payload
    if {path.name for path in PUBLICATION_ROOT.iterdir()} != expected_names:
        raise ArithmeticError("corrected publication inventory changed during read")

    logical = manifest.get("logical_pins", {})
    if logical != {
        "certificate_raw_sha256": EXPECTED_CERTIFICATE_RAW_SHA256,
        "exact_LDL_pivot_sha256": EXPECTED_LDL_SHA256,
        "exact_coordinate_sha256": EXPECTED_COORDINATE_SHA256,
        "map_numerator_csr_sha256": EXPECTED_MAP_SHA256,
        "system_raw_sha256": EXPECTED_SYSTEM_RAW_SHA256,
        "target_numerator_sha256": EXPECTED_TARGET_SHA256,
    }:
        raise ArithmeticError("corrected publication logical pins drifted")
    if manifest.get("heavy_validation") != {
        "embedded_full_RHS_reconstruction_count": 1,
        "entrypoint": (
            "heavy_regenerate_exact_gauged_u1x_g3_rank1_su4_corrected_"
            "system_v21.py --check"
        ),
        "full_map_reconstruction_count": 1,
        "ordinary_unittest_discovery_runs_heavy_entrypoint": False,
    }:
        raise ArithmeticError("corrected publication heavy/fast boundary drifted")

    return {
        "manifest": manifest,
        "theorem": _parse_json_bytes(
            verified_payloads[THEOREM_PATH.name], THEOREM_PATH.name
        ),
        "source": _parse_json_bytes(
            verified_payloads[SOURCE_REPORT_PATH.name], SOURCE_REPORT_PATH.name
        ),
        "verify": _parse_json_bytes(
            verified_payloads[VERIFY_REPORT_PATH.name], VERIFY_REPORT_PATH.name
        ),
        "live": _parse_json_bytes(
            verified_payloads[LIVE_REPORT_PATH.name], LIVE_REPORT_PATH.name
        ),
        "overflow": _parse_json_bytes(
            verified_payloads[OVERFLOW_REPORT_PATH.name], OVERFLOW_REPORT_PATH.name
        ),
    }


def load_validated_publication() -> dict[str, Any]:
    """Rehash every byte, then return a defensive copy of the publication.

    The inventory is intentionally not cached: a successful first read must not
    hide a later same-process mutation of any frozen byte.
    """
    return deepcopy(_validated_publication_uncached())


def corrected_fixed_endpoint_theorem_exact(
    publication: dict[str, Any] | None = None,
) -> bool:
    """Recognize exactly the audited fixed-H/fixed-Sigma arbitrary-Phi theorem."""
    try:
        canonical_publication = load_validated_publication()
        if publication is None:
            publication = canonical_publication
        elif _canonical_json_bytes(publication) != _canonical_json_bytes(
            canonical_publication
        ):
            return False
        else:
            publication = canonical_publication
        if set(publication) != {
            "manifest", "theorem", "source", "verify", "live", "overflow"
        }:
            return False
        manifest = publication["manifest"]
        theorem = publication["theorem"]
        source = publication["source"]
        verify = publication["verify"]
        live = publication["live"]
        overflow = publication["overflow"]
        claim = theorem.get("claim_boundary", {})
        theorem_body = theorem.get("theorem", {})
        evidence = theorem.get("exact_evidence", {})
        source_boundary = source.get("claim_boundary", {})
        source_generation = source.get("generation_boundary", {})
        source_map = source.get("map", {})
        rhs = source.get("physical_RHS", {})
        verify_boundary = verify.get("claim_boundary", {})
        block_diagnostics = verify.get("block_diagnostics", [])
        manifest_boundary = manifest.get("claim_boundary", {})
        live_regression = theorem.get("live_SU3_regression", {})
        overflow_hardening = theorem.get("overflow_audit_hardening", {})

        return bool(
            theorem.get("status")
            == "EXACT_RANK1_SU4_CORRECTED_FIXED_ENDPOINT_THEOREM_V21_PASS"
            and source.get("status")
            == "EXACT_RANK1_SU4_CORRECTED_SOURCE_RECONSTRUCTION_V21_PASS"
            and verify.get("status")
            == "EXACT_RANK1_SU4_CORRECTED_POSITIVE_GRAM_PRIMAL_V21_"
            "INDEPENDENT_VERIFY_PASS"
            and live.get("status")
            == "EXACT_RANK1_SU4_CORRECTED_LIVE_POLYNOMIAL_V21_PASS"
            and overflow.get("status")
            == "EXACT_RANK1_SU4_CORRECTED_ORDERED_SPECTRAL_OVERFLOW_V21_PASS"
            and claim
            == {
                "G3_closed": False,
                "arbitrary_real_Phi_at_this_fixed_endpoint": True,
                "fixed_H_h_minus": True,
                "fixed_Sigma_q_over_4": True,
                "full_H_proved": False,
                "full_Hessian_proved": False,
                "general_H_proved": False,
                "global_Sigma_proved": False,
            }
            and manifest_boundary
            == {
                "G3_closed": False,
                "arbitrary_real_Phi_at_fixed_endpoint": True,
                "fixed_H": "h_-=(e0-i e1)/sqrt(2)",
                "fixed_Sigma": "q/4",
                "full_H_proved": False,
                "full_Hessian_proved": False,
                "general_H_proved": False,
                "global_Sigma_proved": False,
            }
            and source_boundary.get("G3_closed") is False
            and source_boundary.get("fixed_H") == "h_-=(e0-i e1)/sqrt(2)"
            and source_boundary.get("fixed_Sigma") == "q/4"
            and source_boundary.get("general_H_proved") is False
            and source_boundary.get("global_Sigma_proved") is False
            and source_boundary.get("full_Hessian_proved") is False
            and verify_boundary.get("G3_closed") is False
            and verify_boundary.get("exact_affine_equalities_proved") is True
            and verify_boundary.get("exact_strict_PSD_primal_independently_verified")
            is True
            and verify_boundary.get("arbitrary_Phi_endpoint_proved") is False
            and theorem_body.get("complete_polynomial_identity_for_all_real_t_Phi")
            is True
            and theorem_body.get("strict_positive_off_homogeneous_origin") is True
            and theorem_body.get("at_t_equals_one")
            == "A(Phi)>3/200 for every real Phi"
            and theorem_body.get("p_zero_set_at_t_equals_one") == "empty"
            and theorem_body.get("fixed_endpoint")
            == {
                "H": "h_-=(e0-i e1)/sqrt(2)",
                "Sigma": "q/4",
                "unbroken_stabilizer_used": "SU(4)",
            }
            and evidence.get("map_numerator_csr_sha256") == EXPECTED_MAP_SHA256
            and evidence.get("target_numerator_sha256") == EXPECTED_TARGET_SHA256
            and evidence.get("exact_coordinate_sha256")
            == EXPECTED_COORDINATE_SHA256
            and evidence.get("exact_LDL_pivot_sha256") == EXPECTED_LDL_SHA256
            and evidence.get("coefficient_equalities") == 6_585
            and evidence.get("strict_positive_Gram_blocks") == 22
            and evidence.get("strict_positive_LDL_pivots") == 824
            and evidence.get("carrier_dimension") == 22_366
            and source_map.get("shape") == [6_585, 19_594]
            and source_map.get("common_denominator") == 256
            and source_map.get("nnz") == 138_550
            and source_map.get("numerator_csr_sha256") == EXPECTED_MAP_SHA256
            and source_map.get("full_column_reconstruction_count") == 19_594
            and source_map.get("grade01_formula")
            == "linear_column returns solved coordinates divided by 16; the "
            "off-diagonal factor 2 remains in the carrier expansion"
            and rhs.get("common_denominator") == 576_000
            and rhs.get("full_nonzero_count") == 512
            and rhs.get("numerator_sha256") == EXPECTED_TARGET_SHA256
            and rhs.get("quartic_row_count") == 6_057
            and rhs.get("row_by_row_direct_evaluator_mismatch_count") == 0
            and rhs.get("first_quartic_value_correct") == "27776/1125"
            and source_generation.get("v20_physical_target_payload_read") is False
            and source_generation.get("prior_assembled_map_read") is False
            and source_generation.get("prior_primal_certificate_read") is False
            and verify.get("exact_coefficient_equalities_verified") == 6_585
            and verify.get("strictly_positive_Gram_blocks_verified") == 22
            and len(block_diagnostics) == 22
            and all(
                row.get("all_leading_principal_minors_strictly_positive") is True
                for row in block_diagnostics
            )
            and sum(
                row.get("positive_leading_principal_minor_count", -1)
                for row in block_diagnostics
            ) == 824
            and verify.get("exact_rational_coordinates_verified") == 19_594
            and live_regression.get("exact_grade_residuals") == ["0"] * 5
            and live_regression.get("target_and_carrier_total")
            == "15742745821207/3000000000000000"
            and overflow_hardening.get("both_exceed_signed_int64") is True
            and overflow_hardening.get("coarse_bit_length") == 68
            and overflow_hardening.get("sharp_bit_length") == 108
            and overflow_hardening.get("fixed_width_physical_contraction_used")
            is False
        )
    except (ArithmeticError, KeyError, OSError, TypeError, ValueError):
        return False


def central_view(
    publication: dict[str, Any] | None = None,
) -> dict[str, Any]:
    publication = (
        load_validated_publication() if publication is None else deepcopy(publication)
    )
    exact = corrected_fixed_endpoint_theorem_exact(publication)
    if not exact:
        raise ArithmeticError("corrected fixed-endpoint publication failed centrally")
    theorem = publication["theorem"]
    source = publication["source"]
    verify = publication["verify"]
    return {
        "publication_manifest_raw_sha256": EXPECTED_MANIFEST_RAW_SHA256,
        "legacy_v20_physical_target_valid": False,
        "legacy_v20_primal_valid": False,
        "corrected_fixed_endpoint_theorem_exact": True,
        "fixed_H": "h_-=(e0-i e1)/sqrt(2)",
        "fixed_Sigma": "q/4",
        "arbitrary_real_Phi_at_fixed_endpoint": True,
        "strict_positive_off_homogeneous_origin": True,
        "A_greater_than_3_over_200_at_t1": True,
        "p_zero_set_at_t1_empty": True,
        "map_shape": source["map"]["shape"],
        "map_common_denominator": source["map"]["common_denominator"],
        "map_nnz": source["map"]["nnz"],
        "map_numerator_csr_sha256": EXPECTED_MAP_SHA256,
        "target_common_denominator": source["physical_RHS"]["common_denominator"],
        "target_nonzero_count": source["physical_RHS"]["full_nonzero_count"],
        "target_numerator_sha256": EXPECTED_TARGET_SHA256,
        "exact_coefficient_equalities": verify["exact_coefficient_equalities_verified"],
        "strict_positive_Gram_blocks": verify["strictly_positive_Gram_blocks_verified"],
        "strict_positive_LDL_pivots": theorem["exact_evidence"][
            "strict_positive_LDL_pivots"
        ],
        "exact_coordinate_sha256": EXPECTED_COORDINATE_SHA256,
        "exact_LDL_pivot_sha256": EXPECTED_LDL_SHA256,
        "global_Sigma_proved": False,
        "general_H_proved": False,
        "full_H_proved": False,
        "full_Hessian_proved": False,
        "G3_closed": False,
    }


if __name__ == "__main__":
    view = central_view()
    print(
        "corrected rank-one endpoint PASS: "
        f"map={view['map_numerator_csr_sha256'][:12]}..., "
        f"target={view['target_numerator_sha256'][:12]}..., "
        f"equalities={view['exact_coefficient_equalities']}, "
        f"blocks={view['strict_positive_Gram_blocks']}, "
        f"pivots={view['strict_positive_LDL_pivots']}, G3=false"
    )
