from __future__ import annotations

import copy

import pytest

import exact_gauged_u1x_g1_component_tensor_closure_v20 as theorem


@pytest.fixture(scope="module")
def report():
    return theorem.build_report()


def test_complete_gauged_component_tensor_ring(report):
    assert report["n_failed"] == 0
    assert report["status"] == theorem.STATUS
    assert report["model_contract_id"] == theorem.MODEL_CONTRACT_ID
    assert report["canonical_direction_map_sha256"] == theorem.EXPECTED_DIRECTION_MAP_SHA256
    assert report["counts"] == {
        "multidegrees": 34,
        "Hermitian_conjugacy_orbits": 28,
        "invariant_directions": 44,
        "self_conjugate_directions": 37,
        "complex_paired_directions": 7,
        "real_parameters": 51,
        "tensor_families": 18,
        "real_field_dimension": 486,
    }


def test_exact_independence_and_compiler_binding(report):
    assert len(report["orbit_independence_audit"]) == 28
    assert all(
        row["D5_multiplicity"]
        == row["declared_multiplicity"]
        == row["basis_length"]
        for row in report["orbit_independence_audit"]
    )
    assert len(report["direction_ids"]) == len(set(report["direction_ids"])) == 44
    assert len(report["parameter_ids"]) == len(set(report["parameter_ids"])) == 51
    assert len(report["certificate_reports"]) == 14
    assert all(row["n_failed"] == 0 for row in report["certificate_reports"].values())
    assert all(report["checks"].values())


def test_scope_is_mathematical_g1_not_fabricated_release(report):
    closure = report["closure"]
    classification = report["classification"]
    assert closure["explicit_component_tensor_subset_integration_closed"]
    assert closure["full_renormalizable_G1_mathematical_ring_closed"]
    assert not closure["external_model_execution_contract_closed"]
    assert classification["scoped_mathematical_G1_closed"]
    assert not classification["authoritative_G1_promoted_closed"]
    assert not classification["release_G1_verified"]
    assert not classification["renormalizable_model_mutated"]
    assert not classification["new_physics_required_for_G1"]
    assert report["release_blockers"] == [
        "AUTHORITATIVE_GAUGED_U1X_EXTERNAL_SARAH_EXECUTION_REQUIRED",
    ]
    assert all(report["integration"].values())


def test_direction_reordering_fails_closed(monkeypatch):
    original = theorem.contract.build_report
    tampered = copy.deepcopy(original())
    tampered["gauged_directions"][0], tampered["gauged_directions"][1] = (
        tampered["gauged_directions"][1],
        tampered["gauged_directions"][0],
    )
    monkeypatch.setattr(theorem.contract, "build_report", lambda: tampered)
    mutated = theorem.build_report()
    assert mutated["n_failed"] > 0
    assert not mutated["checks"]["canonical_44_row_map_hash_exact"]
    assert not mutated["checks"][
        "arbitrary_component_evaluator_covers_ordered_44_at_two_states"
    ]


def test_source_drift_fails_before_claim(monkeypatch):
    name = "g1_exact_declared_symmetry_character_census_v20.py"
    altered = dict(theorem.EXPECTED_SOURCE_SHA256)
    altered[name] = "0" * 64
    monkeypatch.setattr(theorem, "EXPECTED_SOURCE_SHA256", altered)
    with pytest.raises(ArithmeticError, match="G1 tensor source drifted"):
        theorem.build_report()
