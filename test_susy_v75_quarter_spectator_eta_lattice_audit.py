from fractions import Fraction
import json

import pytest

import susy_v75_quarter_spectator_eta_lattice_audit as audit


def report():
    return audit.build_report()


def test_v74_route_and_master_are_recomputed_and_bound():
    value = report()["lineage"]
    assert value["V71_route_core_for_equal_corner_residue"] == audit.EXPECTED_CORES[
        "v71_route"
    ]
    assert value["V74_route_core"] == audit.EXPECTED_CORES["v74_route"]
    assert value["V74_master_core"] == audit.EXPECTED_CORES["v74_master"]


def test_mutated_parent_with_unchanged_embedded_core_is_rejected(tmp_path):
    parent = json.loads(audit.V74_ROUTE_PATH.read_text(encoding="utf-8"))
    parent["status"] += "__MUTATED"
    path = tmp_path / "mutated.json"
    path.write_text(json.dumps(parent), encoding="utf-8")
    with pytest.raises(RuntimeError, match="noncanonical parent core"):
        audit.load_bound(path, audit.EXPECTED_CORES["v74_route"])


def test_honest_line_weights_pass_both_center_rules():
    lines = report()["virtual_line_eta_representative"]["honest_endpoint_lines"]
    for value in lines.values():
        n, x, r = value["weight_n_x_r"]
        assert (2 * x) % 5 == 0
        assert (n + x + r) % 2 == 0


def test_virtual_line_difference_gives_eta_curvature_exactly():
    plus = audit.line_index_cubic((1, Fraction(1, 2)))
    minus = audit.line_index_cubic((1, Fraction(-1, 2)))
    value = audit.add_polynomials(
        audit.scale_polynomial(plus, Fraction(2)),
        audit.scale_polynomial(minus, Fraction(-2)),
    )
    nonzero = {key: coefficient for key, coefficient in value.items() if coefficient}
    assert nonzero == {
        "nu3": Fraction(1, 12),
        "nu_ell2": 1,
        "nu_p1": Fraction(-1, 12),
    }
    stored = report()["virtual_line_eta_representative"]["computed_coefficients"]
    assert stored == {key: audit.fstr(coefficient) for key, coefficient in nonzero.items()}


def test_cp3_witness_turns_25_over_4_into_integral_six():
    value = report()["virtual_line_eta_representative"]["CP3_diagonal_witness"]
    p = Fraction(value["P_period"])
    spectator = Fraction(value["S_eta_period"])
    assert p == Fraction(25, 4)
    assert value["I6_L_plus"] == "4"
    assert value["I6_L_minus"] == "1"
    assert spectator == Fraction(1 - value["p1_TCP3"], 12) == Fraction(-1, 4)
    assert p + spectator == Fraction(value["C_eta_period"]) == 6


def test_cubic_threefold_and_cp3_witnesses_generate_the_diagonal_spin_lattice():
    eta = report()["virtual_line_eta_representative"]
    cubic = eta["spin_cubic_threefold_witness"]
    assert cubic["spin_reason"].startswith("c1(TX3)=2h")
    assert cubic["I6_L_plus"] == "15"
    assert cubic["I6_L_minus"] == "5"
    assert cubic["C_eta_period"] == "20"
    lattice = eta["diagonal_spin_normal_gravity_lattice"]
    assert lattice["witness_rows_X_Y"] == [[1, 4], [3, -12]]
    assert lattice["determinant_absolute"] == 24
    assert lattice["C_eta_passes_dual_lattice"]


def test_eta_spectator_cancels_out_of_the_common_overlap_difference():
    value = report()["virtual_line_eta_representative"]
    assert value["common_overlap_difference"].endswith("=nu A B")
    assert not value["V74_common_bridge_changed"]
    assert not value["pure_P_refinement_constructed"]
    assert value["closed_smooth_spin_H_Dai_Freed_phase_constructed"]
    assert not value["full_H_bordism_classification_computed"]
    assert not value["Z4_equivariant_orbifold_extension_constructed"]
    assert "xi=(eta+dim ker D)/2" in value["tau_normalization"]
    flavor = value["optional_flavor_quotient"]
    assert not flavor["used_in_displayed_formula"]
    assert flavor["additional_center_check"] == "x+f=5+1=0 mod2"
    assert "nu B(A+2v)" in flavor["required_change"]
    assert not flavor["complete_flavor_anomaly_ledger"]


