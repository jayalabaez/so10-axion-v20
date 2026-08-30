from __future__ import annotations

import json

import susy_v69_multipath_g1_frontier_master_audit as master


def report():
    return master.build_report()


def routes(value):
    return {row["route_id"]: row for row in value["route_matrix"]}


def test_master_canonical_recomputation_and_integrity():
    value = report()
    master.validate(value)
    assert value["core_sha256"] == master.canonical_sha(value)
    assert value["n_failed_integrity_checks"] == 0


def test_input_cores_and_route_supersession_are_exact():
    value = report()
    by_id = routes(value)
    assert value["input_core_hashes"] == master.EXPECTED_CORES
    assert list(by_id) == ["A60", "B69", "C"]
    assert by_id["B69"]["supersedes_V68_route_id"] == "B68"
    assert by_id["B69"]["bound_V69_route_core"] == master.EXPECTED_CORES["v69_order4"]


def test_A60_and_C_are_preserved_canonically():
    by_id = routes(report())
    assert master.object_sha(by_id["A60"]) == master.V68_ROW_SHA["A60"]
    assert master.object_sha(by_id["C"]) == master.V68_ROW_SHA["C"]


def test_full_B68_parent_is_bound_inside_B69():
    b = routes(report())["B69"]
    assert b["inherited_B68_row_sha256"] == master.V68_ROW_SHA["B68"]
    assert master.object_sha(b["inherited_B68_row"]) == master.V68_ROW_SHA["B68"]
    assert b["current_bound_action_status"] == "REJECTED"
    assert b["V64_null_mode_stands_for_current_action"]


def test_direct_order_two_lift_is_closed_but_F69_is_separate():
    b = routes(report())["B69"]
    assert b["direct_order2_6D_lift"] == "CLOSED"
    assert b["conventional_full_hyper_scalar_import"] == "CLOSED_SCOPED"
    assert b["pseudoreal_half_32_projection"] == "OPEN_NOT_COMPUTED"
    assert b["V69_new_action"]["terminal_decision"]["V69_order4_gauge_skeleton"] == "EXACT_KINEMATIC_CANDIDATE"
    assert not b["V69_new_action"]["accepted"]


def test_embedded_order_four_geometry_is_exact():
    embedded = routes(report())["B69"]["V69_new_action"]
    geometry = embedded["order4_space_group_and_fixed_algebra_audit"]
    assert geometry["all_vector_space_group_relations_pass"]
    assert geometry["fixed_algebra_dimensions"]["C_Q_U5"] == 25
    assert geometry["fixed_algebra_dimensions"]["C_Q_and_W_common_G3211"] == 13
    assert geometry["spin_lift_audit"]["status"].startswith("OPEN")


def test_orphan_absence_is_scoped_to_action_replacement():
    rank = routes(report())["B69"]["V69_new_action"]["geometric_rank_replacement"]
    assert rank["orphan_statement"]["classification"] == "ABSENT_BY_ACTION_REPLACEMENT_NOT_MASS_LIFTED"
    assert not rank["orphan_statement"]["V59_C16_Cbar16_rank_sector_present"]
    assert rank["orphan_statement"]["colored_rank_fields"] == 0


def test_integrated_bulk_parents_factorize_but_are_not_local_completion():
    anomaly = routes(report())["B69"]["V69_new_action"]["bulk_and_fixed_locus_anomaly_audit"]
    assert all(row["factorization_passes"] for row in anomaly["variants"])
    assert "projector weights" in anomaly["nonimport_rule"]
    assert anomaly["status"].endswith("NOT_FIXED_POINT_COMPLETIONS")


def test_candidate_matrix_is_isolated_and_unaccepted():
    rows = {row["id"]: row for row in routes(report())["B69"]["candidate_matrix"]}
    assert set(rows) == {"D67", "H66", "T66", "B3_IR", "E68", "F69"}
    assert rows["F69"]["status"] == "EXACT_KINEMATIC_GAUGE_AND_CLASSICAL_RANK_SKELETON"
    assert all(not row["accepted"] and not row["same_action_complete"] for row in rows.values())


def test_regression_scope_is_pinned():
    scope = report()["regression_scope"]
    assert scope["file_count"] == master.EXPECTED_REGRESSION_FILES == 24
    assert scope["test_count"] == master.EXPECTED_REGRESSION_TESTS == 321
    assert "test_susy_v69_multipath_g1_frontier_master_audit.py" not in {
        row["path"] for row in scope["files"]
    }


def test_no_cross_route_splice_or_acceptance():
    value = report()
    rule = value["cross_route_composition_rule"]
    assert not rule["cross_route_splicing_allowed"]
    assert not rule["aggregated_gate_closure"]
    assert value["consolidated_theory_card"]["accepted_extension_count"] == 0


def test_all_gates_and_acceptance_criteria_remain_open():
    value = report()
    assert all(row["status"] == "OPEN" for row in value["acceptance_criteria"])
    assert all(row["status"] == "OPEN" and not row["V69_master_closed"] for row in value["gate_ledger"])


def test_strict_decision_is_fail_closed():
    decision = report()["strict_master_decision"]
    assert decision["current_Spin11_action_status"] == "REJECTED"
    assert decision["direct_Hall_order2_lift_status"] == "CLOSED"
    assert decision["conventional_full_hyper_scalar_import_status"] == "CLOSED_SCOPED"
    assert decision["pseudoreal_half_32_projection_status"] == "OPEN_NOT_COMPUTED"
    assert not decision["F69_new_action_accepted"]
    assert not decision["same_action_microscopic_completion_found"]
    assert decision["closed_gates"] == []
    assert not decision["complete_theory"]


def test_generated_master_artifacts_match_when_present():
    value = report()
    if master.JSON_PATH.is_file():
        assert json.loads(master.JSON_PATH.read_text(encoding="utf-8")) == value
    if master.MD_PATH.is_file():
        assert master.MD_PATH.read_text(encoding="utf-8") == master.render_markdown(value)
