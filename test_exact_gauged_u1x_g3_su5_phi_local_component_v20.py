import exact_gauged_u1x_g3_su5_phi_local_component_v20 as local_component


def test_linearized_kernel_is_exactly_orbit_radial_and_complex_five():
    report = local_component.build_report()
    kernel = report["linearized_kernel"]
    assert kernel["exact_linearized_rank_over_Q_R"] == 179
    assert kernel["exact_linearized_nullity"] == 31
    assert kernel["SO10_orbit_tangent_rank"] == 20
    assert kernel["holomorphic_four_form_real_rank"] == 10
    assert kernel["combined_exhibited_kernel_rank"] == 31
    assert kernel["Gram_times_exhibited_kernel_max_abs"] == 0
    assert kernel["orbit_holomorphic_inner_product_max_abs"] == 0
    assert kernel["radial_holomorphic_inner_product_max_abs"] == 0
    assert kernel["radial_orbit_inner_product_max_abs"] == 0
    assert kernel["kernel_decomposition_exact"] is True


def test_unit_normal_slice_count_supports_implicit_function_step():
    kernel = local_component.build_report()["linearized_kernel"]
    assert kernel["unit_sphere_SO10_normal_slice_dimension"] == 189
    assert kernel["massive_slice_dimension"] == 179
    assert kernel["remaining_slice_kernel_dimension"] == 10


def test_complete_su4_fixed_space_and_obstruction_are_exact():
    fixed = local_component.build_report()["SU4_fixed_space"]
    assert fixed["integral_su4_generator_count"] == 15
    assert fixed["stacked_action_rank_mod_prime"] == 206
    assert fixed["exact_fixed_space_dimension"] == 4
    assert fixed["displayed_basis_rank"] == 4
    assert fixed["generator_times_displayed_basis_max_abs"] == 0
    assert fixed["displayed_basis_is_complete_fixed_space"] is True
    assert fixed["common_real_zero_locus"] == "c=0 and a^2=b^2"


def test_local_theorem_closes_only_local_components():
    report = local_component.build_report()
    assert report["n_failed"] == 0
    assert report["overall_state"] == "LOCAL_COMPONENT_THEOREM_CLOSED"
    assert report["scope"]["signed_orbit_locally_isolated"] is True
    assert report["scope"]["disconnected_distant_components_excluded"] is False
    assert report["scope"]["corrected_signed_global_orbit_theorem_proved"] is False
    assert report["scope"]["G3_closed"] is False
