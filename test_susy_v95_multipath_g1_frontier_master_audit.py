import copy
import json
import unittest

import susy_v95_multipath_g1_frontier_master_audit as audit


class TestV95Master(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_report()
        cls.previous = audit.load_bound(audit.V94_PATH, audit.EXPECTED_CORES["v94_master"])
        cls.route = audit.load_bound(audit.V95_PATH, audit.EXPECTED_CORES["v95_route"])

    def test_lineage_and_core(self):
        self.assertEqual(self.report["input_core_hashes"], audit.EXPECTED_CORES)
        self.assertEqual(self.report["core_sha256"], audit.canonical_sha(self.report))
        audit.validate_report(self.report)

    def test_all_twenty_two_old_routes_unchanged(self):
        self.assertEqual(self.report["route_matrix"][:-1], self.previous["route_matrix"])
        self.assertEqual(json.dumps(self.report["route_matrix"][:-1], sort_keys=True, separators=(",", ":")),
                         json.dumps(self.previous["route_matrix"], sort_keys=True, separators=(",", ":")))
        self.assertEqual(self.report["lineage"]["parent_route_matrix_sha256"], audit.canonical_sha(self.previous["route_matrix"]))
        self.assertEqual(self.report["lineage"]["parent_route_count"], 22)

    def test_B95_appended_unaccepted_ordinal23(self):
        rows = self.report["route_matrix"]
        self.assertEqual(len(rows), 23)
        self.assertEqual([r["ordinal"] for r in rows], list(range(1, 24)))
        self.assertEqual(rows[-1]["route_id"], "B95")
        self.assertFalse(rows[-1]["accepted"])
        self.assertFalse(rows[-1]["same_action_microscopic_completion"])

    def test_wall_obstruction_is_eight_of_twenty_eight(self):
        card = self.report["consolidated_theory_card"]
        self.assertEqual(card["conditional_wall_Weyl_components_per_C4"], 28)
        self.assertEqual(card["wall_components_failing_geometric_kernel_per_module"], 8)
        self.assertFalse(card["independent_internal_centers_rescue_unchanged_wall"])
        self.assertTrue(card["new_internal_anomaly_curvatures_retained"])

    def test_local_CP3_periods_and_physical_C2_normalization(self):
        self.assertEqual(self.report["consolidated_theory_card"]["physical_U1_slice_CP3_index_periods"],
                         {"z00": "487/4", "z11": "487/4", "physical_C2_orbit": "-21/2"})

    def test_formal_transfer_is_not_an_inflow_action(self):
        card = self.report["consolidated_theory_card"]
        self.assertEqual(card["formal_charge2_index_transfer_coefficients"], ["1/4", "1/4", "-1/2"])
        self.assertEqual(card["formal_transfer_global_sum"], "0")
        self.assertFalse(card["formal_transfer_constructs_quantized_action"])

    def test_finite_defect_lens_and_torus_signs_not_polynomial_periods(self):
        card = self.report["consolidated_theory_card"]
        self.assertEqual(card["unit_defect_primitive_lens_bare_phase_chosen_convention"], "+i")
        self.assertEqual(card["unit_defect_primitive_lens_required_inverse_chosen_convention"], "-i")
        self.assertEqual(card["unit_defect_primitive_torus_bare_phase"], "-1")
        self.assertEqual(card["unit_defect_primitive_torus_required_inverse"], "-1")
        self.assertTrue(card["CP3_polynomial_periods_are_not_defect_lens_eta_phases"])
        self.assertFalse(card["lens_sign_convention_glued_to_full_relative_action"])
        self.assertFalse(card["bare_defect_anomaly_rejects_total_theory"])

    def test_original_torsion_rank_bound_and_generic_field_scope(self):
        card = self.report["consolidated_theory_card"]
        self.assertEqual(card["actual_Jacobian_torsion_order"], 1)
        self.assertIsNone(card["actual_Jacobian_free_MW_rank"])
        self.assertEqual(card["actual_Jacobian_free_MW_rank_lower_bound"], 0)
        self.assertEqual(card["actual_Jacobian_free_MW_rank_upper_bound"], 12)
        self.assertFalse(card["rank_bound_uses_fixed_numerical_specialization"])
        self.assertFalse(card["actual_original_nonzero_section_constructed"])

    def test_height_branches_and_squared_charge_scale(self):
        card = self.report["consolidated_theory_card"]
        branches = card["conditional_section_height_branches"]
        self.assertEqual([r["q_displayed_over_q_Sh"] for r in branches], [1, 2])
        self.assertEqual([r["q_Sh_over_q_displayed"] for r in branches], ["1", "1/2"])
        self.assertEqual([r["displayed_height_over_section_height"] for r in branches], [1, 4])
        self.assertEqual([r["required_section_height_class_S_F"] for r in branches], [["148", "768"], ["37", "192"]])
        self.assertEqual([r["surviving_component_nodes"] for r in branches], [[0], [1]])
        self.assertTrue(all(r["necessary_conditions_only"] for r in branches))
        self.assertTrue(all(r["actual_section_exists"] is None for r in branches))
        self.assertTrue(card["global_height_formula_is_conditional"])
        self.assertFalse(card["primitive_global_U1_generator_proved"])

    def test_route_decisions_gates_and_next_copied_exactly(self):
        for master_key, route_key in (("strict_master_decision", "terminal_decision"),
                                      ("supersession_ledger", "supersession_boundary"),
                                      ("gate_ledger", "gate_ledger"),
                                      ("next_required_action", "next_required_action"),
                                      ("primary_sources", "primary_sources")):
            self.assertEqual(self.report[master_key], self.route[route_key])

    def test_all_eight_gates_remain_open_and_F96(self):
        card = self.report["consolidated_theory_card"]
        self.assertEqual(card["accepted_extension_count"], 0)
        self.assertEqual(set(self.report["gate_ledger"]), {"G"+str(i) for i in range(1, 9)})
        self.assertTrue(all(v.startswith("OPEN:") for v in self.report["gate_ledger"].values()))
        self.assertEqual(self.report["strict_master_decision"]["closed_gates"], [])
        self.assertEqual(self.report["next_required_action"]["id"], audit.NEXT_ID)
        self.assertTrue(self.report["lineage"]["canonical_V21_gate_scope_unchanged"])
        for key in ("full_quantum_anomaly_cancelled", "same_action_spectrum_and_geometry_realized", "soft_spectrum_unification_cosmology_complete"):
            self.assertFalse(card[key])

    def test_rehashed_promotion_rejected(self):
        changed = copy.deepcopy(self.report)
        changed["strict_master_decision"]["theory_complete"] = True
        changed["core_sha256"] = audit.canonical_sha(changed)
        with self.assertRaises(RuntimeError):
            audit.validate_report(changed)

    def test_rehashed_history_change_rejected(self):
        changed = copy.deepcopy(self.report)
        changed["route_matrix"][0]["name"] = "forged"
        changed["core_sha256"] = audit.canonical_sha(changed)
        with self.assertRaises(RuntimeError):
            audit.validate_report(changed)

    def test_rehashed_exact_rank_claim_rejected(self):
        changed = copy.deepcopy(self.report)
        changed["consolidated_theory_card"]["actual_Jacobian_free_MW_rank"] = 12
        changed["core_sha256"] = audit.canonical_sha(changed)
        with self.assertRaises(RuntimeError):
            audit.validate_report(changed)

    def test_rehashed_quantized_inflow_claim_rejected(self):
        changed = copy.deepcopy(self.report)
        changed["consolidated_theory_card"]["formal_transfer_constructs_quantized_action"] = True
        changed["core_sha256"] = audit.canonical_sha(changed)
        with self.assertRaises(RuntimeError):
            audit.validate_report(changed)

    def test_readable_report_retains_boundaries(self):
        markdown = audit.render_markdown(self.report)
        self.assertNotIn("|---", markdown)
        for phrase in ("All eight SUSY/C8 gates remain OPEN", "not a quantized inflow action", "chosen", "necessary", "No complete theory"):
            if phrase == "chosen":
                self.assertIn("stated convention", markdown)
            else:
                self.assertIn(phrase, markdown)
        self.assertIn("q_Sh=q_displayed/2", markdown)

    def test_generated_artifacts_current(self):
        self.assertEqual(json.loads(audit.OUT_JSON.read_text(encoding="utf-8")), self.report)
        self.assertEqual(audit.OUT_MD.read_text(encoding="utf-8"), audit.render_markdown(self.report))


if __name__ == "__main__":
    unittest.main()
