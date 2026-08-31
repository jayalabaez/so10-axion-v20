import copy
import json

import pytest

import susy_v79_multipath_g1_frontier_master_audit as audit


@pytest.fixture(scope="module")
def report():
    value = audit.build_report()
    audit.validate_report(value)
    return value


def test_bound_parent_and_route_cores_are_canonical(report):
    assert report["input_core_hashes"]["V78_master"] == audit.EXPECTED_CORES[
        "v78_master"
    ]
    assert report["input_core_hashes"]["V79_route"] == audit.EXPECTED_CORES[
        "v79_route"
    ]
    for path, key in (
        (audit.V78_MASTER_PATH, "v78_master"),
        (audit.V79_ROUTE_PATH, "v79_route"),
    ):
        value = json.loads(path.read_text(encoding="utf-8"))
        assert audit.canonical_sha(value) == value["core_sha256"]
        assert value["core_sha256"] == audit.EXPECTED_CORES[key]


def test_mutated_route_with_old_core_is_rejected(tmp_path):
    value = json.loads(audit.V79_ROUTE_PATH.read_text(encoding="utf-8"))
    value["status"] += "_MUTATED"
    path = tmp_path / "mutated.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(RuntimeError, match="noncanonical parent core"):
        audit.load_bound(path, audit.EXPECTED_CORES["v79_route"])


def test_route_matrix_extends_v78_once(report):
    parent = json.loads(audit.V78_MASTER_PATH.read_text(encoding="utf-8"))
    assert len(report["route_matrix"]) == len(parent["route_matrix"]) + 1
    assert report["lineage"]["parent_route_count"] == len(parent["route_matrix"])
    row = report["route_matrix"][-1]
    assert row["route_id"] == "B79"
    assert not row["same_action_microscopic_completion"]
    assert not row["accepted"]


def test_acceptance_criteria_separate_pass_reject_and_open(report):
    rows = {row["id"]: row["status"] for row in report["acceptance_criteria"]}
    assert rows["A3"] == "PASS_EXHAUSTIVE"
    assert rows["A5"] == "PASS_UNIQUE_ONE"
    assert rows["A8"] == "PASS_RP7_MINUS_ONE"
    assert rows["A9"] == "REJECTED_NOT_H78"
    assert rows["A11"] == "OPEN_UNCOMPUTED"
    assert rows["A17"] == "REJECTED_EXACT"
    assert rows["A19"] == "OPEN_UNCOMPUTED"
    assert rows["A20"] == "OPEN_FAILED"


def test_master_records_all_half_counts_exactly(report):
    value = report["strict_master_decision"]
    assert value["all_half_pair_count"] == 256
    assert value["selected_half_pair_count"] == 64
    assert value["selected_zero_Y_pair_count"] == 1
    assert value["selected_zero_bilinear_count"] == 28
    assert value["selected_distinct_bilinear_classes"] == 7


def test_twice_y_uniqueness_is_not_quantum_half_uniqueness(report):
    value = report["strict_master_decision"]
    assert value["selected_twice_Y_row_unique"]
    assert not value["selected_twice_Y_row_unique_quantum_half"]


def test_relative_torsion_increment_is_not_full_wucs(report):
    value = report["strict_master_decision"]
    assert value["canonical_zero_half_primary_relative_torsion_increment_trivial"]
    assert not value["canonical_zero_half_full_baseline_WCS_phase_computed"]
    assert not value["canonical_zero_half_selected_by_parent_eta"]
    assert not value["Omega7_H78_computed"]
    assert not value["combined_anomaly_line_trivialized"]


def test_h4_explicit_block_is_rejected_without_overgeneralizing(report):
    value = report["strict_master_decision"]
    assert value["h4_translation_multiplicity_per_weight"] == 2
    assert value["explicit_h4_J_block_three_family_projector_rejected"]
    assert not value["all_h4_parent_actions_rejected"]
    assert not value["h6_or_h8_changed_parent_accepted"]


def test_theory_card_records_new_exact_gains(report):
    gains = report["consolidated_theory_card"]["exact_gains"]
    assert any("all 256 integral half-pairs" in item for item in gains)
    assert any("64 halves, one zero-Y half" in item for item in gains)
    assert any("ordinary-spin diagonal RP7" in item for item in gains)
    assert any("h4 repeated-J block rejected" in item for item in gains)


def test_theory_card_retires_only_invalid_shortcuts(report):
    rows = report["consolidated_theory_card"]["retired_shortcuts"]
    assert any("twice-Y correction" in item for item in rows)
    assert any("zero ordinary U bilinear" in item for item in rows)
    assert any("ordinary group cohomology" in item for item in rows)
    assert any("generalizing the explicit h4" in item for item in rows)


def test_next_action_prioritizes_h78_and_keeps_changed_parent_fallback(report):
    value = report["next_required_action"]
    assert value["id"] == "F80_H78_BORDISM_ETA_CAP_OR_H6_H8_PROJECTOR"
    assert "H78 Thom/bordism" in value["primary_objective"]
    assert "h6 and h8" in value["fallback_if_h0_falsified"]
    assert not value["accepted"]


def test_no_action_or_candidate_is_accepted(report):
    value = report["strict_master_decision"]
    assert not value["same_action_microscopic_completion_found"]
    assert not value["selected_candidate_accepted"]
    assert report["consolidated_theory_card"]["accepted_extension_count"] == 0
    assert value["current_action_status"] == "REJECTED"
    assert value["research_program_status"] == "VIABLE_NARROWED_FRONTIER"


def test_all_gates_remain_open(report):
    assert set(report["gate_ledger"]) == {f"G{i}" for i in range(1, 9)}
    assert all(value.startswith("OPEN") for value in report["gate_ledger"].values())
    value = report["strict_master_decision"]
    assert value["closed_gates"] == []
    assert not value["complete_theory"]


def test_source_manifest_is_inherited_from_route_and_primary(report):
    route = json.loads(audit.V79_ROUTE_PATH.read_text(encoding="utf-8"))
    assert report["source_manifest"] == route["source_manifest"]
    assert report["source_manifest"]["kind"] == "primary_sources_only"
    assert "guo_ohmori_putrov_wan_wang_2018" in report["source_manifest"]["ids"]
    assert "dierigl_tartaglia_2025" in report["source_manifest"]["ids"]


def test_regression_scope_names_both_v79_tests(report):
    files = report["regression_scope"]["new_test_files"]
    assert audit.TEST_PATH.name in files
    assert "test_susy_v79_torsion_half_refinement_h4_projector_audit.py" in files
    assert report["regression_scope"]["recommended_full_pattern"] == "test_susy_v*.py"


def test_report_core_is_canonical(report):
    assert audit.canonical_sha(report) == report["core_sha256"]


def test_generated_artifacts_are_fresh_when_present(report):
    if audit.OUT_JSON.is_file() and audit.OUT_MD.is_file():
        assert json.loads(audit.OUT_JSON.read_text(encoding="utf-8")) == report
        assert audit.OUT_MD.read_text(encoding="utf-8") == audit.render_markdown(report)
