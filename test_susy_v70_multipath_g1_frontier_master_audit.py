from __future__ import annotations

import json

import susy_v70_multipath_g1_frontier_master_audit as audit


def report():
    return audit.build_report()


def routes():
    return {row["route_id"]: row for row in report()["route_matrix"]}


def candidates():
    return {row["id"]: row for row in routes()["B70"]["candidate_matrix"]}


def test_v70_master_canonical_recomputation_and_integrity():
    value = report()
    audit.validate(value)
    assert value["core_sha256"] == audit.canonical_sha(value)
    assert value["n_failed_integrity_checks"] == 0


def test_bound_input_cores_are_exact():
    assert report()["input_core_hashes"] == audit.EXPECTED_CORES
    assert report()["lineage"]["parent_V69_master_core"] == audit.EXPECTED_CORES["v69_master"]
    assert report()["lineage"]["V70_route_core"] == audit.EXPECTED_CORES["v70_route"]


def test_A60_C_and_complete_B69_lineage_are_preserved():
    value = routes()
    assert audit.object_sha(value["A60"]) == audit.V69_ROW_SHA["A60"]
    assert audit.object_sha(value["C"]) == audit.V69_ROW_SHA["C"]
    b = value["B70"]
    assert b["inherited_B69_row_sha256"] == audit.V69_ROW_SHA["B69"]
    assert audit.object_sha(b["inherited_B69_row"]) == audit.V69_ROW_SHA["B69"]


def test_only_F69_is_superseded_and_old_candidates_are_identical():
    b = routes()["B70"]
    old = [row for row in b["inherited_B69_row"]["candidate_matrix"] if row["id"] != "F69"]
    new = [row for row in b["candidate_matrix"] if row["id"] not in {"F70", "F70_ALT"}]
    assert old == new
    assert set(candidates()) == {"D67", "H66", "T66", "B3_IR", "E68", "F70", "F70_ALT"}


def test_integer_m301_is_selected_but_not_accepted():
    f70 = candidates()["F70"]
    assert f70["selected"]
    assert not f70["accepted"]
    assert not f70["same_action_complete"]
    assert f70["phase_assignment"] == "A:m=3, B:m=0, C:m=1"


def test_flavor_wilson_is_an_isolated_alternate():
    alternate = candidates()["F70_ALT"]
    assert not alternate["selected"]
    assert not alternate["accepted"]
    assert not alternate["same_action_complete"]
    assert "NO_ZERO_MODES" in alternate["spectator_status"]


def test_charged_spin_susy_and_higgs_passes_are_exactly_scoped():
    f70 = candidates()["F70"]
    assert f70["charged_spin_SUSY_lift"] == "PASS_EXACT_CLASSICAL_SUPERFIELD"
    assert f70["Higgs_spectrum"] == "PASS_EXACT_IN_BOTH_DISPLAYED_BRANCHES"
    assert f70["rank_and_Hessian"]["doublet_mass_rank"] == 1
    assert f70["rank_and_Hessian"]["driver_nondegeneracy"] == "det J != 0"


def test_charged_pointwise_and_4d_anomalies_vanish():
    f70 = candidates()["F70"]
    assert f70["pointwise_charged_anomaly_zero"]
    assert f70["four_dimensional_anomalies"]["all_perturbative_coefficients_zero"]
    assert f70["four_dimensional_anomalies"]["SU2_Witten"]["even"]


def test_smooth_bulk_quantization_and_positive_chamber_are_scoped():
    f70 = candidates()["F70"]
    quantization = f70["smooth_bulk_quantization"]
    chamber = f70["positive_tensor_chamber"]
    assert quantization["coefficient_quantization"] == "PASS_ON_THE_SMOOTH_BULK"
    assert quantization["unimodular_integral"]
    assert quantization["a_characteristic"]
    assert chamber["gauge_kinetic_positive_and_j_dot_a_positive"]
    assert not chamber["stabilized_tensor_vacuum"]


def test_required_neutral_global_quantum_and_phenomenology_obligations_stay_open():
    obligations = report()["consolidated_theory_card"]["open_obligations"]
    for term in ("266 neutral", "Green-Schwarz", "global Spin", "Z4R", "all-order", "KK", "soft spectrum"):
        assert any(term in item for item in obligations)


def test_regression_scope_is_exact():
    scope = report()["regression_scope"]
    assert scope["file_count"] == audit.EXPECTED_REGRESSION_FILES
    assert scope["test_count"] == audit.EXPECTED_REGRESSION_TESTS


def test_no_cross_route_splice_or_accepted_extension():
    value = report()
    rule = value["cross_route_composition_rule"]
    assert not rule["cross_route_splicing_allowed"]
    assert not rule["aggregated_gate_closure"]
    assert routes()["B70"]["accepted_extension_count"] == 0


def test_current_action_and_F70_are_fail_closed():
    decision = report()["strict_master_decision"]
    assert decision["current_Spin11_action_status"] == "REJECTED"
    assert not decision["F70_new_action_accepted"]
    assert not decision["same_action_microscopic_completion_found"]
    assert decision["closed_gates"] == []
    assert not decision["complete_theory"]


def test_all_acceptance_criteria_and_gates_remain_open():
    value = report()
    assert all(row["status"] == "OPEN" for row in value["acceptance_criteria"])
    assert all(row["status"] == "OPEN" and not row["V70_master_closed"] for row in value["gate_ledger"])


def test_generated_artifacts_match_when_present():
    value = report()
    if audit.JSON_PATH.is_file():
        assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == value
    if audit.MD_PATH.is_file():
        assert audit.MD_PATH.read_text(encoding="utf-8") == audit.render_markdown(value)
