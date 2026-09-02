import copy
import json
import unittest

import susy_v87_b_neutral_bisection_diagonal_inflow_resolution_audit as audit


class TestV87BNeutralBisectionDiagonalInflowResolutionAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_report()

    def test_report_validates_and_is_canonical(self):
        audit.validate_report(self.report)
        self.assertEqual(audit.canonical_sha(self.report), self.report["core_sha256"])

    def test_all_parent_cores_are_hash_pinned(self):
        self.assertEqual(self.report["input_core_hashes"], {
            "V70_route": audit.EXPECTED_CORES["v70"],
            "V83_route": audit.EXPECTED_CORES["v83"],
            "V85_route": audit.EXPECTED_CORES["v85"],
            "V86_route": audit.EXPECTED_CORES["v86"],
            "V86_master": audit.EXPECTED_CORES["v86_master"],
        })

    def test_global_ambient_blowups_are_projective_and_crepant(self):
        compact = self.report["compact_resolution_globalization"]["canonical_compact_completion"]
        self.assertTrue(compact["ambient_blowup_sequence_globally_constructed"])
        self.assertTrue(compact["all_ambient_centers_smooth"])
        self.assertTrue(compact["all_ambient_blowups_projective"])
        self.assertEqual(compact["discrepancies"], [0, 0, 0, 0, 0])

    def test_compact_flatness_is_exact(self):
        flat = self.report["compact_resolution_globalization"]["flatness"]
        self.assertTrue(flat["no_ambient_surface_component_contained_in_hypersurface"])
        self.assertTrue(flat["pure_one_dimensional_fibers"])
        self.assertTrue(flat["miracle_flatness_applies"])
        self.assertTrue(flat["compact_family_flat"])

    def test_embedded_geometry_certificate_is_executable_and_canonical(self):
        certificate = self.report["compact_resolution_globalization"]["executable_geometry_certificate"]
        audit.compact_certificate.validate_report(certificate)
        self.assertEqual(certificate["chart_jacobian_certificate"]["n_unit_ideals"], 25)
        self.assertEqual(certificate["flatness_certificate"]["n_nonzero_component_restrictions"], 6)
        self.assertEqual(certificate["chern_pushforward_certificate"]["formal_Euler"], -520)

    def test_branch_transversality_is_one_quarter(self):
        branch = self.report["compact_resolution_globalization"]["simple_branch_transversality"]
        self.assertEqual(branch["F_q_at_critical_point"], "1/4")
        self.assertTrue(branch["generic_simple_branch_total_space_smooth"])

    def test_independent_formal_euler_is_minus_520(self):
        chern = self.report["compact_resolution_globalization"]["formal_Chern_pushforward"]
        self.assertEqual(chern["base_class"], "-60*L^2+84*L*S-32*S^2")
        self.assertEqual(chern["formal_Euler"], -520)
        self.assertEqual(chern["conditional_Hodge"], [8, 268])
        self.assertFalse(chern["Shioda_Tate_Wazir_h11_8_proved_for_a_frozen_member"])
        self.assertIn("Mordell-Weil rank zero", chern["conditional_Hodge_additional_assumptions"])

    def test_compact_smoothness_is_not_promoted(self):
        boundary = self.report["compact_resolution_globalization"]["remaining_compact_certificate"]
        self.assertFalse(boundary["explicit_homogeneous_A1_A3_beta2_beta4_beta6_frozen"])
        self.assertFalse(boundary["full_Cox_Jacobian_saturation_run"])
        self.assertFalse(boundary["strict_transform_smooth_certified"])
        self.assertFalse(boundary["Hodge_numbers_unconditional"])

    def test_bisection_binary_quartic_orders_are_exact(self):
        invariants = self.report["period_two_bisection_candidate"]["binary_quartic_invariants"]
        self.assertEqual(invariants["orders_I_J_Delta"], [2, 3, 8])
        self.assertEqual(invariants["I_z2"], "16*L^2")
        self.assertEqual(invariants["J_z3"], "-128*L^3")
        self.assertEqual(invariants["Delta_z8"], "6912*L^4*P_plus*P_minus")

    def test_bisection_jacobian_is_non_split_I2star(self):
        jac = self.report["period_two_bisection_candidate"]["Jacobian_Tate_reconstruction"]
        self.assertEqual(jac["Tate_orders"], ["infinity", 1, "infinity", 3, 5])
        self.assertTrue(jac["non_split_I2star_B5_for_generic_witness"])
        self.assertEqual(jac["monodromy_cover_branch_count"], 8)
        self.assertEqual(jac["monodromy_cover_genus"], 3)

    def test_explicit_cox_witness_has_eight_simple_branches(self):
        witness = self.report["period_two_bisection_candidate"]["explicit_Cox_witness"]
        self.assertTrue(witness["P_plus_and_P_minus_each_nonsquare"])
        self.assertTrue(witness["no_common_root"])
        self.assertTrue(witness["product_has_eight_simple_roots"])

    def test_bisection_has_period_and_index_two(self):
        proof = self.report["period_two_bisection_candidate"]["period_index_proof"]
        self.assertEqual(proof["tested_local_field"], "completion of K(F4) at the divisor S, with residue field K(S)")
        self.assertFalse(proof["point_over_completed_local_field_exists"])
        self.assertFalse(proof["K_F4_rational_point_exists"])
        self.assertFalse(proof["global_rational_section_exists"])
        self.assertEqual((proof["period"], proof["index"]), (2, 2))

    def test_resolved_bisection_relation_is_not_promoted(self):
        boundary = self.report["period_two_bisection_candidate"]["geometric_boundaries"]
        self.assertFalse(boundary["global_crepant_resolution_of_bisection_constructed"])
        self.assertFalse(boundary["resolved_bisection_component_intersections_computed"])
        self.assertFalse(boundary["resolved_geometric_proof_j_squared_equals_Spin_center"])

    def test_B_neutral_charge_pattern_and_phase_candidate_not_full_projectors(self):
        redesign = self.report["B_neutral_orbifold_redesign"]
        charges = redesign["charge_redesign"]
        self.assertEqual([charges["A_hyper_qF"], charges["B_hyper_qF"], charges["C_hyper_qF"]], [2, 0, 2])
        lift = redesign["Sp3_diagonal_Wilson_lift"]
        self.assertEqual(lift["H_AC"], "diag(-1,+1,-1,-1,+1,-1)")
        self.assertTrue(lift["commutes_with_A3"])
        self.assertTrue(lift["candidate_fixed_stratum_phase_rows_match_V70"])
        self.assertFalse(lift["full_Gammahat_lift_cocycle_and_kernel_recomputed"])
        self.assertFalse(lift["all_V70_A_B_C_projectors_restored"])
        self.assertFalse(lift["pure_Spin11_center_added_to_kernel"])

    def test_rank_one_mass_and_light_pair(self):
        mass = self.report["B_neutral_orbifold_redesign"]["operator_and_doublet_mass_audit"]
        self.assertEqual(mass["matrix_rows_HuA_HuB_cols_HdSigma_HdC"], [["0", "0"], ["sqrt(2)*g*v_B", "0"]])
        self.assertEqual(mass["rank_for_g_vB_nonzero"], 1)
        self.assertEqual(mass["light_pair"], ["H_uA", "H_dC"])
        self.assertFalse(mass["even_B0_potential_symmetry_enforced"])

    def test_B_neutral_anomaly_tensor_and_residues(self):
        anomaly = self.report["B_neutral_orbifold_redesign"]["ordinary_zero_mode_anomaly"]
        self.assertEqual(anomaly["integer_tensor"], {
            "A3": 12, "A2": 16, "FY6_squared": 432, "FX_squared": 672,
            "TrF": 64, "TrF_cubed": 112, "F_squared_Y6": 0,
            "F_squared_X": 0, "FY6X": 48,
        })
        self.assertFalse(any(anomaly["mod4_tensor"].values()))
        self.assertEqual(anomaly["unit_SU2_instanton_phase"], "+1")

    def test_charge_four_GS_factorization_screen(self):
        gs = self.report["B_neutral_orbifold_redesign"]["charge4_GS_Stueckelberg_screen"]
        self.assertEqual(gs["K"], 4)
        self.assertTrue(gs["all_levels_integer"])
        self.assertTrue(gs["F_squared_Y6_and_X_obstructions_zero"])
        self.assertFalse(gs["supersymmetric_differential_cocycle_and_common_regulator_constructed"])

    def test_vacuum_stabilizer_is_only_C2_and_not_faithful_on_light_sector(self):
        vacuum = self.report["vacuum_stabilizer_audit"]["B_neutral_vacuum"]
        self.assertTrue(vacuum["h_fixes_B0_X_Xbar"])
        self.assertEqual(vacuum["h_squared"], "z*J^2=z*z=1")
        self.assertEqual(vacuum["surviving_nongauge_component"], "C2")
        self.assertFalse(vacuum["faithful_C4_low_energy_selector_survives"])
        self.assertEqual(vacuum["h_action_on_families_and_light_HuA_HdC"], "trivial")

    def test_GF_bundle_constraint_and_spin_c_class(self):
        inflow = self.report["diagonal_quotient_bundle_and_inflow"]
        self.assertEqual(inflow["central_extension"]["extension_class"], "w2(V)+a^2")
        self.assertEqual(inflow["central_extension"]["component_group"], "C2")
        self.assertFalse(inflow["central_extension"]["universal_C4_valued_H1_class_exists"])
        self.assertEqual(inflow["Spin_c_characteristic_class"]["rho2_q1"], "w4(V)")

    def test_smooth_aw4_character_is_nonzero_but_uv_coefficient_is_open(self):
        inflow = self.report["diagonal_quotient_bundle_and_inflow"]
        smooth = inflow["ordinary_smooth_inflow_character"]
        self.assertEqual(smooth["class"], "omega5=a*w4(V)=a*rho2(q1(V,a))")
        self.assertEqual(smooth["witness_phase"], -1)
        relation = inflow["B_neutral_branch_relation"]
        self.assertEqual(relation["omega5_coefficient_required_by_displayed_zero_mode_shadow"], 0)
        self.assertFalse(relation["zero_mode_shadow_requires_V86_k2"])
        self.assertFalse(relation["UV_k2_counterterm_coefficient_determined"])

    def test_full_HGamma_target_remains_ambiguous(self):
        target = self.report["full_HGamma_target_audit"]
        shared = target["ordinary_smooth_target_alternatives"]["shared_physical_SO11_bundle"]
        self.assertEqual(shared["forced_relation"], "y+b+a^2=0")
        self.assertFalse(target["ordinary_smooth_target_alternatives"]["unique_smooth_degree7_target_selected"])
        self.assertFalse(target["full_stratified_HGamma_bordism_target_defined"])
        self.assertFalse(target["full_fixed_wall_Dai_Freed_character_computed"])

    def test_terminal_decision_is_fail_closed(self):
        decision = self.report["terminal_decision"]
        self.assertTrue(decision["B_neutral_fixed_stratum_phase_candidate_passes"])
        self.assertFalse(decision["B_neutral_full_space_group_projectors_restored"])
        self.assertTrue(decision["B_neutral_rank1_action_exact"])
        self.assertTrue(decision["B_neutral_ordinary_C4_anomaly_residues_zero"])
        self.assertFalse(decision["compact_strict_transform_smooth_certified"])
        self.assertFalse(decision["full_fixed_wall_Dai_Freed_trivialization_constructed"])
        self.assertFalse(decision["accepted_full_parent_action_exists"])
        self.assertEqual(decision["closed_gates"], [])
        self.assertFalse(decision["theory_complete"])
        self.assertTrue(all(value.startswith("OPEN:") for value in self.report["gate_ledger"].values()))

    def test_validator_rejects_false_promotions_and_mutations(self):
        mutations = [
            lambda x: x["compact_resolution_globalization"]["remaining_compact_certificate"].__setitem__("strict_transform_smooth_certified", True),
            lambda x: x["period_two_bisection_candidate"]["period_index_proof"].__setitem__("period", 1),
            lambda x: x["period_two_bisection_candidate"]["geometric_boundaries"].__setitem__("resolved_geometric_proof_j_squared_equals_Spin_center", True),
            lambda x: x["B_neutral_orbifold_redesign"]["charge_redesign"].__setitem__("B_hyper_qF", 2),
            lambda x: x["B_neutral_orbifold_redesign"]["Sp3_diagonal_Wilson_lift"].__setitem__("all_V70_A_B_C_projectors_restored", True),
            lambda x: x["B_neutral_orbifold_redesign"]["ordinary_zero_mode_anomaly"]["mod4_tensor"].__setitem__("A2", 2),
            lambda x: x["vacuum_stabilizer_audit"]["B_neutral_vacuum"].__setitem__("h_squared", "z"),
            lambda x: x["diagonal_quotient_bundle_and_inflow"]["central_extension"].__setitem__("extension_class", "w2(V)"),
            lambda x: x["diagonal_quotient_bundle_and_inflow"]["B_neutral_branch_relation"].__setitem__("UV_k2_counterterm_coefficient_determined", True),
            lambda x: x["full_HGamma_target_audit"].__setitem__("full_stratified_HGamma_bordism_target_defined", True),
            lambda x: x["terminal_decision"].__setitem__("accepted_full_parent_action_exists", True),
            lambda x: x["terminal_decision"].__setitem__("theory_complete", True),
            lambda x: x["gate_ledger"].__setitem__("G1", "CLOSED"),
        ]
        for mutate in mutations:
            value = copy.deepcopy(self.report)
            mutate(value)
            value["core_sha256"] = audit.canonical_sha(value)
            with self.assertRaises(RuntimeError):
                audit.validate_report(value)

    def test_generated_artifacts_are_current(self):
        self.assertEqual(json.loads(audit.OUT_JSON.read_text(encoding="utf-8")), self.report)
        self.assertEqual(audit.OUT_MD.read_text(encoding="utf-8"), audit.render_markdown(self.report))


if __name__ == "__main__":
    unittest.main()
