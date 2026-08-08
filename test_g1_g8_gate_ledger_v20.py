#!/usr/bin/env python3
"""Regression tests for the contract-aware G1-G8 gate ledger."""
from __future__ import annotations

import copy
import unittest

import g1_g8_gate_ledger_v20 as mod


def _bind_tool_native_root_evidence(report):
    scaffold = report["executable_scaffold_contract"]
    scaffold["model_syntax_class"] = "sarah_native"
    scaffold["tool_native_sarah_syntax"] = True
    scaffold["statically_executable_model_contract"] = True
    scaffold["lagrangian"][
        "registered_in_GaugeES_LagrangianInput"
    ] = True
    external = report["external_model_validation"]
    external["schema"] = mod.exact_x.EXTERNAL_VALIDATION_SCHEMA
    external["valid"] = True
    for name in (
        "tool_native_model_format_matches_path",
        "external_process_command_matches_tool",
        "input_manifest_schema_is_supported",
        "input_manifest_sha256_matches_entries",
        "primary_model_is_bound_in_input_manifest",
        "validation_driver_is_bound_to_command",
        "captured_process_log_is_hash_bound",
        "captured_process_log_has_all_required_pass_markers",
    ):
        external["checks"][name] = True


class G1G8GateLedgerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_audit_succeeds_while_science_is_blocked(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["audit_failures"])
        self.assertEqual(
            self.report["status"],
            "G1_G8_LEDGER_AUDIT_COMPLETE__MODEL_CONTRACT_BLOCKED__GAUGED_G1_G2_SCOPED_RECERTIFIED",
        )
        self.assertEqual(self.report["overall_state"], mod.STATUS_BLOCKED)
        self.assertFalse(self.report["contract_consistent"])
        self.assertIn(mod.CONTRACT_BLOCKER, self.report["scientific_blockers"])
        self.assertIn(
            "G3_ARBITRARY_NON_PURE_DELTA_SIGMA_UNIFORM_COERCIVITY_OPEN",
            self.report["scientific_blockers"],
        )

    def test_rank1_slice_rejects_wrong_fixed_H_orientation(self):
        forged = copy.deepcopy(
            mod._load_json_artifact(mod.G3_SU5_MAX_NEGATIVE_RANK1_SU3_SLICE_JSON)
        )
        forged["scope"]["H_fixed_to_h_minus"] = False
        report = mod._build_report_from_inputs(
            x_report=mod.exact_x.build_report(),
            g1_report=mod.gauged_g1.build_report(),
            g2_report=mod._load_or_build_gauged_g2_report(),
            filter_report=mod.gauged_filter.build_report(),
            g3_su5_max_negative_rank1_su3_slice_report=forged,
        )
        frontier = report["gauged_u1x_g3_constructive_frontier"]
        self.assertFalse(
            frontier[
                "SU5_max_negative_rank1_SU3_four_dimensional_slice_closed"
            ]
        )
        self.assertFalse(frontier["integrity_pass"])
        self.assertFalse(
            report["checks"][
                "gauged_G3_rank1_SU3_four_dimensional_slice_is_exact_and_fail_closed"
            ]
        )

    def test_fresh_contract_reports_are_integrated(self):
        reports = self.report["model_contract_reports"]
        x_report = reports["exact_X"]
        g1_report = reports["gauged_G1_character_census"]
        g2_report = reports["gauged_G2_derivative_audit"]
        filter_report = reports["gauged_scalar_filter"]
        sos_report = reports["gauged_G3_SOS_candidate"]
        pd_report = reports["gauged_G3_direct_exact_PD_rank"]
        a_square_report = reports["gauged_G3_exact_A_square_recoupling"]
        sos_bfb_report = reports["gauged_G3_exact_SOS_BFB_stationarity"]
        kernel_bound = reports["gauged_G3_fixed_P_kernel_no_go"]
        replacement = reports["gauged_G3_lower_replacement_orbit"]
        su5_pd = reports["gauged_G3_SU5_Delta_PD_global_SOS"]
        su5_hsx = reports["gauged_G3_SU5_Delta_HSX_extension"]
        su5_hsx_exact = reports["gauged_G3_SU5_Delta_HSX_exact_Hessian"]
        su5_equality = reports["gauged_G3_SU5_Delta_equality_orbit"]
        su5_phi_orbit = reports[
            "gauged_G3_SU5_Delta_Phi_orbit_lemma_audit"
        ]
        su5_phi_local = reports[
            "gauged_G3_SU5_Delta_Phi_local_component_theorem"
        ]
        su5_phi_su3 = reports[
            "gauged_G3_SU5_Delta_Phi_SU3_fixed_slice_theorem"
        ]
        su5_gap = reports["gauged_G3_SU5_Delta_chiral_global_gap"]
        fixed_f_bound = reports["gauged_G3_SU5_fixed_F_full_offkernel_bound"]
        max_negative_bound = reports[
            "gauged_G3_SU5_max_negative_all_zero_residual_bound"
        ]
        max_negative_full_bound = reports[
            "gauged_G3_SU5_max_negative_full_residual_pure_Delta_bound"
        ]
        rank1_su3_bound = reports[
            "gauged_G3_SU5_max_negative_rank1_SU3_four_dimensional_slice_bound"
        ]
        alternative_sos = reports["gauged_G3_alternative_global_SOS_audit"]
        self.assertEqual(x_report["n_failed"], 0)
        self.assertFalse(x_report["contract_consistent"])
        self.assertEqual(x_report["blocker"], mod.CONTRACT_BLOCKER)
        self.assertEqual(g1_report["model_contract_id"], mod.AUTHORITATIVE_CONTRACT_ID)
        self.assertEqual(g1_report["counts"]["hermitian_conjugacy_orbits"], 28)
        self.assertEqual(g1_report["counts"]["total_potential_orbit_multiplicity"], 44)
        self.assertEqual(g1_report["counts"]["total_real_potential_parameters"], 51)
        self.assertEqual(g2_report["n_failed"], 0, g2_report["failures"])
        self.assertEqual(g2_report["counts"]["invariant_directions"], 44)
        self.assertEqual(g2_report["counts"]["real_parameters"], 51)
        self.assertEqual(g2_report["counts"]["real_field_dimension"], 486)
        self.assertEqual(g2_report["counts"]["Hessian_shape_per_parameter"], [486, 486])
        self.assertTrue(g2_report["flags"]["G2_gauged_u1x_derivatives_certified"])
        self.assertTrue(
            filter_report["declared_symmetry_contract"]["continuous_X_imposed"]
        )
        self.assertEqual(sos_report["n_failed"], 0, sos_report["failures"])
        self.assertEqual(pd_report["n_failed"], 0, pd_report["failures"])
        self.assertEqual(
            a_square_report["status"], "EXACT_A_SQUARE_RECOUPLING_CERTIFIED"
        )
        self.assertEqual(sos_bfb_report["n_failed"], 0)
        self.assertEqual(kernel_bound["n_failed"], 0)
        self.assertEqual(replacement["n_failed"], 0)
        self.assertEqual(su5_pd["n_failed"], 0)
        self.assertEqual(su5_hsx["n_failed"], 0)
        self.assertEqual(su5_hsx_exact["n_failed"], 0)
        self.assertEqual(su5_equality["n_failed"], 0)
        self.assertEqual(su5_phi_orbit["n_failed"], 0)
        self.assertEqual(su5_phi_local["n_failed"], 0)
        self.assertEqual(su5_phi_su3["n_failed"], 0)
        self.assertEqual(su5_gap["n_failed"], 0)
        self.assertEqual(fixed_f_bound["n_failed"], 0)
        self.assertEqual(max_negative_bound["n_failed"], 0)
        self.assertEqual(
            max_negative_bound["exact_stratum_gap"]["strict_margin"],
            "7859/140295000",
        )
        self.assertEqual(max_negative_full_bound["n_failed"], 0)
        self.assertEqual(
            max_negative_full_bound["scope"]["restricted_gap_global_minimum"],
            "1/5000",
        )
        self.assertEqual(rank1_su3_bound["n_failed"], 0)
        self.assertEqual(
            rank1_su3_bound["model_contract_id"], mod.AUTHORITATIVE_CONTRACT_ID
        )
        self.assertTrue(rank1_su3_bound["scope"]["H_fixed_to_h_minus"])
        self.assertEqual(rank1_su3_bound["scope"]["Phi_slice_real_dimension"], 4)
        self.assertEqual(
            rank1_su3_bound["scope"]["full_SU3_fixed_space_real_dimension"],
            16,
        )
        self.assertEqual(
            rank1_su3_bound["radial_patch"]["restricted_global_minimum"],
            "1/5000",
        )
        self.assertFalse(rank1_su3_bound["checks"]["arbitrary_rank1_Phi_proved"])
        self.assertFalse(rank1_su3_bound["checks"]["arbitrary_Sigma35_proved"])
        self.assertFalse(rank1_su3_bound["checks"]["G3_closed"])
        self.assertEqual(alternative_sos["n_failed"], 0)

    def test_constructive_g3_frontier_is_present_but_fail_closed(self):
        frontier = self.report["gauged_u1x_g3_constructive_frontier"]
        self.assertTrue(all(frontier["artifacts_present"].values()))
        self.assertTrue(frontier["integrity_pass"])
        self.assertTrue(frontier["exact_A_square_recoupling_source_bound"])
        self.assertTrue(frontier["exact_SOS_BFB_stationarity_source_bound"])
        self.assertTrue(frontier["direct_exact_PD_rank_honestly_scoped"])
        self.assertTrue(
            frontier["SOS_candidate_exact_local_and_globally_rejected"]
        )
        self.assertTrue(frontier["fixed_P_branch_exactly_excluded"])
        self.assertTrue(
            frontier["lower_replacement_rejected_for_wrong_symmetry"]
        )
        self.assertTrue(frontier["SU5_Delta_PD_exact_global_frontier"])
        self.assertEqual(frontier["SU5_Delta_PD_exact_Hessian_rank"], 429)
        self.assertEqual(frontier["SU5_Delta_PD_exact_Hessian_nullity"], 33)
        self.assertTrue(frontier["SU5_Delta_PD_full_486_extension_open"])
        self.assertTrue(
            frontier["SU5_Delta_PD_disconnected_equality_orbits_open"]
        )
        self.assertTrue(frontier["SU5_Delta_HSX_honest_frontier"])
        self.assertEqual(frontier["SU5_Delta_HSX_nonzero_real_parameters"], 28)
        self.assertEqual(
            frontier["SU5_Delta_HSX_maximum_absolute_coefficient"], 11.0
        )
        self.assertEqual(
            frontier["SU5_Delta_HSX_exact_symmetry_ranks"], [36, 37, 38]
        )
        self.assertEqual(frontier["SU5_Delta_HSX_transverse_dimension"], 448)
        self.assertGreater(
            frontier["SU5_Delta_HSX_minimum_transverse_eigenvalue_numeric"],
            0.0,
        )
        self.assertFalse(frontier["SU5_Delta_HSX_full_Hessian_proof_grade"])
        self.assertTrue(frontier["SU5_Delta_HSX_exact_Hessian_closed"])
        self.assertEqual(frontier["SU5_Delta_HSX_exact_Hessian_rank"], 448)
        self.assertEqual(frontier["SU5_Delta_HSX_exact_Hessian_nullity"], 38)
        self.assertTrue(frontier["SU5_Delta_HSX_exact_Hessian_PSD"])
        self.assertTrue(
            frontier["SU5_Delta_HSX_exact_Hessian_kernel_is_symmetry"]
        )
        self.assertTrue(frontier["SU5_Delta_HSX_exact_quotient_positive"])
        self.assertTrue(frontier["SU5_Delta_HSX_full_quartic_BFB_exact"])
        self.assertTrue(frontier["SU5_Delta_HSX_finite_field_global_gap_open"])
        self.assertTrue(
            frontier["SU5_Delta_HSX_global_equality_classification_open"]
        )
        self.assertTrue(frontier["SU5_Delta_equality_honestly_reduced"])
        self.assertTrue(frontier["SU5_Delta_Phi_orbit_audit_honest"])
        self.assertTrue(frontier["SU5_Delta_literal_single_Phi_orbit_refuted"])
        self.assertTrue(frontier["SU5_Delta_signed_Phi_orbit_theorem_open"])
        self.assertTrue(frontier["SU5_Delta_SU4_Phi_slice_classified"])
        self.assertTrue(frontier["SU5_Delta_signed_Phi_local_components_closed"])
        self.assertFalse(frontier["SU5_Delta_distant_Phi_components_excluded"])
        self.assertTrue(frontier["SU5_Delta_Phi_SU3_fixed_slice_closed"])
        self.assertEqual(frontier["SU5_Delta_Phi_SU3_fixed_slice_dimension"], 16)
        self.assertTrue(frontier["SU5_Delta_fixed_F_Sigma_one_orbit_exact"])
        self.assertTrue(
            frontier["SU5_Delta_diagonal_Phi_slice_one_orbit_exact"]
        )
        self.assertTrue(frontier["SU5_Delta_global_Phi_orbit_lemma_open"])
        self.assertTrue(
            frontier["SU5_Delta_chiral_global_gap_honestly_reduced"]
        )
        self.assertFalse(frontier["SU5_Delta_chiral_lower_witness_found"])
        self.assertTrue(frontier["SU5_Delta_chiral_small_beta_route_exists"])
        self.assertFalse(
            frontier["SU5_Delta_chiral_beta_1_over_20_global_certified"]
        )
        self.assertFalse(
            frontier["SU5_Delta_chiral_final_acceptance_test_passes"]
        )
        self.assertTrue(frontier["SU5_fixed_F_full_offkernel_gap_closed"])
        self.assertTrue(frontier["SU5_fixed_F_gap_equality_is_selected_flag"])
        self.assertTrue(frontier["SU5_arbitrary_Phi_offstratum_gap_open"])
        self.assertTrue(
            frontier["SU5_max_negative_all_zero_residual_route_excluded"]
        )
        self.assertEqual(
            frontier["SU5_max_negative_all_zero_residual_strict_margin"],
            "7859/140295000",
        )
        self.assertTrue(
            frontier["SU5_max_negative_pure_Delta_full_residual_gap_closed"]
        )
        self.assertEqual(
            frontier["SU5_max_negative_pure_Delta_full_residual_minimum"],
            "1/5000",
        )
        self.assertTrue(
            frontier[
                "SU5_max_negative_rank1_SU3_four_dimensional_slice_closed"
            ]
        )
        self.assertEqual(
            frontier["SU5_max_negative_rank1_SU3_slice_dimension"], 4
        )
        self.assertEqual(
            frontier["SU5_max_negative_rank1_SU3_ambient_dimension"], 16
        )
        self.assertEqual(
            frontier["SU5_max_negative_rank1_SU3_slice_minimum"], "1/5000"
        )
        self.assertTrue(frontier["SU5_max_negative_arbitrary_rank1_Phi_open"])
        self.assertTrue(
            frontier["SU5_max_negative_arbitrary_Sigma_orientation_open"]
        )
        self.assertFalse(
            frontier["SU5_arbitrary_Phi_nonzero_residual_cancellations_open"]
        )
        self.assertTrue(
            frontier[
                "SU5_arbitrary_non_pure_Delta_Sigma_uniform_coercivity_open"
            ]
        )
        self.assertTrue(frontier["SU5_arbitrary_Phi_uniform_coercivity_open"])
        self.assertTrue(frontier["alternative_global_SOS_audit_honestly_open"])
        self.assertTrue(
            frontier["all_vanishing_global_SOS_replacements_excluded"]
        )
        self.assertFalse(
            frontier["nonvanishing_residual_global_SOS_replacements_excluded"]
        )
        self.assertEqual(frontier["candidate_nonzero_real_parameters"], 27)
        self.assertEqual(frontier["candidate_real_parameter_count"], 51)
        self.assertEqual(frontier["candidate_maximum_absolute_coefficient"], 9.125)
        self.assertEqual(frontier["candidate_J0"], "-21/200")
        self.assertEqual(frontier["exact_PD_rank"], 429)
        self.assertEqual(frontier["exact_PD_nullity"], 33)
        self.assertEqual(frontier["exact_full_Hessian_rank"], 448)
        self.assertTrue(frontier["direct_exact_PD_source_binding"])
        self.assertTrue(frontier["complete_potential_BFB_exactly_certified"])
        self.assertTrue(frontier["selected_vacuum_stationarity_exactly_certified"])
        self.assertTrue(frontier["strict_local_minimum_certified"])
        self.assertFalse(frontier["global_minimum_certified"])
        self.assertTrue(frontier["selected_global_minimum_disproved"])
        self.assertTrue(frontier["exact_lower_energy_field_witness_certified"])
        self.assertTrue(frontier["constructive_candidate_rejected_for_G3"])
        self.assertFalse(frontier["global_uniqueness_certified"])
        self.assertFalse(frontier["G3_closed"])
        self.assertFalse(frontier["whole_model_validated"])
        self.assertFalse(frontier["whole_model_excluded"])
        self.assertTrue(
            self.report["checks"][
                "gauged_G3_rank1_SU3_four_dimensional_slice_is_exact_and_fail_closed"
            ]
        )
        self.assertEqual(self.report["gates"]["G3"]["status"], mod.STATUS_BLOCKED)
        self.assertEqual(
            self.report["gates"]["G3"]["constructive_frontier_evidence"],
            frontier,
        )

    def test_gauged_g1_g2_are_complete_scoped_subtheorems(self):
        scoped = self.report["gauged_u1x_scalar_subtheorems"]
        self.assertEqual(scoped["model_contract_id"], mod.AUTHORITATIVE_CONTRACT_ID)
        self.assertFalse(scoped["whole_model_gate_closure"])
        self.assertEqual(scoped["G1"]["invariant_directions"], 44)
        self.assertEqual(scoped["G1"]["real_potential_parameters"], 51)
        self.assertEqual(scoped["G2"]["invariant_directions"], 44)
        self.assertEqual(scoped["G2"]["real_potential_parameters"], 51)
        self.assertEqual(scoped["G2"]["real_field_dimension"], 486)
        self.assertEqual(scoped["G2"]["promoted_stationarity_rank"], 13)
        self.assertEqual(scoped["G2"]["promoted_stationarity_nullity"], 38)
        self.assertFalse(scoped["G2"]["raw_dense_rank_14_certified"])
        self.assertTrue(scoped["G2"]["exact_Delta_R_projector_zero_certificate"])
        self.assertTrue(
            scoped["G2"]["exact_projector_zero_corrected_normalized_SVD_rank_13"]
        )
        self.assertTrue(scoped["G2"]["stationarity_rank_13_exactly_certified"])
        self.assertTrue(scoped["G2"]["stationarity_nullity_38_exactly_certified"])
        self.assertFalse(scoped["G2"]["G3_closed"])
        for gate_name in ("G1", "G2"):
            gate = self.report["gates"][gate_name]
            self.assertEqual(gate["status"], mod.STATUS_BLOCKED)
            self.assertTrue(gate["scoped_calculation_complete"])

    def test_every_authoritative_gate_is_blocked_and_none_is_closed(self):
        gates = self.report["gates"]
        self.assertEqual(set(gates), {f"G{i}" for i in range(1, 9)})
        self.assertTrue(all(row["status"] == mod.STATUS_BLOCKED for row in gates.values()))
        self.assertEqual(self.report["summary"]["closed"], [])
        self.assertEqual(self.report["summary"]["blocked"], list(gates))
        self.assertEqual(self.report["summary"]["n_closed"], 0)
        self.assertEqual(self.report["summary"]["n_blocked"], 8)

    def test_wave_zero_model_contract_precedes_g1(self):
        self.assertTrue(mod._acyclic_dependencies())
        self.assertEqual(self.report["dependencies"]["MODEL_CONTRACT"], [])
        self.assertEqual(self.report["dependencies"]["G1"], ["MODEL_CONTRACT"])
        wave0 = self.report["closure_waves"][0]
        self.assertEqual(wave0["wave"], 0)
        self.assertEqual(wave0["id"], "MODEL_CONTRACT")
        self.assertEqual(wave0["status"], mod.STATUS_BLOCKED)

    def test_historical_g1_g2_results_are_preserved_but_scoped(self):
        historical = self.report["historical_option_c_subtheorems"]
        self.assertEqual(historical["model_contract_id"], mod.HISTORICAL_CONTRACT_ID)
        self.assertFalse(historical["authoritative_for_gauged_model"])
        self.assertEqual(
            set(historical["source_contract_ids"].values()),
            {mod.HISTORICAL_CONTRACT_ID},
        )
        self.assertEqual(historical["G1"]["base_tensor_families"], 18)
        self.assertEqual(historical["G1"]["invariant_directions"], 64)
        self.assertEqual(historical["G1"]["real_potential_parameters"], 91)
        self.assertEqual(historical["G2"]["real_field_dimension"], 486)
        self.assertEqual(historical["G2"]["dense_Hessian_shape"], [486, 486])

    def test_historical_g3_saddle_and_search_facts_are_not_erased(self):
        g3 = self.report["historical_option_c_subtheorems"]["G3"]
        self.assertEqual(g3["massive_physical_quotient_dimension"], 449)
        self.assertEqual(g3["anchored_witness_negative_modes"], 46)
        self.assertEqual(g3["anchored_witness_zero_modes"], 0)
        self.assertEqual(g3["anchored_witness_positive_modes"], 403)
        self.assertEqual(g3["stationary_affine_dimension"], 77)
        self.assertEqual(g3["stability_search_iterations"], 80)
        self.assertEqual(
            g3["best_minimum_equilibrated_eigenvalue"],
            -0.025502339625368114,
        )
        self.assertFalse(g3["strict_local_minimum_found"])
        self.assertFalse(g3["whole_gauged_model_excluded"])

    def test_no_whole_model_validation_or_exclusion_claim(self):
        feasibility = self.report["feasibility"]
        self.assertEqual(feasibility["current_authoritative_closed_gates"], 0)
        self.assertFalse(feasibility["guarantee_model_survives_recertification"])
        self.assertTrue(
            feasibility["gauged_G1_scalar_census_scoped_subtheorem_complete"]
        )
        self.assertTrue(
            feasibility["gauged_G2_dense_derivative_scoped_subtheorem_complete"]
        )
        self.assertFalse(feasibility["whole_model_validated"])
        self.assertFalse(feasibility["whole_model_excluded"])
        self.assertTrue(feasibility["gauged_G3_constructive_candidate_available"])
        self.assertTrue(
            feasibility["gauged_G3_direct_exact_source_binding_complete"]
        )

    def test_repaired_contract_promotes_g1_g2_without_audit_failure(self):
        inputs = self.report["model_contract_reports"]
        repaired_x = copy.deepcopy(inputs["exact_X"])
        repaired_x.update(
            contract_consistent=True,
            blocker=None,
            scientific_blockers=[],
            contract_conflicts=[],
            overall_state="PASS",
        )
        repaired_x["flag"]["contract_consistent"] = True
        repaired_x["flag"]["x_selection_rule_consistently_declared"] = True
        _bind_tool_native_root_evidence(repaired_x)

        report = mod._build_report_from_inputs(
            x_report=repaired_x,
            g1_report=inputs["gauged_G1_character_census"],
            g2_report=inputs["gauged_G2_derivative_audit"],
            filter_report=inputs["gauged_scalar_filter"],
            g3_sos_report=inputs["gauged_G3_SOS_candidate"],
            g3_pd_report=inputs["gauged_G3_direct_exact_PD_rank"],
            g3_a_square_report=inputs["gauged_G3_exact_A_square_recoupling"],
            g3_sos_bfb_report=inputs["gauged_G3_exact_SOS_BFB_stationarity"],
        )

        self.assertEqual(report["n_failed"], 0, report["audit_failures"])
        self.assertEqual(report["overall_state"], mod.STATUS_OPEN)
        self.assertEqual(report["summary"]["closed"], ["G1", "G2", "G5"])
        self.assertEqual(report["summary"]["open"], ["G3"])
        self.assertEqual(
            {name: row["status"] for name, row in report["gates"].items()},
            {
                "G1": mod.STATUS_CLOSED,
                "G2": mod.STATUS_CLOSED,
                "G3": mod.STATUS_OPEN,
                "G4": mod.STATUS_BLOCKED,
                "G5": mod.STATUS_CLOSED,
                "G6": mod.STATUS_BLOCKED,
                "G7": mod.STATUS_BLOCKED,
                "G8": mod.STATUS_BLOCKED,
            },
        )
        self.assertEqual(report["gates"]["G4"]["unsatisfied_dependencies"], ["G3"])
        self.assertEqual(report["gates"]["G7"]["unsatisfied_dependencies"], ["G6"])
        self.assertNotIn(mod.CONTRACT_BLOCKER, report["scientific_blockers"])

    def test_unbound_boolean_cannot_promote_model_contract(self):
        inputs = self.report["model_contract_reports"]
        forged = copy.deepcopy(inputs["exact_X"])
        forged.update(
            contract_consistent=True,
            blocker=None,
            scientific_blockers=[],
            contract_conflicts=[],
            overall_state="PASS",
        )
        report = mod._build_report_from_inputs(
            x_report=forged,
            g1_report=inputs["gauged_G1_character_census"],
            g2_report=inputs["gauged_G2_derivative_audit"],
            filter_report=inputs["gauged_scalar_filter"],
            g3_sos_report=inputs["gauged_G3_SOS_candidate"],
            g3_pd_report=inputs["gauged_G3_direct_exact_PD_rank"],
            g3_a_square_report=inputs["gauged_G3_exact_A_square_recoupling"],
            g3_sos_bfb_report=inputs["gauged_G3_exact_SOS_BFB_stationarity"],
        )
        self.assertFalse(report["contract_evidence_complete"])
        self.assertFalse(report["contract_consistent"])
        self.assertNotEqual(report["overall_state"], mod.STATUS_OPEN)
        self.assertIn(
            "consistent_contract_requires_tool_native_bound_evidence",
            report["audit_failures"],
        )

    def test_dropped_pd_source_binding_breaks_fail_closed_frontier(self):
        inputs = self.report["model_contract_reports"]
        forged_pd = copy.deepcopy(inputs["gauged_G3_direct_exact_PD_rank"])
        forged_pd["flags"]["direct_exact_source_binding"] = False
        report = mod._build_report_from_inputs(
            x_report=inputs["exact_X"],
            g1_report=inputs["gauged_G1_character_census"],
            g2_report=inputs["gauged_G2_derivative_audit"],
            filter_report=inputs["gauged_scalar_filter"],
            g3_sos_report=inputs["gauged_G3_SOS_candidate"],
            g3_pd_report=forged_pd,
            g3_a_square_report=inputs["gauged_G3_exact_A_square_recoupling"],
            g3_sos_bfb_report=inputs["gauged_G3_exact_SOS_BFB_stationarity"],
        )
        self.assertEqual(report["overall_state"], "EXECUTION_FAIL")
        self.assertFalse(
            report["gauged_u1x_g3_constructive_frontier"][
                "direct_exact_PD_rank_honestly_scoped"
            ]
        )
        self.assertIn(
            "gauged_G3_direct_exact_PD_rank_is_honestly_scoped",
            report["audit_failures"],
        )

    def test_rank1_slice_cannot_overclaim_arbitrary_sigma_or_g3(self):
        inputs = self.report["model_contract_reports"]
        forged = copy.deepcopy(
            inputs[
                "gauged_G3_SU5_max_negative_rank1_SU3_four_dimensional_slice_bound"
            ]
        )
        forged["checks"]["arbitrary_Sigma35_proved"] = True
        report = mod._build_report_from_inputs(
            x_report=inputs["exact_X"],
            g1_report=inputs["gauged_G1_character_census"],
            g2_report=inputs["gauged_G2_derivative_audit"],
            filter_report=inputs["gauged_scalar_filter"],
            g3_su5_max_negative_rank1_su3_slice_report=forged,
        )
        self.assertEqual(report["overall_state"], "EXECUTION_FAIL")
        self.assertFalse(
            report["gauged_u1x_g3_constructive_frontier"][
                "SU5_max_negative_rank1_SU3_four_dimensional_slice_closed"
            ]
        )
        self.assertIn(
            "gauged_G3_rank1_SU3_four_dimensional_slice_is_exact_and_fail_closed",
            report["audit_failures"],
        )


if __name__ == "__main__":
    unittest.main()
