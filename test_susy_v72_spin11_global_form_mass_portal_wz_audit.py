from __future__ import annotations

import copy
from fractions import Fraction
import json

import pytest

import susy_v72_spin11_global_form_mass_portal_wz_audit as audit


def report():
    return audit.build_report()


def test_v72_integrity_and_lineage_are_exact():
    value = report()
    audit.validate(value)
    assert value["core_sha256"] == audit.canonical_sha(value)
    assert value["lineage"]["bound_V71_core"] == audit.EXPECTED_V71_CORE
    assert value["lineage"]["bound_V70_core"] == audit.EXPECTED_V70_CORE


def test_true_fixed_group_is_the_connected_spin_preimage():
    value = report()["true_fixed_group_and_global_gluing"]
    assert value["centralizer_proof"]["SO11_centralizer"].startswith("U(5)")
    assert "U(5)-tilde" in value["centralizer_proof"]["Spin11_centralizer"]
    assert value["presentations"]["pullback"] == "{(A,u) in U(5)xU(1): u^2=det(A)}"
    assert value["presentations"]["quotient"] == "(SU(5)xU(1)_X)/<(omega I5,omega^2)>"
    assert value["representation_rule"].endswith("k+2x=0 mod5")


def test_representation_lattice_validates_charge_five_but_not_vector_U5():
    value = report()["true_fixed_group_and_global_gluing"]
    rows = {row["representation"]: row for row in value["representation_checks"]}
    assert all(row["k_plus_2x_mod5"] == 0 for row in rows.values())
    assert rows["1_(+5)"]["descends_to_U5_tilde"]
    assert not rows["1_(+5)"]["descends_to_vector_U5"]
    assert rows["1_(+10)"]["descends_to_vector_U5"]
    chars = value["character_group"]
    assert chars["generator"] == "chi5([S,t])=t^5=u"
    assert chars["singlet_lattice_U5_tilde"] == "X in 5 Z"
    assert chars["singlet_lattice_vector_U5"] == "X in 10 Z"


def test_quotient_kernel_phases_and_vector_descent_are_recomputed_independently():
    rows = report()["true_fixed_group_and_global_gluing"]["representation_checks"]
    for row in rows:
        kernel_exponent = row["SU5_five_ality"] + 2 * row["X"]
        assert kernel_exponent % 5 == 0
        expected_center_phase = -1 if row["X"] % 2 else 1
        assert row["spin_cover_center_phase"] == expected_center_phase
        assert row["descends_to_vector_U5"] == (row["X"] % 2 == 0)


def test_spinor_branching_and_z11_center_sign_are_bound():
    value = report()["true_fixed_group_and_global_gluing"]
    assert value["spinor_branching"]["16_even_p"] == "1_-5 + 10_-1 + 5bar_3"
    assert value["spinor_branching"]["11"] == "5_2 + 5bar_-2 + 1_0"
    z11 = value["z11_conjugate_stabilizer"]
    assert z11["lift_relation"] == "qhat_prime=-s qhat s^-1"
    assert z11["chi5_isotropy_sign_must_be_tracked"]


def test_combined_center_pattern_is_possible_but_not_yet_a_multiplet():
    value = report()["true_fixed_group_and_global_gluing"]["combined_local_center_quotient"]
    assert value["component_rule"] == "n+x+r=0 mod2"
    assert all(row["hypermultiplet_center_pattern_passes"] for row in value["charge_five_checks"])
    assert "standalone 4D chirals" in value["consequence"]


def test_translation_lifts_have_a_real_cocycle_and_only_an_algebraic_completion():
    value = report()["true_fixed_group_and_global_gluing"]["space_group_cocycle"]
    assert not value["ordinary_wallpaper_homomorphism"]
    assert value["odd_X_line_mismatch"] == "-1"
    assert value["completion_exists_algebraically"]
    assert not value["completion_applied_to_full_action"]
    assert not value["global_equivariant_orbibundle_constructed"]
    assert "U(1)_F" in value["minimal_algebraic_completion"]


def test_z00_all_order_ring_has_no_charge_five_mass_or_interaction():
    value = report()["charge_five_mass_and_portal_audit"]["z00_all_order_module_ring"]
    assert value["solution"] == "p=m=0, c=1, a=b"
    assert value["finite_symbolic_check_only_S_times_equal_rank"]
    assert value["ring"] == "W00=S0 F(N_i,X Xbar)"
    assert not value["charge_five_W_mass_or_interaction_at_any_order"]
    assert "(S0^dagger)^2" in value["first_existing_field_mass_like_Kahler"]
    assert value["inactive_on_V70_branch"] == "<S0>=F_S0=0"


