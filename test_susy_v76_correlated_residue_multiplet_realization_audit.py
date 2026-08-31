from fractions import Fraction
import json

import pytest

import susy_v76_correlated_residue_multiplet_realization_audit as audit


def report():
    return audit.build_report()


def test_v75_route_and_master_are_recomputed_and_bound():
    lineage = report()["lineage"]
    assert lineage["V75_route_core"] == audit.EXPECTED_CORES["v75_route"]
    assert lineage["V75_master_core"] == audit.EXPECTED_CORES["v75_master"]


def test_mutated_v75_parent_is_rejected_even_with_old_embedded_core(tmp_path):
    parent = json.loads(audit.V75_ROUTE_PATH.read_text(encoding="utf-8"))
    parent["status"] += "__MUTATED"
    path = tmp_path / "mutated.json"
    path.write_text(json.dumps(parent), encoding="utf-8")
    with pytest.raises(RuntimeError, match="noncanonical parent core"):
        audit.load_bound(path, audit.EXPECTED_CORES["v75_route"])


def test_universal_clean_targets_are_outside_even_half_index_lattice():
    value = report()["universal_clean_half_index_no_go"]
    assert value["target_periods"] == {
        "plus_nu_c2R": "-1/4",
        "minus_nu_c2R": "1/4",
        "normal_quarter": "1/4",
        "inverse_V71_parent_residue": "5/8",
    }
    assert not any(value["integer_index_membership"].values())
    assert not any(value["half_index_membership"].values())
    assert value["all_targets_outside_half_index_lattice"]


def test_correlated_R_completion_has_integral_cp3_period_six():
    value = report()["universal_clean_half_index_no_go"][
        "correlated_allowed_witness"
    ]
    assert value["period"] == "6"
    assert value["integer"]


def test_total_two_corner_residue_is_an_odd_quarter_on_both_witnesses():
    value = report()["total_two_corner_index_period_no_go"]
    assert Fraction(value["common_CP3_witness"]["two_corner_residue"]) == Fraction(
        -5, 4
    )
    assert Fraction(
        value["spin_cubic_threefold_witness"]["two_corner_residue"]
    ) == Fraction(9, 4)
    for shift in range(-20, 21):
        assert Fraction(-5, 4) + shift != 0
        assert Fraction(9, 4) + shift != 0
    for half_steps in range(-40, 41):
        assert Fraction(-5, 4) + Fraction(half_steps, 2) != 0
        assert Fraction(9, 4) + Fraction(half_steps, 2) != 0
    assert not value["ordinary_free_field_two_corner_completion_exists"]
    assert not value["V75_level4_changes_odd_quarter_class"]


def test_four_line_correlated_index_has_forced_eta_spectator():
    value = report()["four_line_diagonal_eta_representative"]
    cp3 = value["witness_periods"]["CP3"]
    cubic = value["witness_periods"]["spin_cubic_threefold"]
    assert Fraction(cp3["diagonal"]) == Fraction(13, 4)
    assert Fraction(cp3["S_eta"]) == Fraction(-1, 4)
    assert cp3["total_index"] == "3"
    assert Fraction(cubic["diagonal"]) == Fraction(39, 4)
    assert Fraction(cubic["S_eta"]) == Fraction(5, 4)
    assert cubic["total_index"] == "11"
    assert value["total_is_honest_integral_index"]
    assert not value["pure_diagonal_quarter_refinement_constructed"]
    assert not value["standard_neutral_free_inverse_spectator_exists"]


def test_seven_weyl_moments_cancel_parent_residue_exactly():
    value = report()["seven_weyl_local_correlated_inverse"]
    assert value["complex_Weyl_count"] == 7
    assert value["moments"]["Q1"] == "-3"
    assert value["moments"]["Q3"] == "3/4"
    assert value["moments"]["normal_X_squared"] == "-125"
    assert value["moments"]["normal_squared_X"] == "0"
    assert value["polynomial_coefficients"] == {
        "nu_ell_squared": "-5/2",
        "nu_cubed": "1/8",
        "nu_p1": "1/8",
    }
    assert value["local_parent_residue_cancelled"]


def test_seven_weyl_gauge_spectators_are_vectorlike_in_X():
    moments = report()["seven_weyl_local_correlated_inverse"]["moments"]
    assert moments["gravity_X"] == 0
    assert moments["X_cubed"] == 0
    assert moments["normal_squared_X"] == "0"


def test_all_seven_weyl_entries_have_standard_hyper_component_centers():
    value = report()["seven_weyl_local_correlated_inverse"]
    assert value["all_standard_hyper_component_centers_pass"]
    for field in value["fields"]:
        assert (field["nphi"] + field["X"]) % 2 == 1


