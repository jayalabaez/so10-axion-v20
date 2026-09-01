import copy
import json

import pytest

import susy_v80_h78_category_ahss_flat_parent_no_go_audit as audit


@pytest.fixture(scope="module")
def report():
    value = audit.build_report()
    audit.validate_report(value)
    return value


def test_all_frozen_parent_cores_are_canonical_and_bound(report):
    paths = {
        "v70_route": audit.V70_ROUTE_PATH,
        "v77_route": audit.V77_ROUTE_PATH,
        "v78_route": audit.V78_ROUTE_PATH,
        "v79_route": audit.V79_ROUTE_PATH,
        "v79_master": audit.V79_MASTER_PATH,
    }
    lineage = {
        "v70_route": "V70_route_core",
        "v77_route": "V77_route_core",
        "v78_route": "V78_route_core",
        "v79_route": "V79_route_core",
        "v79_master": "V79_master_core",
    }
    for key, path in paths.items():
        value = json.loads(path.read_text(encoding="utf-8"))
        assert audit.canonical_sha(value) == value["core_sha256"]
        assert value["core_sha256"] == audit.EXPECTED_CORES[key]
        assert report["lineage"][lineage[key]] == audit.EXPECTED_CORES[key]


def test_mutated_parent_with_old_core_is_rejected(tmp_path):
    value = json.loads(audit.V79_ROUTE_PATH.read_text(encoding="utf-8"))
    value["status"] += "_MUTATED"
    path = tmp_path / "mutated.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(RuntimeError, match="noncanonical parent core"):
        audit.load_bound(path, audit.EXPECTED_CORES["v79_route"])


def test_h78_is_homotopy_fiber_of_exactly_two_obstructions(report):
    topology = report["smooth_reduced_H78_Thom_AHSS_audit"]
    value = topology["bulk_classifying_space"]
    assert topology["scope"]["structure"] == "reduced GS/tangential H78"
    assert not topology["scope"]["is_full_parent_bordism_problem"]
    assert value["definition"] == "BH78=hofib_0(F)"
    assert value["obstruction_map"].startswith("F=(w2(T)+y")
    assert value["nullhomotopies"] == [
        "Spin^c lift of T with determinant L_r",
        "Spin^c lift of T+E with determinant L_s",
    ]
    assert value["derived_relation"] == "w2(E)=y+b"
    assert not value["third_independent_nullhomotopy_imposed"]
    assert value["Thom_spectrum"] == "MTH78=Th(BH78;-theta)"
    assert value["smooth_reduced_bulk_defined"]
    assert not value["full_parent_HGamma_defined"]
    assert not value["stratified_orbifold_extension_defined"]


def test_stable_spin_presentation_and_spin_z8_factor_are_explicit(report):
    value = report["smooth_reduced_H78_Thom_AHSS_audit"][
        "stable_low_degree_presentation"
    ]
    assert value["spin_tangent_bundle"] == "W=T+(L_r)_R"
    assert value["spin_gauge_bundle"] == "F_E=E+(L_s)_R-(L_r)_R"
    assert value["through_degree"] == 8
    assert "MSpin-Z8" in value["Spin_Z8_factorization"]
    assert value["d2_cohomology_operator"] == (
        "D=Sq^2+y cup after mod-2 reduction"
    )


def test_mod2_bases_have_the_exact_low_degree_dimensions(report):
    assert [len(audit.bg_basis(n)) for n in range(9)] == list(range(1, 10))
    mod2 = report["smooth_reduced_H78_Thom_AHSS_audit"]["mod2_calculation"]
    assert mod2[
        "active_basis_dimensions"
    ] == {
        "X3": 4,
        "X4": 6,
        "X5": 8,
        "X6": 11,
        "X7": 15,
        "X8": 19,
    }
    assert mod2["degree8_passive_BSpin_generators"] == ["u^2", "w8"]
    assert mod2["full_X8_dimension"] == 21
    assert all(audit.term_degree(term) == 7 for term in audit.x_basis(7))


