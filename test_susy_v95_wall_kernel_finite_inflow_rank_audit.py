import copy
import json
import unittest

import susy_v95_wall_kernel_finite_inflow_rank_audit as audit


class TestV95Route(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=audit.build_report()

    def test_core_and_parent_pins(self):
        self.assertEqual(self.report["core_sha256"],audit.canonical_sha(self.report))
        self.assertEqual(self.report["input_core_hashes"],{k:v[1] for k,v in audit.PARENTS.items()})

    def test_all_helper_cores_reconstruct(self):
        keys=("wall_symmetry_lift","local_U1_inflow_lattice","finite_defect_inflow","original_Jacobian_rank_height")
        for key,module in zip(keys,audit.MODULES):
            with self.subTest(key=key):
                self.assertEqual(self.report[key],module.build_certificate())

    def test_source_and_test_hashes(self):
        hashes=self.report["artifact_hashes"]
        self.assertEqual(hashes["generator_sha256"],audit.file_sha(audit.ROOT/(audit.__name__+".py")))
        self.assertEqual(hashes["test_sha256"],audit.file_sha(audit.TEST_PATH))
        for name,digest in hashes.items():
            if name.endswith(".py"):
                self.assertEqual(digest,audit.file_sha(audit.ROOT/name))

    def test_kernel_failure_is_unchanged_28_component_module(self):
        row=self.report["cross_certificate_checks"]
        self.assertEqual(row["unchanged_V94_wall_components_per_C4"],28)
        self.assertEqual(row["unchanged_V94_geometric_kernel_failures_per_C4"],8)
        self.assertFalse(self.report["wall_symmetry_lift"]["geometric_kernel"]["independent_R_flavor_or_C8_character_can_change_D"])

    def test_local_fractional_periods_not_global_cancellation(self):
        row=self.report["cross_certificate_checks"]
        self.assertEqual(row["bare_CP3_local_periods"],["487/4","487/4","-21/2"])
        self.assertEqual(row["formally_shifted_CP3_local_periods"],["122","122","-11"])
        self.assertEqual(row["integrated_CP3_index_before_and_after"],"233")
        self.assertFalse(self.report["local_U1_inflow_lattice"]["global_crosscheck"]["zero_sum_transfer_cancels_full_visible_anomaly"])

    def test_fractional_transfer_requires_quantized_action(self):
        row=self.report["local_U1_inflow_lattice"]["formal_zero_sum_inflow_target"]
        self.assertEqual(row["signed_localized_source_weights"],["1/4","1/4","-1/2"])
        self.assertEqual(row["minimum_common_denominator_in_enlarged_lattice"],4)
        self.assertFalse(row["quantized_bulk_tensor_or_relative_differential_action_constructed"])

    def test_defect_phases_include_orientation_and_real_half(self):
        row=self.report["finite_defect_inflow"]
        self.assertTrue(row["normalization"]["real_half_taken_before_modulo_one"])
        self.assertEqual(row["lens_C8_witnesses"]["primitive_holonomy_bare_phase_in_chosen_convention"],"+i")
        self.assertEqual(row["inflow_obligation"]["primitive_lens_required_phase_chosen_convention"],"-i")
        self.assertEqual(row["inflow_obligation"]["primitive_torus_required_phase"],"-1")
        self.assertFalse(row["lens_C8_witnesses"]["full_relative_action_orientation_dictionary_fixed"])

    def test_defect_curvature_match_is_retained_not_promoted(self):
        row=self.report["cross_certificate_checks"]
        self.assertTrue(row["finite_defect_uses_unchanged_unit_mass_index"])
        self.assertEqual(row["V94_defect_curvature_residual"],"0")
        self.assertTrue(row["CP3_index_periods_are_not_defect_eta_phases"])
        self.assertFalse(row["all_checks_prove_quantized_same_action_completion"])

    def test_original_torsion_and_rank_bound(self):
        row=self.report["original_Jacobian_rank_height"]["original_free_MW_rank_bound"]
        self.assertEqual(row["V94_original_torsion_order"],1)
        self.assertEqual([row["original_field_rank_lower_bound"],row["original_field_rank_upper_bound"]],[0,12])
        self.assertFalse(row["exact_free_rank_computed"])
        self.assertFalse(row["original_nonzero_section_constructed"])

    def test_two_conditional_height_normalizations(self):
        row=self.report["original_Jacobian_rank_height"]["conditional_target_height_normalizations"]
        self.assertEqual([b["required_section_height_class_S_F"] for b in row["branches"]],[["148","768"],["37","192"]])
        self.assertEqual([b["surviving_nodes"] for b in row["branches"]],[[0],[1]])
        self.assertFalse(row["branch_choice_or_actual_section_constructed"])

    def test_no_false_retraction_or_global_no_go(self):
        row=self.report["supersession_boundary"]
        for key,value in row.items():
            if key != "unchanged_module_repair_by_independent_internal_centers":
                self.assertFalse(value,key)
        self.assertTrue(row["unchanged_module_repair_by_independent_internal_centers"].startswith("REJECTED:"))

    def test_all_gates_open_and_F96_is_required(self):
        self.assertEqual(set(self.report["gate_ledger"]),{"G"+str(i) for i in range(1,9)})
        self.assertTrue(all(v.startswith("OPEN:") for v in self.report["gate_ledger"].values()))
        self.assertEqual(self.report["terminal_decision"]["closed_gates"],[])
        self.assertFalse(self.report["terminal_decision"]["all_F95_obligations_fully_completed"])
        self.assertEqual(self.report["next_required_action"]["id"],"F96_QUANTIZED_RELATIVE_INFLOW_AND_ORIGINAL_MW_GENERATOR")

    def test_noncanonical_report_rejected(self):
        changed=copy.deepcopy(self.report)
        changed["core_sha256"]="0"*64
        with self.assertRaises(RuntimeError):
            audit.validate_report(changed)

    def test_rehashed_quantum_promotion_rejected(self):
        changed=copy.deepcopy(self.report)
        changed["terminal_decision"]["quantized_relative_WCS_Dai_Freed_trivialization_constructed"]=True
        changed["core_sha256"]=audit.canonical_sha(changed)
        with self.assertRaises(RuntimeError):
            audit.validate_report(changed)

    def test_rehashed_rank_change_rejected(self):
        changed=copy.deepcopy(self.report)
        changed["original_Jacobian_rank_height"]["original_free_MW_rank_bound"]["original_field_rank_upper_bound"]=0
        changed["core_sha256"]=audit.canonical_sha(changed)
        with self.assertRaises(RuntimeError):
            audit.validate_report(changed)

    def test_generated_artifacts_current(self):
        self.assertEqual(json.loads(audit.OUT_JSON.read_text(encoding="utf-8")),self.report)
        self.assertEqual(audit.OUT_MD.read_text(encoding="utf-8"),audit.render_markdown(self.report))


if __name__=="__main__":
    unittest.main()