def test_z00_Diophantine_solution_is_independently_exhausted_to_rank_20():
    solutions = []
    for a in range(21):
        for b in range(21):
            for c in range(2):
                for p in range(2):
                    for m in range(2):
                        if c + p + m == 1 and 2 * (a - b) + p - m == 0:
                            solutions.append((a, b, c, p, m))
    assert set(solutions) == {(a, a, 1, 0, 0) for a in range(21)}


def test_z11_ring_has_no_bare_mass_and_full_rank_needs_symmetry_breaking():
    value = report()["charge_five_mass_and_portal_audit"]["z11_all_order_module_ring"]
    assert value["invariants"] == "M_ab=Pprime+_a Pprime-_b"
    assert value["determinantal_relation"] == "M11 M22-M12 M21=0"
    assert not value["bare_mass"]
    assert "breaks continuous U1L" in value["full_rank_from_Z_VEV"]
    assert "supergravity" in value["GM_boundary"]


def test_mass_anomaly_matching_theorem_rejects_a_trivial_gap():
    value = report()["charge_five_mass_and_portal_audit"]["mass_anomaly_matching_theorem"]
    assert value["fermion_normal_sum"].endswith("=0")
    assert value["conjugate_pair_mixed_anomaly"].endswith("=0")
    assert not value["full_rank_trivially_gapped_sector_nonzero_U1L_X2_anomaly"]
    assert value["F71_required_nonzero_shifts"] == {"z00_charge_five": "+50", "z11": "-50"}
    assert value["opposite_q_partners_erase_repair"]
    assert value["symmetry_breaking_mass_requires_WZ_transfer"]


def test_all_order_portal_parity_makes_the_lightest_z11_state_stable():
    value = report()["charge_five_mass_and_portal_audit"][
        "all_order_nonderivative_chiral_portal_theorem"
    ]
    assert value["charge_five_center_parity"] == "odd"
    assert "odd number" in value["gauge_invariance_linear_in_P"]
    assert not value["nonderivative_local_chiral_W_or_K_portal_at_any_order"]
    assert value["lightest_charge_five_state_stable"]
    assert value["z11_lightest_electric_charge_absolute"] == 1
    assert "no co-localized family" in value["z11_locality"]
    assert "nonlocal interactions" in value["scope"]
    assert "arbitrary new bridge sectors are not excluded" in value["scope"]


def test_operator_ring_scope_does_not_overclaim_unpinned_V70_lifts():
    scope = report()["charge_five_mass_and_portal_audit"]["scope_boundary"]
    assert scope["complete_corrected_module_ring"]
    assert not scope["complete_mixed_V70_V71_ring"]
    assert "P3(A0,S0) is not invariant" in scope["reason"]


def test_discrete_R_new_field_and_complete_module_ledgers_are_distinguished():
    value = report()["discrete_R_running_and_relic_audit"]
    new = value["new_field_shifts_relative_to_V70"]
    assert new["z00"] == {"Delta_A3": 0, "Delta_A2": 0, "Delta_A_X2R": 100, "Delta_Agrav": 1}
    assert new["z11"]["Delta_A_Xprime2R"] == -100
    assert new["z11"]["Delta_A1_GUT"] == "-12/5"
    complete = value["complete_local_modules"]
    assert complete["z00_Agrav"] == complete["z11_Agrav"] == 0
    assert complete["both_Agrav_zero_from_Q1_zero"]
    assert complete["doubled_X2R_mod4"] == {"z00": 0, "z11": 0}
    assert complete["full_bulk_gravitino_tensor_neutral_discrete_ledger"] == "OPEN_NOT_COMPUTED"


def test_two_charged_pairs_shift_only_b1_and_distort_unification():
    value = report()["discrete_R_running_and_relic_audit"]["charged_z11_threshold"]
    assert value["number_of_vectorlike_pairs"] == 2
    assert value["Delta_b_per_pair"] == {"b1_GUT": "6/5", "b2": "0", "b3": "0"}
    assert value["Delta_b_total"] == {"b1_GUT": "12/5", "b2": "0", "b3": "0"}
    assert "ln(M23^2/(M1 M2))" in value["two_mass_one_loop_shift"]
    assert value["unification_without_compensating_thresholds"] == "requires sqrt(M1 M2)=M23"
    assert value["do_not_splice_V65_orphans"]


