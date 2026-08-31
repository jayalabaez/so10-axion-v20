import json

import pytest

import susy_v78_multipath_g1_frontier_master_audit as master


@pytest.fixture(scope="module")
def report():
    return master.build_report()


def test_v77_master_and_v78_route_are_canonical_and_bound(report):
    assert report["input_core_hashes"]["V77_master"] == master.EXPECTED_CORES["v77_master"]
    assert report["input_core_hashes"]["V78_route"] == master.EXPECTED_CORES["v78_route"]


def test_mutated_v78_route_is_rejected(tmp_path):
    route = json.loads(master.V78_ROUTE_PATH.read_text(encoding="utf-8"))
    route["status"] += "__MUTATED"
    path = tmp_path / "mutated.json"
    path.write_text(json.dumps(route), encoding="utf-8")
    with pytest.raises(RuntimeError, match="noncanonical parent core"):
        master.load_bound(path, master.EXPECTED_CORES["v78_route"])


def test_route_matrix_appends_exactly_one_unaccepted_b78_row(report):
    assert len(report["route_matrix"]) == report["lineage"]["parent_route_count"] + 1
    row = report["route_matrix"][-1]
    assert row["route_id"] == "B78"
    assert not row["same_action_microscopic_completion"]
    assert not row["accepted"]
    assert row["selected_open_candidates"] == [
        "F78_TADPOLE_FREE_H78",
        "F78_LEVEL_ONE_BRIDGE",
    ]


def test_acceptance_criteria_distinguish_exact_passes_from_open_action(report):
    rows = {row["id"]: row["status"] for row in report["acceptance_criteria"]}
    assert rows["A3"] == "PASS_REPAIRED"
    assert rows["A5"] == "PASS_EXACT"
    assert rows["A6"] == "PASS_ON_DEFINED_CATEGORY"
    assert rows["A8"] == "REJECTED_INCOMPLETE_FACTORIZATION"
    assert rows["A9"] == "PASS_EXACT"
    assert rows["A12"] == "PASS_EXACT"
    assert rows["A14"] == "PASS_7_AND_8"
    assert rows["A19"] == "SELECTED_OPEN"
    assert rows["A20"] == "OPEN_FAILED"


def test_theory_card_records_unique_tadpole_free_class(report):
    decision = report["strict_master_decision"]
    assert decision["ordinary_V77_isotropy_divisibility_repaired"]
    assert decision["selected_delta_twice_Y"] == ["r^2", "2r^2+s^2"]
    assert decision["selected_delta_unique_tadpole_free"]
    assert decision["selected_H78_class_integral"]
    assert decision["selected_H78_class_preserves_smooth_I8"]
    assert decision["canonical_flat_vacuum_internal_Y"] == ["0", "0"]


def test_exact_bosonic_bridge_is_not_called_supersymmetric(report):
    decision = report["strict_master_decision"]
    assert decision["level_one_bosonic_bridge_constructed"]
    assert not decision["supersymmetric_curved_bridge_constructed"]


def test_changed_parent_progress_is_scoped_exactly(report):
    decision = report["strict_master_decision"]
    assert decision["integrated_parent_row_count"] == 10
    assert decision["parity_allowed_changed_parent_rows"] == [2, 4, 6, 8]
    assert decision["even_half32_space_group_representation_constructed"]
    assert not decision["changed_parent_three_family_projector_constructed"]


def test_retired_shortcuts_include_old_false_terminal_and_new_overclaims(report):
    text = " ".join(report["consolidated_theory_card"]["retired_shortcuts"])
    assert "terminal" in text
    assert "three unrelated fixed-point" in text
    assert "curved p1(SU2R)" in text
    assert "even half-32" in text
    assert "larger odd normal charges" in text
    assert "bosonic bridge" in text


def test_next_action_targets_the_actual_global_completion(report):
    value = report["next_required_action"]
    assert value["id"] == "F79_H78_ANOMALY_LINE_HOLONOMY_AND_CAP_COMPLETION"
    assert "Dai--Freed" in value["objective"]
    assert "WuCS" in value["objective"]
    assert "cap" in value["objective"]
    assert "h=4" in value["fallback_if_falsified"]
    assert not value["accepted"]


def test_master_remains_fail_closed(report):
    decision = report["strict_master_decision"]
    assert not decision["bare_eta_selects_discrete_refinement"]
    assert not decision["shifted_WCS_Dai_Freed_cap_identity_proved"]
    assert not decision["same_action_microscopic_completion_found"]
    assert not decision["selected_candidate_accepted"]
    assert decision["current_action_status"] == "REJECTED"
    assert decision["research_program_status"] == "VIABLE_STRUCTURAL_FRONTIER"
    assert decision["closed_gates"] == []
    assert not decision["complete_theory"]


def test_all_eight_gates_remain_open(report):
    assert set(report["gate_ledger"]) == {f"G{i}" for i in range(1, 9)}
    assert all(value.startswith("OPEN") for value in report["gate_ledger"].values())


def test_regression_scope_includes_both_v78_tests(report):
    assert set(report["regression_scope"]["new_test_files"]) == {
        "test_susy_v78_multipath_g1_frontier_master_audit.py",
        "test_susy_v78_torsion_character_parent_redesign_audit.py",
    }
    assert report["regression_scope"]["recommended_full_pattern"] == "test_susy_v*.py"


def test_source_manifest_is_inherited_from_v78_route(report):
    route = json.loads(master.V78_ROUTE_PATH.read_text(encoding="utf-8"))
    assert report["source_manifest"] == route["source_manifest"]


def test_master_core_is_canonical(report):
    assert master.canonical_sha(report) == report["core_sha256"]


def test_generated_master_artifacts_are_fresh_when_present(report):
    if master.OUT_JSON.is_file() and master.OUT_MD.is_file():
        assert json.loads(master.OUT_JSON.read_text(encoding="utf-8")) == report
        assert master.OUT_MD.read_text(encoding="utf-8") == master.render_markdown(report)
