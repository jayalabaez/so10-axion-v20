from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

import exact_gauged_u1x_g2_mathematical_closure_v20 as theorem


@pytest.fixture(scope="module")
def report() -> dict:
    return theorem.build_report()


def test_frozen_mathematical_g2_core_passes(report: dict) -> None:
    assert report["status"] == theorem.STATUS
    assert report["overall_state"] == "CLOSED_SUBPROBLEM"
    assert report["core_sha256"] == theorem.EXPECTED_CORE_SHA256
    assert report["n_failed"] == 0
    assert not report["failures"]
    assert all(report["checks"].values())


def test_all_upstream_and_derivative_owner_bytes_are_bound(report: dict) -> None:
    assert len(report["artifact_sha256"]) == 16
    assert len(report["derivative_owner_modules"]) == 10
    for label, (path, expected) in theorem.EXPECTED_ARTIFACT_SHA256.items():
        assert path.is_file(), label
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected
        assert report["artifact_sha256"][label] == expected


def test_terminal_g1_and_ordered_basis_are_exact(report: dict) -> None:
    assert report["upstream_cores"] == {
        "terminal_mathematical_G1": theorem.EXPECTED_G1_CORE_SHA256
    }
    assert report["basis_identity"] == {
        "ordered_direction_ids_sha256": theorem.EXPECTED_ORDERED_DIRECTION_IDS_SHA256,
        "ordered_parameter_ids_sha256": theorem.EXPECTED_ORDERED_PARAMETER_IDS_SHA256,
    }
    assert report["closure"]["terminal_mathematical_G1_prerequisite_closed"]


def test_complete_44_51_18_486_derivative_contract(report: dict) -> None:
    assert report["counts"] == {
        "invariant_directions": 44,
        "real_parameters": 51,
        "base_tensor_families": 18,
        "real_field_dimension": 486,
        "gradient_entries_per_parameter": 486,
        "Hessian_shape_per_parameter": [486, 486],
        "symmetric_Hessian_entries_per_parameter": 118341,
        "upstream_derivative_audit_checks": 49,
    }
    assert len(report["upstream_derivative_check_surface"]) == 49
    assert all(report["upstream_derivative_check_surface"].values())
    assert all(report["derivative_coverage"].values())


def test_complete_so10_and_u1x_ward_coverage(report: dict) -> None:
    assert set(report["Ward_identity_coverage"]) == set(theorem.WARD_CHECKS)
    assert all(report["Ward_identity_coverage"].values())


def test_exact_stationarity_rank_and_nullity(report: dict) -> None:
    stationarity = report["stationarity"]
    assert stationarity["matrix_shape"] == [486, 51]
    assert stationarity["exact_rank"] == 13
    assert stationarity["exact_nullity"] == 38
    assert stationarity["exact_nonzero_13x13_minor"]
    assert stationarity["exact_rank_upper_factorization"]
    assert stationarity["compiler_minor_binding"]
    assert stationarity["stationary_witness_P24_trace"] == 288
    assert stationarity["stationary_Hessian_compiler_binding"]
    assert stationarity["float64_SVD_is_diagnostic_only"]


def test_scope_closes_mathematical_g2_without_overclaim(report: dict) -> None:
    classification = report["classification"]
    assert classification == {
        "mathematical_renormalizable_G2_closed": True,
        "authoritative_G2_promoted_closed": False,
        "release_G2_verified": False,
        "renormalizable_model_mutated": False,
        "new_physics_required_for_G2": False,
        "G3_closed_by_this_theorem": False,
    }
    assert report["release_blockers"] == [
        "AUTHORITATIVE_GAUGED_U1X_EXTERNAL_SARAH_EXECUTION_REQUIRED"
    ]


def test_bundle_is_consumed_by_every_downstream_surface(report: dict) -> None:
    assert len(report["integration"]) == 4
    assert all(report["integration"].values())
    assert report["integration_blockers"] == []


def test_frozen_json_is_the_exact_deterministic_report(report: dict) -> None:
    frozen = json.loads(theorem.OUT_JSON.read_text(encoding="utf-8"))
    assert frozen == report


def test_markdown_records_decisive_scope(report: dict) -> None:
    text = theorem.OUT_MD.read_text(encoding="utf-8")
    assert report["status"] in text
    assert report["core_sha256"] in text
    assert "13/38" in text
    assert "external SARAH execution" in text