def test_stable_charged_relic_thermal_viability_remains_open_without_a_yield():
    value = report()["discrete_R_running_and_relic_audit"]["stable_charged_relic"]
    assert not value["GM_mass_breaks_exotic_number"]
    assert value["lightest_state_stable_without_portal"]
    assert value["CMS_one_species_Q1_DY_observed_limit_TeV"] == "1.14"
    assert value["two_species_recast_required"]
    assert value["long_lifetime_reference"] == {"tau_seconds": ">1e5", "n_over_s_sensitivity": "3e-17"}
    assert not value["thermal_freezeout_yield_computed"]
    assert value["standard_thermal_history_viability"] == "OPEN_NOT_COMPUTED"
    assert value["qualitative_thermal_assessment"].startswith("EXPECTED_SEVERELY_CONSTRAINED")
    assert "conditional only" in value["low_reheat_loophole"]


def test_F72_opposite_WZ_transfer_aligns_both_corners():
    value = report()["F72_opposite_level_WZ_transfer_candidate"]
    assert value["bulk_each_corner"] == ["-1/4", "40"]
    assert value["aligned_target"] == ["-1/4", "-10"]
    assert value["z00"]["fermion_shift"] == ["0", "-100"]
    assert value["z00"]["WZ_variation"] == ["0", "50"]
    assert value["z11"]["charged_defect_fermions_added"] == 0
    assert value["z11"]["WZ_variation"] == ["0", "-50"]
    assert value["z00"]["final_vector"] == value["z11"]["final_vector"] == ["-1/4", "-10"]
    assert value["both_corners_align"]


def test_WZ_coefficients_pass_only_the_U5tilde_restricted_integrality_check():
    value = report()["F72_opposite_level_WZ_transfer_candidate"][
        "U5tilde_restricted_local_coefficient_integrality"
    ]
    assert value["primitive_character"] == "chi5=1_(+5)"
    assert value["line_class"] == "l=c1(chi5)=5 f_X"
    assert value["restricted_coefficients"] == {"z00": 1, "z11": -1}
    assert value["coefficient_sum"] == 0
    assert value["restricted_denominator"] == 1
    assert not value["full_diagonal_quotient_level_quantization_established"]
    assert "necessary integrality check" in value["scope"]
    assert "quarter-integral" in value["vector_U5_counterfactual"]


def test_WZ_restricted_coefficients_are_recomputed_from_the_anomaly_polynomial():
    assert Fraction(1, 2) * 50 / (5**2) == 1
    assert Fraction(1, 2) * -50 / (5**2) == -1


def test_F72_improves_physics_but_remains_unaccepted():
    value = report()["F72_opposite_level_WZ_transfer_candidate"]
    advantages = value["advantages_over_F71_charge_five_fermions"]
    assert advantages["new_electrically_charged_fields"] == 0
    assert advantages["new_one_loop_SM_beta_shift"] == {"b1": "0", "b2": "0", "b3": "0"}
    assert advantages["no_new_F71_type_stable_charged_relic"]
    assert value["not_yet_constructed"]
    assert value["selected_for_next_frontier"]
    assert not value["accepted"]
    assert not value["same_action_complete"]


def test_fail_closed_decision_and_all_gates_open():
    value = report()
    adjudication = value["candidate_adjudication"]
    assert adjudication["F71_charge_five_local_representation"] == "PASS_EXACT"
    assert adjudication["F71_conventional_massive_decaying_completion"].startswith("REJECTED")
    assert adjudication["F72_U5tilde_restricted_WZ_coefficient"].startswith("PASS_EXACT")
    assert adjudication["F72_global_supersymmetric_action"] == "OPEN_NOT_CONSTRUCTED"
    decision = value["terminal_decision"]
    assert decision["F72_selected"]
    assert not decision["F72_accepted"]
    assert not decision["same_action_microscopic_completion_found"]
    assert decision["closed_gates"] == []
    assert not decision["theory_complete"]
    assert all(state == "OPEN" for state in value["gate_ledger"].values())


def test_validation_is_mutation_sensitive():
    value = report()
    value["F72_opposite_level_WZ_transfer_candidate"][
        "U5tilde_restricted_local_coefficient_integrality"
    ]["restricted_coefficients"]["z11"] = 0
    value["core_sha256"] = audit.canonical_sha(value)
    with pytest.raises(RuntimeError, match="wz_restricted_coefficients"):
        audit.validate(value)


def test_generated_artifacts_are_required_and_match():
    value = report()
    assert audit.JSON_PATH.is_file()
    assert audit.MD_PATH.is_file()
    assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == value
    assert audit.MD_PATH.read_text(encoding="utf-8") == audit.render_markdown(value)
