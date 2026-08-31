from __future__ import annotations

from fractions import Fraction
import json

import pytest

import susy_v73_spin11_full_quotient_supersymmetric_wz_audit as audit


def report():
    return audit.build_report()


def test_v73_integrity_and_both_v72_cores_are_bound():
    value = report()
    audit.validate(value)
    assert value["core_sha256"] == audit.canonical_sha(value)
    lineage = value["lineage"]
    assert lineage["bound_V72_route_core"] == audit.EXPECTED_V72_ROUTE_CORE
    assert lineage["bound_V72_master_core"] == audit.EXPECTED_V72_MASTER_CORE
    assert lineage["bound_V71_route_core"] == audit.EXPECTED_V71_ROUTE_CORE
    assert lineage["V72_restricted_coefficients"] == {"z00": 1, "z11": -1}
    assert lineage["V72_all_gates_open"]


def test_exact_weight_rules_distinguish_local_chi5_from_the_full_quotient():
    value = report()["full_diagonal_quotient_lattice"]
    assert value["weight_rules"] == {
        "U5tilde": "k+2x=0 mod5",
        "diagonal_center": "n+x+r=0 mod2",
        "optional_flavor_center": "x+f=0 mod2",
        "normal_charge": "qL=n/2",
    }
    rows = {row["name"]: row for row in value["representation_checks"]}
    assert rows["chi5_standalone"]["U5tilde_descends"]
    assert not rows["chi5_standalone"]["full_diagonal_descends_without_flavor_quotient"]
    assert rows["chiL_chi5"]["full_diagonal_descends_without_flavor_quotient"]
    assert rows["E5R"]["full_diagonal_descends_without_flavor_quotient"]
    assert rows["E5RF"]["full_diagonal_descends_with_flavor_quotient"]
    assert rows["chi5_squared"]["full_diagonal_descends_without_flavor_quotient"]


def test_kernel_congruences_are_recomputed_independently():
    rows = report()["full_diagonal_quotient_lattice"]["representation_checks"]
    for row in rows:
        assert row["U5tilde_descends"] == (
            (row["SU5_five_ality"] + 2 * row["X"]) % 5 == 0
        )
        assert row["full_diagonal_descends_without_flavor_quotient"] == (
            row["U5tilde_descends"]
            and (row["n"] + row["X"] + row["SU2R_highest_weight_parity"]) % 2 == 0
        )
        assert row["full_diagonal_descends_with_flavor_quotient"] == (
            row["full_diagonal_descends_without_flavor_quotient"]
            and (row["X"] + row["F"]) % 2 == 0
        )


def test_abelian_character_and_cocharacter_lattices_have_the_diagonal_half_loop():
    value = report()["full_diagonal_quotient_lattice"]
    assert "n+b=0 mod2" in value["abelian_character_lattice_without_flavor"]
    assert "(Z+1/2)^2" in value["abelian_cocharacter_projection_without_flavor"]
    assert "n congruent b congruent f" in value["abelian_character_lattice_with_flavor"]
    generators = value["cocharacter_lattice_generators_beyond_the_cover"]
    assert generators["kappaD"] == "(1/2,0,1/2,varpiR_dual[,0])"
    assert generators["kappaF_optional"] == "(0,0,1/2,0,-1/2)"


def test_inherited_normalization_is_the_normal_vector_root_not_the_spin_root():
    value = report()["ordinary_WZ_quantization_and_correlated_repair"]["normalization"]
    assert value["V71_definition"] == "fL=x=c1(N)=nu, the normal vector root"
    assert value["primitive_Spin2_root"] == "sigma=nu/2"
    assert value["physical_charge"] == "qL=n/2"
    assert value["restricted_U5tilde_level"] == "1"
    assert Fraction(1, 2) * 50 / 25 == 1


def test_diagonal_cocharacter_gives_25_over_4_and_minimal_multiplier_four():
    value = report()["ordinary_WZ_quantization_and_correlated_repair"][
        "diagonal_cocharacter_test"
    ]
    nu = Fraction(value["nu"])
    ell = Fraction(value["ell"])
    period = nu * ell**2
    assert period == Fraction(25, 4)
    assert value["P_period"] == str(period)
    assert not value["P_integral"]
    multipliers = [m for m in range(1, 17) if (m * period).denominator == 1]
    assert multipliers == value["integral_multipliers_through_16"]
    assert multipliers[0] == value["minimal_pure_multiplier"] == 4
    assert value["sufficiency_identity"] == "4 P=nu (2 ell)^2"
    assert "honest full-quotient lines" in value["sufficiency_reason"]


