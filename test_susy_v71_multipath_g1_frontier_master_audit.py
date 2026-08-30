from __future__ import annotations

import json

import susy_v71_multipath_g1_frontier_master_audit as audit


def report():
    return audit.build_report()


def routes():
    return {row["route_id"]: row for row in report()["route_matrix"]}


def candidates():
    return {row["id"]: row for row in routes()["B71"]["candidate_matrix"]}


def test_v71_master_canonical_recomputation_and_integrity():
    value = report()
    audit.validate(value)
    assert value["core_sha256"] == audit.canonical_sha(value)
    assert value["n_failed_integrity_checks"] == 0


def test_bound_input_cores_are_exact():
    value = report()
    assert value["input_core_hashes"] == audit.EXPECTED_CORES
    assert value["lineage"]["parent_V70_master_core"] == audit.EXPECTED_CORES["v70_master"]
    assert value["lineage"]["V71_route_core"] == audit.EXPECTED_CORES["v71_route"]


def test_A60_C_and_complete_B70_lineage_are_preserved():
    value = routes()
    assert audit.object_sha(value["A60"]) == audit.V70_ROW_SHA["A60"]
    assert audit.object_sha(value["C"]) == audit.V70_ROW_SHA["C"]
    b = value["B71"]
    assert b["inherited_B70_row_sha256"] == audit.V70_ROW_SHA["B70"]
    assert audit.object_sha(b["inherited_B70_row"]) == audit.V70_ROW_SHA["B70"]


def test_only_F70_and_F70ALT_are_superseded():
    b = routes()["B71"]
    old = [row for row in b["inherited_B70_row"]["candidate_matrix"] if row["id"] not in {"F70", "F70_ALT"}]
    new = [row for row in b["candidate_matrix"] if row["id"] != "F71"]
    assert old == new
    assert b["superseded_candidate_ids"] == ["F70", "F70_ALT"]
    assert set(candidates()) == {"D67", "H66", "T66", "B3_IR", "E68", "F71"}


def test_unmodified_V70_candidates_are_rejected_by_exact_local_obstruction():
    b = routes()["B71"]
    assert all(value.startswith("REJECTED") for value in b["superseded_candidate_adjudication"].values())
    obstruction = b["V71_selected_candidate"]["exact_rejection_of_superseded_candidates"]
    assert obstruction["F70_vector_each_Z4"] == ["-1/4", "40"]
    assert obstruction["bulk_GS_direction"] == ["1", "40"]
    assert obstruction["determinant"] == "-50"
    assert not obstruction["z11_has_V70_local_repair"]


def test_F71_is_selected_but_not_accepted():
    f71 = candidates()["F71"]
    assert f71["selected"]
    assert not f71["accepted"]
    assert not f71["same_action_complete"]
    assert f71["supersedes_candidates"] == ["F70", "F70_ALT"]


def test_F71_corrected_local_modules_are_anomaly_selective():
    repair = candidates()["F71"]["exact_repair_contract"]
    retracted = repair["retracted_four_fermion_module"]
    assert retracted["standalone_mixed_repair"].startswith("FAIL")
    modules = repair["corrected_charge_lattice_modules"]
    assert modules["both_mixed_vectors_align"]
    assert modules["z00_complete_ledger"]["U1L_X_squared"] == "-50"
    assert modules["z11_complete_ledger"]["U1L_X_squared"] == "-50"
    assert modules["z00_complete_ledger"]["all_spectator_anomalies_zero"]
    assert modules["z11_complete_ledger"]["all_spectator_anomalies_zero"]
    assert "literal vector-form U(5)" in modules["global_form_boundary"]
    assert "Giudice-Masiero" in modules["mass_boundary"]
    assert "z00 each charged scalar has continuous normal charge +1" in modules["mass_boundary"]
    assert "eight-new-chiral" in repair["selected_hybrid"]["z11"]
    assert not repair["continuous_Stueckelberg"]["four_dimensional_crosscheck"]["forced_mass_for_hypercharge"]


def test_neutral_delta_and_zero_mode_theorem_are_carried_exactly():
    repair = candidates()["F71"]["exact_repair_contract"]
    assert repair["neutral_Delta"] == -10
    assert repair["neutral_zero_mode_minimum"] == 10
    assert repair["neutral_266_witness"]["dimension"] == 266
    assert repair["neutral_266_witness"]["Delta_at_each_corner"] == -10
    assert repair["neutral_symmetric_QK_target"]["target"] == "Sp(266,1)/(Sp(266)xSp(1))"
    assert repair["neutral_symmetric_QK_target"]["local_space_group_and_bundle_lift"].startswith("PASS_EXACT")
    assert not repair["local_fermion_only_residue_cancellation"]


def test_F71_open_boundary_contains_real_microscopic_obligations():
    f71 = candidates()["F71"]
    joined = " ".join(f71["required_new_data"] + f71["not_yet_passes"])
    for term in ("z11", "quaternionic", "Wu-Chern-Simons", "hypercharge", "Dai-Freed"):
        assert term in joined
    assert not f71["equivariant_WuCS_constructed"]
    torsion = f71["naive_WuCS_torsion_divisibility"]
    assert torsion["all_loci_fail_ordinary_divisibility"]
    assert [row["two_Y_mod_order"] for row in torsion["rows"]] == [[3, 2], [3, 2], [1, 1]]


def test_regression_scope_is_exact():
    scope = report()["regression_scope"]
    assert scope["file_count"] == audit.EXPECTED_REGRESSION_FILES
    assert scope["test_count"] == audit.EXPECTED_REGRESSION_TESTS
    assert scope["manifest_sha256"] == audit.EXPECTED_REGRESSION_MANIFEST_SHA256
    assert all(row["sha256"] for row in scope["files"])


def test_no_cross_route_splice_or_accepted_extension():
    value = report()
    rule = value["cross_route_composition_rule"]
    assert not rule["cross_route_splicing_allowed"]
    assert not rule["aggregated_gate_closure"]
    assert routes()["B71"]["accepted_extension_count"] == 0


def test_current_action_and_F71_are_fail_closed():
    decision = report()["strict_master_decision"]
    assert decision["current_Spin11_action_status"] == "REJECTED"
    assert decision["F70_and_F70ALT_rejected_unmodified"]
    assert not decision["F71_new_action_accepted"]
    assert not decision["same_action_microscopic_completion_found"]
    assert decision["closed_gates"] == []
    assert not decision["complete_theory"]


def test_all_acceptance_criteria_and_gates_remain_open():
    value = report()
    assert all(row["status"].startswith("OPEN") for row in value["acceptance_criteria"])
    assert all(row["status"] == "OPEN" and not row["V71_master_closed"] for row in value["gate_ledger"])


def test_generated_artifacts_are_required_and_match():
    value = report()
    assert audit.JSON_PATH.is_file()
    assert audit.MD_PATH.is_file()
    assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == value
    assert audit.MD_PATH.read_text(encoding="utf-8") == audit.render_markdown(value)
