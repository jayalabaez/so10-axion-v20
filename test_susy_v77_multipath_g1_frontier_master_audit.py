import json

import pytest

import susy_v77_multipath_g1_frontier_master_audit as audit


def report():
    return audit.build_report()


def test_v76_master_and_v77_route_are_canonical_and_bound():
    value = report()["input_core_hashes"]
    assert value["V76_master"] == audit.EXPECTED_CORES["v76_master"]
    assert value["V77_route"] == audit.EXPECTED_CORES["v77_route"]


def test_mutated_v77_route_with_old_embedded_core_is_rejected(tmp_path):
    parent = json.loads(audit.V77_ROUTE_PATH.read_text(encoding="utf-8"))
    parent["status"] += "__MUTATED"
    path = tmp_path / "mutated.json"
    path.write_text(json.dumps(parent), encoding="utf-8")
    with pytest.raises(RuntimeError, match="noncanonical parent core"):
        audit.load_bound(path, audit.EXPECTED_CORES["v77_route"])


def test_route_summary_adds_one_fail_closed_B77_row():
    value = report()
    assert len(value["route_matrix"]) == value["lineage"]["parent_route_count"] + 1
    row = value["route_matrix"][-1]
    assert row["route_id"] == "B77"
    assert not row["same_action_microscopic_completion"]
    assert not row["accepted"]
    assert row["selected_open_candidate"] == (
        "F77E_EQUIVARIANT_ANOMALY_LINE_WUCS_TRIVIALIZATION"
    )


def test_acceptance_criteria_preserve_exact_conditional_and_open_distinctions():
    criteria = {row["id"]: row["status"] for row in report()["acceptance_criteria"]}
    assert criteria["A2"] == "PASS_EXACT_DIAGNOSTIC"
    assert criteria["A4"] == "REJECTED_TEN_ZERO_MODES"
    assert criteria["A5"] == "REJECTED_CATEGORY_ERROR"
    assert criteria["A7"] == "REJECTED_IDENTITY_ONLY"
    assert criteria["A8"] == "REJECTED_DIVISIBILITY"
    assert criteria["A9"] == "PASS_CONDITIONAL_LOCAL"
    assert criteria["A10"] == "PASS_CONDITIONAL_LOCAL"
    assert criteria["A15"] == "SELECTED_OPEN"
    assert criteria["A17"] == "BLOCKED_BY_ACTION"


def test_theory_card_distinguishes_rejected_action_from_viable_research():
    card = report()["consolidated_theory_card"]
    assert card["current_action_status"] == "REJECTED"
    assert card["research_program_status"].startswith("VIABLE_ONLY_IF")
    assert card["accepted_extension_count"] == 0
    assert card["selected_open_candidate"] == (
        "F77E_EQUIVARIANT_ANOMALY_LINE_WUCS_TRIVIALIZATION"
    )
    assert any("2Y=(3,2)" in gain for gain in card["exact_gains"])
    assert any("combined-H" in route for route in card["open_new_physics"])


def test_strict_decision_binds_exact_new_obstructions_without_overclaim():
    value = report()["strict_master_decision"]
    assert not value[
        "naive_smooth_GS_class_has_ordinary_integral_isotropy_restriction"
    ]
    assert value["tensor_lattice_basis_determinant"] == -6
    assert not value["nontrivial_unchanged_tensor_lattice_twist_exists"]
    assert value["minimum_neutral_chiral_compactification_zero_modes"] == 10
    assert not value["equal_corner_profile_is_an_accepted_current_action"]
    assert value["V71_provisional_lifts_on_V70_fields_normal_profiles"] == {
        "z00": [-28, -20],
        "z11": [-24, -24],
    }
    assert value["conditional_Z2_SU2R_coefficients_over_96"] == [4, 21, -25]
    assert "gauge and flavor curvatures are set to zero" in value[
        "conditional_Z2_projection_scope"
    ]
    assert value["conditional_Z4_coefficients_over_192"] == [
        -24,
        -24,
        -196,
        -23,
        303,
        -132,
    ]
    assert "excludes inherited V70" in value["conditional_Z4_projection_scope"]
    assert "not the full action" in value["conditional_Z4_projection_scope"]
    assert not value["conditional_SU2R_results_globalized"]
    assert not value["combined_anomaly_line_trivialized"]
    assert not value["same_action_microscopic_completion_found"]
    assert not value["selected_candidate_accepted"]
    assert value["current_Spin11_action_status"] == "REJECTED"


def test_combined_anomaly_line_identity_is_carried_into_master():
    decision = report()["strict_master_decision"]
    value = decision["combined_anomaly_line_identity"]
    assert "A_bare(U)" in value
    assert "WCS" in value
    assert "A_cap_defect(U)" in value
    assert value.endswith("= 1")
    assert "symmetric-monoidal isomorphism" in decision[
        "combined_anomaly_line_categorical_target"
    ]


def test_all_eight_master_gates_remain_open():
    gates = report()["gate_ledger"]
    assert set(gates) == {f"G{i}" for i in range(1, 9)}
    assert all(status.startswith("OPEN") for status in gates.values())
    decision = report()["strict_master_decision"]
    assert decision["closed_gates"] == []
    assert not decision["complete_theory"]


def test_source_manifest_is_bound_from_v77_route():
    route = json.loads(audit.V77_ROUTE_PATH.read_text(encoding="utf-8"))
    assert report()["source_manifest"] == route["source_manifest"]
    assert report()["source_manifest"]["kind"] == "primary_sources_only"
    assert report()["source_manifest"]["count"] >= 12


def test_master_core_is_canonical_and_artifacts_are_fresh():
    value = report()
    assert audit.canonical_sha(value) == value["core_sha256"]
    checked = audit.check_artifacts()
    assert checked["core_sha256"] == value["core_sha256"]