def test_D_on_X4_matches_the_exact_ordered_image_list():
    images = audit.map_images(audit.D_image, 4)
    expected = (
        frozenset({("1", 0, 1, 4)}),
        frozenset({("1", 0, 1, 4)}),
        frozenset({("1", 0, 3, 0)}),
        frozenset({("1", 1, 1, 3), ("1", 1, 0, 5)}),
        frozenset(),
        frozenset({("v", 0, 0, 0), ("u", 0, 1, 0)}),
    )
    assert images == expected
    assert audit.vector_rank(images) == 4


def test_all_d2_linear_algebra_ranks_are_recomputed_exactly(report):
    value = report["smooth_reduced_H78_Thom_AHSS_audit"]["mod2_calculation"]
    assert value["ranks"] == {
        "rank_D_X4_to_X6": 4,
        "rank_D_X5_to_X7": 6,
        "rank_D_X6_to_X8": 7,
        "rank_Sq1_X6_to_X7": 5,
        "rank_Sq1_X7_to_X8": 8,
        "rank_span_D5_plus_Sq1_6": 10,
        "rank_span_D6_plus_Sq1_7": 13,
    }
    assert value["q0_outgoing_d2_rank"] == 5
    assert value["q0_incoming_d2_rank"] == 5


def test_integral_E2_7_0_kernel_has_exact_Z4_plus_Z2_5_structure(report):
    value = report["smooth_reduced_H78_Thom_AHSS_audit"]["mod2_calculation"][
        "integral_E2_7_0_kernel"
    ]
    assert value["ordered_generators"] == [
        "a7_2",
        "ya5_2",
        "y2a3_2",
        "y3a_2",
        "xy3_4",
        "ua3_2",
        "uya_2",
        "uxy_4",
        "va_2",
        "vx_2",
    ]
    assert value["d2_rank"] == 5
    assert value["source_order_power_of_two"] == 12
    assert value["kernel_order_power_of_two"] == 7
    assert value["orders"]["xy3_4"] == value["orders"]["uxy_4"] == 4
    assert value["d2_outputs_in_dual_X5_basis"]["uxy_4"] == [8]
    assert value["d2_outputs_in_dual_X5_basis"]["vx_2"] == [8]
    assert value["order4_kernel_witness"] == "uxy_4+vx_2"
    assert value["kernel_structure"] == "Z4 + Z2^5"


def test_mixed_y2a3_class_is_not_in_the_early_image(report):
    candidate = frozenset({("1", 0, 2, 3)})
    early = audit.map_images(audit.D_image, 5) + audit.map_images(
        audit.sq1_image, 6
    )
    assert not audit.vector_in_span(candidate, early)
    value = report["smooth_reduced_H78_Thom_AHSS_audit"]["mixed_class_E3_probe"]
    assert value["class"] == "c=y^2 a^3"
    assert not value["in_image_D_X5_plus_Sq1_X6"]
    assert value["pairs_with_an_E3_7_0_survivor"]
    assert value["survival_proved_through"] == "E3"
    assert value["E_infinity_status"] == "UNRESOLVED"
    assert not value["bordism_obstruction_claimed"]


def test_total_degree_seven_E2_and_E3_pages_are_exact(report):
    value = report["smooth_reduced_H78_Thom_AHSS_audit"]
    assert value["total_degree7_E2"] == {
        "E2_7_0": "Z4^2 + Z2^8",
        "E2_6_1": "Z2^11",
        "E2_5_2": "Z2^8",
        "E2_3_4": "Z4 + Z2^2",
        "E2_7_0_kunneth": [
            "H7(BG)=Z4+Z2^4",
            "H4(BSpin11) tensor H3(BG)=Z4+Z2^2",
            "H6(BSpin11) tensor H1(BG)=Z2^2",
        ],
    }
    e3 = value["total_degree7_E3"]
    assert (e3["E3_7_0"], e3["E3_6_1"], e3["E3_5_2"], e3["E3_3_4"]) == (
        "Z4 + Z2^5",
        "Z2^2",
        "Z2^2",
        "Z4 + Z2^2",
    )
    assert e3["total_order"] == 2**15
    assert not e3["later_differentials_resolved"]
    assert not e3["extensions_resolved"]
    assert not e3["Omega7_H78_computed"]


