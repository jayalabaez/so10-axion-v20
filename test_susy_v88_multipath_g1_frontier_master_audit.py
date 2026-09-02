import copy
import json
import unittest

import susy_v88_multipath_g1_frontier_master_audit as master


class TestV88MultipathG1FrontierMasterAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = master.build_report()

    def test_report_validates_and_core_is_canonical(self):
        master.validate_report(self.report)
        self.assertEqual(self.report["core_sha256"], master.canonical_sha(self.report))

    def test_parent_cores_are_exactly_pinned(self):
        self.assertEqual(self.report["input_core_hashes"], {
            "V87_master": master.EXPECTED_CORES["v87_master"],
            "V88_route": master.EXPECTED_CORES["v88_route"],
        })

    def test_v87_route_matrix_is_inherited_and_b88_appended(self):
        v87 = master.load_bound(master.V87_MASTER_PATH, master.EXPECTED_CORES["v87_master"])
        self.assertEqual(self.report["route_matrix"][:-1], v87["route_matrix"])
        row = self.report["route_matrix"][-1]
        self.assertEqual(row["route_id"], "B88")
        self.assertFalse(row["same_action_microscopic_completion"])
        self.assertFalse(row["accepted"])

    def test_route_ordinals_are_contiguous(self):
        rows = self.report["route_matrix"]
        self.assertEqual([row["ordinal"] for row in rows], list(range(1, len(rows) + 1)))

    def test_acceptance_ledger_records_exact_gains_and_open_boundaries(self):
        rows = {row["id"]: row["status"] for row in self.report["acceptance_criteria"]}
        self.assertEqual(rows["A4"], "PASS_EXACT")
        self.assertEqual(rows["A6"], "PASS_EXACT_RESTORED")
        self.assertEqual(rows["A8"], "PASS_EXACT")
        self.assertEqual(rows["A13"], "RETRACTED_NOT_ESTABLISHED")
        self.assertEqual(rows["A18"], "OPEN_FOUR_CANDIDATE_LABELS")
        self.assertEqual(rows["A22"], "OPEN_UNCONSTRUCTED")
        self.assertEqual(rows["A26"], "REJECTED_NOT_FOUND")

    def test_smooth_bulk_gammahat_restores_projectors_but_not_localized_bundle(self):
        row = self.report["strict_master_decision"]
        self.assertTrue(row["selected_smooth_bulk_Gammahat_cocycle_constructed"])
        self.assertTrue(row["all_V70_A_B_C_projectors_restored"])
        self.assertFalse(row["pure_Spin11_center_in_kernel"])
        self.assertFalse(row["full_localized_isotropy_and_regulator"])

    def test_relative_bisection_resolution_and_center_class_are_exact(self):
        row = self.report["strict_master_decision"]
        self.assertTrue(row["relative_projective_crepant_resolution_over_S"])
        self.assertTrue(row["bisection_center_coset_realizes_j_squared_equals_z"])
        self.assertFalse(row["compact_resolved_bisection_complete"])
        self.assertFalse(row["inherited_compact_strict_transform_smooth_certified"])

    def test_v87_continuous_gs_promotion_is_retracted(self):
        row = self.report["strict_master_decision"]
        self.assertTrue(row["V87_discrete_zero_mode_residue_screen_retained"])
        self.assertFalse(row["V87_tensor_over_four_is_continuous_6D_GS_factorization"])

    def test_one_minimal_integer_lift_is_exact_but_not_canonical(self):
        row = self.report["strict_master_decision"]
        self.assertEqual(row["one_minimal_integer_lift_tensor"], {
            "A3": 12, "A2": 16, "FY6_squared": 432, "FX_squared": 672,
            "TrF": 60, "TrF_cubed": 96, "F_squared_Y6": 0,
            "F_squared_X": 0, "FY6X": 48,
        })
        self.assertFalse(row["one_minimal_integer_lift_is_canonical_continuous_U1_tensor"])

    def test_aw4_witness_and_t2_candidate_labels_remain_scoped(self):
        row = self.report["strict_master_decision"]
        self.assertTrue(row["ordinary_aw4_displayed_witness_requires_no_term"])
        self.assertEqual(row["t2_component_candidate_lattice_labels"], 4)
        self.assertFalse(row["WCS_admissibility_conditions_checked"])
        self.assertFalse(row["complete_signed_6D_anomaly_polynomial"])
        self.assertFalse(row["full_fixed_wall_Dai_Freed_trivialization"])

    def test_cbar45c_is_not_a_selected_action_obligation(self):
        self.assertFalse(self.report["strict_master_decision"]["Cbar45C_is_current_selected_action_obligation"])
        ledger = self.report["supersession_ledger"]
        self.assertFalse(ledger["V84_Cbar45C_blocker_applies_to_selected_V70_action"])
        self.assertTrue(ledger["V85_mixed_action_retraction_retained"])

    def test_c8_parity_screen_is_scoped_to_neutral_coefficients(self):
        row = self.report["strict_master_decision"]
        self.assertTrue(row["C8_neutral_coefficient_B0_parity_screen_passes"])
        self.assertFalse(row["C8_unconditional_all_order_selector_after_charged_spurions"])

    def test_c8_compensated_displayed_tensor_is_zero_mod_eight(self):
        row = self.report["strict_master_decision"]
        self.assertTrue(row["C8_compensated_displayed_mod8_screen_zero"])
        tensor = row["C8_compensated_tensor"]
        self.assertEqual(tensor, {
            "A3": 64, "A2": 80, "FY6_squared": 2208, "FX_squared": 2208,
            "TrF": 312, "TrF_cubed": 7824, "F_squared_Y6": 96,
            "F_squared_X": 544, "FY6X": 192,
        })
        self.assertFalse(any(value % 8 for value in tensor.values()))

    def test_c8_parent_mass_and_phenomenology_are_not_promoted(self):
        row = self.report["strict_master_decision"]
        self.assertFalse(row["C8_full_order8_Gammahat_lift_constructed"])
        self.assertFalse(row["GM_spurion_sector_constructed"])
        self.assertFalse(row["localized_compensator_mass_coupling_constructed"])
        self.assertFalse(row["compensator_decay_Higgs_identity_and_proton_safety_proved"])

    def test_no_route_or_gate_is_accepted(self):
        decision = self.report["strict_master_decision"]
        self.assertEqual(decision["accepted_extension_count"], 0)
        self.assertFalse(decision["same_action_microscopic_completion_found"])
        self.assertFalse(decision["accepted_full_parent_action_exists"])
        self.assertEqual(decision["closed_gates"], [])
        self.assertFalse(decision["theory_complete"])

    def test_all_eight_gates_remain_open(self):
        self.assertEqual(set(self.report["gate_ledger"]), {f"G{i}" for i in range(1, 9)})
        self.assertTrue(all(value.startswith("OPEN:") for value in self.report["gate_ledger"].values()))

    def test_fail_closed_logic_is_explicit(self):
        row = self.report["fail_closed_logic"]
        self.assertTrue(row["smooth_bulk_projectors_are_not_localized_orbibundle"])
        self.assertTrue(row["relative_resolution_over_S_is_not_compact_global_smoothness"])
        self.assertTrue(row["ordinary_modN_residues_are_not_full_Dai_Freed_character"])
        self.assertTrue(row["algebraic_C8_selector_is_not_full_order8_Gammahat_parent"])
        self.assertFalse(row["accept_if_partial_scaffolds_only"])

    def test_next_action_targets_the_live_frontier(self):
        row = self.report["consolidated_theory_card"]["next_required_action"]
        self.assertEqual(row["id"], "F89_C8_GAMMAHAT_LOCALIZED_ISOTROPY_AND_COMPACT_GLOBAL_GLUE")
        self.assertFalse(row["accepted"])

    def test_source_manifest_remains_canonical(self):
        manifest = self.report["source_manifest"]
        self.assertEqual(manifest["catalog_sha256"], master.canonical_sha(self.report["primary_sources"]))

    def test_validator_rejects_false_promotions_and_mutations(self):
        mutations = [
            lambda x: x["route_matrix"][-1].__setitem__("accepted", True),
            lambda x: x["strict_master_decision"].__setitem__("pure_Spin11_center_in_kernel", True),
            lambda x: x["strict_master_decision"].__setitem__("all_V70_A_B_C_projectors_restored", False),
            lambda x: x["strict_master_decision"].__setitem__("compact_resolved_bisection_complete", True),
            lambda x: x["strict_master_decision"].__setitem__("V87_tensor_over_four_is_continuous_6D_GS_factorization", True),
            lambda x: x["strict_master_decision"].__setitem__("one_minimal_integer_lift_is_canonical_continuous_U1_tensor", True),
            lambda x: x["strict_master_decision"].__setitem__("WCS_admissibility_conditions_checked", True),
            lambda x: x["strict_master_decision"].__setitem__("C8_unconditional_all_order_selector_after_charged_spurions", True),
            lambda x: x["strict_master_decision"].__setitem__("C8_full_order8_Gammahat_lift_constructed", True),
            lambda x: x["strict_master_decision"].__setitem__("localized_compensator_mass_coupling_constructed", True),
            lambda x: x["strict_master_decision"].__setitem__("accepted_full_parent_action_exists", True),
            lambda x: x["strict_master_decision"].__setitem__("theory_complete", True),
            lambda x: x["supersession_ledger"].__setitem__("UV_aw4_and_torsion_WCS_coefficients_fully_determined", True),
            lambda x: x["fail_closed_logic"].__setitem__("ordinary_aw4_reduction_is_not_full_spin_bordism_classification", False),
            lambda x: x["fail_closed_logic"].__setitem__("ordinary_modN_residues_are_not_full_Dai_Freed_character", False),
            lambda x: x["gate_ledger"].__setitem__("G1", "CLOSED"),
        ]
        for mutate in mutations:
            value = copy.deepcopy(self.report)
            mutate(value)
            value["core_sha256"] = master.canonical_sha(value)
            with self.assertRaises(RuntimeError):
                master.validate_report(value)

    def test_generated_artifacts_are_current(self):
        self.assertEqual(json.loads(master.OUT_JSON.read_text(encoding="utf-8")), self.report)
        self.assertEqual(master.OUT_MD.read_text(encoding="utf-8"), master.render_markdown(self.report))


if __name__ == "__main__":
    unittest.main()