def test_bound_equal_corner_parent_residue_does_not_match_eta_spectators():
    value = report()["bound_parent_equal_corner_residue"]
    assert "-(1/8)" in value["bound_V71_input"]
    assert value["combined_residuals"] == {
        "z00_R_plus_S": "-nu[nu^2+5p]/24",
        "z11_R_minus_S": "-nu[5nu^2+p]/24",
    }
    assert value["CP3_periods"]["R_plus_S_z00"] == "-7/8"
    assert value["CP3_periods"]["R_minus_S_z11"] == "-3/8"
    assert value["bound_V71_Ahat_T4_convention"] == "1-p/24+..."
    assert not value["primitive_AB_bridge_contains_normal_gravity_curvature"]
    assert not value["equal_nonzero_parent_residue_cancelled"]


def test_R_correlated_eight_weyl_module_polynomial():
    charged = audit.scale_polynomial(audit.singlet_polynomial(Fraction(1, 2)), 4)
    neutral = audit.scale_polynomial(audit.doublet_polynomial(Fraction(-1, 2)), 2)
    total = audit.add_polynomials(charged, neutral)
    assert total == {"nu3": 0, "nu_c2R": 1, "nu_p1": 0}
    value = report()["exact_correlated_fermion_modules"]["R_completion"]
    assert value["normal_moments_Q1_Q3"] == ["0", "0"]
    assert value["normal_X2"] == 50
    assert value["SU2R_doublet_count"] == 2
    assert value["Witten_SU2_global_parity_even"]
    assert value["complete_polynomial"] == "C_R=nu[ell^2+c2(R)]"
    assert value["diagonal_period"] == 6


def test_normal_line_six_weyl_module_polynomial():
    charged = audit.scale_polynomial(audit.singlet_polynomial(Fraction(1, 2)), 4)
    neutral = audit.scale_polynomial(audit.singlet_polynomial(Fraction(-1)), 2)
    total = audit.add_polynomials(charged, neutral)
    assert total == {
        "nu3": Fraction(-1, 4),
        "nu_c2R": 0,
        "nu_p1": 0,
    }
    value = report()["exact_correlated_fermion_modules"]["normal_line_completion"]
    assert value["normal_moments_Q1_Q3"] == ["0", "-3/2"]
    assert value["normal_X2"] == 50
    assert value["complete_polynomial"] == "C_N=nu[ell^2-nu^2/4]"


def test_six_weyl_spectator_shift_module_is_exact():
    doublets = audit.scale_polynomial(audit.doublet_polynomial(Fraction(-1, 2)), 2)
    singlets = audit.scale_polynomial(audit.singlet_polynomial(Fraction(1)), 2)
    total = audit.add_polynomials(doublets, singlets)
    assert total == {
        "nu3": Fraction(1, 4),
        "nu_c2R": 1,
        "nu_p1": 0,
    }
    value = report()["exact_correlated_fermion_modules"][
        "integral_spectator_shift_module"
    ]
    assert value["complete_polynomial"] == "D=C_R-C_N=nu[c2(R)+nu^2/4]"
    assert value["ordinary_integral"]


def test_modular_identities_used_by_no_go_are_exact():
    for n in range(-31, 32, 2):
        assert (n**3 - n) % 8 == 0
    for m in range(-32, 33):
        assert (m**3 - m) % 2 == 0


def test_pure_R_spectator_equations_contradict_mod8():
    value = report()["standard_neutral_free_eta_no_go"]["pure_R_spectator"]
    assert value["cubic_left_mod8"] == 4
    assert value["cubic_right_mod8"] == 0
    assert not value["solution_exists"]
    assert value["both_signs_excluded"]


def test_pure_normal_quarter_equations_contradict_mod8():
    value = report()["standard_neutral_free_eta_no_go"]["pure_normal_quarter"]
    assert value["cubic_left_mod8"] == 0
    assert value["cubic_right_mod8"] == 4
    assert not value["solution_exists"]


def test_inverse_eta_gravity_spectator_equations_contradict_mod8():
    value = report()["standard_neutral_free_eta_no_go"]["eta_gravity_spectator"]
    assert value["cubic_left_mod8"] == 0
    assert value["cubic_right_mod8"] == 4
    assert not value["solution_exists"]
    assert value["both_signs_excluded"]


def test_eta_spectator_plus_bound_parent_residue_still_contradicts_mod8():
    value = report()["standard_neutral_free_eta_no_go"][
        "eta_spectator_plus_bound_V71_residue"
    ]
    assert value["cubic_left_mod8"] == 0
    assert value["cubic_right_mod8"] == 2
    assert not value["solution_exists"]


