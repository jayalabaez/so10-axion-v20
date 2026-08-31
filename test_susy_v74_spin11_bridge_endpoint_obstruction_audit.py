from fractions import Fraction
import json

import pytest

import susy_v74_spin11_bridge_endpoint_obstruction_audit as audit


def report():
    return audit.build_report()


def coefficient_of_product(linears, powers):
    polynomial = {(0,) * len(powers): 1}
    for linear in linears:
        updated = {}
        for monomial, coefficient in polynomial.items():
            for index, value in enumerate(linear):
                new_monomial = list(monomial)
                new_monomial[index] += 1
                key = tuple(new_monomial)
                updated[key] = updated.get(key, 0) + coefficient * value
        polynomial = updated
    return polynomial.get(tuple(powers), 0)


def determinant3(rows):
    (a, b, c), (d, e, f), (g, h, i) = rows
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)


def test_v73_route_and_master_cores_are_bound_exactly():
    value = report()["lineage"]
    assert value["V73_route_core"] == audit.EXPECTED_CORES["v73_route"]
    assert value["V73_master_core"] == audit.EXPECTED_CORES["v73_master"]


def test_parent_binding_rejects_an_embedded_core_with_mutated_content(tmp_path):
    parent = json.loads(audit.V73_ROUTE_PATH.read_text(encoding="utf-8"))
    parent["status"] = parent["status"] + "__MUTATED"
    mutated = tmp_path / "mutated_parent.json"
    mutated.write_text(json.dumps(parent), encoding="utf-8")
    with pytest.raises(RuntimeError, match="noncanonical parent core"):
        audit.load_bound(mutated, audit.EXPECTED_CORES["v73_route"])


def test_common_k_cocharacter_generators_obey_the_parity_relation():
    value = report()["common_K_lattice_and_spin_periods"]
    assert value["abelian_cocharacter_projection"].endswith("nu-A-B=0 mod2}")
    for nu, a, b in value["generators"]:
        assert (nu - a - b) % 2 == 0


def test_half_sum_is_an_honest_character_on_the_lattice():
    for nu in range(-3, 4):
        for a in range(-3, 4):
            for b in range(-3, 4):
                if (nu - a - b) % 2 == 0:
                    assert Fraction(nu + a + b, 2).denominator == 1


def test_both_diagonal_cocharacters_are_allowed_and_have_opposite_ab():
    value = report()["common_K_lattice_and_spin_periods"]
    k00 = value["diagonal_cocharacters"]["z00"]
    k11 = value["diagonal_cocharacters"]["z11"]
    assert value["diagonal_relation_checks"] == {"z00": True, "z11": True}
    assert k00[0] * k00[1] * k00[2] == 6
    assert k11[0] * k11[1] * k11[2] == -6


def test_cp2_times_cp1_witness_makes_nu_ab_primitive():
    # nu=x, A=x+y, B=y; coefficient of x^2 y is one.
    period = coefficient_of_product([(1, 0), (1, 1), (0, 1)], (2, 1))
    value = report()["common_K_lattice_and_spin_periods"][
        "ordinary_primitivity_witness"
    ]
    assert period == value["period"] == 1


def test_spin_mod_two_identity_is_the_steenrod_square():
    value = report()["common_K_lattice_and_spin_periods"]["spin_period_theorem"]
    assert value["mod2_relation"] == "nu=A+B"
    assert value["steenrod_identity"] == "r=A^2 B+A B^2=Sq^2(A B) mod2"
    assert value["all_spin_periods_even"]


def test_s2_cubed_witness_shows_spin_period_gcd_two():
    # nu=x, A=x+y, B=y+2z; coefficient of xyz is two.
    period = coefficient_of_product(
        [(1, 0, 0), (1, 1, 0), (0, 1, 2)], (1, 1, 1)
    )
    value = report()["common_K_lattice_and_spin_periods"]["spin_period_theorem"]
    assert period == value["sharp_witness"]["period"] == 2
    assert value["free_spin_period_gcd"] == 2
    assert value["free_curvature_candidate_level_lattice"] == "(1/2) Z"
    assert value["full_differential_Dai_Freed_refinement"] == "OPEN"