def test_published_spin_z8_factor_proves_only_a_split_z4(report):
    value = report["smooth_reduced_H78_Thom_AHSS_audit"]["known_bordism_direct_summand"]
    assert value["group"] == "Z4"
    assert value["origin"] == "Omega_7^(Spin-Z8)(pt)"
    assert "structured Spin-Z8 pair" in value["generator"]
    assert "Q_4^7" in value["generator"]
    assert value["detecting_invariant"].endswith("=1/4 mod Z")
    assert not value["evaluated_for_the_V80_parent_field_content"]
    assert value["associated_graded_filtration_placement"] == "UNRESOLVED"
    assert not value["full_parent_HGamma_lift_constructed"]
    assert not value["is_currently_a_full_parent_test_generator"]
    assert report["terminal_decision"]["reduced_Omega7_H78_split_Z4_proved"]
    assert not report["terminal_decision"]["reduced_Omega7_H78_computed"]


def test_common_stratified_anomaly_identity_is_not_well_typed(report):
    value = report["typed_H0_anomaly_contract_audit"]
    assert value["status"] == (
        "NON_IDENTIFIABLE_FROM_EXISTING_H0_DATA__TOTAL_IDENTITY_ILL_TYPED"
    )
    assert value["required_common_category"]["symbol"] == (
        "C80=Bord_(7,6)^{H_Gamma^parent,strat}(checkY78,t=0)"
    )
    assert value["required_common_category"]["forgetful_map"].startswith(
        "H_Gamma^parent,strat -> reduced GS/tangential H78"
    )
    assert value["required_common_category"]["specified_as_completion_target"]
    assert not value["required_common_category"]["constructed_from_current_action"]
    assert all(not row["functor_on_C80_defined"] for row in value["factors"])
    typing = value["typing_decision"]
    assert not typing["common_stratified_domain_defined"]
    assert not typing["total_natural_isomorphism_defined"]
    assert not typing["total_phase_evaluated_on_generators"]
    assert not typing["identity_currently_well_formed"]
    assert not typing["identity_currently_evaluable"]
    assert "Z_bare Z_WCS=1" in value["smooth_empty_strata_reduction"]


def test_canonical_t0_half_is_distinguished_but_not_selected(report):
    value = report["typed_H0_anomaly_contract_audit"]["canonical_half"]
    assert value["selected_twice_Y_half_count"] == 64
    assert value["strict_zero_internal_half_count"] == 1
    assert value["canonical_zero_internal_half_distinguished"]
    assert value["canonical_flat_product_Y"] == ["lambda4", "lambda4"]
    assert not value["full_checkY_globally_zero"]
    assert not value["unique_global_differential_refinement"]
    assert value["relative_t0_action_shift_mod1"] == "0"
    assert value["relative_t0_phase_ratio"] == "1"
    assert not value["baseline_q_Arf_eta_cap_phase_known"]
    assert not value["parent_eta_selection_computed"]
    assert not value["canonical_half_falsified"]
    assert not value["canonical_half_accepted"]


def test_D14_is_partial_and_D15_is_globally_absent(report):
    rows = {
        row["id"]: row
        for row in report["typed_H0_anomaly_contract_audit"][
            "updated_input_contract"
        ]
    }
    assert rows["D14"]["status"] == "PARTIAL"
    assert "conditional differential ansatz" in rows["D14"]["input"]
    assert "canonical differential refinement" in rows["D14"]["input"]
    assert rows["D15"]["status"] == "ABSENT"
    assert rows["D5"]["status"] == "ABSENT"
    assert rows["D10"]["status"] == "ABSENT"
    assert rows["D12"]["status"] == "ABSENT"


