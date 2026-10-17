#!/usr/bin/env python3
"""Regression tests for the contract-aware G1-G8 gate ledger.

G3 closes only through the SM Pati-Salam track, G5 only on its bound coupling
vector and G4 only through the pure binding g4_sm_closure_binding_v20 on the
committed exact G4 certificate (at the G3 witness, tree level).  With G3, G4
and G5 CLOSED, G6 is OPEN (never CLOSED here: the G6 tree spectrum at
mu = M_GUT, the G6 remnant RG no-go on the SOS witness family and the G8 Route C
flavour no-go are evidence only) and G7/G8 stay BLOCKED.  Any missing, forged or
mismatched G4 certificate reopens G4 fail-closed.  The G1 truncation scope
(decision U5), the G7 BM-DA1 benchmark evidence, the G8 structural obstruction
and the separate program verdict (decision U1) are bound fail-closed to their
committed JSONs and never change a gate, a check or the ledger status.
"""
from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

import g1_g8_gate_ledger_v20 as mod
import g3_sm_target_track_v20 as sm_track
import g4_sm_closure_binding_v20 as g4_closure

CLOSED_G4_STATUS = (
    "G1_G8_LEDGER_AUDIT_COMPLETE__MODEL_CONTRACT_CONSISTENT__"
    "G1_G2_G3_G4_G5_CLOSED__G6_OPEN"
)
G4_OPEN_STATUS = (
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
    "G4": mod.STATUS_CLOSED,
    "G5": mod.STATUS_CLOSED,
    "G6": mod.STATUS_OPEN,
    "G7": mod.STATUS_BLOCKED,
    "G8": mod.STATUS_BLOCKED,
}
G4_REOPENED_STATUSES = {
    **SM_TRACK_CLOSED_STATUSES,
    "G4": mod.STATUS_OPEN,
    "G6": mod.STATUS_BLOCKED,
}
RENAMED_G3_G5_CHECK = "only_sm_track_G3_certified_G4_and_bound_G5_close_among_G3_G8"
NEW_G4_CHECKS = (
    "g4_closed_only_on_the_certified_witness_binding",
    "g6_g8_certificates_are_evidence_only",
)
G6_SPECIFICATION = (
    "with G3, G4 and G5 CLOSED, emit the complete positive physical spectrum with "
    "SM provenance (eigenmasses, irreps, mixings and uncertainties) beyond tree level"
)
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

    def _build_with(self, **reports):
        inputs = self.report["model_contract_reports"]
        return mod._build_report_from_inputs(
            x_report=inputs["exact_X"],
            g1_report=inputs["gauged_G1_character_census"],
            g2_report=inputs["gauged_G2_derivative_audit"],
            filter_report=inputs["gauged_scalar_filter"],
            **reports,
        )

    def test_audit_succeeds_with_attested_contract_and_g3_closed_on_sm_track(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["audit_failures"])
        self.assertEqual(self.report["status"], CLOSED_G4_STATUS)
        self.assertEqual(self.report["overall_state"], mod.STATUS_OPEN)
        self.assertEqual(self.report["n_checks"], 45)
        self.assertIs(
            self.report["checks"]["program_verdict_and_scope_records_never_change_a_gate"], True
        )
        self.assertTrue(self.report["contract_consistent"])
        self.assertTrue(self.report["contract_evidence_complete"])
        self.assertNotIn(mod.CONTRACT_BLOCKER, self.report["scientific_blockers"])
        self.assertEqual(
            self.report["scientific_blockers"],
            list(g4_closure.DOWNSTREAM_BLOCKERS_AFTER_G4),
        )
        self.assertNotIn(
            "G4_SM_WITNESS_ZERO_MODES_AND_RANKS_34_35_UNCLASSIFIED",
            self.report["scientific_blockers"],
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
            RENAMED_G3_G5_CHECK,
            *NEW_G4_CHECKS,
            "g3_sm_track_is_the_only_closure_route",
            "chiral_H_diagnostic_track_cannot_close_G3",
            "g5_closed_only_on_the_bound_pati_salam_vector",
            "gate_frontier_matches_contract_state",
            "closed_gates_have_closed_dependencies",
            "open_gates_have_closed_dependencies",
        ):
            self.assertIs(self.report["checks"][name], True, name)
        self.assertNotIn(
            "only_certified_G5_closes_among_G3_G8", self.report["checks"]
        )
        self.assertNotIn(
            "only_sm_track_G3_and_bound_G5_close_among_G3_G8", self.report["checks"]
        )
        self.assertIs(
            self.report["feasibility"]["gauged_G3_sm_pati_salam_track_closed"],
            True,
        )
        self.assertIs(
            self.report["feasibility"]["gauged_G4_sm_witness_quotient_closed"],
            True,
        )

    def test_expected_gate_statuses_follow_the_sm_track_and_the_dag(self):
        blocked = {f"G{i}": mod.STATUS_BLOCKED for i in range(1, 9)}
        for g3_closed in (False, True):
            for g4_closed in (False, True):
                for g5_closed in (False, True):
                    flags = dict(
                        g3_closed=g3_closed, g5_closed=g5_closed, g4_closed=g4_closed
                    )
                    self.assertEqual(
                        mod._expected_gate_statuses(False, **flags), blocked
                    )
                    if g3_closed:
                        g4_status = mod.STATUS_CLOSED if g4_closed else mod.STATUS_OPEN
                    else:
                        g4_status = mod.STATUS_BLOCKED
                    self.assertEqual(
                        mod._expected_gate_statuses(True, **flags),
                        {
                            "G1": mod.STATUS_CLOSED,
                            "G2": mod.STATUS_CLOSED,
                            "G3": mod.STATUS_CLOSED if g3_closed else mod.STATUS_OPEN,
                            "G4": g4_status,
                            "G5": mod.STATUS_CLOSED if g5_closed else mod.STATUS_OPEN,
                            "G6": (
                                mod.STATUS_OPEN
                                if g3_closed and g4_closed and g5_closed
                                else mod.STATUS_BLOCKED
                            ),
                            "G7": mod.STATUS_BLOCKED,
                            "G8": mod.STATUS_BLOCKED,
                        },
                        flags,
                    )
        with self.assertRaises(TypeError):
            mod._expected_gate_statuses(True)  # the track inputs are required
        with self.assertRaises(TypeError):
            # g4_closed is required (keyword-only, no default).
            mod._expected_gate_statuses(True, g3_closed=True, g5_closed=True)
        with self.assertRaises(TypeError):
            mod._expected_gate_statuses(True, True, True, True)

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

    def test_attested_contract_closes_g1_to_g5_and_opens_g6(self):
        gates = self.report["gates"]
        self.assertEqual(set(gates), {f"G{i}" for i in range(1, 9)})
        self.assertEqual(
            {name: row["status"] for name, row in gates.items()},
            SM_TRACK_CLOSED_STATUSES,
        )
        self.assertEqual(
            self.report["summary"]["closed"], ["G1", "G2", "G3", "G4", "G5"]
        )
        self.assertEqual(self.report["summary"]["open"], ["G6"])
        self.assertEqual(self.report["summary"]["blocked"], ["G7", "G8"])
        self.assertEqual(self.report["summary"]["n_closed"], 5)
        self.assertEqual(self.report["summary"]["n_open"], 1)
        self.assertEqual(self.report["summary"]["n_blocked"], 2)
        for name in ("G4", "G6"):
            self.assertEqual(gates[name]["unsatisfied_dependencies"], [], name)
            self.assertIsNone(gates[name]["blocking_root"], name)
        self.assertEqual(gates["G7"]["unsatisfied_dependencies"], ["G6"])
        self.assertEqual(gates["G7"]["blocking_root"], "DEPENDENCY_NOT_CLOSED")
        self.assertEqual(gates["G8"]["unsatisfied_dependencies"], ["G6", "G7"])
        # G4 closes on the certified witness binding, never on a status alone.
        g4 = gates["G4"]
        evidence = g4["closure_evidence"]
        self.assertIs(evidence["certified"], True, evidence["blockers"])
        self.assertEqual(evidence["blockers"], [])
        self.assertEqual(evidence["status"], g4_closure.REQUIRED_STATUS)
        self.assertEqual(evidence["required_status"], g4_closure.REQUIRED_STATUS)
        self.assertIs(evidence["witness_bound_to_g3_track"], True)
        self.assertEqual(
            evidence,
            g4_closure.evaluate_g4_binding(
                g4_closure.load_g4_report(mod.G4_PHYSICAL_QUOTIENT_JSON),
                g3_witness=self.report["g3_sm_target_track"]["witness"],
                g4_open_scope=g4["open_scope"],
            ),
        )
        self.assertIs(g4["closed_on_current_authoritative_contract"], True)
        self.assertEqual(g4["closure_scope"], g4_closure.G4_LEDGER_CLOSED_SCOPE)
        self.assertEqual(
            g4["routed_caveats_resolved_by_closure"],
            [g4_closure.ROUTED_G4_CAVEAT_ID],
        )
        self.assertEqual(g4["decision"], g4_closure.G4_CLOSURE_DECISION)
        # Decision D-E: the G4 closure itself approves no internal candidate.
        self.assertIn("held until G7 is CLOSED", g4["decision"])
        self.assertIs(g4_closure.ledger_g4_closed(self.report), True)
        self.assertIs(
            g4_closure.ledger_g4_closed(json.loads(json.dumps(self.report))), True
        )
        # G6 is OPEN, not CLOSED: the tree spectrum is evidence only.
        self.assertIs(gates["G6"]["closed_on_current_authoritative_contract"], False)
        self.assertEqual(gates["G6"]["authoritative_closed_scope"], [])
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
                "G1": ["promoted exact-X scalar census", mod.G1_TRUNCATION_CLOSED_SCOPE],
                "G2": ["promoted exact-X dense derivative and Ward audit"],
                "G3": [sm_track.G3_LEDGER_CLOSED_SCOPE],
                "G4": [g4_closure.G4_LEDGER_CLOSED_SCOPE],
                "G5": [sm_track.G5_LEDGER_CLOSED_SCOPE],
                "G6": [],
                "G7": [],
                "G8": [],
            },
        )
        # The G4 open scope is unchanged by the closure (the certificate pins it).
        self.assertEqual(
            gates["G4"]["open_scope"], mod._gate_open_scope("G4", track)
        )
        self.assertEqual(len(gates["G4"]["open_scope"]), 3)
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
            "G6": [G6_SPECIFICATION],
            "G7": ["await G6 and independently validate the full beta system"],
            "G8": ["await authoritative G3/G6/G7 before any unique lifetime claim"],
        }
        evidence_items = {
            "G6": [mod.G6_EVIDENCE_RECORDED_ITEM, mod.G6_REMNANT_RG_RECORDED_ITEM],
            "G7": [mod.G7_COUPLED_SINGLET_PROBE_RECORDED_ITEM, mod.G7_BENCHMARK_RECORDED_ITEM],
            "G8": [mod.G8_EVIDENCE_RECORDED_ITEM, mod.G8_STRUCTURAL_RECORDED_ITEM],
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
            if gate_name in evidence_items:
                n_evidence = len(evidence_items[gate_name])
                self.assertEqual(open_scope[n_spec:-n_evidence], routed, gate_name)
                self.assertEqual(
                    open_scope[-n_evidence:], evidence_items[gate_name], gate_name
                )
            else:
                self.assertEqual(open_scope[n_spec:], routed, gate_name)
        self.assertEqual(
            mod.G6_EVIDENCE_RECORDED_ITEM,
            "tree-level evidence at mu = M_GUT (does not close G6): "
            "g6_sm_pati_salam_tree_spectrum_v20 (G6_SM_PATI_SALAM_TREE_SPECTRUM_V20.json) "
            "certifies exactly, for all r0, x0, eps > 0, the tree-level Hessian spectrum at "
            "mu = M_GUT at the G3 witness vacuum: 35 zero modes (34 eaten Goldstones + the "
            "axion), 451 positive and 0 negative, with exact SM labels; still open: one-loop "
            "positivity of the light 126bar remnant multiplets at the physical hierarchy (R1), "
            "electroweak symmetry breaking (H = 0 at the witness; the eps < 0 member is not "
            "certified) and the uncertainty budget",
        )
        self.assertEqual(
            mod.G6_REMNANT_RG_RECORDED_ITEM,
            "remnant RG evidence (does not close G6): g6_sm_pati_salam_remnant_rg_nogo_v20 "
            "(G6_SM_PATI_SALAM_REMNANT_RG_NOGO_V20.json) records that G6 is not closable on "
            "the SOS-certified witness family at one loop with tree-level matching: exact "
            "tree-level matching at mu = M_GUT forces lambda4 >= lambda5 for every SOS-safe "
            "126bar weight vector, while the research-recorded one-loop-positive remnant "
            "region (sampled scans; best points recomputed) needs lambda4 - lambda5 < 0 at "
            "M_GUT, and the certified witness runs tachyonic (lambda5 = 0 near 4.7e16 GeV at "
            "rho = 1e3); with the only computed one-loop M_GUT threshold (at the witness; "
            "assumed weight independent, not verified) lambda4 - lambda5 shifts by -0.57, "
            "which removes the lambda4 >= lambda5 obstruction: the remaining separation is "
            "0.042 at rho = 1e3 and closes at 1.2-1.7 times that threshold, so only the "
            "tree-matching statement is robust; G6 is not shown impossible in the contract "
            "(an anti-SOS G3 witness might exist) and the G3/G4 tree-level closures are "
            "unchanged; closing G6 would need controlled M_GUT thresholds and two-loop "
            "quartic running and, unless those thresholds open an SOS-safe route, an "
            "anti-SOS G3 witness",
        )
        self.assertEqual(
            mod.G6_REMNANT_RG_SCOPE,
            (
                "SOS-certified witness family only (126bar self weights w_q >= w_2772)",
                "tree-level matching at mu = M_GUT; one-loop quartic running with two-loop PS gauge profiles",
                "the M_GUT one-loop threshold is assumed weight independent (not verified)",
                "not a proof that G6 is impossible in the contract",
                "disjointness robust at tree matching only (marginal with the one-loop M_GUT "
                "threshold: 0.042 at rho = 1e3, closing at 1.2-1.7 times that threshold)",
                "the one-loop-positive region is a sampled, box-bounded research scan (its best "
                "points are recomputed)",
            ),
        )
        self.assertIn("records Route C", mod.G8_EVIDENCE_RECORDED_ITEM)
        # Decision U1: routes A and B are not pursued (no user decision pending).
        self.assertIn("are not pursued (user decision U1", mod.G8_EVIDENCE_RECORDED_ITEM)
        self.assertTrue(
            mod.G8_EVIDENCE_RECORDED_ITEM.endswith(
                "are not pursued (user decision U1: the no-go is accepted and the program "
                "claim re-scoped; see program_verdict)"
            )
        )
        self.assertNotIn("need a user decision", mod.G8_EVIDENCE_RECORDED_ITEM)
        # Rescue-study correction of the Route B parenthesis (text only; the companion module is not wired in).
        for text in (
            "on the certified witness orientation, among the analysed extensions only a 120_H can split d from e",
            "only through a (15,2,2)_120 admixture of O((v_R/M15)^2)",
            "a tuned-light (15,2,2)_120, which SOS squares allow, gives O(1) splitting",
            "also split d from e but sit off the certified orientation",
            "g8_sm_pati_salam_structural_obstruction_v20",
        ):
            self.assertIn(text, mod.G8_EVIDENCE_RECORDED_ITEM)
        self.assertNotIn("vectorlike matter were not analysed", mod.G8_EVIDENCE_RECORDED_ITEM)
        self.assertNotIn("orientation only a 120_H", mod.G8_EVIDENCE_RECORDED_ITEM)
        self.assertNotIn("at O(r0^2) when added as SOS squares", mod.G8_EVIDENCE_RECORDED_ITEM)
        tree = gates["G6"]["tree_level_evidence"]
        self.assertEqual(
            tree,
            {
                "source": "g6_sm_pati_salam_tree_spectrum_v20",
                "report": "G6_SM_PATI_SALAM_TREE_SPECTRUM_V20.json",
                "required_status": mod.G6_TREE_SPECTRUM_STATUS,
                "status": mod.G6_TREE_SPECTRUM_STATUS,
                "n_failed": 0,
                "recorded": True,
                "closes_gate": False,
                "role": "evidence only: cited in the G6 open scope, never changes the G6 status",
                "still_open": [
                    "one-loop positivity of the light 126bar remnant multiplets at the physical hierarchy (R1)",
                    "electroweak symmetry breaking (H = 0 at the witness; the eps < 0 member is not certified)",
                    "the uncertainty budget of the threshold spectrum",
                ],
            },
        )
        self.assertEqual(
            gates["G6"]["remnant_rg_evidence"],
            {
                "source": "g6_sm_pati_salam_remnant_rg_nogo_v20",
                "report": "G6_SM_PATI_SALAM_REMNANT_RG_NOGO_V20.json",
                "required_status": mod.G6_REMNANT_RG_NOGO_STATUS,
                "status": mod.G6_REMNANT_RG_NOGO_STATUS,
                "n_failed": 0,
                "recorded": True,
                "closes_gate": False,
                "role": "evidence only: cited in the G6 open scope, never changes the G6 status",
                "scope": list(mod.G6_REMNANT_RG_SCOPE),
            },
        )
        self.assertEqual(
            mod.G6_REMNANT_RG_NOGO_STATUS,
            "G6_SM_PATI_SALAM_REMNANT_RG__NOT_CLOSABLE_ON_SOS_WITNESS_FAMILY__G6_OPEN",
        )
        self.assertEqual(mod.G6_REMNANT_RG_NOGO_N_CHECKS, 58)
        self.assertEqual(mod.G6_REMNANT_RG_TREE_SCOPE, "tree level at mu = M_GUT")
        self.assertEqual(len(mod.G6_REMNANT_RG_NEVER_TRUE_FLAGS), 13)
        self.assertIn(
            "disjointness_robust_to_one_loop_threshold", mod.G6_REMNANT_RG_NEVER_TRUE_FLAGS
        )
        flavour = gates["G8"]["flavour_evidence"]
        g8_data = mod._load_json_artifact(mod.G8_FLAVOUR_NOGO_JSON)["data"]
        self.assertEqual(
            flavour,
            {
                "source": "g8_sm_pati_salam_flavour_nogo_v20",
                "report": "G8_SM_PATI_SALAM_FLAVOUR_NOGO_V20.json",
                "required_status": mod.G8_FLAVOUR_NOGO_STATUS,
                "status": mod.G8_FLAVOUR_NOGO_STATUS,
                "n_failed": 0,
                "recorded": True,
                "closes_gate": False,
                "role": "evidence only: cited in the G8 open scope, never changes the G8 status",
                "route_recorded": "C",
                "routes_not_pursued_user_decision_U1": ["A", "B"],
                "pull_fields": [
                    "data.minimum_load_bearing_pull_raw_sigma",
                    "data.minimum_load_bearing_pull_conservative_sigma",
                ],
                "minimum_load_bearing_pull_raw_sigma": g8_data["minimum_load_bearing_pull_raw_sigma"],
                "minimum_load_bearing_pull_conservative_sigma": g8_data[
                    "minimum_load_bearing_pull_conservative_sigma"
                ],
                "threshold_sigma": g8_data["threshold_sigma"],
                "scale_band_GeV": [1e9, 2e16],
            },
        )
        self.assertNotIn("routes_needing_user_decision", flavour)
        self.assertEqual(f"{flavour['minimum_load_bearing_pull_raw_sigma']:.1f}", "13.2")
        self.assertEqual(f"{flavour['minimum_load_bearing_pull_conservative_sigma']:.1f}", "8.9")
        self.assertEqual(flavour["threshold_sigma"], 5.0)
        self.assertEqual(gates["G8"]["status"], mod.STATUS_BLOCKED)
        # G7 and G8 cite the PR #206 records as evidence only; G1 carries its
        # truncation scope (decision U5).  None of them changes a status.
        self.assertEqual(
            gates["G7"]["benchmark_evidence"],
            {
                "source": "g7_decoupled_singlet_benchmark_evidence_v20",
                "report": "G7_DECOUPLED_SINGLET_BENCHMARK_EVIDENCE_V20.json",
                "required_status": mod.G7_BENCHMARK_STATUS,
                "status": mod.G7_BENCHMARK_STATUS,
                "n_failed": 0,
                "recorded": True,
                "closes_gate": False,
                "role": "evidence only: cited in the G7 open scope, never changes the G7 status",
            },
        )
        self.assertEqual(
            gates["G7"]["coupled_singlet_two_loop_probe"],
            {
                "source": "two_loop_thresholds_v20",
                "report": "two_loop_thresholds_v20.json",
                "field": "spectator_two_loop_probe",
                "status": "two-loop threshold RG report",
                "recorded": True,
                "closes_gate": False,
                "role": (
                    "evidence only: reproduces the decision-D-E coupled-singlet two-loop "
                    "non-unification; never changes the G7 status"
                ),
                "label": (
                    "NUM (gauge-only two-loop Machacek-Vaughn running; Yukawa terms and "
                    "threshold matching omitted)"
                ),
                "content": "anchor content + 5 x (16+16bar) at M_s = M_I",
                "scan_log10_M_I": [8.0, 14.5],
                "perturbative_root_exists": False,
            },
        )
        self.assertEqual(
            gates["G8"]["structural_obstruction_evidence"],
            {
                "source": "g8_sm_pati_salam_structural_obstruction_v20",
                "report": "G8_SM_PATI_SALAM_STRUCTURAL_OBSTRUCTION_V20.json",
                "required_status": mod.G8_STRUCTURAL_STATUS,
                "status": mod.G8_STRUCTURAL_STATUS,
                "n_failed": 0,
                "recorded": True,
                "closes_gate": False,
                "role": "evidence only: cited in the G8 open scope, never changes the G8 status",
                "label": (
                    "EXACT at the dimension-4 level on the degree-2-SOS-certified witness family; "
                    "off-orientation splitters research-recorded"
                ),
            },
        )
        self.assertEqual(
            gates["G1"]["model_contract_truncation_scope"],
            {
                "source": "g1_contract_truncation_scope_v20",
                "report": "G1_CONTRACT_TRUNCATION_SCOPE_V20.json",
                "required_status": mod.G1_TRUNCATION_STATUS,
                "status": mod.G1_TRUNCATION_STATUS,
                "n_failed": 0,
                "recorded": True,
                "changes_gate": False,
                "role": (
                    "scope only: states that G1 and the attested model contract attest a "
                    "truncation; never changes the G1 status"
                ),
                "allowed_count": 26,
                "declared_count": 10,
                "undeclared": list(mod.G1_TRUNCATION_UNDECLARED),
                "F_16bar_mass_mixings": ["Phi17.F.Rbar", "conj[Phi17].F.Pbar"],
                "scope_text": mod.G1_TRUNCATION_SCOPE_TEXT,
            },
        )
        self.assertEqual(
            self.report["model_contract_scope"], gates["G1"]["model_contract_truncation_scope"]
        )
        self.assertEqual(len(mod.G1_TRUNCATION_UNDECLARED), 16)
        self.assertEqual(
            mod.G1_TRUNCATION_UNDECLARED,
            tuple(
                mod._load_json_artifact(mod.G8_FLAVOUR_NOGO_JSON)["contract"][
                    "allowed_but_undeclared"
                ]
            ),
        )
        for label in mod.G1_TRUNCATION_UNDECLARED:
            self.assertIn(label, mod.G1_TRUNCATION_SCOPE_TEXT)
        self.assertIn("ARGUMENT, not computed", mod.G1_TRUNCATION_SCOPE_TEXT)
        self.assertIn("The couplings are not added", mod.G1_TRUNCATION_SCOPE_TEXT)
        # The 16 labels refer to the model file's field basis; the truncation
        # itself is basis independent (exact dimension count 48 > 25).
        for text in (mod.G1_TRUNCATION_SCOPE_TEXT, mod.G1_TRUNCATION_CLOSED_SCOPE):
            self.assertIn("model file's field basis", text)
        self.assertIn("no field basis removes the truncation", mod.G1_TRUNCATION_SCOPE_TEXT)
        self.assertIn("more than the 25 of U(5)", mod.G1_TRUNCATION_SCOPE_TEXT)
        self.assertEqual(
            mod.G1_TRUNCATION_REDEFINITION_DIMENSIONS,
            {
                "undeclared_real_dimension": 48,
                "mixing_redefinition_real_dimension": 25,
                "declared_orbit_real_dimension_bound": 125,
                "all_couplings_real_dimension": 148,
            },
        )
        for text in (
            "BM-DA1 (v_S decoupled from v_R)",
            "so G7 stays BLOCKED",
            "with the U1 root held fixed",
            "a 120_H, a second 126bar and vectorlike pairs (also with a 45_H) fail the criterion "
            "already at two loops",
            "(10_F, a real or complex 45_H) pass at two loops and fail at three loops, as does the "
            "contract content itself on that root",
            "convention- and threshold-limited",
            "not conservative for a fail statement",
        ):
            self.assertIn(text, mod.G7_BENCHMARK_RECORDED_ITEM)
        self.assertNotIn("every analysed flavour-capable", mod.G7_BENCHMARK_RECORDED_ITEM)
        for text in (
            "three independent two-loop RG codes",
            "research runs recorded with decision D-E",
            "two_loop_thresholds_v20.json, spectator_two_loop_probe",
            "no perturbative root for log10(M_I/GeV) in [8, 14.5]",
        ):
            self.assertIn(text, mod.G7_COUPLED_SINGLET_PROBE_RECORDED_ITEM)
        self.assertIn(
            "research runs recorded with decision D-E, not a committed certificate",
            mod.G7_COUPLED_SINGLET_PROBE_UNAVAILABLE_ITEM,
        )
        for text in (
            "degree-2-SOS-certified witness family",
            "flavour-dead at the dimension-4 level",
            "the in-contract H-linear-portal down-type sources require leaving the certified "
            "orientation (exact, dimension 4)",
            "a tuned-light (15,2,2)_120 extension is excluded only numerically (research)",
            "the unanalysed extensions remain open",
            "no certification method has been demonstrated for the flavour-capable orientations",
            "research-recorded, not proved",
            "the SO(10) contract and the G3-G5 certificates are not falsified",
        ):
            self.assertIn(text, mod.G8_STRUCTURAL_RECORDED_ITEM)
        for stale in ("flavour-capable sources require leaving", "no certification method is available"):
            self.assertNotIn(stale, mod.G8_STRUCTURAL_RECORDED_ITEM)
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
            wave3["status"],
            "G3_CLOSED_ON_SM_PATI_SALAM_TRACK__G4_CLOSED_AT_G3_WITNESS__G5_CLOSED",
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
            + " "
            + g4_closure.G4_CLOSED_SENTENCE
            + " G5 is CLOSED on the same Pati-Salam coupling vector. "
            + mod.CHIRAL_WAVE3_TAIL,
        )
        self.assertNotIn("G4 is OPEN", deliverable)
        self.assertIn("massless only for the renormalizable PQ-neutral", deliverable)
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
            [(4, "OPEN"), (5, "BLOCKED_ON_G6"), (6, "BLOCKED_ON_G6_G7")],
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
                "(V4 >= |q|^4/167; the eps N_H term is quadratic). "
                + g4_closure.G4_CLOSED_SENTENCE
                + " G6 is OPEN (tree-level evidence at mu = M_GUT only: "
                "g6_sm_pati_salam_tree_spectrum_v20; one-loop positivity of the "
                "light 126bar remnants at the physical hierarchy, electroweak symmetry "
                "breaking and the uncertainty budget are open, and the G6 open scope "
                "cites the remnant RG no-go on the SOS witness family); G7 and G8 remain "
                "dependency-blocked. "
                + sm_track.CAVEAT_ROUTING_SENTENCE
                + " Diagnostics that cannot close G3: A perturbative 27-of-51 "
                "SOS candidate with J0=-21/200 has"
            )
        )
        self.assertNotIn("G4 is OPEN", verdict)
        self.assertNotIn("G6 is CLOSED", verdict)
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
            self.assertEqual(report["gates"]["G4"]["authoritative_closed_scope"], [], key)
            self.assertIsNone(report["gates"]["G4"]["closure_scope"], key)
            self.assertIs(
                report["feasibility"]["gauged_G3_sm_pati_salam_track_closed"],
                False,
            )
            self.assertIs(
                report["feasibility"]["gauged_G4_sm_witness_quotient_closed"],
                False,
            )
            for name in (
                RENAMED_G3_G5_CHECK,
                *NEW_G4_CHECKS,
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
        # A certified G4 binding cannot close G4 on a blocked contract.
        g4 = report["gates"]["G4"]
        self.assertEqual(g4["status"], mod.STATUS_BLOCKED)
        self.assertEqual(g4["blocking_root"], mod.CONTRACT_BLOCKER)
        # The binding itself is certified (the witness is the track's own),
        # but the blocked contract keeps G4 BLOCKED.
        self.assertIs(g4["closure_evidence"]["certified"], True)
        self.assertEqual(g4["closure_evidence"]["blockers"], [])
        self.assertIs(g4["closed_on_current_authoritative_contract"], False)
        self.assertEqual(g4["authoritative_closed_scope"], [])
        self.assertIsNone(g4["closure_scope"])
        self.assertEqual(g4["routed_caveats_resolved_by_closure"], [])
        self.assertIs(g4_closure.ledger_g4_closed(report), False)
        self.assertIs(
            report["feasibility"]["gauged_G4_sm_witness_quotient_closed"], False
        )
        for name in (RENAMED_G3_G5_CHECK, *NEW_G4_CHECKS):
            self.assertIs(report["checks"][name], True, name)
        # Forged frontier: a blocked contract never carries a recorded program
        # verdict, even though every bound certificate is still recorded.
        verdict = report["program_verdict"]
        self.assertIs(verdict["recorded"], False)
        self.assertEqual(verdict["code"], mod.PROGRAM_VERDICT_CODE_UNAVAILABLE)
        self.assertEqual(verdict["text"], mod.PROGRAM_VERDICT_UNAVAILABLE_TEXT)
        self.assertIsNone(verdict["headline"])
        self.assertEqual(
            verdict["gate_statuses"], {f"G{i}": mod.STATUS_BLOCKED for i in range(1, 9)}
        )
        self.assertIs(
            report["checks"]["program_verdict_and_scope_records_never_change_a_gate"], True
        )
        self.assertEqual(report["gates"]["G1"]["authoritative_closed_scope"], [])
        self.assertIs(report["gates"]["G1"]["model_contract_truncation_scope"]["recorded"], True)

    def test_blocked_contract_keeps_g4_blocked_even_with_a_certified_binding(self):
        inputs = self.report["model_contract_reports"]
        blocked_x = mod.exact_x.build_report(
            model_text=mod.exact_x.MODEL.read_text(encoding="utf-8")
        )
        certified = g4_closure.evaluate_g4_binding(
            g4_closure.load_g4_report(mod.G4_PHYSICAL_QUOTIENT_JSON)
        )
        self.assertIs(certified["certified"], True)
        self.assertEqual(
            mod._expected_gate_statuses(
                False, g3_closed=True, g5_closed=True, g4_closed=True
            ),
            {f"G{i}": mod.STATUS_BLOCKED for i in range(1, 9)},
        )
        report = mod._build_report_from_inputs(
            x_report=blocked_x,
            g1_report=inputs["gauged_G1_character_census"],
            g2_report=inputs["gauged_G2_derivative_audit"],
            filter_report=inputs["gauged_scalar_filter"],
            g4_report=g4_closure.load_g4_report(mod.G4_PHYSICAL_QUOTIENT_JSON),
        )
        self.assertEqual(report["n_failed"], 0, report["audit_failures"])
        self.assertEqual(
            {row["status"] for row in report["gates"].values()},
            {mod.STATUS_BLOCKED},
        )
        self.assertEqual(report["gates"]["G4"]["authoritative_closed_scope"], [])
        self.assertNotIn("G4", report["summary"]["closed"])

    def test_forged_or_missing_g4_report_reopens_g4_fail_closed(self):
        committed = g4_closure.load_g4_report(mod.G4_PHYSICAL_QUOTIENT_JSON)
        n_failed_bool = copy.deepcopy(committed)
        n_failed_bool["n_failed"] = True
        old_status = copy.deepcopy(committed)
        old_status["status"] = "G4_SM_PATI_SALAM_PHYSICAL_QUOTIENT_CERTIFIED__G4_NOT_WIRED"
        superseded_ranks = copy.deepcopy(committed)
        gauge = superseded_ranks["gauge_quotient"]
        gauge["ranks"]["SO10_x_U1X"] = 37
        gauge["ranks"]["SO10_x_U1X_x_PQ"] = 38
        gauge["gauge_quotient_dimension_including_axion"] = 449
        gauge["massive_transverse_quotient_dimension"] = 448
        superseded_json = mod._load_json_artifact(
            mod.ROOT / "EXACT_GAUGED_U1X_PHYSICAL_QUOTIENT_V20.json"
        )
        self.assertTrue(superseded_json)
        cases = {
            "empty": {},
            "n_failed True": n_failed_bool,
            "old status": old_status,
            "ranks 37/38, quotients 449/448": superseded_ranks,
            "superseded p+delta quotient JSON": superseded_json,
        }
        for label, forged in cases.items():
            with self.subTest(case=label):
                report = self._build_with(g4_report=forged)
                self._assert_g4_reopened(report, label)

    def _assert_g4_reopened(self, report, label):
        statuses = {name: row["status"] for name, row in report["gates"].items()}
        self.assertEqual(report["n_failed"], 0, (label, report["audit_failures"]))
        self.assertEqual(report["status"], G4_OPEN_STATUS, label)
        self.assertEqual(report["overall_state"], mod.STATUS_OPEN, label)
        self.assertEqual(statuses, G4_REOPENED_STATUSES, label)
        self.assertEqual(
            report["scientific_blockers"], list(sm_track.DOWNSTREAM_BLOCKERS), label
        )
        waves = report["closure_waves"]
        self.assertEqual(
            waves[3]["status"],
            "G3_CLOSED_ON_SM_PATI_SALAM_TRACK__G4_OPEN__G5_CLOSED",
            label,
        )
        self.assertEqual(waves[4]["status"], "BLOCKED_ON_G4", label)
        g4 = report["gates"]["G4"]
        self.assertIn(
            "the G4 closure binding is not certified; blockers: "
            + ", ".join(g4["closure_evidence"]["blockers"])
            + ").",
            waves[3]["deliverable"],
            label,
        )
        self.assertNotIn(g4_closure.G4_CLOSED_SENTENCE, waves[3]["deliverable"], label)
        self.assertIn(
            "G4 is OPEN; G6-G8 remain dependency-blocked.", report["verdict"], label
        )
        self.assertIs(g4["closure_evidence"]["certified"], False, label)
        self.assertTrue(g4["closure_evidence"]["blockers"], label)
        self.assertEqual(g4["authoritative_closed_scope"], [], label)
        self.assertIsNone(g4["closure_scope"], label)
        self.assertEqual(g4["routed_caveats_resolved_by_closure"], [], label)
        self.assertEqual(g4["open_scope"], self.report["gates"]["G4"]["open_scope"], label)
        self.assertEqual(report["gates"]["G6"]["unsatisfied_dependencies"], ["G4"], label)
        self.assertEqual(
            report["gates"]["G6"]["blocking_root"], "DEPENDENCY_NOT_CLOSED", label
        )
        self.assertIs(g4_closure.ledger_g4_closed(report), False, label)
        self.assertIs(
            report["feasibility"]["gauged_G4_sm_witness_quotient_closed"], False, label
        )
        self.assertEqual(report["feasibility"]["current_authoritative_closed_gates"], 4)
        for name in (RENAMED_G3_G5_CHECK, *NEW_G4_CHECKS, "gate_frontier_matches_contract_state"):
            self.assertIs(report["checks"][name], True, (label, name))

    def test_g4_witness_mismatched_with_the_g3_track_leaves_g4_open(self):
        committed = g4_closure.load_g4_report(mod.G4_PHYSICAL_QUOTIENT_JSON)
        kappa = copy.deepcopy(committed)
        kappa["witness"]["kappa"] = "-1/10"
        vacuum = copy.deepcopy(committed)
        vacuum["witness"]["vacuum"] = (
            "q0 = (Phi, H, Sigma, S, Phi17) = (F, 0, r Delta_R, r0, x0), independent of eps"
        )
        for label, forged in (("kappa", kappa), ("vacuum", vacuum)):
            with self.subTest(forged=label):
                report = self._build_with(g4_report=forged)
                self._assert_g4_reopened(report, label)
                self.assertIn(
                    "g4_witness_is_the_g3_witness",
                    report["gates"]["G4"]["closure_evidence"]["blockers"],
                )

    def test_g6_g8_evidence_never_changes_a_gate(self):
        report = self._build_with(g6_report={}, g8_report={}, g6_rg_report={})
        tree = report["gates"]["G6"]["tree_level_evidence"]
        remnant = report["gates"]["G6"]["remnant_rg_evidence"]
        flavour = report["gates"]["G8"]["flavour_evidence"]
        self.assertIs(tree["recorded"], False)
        self.assertIs(tree["closes_gate"], False)
        self.assertIsNone(tree["status"])
        self.assertIs(remnant["recorded"], False)
        self.assertIs(remnant["closes_gate"], False)
        self.assertIsNone(remnant["status"])
        self.assertIs(flavour["recorded"], False)
        self.assertIs(flavour["closes_gate"], False)
        self.assertIsNone(flavour["route_recorded"])
        self.assertEqual(
            report["gates"]["G6"]["open_scope"][-2], mod.G6_EVIDENCE_UNAVAILABLE_ITEM
        )
        self.assertEqual(
            report["gates"]["G6"]["open_scope"][-1], mod.G6_REMNANT_RG_UNAVAILABLE_ITEM
        )
        self.assertEqual(
            report["gates"]["G8"]["open_scope"][-2], mod.G8_EVIDENCE_UNAVAILABLE_ITEM
        )
        self.assertEqual(
            report["gates"]["G8"]["open_scope"][-1], mod.G8_STRUCTURAL_RECORDED_ITEM
        )
        self.assertEqual(
            {name: row["status"] for name, row in report["gates"].items()},
            {name: row["status"] for name, row in self.report["gates"].items()},
        )
        self.assertEqual(report["status"], self.report["status"])
        self.assertEqual(report["checks"], self.report["checks"])
        self.assertEqual(report["n_failed"], 0, report["audit_failures"])
        # Without the G8 flavour JSON the ledger-side truncation cross-check
        # and two program-verdict components fail closed.
        self.assertIs(report["gates"]["G1"]["model_contract_truncation_scope"]["recorded"], False)
        self.assertIs(report["program_verdict"]["recorded"], False)
        self.assertEqual(report["program_verdict"]["code"], mod.PROGRAM_VERDICT_CODE_UNAVAILABLE)
        # Replacing only the remnant RG report flips only that record and item.
        only_rg = self._build_with(g6_rg_report={})
        self.assertIs(only_rg["gates"]["G6"]["remnant_rg_evidence"]["recorded"], False)
        self.assertIs(only_rg["gates"]["G6"]["tree_level_evidence"]["recorded"], True)
        self.assertEqual(
            only_rg["gates"]["G6"]["open_scope"][:-1],
            self.report["gates"]["G6"]["open_scope"][:-1],
        )
        self.assertEqual(
            only_rg["gates"]["G6"]["open_scope"][-1], mod.G6_REMNANT_RG_UNAVAILABLE_ITEM
        )
        self.assertEqual(
            {name: row["status"] for name, row in only_rg["gates"].items()},
            {name: row["status"] for name, row in self.report["gates"].items()},
        )
        self.assertEqual(only_rg["status"], self.report["status"])
        self.assertEqual(only_rg["checks"], self.report["checks"])

    def test_g6_g8_evidence_records_are_fail_closed(self):
        g6 = mod._load_json_artifact(mod.G6_TREE_SPECTRUM_JSON)
        g6_rg = mod._load_json_artifact(mod.G6_REMNANT_RG_NOGO_JSON)
        g8 = mod._load_json_artifact(mod.G8_FLAVOUR_NOGO_JSON)
        self.assertIs(mod.g6_tree_evidence(g6)["recorded"], True)
        self.assertIs(mod.g6_remnant_rg_evidence(g6_rg)["recorded"], True)
        self.assertIs(mod.g8_flavour_evidence(g8)["recorded"], True)

        def forged(report, *path, value):
            copied = copy.deepcopy(report)
            target = copied
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = value
            return copied

        g6_cases = (
            None, [], {}, forged(g6, "n_failed", value=False), forged(g6, "n_checks", value=80),
            forged(g6, "status", value="G6_CLOSED"), forged(g6, "flags", "G6_closed", value=True),
            forged(g6, "flags", "report_closes_g6_by_itself", value=True),
            forged(g6, "flags", "tree_level_proof_grade", value=False),
            forged(g6, "flags", value=None),
        )
        for case in g6_cases:
            record = mod.g6_tree_evidence(case)
            self.assertIs(record["recorded"], False)
            self.assertIs(record["closes_gate"], False)
        g8_cases = (
            None, [], {}, forged(g8, "n_failed", value="0"), forged(g8, "n_checks", value=102),
            forged(g8, "flags", "G8_closed", value=True),
            forged(g8, "flags", "route_C_recorded", value=False),
            forged(g8, "flags", "falsifies_G3_G5_scalar_vacuum_certificates", value=True),
        )
        for case in g8_cases:
            record = mod.g8_flavour_evidence(case)
            self.assertIs(record["recorded"], False)
            self.assertIsNone(record["route_recorded"])
            self.assertIs(record["closes_gate"], False)
        g6_rg_cases = (
            None, [], {}, forged(g6_rg, "n_failed", value=False),
            forged(g6_rg, "n_checks", value=52),
            forged(g6_rg, "status", value="G6_CLOSED"),
            forged(g6_rg, "flags", "G6_closed", value=True),
            forged(g6_rg, "flags", "report_closes_g6_by_itself", value=True),
            forged(g6_rg, "flags", "not_closable_on_sos_witness_family", value=False),
            forged(
                g6_rg, "flags", "sos_family_tree_matching_forces_lam4_ge_lam5_exact",
                value=False,
            ),
            forged(g6_rg, "flags", "g6_impossible_in_contract_claimed", value=True),
            forged(g6_rg, "flags", "changes_g3_g4_closure", value=True),
            forged(
                g6_rg, "flags", "one_loop_gut_threshold_w_independence_verified",
                value=True,
            ),
            forged(g6_rg, "flags", value=None),
            forged(g6_rg, "failures", value=["x"]),
            forged(g6_rg, "G6_status", value="CLOSED"),
            forged(g6_rg, "gate", value="G7"),
            forged(g6_rg, "tree_certificate_scope", value="all scales"),
        ) + tuple(
            forged(g6_rg, "flags", name, value=True)
            for name in mod.G6_REMNANT_RG_NEVER_TRUE_FLAGS
        ) + tuple(
            forged(g6_rg, "flags", name, value=None)
            for name in mod.G6_REMNANT_RG_NEVER_TRUE_FLAGS
        )
        for case in g6_rg_cases:
            record = mod.g6_remnant_rg_evidence(case)
            self.assertIs(record["recorded"], False)
            self.assertIs(record["closes_gate"], False)

    # ------------------------------------------------------------------
    # Decisions U1/U3/U5: scope and evidence records bound to committed
    # JSONs, and the separate program verdict.  None changes a gate.
    # ------------------------------------------------------------------

    @staticmethod
    def _forged(report, *path, value=None, delete=False):
        copied = copy.deepcopy(report)
        target = copied
        for key in path[:-1]:
            target = target[key]
        if delete:
            del target[path[-1]]
        else:
            target[path[-1]] = value
        return copied

    def test_program_verdict_records_decision_u1_without_changing_a_gate(self):
        verdict = self.report["program_verdict"]
        self.assertIs(verdict["recorded"], True)
        self.assertEqual(
            verdict["code"], "NOT_VIABLE_UNDER_DECLARED_STANDARDS__NO_GO_METHOD_LIMITED_AT_G3_X_G8"
        )
        self.assertEqual(verdict["code"], mod.PROGRAM_VERDICT_CODE)
        self.assertEqual(verdict["headline"], mod.PROGRAM_VERDICT_HEADLINE)
        self.assertEqual(
            verdict["headline"],
            "NOT VIABLE as a complete description of nature under the declared standards; "
            "the no-go is method-limited at G3 x G8",
        )
        self.assertEqual(verdict["text"], mod.PROGRAM_VERDICT_TEXT)
        self.assertEqual(verdict["decision"], mod.PROGRAM_VERDICT_DECISION)
        self.assertEqual(verdict["role"], mod.PROGRAM_VERDICT_ROLE)
        self.assertEqual(verdict["gate_statuses"], mod.PROGRAM_VERDICT_EXPECTED_STATUSES)
        self.assertEqual(verdict["gate_statuses"], SM_TRACK_CLOSED_STATUSES)
        self.assertEqual(verdict["expected_gate_statuses"], SM_TRACK_CLOSED_STATUSES)
        self.assertIs(verdict["gate_statuses_changed"], False)
        self.assertIs(verdict["proof_grade_whole_model_exclusion"], False)
        self.assertEqual(verdict["method_limited_at"], ["G3", "G8"])
        expected_components = [
            ("certified_tree_level_vacuum", "EXACT (tree level)",
             ["FINAL_G3_ACCEPTANCE_GATE_V20.json", "G4_SM_PATI_SALAM_PHYSICAL_QUOTIENT_V20.json"]),
            ("certified_family_flavour_dead", "EXACT (dimension 4; SOS-certified witness family)",
             ["G8_SM_PATI_SALAM_STRUCTURAL_OBSTRUCTION_V20.json"]),
            ("witness_branch_flavour_excluded", "EXACT relations, NUM data comparison",
             ["G8_SM_PATI_SALAM_FLAVOUR_NOGO_V20.json"]),
            ("flavour_capable_orientations_uncertified", "RESEARCH_RECORDED (not a committed certificate)",
             ["G8_SM_PATI_SALAM_STRUCTURAL_OBSTRUCTION_V20.json"]),
            ("g6_not_closable_on_certified_family", "EXACT tree-matching map, NUM region",
             ["G6_SM_PATI_SALAM_REMNANT_RG_NOGO_V20.json"]),
            ("flavour_capable_additions_fail_landau", "NUM (gauge + matter running, U1 root held fixed)",
             ["G7_DECOUPLED_SINGLET_BENCHMARK_EVIDENCE_V20.json"]),
            ("contract_truncation",
             "EXACT census and symmetry statement; radiative generation argued, not computed",
             ["G1_CONTRACT_TRUNCATION_SCOPE_V20.json"]),
        ]
        components = verdict["components"]
        self.assertEqual(
            [(c["id"], c["label"], c["sources"]) for c in components], expected_components
        )
        for component in components:
            self.assertIs(component["recorded"], True, component["id"])
            self.assertEqual(
                set(component), {"id", "label", "text", "sources", "recorded"}, component["id"]
            )
        g8_data = mod._load_json_artifact(mod.G8_FLAVOUR_NOGO_JSON)["data"]
        raw = f"{g8_data['minimum_load_bearing_pull_raw_sigma']:.2f}"
        cons = f"{g8_data['minimum_load_bearing_pull_conservative_sigma']:.2f}"
        self.assertEqual((raw, cons), ("13.24", "8.86"))
        flavour_text = components[2]["text"]
        # Two-decimal minimum pulls, never preceded by ">=" or "at least".
        self.assertIn(f"minimum load-bearing pulls of {raw} sigma", flavour_text)
        self.assertIn(f"and {cons} sigma (with a 10% theory term)", flavour_text)
        self.assertIn("13.24 sigma (experimental errors alone)", flavour_text)
        self.assertIn("1e9-2e16 GeV", flavour_text)
        for stale in ("at least", ">=", "rounded"):
            self.assertNotIn(stale, flavour_text)
        # Scoped negative statements only; the research claim is labelled.
        self.assertIn("research, not proved", components[3]["text"])
        self.assertIn(
            "no certification method has been demonstrated for the flavour-capable vacuum orientations",
            components[3]["text"],
        )
        self.assertNotIn("no other exact", components[3]["text"])
        self.assertIn("not a proof that G6 is impossible in the contract", components[4]["text"])
        self.assertIn("at one loop with tree-level matching", components[4]["text"])
        for fragment in (
            "U1 root held fixed; gauge + matter running",
            "fail the reduced-Planck Landau criterion already at two loops",
            "as does the contract content itself on that root",
            "omitted Yukawa terms not conservative for a fail statement",
        ):
            self.assertIn(fragment, components[5]["text"])
        self.assertIn("model file's field basis", components[6]["text"])
        for fragment in (
            "under the declared standards (exact G3 vacuum certification and the G1-G8 gate criteria of "
            "G1_G8_GATE_LEDGER_V20)",
            "method-limited at G3 x G8",
            "Research-recorded, not a committed certificate",
            "no certification method has been demonstrated for the flavour-capable vacuum orientations",
            "EXACT relations, NUM data comparison: on the witness branch",
            "G6 is not closable on the SOS-certified witness family at one loop with tree-level matching",
            "(U1 root held fixed; gauge + matter running)",
            "fail the reduced-Planck Landau criterion already at two loops",
            "as does the contract content itself on that root",
            "three-loop verdict convention- and threshold-limited",
            "Gate statuses are unchanged (G1-G5 CLOSED, G6 OPEN, G7 BLOCKED, G8 BLOCKED)",
            "not a proof-grade exclusion of the SO(10) x U(1)_X contract",
        ):
            self.assertIn(fragment, mod.PROGRAM_VERDICT_TEXT)
        for stale in ("every analysed flavour-capable", "no other exact", "has a certification method"):
            self.assertNotIn(stale, mod.PROGRAM_VERDICT_TEXT)
        # The program verdict never feeds the ledger status or verdict.
        self.assertEqual(self.report["status"], CLOSED_G4_STATUS)
        self.assertNotIn("NOT VIABLE", self.report["verdict"])

    def test_scope_and_evidence_records_never_change_a_gate(self):
        report = self._build_with(g1_truncation_report={}, g7_report={}, g8_structural_report={})
        gates = report["gates"]
        truncation = gates["G1"]["model_contract_truncation_scope"]
        g7 = gates["G7"]["benchmark_evidence"]
        structural = gates["G8"]["structural_obstruction_evidence"]
        self.assertIs(truncation["recorded"], False)
        self.assertIs(truncation["changes_gate"], False)
        self.assertEqual(truncation["scope_text"], mod.G1_TRUNCATION_UNAVAILABLE_SCOPE)
        for key in ("allowed_count", "declared_count", "undeclared", "F_16bar_mass_mixings"):
            self.assertIsNone(truncation[key], key)
        self.assertIs(g7["recorded"], False)
        self.assertIs(g7["closes_gate"], False)
        self.assertIs(structural["recorded"], False)
        self.assertIs(structural["closes_gate"], False)
        self.assertEqual(
            gates["G1"]["authoritative_closed_scope"],
            ["promoted exact-X scalar census", mod.G1_TRUNCATION_UNAVAILABLE_SCOPE],
        )
        self.assertEqual(gates["G7"]["open_scope"][-1], mod.G7_BENCHMARK_UNAVAILABLE_ITEM)
        self.assertEqual(gates["G7"]["open_scope"][-2], mod.G7_COUPLED_SINGLET_PROBE_RECORDED_ITEM)
        self.assertEqual(gates["G8"]["open_scope"][-1], mod.G8_STRUCTURAL_UNAVAILABLE_ITEM)
        self.assertEqual(gates["G8"]["open_scope"][-2], mod.G8_EVIDENCE_RECORDED_ITEM)
        verdict = report["program_verdict"]
        self.assertIs(verdict["recorded"], False)
        self.assertEqual(verdict["code"], mod.PROGRAM_VERDICT_CODE_UNAVAILABLE)
        self.assertEqual(verdict["text"], mod.PROGRAM_VERDICT_UNAVAILABLE_TEXT)
        self.assertIsNone(verdict["headline"])
        self.assertEqual(
            {c["id"]: c["recorded"] for c in verdict["components"]},
            {
                "certified_tree_level_vacuum": True,
                "certified_family_flavour_dead": False,
                "witness_branch_flavour_excluded": True,
                "flavour_capable_orientations_uncertified": False,
                "g6_not_closable_on_certified_family": True,
                "flavour_capable_additions_fail_landau": False,
                "contract_truncation": False,
            },
        )
        self.assertEqual(
            {name: row["status"] for name, row in gates.items()},
            {name: row["status"] for name, row in self.report["gates"].items()},
        )
        self.assertEqual(report["status"], self.report["status"])
        self.assertEqual(report["checks"], self.report["checks"])
        self.assertEqual(report["verdict"], self.report["verdict"])
        self.assertEqual(report["n_failed"], 0, report["audit_failures"])
        # Each missing certificate alone makes the program verdict unavailable.
        for label, kwargs in (
            ("truncation", {"g1_truncation_report": {}}),
            ("g7", {"g7_report": {}}),
            ("structural", {"g8_structural_report": {}}),
            ("g6_rg", {"g6_rg_report": {}}),
            ("g8_flavour", {"g8_report": {}}),
        ):
            with self.subTest(missing=label):
                single = self._build_with(**kwargs)
                self.assertIs(single["program_verdict"]["recorded"], False)
                self.assertEqual(
                    single["program_verdict"]["code"], mod.PROGRAM_VERDICT_CODE_UNAVAILABLE
                )
                self.assertEqual(
                    {name: row["status"] for name, row in single["gates"].items()},
                    SM_TRACK_CLOSED_STATUSES,
                )
                self.assertEqual(single["checks"], self.report["checks"])
        # The coupled-singlet two-loop probe is G7 evidence only: without it the
        # G7 item says so, and nothing else changes (not a program-verdict input).
        no_probe = self._build_with(two_loop_probe_report={})
        probe = no_probe["gates"]["G7"]["coupled_singlet_two_loop_probe"]
        self.assertIs(probe["recorded"], False)
        self.assertIs(probe["closes_gate"], False)
        for key in ("content", "scan_log10_M_I", "perturbative_root_exists", "status"):
            self.assertIsNone(probe[key], key)
        self.assertEqual(
            no_probe["gates"]["G7"]["open_scope"][-2], mod.G7_COUPLED_SINGLET_PROBE_UNAVAILABLE_ITEM
        )
        self.assertEqual(
            no_probe["gates"]["G7"]["open_scope"][-1], mod.G7_BENCHMARK_RECORDED_ITEM
        )
        self.assertEqual(no_probe["program_verdict"], self.report["program_verdict"])
        self.assertEqual(
            {name: row["status"] for name, row in no_probe["gates"].items()},
            SM_TRACK_CLOSED_STATUSES,
        )
        self.assertEqual(no_probe["checks"], self.report["checks"])
        self.assertEqual(no_probe["n_failed"], 0, no_probe["audit_failures"])
        # A reopened G4 changes the frontier: no recorded program verdict.
        reopened = self._build_with(g4_report={})
        self.assertEqual(reopened["status"], G4_OPEN_STATUS)
        self.assertIs(reopened["program_verdict"]["recorded"], False)
        self.assertIs(reopened["program_verdict"]["components"][0]["recorded"], False)

    def test_program_verdict_is_unavailable_after_an_audit_failure(self):
        record = mod.program_verdict_record(
            contract_consistent=True,
            statuses=dict(SM_TRACK_CLOSED_STATUSES),
            track=self.report["g3_sm_target_track"],
            g4_binding=self.report["gates"]["G4"]["closure_evidence"],
            g1_truncation=self.report["gates"]["G1"]["model_contract_truncation_scope"],
            g6_rg_evidence=self.report["gates"]["G6"]["remnant_rg_evidence"],
            g7_evidence=self.report["gates"]["G7"]["benchmark_evidence"],
            g8_evidence=self.report["gates"]["G8"]["flavour_evidence"],
            g8_structural=self.report["gates"]["G8"]["structural_obstruction_evidence"],
        )
        self.assertEqual(record, self.report["program_verdict"])
        failed = mod.program_verdict_record(
            contract_consistent=True,
            statuses=dict(SM_TRACK_CLOSED_STATUSES),
            track=self.report["g3_sm_target_track"],
            g4_binding=self.report["gates"]["G4"]["closure_evidence"],
            g1_truncation=self.report["gates"]["G1"]["model_contract_truncation_scope"],
            g6_rg_evidence=self.report["gates"]["G6"]["remnant_rg_evidence"],
            g7_evidence=self.report["gates"]["G7"]["benchmark_evidence"],
            g8_evidence=self.report["gates"]["G8"]["flavour_evidence"],
            g8_structural=self.report["gates"]["G8"]["structural_obstruction_evidence"],
            audit_failed=True,
        )
        self.assertIs(failed["recorded"], False)
        self.assertEqual(failed["code"], mod.PROGRAM_VERDICT_CODE_UNAVAILABLE)
        for statuses in (
            dict(SM_TRACK_CLOSED_STATUSES, G6="CLOSED"),
            dict(SM_TRACK_CLOSED_STATUSES, G8="CLOSED"),
            dict(SM_TRACK_CLOSED_STATUSES, G7="OPEN"),
        ):
            forged = mod.program_verdict_record(
                contract_consistent=True,
                statuses=statuses,
                track=self.report["g3_sm_target_track"],
                g4_binding=self.report["gates"]["G4"]["closure_evidence"],
                g1_truncation=self.report["gates"]["G1"]["model_contract_truncation_scope"],
                g6_rg_evidence=self.report["gates"]["G6"]["remnant_rg_evidence"],
                g7_evidence=self.report["gates"]["G7"]["benchmark_evidence"],
                g8_evidence=self.report["gates"]["G8"]["flavour_evidence"],
                g8_structural=self.report["gates"]["G8"]["structural_obstruction_evidence"],
            )
            self.assertIs(forged["recorded"], False, statuses)

    def test_record_constants_are_pinned_to_the_record_modules(self):
        # Imported here only: the ledger itself never imports these modules.
        import g1_contract_truncation_scope_v20 as g1_truncation
        import g7_decoupled_singlet_benchmark_evidence_v20 as g7
        import g8_sm_pati_salam_structural_obstruction_v20 as structural

        self.assertEqual(mod.G1_TRUNCATION_NEVER_TRUE_FLAGS, g1_truncation.NEVER_TRUE_FLAGS)
        self.assertEqual(mod.G1_TRUNCATION_TRUE_FLAGS, g1_truncation.TRUE_FLAGS)
        self.assertEqual(mod.G1_TRUNCATION_N_CHECKS, g1_truncation.EXPECTED_N_CHECKS)
        self.assertEqual(mod.G1_TRUNCATION_STATUS, g1_truncation.STATUS_RECORDED)
        self.assertEqual(mod.G1_TRUNCATION_UNDECLARED, g1_truncation.EXPECTED_UNDECLARED_LABELS)
        self.assertEqual(mod.G1_TRUNCATION_F_MASS_MIXINGS, g1_truncation.EXPECTED_F_MASS_MIXINGS)
        self.assertEqual(
            mod.G1_TRUNCATION_KERNEL_DIMENSIONS, g1_truncation.EXPECTED_KERNEL_DIMENSIONS
        )
        self.assertEqual(mod.G1_TRUNCATION_SOURCE, g1_truncation.MODULE_NAME)
        self.assertEqual(mod.G1_TRUNCATION_JSON.name, g1_truncation.OUT_JSON.name)
        self.assertEqual(mod.G7_BENCHMARK_NEVER_TRUE_FLAGS, g7.NEVER_TRUE_FLAGS)
        self.assertEqual(set(mod.G7_BENCHMARK_TRUE_FLAGS), set(g7.DERIVED_FLAGS))
        self.assertEqual(mod.G8_STRUCTURAL_NEVER_TRUE_FLAGS, structural.NEVER_TRUE_FLAGS)
        source = Path(mod.__file__).read_text(encoding="utf-8")
        for module_name in (
            "g1_contract_truncation_scope_v20",
            "g7_decoupled_singlet_benchmark_evidence_v20",
            "g8_sm_pati_salam_structural_obstruction_v20",
            "g8_sm_pati_salam_flavour_nogo_v20",
            "g6_sm_pati_salam_remnant_rg_nogo_v20",
        ):
            self.assertNotIn(f"import {module_name}", source, module_name)

    def test_u1_u5_evidence_records_are_fail_closed(self):
        g1t = mod._load_json_artifact(mod.G1_TRUNCATION_JSON)
        g7 = mod._load_json_artifact(mod.G7_BENCHMARK_JSON)
        structural = mod._load_json_artifact(mod.G8_STRUCTURAL_JSON)
        g8 = mod._load_json_artifact(mod.G8_FLAVOUR_NOGO_JSON)
        forged = self._forged
        self.assertIs(mod.g1_truncation_evidence(g1t, g8)["recorded"], True)
        self.assertIs(mod.g7_benchmark_evidence(g7)["recorded"], True)
        self.assertIs(mod.g8_structural_evidence(structural)["recorded"], True)
        self.assertIs(mod.g8_flavour_evidence(g8)["recorded"], True)
        # The ledger-side cross-check needs the G8 flavour JSON.
        self.assertIs(mod.g1_truncation_evidence(g1t)["recorded"], False)

        undeclared = list(mod.G1_TRUNCATION_UNDECLARED)
        g1_cases = [
            None, [], {},
            forged(g1t, "status", value="G1_REOPENED"),
            forged(g1t, "module", value="other_module"),
            forged(g1t, "gate", value="G8"),
            forged(g1t, "model_contract_id", value="historical_option_c_no_x_v20"),
            forged(g1t, "n_checks", value=35),
            forged(g1t, "n_failed", value=False),
            forged(g1t, "failures", value=["x"]),
            forged(g1t, "census", "undeclared", value=undeclared[1:]),
            forged(g1t, "census", "undeclared", value=list(reversed(undeclared))),
            forged(g1t, "census", "undeclared_count", value=15),
            forged(g1t, "census", "allowed_count", value=True),
            forged(g1t, "kernel", "dimensions", "declared_LagHC", value=4),
            forged(g1t, "pq", "anomaly", "N_PQ", value=-33),
            forged(g1t, "sector", "F_16bar_mass_mixings",
                   value=list(reversed(mod.G1_TRUNCATION_F_MASS_MIXINGS))),
            forged(g1t, "flags", value=None),
            forged(g1t, "census", "field_redefinitions", "undeclared_real_dimension", value=24),
            forged(g1t, "census", "field_redefinitions", "mixing_redefinition_real_dimension", value=50),
            forged(g1t, "census", "field_redefinitions", "declared_orbit_real_dimension_bound",
                   value=148),
            forged(g1t, "census", "field_redefinitions", "all_couplings_real_dimension", value=True),
            forged(g1t, "census", "field_redefinitions", delete=True),
        ]
        g1_cases += [forged(g1t, "flags", name, value=True) for name in mod.G1_TRUNCATION_NEVER_TRUE_FLAGS]
        g1_cases += [forged(g1t, "flags", name, value=False) for name in mod.G1_TRUNCATION_TRUE_FLAGS]
        for case in g1_cases:
            record = mod.g1_truncation_evidence(case, g8)
            self.assertIs(record["recorded"], False)
            self.assertIs(record["changes_gate"], False)
            self.assertEqual(record["scope_text"], mod.G1_TRUNCATION_UNAVAILABLE_SCOPE)
            self.assertIsNone(record["undeclared"])
        for g8_case in (
            forged(g8, "contract", "allowed_but_undeclared", value=undeclared[1:]),
            forged(g8, "contract", value=None),
            {}, None,
        ):
            record = mod.g1_truncation_evidence(g1t, g8_case)
            self.assertIs(record["recorded"], False)
            self.assertIs(record["changes_gate"], False)

        g7_cases = [
            None, [], {},
            forged(g7, "status", value="G7_CLOSED"),
            forged(g7, "G7_status", value="CLOSED"),
            forged(g7, "gate", value="G8"),
            forged(g7, "n_checks", value=45),
            forged(g7, "n_failed", value=False),
            forged(g7, "failures", value=["x"]),
            forged(g7, "checks", "landau_cost.every_option_fails_three_loop", value=False),
            forged(g7, "checks", value=None),
        ]
        g7_cases += [forged(g7, "flags", name, value=False) for name in mod.G7_BENCHMARK_TRUE_FLAGS]
        g7_cases += [forged(g7, "flags", name, value=True) for name in mod.G7_BENCHMARK_NEVER_TRUE_FLAGS]
        for case in g7_cases:
            record = mod.g7_benchmark_evidence(case)
            self.assertIs(record["recorded"], False)
            self.assertIs(record["closes_gate"], False)

        not_claimed = [
            line for line in structural["scope"]["not_claimed"]
            if line != mod.G8_STRUCTURAL_PHI_SECTOR_NOT_CLAIMED
        ]
        structural_cases = [
            None, [], {},
            forged(structural, "status", value="G8_CLOSED"),
            forged(structural, "overall_state", value="ANY"),
            forged(structural, "gate", value="G7"),
            forged(structural, "n_checks", value=77),
            forged(structural, "n_failed", value=False),
            forged(structural, "failures", value=["x"]),
            forged(
                structural, "headline", "checks",
                "flavour_capable_sources_require_leaving_the_certified_orientation", value=False,
            ),
            forged(structural, "scope", "not_claimed", value=not_claimed),
        ]
        structural_cases += [
            forged(structural, "flags", name, value=False) for name in mod.G8_STRUCTURAL_TRUE_FLAGS
        ]
        structural_cases += [
            forged(structural, "flags", name, value=True) for name in mod.G8_STRUCTURAL_NEVER_TRUE_FLAGS
        ]
        for case in structural_cases:
            record = mod.g8_structural_evidence(case)
            self.assertIs(record["recorded"], False)
            self.assertIs(record["closes_gate"], False)

        probe_json = mod._load_json_artifact(mod.TWO_LOOP_PROBE_JSON)
        self.assertIs(mod.g7_coupled_singlet_probe_evidence(probe_json)["recorded"], True)
        first_finite = next(
            index for index, row in enumerate(probe_json["spectator_two_loop_probe"]["rows"])
            if row["delta_RL"] is not None
        )
        probe_cases = [
            None, [], {},
            forged(probe_json, "status", value="other"),
            forged(probe_json, "spectator_two_loop_probe", value=None),
            forged(probe_json, "spectator_two_loop_probe", "available", value="true"),
            forged(probe_json, "spectator_two_loop_probe", "perturbative_root_exists", value=True),
            forged(probe_json, "spectator_two_loop_probe", "perturbative_root_exists", value=0),
            forged(probe_json, "spectator_two_loop_probe", "sign_change", value=True),
            forged(probe_json, "spectator_two_loop_probe", "content", value="anchor content"),
            forged(probe_json, "spectator_two_loop_probe", "scan_log10_M_I", value=[8.0, 13.0]),
            forged(probe_json, "spectator_two_loop_probe", "n_rows", value=26),
            forged(probe_json, "spectator_two_loop_probe", "n_finite", value=True),
            forged(probe_json, "spectator_two_loop_probe", "rows", value=[]),
            forged(probe_json, "spectator_two_loop_probe", "rows", first_finite, "delta_RL", value=0.5),
            forged(probe_json, "spectator_two_loop_probe", "rows", first_finite, "delta_RL",
                   value=float("nan")),
            forged(probe_json, "spectator_two_loop_probe", "rows", 0, "reason", value=None),
            forged(probe_json, "spectator_two_loop_probe", "available", delete=True),
        ]
        for case in probe_cases:
            record = mod.g7_coupled_singlet_probe_evidence(case)
            self.assertIs(record["recorded"], False)
            self.assertIs(record["closes_gate"], False)
            self.assertIsNone(record["perturbative_root_exists"])

        pull = "minimum_load_bearing_pull_conservative_sigma"
        raw = "minimum_load_bearing_pull_raw_sigma"
        flavour_cases = [
            forged(g8, "data", pull, value=4.0),
            forged(g8, "data", pull, value=True),
            forged(g8, "data", pull, value="8.9"),
            forged(g8, "data", pull, value=float("nan")),
            forged(g8, "data", pull, delete=True),
            forged(g8, "data", raw, value=8.0),
            forged(g8, "data", raw, value=float("inf")),
            forged(g8, "data", "threshold_sigma", value=3.0),
            forged(g8, "data", "scale_band", "2e+16 GeV", value=1e16),
            forged(g8, "data", "scale_band", value={}),
            forged(g8, "verdict", value=g8["verdict"].replace("1e9-2e16 GeV", "1e9-1e16 GeV")),
            forged(g8, "verdict", value=g8["verdict"].replace("tan-beta-independent tests", "tests")),
            forged(g8, "data", "checks", "every_load_bearing_test_excluded_conservative_at_threshold",
                   value=False),
            forged(g8, "data", "checks", "every_load_bearing_test_excluded_raw_at_threshold",
                   value=False),
            forged(g8, "data", value=None),
        ]
        for case in flavour_cases:
            record = mod.g8_flavour_evidence(case)
            self.assertIs(record["recorded"], False)
            self.assertIs(record["closes_gate"], False)
            self.assertIsNone(record["route_recorded"])
            for key in (raw, pull, "threshold_sigma", "scale_band_GeV"):
                self.assertIsNone(record[key], key)
            self.assertEqual(
                record["pull_fields"],
                ["data.minimum_load_bearing_pull_raw_sigma",
                 "data.minimum_load_bearing_pull_conservative_sigma"],
            )

    def test_committed_ledger_json_records_the_g4_closure(self):
        # Regenerated by the integrator (g1_g8_gate_ledger_v20.py --write).
        committed = json.loads(mod.OUT_JSON.read_text(encoding="utf-8"))
        self.assertEqual(committed["status"], CLOSED_G4_STATUS)
        self.assertIs(g4_closure.ledger_g4_closed(committed), True)
        self.assertEqual(
            {name: row["status"] for name, row in committed["gates"].items()},
            SM_TRACK_CLOSED_STATUSES,
        )
        self.assertEqual(
            committed["gates"]["G4"]["closure_evidence"],
            self.report["gates"]["G4"]["closure_evidence"],
        )
        self.assertIs(committed["gates"]["G6"]["tree_level_evidence"]["recorded"], True)
        self.assertIs(committed["gates"]["G6"]["remnant_rg_evidence"]["recorded"], True)
        self.assertIs(committed["gates"]["G6"]["remnant_rg_evidence"]["closes_gate"], False)
        self.assertIs(committed["gates"]["G8"]["flavour_evidence"]["recorded"], True)
        # Decision U1 (regenerated by the integrator's chain).
        self.assertIs(committed["program_verdict"]["recorded"], True)
        self.assertEqual(committed["program_verdict"]["code"], mod.PROGRAM_VERDICT_CODE)
        self.assertEqual(committed["program_verdict"], self.report["program_verdict"])
        self.assertEqual(committed["n_checks"], 45)
        self.assertIs(committed["gates"]["G7"]["benchmark_evidence"]["recorded"], True)
        self.assertIs(committed["gates"]["G7"]["coupled_singlet_two_loop_probe"]["recorded"], True)
        self.assertIs(
            committed["gates"]["G7"]["coupled_singlet_two_loop_probe"]["closes_gate"], False
        )
        self.assertIs(
            committed["gates"]["G8"]["structural_obstruction_evidence"]["recorded"], True
        )
        self.assertIs(
            committed["gates"]["G1"]["model_contract_truncation_scope"]["recorded"], True
        )

    def test_markdown_states_the_g4_closure_and_the_evidence_only_citations(self):
        text = mod.write_markdown(json.loads(json.dumps(self.report)))
        self.assertIn("## G4: gauge quotient and physical Hessian at the G3 witness", text)
        self.assertIn("**G4 status:** `CLOSED`", text)
        self.assertIn("**Closure evidence certified:** `True`", text)
        self.assertIn("Closure scope: " + g4_closure.G4_LEDGER_CLOSED_SCOPE, text)
        for item in g4_closure.G4_SCOPE_LIMITS:
            self.assertIn("- " + item, text)
        self.assertIn("recorded `True`, closes gate `False`", text)
        self.assertIn("route `C`", text)
        self.assertIn(
            "remnant RG no-go `g6_sm_pati_salam_remnant_rg_nogo_v20` recorded `True`, "
            "closes gate `False`",
            text,
        )
        self.assertIn("## Program verdict (decision U1)", text)
        self.assertIn(f"**Code:** `{mod.PROGRAM_VERDICT_CODE}`", text)
        self.assertIn(mod.PROGRAM_VERDICT_TEXT, text)
        for component in self.report["program_verdict"]["components"]:
            self.assertIn(
                f"- [{component['label']}] {component['text']} "
                f"({', '.join(component['sources'])}; recorded `True`)",
                text,
            )
        self.assertIn("## Model-contract scope (G1)", text)
        self.assertIn(mod.G1_TRUNCATION_SCOPE_TEXT, text)
        self.assertIn(
            "- G7 (`BLOCKED`): decoupled-singlet benchmark evidence "
            "`g7_decoupled_singlet_benchmark_evidence_v20` recorded `True`, closes gate `False`",
            text,
        )
        self.assertIn(
            "- G7 (`BLOCKED`): coupled-singlet two-loop probe `two_loop_thresholds_v20` recorded "
            "`True`, closes gate `False`",
            text,
        )
        self.assertIn(
            "- G8 (`BLOCKED`): structural obstruction "
            "`g8_sm_pati_salam_structural_obstruction_v20` recorded `True`, closes gate `False`",
            text,
        )
        self.assertIn(
            "- `G1`: `CLOSED` - promoted exact-X scalar census, " + mod.G1_TRUNCATION_CLOSED_SCOPE,
            text,
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
        self.assertEqual(feasibility["current_authoritative_closed_gates"], 5)
        self.assertIs(feasibility["gauged_G3_sm_pati_salam_track_closed"], True)
        self.assertIs(feasibility["gauged_G4_sm_witness_quotient_closed"], True)
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
        self.assertEqual(report["status"], CLOSED_G4_STATUS)
        self.assertEqual(
            report["summary"]["closed"], ["G1", "G2", "G3", "G4", "G5"]
        )
        self.assertEqual(report["summary"]["open"], ["G6"])
        self.assertEqual(
            {name: row["status"] for name, row in report["gates"].items()},
            SM_TRACK_CLOSED_STATUSES,
        )
        self.assertEqual(report["gates"]["G4"]["unsatisfied_dependencies"], [])
        self.assertEqual(report["gates"]["G6"]["unsatisfied_dependencies"], [])
        self.assertEqual(report["gates"]["G7"]["unsatisfied_dependencies"], ["G6"])
        self.assertIs(report["gates"]["G4"]["closure_evidence"]["certified"], True)
        self.assertNotIn(mod.CONTRACT_BLOCKER, report["scientific_blockers"])
        self.assertEqual(
            report["scientific_blockers"],
            list(g4_closure.DOWNSTREAM_BLOCKERS_AFTER_G4),
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
