import json

import pytest

import susy_v81_multipath_g1_frontier_master_audit as audit


@pytest.fixture(scope="module")
def report():
    value = audit.build_report()
    audit.validate_report(value)
    return value


def test_frozen_v80_master_and_v81_route_are_canonical_and_bound(report):
    for path, key, report_key in (
        (audit.V80_MASTER_PATH, "v80_master", "V80_master"),
        (audit.V81_ROUTE_PATH, "v81_route", "V81_route"),
    ):
        value = json.loads(path.read_text(encoding="utf-8"))
        assert audit.canonical_sha(value) == value["core_sha256"]
        assert value["core_sha256"] == audit.EXPECTED_CORES[key]
        assert report["input_core_hashes"][report_key] == audit.EXPECTED_CORES[key]


def test_mutated_v81_route_with_old_core_is_rejected(tmp_path):
    value = json.loads(audit.V81_ROUTE_PATH.read_text(encoding="utf-8"))
    value["status"] += "_MUTATED"
    path = tmp_path / "mutated.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(RuntimeError, match="noncanonical parent core"):
        audit.load_bound(path, audit.EXPECTED_CORES["v81_route"])


def test_B81_is_appended_without_altering_parent_routes(report):
    parent = json.loads(audit.V80_MASTER_PATH.read_text(encoding="utf-8"))
    assert report["route_matrix"][:-1] == parent["route_matrix"]
    assert report["route_matrix"][-1]["route_id"] == "B81"
    assert not report["route_matrix"][-1]["accepted"]
    assert report["lineage"]["parent_route_count"] == len(parent["route_matrix"])
    assert report["lineage"]["parent_route_matrix_sha256"] == audit.canonical_sha(
        parent["route_matrix"]
    )


def test_acceptance_criteria_record_progress_without_promotion(report):
    rows = {row["id"]: row for row in report["acceptance_criteria"]}
    assert rows["A2"]["status"] == "PASS_EXACT"
    assert rows["A4"]["status"] == "OPEN_UNDEFINED"
    assert rows["A7"]["status"] == "REJECTED_LAMBDA_2R2"
    assert rows["A9"]["status"] == "OPEN_UNCONSTRUCTED"
    assert rows["A11"]["status"] == "REJECTED_EXACT"
    assert rows["A12"]["status"] == "REJECTED_NONZERO_Y"
    assert rows["A14"]["status"] == "PASS_EXACT"
    assert rows["A15"]["status"] == "PASS_EXACT_SCOPED"
    assert rows["A18"]["status"] == "OPEN_ILL_TYPED"
    assert rows["A22"]["status"] == "ABSENT"
    assert rows["A24"]["status"] == "REJECTED_TAUTOLOGICAL_ACTION_CHANGE"
    assert rows["A27"]["status"] == "OPEN_FAILED"


def test_theory_card_has_no_accepted_extension_and_scopes_every_gain(report):
    card = report["consolidated_theory_card"]
    assert card["current_action_status"] == "REJECTED"
    assert card["accepted_extension_count"] == 0
    assert len(card["exact_gains"]) == 9
    assert any("lambda=2r^2" in item for item in card["exact_gains"])
    assert any("source-free" in item for item in card["exact_gains"])
    assert any("complex Dirac character" in item for item in card["retired_shortcuts"])
    assert any("formal inverse" in item for item in card["retired_shortcuts"])
    assert len(card["remaining_global_blockers"]) == 7


def test_master_preserves_v80_results(report):
    value = report["strict_master_decision"]
    assert value["inherited_reduced_H78_AHSS_through_E3"]
    assert value["inherited_AHSS_E3_total_order"] == 2**15
    assert value["inherited_split_Z4_proved"]
    assert not value["inherited_full_reduced_Omega7_computed"]
    assert value["inherited_flat_QW_bulk_family_parents_rejected"]
    assert not value["canonical_zero_half_accepted"]
    assert not value["canonical_zero_half_falsified"]