def test_flat_nonidentifiability_is_not_overclaimed(report):
    value = report["typed_H0_anomaly_contract_audit"][
        "flat_non_identifiability"
    ]
    assert value["space_group_flat_character_count"] == 8
    reduced = value["reduced_smooth_statement"]
    assert reduced["proved_bordism_summand"] == "Z4"
    assert reduced["flat_character_count_on_split_summand"] == 4
    assert not reduced["Q4_reduced_phase_pinned_by_current_data"]
    assert not reduced["extension_to_full_parent_HGamma_category_proved"]
    parent = value["full_parent_stratified_statement"]
    assert parent["closed_flat_difference_group"].startswith("Hom(Omega_7")
    assert not parent["B_over_S_nonzero_proved"]
    assert not parent["physical_parent_flat_ambiguity_proved"]
    assert not value["local_data_uniquely_determine_eta"]


def test_formal_inverse_cap_is_not_promoted_to_physics(report):
    value = report["typed_H0_anomaly_contract_audit"]["cap_criterion"]
    assert "every closed allowed full-parent cycle" in value["necessary_closed_cycle_test"]
    assert "junction coherence" in value["relative_test"]
    assert value["cap_choice_independence"] == "Z_tot(C union -C_prime)=1"
    assert "reference states" in value["nonbounding_Omega6_components"]
    assert not value["formal_inverse_cap_is_physical_construction"]


def test_spinor_weight_table_is_exhaustive_and_dimensionally_exact(report):
    rows = report["flat_changed_parent_projector_audit"]["weight_formula"]["rows"]
    assert len(rows) == 12
    assert sum(row["degeneracy"] for row in rows) == 32
    assert sum(row["degeneracy"] for row in rows if row["chirality"] == "16") == 16
    assert sum(row["degeneracy"] for row in rows if row["chirality"] == "bar16") == 16
    assert {(row["a"], row["l"]) for row in rows} == {
        (a, l) for a in range(3) for l in range(4)
    }


def test_key_joint_character_rows_match_rank_breaking_pairs(report):
    rows = report["flat_changed_parent_projector_audit"]["weight_formula"]["rows"]
    by_al = {(row["a"], row["l"]): row for row in rows}
    assert (by_al[(0, 0)]["degeneracy"], by_al[(0, 0)]["qhat"], by_al[(0, 0)]["what"]) == (
        1,
        "zeta^5",
        "-i",
    )
    assert (by_al[(2, 2)]["degeneracy"], by_al[(2, 2)]["qhat"], by_al[(2, 2)]["what"]) == (
        3,
        "zeta^5",
        "-i",
    )
    assert (by_al[(2, 3)]["degeneracy"], by_al[(2, 3)]["qhat"], by_al[(2, 3)]["what"]) == (
        1,
        "zeta^3",
        "+i",
    )
    assert (by_al[(0, 1)]["degeneracy"], by_al[(0, 1)]["qhat"], by_al[(0, 1)]["what"]) == (
        3,
        "zeta^3",
        "+i",
    )


def test_repeated_J_tau_spectrum_and_h6_h8_failure_are_exact(report):
    value = report["flat_changed_parent_projector_audit"]["repeated_J_block"]
    assert value["per_block_spectrum"] == {
        "+1": {"16": 6, "bar16": 6, "total": 12},
        "+i": {"16": 4, "bar16": 4, "total": 8},
        "-1": {"16": 2, "bar16": 2, "total": 4},
        "-i": {"16": 4, "bar16": 4, "total": 8},
    }
    assert value["minimum_two_half_hyper_blocks"] == 12
    assert value["minimum_h"] == 24
    assert value["h6_block_count"] == 3
    assert value["h8_block_count"] == 4
    assert not value["h6_three_complete_16s"]
    assert not value["h8_three_complete_16s"]


def test_general_flat_bound_closes_the_integrated_half32_family(report):
    value = report["flat_changed_parent_projector_audit"][
        "general_flat_flavor_bound"
    ]
    assert value["p_minimum"] == 6
    assert value["h_minimum"] == 12
    assert value["integrated_neutral_count"] == "n0=266-27h"
    assert value["integrated_h_maximum"] == 9
    assert not value["bounds_compatible"]
    assert value["h6_rejected"]
    assert value["h8_rejected"]
    assert value["all_integrated_family_rows_rejected_for_bulk_three_families"]


