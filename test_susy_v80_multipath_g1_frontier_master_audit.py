import json

import pytest

import susy_v80_multipath_g1_frontier_master_audit as audit


@pytest.fixture(scope="module")
def report():
    value = audit.build_report()
    audit.validate_report(value)
    return value


def test_frozen_v79_master_and_v80_route_are_canonical_and_bound(report):
    for path, key, report_key in (
        (audit.V79_MASTER_PATH, "v79_master", "V79_master"),
        (audit.V80_ROUTE_PATH, "v80_route", "V80_route"),
    ):
        value = json.loads(path.read_text(encoding="utf-8"))
        assert audit.canonical_sha(value) == value["core_sha256"]
        assert value["core_sha256"] == audit.EXPECTED_CORES[key]
        assert report["input_core_hashes"][report_key] == audit.EXPECTED_CORES[key]


def test_mutated_v80_route_with_old_core_is_rejected(tmp_path):
    value = json.loads(audit.V80_ROUTE_PATH.read_text(encoding="utf-8"))
    value["status"] += "_MUTATED"
    path = tmp_path / "mutated.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(RuntimeError, match="noncanonical parent core"):
        audit.load_bound(path, audit.EXPECTED_CORES["v80_route"])


def test_B80_is_appended_without_altering_parent_routes(report):
    parent = json.loads(audit.V79_MASTER_PATH.read_text(encoding="utf-8"))
    assert report["route_matrix"][:-1] == parent["route_matrix"]
    assert report["route_matrix"][-1]["route_id"] == "B80"
    assert not report["route_matrix"][-1]["accepted"]
    assert report["lineage"]["parent_route_count"] == len(parent["route_matrix"])
    assert report["lineage"]["parent_route_matrix_sha256"] == audit.canonical_sha(
        parent["route_matrix"]
    )


def test_acceptance_criteria_record_exact_progress_without_promotion(report):
    rows = {row["id"]: row for row in report["acceptance_criteria"]}
    assert rows["A2"]["status"] == "PASS_EXACT"
    assert rows["A7"]["status"] == "PASS_ORDER_2POW15"
    assert rows["A8"]["status"] == "OPEN_UNCOMPUTED"
    assert rows["A9"]["status"] == "PASS_SPLIT_Z4"
    assert rows["A10"]["status"] == "OPEN_UNCONSTRUCTED"
    assert rows["A18"]["status"] == "OPEN_ILL_TYPED"
    assert rows["A23"]["status"] == "REJECTED_EXACT"
    assert rows["A24"]["status"] == "REJECTED_EXACT"
    assert rows["A26"]["status"] == "OPEN_FAILED"


def test_theory_card_records_no_accepted_extension(report):
    card = report["consolidated_theory_card"]
    assert card["current_action_status"] == "REJECTED"
    assert card["accepted_extension_count"] == 0
    assert len(card["exact_gains"]) == 8
    assert any("split Z4" in item for item in card["exact_gains"])
    assert any("h>=12" in item for item in card["exact_gains"])
    assert any("E3 page" in item for item in card["retired_shortcuts"])
    assert len(card["remaining_global_blockers"]) >= 6


def test_master_separates_split_z4_from_full_bordism(report):
    value = report["strict_master_decision"]
    assert value["reduced_Omega7_H78_split_Z4_proved"]
    assert "Q_4^7" in value["split_Z4_structured_representative"]
    assert not value["Q4_full_parent_HGamma_lift_constructed"]
    assert not value["Q4_is_currently_full_parent_test_generator"]
    assert not value["split_Z4_parent_phase_evaluated"]
    assert not value["full_reduced_Omega7_H78_computed"]
    assert value["AHSS_through_E3"]
    assert value["AHSS_E3_total_order"] == 2**15


def test_master_preserves_canonical_half_nonverdict(report):
    value = report["strict_master_decision"]
    assert value["canonical_zero_half_distinguished"]
    assert not value["canonical_zero_half_accepted"]
    assert not value["canonical_zero_half_falsified"]
    assert not value["full_parent_stratified_category_constructed"]
    assert not value["total_anomaly_identity_well_typed"]
    assert value["D14_status"] == "PARTIAL"
    assert value["D15_status"] == "ABSENT"


def test_master_closes_flat_parent_fallback_only_in_stated_scope(report):
    value = report["strict_master_decision"]
    assert value["flat_three_family_h_min"] == 12
    assert value["integrated_parent_h_max"] == 9
    assert value["all_integrated_flat_QW_bulk_family_parents_rejected"]
    assert not value["clean_rank_breaking_pair_from_QW"]
    boundary = report["next_required_action"]["changed_action_boundary"]
    assert "do not revive h6/h8" in boundary
    assert "rebuilt fixed-point and global anomaly ledger" in boundary


def test_next_action_separates_smooth_and_relative_parent_tests(report):
    value = report["next_required_action"]
    assert value["id"] == (
        "F81_FULL_PARENT_HGAMMA_LIFT_AND_SEPARATE_SMOOTH_RELATIVE_TESTS"
    )
    assert "full-parent H_Gamma category" in value["primary_objective"]
    assert "A_bare x WCS" in value["primary_objective"]
    assert "later AHSS differentials" in value["topological_objective"]
    assert "bridge and cap/junction factors separately" in value[
        "stratified_objective"
    ]
    assert not value["accepted"]


def test_regression_scope_includes_both_v80_test_files(report):
    files = report["regression_scope"]["new_test_files"]
    assert files == [
        "test_susy_v80_multipath_g1_frontier_master_audit.py",
        "test_susy_v80_h78_category_ahss_flat_parent_no_go_audit.py",
    ]
    assert report["regression_scope"]["recommended_full_pattern"] == (
        "test_susy_v*.py"
    )


def test_source_manifest_is_bound_from_v80_route(report):
    route = json.loads(audit.V80_ROUTE_PATH.read_text(encoding="utf-8"))
    assert report["source_manifest"] == route["source_manifest"]
    assert "debray_dierigl_heckman_montero_2023" in report[
        "source_manifest"
    ]["ids"]
    assert "kumar_taylor_2009" in report["source_manifest"]["ids"]


def test_terminal_master_is_strictly_fail_closed(report):
    value = report["strict_master_decision"]
    assert not value["same_action_microscopic_completion_found"]
    assert not value["accepted_full_parent_action_exists"]
    assert not value["selected_candidate_accepted"]
    assert value["current_action_status"] == "REJECTED"
    assert value["research_program_status"] == (
        "VIABLE_ONLY_AFTER_EXPLICIT_CATEGORY_OR_CHANGED_PROJECTOR"
    )
    assert value["closed_gates"] == []
    assert not value["complete_theory"]
    assert all(status.startswith("OPEN") for status in report["gate_ledger"].values())


def test_build_is_deterministic(report):
    second = audit.build_report()
    assert second == report
    assert audit.canonical_sha(second) == second["core_sha256"]


def test_generated_artifacts_are_fresh(report):
    audit.check_artifacts(report)
