import copy
import json
import unittest

import susy_v84_gammahat_bare_phase_f4_heterotic_string_audit as v84


class TestV84GammahatBarePhaseF4HeteroticStringAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = v84.build_report()

    def test_report_validates_and_is_canonical(self):
        v84.validate_report(self.report)
        self.assertEqual(v84.canonical_sha(self.report), self.report["core_sha256"])

    def test_lineage_is_hash_pinned(self):
        mapping = {
            "v65_route": "V65_route_core",
            "v70_route": "V70_route_core", "v71_route": "V71_route_core", "v78_route": "V78_route_core",
            "v81_route": "V81_route_core", "v82_route": "V82_route_core", "v83_route": "V83_route_core",
            "v83_master": "V83_master_core",
        }
        for key, report_key in mapping.items():
            self.assertEqual(self.report["lineage"][report_key], v84.EXPECTED_CORES[key])

    def test_full_gammahat_no_go_is_universal_in_scoped_scan(self):
        audit = self.report["unchanged_five_factor_Gammahat_no_go"]
        theorem = audit["universal_relation_theorem"]
        self.assertEqual(theorem["D1"], "x+y")
        self.assertEqual(theorem["D2"], "x+y+e11")
        self.assertEqual(theorem["D1_plus_D2"], "e11")
        self.assertTrue(theorem["pure_Spin11_center_forced_for_every_assignment"])
        self.assertFalse(theorem["gerbe_2group_or_added_spin_charge_factor_excluded"])
        self.assertEqual(audit["finite_enumeration"]["raw"], 1024)
        self.assertEqual(audit["finite_enumeration"]["contains_e11"], 1024)
        self.assertEqual(audit["finite_enumeration"]["kernel_dimension_2"], 128)
        self.assertEqual(audit["finite_enumeration"]["kernel_dimension_3"], 896)
        self.assertEqual(audit["finite_enumeration"]["Kmin_solutions"], 0)

    def test_unchanged_parent_fails_spinor_descent_and_quantization(self):
        fatal = self.report["unchanged_five_factor_Gammahat_no_go"]["fatal_consequences"]
        self.assertFalse(fatal["localized_16_descends_through_Kmax"])
        self.assertFalse(fatal["multiplicity_repairs_center_character"])
        self.assertEqual(fatal["Kmax_global_gauge_form"], "SO(11)")
        self.assertEqual(fatal["b"], [2, -1])
        self.assertFalse(fatal["b_in_2U"])

    def test_c4f_kernel_repairs_pure_center_without_killing_spin11(self):
        audit = self.report["C4F_spinor_grading_repair_scout"]
        kernel = audit["extended_kernel"]
        self.assertEqual(len(kernel["elements"]), 4)
        self.assertFalse(kernel["contains_pure_Spin11_center"])
        self.assertTrue(kernel["Spin11_remains_faithful"])
        self.assertEqual(len(audit["lift_choice"]["direct_bit_matched_representative_rows"]), 4)
        self.assertTrue(all(row["relations_exact_mod_KF"] for row in audit["lift_choice"]["direct_bit_matched_representative_rows"]))
        self.assertEqual(audit["lift_choice"]["independent_rows_total"], 16)
        self.assertEqual(audit["lift_choice"]["independent_rows_passing"], 8)
        self.assertTrue(all(row["passes"] == (row["gauge_parity"] == row["flavor_parity"]) for row in audit["lift_choice"]["all_independent_gauge_flavor_sign_rows"]))
        self.assertTrue(audit["representation_descent"]["localized_16_pure_center_repaired"])
        self.assertFalse(audit["representation_descent"]["full_localized_krot_and_isotropy_descent"])

    def test_c4f_operator_and_stabilizer_scaffold(self):
        audit = self.report["C4F_spinor_grading_repair_scout"]
        rows = {row["operator"]: row for row in audit["operator_audit"]["rows"]}
        self.assertTrue(rows["16 16 H_u"]["C4F_invariant"])
        self.assertTrue(rows["N N X"]["C4F_invariant"])
        self.assertTrue(rows["16 16 Cbar Cbar"]["C4F_invariant"])
        self.assertFalse(rows["old B0 H_uB H_dC"]["C4F_invariant"])
        self.assertFalse(rows["old A0 H_uA H_dC"]["C4F_invariant"])
        self.assertTrue(rows["Cbar 45 C"]["C4F_invariant"])
        self.assertFalse(rows["Cbar 45 C"]["target_vacuum_admissible"])
        self.assertIn("forces v=0", rows["Cbar 45 C"]["dynamical_note"])
        self.assertTrue(audit["operator_audit"]["spinor_Higgs_vacuum_selector_still_required"])
        self.assertTrue(audit["stabilizer_redesign"]["local_Hessian_blocks_nondegenerate_after_gauge_null"])
        self.assertFalse(audit["stabilizer_redesign"]["global_supersymmetric_profile_constructed"])

    def test_eta_tables_and_rarita_virtual_class_are_exact(self):
        audit = self.report["regulated_Q4_bare_and_WCS_audit"]
        self.assertEqual(audit["eta_tables_numerator_over_16"]["0"], [-2, 2, 2, -2])
        self.assertEqual(audit["eta_tables_numerator_over_16"]["2"], [-7, -1, 5, 3])
        self.assertEqual(audit["eta_tables_numerator_over_16"]["-2"], [3, 5, -1, -7])
        self.assertEqual(audit["Rarita_Vec_minus_one"]["numerator_over_16"], 8)
        self.assertEqual(audit["Rarita_Vec_minus_one"]["value_mod1"], "1/2")
        self.assertIn("(1/2) xi_Rprime", audit["Rarita_Vec_minus_one"]["quantity_in_anomaly_ledger"])
        self.assertEqual(audit["spin_half_ledger"]["eta_R_minus_eta_Ad"], "-3/4")
        self.assertFalse(audit["spin_half_ledger"]["halving_V81_again_allowed"])
        proof = audit["SMW_pair_normalization_proof"]
        self.assertEqual((proof["hyper_one_root_dimension"], proof["hyper_full_complex_pair_dimension"]), (299, 598))
        self.assertEqual((proof["adjoint_one_R_root_dimension"], proof["adjoint_full_R_pair_dimension"]), (55, 110))
        self.assertTrue(proof["outer_half_already_consumed_by_pair_doubling"])
        self.assertFalse(proof["common_BV_Pfaffian_orientation_constructed"])

    def test_bare_phase_is_primitive_fourth_root_but_orientation_pair(self):
        bare = self.report["regulated_Q4_bare_and_WCS_audit"]["bare_character"]
        self.assertEqual(bare["possible_exponents_mod4"], [1, 3])
        self.assertEqual(bare["possible_phases"], ["i", "-i"])
        self.assertTrue(bare["primitive_fourth_root_proved"])
        self.assertEqual(bare["preferred_primary_calibrated_phase"], "-i")
        self.assertFalse(bare["fully_BV_orientation_pinned"])
        self.assertFalse(bare["full_HGamma_physical_bare_character_constructed"])

    def test_all_sixteen_algebraic_r2_screen_rows_fail_without_physical_promotion(self):
        audit = self.report["regulated_Q4_bare_and_WCS_audit"]
        shift = audit["algebraic_r2_coefficient_shift_screen"]
        self.assertEqual(len(shift["rows"]), 16)
        self.assertEqual(shift["WCS_exponent_counts"], {"0": 4, "2": 12})
        self.assertTrue(shift["all_sixteen_fail_cancellation"])
        self.assertTrue(all(row["WCS_exponent_mod4"] in (0, 2) for row in shift["rows"]))
        self.assertTrue(all(not row["cancels_for_any_allowed_bare_convention"] for row in shift["rows"]))
        self.assertIn("not V78's 16 local corrections", shift["classification_boundary"])
        self.assertFalse(shift["V78_half_choice_from_delta_2Y_to_delta_Y_constructed"])
        self.assertFalse(audit["scope"]["all_physical_full_HGamma_refinements_rejected"])
        self.assertFalse(audit["counterterm_boundary"]["extension_to_full_Omega7_HGamma_proved"])

    def test_f4_geometry_exactly_is_u_lattice(self):
        geometry = self.report["F4_SO11_heterotic_string_scaffold"]["geometry"]
        self.assertEqual(geometry["section_S"], [2, -1])
        self.assertEqual(geometry["fiber_F"], [-1, 0])
        self.assertEqual(geometry["canonical_K"], [2, 2])
        self.assertEqual(geometry["intersections"], {"S2": -4, "F2": 0, "S_dot_F": 1, "K2": 8, "K_dot_S": 2, "K_dot_F": -2})
        self.assertEqual(geometry["adjunction_genera"], {"S": 0, "F": 0})
        self.assertEqual(geometry["geometric_Kahler_witness"]["j_dot_S"], "3/2")
        self.assertEqual(geometry["geometric_Kahler_witness"]["j_dot_F"], "1/4")
        self.assertTrue(geometry["chamber_redesign_required"])

    def test_f4_so11_spectrum_and_critical_heterotic_string(self):
        audit = self.report["F4_SO11_heterotic_string_scaffold"]
        spectrum = audit["so11_Lie_algebra_divisor_spectrum"]
        self.assertEqual((spectrum["vector_hypers"], spectrum["spinor_hypers"]), (3, 0))
        self.assertEqual((spectrum["H_charged"], spectrum["H_neutral"]), (33, 266))
        self.assertTrue(spectrum["matches_frozen_Lie_algebra_and_multiplicity_scaffold"])
        self.assertFalse(spectrum["global_gauge_group_or_line_operator_match"])
        string = audit["critical_heterotic_fiber_string"]
        self.assertEqual((string["Q2"], string["Q_dot_K"], string["Q_dot_b"]), (0, -2, 1))
        self.assertEqual(string["interacting_cL_cR"], [20, 6])
        self.assertEqual(string["full_cL_cR"], [24, 12])
        self.assertEqual(string["Spin11_Sugawara_c"], "11/2")
        self.assertTrue(string["matches_published_critical_heterotic_fiber_sector"])
        self.assertTrue(string["conditional_on_explicit_F4_Ftheory_realization"])
        self.assertFalse(string["D3_worldsheet_in_this_model_constructed"])

    def test_f4_effective_residue_lifts_are_minimal_but_reducible(self):
        audit = self.report["F4_SO11_heterotic_string_scaffold"]["effective_Q4_residue_lifts"]
        rows = audit["rows"]
        self.assertEqual([(row["Q"], row["target_residue_mod4"]) for row in rows], [([1, -1], [1, 3]), ([5, -3], [1, 1])])
        self.assertEqual([row["tension"] for row in rows], ["7/4", "19/4"])
        self.assertEqual([row["congruence_solutions_a_c_mod4"] for row in rows], [[[1, 1]], [[3, 1]]])
        self.assertTrue(all(row["S_is_forced_component"] for row in rows))
        self.assertTrue(all(not row["irreducible_curve"] for row in rows))
        self.assertTrue(audit["coefficient_minimal_lifts_unique"])
        self.assertTrue(audit["coefficient_minimal_representative_selected_in_F4_effective_cone"])
        self.assertTrue(audit["infinitely_many_nonminimal_effective_lifts_remain"])
        self.assertFalse(audit["elementary_new_string_constructed"])

    def test_uv_scaffold_is_not_explicit_weierstrass_model(self):
        boundary = self.report["F4_SO11_heterotic_string_scaffold"]["UV_acceptance_boundary"]
        self.assertTrue(boundary["anomaly_divisor_heterotic_dual_scaffold"])
        self.assertFalse(boundary["explicit_compact_non_split_I2star_Weierstrass"])
        self.assertFalse(boundary["Mordell_Weil_and_global_Spin11_form"])
        self.assertFalse(boundary["full_HGamma_lift"])

    def test_restricted_product_is_non_bps_but_ordinary_cap_exists(self):
        audit = self.report["relative_cap_BPS_and_delta_audit"]
        bps = audit["restricted_T2xS4_BPS_audit"]
        self.assertFalse(bps["round_S4_has_parallel_spinor"])
        self.assertFalse(bps["half_BPS_solution_in_restricted_ansatz"])
        self.assertFalse(bps["warped_fluxed_singular_or_R_twisted_generalization_excluded"])
        cap = audit["ordinary_relative_cap"]
        self.assertEqual((cap["H2_RmodZ"], cap["H3_RmodZ"]), (0, 0))
        self.assertEqual(cap["residual"], [0, 0])
        self.assertTrue(cap["ordinary_differential_trivialization_exists"])
        self.assertFalse(cap["WCS_Wu_quadratic_trivialization_constructed"])

    def test_product_double_cannot_be_q4_and_delta_candidate_retains_d3_d4_and_extension(self):
        audit = self.report["relative_cap_BPS_and_delta_audit"]
        double = audit["product_double_no_go"]
        self.assertEqual(double["forgetful_product_class_in_Omega7SpinZ8"], 0)
        self.assertEqual(double["Q4_forgetful_order"], 4)
        self.assertFalse(double["product_double_equals_Q4"])
        delta = audit["delta_AHSS_d3_d4_candidate_audit"]
        maps = delta["potential_incoming_AHSS_differentials_on_associated_graded_candidate"]
        self.assertEqual(len(maps), 2)
        self.assertIn("potential incoming d3:", maps[0])
        self.assertIn("potential incoming d4:", maps[1])
        self.assertEqual(len(delta["differential_elimination"]), 5)
        self.assertEqual(delta["coefficient_and_homology_input_data"]["H7_BSpin11_Z8_by_UCT"], "Z2 from Tor(H6,Z8)")
        self.assertFalse(delta["source_page_precursor_audit"]["d3_source_E3_survival_computed"])
        self.assertFalse(delta["source_page_precursor_audit"]["d4_source_E4_survival_computed"])
        self.assertEqual(delta["degree8_d4_controller"], "q2=(p2-lambda^2)/2 reducing to w8")
        self.assertFalse(delta["half_vector_eta_is_bordism_character"])
        self.assertFalse(delta["d3_value_computed"])
        self.assertFalse(delta["candidate_d4_value_computed"])
        self.assertFalse(delta["chain_level_identification_of_delta_with_candidate_proved"])
        self.assertFalse(delta["post_Einfinity_hidden_extension_resolved"])
        self.assertEqual(delta["delta_exact_order"], "OPEN_ZERO_OR_ORDER2")

    def test_terminal_decision_is_fail_closed(self):
        decision = self.report["terminal_decision"]
        self.assertTrue(decision["unchanged_five_factor_parent_rejected_exactly"])
        self.assertTrue(decision["C4F_extended_central_algebra_constructed"])
        self.assertTrue(decision["F4_charge_lattice_and_so11_Lie_algebra_spectrum_match"])
        self.assertFalse(decision["explicit_compact_F4_Weierstrass_parent_constructed"])
        self.assertFalse(decision["accepted_full_parent_action_exists"])
        self.assertEqual(decision["current_action_status"], "REJECTED")
        self.assertEqual(decision["closed_gates"], [])
        self.assertFalse(decision["theory_complete"])

    def test_acceptance_ledger_is_empty(self):
        accepted = [row["id"] for row in self.report["candidate_matrix"] if row["accepted"]]
        self.assertEqual(accepted, [])
        self.assertEqual(self.report["candidate_adjudication"]["accepted_ids"], [])
        self.assertEqual(len(self.report["candidate_adjudication"]["selected_ids"]), 2)

    def test_validator_rejects_promotions(self):
        mutations = [
            (lambda x: x["unchanged_five_factor_Gammahat_no_go"]["fatal_consequences"].__setitem__("b_in_2U", True), "fatal"),
            (lambda x: x["C4F_spinor_grading_repair_scout"]["representation_descent"].__setitem__("full_localized_krot_and_isotropy_descent", True), "promoted"),
            (lambda x: x["regulated_Q4_bare_and_WCS_audit"]["scope"].__setitem__("all_physical_full_HGamma_refinements_rejected", True), "overpromoted"),
            (lambda x: x["F4_SO11_heterotic_string_scaffold"]["UV_acceptance_boundary"].__setitem__("explicit_compact_non_split_I2star_Weierstrass", True), "promoted"),
            (lambda x: x["relative_cap_BPS_and_delta_audit"]["delta_AHSS_d3_d4_candidate_audit"].__setitem__("half_vector_eta_is_bordism_character", True), "falsely"),
        ]
        for mutate, message in mutations:
            with self.subTest(message=message):
                value = copy.deepcopy(self.report)
                mutate(value)
                value["core_sha256"] = v84.canonical_sha(value)
                with self.assertRaisesRegex(RuntimeError, message):
                    v84.validate_report(value)

    def test_generated_artifacts_are_current(self):
        disk = json.loads(v84.OUT_JSON.read_text(encoding="utf-8"))
        self.assertEqual(disk, self.report)
        self.assertEqual(v84.OUT_MD.read_text(encoding="utf-8"), v84.render_markdown(self.report))


if __name__ == "__main__":
    unittest.main()