def test_bundle_sum_and_difference_identities_are_normalized_correctly():
    value = report()["two_corner_common_sum_no_go"]
    assert value["identities"]["ell_squared_minus_ellprime_squared"] == "A B"
    assert (
        value["identities"]["ell_squared_plus_ellprime_squared"]
        == "(A^2+B^2)/2"
    )
    assert value["common_signed_sum"] == "-(5/4)nu(A^2+B^2)"


def test_two_corner_inverse_has_quarter_periods_on_both_spin_witnesses():
    witnesses = report()["two_corner_common_sum_no_go"]["witness_periods"]
    assert Fraction(witnesses["CP3"]["required_inverse"]) == Fraction(65, 4)
    assert witnesses["CP3"]["fractional_part"] == "1/4"
    assert Fraction(
        witnesses["spin_cubic_threefold"]["required_inverse"]
    ) == Fraction(195, 4)
    assert witnesses["spin_cubic_threefold"]["fractional_part"] == "3/4"


def test_integer_AB_bridge_units_cannot_change_quarter_fractional_parts():
    value = report()["two_corner_common_sum_no_go"]
    assert value["witness_periods"]["CP3"]["integer_AB_bridge_unit"] == 6
    assert (
        value["witness_periods"]["spin_cubic_threefold"][
            "integer_AB_bridge_unit"
        ]
        == 18
    )
    assert not value["any_integer_V74_AB_bridge_repairs"]
    assert not value["required_inverse_in_half_index_lattice"]
    assert not value["both_seven_weyl_route_accepted"]


def test_flipping_second_seven_weyl_module_doubles_parent_residue():
    value = report()["two_corner_common_sum_no_go"]["same_sign_is_forced"]
    assert "-2T" in value["flipped_z11_failure"]


def test_general_integer_pure_gauge_repair_coset_is_exact():
    value = report()["pure_gauge_two_corner_lattice_no_go"]
    integer = value["ordinary_integer_endpoint_lattice"]
    assert integer["solution_coset"] == "g=-5/2+4Z"
    for n in range(-10, 11):
        g = 4 * n - Fraction(5, 2)
        assert Fraction(5, 8) + Fraction(25, 4) * g == 25 * n - 15
        assert Fraction(5, 8) + Fraction(1, 4) * g == n
    consequence = value["ordinary_lattice_consequence"]
    assert consequence["diagonal_coefficient"] == "(g0+g1)/4=3/4 mod Z"
    assert not consequence["AB_bridge_can_remove_diagonal_quarter"]


def test_general_half_index_pure_gauge_repair_still_leaves_odd_quarter():
    value = report()["pure_gauge_two_corner_lattice_no_go"]
    half = value["permissive_half_index_endpoint_lattice"]
    assert half["solution_coset"] == "g=-5/2+2Z"
    for n in range(-10, 11):
        g = 2 * n - Fraction(5, 2)
        first = 2 * (Fraction(5, 8) + Fraction(25, 4) * g)
        second = 2 * (Fraction(5, 8) + Fraction(1, 4) * g)
        assert first.denominator == second.denominator == 1
    consequence = value["half_index_lattice_consequence"]
    assert consequence["diagonal_coefficient"] == "an odd quarter mod Z"
    assert not consequence["AB_bridge_can_remove_diagonal_quarter"]
    assert not value["ordinary_or_half_index_pure_gauge_route_exists"]


def test_smallest_mixed_integer_remainder_keeps_diagonal_quarter():
    value = report()["pure_gauge_two_corner_lattice_no_go"][
        "smallest_absolute_ordinary_remainder"
    ]
    assert value["g0_g1"] == ["3/2", "-5/2"]
    assert value["required_integer_AB_bridge_level"] == -6
    assert value["diagonal_quarter_survives"]


def test_optional_flavor_has_v_zero_subbackground_and_cannot_evade():
    value = report()["pure_gauge_two_corner_lattice_no_go"][
        "optional_flavor_extension"
    ]
    assert value["odd_X_requires_odd_flavor"]
    assert value["v_zero_is_admissible"]
    assert not value["evades_no_go"]


def test_four_image_chain_supports_only_level_four_opposite_sources():
    value = report()["orbifold_chain_and_source_conservation_audit"]
    assert not value["fixed_strata"]["one_dimensional_fixed_locus_exists"]
    chain = value["four_image_chain"]
    assert chain["boundary"] == "partial Gamma=4(p1-p0)"
    assert chain["supports_level4_opposite_corner_profile"]
    assert chain[
        "within_integral_four_image_cover_orbit_sum_ansatz_primitive_level1_requires_fractional_wall_or_cap"
    ]
    assert not chain["quotient_primitive_level1_excluded"]
    assert not chain["quotient_delta_normalization_calibrated"]
    assert not chain["common_BPS_projector_constructed"]
    same = value["same_sign_source"]
    assert not same["is_boundary_on_compact_T2"]
    assert not value["equal_corner_one_eighth_inverse_from_two_corner_only_GS_cap"]