def test_differential_cup_bridge_is_ordinary_level_one_quantized():
    value = report()["differential_cohomology_bridge"]
    assert "c1check(N)" in value["differential_character"]
    assert value["ordinary_level_one_quantized"]
    assert "in 2 pi i Z" in value["large_normal_gauge_transformation"]


def test_bridge_is_new_anomalous_k_sector_not_a_degree_five_trivialization():
    value = report()["differential_cohomology_bridge"]["Mayer_Vietoris_scope"]
    assert value["mismatch"] == "r=nu A B is nonzero in free cohomology"
    assert not value["degree_five_trivialization_exists"]
    assert "new anomalous K sector" in value["interpretation"]


def test_smooth_spin11_restriction_has_no_ab_direction():
    value = report()["differential_cohomology_bridge"]["smooth_Spin11_restriction"]
    assert value["AB_coefficient"] == 0
    assert not value["nu_AB_in_image"]
    assert not value["existing_two_form_tensor_supplies_bridge"]


def test_physical_bridge_requires_a_new_k_reducing_defect():
    value = report()["differential_cohomology_bridge"]["physical_defect_requirements"]
    assert not value["T2_over_Z4_has_codimension_one_K_fixed_stratum"]
    assert value["new_K_reducing_domain_wall_or_order_parameter"]
    assert value["Z4_orbit_and_isotropy_lifts"].startswith("OPEN")


def test_unit_local_completion_forces_opposite_quarter_spectators():
    value = report()["endpoint_spectator_theorem"]
    spectators = value["general_integral_completion_theorem"][
        "signed_fractional_spectators"
    ]
    assert Fraction(value["unit_target"]["P_diagonal_period"]) == Fraction(25, 4)
    assert Fraction(spectators["z00"]) == Fraction(-1, 4)
    assert Fraction(spectators["z11"]) == Fraction(1, 4)
    assert value["general_integral_completion_theorem"][
        "independent_of_choice_of_integral_completion"
    ]


def test_integer_bridge_levels_cannot_change_the_quarter_class():
    value = report()["endpoint_spectator_theorem"]
    assert value["bridge_endpoint_periods"] == {"z00": 6, "z11": -6}
    for level in range(-8, 9):
        assert (6 * level) % 1 == 0
    assert not value["quarter_class_changed_by_bridge"]


def test_allowed_free_spin_half_levels_still_shift_integrally():
    value = report()["endpoint_spectator_theorem"]
    for twice_level in range(-9, 10):
        level = Fraction(twice_level, 2)
        assert (6 * level).denominator == 1
    assert value["free_spin_bridge_shifts"] == "3 Z at either endpoint"


def test_correlated_class_integrality_congruence_is_exact():
    value = report()["endpoint_spectator_theorem"]["correlated_class_lattice"]
    assert value["integrality_congruence"] == "g-rR+sN=0 mod4"
    for g in range(-4, 5):
        for r_r in range(-4, 5):
            for s_n in range(-4, 5):
                period = Fraction(25 * g - r_r + s_n, 4)
                assert (period.denominator == 1) == ((g - r_r + s_n) % 4 == 0)


def test_correlated_lattice_basis_has_index_four():
    value = report()["endpoint_spectator_theorem"]["correlated_class_lattice"]
    basis = value["Z_basis"]
    assert abs(determinant3(basis)) == value["basis_index_in_Z3"] == 4
    dependent = value["useful_dependent_integral_class"]
    assert tuple(dependent["vector"]) == tuple(
        basis[0][index] - basis[1][index] for index in range(3)
    )


