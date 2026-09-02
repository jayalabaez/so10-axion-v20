import copy
import json
import unittest

import susy_v96_multipath_g1_frontier_master_audit as audit


class TestV96Master(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_report()
        cls.previous = audit.load_bound(audit.V95_PATH, audit.EXPECTED_CORES["v95_master"])
        cls.route = audit.load_bound(audit.V96_PATH, audit.EXPECTED_CORES["v96_route"])

    def test_lineage_and_canonical_core(self):
        self.assertEqual(self.report["input_core_hashes"], audit.EXPECTED_CORES)
        self.assertEqual(self.report["core_sha256"], audit.canonical_sha(self.report))
        audit.validate_report(self.report)

    def test_all_twenty_three_old_routes_unchanged(self):
        self.assertEqual(self.report["route_matrix"][:-1], self.previous["route_matrix"])
        self.assertEqual(json.dumps(self.report["route_matrix"][:-1], sort_keys=True, separators=(",", ":")),
                         json.dumps(self.previous["route_matrix"], sort_keys=True, separators=(",", ":")))
        self.assertEqual(self.report["lineage"]["parent_route_matrix_sha256"], audit.canonical_sha(self.previous["route_matrix"]))
        self.assertEqual(self.report["lineage"]["parent_route_count"], 23)

    def test_B96_appended_unaccepted_ordinal24(self):
        rows = self.report["route_matrix"]
        self.assertEqual(len(rows), 24)
        self.assertEqual([r["ordinal"] for r in rows], list(range(1, 25)))
        self.assertEqual(rows[-1]["route_id"], "B96")
        self.assertFalse(rows[-1]["accepted"])
        self.assertFalse(rows[-1]["same_action_microscopic_completion"])

    def test_normal_two_field_candidate_and_quantized_product_CS(self):
        card = self.report["consolidated_theory_card"]
        self.assertTrue(card["normal_product_CS_quantized"])
        self.assertFalse(card["normal_product_CS_requires_a_nonzero_root_section"])
        self.assertEqual(card["selected_normal_Weyl_components_per_C4"], 2)
        self.assertEqual(card["selected_normal_root_charges"], [-3, -3])
        self.assertEqual(card["selected_normal_CS_cubic_integer_level"], 10)
        self.assertEqual(card["selected_normal_CS_mixed_u_c2_integer_level"], -1)
        self.assertEqual(card["selected_normal_slice_residual"], "0")

    def test_normal_candidate_does_not_cancel_R_or_construct_Gammahat(self):
        card = self.report["consolidated_theory_card"]
        self.assertNotEqual(card["selected_normal_full_R_residual"], "0")
        self.assertFalse(card["selected_normal_witness_added_to_old_28_component_module"])
        self.assertFalse(card["selected_normal_witness_constructs_full_Gammahat_representations"])
        self.assertFalse(card["normal_CS_descends_to_full_Gammahat"])

    def test_natural_Spin_c_half_period_is_not_product_category_failure(self):
        card = self.report["consolidated_theory_card"]
        self.assertEqual(card["natural_Spin_c_unchanged_target_CP2_times_CP1_period"], "3/2")
        self.assertFalse(card["natural_Spin_c_unchanged_target_absolute_descent"])
        self.assertTrue(card["normal_product_CS_quantized"])

    def test_ordinary_integer_eta_CS_exists_but_fractional_independent_edges_fail(self):
        card = self.report["consolidated_theory_card"]
        self.assertTrue(card["ordinary_integer_eta_CS_refinement_exists"])
        self.assertFalse(card["fractional_free_edge_transport_is_quantized_standalone_ordinary_CS"])
        self.assertFalse(card["equivariant_quantized_transport_action_constructed"])

    def test_smooth_mass_is_nonholomorphic_and_has_uncomputed_defect_modes(self):
        card = self.report["consolidated_theory_card"]
        self.assertTrue(card["mass_intertwiner_smooth_on_cover"])
        self.assertFalse(card["mass_intertwiner_holomorphic_superpotential_profile"])
        self.assertFalse(card["mass_intertwiner_nowhere_nonzero"])
        self.assertEqual(card["mass_cover_zero_windings"], {"z00": 1, "z11": 1, "z10": -1, "z01": -1})
        self.assertFalse(card["mass_defect_zero_modes_computed"])
        self.assertFalse(card["virtual_opposite_chirality_pair_is_accepted_6D_N1_sector"])

    def test_virtual_pure_U1_cancellation_retains_nonzero_normal_residual(self):
        card = self.report["consolidated_theory_card"]
        self.assertTrue(card["virtual_character_pure_U1_transport_matches"])
        self.assertEqual(card["virtual_character_integrated_pure_U1_residual"], "0")
        self.assertEqual(card["virtual_character_integrated_normal_residual"], "-f*x**2/2")
        self.assertFalse(card["virtual_character_new_normal_anomaly_canceled"])

    def test_restricted_bordism_and_all_class_inverse_cancellation(self):
        card = self.report["consolidated_theory_card"]
        self.assertEqual(card["restricted_defect_bordism_groups"], {"C4": "Z8 x Z2", "C8": "Z16 x Z2"})
        self.assertEqual(card["restricted_defect_bordism_orders"], {"C4": 16, "C8": 32})
        self.assertEqual(card["restricted_defect_bare_characters"], {"C4": [1, 1], "C8": [4, 1]})
        self.assertEqual(card["restricted_defect_inverse_characters"], {"C4": [7, 1], "C8": [12, 1]})
        self.assertEqual(card["restricted_defect_all_reduced_characters_cancel"], {"C4": True, "C8": True})

    def test_mixed_gauge_quotient_witness_survives_the_restricted_repairs(self):
        card = self.report["consolidated_theory_card"]
        self.assertEqual(card["mixed_gauge_quotient_CP3_physical_local_periods"], ["61/4", "61/4", "-1/2"])
        self.assertEqual(card["mixed_gauge_quotient_CP3_pure_J2_period"], "0")
        self.assertEqual(card["mixed_gauge_quotient_CP3_normal_repair_period"], "0")
        self.assertFalse(card["mixed_gauge_fractional_periods_removed_by_pure_J2_transport"])
        self.assertFalse(card["mixed_gauge_fractional_periods_removed_by_ordinary_local_Weyls_alone"])
        self.assertFalse(card["separate_five_and_three_dimensional_responses_glued"])

    def test_inverse_is_quantized_background_CS_ABK_not_dynamical_CS(self):
        card = self.report["consolidated_theory_card"]
        self.assertEqual(card["restricted_defect_inverse_CS_level_for_D"], 3)
        self.assertEqual(card["restricted_defect_inverse_ABK_level_mod8"], 3)
        self.assertTrue(card["restricted_defect_inverse_quantized"])
        self.assertFalse(card["restricted_defect_response_gauge_field_is_integrated_over"])

    def test_defect_gravity_and_same_action_completion_remain_open(self):
        card = self.report["consolidated_theory_card"]
        self.assertEqual(card["restricted_defect_gravitational_central_charge_remaining"], "9/2")
        self.assertFalse(card["restricted_defect_physical_gravitational_anomaly_cancelled"])
        self.assertFalse(card["restricted_defect_same_action_bulk_inflow_constructed"])

    def test_actual_moduli_variation_strengthens_original_bound_to_eleven(self):
        card = self.report["consolidated_theory_card"]
        self.assertEqual(card["actual_Jacobian_torsion_order"], 1)
        self.assertIsNone(card["actual_Jacobian_free_MW_rank"])
        self.assertEqual(card["actual_Jacobian_free_MW_rank_lower_bound"], 0)
        self.assertEqual(card["actual_Jacobian_free_MW_rank_upper_bound"], 11)
        self.assertEqual(card["actual_geometric_generic_K3_Picard_rank_upper_bound"], 19)
        self.assertEqual(card["actual_K3_moduli_image_dimension"], 1)
        self.assertFalse(card["rank_bound_assumes_fixed_specialization_injectivity"])

    def test_polynomial_ansatz_exclusions_are_not_general_rank_zero(self):
        card = self.report["consolidated_theory_card"]
        for key in ("polynomial_x_degree_at_most_two_section_exists", "original_field_leading_twelve_cubic_section_exists",
                    "remaining_cubic_original_field_system_solved", "all_original_rational_sections_excluded",
                    "actual_original_nonzero_section_constructed"):
            self.assertFalse(card[key])

    def test_inherited_height_and_charge_normalization_not_promoted_to_section(self):
        card = self.report["consolidated_theory_card"]
        self.assertEqual(card["conditional_unit_charge_section_height_S_F"], [148, 768])
        self.assertEqual(card["conditional_doubled_charge_section_height_S_F"], [37, 192])
        self.assertIn("k^2", card["height_charge_scaling"])
        self.assertFalse(card["actual_charge_unit_or_target_section_proved"])

    def test_route_crosscheck_decisions_and_sources_copied_exactly(self):
        for master_key, route_key in (("formal_combination_and_quotient_periods", "formal_combination_and_quotient_periods"),
                                      ("strict_master_decision", "terminal_decision"),
                                      ("supersession_ledger", "supersession_boundary"),
                                      ("gate_ledger", "gate_ledger"),
                                      ("next_required_action", "next_required_action"),
                                      ("primary_sources", "primary_sources")):
            self.assertEqual(self.report[master_key], self.route[route_key])

    def test_all_eight_gates_remain_open_and_F97(self):
        card = self.report["consolidated_theory_card"]
        self.assertEqual(card["accepted_extension_count"], 0)
        self.assertEqual(set(self.report["gate_ledger"]), {"G"+str(i) for i in range(1, 9)})
        self.assertTrue(all(v.startswith("OPEN:") for v in self.report["gate_ledger"].values()))
        self.assertEqual(self.report["strict_master_decision"]["closed_gates"], [])
        self.assertEqual(self.report["next_required_action"]["id"], audit.NEXT_ID)
        self.assertTrue(self.report["lineage"]["canonical_V21_gate_scope_unchanged"])
        for key in ("full_quantum_anomaly_cancelled", "same_action_spectrum_and_geometry_realized", "soft_spectrum_unification_cosmology_complete"):
            self.assertFalse(card[key])

    def assert_rehashed_mutation_rejected(self, key, value):
        changed = copy.deepcopy(self.report)
        changed["consolidated_theory_card"][key] = value
        changed["core_sha256"] = audit.canonical_sha(changed)
        with self.assertRaises(RuntimeError):
            audit.validate_report(changed)

    def test_rehashed_history_change_rejected(self):
        changed = copy.deepcopy(self.report)
        changed["route_matrix"][0]["name"] = "forged"
        changed["core_sha256"] = audit.canonical_sha(changed)
        with self.assertRaises(RuntimeError):
            audit.validate_report(changed)

    def test_rehashed_gate_promotion_rejected(self):
        changed = copy.deepcopy(self.report)
        changed["strict_master_decision"]["theory_complete"] = True
        changed["core_sha256"] = audit.canonical_sha(changed)
        with self.assertRaises(RuntimeError):
            audit.validate_report(changed)

    def test_rehashed_full_Gammahat_normal_claim_rejected(self):
        self.assert_rehashed_mutation_rejected("normal_CS_descends_to_full_Gammahat", True)

    def test_rehashed_nonzero_normal_residual_erasure_rejected(self):
        self.assert_rehashed_mutation_rejected("virtual_character_integrated_normal_residual", "0")

    def test_rehashed_mixed_gauge_fraction_erasure_rejected(self):
        self.assert_rehashed_mutation_rejected("mixed_gauge_quotient_CP3_physical_local_periods", ["0", "0", "0"])

    def test_rehashed_holomorphic_mass_claim_rejected(self):
        self.assert_rehashed_mutation_rejected("mass_intertwiner_holomorphic_superpotential_profile", True)

    def test_rehashed_same_action_finite_inflow_claim_rejected(self):
        self.assert_rehashed_mutation_rejected("restricted_defect_same_action_bulk_inflow_constructed", True)

    def test_rehashed_exact_rank_claim_rejected(self):
        self.assert_rehashed_mutation_rejected("actual_Jacobian_free_MW_rank", 11)

    def test_rehashed_cubic_system_solution_claim_rejected(self):
        self.assert_rehashed_mutation_rejected("remaining_cubic_original_field_system_solved", True)

    def test_readable_report_retains_mixed_residual_and_scope_boundaries(self):
        markdown = audit.render_markdown(self.report)
        self.assertNotIn("|---", markdown)
        for phrase in ("All eight SUSY/C8 gates remain OPEN", "nonholomorphic", "-f*x^2/2",
                       "61/4", "-1/2", "gravitationally subtracted", "No complete theory",
                       "between 0 and 11", "saved but unsolved", "q_Sh=q_displayed/2"):
            self.assertIn(phrase, markdown)
        self.assertIn("cancels the isolated defect's reduced anomaly on every bordism class", markdown)
        self.assertNotIn("cancels every reduced character", markdown)

    def test_generated_artifacts_current(self):
        self.assertEqual(json.loads(audit.OUT_JSON.read_text(encoding="utf-8")), self.report)
        self.assertEqual(audit.OUT_MD.read_text(encoding="utf-8"), audit.render_markdown(self.report))


if __name__ == "__main__":
    unittest.main()
