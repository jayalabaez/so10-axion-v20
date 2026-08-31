import json

import pytest

import susy_v75_multipath_g1_frontier_master_audit as audit


def report():
    return audit.build_report()


def route(route_id):
    return next(row for row in report()["route_matrix"] if row["route_id"] == route_id)


def candidates():
    return route("B75")["candidate_matrix"]


def test_v74_master_and_v75_route_cores_are_recomputed_and_bound():
    value = report()
    assert value["input_core_hashes"] == audit.EXPECTED_CORES
    assert value["lineage"]["parent_V74_master_core"] == audit.EXPECTED_CORES[
        "v74_master"
    ]
    assert value["lineage"]["V75_route_core"] == audit.EXPECTED_CORES["v75_route"]


def test_mutated_route_with_unchanged_embedded_core_is_rejected(tmp_path, monkeypatch):
    parent = json.loads(audit.INPUTS["v75_route"].read_text(encoding="utf-8"))
    parent["status"] += "__MUTATED"
    path = tmp_path / "mutated.json"
    path.write_text(json.dumps(parent), encoding="utf-8")
    monkeypatch.setitem(audit.INPUTS, "v75_route", path)
    with pytest.raises(RuntimeError, match="noncanonical core"):
        audit.load_bound("v75_route")


def test_v74_a60_b74_and_c_rows_are_frozen_before_supersession():
    value = report()["lineage"]
    assert value["A60_row_sha256"] == audit.V74_ROW_SHA["A60"]
    assert value["B74_row_sha256"] == audit.V74_ROW_SHA["B74"]
    assert value["C_row_sha256"] == audit.V74_ROW_SHA["C"]
    assert value["only_F74_selected_refined_endpoint_row_superseded"]


def test_b75_preserves_complete_b74_row_by_hash_and_value():
    b75 = route("B75")
    assert b75["inherited_B74_row_sha256"] == audit.V74_ROW_SHA["B74"]
    assert audit.object_sha(b75["inherited_B74_row"]) == audit.V74_ROW_SHA["B74"]
    assert b75["superseded_candidate_ids"] == ["F74_VECTOR_LINEAR_REFINED_BRIDGE"]


def test_f74_selected_scaffold_is_retained_but_deselected():
    row = next(item for item in candidates() if item["id"] == "F74_VECTOR_LINEAR_REFINED_BRIDGE")
    assert row["inherited_candidate"]["selected"]
    assert not row["selected"]
    assert not row["accepted"]
    assert row["V75_adjudication"] == {
        "correlated_eta_representative_constructed": True,
        "pure_quarter_spectator_cancelled_by_eta_route": False,
        "standard_neutral_free_eta_route_closed": True,
        "same_action_microscopic_completion_found": False,
        "level4_quarter_coset_removed_algebraically": True,
        "clean_parent_residue_inverse_route_closed": True,
    }


def test_all_f75_candidates_are_present_without_acceptance():
    rows = candidates()
    ids = {row["id"] for row in rows}
    assert {
        "F75_VIRTUAL_LINE_ETA_REPRESENTATIVE",
        "F75_CORRELATED_R_OR_NORMAL_FERMION_MODULE",
        "F75_STANDARD_NEUTRAL_FREE_ETA_SPECTATOR",
        "F75_GAUGE_CHARGED_SPECTRUM_REDESIGN",
        "F75_ODD_X_NEUTRAL_MOD8_EVASION",
        "F75_CLEAN_GAUGE_CHARGED_PARENT_RESIDUE_INVERSE",
        "F75_INTERACTING_REFINED_ENDPOINT_SECTOR",
    } <= ids
    assert not any(row.get("accepted") for row in rows)
    assert all(not row["same_action_complete"] for row in rows if row["id"].startswith("F75_"))


def test_level4_spectrum_redesign_is_only_selected_candidate():
    selected = [row for row in candidates() if row.get("selected")]
    assert [row["id"] for row in selected] == ["F75_GAUGE_CHARGED_SPECTRUM_REDESIGN"]
    assert not selected[0]["accepted"]
    assert route("B75")["V75_selected_candidate"] == selected[0]


