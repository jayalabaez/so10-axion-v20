from __future__ import annotations

import susy_v70_spin11_localized_parent_spin_flavor_completion_audit as audit


def report():
    return audit.build_report()


def test_v70_integrity_and_v69_lineage():
    value = report()
    audit.validate(value)
    assert value["core_sha256"] == audit.canonical_sha(value)
    assert value["lineage"]["bound_V69_core"] == audit.EXPECTED_V69_CORE


def test_genuine_spin_lift_cocycle_is_exact():
    spin = report()["genuine_spin_lift"]
    assert spin["exact_relations"]["qhat_fourth"] == "-1"
    assert spin["exact_relations"]["what_squared"] == "-1"
    assert spin["spinor_weight_formula"]["all_32_weights_qhat4_minus_one"]
    assert spin["spinor_weight_formula"]["all_32_weights_what2_minus_one"]


def test_lorentz_SU2R_lift_preserves_exactly_an_N1_choice():
    susy = report()["lorentz_SU2R_and_N1_superfield_lift"]
    assert susy["SU2R_twist"]["one_product_is_identity"]
    assert susy["SU2R_twist"]["identity_eigenlines_before_reality"] == 2
    assert susy["SU2R_twist"]["symplectic_Majorana_identity_orbits"] == 1
    assert susy["SU2R_twist"]["preserved_4D_N"] == 1
    assert susy["N1_superfield_rules"]["full_hyper_constraint"].startswith("Z_plus Z_minus")


def test_odd_half32_multiplicity_is_rejected():
    no_go = report()["published_half32_parent_adjudication"]
    assert no_go["single_half32"] == "REJECTED"
    assert no_go["three_half32s"] == "REJECTED"
    assert "n must be even" in no_go["determinant_proof"][-1]


def test_vector_sigma_is_one_weak_doublet_without_triplet():
    vector = report()["vector_multiplet_zero_modes"]
    assert vector["V_zero_complex_dimension"] == 13
    assert vector["Sigma_zero_complex_dimension"] == 2
    assert vector["weak_doublets"] == 1
    assert vector["color_triplets"] == 0


def test_active_m3_11_is_conjugate_doublet_plus_singlet():
    row = audit.full_11_zero_modes(3, 1)
    assert row["plus_zero_sectors"] == ["weak_hol"]
    assert row["minus_column_sectors"] == ["singlet"]
    assert not row["triplet_zero"]


def test_full_integer_phase_table_and_half_integer_nonimport():
    table = report()["full_11_phase_table"]
    assert len(table["rows"]) == 8
    assert not table["half_integer_nonimport"]["used_in_V70"]
    assert table["half_integer_nonimport"]["verdict"].startswith("PROJECTIVE")


def test_paired_spectator_flavor_wilson_lift_and_zero_mode_proof():
    branch = report()["localized_parent_completion_branches"]["minimal_flavor_Wilson_projection"]
    spectator = branch["spectator_pair"]
    assert spectator["all_checks_pass"]
    assert all(spectator["plus_space_group_checks"].values())
    assert all(spectator["minus_space_group_checks"].values())
    assert all(spectator["full_hyper_action_checks"].values())
    assert spectator["zero_mode_proof"]["T2_equals_minus_T1"]
    assert spectator["zero_mode_proof"]["n_zero_modes"] == 0


def test_integer_m301_zero_ledger_is_exact():
    branch = report()["localized_parent_completion_branches"]["integer_m301_dynamical_reduction"]
    fields = branch["phase_assignments"]
    assert fields["A_m3"]["plus_zero_sectors"] == ["weak_hol"]
    assert fields["A_m3"]["minus_column_sectors"] == ["singlet"]
    assert fields["B_m0"]["plus_zero_sectors"] == ["singlet"]
    assert fields["B_m0"]["minus_column_sectors"] == ["weak_anti"]
    assert fields["C_m1"]["plus_zero_sectors"] == ["weak_anti"]
    assert fields["C_m1"]["minus_column_sectors"] == []
    assert branch["zero_mode_ledger_before_superpotential"]["color_triplets"] == []