def test_known_off_shell_and_self_dual_sectors_do_not_complete_the_action():
    value = report()["off_shell_and_exotic_sector_audit"]
    known = value["known_off_shell_scope"]
    assert known["ordinary_vector_linear_density_exists"]
    assert known["full_curvature_squared_superinvariants_exist"]
    assert not known["isolated_normal_U1_or_nu_c2R_superinvariant_bound_to_current_action"]
    exotic = value["self_dual_and_refined_loophole"]
    assert not exotic["quadratic_refined_self_dual_theory_representation_independently_excluded"]
    assert exotic["six_dimensional_self_dual_tensor_changes_I8_and_string_charge_lattice"]
    assert not exotic["GS_coefficient_is_free_one_eighth_knob"]
    assert exotic["standard_Maxwell_duality_structure_is_different"]
    assert not exotic["required_normal_U1_class_matched_or_constructed"]
    assert not exotic["explicit_refined_five_dimensional_anomaly_theory_constructed"]
    assert not value["accepted_exotic_completion"]


def test_all_v75_level4_components_pass_their_multiplet_center_pattern():
    value = report()["V75_level4_component_multiplet_audit"]
    assert value["all_V75_level4_component_centers_pass"]
    for module in value["modules"].values():
        assert module["all_component_centers_pass"]
        for field in module["rows"]:
            if field["SU2R_dimension"] == 1:
                assert (field["nphi"] + field["X"]) % 2 == 1
            else:
                assert field["SU2R_dimension"] == 2
                assert (field["nphi"] + field["X"]) % 2 == 0


def test_component_pass_is_not_overpromoted_to_complete_multiplets():
    value = report()["V75_level4_component_multiplet_audit"]
    assert not value["bulk_multiplet_realization_constructed"]
    assert not value["localized_defect_action_constructed"]
    assert not value["same_action_microscopic_completion"]
    assert any("symplectic-Majorana" in item for item in value["not_supplied_by_component_pass"])


def test_ordinary_6d_and_5d_multiplet_routes_do_not_realize_level4_rows():
    value = report()["V75_level4_component_multiplet_audit"]
    bulk = value["ordinary_bulk_realization_diagnostics"]
    assert bulk["T2_Z4_vector_superfield_rule"] == "V -> rho V; Sigma -> i rho Sigma"
    assert not bulk["one_rho_keeps_both_V_and_Sigma"]
    assert not bulk["N1_corner_keeps_full_SU2R_gaugino_doublet"]
    assert not bulk["ordinary_bulk_fields_generate_V75_large_q_without_changed_quotient"]
    assert not bulk["genuine_Sigma_supplies_qphi_plus_or_minus2_driver"]
    assert not bulk["five_dimensional_codimension1_fixed_stratum_exists"]


def test_formal_bulk_HVT_diagnostic_rejects_the_m11_vector_interpretation():
    value = report()["V75_level4_component_multiplet_audit"][
        "formal_complete_multiplet_gravitational_diagnostic"
    ]
    assert value["vector_interpretation"]["M00_shift"] == 0
    assert value["vector_interpretation"]["M11_shift"] == 2
    assert value["tensor_interpretation"]["M00_shift"] == 120
    assert value["tensor_interpretation"]["M11_shift"] == 62
    assert not value["is_full_bulk_anomaly_calculation"]


def test_every_proposed_driver_is_a_nontrivial_line_power_on_cp3():
    value = report()["normal_bundle_driver_obstruction"]
    assert value["admissible_witness"]["c1_N"] == "H"
    assert value["all_proposed_nonzero_charge_drivers_obstructed_on_witness"]
    assert {row["qphi"] for row in value["drivers"]} == {-4, -2, 2}
    for driver in value["drivers"]:
        assert driver["c1_on_CP3"] != "0 H"
        assert not driver["nowhere_zero_on_CP3"]


def test_minimal_neutral_singlet_chiral_driver_lifts_fail_the_center_rule():
    value = report()["normal_bundle_driver_obstruction"]
    lift = value["minimal_chiral_lift"]
    assert lift["all_neutral_SU2R_singlet_driver_fermions_fail"]
    assert not lift["vector_or_tensor_type_lift_constructed"]
    for driver in value["drivers"]:
        assert driver["scalar_center_pass"]
        assert driver["npsi_for_minimal_chiral"] % 2 == 1
        assert not driver["minimal_neutral_SU2R_singlet_chiral_center_pass"]
        assert driver["vector_or_tensor_SU2R_doublet_partner_would_pass"]