def test_no_go_is_scoped_and_does_not_claim_interacting_classification():
    value = report()["standard_neutral_free_eta_no_go"]
    assert "neutral" in value["scope"]
    assert "gauge-charged" in value["not_a_no_go_for"][0]
    assert any("interacting" in item for item in value["not_a_no_go_for"])
    decision = report()["terminal_decision"]
    assert decision["standard_neutral_free_eta_route_closed"]
    assert not decision["gauge_charged_routes_exhaustively_classified"]
    assert not decision["interacting_endpoint_action_constructed"]


def test_half_level_lattice_is_explicitly_more_permissive_than_ordinary_determinants():
    charges = report()["standard_neutral_free_eta_no_go"]["allowed_charges"]
    assert charges["index_unit"].startswith("I_s and I_d denote one positive")
    assert charges["ordinary_4D_determinant_multiplicity"] == "t in Z"
    assert "t=u/2" in charges["signed_multiplicity"]
    assert "mass-sign difference is integer" in charges["five_dimensional_convention"]


def test_odd_X_module_evades_neutral_parity_but_keeps_mixed_gauge_curvature():
    value = report()["gauge_charged_neutral_theorem_loophole"]
    assert value["all_center_checks_pass"]
    assert value["neutral_mod8_R_coefficient_evasion"] == "-5=-1 mod4"
    assert value["gauge_independent_curvature"].startswith("(5/3)nu^3")
    mixed = value["surviving_mixed_gauge_curvature"]
    assert "nonzero" in mixed["normal_SU5_squared"]
    assert mixed["normal_X_squared"] == "45 nu f_X^2"
    assert not value["same_action_repair"]
    assert not value["full_odd_X_representation_ring_classified"]


def test_clean_parent_residue_inverse_has_forbidden_five_eighths_period():
    value = report()["clean_parent_residue_index_period_no_go"]
    target = value["target"]
    assert target["local_Weyl_moments"] == {"Q1": "-3", "Q3": "3/4"}
    assert target["scaled_n_moments"] == {
        "N1_equals_2Q1": "-6",
        "N3_equals_8Q3": "6",
    }
    witness = value["CP3_full_quotient_witness"]
    assert witness["spin"]
    assert "honest cocharacter" in witness["admissibility"]
    assert Fraction(witness["inverse_residue_period"]) == Fraction(5, 8)
    lattices = value["index_lattices"]
    assert not lattices["inverse_period_belongs_to_integer_lattice"]
    assert not lattices["inverse_period_belongs_to_half_integer_lattice"]
    assert lattices["level4_completed_endpoint_periods"] == [24, -24]
    assert value["forced_correlated_remainder"]["ordinary_Weyl_module"].endswith(
        "3/8 mod Z"
    )
    assert not value["optional_flavor_quotient"]["evades_theorem"]
    assert "CP3 index=-15" in value["correlated_scope_witnesses_not_repairs"][
        "charge_five"
    ]
    assert not value["clean_parent_residue_inverse_exists"]


def test_clean_parent_residue_mod48_cross_check_is_exact():
    value = report()["clean_parent_residue_index_period_no_go"][
        "mod48_singlet_doublet_cross_check"
    ]
    for z in range(-40, 41, 2):
        assert (z**3 - 4 * z) % 48 == 0
    for z in range(-39, 40, 2):
        assert (2 * (z**3 - z)) % 48 == 0
    assert "N3-4N1-4X1+6(D_n+D_x)" in value["summed_identity"]
    assert value["target_residue_mod48"] == 30
    assert value["required_zero_mod48"] == 0
    assert not value["solution_exists"]


def test_level4_field_ledgers_hit_exact_correlated_targets():
    value = report()["correlated_level4_spectrum_redesign"]
    m00 = value["added_modules"]["M00"]
    m11 = value["added_modules"]["M11"]
    assert m00["complex_Weyl_component_count"] == 12
    assert m11["complex_Weyl_component_count"] == 8
    assert m00["SU2R_doublet_count"] == 4
    assert m11["SU2R_doublet_count"] == 2
    assert m00["target_coefficients_g_r_s"] == ["3", "3", "0"]
    assert m11["target_coefficients_g_r_s"] == ["-3", "-3", "0"]
    for module in (m00, m11):
        assert module["all_full_quotient_center_checks_pass"]
        assert module["Witten_SU2_global_parity_even"]
        assert set(module["continuous_moments"].values()) == {"0"}
        assert module["discrete_checks"]["gravity_sum_mdn"] == 0
        assert module["discrete_checks"]["X_squared_mod4"] == 0
        assert module["discrete_checks"]["SU2R_mod2"] == 0


