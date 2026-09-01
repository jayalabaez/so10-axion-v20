import copy
import json
import unittest

import susy_v85_f4_weierstrass_c4f_isotropy_ahss_glue_audit as v85


class TestV85F4WeierstrassC4FIsotropyAHSSGlueAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = v85.build_report()

    def test_report_validates_and_is_canonical(self):
        v85.validate_report(self.report)
        self.assertEqual(v85.canonical_sha(self.report), self.report["core_sha256"])

    def test_lineage_is_hash_pinned(self):
        self.assertEqual(self.report["lineage"]["V70_route_core"], v85.EXPECTED_CORES["v70_route"])
        self.assertEqual(self.report["lineage"]["V84_route_core"], v85.EXPECTED_CORES["v84_route"])
        self.assertEqual(self.report["lineage"]["V84_master_core"], v85.EXPECTED_CORES["v84_master"])

    def test_legacy_spinor_higgs_rows_are_retracted_from_actual_action(self):
        correction = self.report["action_lineage_correction"]
        self.assertFalse(correction["actual_rank_branch"]["spinor_Higgs_C_plus_Cbar_present"])
        self.assertEqual(correction["actual_rank_branch"]["VEV"], "<B0>=v_B e11")
        self.assertEqual(correction["retracted_operator_names"], ["16 16 Cbar Cbar", "Cbar 45 C", "Cbar C"])
        self.assertFalse(correction["V84_fatal_Cbar45C_is_an_actual_V70_obligation"])
        self.assertTrue(correction["hybrid_reintroduction_boundary"]["would_define_new_action"])

    def test_f4_global_tate_classes_and_orders(self):
        geometry = self.report["compact_F4_non_split_I2star_audit"]
        self.assertEqual(geometry["base"]["S2"], -4)
        self.assertEqual(geometry["global_Tate_family"]["classes_aS_plus_bF"], {
            "A1": [1, 6], "A2": [3, 12], "A3": [3, 18], "A4": [5, 24], "A6": [7, 36]
        })
        self.assertEqual(geometry["global_Tate_family"]["restriction_degrees_on_S"], {
            "A1": 2, "A2": 0, "A3": 6, "A4": 4, "A6": 8
        })
        self.assertEqual(geometry["global_Tate_family"]["Tate_orders"], [1, 1, 3, 3, 5])
        self.assertEqual(geometry["global_Tate_family"]["Lie_algebra"], "B5=so(11)")

    def test_cox_witness_gives_squarefree_degree_eight_monodromy(self):
        witness = self.report["compact_F4_non_split_I2star_audit"]["Cox_witness"]
        self.assertEqual(witness["P_on_S_up_to_nonzero_t_power"], "u^8-v^8")
        self.assertEqual(witness["simple_branch_points"], 8)
        self.assertTrue(witness["P_squarefree"])
        self.assertFalse(witness["P_rational_square"])

    def test_nonlocal_matter_and_minimality_are_exact(self):
        matter = self.report["compact_F4_non_split_I2star_audit"]["discriminant_and_matter"]
        self.assertEqual(matter["residual_intersection_with_S"], 8)
        self.assertEqual(matter["monodromy_cover_genus"], 3)
        self.assertEqual(matter["vector_hypermultiplets"], 3)
        self.assertFalse(matter["branch_points_are_independent_local_hypers"])
        self.assertEqual(matter["branch_local_orders_f_g_Delta"], [2, 3, 9])
        self.assertEqual(matter["forced_4_6_points_on_S"], 0)

    def test_anomaly_and_deformation_counts_cross_check(self):
        geometry = self.report["compact_F4_non_split_I2star_audit"]
        anomaly = geometry["six_dimensional_anomaly_consistency_prediction"]
        self.assertEqual(anomaly["H_neutral_required_by_gravitational_anomaly"], 266)
        self.assertEqual(anomaly["H_neutral_predicted_by_h21_plus_universal_hyper"], 266)
        self.assertEqual(anomaly["conditional_H_minus_V_plus_29T"], 273)
        self.assertFalse(anomaly["independent_H_neutral_or_Hodge_certificate"])
        self.assertIn("PREDICTION", anomaly["classification"])
        deformation = geometry["deformation_count"]
        self.assertEqual((deformation["h0_minus_4K"], deformation["h0_minus_6K"]), (91, 190))
        self.assertEqual(deformation["I2star_constraints"]["total"], 6)
        self.assertEqual(deformation["equisingular_fibration_preserving_complex_structure_dimension"], 265)
        self.assertEqual(deformation["Tate_coordinate_cross_check"]["quotient_dimension"], 265)

    def test_very_general_global_form_but_hodge_is_prediction(self):
        geometry = self.report["compact_F4_non_split_I2star_audit"]
        mw = geometry["very_general_Mordell_Weil_and_global_form"]
        self.assertEqual((mw["Mordell_Weil_rank"], mw["Mordell_Weil_torsion"]), (0, "0 for the very-general ordinary Jacobian"))
        self.assertEqual(mw["ordinary_Jacobian_nonabelian_factor"], "Spin(11)")
        self.assertFalse(mw["vector_only_spectrum_distinguishes_Spin11_from_SO11"])
        boundary = geometry["resolution_boundary"]
        self.assertEqual((boundary["predicted_h11"], boundary["predicted_h21"]), (8, 265))
        self.assertFalse(boundary["projective_crepant_resolution_exhibited"])
        self.assertFalse(boundary["Hodge_numbers_certified"])

    def test_c4f_eight_rows_reduce_to_two_quotient_classes(self):
        lift = self.report["C4F_stratified_action_audit"]["lift_classification"]
        self.assertEqual(len(lift["rows"]), 16)
        self.assertEqual(lift["passing_rows"], 8)
        self.assertTrue(all(row["passes"] == (row["gauge_parity"] == row["flavor_parity"]) for row in lift["rows"]))
        self.assertEqual(lift["quotient_classes"], [0, 1])
        self.assertEqual(lift["representatives_u_v_r_s"], [[0, 0, 0, 0], [0, 0, 1, 1]])

    def test_all_four_strata_are_explicit_but_family_isotropy_open(self):
        audit = self.report["C4F_stratified_action_audit"]
        self.assertEqual([row["stabilizer"] for row in audit["fixed_strata"]], ["A", "U*A", "U*A^2", "V*A^2"])
        self.assertEqual(audit["descent_equations_mod2"], ["t+c+r+h3+h266=0", "c+qF=0"])
        self.assertTrue(audit["smooth_V70_physical_multiplets_descend"])
        self.assertTrue(audit["localized_family_boundary"]["central_character_completion_exists"])
        self.assertFalse(audit["localized_family_boundary"]["full_family_isotropy_constructed"])
        self.assertFalse(audit["rank_VEV_boundary"]["global_order_through_U5_quotient_proved"])

    def test_actual_operator_redesign_deletes_one_v70_driver_and_keeps_rank(self):
        operators = self.report["C4F_stratified_action_audit"]["actual_operator_redesign"]
        self.assertIn("B0 H_uB H_dC", operators["deleted_from_original_V70"])
        self.assertNotIn("X Xbar", operators["retained"])
        self.assertIn("S_X(X Xbar-v_X^2)", operators["retained"])
        self.assertEqual(operators["heavy_doublet_row"], ["sqrt(2)*g*v_B", "mu_B"])
        self.assertEqual(operators["heavy_doublet_rank"], 1)
        self.assertFalse(operators["all_order_operator_closure_proved"])

    def test_field_only_anomaly_shadow_has_exact_su2_residue(self):
        shadow = self.report["C4F_stratified_action_audit"]["field_only_anomaly_shadow"]
        self.assertEqual(len(shadow["field_ledger"]), 4)
        self.assertEqual((shadow["Delta_s1"], shadow["Delta_s3"]), (70, 136))
        self.assertTrue(shadow["pure_and_gravitational_conditions"]["passes"])
        self.assertEqual(shadow["mixed_instanton_coefficients_mod4"], {
            "SU3_squared_C4F": 0, "SU2_squared_C4F": 2, "6Y_squared_C4F": 0, "X_squared_C4F": 0,
        })
        self.assertEqual(shadow["mixed_instanton_coefficients_integer"], {
            "SU3_squared_C4F": 12, "SU2_squared_C4F": 18,
            "6Y_squared_C4F": 468, "X_squared_C4F": 688,
        })
        self.assertFalse(shadow["C4F_shifting_GS_axion_present"])
        self.assertFalse(shadow["quantum_parent_accepted"])

    def test_ahss_precursor_pages_now_survive(self):
        audit = self.report["delta_AHSS_precursor_audit"]
        self.assertEqual(audit["integral_homology_inputs"]["H9_BSpin11_Z"], "0")
        self.assertEqual(audit["integral_homology_inputs"]["H8_BSpin11_Z"], "Z^2")
        self.assertEqual([row["value"] for row in audit["precursor_maps"]], ["0_DOMAIN_ZERO", "0", "0_TARGET_ZERO"])
        self.assertIn("E3_(7,1)=H7(BSpin11;Z8)=Z2", audit["precursor_maps"][0]["consequence"])
        self.assertEqual(audit["precursor_maps"][2]["consequence"], "E4_(8,0)=Z^2")

    def test_d3_d4_q2_and_delta_remain_fail_closed(self):
        audit = self.report["delta_AHSS_precursor_audit"]
        remaining = audit["surviving_incoming_maps_to_E_(4,3)_Z2"]
        self.assertEqual(len(remaining["possible_d4_functionals"]), 4)
        self.assertFalse(remaining["spectrum_specific_Postnikov_operations_computed"])
        self.assertTrue(audit["q2_boundary"]["independent_w8_parity_direction"])
        self.assertFalse(audit["q2_boundary"]["q2_existence_determines_d4"])
        boundary = audit["chain_and_extension_boundary"]
        self.assertEqual(boundary["delta_exact_order"], "OPEN_ZERO_OR_ORDER2")
        self.assertFalse(boundary["Q4_graph_cycle_identified_with_associated_graded_survivor"])

    def test_same_action_glue_remains_absent(self):
        glue = self.report["same_action_glue_audit"]
        self.assertTrue(glue["ordinary_Jacobian"]["compact_singular_Weierstrass_model_exists"])
        self.assertFalse(glue["ordinary_Jacobian"]["independent_C4F_geometry_present"])
        self.assertFalse(glue["required_C4F_UV_object"]["object_constructed"])
        self.assertFalse(glue["resolution"]["projective_crepant_resolution_sequence"])
        self.assertFalse(glue["same_action_microscopic_completion"])
        self.assertFalse(glue["accepted_parent"])

    def test_acceptance_ledger_is_empty_and_all_gates_open(self):
        self.assertEqual(self.report["candidate_adjudication"]["accepted_ids"], [])
        self.assertEqual(len(self.report["candidate_adjudication"]["selected_ids"]), 3)
        self.assertTrue(all(value.startswith("OPEN") for value in self.report["gate_ledger"].values()))
        decision = self.report["terminal_decision"]
        self.assertEqual(decision["closed_gates"], [])
        self.assertFalse(decision["accepted_full_parent_action_exists"])
        self.assertFalse(decision["theory_complete"])

    def test_validator_rejects_promotions_and_retractions_of_exact_gains(self):
        mutations = [
            (lambda x: x["action_lineage_correction"]["actual_rank_branch"].__setitem__("spinor_Higgs_C_plus_Cbar_present", True), "reimported"),
            (lambda x: x["compact_F4_non_split_I2star_audit"]["resolution_boundary"].__setitem__("Hodge_numbers_certified", True), "promoted"),
            (lambda x: x["C4F_stratified_action_audit"]["field_only_anomaly_shadow"]["mixed_instanton_coefficients_mod4"].__setitem__("SU2_squared_C4F", 0), "field-derived"),
            (lambda x: x["C4F_stratified_action_audit"]["field_only_anomaly_shadow"]["field_ledger"][0].__setitem__("multiplicity", 999), "field-derived"),
            (lambda x: x["C4F_stratified_action_audit"]["field_only_anomaly_shadow"]["mixed_instanton_coefficients_mod4"].__setitem__("SU3_squared_C4F", 3), "field-derived"),
            (lambda x: x["delta_AHSS_precursor_audit"]["surviving_incoming_maps_to_E_(4,3)_Z2"].__setitem__("spectrum_specific_Postnikov_operations_computed", True), "promoted"),
            (lambda x: x["same_action_glue_audit"]["required_C4F_UV_object"].__setitem__("object_constructed", True), "promoted"),
            (lambda x: x["gate_ledger"].__setitem__("G5", "OPEN: reassigned meaning"), "gate identity"),
        ]
        for mutate, message in mutations:
            with self.subTest(message=message):
                value = copy.deepcopy(self.report)
                mutate(value)
                value["core_sha256"] = v85.canonical_sha(value)
                with self.assertRaisesRegex(RuntimeError, message):
                    v85.validate_report(value)

    def test_generated_artifacts_are_current(self):
        disk = json.loads(v85.OUT_JSON.read_text(encoding="utf-8"))
        self.assertEqual(disk, self.report)
        self.assertEqual(v85.OUT_MD.read_text(encoding="utf-8"), v85.render_markdown(self.report))


if __name__ == "__main__":
    unittest.main()
