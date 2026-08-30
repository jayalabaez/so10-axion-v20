from __future__ import annotations

import json

import susy_v56_two_site_link_parity_selector_audit as audit


def report():
    result = audit.build_report()
    audit.validate_report(result)
    return result


def test_upstream_cores_are_bound_and_cross_action_is_explicit() -> None:
    result = report()
    assert result["source_manifest"] == {
        "SUSY_V55_R1_MATTER_OPERATOR_AUDIT.json": audit.EXPECTED_V55_CORE,
        "SUSY_V54_CONTINUOUS_PARENT_FI_ROUTE_AUDIT.json": audit.EXPECTED_V54_R1_CORE,
    }
    assert "changed from a one-site 45" in result["cross_action_rule"]


def test_field_ledger_is_two_site_with_even_B_and_odd_identity_links() -> None:
    fields = report()["field_and_vacuum_ledger"]
    assert fields["gauge_group"] == "Spin(10)_L x Spin(10)_R"
    assert fields["fields"]["B_LR_missing"]["Z2_link"] == "even"
    assert fields["fields"]["Omega_LR"]["Z2_link"] == "odd"
    assert fields["fields"]["Omegabar_LR"]["Z2_link"] == "odd"


def test_required_filter_terms_allowed_and_named_fillers_forbidden() -> None:
    operators = report()["minimal_action_and_operator_checks"]
    assert operators["all_required_allowed"] is True
    assert operators["named_fatal_fillers_forbidden"] is True
    rows = {row["operator"]: row for row in operators["rows"]}
    assert rows["h_L B_LR H2_R"]["gauge_invariant"] and rows["h_L B_LR H2_R"]["Z2_even"]
    assert rows["h_L A_L H2_R"]["gauge_invariant"] is False
    assert rows["L h_L H2_R"]["gauge_invariant"] is False
    assert rows["h_L Omega_LR H2_R"]["Z2_even"] is False


def test_bounded_path_census_has_no_counterexample() -> None:
    paths = report()["exact_link_path_selector"]
    assert paths["maximum_link_length_enumerated"] == 9
    assert paths["counterexamples"] == []
    assert [row["all_words"] for row in paths["rows"]] == [2, 8, 32, 128, 512]
    assert all(row["Z2_allowed_words"] == row["allowed_words_containing_B"] for row in paths["rows"])


def test_all_order_path_identity_forces_an_odd_number_of_B_links() -> None:
    proof = report()["exact_link_path_selector"]["connected_path_all_order_proof"]
    assert "odd number Nlink" in proof
    assert "NB=Nlink-NOmega is odd" in proof
    assert "2(1+Nlink)=0 mod4" in report()["exact_link_path_selector"]["Spin10_center_check"]


def test_factorized_degree6_adjoint_counterexample_is_nonzero() -> None:
    stress = report()["factorized_epsilon_and_adjoint_stress_test"]
    leak = stress["first_explicit_vacuum_nonzero_counterexample"]
    assert leak["total_degree"] == 6
    assert leak["gauge_invariant"] and leak["Z2_even"]
    assert leak["Tr_A0_B0"] == -6
    assert leak["vacuum_nonzero"] is True
    assert "direct cross-site h-H2 mass" in leak["effect"]


def test_pure_link_epsilon_determinant_and_cofactor_pass() -> None:
    epsilon = report()["factorized_epsilon_and_adjoint_stress_test"]["epsilon_determinant_audit"]
    assert epsilon["determinant_formula"] == "det(I_10+t B0)=(1+t^2)^3"
    assert epsilon["odd_B_coefficients_in_determinant"] == [0] * 5
    assert epsilon["odd_B_coefficients_in_weak_cofactor"] == [0] * 5


def test_exact_filter_rank_is36_with_four_weak_modes() -> None:
    ranks = report()["exact_filter_mass_rank"]
    assert ranks["full_rank_QQ"] == 36
    assert ranks["full_nullity"] == 4
    assert ranks["color_rank_QQ"] == 24
    assert ranks["color_nullity"] == 0
    assert ranks["weak_rank_QQ"] == 12
    assert ranks["weak_nullity"] == 4
    assert ranks["coefficient_equality_required"] is False


def test_direct_filler_control_would_destroy_the_weak_kernel() -> None:
    ranks = report()["exact_filter_mass_rank"]
    assert ranks["control_direct_hH2_filler_weak_rank_QQ"] == 16
    assert ranks["control_direct_hH2_filler_full_rank_QQ"] == 40


def test_Z2_anomaly_counts_are_even_but_representation_cost_is_large() -> None:
    cost = report()["finite_selector_anomaly_and_representation_cost"]
    anomaly = cost["Z2_link_mixed_anomaly"]
    assert anomaly["Spin10L_index_sum_in_T10_equals1_convention"] == 20
    assert anomaly["Spin10R_index_sum_in_T10_equals1_convention"] == 20
    assert anomaly["odd_Weyl_component_count"] == 200
    assert anomaly["all_even_mod2"] is True
    assert cost["representation_cost"]["new_bifundamental_coordinates"] == 300
    running = cost["one_loop_per_site_running"]
    assert running["minimal_three_link_plus_XL_driver_filter"]["left_b"] == 29
    assert running["minimal_three_link_plus_XL_driver_filter"]["right_b"] == 7
    assert 100 < running["minimal_three_link_plus_XL_driver_filter"]["left_pole_ratio"] < 1000
    assert running["R1_source_transplant_without_families"]["left_b"] == 53
    assert running["R1_source_transplant_without_families"]["left_pole_ratio"] < 100
    assert running["R1_source_plus_three_left_families"]["left_b"] == 59


def test_fail_closed_and_no_gate_promotion() -> None:
    result = report()
    assert len(result["unresolved_same_action_obligations"]) == 5
    assert result["gate_effect"]["filter_selector_mechanism"] == "CONNECTED_PATH_ONLY__FULL_INVARIANT_RING_FAILED_AT_DEGREE6"
    assert result["gate_effect"]["complete_two_site_action"] == "OPEN"
    assert result["gate_effect"]["candidate_gate_promotions"] == 0
    assert result["gate_effect"]["G1_through_G8_promotions"] == []


def test_hash_and_artifacts_are_current() -> None:
    result = audit.check_artifacts()
    assert audit.canonical_sha(result) == result["core_sha256"]
    assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == result
    assert audit.MD_PATH.read_text(encoding="utf-8") == audit.markdown(result)
