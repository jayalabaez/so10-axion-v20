import copy
import json

import susy_v22r_g3_generic_vacuum_frontier as frontier


def test_v22r_g3_frontier_executes_without_failure():
    report = frontier.build_report()
    assert report["n_failed"] == 0
    assert report["status"] == (
        "V22R_108_SECTOR_GENERIC_SINGLET_F_FLAT_BRANCH_EXHIBITED__FULL_G3_OPEN"
    )


def test_exact_driver_sector_classification():
    report = frontier.build_report()
    classification = report["accepted_basis_classification"]
    assert classification["selected_sector_count"] == 108
    assert classification["driver_sector_count"] == 40
    assert classification["driver_sector_degree_counts"] == {"1": 5, "3": 25, "4": 10}
    assert len(classification["driver_product_grid"]) == 25
    assert all(row["selected"] for row in classification["driver_product_grid"])
    assert classification["quartic_driver_deformations"]["all_ten_and_only_ten_expected"]
    assert classification["declared_vs_forced_driver_sectors"] == {"declared": 12, "forced": 28}


def test_non_driver_terms_vanish_to_first_order_but_change_quadratic_blocks():
    classification = frontier.build_report()["accepted_basis_classification"]
    assert classification["non_driver_sector_count"] == 68
    assert classification["non_driver_declared_vs_forced"] == {"declared": 17, "forced": 51}
    assert classification["non_driver_zero_field_degree_histogram"] == {"2": 40, "3": 28}
    assert classification["non_driver_rows_with_fewer_than_two_zero_background_fields"] == []


def test_dense_exact_witness_and_regular_rank():
    witness = frontier.dense_witness()
    assert witness["linear_driver_vector_b"] == [-9, -11, -14, -17, -22]
    assert witness["F_driver_values"] == [0] * 5
    assert witness["F_driver_values_at_all_zero_chiral_fields"] == [-9, -11, -14, -17, -22]
    assert witness["cubic_driver_product_matrix_determinant"] == 6
    assert witness["Jacobian_rank"] == 5
    assert witness["regular_minor_determinant"] == -60
    assert witness["aggregate_D_values"] == {
        "SO10_C_pair_norm_difference": 0,
        "U1X": 0,
    }


def test_exact_elimination_certificate():
    elimination = frontier.dense_witness()["elimination"]
    assert elimination["effective_matrix_determinant_coefficients_ascending"] == [6, -19, 7]
    assert elimination["Phi210_branch_polynomial_coefficients_ascending"] == [
        -19, 13, -6, 19, -7,
    ]
    assert elimination["Phi210_branch_polynomial_degree"] == 4
    assert elimination["Phi210_branch_polynomial_discriminant"] == -693060300
    assert elimination["determinant_branch_resultant"] == -395136
    assert elimination["branch_product_numerator_resultants"] == [
        415872, -10512, 2525616, 17605872, -46932336,
    ]
    assert elimination["all_Cramer_products_at_phi_one"] == [1] * 5


def test_claim_boundary_keeps_full_g3_and_g4_open():
    boundary = frontier.build_report()["claim_boundary"]
    assert boundary["abstract_invariant_coordinate_F_flat_branch_exists"]
    assert boundary[
        "restricted_eight_coordinate_slice_has_one_formal_complex_modulus_after_two_direction_gauge_quotient"
    ]
    assert boundary["three_spectator_flat_directions_are_additional_to_the_restricted_slice"]
    assert boundary["full_declared_degree_four_EFT_quotient_dimension_is_at_least_four"]
    assert boundary["full_declared_degree_four_EFT_has_exactly_one_complex_modulus"] is False
    assert boundary["source_exact_SO10_component_embedding_closed"] is False
    assert boundary["global_F_D_branch_classification_closed"] is False
    assert boundary["all_order_holomorphic_vacuum_closed"] is False
    assert boundary["soft_vacuum_and_complete_Hessian_closed"] is False
    assert boundary["V22R_G3_closed"] is False
    assert boundary["V22R_G4_closed"] is False


def test_restricted_slice_dimension_count_keeps_three_spectator_flat_directions_separate():
    dimensions = frontier.build_report()["generic_branch_theorem"]["regular_local_dimensions"]
    assert dimensions["coordinate_scope"] == "restricted eight-coordinate VEV slice"
    assert dimensions["restricted_slice_complex_VEV_coordinates"] == 8
    assert dimensions["restricted_slice_complex_F_flat_tangent_before_gauge"] == 3
    assert dimensions["restricted_slice_formal_complex_quotient_moduli"] == 1
    assert dimensions["decoupled_gauge_singlet_spectator_flat_directions"] == 3
    assert dimensions["spectators"] == ["Z0", "Z1", "Z2"]
    assert dimensions["full_declared_degree_le_4_EFT_quotient_moduli_lower_bound"] == 4


def test_degree_five_spurion_layer_deforms_the_full_driver_grid():
    report = frontier.build_report()
    layer = report["broken_selector_spurion_boundary"]
    assert layer["degree_five_sector_count"] == 67
    assert layer["complete_degree_five_census"] is False
    assert layer["degree_five_component_count"] == 160
    assert layer["driver_deformation_sector_count"] == 25
    assert layer["driver_deformations_are_exactly_XMP_squared_times_the_full_grid"]
    assert layer["non_driver_sector_count"] == 42
    assert layer["non_driver_zero_field_degree_histogram"] == {"2": 26, "3": 16}


def test_every_z28r_element_has_explicit_gauge_compensation():
    stabilizer = frontier.gauge_compensated_z28r_stabilizer()
    assert stabilizer["all_28_Z28R_elements_compensated"]
    assert len(stabilizer["rows"]) == 28
    assert all(row["all_integer"] for row in stabilizer["rows"])
    k_one = stabilizer["rows"][1]
    assert k_one["U1X_t"] == "-5/7"
    assert k_one["SO10_chi"] == "1/35"
    assert k_one["compensated_integer_phases"] == {
        "Splus": -2,
        "Sminus": 3,
        "Phi17p": -12,
        "Phi17m": 13,
        "C16_chi_plus_five": 1,
        "C16bar_chi_minus_five": 0,
    }


def test_classifier_detects_a_missing_driver_grid_sector():
    basis = json.loads(frontier.ACCEPTED_BASIS.read_text(encoding="utf-8"))
    changed = copy.deepcopy(basis)
    changed["selected_sectors"] = [
        row for row in changed["selected_sectors"]
        if row["monomial"] != "Phi210^2 NX"
    ]
    classification = frontier.classify_basis(changed)
    assert classification["selected_sector_count"] == 107
    assert sum(row["selected"] for row in classification["driver_product_grid"]) == 24


def test_frozen_outputs_match_recomputation():
    report = frontier.build_report()
    assert json.loads(frontier.OUT_JSON.read_text(encoding="utf-8")) == report
    assert frontier.OUT_MD.read_text(encoding="utf-8") == frontier.markdown(report)
