#!/usr/bin/env python3
"""Regression tests for the contract-aware G1-G8 gate ledger."""
from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

import g1_g8_gate_ledger_v20 as mod
import g3_sm_target_track_v20 as sm_track

CLOSED_G3_STATUS = (
    "G1_G8_LEDGER_AUDIT_COMPLETE__MODEL_CONTRACT_CONSISTENT__"
    "G1_G2_G3_G5_CLOSED__G4_OPEN"
)
OPEN_G3_STATUS = (
    "G1_G8_LEDGER_AUDIT_COMPLETE__MODEL_CONTRACT_CONSISTENT__"
    "G3_SM_TRACK_NOT_CERTIFIED__G3_OPEN"
)
SM_TRACK_CLOSED_STATUSES = {
    "G1": mod.STATUS_CLOSED,
    "G2": mod.STATUS_CLOSED,
    "G3": mod.STATUS_CLOSED,
    "G4": mod.STATUS_OPEN,
    "G5": mod.STATUS_CLOSED,
    "G6": mod.STATUS_BLOCKED,
    "G7": mod.STATUS_BLOCKED,
    "G8": mod.STATUS_BLOCKED,
}
DIAGNOSTIC_COERCIVITY_PROBLEM = (
    "G3_ARBITRARY_NON_PURE_DELTA_SIGMA_UNIFORM_COERCIVITY_OPEN"
)


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

    def _build_with_sm_track_inputs(self, sm_inputs):
        inputs = self.report["model_contract_reports"]
        return mod._build_report_from_inputs(
            x_report=inputs["exact_X"],
            g1_report=inputs["gauged_G1_character_census"],
            g2_report=inputs["gauged_G2_derivative_audit"],
            filter_report=inputs["gauged_scalar_filter"],
            g3_sm_track_inputs=sm_inputs,
        )

    def test_audit_succeeds_with_attested_contract_and_g3_closed_on_sm_track(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["audit_failures"])
        self.assertEqual(self.report["status"], CLOSED_G3_STATUS)
        self.assertEqual(self.report["overall_state"], mod.STATUS_OPEN)
        self.assertTrue(self.report["contract_consistent"])
        self.assertTrue(self.report["contract_evidence_complete"])
        self.assertNotIn(mod.CONTRACT_BLOCKER, self.report["scientific_blockers"])
        self.assertEqual(
            self.report["scientific_blockers"],
            list(sm_track.DOWNSTREAM_BLOCKERS),
        )
        self.assertNotIn(
            "G3_SM_PRESERVING_TARGET_REQUIRED",
            self.report["scientific_blockers"],
        )
        self.assertNotIn(
            DIAGNOSTIC_COERCIVITY_PROBLEM, self.report["scientific_blockers"]
        )
        self.assertEqual(
            self.report["diagnostic_open_problems"],
            [DIAGNOSTIC_COERCIVITY_PROBLEM],
        )
        self.assertIn(
            "chiral_H_SU5_Delta diagnostic track",
            self.report["diagnostic_open_problems_note"],
        )
        track = self.report["g3_sm_target_track"]
        self.assertEqual(track["track"], sm_track.TRACK_NAME)
        self.assertIs(track["closed"], True)
        self.assertIs(track["prerequisites_evaluated"], True)
        self.assertEqual(track["blockers"], [])
        self.assertIs(track["downstream_caveats_resolved"], False)
        self.assertEqual(track["closure_scope"], sm_track.CLOSURE_SCOPE)
        for name in (
            "only_sm_track_G3_and_bound_G5_close_among_G3_G8",
            "g3_sm_track_is_the_only_closure_route",
            "chiral_H_diagnostic_track_cannot_close_G3",
            "g5_closed_only_on_the_bound_pati_salam_vector",
            "gate_frontier_matches_contract_state",
        ):
            self.assertIs(self.report["checks"][name], True, name)
        self.assertNotIn(
            "only_certified_G5_closes_among_G3_G8", self.report["checks"]
        )
        self.assertIs(
            self.report["feasibility"]["gauged_G3_sm_pati_salam_track_closed"],
            True,
        )

    def test_expected_gate_statuses_follow_the_sm_track_and_the_dag(self):
        blocked = {f"G{i}": mod.STATUS_BLOCKED for i in range(1, 9)}
        for g3_closed in (False, True):
            for g5_closed in (False, True):
                self.assertEqual(
                    mod._expected_gate_statuses(
                        False, g3_closed=g3_closed, g5_closed=g5_closed
                    ),
                    blocked,
                )
                self.assertEqual(
                    mod._expected_gate_statuses(
                        True, g3_closed=g3_closed, g5_closed=g5_closed
                    ),
                    {
                        "G1": mod.STATUS_CLOSED,
                        "G2": mod.STATUS_CLOSED,
                        "G3": mod.STATUS_CLOSED if g3_closed else mod.STATUS_OPEN,
                        "G4": mod.STATUS_OPEN if g3_closed else mod.STATUS_BLOCKED,
                        "G5": mod.STATUS_CLOSED if g5_closed else mod.STATUS_OPEN,
                        "G6": mod.STATUS_BLOCKED,
                        "G7": mod.STATUS_BLOCKED,
                        "G8": mod.STATUS_BLOCKED,
                    },
                )
        with self.assertRaises(TypeError):
            mod._expected_gate_statuses(True)  # the track inputs are required

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
        rank1_su4_stabilizer = reports[
            "gauged_G3_rank1_SU4_stabilizer_infrastructure"
        ]
        rank1_su4_intertwiners = reports[
            "gauged_G3_rank1_SU4_Phi210_intertwiner_infrastructure"
        ]
        rank1_su4_aligned = reports[
            "gauged_G3_rank1_SU4_aligned_carrier_infrastructure"
        ]
        rank1_su4_quadratic = reports[
            "gauged_G3_rank1_SU4_Phi210_quadratic_basis"
        ]
        rank1_su4_census = reports[
            "gauged_G3_rank1_SU4_augmented_SOS_census"
        ]
        rank1_su4_cubic = reports[
            "gauged_G3_rank1_SU4_augmented_SOS_cubic_map"
        ]
        rank1_su4_quartic = reports[
            "gauged_G3_rank1_SU4_augmented_SOS_quartic_map"
        ]
        rank1_su4_psd_target = reports[
            "gauged_G3_rank1_SU4_legacy_v20_PSD_routes_and_rejected_target"
        ]
        rank1_su4_corrected = reports[
            "gauged_G3_rank1_SU4_corrected_fixed_endpoint_publication_v21"
        ]
        alternative_sos = reports["gauged_G3_alternative_global_SOS_audit"]
        self.assertEqual(x_report["n_failed"], 0)
        self.assertTrue(x_report["contract_consistent"])
        self.assertIsNone(x_report["blocker"])
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
        self.assertEqual(rank1_su4_stabilizer["n_failed"], 0)
        self.assertTrue(rank1_su4_stabilizer["scope"]["infrastructure_only"])
        self.assertFalse(rank1_su4_stabilizer["scope"]["G3_closed"])
        self.assertEqual(rank1_su4_intertwiners["n_failed"], 0)
        self.assertEqual(
            rank1_su4_intertwiners["carriers"][
                "Sym2_Phi210_SU4_singlet_dimension"
            ],
            45,
        )
        self.assertFalse(
            rank1_su4_intertwiners["scope"]["Schur_SOS_SDP_constructed"]
        )
        self.assertFalse(rank1_su4_intertwiners["scope"]["G3_closed"])
        self.assertEqual(
            rank1_su4_aligned["alignment"][
                "concatenated_aligned_basis_rank_mod_prime"
            ],
            210,
        )
        self.assertTrue(
            rank1_su4_aligned["scope"][
                "physical_real_structure_and_Gaussian_embeddings_constructed"
            ]
        )
        self.assertEqual(
            rank1_su4_quadratic["constraint_system"]["reduced_constraint_shape"],
            [5952, 551],
        )
        self.assertEqual(
            rank1_su4_quadratic["constraint_system"]["exact_rational_rank"], 506
        )
        self.assertEqual(
            rank1_su4_quadratic["constraint_system"]["exact_rational_nullity"], 45
        )
        self.assertFalse(
            rank1_su4_quadratic["scope"][
                "augmented_homogeneous_Schur_SOS_SDP_constructed"
            ]
        )
        self.assertEqual(
            rank1_su4_census["augmented_representation"][
                "augmented_homogeneous_dimension"
            ],
            22_366,
        )
        self.assertEqual(
            rank1_su4_census["augmented_representation"][
                "complex_irreducible_copy_count"
            ],
            824,
        )
        self.assertEqual(
            rank1_su4_census["augmented_representation"][
                "Schur_real_parameter_count"
            ],
            19_594,
        )
        self.assertEqual(
            rank1_su4_census["invariant_quartic_target"][
                "invariant_equation_count"
            ],
            6_585,
        )
        self.assertFalse(
            rank1_su4_census["scope"][
                "Schur_coordinate_6585_by_19594_coefficient_matrix_constructed"
            ]
        )
        self.assertEqual(
            rank1_su4_cubic["cubic_coordinate_map"]["coordinate_map_shape"],
            [478, 1_414],
        )
        self.assertEqual(
            rank1_su4_cubic["cubic_coordinate_map"]["exact_rank"], 478
        )
        self.assertEqual(
            rank1_su4_cubic["cubic_coordinate_map"]["exact_kernel_dimension"],
            936,
        )
        self.assertTrue(
            rank1_su4_cubic["cubic_coordinate_map"][
                "abstract_zero_placeholder_is_not_a_physical_G3_target"
            ]
        )
        self.assertFalse(
            rank1_su4_cubic["scope"][
                "physical_G3_gap_target_vector_constructed"
            ]
        )
        self.assertFalse(rank1_su4_cubic["scope"]["G3_closed"])
        self.assertEqual(
            rank1_su4_quartic["coefficient_map_certificate"]["shape"],
            [6_057, 18_085],
        )
        self.assertEqual(
            rank1_su4_quartic["coefficient_map_certificate"]["rank_over_Q_exact"],
            6_057,
        )
        self.assertEqual(
            rank1_su4_quartic["coefficient_map_certificate"][
                "kernel_dimension_over_Q_exact"
            ],
            12_028,
        )
        self.assertFalse(
            rank1_su4_quartic["scope"]["physical_quartic_target_constructed"]
        )
        self.assertFalse(rank1_su4_quartic["scope"]["G3_closed"])
        self.assertTrue(
            rank1_su4_psd_target["scope"][
                "all_22_standard_PSD_coordinate_routes_constructed"
            ]
        )
        self.assertEqual(
            rank1_su4_psd_target["standard_PSD_coordinate_routes"][
                "standard_total_parameter_count"
            ],
            19_594,
        )
        self.assertTrue(
            mod.corrected_rank1.corrected_fixed_endpoint_theorem_exact(
                rank1_su4_corrected
            )
        )
        self.assertFalse(
            rank1_su4_psd_target["scope"]["semidefinite_feasibility_solved"]
        )
        self.assertFalse(rank1_su4_psd_target["scope"]["G3_closed"])
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
        self.assertTrue(frontier["rank1_SU4_stabilizer_infrastructure_exact"])
        self.assertEqual(frontier["rank1_SU4_joint_stabilizer_dimension"], 15)
        self.assertTrue(
            frontier["rank1_SU4_Phi210_intertwiner_infrastructure_exact"]
        )
        self.assertEqual(frontier["rank1_SU4_Phi210_carrier_count"], 25)
        self.assertEqual(frontier["rank1_SU4_Sym2_invariant_dimension"], 45)
        self.assertTrue(frontier["rank1_SU4_aligned_carriers_exact"])
        self.assertEqual(frontier["rank1_SU4_aligned_direct_sum_rank"], 210)
        self.assertTrue(frontier["rank1_SU4_physical_real_maps_exact"])
        self.assertTrue(frontier["rank1_SU4_Phi210_quadratic_basis_exact"])
        self.assertEqual(
            frontier["rank1_SU4_quadratic_constraint_shape"], [5952, 551]
        )
        self.assertEqual(frontier["rank1_SU4_quadratic_constraint_rank"], 506)
        self.assertEqual(frontier["rank1_SU4_quadratic_constraint_nullity"], 45)
        self.assertEqual(frontier["rank1_SU4_quadratic_basis_count"], 45)
        self.assertEqual(frontier["rank1_SU4_quadratic_basis_rank"], 45)
        self.assertTrue(frontier["rank1_SU4_quadratic_live_invariance_exact"])
        self.assertTrue(frontier["rank1_SU4_Schur_SOS_SDP_open"])
        self.assertTrue(frontier["rank1_SU4_arbitrary_Phi_bound_open"])
        self.assertTrue(frontier["rank1_SU4_augmented_SOS_census_exact"])
        self.assertEqual(
            frontier["rank1_SU4_augmented_homogeneous_dimension"], 22_366
        )
        self.assertEqual(
            frontier["rank1_SU4_augmented_complex_isotypic_type_count"], 35
        )
        self.assertEqual(
            frontier["rank1_SU4_augmented_complex_irreducible_copy_count"], 824
        )
        self.assertEqual(
            frontier["rank1_SU4_augmented_real_isotypic_block_count"], 22
        )
        self.assertEqual(
            frontier["rank1_SU4_augmented_Schur_real_parameter_count"], 19_594
        )
        self.assertEqual(
            frontier["rank1_SU4_augmented_invariant_equation_count"], 6_585
        )
        self.assertTrue(frontier["rank1_SU4_augmented_coordinate_Schur_map_open"])
        self.assertTrue(frontier["rank1_SU4_augmented_isotypic_maps_open"])
        self.assertTrue(frontier["rank1_SU4_augmented_physical_target_open"])
        self.assertTrue(frontier["rank1_SU4_augmented_Schur_SOS_SDP_open"])
        self.assertTrue(frontier["rank1_SU4_augmented_arbitrary_Phi_bound_open"])
        self.assertTrue(frontier["rank1_SU4_augmented_cubic_map_exact"])
        self.assertEqual(
            frontier["rank1_SU4_augmented_cubic_coordinate_map_shape"],
            [478, 1_414],
        )
        self.assertEqual(
            frontier["rank1_SU4_augmented_cubic_coordinate_map_rank"], 478
        )
        self.assertEqual(
            frontier[
                "rank1_SU4_augmented_cubic_coordinate_map_kernel_dimension"
            ],
            936,
        )
        self.assertTrue(
            frontier["rank1_SU4_augmented_cubic_zero_placeholder_nonphysical"]
        )
        self.assertTrue(
            frontier["rank1_SU4_augmented_cubic_other_graded_maps_open"]
        )
        self.assertTrue(
            frontier["rank1_SU4_augmented_cubic_physical_target_open"]
        )
        self.assertTrue(
            frontier["rank1_SU4_augmented_cubic_Schur_SOS_SDP_open"]
        )
        self.assertTrue(frontier["rank1_SU4_augmented_cubic_G3_open"])
        self.assertTrue(frontier["rank1_SU4_augmented_quartic_map_exact"])
        self.assertEqual(
            frontier["rank1_SU4_augmented_quartic_coordinate_map_shape"],
            [6_057, 18_085],
        )
        self.assertEqual(
            frontier["rank1_SU4_augmented_quartic_coordinate_map_rank"], 6_057
        )
        self.assertEqual(
            frontier[
                "rank1_SU4_augmented_quartic_coordinate_map_kernel_dimension"
            ],
            12_028,
        )
        self.assertTrue(
            frontier["rank1_SU4_augmented_quartic_physical_target_open"]
        )
        self.assertTrue(
            frontier[
                "rank1_SU4_augmented_quartic_standard_PSD_congruences_open"
            ]
        )
        self.assertTrue(frontier["rank1_SU4_augmented_quartic_SDP_open"])
        self.assertTrue(frontier["rank1_SU4_augmented_quartic_G3_open"])
        self.assertTrue(
            frontier[
                "rank1_SU4_legacy_v20_PSD_routes_and_stale_payload_well_formed"
            ]
        )
        self.assertFalse(frontier["rank1_SU4_legacy_v20_physical_target_valid"])
        self.assertFalse(frontier["rank1_SU4_legacy_v20_primal_valid"])
        self.assertEqual(
            frontier["rank1_SU4_augmented_standard_PSD_route_count"], 22
        )
        self.assertEqual(
            frontier["rank1_SU4_augmented_standard_PSD_parameter_count"],
            19_594,
        )
        self.assertTrue(frontier["rank1_SU4_corrected_fixed_endpoint_theorem_exact"])
        self.assertEqual(
            frontier["rank1_SU4_corrected_positive_Gram_map_shape"],
            [6_585, 19_594],
        )
        self.assertEqual(
            frontier["rank1_SU4_corrected_positive_Gram_map_common_denominator"],
            256,
        )
        self.assertEqual(
            frontier["rank1_SU4_corrected_positive_Gram_map_nnz"], 138_550
        )
        self.assertEqual(
            frontier["rank1_SU4_corrected_physical_target_common_denominator"],
            576_000,
        )
        self.assertEqual(
            frontier["rank1_SU4_corrected_physical_target_nonzero_count"], 512
        )
        self.assertEqual(
            frontier["rank1_SU4_corrected_exact_coefficient_equalities"], 6_585
        )
        self.assertEqual(
            frontier["rank1_SU4_corrected_strict_positive_Gram_blocks"], 22
        )
        self.assertEqual(
            frontier["rank1_SU4_corrected_strict_positive_LDL_pivots"], 824
        )
        self.assertTrue(
            frontier["rank1_SU4_corrected_arbitrary_real_Phi_at_fixed_endpoint"]
        )
        self.assertFalse(frontier["rank1_SU4_corrected_global_Sigma_proved"])
        self.assertFalse(frontier["rank1_SU4_corrected_general_H_proved"])
        self.assertFalse(frontier["rank1_SU4_corrected_full_Hessian_proved"])
        self.assertFalse(frontier["rank1_SU4_corrected_G3_closed"])
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
        self.assertTrue(
            self.report["checks"][
                "gauged_G3_rank1_SU4_infrastructure_is_exact_and_fail_closed"
            ]
        )
        # The chiral/SOS frontier stays fail-closed (its own G3_closed flag is
        # False); the ledger's G3 is CLOSED only through the SM track.
        self.assertEqual(self.report["gates"]["G3"]["status"], mod.STATUS_CLOSED)
        self.assertEqual(
            self.report["gates"]["G3"]["closing_track"], sm_track.TRACK_NAME
        )
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
            self.assertEqual(gate["status"], mod.STATUS_CLOSED)
            self.assertTrue(gate["scoped_calculation_complete"])

    def test_attested_contract_closes_g1_g2_g3_g5_and_leaves_g4_open(self):
        gates = self.report["gates"]
        self.assertEqual(set(gates), {f"G{i}" for i in range(1, 9)})
        self.assertEqual(
            {name: row["status"] for name, row in gates.items()},
            SM_TRACK_CLOSED_STATUSES,
        )
        self.assertEqual(
            self.report["summary"]["closed"], ["G1", "G2", "G3", "G5"]
        )
        self.assertEqual(self.report["summary"]["open"], ["G4"])
        self.assertEqual(self.report["summary"]["blocked"], ["G6", "G7", "G8"])
        self.assertEqual(self.report["summary"]["n_closed"], 4)
        self.assertEqual(self.report["summary"]["n_open"], 1)
        self.assertEqual(self.report["summary"]["n_blocked"], 3)
        self.assertEqual(gates["G4"]["unsatisfied_dependencies"], [])
        self.assertIsNone(gates["G4"]["blocking_root"])
        self.assertEqual(gates["G6"]["unsatisfied_dependencies"], ["G4"])
        self.assertEqual(gates["G6"]["blocking_root"], "DEPENDENCY_NOT_CLOSED")
        g3 = gates["G3"]
        self.assertEqual(g3["closing_track"], "sm_pati_salam")
        self.assertEqual(g3["closure_scope"], sm_track.CLOSURE_SCOPE)
        self.assertEqual(
            g3["disclosures"], self.report["g3_sm_target_track"]["disclosures"]
        )
        self.assertEqual(len(g3["disclosures"]), 7)
        self.assertEqual(
            g3["diagnostic_tracks"],
            {
                "chiral_H_SU5_Delta": (
                    "integrity-checked diagnostic "
                    "(constructive_frontier_evidence); can never close G3"
                )
            },
        )
        # G3 keeps its definition; the caveats are disclosures, not G3 items.
        self.assertEqual(
            g3["open_scope"],
            [
                "classify every competing stationary symmetry orbit and compare exact potential values",
                "prove global minimality and uniqueness, or exhibit a lower competing extremum",
            ],
        )

    def test_closed_scopes_g4_g5_specs_and_d5_routed_caveats(self):
        gates = self.report["gates"]
        track = self.report["g3_sm_target_track"]
        self.assertEqual(
            {name: row["authoritative_closed_scope"] for name, row in gates.items()},
            {
                "G1": ["promoted exact-X scalar census"],
                "G2": ["promoted exact-X dense derivative and Ward audit"],
                "G3": [sm_track.G3_LEDGER_CLOSED_SCOPE],
                "G4": [],
                "G5": [sm_track.G5_LEDGER_CLOSED_SCOPE],
                "G6": [],
                "G7": [],
                "G8": [],
            },
        )
        g4_spec = gates["G4"]["open_scope"][0]
        self.assertIn("rank 34", g4_spec)
        self.assertIn("452", g4_spec)
        self.assertIn("rank 35", g4_spec)
        self.assertIn("451", g4_spec)
        self.assertIn("SM Pati-Salam eps member", g4_spec)
        self.assertIn(
            "the axion/PQ direction and the eps -> 0 tuned light doublet",
            gates["G4"]["open_scope"][1],
        )
        self.assertEqual(
            gates["G5"]["open_scope"],
            [
                "keep the source-bound BFB certificate bound to the coupling vector of the accepted G3 witness (the SM Pati-Salam 27-parameter vector, V4 >= |q|^4/167; the eps N_H term is quadratic)"
            ],
        )
        spec_items = {
            "G4": list(gates["G4"]["open_scope"][:2]),
            "G6": ["await authoritative G3/G4/G5 and emit the complete positive spectrum"],
            "G7": ["await G6 and independently validate the full beta system"],
            "G8": ["await authoritative G3/G6/G7 before any unique lifetime claim"],
        }
        caveats = track["downstream_caveats"]
        self.assertEqual(len(caveats), 10)
        for gate_name, specification in spec_items.items():
            open_scope = gates[gate_name]["open_scope"]
            n_spec = len(specification)
            self.assertEqual(open_scope[:n_spec], specification, gate_name)
            routed = [
                f"routed from G3 by decision D5 ({c['id']}): {c['text']}"
                for c in caveats
                if c["gate"] == gate_name
            ]
            self.assertTrue(routed, gate_name)
            self.assertEqual(open_scope[n_spec:], routed, gate_name)
        self.assertTrue(
            any(
                item.startswith(
                    "routed from G3 by decision D5 (sub_M_I_coloured_126bar_states): "
                )
                for item in gates["G6"]["open_scope"]
            )
        )
        self.assertTrue(
            any(
                item.startswith(
                    "routed from G3 by decision D5 (zero_modes_and_ranks_at_witness): "
                )
                for item in gates["G4"]["open_scope"]
            )
        )
        # Naturalness lies outside G1-G8 and G3 keeps only disclosures.
        routed_everywhere = "\n".join(
            item for row in gates.values() for item in row["open_scope"]
        )
        self.assertNotIn("(naturalness_of_tunings)", routed_everywhere)
        self.assertNotIn("routed from G3", "\n".join(gates["G3"]["open_scope"]))
        self.assertNotIn("routed from G3", "\n".join(gates["G5"]["open_scope"]))
        # G5 is carried by the SM Pati-Salam coupling vector (decision D4).
        binding = gates["G5"]["bfb_coupling_vector"]
        self.assertEqual(binding, track["g5_bfb_binding"])
        self.assertIs(binding["certified"], True)
        self.assertEqual(len(binding["coefficients"]), 27)
        self.assertEqual(binding["quartic_bound_constant"], "1/167")
        # The G3 row's embedded frontier evidence keeps its own G3_closed=false
        # self-claim; the row labels that role (decision D1).
        self.assertEqual(gates["G3"]["status"], mod.STATUS_CLOSED)
        self.assertIs(gates["G3"]["constructive_frontier_evidence"]["G3_closed"], False)
        self.assertIn("decision D1", gates["G3"]["constructive_frontier_evidence_role"])
        self.assertIn("self-claims", gates["G3"]["constructive_frontier_evidence_role"])
        self.assertIn("decision D4", gates["G5"]["constructive_frontier_evidence_role"])
        self.assertIn(
            "no longer carries G5", gates["G5"]["constructive_frontier_evidence_role"]
        )
        self.assertEqual(
            gates["G5"]["constructive_frontier_evidence"],
            self.report["gauged_u1x_g3_constructive_frontier"],
        )

    def test_wave_zero_model_contract_precedes_g1(self):
        self.assertTrue(mod._acyclic_dependencies())
        self.assertEqual(self.report["dependencies"]["MODEL_CONTRACT"], [])
        self.assertEqual(self.report["dependencies"]["G1"], ["MODEL_CONTRACT"])
        wave0 = self.report["closure_waves"][0]
        self.assertEqual(wave0["wave"], 0)
        self.assertEqual(wave0["id"], "MODEL_CONTRACT")
        self.assertEqual(wave0["status"], mod.STATUS_CLOSED)

    def test_wave3_closes_g3_on_the_sm_track_with_d5_caveat_routing(self):
        waves = self.report["closure_waves"]
        wave3 = waves[3]
        self.assertEqual(wave3["wave"], 3)
        self.assertEqual(wave3["gates"], ["G3", "G4", "G5"])
        self.assertEqual(
            wave3["status"], "G3_CLOSED_ON_SM_PATI_SALAM_TRACK__G4_OPEN__G5_CLOSED"
        )
        deliverable = wave3["deliverable"]
        self.assertEqual(
            deliverable,
            "G3 is CLOSED on the SM Pati-Salam track (g3_sm_target_track_v20 "
            "through final_g3_acceptance_gate_v20). "
            + sm_track.CLOSURE_SCOPE
            + " "
            + sm_track.WITNESS_SENTENCE
            + " "
            + sm_track.CAVEAT_ROUTING_SENTENCE
            + " G4 is OPEN: recompute the ranks 34/35 (quotients 452/451) at "
            "the witness and classify its zero modes. G5 is CLOSED on the same "
            "Pati-Salam coupling vector. "
            + mod.CHIRAL_WAVE3_TAIL,
        )
        self.assertIn(sm_track.CAVEAT_ROUTING_SENTENCE, deliverable)
        self.assertIn(sm_track.CLOSURE_SCOPE, deliverable)
        self.assertNotIn("still needs its model-level caveats resolved", deliverable)
        self.assertNotIn("remaining coercivity problem is mathematical only", deliverable)
        self.assertNotIn("G3 needs an SM-preserving candidate", deliverable)
        self.assertIn(
            "and is kept only as an integrity-checked diagnostic track that can "
            "never close G3. The chiral-H point's full 486-real Hessian",
            deliverable,
        )
        self.assertTrue(
            deliverable.endswith(
                "Global Sigma and general/full H remain open for that non-SM "
                "point (the exact 448/38 full Hessian is certified separately)."
            )
        )
        self.assertNotIn("and G3 remain open", deliverable)
        self.assertEqual(
            [(wave["wave"], wave["status"]) for wave in waves[4:]],
            [(4, "BLOCKED_ON_G4"), (5, "BLOCKED_ON_G6"), (6, "BLOCKED_ON_G6_G7")],
        )
        verdict = self.report["verdict"]
        self.assertTrue(
            verdict.startswith(
                "The ledger audit succeeds and the repaired gauged-U(1)_X "
                "contract promotes the completed G1 scalar census and G2 dense "
                "derivative theorem to CLOSED. G3 is CLOSED on the SM "
                "Pati-Salam track, its only closure route "
                "(g3_sm_target_track_v20 through final_g3_acceptance_gate_v20): "
                + sm_track.CLOSURE_SCOPE
                + " "
                + sm_track.WITNESS_SENTENCE
                + " G5 is CLOSED on the same Pati-Salam coupling vector "
                "(V4 >= |q|^4/167; the eps N_H term is quadratic). G4 is OPEN; "
                "G6-G8 remain dependency-blocked. "
                + sm_track.CAVEAT_ROUTING_SENTENCE
                + " Diagnostics that cannot close G3: A perturbative 27-of-51 "
                "SOS candidate with J0=-21/200 has"
            )
        )
        self.assertTrue(
            verdict.endswith(
                "Historical Option-C evidence remains scoped and closes no "
                "gauged-model gate."
            )
        )
        self.assertNotIn("G5 is CLOSED; G4 and G6-G8 remain", verdict)

    def test_pati_salam_equality_set_binding_is_informational(self):
        committed = mod.load_sm_pati_salam_equality_set_report()
        self.assertEqual(
            committed.get("status"),
            mod.G3_SM_PATI_SALAM_EQUALITY_SET_PROVED_STATUS,
        )
        self.assertIs(type(committed.get("n_failed")), int)
        self.assertEqual(committed["n_failed"], 0)
        self.assertTrue(mod.sm_pati_salam_equality_set_certified(committed))
        self.assertFalse(hasattr(mod, "G3_SM_PATI_SALAM_EQUALITY_SET_WAVE3_CERTIFIED"))
        self.assertFalse(hasattr(mod, "G3_SM_PATI_SALAM_EQUALITY_SET_WAVE3_FALLBACK"))
        binding = self.report["g3_sm_pati_salam_equality_set_binding"]
        self.assertEqual(
            binding,
            {
                "source": "g3_sm_pati_salam_equality_set_v20",
                "report": "G3_SM_PATI_SALAM_EQUALITY_SET_V20.json",
                "required_status": mod.G3_SM_PATI_SALAM_EQUALITY_SET_PROVED_STATUS,
                "status": mod.G3_SM_PATI_SALAM_EQUALITY_SET_PROVED_STATUS,
                "n_failed": 0,
                "certified": True,
            },
        )

    def test_pati_salam_equality_set_certification_is_fail_closed(self):
        committed = mod.load_sm_pati_salam_equality_set_report()
        rejected = (
            {},
            None,
            [],
            {**committed, "n_failed": 1},
            {**committed, "n_failed": False},
            {**committed, "n_failed": "0"},
            {**committed, "n_failed": 0.0},
            {key: value for key, value in committed.items() if key != "n_failed"},
            {
                **committed,
                "status": "SM_PATI_SALAM_EQUALITY_SET__UNIQUENESS_MODULO_SYMMETRY__OPEN",
            },
            {"status": "G3_SM_PATI_SALAM_EQUALITY_SET_AUDIT_FAILED", "n_failed": 0},
        )
        for forged in rejected:
            self.assertFalse(mod.sm_pati_salam_equality_set_certified(forged))
            self.assertFalse(
                mod.sm_pati_salam_equality_set_binding(forged)["certified"]
            )
        self.assertEqual(
            mod.load_sm_pati_salam_equality_set_report(
                mod.ROOT / "NO_SUCH_PATI_SALAM_EQUALITY_SET_REPORT.json"
            ),
            {},
        )
        with tempfile.TemporaryDirectory() as scratch:
            for name, payload in (
                ("corrupt.json", b"{not json"),
                ("undecodable.json", b"\xff\xfe\xfa"),
                ("listed.json", b"[1, 2]"),
            ):
                path = Path(scratch) / name
                path.write_bytes(payload)
                self.assertEqual(mod.load_sm_pati_salam_equality_set_report(path), {})

    def test_informational_equality_set_binding_never_changes_a_gate(self):
        inputs = self.report["model_contract_reports"]
        committed = mod.load_sm_pati_salam_equality_set_report()
        for forged in ({}, {**committed, "n_failed": True}):
            report = mod._build_report_from_inputs(
                x_report=inputs["exact_X"],
                g1_report=inputs["gauged_G1_character_census"],
                g2_report=inputs["gauged_G2_derivative_audit"],
                filter_report=inputs["gauged_scalar_filter"],
                g3_sm_pati_salam_equality_set_report=forged,
            )
            self.assertFalse(
                report["g3_sm_pati_salam_equality_set_binding"]["certified"]
            )
            # G3 is decided by the SM track inputs, not by this binding.
            self.assertEqual(report["status"], self.report["status"])
            self.assertEqual(report["overall_state"], self.report["overall_state"])
            self.assertEqual(report["n_failed"], 0, report["audit_failures"])
            self.assertEqual(report["checks"], self.report["checks"])
            self.assertEqual(
                {name: row["status"] for name, row in report["gates"].items()},
                {name: row["status"] for name, row in self.report["gates"].items()},
            )
            self.assertEqual(
                report["closure_waves"][3], self.report["closure_waves"][3]
            )

    def test_missing_sm_track_input_reopens_g3_fail_closed(self):
        committed_inputs = sm_track.load_inputs()
        self.assertEqual(set(committed_inputs), set(sm_track.INPUT_FILES))
        for key, file_name in sm_track.INPUT_FILES.items():
            sm_inputs = copy.deepcopy(committed_inputs)
            sm_inputs[key] = {}
            report = self._build_with_sm_track_inputs(sm_inputs)
            track = report["g3_sm_target_track"]
            statuses = {name: row["status"] for name, row in report["gates"].items()}
            self.assertEqual(report["n_failed"], 0, (key, report["audit_failures"]))
            self.assertEqual(report["overall_state"], mod.STATUS_OPEN, key)
            self.assertEqual(report["status"], OPEN_G3_STATUS, key)
            self.assertEqual(
                report["scientific_blockers"],
                list(sm_track.FAIL_CLOSED_BLOCKERS),
                key,
            )
            self.assertIs(track["closed"], False, key)
            self.assertIn(file_name, track["missing_inputs"], key)
            self.assertEqual(statuses["G3"], mod.STATUS_OPEN, key)
            self.assertEqual(statuses["G4"], mod.STATUS_BLOCKED, key)
            self.assertEqual(
                statuses["G5"],
                mod.STATUS_CLOSED
                if track["g5_bfb_binding"]["certified"] is True
                else mod.STATUS_OPEN,
                key,
            )
            if key in {"candidate", "exact_hessian"}:
                # Both BFB halves (candidate certificate, quadratic-eps lemma)
                # are required, so G5 also reopens fail-closed.
                self.assertEqual(statuses["G5"], mod.STATUS_OPEN, key)
                self.assertEqual(
                    report["gates"]["G5"]["authoritative_closed_scope"], [], key
                )
            for name in ("G6", "G7", "G8"):
                self.assertEqual(statuses[name], mod.STATUS_BLOCKED, (key, name))
            g3 = report["gates"]["G3"]
            self.assertIsNone(g3["closing_track"], key)
            self.assertIsNone(g3["closure_scope"], key)
            self.assertEqual(g3["authoritative_closed_scope"], [], key)
            self.assertEqual(g3["unsatisfied_dependencies"], [], key)
            self.assertEqual(report["gates"]["G4"]["unsatisfied_dependencies"], ["G3"])
            self.assertIs(
                report["feasibility"]["gauged_G3_sm_pati_salam_track_closed"],
                False,
            )
            for name in (
                "only_sm_track_G3_and_bound_G5_close_among_G3_G8",
                "g3_sm_track_is_the_only_closure_route",
                "g5_closed_only_on_the_bound_pati_salam_vector",
                "gate_frontier_matches_contract_state",
            ):
                self.assertIs(report["checks"][name], True, (key, name))
            wave3 = report["closure_waves"][3]
            self.assertEqual(
                wave3["status"],
                f"G3_OPEN__G4_BLOCKED__G5_{statuses['G5']}",
                key,
            )
            self.assertEqual(
                wave3["deliverable"],
                "G3 is OPEN: the SM Pati-Salam track (g3_sm_target_track_v20), "
                "its only closure route, is not certified (blockers: "
                + ", ".join(track["blockers"])
                + "). "
                + sm_track.CAVEAT_ROUTING_SENTENCE
                + " "
                + mod.CHIRAL_WAVE3_TAIL,
            )
            self.assertNotIn(sm_track.CLOSURE_SCOPE, wave3["deliverable"])
            self.assertEqual(
                [(wave["wave"], wave["status"]) for wave in report["closure_waves"][4:]],
                [
                    (4, "BLOCKED_ON_G3_G4" + ("" if statuses["G5"] == mod.STATUS_CLOSED else "_G5")),
                    (5, "BLOCKED_ON_G6"),
                    (6, "BLOCKED_ON_G3_G6_G7"),
                ],
                key,
            )
            self.assertIn(
                "G3 is OPEN: the SM Pati-Salam track, its only closure route, "
                "is not certified (blockers: ",
                report["verdict"],
            )
            self.assertIn(
                "). G5 is " + statuses["G5"] + "; G4 and G6-G8 remain "
                "dependency-blocked. " + sm_track.CAVEAT_ROUTING_SENTENCE,
                report["verdict"],
            )
            self.assertNotIn(sm_track.CLOSURE_SCOPE, report["verdict"])

    def test_forged_decisive_statement_reopens_g3_but_keeps_g5_closed(self):
        sm_inputs = copy.deepcopy(sm_track.load_inputs())
        acceptance = sm_inputs["exact_hessian"]["eps_family"]["final_acceptance_test"]
        acceptance["required_statement"] = acceptance["required_statement"].replace(
            "V_PS,eps", "V_beta"
        )
        report = self._build_with_sm_track_inputs(sm_inputs)
        statuses = {name: row["status"] for name, row in report["gates"].items()}
        self.assertEqual(report["n_failed"], 0, report["audit_failures"])
        self.assertEqual(report["status"], OPEN_G3_STATUS)
        self.assertEqual(statuses["G3"], mod.STATUS_OPEN)
        self.assertEqual(statuses["G4"], mod.STATUS_BLOCKED)
        self.assertEqual(statuses["G5"], mod.STATUS_CLOSED)
        self.assertEqual(report["summary"]["closed"], ["G1", "G2", "G5"])
        self.assertEqual(report["summary"]["open"], ["G3"])
        track = report["g3_sm_target_track"]
        self.assertIs(track["closed"], False)
        self.assertIn("sm_decisive_theorem_string_bound", track["blockers"])
        self.assertIs(track["g5_bfb_binding"]["certified"], True)
        self.assertEqual(
            report["gates"]["G5"]["authoritative_closed_scope"],
            [sm_track.G5_LEDGER_CLOSED_SCOPE],
        )
        self.assertEqual(
            report["scientific_blockers"], list(sm_track.FAIL_CLOSED_BLOCKERS)
        )
        self.assertEqual(
            report["closure_waves"][3]["status"], "G3_OPEN__G4_BLOCKED__G5_CLOSED"
        )
        self.assertIn("sm_decisive_theorem_string_bound", report["verdict"])
        self.assertIn("). G5 is CLOSED; G4 and G6-G8 remain", report["verdict"])

    def test_blocked_contract_keeps_every_gate_blocked_and_the_track_open(self):
        inputs = self.report["model_contract_reports"]
        blocked_x = mod.exact_x.build_report(
            model_text=mod.exact_x.MODEL.read_text(encoding="utf-8")
        )
        self.assertFalse(blocked_x["contract_consistent"])
        report = mod._build_report_from_inputs(
            x_report=blocked_x,
            g1_report=inputs["gauged_G1_character_census"],
            g2_report=inputs["gauged_G2_derivative_audit"],
            filter_report=inputs["gauged_scalar_filter"],
        )
        self.assertEqual(report["n_failed"], 0, report["audit_failures"])
        self.assertEqual(report["overall_state"], mod.STATUS_BLOCKED)
        self.assertEqual(
            {row["status"] for row in report["gates"].values()},
            {mod.STATUS_BLOCKED},
        )
        track = report["g3_sm_target_track"]
        self.assertIs(track["closed"], False)
        for name in (
            "authoritative_external_model_contract_executed",
            "G1_promoted_closed",
            "G2_promoted_closed",
        ):
            self.assertIs(track["release_prerequisites"][name], False, name)
            self.assertIn(name, track["blockers"])
        self.assertIsNone(report["gates"]["G3"]["closing_track"])
        self.assertEqual(
            report["scientific_blockers"][-2:], list(sm_track.FAIL_CLOSED_BLOCKERS)
        )
        self.assertEqual(report["closure_waves"][3]["status"], "BLOCKED_ON_G2")
        self.assertEqual(
            report["closure_waves"][4]["status"], "BLOCKED_ON_G3_G4_G5"
        )
        self.assertEqual(
            report["closure_waves"][6]["status"], "BLOCKED_ON_G3_G6_G7"
        )
        self.assertIs(
            report["feasibility"]["gauged_G3_sm_pati_salam_track_closed"], False
        )

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
        self.assertEqual(feasibility["current_authoritative_closed_gates"], 4)
        self.assertIs(feasibility["gauged_G3_sm_pati_salam_track_closed"], True)
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
        self.assertEqual(report["status"], CLOSED_G3_STATUS)
        self.assertEqual(report["summary"]["closed"], ["G1", "G2", "G3", "G5"])
        self.assertEqual(report["summary"]["open"], ["G4"])
        self.assertEqual(
            {name: row["status"] for name, row in report["gates"].items()},
            SM_TRACK_CLOSED_STATUSES,
        )
        self.assertEqual(report["gates"]["G4"]["unsatisfied_dependencies"], [])
        self.assertEqual(report["gates"]["G7"]["unsatisfied_dependencies"], ["G6"])
        self.assertNotIn(mod.CONTRACT_BLOCKER, report["scientific_blockers"])
        self.assertEqual(
            report["scientific_blockers"], list(sm_track.DOWNSTREAM_BLOCKERS)
        )

    def test_unbound_boolean_cannot_promote_model_contract(self):
        inputs = self.report["model_contract_reports"]
        # Start from the shipped model audited without its SARAH attestation.
        forged = copy.deepcopy(
            mod.exact_x.build_report(
                model_text=mod.exact_x.MODEL.read_text(encoding="utf-8")
            )
        )
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

    def test_rank1_su4_infrastructure_mutations_fail_closed(self):
        inputs = self.report["model_contract_reports"]
        stabilizer = inputs["gauged_G3_rank1_SU4_stabilizer_infrastructure"]
        intertwiners = inputs[
            "gauged_G3_rank1_SU4_Phi210_intertwiner_infrastructure"
        ]
        mutations = []

        forged_stabilizer = copy.deepcopy(stabilizer)
        forged_stabilizer["scope"]["G3_closed"] = True
        mutations.append((forged_stabilizer, copy.deepcopy(intertwiners)))

        forged_intertwiners = copy.deepcopy(intertwiners)
        forged_intertwiners["scope"]["Schur_SOS_SDP_constructed"] = True
        mutations.append((copy.deepcopy(stabilizer), forged_intertwiners))

        forged_intertwiners = copy.deepcopy(intertwiners)
        forged_intertwiners["companion_stabilizer_provenance"][
            "all_required_provenance_exact"
        ] = False
        mutations.append((copy.deepcopy(stabilizer), forged_intertwiners))

        forged_intertwiners = copy.deepcopy(intertwiners)
        forged_intertwiners["intertwiner"]["intertwining_count"] = 14
        mutations.append((copy.deepcopy(stabilizer), forged_intertwiners))

        for forged_stabilizer, forged_intertwiners in mutations:
            with self.subTest(
                stabilizer_G3=forged_stabilizer["scope"]["G3_closed"],
                sdp=forged_intertwiners["scope"]["Schur_SOS_SDP_constructed"],
                provenance=forged_intertwiners[
                    "companion_stabilizer_provenance"
                ]["all_required_provenance_exact"],
                count=forged_intertwiners["intertwiner"]["intertwining_count"],
            ):
                report = mod._build_report_from_inputs(
                    x_report=inputs["exact_X"],
                    g1_report=inputs["gauged_G1_character_census"],
                    g2_report=inputs["gauged_G2_derivative_audit"],
                    filter_report=inputs["gauged_scalar_filter"],
                    g3_rank1_su4_stabilizer_report=forged_stabilizer,
                    g3_rank1_su4_phi210_intertwiners_report=forged_intertwiners,
                )
                frontier = report["gauged_u1x_g3_constructive_frontier"]
                self.assertEqual(report["overall_state"], "EXECUTION_FAIL")
                self.assertFalse(frontier["integrity_pass"])
                self.assertFalse(
                    frontier[
                        "rank1_SU4_Phi210_intertwiner_infrastructure_exact"
                    ]
                )
                self.assertIn(
                    "gauged_G3_rank1_SU4_infrastructure_is_exact_and_fail_closed",
                    report["audit_failures"],
                )

    def test_rank1_su4_predicates_reject_schema_and_stale_aggregates(self):
        inputs = self.report["model_contract_reports"]
        stabilizer = inputs["gauged_G3_rank1_SU4_stabilizer_infrastructure"]
        intertwiners = inputs[
            "gauged_G3_rank1_SU4_Phi210_intertwiner_infrastructure"
        ]

        stabilizer_mutations = (
            lambda value: value["checks"].__setitem__(
                "unexpected_new_critical_check", False
            ),
            lambda value: value["joint_stabilizer_tangent"].__setitem__(
                "displayed_kernel_residual_max_abs", 1
            ),
            lambda value: value["joint_stabilizer_tangent"].__setitem__(
                "joint_tangent_rank_mod_prime", 29
            ),
            lambda value: value["Phi210_action"].__setitem__(
                "skew_transpose_max_abs_residual", 1
            ),
            lambda value: value["Lie_algebra"].__setitem__(
                "Jacobi_max_abs_residual", 1
            ),
            lambda value: value["generator_basis"].__setitem__(
                "coefficient_rank_mod_prime", 14
            ),
            lambda value: value["generator_basis"].__setitem__("prime", 4),
            lambda value: value["joint_stabilizer_tangent"].__setitem__(
                "prime", 4
            ),
            lambda value: value["Phi210_action"].__setitem__("prime", 4),
            lambda value: value["generator_basis"]["ordered_labels"].__setitem__(
                0, "WRONG"
            ),
            lambda value: value["Phi210_action"]["ordered_labels"].__setitem__(
                0, "WRONG"
            ),
        )
        for mutate in stabilizer_mutations:
            forged = copy.deepcopy(stabilizer)
            mutate(forged)
            self.assertFalse(
                mod._rank1_su4_stabilizer_infrastructure_exact(forged),
                mutate.__code__.co_firstlineno,
            )

        intertwiner_mutations = (
            lambda value: value["checks"].__setitem__(
                "unexpected_new_critical_check", False
            ),
            lambda value: value["companion_stabilizer_provenance"].__setitem__(
                "module", "quarantined_or_wrong.py"
            ),
            lambda value: value["integral_C8"].__setitem__(
                "minimal_polynomial_annihilates_exact", False
            ),
            lambda value: value["integral_C8"].__setitem__(
                "modular_nullities_sum", 0
            ),
            lambda value: value["integral_C8"].__setitem__("modular_prime", 4),
            lambda value: value["carriers"].__setitem__(
                "all_carrier_dimensions_eigenvalues_characters_exact", False
            ),
            lambda value: value["carriers"].__setitem__(
                "future_Schur_SDP_multiplicity_matrix_dimension", 45
            ),
            lambda value: value["intertwiner"]["intertwinings"][0].__setitem__(
                "generator", "WRONG"
            ),
        )
        for mutate in intertwiner_mutations:
            forged = copy.deepcopy(intertwiners)
            mutate(forged)
            self.assertFalse(
                mod._rank1_su4_phi210_intertwiners_exact(forged, stabilizer),
                mutate.__code__.co_firstlineno,
            )

        forged_stabilizer = copy.deepcopy(stabilizer)
        forged_intertwiners = copy.deepcopy(intertwiners)
        forged_stabilizer["joint_stabilizer_tangent"]["fixed_endpoint"][
            "H"
        ] = "wrong_H"
        forged_intertwiners["companion_stabilizer_provenance"]["fixed_endpoint"][
            "H"
        ] = "wrong_H"
        self.assertFalse(
            mod._rank1_su4_stabilizer_infrastructure_exact(forged_stabilizer)
        )
        self.assertFalse(
            mod._rank1_su4_phi210_intertwiners_exact(
                forged_intertwiners,
                forged_stabilizer,
            )
        )

    def test_rank1_su4_stage2_predicates_reject_adversarial_mutations(self):
        inputs = self.report["model_contract_reports"]
        stabilizer = inputs["gauged_G3_rank1_SU4_stabilizer_infrastructure"]
        intertwiners = inputs[
            "gauged_G3_rank1_SU4_Phi210_intertwiner_infrastructure"
        ]
        aligned = inputs["gauged_G3_rank1_SU4_aligned_carrier_infrastructure"]
        quadratic = inputs["gauged_G3_rank1_SU4_Phi210_quadratic_basis"]

        aligned_mutations = (
            lambda value: value["scope"].__setitem__("G3_closed", True),
            lambda value: value["checks"].__setitem__(
                "aligned_25_carrier_direct_sum_rank_210_exact", False
            ),
            lambda value: value["alignment"].__setitem__(
                "concatenated_aligned_basis_rank_mod_prime", 209
            ),
            lambda value: value["alignment"]["carriers"][0].__setitem__(
                "physical_conjugation_embedding_exact", False
            ),
            lambda value: value["upstream_provenance"].__setitem__(
                "upstream_report_sha256", "0" * 64
            ),
            lambda value: value["upstream_provenance"][
                "source_contract"
            ].__setitem__("upstream_module_sha256", "0" * 64),
            lambda value: (
                value["alignment"].__setitem__("carrier_count", 24),
                value["alignment_provenance"].__setitem__(
                    "certificate_sha256",
                    mod._canonical_json_sha256(value["alignment"]),
                ),
                value["alignment_provenance"].__setitem__(
                    "expected_live_certificate_sha256",
                    mod._canonical_json_sha256(value["alignment"]),
                ),
            ),
        )
        for mutate in aligned_mutations:
            forged = copy.deepcopy(aligned)
            mutate(forged)
            self.assertFalse(
                mod._rank1_su4_aligned_carriers_exact(
                    forged, intertwiners, stabilizer
                ),
                mutate.__code__.co_firstlineno,
            )

        quadratic_mutations = (
            lambda value: value["scope"].__setitem__(
                "augmented_homogeneous_Schur_SOS_SDP_constructed", True
            ),
            lambda value: value["constraint_system"].__setitem__(
                "reduced_constraint_shape", [5951, 551]
            ),
            lambda value: value["constraint_system"].__setitem__(
                "exact_rational_rank", 505
            ),
            lambda value: value["quadratic_basis"].__setitem__(
                "matrix_count", 44
            ),
            lambda value: value["quadratic_basis"].__setitem__(
                "all_45_commute_with_all_15_live_Phi210_generators_exact", False
            ),
            lambda value: value["construction_metadata"][
                "selected_candidate_indices"
            ].__setitem__(0, 72),
            lambda value: value["reconstruction_api"].__setitem__(
                "basis_accessor", "forged()"
            ),
            lambda value: value["source_provenance"].__setitem__(
                "intertwiner_module_sha256", "0" * 64
            ),
            lambda value: value["scope"].__setitem__(
                "arbitrary_real_Phi_lower_bound_proved", True
            ),
            lambda value: value["scope"].__setitem__(
                "arbitrary_rank1_Phi_proved", True
            ),
            lambda value: value["scope"].__setitem__("G3_closed", True),
            lambda value: value["scope"].__setitem__(
                "whole_model_validated", True
            ),
            lambda value: value["scope"].__setitem__(
                "whole_model_excluded", True
            ),
        )
        for mutate in quadratic_mutations:
            forged = copy.deepcopy(quadratic)
            mutate(forged)
            self.assertFalse(
                mod._rank1_su4_phi210_quadratic_basis_exact(
                    forged, stabilizer, intertwiners, aligned
                ),
                mutate.__code__.co_firstlineno,
            )

        forged = copy.deepcopy(quadratic)
        forged["scope"]["G3_closed"] = True
        report = mod._build_report_from_inputs(
            x_report=inputs["exact_X"],
            g1_report=inputs["gauged_G1_character_census"],
            g2_report=inputs["gauged_G2_derivative_audit"],
            filter_report=inputs["gauged_scalar_filter"],
            g3_rank1_su4_stabilizer_report=stabilizer,
            g3_rank1_su4_phi210_intertwiners_report=intertwiners,
            g3_rank1_su4_aligned_carriers_report=aligned,
            g3_rank1_su4_phi210_quadratic_basis_report=forged,
        )
        self.assertEqual(report["overall_state"], "EXECUTION_FAIL")
        self.assertFalse(
            report["gauged_u1x_g3_constructive_frontier"][
                "rank1_SU4_Phi210_quadratic_basis_exact"
            ]
        )
        self.assertFalse(
            report["gauged_u1x_g3_constructive_frontier"][
                "rank1_SU4_augmented_quartic_map_exact"
            ]
        )

    def test_rank1_su4_augmented_census_rejects_every_physical_overclaim(self):
        inputs = self.report["model_contract_reports"]
        stabilizer = inputs["gauged_G3_rank1_SU4_stabilizer_infrastructure"]
        intertwiners = inputs[
            "gauged_G3_rank1_SU4_Phi210_intertwiner_infrastructure"
        ]
        aligned = inputs["gauged_G3_rank1_SU4_aligned_carrier_infrastructure"]
        quadratic = inputs["gauged_G3_rank1_SU4_Phi210_quadratic_basis"]
        census = inputs["gauged_G3_rank1_SU4_augmented_SOS_census"]

        mutations = [
            lambda value: value.__setitem__("status", "FORGED"),
            lambda value: value.__setitem__("n_failed", 1),
            lambda value: value["checks"].__setitem__("unexpected_check", True),
            lambda value: value["checks"].__setitem__(
                "universal_GL211_equivariant_section_exact", False
            ),
            lambda value: value["source_provenance"].__setitem__(
                "aligned_source_sha256", "0" * 64
            ),
            lambda value: value["source_provenance"].__setitem__(
                "quadratic_report_sha256", "0" * 64
            ),
            lambda value: value["augmented_representation"].__setitem__(
                "complex_isotypic_type_count", 34
            ),
            lambda value: value["augmented_representation"].__setitem__(
                "Schur_real_parameter_count", 19_593
            ),
            lambda value: value["invariant_quartic_target"].__setitem__(
                "invariant_equation_count", 6_584
            ),
            lambda value: value["abstract_coefficient_map_census"].__setitem__(
                "abstract_total_rank_exact", 6_584
            ),
        ]
        false_scope = (
            "all_35_isotypic_type_maps_spanning_824_irreducible_copies_constructed",
            "ordered_invariant_cubic_basis_constructed",
            "ordered_invariant_quartic_basis_constructed",
            "Schur_coordinate_6585_by_19594_coefficient_matrix_constructed",
            "physical_G3_gap_target_vector_constructed",
            "physical_G3_gap_cubic_zero_RHS_certified",
            "augmented_Schur_SOS_SDP_constructed",
            "augmented_Schur_SOS_SDP_feasibility_certified",
            "augmented_Schur_SOS_SDP_infeasibility_certified",
            "arbitrary_real_Phi_lower_bound_proved",
            "arbitrary_rank1_Phi_proved",
            "G3_closed",
            "whole_model_validated",
            "whole_model_excluded",
        )
        mutations.extend(
            lambda value, key=key: value["scope"].__setitem__(key, True)
            for key in false_scope
        )
        for mutate in mutations:
            forged = copy.deepcopy(census)
            mutate(forged)
            self.assertFalse(
                mod._rank1_su4_augmented_sos_census_exact(
                    forged, stabilizer, intertwiners, aligned, quadratic
                )
            )

        forged = copy.deepcopy(census)
        forged["scope"]["G3_closed"] = True
        report = mod._build_report_from_inputs(
            x_report=inputs["exact_X"],
            g1_report=inputs["gauged_G1_character_census"],
            g2_report=inputs["gauged_G2_derivative_audit"],
            filter_report=inputs["gauged_scalar_filter"],
            g3_rank1_su4_stabilizer_report=stabilizer,
            g3_rank1_su4_phi210_intertwiners_report=intertwiners,
            g3_rank1_su4_aligned_carriers_report=aligned,
            g3_rank1_su4_phi210_quadratic_basis_report=quadratic,
            g3_rank1_su4_augmented_sos_census_report=forged,
        )
        self.assertEqual(report["overall_state"], "EXECUTION_FAIL")
        self.assertFalse(
            report["gauged_u1x_g3_constructive_frontier"][
                "rank1_SU4_augmented_SOS_census_exact"
            ]
        )
        self.assertFalse(
            report["gauged_u1x_g3_constructive_frontier"][
                "rank1_SU4_augmented_quartic_map_exact"
            ]
        )

    def test_rank1_su4_augmented_cubic_map_is_canonical_and_fail_closed(self):
        inputs = self.report["model_contract_reports"]
        stabilizer = inputs["gauged_G3_rank1_SU4_stabilizer_infrastructure"]
        intertwiners = inputs[
            "gauged_G3_rank1_SU4_Phi210_intertwiner_infrastructure"
        ]
        aligned = inputs["gauged_G3_rank1_SU4_aligned_carrier_infrastructure"]
        quadratic = inputs["gauged_G3_rank1_SU4_Phi210_quadratic_basis"]
        census = inputs["gauged_G3_rank1_SU4_augmented_SOS_census"]
        cubic = inputs["gauged_G3_rank1_SU4_augmented_SOS_cubic_map"]

        self.assertTrue(
            mod._rank1_su4_augmented_sos_cubic_map_exact(
                cubic, stabilizer, intertwiners, aligned, quadratic, census
            )
        )
        mutations = [
            lambda value: value.__setitem__("status", "FORGED"),
            lambda value: value.__setitem__("n_failed", 1),
            lambda value: value["checks"].__setitem__("unexpected_check", True),
            lambda value: value["source_provenance"].__setitem__(
                "census_report_sha256", "0" * 64
            ),
            lambda value: value["source_provenance"].__setitem__(
                "quadratic_basis_sha256", "0" * 64
            ),
            lambda value: value["source_provenance"].__setitem__(
                "live_target_invariant_grade_counts", [1, 4, 45, 477, 6_058]
            ),
            lambda value: value["Sym2_target_carriers"].__setitem__(
                "total_complex_carrier_copy_count", 539
            ),
            lambda value: value["Sym2_target_carriers"]["families"][0].__setitem__(
                "nullity", 44
            ),
            lambda value: value["contragredient_pairings"].__setitem__(
                "all_15_compact_tensor_equations_exact", False
            ),
            lambda value: value["physical_cubic_domain"].__setitem__(
                "physical_basis_count", 1_413
            ),
            lambda value: value["physical_cubic_domain"][
                "all_22_augmented_block_rows"
            ][0].__setitem__("constructed_physical_basis_variable_count", 179),
            lambda value: value["cubic_coordinate_map"].__setitem__(
                "coordinate_map_sha256", "f" * 64
            ),
            lambda value: value["cubic_coordinate_map"].__setitem__(
                "coordinate_map_shape", [477, 1_414]
            ),
            lambda value: value["cubic_coordinate_map"].__setitem__(
                "exact_rank", 477
            ),
            lambda value: value["cubic_coordinate_map"].__setitem__(
                "exact_kernel_dimension", 937
            ),
            lambda value: value["cubic_coordinate_map"].__setitem__(
                "selected_minor_determinant_nonzero_mod_prime", False
            ),
            lambda value: value["cubic_coordinate_map"].__setitem__(
                "abstract_zero_interface_placeholder_nnz", 1
            ),
            lambda value: value["cubic_coordinate_map"].__setitem__(
                "abstract_zero_placeholder_is_not_a_physical_G3_target", False
            ),
            lambda value: value["exact_arithmetic_safety"].__setitem__(
                "proof_grade", False
            ),
        ]
        true_scope = (
            "H_fixed_to_h_minus",
            "Sigma_fixed_to_q_over_4",
            "rank1_endpoint_SU4_stabilizer_used",
            "all_1414_real_structure_fixed_cubic_Schur_cross_variables_constructed",
            "explicit_478_by_1414_cubic_coordinate_map_constructed",
            "cubic_map_rank_478_and_kernel_dimension_936_exact",
            "abstract_478_coordinate_zero_placeholder_available",
        )
        false_scope = (
            "degree_zero_coefficient_map_constructed",
            "degree_one_coefficient_map_constructed",
            "degree_two_coefficient_map_constructed",
            "degree_four_coefficient_map_constructed",
            "full_6585_by_19594_Schur_coordinate_matrix_constructed",
            "physical_G3_gap_target_vector_constructed",
            "physical_G3_gap_cubic_zero_RHS_certified",
            "augmented_Schur_SOS_SDP_constructed",
            "augmented_Schur_SOS_SDP_feasibility_certified",
            "augmented_Schur_SOS_SDP_infeasibility_certified",
            "arbitrary_real_Phi_lower_bound_proved",
            "arbitrary_rank1_Phi_proved",
            "G3_closed",
            "whole_model_validated",
            "whole_model_excluded",
        )
        mutations.extend(
            lambda value, key=key: value["scope"].__setitem__(key, False)
            for key in true_scope
        )
        mutations.extend(
            lambda value, key=key: value["scope"].__setitem__(key, True)
            for key in false_scope
        )
        for field in (
            "physical_G3_gap_target_vector_constructed",
            "physical_G3_gap_cubic_zero_RHS_certified",
        ):
            mutations.append(
                lambda value, field=field: value["cubic_coordinate_map"].__setitem__(
                    field, True
                )
            )
        for field in (
            "census_physical_G3_gap_target_vector_constructed",
            "census_physical_G3_gap_cubic_zero_RHS_certified",
        ):
            mutations.append(
                lambda value, field=field: value["source_provenance"].__setitem__(
                    field, True
                )
            )
        for mutate in mutations:
            forged = copy.deepcopy(cubic)
            mutate(forged)
            self.assertFalse(
                mod._rank1_su4_augmented_sos_cubic_map_exact(
                    forged, stabilizer, intertwiners, aligned, quadratic, census
                ),
                mutate.__code__.co_firstlineno,
            )

        forged = copy.deepcopy(cubic)
        forged["cubic_coordinate_map"][
            "physical_G3_gap_target_vector_constructed"
        ] = True
        report = mod._build_report_from_inputs(
            x_report=inputs["exact_X"],
            g1_report=inputs["gauged_G1_character_census"],
            g2_report=inputs["gauged_G2_derivative_audit"],
            filter_report=inputs["gauged_scalar_filter"],
            g3_rank1_su4_stabilizer_report=stabilizer,
            g3_rank1_su4_phi210_intertwiners_report=intertwiners,
            g3_rank1_su4_aligned_carriers_report=aligned,
            g3_rank1_su4_phi210_quadratic_basis_report=quadratic,
            g3_rank1_su4_augmented_sos_census_report=census,
            g3_rank1_su4_augmented_sos_cubic_map_report=forged,
        )
        frontier = report["gauged_u1x_g3_constructive_frontier"]
        self.assertEqual(report["overall_state"], "EXECUTION_FAIL")
        self.assertFalse(frontier["integrity_pass"])
        self.assertFalse(frontier["rank1_SU4_augmented_cubic_map_exact"])
        self.assertFalse(frontier["rank1_SU4_augmented_quartic_map_exact"])
        self.assertFalse(
            report["checks"][
                "gauged_G3_rank1_SU4_infrastructure_is_exact_and_fail_closed"
            ]
        )

    def test_rank1_su4_augmented_quartic_map_is_canonical_and_fail_closed(self):
        inputs = self.report["model_contract_reports"]
        census = inputs["gauged_G3_rank1_SU4_augmented_SOS_census"]
        cubic = inputs["gauged_G3_rank1_SU4_augmented_SOS_cubic_map"]
        quartic = inputs["gauged_G3_rank1_SU4_augmented_SOS_quartic_map"]

        self.assertTrue(
            mod._rank1_su4_augmented_sos_quartic_map_exact(
                quartic, census, cubic
            )
        )
        mutations = (
            lambda value: value.__setitem__("status", "FORGED"),
            lambda value: value["scope"].__setitem__("G3_closed", True),
            lambda value: value["scope"].__setitem__(
                "physical_quartic_target_constructed", True
            ),
            lambda value: value["scope"].__setitem__(
                "standard_PSD_congruences_for_real_type_fixed_bases_constructed",
                True,
            ),
            lambda value: value["scope"].__setitem__(
                "semidefinite_feasibility_solved", True
            ),
            lambda value: value["dimensions"].__setitem__(
                "quartic_kernel", 12_029
            ),
            lambda value: value["provenance"].__setitem__(
                "cubic_source_sha256_canonical_LF", "0" * 64
            ),
            lambda value: value["carrier_certificate"].__setitem__(
                "irreducible_copy_count", 797
            ),
            lambda value: value["pairing_certificate"].__setitem__(
                "real_block_count", 21
            ),
            lambda value: value["realification_certificate"].__setitem__(
                "domain_dimension", 18_084
            ),
            lambda value: value["coefficient_map_certificate"].__setitem__(
                "shape", [6_056, 18_085]
            ),
            lambda value: value["coefficient_map_certificate"].__setitem__(
                "nnz", 115_640
            ),
            lambda value: value["coefficient_map_certificate"].__setitem__(
                "rank_over_Q_exact", 6_056
            ),
            lambda value: value["coefficient_map_certificate"].__setitem__(
                "kernel_dimension_over_Q_exact", 12_029
            ),
            lambda value: value["coefficient_map_certificate"].__setitem__(
                "coordinate_map_sha256", "f" * 64
            ),
            lambda value: value["coefficient_map_certificate"].__setitem__(
                "unexpected_schema_key", True
            ),
        )
        for mutate in mutations:
            forged = copy.deepcopy(quartic)
            mutate(forged)
            self.assertFalse(
                mod._rank1_su4_augmented_sos_quartic_map_exact(
                    forged, census, cubic
                ),
                mutate.__code__.co_firstlineno,
            )

        forged = copy.deepcopy(quartic)
        forged["scope"]["semidefinite_feasibility_solved"] = True
        report = mod._build_report_from_inputs(
            x_report=inputs["exact_X"],
            g1_report=inputs["gauged_G1_character_census"],
            g2_report=inputs["gauged_G2_derivative_audit"],
            filter_report=inputs["gauged_scalar_filter"],
            g3_rank1_su4_augmented_sos_quartic_map_report=forged,
        )
        frontier = report["gauged_u1x_g3_constructive_frontier"]
        self.assertEqual(report["overall_state"], "EXECUTION_FAIL")
        self.assertFalse(frontier["integrity_pass"])
        self.assertFalse(frontier["rank1_SU4_augmented_quartic_map_exact"])
        self.assertFalse(
            report["checks"][
                "gauged_G3_rank1_SU4_infrastructure_is_exact_and_fail_closed"
            ]
        )

    def test_rank1_su4_corrected_endpoint_supersedes_v20_target_fail_closed(self):
        inputs = self.report["model_contract_reports"]
        census = inputs["gauged_G3_rank1_SU4_augmented_SOS_census"]
        cubic = inputs["gauged_G3_rank1_SU4_augmented_SOS_cubic_map"]
        quartic = inputs["gauged_G3_rank1_SU4_augmented_SOS_quartic_map"]
        psd_target = inputs[
            "gauged_G3_rank1_SU4_legacy_v20_PSD_routes_and_rejected_target"
        ]
        corrected_publication = inputs[
            "gauged_G3_rank1_SU4_corrected_fixed_endpoint_publication_v21"
        ]

        self.assertFalse(
            mod._rank1_su4_augmented_sos_psd_target_exact(
                psd_target, census, cubic, quartic
            )
        )
        self.assertTrue(
            mod._rank1_su4_augmented_sos_psd_routes_and_stale_payload_well_formed(
                psd_target, census, cubic, quartic
            )
        )
        self.assertTrue(
            mod.corrected_rank1.corrected_fixed_endpoint_theorem_exact(
                corrected_publication
            )
        )
        verdict = self.report["verdict"]
        self.assertIn("legacy v20 assembled physical target is rejected", verdict)
        self.assertIn("corrected 6585x19594 standard positive-Gram map", verdict)
        self.assertIn("strict 22-block/824-pivot primal", verdict)
        self.assertIn("every real Phi210", verdict)
        self.assertIn(
            "Global Sigma and general/full H remain open for that non-SM point (the exact 448/38 full Hessian is certified separately)",
            verdict,
        )
        self.assertNotIn("general/full H, and G3 remain open", verdict)
        self.assertNotIn("only a four-real-dimensional Phi sub-slice", verdict)
        self.assertNotIn("arbitrary-Phi bound remain open", verdict)
        mutations = (
            lambda value: value["scope"].__setitem__("G3_closed", True),
            lambda value: value["scope"].__setitem__(
                "semidefinite_feasibility_solved", True
            ),
            lambda value: value["standard_PSD_coordinate_routes"].__setitem__(
                "standard_total_parameter_count", 19_593
            ),
            lambda value: value["physical_target"]["full_graded_chart"].__setitem__(
                "row_count", 6_584
            ),
        )
        for mutate in mutations:
            forged = copy.deepcopy(psd_target)
            mutate(forged)
            self.assertFalse(
                mod._rank1_su4_augmented_sos_psd_routes_and_stale_payload_well_formed(
                    forged, census, cubic, quartic
                ),
                mutate.__code__.co_firstlineno,
            )

        forged = copy.deepcopy(psd_target)
        forged["scope"]["G3_closed"] = True
        report = mod._build_report_from_inputs(
            x_report=inputs["exact_X"],
            g1_report=inputs["gauged_G1_character_census"],
            g2_report=inputs["gauged_G2_derivative_audit"],
            filter_report=inputs["gauged_scalar_filter"],
            g3_rank1_su4_augmented_sos_psd_target_report=forged,
        )
        frontier = report["gauged_u1x_g3_constructive_frontier"]
        self.assertEqual(report["overall_state"], "EXECUTION_FAIL")
        self.assertFalse(frontier["integrity_pass"])
        self.assertFalse(
            frontier[
                "rank1_SU4_legacy_v20_PSD_routes_and_stale_payload_well_formed"
            ]
        )
        self.assertFalse(
            report["checks"][
                "gauged_G3_rank1_SU4_infrastructure_is_exact_and_fail_closed"
            ]
        )


if __name__ == "__main__":
    unittest.main()
