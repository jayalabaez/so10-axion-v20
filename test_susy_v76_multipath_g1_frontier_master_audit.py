import json

import pytest

import susy_v76_multipath_g1_frontier_master_audit as audit


def report():
    return audit.build_report()


def test_v75_master_and_v76_route_are_canonical_and_bound():
    value = report()["input_core_hashes"]
    assert value["V75_master"] == audit.EXPECTED_CORES["v75_master"]
    assert value["V76_route"] == audit.EXPECTED_CORES["v76_route"]


def test_mutated_v76_route_with_old_embedded_core_is_rejected(tmp_path):
    parent = json.loads(audit.V76_ROUTE_PATH.read_text(encoding="utf-8"))
    parent["status"] += "__MUTATED"
    path = tmp_path / "mutated.json"
    path.write_text(json.dumps(parent), encoding="utf-8")
    with pytest.raises(RuntimeError, match="noncanonical parent core"):
        audit.load_bound(path, audit.EXPECTED_CORES["v76_route"])


def test_route_summary_adds_one_fail_closed_B76_row():
    value = report()
    assert len(value["route_matrix"]) == value["lineage"]["parent_route_count"] + 1
    row = value["route_matrix"][-1]
    assert row["route_id"] == "B76"
    assert not row["same_action_microscopic_completion"]
    assert not row["accepted"]
    assert row["selected_open_candidate"] == "F76_FULL_EQUIVARIANT_PARENT_DETERMINANT"


def test_acceptance_criteria_preserve_pass_reject_and_open_distinctions():
    criteria = {row["id"]: row["status"] for row in report()["acceptance_criteria"]}
    assert criteria["A2"] == "REJECTED_ODD_QUARTER"
    assert criteria["A3"] == "PASS_CORRELATED_ONLY"
    assert criteria["A4"] == "PASS_EXACT_LOCAL"
    assert criteria["A7"] == "PASS_TOPOLOGICAL_SCAFFOLD"
    assert criteria["A11"] == "REJECTED_TOPOLOGY"
    assert criteria["A12"] == "REJECTED_CHANGES_TARGET"
    assert criteria["A15"] == "SELECTED_OPEN"
    assert criteria["A16"] == "OPEN_FAILED"


def test_theory_card_distinguishes_rejected_action_from_viable_research():
    card = report()["consolidated_theory_card"]
    assert card["current_action_status"] == "REJECTED"
    assert card["research_program_status"].startswith("VIABLE_ONLY")
    assert "CHANGED_STRUCTURE" in card["research_program_status"]
    assert card["accepted_extension_count"] == 0
    assert card["selected_open_candidate"] == "F76_FULL_EQUIVARIANT_PARENT_DETERMINANT"
    assert any("odd-quarter" in gain for gain in card["exact_gains"])
    assert any("self-dual" in route for route in card["open_new_physics"])


def test_strict_decision_carries_exact_route_adjudication_without_overclaim():
    value = report()["strict_master_decision"]
    assert value["ordinary_free_field_two_corner_routes_closed"]
    assert value["four_line_correlated_representative_constructed"]
    assert not value["pure_diagonal_quarter_refinement_constructed"]
    assert value["level4_component_centers_pass"]
    assert not value["level4_complete_multiplets_constructed"]
    assert value["normal_driver_no_go_on_original_backgrounds"]
    assert not value["same_action_microscopic_completion_found"]
    assert not value["selected_candidate_accepted"]
    assert value["current_Spin11_action_status"] == "REJECTED"


def test_all_eight_master_gates_remain_open():
    gates = report()["gate_ledger"]
    assert set(gates) == {f"G{i}" for i in range(1, 9)}
    assert all(status.startswith("OPEN") for status in gates.values())
    decision = report()["strict_master_decision"]
    assert decision["closed_gates"] == []
    assert not decision["complete_theory"]


def test_source_manifest_is_bound_from_the_v76_route():
    route = json.loads(audit.V76_ROUTE_PATH.read_text(encoding="utf-8"))
    assert report()["source_manifest"] == route["source_manifest"]
    assert len(report()["source_manifest"]) >= 10


def test_master_core_is_canonical_and_artifacts_are_fresh():
    value = report()
    assert audit.canonical_sha(value) == value["core_sha256"]
    checked = audit.check_artifacts()
    assert checked["core_sha256"] == value["core_sha256"]
