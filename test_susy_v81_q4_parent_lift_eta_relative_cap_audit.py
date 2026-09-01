import json
from fractions import Fraction

import pytest

import susy_v81_q4_parent_lift_eta_relative_cap_audit as audit


@pytest.fixture(scope="module")
def report():
    value = audit.build_report()
    audit.validate_report(value)
    return value


def test_all_frozen_parent_cores_are_canonical_and_bound(report):
    rows = (
        (audit.V71_ROUTE_PATH, "v71_route", "V71_route_core"),
        (audit.V74_ROUTE_PATH, "v74_route", "V74_route_core"),
        (audit.V78_ROUTE_PATH, "v78_route", "V78_route_core"),
        (audit.V80_ROUTE_PATH, "v80_route", "V80_route_core"),
        (audit.V80_MASTER_PATH, "v80_master", "V80_master_core"),
    )
    for path, key, report_key in rows:
        value = json.loads(path.read_text(encoding="utf-8"))
        assert audit.canonical_sha(value) == value["core_sha256"]
        assert value["core_sha256"] == audit.EXPECTED_CORES[key]
        assert report["lineage"][report_key] == audit.EXPECTED_CORES[key]


def test_mutated_parent_with_old_core_is_rejected(tmp_path):
    value = json.loads(audit.V80_ROUTE_PATH.read_text(encoding="utf-8"))
    value["status"] += "_MUTATED"
    path = tmp_path / "mutated.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(RuntimeError, match="noncanonical parent core"):
        audit.load_bound(path, audit.EXPECTED_CORES["v80_route"])


def test_exact_q4_eta_table_and_detector_are_recomputed():
    table = [audit.q4_dirac_eta(m) for m in range(4)]
    assert table == [
        Fraction(-1, 8),
        Fraction(1, 8),
        Fraction(1, 8),
        Fraction(-1, 8),
    ]
    assert table[1] - table[0] == Fraction(1, 4)
    assert audit.q4_dirac_eta(4) == audit.q4_dirac_eta(0)


def test_universal_center_lift_contract_is_explicit_but_not_promoted(report):
    value = report["cyclic_parent_group_candidate_audit"]
    criterion = value["universal_criterion"]
    assert "image of H^2(Q4;K_rho)" in criterion["lift_condition"]
    assert "every center character chi" in criterion["character_form"]
    candidate = value["minimal_cyclic_diagonal_candidate"]
    assert candidate["tuple_fourth_power_is_candidate_kernel_generator"]
    assert not candidate["primary_degree2_obstruction_seen_in_recorded_roots"]
    assert not value["full_HGamma_defined"]
    assert not value["all_field_and_ghost_representations_descend"]
    assert not value["full_parent_Q4_lift_constructed"]


def test_qhat_and_v80_basepoint_stable_bundles_are_distinct(report):
    value = report["structured_Q4_direct_lift_audit"]
    assert value["V80_split_basepoint"]["F_E"].endswith("R^11 stably")
    qhat = value["physical_five_plane_qhat"]
    assert qhat["stable_spin_bundle"] == "F_E,qhat=R^3+4(L_r)_R"
    assert qhat["chern_class"] == "c2(4L_r)=C(4,2)r^2=6r^2"
    assert qhat["lambda_F_E"] == "2r^2"
    assert qhat["lambda_nonzero"]
    assert value["cohomology_input"]["nonzero_class"] == "2r^2 != 0"


def test_direct_flat_lift_is_rejected_without_overclaiming_general_no_go(report):
    value = report["structured_Q4_direct_lift_audit"]["comparison"]
    assert not value["same_reduced_structured_background"]
    assert not value["direct_flat_qhat_lift_of_V80_split_representative_exists"]
    assert value["qhat_decorated_Q4_is_a_separate_reduced_H78_background"]
    assert value["qhat_decorated_Q4_bordism_order_and_filtration"] == "OPEN_UNCOMPUTED"
    assert not value["general_full_parent_lift_rejected"]
    repair = report["structured_Q4_direct_lift_audit"]["same_projector_nonflat_repair"]
    assert repair["required_compensator"].endswith("lambda=2r^2")
    assert repair["characteristic_shift"] == "Delta lambda=2r^2 is necessary"
    assert not repair["fixed_rank_equivariant_realization_follows_from_bookkeeping"]
    assert not repair["constructed"]


def test_one_plane_flat_alternative_is_a_changed_projector(report):
    value = report["structured_Q4_direct_lift_audit"]["one_plane_flat_alternative"]
    assert value["matches_V80_basepoint"]
    assert value["centralizer"] == "SO(9)xSO(2)"
    assert not value["preserves_required_U5_fixed_group"]
    assert value["verdict"] == "REJECTED_CHANGED_PROJECTOR_AND_ACTION"