def test_master_records_scoped_direct_lift_rejection(report):
    value = report["strict_master_decision"]
    assert not value["full_HGamma_defined"]
    assert value["direct_flat_qhat_lift_of_split_Q4_rejected"]
    assert value["direct_lift_obstruction"] == "2r^2"
    assert not value["general_compensated_lift_rejected"]
    assert not value["general_compensated_lift_constructed"]
    assert value["qhat_Q4_is_separate_reduced_background"]
    assert not value["qhat_Q4_bordism_class_computed"]


def test_master_records_source_and_eta_boundaries(report):
    value = report["strict_master_decision"]
    assert not value["V80_basepoint_admissible_source_free"]
    assert value["Q4_qT"] == "lambda(W)-r^2=r^2+2rx"
    assert value["V80_basepoint_Y"] == ["r^2+2rx", "3r^2+2rx"]
    assert value["qhat_Q4_Y"] == ["r^2+2rx", "r^2+2rx"]
    assert value["qhat_Q4_source_free_verdict_computed"]
    assert not value["qhat_Q4_admissible_source_free"]
    assert value["D15_status"] == "ABSENT"
    assert value["ordinary_Q4_eta_table"] == ["-1/8", "1/8", "1/8", "-1/8"]
    assert value["qhat_eta_shadow"] == "-3/4"
    assert not value["physical_bare_times_WCS_evaluated"]


def test_master_keeps_relative_category_and_caps_open(report):
    value = report["strict_master_decision"]
    assert not value["relative_Bord765_constructed"]
    assert not value["physical_cap_sector_constructed"]
    assert not value["total_relative_identity_well_typed"]
    frontier = report["exact_frontier_objects"]
    assert frontier["relative_category"]["symbol"].startswith("C81=Bord_(7,6,5)")
    assert len(frontier["cap_contract"]) == 7
    assert not frontier["eta_scope"]["shadow_is_physical_A_bare"]


def test_next_action_executes_the_exact_remaining_fork(report):
    value = report["next_required_action"]
    assert value["id"] == "F82_QHAT_Q4_CLASS_NONFLAT_COMPENSATOR_AND_PARENT_INCIDENCE_CATEGORY"
    assert "qhat-decorated Q4" in value["primary_objective"]
    assert "lambda=2r^2" in value["primary_objective"]
    assert "K and Gammahat" in value["parent_objective"]
    assert "Bord_(7,6,5)" in value["relative_objective"]
    assert not value["accepted"]


def test_regression_scope_includes_both_v81_test_files(report):
    assert report["regression_scope"]["new_test_files"] == [
        "test_susy_v81_multipath_g1_frontier_master_audit.py",
        "test_susy_v81_q4_parent_lift_eta_relative_cap_audit.py",
    ]
    assert report["regression_scope"]["recommended_full_pattern"] == "test_susy_v*.py"


def test_source_manifest_is_bound_from_v81_route(report):
    route = json.loads(audit.V81_ROUTE_PATH.read_text(encoding="utf-8"))
    assert report["source_manifest"] == route["source_manifest"]
    assert "debray_dierigl_heckman_montero_2023" in report["source_manifest"]["ids"]
    assert "dai_freed_1994" in report["source_manifest"]["ids"]
    assert "monnier_moore_2018" in report["source_manifest"]["ids"]


def test_terminal_master_is_strictly_fail_closed(report):
    value = report["strict_master_decision"]
    assert not value["same_action_microscopic_completion_found"]
    assert not value["accepted_full_parent_action_exists"]
    assert not value["selected_candidate_accepted"]
    assert value["current_action_status"] == "REJECTED"
    assert value["research_program_status"] == (
        "VIABLE_ONLY_AFTER_QHAT_CLASS_OR_NONFLAT_COMPENSATOR_AND_FULL_PARENT_CATEGORY"
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