def test_alternate_spin_root_hybrid_is_not_a_second_physical_answer():
    value = report()["ordinary_WZ_quantization_and_correlated_repair"][
        "alternate_spin_root_convention_not_inherited"
    ]
    assert Fraction(value["period"]) == Fraction(25, 8)
    assert value["minimal_pure_multiplier"] == 8
    assert "hybrid diagnostic" in value["ledger_warning"]
    assert "doubles DeltaA from 50 to 100" in value["consistent_conversion"]
    assert value["consistent_physical_class"] == "(1/2)(100)(nu/2)fX^2=nu ell^2"
    assert value["consistent_minimal_multiplier"] == 4


def test_pure_ordinary_counterterm_is_rejected_without_rejecting_eta_refinement():
    value = report()["ordinary_WZ_quantization_and_correlated_repair"]
    scope = value["ordinary_vs_spin_eta_scope"]
    assert not value["F72_pure_ordinary_WZ_accepted"]
    assert scope["ordinary_integral_H6_counterterm"] == "FAIL"
    assert scope["rational_perturbative_spin_anomaly_polynomial"] == "ALLOWED_AS_LOCAL_DATA"
    assert scope["eta_or_Wu_refined_invertible_theory"] == "OPEN_NOT_CONSTRUCTED"


def test_E5R_correlated_class_is_integral_and_forces_the_R_term():
    value = report()["ordinary_WZ_quantization_and_correlated_repair"][
        "correlated_E5R_repair"
    ]
    ell = Fraction(5, 2)
    rho = Fraction(1, 2)
    assert ell**2 - rho**2 == 6
    assert value["kappaD_c2_period"] == "6"
    assert value["kappaD_nu_c2_period"] == "6"
    assert value["integral_by_associated_bundle"]
    assert value["forced_component"].startswith("+nu c2(R)")
    assert not value["full_R_anomaly_ledger_computed"]


def test_normal_line_correlated_class_is_integral_but_spectator_is_unmatched():
    value = report()["ordinary_WZ_quantization_and_correlated_repair"][
        "correlated_normal_line_repair"
    ]
    assert value["kappaD_period"] == "6"
    assert value["integral_by_product_of_honest_lines"]
    assert value["forced_component"] == "-nu^3/4"
    assert not value["existing_V71_symmetric_normal_cubic_ledger_supplies_it"]
    assert "(-1/4,+1/4)" in value["reason"]


def test_existing_bulk_SU2R_numerical_attempt_is_explicitly_uncertified():
    value = report()["existing_bulk_SU2R_spectator"]
    exact = value["exact_bound_inputs"]
    c = [Fraction(item) for item in exact["V71_spin_half_linear_coefficients_c_m0123"]]
    assert c == [Fraction(1, 8), Fraction(-1, 8), Fraction(-1, 8), Fraction(1, 8)]
    assert exact["Spin11_adjoint_phase_dimensions_m0123"] == [25, 5, 20, 5]
    attempt = value["uncertified_11_over_16_attempt"]
    assert attempt["attempted_total_each_corner"] == "11/16"
    assert not attempt["certified"]
    assert "already uses the total phase" in attempt["blocking_reason"]
    assert value["bulk_total_each_Z4_corner_nu_c2R"] == "OPEN_NOT_CERTIFIED"


def test_correlated_PR_has_no_symmetric_bulk_R_GS_solution():
    value = report()["existing_bulk_SU2R_spectator"]
    assert value["inherited_bulk_sources_have_identical_corner_lift"]
    assert not value["common_bulk_R_GS_solution_exists"]
    assert "(C+1,C-1)" in value["proof"]
    assert value["required_new_antisymmetric_source"] == [
        "-nu c2(R)",
        "+nu c2(R)",
    ]


def test_optional_flavor_completion_has_exact_forced_terms():
    value = report()["ordinary_WZ_quantization_and_correlated_repair"][
        "optional_flavor_completion"
    ]
    assert value["center_checks"] == ["x+r=0 mod2", "x+f=0 mod2"]
    assert value["c2"] == "(ell+v)^2+c2(R)"
    assert value["expanded_forced_terms"] == [
        "nu c2(R)",
        "2 nu ell v",
        "nu v^2",
    ]
    assert not value["pure_term_rescued_without_correlated_terms"]