def test_level4_completion_is_integral_and_uses_quantized_bridge_level_minus_four():
    value = report()["correlated_level4_spectrum_redesign"]
    completed = value["completed_classes"]
    assert completed["z00"] == ["4", "4", "0"]
    assert completed["z11"] == ["-4", "-4", "0"]
    assert completed["diagonal_periods"] == [24, -24]
    assert completed["quarter_coset_removed_algebraically"]
    bridge = value["common_overlap_and_bridge"]
    assert bridge["mismatch_without_flavor"] == "4 nu A B"
    assert bridge["required_V74_bridge_level"] == -4
    assert bridge["level_is_quantized"]
    assert not bridge["optional_flavor_bridge_built"]
    assert not value["unresolved_bound_parent"][
        "V71_equal_corner_normal_gravity_residue_cancelled"
    ]


def test_level4_cross_mass_operator_is_selector_safe_but_dynamically_open():
    value = report()["correlated_level4_spectrum_redesign"]
    mass = value["conditional_cross_mass_operator"]
    assert mass["vector_type_scalars"] == {
        "Z00": {"Qphi": -2, "Z4R": 0},
        "Z11": {"Qphi": 2, "Z4R": 0},
    }
    assert mass["z00_charge_check"]["normal"] == "-2+1+2=1"
    assert mass["z11_charge_check"]["normal"] == "+2+0-1=1"
    assert mass["Z4R_preserved_by_condensates"]
    assert not mass["mu_or_16_four_regenerated_by_selection_rule"]
    assert not mass["two_by_two_cross_blocks_full_rank_proven"]
    assert value["beta_function_branches"] == {
        "both_cross_blocks_GUT_rank_two": ["0", "0", "0"],
        "new_charge_five_fields_light": ["12/5", "0", "0"],
        "old_plus_new_charge_five_fields_light": ["24/5", "0", "0"],
    }
    assert not value["same_action_microscopic_completion"]


def test_supersymmetric_mass_and_global_defect_remain_open():
    value = report()["supersymmetry_and_mass_audit"]
    local = value["local_N1_implications"]
    assert "Q_N_MINUS2" in local["z00_Kahler_GM_bilinear"]
    assert "BREAKS_Z4R" in local["z00_superpotential_mass"]
    assert not local["z00_certified_high_scale_mass"]
    assert value["eta_domain_wall_scope"][
        "closed_smooth_spin_H_Dai_Freed_phase_exact"
    ]
    assert not value["eta_domain_wall_scope"][
        "orbifold_relative_capped_Dai_Freed_theory_constructed"
    ]
    assert not value["eta_domain_wall_scope"]["symmetry_preserving_gap_proven"]
    assert not value["accepted_same_action_completion"]


def test_only_level4_spectrum_redesign_is_selected_and_unaccepted():
    rows = report()["F75_candidate_matrix"]
    selected = [row for row in rows if row["selected"]]
    assert [row["id"] for row in selected] == ["F75_GAUGE_CHARGED_SPECTRUM_REDESIGN"]
    assert not selected[0]["accepted"]
    assert not any(row["accepted"] for row in rows)


def test_terminal_decision_is_fail_closed():
    decision = report()["terminal_decision"]
    assert decision["correlated_eta_representative_constructed"]
    assert decision["closed_smooth_spin_H_Dai_Freed_phase_constructed"]
    assert not decision["pure_quarter_spectator_cancelled_by_eta_route"]
    assert decision["level4_quarter_coset_removed_algebraically"]
    assert decision["level4_mass_operator_charge_checks_pass"]
    assert not decision["level4_microscopic_action_constructed"]
    assert not decision["bound_V71_equal_corner_residue_cancelled"]
    assert decision[
        "clean_local_Weyl_or_standard_half_eta_parent_residue_route_closed"
    ]
    assert not decision["same_action_microscopic_completion_found"]
    assert not decision["selected_candidate_accepted"]
    assert decision["closed_gates"] == []
    assert not decision["theory_complete"]
    assert report()["gate_ledger"] == {f"G{i}": "OPEN" for i in range(1, 9)}


def test_core_and_generated_artifacts_are_canonical_when_present():
    value = report()
    assert audit.canonical_sha(value) == value["core_sha256"]
    if audit.OUT_JSON.is_file() and audit.OUT_MD.is_file():
        disk = json.loads(audit.OUT_JSON.read_text(encoding="utf-8"))
        assert disk["core_sha256"] == value["core_sha256"]
        assert audit.OUT_MD.read_text(encoding="utf-8") == audit.render_markdown(value)