def test_v80_basepoint_is_not_in_source_free_Y_zero_domain(report):
    geometry = report["Q4_source_domain_audit"]["Q4_tangent_geometry"]
    assert geometry["cohomology"] == "H^4(Q4;Z)=Z4{r^2}+Z4{rx}"
    assert geometry["orders"] == {"r^2": 4, "rx": 4}
    assert geometry["lambda_W"].endswith("2r^2+2rx")
    assert geometry["qT"] == "lambda(W)-r^2=r^2+2rx"
    assert geometry["qT_nonzero"]
    assert geometry["qT_restriction_to_L45"] == "r^2 != 0"
    value = report["Q4_source_domain_audit"]["V80_basepoint_restriction"]
    assert value["p1_E"] == "r^2"
    assert value["qT"] == "r^2+2rx"
    assert value["qTE"] == "2r^2+2rx"
    assert value["Y_restriction"] == ["r^2+2rx", "3r^2+2rx"]
    assert not value["simultaneous_Y_zero_possible"]
    assert value["both_components_nonzero"]
    assert not value["admissible_in_source_free_Y_zero_category"]
    assert value["physical_test_requires_D15_source_worldsheet_sector"]


def test_qhat_source_domain_is_equalized_but_exactly_nonzero(report):
    value = report["Q4_source_domain_audit"]["qhat_decorated_restriction"]
    assert value["p1_E"] == "5r^2"
    assert value["lambda_F_E"] == "2r^2"
    assert value["qTE_relation"] == "qTE=qT+3r^2"
    assert value["qTE"] == "2rx"
    assert value["Y_restriction"] == ["r^2+2rx", "r^2+2rx"]
    assert value["qhat_equalizes_Y_components"]
    assert not value["admissible_in_source_free_Y_zero_category"]
    assert value["qT_on_qhat_decorated_Q4_evaluated"]
    assert value["source_free_verdict"] == "REJECTED_SOURCE_REQUIRED"
    assert report["Q4_source_domain_audit"]["D15_status"] == "ABSENT"


def test_v71_qhat_eta_shadow_is_exact(report):
    value = report["Q4_eta_shadow_audit"]["V71_qhat_projector_character_shadow"]
    assert value["three_11_intrinsic_m"] == [3, 0, 1]
    assert value["three_11_eta_shadow"] == "-1/8"
    assert value["neutral_266_counts_m0123"] == [74, 64, 64, 64]
    assert value["neutral_266_eta_shadow"] == "-5/4"
    assert value["adjoint_same_chirality_eta_shadow"] == "-5/8"
    assert value["opposite_chirality_gaugino_eta_shadow"] == "5/8"
    assert value["formal_spin_half_matter_plus_gaugino_shadow"] == "-3/4"
    assert value["formal_eta_shadow_mod1"] == "1/4"


def test_eta_shadow_is_never_promoted_to_physical_parent_phase(report):
    value = report["Q4_eta_shadow_audit"]
    theorem = value["nonidentification_theorem"]
    assert not theorem["shadow_is_physical_A_bare"]
    assert not theorem["shadow_is_A_bare_times_WCS"]
    assert not theorem["shadow_selects_t0"]
    assert len(theorem["reasons"]) == 6
    assert not value["flat_character_ambiguity"]["t0_determines_WCS_on_Q4"]
    assert not value["physical_parent_phase_evaluated"]


def test_relative_category_and_cap_contract_are_correctly_typed(report):
    value = report["relative_stratified_cap_audit"]
    assert value["minimum_category"]["symbol"].startswith("C81=Bord_(7,6,5)")
    assert not value["minimum_category"]["constructed"]
    split = value["correct_functorial_split"]
    assert split["pre_cap_functor"].startswith("A_pre=A_bare tensor WCS")
    assert "tau:A_pre=>1" in split["cap_role"]
    assert "one cap supplies one state" in split["cap_role"]
    assert not split["cap_is_arbitrary_inverse_factor"]
    assert split["formal_inverse_cap_verdict"] == "REJECTED_TAUTOLOGICAL_ACTION_CHANGE"
    assert len(value["cap_existence_and_independence_contract"]) == 7


def test_existing_bridge_witnesses_remain_exact_and_scoped(report):
    value = report["relative_stratified_cap_audit"]["exact_existing_bridge_witnesses"]
    assert value["class"] == "r=nu A B"
    assert value["ordinary_CP2xCP1_period"] == 1
    assert value["spin_S2cubed_period"] == 2
    assert value["ordinary_level_one_quantized"]
    assert value["endpoint_diagonal_values"] == {"z00": 6, "z11": -6}
    assert value["localized_source"] == "J2=PD(boundary(gamma))=delta11-delta00"
    assert "not parent bordism generators" in value["scope"]