def test_common_corner_identity_leaves_a_nonzero_AB_residue():
    value = report()["z00_z11_common_subgroup_gluing"]
    # Independent coefficient expansion:
    # ((A+B)/2)^2-((A-B)/2)^2 has only A*B with coefficient one.
    first = {
        "A2": Fraction(1, 4),
        "AB": Fraction(1, 2),
        "B2": Fraction(1, 4),
    }
    second = {
        "A2": Fraction(1, 4),
        "AB": Fraction(-1, 2),
        "B2": Fraction(1, 4),
    }
    difference = {key: first[key] - second[key] for key in first}
    assert difference == {"A2": 0, "AB": 1, "B2": 0}
    assert value["exact_identity"] == "ell^2-ellprime^2=A B"
    assert value["opposite_profile_common_restriction_inherited_normalization"] == "nu A B"
    assert not value["ordinary_single_transfer_glues"]
    assert not value["coefficient_sum_zero_sufficient"]


def test_flavor_and_z11_center_sign_do_not_remove_the_curvature_residue():
    value = report()["z00_z11_common_subgroup_gluing"]
    assert value["optional_flavor_identity"] == (
        "(ell+v)^2-(ellprime+v)^2=A B+2 B v"
    )
    z11 = value["z11_conjugation"]
    assert z11["odd_X_isotropy_phase_flips"]
    assert not z11["curvature_square_gets_automatic_minus_sign"]
    assert z11["normal_derivative_orientation"].endswith("+i")


def test_unique_SU5_characteristic_correction_is_the_bulk_direction():
    value = report()["z00_z11_common_subgroup_gluing"][
        "SU5_characteristic_correction_theorem"
    ]
    # Solve a+b=0 and 1+a-b=0 independently.
    b = Fraction(1, 2)
    a = -b
    assert a + b == 0
    assert 1 + a - b == 0
    assert 1 - 2 * b == 0
    assert value["unique_solution"] == {"a": "-1/2", "b": "1/2"}
    assert value["solution_checks"] == {
        "common_c2_coefficient": "0",
        "common_AB_coefficient": "0",
    }
    assert value["bundle_Chern_classes"]["difference"] == "c2(E)-c2(Eprime)=2 A B"
    assert value["corrected_forms"] == {
        "W00": "+p1(V10)/4",
        "W11": "-p1(V10)/4",
    }
    assert value["p1_over_4_ordinary_integrality"].startswith("OPEN")
    assert not value["rescues_F72_orthogonal_transfer"]


def test_component_center_patterns_reject_P0_as_an_ordinary_hyper():
    value = report()["scalar_fermion_center_patterns"]
    assert value["standard_hyper_pattern"]["criterion"] == "n_phi+x is odd"
    assert value["vector_type_pattern"]["criterion"] == "n_phi+x is even"
    assert value["all_F71_charge_five_standard_hypers_pass"]
    assert not value["all_F72_z00_fields_standard_hypers_pass"]
    assert value["all_F72_z00_fields_vector_type_centers_pass"]
    rows = {row["name"]: row for row in value["F72_z00_rows"]}
    assert not rows["P0"]["standard_hyper_center_pass"]
    assert rows["P0"]["vector_type_center_pass"]
    assert not value["P0_as_ordinary_neutral_hyper"]


def test_axino_and_R2_partner_polynomials_cancel_exactly():
    value = report()["N1_axion_GCS_and_tensor_completion"]
    axino = value["axino"]
    partner = value["neutral_R2_partner"]
    assert axino["qL_fermion"] == "-1/2"
    assert axino["I6_coefficients_x3_xp1"] == ["-1/48", "1/48"]
    assert partner["qL_fermion"] == "1/2"
    assert partner["I6_coefficients_x3_xp1"] == ["1/48", "-1/48"]
    assert not value["pair_ledger"]["unique_consequence_of_supersymmetry_alone"]
    assert len(value["pair_ledger"]["minimality_assumptions"]) == 3
    pair = value["pair_ledger"]
    assert pair["Q1"] == pair["Q3"] == "0"
    assert pair["I6_coefficients_x3_xp1"] == ["0", "0"]
    assert pair["preserves_local_Delta_minus10_normal_gravity_factorization"]


def test_local_N1_action_is_schematic_and_requires_GCS():
    value = report()["N1_axion_GCS_and_tensor_completion"]["N1_structure"]
    action = value["local_chiral_action_schema"]
    assert "A_i-i m_i Lambda_L" in action["gauge_transformations"][1]
    assert "Omega(E_i)" in action["Bardeen_GCS"]
    assert "preserving the fixed-group gauge current" in action["why_GCS_is_required"]
    assert value["status"].startswith("SCHEMATIC_FLAT_N1_DESCENT_ONLY")
    assert "normal/Lorentz-R" in action["scope"]
    levels = value["provisional_compact_level_normalization"]
    assert levels["z00"] == "m00 k00=+1"
    assert levels["z11"] == "m11 k11=-1"
    assert levels["formal_integer_solution_after_unit_normalization"] == (
        "|m_i|=|k_i|=1 for one compact multiplet"
    )
    assert not levels["normalization_pinned"]
    assert value["gauge_kinetic_positivity_and_stabilization"] == "OPEN_NOT_COMPUTED"


