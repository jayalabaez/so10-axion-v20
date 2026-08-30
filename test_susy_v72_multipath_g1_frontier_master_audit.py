from __future__ import annotations

import json

import susy_v72_multipath_g1_frontier_master_audit as audit


def report():
    return audit.build_report()


def routes():
    return {row["route_id"]: row for row in report()["route_matrix"]}


def candidates():
    return {row["id"]: row for row in routes()["B72"]["candidate_matrix"]}


def test_v72_master_canonical_recomputation_and_integrity():
    value = report()
    audit.validate(value)
    assert value["core_sha256"] == audit.canonical_sha(value)
    assert value["n_failed_integrity_checks"] == 0


def test_bound_input_cores_are_exact():
    value = report()
    assert value["input_core_hashes"] == audit.EXPECTED_CORES
    assert value["lineage"]["parent_V71_master_core"] == audit.EXPECTED_CORES["v71_master"]
    assert value["lineage"]["V72_route_core"] == audit.EXPECTED_CORES["v72_route"]


def test_A60_C_and_complete_B71_lineage_are_preserved():
    value = routes()
    assert audit.object_sha(value["A60"]) == audit.V71_ROW_SHA["A60"]
    assert audit.object_sha(value["C"]) == audit.V71_ROW_SHA["C"]
    b = value["B72"]
    assert b["inherited_B71_row_sha256"] == audit.V71_ROW_SHA["B71"]
    assert audit.object_sha(b["inherited_B71_row"]) == audit.V71_ROW_SHA["B71"]


def test_only_F71_conventional_completion_is_superseded():
    b = routes()["B72"]
    old = [row for row in b["inherited_B71_row"]["candidate_matrix"] if row["id"] != "F71"]
    new = [row for row in b["candidate_matrix"] if row["id"] not in {"F71", "F72"}]
    assert old == new
    assert b["superseded_candidate_ids"] == ["F71"]
    assert set(candidates()) == {"D67", "H66", "T66", "B3_IR", "E68", "F71", "F72"}


def test_F71_local_rep_is_honest_but_conventional_completion_is_rejected():
    f71 = candidates()["F71"]
    assert f71["local_representation_is_honest"]
    assert not f71["selected"]
    assert not f71["accepted"]
    assert not f71["same_action_complete"]
    assert not f71["total_spin_R_multiplet_and_orbibundle_constructed"]
    assert not f71["additional_new_bridge_physics_excluded_by_the_no_go"]
    assert "does not prove" in f71["scope_clause"]


def test_F71_mass_anomaly_and_all_order_portal_theorems_are_bound():
    f71 = candidates()["F71"]
    audit_data = f71["mass_and_portal_theorems"]
    mass = audit_data["mass_anomaly_matching_theorem"]
    assert mass["strict_W_mass_condition"] == "r_i+r_j=1"
    assert mass["opposite_q_partners_erase_repair"]
    assert not mass["full_rank_trivially_gapped_sector_nonzero_U1L_X2_anomaly"]
    portal = audit_data["all_order_nonderivative_chiral_portal_theorem"]
    assert not portal["nonderivative_local_chiral_W_or_K_portal_at_any_order"]
    assert portal["lightest_charge_five_state_stable"]
    assert "nonlocal interactions" in portal["scope"]
    assert f71["exact_V72_adjudication"]["F71_conventional_massive_decaying_completion"].startswith("REJECTED")


def test_F71_relic_claim_is_scoped_and_collider_benchmark_is_not_overread():
    pheno = candidates()["F71"]["phenomenology"]
    relic = pheno["stable_charged_relic"]
    assert relic["lightest_state_stable_without_portal"]
    assert not relic["thermal_freezeout_yield_computed"]
    assert relic["standard_thermal_history_viability"] == "OPEN_NOT_COMPUTED"
    assert "conditional only" in relic["low_reheat_loophole"]
    assert relic["CMS_one_species_Q1_DY_observed_limit_TeV"] == "1.14"
    assert relic["two_species_recast_required"]


def test_F72_is_selected_but_not_accepted():
    f72 = candidates()["F72"]
    assert f72["selected"]
    assert not f72["accepted"]
    assert not f72["same_action_complete"]
    assert f72["supersedes_candidates"] == ["F71"]


def test_F72_opposite_U5tilde_restricted_coefficients_and_alignment_are_exact():
    f72 = candidates()["F72"]
    quant = f72["U5tilde_restricted_local_coefficient_integrality"]
    assert quant["line_class"] == "l=c1(chi5)=5 f_X"
    assert quant["restricted_coefficients"] == {"z00": 1, "z11": -1}
    assert quant["restricted_denominator"] == 1
    assert quant["coefficient_sum"] == 0
    assert not quant["full_diagonal_quotient_level_quantization_established"]
    assert f72["both_corners_align"]
    assert f72["z00"]["final_vector"] == ["-1/4", "-10"]
    assert f72["z11"]["final_vector"] == ["-1/4", "-10"]


def test_F72_has_no_new_charged_exotic_or_SM_running_shift():
    advantage = candidates()["F72"]["advantages_over_F71_charge_five_fermions"]
    assert advantage["new_electrically_charged_fields"] == 0
    assert advantage["new_one_loop_SM_beta_shift"] == {"b1": "0", "b2": "0", "b3": "0"}
    assert advantage["no_new_F71_type_stable_charged_relic"]


def test_F72_zero_sum_is_necessary_not_sufficient():
    f72 = candidates()["F72"]
    profile = f72["globally_vanishing_profile"]
    assert profile["passes_necessary_sum_rule"]
    assert not profile["sufficient_for_global_differential_cocycle"]
    joined = " ".join(f72["required_new_data"])
    for term in ("supersymmetric", "P0", "quotient", "differential-cohomology", "Dai-Freed"):
        assert term in joined


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
    assert routes()["B72"]["accepted_extension_count"] == 0


def test_current_action_F72_and_all_gates_are_fail_closed():
    value = report()
    decision = value["strict_master_decision"]
    assert decision["current_Spin11_action_status"] == "REJECTED"
    assert not decision["F71_conventional_completion_accepted"]
    assert not decision["F72_new_action_accepted"]
    assert decision["F72_selected_for_next_frontier"]
    assert not decision["same_action_microscopic_completion_found"]
    assert decision["closed_gates"] == []
    assert not decision["complete_theory"]
    assert all(row["status"].startswith("OPEN") for row in value["acceptance_criteria"])
    assert all(row["status"] == "OPEN" and not row["V72_master_closed"] for row in value["gate_ledger"])


def test_generated_artifacts_are_required_and_match():
    value = report()
    assert audit.JSON_PATH.is_file()
    assert audit.MD_PATH.is_file()
    assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == value
    assert audit.MD_PATH.read_text(encoding="utf-8") == audit.render_markdown(value)
