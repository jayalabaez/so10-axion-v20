from __future__ import annotations

import json

import susy_v73_multipath_g1_frontier_master_audit as audit


def report():
    return audit.build_report()


def routes():
    return {row["route_id"]: row for row in report()["route_matrix"]}


def candidates():
    return {row["id"]: row for row in routes()["B73"]["candidate_matrix"]}


def test_v73_master_canonical_recomputation_and_integrity():
    value = report()
    audit.validate(value)
    assert value["core_sha256"] == audit.canonical_sha(value)
    assert value["n_failed_integrity_checks"] == 0


def test_bound_input_cores_are_exact():
    value = report()
    assert value["input_core_hashes"] == audit.EXPECTED_CORES
    assert value["lineage"]["parent_V72_master_core"] == audit.EXPECTED_CORES["v72_master"]
    assert value["lineage"]["V73_route_core"] == audit.EXPECTED_CORES["v73_route"]


def test_A60_C_and_complete_B72_lineage_are_preserved():
    value = routes()
    assert audit.object_sha(value["A60"]) == audit.V72_ROW_SHA["A60"]
    assert audit.object_sha(value["C"]) == audit.V72_ROW_SHA["C"]
    b = value["B73"]
    assert b["inherited_B72_row_sha256"] == audit.V72_ROW_SHA["B72"]
    assert audit.object_sha(b["inherited_B72_row"]) == audit.V72_ROW_SHA["B72"]


def test_only_F72_pure_full_quotient_extension_is_superseded():
    b = routes()["B73"]
    old = [row for row in b["inherited_B72_row"]["candidate_matrix"] if row["id"] != "F72"]
    new = [
        row
        for row in b["candidate_matrix"]
        if row["id"] not in {"F72", "F73_AXION", "F73_NORMAL", "F73_FLAVOR", "F73_TENSOR_BRIDGE"}
    ]
    assert old == new
    assert b["superseded_candidate_ids"] == ["F72_PURE_FULL_QUOTIENT_EXTENSION"]


def test_F72_scoped_result_is_retained_but_pure_extension_is_rejected():
    f72 = candidates()["F72"]
    assert f72["retained_exact_scoped_result"]["U5tilde_restricted_coefficients"] == {
        "z00": 1,
        "z11": -1,
    }
    assert f72["V73_full_quotient_adjudication"] == {
        "diagonal_period": "25/4",
        "minimal_pure_multiplier": 4,
        "common_residue": "nu A B",
        "ordinary_single_transfer_glues": False,
    }
    assert not f72["accepted"]
    assert not f72["spin_eta_or_bridge_refinement_excluded"]
    assert "not that scoped calculation" in f72["scope_clause"]


def test_correlated_integral_candidates_remain_unaccepted():
    rows = candidates()
    assert "LOCAL_INTEGRAL_CLASS_PASS" in rows["F73_AXION"]["status"]
    assert "FORCED_ASYMMETRIC_NORMAL_CUBIC" in rows["F73_NORMAL"]["status"]
    assert "FLAVOR_R_TORSION" in rows["F73_FLAVOR"]["status"]
    for key in ("F73_AXION", "F73_NORMAL", "F73_FLAVOR"):
        assert not rows[key]["selected"]
        assert not rows[key]["accepted"]
        assert not rows[key]["same_action_complete"]


def test_tensor_bridge_inflow_is_the_only_selected_unaccepted_frontier():
    rows = candidates()
    selected = [row for row in rows.values() if row.get("selected")]
    assert [row["id"] for row in selected] == ["F73_TENSOR_BRIDGE"]
    assert "PURE_OPPOSITE_SLOPE_SUBCANDIDATE_REJECTED" in selected[0]["status"]
    assert "BRIDGE_FIELD_CONTENT_OPEN" in selected[0]["status"]
    assert not selected[0]["accepted"]
    assert routes()["B73"]["accepted_extension_count"] == 0


def test_theory_card_binds_exact_new_physics_without_overclaim():
    card = report()["consolidated_theory_card"]
    joined = " ".join(card["exact_advances"])
    for term in ("25/4", "11/16", "coefficient C", "nu A B", "p1(V10)/4", "affine N1 axion"):
        assert term in joined
    assert card["accepted_extension_count"] == 0
    assert not card["cross_route_splicing_allowed"]
    assert "design target" in card["honesty_clause"]


def test_regression_scope_is_exact_and_hash_pinned():
    scope = report()["regression_scope"]
    assert scope["file_count"] == audit.EXPECTED_REGRESSION_FILES
    assert scope["test_count"] == audit.EXPECTED_REGRESSION_TESTS
    assert scope["manifest_sha256"] == audit.EXPECTED_REGRESSION_MANIFEST_SHA256
    assert all(row["sha256"] and row["test_functions"] for row in scope["files"])


def test_no_cross_route_splice_or_accepted_candidate():
    value = report()
    rule = value["cross_route_composition_rule"]
    assert not rule["cross_route_splicing_allowed"]
    assert not rule["aggregated_gate_closure"]
    assert not any(row["accepted"] for row in candidates().values())


def test_strict_decision_and_all_gates_are_fail_closed():
    value = report()
    decision = value["strict_master_decision"]
    assert decision["current_Spin11_action_status"] == "REJECTED"
    assert not decision["F72_pure_full_quotient_extension_accepted"]
    assert not decision["F73_plain_tensor_accepted"]
    assert decision["F73_tensor_bridge_inflow_selected"]
    assert not decision["F73_tensor_bridge_inflow_accepted"]
    assert not decision["same_action_microscopic_completion_found"]
    assert decision["closed_gates"] == []
    assert not decision["complete_theory"]
    assert all(row["status"].startswith("OPEN") for row in value["acceptance_criteria"])
    assert all(
        row["status"] == "OPEN" and not row["V73_master_closed"]
        for row in value["gate_ledger"]
    )


def test_source_manifest_is_complete():
    rows = report()["source_manifest"]
    names = {row["path"] for row in rows}
    for required in (
        audit.JSON_PATH.name.replace("V73", "V72", 1),
        "SUSY_V73_SPIN11_FULL_QUOTIENT_SUPERSYMMETRIC_WZ_AUDIT.json",
        audit.ROUTE_MD_PATH.name,
        audit.TEST_PATH.name,
    ):
        assert required in names
    assert all(row["exists"] and row["sha256"] for row in rows)


def test_generated_artifacts_are_required_and_match():
    value = report()
    assert audit.JSON_PATH.is_file()
    assert audit.MD_PATH.is_file()
    assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == value
    assert audit.MD_PATH.read_text(encoding="utf-8") == audit.render_markdown(value)
