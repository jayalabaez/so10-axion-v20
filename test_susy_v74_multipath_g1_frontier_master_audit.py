import json

import susy_v74_multipath_g1_frontier_master_audit as audit


def report():
    return audit.build_report()


def route(route_id):
    return next(row for row in report()["route_matrix"] if row["route_id"] == route_id)


def candidates():
    return route("B74")["candidate_matrix"]


def test_v73_master_and_v74_route_cores_are_bound():
    value = report()
    assert value["input_core_hashes"] == audit.EXPECTED_CORES
    assert value["lineage"]["parent_V73_master_core"] == audit.EXPECTED_CORES[
        "v73_master"
    ]
    assert value["lineage"]["V74_route_core"] == audit.EXPECTED_CORES["v74_route"]


def test_v73_a60_b73_and_c_rows_are_frozen_before_supersession():
    value = report()["lineage"]
    assert value["A60_row_sha256"] == audit.V73_ROW_SHA["A60"]
    assert value["B73_row_sha256"] == audit.V73_ROW_SHA["B73"]
    assert value["C_row_sha256"] == audit.V73_ROW_SHA["C"]
    assert value["only_F73_selected_bridge_row_superseded"]


def test_b74_preserves_the_complete_b73_row_by_hash_and_value():
    b74 = route("B74")
    assert b74["inherited_B73_row_sha256"] == audit.V73_ROW_SHA["B73"]
    assert audit.object_sha(b74["inherited_B73_row"]) == audit.V73_ROW_SHA["B73"]
    assert b74["superseded_candidate_ids"] == ["F73_TENSOR_BRIDGE"]


def test_f73_bridge_scoped_advance_is_retained_but_deselected():
    row = next(item for item in candidates() if item["id"] == "F73_TENSOR_BRIDGE")
    assert row["inherited_candidate"]["selected"]
    assert not row["selected"]
    assert not row["accepted"]
    assert row["V74_adjudication"] == {
        "common_K_bridge_exists": True,
        "bridge_is_existing_action_content": False,
        "common_gluing_solved": True,
        "quarter_endpoint_spectator_solved": False,
    }


def test_all_f74_candidates_are_present_without_acceptance():
    rows = candidates()
    ids = {row["id"] for row in rows}
    assert {
        "F74_K_CS_BRIDGE",
        "F74_VECTOR_LINEAR_REFINED_BRIDGE",
        "F74_COEFFICIENT_FOUR",
        "F74_DIRECT_LOCAL_FIVE",
        "F74_COMMON_MATTER_INTERFACE",
    } <= ids
    assert not any(row.get("accepted") for row in rows)
    assert all(not row["same_action_complete"] for row in rows if row["id"].startswith("F74_"))


def test_vector_linear_refined_bridge_is_the_only_selected_candidate():
    selected = [row for row in candidates() if row.get("selected")]
    assert [row["id"] for row in selected] == ["F74_VECTOR_LINEAR_REFINED_BRIDGE"]
    assert not selected[0]["accepted"]
    assert route("B74")["V74_selected_candidate"] == selected[0]


def test_acceptance_matrix_records_passes_and_blockers_without_promotion():
    rows = {row["id"]: row["status"] for row in report()["acceptance_criteria"]}
    assert rows["A2"] == "PASS_EXACT"
    assert rows["A3"] == "PASS_EXACT"
    assert rows["A4"] == "REJECTED"
    assert rows["A5"] == "PASS_CONDITIONAL_LOCAL"
    assert rows["A7"] == "OPEN_FAILED"
    assert rows["A10"] == "REJECTED"
    assert rows["A11"] == "REJECTED"


def test_theory_card_records_the_exact_bridge_and_quarter_obstruction():
    card = report()["consolidated_theory_card"]
    advances = " ".join(card["exact_advances"])
    assert "primitive ordinary integral" in advances
    assert "spin periods of r have exact gcd two" in advances
    assert "opposite quarter-period spectators" in advances
    assert "cannot change the quarter class" in advances
    assert card["accepted_extension_count"] == 0
    assert not card["cross_route_splicing_allowed"]


def test_regression_scope_is_frozen():
    scope = report()["regression_scope"]
    assert scope["file_count"] == audit.EXPECTED_REGRESSION_FILES
    assert scope["test_count"] == audit.EXPECTED_REGRESSION_TESTS
    assert scope["manifest_sha256"] == audit.EXPECTED_REGRESSION_MANIFEST_SHA256
    assert "V74 master test is excluded" in scope["selection"]


def test_cross_route_evidence_is_not_spliced():
    rule = report()["cross_route_composition_rule"]
    assert not rule["cross_route_splicing_allowed"]
    assert not rule["aggregated_gate_closure"]
    assert not route("B74")["cross_route_evidence_spliced"]


def test_strict_decision_is_fail_closed():
    decision = report()["strict_master_decision"]
    assert decision["current_Spin11_action_status"] == "REJECTED"
    assert decision["primitive_common_K_bridge_passed"]
    assert not decision["existing_Spin11_tensor_bridge_accepted"]
    assert not decision["quarter_endpoint_spectator_solved"]
    assert decision["F74_vector_linear_refined_bridge_selected"]
    assert not decision["F74_vector_linear_refined_bridge_accepted"]
    assert not decision["same_action_microscopic_completion_found"]
    assert decision["closed_gates"] == []
    assert not decision["complete_theory"]


def test_all_eight_gates_remain_open_with_v74_specific_reasons():
    gates = report()["gate_ledger"]
    assert set(gates) == {f"G{i}" for i in range(1, 9)}
    assert all(value.startswith("OPEN") for value in gates.values())
    assert "quarter endpoint spectator" in gates["G1"]
    assert "Dai--Freed" in gates["G8"]


def test_source_manifest_is_unique_complete_and_hash_pinned():
    rows = report()["source_manifest"]
    paths = [row["path"] for row in rows]
    assert len(paths) == len(set(paths))
    assert all(row["exists"] for row in rows)
    assert all(len(row["sha256"]) == 64 for row in rows)
    assert "SUSY_V73_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json" in paths
    assert "SUSY_V74_SPIN11_BRIDGE_ENDPOINT_OBSTRUCTION_AUDIT.json" in paths


def test_master_core_and_generated_artifacts_are_canonical():
    value = report()
    copy_value = dict(value)
    core = copy_value.pop("core_sha256")
    assert audit.canonical_sha(copy_value) == core
    if audit.OUT_JSON.is_file() and audit.OUT_MD.is_file():
        disk = json.loads(audit.OUT_JSON.read_text(encoding="utf-8"))
        assert disk["core_sha256"] == core
        assert audit.OUT_MD.read_text(encoding="utf-8") == audit.render_markdown(value)