def test_endpoint_symmetric_correlated_spectators_are_impossible_mod_four():
    # +1-r+s=0 and -1-r+s=0 cannot both hold modulo four.
    solutions = []
    for r_r in range(4):
        for s_n in range(4):
            if (1 - r_r + s_n) % 4 == 0 and (-1 - r_r + s_n) % 4 == 0:
                solutions.append((r_r, s_n))
    value = report()["endpoint_spectator_theorem"]["correlated_class_lattice"]
    assert solutions == []
    assert not value["endpoint_symmetric_rR_and_sN_possible_for_g_plus1_minus1"]


def test_torsion_only_eta_cannot_cancel_nonzero_free_curvature():
    value = report()["endpoint_spectator_theorem"]["eta_scope"]
    assert not value["torsion_only_or_zero_curvature_eta_cancels_free_residue"]
    assert not value["torsion_only_or_zero_curvature_eta_cancels_quarter_spectator"]
    assert "curvature kernel" in value["reason"]


def test_coefficient_four_is_integral_but_overshoots_current_anomaly():
    value = report()["endpoint_spectator_theorem"]["coefficient_four_escape"]
    assert Fraction(value["diagonal_period"]) == 25
    assert value["ordinary_integral"]
    assert value["inverse_bridge_level"] == -4
    assert value["overshoot_units"] == 3
    assert value["mixed_ledger_overshoot_DeltaA"] == 150
    assert not value["repairs_current_action"]


def test_four_form_bf_scaffold_has_the_required_endpoint_orientation():
    value = report()["supersymmetric_vector_linear_scaffold"][
        "bosonic_local_scaffold"
    ]
    assert value["orientation"] == "boundary(gamma)=z11-z00"
    assert value["derivative"] == "d omega5_LAB=-nu A B"
    assert value["invariant_H5"]
    assert "delta11-delta00" in value["source"]


def test_vector_linear_smooth_perturbative_i8_cancels_but_pointwise_is_open():
    value = report()["supersymmetric_vector_linear_scaffold"][
        "new_multiplet_anomaly_ledger"
    ]
    assert value["Omega_plus"] == "+P_R"
    assert value["phi_minus"] == "-P_R"
    assert value["sum"] == "0"
    assert value["irreducible_p2_sum"] == "0"
    assert value["smooth_perturbative_I8_cancellation"]
    assert value["pointwise_equivariant_cancellation"].startswith("OPEN")
    assert not value["single_linear_without_compensating_anomaly_sector_allowed"]


def test_gaugino_condition_keeps_source_normalization_and_full_bps_open():
    value = report()["supersymmetric_vector_linear_scaffold"]["minimal_multiplets"]
    assert "(gamma dot F_Delta)" in value["gaugino_variation_condition"]
    assert not value["component_contraction_to_F56_fixed"]
    assert not value["full_BPS_and_source_equations_solved"]


def test_vector_linear_pair_does_not_cancel_the_endpoint_spectator():
    value = report()["supersymmetric_vector_linear_scaffold"]["endpoint_spectator"]
    assert value["vector_linear_pair_contribution"] == "0"
    assert not value["quarter_spectator_cancelled"]
    assert not value["twisting_lifts_to_leave_quarter_is_BF_compatible"]
    assert value["additional_free_curvature_or_fields_required"]


def test_existing_two_form_tensor_is_not_the_new_four_form_linear_multiplet():
    value = report()["supersymmetric_vector_linear_scaffold"][
        "existing_tensor_distinction"
    ]
    assert value["existing_physical_field"].startswith("anti-self-dual")
    assert "opposite duality to gravity B_plus" in value["existing_physical_field"]
    assert value["bridge_field"] == "four-form linear multiplet"
    assert not value["same_field"]


def test_profile_identity_has_only_the_zero_gluing_solution():
    value = report()["alternative_profile_and_matter_audit"]["profile_theorem"]
    assert value["scope"] == "displayed pure determinant-square ansatz only"
    assert value["zero_overlap_coefficients"] == "k0+k1=0 and k0-k1=0"
    assert value["only_zero_solution"] == {"k0": 0, "k1": 0}
    assert value["required_profile_residue"] == "A B"
    assert "loses G3211" in value["remove_flip_consequence"]