def test_axino_polynomial_is_independently_derived_from_the_Weyl_index():
    q = Fraction(-1, 2)
    assert q**3 / 6 == Fraction(-1, 48)
    assert -q / 24 == Fraction(1, 48)
    q_partner = -q
    assert q_partner**3 / 6 == Fraction(1, 48)
    assert -q_partner / 24 == Fraction(-1, 48)


def test_P0_is_the_partner_not_the_affine_axion():
    value = report()["N1_axion_GCS_and_tensor_completion"]
    distinction = value["P0_is_not_the_axion"]
    assert distinction["P0"].startswith("homogeneous R=2")
    assert distinction["A"].startswith("homogeneous R=0")
    assert "singular at P0=0" in distinction["log_P0"]
    assert not distinction["identification_valid"]
    route = value["two_independent_localized_axion_route"]
    assert route["new_axinos"] == 2
    assert route["new_R2_partners_beyond_the_provisional_F72_P0"] == 2
    assert "cannot cancel the new axino a second time" in route["z00"]
    assert "minimal under" in route["partner_count_scope"]
    assert not route["accepted"]


def test_existing_tensor_route_is_preferred_but_not_accepted():
    value = report()["N1_axion_GCS_and_tensor_completion"][
        "preferred_existing_tensor_route"
    ]
    assert "existing six-dimensional tensor" in value["candidate"]
    assert "bridge/transgression" in value["candidate"]
    assert "pre-existing tensor itself adds no new localized axino" in value["potential_advantage"]
    assert not value["complete_bridge_field_content_known"]
    assert value["common_residue"] == "nu A B"
    assert value["common_residue_is_nonzero_free_de_Rham_class"]
    assert not value["torsion_or_zero_curvature_eta_refinement_can_cancel_residue"]
    assert value["required_bridge_curvature_or_anomaly_polynomial"] == "-nu A B"
    assert "it then is the bridge/inflow sector" in value["spin_eta_scope"]
    assert not value["single_ordinary_transfer_cocycle_exists"]
    assert value["ordinary_opposite_slope_tensor_subcandidate_rejected"]
    assert value["selected_for_next_frontier"]
    assert not value["accepted"]


def test_candidate_matrix_has_one_selected_and_no_accepted_route():
    rows = report()["F73_candidate_matrix"]
    assert [row["id"] for row in rows] == [
        "F72_PURE",
        "F73_AXION",
        "F73_NORMAL",
        "F73_FLAVOR",
        "F73_TENSOR_BRIDGE",
    ]
    assert sum(row["selected"] for row in rows) == 1
    assert next(row for row in rows if row["selected"])["id"] == "F73_TENSOR_BRIDGE"
    assert not any(row["accepted"] for row in rows)


def test_fail_closed_decision_and_all_gates_remain_open():
    value = report()
    adjudication = value["candidate_adjudication"]
    assert adjudication["F72_pure_full_quotient_ordinary_WZ"].startswith("REJECTED")
    assert adjudication["F73_correlated_E5R_local_class"].startswith("PASS_EXACT")
    assert adjudication["F73_plain_opposite_slope_tensor"].startswith("REJECTED")
    assert adjudication["F73_tensor_bridge_inflow_route"].startswith("SELECTED")
    decision = value["terminal_decision"]
    assert not decision["F72_pure_WZ_accepted"]
    assert decision["F73_plain_tensor_subcandidate_rejected"]
    assert decision["F73_tensor_bridge_inflow_route_selected"]
    assert not decision["F73_tensor_bridge_inflow_route_accepted"]
    assert decision["closed_gates"] == []
    assert not decision["theory_complete"]
    assert all(state == "OPEN" for state in value["gate_ledger"].values())


def test_validation_is_mutation_sensitive_to_the_period():
    value = report()
    value["ordinary_WZ_quantization_and_correlated_repair"][
        "diagonal_cocharacter_test"
    ]["P_period"] = "1"
    value["core_sha256"] = audit.canonical_sha(value)
    with pytest.raises(RuntimeError, match="period"):
        audit.validate(value)


def test_generated_artifacts_are_required_and_match():
    value = report()
    assert audit.JSON_PATH.is_file()
    assert audit.MD_PATH.is_file()
    assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == value
    assert audit.MD_PATH.read_text(encoding="utf-8") == audit.render_markdown(value)