def test_QW_projectors_cannot_isolate_the_rank_breaking_pair(report):
    value = report["flat_changed_parent_projector_audit"][
        "rank_breaking_joint_character_obstruction"
    ]
    assert value["nu_c"]["joint_character"] == value[
        "inseparable_color_partner"
    ]["joint_character"]
    assert value["bar_nu_c"]["joint_character"] == value[
        "inseparable_conjugate_color_partner"
    ]["joint_character"]
    assert not value["clean_D_flat_rank_pair_from_QW_projectors"]
    assert "additional gauge-dependent" in value["required_new_structure"]


def test_h6_and_h8_fail_the_frozen_positive_tensor_chamber(report):
    value = report["flat_changed_parent_projector_audit"]["frozen_tensor_chamber"]
    assert value["V70_j"] == ["1/2", "1"]
    assert value["h6"]["b_equals_minus_a_over_2"]
    assert value["h6"]["Gram_det"] == 0
    assert value["h6"]["j_dot_a"] == "3"
    assert value["h6"]["j_dot_b"] == "-3/2"
    assert not value["h6"]["positive_gauge_kinetic_in_frozen_chamber"]
    assert value["h8"]["Gram_det"] == -4
    assert value["h8"]["j_dot_a"] == "3"
    assert value["h8"]["j_dot_b"] == "-5/2"
    assert not value["h8"]["positive_gauge_kinetic_in_frozen_chamber"]


def test_candidate_matrix_accepts_no_theory_route(report):
    rows = {row["id"]: row for row in report["candidate_matrix"]}
    assert rows["F80B_REDUCED_SMOOTH_H78_E3_AS_FULL_BORDISM"]["result"].startswith(
        "REJECTED"
    )
    assert rows["F80C_H6_FLAT_HALF32_PARENT"]["result"].startswith("REJECTED")
    assert rows["F80D_H8_FLAT_HALF32_PARENT"]["result"].startswith("REJECTED")
    assert rows[
        "F80E_ANY_INTEGRATED_FLAT_QW_BULK_THREE_FAMILY_PARENT"
    ]["result"].startswith("REJECTED")
    assert rows["F80F_COMMON_FULL_PARENT_HGAMMA_ANOMALY_THEORY"]["selected"]
    assert report["candidate_adjudication"]["accepted_ids"] == []


def test_action_redesign_does_not_smuggle_in_a_new_action(report):
    value = report["action_redesign"]
    assert value["flat_half32_route"] == (
        "REJECTED_FOR_ALL_INTEGRATED_ONE_TENSOR_ROWS"
    )
    assert "gauge-dependent projector" in value["minimal_changed_action_requirement"]
    assert not value["accepted_new_action"]
    assert len(value["mandatory_reaudit_after_change"]) == 4


def test_terminal_decision_is_strictly_fail_closed(report):
    value = report["terminal_decision"]
    assert value["smooth_reduced_BH78_defined"]
    assert value["AHSS_total_degree7_computed_through_E3"]
    assert value["AHSS_E3_total_order"] == 2**15
    assert value["reduced_Omega7_H78_split_Z4_proved"]
    assert not value["reduced_Omega7_H78_computed"]
    assert not value["Q4_full_parent_HGamma_lift_constructed"]
    assert not value["full_parent_stratified_category_constructed"]
    assert not value["total_anomaly_identity_well_typed"]
    assert value["canonical_zero_internal_half_distinguished"]
    assert not value["parent_eta_selection_computed"]
    assert not value["canonical_zero_internal_half_accepted"]
    assert not value["canonical_zero_internal_half_falsified"]
    assert value["all_integrated_flat_QW_bulk_three_family_parents_rejected"]
    assert not value["accepted_full_parent_action_exists"]
    assert value["current_action_status"] == "REJECTED"
    assert value["closed_gates"] == []
    assert not value["theory_complete"]
    assert all(status.startswith("OPEN") for status in report["gate_ledger"].values())


def test_build_is_deterministic(report):
    second = audit.build_report()
    assert second == report
    assert audit.canonical_sha(second) == second["core_sha256"]


def test_generated_artifacts_are_fresh(report):
    audit.check_artifacts(report)