def test_driver_isotropy_and_fermion_anomalies_block_the_naive_mass_sector():
    value = report()["normal_bundle_driver_obstruction"]
    isotropy = value["flat_orbifold_isotropy"]
    assert isotropy["qphi_plus_or_minus2_phase"] == "-1"
    assert isotropy["qphi_minus4_phase"] == "+1"
    assert not isotropy["R0_alone_implies_trivial_geometric_isotropy"]
    ledger = value["dynamical_chiral_driver_anomaly_ledger"]
    assert ledger["seven_route_driver_fermions"]["Delta_Q1"] == "-3"
    assert ledger["seven_route_driver_fermions"]["Delta_Q3"] == "-351/4"
    assert ledger["seven_module_plus_drivers_Q1_Q3"] == ["-6", "-87"]
    assert not ledger["still_cancels_intended_parent_residue"]
    partners = value["anomaly_vectorlike_partner_requirements"]
    assert partners["Z2_partner"] == {"qphi": -1, "Z4R": 2}
    assert partners["Zminus4_partner"] == {"qphi": 5, "Z4R": 2}
    assert not partners["partners_supply_nonzero_driver_VEV_potential"]


def test_driver_zero_divisor_prevents_an_everywhere_full_rank_gap():
    value = report()["normal_bundle_driver_obstruction"]["allowing_zero_divisor"]
    assert not value["mass_matrix_full_rank_everywhere"]
    assert "mass vanishes" in value["consequence"]


def test_spin_gauge_locking_is_a_changed_action_not_a_completion():
    value = report()["normal_bundle_driver_obstruction"][
        "spin_gauge_locking_escape"
    ]
    assert value["requires_new_U1_g"]
    assert value["changes_tangential_structure"]
    assert value["requires_recomputed_anomaly_ledger"]
    assert not value["constructs_current_action"]


def test_seven_weyl_local_mass_operator_charges_are_exact():
    value = report()["seven_weyl_mass_audit"]
    assert value["cross_operator"]["normal_charge_check"] == "+2-1+0=+1"
    assert value["cross_operator"]["Z4R_check"] == "0+2+0=2 mod4"
    assert value["cross_operator"]["two_independent_blocks"]
    assert value["cross_operator"]["rank_per_one_by_two_block_at_most"] == 1
    assert value["cross_operator"]["maximum_total_charged_rank"] == 2
    assert value["leftover_B_pair"]["Giudice_Masiero_class"]
    assert "only the Z2 matter parity" in value["leftover_B_pair"]["symmetry_statement"]
    assert value["leftover_B_pair"]["z11_if_light"]["Delta_b_GUT"] == [
        "6/5",
        "0",
        "0",
    ]
    assert value["neutral_N"]["normal_charge_check"] == "-4+5/2+5/2=+1"
    assert value["neutral_N"]["Z4R_check"] == "0+1+1=2 mod4"
    assert not value["neutral_N"]["standalone_full_quotient_N1_chiral_certified"]
    parity = value["combined_with_V75_mass_parity_theorem"]
    assert parity["z00_per_X_sign"]["two_half_charge_class_counts"] == [4, 3]
    assert parity["z11_per_X_sign"]["two_half_charge_class_counts"] == [3, 4]
    assert parity["one_vectorlike_charge_five_pair_survives"]
    assert not parity["R2_condensate_preserves_high_scale_Z4R"]
    assert not value["accepted_mass_gap"]


def test_full_parent_determinant_is_selected_but_not_accepted():
    candidates = report()["F76_candidate_matrix"]
    selected = [row for row in candidates if row["selected"]]
    assert len(selected) == 1
    assert selected[0]["id"] == "F76_FULL_EQUIVARIANT_PARENT_DETERMINANT"
    assert not selected[0]["accepted"]


def test_fail_closed_terminal_decision_keeps_all_gates_open():
    value = report()
    assert set(value["gate_ledger"].values()) == {"OPEN"}
    decision = value["terminal_decision"]
    assert decision["seven_weyl_local_parent_residue_cancelled"]
    assert decision["seven_weyl_two_corner_route_closed"]
    assert decision["V75_level4_component_centers_pass"]
    assert not decision["same_action_microscopic_completion_found"]
    assert decision["closed_gates"] == []
    assert not decision["theory_complete"]


def test_report_core_is_canonical_and_artifacts_are_fresh():
    value = report()
    assert audit.canonical_sha(value) == value["core_sha256"]
    checked = audit.check_artifacts()
    assert checked["core_sha256"] == value["core_sha256"]