def test_integer_m301_flat_branch_and_rank_one_doublet_matrix():
    branch = report()["localized_parent_completion_branches"]["integer_m301_dynamical_reduction"]
    assert branch["local_U5_stabilizer"]["D_flat"]
    driver = branch["local_U5_stabilizer"]["complete_renormalizable_driver_class"]
    assert "z_X=X Xbar" in driver["fields"]
    assert "not an added field" in driver["fields"]
    assert driver["nondegeneracy_condition"] == "det J != 0"
    assert driver["exact_determinant"] == "det H=(det J)^2"
    assert "quadratic driver monomials" in driver["P_3_boundary"]
    assert branch["bulk_breaking"]["orbifold_compatible"].startswith("Q e11=W e11")
    assert branch["mandatory_and_local_masses"]["rank_for_g_nonzero_vB_nonzero"] == 1
    assert "nonzero" in branch["mandatory_and_local_masses"]["H_dC_projection"]
    assert "H_uA" in branch["mandatory_and_local_masses"]["light_pair"]
    operators = branch["complete_renormalizable_local_operator_ledger"]
    assert operators["forbidden_terms"]["light_mu_HuA_Hd"] == "R=0 not 2"
    assert operators["forbidden_terms"]["16_to_the_fourth"] == "R=0 not 2"
    assert operators["arbitrary_local_Sigma_polynomial"].startswith("FORBIDDEN")


def test_4d_zero_mode_anomalies_and_Witten_parity_cancel():
    anomaly = report()["four_dimensional_zero_mode_anomaly_audit"]
    assert anomaly["all_perturbative_coefficients_zero"]
    assert set(anomaly["coefficients"].values()) == {"0"}
    assert anomaly["SU2_Witten"]["number_of_fundamental_doublets_with_color_multiplicity"] == 14
    assert anomaly["SU2_Witten"]["even"]


def test_fixed_locus_twists_and_fail_closed_boundary():
    value = report()
    local = value["fixed_locus_twist_ledger"]
    assert local["fixed_gauge_algebras"]["z00"].startswith("C(Q)=u(5)")
    assert local["adjoint_superfields"]["z10_z01"] == ["V:Ad(R)", "Sigma:-Ad(R)"]
    m301 = {row["hyper"]: row for row in local["selected_integer_m301_11s"]}
    assert m301["A"]["z10_z01"] == ["Phi+:-R", "Phi-:+R"]
    assert m301["B"]["z10_z01"] == ["Phi+:+R", "Phi-:-R"]
    assert m301["C"]["z10_z01"] == ["Phi+:-R", "Phi-:+R"]
    assert value["acceptance"]["A9_charged_fermion_pointwise_gauge_anomaly"] == "PASS_EXACT_ZERO"
    assert value["acceptance"]["A9_full_local_supergravity_and_GS"] == "OPEN"
    assert all(state == "OPEN" for state in value["gate_ledger"].values())
    assert not value["terminal_decision"]["theory_complete"]


def test_pointwise_charged_anomalies_quantization_and_positive_chamber():
    local = report()["localized_anomaly_and_bulk_global_audit"]
    projector = local["projector_convention"]
    assert "eta is not raw P_f" in projector["table_key"]
    assert projector["fermion_from_superfield_conversion"].startswith("P_f(eta)=")
    assert local["minimal_flavor_Wilson_branch"]["z00_U5"]["sum"] == "0"
    assert local["minimal_flavor_Wilson_branch"]["z11_U5_prime"]["sum"] == "0"
    assert local["minimal_flavor_Wilson_branch"]["all_local_charged_fermion_polynomials_zero"]
    assert local["minimal_flavor_Wilson_branch"]["z10_z01_Spin4xSpin7"]["SU2_fundamental_doublet_total"] == 20
    assert local["integer_m301_branch"]["z00_and_z11_coefficients_in_B_units"]["sum"] == "0"
    assert local["integer_m301_branch"]["z10_z01_SU2_fundamental_doublet_total"] == 20
    assert local["local_GS_decision"]["hypercharge_or_X_Stueckelberg_from_equivariant_GS_descent"] == "OPEN_NOT_COMPUTED"
    assert local["smooth_bulk_quantization"]["coefficient_quantization"] == "PASS_ON_THE_SMOOTH_BULK"
    assert local["positive_tensor_chamber"]["j_squared"] == "1"
    assert local["positive_tensor_chamber"]["j_dot_b"] == "3/2"
    assert local["positive_tensor_chamber"]["j_dot_a"] == "3"
    assert local["positive_tensor_chamber"]["gauge_kinetic_positive_and_j_dot_a_positive"]
    assert "not labeled a gravitational kinetic coefficient" in local["positive_tensor_chamber"]["scope"]
    assert not local["positive_tensor_chamber"]["stabilized_tensor_vacuum"]
