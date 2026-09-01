import copy
import json
import unittest

import susy_v86_spin11_hodge_c4f_u1_parent_ahss_d3_audit as v86


class TestV86Spin11HodgeC4FParentAHSSAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = v86.build_report()

    def test_report_validates_and_is_canonical(self):
        v86.validate_report(self.report)
        self.assertEqual(v86.canonical_sha(self.report), self.report["core_sha256"])

    def test_lineage_binds_v82_and_v85(self):
        self.assertEqual(self.report["lineage"]["V82_route_core"], v86.EXPECTED_CORES["v82_route"])
        self.assertEqual(self.report["lineage"]["V85_route_core"], v86.EXPECTED_CORES["v85_route"])
        self.assertEqual(self.report["lineage"]["V85_master_core"], v86.EXPECTED_CORES["v85_master"])

    def test_v85_hodge_prediction_is_retracted_and_corrected(self):
        audit = self.report["V85_Hodge_retraction_and_Grassi_Morrison_correction"]
        self.assertEqual(audit["retracted_V85_prediction"], {"h11": 8, "h21": 265, "Euler": -514})
        self.assertEqual(audit["conditional_topological_invariants"], {"h11": 8, "h21": 268, "Euler": -520})
        self.assertEqual(audit["Spin11_non_split_I2star_data"]["R"], -20)
        self.assertEqual(audit["missing_nonpolynomial_or_zero_weight_modes"], 3)
        self.assertFalse(audit["conditionality"]["such_resolution_constructed_for_V85_model"])

    def test_both_six_dimensional_ledgers_equal_273(self):
        ledgers = self.report["V85_Hodge_retraction_and_Grassi_Morrison_correction"]["gravitational_cross_checks"]
        self.assertEqual(ledgers["Coulomb_charged_dimension_ledger"]["H_minus_V_plus_29T"], 273)
        self.assertEqual(ledgers["full_representation_ledger"]["H_minus_V_plus_29T"], 273)

    def test_published_resolution_template_is_crepant_but_not_promoted(self):
        resolution = self.report["resolution_and_multisection_frontier"]["published_non_split_I2star_resolution_template"]
        self.assertEqual(len(resolution["blowups"]), 5)
        self.assertEqual(resolution["discrepancies_c_minus_one_minus_m"], [0, 0, 0, 0, 0])
        self.assertFalse(resolution["global_Cox_chart_Jacobian_saturation_completed"])
        self.assertFalse(resolution["compact_resolution_certified"])

    def test_four_section_target_is_retracted_for_bisection(self):
        target = self.report["resolution_and_multisection_frontier"]["charge_lattice_target_correction"]
        self.assertEqual(target["desired_center_trivial_Q4_Higgs_has_geometric_q"], 2)
        self.assertEqual(target["desired_transition_geometry"], "BISECTION_ORDER2_WEIL_CHATELET_TORSOR")
        self.assertEqual(target["lifted_generator_relation"], "j has order four on the total quotient and j^2=z")
        self.assertFalse(target["V85_four_section_with_j_squared_z_obligation_well_specified"])
        self.assertIn("u^4=z", target["nef_5_1_generator_relation"])

    def test_biquadric_start_is_i0star_not_spin11(self):
        biquadric = self.report["resolution_and_multisection_frontier"]["biquadric_four_section_framework"]
        self.assertEqual(biquadric["symmetric_F4_choice"]["class_dot_S"], -1)
        self.assertEqual(biquadric["asymmetric_effective_start"]["generic_orders_I_J_Delta"], [2, 3, 6])
        self.assertEqual(biquadric["asymmetric_effective_start"]["extra_discriminant_cancellations_needed_for_I2star"], 2)
        self.assertFalse(biquadric["asymmetric_effective_start"]["Spin11_non_split_tuning_solved"])

    def test_continuous_group_quotient_and_boundary(self):
        parent = self.report["continuous_U1F_diagonal_parent_algebra"]
        self.assertEqual(parent["kernel_pairs_center_bit_quarter_turn"], [[0, 0], [1, 2]])
        self.assertEqual((parent["j_class"], parent["Spin_center_class"], parent["j_squared_class"]), (1, 2, 2))
        self.assertTrue(parent["j_squared_equals_Spin_center_in_abstract_quotient"])
        self.assertEqual(parent["Higgs_sector"]["component_group_after_quotient_by_connected_Spin11"], "Z2")
        self.assertFalse(parent["hard_boundaries"]["order_two_torsor_or_bisection_constructed"])

    def test_exact_positive_lift_anomaly_tensor(self):
        audit = self.report["C4F_anomaly_tensor_audit"]
        self.assertEqual(audit["integer_tensor"], {
            "A3": 12, "A2": 18, "FY6_squared": 468, "FX_squared": 688,
            "TrF": 70, "TrF_cubed": 136, "F_squared_Y6": 24,
            "F_squared_X": 16, "FY6X": 72,
        })
        self.assertEqual(audit["mod4_tensor"]["A2"], 2)
        self.assertEqual(audit["discrete_conditions"]["TrF_mod2_gravitational_condition"], 0)
        self.assertEqual(audit["unit_SU2_instanton"]["fermion_phase"], "exp(2*pi*i*18/4)=-1")
        self.assertTrue(all(value == 0 for value in audit["continuous_and_Witten_cross_checks"]["pure_abelian_trace_vector"].values()))
        self.assertEqual(audit["continuous_and_Witten_cross_checks"]["SU2_half_integer_doublet_count"], 16)

    def test_gapped_matter_no_go_enumeration(self):
        audit = self.report["C4_preserving_gapped_matter_no_go"]
        self.assertEqual(audit["Dirac_pairs_tested"], 64)
        self.assertTrue(all(row["A2_shift_mod4"] == 0 for row in audit["Dirac_pair_rows"]))
        self.assertTrue(all(row["q2_Majorana_shift_mod4"] == 0 for row in audit["real_SU2_Majorana_rows"]))

    def test_stueckelberg_no_go_and_inflow_mapping_torus(self):
        audit = self.report["Stueckelberg_and_topological_inflow_audit"]
        rows = audit["one_axion_Stueckelberg"]["integer_divisor_rows"]
        self.assertFalse(any(row["residual_order_gcd_4_K"] == 4 for row in rows))
        self.assertFalse(audit["one_axion_Stueckelberg"]["K4_attempt"]["integer_level"])
        inflow = audit["order_two_five_dimensional_inflow_target"]
        self.assertEqual(inflow["coefficient_k_in_Z4"], 2)
        self.assertTrue(all(row["product"] == 1 for row in inflow["phase_rows"]))
        self.assertEqual(sorted({row["instanton_number"] for row in inflow["phase_rows"]}), list(range(8)))
        self.assertTrue(all("instanton_number_mod4" not in row for row in inflow["phase_rows"]))
        self.assertFalse(inflow["same_action_trivialization_constructed"])

    def test_z2_endpoint_repairs_ledger_but_is_not_c4(self):
        endpoint = self.report["explicit_Z2_endpoint_repair"]
        self.assertEqual(endpoint["delta_tensor"]["A2"], 2)
        self.assertEqual(endpoint["total_tensor"], {
            "A3": 12, "A2": 20, "FY6_squared": 504, "FX_squared": 704,
            "TrF": 74, "TrF_cubed": 152, "F_squared_Y6": 0,
            "F_squared_X": 0, "FY6X": 96,
        })
        self.assertEqual(endpoint["bare_B0_qF2_VEV_endpoint"], "Z2")
        self.assertEqual(endpoint["charge_ledger"]["D_d"]["qR"], 2)
        self.assertEqual(endpoint["mass_operator_charges"], {"qF_mod4": 0, "qR_mod4": 2, "X": 0, "y6": 0})
        self.assertEqual(endpoint["direct_and_dangerous_operator_selectors"], {
            "direct_DuDd_qF_mod4": 2,
            "16_16_Dd_qF_mod4": 0,
            "16_16_Dd_qR_mod4": 0,
            "16_16_Du_qF_mod4": 2,
            "16_16_Du_qR_mod4": 2,
            "16_fourth_qR_mod4": 0,
        })
        self.assertTrue(endpoint["direct_DuDd_mass_forbidden_before_B0_VEV"])
        self.assertTrue(endpoint["16_16_Dd_forbidden_by_qR"])
        self.assertTrue(endpoint["16_16_Du_forbidden_by_qF"])
        self.assertTrue(endpoint["16_fourth_forbidden_by_qR"])
        self.assertFalse(endpoint["accepted_for_C4_theory"])

    def test_ahss_d3_is_zero_for_both_lifts(self):
        ahss = self.report["AHSS_d3_audit"]
        self.assertTrue(ahss["d3_value_computed"])
        self.assertEqual(ahss["d3_value"], "ZERO")
        self.assertEqual([row["source_generator_4g_image_in_Z8_plus_Z2"] for row in ahss["lift_rows"]], [[0, 0], [0, 0]])

    def test_scoped_d4_extension_and_delta_are_closed(self):
        ahss = self.report["AHSS_d3_audit"]
        self.assertEqual(ahss["lambda_seven_equivalence"]["total_group"], "Z4 direct_sum Z4")
        self.assertTrue(ahss["lambda_seven_equivalence"]["X_is_connective"])
        self.assertEqual((ahss["lambda_seven_equivalence"]["H2_BZ4_Z"], ahss["lambda_seven_equivalence"]["H3_BZ4_Z"]), ("0", "Z4"))
        self.assertEqual(ahss["hidden_extension_Smith_check"], [
            {"epsilon": 0, "Smith_cokernel_invariants": [2, 2]},
            {"epsilon": 1, "Smith_cokernel_invariants": [4]},
        ])
        self.assertEqual(ahss["actual_lift_epsilon"], 1)
        self.assertEqual(ahss["d4"]["value"], [0, 0])
        self.assertEqual(ahss["hidden_extension"], "NON_SPLIT_Z4_NOT_Z2_PLUS_Z2")
        self.assertEqual(ahss["qhat_delta"]["delta_value"], "ZERO")
        self.assertEqual(ahss["qhat_delta"]["alpha_times_r_character_order"], 4)
        self.assertFalse(ahss["scope_boundary"]["physical_total_anomaly_trivialization_follows"])
        candidate = next(row for row in self.report["candidate_matrix"] if row["id"] == "F86_AHSS_POSTNIKOV_ROUTE")
        self.assertIn("d3=d4=0", candidate["exact_gain"])
        self.assertIn("full-HGamma", candidate["blocker"])

    def test_no_candidate_or_gate_is_closed(self):
        self.assertFalse(any(row["accepted"] for row in self.report["candidate_matrix"]))
        self.assertEqual(self.report["candidate_adjudication"]["accepted_ids"], [])
        self.assertTrue(all(value.startswith("OPEN:") for value in self.report["gate_ledger"].values()))
        self.assertEqual(self.report["terminal_decision"]["closed_gates"], [])
        self.assertFalse(self.report["terminal_decision"]["theory_complete"])

    def test_validator_rejects_overclaims_and_corruptions(self):
        mutations = [
            lambda x: x["V85_Hodge_retraction_and_Grassi_Morrison_correction"]["conditionality"].__setitem__("such_resolution_constructed_for_V85_model", True),
            lambda x: x["resolution_and_multisection_frontier"]["published_non_split_I2star_resolution_template"].__setitem__("compact_resolution_certified", True),
            lambda x: x["resolution_and_multisection_frontier"]["charge_lattice_target_correction"].__setitem__("V85_four_section_with_j_squared_z_obligation_well_specified", True),
            lambda x: x["C4F_anomaly_tensor_audit"]["mod4_tensor"].__setitem__("A2", 0),
            lambda x: x["Stueckelberg_and_topological_inflow_audit"]["order_two_five_dimensional_inflow_target"].__setitem__("same_action_trivialization_constructed", True),
            lambda x: x["explicit_Z2_endpoint_repair"]["mass_operator_charges"].__setitem__("qR_mod4", 0),
            lambda x: x["AHSS_d3_audit"].__setitem__("d3_value", "ISOMORPHISM"),
            lambda x: x["AHSS_d3_audit"]["d4"].__setitem__("value", [1, 0]),
            lambda x: x["AHSS_d3_audit"]["scope_boundary"].__setitem__("BC4F_or_full_HGamma_or_fixed_strata_included", True),
            lambda x: x["candidate_matrix"][0].__setitem__("accepted", True),
            lambda x: x["terminal_decision"].__setitem__("theory_complete", True),
        ]
        for mutate in mutations:
            value = copy.deepcopy(self.report)
            mutate(value)
            value["core_sha256"] = v86.canonical_sha(value)
            with self.assertRaises(RuntimeError):
                v86.validate_report(value)

    def test_generated_artifacts_are_current(self):
        disk = json.loads(v86.OUT_JSON.read_text(encoding="utf-8"))
        self.assertEqual(disk, self.report)
        self.assertEqual(v86.OUT_MD.read_text(encoding="utf-8"), v86.render_markdown(self.report))


if __name__ == "__main__":
    unittest.main()