def test_direct_local_five_is_a_formal_mixed_diagnostic_and_is_fatal():
    value = report()["alternative_profile_and_matter_audit"]["direct_local_five"]
    assert value["U5tilde_center"].endswith("0 mod5")
    assert value["mixed_shift_SU5_X2"] == ["1/4", "10"]
    assert value["target_residual_SU5_X2"] == ["-1/4", "-10"]
    assert value["formal_one_Weyl_mixed_residual_cancelled"]
    assert not value["continuous_SU2R_multiplet_constructed"]
    assert not value["full_local_supersymmetric_lift_constructed"]
    assert any("colored triplet" in reason for reason in value["fatal_obstructions"])
    assert not value["accepted"]


def test_common_group_matter_is_only_an_interface_diagnostic():
    value = report()["alternative_profile_and_matter_audit"][
        "common_group_matter_diagnostic"
    ]
    assert value["mixed_bridge_component"] == "-nu A B"
    assert value["normal_Q1_Q3"] == [0, 0]
    assert not value["complete_U5_fixed_point_representations"]
    assert not value["full_K_center_and_Z4R_lift_checked"]
    assert not value["explicit_determinant_anomaly_ledger_complete"]
    assert not value["determinant_and_mixed_gauge_anomalies_cancelled"]
    assert not value["accepted"]


def test_bifundamental_diagnostic_derives_bridge_and_exposes_open_gauge_ledger():
    # ch2(E2 tensor E3) contains +A B, while replacing E3 by bar(E3)
    # changes that coefficient to -A B.  Multiplication by exp(q nu)
    # supplies q nu ch2, so q=(-1/2,+1/2) sums to -nu A B.
    normal_charges = (Fraction(-1, 2), Fraction(1, 2))
    ab_coefficients = (1, -1)
    bridge_coefficient = sum(
        q * coefficient for q, coefficient in zip(normal_charges, ab_coefficients)
    )
    normal_q1 = sum(6 * q for q in normal_charges)
    normal_q3 = sum(6 * q**3 for q in normal_charges)
    value = report()["alternative_profile_and_matter_audit"][
        "common_group_matter_diagnostic"
    ]
    assert bridge_coefficient == -1
    assert normal_q1 == normal_q3 == 0
    assert value["mixed_bridge_component"] == "-nu A B"
    assert not value["explicit_determinant_anomaly_ledger_complete"]


def test_only_vector_linear_refined_scaffold_is_selected_and_unaccepted():
    rows = report()["F74_candidate_matrix"]
    selected = [row for row in rows if row["selected"]]
    assert [row["id"] for row in selected] == ["F74_VECTOR_LINEAR_REFINED_BRIDGE"]
    assert not selected[0]["accepted"]
    assert not any(row["accepted"] for row in rows)


def test_terminal_decision_is_fail_closed():
    decision = report()["terminal_decision"]
    assert decision["common_K_bridge_exists"]
    assert not decision["bridge_is_existing_action_content"]
    assert decision["common_gluing_solved"]
    assert not decision["quarter_endpoint_spectator_solved"]
    assert not decision["supersymmetric_global_orbifold_action_constructed"]
    assert not decision["selected_candidate_accepted"]
    assert not decision["same_action_microscopic_completion_found"]
    assert decision["closed_gates"] == []
    assert not decision["theory_complete"]


def test_all_gates_remain_open():
    assert report()["gate_ledger"] == {f"G{i}": "OPEN" for i in range(1, 9)}


def test_core_hash_and_generated_artifacts_are_canonical():
    value = report()
    copy = dict(value)
    core = copy.pop("core_sha256")
    assert audit.canonical_sha(copy) == core
    if audit.OUT_JSON.is_file() and audit.OUT_MD.is_file():
        disk = json.loads(audit.OUT_JSON.read_text(encoding="utf-8"))
        assert disk["core_sha256"] == core
        assert audit.OUT_MD.read_text(encoding="utf-8") == audit.render_markdown(value)