def test_acceptance_matrix_records_exact_advances_and_blockers():
    rows = {row["id"]: row["status"] for row in report()["acceptance_criteria"]}
    assert rows["A2"] == "PASS_EXACT"
    assert rows["A3"] == "PASS_EXACT_SCOPED"
    assert rows["A5"] == "REJECTED_MISMATCH"
    assert rows["A7"] == "REJECTED_MOD8"
    assert rows["A8"] == "REJECTED_INDEX_PERIOD"
    assert rows["A10"] == "OPEN"
    assert rows["A11"] == "OPEN_FAILED"
    assert rows["A12"] == "PASS_EXACT_ALGEBRAIC"
    assert rows["A13"] == "PASS_EXACT_CONDITIONAL"


def test_theory_card_distinguishes_eta_curvature_from_microscopic_action():
    card = report()["consolidated_theory_card"]
    advances = " ".join(card["exact_advances"])
    assert "closed-spin virtual eta phase" in advances
    assert "compulsory gravity spectator" in advances
    assert "mod-eight theorem" in advances
    assert "CP3 index-period theorem" in advances
    assert "M00=(3,3,0)" in advances
    assert "cross-mass operators pass" in advances
    assert card["accepted_extension_count"] == 0
    assert not card["cross_route_splicing_allowed"]
    assert "curvature representative" in card["honesty_clause"]


def test_regression_scope_is_frozen():
    scope = report()["regression_scope"]
    assert scope["file_count"] == audit.EXPECTED_REGRESSION_FILES
    assert scope["test_count"] == audit.EXPECTED_REGRESSION_TESTS
    assert scope["manifest_sha256"] == audit.EXPECTED_REGRESSION_MANIFEST_SHA256
    assert "V75 master test is excluded" in scope["selection"]


def test_cross_route_evidence_is_not_spliced():
    rule = report()["cross_route_composition_rule"]
    assert not rule["cross_route_splicing_allowed"]
    assert not rule["aggregated_gate_closure"]
    assert not route("B75")["cross_route_evidence_spliced"]


def test_strict_decision_is_fail_closed():
    decision = report()["strict_master_decision"]
    assert decision["current_Spin11_action_status"] == "REJECTED"
    assert decision["closed_spin_correlated_eta_phase_constructed"]
    assert not decision["Z4_equivariant_supersymmetric_eta_phase_constructed"]
    assert not decision["bound_equal_corner_residue_cancelled"]
    assert decision["standard_neutral_free_eta_route_rejected"]
    assert decision[
        "clean_local_Weyl_or_standard_half_eta_parent_residue_route_rejected"
    ]
    assert decision["level4_quarter_coset_removed_algebraically"]
    assert decision["level4_mass_operator_charge_checks_pass"]
    assert not decision["level4_vector_type_VEV_action_constructed"]
    assert not decision["gauge_charged_routes_exhaustively_classified"]
    assert decision["level4_spectrum_redesign_selected"]
    assert not decision["level4_spectrum_redesign_accepted"]
    assert not decision["same_action_microscopic_completion_found"]
    assert decision["closed_gates"] == []
    assert not decision["complete_theory"]


def test_all_eight_gates_remain_open_with_v75_specific_reasons():
    gates = report()["gate_ledger"]
    assert set(gates) == {f"G{i}" for i in range(1, 9)}
    assert all(value.startswith("OPEN") for value in gates.values())
    assert "level-four spectrum" in gates["G1"]
    assert "Dai--Freed" in gates["G8"]


def test_source_manifest_is_unique_complete_and_hash_pinned():
    rows = report()["source_manifest"]
    paths = [row["path"] for row in rows]
    assert len(paths) == len(set(paths))
    assert all(row["exists"] for row in rows)
    assert all(len(row["sha256"]) == 64 for row in rows)
    assert "SUSY_V74_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json" in paths
    assert "SUSY_V75_QUARTER_SPECTATOR_ETA_LATTICE_AUDIT.json" in paths


def test_master_core_and_generated_artifacts_are_canonical_when_present():
    value = report()
    assert audit.canonical_sha(value) == value["core_sha256"]
    if audit.OUT_JSON.is_file() and audit.OUT_MD.is_file():
        disk = json.loads(audit.OUT_JSON.read_text(encoding="utf-8"))
        assert disk["core_sha256"] == value["core_sha256"]
        assert audit.OUT_MD.read_text(encoding="utf-8") == audit.render_markdown(value)