def test_caps_are_not_attached_to_smooth_q4_and_no_cap_is_invented(report):
    value = report["relative_stratified_cap_audit"]
    assert not value["smooth_Q4_rule"]["bridge_or_cap_inserted_on_smooth_empty_strata_Q4"]
    assert value["smooth_Q4_rule"]["can_appear_as_cap_double_after_parent_and_D15_completion"]
    assert "worldsheet anomaly factor" in value["smooth_Q4_rule"]["source_completed_factor"]
    assert not value["cap_sector_constructed"]
    assert not value["cap_choice_independence_evaluated"]
    assert not value["total_relative_identity_well_typed"]
    rows = {row["id"]: row for row in value["route_matrix"]}
    assert rows["R81_3"]["status"] == "PASS_EXACT_SCOPED"
    assert rows["R81_8"]["status"] == "ABSENT"
    assert rows["R81_11"]["status"] == "ILL_TYPED"


def test_completion_contract_keeps_D15_and_relative_data_absent(report):
    rows = {row["id"]: row for row in report["updated_input_contract"]}
    assert rows["D5"]["status"] == "PARTIAL_CYCLIC_CENTER_CRITERION_ONLY"
    assert rows["D9"]["status"] == "PARTIAL_RECORDED_LOCAL_ROOTS_ONLY"
    assert rows["D10"]["status"] == "ABSENT"
    assert rows["D12"]["status"] == "PARTIAL_INTEGRAL_CLASS_ONLY"
    assert rows["D15"]["status"] == "ABSENT"
    assert rows["D16"]["status"] == "ABSENT"
    assert rows["D17"]["status"] == "ABSENT"


def test_candidate_matrix_selects_only_open_construction_targets(report):
    rows = {row["id"]: row for row in report["candidate_matrix"]}
    assert rows["F81B_DIRECT_CURRENT_QHAT_FLAT_LIFT_OF_SPLIT_Q4"]["result"] == "REJECTED_LAMBDA_2R2"
    assert rows["F81D_NONFLAT_Q1_COMPENSATOR"]["selected"]
    assert rows["F81E_QHAT_DECORATED_Q4_AS_DISTINCT_TEST"]["selected"]
    assert rows["F81F_ETA_SHADOW_AS_PHYSICAL_BARE_PHASE"]["result"].startswith("REJECTED")
    assert rows["F81H_FORMAL_INVERSE_CAP"]["result"] == "REJECTED_TAUTOLOGICAL_ACTION_CHANGE"
    assert report["candidate_adjudication"]["accepted_ids"] == []


def test_terminal_decision_is_strictly_fail_closed(report):
    value = report["terminal_decision"]
    assert value["direct_flat_qhat_lift_of_split_Q4_rejected"]
    assert not value["general_compensated_full_parent_lift_rejected"]
    assert not value["general_compensated_full_parent_lift_constructed"]
    assert value["qhat_decorated_Q4_is_separate_reduced_background"]
    assert not value["qhat_decorated_Q4_bordism_class_computed"]
    assert not value["V80_basepoint_admissible_source_free"]
    assert not value["physical_A_bare_times_WCS_evaluated"]
    assert not value["accepted_full_parent_action_exists"]
    assert value["current_action_status"] == "REJECTED"
    assert value["closed_gates"] == []
    assert not value["theory_complete"]
    assert all(status.startswith("OPEN") for status in report["gate_ledger"].values())


def test_next_action_targets_the_exact_remaining_fork(report):
    value = report["next_required_action"]
    assert value["id"] == "F82_QHAT_Q4_CLASS_NONFLAT_COMPENSATOR_AND_PARENT_INCIDENCE_CATEGORY"
    assert "qhat-decorated" in value["primary_objective"]
    assert "lambda=2r^2" in value["primary_objective"]
    assert "define K and Gammahat" in value["parent_objective"]
    assert "Bord_(7,6,5)" in value["relative_objective"]
    assert not value["accepted"]


def test_source_manifest_contains_the_primary_q4_and_anomaly_sources(report):
    ids = report["source_manifest"]["ids"]
    assert "debray_dierigl_heckman_montero_2023" in ids
    assert "dai_freed_1994" in ids
    assert "monnier_2016" in ids
    assert "monnier_moore_2018" in ids
    assert "muller_2020" in ids
    assert report["source_manifest"]["count"] == len(report["primary_sources"])


def test_build_is_deterministic(report):
    second = audit.build_report()
    assert second == report
    assert audit.canonical_sha(second) == second["core_sha256"]


def test_generated_artifacts_are_fresh(report):
    audit.check_artifacts(report)
